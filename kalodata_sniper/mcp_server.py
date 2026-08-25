"""MCP-Server: den Sniper direkt aus Claude heraus bedienen.

Spricht JSON-RPC 2.0 ueber stdio, zeilenweise - genau wie es der
Model-Context-Protocol-Transport erwartet. Bewusst ohne SDK-Abhaengigkeit,
damit der Server dieselbe Standardbibliothek nutzt wie der Rest des Projekts.

Start:  python -m kalodata_sniper mcp

Wichtig: ueber stdout laeuft das Protokoll. Alles, was die Pipeline sonst
ausgibt, wird deshalb nach stderr umgeleitet - eine einzige Zeile Text auf
stdout wuerde die Verbindung zerlegen.
"""

from __future__ import annotations

import contextlib
import json
import sys
import traceback
from typing import Any, Callable, Dict, List, Optional

from . import __version__, pipeline
from .config import Config
from .models import ScoredProduct
from .scoring import score_product
from .state import State
from .util import fmt_money, fmt_pct

PROTOCOL_VERSION = "2025-06-18"
SUPPORTED_PROTOCOLS = {"2024-11-05", "2025-03-26", "2025-06-18"}

# JSON-RPC-Fehlercodes
INVALID_PARAMS = -32602
METHOD_NOT_FOUND = -32601
INTERNAL_ERROR = -32603
PARSE_ERROR = -32700


# --- Werkzeugdefinitionen --------------------------------------------------
def tool_definitions() -> List[Dict[str, Any]]:
    return [
        {
            "name": "sniper_scan",
            "description": (
                "Einen Sniper-Lauf ausfuehren: Kalodata-Daten laden, filtern, scoren "
                "und die besten Produkte zurueckgeben. Schreibt standardmaessig den "
                "Verlauf fort (noetig fuer die Momentum-Erkennung beim naechsten Lauf)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "input": {"type": "string",
                              "description": "Exportdatei oder -ordner. Leer = Quelle aus der Config."},
                    "top": {"type": "integer", "minimum": 1, "maximum": 100, "default": 10,
                            "description": "Wie viele Kandidaten zurueckgegeben werden."},
                    "min_score": {"type": "number", "minimum": 0, "maximum": 100,
                                  "description": "Alarmschwelle fuer diesen Lauf."},
                    "dry_run": {"type": "boolean", "default": False,
                                "description": "Nichts schreiben: kein Verlauf, keine Reports."},
                    "send_alerts": {"type": "boolean", "default": False,
                                    "description": "Konfigurierte Kanaele (Telegram etc.) benachrichtigen."},
                    "region": {"type": "string",
                               "description": "Marktregion fuer den API-Abruf: US BR MX ID JP MY "
                                              "PH SG TH VN GB ES DE FR IT. Standard aus der Config."},
                    "date_range": {"type": "string",
                                   "description": "Zeitraum: lastDay, last7Day, last30Day, last60Day, "
                                                  "last90Day, last180Day, last365Day, ein Bereich "
                                                  "'yyyy-MM-dd~yyyy-MM-dd' oder ein Monat 'yyyy-MM'."},
                },
            },
        },
        {
            "name": "sniper_explain",
            "description": (
                "Den Score eines einzelnen Produkts aufschluesseln: welcher Baustein "
                "wie viele Punkte beisteuert und - falls ausgefiltert - warum."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Teil des Produktnamens oder Produkt-ID."},
                    "input": {"type": "string", "description": "Optionale Exportdatei."},
                },
                "required": ["query"],
            },
        },
        {
            "name": "sniper_watchlist",
            "description": (
                "Den Verlaufsspeicher abfragen: welche Produkte beobachtet werden, "
                "wie sich ihr Score entwickelt hat und was am staerksten steigt."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "top": {"type": "integer", "minimum": 1, "maximum": 100, "default": 15},
                    "sort": {"type": "string", "enum": ["score", "trend"], "default": "score",
                             "description": "'score' = aktuell beste, 'trend' = staerkster Anstieg."},
                },
            },
        },
        {
            "name": "sniper_config",
            "description": (
                "Aktuelle Filter, Gewichte und Alarmschwellen anzeigen - damit "
                "nachvollziehbar ist, warum ein Lauf so ausfaellt, wie er ausfaellt."
            ),
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "sniper_probe_api",
            "description": (
                "Die Anbindung an die Kalodata Open API pruefen: ein einzelner Aufruf, "
                "danach das Feld-Mapping. Kostet genau einen Request."
            ),
            "inputSchema": {"type": "object", "properties": {}},
        },
    ]


