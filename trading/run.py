"""Scanner + Backtest ausführen und Bericht schreiben.

Aufruf (im Repository-Hauptordner):
    python3 -m trading.run                     # 24 h, Stundenkerzen
    python3 -m trading.run --horizon 168 --interval FourHours   # 1 Woche
    python3 -m trading.run --horizon 720 --interval OneDay      # 1 Monat
    python3 -m trading.run --cached            # gespeicherte Kurse verwenden
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from . import config as cfg
from .analysis import backtest, period_multipliers, scan
from .etoro_client import get_candles

ROOT = Path(__file__).parent
CACHE = ROOT / "data"
RESULTS = ROOT / "results"


def load_candles(symbol: str, use_cache: bool) -> list[dict]:
    path = CACHE / f"{symbol}_{cfg.CANDLE_INTERVAL}_{cfg.CANDLE_COUNT}.json"
    if use_cache and path.exists():
        return json.loads(path.read_text())
    candles = get_candles(cfg.UNIVERSE[symbol][0], cfg.CANDLE_INTERVAL, cfg.CANDLE_COUNT)
    CACHE.mkdir(exist_ok=True)
    path.write_text(json.dumps(candles))
    return candles


def pct(x: float) -> str:
    return f"{x * 100:+.1f} %"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizon", type=int, default=cfg.HORIZON_HOURS,
                    help="Zeitfenster pro Trade in Stunden (168 = 1 Woche)")
    ap.add_argument("--interval", default=cfg.CANDLE_INTERVAL, choices=cfg.INTERVAL_HOURS)
    ap.add_argument("--target", type=float, default=cfg.MIN_NET_PROFIT_PCT,
                    help="Mindest-Nettogewinn pro Trade in %%")
    ap.add_argument("--stop", type=float, default=cfg.STOP_LOSS_PCT_OF_MARGIN,
                    help="Stop-Loss in %% des Einsatzes")
    ap.add_argument("--max-leverage", type=int, default=None,
                    help="Hebel begrenzen (1 = ohne Hebel)")
    ap.add_argument("--risk", type=float, default=None,
                    help="Risiko pro Trade in %% des Kontos (bestimmt den Einsatz)")
    ap.add_argument("--cached", action="store_true")
    args = ap.parse_args()
    cfg.HORIZON_HOURS = args.horizon
    cfg.CANDLE_INTERVAL = args.interval
    cfg.MIN_NET_PROFIT_PCT = args.target
    cfg.STOP_LOSS_PCT_OF_MARGIN = args.stop
    cfg.MAX_LEVERAGE = args.max_leverage
    if args.risk is not None:
        cfg.STAKE_PCT_OF_EQUITY = min(100.0, args.risk / args.stop * 100)
    # Breakout über das Hoch/Tief eines Zeitraums so lang wie das Zeitfenster.
    cfg.BREAKOUT_LOOKBACK_HOURS = args.horizon

    rows, all_trades, total_start, total_end = [], [], 0.0, 0.0
    weeks = []
    # Auswertung je Woche, ab Zeitfenstern von einem Monat je Monat.
    period_days = 30 if args.horizon >= 720 else 7
    period_name, period_plural = ("Monat", "Monate") if period_days == 30 else ("Woche", "Kalenderwochen")

    for symbol in cfg.UNIVERSE:
        candles = load_candles(symbol, args.cached)
        if len(candles) < cfg.BREAKOUT_LOOKBACK_HOURS // cfg.INTERVAL_HOURS[args.interval] + 2:
            print(f"{symbol}: zu wenig Kursdaten, übersprungen")
            continue
        s = scan(symbol, candles)
        bt = backtest(symbol, candles)
        all_trades += bt.trades
        total_start += cfg.START_CAPITAL
        total_end += bt.final_equity
        weeks += period_multipliers(bt, candles, period_days)
        rows.append((symbol, candles, s, bt))
        print(f"{symbol:8} Bewegung nötig {cfg.required_move_pct(symbol):6.2f} % | "
              f"möglich (perfekte Vorhersage) {s['hit_rate']*100:5.1f} % | "
              f"Trades {len(bt.trades):3} Ziel {bt.wins:3} | "
              f"{cfg.START_CAPITAL:.0f} -> {bt.final_equity:9.2f}")

    first = min(r[1][0]["time"] for r in rows)[:10]
    last = max(r[1][-1]["time"] for r in rows)[:10]
    wins = sum(t.outcome == "Ziel" for t in all_trades)
    ruined = sum(r[3].ruined for r in rows)

    lines = [
        "# Backtest: mindestens "
        f"{cfg.MIN_NET_PROFIT_PCT:.0f} % netto pro Trade",
        "",
        f"Erstellt: {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC · "
        f"Kursdaten: eToro, {cfg.CANDLE_INTERVAL}-Kerzen, {first} bis {last}",
        "",
        "## Regeln",
        "",
        f"- Ziel: +{cfg.MIN_NET_PROFIT_PCT:.0f} % auf den Einsatz **nach Kosten**, "
        f"innerhalb von {cfg.HORIZON_HOURS} Stunden",
        f"- Stop-Loss: −{cfg.STOP_LOSS_PCT_OF_MARGIN:.0f} % des Einsatzes; "
        f"Einsatz pro Trade: {cfg.STAKE_PCT_OF_EQUITY:.0f} % des Kontos",
        ("- Hebel: jeweils der für Privatkunden maximal erlaubte (ESMA)"
         if not cfg.MAX_LEVERAGE else
         f"- Hebel: höchstens {cfg.MAX_LEVERAGE}x" + (" (ohne Hebel)" if cfg.MAX_LEVERAGE == 1 else "")),
        f"- Risiko pro Trade: {cfg.STAKE_PCT_OF_EQUITY * cfg.STOP_LOSS_PCT_OF_MARGIN / 100:.1f} % "
        "des Kontos (Einsatz × Stop-Loss)",
        f"- Einstieg: Breakout über das Hoch / unter das Tief der letzten "
        f"{cfg.BREAKOUT_LOOKBACK_HOURS} Stunden",
        f"- Startkapital je Markt: {cfg.START_CAPITAL:.0f} $",
        "",
        "## Ergebnis gesamt",
        "",
        f"- Trades: **{len(all_trades)}**, davon Ziel erreicht: **{wins}** "
        f"({wins / len(all_trades) * 100 if all_trades else 0:.1f} %)",
        f"- Kapital gesamt: {total_start:.0f} $ → **{total_end:.2f} $** "
        f"({pct(total_end / total_start - 1)})",
        f"- Märkte mit Totalverlust (< 1 % übrig): **{ruined} von {len(rows)}**",
        f"- {period_plural} à {period_days} Tage (alle Märkte zusammen): **{len(weeks)}**, davon Konto "
        f"verdoppelt: **{sum(w >= 2 for w in weeks)}**, im Plus: "
        f"{sum(w > 1 for w in weeks)}, im Minus: {sum(w < 1 for w in weeks)}",
        f"- Beste(r) {period_name}: {pct(max(weeks) - 1) if weeks else '–'}, "
        f"schlechteste(r) {period_name}: {pct(min(weeks) - 1) if weeks else '–'}",
        "",
        "## Je Markt",
        "",
        "| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* "
        "| Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for symbol, _, s, bt in rows:
        stops = sum(t.outcome == "Stop" for t in bt.trades)
        timeouts = sum(t.outcome == "Zeit" for t in bt.trades)
        lines.append(
            f"| {symbol} | {cfg.leverage_for(symbol)}x | {cfg.required_move_pct(symbol):.2f} % "
            f"| {f'−{cfg.stop_move_pct(symbol):.2f} %' if cfg.stop_move_pct(symbol) > 0 else 'Kosten > Stop'} "
            f"| {s['hit_rate'] * 100:.1f} % "
            f"| {len(bt.trades)} | {bt.wins} | {stops} | {timeouts} "
            f"| {bt.final_equity:.2f} $ | {bt.max_drawdown * 100:.0f} % |"
        )
    lines += [
        "",
        "\\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von "
        f"{cfg.HORIZON_HOURS} h weit genug bewegt hat, **mit perfekter Vorhersage "
        "der Richtung** und ohne Rücksicht auf den Stop. Das ist die "
        "theoretische Obergrenze, die keine Strategie erreicht.",
        "",
        "Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene "
        "Ergebnisse sind keine Garantie für die Zukunft.",
    ]

    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / f"report_{cfg.HORIZON_HOURS}h_{cfg.MIN_NET_PROFIT_PCT:g}pct.md"
    out.write_text("\n".join(lines) + "\n")
    print(f"\nBericht: {out}")


if __name__ == "__main__":
    main()
