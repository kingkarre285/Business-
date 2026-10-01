"""Historische Kerzen: bevorzugt von eToro (exakt die gehandelten CFD-Kurse),
ohne API-Schlüssel ersatzweise von Yahoo Finance."""
import os
from datetime import datetime, timedelta, timezone

import pandas as pd

# Yahoo liefert Intraday-Daten nur begrenzt weit zurück
YAHOO_MAX_DAYS = {"1m": 7, "5m": 60, "15m": 60, "30m": 60, "1h": 730}


def has_etoro_keys() -> bool:
    return bool(os.environ.get("ETORO_API_KEY") and os.environ.get("ETORO_USER_KEY"))


def candles(item: dict, interval: str = "1d", days: int = 730) -> pd.DataFrame:
    """item: Watchlist-Eintrag (instrument_id, yahoo). Gibt open/high/low/close, älteste zuerst."""
    if has_etoro_keys() and item.get("instrument_id"):
        return etoro_candles(int(item["instrument_id"]), interval, days)
    days = min(days, YAHOO_MAX_DAYS.get(interval, days))
    period = f"{max(1, round(days / 365))}y" if days >= 365 else f"{days}d"
    return yahoo_candles(item["yahoo"], interval, period)


def etoro_candles(instrument_id: int, interval: str, days: int) -> pd.DataFrame:
    from .etoro_client import EtoroClient
    start = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    rows = EtoroClient(demo=True).candles(instrument_id, interval, start=start)
    if not rows:
        return pd.DataFrame(columns=["open", "high", "low", "close"])
    df = pd.DataFrame(rows)
    df.index = pd.to_datetime(df["time"], utc=True)
    return df[["open", "high", "low", "close"]].astype(float).dropna()


def yahoo_candles(ticker: str, interval: str = "1d", period: str = "2y") -> pd.DataFrame:
    import yfinance as yf
    df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
    if df.empty:
        return pd.DataFrame(columns=["open", "high", "low", "close"])
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.rename(columns=str.lower)[["open", "high", "low", "close"]].dropna()


def daily_candles(item: dict, days: int = 730) -> pd.DataFrame:
    return candles(item, "1d", days)
