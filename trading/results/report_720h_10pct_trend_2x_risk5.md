# Backtest: mindestens 10 % netto pro Trade (trend)

Erstellt: 2026-10-02 08:29 UTC · Kursdaten: eToro, OneDay-Kerzen, 2022-09-02 bis 2026-10-02

## Regeln

- Ziel: +10 % auf den Einsatz **nach Kosten**, innerhalb von 720 Stunden
- Stop-Loss: −5 % des Einsatzes; Einsatz pro Trade: 100 % des Kontos
- Hebel: höchstens 2x
- Risiko pro Trade: 5.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Trendfolge: Long, wenn Kurs > 50-Perioden-Schnitt > 200-Perioden-Schnitt; Short umgekehrt
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **2032**, davon Ziel erreicht: **406** (20.0 %)
- Kapital gesamt: 2000 $ → **1274.18 $** (-36.3 %)
- Märkte mit Totalverlust (< 1 % übrig): **5 von 20**
- Monate à 30 Tage (alle Märkte zusammen): **874**, davon Konto verdoppelt: **0**, im Plus: 208, im Minus: 342
- Beste(r) Monat: +86.6 %, schlechteste(r) Monat: -53.9 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 2x | 8.20 % | −0.50 % | 88.9 % | 109 | 6 | 103 | 0 | 0.96 $ | 99 % |
| ETH | 2x | 8.20 % | −0.50 % | 98.8 % | 106 | 5 | 101 | 0 | 0.98 $ | 99 % |
| SOL | 2x | 8.20 % | −0.50 % | 99.5 % | 116 | 8 | 108 | 0 | 0.99 $ | 99 % |
| XRP | 2x | 8.20 % | −0.50 % | 98.8 % | 106 | 5 | 101 | 0 | 1.00 $ | 99 % |
| DOGE | 2x | 8.20 % | −0.50 % | 98.4 % | 110 | 6 | 104 | 0 | 0.96 $ | 99 % |
| TSLA | 2x | 6.20 % | −2.20 % | 99.3 % | 140 | 26 | 114 | 0 | 2.86 $ | 97 % |
| NVDA | 2x | 6.20 % | −2.20 % | 97.1 % | 146 | 39 | 106 | 1 | 18.78 $ | 86 % |
| AMD | 2x | 6.20 % | −2.20 % | 99.7 % | 160 | 46 | 113 | 1 | 36.01 $ | 83 % |
| COIN | 2x | 6.20 % | −2.20 % | 100.0 % | 167 | 39 | 128 | 0 | 9.47 $ | 92 % |
| MSTR | 2x | 6.20 % | −2.20 % | 99.9 % | 212 | 59 | 153 | 0 | 24.03 $ | 88 % |
| PLTR | 2x | 6.20 % | −2.20 % | 99.6 % | 176 | 56 | 119 | 1 | 87.19 $ | 62 % |
| EURUSD | 2x | 5.32 % | −2.48 % | 2.4 % | 26 | 0 | 3 | 23 | 82.09 $ | 22 % |
| USDJPY | 2x | 5.32 % | −2.48 % | 8.9 % | 31 | 1 | 12 | 18 | 77.60 $ | 32 % |
| GBPJPY | 2x | 5.32 % | −2.48 % | 6.3 % | 33 | 0 | 9 | 24 | 78.24 $ | 29 % |
| GOLD | 2x | 5.70 % | −2.40 % | 51.3 % | 59 | 23 | 26 | 10 | 324.70 $ | 28 % |
| SILVER | 2x | 5.70 % | −2.40 % | 88.2 % | 105 | 37 | 65 | 3 | 157.58 $ | 60 % |
| OIL | 2x | 5.70 % | −2.40 % | 89.5 % | 103 | 30 | 70 | 3 | 61.75 $ | 73 % |
| SPX500 | 2x | 5.65 % | −2.45 % | 24.7 % | 41 | 3 | 19 | 19 | 104.64 $ | 26 % |
| NSDQ100 | 2x | 5.65 % | −2.45 % | 53.4 % | 47 | 11 | 25 | 11 | 118.57 $ | 26 % |
| GER40 | 2x | 5.65 % | −2.45 % | 28.6 % | 39 | 6 | 20 | 13 | 85.80 $ | 40 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 720 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
