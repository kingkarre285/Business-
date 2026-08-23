"""Kleine Helfer zum Parsen der Kalodata-Exportwerte."""

from __future__ import annotations

import math
import re
import unicodedata
from datetime import datetime, date, timezone
from typing import Optional

_SUFFIXES = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000, "t": 1_000_000_000_000}

# Waehrungssymbole und Tausender-/Dezimaltrenner, die in Exporten auftauchen
_CURRENCY = "$€£¥₫₹฿₽₩zł"


def slug(text: str) -> str:
    """Normalisiert einen Spaltennamen fuer den Vergleich (case/space/accent-frei)."""
    text = unicodedata.normalize("NFKD", str(text))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("ß", "ss")
    return re.sub(r"[^a-z0-9]+", "", text)


def parse_number(value, default: Optional[float] = None) -> Optional[float]:
    """Wandelt '$1.2M', '12,3 K', '1.234,56', '45%' oder 1234 in einen float.

    Gibt ``default`` zurueck, wenn nichts Sinnvolles erkennbar ist.
    """
    if value is None:
        return default
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return default if isinstance(value, float) and math.isnan(value) else float(value)

    text = str(value).strip()
    if not text or text.lower() in {"-", "--", "n/a", "na", "null", "none", "keine"}:
        return default

    for sym in _CURRENCY:
        text = text.replace(sym, "")
    text = text.replace("usd", "").replace("USD", "").replace("EUR", "").replace("eur", "")
    text = text.replace(" ", " ").strip()

    is_percent = "%" in text
    text = text.replace("%", "").strip()

    multiplier = 1.0
    match = re.search(r"([kmbt])\s*$", text, flags=re.IGNORECASE)
    if match:
        multiplier = _SUFFIXES[match.group(1).lower()]
        text = text[: match.start()].strip()

    negative = text.startswith("-") or (text.startswith("(") and text.endswith(")"))
    text = text.strip("()+-").strip()

    text = _normalise_separators(text)
    if not text:
        return default

    try:
        number = float(text)
    except ValueError:
        return default

    number *= multiplier
    if negative:
        number = -number
    if is_percent:
        # Prozentwerte werden intern immer als Anteil 0..1 gefuehrt
        number /= 100.0
    return number


def _normalise_separators(text: str) -> str:
    """Loest die Mehrdeutigkeit zwischen '1,234.5' (EN) und '1.234,5' (DE) auf."""
    text = text.replace(" ", "")
    if "," in text and "." in text:
        # Der zuletzt auftretende Trenner ist der Dezimaltrenner
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        head, _, tail = text.rpartition(",")
        # ',' mit genau 3 Nachkommastellen und vorhandenem Kopf = Tausendertrenner
        if len(tail) == 3 and head and head.replace(",", "").isdigit():
            text = text.replace(",", "")
        else:
            text = text.replace(",", ".")
    else:
        parts = text.split(".")
        if len(parts) > 2:
            text = "".join(parts[:-1]) + "." + parts[-1]
    return re.sub(r"[^0-9.]", "", text)


def parse_percent(value, default: Optional[float] = None) -> Optional[float]:
    """Wie ``parse_number``, erzwingt aber den Anteil 0..1.

    '45%' -> 0.45, '45' -> 0.45, '0.45' -> 0.45
    """
    number = parse_number(value, None)
    if number is None:
        return default
    if isinstance(value, str) and "%" in value:
        return number
    # Rohzahlen > 1 werden als Prozentangabe gelesen
    return number / 100.0 if number > 1 else number


def parse_date(value) -> Optional[date]:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y", "%Y/%m/%d", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S", "%d-%m-%Y", "%b %d, %Y"):
        try:
            return datetime.strptime(text[: len(fmt) + 6], fmt).date()
        except ValueError:
            continue
    if text.isdigit() and len(text) in (10, 13):  # Unix-Timestamp
        ts = int(text) / (1000 if len(text) == 13 else 1)
        return datetime.fromtimestamp(ts, tz=timezone.utc).date()
    return None


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def fmt_money(value: Optional[float], currency: str = "$") -> str:
    if value is None:
        return "-"
    for limit, suffix in ((1_000_000_000, "B"), (1_000_000, "M"), (1_000, "K")):
        if abs(value) >= limit:
            return f"{currency}{value / limit:.1f}{suffix}"
    return f"{currency}{value:,.0f}"


def fmt_pct(value: Optional[float]) -> str:
    return "-" if value is None else f"{value * 100:.1f}%"
