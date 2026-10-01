"""Positionsgrößen und Risikolimits."""


def position_size_usd(equity: float, price: float, stop_loss: float, cfg: dict, min_usd: float = 0) -> float:
    """Betrag so wählen, dass ein Stop-Loss-Treffer max. risk_per_trade_pct kostet,
    gedeckelt auf max_position_pct des Kapitals. 0 = kein Trade."""
    if price <= 0 or stop_loss is None or stop_loss >= price:
        return 0.0
    risk_usd = equity * cfg["risk_per_trade_pct"] / 100
    stop_dist_pct = (price - stop_loss) / price
    amount = min(risk_usd / stop_dist_pct, equity * cfg["max_position_pct"] / 100)
    if amount < max(cfg["min_order_usd"], min_usd):
        return 0.0
    return round(amount, 2)


def daily_loss_exceeded(start_equity: float, equity: float, cfg: dict) -> bool:
    if start_equity <= 0:
        return False
    return (start_equity - equity) / start_equity * 100 >= cfg["max_daily_loss_pct"]
