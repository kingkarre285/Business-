# Backtest: mindestens 3 % netto pro Trade

Erstellt: 2026-10-02 08:23 UTC · Kursdaten: eToro, OneHour-Kerzen, 2026-07-24 bis 2026-10-02

## Regeln

- Ziel: +3 % auf den Einsatz **nach Kosten**, innerhalb von 24 Stunden
- Stop-Loss: −2 % des Einsatzes; Einsatz pro Trade: 67 % des Kontos
- Hebel: höchstens 1x (ohne Hebel)
- Risiko pro Trade: 1.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Breakout über das Hoch / unter das Tief der letzten 24 Stunden
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **473**, davon Ziel erreicht: **44** (9.3 %)
- Kapital gesamt: 2000 $ → **1943.71 $** (-2.8 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**
- Kalenderwochen (alle Märkte zusammen): **137**, davon Konto verdoppelt: **0**, im Plus: 44, im Minus: 68
- Beste Woche: +4.1 %, schlechteste Woche: -5.3 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 1x | 5.04 % | Kosten > Stop | 6.9 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| ETH | 1x | 5.04 % | Kosten > Stop | 12.3 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| SOL | 1x | 5.04 % | Kosten > Stop | 24.2 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| XRP | 1x | 5.04 % | Kosten > Stop | 33.6 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| DOGE | 1x | 5.04 % | Kosten > Stop | 33.8 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| TSLA | 1x | 3.33 % | −1.20 % | 25.4 % | 31 | 3 | 19 | 9 | 89.69 $ | 11 % |
| NVDA | 1x | 3.33 % | −1.20 % | 16.0 % | 28 | 2 | 10 | 16 | 103.48 $ | 5 % |
| AMD | 1x | 3.33 % | −1.20 % | 44.4 % | 40 | 8 | 25 | 7 | 94.80 $ | 9 % |
| COIN | 1x | 3.33 % | −1.20 % | 59.2 % | 43 | 7 | 32 | 4 | 83.88 $ | 16 % |
| MSTR | 1x | 3.33 % | −1.20 % | 76.3 % | 42 | 11 | 29 | 2 | 93.89 $ | 10 % |
| PLTR | 1x | 3.33 % | −1.20 % | 36.7 % | 37 | 5 | 21 | 11 | 95.46 $ | 7 % |
| EURUSD | 1x | 3.03 % | −1.48 % | 0.0 % | 24 | 0 | 0 | 24 | 100.30 $ | 1 % |
| USDJPY | 1x | 3.03 % | −1.48 % | 0.0 % | 26 | 0 | 0 | 26 | 101.79 $ | 1 % |
| GBPJPY | 1x | 3.03 % | −1.48 % | 0.0 % | 27 | 0 | 0 | 27 | 100.41 $ | 1 % |
| GOLD | 1x | 3.12 % | −1.40 % | 3.8 % | 27 | 1 | 3 | 23 | 99.53 $ | 3 % |
| SILVER | 1x | 3.12 % | −1.40 % | 25.2 % | 27 | 3 | 14 | 10 | 97.95 $ | 3 % |
| OIL | 1x | 3.12 % | −1.40 % | 38.8 % | 37 | 4 | 22 | 11 | 89.46 $ | 13 % |
| SPX500 | 1x | 3.07 % | −1.45 % | 0.0 % | 27 | 0 | 1 | 26 | 97.73 $ | 3 % |
| NSDQ100 | 1x | 3.07 % | −1.45 % | 0.1 % | 28 | 0 | 2 | 26 | 94.11 $ | 6 % |
| GER40 | 1x | 3.07 % | −1.45 % | 0.0 % | 29 | 0 | 0 | 29 | 101.21 $ | 1 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 24 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
