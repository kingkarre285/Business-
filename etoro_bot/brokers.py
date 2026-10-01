"""Broker-Abstraktion: Papier-Simulation oder echtes eToro-Konto (Demo/Live).

Positionen werden einheitlich als {symbol: {"side": "long"|"short", "exposure": ...}} geliefert.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from .etoro_client import EtoroClient


def _pnl(pos: dict, price: float) -> float:
    sign = 1 if pos["side"] == "long" else -1
    return sign * (price - pos["open_rate"]) * pos["units"]


class PaperBroker:
    """Simuliert Trades lokal mit echten Kursen. Zustand in state/paper_state.json."""

    tag = "PAPIER"

    def __init__(self, state_file: Path, start_balance: float):
        self.state_file = state_file
        if state_file.exists():
            self.state = json.loads(state_file.read_text())
        else:
            self.state = {"cash": start_balance, "positions": {}, "closed": [], "next_id": 1}
        self.prices: dict[str, float] = {}

    def save(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self.state, indent=2))

    def update_price(self, symbol: str, price: float):
        self.prices[symbol] = price

    def check_stops(self, symbol: str, low: float, high: float, log) -> None:
        """Stop-Loss / Take-Profit anhand der letzten Tageskerze auslösen."""
        pos = self.state["positions"].get(symbol)
        if not pos:
            return
        long = pos["side"] == "long"
        sl_hit = pos.get("stop_loss") and (low <= pos["stop_loss"] if long else high >= pos["stop_loss"])
        tp_hit = pos.get("take_profit") and (high >= pos["take_profit"] if long else low <= pos["take_profit"])
        if sl_hit:
            self._close(symbol, pos["stop_loss"], "Stop-Loss", log)
        elif tp_hit:
            self._close(symbol, pos["take_profit"], "Take-Profit", log)

    def positions(self, watchlist) -> dict[str, dict]:
        return self.state["positions"]

    def equity(self) -> float:
        value = self.state["cash"]
        for sym, p in self.state["positions"].items():
            value += p["margin"] + _pnl(p, self.prices.get(sym, p["open_rate"]))
        return value

    def open(self, item: dict, side: str, exposure: float, margin: float, leverage: int,
             price: float, sl, tp, log):
        if margin > self.state["cash"]:
            log(f"  -> übersprungen: zu wenig freies Kapital")
            return
        self.state["cash"] -= margin
        self.state["positions"][item["symbol"]] = {
            "id": self.state["next_id"], "side": side, "open_rate": price, "units": exposure / price,
            "exposure": exposure, "margin": margin, "leverage": leverage,
            "stop_loss": sl, "take_profit": tp, "opened": datetime.now(timezone.utc).isoformat(),
        }
        self.state["next_id"] += 1
        log(f"[PAPIER] {'KAUF' if side == 'long' else 'SHORT'} {item['symbol']} Einsatz {margin:.2f} USD "
            f"x{leverage} = {exposure:.2f} USD @ {price:.2f} (SL {sl}, TP {tp})")

    def close(self, item: dict, position: dict, price: float, reason: str, log):
        self._close(item["symbol"], price, reason, log)

    def _close(self, symbol: str, price: float, reason: str, log):
        pos = self.state["positions"].pop(symbol)
        pnl = _pnl(pos, price)
        self.state["cash"] += pos["margin"] + pnl
        self.state["closed"].append({**pos, "symbol": symbol, "close_rate": price, "pnl": pnl,
                                     "reason": reason, "closed": datetime.now(timezone.utc).isoformat()})
        log(f"[PAPIER] SCHLIESSEN {pos['side'].upper()} {symbol} @ {price:.2f} ({reason}) PnL {pnl:+.2f} USD")


class EtoroBroker:
    """Handelt über die eToro-API. demo=True -> virtuelles Konto, sonst Echtgeld."""

    def __init__(self, demo: bool):
        self.client = EtoroClient(demo=demo)
        self.tag = "DEMO" if demo else "LIVE"
        self._ids: dict[str, int] = {}

    def instrument_id(self, item: dict) -> int:
        if item.get("instrument_id"):
            return int(item["instrument_id"])
        if item["symbol"] not in self._ids:
            self._ids[item["symbol"]] = self.client.resolve_instrument_id(item["symbol"])
        return self._ids[item["symbol"]]

    def save(self):
        pass

    def update_price(self, symbol, price):
        pass

    def check_stops(self, symbol, low, high, log):
        pass  # Stop-Loss / Take-Profit werden direkt bei eToro verwaltet

    def positions(self, watchlist) -> dict[str, dict]:
        """Nur Positionen auf Watchlist-Instrumenten (kopierte Trader etc. bleiben unberührt)."""
        by_id = {self.instrument_id(it): it["symbol"] for it in watchlist}
        out = {}
        for p in self.client.positions():
            sym = by_id.get(p["instrument_id"])
            if sym:
                out[sym] = {**p, "side": "long" if p["is_buy"] else "short",
                            "exposure": p["amount"] * p.get("leverage", 1)}
        return out

    def equity(self) -> float:
        return self.client.equity()

    def open(self, item: dict, side: str, exposure: float, margin: float, leverage: int,
             price: float, sl, tp, log):
        res = self.client.open_position(self.instrument_id(item), side, margin, leverage, sl, tp)
        log(f"[{self.tag}] {'KAUF' if side == 'long' else 'SHORT'} {item['symbol']} Einsatz {margin:.2f} USD "
            f"x{leverage} (SL {sl}, TP {tp}) -> {res}")

    def close(self, item: dict, position: dict, price: float, reason: str, log):
        res = self.client.close(position["position_id"])
        log(f"[{self.tag}] SCHLIESSEN {item['symbol']} ({reason}) -> {res}")
