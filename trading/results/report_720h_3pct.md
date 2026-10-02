# Backtest: mindestens 3 % netto pro Trade

Erstellt: 2026-10-02 08:25 UTC · Kursdaten: eToro, OneDay-Kerzen, 2022-09-02 bis 2026-10-02

## Regeln

- Ziel: +3 % auf den Einsatz **nach Kosten**, innerhalb von 720 Stunden
- Stop-Loss: −2 % des Einsatzes; Einsatz pro Trade: 67 % des Kontos
- Hebel: höchstens 1x (ohne Hebel)
- Risiko pro Trade: 1.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Breakout über das Hoch / unter das Tief der letzten 720 Stunden
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **866**, davon Ziel erreicht: **206** (23.8 %)
- Kapital gesamt: 2000 $ → **1879.52 $** (-6.0 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**
- Monate à 30 Tage (alle Märkte zusammen): **874**, davon Konto verdoppelt: **0**, im Plus: 178, im Minus: 316
- Beste(r) Monat: +9.5 %, schlechteste(r) Monat: -4.9 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 1x | 6.20 % | Kosten > Stop | 95.9 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| ETH | 1x | 6.20 % | Kosten > Stop | 99.5 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| SOL | 1x | 6.20 % | Kosten > Stop | 99.8 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| XRP | 1x | 6.20 % | Kosten > Stop | 100.0 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| DOGE | 1x | 6.20 % | Kosten > Stop | 99.9 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| TSLA | 1x | 4.20 % | −1.20 % | 100.0 % | 74 | 17 | 57 | 0 | 86.78 $ | 20 % |
| NVDA | 1x | 4.20 % | −1.20 % | 99.9 % | 77 | 14 | 63 | 0 | 74.29 $ | 26 % |
| AMD | 1x | 4.20 % | −1.20 % | 100.0 % | 78 | 17 | 61 | 0 | 79.74 $ | 22 % |
| COIN | 1x | 4.20 % | −1.20 % | 100.0 % | 72 | 16 | 56 | 0 | 85.46 $ | 15 % |
| MSTR | 1x | 4.20 % | −1.20 % | 100.0 % | 80 | 18 | 62 | 0 | 84.48 $ | 20 % |
| PLTR | 1x | 4.20 % | −1.20 % | 100.0 % | 78 | 21 | 57 | 0 | 95.07 $ | 11 % |
| EURUSD | 1x | 3.32 % | −1.48 % | 14.9 % | 33 | 3 | 15 | 15 | 91.95 $ | 9 % |
| USDJPY | 1x | 3.32 % | −1.48 % | 46.6 % | 37 | 4 | 25 | 8 | 87.92 $ | 12 % |
| GBPJPY | 1x | 3.32 % | −1.48 % | 34.8 % | 30 | 4 | 12 | 14 | 97.34 $ | 9 % |
| GOLD | 1x | 3.70 % | −1.40 % | 76.9 % | 48 | 19 | 27 | 2 | 115.76 $ | 12 % |
| SILVER | 1x | 3.70 % | −1.40 % | 98.6 % | 67 | 17 | 50 | 0 | 89.32 $ | 19 % |
| OIL | 1x | 3.70 % | −1.40 % | 98.6 % | 48 | 17 | 31 | 0 | 107.53 $ | 8 % |
| SPX500 | 1x | 3.65 % | −1.45 % | 62.6 % | 46 | 10 | 30 | 6 | 90.88 $ | 13 % |
| NSDQ100 | 1x | 3.65 % | −1.45 % | 85.6 % | 53 | 18 | 34 | 1 | 104.33 $ | 7 % |
| GER40 | 1x | 3.65 % | −1.45 % | 68.1 % | 45 | 11 | 32 | 2 | 88.68 $ | 14 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 720 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