# --- Werkzeuge -------------------------------------------------------------
def _load_config(config_path: Optional[str]) -> Config:
    return Config.load(config_path)


def tool_sniper_scan(config: Config, args: Dict[str, Any]) -> str:
    if args.get("min_score") is not None:
        config.data["alerts"]["min_score"] = float(args["min_score"])
    request = config.data["source"]["api"]["request"]
    for key in ("region", "date_range"):
        if args.get(key):
            request[key] = args[key]
    result = pipeline.run(
        config,
        input_path=args.get("input"),
        dry_run=bool(args.get("dry_run", False)),
        send_alerts=bool(args.get("send_alerts", False)),
        quiet=True,
    )
    top = int(args.get("top", 10))
    currency = config.get("output.currency", "$")

    lines = [
        f"Quelle: {result.source}",
        "  ".join(f"{k}: {v}" for k, v in result.stats.items()),
        "",
    ]
    if not result.hits:
        lines.append("Kein Produkt hat die Filter passiert. Filter lockern: "
                     "filters.revenue_min senken oder filters.creators_max erhoehen.")
    else:
        lines.append(f"Top {min(top, len(result.hits))} von {len(result.hits)} Kandidaten:")
        lines += [_describe(item, index, currency)
                  for index, item in enumerate(result.hits[:top], 1)]
    if result.alerts:
        lines.append(f"\n{len(result.alerts)} Alarm(e) ausgeloest.")
    for path in result.reports.values():
        lines.append(f"Report: {path}")
    for error in result.errors:
        lines.append(f"FEHLER {error}")
    return "\n".join(lines)


def _describe(item: ScoredProduct, index: int, currency: str) -> str:
    product = item.product
    facts = [f"Score {item.score:.0f}"]
    if product.revenue is not None:
        facts.append(f"Umsatz {fmt_money(product.revenue, currency)}")
    if product.price is not None:
        facts.append(f"Preis {fmt_money(product.price, currency)}")
    if product.commission_rate is not None:
        facts.append(f"Provision {fmt_pct(product.commission_rate)}")
    if product.creators is not None:
        facts.append(f"{product.creators:,.0f} Creator")
    if item.momentum is not None:
        facts.append(f"Momentum {fmt_pct(item.momentum)}")

    out = [f"{index}. {product.name.strip()}", "   " + " | ".join(facts)]
    if item.reasons:
        out.append("   " + " · ".join(item.reasons[:4]))
    if product.url:
        out.append(f"   {product.url}")
    return "\n".join(out)


