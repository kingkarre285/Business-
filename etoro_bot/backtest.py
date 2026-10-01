"""Einfacher Backtest der Strategie auf historischen Tageskursen."""
from . import data, risk
from .strategy import generate_signal


def backtest(cfg: dict, period: str = "5y") -> None:
    scfg, rcfg = cfg["strategy"], cfg["risk"]
    warmup = max(scfg["slow_sma"], scfg["trend_sma"]) + 2
    total_pnl, total_trades, wins = 0.0, 0, 0
    print(f"{'Symbol':8s} {'Trades':>6s} {'Treffer':>8s} {'PnL USD':>10s}")
    for item in cfg["watchlist"]:
        df = data.daily_candles(item["yahoo"], period=period)
        equity = float(cfg["paper_start_balance"])
        pos, trades, hits = None, 0, 0
        for i in range(warmup, len(df)):
            window = df.iloc[: i + 1]
            bar = window.iloc[-1]
            if pos:
                exit_price = None
                if bar["low"] <= pos["sl"]:
                    exit_price = pos["sl"]
                elif bar["high"] >= pos["tp"]:
                    exit_price = pos["tp"]
                else:
                    sig = generate_signal(window, scfg, has_position=True)
                    if sig.action == "sell":
                        exit_price = sig.price
                if exit_price is not None:
                    pnl = pos["units"] * exit_price - pos["amount"]
                    equity += pnl
                    trades += 1
                    hits += pnl > 0
                    pos = None
                continue
            sig = generate_signal(window, scfg, has_position=False)
            if sig.action == "buy":
                amount = risk.position_size_usd(equity, sig.price, sig.stop_loss, rcfg)
                if amount > 0:
                    pos = {"units": amount / sig.price, "amount": amount, "sl": sig.stop_loss, "tp": sig.take_profit}
        if pos:
            equity += pos["units"] * float(df["close"].iloc[-1]) - pos["amount"]
        pnl = equity - cfg["paper_start_balance"]
        total_pnl += pnl
        total_trades += trades
        wins += hits
        rate = f"{hits / trades * 100:.0f}%" if trades else "-"
        print(f"{item['symbol']:8s} {trades:6d} {rate:>8s} {pnl:10.2f}")
    rate = f"{wins / total_trades * 100:.0f}%" if total_trades else "-"
    print(f"{'GESAMT':8s} {total_trades:6d} {rate:>8s} {total_pnl:10.2f}")
    print("(jedes Instrument einzeln mit Startkapital simuliert; ohne Gebühren/Spreads)")
