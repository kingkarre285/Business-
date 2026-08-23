"""Alarmkanaele - bewusst nur mit der Standardbibliothek (kein requests noetig)."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from .models import ScoredProduct
from .util import fmt_money, fmt_pct

TIMEOUT = 20


def _post_json(url: str, payload: Dict[str, Any]) -> None:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "kalodata-sniper/0.1"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        response.read()


def _env(name: Optional[str]) -> Optional[str]:
    return os.environ.get(name) if name else None


# --- Formatierung ----------------------------------------------------------
def format_product_line(item: ScoredProduct, index: int = 0, currency: str = "$") -> str:
    p = item.product
    head = f"{index}. " if index else ""
    parts = [
        f"{head}{p.name.strip()[:90]}",
        f"   Score {item.score:.0f}/100"
        + (f" | Umsatz {fmt_money(p.revenue, currency)}" if p.revenue is not None else "")
        + (f" | Preis {fmt_money(p.price, currency)}" if p.price is not None else "")
        + (f" | Provision {fmt_pct(p.commission_rate)}" if p.commission_rate is not None else ""),
    ]
    if item.reasons:
        parts.append("   " + " · ".join(item.reasons[:4]))
    if p.url:
        parts.append(f"   {p.url}")
    return "\n".join(parts)


def format_digest(items: List[ScoredProduct], currency: str = "$", title: str = "Kalodata Sniper") -> str:
    if not items:
        return f"{title}: keine neuen Treffer."
    lines = [f"{title}: {len(items)} Treffer", ""]
    lines += [format_product_line(item, i, currency) for i, item in enumerate(items, 1)]
    return "\n".join(lines)


# --- Kanaele ---------------------------------------------------------------
class Notifier:
    type = "base"

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def send(self, items: List[ScoredProduct], currency: str = "$") -> None:
        raise NotImplementedError


class ConsoleNotifier(Notifier):
    type = "console"

    def send(self, items, currency="$"):
        print(format_digest(items, currency))


class TelegramNotifier(Notifier):
    type = "telegram"

    def send(self, items, currency="$"):
        token = self.config.get("token") or _env(self.config.get("token_env", "TELEGRAM_BOT_TOKEN"))
        chat_id = self.config.get("chat_id") or _env(self.config.get("chat_id_env", "TELEGRAM_CHAT_ID"))
        if not token or not chat_id:
            raise RuntimeError("Telegram: Token oder Chat-ID fehlt (Env-Variablen setzen).")
        text = format_digest(items, currency)
        # Telegram deckelt bei 4096 Zeichen - lieber stueckeln als abschneiden
        for chunk in _chunks(text, 3900):
            _post_json(f"https://api.telegram.org/bot{token}/sendMessage",
                       {"chat_id": chat_id, "text": chunk, "disable_web_page_preview": True})


class DiscordNotifier(Notifier):
    type = "discord"

    def send(self, items, currency="$"):
        url = self.config.get("webhook") or _env(self.config.get("webhook_env", "DISCORD_WEBHOOK_URL"))
        if not url:
            raise RuntimeError("Discord: Webhook-URL fehlt.")
        for chunk in _chunks(format_digest(items, currency), 1900):
            _post_json(url, {"content": chunk})


class SlackNotifier(Notifier):
    type = "slack"

    def send(self, items, currency="$"):
        url = self.config.get("webhook") or _env(self.config.get("webhook_env", "SLACK_WEBHOOK_URL"))
        if not url:
            raise RuntimeError("Slack: Webhook-URL fehlt.")
        _post_json(url, {"text": format_digest(items, currency)})


class WebhookNotifier(Notifier):
    """Roh-JSON an eine beliebige URL - fuer Make, n8n, Zapier, eigene Backends."""

    type = "webhook"

    def send(self, items, currency="$"):
        url = self.config.get("url") or _env(self.config.get("url_env", "SNIPER_WEBHOOK_URL"))
        if not url:
            raise RuntimeError("Webhook: URL fehlt.")
        _post_json(url, {"count": len(items), "products": [i.to_dict() for i in items]})


REGISTRY = {n.type: n for n in (ConsoleNotifier, TelegramNotifier, DiscordNotifier,
                                SlackNotifier, WebhookNotifier)}


def build_notifiers(configs: List[Dict[str, Any]]) -> List[Notifier]:
    notifiers = []
    for entry in configs:
        cls = REGISTRY.get(entry.get("type", ""))
        if cls is None:
            raise ValueError(f"Unbekannter Notifier-Typ: {entry.get('type')!r}")
        notifiers.append(cls(entry))
    return notifiers


def dispatch(notifiers: List[Notifier], items: List[ScoredProduct],
             currency: str = "$") -> List[str]:
    """Verschickt an alle Kanaele. Ein kaputter Kanal stoppt die anderen nicht."""
    errors = []
    for notifier in notifiers:
        try:
            notifier.send(items, currency)
        except (urllib.error.URLError, RuntimeError, OSError, ValueError) as exc:
            errors.append(f"{notifier.type}: {exc}")
    return errors


def _chunks(text: str, size: int) -> List[str]:
    if len(text) <= size:
        return [text]
    out, current = [], ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > size:
            out.append(current)
            current = ""
        current += line + "\n"
    if current.strip():
        out.append(current)
    return out
