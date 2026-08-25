"""Filterwerte aus echten Daten ableiten statt raten.

Die Standardfilter sind eine Annahme. Wie viel Umsatz ein Produkt im deutschen
Markt macht, wie viele Creator dort ueblich sind - das steht in den Daten, nicht
im Bauchgefuehl. Dieses Modul liest einen echten Export und schlaegt Schwellen
vor, die eine brauchbare Menge Kandidaten durchlassen.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from .config import Config
from .models import Product
from .scoring import apply_filters
from .util import fmt_money, fmt_pct

# Wie viele Produkte die Filter idealerweise passieren sollen
TARGET_PASS_RATIO = 0.25


def percentile(values: Sequence[float], fraction: float) -> Optional[float]:
    """Lineare Interpolation - robust auch bei sehr kleinen Datenmengen."""
    clean = sorted(v for v in values if v is not None)
    if not clean:
        return None
    if len(clean) == 1:
        return clean[0]
    position = fraction * (len(clean) - 1)
    low = int(position)
    high = min(low + 1, len(clean) - 1)
    weight = position - low
    return clean[low] * (1 - weight) + clean[high] * weight


def _column(products: Sequence[Product], attribute: str) -> List[float]:
    return [getattr(p, attribute) for p in products if getattr(p, attribute) is not None]


# Je Filter: (Produktfeld, Richtung, Perzentilposition bei voller Strenge).
# Die Richtung wird deklariert, nicht aus der Position abgeleitet - eine
# Untergrenze kann durchaus im oberen Perzentilbereich liegen (revenue_min).
_SPEC = {
    "price_min":       ("price",           "min", 0.15),
    "price_max":       ("price",           "max", 0.85),
    "revenue_min":     ("revenue",         "min", 0.60),
    "units_min":       ("units_sold",      "min", 0.50),
    "commission_min":  ("commission_rate", "min", 0.50),
    "rating_min":      ("rating",          "min", 0.30),
    "creators_max":    ("creators",        "max", 0.60),
}


def suggest_at(products: Sequence[Product], strictness: float) -> Dict[str, Any]:
    """Filtervorschlaege bei gegebener Strenge (0 = alles durch, 1 = streng)."""
    suggestions: Dict[str, Any] = {}
    for key, (attribute, direction, position) in _SPEC.items():
        values = _column(products, attribute)
        if not values:
            continue
        # Locker (strictness 0): Untergrenze auf das Minimum, Obergrenze auf
        # das Maximum - dann passiert jedes Produkt.
        fraction = (position * strictness if direction == "min"
                    else 1.0 - (1.0 - position) * strictness)
        value = percentile(values, fraction)
        if value is None:
            continue

        if key in ("price_min", "price_max", "revenue_min"):
            suggestions[key] = _round_money(value)
        elif key == "units_min":
            suggestions[key] = max(int(value), 0)
        elif key == "commission_min":
            # Nie unter 5% - darunter lohnt der Aufwand unabhaengig vom Markt
            suggestions[key] = round(max(value, 0.05), 2)
        elif key == "rating_min":
            suggestions[key] = round(min(max(value, 3.5), 4.6), 1)
        elif key == "creators_max":
            suggestions[key] = max(int(value), 1)
    return suggestions


def suggest_filters(products: Sequence[Product],
                    target_ratio: float = TARGET_PASS_RATIO) -> Dict[str, Any]:
    """Sucht die Strenge, bei der etwa ``target_ratio`` der Produkte durchkommt.

    Einzeln plausible Perzentilwerte ergeben kombiniert oft fast keine Treffer -
    sechs Filter multiplizieren sich. Deshalb wird nicht jeder Filter fuer sich
    gesetzt, sondern die gemeinsame Strenge auf die Zielquote eingeregelt.
    """
    if not products:
        return {}
    target_count = max(1, round(len(products) * target_ratio))

    best: Dict[str, Any] = {}
    best_cost = None
    for step in range(20, -1, -1):                 # streng nach locker
        candidate = suggest_at(products, step / 20)
        if not candidate:
            continue
        passing = count_passing(products, candidate)
        # Asymmetrisch: zu streng wiegt schwerer als zu locker. Ein Filtersatz
        # ohne Treffer ist wertlos, ein etwas zu weiter nur unschaerfer.
        cost = (target_count - passing) * 3 if passing < target_count else passing - target_count
        if best_cost is None or cost < best_cost:
            best, best_cost = candidate, cost
    return best


def _round_money(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    if value >= 10_000:
        return round(value / 1_000) * 1_000
    if value >= 100:
        return round(value / 10) * 10
    return round(value, 2)


def count_passing(products: Sequence[Product], filters: Dict[str, Any]) -> int:
    return sum(1 for p in products if not apply_filters(p, filters))


def build_report(products: Sequence[Product], config: Config,
                 target_ratio: float = TARGET_PASS_RATIO) -> Dict[str, Any]:
    """Vergleicht aktuelle und vorgeschlagene Filter samt Trefferzahl."""
    current = dict(config.filters)
    suggested = suggest_filters(products, target_ratio)
    merged = {**current, **suggested}

    rows = []
    for key in ("price_min", "price_max", "revenue_min", "units_min",
                "commission_min", "rating_min", "creators_max"):
        if key not in suggested:
            continue
        rows.append({"filter": key, "current": current.get(key),
                     "suggested": suggested[key],
                     "formatted_current": _format(key, current.get(key)),
                     "formatted_suggested": _format(key, suggested[key])})

    return {
        "products": len(products),
        "rows": rows,
        "passing_now": count_passing(products, current),
        "passing_suggested": count_passing(products, merged),
        "suggested": suggested,
        "missing_columns": sorted(
            {"price", "revenue", "units_sold", "commission_rate", "rating", "creators"}
            - {a for a in ("price", "revenue", "units_sold", "commission_rate",
                           "rating", "creators") if _column(products, a)}
        ),
    }


def _format(key: str, value: Any) -> str:
    if value is None:
        return "-"
    if key in ("price_min", "price_max", "revenue_min"):
        return fmt_money(value)
    if key == "commission_min":
        return fmt_pct(value)
    return f"{value:g}"


def render(report: Dict[str, Any]) -> str:
    lines = [f"{report['products']} Produkte ausgewertet.", ""]
    if not report["rows"]:
        lines.append("Keine auswertbaren Spalten gefunden - Export pruefen.")
        return "\n".join(lines)

    lines.append(f"{'Filter':<16}{'aktuell':>14}{'vorgeschlagen':>18}")
    lines.append("-" * 48)
    for row in report["rows"]:
        marker = " " if row["current"] == row["suggested"] else "*"
        lines.append(f"{row['filter']:<16}{row['formatted_current']:>14}"
                     f"{row['formatted_suggested']:>18} {marker}")
    lines += [
        "",
        f"Kandidaten aktuell:       {report['passing_now']} von {report['products']}",
        f"Kandidaten nach Vorschlag: {report['passing_suggested']} von {report['products']}",
    ]
    if report["missing_columns"]:
        lines.append("\nOhne Daten (Filter unveraendert): "
                     + ", ".join(report["missing_columns"]))
    lines.append("\nUebernehmen mit: python -m kalodata_sniper calibrate --apply")
    return "\n".join(lines)


def apply_to_config(config: Config, suggested: Dict[str, Any], path: str) -> str:
    config.data["filters"].update(suggested)
    config.dump(path)
    return path