def tool_sniper_explain(config: Config, args: Dict[str, Any]) -> str:
    query = str(args.get("query", "")).strip()
    if not query:
        raise ValueError("Parameter 'query' fehlt.")

    products, source = pipeline.load_input(config, args.get("input"))
    needle = query.lower()
    matches = [p for p in products
               if needle in p.name.lower() or needle == str(p.product_id or "").lower()]
    if not matches:
        return f"Kein Produkt zu '{query}' in {source}."

    state = State(config.get("output.state_file", "data/state.json"))
    weights = config.weights
    currency = config.get("output.currency", "$")

    blocks = []
    for product in matches[:3]:
        scored = score_product(product, config, state)
        total = sum(weights.get(k, 0) for k in scored.components) or 1
        lines = [
            product.name,
            f"  Score {scored.score:.1f}/100" + ("" if scored.passed else "   AUSGEFILTERT"),
            f"  Preis {fmt_money(product.price, currency)} | "
            f"Umsatz {fmt_money(product.revenue, currency)} | "
            f"Provision {fmt_pct(product.commission_rate)} | "
            f"Creator {product.creators if product.creators is not None else '-'}",
            "  Bausteine:",
        ]
        for name, value in sorted(scored.components.items(), key=lambda kv: -kv[1]):
            weight = weights.get(name, 0)
            lines.append(f"    {name:<12} {value:4.2f} x Gewicht {weight:<4g} "
                         f"-> {100 * weight * value / total:5.1f} Pkt")
        missing = [k for k in weights if k not in scored.components]
        if missing:
            lines.append(f"    keine Daten fuer: {', '.join(missing)} "
                         "(aus der Gewichtung genommen)")
        if scored.rejected_by:
            lines.append("  Ausgefiltert wegen: " + "; ".join(scored.rejected_by))
        if scored.reasons:
            lines.append("  Pro: " + " · ".join(scored.reasons))
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def tool_sniper_watchlist(config: Config, args: Dict[str, Any]) -> str:
    path = config.get("output.state_file", "data/state.json")
    state = State(path)
    entries = state.data.get("products", {})
    if not entries:
        return (f"Noch kein Verlauf in {path}. Erst 'sniper_scan' laufen lassen - "
                "Momentum braucht mindestens zwei Laeufe.")

    def scores(entry: Dict[str, Any]) -> List[float]:
        return [h["score"] for h in entry.get("history", []) if h.get("score") is not None]

    def current(item) -> float:
        values = scores(item[1])
        return values[-1] if values else 0.0

    def trend(item) -> float:
        values = scores(item[1])
        return values[-1] - values[0] if len(values) > 1 else 0.0

    key = trend if args.get("sort") == "trend" else current
    ranked = sorted(entries.items(), key=key, reverse=True)[: int(args.get("top", 15))]

    lines = [f"{len(entries)} beobachtete Produkte, {state.data.get('runs', 0)} Laeufe, "
             f"zuletzt {state.data.get('last_run') or '-'}", ""]
    for entry_key, entry in ranked:
        values = scores(entry)
        lines.append(entry.get("name", entry_key)[:70])
        if not values:
            lines.append("  noch keine Bewertung")
            continue
        movement = ""
        if len(values) > 1:
            arrow = ("steigt" if values[-1] > values[0]
                     else "faellt" if values[-1] < values[0] else "flach")
            movement = f"  {values[0]:.0f} -> {values[-1]:.0f} ({arrow})"
        lines.append(f"  Score {values[-1]:.0f}{movement}  "
                     f"{len(entry.get('history', []))} Datenpunkte")
    return "\n".join(lines)


def tool_sniper_config(config: Config, args: Dict[str, Any]) -> str:
    view = {
        "quelle": config.get("source.type"),
        "filters": config.filters,
        "weights": config.data["weights"],
        "targets": config.targets,
        "alerts": config.data["alerts"],
        "aktive_kanaele": [n["type"] for n in config.enabled_notifiers()],
    }
    return json.dumps(view, indent=2, ensure_ascii=False)


def tool_sniper_probe_api(config: Config, args: Dict[str, Any]) -> str:
    from .sources.api_source import probe
    info = probe(config.get("source.api", {}), "data/api_probe.json")
    lines = [f"{info['url']}", f"Request: {json.dumps(info['request'], ensure_ascii=False)}",
             f"{info['records']} Datensaetze empfangen.", ""]
    if info["mapped"]:
        lines.append("Erkannte Felder:")
        lines += [f"  {src:<32} -> {dst}"
                  for src, dst in sorted(info["mapped"].items(), key=lambda kv: kv[1])]
    missing = {"name", "revenue"} - set(info["mapped"].values())
    if missing:
        lines.append(f"\nACHTUNG: kein Feld fuer {', '.join(sorted(missing))} erkannt.")
    if info["unmapped"]:
        lines.append("\nNicht zugeordnet: " + ", ".join(info["unmapped"]))
    return "\n".join(lines)


TOOLS: Dict[str, Callable[[Config, Dict[str, Any]], str]] = {
    "sniper_scan": tool_sniper_scan,
    "sniper_explain": tool_sniper_explain,
    "sniper_watchlist": tool_sniper_watchlist,
    "sniper_config": tool_sniper_config,
    "sniper_probe_api": tool_sniper_probe_api,
}


