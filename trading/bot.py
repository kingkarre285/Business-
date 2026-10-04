"""Demo-Bot: handelt die Walk-Forward-Auswahl im eToro-DEMOKONTO.

Er führt mehrere Profile nebeneinander (siehe PROFILES), jedes mit eigenem
virtuellen Budget, eigenem Hebel und Risiko, eigener Auswahl und eigener
Abrechnung. So lassen sich Varianten unter echten Marktbedingungen vergleichen.

Ablauf je Profil bei jedem Lauf (gedacht für einmal täglich):
1. Abgleich: Positionen, die eToro per Stop-Loss/Kursziel geschlossen hat,
   werden mit ihrem realisierten Gewinn/Verlust verbucht.
2. Zeitlimit: Positionen, die länger als 30 Tage offen sind, werden geschlossen.
3. Auswahl: die besten Kombinationen aus Markt und Einstiegsregel der letzten
   Monate (wie in walkforward.py), einmal pro Monat festgelegt.
4. Einstieg: Gibt eine ausgewählte Kombination auf der letzten abgeschlossenen
   Tageskerze ein Signal und hat das Profil dort noch keine Position, wird eine
   Position mit Stop-Loss und Kursziel eröffnet.

Der Bot fasst nur Positionen an, die er selbst eröffnet hat (siehe state.json).
Pro Profil und Markt versucht er höchstens einmal am Tag einen Einstieg.
Gespeichert und protokolliert wird nur, wenn sich etwas geändert hat.
Ohne --execute zeigt er nur an, was er tun würde.

Aufruf:
    python3 -m trading.bot              # Probelauf, keine Orders
    python3 -m trading.bot --execute    # Orders im Demokonto ausführen
    python3 -m trading.bot --status     # Zwischenstand je Profil
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

TOP_N = 5
LOOKBACK_MONTHS = 6
MAX_HOLD_DAYS = 30

# Virtuelles Budget je Profil (zusammen 79.000 $ = Demo-Guthaben beim Start).
PROFILES = {
    "A": {"name": "Standard", "capital": 54000.0, "leverage": 2,
          "target": 10.0, "stop": 5.0, "risk": 1.0},
    "B": {"name": "Offensiv", "capital": 25000.0, "leverage": 5,
          "target": 25.0, "stop": 12.5, "risk": 2.0},
}


def configure(p: dict) -> None:
    cfg.HORIZON_HOURS = MAX_HOLD_DAYS * 24
    cfg.CANDLE_INTERVAL = "OneDay"
    cfg.BREAKOUT_LOOKBACK_HOURS = cfg.HORIZON_HOURS
    cfg.MIN_NET_PROFIT_PCT = p["target"]
    cfg.STOP_LOSS_PCT_OF_MARGIN = p["stop"]
    cfg.MAX_LEVERAGE = p["leverage"]


def load_state() -> dict:
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    if "profiles" not in state:
        # Alter Zustand (ein Profil) gehört zu Profil A.
        state = {"profiles": {"A": state} if state else {}}
    for pid in PROFILES:
        prof = state["profiles"].setdefault(pid, {})
        for key, default in (("selection", {}), ("open", []), ("closed", []),
                             ("attempts", {}), ("realized", 0.0)):
            prof.setdefault(key, default)
    return state


def save_state(state: dict) -> None:
    ROOT.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2) + "\n")


def log(lines: list[str]) -> None:
    ROOT.mkdir(exist_ok=True)
    if not LOG.exists():
        LOG.write_text("# Demo-Bot Protokoll\n")
    with LOG.open("a") as f:
        f.write("\n" + "\n".join(lines) + "\n")


def closed_trades(since: str) -> dict:
    """Geschlossene Demo-Trades seit `since` (YYYY-MM-DD), nach positionID."""
    rows = api._get(f"/api/v1/trading/info/trade/demo/history?minDate={since}&pageSize=500")
    return {r["positionId"]: r for r in rows}


def run_profile(pid: str, prof: dict, portfolio: dict, history: dict, candles: dict,
                now: datetime, execute: bool, credit: float) -> tuple[list[str], float]:
    p = PROFILES[pid]
    configure(p)
    out = [f"### Profil {pid} · {p['name']} (Hebel bis {p['leverage']}x, "
           f"Ziel +{p['target']:g} % / Stop −{p['stop']:g} %, Risiko {p['risk']:g} %)"]
    today = now.strftime("%Y-%m-%d")
    month = now.strftime("%Y-%m")
    prof["attempts"] = {k: v for k, v in prof["attempts"].items() if k.startswith(today)}
    by_order = {x["orderID"]: x for x in portfolio["positions"]}
    by_position = {x["positionID"]: x for x in portfolio["positions"]}

    # 1. Abgleich mit dem Demokonto.
    still_open = []
    for pos in prof["open"]:
        live = by_position.get(pos.get("positionID")) or by_order.get(pos["orderID"])
        if live:
            pos["positionID"] = live["positionID"]
            pos["openRate"] = live["openRate"]
            still_open.append(pos)
        elif pos.get("positionID") or now - datetime.fromisoformat(pos["opened"]) > timedelta(hours=1):
            h = history.get(pos.get("positionID"))
            pnl = h["netProfit"] if h else 0.0
            prof["realized"] += pnl
            reason = "von eToro geschlossen (Stop/Ziel)" if h else "nicht gefunden (Order abgelehnt?)"
            out.append(f"- {pos['symbol']}: {reason}, Ergebnis {pnl:+.2f} $")
            prof["closed"].append({**pos, "closed": now.isoformat(), "reason": "eToro", "pnl": pnl})
        else:
            still_open.append(pos)  # Order gerade erst gesendet
    prof["open"] = still_open

    # 2. Zeitlimit.
    for pos in list(prof["open"]):
        age = now - datetime.fromisoformat(pos["opened"])
        if age > timedelta(days=MAX_HOLD_DAYS) and pos.get("positionID"):
            out.append(f"- {pos['symbol']}: {age.days} Tage offen → schließen")
            if execute:
                api.demo_close(pos["positionID"], pos["instrumentID"])
                # Ergebnis wird beim nächsten Lauf aus der Historie verbucht.

    # 3. Auswahl für diesen Monat (hängt von Hebel und Ziel des Profils ab).
    done = {s: c[:-1] for s, c in candles.items() if len(c) > 201}
    if month not in prof["selection"]:
        trades = {(s, st): backtest(s, done[s], st).trades for s in done for st in STRATEGIES}
        prof["selection"][month] = [list(c) for c in select(trades, month, LOOKBACK_MONTHS, TOP_N)]
    selection = prof["selection"][month]
    out.append(f"- Auswahl {month}: "
               + (", ".join(f"{s} / {st}" for s, st in selection) or "keine Kombination im Plus"))

    # 4. Signale prüfen und Positionen eröffnen.
    equity = p["capital"] + prof["realized"]
    used = sum(x["amount"] for x in prof["open"])
    amount = equity * p["risk"] / p["stop"]
    held = {x["symbol"] for x in prof["open"]}
    for symbol, strategy in selection:
        if symbol in held or symbol not in done or f"{today}:{symbol}" in prof["attempts"]:
            continue
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
        if used + amount > equity or amount > credit:
            out.append(f"- {symbol} / {strategy}: {side}-Signal, aber Budget ausgeschöpft")
            continue
        out.append(f"- {symbol} / {strategy}: **{side}** {amount:.2f} $ × {lev}x "
                   f"bei ~{price:g}, Stop {sl:.5g}, Ziel {tp:.5g}")
        if execute:
            prof["attempts"][f"{today}:{symbol}"] = strategy
            try:
                res = api.demo_open_by_amount(cfg.UNIVERSE[symbol][0], d == 1, amount,
                                              lev, round(sl, 5), round(tp, 5))
            except Exception as e:  # Order abgelehnt: protokollieren, weitermachen
                out.append(f"  - Fehler: {e}")
                continue
            order = res["orderForOpen"]
            prof["open"].append({
                "symbol": symbol, "strategy": strategy, "instrumentID": order["instrumentID"],
                "orderID": order["orderID"], "isBuy": d == 1, "amount": amount,
                "leverage": lev, "stopLoss": sl, "takeProfit": tp, "opened": now.isoformat(),
            })
            held.add(symbol)
            used += amount
            credit -= amount
            out.append(f"  - Order gesendet, orderID {order['orderID']}")

    out.append(f"- Budget {equity:.2f} $ (davon investiert {used:.2f} $), "
               f"offene Positionen: {len(prof['open'])}")
    return out, credit


def status(state: dict) -> None:
    pnl = api._get("/api/v1/trading/info/demo/pnl")["clientPortfolio"]["positions"]
    by_position = {x["positionID"]: x for x in pnl}
    by_order = {x["orderID"]: x for x in pnl}

    def find(x: dict) -> dict:
        return by_position.get(x.get("positionID")) or by_order.get(x["orderID"]) or {}

    for pid, p in PROFILES.items():
        prof = state["profiles"][pid]
        unreal = sum(find(x).get("unrealizedPnL", {}).get("pnL", 0.0) for x in prof["open"])
        total = prof["realized"] + unreal
        print(f"Profil {pid} · {p['name']}: Budget {p['capital']:.0f} $, "
              f"realisiert {prof['realized']:+.2f} $, offen {unreal:+.2f} $, "
              f"gesamt {total:+.2f} $ ({total / p['capital'] * 100:+.2f} %)")
        for x in prof["open"]:
            u = find(x).get("unrealizedPnL", {})
            print(f"  {x['symbol']:8} {'Long' if x['isBuy'] else 'Short'} {x['amount']:.0f} $ "
                  f"× {x['leverage']}x  aktuell {u.get('closeRate', '?')}  {u.get('pnL', 0):+.2f} $")
        print(f"  geschlossen: {len(prof['closed'])} Trades")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true",
                    help="Orders wirklich im Demokonto ausführen")
    ap.add_argument("--status", action="store_true", help="nur Zwischenstand anzeigen")
    args = ap.parse_args()

    state = load_state()
    if args.status:
        status(state)
        return

    now = datetime.now(timezone.utc)
    mode = "AUSFÜHRUNG (Demokonto)" if args.execute else "PROBELAUF (keine Orders)"
    before = json.dumps(state, sort_keys=True)

    portfolio = api.demo_portfolio()
    history = closed_trades((now - timedelta(days=60)).strftime("%Y-%m-%d"))
    candles = {s: api.get_candles(cfg.UNIVERSE[s][0], "OneDay", 1000) for s in cfg.UNIVERSE}
    credit = portfolio["credit"]

    out = [f"## {now:%Y-%m-%d %H:%M} UTC · {mode}", ""]
    for pid in PROFILES:
        lines, credit = run_profile(pid, state["profiles"][pid], portfolio, history,
                                    candles, now, args.execute, credit)
        out += lines + [""]
    out.append(f"Freies Demo-Guthaben: {credit:.2f} $")
    print("\n".join(out))
    if args.execute and json.dumps(state, sort_keys=True) != before:
        save_state(state)
        log(out)


if __name__ == "__main__":
    main()
