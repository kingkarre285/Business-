"""Datenmodell fuer ein Produkt aus Kalodata."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from datetime import date
from typing import Any, Dict, Optional


@dataclass
class Product:
    """Ein normalisiertes Produkt, unabhaengig von der Datenquelle.

    Alle Prozentwerte sind Anteile (0.25 == 25%), alle Geldwerte sind
    Absolutbetraege in der Waehrung des Exports.
    """

    name: str
    product_id: Optional[str] = None
    category: Optional[str] = None
    shop: Optional[str] = None
    url: Optional[str] = None

    price: Optional[float] = None
    revenue: Optional[float] = None            # Umsatz im Betrachtungszeitraum
    units_sold: Optional[float] = None
    commission_rate: Optional[float] = None    # Anteil, z.B. 0.25
    revenue_growth: Optional[float] = None     # Anteil, z.B. 3.4 == +340%
    rating: Optional[float] = None             # 0..5

    creators: Optional[float] = None           # Anzahl bewerbender Creator
    videos: Optional[float] = None
    lives: Optional[float] = None
    gpm: Optional[float] = None                # Gross per mille (Umsatz je 1000 Views)
    launch_date: Optional[date] = None

    raw: Dict[str, Any] = field(default_factory=dict)

    # --- abgeleitete Werte -------------------------------------------------
    @property
    def key(self) -> str:
        """Stabiler Schluessel fuer den Verlaufsspeicher."""
        if self.product_id:
            return str(self.product_id)
        base = f"{self.name}|{self.shop or ''}".lower()
        return "h:" + hashlib.sha1(base.encode("utf-8")).hexdigest()[:16]

    @property
    def payout_per_sale(self) -> Optional[float]:
        """Provision in Geld pro verkaufter Einheit."""
        if self.price is None or self.commission_rate is None:
            return None
        return self.price * self.commission_rate

    @property
    def revenue_per_creator(self) -> Optional[float]:
        if self.revenue is None or not self.creators:
            return None
        return self.revenue / self.creators

    @property
    def revenue_per_video(self) -> Optional[float]:
        if self.revenue is None or not self.videos:
            return None
        return self.revenue / self.videos

    @property
    def age_days(self) -> Optional[int]:
        if self.launch_date is None:
            return None
        return (date.today() - self.launch_date).days

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data.pop("raw", None)
        if self.launch_date:
            data["launch_date"] = self.launch_date.isoformat()
        data["key"] = self.key
        return data


@dataclass
class ScoredProduct:
    """Produkt plus Bewertung durch die Sniper-Engine."""

    product: Product
    score: float                                  # 0..100
    components: Dict[str, float] = field(default_factory=dict)   # 0..1 je Kriterium
    reasons: list = field(default_factory=list)   # menschenlesbare Begruendung
    rejected_by: list = field(default_factory=list)
    momentum: Optional[float] = None              # Umsatzdelta ggue. letztem Lauf (Anteil)
    is_new: bool = False                          # zum ersten Mal gesehen

    @property
    def passed(self) -> bool:
        return not self.rejected_by

    def to_dict(self) -> Dict[str, Any]:
        return {
            **self.product.to_dict(),
            "score": round(self.score, 2),
            "components": {k: round(v, 4) for k, v in self.components.items()},
            "reasons": self.reasons,
            "rejected_by": self.rejected_by,
            "momentum": self.momentum,
            "is_new": self.is_new,
        }