# --- JSON-RPC --------------------------------------------------------------
class MCPServer:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.initialized = False
        self.config_note: Optional[str] = None

    def config(self) -> Config:
        # Bei jedem Aufruf frisch laden: so wirken Config-Aenderungen sofort,
        # ohne den Server neu zu starten.
        try:
            config = _load_config(self.config_path)
            self.config_note = None
            return config
        except FileNotFoundError:
            # Eine fehlende Config darf nicht jeden Aufruf toeten - mit den
            # Standardwerten weiterarbeiten und einmal darauf hinweisen.
            self.config_note = (
                f"Hinweis: {self.config_path} existiert nicht, es gelten die Standardwerte. "
                "Mit 'python -m kalodata_sniper init' anlegen."
            )
            return Config()

    def handle(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        method = message.get("method")
        message_id = message.get("id")
        params = message.get("params") or {}

        if method is None:
            return None  # Antwort eines Clients - hier ohne Bedeutung
        if message_id is None:
            if method == "notifications/initialized":
                self.initialized = True
            return None  # Notifications werden nie beantwortet

        try:
            if method == "initialize":
                return _ok(message_id, self._initialize(params))
            if method == "ping":
                return _ok(message_id, {})
            if method == "tools/list":
                return _ok(message_id, {"tools": tool_definitions()})
            if method == "tools/call":
                return _ok(message_id, self._call_tool(params))
            if method in ("resources/list", "prompts/list"):
                key = method.split("/")[0]
                return _ok(message_id, {key: []})
            return _error(message_id, METHOD_NOT_FOUND, f"Unbekannte Methode: {method}")
        except ValueError as exc:
            return _error(message_id, INVALID_PARAMS, str(exc))
        except Exception as exc:  # nie den Server abstuerzen lassen
            traceback.print_exc(file=sys.stderr)
            return _error(message_id, INTERNAL_ERROR, f"{type(exc).__name__}: {exc}")

    def _initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        requested = params.get("protocolVersion")
        version = requested if requested in SUPPORTED_PROTOCOLS else PROTOCOL_VERSION
        return {
            "protocolVersion": version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "kalodata-sniper", "version": __version__},
            "instructions": (
                "Product Sniper fuer Kalodata/TikTok-Shop-Daten. sniper_scan fuehrt einen "
                "Lauf aus, sniper_explain begruendet einen einzelnen Score, sniper_watchlist "
                "zeigt die Entwicklung ueber mehrere Laeufe. Momentum entsteht erst ab dem "
                "zweiten Lauf im Abstand von Stunden."
            ),
        }

    def _call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        name = params.get("name")
        handler = TOOLS.get(name)
        if handler is None:
            raise ValueError(f"Unbekanntes Werkzeug: {name}")
        arguments = params.get("arguments") or {}

        # stdout gehoert dem Protokoll - alles andere nach stderr umleiten
        try:
            with contextlib.redirect_stdout(sys.stderr):
                config = self.config()
                text = handler(config, arguments)
            if self.config_note:
                text = f"{self.config_note}\n\n{text}"
            is_error = False
        except Exception as exc:
            text = f"{type(exc).__name__}: {exc}"
            is_error = True
            traceback.print_exc(file=sys.stderr)
        return {"content": [{"type": "text", "text": text}], "isError": is_error}

    def serve(self, stdin=None, stdout=None) -> int:
        stdin = stdin or sys.stdin
        stdout = stdout or sys.stdout
        for line in stdin:
            line = line.strip()
            if not line:
                continue
            try:
                message = json.loads(line)
            except json.JSONDecodeError:
                _write(stdout, _error(None, PARSE_ERROR, "Ungueltiges JSON"))
                continue
            if isinstance(message, list):   # Batch
                for response in filter(None, (self.handle(m) for m in message)):
                    _write(stdout, response)
                continue
            response = self.handle(message)
            if response is not None:
                _write(stdout, response)
        return 0


def _ok(message_id: Any, result: Dict[str, Any]) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": message_id, "result": result}


def _error(message_id: Any, code: int, message: str) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": message_id, "error": {"code": code, "message": message}}


def _write(stream, payload: Dict[str, Any]) -> None:
    stream.write(json.dumps(payload, ensure_ascii=False) + "\n")
    stream.flush()


def main(config_path: Optional[str] = None) -> int:
    return MCPServer(config_path).serve()
