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
        return EtoroBroker(demo=True, leverage=cfg["risk"]["leverage"])
    if mode == "live":
        if os.environ.get("ETORO_ALLOW_LIVE") != "yes":
            raise SystemExit("Live-Modus gesperrt: ETORO_ALLOW_LIVE=yes setzen, um mit echtem Geld zu handeln.")
        return EtoroBroker(demo=False, leverage=cfg["risk"]["leverage"])
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
    log = make_logger()
    broker = make_broker(cfg)
    paper = isinstance(broker, PaperBroker)
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
    halted = risk.daily_loss_exceeded(start, equity, cfg["risk"])
    log(f"Kapital: {equity:.2f} USD (Tagesstart {start:.2f})" + (" – TAGESVERLUST-STOPP AKTIV" if halted else ""))

    held = broker.positions() if paper else broker.positions_by_instrument()

    # 2) Signale auswerten
    for item in cfg["watchlist"]:
        df = candles.get(item["symbol"])
        if df is None:
            continue
        if paper:
            position = held.get(item["symbol"])
        else:
            position = held.get(broker.instrument_id(item))
        sig = generate_signal(df, cfg["strategy"], has_position=position is not None)
        log(f"{item['symbol']:8s} {sig.price:>10.2f}  {sig.action.upper():4s}  {sig.reason}")

        if sig.action == "sell" and position:
            if paper:
                broker.close(item["symbol"], sig.price, sig.reason, log)
            else:
                broker.close_position(item, position, sig.reason, log)
        elif sig.action == "buy" and not position:
            if halted:
                log(f"  -> übersprungen: Tagesverlust-Stopp")
                continue
            if len(held) >= cfg["risk"]["max_open_positions"]:
                log(f"  -> übersprungen: max. {cfg['risk']['max_open_positions']} Positionen offen")
                continue
            amount = risk.position_size_usd(equity, sig.price, sig.stop_loss, cfg["risk"])
            if amount <= 0:
                log("  -> übersprungen: Positionsgröße unter Mindestbetrag")
                continue
            broker.open_long(item, amount, sig.price, sig.stop_loss, sig.take_profit, log)
            held = broker.positions() if paper else {**held, broker.instrument_id(item): {}}

    broker.save()
    log(f"=== Lauf beendet. Kapital: {broker.equity():.2f} USD ===")
