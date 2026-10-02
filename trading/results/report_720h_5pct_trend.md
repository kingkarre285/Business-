# Backtest: mindestens 5 % netto pro Trade (trend)

Erstellt: 2026-10-02 08:27 UTC · Kursdaten: eToro, OneDay-Kerzen, 2022-09-02 bis 2026-10-02

## Regeln

- Ziel: +5 % auf den Einsatz **nach Kosten**, innerhalb von 720 Stunden
- Stop-Loss: −2 % des Einsatzes; Einsatz pro Trade: 40 % des Kontos
- Hebel: höchstens 1x (ohne Hebel)
- Risiko pro Trade: 1.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Trendfolge: Long, wenn Kurs > 50-Perioden-Schnitt > 200-Perioden-Schnitt; Short umgekehrt
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **2456**, davon Ziel erreicht: **437** (17.8 %)
- Kapital gesamt: 2000 $ → **1511.99 $** (-24.4 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**
- Monate à 30 Tage (alle Märkte zusammen): **874**, davon Konto verdoppelt: **0**, im Plus: 218, im Minus: 381
- Beste(r) Monat: +14.2 %, schlechteste(r) Monat: -14.1 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 1x | 8.20 % | −0.50 % | 88.9 % | 166 | 8 | 157 | 1 | 24.62 $ | 75 % |
| ETH | 1x | 8.20 % | −0.50 % | 98.8 % | 188 | 13 | 174 | 1 | 23.74 $ | 76 % |
| SOL | 1x | 8.20 % | −0.50 % | 99.5 % | 214 | 13 | 201 | 0 | 18.13 $ | 82 % |
| XRP | 1x | 8.20 % | −0.50 % | 98.8 % | 206 | 14 | 192 | 0 | 20.24 $ | 80 % |
| DOGE | 1x | 8.20 % | −0.50 % | 98.4 % | 197 | 13 | 184 | 0 | 21.41 $ | 79 % |
| TSLA | 1x | 6.20 % | −2.20 % | 99.3 % | 140 | 26 | 114 | 0 | 52.06 $ | 49 % |
| NVDA | 1x | 6.20 % | −2.20 % | 97.1 % | 146 | 39 | 106 | 1 | 76.80 $ | 28 % |
| AMD | 1x | 6.20 % | −2.20 % | 99.7 % | 160 | 46 | 113 | 1 | 87.73 $ | 28 % |
| COIN | 1x | 6.20 % | −2.20 % | 100.0 % | 167 | 39 | 128 | 0 | 66.73 $ | 36 % |
| MSTR | 1x | 6.20 % | −2.20 % | 99.9 % | 212 | 59 | 153 | 0 | 82.46 $ | 33 % |
| PLTR | 1x | 6.20 % | −2.20 % | 99.6 % | 176 | 56 | 119 | 1 | 105.68 $ | 16 % |
| EURUSD | 1x | 5.32 % | −2.48 % | 2.4 % | 26 | 0 | 3 | 23 | 96.31 $ | 5 % |
| USDJPY | 1x | 5.32 % | −2.48 % | 8.9 % | 31 | 1 | 12 | 18 | 95.50 $ | 7 % |
| GBPJPY | 1x | 5.32 % | −2.48 % | 6.3 % | 33 | 0 | 9 | 24 | 95.50 $ | 6 % |
| GOLD | 1x | 5.70 % | −2.40 % | 51.3 % | 59 | 23 | 26 | 10 | 129.97 $ | 6 % |
| SILVER | 1x | 5.70 % | −2.40 % | 88.2 % | 105 | 37 | 65 | 3 | 114.85 $ | 15 % |
| OIL | 1x | 5.70 % | −2.40 % | 89.5 % | 103 | 30 | 70 | 3 | 94.72 $ | 22 % |
| SPX500 | 1x | 5.65 % | −2.45 % | 24.7 % | 41 | 3 | 19 | 19 | 102.01 $ | 5 % |
| NSDQ100 | 1x | 5.65 % | −2.45 % | 53.4 % | 47 | 11 | 25 | 11 | 105.32 $ | 5 % |
| GER40 | 1x | 5.65 % | −2.45 % | 28.6 % | 39 | 6 | 20 | 13 | 98.21 $ | 9 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 720 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
