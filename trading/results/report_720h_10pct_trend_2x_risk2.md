# Backtest: mindestens 10 % netto pro Trade (trend)

Erstellt: 2026-10-02 08:29 UTC · Kursdaten: eToro, OneDay-Kerzen, 2022-09-02 bis 2026-10-02

## Regeln

- Ziel: +10 % auf den Einsatz **nach Kosten**, innerhalb von 720 Stunden
- Stop-Loss: −5 % des Einsatzes; Einsatz pro Trade: 40 % des Kontos
- Hebel: höchstens 2x
- Risiko pro Trade: 2.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Trendfolge: Long, wenn Kurs > 50-Perioden-Schnitt > 200-Perioden-Schnitt; Short umgekehrt
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **2456**, davon Ziel erreicht: **437** (17.8 %)
- Kapital gesamt: 2000 $ → **1362.62 $** (-31.9 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**
- Monate à 30 Tage (alle Märkte zusammen): **874**, davon Konto verdoppelt: **0**, im Plus: 216, im Minus: 383
- Beste(r) Monat: +29.8 %, schlechteste(r) Monat: -26.3 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 2x | 8.20 % | −0.50 % | 88.9 % | 166 | 8 | 157 | 1 | 5.93 $ | 94 % |
| ETH | 2x | 8.20 % | −0.50 % | 98.8 % | 188 | 13 | 174 | 1 | 5.50 $ | 95 % |
| SOL | 2x | 8.20 % | −0.50 % | 99.5 % | 214 | 13 | 201 | 0 | 3.19 $ | 97 % |
| XRP | 2x | 8.20 % | −0.50 % | 98.8 % | 206 | 14 | 192 | 0 | 3.99 $ | 96 % |
| DOGE | 2x | 8.20 % | −0.50 % | 98.4 % | 197 | 13 | 184 | 0 | 4.46 $ | 96 % |
| TSLA | 2x | 6.20 % | −2.20 % | 99.3 % | 140 | 26 | 114 | 0 | 26.32 $ | 75 % |
| NVDA | 2x | 6.20 % | −2.20 % | 97.1 % | 146 | 39 | 106 | 1 | 56.93 $ | 49 % |
| AMD | 2x | 6.20 % | −2.20 % | 99.7 % | 160 | 46 | 113 | 1 | 74.14 $ | 48 % |
| COIN | 2x | 6.20 % | −2.20 % | 100.0 % | 167 | 39 | 128 | 0 | 43.04 $ | 60 % |
| MSTR | 2x | 6.20 % | −2.20 % | 99.9 % | 212 | 59 | 153 | 0 | 64.87 $ | 56 % |
| PLTR | 2x | 6.20 % | −2.20 % | 99.6 % | 176 | 56 | 119 | 1 | 107.06 $ | 30 % |
| EURUSD | 2x | 5.32 % | −2.48 % | 2.4 % | 26 | 0 | 3 | 23 | 92.67 $ | 9 % |
| USDJPY | 2x | 5.32 % | −2.48 % | 8.9 % | 31 | 1 | 12 | 18 | 90.98 $ | 14 % |
| GBPJPY | 2x | 5.32 % | −2.48 % | 6.3 % | 33 | 0 | 9 | 24 | 91.07 $ | 13 % |
| GOLD | 2x | 5.70 % | −2.40 % | 51.3 % | 59 | 23 | 26 | 10 | 166.64 $ | 12 % |
| SILVER | 2x | 5.70 % | −2.40 % | 88.2 % | 105 | 37 | 65 | 3 | 128.74 $ | 29 % |
| OIL | 2x | 5.70 % | −2.40 % | 89.5 % | 103 | 30 | 70 | 3 | 87.81 $ | 39 % |
| SPX500 | 2x | 5.65 % | −2.45 % | 24.7 % | 41 | 3 | 19 | 19 | 103.50 $ | 10 % |
| NSDQ100 | 2x | 5.65 % | −2.45 % | 53.4 % | 47 | 11 | 25 | 11 | 109.92 $ | 11 % |
| GER40 | 2x | 5.65 % | −2.45 % | 28.6 % | 39 | 6 | 20 | 13 | 95.84 $ | 18 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 720 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
