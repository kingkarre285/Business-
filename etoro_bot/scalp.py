"""Intraday-/Scalping-Backtest auf 5-Minuten-Kerzen (Yahoo liefert max. 60 Tage).

Zwei Strategien:
  pullback – mit dem Trend (EMA 50) handeln, Einstieg nach kurzem Rücksetzer (RSI 7),
             Long und Short, Stop 1,5 x ATR, Ziel 2 x ATR, max. 1 Stunde Haltedauer
  orb      – Opening-Range-Breakout: Ausbruch aus der Spanne der ersten 30 Minuten
             (nur Indizes), Stop an der Gegenseite der Spanne, Ziel 2 x Risiko

Kosten: eToro-Spread je Instrument (gemessen, x2 Sicherheitsaufschlag) wird pro
Round-Trip abgezogen. Alle Positionen werden vor Handelsschluss geschlossen
(keine Übernachtgebühren).
"""
import numpy as np
import pandas as pd
import yfinance as yf

from .strategy import atr, rsi

# (Yahoo-Ticker, eToro-Spread in % des Kurses (gemessen 01.10.2026), max. eToro-Hebel, nur Kernhandelszeit)
MARKETS = {
    "SPX500": ("^GSPC", 0.0039, 20, True),
    "NSDQ100": ("^NDX", 0.0046, 20, True),
    "GER40": ("^GDAXI", 0.0088, 20, True),
    "GOLD": ("GC=F", 0.0048, 10, False),
    "OIL": ("CL=F", 0.0217, 10, False),
}

RISK_PCT = 0.5          # Risiko pro Trade in % des Kapitals
MAX_EXPOSURE_X = 5.0    # max. Marktwert pro Trade = 5 x Kapital
SPREAD_SAFETY = 2.0


def load(ticker: str, interval: str = "5m") -> pd.DataFrame:
    df = yf.download(ticker, period="60d", interval=interval, progress=False, auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df.rename(columns=str.lower)[["open", "high", "low", "close"]].dropna()


def pullback_signals(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    c = df["close"]
    ema9, ema21, ema50 = (c.ewm(span=n, adjust=False).mean() for n in (9, 21, 50))
    r = rsi(c, 7)
    a = atr(df, 14)
    long_ = (c > ema50) & (ema9 > ema21) & (r.shift() < 35) & (r >= 35)
    short = (c < ema50) & (ema9 < ema21) & (r.shift() > 65) & (r <= 65)
    out["side"] = np.where(long_, 1, np.where(short, -1, 0))
    out["stop_dist"] = 1.5 * a
    out["target_dist"] = 2.0 * a
    out["max_bars"] = 12
    return out


def orb_signals(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index, data={"side": 0, "stop_dist": np.nan, "target_dist": np.nan, "max_bars": 999})
    for _, day in df.groupby(df.index.date):
        if len(day) < 10:
            continue
        rng = day.iloc[:6]                      # erste 30 Minuten
        hi, lo = rng["high"].max(), rng["low"].min()
        width = hi - lo
        for ts, bar in day.iloc[6:].iterrows():
            if bar["close"] > hi:
                out.loc[ts, ["side", "stop_dist", "target_dist"]] = [1, bar["close"] - lo, 2 * (bar["close"] - lo)]
                break
            if bar["close"] < lo:
                out.loc[ts, ["side", "stop_dist", "target_dist"]] = [-1, hi - bar["close"], 2 * (hi - bar["close"])]
                break
        _ = width
    return out


def simulate(df: pd.DataFrame, sig: pd.DataFrame, spread_pct: float, max_lev: int,
             start: float = 10000.0) -> dict:
    equity, peak, max_dd = start, start, 0.0
    trades, wins = 0, 0
    pos = None
    dates = df.index.date
    cost_pct = spread_pct / 100 * SPREAD_SAFETY
    for i in range(len(df)):
        bar = df.iloc[i]
        last_of_day = i == len(df) - 1 or dates[i + 1] != dates[i]
        if pos:
            exit_price = None
            if pos["side"] == 1:
                if bar["low"] <= pos["sl"]:
                    exit_price = pos["sl"]
                elif bar["high"] >= pos["tp"]:
                    exit_price = pos["tp"]
            else:
                if bar["high"] >= pos["sl"]:
                    exit_price = pos["sl"]
                elif bar["low"] <= pos["tp"]:
                    exit_price = pos["tp"]
            pos["bars"] += 1
            if exit_price is None and (pos["bars"] >= pos["max_bars"] or last_of_day):
                exit_price = bar["close"]
            if exit_price is not None:
                pnl = pos["side"] * (exit_price - pos["entry"]) / pos["entry"] * pos["exposure"]
                pnl -= pos["exposure"] * cost_pct
                equity += pnl
                trades += 1
                wins += pnl > 0
                peak = max(peak, equity)
                max_dd = max(max_dd, (peak - equity) / peak)
                pos = None
            continue
        s = sig.iloc[i]
        if s["side"] != 0 and not last_of_day and s["stop_dist"] > 0:
            entry = bar["close"]
            stop_pct = s["stop_dist"] / entry
            exposure = min(equity * RISK_PCT / 100 / stop_pct, equity * MAX_EXPOSURE_X, equity * max_lev)
            pos = {"side": int(s["side"]), "entry": entry, "exposure": exposure, "bars": 0,
                   "max_bars": s["max_bars"],
                   "sl": entry - s["side"] * s["stop_dist"], "tp": entry + s["side"] * s["target_dist"]}
    return {"trades": trades, "winrate": wins / trades * 100 if trades else 0,
            "return_pct": (equity / start - 1) * 100, "max_dd_pct": max_dd * 100}


def scalp_backtest(spread_safety: float | None = None) -> None:
    global SPREAD_SAFETY
    if spread_safety is not None:
        SPREAD_SAFETY = spread_safety
    print(f"5-Minuten-Backtest, letzte ~60 Handelstage, Risiko {RISK_PCT} %/Trade, "
          f"Spread x{SPREAD_SAFETY}, Startkapital je Markt 10.000 USD\n")
    print(f"{'Markt':8s} {'Strategie':9s} {'Trades':>6s} {'Treffer':>8s} {'Rendite':>8s} {'max. DD':>8s}")
    for name, (ticker, spread, lev, rth_only) in MARKETS.items():
        df = load(ticker)
        if df.empty:
            print(f"{name:8s} keine Daten")
            continue
        strategies = {"pullback": pullback_signals(df)}
        if rth_only:
            strategies["orb"] = orb_signals(df)
        for sname, sig in strategies.items():
            r = simulate(df, sig, spread, lev)
            print(f"{name:8s} {sname:9s} {r['trades']:6d} {r['winrate']:7.0f}% {r['return_pct']:+7.1f}% "
                  f"{r['max_dd_pct']:7.1f}%")
