"""Historische Tageskerzen (Yahoo Finance) für die Signalberechnung."""
import pandas as pd
import yfinance as yf


def daily_candles(yahoo_ticker: str, period: str = "2y") -> pd.DataFrame:
    df = yf.download(yahoo_ticker, period=period, interval="1d", progress=False, auto_adjust=True)
    if df.empty:
        return pd.DataFrame(columns=["open", "high", "low", "close"])
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=str.lower)[["open", "high", "low", "close"]].dropna()
    return df
