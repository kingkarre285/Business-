"""Broker-Abstraktion: Papier-Simulation oder echtes eToro-Konto (Demo/Live)."""
import json
from datetime import datetime, timezone
from pathlib import Path

from .etoro_client import EtoroClient


class PaperBroker:
    """Simuliert Trades lokal mit echten Kursen. Zustand in state/paper_state.json."""

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
        if pos.get("stop_loss") and low <= pos["stop_loss"]:
            self._close(symbol, pos["stop_loss"], "Stop-Loss", log)
        elif pos.get("take_profit") and high >= pos["take_profit"]:
            self._close(symbol, pos["take_profit"], "Take-Profit", log)

    def positions(self) -> dict[str, dict]:
        return self.state["positions"]

    def equity(self) -> float:
        value = self.state["cash"]
        for sym, p in self.state["positions"].items():
            value += p["units"] * self.prices.get(sym, p["open_rate"])
        return value

    def open_long(self, item: dict, amount: float, price: float, sl, tp, log):
        amount = min(amount, self.state["cash"])
        if amount <= 0:
            return
        self.state["cash"] -= amount
        self.state["positions"][item["symbol"]] = {
            "id": self.state["next_id"], "open_rate": price, "units": amount / price,
            "amount": amount, "stop_loss": sl, "take_profit": tp,
            "opened": datetime.now(timezone.utc).isoformat(),
        }
        self.state["next_id"] += 1
        log(f"[PAPIER] KAUF {item['symbol']} {amount:.2f} USD @ {price:.2f} (SL {sl}, TP {tp})")

    def close(self, symbol: str, price: float, reason: str, log):
        self._close(symbol, price, reason, log)

    def _close(self, symbol: str, price: float, reason: str, log):
        pos = self.state["positions"].pop(symbol)
        proceeds = pos["units"] * price
        self.state["cash"] += proceeds
        pnl = proceeds - pos["amount"]
        self.state["closed"].append({**pos, "symbol": symbol, "close_rate": price, "pnl": pnl,
                                     "reason": reason, "closed": datetime.now(timezone.utc).isoformat()})
        log(f"[PAPIER] VERKAUF {symbol} @ {price:.2f} ({reason}) PnL {pnl:+.2f} USD")


class EtoroBroker:
    """Handelt über die eToro-API. demo=True -> virtuelles Konto, sonst Echtgeld."""

    def __init__(self, demo: bool, leverage: int):
        self.client = EtoroClient(demo=demo)
        self.leverage = leverage
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

    def positions_by_instrument(self) -> dict[int, dict]:
        return {p["instrument_id"]: p for p in self.client.positions() if p["is_buy"]}

    def equity(self) -> float:
        return self.client.equity()

    def open_long(self, item: dict, amount: float, price: float, sl, tp, log):
        res = self.client.open_long(self.instrument_id(item), amount, self.leverage, sl, tp)
        log(f"[{self.tag}] KAUF {item['symbol']} {amount:.2f} USD (SL {sl}, TP {tp}) -> {res}")

    def close_position(self, item: dict, position: dict, reason: str, log):
        res = self.client.close(position["position_id"])
        log(f"[{self.tag}] VERKAUF {item['symbol']} ({reason}) -> {res}")
