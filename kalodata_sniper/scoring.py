"""Die Sniper-Engine: harte Filter, gewichtetes Scoring, Momentum aus dem Verlauf."""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

from .config import Config
from .models import Product, ScoredProduct
from .state import State
from .util import clamp, fmt_money, fmt_pct


# --- Normierungskurven -----------------------------------------------------
def saturate(value: Optional[float], target: float) -> Optional[float]:
    """Linear bis zum Zielwert, danach 1.0."""
    if value is None or target <= 0:
        return None
    return clamp(value / target)


def log_saturate(value: Optional[float], target: float) -> Optional[float]:
    """Logarithmisch - grosse Ausreisser dominieren den Score nicht."""
    if value is None or target <= 0:
        return None
    return clamp(math.log1p(max(value, 0)) / math.log1p(target))


def inverse_log_saturate(value: Optional[float], target: float) -> Optional[float]:
    """Weniger ist besser (z.B. Anzahl konkurrierender Creator)."""
    scored = log_saturate(value, target)
    return None if scored is None else 1.0 - scored


# --- Filter ----------------------------------------------------------------
def apply_filters(product: Product, filters: Dict[str, Any]) -> List[str]:
    """Gibt die Gruende zurueck, warum das Produkt rausfliegt (leer = bestanden)."""
    out: List[str] = []

    for field in filters.get("require_fields") or []:
        if getattr(product, field, None) in (None, ""):
            out.append(f"{field} fehlt")

    checks: List[Tuple[str, Optional[float], Optional[float], Optional[float]]] = [
        ("Preis", product.price, filters.get("price_min"), filters.get("price_max")),
        ("Umsatz", product.revenue, filters.get("revenue_min"), filters.get("revenue_max")),
        ("Verkaeufe", product.units_sold, filters.get("units_min"), None),
        ("Provision", product.commission_rate, filters.get("commission_min"), None),
        ("Bewertung", product.rating, filters.get("rating_min"), None),
        ("Creator", product.creators, None, filters.get("creators_max")),
        ("Alter", product.age_days, None, filters.get("max_age_days")),
    ]
    for label, value, low, high in checks:
        if value is None:
            continue  # Fehlende Daten schliessen nicht aus - dafuer require_fields
        if low is not None and value < low:
            out.append(f"{label} {_fmt(label, value)} < min {_fmt(label, low)}")
        if high is not None and value > high:
            out.append(f"{label} {_fmt(label, value)} > max {_fmt(label, high)}")

    include = [c.lower() for c in filters.get("categories_include") or []]
    exclude = [c.lower() for c in filters.get("categories_exclude") or []]
    category = (product.category or "").lower()
    if include and not any(c in category for c in include):
        out.append(f"Kategorie '{product.category}' nicht in Whitelist")
    if exclude and any(c in category for c in exclude):
        out.append(f"Kategorie '{product.category}' auf Blacklist")

    haystack = f"{product.name} {product.category or ''}".lower()
    for word in filters.get("keywords_exclude") or []:
        if word.lower() in haystack:
            out.append(f"Stichwort '{word}' ausgeschlossen")

    return out


def _fmt(label: str, value: float) -> str:
    if label in ("Provision",):
        return fmt_pct(value)
    if label in ("Preis", "Umsatz"):
        return fmt_money(value)
    return f"{value:g}"


# --- Momentum aus dem Verlauf ---------------------------------------------
def compute_momentum(product: Product, state: Optional[State],
                     lookback_hours: float = 12.0) -> Optional[float]:
    """Umsatzwachstum als Anteil.

    Bevorzugt wird das Delta zu einem ausreichend alten eigenen Snapshot - das ist
    der echte Breakout-Indikator. Gibt es den nicht (erster Lauf, oder derselbe
    Export zweimal hintereinander), greift das Wachstumsfeld aus dem Export.
    """
    if state is not None and product.revenue is not None:
        snapshot = state.snapshot_before(product.key, lookback_hours)
        previous = (snapshot or {}).get("revenue")
        if previous and previous > 0:
            return (product.revenue - previous) / previous
    return product.revenue_growth


