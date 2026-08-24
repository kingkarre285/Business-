"""Konfiguration des Snipers (JSON oder YAML)."""

from __future__ import annotations

import copy
import json
import os
from typing import Any, Dict, List, Optional

DEFAULT_CONFIG: Dict[str, Any] = {
    # Woher die Produktdaten kommen
    "source": {
        "type": "csv",                       # csv | api
        "path": "data/kalodata_export.csv",  # bei type=csv: Datei oder Ordner (neueste Datei)
        "api": {
            # Werte aus dem Kalodata Open Center. Alle Endpunkte sind POST + JSON
            # unter www.kalodata.com/openapi/v1/tiktok/... mit Secret-Key im Header.
            "base_url": "https://www.kalodata.com",
            "api_key_env": "KALODATA_API_KEY",
            "auth": {"header": "secret-key", "prefix": ""},
            "module": "product",
            "endpoints": {
                "rank": "/openapi/v1/tiktok/product/list",
                "detail": "/openapi/v1/tiktok/product/detail",
            },
            "method": "POST",
            # Die vier Pflichtfelder aller Endpunkte
            "request": {
                "region": "DE",          # US BR MX ID JP MY PH SG TH VN GB ES DE FR IT
                # Die API bietet kein de-DE - Textfelder kommen auf Englisch
                "language": "en-US",     # zh-CN en-US id-ID th-TH vi-VN es-ES ja-JP pt-BR ko-KR fr-FR
                "currency": "EUR",       # CNY USD IDR VND THB MYR JPY PHP GBP SGD MXN EUR BRL
                "date_range": "last7Day",  # oder "2026-08-01~2026-08-07" bzw. "2026-08"
                "filters": {},
            },
            # Logischer Name -> Feldname der API (die Doku nutzt snake_case)
            "param_names": {
                "page": "page",
                "page_size": "page_size",
            },
            "pages": 2,
            "page_size": 50,
            # Abrechnung nach Verbrauch: hartes Budget statt boeser Ueberraschung
            "max_requests_per_run": 10,
            "cache_ttl_minutes": 360,
            "cache_dir": "data/.cache",
            # Dokumentiertes Limit: 100 Requests / 10 Sekunden
            "rate_limit_requests": 100,
            "rate_limit_window_seconds": 10,
            "delay_seconds": 0.2,
            "timeout_seconds": 30,
        },
    },

    # Harte Ausschlusskriterien - wer hier durchfaellt, wird nie gescort
    "filters": {
        "price_min": 8.0,
        "price_max": 150.0,
        "revenue_min": 3000.0,
        "revenue_max": None,
        "units_min": 30,
        "commission_min": 0.10,
        "rating_min": 4.0,
        "creators_max": 500,
        "max_age_days": None,
        "categories_include": [],
        "categories_exclude": [],
        "keywords_exclude": ["gift card", "gutschein", "coupon"],
        "require_fields": ["name", "revenue"],
    },

    # Gewichtung der Score-Bausteine (werden intern normiert)
    "weights": {
        "momentum": 3.0,      # Wachstum / Umsatzsprung seit letztem Lauf
        "opportunity": 2.0,   # Provision in Euro pro Verkauf
        "traction": 1.5,      # Absoluter Umsatz - Nachfrage ist bewiesen
        "competition": 2.0,   # Wenig Creator = noch Platz
        "efficiency": 1.0,    # Umsatz je Creator / GPM
        "freshness": 1.5,     # Junges Produkt / neu im Radar
    },

    # Referenzwerte fuer die Normierung (Wert >= Target ergibt 1.0)
    "targets": {
        "growth": 1.0,          # +100% Wachstum = voller Momentum-Score
        "payout_per_sale": 15.0,
        "revenue": 250_000.0,
        "creators": 400,        # ab hier gilt der Markt als dicht
        "revenue_per_creator": 3_000.0,
        "max_age_days": 90,     # aelter als das = keine Frische-Punkte
    },

    "scoring": {
        # Momentum wird gegen den juengsten Snapshot verglichen, der mindestens
        # so alt ist. Verhindert, dass ein Testlauf mit derselben Datei das
        # Wachstum auf 0 setzt.
        "momentum_lookback_hours": 12,
    },

    # Wann alarmiert wird
    "alerts": {
        "min_score": 70.0,
        "top_n": 15,
        "only_new_or_rising": True,   # nur Neuzugaenge oder Score-Anstiege melden
        "rising_delta": 5.0,          # ab wie vielen Score-Punkten "steigend" gilt
        "cooldown_hours": 24,         # gleicher Treffer nicht oefter melden
        "max_per_run": 10,
    },

    "notifiers": [
        {"type": "console", "enabled": True},
        {"type": "telegram", "enabled": False,
         "token_env": "TELEGRAM_BOT_TOKEN", "chat_id_env": "TELEGRAM_CHAT_ID"},
        {"type": "discord", "enabled": False, "webhook_env": "DISCORD_WEBHOOK_URL"},
        {"type": "slack", "enabled": False, "webhook_env": "SLACK_WEBHOOK_URL"},
        {"type": "webhook", "enabled": False, "url_env": "SNIPER_WEBHOOK_URL"},
    ],

    "output": {
        "state_file": "data/state.json",
        "report_dir": "reports",
        "write_html": True,
        "write_csv": True,
        "currency": "\u20ac",
        "history_length": 40,
        "prune_after_days": 120,
    },
}


class Config:
    def __init__(self, data: Optional[Dict[str, Any]] = None, path: Optional[str] = None):
        self.data = _deep_merge(copy.deepcopy(DEFAULT_CONFIG), data or {})
        self.path = path

    # Zugriff per Punktpfad: cfg.get("filters.price_min")
    def get(self, dotted: str, default: Any = None) -> Any:
        node: Any = self.data
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def __getitem__(self, key: str) -> Any:
        return self.data[key]

    @property
    def filters(self) -> Dict[str, Any]:
        return self.data["filters"]

    @property
    def weights(self) -> Dict[str, float]:
        return {k: float(v) for k, v in self.data["weights"].items() if float(v) > 0}

    @property
    def targets(self) -> Dict[str, float]:
        return self.data["targets"]

    @classmethod
    def load(cls, path: Optional[str]) -> "Config":
        if not path:
            return cls()
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config nicht gefunden: {path}")
        with open(path, "r", encoding="utf-8") as handle:
            text = handle.read()
        if path.endswith((".yaml", ".yml")):
            try:
                import yaml  # type: ignore
            except ImportError as exc:
                raise RuntimeError("YAML-Config braucht pyyaml - oder nutze JSON.") from exc
            data = yaml.safe_load(text) or {}
        else:
            data = json.loads(text)
        return cls(data, path=path)

    def dump(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")

    def enabled_notifiers(self) -> List[Dict[str, Any]]:
        return [n for n in self.data.get("notifiers", []) if n.get("enabled")]


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = _deep_merge(base[key], value)
        else:
            base[key] = value
    return base
