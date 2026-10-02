"""Demo-Bot: handelt die Walk-Forward-Auswahl im eToro-DEMOKONTO.

Ablauf bei jedem Lauf (gedacht für einmal täglich):
1. Abgleich: Positionen des Bots, die eToro per Stop-Loss/Kursziel geschlossen
   hat, werden als geschlossen protokolliert.
2. Zeitlimit: Positionen, die länger als 30 Tage offen sind, werden geschlossen.
3. Auswahl: die besten Kombinationen aus Markt und Einstiegsregel der letzten
   Monate (wie in walkforward.py), einmal pro Monat festgelegt.
4. Einstieg: Gibt eine ausgewählte Kombination auf der letzten abgeschlossenen
   Tageskerze ein Signal und hat der Bot dort noch keine Position, wird eine
   Position mit Stop-Loss und Kursziel eröffnet.

Der Bot fasst nur Positionen an, die er selbst eröffnet hat (siehe state.json).
Pro Markt versucht er höchstens einmal am Tag einen Einstieg, so dass er auch
alle 15 Minuten laufen kann. Gespeichert und protokolliert wird nur, wenn sich
etwas geändert hat. Ohne --execute zeigt er nur an, was er tun würde.

Aufruf:
    python3 -m trading.bot              # Probelauf, keine Orders
    python3 -m trading.bot --execute    # Orders im Demokonto ausführen
"""

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import config as cfg
from . import etoro_client as api
from .analysis import STRATEGIES, _signals, backtest
from .walkforward import select

ROOT = Path(__file__).parent / "bot"
STATE = ROOT / "state.json"
LOG = ROOT / "log.md"

# Einstellungen der besten Walk-Forward-Variante.
TOP_N = 5
LOOKBACK_MONTHS = 6
RISK_PCT = 1.0
TARGET_PCT_OF_MARGIN = 10.0
STOP_PCT_OF_MARGIN = 5.0
LEVERAGE = 2
MAX_HOLD_DAYS = 30


def configure() -> None:
    cfg.HORIZON_HOURS = MAX_HOLD_DAYS * 24
    cfg.CANDLE_INTERVAL = "OneDay"
    cfg.BREAKOUT_LOOKBACK_HOURS = cfg.HORIZON_HOURS
    cfg.MIN_NET_PROFIT_PCT = TARGET_PCT_OF_MARGIN
    cfg.STOP_LOSS_PCT_OF_MARGIN = STOP_PCT_OF_MARGIN
    cfg.MAX_LEVERAGE = LEVERAGE


def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"selection": {}, "open": [], "closed": []}


def save_state(state: dict) -> None:
    ROOT.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2) + "\n")