# --- Scoring ---------------------------------------------------------------
def score_product(product: Product, config: Config,
                  state: Optional[State] = None) -> ScoredProduct:
    targets = config.targets
    weights = config.weights

    momentum = compute_momentum(
        product, state, float(config.get("scoring.momentum_lookback_hours", 12)))
    is_new = state is not None and not state.is_known(product.key)

    components: Dict[str, Optional[float]] = {
        "momentum": saturate(momentum, float(targets["growth"])) if momentum is not None else None,
        "opportunity": saturate(product.payout_per_sale, float(targets["payout_per_sale"])),
        "traction": log_saturate(product.revenue, float(targets["revenue"])),
        "competition": inverse_log_saturate(product.creators, float(targets["creators"])),
        "efficiency": log_saturate(product.revenue_per_creator or product.gpm,
                                   float(targets["revenue_per_creator"])),
        "freshness": _freshness(product, state, float(targets["max_age_days"])),
    }

    # Nur vorhandene Bausteine zaehlen - fehlende Daten werden nicht als 0 bestraft,
    # sondern aus der Gewichtung herausgerechnet.
    available = {k: v for k, v in components.items() if v is not None and k in weights}
    total_weight = sum(weights[k] for k in available)
    score = 100.0 * sum(weights[k] * v for k, v in available.items()) / total_weight if total_weight else 0.0

    scored = ScoredProduct(
        product=product,
        score=score,
        components={k: v for k, v in components.items() if v is not None},
        rejected_by=apply_filters(product, config.filters),
        momentum=momentum,
        is_new=bool(is_new),
    )
    scored.reasons = build_reasons(scored, config)
    return scored


def _freshness(product: Product, state: Optional[State], max_age_days: float) -> Optional[float]:
    """Frisch ist, was jung gelistet ist - oder erst kurz im eigenen Radar."""
    age = product.age_days
    if age is None and state is not None:
        age = state.days_tracked(product.key)
        if age is None:
            return 1.0  # zum ersten Mal gesehen = maximal frisch
    if age is None:
        return None
    return clamp(1.0 - age / max_age_days) if max_age_days > 0 else None


def build_reasons(scored: ScoredProduct, config: Config) -> List[str]:
    product, reasons = scored.product, []
    if scored.is_new:
        reasons.append("Neu im Radar")
    if scored.momentum is not None and scored.momentum >= 0.25:
        reasons.append(f"Umsatz {fmt_pct(scored.momentum)} gestiegen")
    if product.payout_per_sale:
        reasons.append(f"{fmt_money(product.payout_per_sale, config.get('output.currency', '$'))} Provision/Verkauf")
    if product.creators is not None and product.creators <= config.targets["creators"] * 0.25:
        reasons.append(f"nur {product.creators:g} Creator aktiv")
    if product.revenue_per_creator and product.revenue_per_creator >= config.targets["revenue_per_creator"]:
        reasons.append(f"{fmt_money(product.revenue_per_creator)} Umsatz je Creator")
    if product.rating is not None and product.rating >= 4.7:
        reasons.append(f"Rating {product.rating:.1f}")
    if product.age_days is not None and product.age_days <= 30:
        reasons.append(f"erst {product.age_days} Tage gelistet")
    return reasons


def run_scoring(products: List[Product], config: Config,
                state: Optional[State] = None) -> List[ScoredProduct]:
    """Bewertet alle Produkte und sortiert die Treffer absteigend nach Score."""
    scored = [score_product(p, config, state) for p in products]
    scored.sort(key=lambda s: (s.passed, s.score), reverse=True)
    return scored


def select_alerts(scored: List[ScoredProduct], config: Config,
                  state: Optional[State]) -> List[ScoredProduct]:
    """Filtert, was tatsaechlich gemeldet wird - inkl. Cooldown und Anstiegslogik."""
    alerts_cfg = config["alerts"]
    min_score = float(alerts_cfg.get("min_score", 70))
    cooldown = float(alerts_cfg.get("cooldown_hours", 0) or 0)
    rising_delta = float(alerts_cfg.get("rising_delta", 5))
    only_new_or_rising = bool(alerts_cfg.get("only_new_or_rising", True))
    max_per_run = int(alerts_cfg.get("max_per_run", 10))

    hits: List[ScoredProduct] = []
    for item in scored:
        if not item.passed or item.score < min_score:
            continue
        if state is not None:
            if cooldown and state.in_cooldown(item.product.key, cooldown):
                continue
            if only_new_or_rising and not item.is_new:
                previous = (state.last_snapshot(item.product.key) or {}).get("score")
                if previous is not None and item.score - previous < rising_delta:
                    continue
        hits.append(item)
        if len(hits) >= max_per_run:
            break
    return hits
