"""Client fuer die offizielle Kalodata Open API.

Vertrag laut Open Center: alle Endpunkte sind HTTP POST + JSON unter
``https://www.kalodata.com/openapi/v1/tiktok/...``, authentifiziert per
Secret-Key im Header. Gemeinsame Pflichtfelder aller Endpunkte sind
``region``, ``language``, ``currency`` und ``date_range``; das Rate-Limit liegt
bei 100 Requests pro 10 Sekunden.

Die Open API folgt dem Listen-plus-Detail-Modell ueber sechs Module (Product,
Creator, Shop, Video, Livestream, Category).

Zwei Dinge praegen den Client:

* **Abrechnung nach Verbrauch.** Jeder Aufruf kostet Credits. Deshalb gibt es ein
  hartes Requestbudget pro Lauf und einen Antwort-Cache auf der Platte - beim
  Tunen der Filter wird dieselbe Antwort wiederverwendet statt neu bezahlt.
* **Konfigurierbare Namen.** Basis-URL, Auth-Header, Endpunktpfade und
  Parameternamen stehen in der Config, nicht im Code. Weicht die Doku deines
  Tarifs ab, ist das eine Config-Aenderung - kein Patch.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from typing import Any, Deque, Dict, List, Optional

from ..models import Product
from .csv_source import load_products

# Aus der Open-API-Doku. Wird vor dem Request geprueft - ein Tippfehler soll
# keinen Credit kosten.
REGIONS = {"US", "BR", "MX", "ID", "JP", "MY", "PH", "SG", "TH", "VN",
           "GB", "ES", "DE", "FR", "IT"}
LANGUAGES = {"zh-CN", "en-US", "id-ID", "th-TH", "vi-VN", "es-ES", "ja-JP",
             "pt-BR", "ko-KR", "fr-FR"}
CURRENCIES = {"CNY", "USD", "IDR", "VND", "THB", "MYR", "JPY", "PHP", "GBP",
              "SGD", "MXN", "EUR", "BRL"}
NAMED_RANGES = {"lastDay", "last7Day", "last30Day", "last60Day", "last90Day",
                "last180Day", "last365Day"}
_RANGE_ALIASES = {r.lower(): r for r in NAMED_RANGES}
_RANGE_ALIASES.update({"1d": "lastDay", "7d": "last7Day", "30d": "last30Day",
                       "60d": "last60Day", "90d": "last90Day",
                       "180d": "last180Day", "365d": "last365Day"})

DEFAULT_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "kalodata-sniper/0.1 (+https://github.com/kingkarre285/Business-)",
}


class KalodataAPIError(RuntimeError):
    pass


def normalise_date_range(value: Any) -> str:
    """Akzeptiert 'last7Day', '7d', '2026-08-01~2026-08-07' oder '2026-08'.

    Named Ranges werden case-insensitiv auf die Schreibweise der API gebracht.
    """
    if value in (None, ""):
        return "last7Day"
    text = str(value).strip()
    if text.lower() in _RANGE_ALIASES:
        return _RANGE_ALIASES[text.lower()]
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}~\d{4}-\d{2}-\d{2}", text):
        return text
    if re.fullmatch(r"\d{4}-\d{2}", text):
        return text
    raise KalodataAPIError(
        f"date_range '{text}' ist ungueltig. Erlaubt: {', '.join(sorted(NAMED_RANGES))}, "
        "ein Bereich 'yyyy-MM-dd~yyyy-MM-dd' oder ein Monat 'yyyy-MM'."
    )


def validate_common(payload: Dict[str, Any]) -> None:
    """Prueft die Pflichtfelder, bevor ein Request Credits kostet."""
    checks = (("region", REGIONS), ("language", LANGUAGES), ("currency", CURRENCIES))
    for field, allowed in checks:
        value = payload.get(field)
        if value is None:
            raise KalodataAPIError(f"Pflichtfeld '{field}' fehlt (source.api.request.{field}).")
        if value not in allowed:
            raise KalodataAPIError(
                f"{field}='{value}' wird nicht unterstuetzt. Erlaubt: {', '.join(sorted(allowed))}."
            )


class RateLimiter:
    """Haelt das dokumentierte Limit von 100 Requests je 10 Sekunden ein."""

    def __init__(self, max_requests: int = 100, window_seconds: float = 10.0):
        self.max_requests = max_requests
        self.window = window_seconds
        self._stamps: Deque[float] = deque()

    def acquire(self) -> None:
        now = time.monotonic()
        while self._stamps and now - self._stamps[0] > self.window:
            self._stamps.popleft()
        if len(self._stamps) >= self.max_requests:
            time.sleep(max(0.0, self.window - (now - self._stamps[0])) + 0.01)
            return self.acquire()
        self._stamps.append(now)


class BudgetExceeded(KalodataAPIError):
    """Das Requestbudget des Laufs ist aufgebraucht - schuetzt vor Credit-Verbrauch."""


class ResponseCache:
    """Simpler Datei-Cache. Spart Credits beim Nachjustieren der Filter."""

    def __init__(self, directory: str, ttl_minutes: float):
        self.directory = directory
        self.ttl = ttl_minutes * 60

    def _path(self, key: str) -> str:
        digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:20]
        return os.path.join(self.directory, f"api_{digest}.json")

    def get(self, key: str) -> Optional[Any]:
        if self.ttl <= 0:
            return None
        path = self._path(key)
        if not os.path.exists(path) or time.time() - os.path.getmtime(path) > self.ttl:
            return None
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except (json.JSONDecodeError, OSError):
            return None

    def put(self, key: str, value: Any) -> None:
        if self.ttl <= 0:
            return
        os.makedirs(self.directory, exist_ok=True)
        try:
            with open(self._path(key), "w", encoding="utf-8") as handle:
                json.dump(value, handle)
        except OSError:
            pass  # Cache ist Komfort, kein Muss


class KalodataClient:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get("base_url", "https://www.kalodata.com").rstrip("/")
        self.module = config.get("module", "product")
        self.endpoints: Dict[str, str] = config.get("endpoints", {})
        self.method = config.get("method", "POST").upper()
        self.pages = int(config.get("pages", 2))
        self.page_size = int(config.get("page_size", 50))
        self.delay = float(config.get("delay_seconds", 0.2))
        self.limiter = RateLimiter(int(config.get("rate_limit_requests", 100)),
                                   float(config.get("rate_limit_window_seconds", 10.0)))
        self.timeout = int(config.get("timeout_seconds", 30))
        self.param_names: Dict[str, str] = config.get("param_names", {})
        self.request_defaults: Dict[str, Any] = config.get("request", {})

        self.max_requests = int(config.get("max_requests_per_run", 10))
        self._requests_made = 0
        self.cache = ResponseCache(config.get("cache_dir", "data/.cache"),
                                   float(config.get("cache_ttl_minutes", 360)))

        self.api_key = config.get("api_key") or os.environ.get(
            config.get("api_key_env", "KALODATA_API_KEY"), "")
        if not self.api_key:
            raise KalodataAPIError(
                "Kein API-Key gefunden. Key im Kalodata Open Center erzeugen und "
                f"als Umgebungsvariable {config.get('api_key_env', 'KALODATA_API_KEY')} setzen."
            )

    # --- Auth --------------------------------------------------------------
    def _auth_headers(self) -> Dict[str, str]:
        auth = self.config.get("auth", {})
        header = auth.get("header", "secret-key")
        prefix = auth.get("prefix", "")
        return {header: f"{prefix}{self.api_key}"}

    # --- Parameter ---------------------------------------------------------
    def param(self, logical: str) -> str:
        """Uebersetzt einen logischen Namen in den Feldnamen der API."""
        return self.param_names.get(logical, logical)

    def build_payload(self, page: int, **overrides: Any) -> Dict[str, Any]:
        request = dict(self.request_defaults)

        # Die vier Pflichtfelder aller Endpunkte
        payload: Dict[str, Any] = {
            "region": request.pop("region", "US"),
            "language": request.pop("language", "en-US"),
            "currency": request.pop("currency", "USD"),
            "date_range": normalise_date_range(request.pop("date_range", None)),
        }
        validate_common(payload)

        payload[self.param("page")] = page
        payload[self.param("page_size")] = self.page_size
        for key in ("sort", "sort_order", "category", "need_extra"):
            if request.get(key) not in (None, "", []):
                payload[self.param(key)] = request.pop(key)
        # Filter und alles Uebrige unveraendert durchreichen
        payload.update(request.pop("filters", {}) or {})
        payload.update(request)
        payload.update(overrides)
        return payload

    # --- HTTP --------------------------------------------------------------
    def _endpoint_url(self, kind: str = "rank") -> str:
        path = self.endpoints.get(kind)
        if not path:
            raise KalodataAPIError(
                f"Kein '{kind}'-Endpunkt konfiguriert (source.api.endpoints.{kind}). "
                "Pfad aus den Open-Center-Docs eintragen."
            )
        return self.base_url + path

    def request(self, payload: Dict[str, Any], kind: str = "rank") -> Any:
        url = self._endpoint_url(kind)
        cache_key = f"{self.method} {url} {json.dumps(payload, sort_keys=True)}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        if self._requests_made >= self.max_requests:
            raise BudgetExceeded(
                f"Requestbudget erreicht ({self.max_requests} Aufrufe). "
                "source.api.max_requests_per_run erhoehen, wenn das gewollt ist."
            )

        headers = {**DEFAULT_HEADERS, **self._auth_headers()}
        if self.method == "GET":
            full_url = f"{url}?{urllib.parse.urlencode(_flatten_params(payload), doseq=True)}"
            request = urllib.request.Request(full_url, headers=headers, method="GET")
        else:
            headers["Content-Type"] = "application/json"
            request = urllib.request.Request(
                url, data=json.dumps(payload).encode("utf-8"),
                headers=headers, method=self.method)

        self.limiter.acquire()
        self._requests_made += 1
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            raise KalodataAPIError(_http_message(exc, url)) from exc
        except urllib.error.URLError as exc:
            raise KalodataAPIError(f"Netzwerkfehler bei {url}: {exc.reason}") from exc

        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise KalodataAPIError(
                f"Antwort von {url} war kein JSON. Anfang: {body[:150]!r}") from exc

        _raise_for_api_error(data, url)
        self.cache.put(cache_key, data)
        return data

    # --- Abruf -------------------------------------------------------------
    def fetch_raw(self) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        for page in range(1, self.pages + 1):
            try:
                payload = self.request(self.build_payload(page), kind="rank")
            except BudgetExceeded:
                break  # was schon geholt wurde, wird trotzdem ausgewertet
            batch = extract_records(payload)
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
        return load_products([flatten(record) for record in records])

    @property
    def requests_made(self) -> int:
        return self._requests_made


def _http_message(exc: urllib.error.HTTPError, url: str) -> str:
    detail = ""
    try:
        detail = exc.read().decode("utf-8", errors="replace")[:200]
    except Exception:
        pass
    hints = {
        400: "Parameter abgelehnt - region/language/currency/date_range gegen die Doku pruefen.",
        401: "Secret-Key ungueltig oder unter falschem Header-Namen gesendet "
             "(source.api.auth.header).",
        403: "Key gueltig, aber ohne Berechtigung fuer diesen Endpunkt (Tarif/Modul).",
        402: "Credits aufgebraucht - im Open Center aufladen.",
        404: "Endpunktpfad stimmt nicht - Pfad aus den Docs in source.api.endpoints eintragen.",
        429: "Rate-Limit (100 Requests/10s) erreicht - source.api.delay_seconds erhoehen.",
    }
    hint = hints.get(exc.code, "")
    return f"HTTP {exc.code} von {url}. {hint} {detail}".strip()


def _raise_for_api_error(payload: Any, url: str) -> None:
    """Die API antwortet mit HTTP 200 und meldet Fehler im Body.

    Huelle laut Doku: {success, data, message, debug, cached, code}. ``success``
    ist das verlaessliche Signal - ``code`` ist ein String ohne dokumentierte
    Erfolgskonstante.
    """
    if not isinstance(payload, dict):
        return

    if payload.get("success") is False:
        # Die Mock-Vorschau der Doku liefert success=false trotz gefuellter Daten.
        # Nur abbrechen, wenn wirklich nichts Verwertbares dabei ist.
        if extract_records(payload):
            return
        message = payload.get("message") or "kein Grund genannt"
        code = payload.get("code")
        suffix = f" (code {code})" if code else ""
        raise KalodataAPIError(f"Kalodata meldet Fehler bei {url}: {message}{suffix}")
    if payload.get("success") is True:
        return

    # Aeltere/abweichende Huellen: numerischer Fehlercode ohne success-Flag
    code = payload.get("code", payload.get("status_code"))
    if code in (None, 0, 200, "0", "200", "success", "OK"):
        return
    if extract_records(payload):
        return  # Daten sind da, der Code meint etwas anderes
    message = payload.get("message") or payload.get("msg") or payload.get("error") or ""
    raise KalodataAPIError(f"Kalodata meldet Fehler {code} bei {url}: {message}")


def _flatten_params(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Verschachtelte Werte fuer GET-Querystrings JSON-kodieren."""
    return {k: (json.dumps(v) if isinstance(v, (dict, list)) else v)
            for k, v in payload.items()}


