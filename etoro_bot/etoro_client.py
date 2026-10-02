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
        # Ohne Umgebungsvariablen werden die Schlüssel ggf. von einem Proxy angehängt
        # (z. B. "API credentials" in der Claude-Cloud-Umgebung).
        self.session = requests.Session()

    # -- HTTP ---------------------------------------------------------------
    def _request(self, method: str, path: str, **kwargs):
        headers = {"x-request-id": str(uuid.uuid4()), "Content-Type": "application/json"}
        if self.api_key and self.user_key:
            headers["x-api-key"] = self.api_key
            headers["x-user-key"] = self.user_key
        for attempt in range(4):
            resp = self.session.request(method, BASE + path, headers=headers, timeout=30, **kwargs)
            if resp.status_code == 429:
                time.sleep(float(resp.headers.get("Retry-After", 2 ** attempt * 5)))
                continue
            if resp.status_code in (502, 503, 504) and method == "GET":
                time.sleep(2 ** attempt * 5)  # vorübergehend nicht verfügbar, Lesen ist wiederholbar
                continue
            if resp.status_code >= 400:
                raise EtoroError(f"{method} {path} -> {resp.status_code}: {resp.text[:500]}")
            return resp.json() if resp.content else {}
        raise EtoroError(f"{method} {path}: nach mehreren Versuchen nicht erreichbar (Rate-Limit/503)")

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

    # Max. Zeitspanne pro Abruf laut eToro: 10.080 Perioden; wir bleiben darunter
    _CANDLE_MINUTES = {"1m": 1, "5m": 5, "10m": 10, "15m": 15, "30m": 30, "1h": 60, "4h": 240, "1d": 1440, "1w": 10080}

    def candles(self, instrument_id: int, interval: str, start: str | None = None,
                end: str | None = None) -> list[dict]:
        """OHLC-Kerzen (Bid) aus eToros Datenplattform, älteste zuerst.
        interval: 1m, 5m, 10m, 15m, 30m, 1h, 4h, 1d, 1w. start/end: ISO 8601 mit Zeitzone.
        Lange Zeiträume werden in Abschnitte zerlegt, jeder Abschnitt seitenweise geladen."""
        from datetime import datetime, timedelta, timezone
        t_end = datetime.fromisoformat(end) if end else datetime.now(timezone.utc)
        t_start = datetime.fromisoformat(start) if start else t_end - timedelta(days=30)
        span = timedelta(minutes=self._CANDLE_MINUTES[interval] * 9000)
        out: dict[str, dict] = {}
        w_end = t_end
        while w_end > t_start:
            w_start = max(t_start, w_end - span)
            base = {"interval": interval, "limit": 2000,
                    "from": w_start.isoformat(), "to": w_end.isoformat()}
            params = dict(base)
            while True:
                page = self._request("GET", f"/api/v1/data/instruments/{instrument_id}/candles", params=params)
                for c in page.get("results", []):
                    out[c["time"]] = c
                nxt = (page.get("pagination") or {}).get("nextCursor")
                if not nxt:
                    break
                params = {**base, "cursor": nxt}
            w_end = w_start
        return [out[k] for k in sorted(out)]

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
                "leverage": int(_first(p, "leverage", default=1)),
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
    def open_position(self, instrument_id: int, side: str, amount_usd: float, leverage: int = 1,
                      stop_loss: float | None = None, take_profit: float | None = None) -> dict:
        """side: "long" oder "short". amount_usd = eingesetztes Kapital (Margin)."""
        path = "/api/v2/trading/execution/demo/orders" if self.demo else "/api/v2/trading/execution/orders"
        body = {
            "action": "open",
            "transaction": "buy" if side == "long" else "sellShort",
            "instrumentId": instrument_id,
            "orderType": "mkt",
            "amount": round(amount_usd, 2),
            "orderCurrency": "usd",
            "leverage": leverage,
        }
        if stop_loss:
            body["stopLossRate"] = stop_loss
        if take_profit:
            body["takeProfitRate"] = take_profit
        return self._request("POST", path, json=body)

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
