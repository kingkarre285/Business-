"""Berichte: CSV fuer die Weiterverarbeitung, HTML zum Draufschauen."""

from __future__ import annotations

import csv
import html
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from .models import ScoredProduct
from .util import fmt_money, fmt_pct

CSV_COLUMNS = ["score", "name", "category", "shop", "price", "revenue", "units_sold",
               "commission_rate", "payout_per_sale", "creators", "videos", "rating",
               "momentum", "is_new", "reasons", "url", "product_id"]


def write_csv(items: List[ScoredProduct], path: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for item in items:
            product = item.product
            writer.writerow({
                "score": round(item.score, 1),
                "name": product.name,
                "category": product.category,
                "shop": product.shop,
                "price": product.price,
                "revenue": product.revenue,
                "units_sold": product.units_sold,
                "commission_rate": product.commission_rate,
                "payout_per_sale": product.payout_per_sale,
                "creators": product.creators,
                "videos": product.videos,
                "rating": product.rating,
                "momentum": item.momentum,
                "is_new": item.is_new,
                "reasons": " | ".join(item.reasons),
                "url": product.url,
                "product_id": product.product_id,
            })
    return path


def write_json(items: List[ScoredProduct], path: str) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump([item.to_dict() for item in items], handle, indent=2, ensure_ascii=False)
    return path


def write_html(items: List[ScoredProduct], path: str, *, currency: str = "$",
               stats: Dict[str, object] | None = None) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(render_html(items, currency=currency, stats=stats))
    return path


def render_html(items: List[ScoredProduct], *, currency: str = "$",
                stats: Dict[str, object] | None = None) -> str:
    """Ein Lauf als lesbare Seite - Ablesewerte oben, Rangliste darunter."""
    stamp = datetime.now().strftime("%d.%m.%Y, %H:%M")
    tiles = "".join(
        f'<div class="tile"><span class="tile-value">{html.escape(str(v))}</span>'
        f'<span class="tile-label">{html.escape(str(k))}</span></div>'
        for k, v in (stats or {}).items()
    )
    rows = "".join(_row(item, index, currency) for index, item in enumerate(items, 1))
    if not rows:
        rows = ('<p class="empty">Kein Produkt hat die Filter passiert. '
                'Schwellen mit <code>calibrate</code> an den Markt anpassen.</p>')

    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Produkt-Radar</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Source+Sans+3:wght@400;600&display=swap">
<style>
:root {{
  --ground:#f4f6f8; --surface:#ffffff; --ink:#141821; --muted:#5d6779;
  --line:#e2e6ec; --track:#eaedf2;
  --accent:#0e6fa8; --rising:#1f7a4d; --falling:#9e4a96;
  --shadow:0 1px 2px rgba(20,24,33,.06);
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#0f1217; --surface:#171b22; --ink:#e8ecf2; --muted:#98a2b3;
    --line:#252b35; --track:#232935;
    --accent:#3e9bdc; --rising:#2f9866; --falling:#be72c4;
    --shadow:none;
  }}
}}
:root[data-theme="dark"] {{
  --ground:#0f1217; --surface:#171b22; --ink:#e8ecf2; --muted:#98a2b3;
  --line:#252b35; --track:#232935;
  --accent:#3e9bdc; --rising:#2f9866; --falling:#be72c4;
  --shadow:none;
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0; padding:2.5rem 1.25rem 4rem; background:var(--ground); color:var(--ink);
  font:400 16px/1.55 "Source Sans 3", ui-sans-serif, system-ui, sans-serif;
  -webkit-font-smoothing:antialiased;
}}
.wrap {{ max-width:960px; margin:0 auto; }}
header {{ margin-bottom:1.75rem; }}
.eyebrow {{
  font:600 .72rem/1 "Archivo", ui-sans-serif, sans-serif; letter-spacing:.13em;
  text-transform:uppercase; color:var(--accent); margin:0 0 .5rem;
}}
h1 {{
  font:700 2rem/1.1 "Archivo", ui-sans-serif, sans-serif; letter-spacing:-.02em;
  margin:0 0 .35rem; text-wrap:balance;
}}
.run-meta {{ color:var(--muted); font-size:.92rem; margin:0; }}
.tiles {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(120px,1fr));
         gap:.6rem; margin:1.5rem 0 2rem; }}
.tile {{ background:var(--surface); border:1px solid var(--line); border-radius:8px;
        padding:.8rem .9rem; box-shadow:var(--shadow); }}
