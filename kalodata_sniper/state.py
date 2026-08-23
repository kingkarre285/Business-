"""Verlaufsspeicher: erst der Vergleich mit dem letzten Lauf macht den Sniper scharf."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from .util import now_iso


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        stamp = datetime.fromisoformat(value)
    except ValueError:
        return None
    return stamp if stamp.tzinfo else stamp.replace(tzinfo=timezone.utc)


class State:
    """JSON-Datei mit dem Verlauf je Produkt.

    Struktur::

        {"version": 1, "runs": 12, "last_run": "...",
         "products": {"<key>": {"first_seen", "last_seen", "last_alert",
                                "history": [{"ts","revenue","units","score"}]}}}
    """

    VERSION = 1

    def __init__(self, path: str, history_length: int = 40):
        self.path = path
        self.history_length = history_length
        self.data: Dict[str, Any] = {"version": self.VERSION, "runs": 0,
                                     "last_run": None, "products": {}}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                loaded = json.load(handle)
        except (json.JSONDecodeError, OSError):
            # Kaputter State darf den Lauf nicht killen - wir starten neu,
            # sichern die alte Datei aber weg.
            try:
                os.replace(self.path, self.path + ".corrupt")
            except OSError:
                pass
            return
        if isinstance(loaded, dict) and isinstance(loaded.get("products"), dict):
            self.data = loaded

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        # Atomar schreiben, damit ein Abbruch den State nicht zerlegt
        handle = tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", delete=False,
            dir=os.path.dirname(self.path) or ".", suffix=".tmp")
        try:
            json.dump(self.data, handle, indent=2, ensure_ascii=False)
            handle.close()
            os.replace(handle.name, self.path)
        except BaseException:
            handle.close()
            if os.path.exists(handle.name):
                os.unlink(handle.name)
            raise

    # --- Abfragen ----------------------------------------------------------
    def entry(self, key: str) -> Optional[Dict[str, Any]]:
        return self.data["products"].get(key)

    def is_known(self, key: str) -> bool:
        return key in self.data["products"]

    def last_snapshot(self, key: str) -> Optional[Dict[str, Any]]:
        history: List[Dict[str, Any]] = (self.entry(key) or {}).get("history", [])
        return history[-1] if history else None

    def snapshot_before(self, key: str, hours: float) -> Optional[Dict[str, Any]]:
        """Juengster Eintrag, der mindestens ``hours`` alt ist.

        Ohne diese Sperre wuerde ein zweiter Lauf mit derselben Exportdatei das
        Momentum auf 0 druecken - verglichen wird dann naemlich der Datensatz
        mit sich selbst.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        history: List[Dict[str, Any]] = (self.entry(key) or {}).get("history", [])
        for snapshot in reversed(history):
            stamp = _parse_iso(snapshot.get("ts"))
            if stamp is not None and stamp <= cutoff:
                return snapshot
        return None

    def first_seen(self, key: str) -> Optional[datetime]:
        return _parse_iso((self.entry(key) or {}).get("first_seen"))

    def days_tracked(self, key: str) -> Optional[float]:
        first = self.first_seen(key)
        if first is None:
            return None
        return (datetime.now(timezone.utc) - first).total_seconds() / 86400

    def in_cooldown(self, key: str, hours: float) -> bool:
        last = _parse_iso((self.entry(key) or {}).get("last_alert"))
        if last is None:
            return False
        return datetime.now(timezone.utc) - last < timedelta(hours=hours)

    # --- Schreiben ---------------------------------------------------------
    def record(self, key: str, *, revenue: Optional[float], units: Optional[float],
               score: float, name: Optional[str] = None) -> None:
        entry = self.data["products"].setdefault(
            key, {"first_seen": now_iso(), "history": []})
        if name:
            entry["name"] = name
        entry["last_seen"] = now_iso()
        entry["history"].append({"ts": now_iso(), "revenue": revenue,
                                 "units": units, "score": round(score, 2)})
        entry["history"] = entry["history"][-self.history_length:]

    def mark_alerted(self, key: str) -> None:
        entry = self.data["products"].setdefault(
            key, {"first_seen": now_iso(), "history": []})
        entry["last_alert"] = now_iso()

    def finish_run(self, prune_after_days: Optional[int] = None) -> int:
        self.data["runs"] = int(self.data.get("runs", 0)) + 1
        self.data["last_run"] = now_iso()
        return self.prune(prune_after_days) if prune_after_days else 0

    def prune(self, older_than_days: int) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
        stale = [key for key, entry in self.data["products"].items()
                 if (_parse_iso(entry.get("last_seen")) or cutoff) < cutoff]
        for key in stale:
            del self.data["products"][key]
        return len(stale)