def extract_records(payload: Any) -> List[Dict[str, Any]]:
    """Findet die Datensaetze in der Antwort.

    Listen-Endpunkte liefern ``data`` als Array, Detail-Endpunkte als einzelnes
    Objekt - beides ergibt hier eine Liste von Datensaetzen.
    """
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
            if _looks_like_record(value):
                return [value]   # Detail-Antwort: data ist der Datensatz selbst

    for value in payload.values():
        if isinstance(value, (dict, list)):
            nested = extract_records(value)
            if nested:
                return nested
    return []


def _looks_like_record(value: Dict[str, Any]) -> bool:
    """Ein Datensatz ist ein Objekt mit skalaren Feldern, keine blosse Huelle."""
    envelope_keys = {"success", "message", "debug", "cached", "code"}
    keys = set(value.keys())
    if not keys or keys <= envelope_keys:
        return False
    return any(not isinstance(v, (dict, list)) for v in value.values())


def flatten(record: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """Verschachteltes JSON zu flachen Spalten - das Header-Mapping erwartet flach.

    Zahlenreihen wie ``revenue_trend`` bleiben als Liste erhalten: aus ihnen
    berechnet das Scoring das Momentum schon beim ersten Lauf. Alle uebrigen
    Listen werden zu ihrer Laenge verdichtet (z.B. Anzahl verknuepfter Creator).
    """
    out: Dict[str, Any] = {}
    for key, value in record.items():
        name = f"{prefix}{key}"
        if isinstance(value, dict):
            out.update(flatten(value, prefix=f"{name} "))
        elif isinstance(value, list):
            out[name] = value if _is_number_series(value) else len(value)
        else:
            out[name] = value
    return out


def _is_number_series(value: List[Any]) -> bool:
    return bool(value) and all(isinstance(v, (int, float)) and not isinstance(v, bool)
                               for v in value)


def fetch_products(config: Dict[str, Any]) -> List[Product]:
    return KalodataClient(config).fetch()


def probe(config: Dict[str, Any], out_path: Optional[str] = None) -> Dict[str, Any]:
    """Ein einzelner Aufruf zum Abgleich mit den Docs - kostet genau einen Request."""
    probe_config = dict(config)
    probe_config["cache_ttl_minutes"] = 0      # bewusst frisch abfragen
    probe_config["max_requests_per_run"] = 1
    client = KalodataClient(probe_config)
    client.page_size = min(client.page_size, 10)

    payload = client.build_payload(1)
    raw = client.request(payload, kind="rank")
    records = extract_records(raw)

    if out_path:
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as handle:
            json.dump({"request": payload, "response": raw}, handle,
                      indent=2, ensure_ascii=False)

    fields = sorted(flatten(records[0]).keys()) if records else []
    mapped = {}
    if records:
        from .csv_source import map_headers
        mapped = map_headers(fields)
    return {"url": client._endpoint_url("rank"), "request": payload,
            "records": len(records), "fields": fields, "mapped": mapped,
            "unmapped": [f for f in fields if f not in mapped], "saved_to": out_path}
