"""Minimaler Lesezugriff auf die eToro Public API (nur Kursdaten, keine Trades).

Authentifizierung: Sind ETORO_API_KEY und ETORO_USER_KEY gesetzt, werden sie als
x-api-key / x-user-key mitgeschickt. In der Claude-Code-Cloud-Umgebung ergänzt
der Proxy die Zugangsdaten automatisch.
"""

import json
import os
import time
import urllib.error
import urllib.request
import uuid

BASE_URL = "https://public-api.etoro.com"
# Geteiltes Limit: 120 Anfragen pro 60 Sekunden.
_MIN_INTERVAL_S = 0.6
_last_call = 0.0


def _get(path: str) -> dict:
    return _request("GET", path)


def _post(path: str, body: dict) -> dict:
    return _request("POST", path, body)


def _request(method: str, path: str, body: dict | None = None) -> dict:
    global _last_call
    wait = _MIN_INTERVAL_S - (time.monotonic() - _last_call)
    if wait > 0:
        time.sleep(wait)

    headers = {"x-request-id": str(uuid.uuid4()), "Accept": "application/json",
               "User-Agent": "business-backtest/1.0"}
    if os.environ.get("ETORO_API_KEY") and os.environ.get("ETORO_USER_KEY"):
        headers["x-api-key"] = os.environ["ETORO_API_KEY"]
        headers["x-user-key"] = os.environ["ETORO_USER_KEY"]

    for attempt in range(3):
        _last_call = time.monotonic()
        data = json.dumps(body).encode() if body is not None else None
        if data is not None:
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(BASE_URL + path, data=data, headers=headers,
                                     method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(int(e.headers.get("Retry-After", "60")))
                continue
            raise
    raise RuntimeError("unreachable")


def get_candles(instrument_id: int, interval: str = "OneHour", count: int = 1000) -> list[dict]:
    """Kerzen von alt nach neu: [{time, open, high, low, close}, ...]."""
    data = _get(f"/api/v1/market-data/instruments/{instrument_id}"
                f"/history/candles/asc/{interval}/{count}")
    raw = data["candles"][0]["candles"] if data.get("candles") else []
    return [
        {"time": c["fromDate"], "open": c["open"], "high": c["high"],
         "low": c["low"], "close": c["close"]}
        for c in raw
    ]


_HISTORY_INTERVALS = {"FifteenMinutes": "15m", "OneHour": "1h", "FourHours": "4h", "OneDay": "1d"}


def get_history(instrument_id: int, interval: str, start: str, end: str) -> list[dict]:
    """Komplette Kurshistorie zwischen start und end (ISO-Zeitpunkte, UTC),
    von alt nach neu. Nutzt die Daten-Schnittstelle mit Blättern (max. 2000 je Seite)."""
    from urllib.parse import urlencode
    params = {"interval": _HISTORY_INTERVALS[interval], "from": start, "to": end, "limit": 2000}
    rows = []
    while True:
        page = _get(f"/api/v1/data/instruments/{instrument_id}/candles?" + urlencode(params))
        rows += page["results"]
        if not page["pagination"]["hasNext"]:
            break
        params["cursor"] = page["pagination"]["nextCursor"]
    candles = [
        {"time": r["time"].replace("+00:00", "Z"), "open": float(r["open"]),
         "high": float(r["high"]), "low": float(r["low"]), "close": float(r["close"])}
        for r in rows if None not in (r["open"], r["high"], r["low"], r["close"])
    ]
    candles.sort(key=lambda c: c["time"])
    return candles


# --- Demokonto (nur Demo-Adressen, kein Echtgeld) ---------------------------

def demo_portfolio() -> dict:
    return _get("/api/v1/trading/info/demo/portfolio")["clientPortfolio"]


def demo_open_by_amount(instrument_id: int, is_buy: bool, amount: float, leverage: int,
                        stop_loss: float, take_profit: float) -> dict:
    return _post("/api/v1/trading/execution/demo/market-open-orders/by-amount", {
        "InstrumentID": instrument_id, "IsBuy": is_buy, "Leverage": leverage,
        "Amount": round(amount, 2), "StopLossRate": stop_loss,
        "TakeProfitRate": take_profit, "IsTslEnabled": False,
    })


def demo_close(position_id: int, instrument_id: int) -> dict:
    return _post(f"/api/v1/trading/execution/demo/market-close-orders/positions/{position_id}",
                 {"InstrumentID": instrument_id})
