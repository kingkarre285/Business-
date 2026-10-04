# 15-Minuten-Richtung vorhersagen (Idee aus dem Video)

Kursdaten: eToro, 15-Minuten-Kerzen, 2025-10-01 bis 2026-09-29. Je Markt wird die beste von 16 Regeln mit den ersten 70% der Daten gewählt und an den restlichen Daten geprüft.

| Markt | Kerzen | Beste Regel (Training) | Treffer Training | Treffer Test (neu) | Signale im Test | nötig bei eToro (CFD) | nötig bei Up/Down (0,85×) |
|---|---|---|---|---|---|---|---|
| BTC | 34837 | RSI 30/70 → Umkehr | 55.8 % | **53.4 %** | 933 | 695.1 % | 54.1 % |
| ETH | 34836 | 5 gleiche Kerzen → Umkehr | 60.3 % | **58.0 %** | 462 | 531.6 % | 54.1 % |
| SOL | 34833 | 5 gleiche Kerzen → Umkehr | 55.4 % | **58.1 %** | 449 | 465.1 % | 54.1 % |
| EURUSD | 25301 | 5 gleiche Kerzen → Umkehr | 55.1 % | **51.3 %** | 314 | 91.5 % | 54.1 % |
| GOLD | 24534 | 5 gleiche Kerzen → Umkehr | 55.0 % | **55.9 %** | 363 | 94.3 % | 54.1 % |
| OIL | 24101 | RSI 20/80 → Umkehr | 53.5 % | **48.8 %** | 80 | 74.3 % | 54.1 % |
| SPX500 | 24137 | 4 gleiche Kerzen → Umkehr | 51.4 % | **49.2 %** | 801 | 95.6 % | 54.1 % |
| NSDQ100 | 24526 | RSI 20/80 → Umkehr | 55.5 % | **40.5 %** | 131 | 81.3 % | 54.1 % |
| TSLA | 23039 | 5 gleiche Kerzen → Umkehr | 55.0 % | **52.2 %** | 347 | 140.8 % | 54.1 % |
| NVDA | 23056 | 5 gleiche Kerzen → Umkehr | 57.6 % | **58.2 %** | 299 | 148.7 % | 54.1 % |

**Durchschnitt Test: 52.5 %** (Zufall wäre 50 %).

„Nötig bei eToro“: Trefferquote, ab der die Regel nach Spread im Schnitt Gewinn macht. Liegt der Wert weit über 100 %, kostet der Spread mehr als eine typische 15-Minuten-Bewegung, dann ist es bei jeder Trefferquote ein Verlustgeschäft.

Kosten sind Schätzwerte (siehe `trading/config.py`).
