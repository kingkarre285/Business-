"""Trendfolge-Strategie für Long und Short: SMA-Kreuzung mit Trendfilter, RSI-Filter und ATR-Stops."""
from dataclasses import dataclass

import pandas as pd


@dataclass
class Signal:
    action: str          # "buy" (Long eröffnen), "short" (Short eröffnen), "close" oder "hold"
    price: float
    stop_loss: float | None = None
    take_profit: float | None = None
    reason: str = ""


def rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    rs = gain / loss.replace(0, float("nan"))
    return (100 - 100 / (1 + rs)).fillna(100)


def atr(df: pd.DataFrame, period: int) -> pd.Series:
    prev_close = df["close"].shift()
    tr = pd.concat(
        [df["high"] - df["low"], (df["high"] - prev_close).abs(), (df["low"] - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False).mean()


def generate_signal(df: pd.DataFrame, cfg: dict, position: str | None) -> Signal:
    """df: Tageskerzen (open/high/low/close), älteste zuerst.
    position: None (keine Position), "long" oder "short"."""
    need = max(cfg["slow_sma"], cfg["trend_sma"]) + 5
    if len(df) < need:
        return Signal("hold", float(df["close"].iloc[-1]) if len(df) else 0.0, reason="zu wenig Daten")

    close = df["close"]
    fast = close.rolling(cfg["fast_sma"]).mean()
    slow = close.rolling(cfg["slow_sma"]).mean()
    trend = close.rolling(cfg["trend_sma"]).mean()
    r = rsi(close, cfg["rsi_period"]).iloc[-1]
    a = atr(df, cfg["atr_period"]).iloc[-1]
    price = float(close.iloc[-1])

    if position == "long":
        if fast.iloc[-1] < slow.iloc[-1]:
            return Signal("close", price, reason="Long: SMA-Trend nach unten gedreht")
        return Signal("hold", price, reason="Long: Trend intakt")
    if position == "short":
        if fast.iloc[-1] > slow.iloc[-1]:
            return Signal("close", price, reason="Short: SMA-Trend nach oben gedreht")
        return Signal("hold", price, reason="Short: Abwärtstrend intakt")

    up = fast.iloc[-1] > slow.iloc[-1] and price > trend.iloc[-1]
    crossed_up = fast.iloc[-2] <= slow.iloc[-2] and fast.iloc[-1] > slow.iloc[-1]
    if up and (crossed_up or (price > fast.iloc[-1] and fast.iloc[-1] > fast.iloc[-5])) and r < cfg["rsi_max_entry"]:
        return Signal(
            "buy", price,
            stop_loss=round(price - cfg["stop_atr_mult"] * a, 4),
            take_profit=round(price + cfg["take_profit_atr_mult"] * a, 4),
            reason=f"Aufwärtstrend (SMA{cfg['fast_sma']}>SMA{cfg['slow_sma']}, Kurs>SMA{cfg['trend_sma']}), RSI {r:.0f}",
        )

    if cfg.get("allow_short", False):
        down = fast.iloc[-1] < slow.iloc[-1] and price < trend.iloc[-1]
        crossed_down = fast.iloc[-2] >= slow.iloc[-2] and fast.iloc[-1] < slow.iloc[-1]
        if down and (crossed_down or (price < fast.iloc[-1] and fast.iloc[-1] < fast.iloc[-5])) \
                and r > cfg["rsi_min_short"]:
            return Signal(
                "short", price,
                stop_loss=round(price + cfg["stop_atr_mult"] * a, 4),
                take_profit=round(price - cfg["take_profit_atr_mult"] * a, 4),
                reason=f"Abwärtstrend (SMA{cfg['fast_sma']}<SMA{cfg['slow_sma']}, Kurs<SMA{cfg['trend_sma']}), RSI {r:.0f}",
            )

    return Signal("hold", price, reason=f"kein Einstieg (RSI {r:.0f})")