.tile-value {{
  display:block; font:600 1.5rem/1.1 "IBM Plex Mono", ui-monospace, monospace;
  font-variant-numeric:tabular-nums; letter-spacing:-.02em;
}}
.tile-label {{
  display:block; margin-top:.2rem; color:var(--muted);
  font:600 .68rem/1.3 "Archivo", sans-serif; letter-spacing:.1em; text-transform:uppercase;
}}
h2 {{
  font:600 .72rem/1 "Archivo", sans-serif; letter-spacing:.13em; text-transform:uppercase;
  color:var(--muted); margin:0 0 .75rem; padding-bottom:.6rem;
  border-bottom:1px solid var(--line);
}}
.list {{ display:flex; flex-direction:column; gap:.5rem; }}
.item {{
  display:grid; gap:.35rem 1rem; align-items:start;
  grid-template-columns:2.1rem minmax(0,1fr) 8.5rem 6.5rem;
  grid-template-areas:"rank name meter spark";
  background:var(--surface); border:1px solid var(--line); border-radius:8px;
  padding:.85rem 1rem; box-shadow:var(--shadow);
}}
.rank {{
  grid-area:rank; font:500 .95rem/1.5 "IBM Plex Mono", monospace;
  color:var(--muted); font-variant-numeric:tabular-nums;
}}
.name {{ grid-area:name; min-width:0; }}
.title {{ font:600 1rem/1.35 "Source Sans 3", sans-serif; margin:0; }}
.title a {{ color:inherit; text-decoration:none; }}
.title a:hover, .title a:focus-visible {{ text-decoration:underline; }}
a:focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; border-radius:2px; }}
.badge {{
  display:inline-block; margin-left:.4rem; vertical-align:1px;
  font:600 .63rem/1.6 "Archivo", sans-serif; letter-spacing:.07em; text-transform:uppercase;
  color:var(--surface); background:var(--accent); border-radius:3px; padding:0 .35rem;
}}
.origin {{ color:var(--muted); font-size:.84rem; margin:.15rem 0 .4rem; }}
.chips {{ display:flex; flex-wrap:wrap; gap:.3rem .9rem; }}
.chip {{ font-size:.84rem; color:var(--muted); white-space:nowrap; }}
.chip b {{
  font:500 .86rem "IBM Plex Mono", monospace; color:var(--ink);
  font-variant-numeric:tabular-nums; font-weight:500;
}}
.meter {{ grid-area:meter; }}
.meter-head {{ display:flex; align-items:baseline; justify-content:space-between; gap:.4rem; }}
.score {{
  font:600 1.4rem/1 "IBM Plex Mono", monospace; font-variant-numeric:tabular-nums;
  letter-spacing:-.02em;
}}
.score-max {{ color:var(--muted); font-size:.78rem; }}
.track {{ height:5px; border-radius:3px; background:var(--track); margin-top:.45rem;
         overflow:hidden; }}
.fill {{ height:100%; border-radius:3px; background:var(--accent); }}
.spark {{ grid-area:spark; }}
.spark svg {{ display:block; width:100%; height:30px; overflow:visible; }}
.delta {{
  font:500 .82rem/1.4 "IBM Plex Mono", monospace; font-variant-numeric:tabular-nums;
  margin-top:.2rem; display:block; text-align:right;
}}
.delta.up {{ color:var(--rising); }}
.delta.down {{ color:var(--falling); }}
.delta.flat {{ color:var(--muted); }}
.empty {{ background:var(--surface); border:1px solid var(--line); border-radius:8px;
         padding:1.25rem; color:var(--muted); }}
code {{ font:500 .88em "IBM Plex Mono", monospace;
        background:var(--track); border-radius:3px; padding:.1em .35em; }}
footer {{ color:var(--muted); font-size:.82rem; margin-top:2rem; padding-top:1rem;
         border-top:1px solid var(--line); }}
@media (max-width:760px) {{
  body {{ padding-top:1.75rem; }}
  h1 {{ font-size:1.6rem; }}
  .item {{
    grid-template-columns:2.1rem minmax(0,1fr) 5.5rem;
    grid-template-areas:"rank name meter" ". spark spark";
    row-gap:.6rem;
  }}
  .spark svg {{ height:26px; }}
  .delta {{ text-align:left; }}
}}
</style></head><body><div class="wrap">
<header>
  <p class="eyebrow">Kalodata Product Sniper</p>
  <h1>Treffer dieses Laufs</h1>
  <p class="run-meta">{stamp} &middot; {len(items)} Kandidaten gelistet</p>
</header>
<div class="tiles">{tiles}</div>
<h2>Rangliste nach Score</h2>
<div class="list">{rows}</div>
<footer>
  Score = gewichtete Kombination aus Momentum, Provision je Verkauf, Traktion,
  Wettbewerbsdichte, Effizienz und Frische. Die Kurve zeigt den Umsatzverlauf im
  abgefragten Zeitraum; die Prozentzahl daneben das Wachstum.
