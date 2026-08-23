"""Einlesen von Kalodata-Exporten (CSV / TSV / XLSX / JSON).

Kalodata benennt Spalten je nach Report und Sprache unterschiedlich. Statt auf
feste Header zu setzen, mappen wir ueber Alias-Listen auf die Felder von
``Product``; unbekannte Spalten bleiben in ``Product.raw`` erhalten.
"""

from __future__ import annotations

import csv
import io
import json
import os
from typing import Any, Dict, Iterable, List, Optional

from ..models import Product
from ..util import parse_date, parse_number, parse_percent, slug

# Reihenfolge zaehlt: der erste Treffer im Header gewinnt.
COLUMN_ALIASES: Dict[str, List[str]] = {
    "product_id": ["product id", "productid", "id", "item id", "produkt id", "sku"],
    "name": ["product name", "product", "produkt", "produktname", "title", "titel", "name"],
    "category": ["category", "kategorie", "product category", "l1 category", "main category"],
    "shop": ["shop name", "shop", "seller", "store", "haendler", "verkaeufer", "shopname"],
    "url": ["product link", "product url", "link", "url", "produktlink"],
    "price": ["price", "avg price", "average price", "preis", "durchschnittspreis", "unit price"],
    "revenue": ["revenue", "gmv", "sales", "umsatz", "revenue($)", "total revenue", "sales amount"],
    "units_sold": ["items sold", "item sold", "units sold", "sales volume", "sold",
                   "verkaufte artikel", "verkaeufe", "stueckzahl", "orders"],
    "commission_rate": ["commission rate", "commission", "provision", "provisionssatz",
                        "commission(%)", "comm rate"],
    "revenue_growth": ["revenue growth", "growth", "growth rate", "wachstum", "umsatzwachstum",
                       "revenue change", "trend"],
    "rating": ["rating", "product rating", "bewertung", "sterne", "stars", "score"],
    "creators": ["creators", "creator count", "influencers", "related creators", "affiliates",
                 "creator", "anzahl creator"],
    "videos": ["videos", "video count", "related videos", "video", "anzahl videos"],
    "lives": ["lives", "live count", "live", "livestreams", "anzahl lives"],
    "gpm": ["gpm", "gross per mille", "revenue per 1000 views"],
    "launch_date": ["launch date", "listing date", "on shelf time", "created", "release date",
                    "veroeffentlichungsdatum", "startdatum", "date"],
}

_ALIAS_INDEX = {
    slug(alias): field
    for field, aliases in COLUMN_ALIASES.items()
    for alias in aliases
}

_PERCENT_FIELDS = {"commission_rate", "revenue_growth"}
_NUMBER_FIELDS = {"price", "revenue", "units_sold", "rating", "creators", "videos", "lives", "gpm"}


def map_headers(headers: Iterable[str]) -> Dict[str, str]:
    """Ordnet Exportspalten den Produktfeldern zu: {header -> feldname}."""
    mapping: Dict[str, str] = {}
    taken: set = set()
    for header in headers:
        if header is None:
            continue
        key = slug(header)
        field = _ALIAS_INDEX.get(key)
        if field is None:
            # Zweiter Versuch: Teilstring-Treffer ("revenue last 7 days" -> revenue)
            candidates = [(len(alias), fld) for alias, fld in _ALIAS_INDEX.items()
                          if len(alias) >= 4 and alias in key]
            field = max(candidates)[1] if candidates else None
        if field and field not in taken:
            mapping[header] = field
            taken.add(field)
    return mapping


def row_to_product(row: Dict[str, Any], mapping: Dict[str, str]) -> Optional[Product]:
    values: Dict[str, Any] = {}
    for header, field in mapping.items():
        raw = row.get(header)
        if raw is None or (isinstance(raw, str) and not raw.strip()):
            continue
        if field in _PERCENT_FIELDS:
            values[field] = parse_percent(raw)
        elif field in _NUMBER_FIELDS:
            values[field] = parse_number(raw)
        elif field == "launch_date":
            values[field] = parse_date(raw)
        else:
            values[field] = str(raw).strip()

    name = values.get("name")
    if not name:
        return None

    # Preis nachrechnen, wenn der Export ihn nicht liefert
    if values.get("price") is None and values.get("revenue") and values.get("units_sold"):
        values["price"] = values["revenue"] / values["units_sold"]

    return Product(raw={k: v for k, v in row.items() if v not in (None, "")}, **values)


def load_products(rows: Iterable[Dict[str, Any]], headers: Optional[List[str]] = None) -> List[Product]:
    rows = list(rows)
    if not rows:
        return []
    mapping = map_headers(headers or rows[0].keys())
    if "name" not in mapping.values():
        raise ValueError(
            "Keine Produktnamen-Spalte erkannt. Gefundene Spalten: "
            + ", ".join(str(h) for h in (headers or rows[0].keys()))
        )
    products = [row_to_product(row, mapping) for row in rows]
    return [p for p in products if p is not None]


def _sniff_delimiter(sample: str) -> str:
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
    except csv.Error:
        return ";" if sample.count(";") > sample.count(",") else ","


def load_from_file(path: str) -> List[Product]:
    """Laedt CSV/TSV/XLSX/JSON und gibt normalisierte Produkte zurueck."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            for key in ("data", "products", "items", "list", "rows"):
                if isinstance(data.get(key), list):
                    data = data[key]
                    break
        return load_products(data)

    if ext in (".xlsx", ".xlsm"):
        return _load_xlsx(path)

    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(8192)
        handle.seek(0)
        reader = csv.DictReader(handle, delimiter=_sniff_delimiter(sample))
        return load_products(list(reader), reader.fieldnames or [])


def _load_xlsx(path: str) -> List[Product]:
    try:
        from openpyxl import load_workbook
    except ImportError as exc:  # pragma: no cover - abhaengig von der Umgebung
        raise RuntimeError(
            "XLSX-Dateien brauchen openpyxl ('pip install openpyxl') - "
            "alternativ in Kalodata als CSV exportieren."
        ) from exc

    sheet = load_workbook(path, read_only=True, data_only=True).active
    rows = sheet.iter_rows(values_only=True)
    headers = [str(h) if h is not None else "" for h in next(rows)]
    records = [dict(zip(headers, row)) for row in rows]
    return load_products(records, headers)


def load_from_text(text: str) -> List[Product]:
    """Praktisch fuer Tests und Copy-Paste aus der Zwischenablage."""
    reader = csv.DictReader(io.StringIO(text), delimiter=_sniff_delimiter(text[:8192]))
    return load_products(list(reader), reader.fieldnames or [])
