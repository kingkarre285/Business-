"""Kommandozeile: python -m kalodata_sniper <befehl>"""

from __future__ import annotations

import argparse
import os
import sys
import time
from typing import List, Optional

from . import __version__, pipeline
from .config import Config
from .scoring import score_product
from .state import State
from .util import fmt_money, fmt_pct


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kalodata-sniper",
        description="Automatisierter Product Sniper fuer Kalodata-Daten.")
    parser.add_argument("--version", action="version", version=f"kalodata-sniper {__version__}")
    parser.add_argument("-c", "--config", default=_default_config_path(),
                        help="Pfad zur Config (JSON/YAML). Standard: config.json falls vorhanden.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Standard-Config schreiben")
    p_init.add_argument("-o", "--output", default="config.json")
    p_init.add_argument("--force", action="store_true")

    p_run = sub.add_parser("run", help="Einen Lauf ausfuehren")
    p_run.add_argument("-i", "--input", help="Exportdatei oder -ordner (ueberschreibt die Config)")
    p_run.add_argument("--dry-run", action="store_true",
                       help="Nichts schreiben - kein State, keine Reports")
    p_run.add_argument("--no-alerts", action="store_true", help="Keine Benachrichtigungen senden")
    p_run.add_argument("--min-score", type=float, help="Alarmschwelle ueberschreiben")
    p_run.add_argument("--top", type=int, help="Anzahl angezeigter Kandidaten")

    p_watch = sub.add_parser("watch", help="Dauerlauf in festem Intervall")
    p_watch.add_argument("--interval", type=int, default=3600, help="Sekunden (Standard 3600)")
    p_watch.add_argument("-i", "--input")
    p_watch.add_argument("--max-runs", type=int, default=0, help="0 = unbegrenzt")

    p_explain = sub.add_parser("explain", help="Score eines Produkts aufschluesseln")
    p_explain.add_argument("query", help="Teil des Produktnamens oder Produkt-ID")
    p_explain.add_argument("-i", "--input")

    p_probe = sub.add_parser(
        "probe-api", help="Einen API-Aufruf machen und die gelieferten Felder pruefen")
    p_probe.add_argument("-o", "--output", default="data/api_probe.json")

    sub.add_parser("test-notify", help="Testnachricht an alle aktiven Kanaele")
    sub.add_parser("mcp", help="Als MCP-Server ueber stdio laufen (fuer Claude & Co.)")
    sub.add_parser("demo", help="Beispieldaten erzeugen und einen Lauf zeigen")

    p_state = sub.add_parser("state", help="Verlaufsspeicher inspizieren")
    p_state.add_argument("--top", type=int, default=10)
    p_state.add_argument("--reset", action="store_true", help="Verlauf loeschen")

    return parser


def _default_config_path() -> Optional[str]:
    for candidate in ("config.json", "config.yaml", "config.yml"):
        if os.path.exists(candidate):
            return candidate
    return None


# --- Befehle ---------------------------------------------------------------
def cmd_init(args) -> int:
    if os.path.exists(args.output) and not args.force:
        print(f"{args.output} existiert bereits - mit --force ueberschreiben.")
        return 1
    Config().dump(args.output)
    print(f"Config geschrieben: {args.output}\n"
          "Naechster Schritt: Kalodata-Export nach data/ legen und "
          "'python -m kalodata_sniper run' aufrufen.")
    return 0


def cmd_run(args, config: Config) -> int:
    if getattr(args, "min_score", None) is not None:
        config.data["alerts"]["min_score"] = args.min_score
    if getattr(args, "top", None) is not None:
        config.data["alerts"]["top_n"] = args.top
    result = pipeline.run(config, input_path=args.input, dry_run=args.dry_run,
                          send_alerts=not args.no_alerts)
    return 1 if result.errors else 0


def cmd_watch(args, config: Config) -> int:
    runs = 0
    print(f"Watch-Modus: alle {args.interval}s (Abbruch mit Ctrl+C)")
    while True:
        runs += 1
        print(f"\n--- Lauf {runs} ---")
        try:
            pipeline.run(config, input_path=args.input)
        except Exception as exc:  # ein Fehlschlag darf den Dauerlauf nicht beenden
            print(f"FEHLER in Lauf {runs}: {exc}", file=sys.stderr)
        if args.max_runs and runs >= args.max_runs:
            return 0
        try:
            time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nBeendet.")
            return 0