</footer>
</div></body></html>
"""


def render_fragment(items: List[ScoredProduct], *, currency: str = "$",
                    stats: Dict[str, object] | None = None) -> str:
    """Dieselbe Seite ohne aeussere Dokument-Tags.

    Fuer Umgebungen, die den Rahmen selbst setzen - etwa veroeffentlichte
    Artifacts, die den Inhalt in ihr eigenes Grundgeruest einsetzen.
    """
    page = render_html(items, currency=currency, stats=stats)
    head_start = page.index("<title>")
    head_end = page.index("</head>")
    body_start = page.index("<body>") + len("<body>")
    body_end = page.rindex("</body>")
    return page[head_start:head_end].rstrip() + "\n" + page[body_start:body_end].strip() + "\n"


def write_fragment(items: List[ScoredProduct], path: str, *, currency: str = "$",
                   stats: Dict[str, object] | None = None) -> str:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(render_fragment(items, currency=currency, stats=stats))
    return path


def _sparkline(series: Optional[List[float]], rising: bool) -> str:
    """Umsatzverlauf als SVG. Ohne Reihe bleibt der Platz leer, statt zu luegen."""
    values = [v for v in (series or []) if isinstance(v, (int, float))]
    if len(values) < 2:
        return '<svg viewBox="0 0 100 30" aria-hidden="true"></svg>'

    low, high = min(values), max(values)
    span = (high - low) or 1
    step = 100 / (len(values) - 1)
    points = [(index * step, 26 - (value - low) / span * 22)
              for index, value in enumerate(values)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    area = f"0,28 {line} 100,28"
    stroke = "var(--rising)" if rising else "var(--falling)"
    last_x, last_y = points[-1]
    return (
        f'<svg viewBox="0 0 100 30" preserveAspectRatio="none" role="img" '
        f'aria-label="Umsatzverlauf">'
        f'<polygon points="{area}" fill="{stroke}" opacity="0.12"></polygon>'
        f'<polyline points="{line}" fill="none" stroke="{stroke}" stroke-width="2" '
        f'stroke-linejoin="round" stroke-linecap="round" '
        f'vector-effect="non-scaling-stroke"></polyline>'
        f'<circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="2.6" fill="{stroke}" '
        f'stroke="var(--surface)" stroke-width="1.5" '
        f'vector-effect="non-scaling-stroke"></circle>'
        f'</svg>'
    )


def _row(item: ScoredProduct, index: int, currency: str) -> str:
    product = item.product
    name = html.escape(product.name.strip())
    if product.url:
        name = (f'<a href="{html.escape(product.url)}" target="_blank" '
                f'rel="noopener">{name}</a>')
    badge = '<span class="badge">neu</span>' if item.is_new else ""
    origin = " &middot; ".join(filter(None, [html.escape(product.category or ""),
                                            html.escape(product.shop or "")]))

    chips = []
    if product.revenue is not None:
        chips.append(f'<span class="chip">Umsatz <b>{fmt_money(product.revenue, currency)}</b></span>')
    if product.price is not None:
        chips.append(f'<span class="chip">Preis <b>{fmt_money(product.price, currency)}</b></span>')
    if product.payout_per_sale is not None:
        chips.append(f'<span class="chip">je Verkauf '
                     f'<b>{fmt_money(product.payout_per_sale, currency)}</b></span>')
    if product.commission_rate is not None:
        chips.append(f'<span class="chip">Provision <b>{fmt_pct(product.commission_rate)}</b></span>')
    if product.creators is not None:
        chips.append(f'<span class="chip">Creator <b>{product.creators:,.0f}</b></span>')

    momentum = item.momentum
    rising = bool(momentum is not None and momentum >= 0)
    if momentum is None:
        delta = '<span class="delta flat">kein Verlauf</span>'
    else:
        # Pfeil und Vorzeichen tragen die Aussage auch ohne Farbe
        arrow = "\u25b2" if momentum > 0.001 else ("\u25bc" if momentum < -0.001 else "\u2013")
        css = "up" if momentum > 0.001 else ("down" if momentum < -0.001 else "flat")
        delta = f'<span class="delta {css}">{arrow} {momentum * 100:+.0f}%</span>'

    return f"""<article class="item">
<span class="rank">{index:02d}</span>
<div class="name">
  <p class="title">{name}{badge}</p>
  <p class="origin">{origin}</p>
  <div class="chips">{"".join(chips)}</div>
</div>
<div class="meter">
  <div class="meter-head"><span class="score">{item.score:.0f}</span>
  <span class="score-max">von 100</span></div>
  <div class="track"><div class="fill" style="width:{max(3, min(100, item.score)):.0f}%"></div></div>
</div>
<div class="spark">{_sparkline(product.revenue_series, rising)}{delta}</div>
</article>"""
