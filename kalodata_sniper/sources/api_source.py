"""Optionaler Live-Abruf mit der eigenen Kalodata-Session.

Kalodata bietet keine oeffentliche API. Dieser Client spricht die interne
Web-API mit *deinem eigenen* Session-Cookie an - also genau die Daten, die dir
im Browser ohnehin angezeigt werden. Damit gilt:

* Das Cookie kommt aus einer Umgebungsvariable, nie aus dem Repo.
* Endpunkt, Parameter und Feldnamen sind konfigurierbar, weil interne APIs sich
  ohne Ankuendigung aendern - bricht der Abruf, bleibt der CSV-Weg.
* Es wird bewusst langsam und seitenweise abgefragt (Rate-Limit), damit der
  Zugriff dem normalen Nutzungsverhalten entspricht.

Pruefe die Kalodata-Nutzungsbedingungen deines Tarifs, bevor du das aktivierst.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from ..models import Product
from .csv_source import load_products

DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,de;q=0.8",
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
}


class KalodataAPIError(RuntimeError):
    pass


class KalodataClient:
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config.get("base_url", "https://www.kalodata.com").rstrip("/")
        self.endpoint = config.get("endpoint", "/api/product/list")
        self.period = config.get("period", "7d")
        self.pages = int(config.get("pages", 3))
        self.page_size = int(config.get("page_size", 50))
        self.extra_params: Dict[str, Any] = config.get("extra_params") or {}
        self.delay = float(config.get("delay_seconds", 2.0))
        self.method = config.get("method", "POST").upper()
        self.cookie = config.get("cookie") or os.environ.get(
            config.get("cookie_env", "KALODATA_COOKIE"), "")
        if not self.cookie:
            raise KalodataAPIError(
                "Kein Session-Cookie gefunden. Setze die Umgebungsvariable "
                f"{config.get('cookie_env', 'KALODATA_COOKIE')} "
                "(Browser -> DevTools -> Network -> Request Headers -> cookie)."
            )

    # --- HTTP --------------------------------------------------------------
    def _request(self, payload: Dict[str, Any]) -> Any:
        url = self.base_url + self.endpoint
        headers = dict(DEFAULT_HEADERS)
        headers["Cookie"] = self.cookie
        headers["Referer"] = self.base_url + "/"

        if self.method == "GET":
            url = f"{url}?{urllib.parse.urlencode(payload, doseq=True)}"
            request = urllib.request.Request(url, headers=headers, method="GET")
        else:
            headers["Content-Type"] = "application/json"
            request = urllib.request.Request(
                url, data=json.dumps(payload).encode("utf-8"),
                headers=headers, method="POST")

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403):
                raise KalodataAPIError(
                    "Kalodata hat den Zugriff abgelehnt (Cookie abgelaufen oder Tarif "
                    "deckt den Endpunkt nicht). Cookie neu kopieren oder auf CSV umstellen."
                ) from exc
            raise KalodataAPIError(f"HTTP {exc.code} von {url}") from exc
        except urllib.error.URLError as exc:
            raise KalodataAPIError(f"Netzwerkfehler bei {url}: {exc.reason}") from exc

        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            snippet = body[:120].replace("\n", " ")
            raise KalodataAPIError(
                "Antwort war kein JSON - meist die Login-Seite, d.h. das Cookie ist "
                f"ungueltig. Anfang der Antwort: {snippet!r}"
            ) from exc

    # --- Abruf -------------------------------------------------------------
    def fetch_raw(self) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        for page in range(1, self.pages + 1):
            payload = {"page": page, "pageSize": self.page_size,
                       "period": self.period, **self.extra_params}
            batch = extract_records(self._request(payload))
            if not batch:
                break
            records.extend(batch)
            if len(batch) < self.page_size:
                break
            if page < self.pages:
                time.sleep(self.delay)
        return records

    def fetch(self) -> List[Product]:
        records = self.fetch_raw()
        if not records:
            return []
        return load_products([flatten(r) for r in records])


def extract_records(payload: Any) -> List[Dict[str, Any]]:
    """Findet die Produktliste im JSON, ohne die genaue Struktur zu kennen."""
    if isinstance(payload, list):
        return [r for r in payload if isinstance(r, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("data", "list", "items", "products", "records", "rows", "result", "content"):
        value = payload.get(key)
        if isinstance(value, list) and value and isinstance(value[0], dict):
            return value
        if isinstance(value, dict):
            nested = extract_records(value)
            if nested:
                return nested
    # Letzter Versuch: erste Liste aus Objekten irgendwo im Baum
    for value in payload.values():
        if isinstance(value, (dict, list)):
            nested = extract_records(value)
            if nested:
                return nested
    return []


def flatten(record: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """Verschachteltes JSON zu flachen Spalten - das Header-Mapping erwartet flach."""
    out: Dict[str, Any] = {}
    for key, value in record.items():
        name = f"{prefix}{key}"
        if isinstance(value, dict):
            out.update(flatten(value, prefix=f"{name} "))
        elif isinstance(value, list):
            out[name] = len(value)
        else:
            out[name] = value
    return out


def fetch_products(config: Dict[str, Any]) -> List[Product]:
    return KalodataClient(config).fetch()


def probe(config: Dict[str, Any], out_path: Optional[str] = None) -> Dict[str, Any]:
    """Einmalabruf zum Debuggen: zeigt, welche Felder die API wirklich liefert."""
    client = KalodataClient(config)
    payload = {"page": 1, "pageSize": min(client.page_size, 10),
               "period": client.period, **client.extra_params}
    raw = client._request(payload)
    records = extract_records(raw)
    if out_path:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as handle:
            json.dump(raw, handle, indent=2, ensure_ascii=False)
    return {"records": len(records),
            "fields": sorted(flatten(records[0]).keys()) if records else [],
            "saved_to": out_path}
