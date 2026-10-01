"""Trendfolge-Strategie: SMA-Kreuzung mit Trendfilter, RSI-Filter und ATR-Stops."""
from dataclasses import dataclass

import pandas as pd


@dataclass
class Signal:
    action: str          # "buy", "sell" (Position schließen) oder "hold"
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


def generate_signal(df: pd.DataFrame, cfg: dict, has_position: bool) -> Signal:
    """df: Tageskerzen mit Spalten open/high/low/close, älteste zuerst."""
    need = max(cfg["slow_sma"], cfg["trend_sma"]) + 2
    if len(df) < need:
        return Signal("hold", float(df["close"].iloc[-1]) if len(df) else 0.0, reason="zu wenig Daten")

    close = df["close"]
    fast = close.rolling(cfg["fast_sma"]).mean()
    slow = close.rolling(cfg["slow_sma"]).mean()
    trend = close.rolling(cfg["trend_sma"]).mean()
    r = rsi(close, cfg["rsi_period"]).iloc[-1]
    a = atr(df, cfg["atr_period"]).iloc[-1]
    price = float(close.iloc[-1])

    uptrend = fast.iloc[-1] > slow.iloc[-1] and price > trend.iloc[-1]

    if has_position:
        if fast.iloc[-1] < slow.iloc[-1]:
            return Signal("sell", price, reason="schnelle SMA unter langsamer SMA – Trend gebrochen")
        return Signal("hold", price, reason="Trend intakt")

    crossed_up = fast.iloc[-2] <= slow.iloc[-2] and fast.iloc[-1] > slow.iloc[-1]
    fresh_trend = uptrend and (crossed_up or (close.iloc[-1] > fast.iloc[-1] and fast.iloc[-1] > fast.iloc[-5]))
    if fresh_trend and r < cfg["rsi_max_entry"]:
        return Signal(
            "buy",
            price,
            stop_loss=round(price - cfg["stop_atr_mult"] * a, 4),
            take_profit=round(price + cfg["take_profit_atr_mult"] * a, 4),
            reason=f"Aufwärtstrend (SMA{cfg['fast_sma']}>SMA{cfg['slow_sma']}, Kurs>SMA{cfg['trend_sma']}), RSI {r:.0f}",
        )
    return Signal("hold", price, reason=f"kein Einstieg (Trend={'ja' if uptrend else 'nein'}, RSI {r:.0f})")
