"""Ein Durchlauf des Bots: Kurse laden, Signale berechnen, Risiko prüfen, handeln."""
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

from . import data, risk
from .brokers import EtoroBroker, PaperBroker
from .strategy import generate_signal

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state"


def load_config(path: Path = ROOT / "config.yaml") -> dict:
    return yaml.safe_load(path.read_text())


def make_logger():
    STATE.mkdir(exist_ok=True)
    logfile = STATE / "trades.log"

    def log(msg: str):
        line = f"{datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S}Z {msg}"
        print(line)
        with logfile.open("a") as f:
            f.write(line + "\n")
    return log


def make_broker(cfg: dict):
    mode = cfg["mode"]
    if mode == "paper":
        return PaperBroker(STATE / "paper_state.json", cfg["paper_start_balance"])
    if mode == "demo":
        return EtoroBroker(demo=True)
    if mode == "live":
        if os.environ.get("ETORO_ALLOW_LIVE") != "yes":
            raise SystemExit("Live-Modus gesperrt: ETORO_ALLOW_LIVE=yes setzen, um mit echtem Geld zu handeln.")
        return EtoroBroker(demo=False)
    raise SystemExit(f"Unbekannter mode: {mode}")


def day_start_equity(equity: float) -> float:
    f = STATE / "daily.json"
    today = date.today().isoformat()
    d = json.loads(f.read_text()) if f.exists() else {}
    if d.get("date") != today:
        d = {"date": today, "equity": equity}
        f.write_text(json.dumps(d))
    return d["equity"]


def run_once(cfg: dict | None = None):
    cfg = cfg or load_config()
    rcfg = cfg["risk"]
    scfg = {**cfg["strategy"], "allow_short": rcfg["allow_short"]}
    log = make_logger()
    broker = make_broker(cfg)
    log(f"=== Lauf gestartet (Modus: {cfg['mode']}) ===")

    # 1) Kurse laden, Papier-Stops prüfen
    candles = {}
    for item in cfg["watchlist"]:
        df = data.daily_candles(item["yahoo"])
        if df.empty:
            log(f"{item['symbol']}: keine Kursdaten")
            continue
        candles[item["symbol"]] = df
        last = df.iloc[-1]
        broker.update_price(item["symbol"], float(last["close"]))
        broker.check_stops(item["symbol"], float(last["low"]), float(last["high"]), log)

    equity = broker.equity()
    start = day_start_equity(equity)
    halted = risk.daily_loss_exceeded(start, equity, rcfg)
    log(f"Kapital: {equity:.2f} USD (Tagesstart {start:.2f})" + (" – TAGESVERLUST-STOPP AKTIV" if halted else ""))

    held = broker.positions(cfg["watchlist"])
    total_exposure = sum(p.get("exposure", 0) for p in held.values())

    # 2) Signale auswerten
    for item in cfg["watchlist"]:
        df = candles.get(item["symbol"])
        if df is None:
            continue
        position = held.get(item["symbol"])
        sig = generate_signal(df, scfg, position["side"] if position else None)
        log(f"{item['symbol']:8s} {sig.price:>10.2f}  {sig.action.upper():5s}  {sig.reason}")

        if sig.action == "close" and position:
            broker.close(item, position, sig.price, sig.reason, log)
            held.pop(item["symbol"])
            total_exposure -= position.get("exposure", 0)
        elif sig.action in ("buy", "short") and not position:
            if halted:
                log("  -> übersprungen: Tagesverlust-Stopp")
                continue
            if len(held) >= rcfg["max_open_positions"]:
                log(f"  -> übersprungen: max. {rcfg['max_open_positions']} Positionen offen")
                continue
            lev = risk.leverage_for(item, rcfg)
            exposure, margin = risk.position_size(equity, sig.price, sig.stop_loss, rcfg, lev,
                                                  item.get("min_usd", 0))
            if exposure <= 0:
                log("  -> übersprungen: Positionsgröße unter Mindestbetrag")
                continue
            if total_exposure + exposure > equity * rcfg["max_total_exposure_pct"] / 100:
                log(f"  -> übersprungen: Gesamt-Exposure über {rcfg['max_total_exposure_pct']} % des Kapitals")
                continue
            side = "long" if sig.action == "buy" else "short"
            broker.open(item, side, exposure, margin, lev, sig.price, sig.stop_loss, sig.take_profit, log)
            held[item["symbol"]] = {"side": side, "exposure": exposure}
            total_exposure += exposure

    broker.save()
    log(f"=== Lauf beendet. Kapital: {broker.equity():.2f} USD ===")
