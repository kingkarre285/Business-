"""Historische Kerzen: bevorzugt von eToro (exakt die gehandelten CFD-Kurse),
ohne API-Schlüssel ersatzweise von Yahoo Finance."""
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

import pandas as pd

# Yahoo liefert Intraday-Daten nur begrenzt weit zurück
YAHOO_MAX_DAYS = {"1m": 7, "5m": 60, "15m": 60, "30m": 60, "1h": 730}


_etoro_ok: bool | None = None


def has_etoro_keys() -> bool:
    """True, wenn eToro-Daten abrufbar sind: Schlüssel als Umgebungsvariablen
    oder von einem Proxy angehängt (wird einmal per Testabruf geprüft)."""
    global _etoro_ok
    if _etoro_ok is None:
        if os.environ.get("ETORO_API_KEY") and os.environ.get("ETORO_USER_KEY"):
            _etoro_ok = True
        else:
            from .etoro_client import EtoroClient
            try:
                EtoroClient(demo=True)._request("GET", "/api/v1/data/instruments/27/candles/coverage")
                _etoro_ok = True
            except Exception:
                _etoro_ok = False
    return _etoro_ok


def candles(item: dict, interval: str = "1d", days: int = 730) -> pd.DataFrame:
    """item: Watchlist-Eintrag (instrument_id, yahoo). Gibt open/high/low/close, älteste zuerst."""
    if has_etoro_keys() and item.get("instrument_id"):
        return etoro_candles(int(item["instrument_id"]), interval, days)
    days = min(days, YAHOO_MAX_DAYS.get(interval, days))
    period = f"{max(1, round(days / 365))}y" if days >= 365 else f"{days}d"
    return yahoo_candles(item["yahoo"], interval, period)


CACHE = Path(__file__).resolve().parent.parent / ".cache"


def etoro_candles(instrument_id: int, interval: str, days: int) -> pd.DataFrame:
    """Lädt Kerzen von eToro; Intraday-Daten werden in .cache/ zwischengespeichert
    und nur um neue Kerzen ergänzt."""
    from .etoro_client import EtoroClient
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days)
    cache = CACHE / f"{instrument_id}_{interval}.pkl"
    df = pd.read_pickle(cache) if cache.exists() else pd.DataFrame(columns=["open", "high", "low", "close"])
    client = EtoroClient(demo=True)
    parts = [df]
    if df.empty or df.index[0] > start + timedelta(days=1):
        older_end = df.index[0].to_pydatetime() if not df.empty else now
        parts.append(_to_frame(client.candles(instrument_id, interval, start.isoformat(), older_end.isoformat())))
    if not df.empty:
        parts.append(_to_frame(client.candles(instrument_id, interval, df.index[-1].isoformat(), now.isoformat())))
    df = pd.concat([p for p in parts if not p.empty])
    df = df[~df.index.duplicated(keep="last")].sort_index()
    if interval != "1d" and not df.empty:
        CACHE.mkdir(exist_ok=True)
        df.to_pickle(cache)
    return df[df.index >= start]


def _to_frame(rows: list[dict]) -> pd.DataFrame:
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
