"""Test der Video-Idee: Lässt sich die Richtung der nächsten 15-Minuten-Kerze
besser als 50 % vorhersagen?

Je Markt werden einfache Regeln geprüft. Die beste Regel wird nur mit den
ersten 70 % der Daten ausgewählt und dann an den letzten 30 % gemessen,
die sie vorher nie gesehen hat.

Nötige Trefferquote:
- CFD bei eToro: Gewinn und Verlust sind die Kursbewegung, der Spread kostet bei
  jedem Trade. Lohnend ab 50 % + Kosten / (2 × durchschnittliche Bewegung).
- Up-or-Down-Kontrakt wie im Video: Gewinn zahlt das 0,85-Fache des Einsatzes,
  Verlust kostet den ganzen Einsatz. Lohnend ab 1 / 1,85 = 54,1 %.

Aufruf:
    python3 -m trading.candle15
"""

from . import config as cfg
from .analysis import _rsi, _sma
from .run import RESULTS
from .walkforward import load_history

MARKETS = ["BTC", "ETH", "SOL", "EURUSD", "GOLD", "OIL", "SPX500", "NSDQ100", "TSLA", "NVDA"]
START, END = "2025-10-01T00:00:00Z", "2026-09-29T00:00:00Z"
TRAIN_SHARE = 0.7
MIN_SIGNALS = 200
BINARY_PAYOUT = 0.85


def rules(closes: list[float]) -> dict:
    """Regeln: Index i -> Vorhersage +1 (höher), -1 (tiefer) oder 0 (keine)."""
    up = [0] + [1 if closes[i] > closes[i - 1] else -1 if closes[i] < closes[i - 1] else 0
                for i in range(1, len(closes))]
    rsi = _rsi(closes)
    sma20 = _sma(closes, 20)
    r = {
        "Momentum (wie letzte Kerze)": lambda i: up[i],
        "Umkehr (gegen letzte Kerze)": lambda i: -up[i],
        "Trend: über/unter 20er-Schnitt": lambda i: 0 if sma20[i] is None else
            (1 if closes[i] > sma20[i] else -1),
        "Gegen 20er-Schnitt": lambda i: 0 if sma20[i] is None else
            (-1 if closes[i] > sma20[i] else 1),
    }
    for k in (2, 3, 4, 5):
        def streak(i, k=k):
            if i < k or up[i] == 0 or any(up[i - j] != up[i] for j in range(k)):
                return 0
            return up[i]
        r[f"{k} gleiche Kerzen → weiter"] = streak
        r[f"{k} gleiche Kerzen → Umkehr"] = lambda i, s=streak: -s(i)
    for lo, hi in ((30, 70), (20, 80)):
        r[f"RSI {lo}/{hi} → Umkehr"] = lambda i, lo=lo, hi=hi: 0 if rsi[i] is None else (
            1 if rsi[i] < lo else -1 if rsi[i] > hi else 0)
        r[f"RSI {lo}/{hi} → Momentum"] = lambda i, lo=lo, hi=hi: 0 if rsi[i] is None else (
            -1 if rsi[i] < lo else 1 if rsi[i] > hi else 0)
    return r


def evaluate(closes, rule, lo, hi):
    hits = n = 0
    for i in range(max(lo, 1), hi - 1):
        p = rule(i)
        if p == 0 or closes[i + 1] == closes[i]:
            continue
        n += 1
        hits += (closes[i + 1] > closes[i]) == (p == 1)
    return hits, n


def main() -> None:
    cfg.CANDLE_INTERVAL = "FifteenMinutes"
    lines = [
        "# 15-Minuten-Richtung vorhersagen (Idee aus dem Video)",
        "",
        f"Kursdaten: eToro, 15-Minuten-Kerzen, {START[:10]} bis {END[:10]}. Je Markt wird die "
        f"beste von {len(rules([1.0] * 30))} Regeln mit den ersten {TRAIN_SHARE:.0%} der Daten "
        "gewählt und an den restlichen Daten geprüft.",
        "",
        "| Markt | Kerzen | Beste Regel (Training) | Treffer Training | Treffer Test (neu) "
        "| Signale im Test | nötig bei eToro (CFD) | nötig bei Up/Down (0,85×) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    all_test = []
    for sym in MARKETS:
        candles = load_history(sym, "FifteenMinutes", START, END)
        closes = [c["close"] for c in candles]
        split = int(len(closes) * TRAIN_SHARE)
        moves = [abs(closes[i + 1] / closes[i] - 1) for i in range(len(closes) - 1)]
        avg_move = sum(moves) / len(moves) * 100
        need_cfd = 50 + cfg.cost_for(sym) / (2 * avg_move) * 100
        need_bin = 100 / (1 + BINARY_PAYOUT)

        best = None
        for name, rule in rules(closes).items():
            h, n = evaluate(closes, rule, 1, split)
            if n >= MIN_SIGNALS and (best is None or h / n > best[1]):
                best = (name, h / n)
        name = best[0]
        h, n = evaluate(closes, rules(closes)[name], split, len(closes))
        test = h / n * 100 if n else 0
        all_test.append(test)
        lines.append(f"| {sym} | {len(closes)} | {name} | {best[1] * 100:.1f} % | **{test:.1f} %** "
                     f"| {n} | {min(need_cfd, 999):.1f} % | {need_bin:.1f} % |")
        print(f"{sym:8} {name:32} Training {best[1] * 100:5.1f} %  Test {test:5.1f} %  "
              f"(n={n})  nötig CFD {need_cfd:6.1f} %  Up/Down {need_bin:.1f} %")

    avg = sum(all_test) / len(all_test)
    lines += [
        "",
        f"**Durchschnitt Test: {avg:.1f} %** (Zufall wäre 50 %).",
        "",
        "„Nötig bei eToro“: Trefferquote, ab der die Regel nach Spread im Schnitt Gewinn macht. "
        "Liegt der Wert weit über 100 %, kostet der Spread mehr als eine typische "
        "15-Minuten-Bewegung, dann ist es bei jeder Trefferquote ein Verlustgeschäft.",
        "",
        "Kosten sind Schätzwerte (siehe `trading/config.py`).",
    ]
    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / "candle15.md"
    out.write_text("\n".join(lines) + "\n")
    print(f"\nDurchschnitt Test {avg:.1f} %\nBericht: {out}")


if __name__ == "__main__":
    main()
