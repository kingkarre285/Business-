"""CLI:
    python -m etoro_bot run              # ein Handelsdurchlauf
    python -m etoro_bot status           # Papier-Konto anzeigen
    python -m etoro_bot backtest [5y]    # Strategie historisch testen
    python -m etoro_bot find "Gold"      # eToro-Instrument-ID suchen (API-Keys nötig)
"""
import json
import sys

from .bot import STATE, load_config, run_once


def main(argv: list[str]) -> None:
    cmd = argv[0] if argv else "run"
    cfg = load_config()
    if cmd == "run":
        run_once(cfg)
    elif cmd == "backtest":
        from .backtest import backtest
        backtest(cfg, argv[1] if len(argv) > 1 else "5y")
    elif cmd == "status":
        f = STATE / "paper_state.json"
        if not f.exists():
            print("Noch kein Papier-Konto – erst 'run' ausführen.")
            return
        s = json.loads(f.read_text())
        print(f"Cash: {s['cash']:.2f} USD")
        for sym, p in s["positions"].items():
            print(f"  {sym:8s} {p['amount']:.2f} USD @ {p['open_rate']:.2f}  SL {p['stop_loss']}  TP {p['take_profit']}")
        pnl = sum(t["pnl"] for t in s["closed"])
        print(f"Geschlossene Trades: {len(s['closed'])}, realisierter PnL {pnl:+.2f} USD")
    elif cmd == "find":
        from .etoro_client import EtoroClient
        demo = cfg["mode"] != "live"
        for r in EtoroClient(demo=demo).search(" ".join(argv[1:]))[:15]:
            print(r)
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
