"""Schlanker Client für die öffentliche eToro-API (https://public-api.etoro.com).

Schlüssel erstellen: eToro -> Settings -> Trading -> API Key Management.
Für Demo und Echtgeld gibt es getrennte User Keys.

Hinweis: eToro dokumentiert nicht alle Antwortformate. Die Auswertung der
Antworten ist daher bewusst tolerant (mehrere mögliche Feldnamen).
"""
import os
import time
import uuid

import requests

BASE = "https://public-api.etoro.com"


class EtoroError(RuntimeError):
    pass


class EtoroClient:
    def __init__(self, demo: bool, api_key: str | None = None, user_key: str | None = None):
        self.demo = demo
        self.api_key = api_key or os.environ.get("ETORO_API_KEY")
        self.user_key = user_key or os.environ.get("ETORO_USER_KEY")
        if not self.api_key or not self.user_key:
            raise EtoroError("ETORO_API_KEY und ETORO_USER_KEY müssen gesetzt sein.")
        self.session = requests.Session()

    # -- HTTP ---------------------------------------------------------------
    def _request(self, method: str, path: str, **kwargs):
        headers = {
            "x-api-key": self.api_key,
            "x-user-key": self.user_key,
            "x-request-id": str(uuid.uuid4()),
            "Content-Type": "application/json",
        }
        for attempt in range(4):
            resp = self.session.request(method, BASE + path, headers=headers, timeout=30, **kwargs)
            if resp.status_code == 429:
                time.sleep(float(resp.headers.get("Retry-After", 2 ** attempt * 5)))
                continue
            if resp.status_code >= 400:
                raise EtoroError(f"{method} {path} -> {resp.status_code}: {resp.text[:500]}")
            return resp.json() if resp.content else {}
        raise EtoroError(f"{method} {path}: Rate-Limit nach mehreren Versuchen")

    # -- Marktdaten ---------------------------------------------------------
    def search(self, query: str) -> list[dict]:
        data = self._request("GET", "/api/v1/market-data/search", params={"query": query})
        return data.get("results") or data.get("items") or data.get("data") or []

    def resolve_instrument_id(self, symbol: str) -> int:
        for item in self.search(symbol):
            sym = str(_first(item, "symbol", "symbolFull", "ticker", default="")).upper()
            if sym == symbol.upper():
                return int(_first(item, "instrumentId", "instrumentID", "id"))
        raise EtoroError(f"Instrument '{symbol}' nicht gefunden – instrument_id in config.yaml eintragen.")

    # -- Konto --------------------------------------------------------------
    def portfolio(self) -> dict:
        path = "/api/v1/trading/info/demo/portfolio" if self.demo else "/api/v1/trading/info/portfolio"
        data = self._request("GET", path)
        if isinstance(data, list):
            return {"positions": data}
        return data.get("clientPortfolio", data)

    def positions(self) -> list[dict]:
        out = []
        for p in self.portfolio().get("positions", []) or []:
            out.append({
                "position_id": _first(p, "positionId", "positionID"),
                "instrument_id": int(_first(p, "instrumentId", "instrumentID", default=0)),
                "is_buy": bool(_first(p, "isBuy", default=True)),
                "open_rate": float(_first(p, "openRate", default=0)),
                "amount": float(_first(p, "investedAmount", "amount", default=0)),
            })
        return out

    def equity(self) -> float:
        path = "/api/v1/trading/info/demo/pnl" if self.demo else "/api/v1/trading/info/real/pnl"
        data = self._request("GET", path)
        data = data.get("clientPortfolio", data)
        value = _first(data, "equity", "totalBalance", "credit", default=None)
        if value is None:
            raise EtoroError(f"Kontostand nicht lesbar: {list(data)[:10]}")
        return float(value)

    # -- Orders -------------------------------------------------------------
    def open_long(self, instrument_id: int, amount_usd: float, leverage: int = 1,
                  stop_loss: float | None = None, take_profit: float | None = None) -> dict:
        path = "/api/v2/trading/execution/demo/orders" if self.demo else "/api/v2/trading/execution/orders"
        body = {
            "action": "open",
            "transaction": "buy",
            "instrumentId": instrument_id,
            "orderType": "mkt",
            "amount": amount_usd,
            "orderCurrency": "usd",
            "leverage": leverage,
            "stopLossType": "fixed",
        }
        result = self._request("POST", path, json=body)
        position_id = _first(result, "positionId", "positionID", default=None)
        if position_id and (stop_loss or take_profit):
            self.set_stops(position_id, stop_loss, take_profit)
        return result

    def set_stops(self, position_id, stop_loss: float | None, take_profit: float | None) -> dict:
        path = (f"/api/v2/trading/demo/positions/{position_id}" if self.demo
                else f"/api/v2/trading/positions/{position_id}")
        body = {"stopLossType": "fixed"}
        if stop_loss:
            body["stopLossRate"] = stop_loss
        if take_profit:
            body["takeProfitRate"] = take_profit
        return self._request("PATCH", path, json=body)

    def close(self, position_id) -> dict:
        env = "trading/execution/demo" if self.demo else "trading/execution"
        return self._request("POST", f"/api/v1/{env}/market-close-orders/positions/{position_id}", json={})


def _first(d: dict, *keys, default=KeyError):
    for k in keys:
        if isinstance(d, dict) and d.get(k) is not None:
            return d[k]
    if default is KeyError:
        raise EtoroError(f"Feld fehlt: {keys}")
    return default
