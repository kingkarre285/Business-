"""Walk-Forward-Test: Markt und Strategie jeden Monat neu wählen.

Am Anfang jedes Monats werden alle Kombinationen aus Markt und Einstiegsregel
nach ihrem Ergebnis der letzten LOOKBACK_MONTHS Monate bewertet. Die besten
TOP_N (nur solche im Plus) werden im folgenden Monat gehandelt. Die Auswahl
kennt also nie die Zukunft, so wie im echten Handel.

Zum Vergleich: dieselbe Auswahl "mit Rückblick", also die Kombinationen, die
über den GESAMTEN Zeitraum am besten waren. Das ist im echten Handel unmöglich.

Aufruf:
    python3 -m trading.walkforward --cached
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from . import config as cfg
from .analysis import STRATEGIES, backtest
from .run import RESULTS, load_candles


def month_key(iso: str) -> str:
    return iso[:7]


def add_months(key: str, n: int) -> str:
    y, m = map(int, key.split("-"))
    m += n
    y, m = y + (m - 1) // 12, (m - 1) % 12 + 1
    return f"{y:04d}-{m:02d}"


def select(trades_by_combo, month: str, lookback: int, top: int) -> list:
    """Die `top` Kombinationen mit der besten Summe der Netto-Renditen aus den
    `lookback` Monaten vor `month` (nur im Plus, mindestens 3 Trades)."""
    window_start = add_months(month, -lookback)
    scores = {}
    for combo, trades in trades_by_combo.items():
        past = [t.net_return for t in trades
                if window_start <= month_key(t.exit_time) < month]
        if len(past) >= 3:
            scores[combo] = sum(past)
    best = sorted((c for c in scores if scores[c] > 0), key=scores.get, reverse=True)
    return best[:top]


def simulate(trades_by_combo, selection_by_month, stake):
    """Konto über alle Trades, deren Einstiegsmonat die Kombination ausgewählt hat."""
    picked = [
        t for combo, trades in trades_by_combo.items() for t in trades
        if combo in selection_by_month.get(month_key(t.entry_time), ())
    ]
    picked.sort(key=lambda t: t.exit_time)
    equity, peak, mdd = cfg.START_CAPITAL, cfg.START_CAPITAL, 0.0
    monthly: dict[str, float] = {}
    for t in picked:
        before = equity
        equity *= 1 + stake * t.net_return
        m = month_key(t.exit_time)
        monthly[m] = monthly.get(m, 1.0) * equity / before
        peak, mdd = max(peak, equity), max(mdd, 1 - equity / peak)
    return equity, mdd, monthly, picked


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=3, help="Anzahl Kombinationen pro Monat")
    ap.add_argument("--lookback", type=int, default=12, help="Bewertungszeitraum in Monaten")
    ap.add_argument("--risk", type=float, default=1.5, help="Risiko pro Trade in %% des Kontos")
    ap.add_argument("--target", type=float, default=10.0)
    ap.add_argument("--stop", type=float, default=5.0)
    ap.add_argument("--max-leverage", type=int, default=2)
    ap.add_argument("--cached", action="store_true")
    args = ap.parse_args()

    cfg.HORIZON_HOURS = 720
    cfg.CANDLE_INTERVAL = "OneDay"
    cfg.BREAKOUT_LOOKBACK_HOURS = 720
    cfg.MIN_NET_PROFIT_PCT = args.target
    cfg.STOP_LOSS_PCT_OF_MARGIN = args.stop
    cfg.MAX_LEVERAGE = args.max_leverage
    stake = args.risk / args.stop  # Anteil des Kontos pro Trade

    trades_by_combo = {}
    for symbol in cfg.UNIVERSE:
        candles = load_candles(symbol, args.cached)
        for strategy in STRATEGIES:
            trades_by_combo[(symbol, strategy)] = backtest(symbol, candles, strategy).trades

    all_months = sorted({month_key(t.entry_time)
                         for ts in trades_by_combo.values() for t in ts})
    first_trade_month = all_months[0]
    start = add_months(first_trade_month, args.lookback)
    months = [m for m in all_months if m >= start]

    # Walk-Forward: Auswahl nur mit Wissen aus der Vergangenheit.
    selection, picks_log = {}, []
    for m in months:
        best = select(trades_by_combo, m, args.lookback, args.top)
        selection[m] = set(best)
        picks_log.append((m, best))

    wf_equity, wf_mdd, wf_monthly, wf_trades = simulate(trades_by_combo, selection, stake)

    # Rückblick: die über den gesamten Testzeitraum besten Kombinationen.
    total = {c: sum(t.net_return for t in ts if month_key(t.entry_time) >= start)
             for c, ts in trades_by_combo.items()}
    hindsight = sorted(total, key=total.get, reverse=True)[:args.top]
    hs_equity, hs_mdd, hs_monthly, hs_trades = simulate(
        trades_by_combo, {m: set(hindsight) for m in months}, stake)

    def summary(name, equity, mdd, monthly, trades):
        vals = list(monthly.values())
        wins = sum(t.outcome == "Ziel" for t in trades)
        return (f"| {name} | {len(trades)} | {wins / len(trades) * 100 if trades else 0:.0f} % "
                f"| {equity:.2f} $ ({(equity / cfg.START_CAPITAL - 1) * 100:+.1f} %) "
                f"| {sum(v > 1 for v in vals)} / {sum(v < 1 for v in vals)} "
                f"| {(max(vals) - 1) * 100 if vals else 0:+.1f} % "
                f"| {(min(vals) - 1) * 100 if vals else 0:+.1f} % | {mdd * 100:.0f} % |")

    lines = [
        "# Walk-Forward-Test: Markt und Strategie monatlich frei wählen",
        "",
        f"Erstellt: {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC · "
        f"Kursdaten: eToro, Tageskerzen · gehandelt: {months[0]} bis {months[-1]}",
        "",
        "## Regeln",
        "",
        f"- Auswahl: jeden Monat die {args.top} besten Kombinationen aus "
        f"{len(cfg.UNIVERSE)} Märkten × {len(STRATEGIES)} Einstiegsregeln "
        f"({', '.join(STRATEGIES)}), bewertet über die letzten {args.lookback} Monate; "
        "nur Kombinationen im Plus und mit mindestens 3 Trades",
        "- Long und Short erlaubt",
        f"- Ziel +{args.target:g} % / Stop −{args.stop:g} % auf den Einsatz, Hebel "
        f"höchstens {args.max_leverage}x, Zeitfenster 30 Tage",
        f"- Risiko pro Trade: {args.risk:g} % des Kontos (Einsatz {stake * 100:.0f} %)",
        f"- Startkapital: {cfg.START_CAPITAL:.0f} $",
        "",
        "## Ergebnis",
        "",
        "| Auswahl | Trades | Ziel erreicht | Endkapital | Monate Plus / Minus "
        "| bester Monat | schlechtester Monat | max. Rückgang |",
        "|---|---|---|---|---|---|---|---|",
        summary("**Walk-Forward (realistisch)**", wf_equity, wf_mdd, wf_monthly, wf_trades),
        summary("Rückblick (unmöglich)", hs_equity, hs_mdd, hs_monthly, hs_trades),
        "",
        f"Rückblick-Auswahl: {', '.join(f'{s} / {st}' for s, st in hindsight)}",
        "",
        "## Monatliche Auswahl (Walk-Forward)",
        "",
        "| Monat | gewählt | Konto im Monat |",
        "|---|---|---|",
    ]
    for m, best in picks_log:
        chosen = ", ".join(f"{s} / {st}" for s, st in best) or "– (nichts im Plus)"
        change = f"{(wf_monthly[m] - 1) * 100:+.1f} %" if m in wf_monthly else "0 %"
        lines.append(f"| {m} | {chosen} | {change} |")
    lines += [
        "",
        "Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene "
        "Ergebnisse sind keine Garantie für die Zukunft.",
    ]

    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / f"walkforward_top{args.top}_risk{args.risk:g}_lb{args.lookback}.md"
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines[13:17]))
    print(f"\nBericht: {out}")


if __name__ == "__main__":
    main()
