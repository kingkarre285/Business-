"""Einfacher Backtest der Strategie auf historischen Tageskursen."""
from . import data, risk
from .strategy import generate_signal


def backtest(cfg: dict, period: str = "5y", quiet: bool = False) -> float:
    rcfg = cfg["risk"]
    scfg = {**cfg["strategy"], "allow_short": rcfg["allow_short"]}
    fee_pct = cfg.get("backtest_overnight_fee_pct_per_year", 0)
    warmup = max(scfg["slow_sma"], scfg["trend_sma"]) + 5
    start = float(cfg["paper_start_balance"])
    total_pnl, total_trades, wins = 0.0, 0, 0
    if not quiet:
        print(f"{'Symbol':8s} {'Trades':>6s} {'Long':>5s} {'Short':>5s} {'Treffer':>8s} {'PnL USD':>10s}  Halten")
    for item in cfg["watchlist"]:
        df = data.daily_candles(item, days=int(period.rstrip("y")) * 365)
        equity, pos = start, None
        trades = hits = longs = shorts = 0
        lev = risk.leverage_for(item, rcfg)
        for i in range(warmup, len(df)):
            window = df.iloc[: i + 1]
            bar = window.iloc[-1]
            if pos:
                long = pos["side"] == "long"
                exit_price = None
                if (bar["low"] <= pos["sl"]) if long else (bar["high"] >= pos["sl"]):
                    exit_price = pos["sl"]
                elif (bar["high"] >= pos["tp"]) if long else (bar["low"] <= pos["tp"]):
                    exit_price = pos["tp"]
                elif generate_signal(window, scfg, pos["side"]).action == "close":
                    exit_price = float(bar["close"])
                pos["days"] += 1
                if exit_price is not None:
                    sign = 1 if long else -1
                    fees = pos["exposure"] * fee_pct / 100 * pos["days"] / 365 if lev > 1 or not long else 0
                    pnl = sign * (exit_price - pos["open"]) * pos["units"] - fees
                    equity += pnl
                    trades += 1
                    hits += pnl > 0
                    pos = None
                continue
            sig = generate_signal(window, scfg, None)
            if sig.action in ("buy", "short"):
                exposure, _ = risk.position_size(equity, sig.price, sig.stop_loss, rcfg, lev, item.get("min_usd", 0))
                if exposure > 0:
                    side = "long" if sig.action == "buy" else "short"
                    longs += side == "long"
                    shorts += side == "short"
                    pos = {"side": side, "units": exposure / sig.price, "open": sig.price, "exposure": exposure,
                           "sl": sig.stop_loss, "tp": sig.take_profit, "days": 0}
        if pos:
            sign = 1 if pos["side"] == "long" else -1
            equity += sign * (float(df["close"].iloc[-1]) - pos["open"]) * pos["units"]
        pnl = equity - start
        hold = (float(df["close"].iloc[-1]) / float(df["close"].iloc[warmup]) - 1) * 100
        total_pnl += pnl
        total_trades += trades
        wins += hits
        if not quiet:
            rate = f"{hits / trades * 100:.0f}%" if trades else "-"
            print(f"{item['symbol']:8s} {trades:6d} {longs:5d} {shorts:5d} {rate:>8s} {pnl:10.2f}  {hold:+.0f}%")
    if not quiet:
        rate = f"{wins / total_trades * 100:.0f}%" if total_trades else "-"
        n = len(cfg["watchlist"])
        print(f"{'GESAMT':8s} {total_trades:6d} {'':5s} {'':5s} {rate:>8s} {total_pnl:10.2f}  "
              f"(= {total_pnl / (start * n) * 100:+.1f} % auf {n} x {start:.0f} USD)")
        print("(jedes Instrument einzeln simuliert; Spreads/Transaktionsgebühren nicht enthalten)")
    return total_pnl
