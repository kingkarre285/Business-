"""Berichte: CSV fuer die Weiterverarbeitung, HTML zum Draufschauen."""

from __future__ import annotations

import csv
import html
import json
import os
from datetime import datetime
from typing import Dict, List

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
    stamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    stat_cards = "".join(
        f'<div class="stat"><span class="stat-value">{html.escape(str(v))}</span>'
        f'<span class="stat-label">{html.escape(str(k))}</span></div>'
        for k, v in (stats or {}).items()
    )
    return f"""<!doctype html>
<html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kalodata Sniper Report</title>
<style>
:root {{ --bg:#fbfaf9; --fg:#1c1b1a; --muted:#6b6663; --card:#fff; --line:#e6e2df;
        --accent:#c25a3a; --good:#2e7d5b; }}
@media (prefers-color-scheme: dark) {{
  :root {{ --bg:#171615; --fg:#eeeceb; --muted:#a09a96; --card:#211f1e; --line:#332f2d;
          --accent:#e08060; --good:#4fb389; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; padding:2rem 1.25rem; background:var(--bg); color:var(--fg);
        font:15px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif; }}
.wrap {{ max-width:1180px; margin:0 auto; }}
h1 {{ font-size:1.6rem; margin:0 0 .25rem; letter-spacing:-.01em; }}
.sub {{ color:var(--muted); margin:0 0 1.5rem; font-size:.9rem; }}
.stats {{ display:flex; flex-wrap:wrap; gap:.75rem; margin-bottom:1.5rem; }}
.stat {{ background:var(--card); border:1px solid var(--line); border-radius:10px;
         padding:.7rem 1rem; min-width:120px; }}
.stat-value {{ display:block; font-size:1.35rem; font-weight:600; }}
.stat-label {{ display:block; color:var(--muted); font-size:.75rem; text-transform:uppercase;
               letter-spacing:.06em; }}
.tablewrap {{ overflow-x:auto; background:var(--card); border:1px solid var(--line);
              border-radius:12px; }}
table {{ border-collapse:collapse; width:100%; font-size:.88rem; min-width:900px; }}
th, td {{ text-align:left; padding:.65rem .8rem; border-bottom:1px solid var(--line);
          vertical-align:top; }}
th {{ font-size:.72rem; text-transform:uppercase; letter-spacing:.06em; color:var(--muted);
      position:sticky; top:0; background:var(--card); }}
tr:last-child td {{ border-bottom:none; }}
td.num {{ text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }}
.score {{ font-weight:700; font-variant-numeric:tabular-nums; }}
.bar {{ height:4px; border-radius:2px; background:var(--accent); margin-top:.3rem; }}
.name {{ font-weight:600; max-width:340px; }}
.name a {{ color:inherit; text-decoration:none; border-bottom:1px solid var(--line); }}
.tags {{ color:var(--muted); font-size:.78rem; margin-top:.25rem; }}
.badge {{ display:inline-block; background:var(--good); color:#fff; border-radius:99px;
          padding:.05rem .45rem; font-size:.7rem; margin-left:.35rem; vertical-align:middle; }}
footer {{ color:var(--muted); font-size:.78rem; margin-top:1.5rem; }}
</style></head><body><div class="wrap">
<h1>Kalodata Product Sniper</h1>
<p class="sub">Lauf vom {stamp} · {len(items)} Treffer</p>
<div class="stats">{stat_cards}</div>
<div class="tablewrap"><table>
<thead><tr>
<th>Score</th><th>Produkt</th><th class="num">Preis</th><th class="num">Umsatz</th>
<th class="num">Verkäufe</th><th class="num">Provision</th><th class="num">Pro Verkauf</th>
<th class="num">Creator</th><th class="num">Momentum</th>
</tr></thead><tbody>
{"".join(_row(item, currency) for item in items) or '<tr><td colspan="9">Keine Treffer.</td></tr>'}
</tbody></table></div>
<footer>Erzeugt von kalodata_sniper · Score = gewichtete Kombination aus Momentum,
Provision, Traktion, Wettbewerbsdichte, Effizienz und Frische.</footer>
</div></body></html>
"""


def _row(item: ScoredProduct, currency: str) -> str:
    p = item.product
    name = html.escape(p.name)
    if p.url:
        name = f'<a href="{html.escape(p.url)}" target="_blank" rel="noopener">{name}</a>'
    badge = '<span class="badge">neu</span>' if item.is_new else ""
    tags = " · ".join(html.escape(r) for r in item.reasons[:3])
    meta = " · ".join(filter(None, [html.escape(p.category or ""), html.escape(p.shop or "")]))
    return f"""<tr>
<td><span class="score">{item.score:.0f}</span><div class="bar" style="width:{max(4, min(100, item.score)):.0f}%"></div></td>
<td class="name">{name}{badge}<div class="tags">{meta}</div><div class="tags">{tags}</div></td>
<td class="num">{fmt_money(p.price, currency)}</td>
<td class="num">{fmt_money(p.revenue, currency)}</td>
<td class="num">{"-" if p.units_sold is None else f"{p.units_sold:,.0f}"}</td>
<td class="num">{fmt_pct(p.commission_rate)}</td>
<td class="num">{fmt_money(p.payout_per_sale, currency)}</td>
<td class="num">{"-" if p.creators is None else f"{p.creators:,.0f}"}</td>
<td class="num">{fmt_pct(item.momentum)}</td>
</tr>"""
