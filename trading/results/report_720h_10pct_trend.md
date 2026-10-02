# Backtest: mindestens 10 % netto pro Trade (trend)

Erstellt: 2026-10-02 08:27 UTC · Kursdaten: eToro, OneDay-Kerzen, 2022-09-02 bis 2026-10-02

## Regeln

- Ziel: +10 % auf den Einsatz **nach Kosten**, innerhalb von 720 Stunden
- Stop-Loss: −5 % des Einsatzes; Einsatz pro Trade: 20 % des Kontos
- Hebel: höchstens 1x (ohne Hebel)
- Risiko pro Trade: 1.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Trendfolge: Long, wenn Kurs > 50-Perioden-Schnitt > 200-Perioden-Schnitt; Short umgekehrt
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **1333**, davon Ziel erreicht: **283** (21.2 %)
- Kapital gesamt: 2000 $ → **1807.12 $** (-9.6 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**
- Monate à 30 Tage (alle Märkte zusammen): **874**, davon Konto verdoppelt: **0**, im Plus: 243, im Minus: 346
- Beste(r) Monat: +9.1 %, schlechteste(r) Monat: -6.9 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 1x | 13.20 % | −3.00 % | 56.4 % | 56 | 8 | 45 | 3 | 73.88 $ | 27 % |
| ETH | 1x | 13.20 % | −3.00 % | 87.3 % | 80 | 17 | 62 | 1 | 76.52 $ | 24 % |
| SOL | 1x | 13.20 % | −3.00 % | 93.6 % | 104 | 18 | 85 | 1 | 62.71 $ | 38 % |
| XRP | 1x | 13.20 % | −3.00 % | 81.3 % | 105 | 16 | 87 | 2 | 58.56 $ | 41 % |
| DOGE | 1x | 13.20 % | −3.00 % | 93.4 % | 100 | 21 | 79 | 0 | 70.47 $ | 33 % |
| TSLA | 1x | 11.20 % | −4.70 % | 81.3 % | 72 | 13 | 57 | 2 | 70.80 $ | 31 % |
| NVDA | 1x | 11.20 % | −4.70 % | 67.8 % | 72 | 19 | 48 | 5 | 90.32 $ | 14 % |
| AMD | 1x | 11.20 % | −4.70 % | 79.4 % | 93 | 33 | 58 | 2 | 109.59 $ | 11 % |
| COIN | 1x | 11.20 % | −4.70 % | 95.7 % | 105 | 25 | 80 | 0 | 71.87 $ | 34 % |
| MSTR | 1x | 11.20 % | −4.70 % | 95.1 % | 126 | 45 | 80 | 1 | 110.01 $ | 17 % |
| PLTR | 1x | 11.20 % | −4.70 % | 86.8 % | 98 | 34 | 63 | 1 | 100.87 $ | 12 % |
| EURUSD | 1x | 10.32 % | −4.98 % | 0.0 % | 26 | 0 | 0 | 26 | 97.56 $ | 3 % |
| USDJPY | 1x | 10.32 % | −4.98 % | 0.6 % | 29 | 0 | 2 | 27 | 95.44 $ | 6 % |
| GBPJPY | 1x | 10.32 % | −4.98 % | 1.1 % | 32 | 0 | 1 | 31 | 97.84 $ | 3 % |
| GOLD | 1x | 10.70 % | −4.90 % | 14.2 % | 36 | 4 | 9 | 23 | 108.70 $ | 4 % |
| SILVER | 1x | 10.70 % | −4.90 % | 46.6 % | 55 | 17 | 28 | 10 | 113.07 $ | 6 % |
| OIL | 1x | 10.70 % | −4.90 % | 44.5 % | 47 | 11 | 27 | 9 | 96.34 $ | 8 % |
| SPX500 | 1x | 10.65 % | −4.95 % | 3.5 % | 31 | 0 | 5 | 26 | 101.83 $ | 2 % |
| NSDQ100 | 1x | 10.65 % | −4.95 % | 12.6 % | 36 | 2 | 13 | 21 | 101.25 $ | 3 % |
| GER40 | 1x | 10.65 % | −4.95 % | 4.3 % | 30 | 0 | 5 | 25 | 99.48 $ | 4 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 720 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