def log(lines: list[str]) -> None:
    ROOT.mkdir(exist_ok=True)
    if not LOG.exists():
        LOG.write_text("# Demo-Bot Protokoll\n")
    with LOG.open("a") as f:
        f.write("\n" + "\n".join(lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true",
                    help="Orders wirklich im Demokonto ausführen")
    args = ap.parse_args()
    configure()

    now = datetime.now(timezone.utc)
    month = now.strftime("%Y-%m")
    mode = "AUSFÜHRUNG (Demokonto)" if args.execute else "PROBELAUF (keine Orders)"
    out = [f"## {now:%Y-%m-%d %H:%M} UTC · {mode}", ""]
    state = load_state()
    state.setdefault("attempts", {})
    before = json.dumps(state, sort_keys=True)
    today = now.strftime("%Y-%m-%d")
    # Alte Einstiegsversuche vergessen, nur heute zählt.
    state["attempts"] = {k: v for k, v in state["attempts"].items() if k.startswith(today)}

    portfolio = api.demo_portfolio()
    by_order = {p["orderID"]: p for p in portfolio["positions"]}
    by_position = {p["positionID"]: p for p in portfolio["positions"]}

    # 1. Abgleich mit dem Demokonto.
    still_open = []
    for pos in state["open"]:
        live = by_position.get(pos.get("positionID")) or by_order.get(pos["orderID"])
        if live:
            pos["positionID"] = live["positionID"]
            pos["openRate"] = live["openRate"]
            still_open.append(pos)
        elif pos.get("positionID") or now - datetime.fromisoformat(pos["opened"]) > timedelta(hours=1):
            out.append(f"- {pos['symbol']} ({pos['strategy']}): nicht mehr offen, "
                       "von eToro per Stop-Loss/Kursziel geschlossen oder Order abgelehnt")
            state["closed"].append({**pos, "closed": now.isoformat(), "reason": "eToro"})
        else:
            still_open.append(pos)  # Order gerade erst gesendet
    state["open"] = still_open

    # 2. Zeitlimit.
    for pos in list(state["open"]):
        age = now - datetime.fromisoformat(pos["opened"])
        if age > timedelta(days=MAX_HOLD_DAYS) and pos.get("positionID"):
            out.append(f"- {pos['symbol']}: {age.days} Tage offen → schließen")
            if args.execute:
                api.demo_close(pos["positionID"], pos["instrumentID"])
                state["open"].remove(pos)
                state["closed"].append({**pos, "closed": now.isoformat(), "reason": "Zeit"})

    # 3. Kurse laden, Auswahl für diesen Monat festlegen.
    candles = {s: api.get_candles(cfg.UNIVERSE[s][0], "OneDay", 1000) for s in cfg.UNIVERSE}
    # Die letzte Kerze ist der laufende Tag; für Signale nur abgeschlossene Kerzen.
    done = {s: c[:-1] for s, c in candles.items() if len(c) > 201}
    if month not in state["selection"]:
        trades = {(s, st): backtest(s, done[s], st).trades
                  for s in done for st in STRATEGIES}
        state["selection"][month] = [list(c) for c in select(trades, month, LOOKBACK_MONTHS, TOP_N)]
    selection = state["selection"][month]
    out.append(f"- Auswahl {month}: "
               + (", ".join(f"{s} / {st}" for s, st in selection) or "keine Kombination im Plus"))

    # 4. Signale prüfen und Positionen eröffnen.
    credit = portfolio["credit"]
    equity = credit + sum(p["amount"] for p in portfolio["positions"])
    amount = equity * RISK_PCT / STOP_PCT_OF_MARGIN
    held = {p["symbol"] for p in state["open"]}
    for symbol, strategy in selection:
        if symbol in held or symbol not in done:
            continue
        if f"{today}:{symbol}" in state["attempts"]:
            continue  # heute schon versucht (eröffnet, abgelehnt oder ausgestoppt)
        _, signal = _signals(done[symbol], strategy)
        d = signal(len(done[symbol]) - 1)
        if d == 0:
            out.append(f"- {symbol} / {strategy}: kein Signal")
            continue
        price = candles[symbol][-1]["close"]
        lev = cfg.leverage_for(symbol)
        tp = price * (1 + d * cfg.required_move_pct(symbol) / 100)
        sl = price * (1 - d * cfg.stop_move_pct(symbol) / 100)
        side = "Long" if d == 1 else "Short"
        if amount > credit:
            out.append(f"- {symbol} / {strategy}: {side}-Signal, aber zu wenig Guthaben")
            continue
        out.append(f"- {symbol} / {strategy}: **{side}** {amount:.2f} $ × {lev}x "
                   f"bei ~{price:g}, Stop {sl:.5g}, Ziel {tp:.5g}")
        if args.execute:
            state["attempts"][f"{today}:{symbol}"] = strategy
            try:
                res = api.demo_open_by_amount(cfg.UNIVERSE[symbol][0], d == 1, amount,
                                              lev, round(sl, 5), round(tp, 5))
            except Exception as e:  # Order abgelehnt: protokollieren, weitermachen
                out.append(f"  - Fehler: {e}")
                continue
            order = res["orderForOpen"]
            state["open"].append({
                "symbol": symbol, "strategy": strategy, "instrumentID": order["instrumentID"],
                "orderID": order["orderID"], "isBuy": d == 1, "amount": amount,
                "leverage": lev, "stopLoss": sl, "takeProfit": tp, "opened": now.isoformat(),
            })
            held.add(symbol)
            credit -= amount
            out.append(f"  - Order gesendet, orderID {order['orderID']}")

    out.append(f"- Konto: {equity:.2f} $ (Guthaben {credit:.2f} $), "
               f"offene Bot-Positionen: {len(state['open'])}")
    print("\n".join(out))
    if args.execute and json.dumps(state, sort_keys=True) != before:
        save_state(state)
        log(out)


if __name__ == "__main__":
    main()