def cmd_explain(args, config: Config) -> int:
    products, source = pipeline.load_input(config, args.input)
    query = args.query.lower()
    matches = [p for p in products
               if query in p.name.lower() or query == str(p.product_id or "").lower()]
    if not matches:
        print(f"Kein Produkt zu '{args.query}' in {source}.")
        return 1

    state = State(config.get("output.state_file", "data/state.json"))
    weights = config.weights
    currency = config.get("output.currency", "$")

    for product in matches[:5]:
        scored = score_product(product, config, state)
        print(f"\n{product.name}")
        print(f"  Score {scored.score:.1f}/100" + ("" if scored.passed else "  (AUSGEFILTERT)"))
        print(f"  Preis {fmt_money(product.price, currency)} | "
              f"Umsatz {fmt_money(product.revenue, currency)} | "
              f"Provision {fmt_pct(product.commission_rate)} | "
              f"Creator {product.creators if product.creators is not None else '-'}")
        total = sum(weights.get(k, 0) for k in scored.components) or 1
        print("  Bausteine (Anteil am Score):")
        for name, value in sorted(scored.components.items(), key=lambda kv: -kv[1]):
            weight = weights.get(name, 0)
            bar = "#" * int(round(value * 20))
            print(f"    {name:<12} {value:5.2f} {bar:<20} "
                  f"Gewicht {weight:g} -> {100 * weight * value / total:5.1f} Pkt")
        missing = [k for k in weights if k not in scored.components]
        if missing:
            print(f"    (keine Daten fuer: {', '.join(missing)} - aus der Gewichtung genommen)")
        if scored.rejected_by:
            print("  Ausgefiltert wegen: " + "; ".join(scored.rejected_by))
        if scored.reasons:
            print("  Pro: " + " · ".join(scored.reasons))
    return 0


def cmd_probe(args, config: Config) -> int:
    from .sources.api_source import probe
    info = probe(config.get("source.api", {}), args.output)
    print(f"POST {info['url']}")
    print(f"Request: {info['request']}")
    print(f"{info['records']} Datensaetze empfangen (1 Request verbraucht), "
          f"Rohantwort in {info['saved_to']}\n")

    if info["mapped"]:
        print("Erkannte Felder:")
        for source_field, target in sorted(info["mapped"].items(), key=lambda kv: kv[1]):
            print(f"  {source_field:<32} -> {target}")
    missing = {"name", "revenue"} - set(info["mapped"].values())
    if missing:
        print(f"\nACHTUNG: kein Feld fuer {', '.join(sorted(missing))} erkannt - "
              "ohne diese laeuft das Scoring nicht.")
    if info["unmapped"]:
        print("\nNicht zugeordnet (bei Bedarf in COLUMN_ALIASES ergaenzen, "
              "kalodata_sniper/sources/csv_source.py):")
        for field in info["unmapped"]:
            print(f"  - {field}")
    return 0


def cmd_test_notify(config: Config) -> int:
    from . import notify
    from .models import Product, ScoredProduct
    demo = ScoredProduct(
        product=Product(name="Testprodukt - Sniper laeuft", price=29.9, revenue=120_000,
                        commission_rate=0.2, creators=42,
                        url="https://www.kalodata.com/"),
        score=88.0, reasons=["Testnachricht"], is_new=True)
    notifiers = notify.build_notifiers(config.enabled_notifiers())
    if not notifiers:
        print("Kein Kanal aktiv - in der Config 'enabled': true setzen.")
        return 1
    errors = notify.dispatch(notifiers, [demo], config.get("output.currency", "$"))
    for error in errors:
        print(f"FEHLER {error}", file=sys.stderr)
    print("Gesendet an: " + ", ".join(n.type for n in notifiers))
    return 1 if errors else 0


def cmd_state(args, config: Config) -> int:
    path = config.get("output.state_file", "data/state.json")
    if args.reset:
        if os.path.exists(path):
            os.remove(path)
            print(f"Verlauf geloescht: {path}")
        else:
            print("Kein Verlauf vorhanden.")
        return 0
    state = State(path)
    entries = state.data.get("products", {})
    print(f"{path}: {len(entries)} Produkte, {state.data.get('runs', 0)} Laeufe, "
          f"zuletzt {state.data.get('last_run') or '-'}")
    ranked = sorted(entries.items(),
                    key=lambda kv: (kv[1].get("history") or [{}])[-1].get("score") or 0,
                    reverse=True)
    for key, entry in ranked[: args.top]:
        history = entry.get("history") or [{}]
        scores = [h.get("score") for h in history if h.get("score") is not None]
        trend = f" {scores[0]:.0f}->{scores[-1]:.0f}" if len(scores) > 1 else ""
        print(f"  {entry.get('name', key)[:60]:<62} "
              f"Score {history[-1].get('score', '-')}{trend}  "
              f"{len(history)} Datenpunkte")
    return 0


def cmd_demo(config: Config) -> int:
    from .demo import write_sample
    path = write_sample("data/demo_export.csv")
    print(f"Beispiel-Export erzeugt: {path}\n")
    demo_config = Config(config.data)
    demo_config.data["output"]["state_file"] = "data/demo_state.json"
    demo_config.data["notifiers"] = [{"type": "console", "enabled": True}]
    pipeline.run(demo_config, input_path=path, dry_run=True, send_alerts=False)
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            return cmd_init(args)
        if args.command == "mcp":
            # Config wird pro Aufruf frisch geladen - hier nur der Pfad
            from .mcp_server import main as serve_mcp
            return serve_mcp(args.config)
        config = Config.load(args.config)
        handlers = {
            "run": lambda: cmd_run(args, config),
            "watch": lambda: cmd_watch(args, config),
            "explain": lambda: cmd_explain(args, config),
            "probe-api": lambda: cmd_probe(args, config),
            "test-notify": lambda: cmd_test_notify(config),
            "state": lambda: cmd_state(args, config),
            "demo": lambda: cmd_demo(config),
        }
        return handlers[args.command]()
    except KeyboardInterrupt:
        print("\nAbgebrochen.")
        return 130
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"FEHLER: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
