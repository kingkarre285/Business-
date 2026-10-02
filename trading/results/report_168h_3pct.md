# Backtest: mindestens 3 % netto pro Trade

Erstellt: 2026-10-02 08:23 UTC · Kursdaten: eToro, FourHours-Kerzen, 2026-01-08 bis 2026-10-02

## Regeln

- Ziel: +3 % auf den Einsatz **nach Kosten**, innerhalb von 168 Stunden
- Stop-Loss: −2 % des Einsatzes; Einsatz pro Trade: 67 % des Kontos
- Hebel: höchstens 1x (ohne Hebel)
- Risiko pro Trade: 1.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Breakout über das Hoch / unter das Tief der letzten 168 Stunden
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **447**, davon Ziel erreicht: **100** (22.4 %)
- Kapital gesamt: 2000 $ → **1944.29 $** (-2.8 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**
- Kalenderwochen (alle Märkte zusammen): **609**, davon Konto verdoppelt: **0**, im Plus: 118, im Minus: 197
- Beste Woche: +6.4 %, schlechteste Woche: -3.0 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 1x | 5.28 % | Kosten > Stop | 45.7 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| ETH | 1x | 5.28 % | Kosten > Stop | 64.3 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| SOL | 1x | 5.28 % | Kosten > Stop | 78.2 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| XRP | 1x | 5.28 % | Kosten > Stop | 79.2 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| DOGE | 1x | 5.28 % | Kosten > Stop | 82.4 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| TSLA | 1x | 3.51 % | −1.20 % | 94.7 % | 32 | 5 | 26 | 1 | 84.68 $ | 15 % |
| NVDA | 1x | 3.51 % | −1.20 % | 89.2 % | 37 | 10 | 27 | 0 | 92.54 $ | 12 % |
| AMD | 1x | 3.51 % | −1.20 % | 99.6 % | 37 | 9 | 28 | 0 | 90.88 $ | 13 % |
| COIN | 1x | 3.51 % | −1.20 % | 99.3 % | 37 | 10 | 27 | 0 | 94.02 $ | 9 % |
| MSTR | 1x | 3.51 % | −1.20 % | 99.4 % | 42 | 10 | 32 | 0 | 89.49 $ | 15 % |
| PLTR | 1x | 3.51 % | −1.20 % | 96.4 % | 38 | 10 | 28 | 0 | 92.84 $ | 9 % |
| EURUSD | 1x | 3.09 % | −1.48 % | 0.0 % | 19 | 0 | 1 | 18 | 97.07 $ | 3 % |
| USDJPY | 1x | 3.09 % | −1.48 % | 5.7 % | 21 | 0 | 3 | 18 | 98.28 $ | 3 % |
| GBPJPY | 1x | 3.09 % | −1.48 % | 4.3 % | 18 | 1 | 2 | 15 | 99.94 $ | 3 % |
| GOLD | 1x | 3.24 % | −1.40 % | 63.5 % | 26 | 11 | 14 | 1 | 109.58 $ | 4 % |
| SILVER | 1x | 3.24 % | −1.40 % | 98.1 % | 33 | 11 | 22 | 0 | 100.21 $ | 9 % |
| OIL | 1x | 3.24 % | −1.40 % | 99.8 % | 38 | 13 | 25 | 0 | 101.53 $ | 8 % |
| SPX500 | 1x | 3.19 % | −1.45 % | 18.8 % | 20 | 1 | 6 | 13 | 98.04 $ | 5 % |
| NSDQ100 | 1x | 3.19 % | −1.45 % | 49.8 % | 23 | 6 | 12 | 5 | 103.47 $ | 7 % |
| GER40 | 1x | 3.19 % | −1.45 % | 28.9 % | 26 | 3 | 15 | 8 | 91.71 $ | 9 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 168 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
