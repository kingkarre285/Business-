"""Der Lauf selbst: laden -> bewerten -> Verlauf schreiben -> melden -> berichten."""

from __future__ import annotations

import glob
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from . import notify, report
from .config import Config
from .models import Product, ScoredProduct
from .scoring import run_scoring, select_alerts
from .sources import csv_source
from .state import State

DATA_EXTENSIONS = (".csv", ".tsv", ".xlsx", ".xlsm", ".json")


@dataclass
class RunResult:
    products: List[Product] = field(default_factory=list)
    scored: List[ScoredProduct] = field(default_factory=list)
    hits: List[ScoredProduct] = field(default_factory=list)
    alerts: List[ScoredProduct] = field(default_factory=list)
    reports: Dict[str, str] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    source: str = ""

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "Produkte": len(self.products),
            "Gefiltert": len(self.products) - len(self.hits),
            "Kandidaten": len(self.hits),
            "Alarme": len(self.alerts),
            "Top-Score": f"{self.hits[0].score:.0f}" if self.hits else "-",
        }


def resolve_input(path: str) -> str:
    """Akzeptiert Datei oder Ordner; bei Ordnern gewinnt der neueste Export."""
    if os.path.isdir(path):
        candidates = [f for f in glob.glob(os.path.join(path, "*"))
                      if f.lower().endswith(DATA_EXTENSIONS)]
        if not candidates:
            raise FileNotFoundError(f"Keine Exportdatei in {path} gefunden ({', '.join(DATA_EXTENSIONS)}).")
        return max(candidates, key=os.path.getmtime)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Export nicht gefunden: {path}\n"
            "In Kalodata unter Products -> Filter setzen -> Export, Datei hier ablegen."
        )
    return path


def load_input(config: Config, override_path: Optional[str] = None) -> tuple[List[Product], str]:
    source_type = "csv" if override_path else config.get("source.type", "csv")
    if source_type == "api":
        from .sources.api_source import fetch_products  # spaeter importieren: optional
        return fetch_products(config.get("source.api", {})), "kalodata-api"
    path = resolve_input(override_path or config.get("source.path", "data"))
    return csv_source.load_from_file(path), path


def run(config: Config, *, input_path: Optional[str] = None, dry_run: bool = False,
        send_alerts: bool = True, quiet: bool = False) -> RunResult:
    result = RunResult()
    products, source = load_input(config, input_path)
    result.products, result.source = products, source
    if not products:
        result.errors.append(f"Keine Produkte in {source} gefunden.")
        return result

    state_path = config.get("output.state_file", "data/state.json")
    state = State(state_path, history_length=int(config.get("output.history_length", 40)))

    result.scored = run_scoring(products, config, state)
    result.hits = [s for s in result.scored if s.passed]
    result.alerts = select_alerts(result.hits, config, state)

    if send_alerts and result.alerts:
        notifiers = notify.build_notifiers(config.enabled_notifiers())
        if notifiers:
            errors = notify.dispatch(notifiers, result.alerts,
                                     config.get("output.currency", "$"))
            result.errors.extend(errors)
            if not errors:
                for item in result.alerts:
                    state.mark_alerted(item.product.key)

    # Verlauf erst nach dem Scoring schreiben - sonst vergleicht der naechste
    # Lauf gegen sich selbst.
    if not dry_run:
        for item in result.scored:
            state.record(item.product.key, revenue=item.product.revenue,
                         units=item.product.units_sold, score=item.score,
                         name=item.product.name)
        state.finish_run(config.get("output.prune_after_days"))
        state.save()
        result.reports = write_reports(result, config)

    if not quiet:
        print(summary(result, config))
    return result


def write_reports(result: RunResult, config: Config) -> Dict[str, str]:
    directory = config.get("output.report_dir", "reports")
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    top_n = int(config.get("alerts.top_n", 15))
    items = result.hits[:top_n] if top_n > 0 else result.hits
    written: Dict[str, str] = {}
    if config.get("output.write_csv", True):
        written["csv"] = report.write_csv(result.hits, os.path.join(directory, f"sniper_{stamp}.csv"))
    if config.get("output.write_html", True):
        written["html"] = report.write_html(
            items, os.path.join(directory, f"sniper_{stamp}.html"),
            currency=config.get("output.currency", "$"), stats=result.stats)
        # Stabiler Pfad fuer Bookmarks / CI-Artefakte
        written["html_latest"] = report.write_html(
            items, os.path.join(directory, "latest.html"),
            currency=config.get("output.currency", "$"), stats=result.stats)
    return written


def summary(result: RunResult, config: Config) -> str:
    currency = config.get("output.currency", "$")
    lines = [
        f"Quelle: {result.source}",
        "  ".join(f"{k}: {v}" for k, v in result.stats.items()),
        "",
    ]
    top = result.hits[: int(config.get("alerts.top_n", 15))]
    if top:
        lines.append("Top-Kandidaten:")
        lines += [notify.format_product_line(item, i, currency)
                  for i, item in enumerate(top, 1)]
    else:
        lines.append("Kein Produkt hat die Filter passiert - Filter lockern "
                     "(filters.revenue_min / commission_min / creators_max).")
    if result.alerts:
        lines.append(f"\n{len(result.alerts)} Alarm(e) versendet.")
    for path in result.reports.values():
        lines.append(f"Report: {path}")
    for error in result.errors:
        lines.append(f"FEHLER {error}")
    return "\n".join(lines)
