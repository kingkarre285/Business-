"""Positionsgrößen und Risikolimits.

Begriffe:
  exposure – Marktwert der Position (das, was sich mit dem Kurs bewegt)
  margin   – eingesetztes Kapital = exposure / Hebel
Der Hebel ändert das Risiko pro Trade NICHT: die Größe richtet sich nach dem
Abstand zum Stop-Loss. Er spart nur Kapital, damit mehr Positionen parallel möglich sind.
"""


def leverage_for(item: dict, cfg: dict) -> int:
    return int(item.get("leverage", cfg["leverage"]))


def position_size(equity: float, price: float, stop_loss: float, cfg: dict,
                  leverage: int = 1, min_exposure: float = 0) -> tuple[float, float]:
    """Gibt (exposure, margin) in USD zurück; (0, 0) = kein Trade.
    Ein Stop-Loss-Treffer kostet höchstens risk_per_trade_pct des Kapitals."""
    if price <= 0 or stop_loss is None or stop_loss == price:
        return 0.0, 0.0
    stop_dist_pct = abs(price - stop_loss) / price
    exposure = min(
        equity * cfg["risk_per_trade_pct"] / 100 / stop_dist_pct,
        equity * cfg["max_exposure_pct"] / 100,
        equity * cfg["max_position_pct"] / 100 * leverage,
    )
    margin = exposure / leverage
    if exposure < min_exposure or margin < cfg["min_order_usd"]:
        return 0.0, 0.0
    return round(exposure, 2), round(margin, 2)


def daily_loss_exceeded(start_equity: float, equity: float, cfg: dict) -> bool:
    if start_equity <= 0:
        return False
    return (start_equity - equity) / start_equity * 100 >= cfg["max_daily_loss_pct"]
