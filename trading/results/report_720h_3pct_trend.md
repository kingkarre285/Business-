# Backtest: mindestens 3 % netto pro Trade (trend)

Erstellt: 2026-10-02 08:27 UTC · Kursdaten: eToro, OneDay-Kerzen, 2022-09-02 bis 2026-10-02

## Regeln

- Ziel: +3 % auf den Einsatz **nach Kosten**, innerhalb von 720 Stunden
- Stop-Loss: −2 % des Einsatzes; Einsatz pro Trade: 67 % des Kontos
- Hebel: höchstens 1x (ohne Hebel)
- Risiko pro Trade: 1.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Trendfolge: Long, wenn Kurs > 50-Perioden-Schnitt > 200-Perioden-Schnitt; Short umgekehrt
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **1991**, davon Ziel erreicht: **484** (24.3 %)
- Kapital gesamt: 2000 $ → **1791.01 $** (-10.4 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**
- Monate à 30 Tage (alle Märkte zusammen): **874**, davon Konto verdoppelt: **0**, im Plus: 200, im Minus: 290
- Beste(r) Monat: +17.2 %, schlechteste(r) Monat: -8.7 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 1x | 6.20 % | Kosten > Stop | 95.9 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| ETH | 1x | 6.20 % | Kosten > Stop | 99.5 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| SOL | 1x | 6.20 % | Kosten > Stop | 99.8 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| XRP | 1x | 6.20 % | Kosten > Stop | 100.0 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| DOGE | 1x | 6.20 % | Kosten > Stop | 99.9 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| TSLA | 1x | 4.20 % | −1.20 % | 100.0 % | 177 | 27 | 150 | 0 | 40.38 $ | 61 % |
| NVDA | 1x | 4.20 % | −1.20 % | 99.9 % | 205 | 52 | 152 | 1 | 76.96 $ | 34 % |
| AMD | 1x | 4.20 % | −1.20 % | 100.0 % | 197 | 42 | 154 | 1 | 58.70 $ | 43 % |
| COIN | 1x | 4.20 % | −1.20 % | 100.0 % | 194 | 39 | 155 | 0 | 56.87 $ | 49 % |
| MSTR | 1x | 4.20 % | −1.20 % | 100.0 % | 246 | 58 | 188 | 0 | 65.49 $ | 37 % |
| PLTR | 1x | 4.20 % | −1.20 % | 100.0 % | 240 | 71 | 168 | 1 | 104.17 $ | 20 % |
| EURUSD | 1x | 3.32 % | −1.48 % | 14.9 % | 27 | 1 | 8 | 18 | 94.16 $ | 7 % |
| USDJPY | 1x | 3.32 % | −1.48 % | 46.6 % | 40 | 6 | 22 | 12 | 97.26 $ | 9 % |
| GBPJPY | 1x | 3.32 % | −1.48 % | 34.8 % | 38 | 3 | 16 | 19 | 98.75 $ | 7 % |
| GOLD | 1x | 3.70 % | −1.40 % | 76.9 % | 98 | 39 | 57 | 2 | 133.51 $ | 9 % |
| SILVER | 1x | 3.70 % | −1.40 % | 98.6 % | 168 | 52 | 115 | 1 | 104.92 $ | 15 % |
| OIL | 1x | 3.70 % | −1.40 % | 98.6 % | 156 | 36 | 120 | 0 | 68.22 $ | 37 % |
| SPX500 | 1x | 3.65 % | −1.45 % | 62.6 % | 59 | 16 | 35 | 8 | 100.35 $ | 13 % |
| NSDQ100 | 1x | 3.65 % | −1.45 % | 85.6 % | 84 | 25 | 55 | 4 | 99.55 $ | 11 % |
| GER40 | 1x | 3.65 % | −1.45 % | 68.1 % | 62 | 17 | 42 | 3 | 91.71 $ | 11 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 720 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
