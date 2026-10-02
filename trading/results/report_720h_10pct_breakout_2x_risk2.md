# Backtest: mindestens 10 % netto pro Trade (breakout)

Erstellt: 2026-10-02 08:29 UTC · Kursdaten: eToro, OneDay-Kerzen, 2022-09-02 bis 2026-10-02

## Regeln

- Ziel: +10 % auf den Einsatz **nach Kosten**, innerhalb von 720 Stunden
- Stop-Loss: −5 % des Einsatzes; Einsatz pro Trade: 40 % des Kontos
- Hebel: höchstens 2x
- Risiko pro Trade: 2.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Breakout über das Hoch / unter das Tief des Zeitfensters davor (720 Stunden)
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **977**, davon Ziel erreicht: **224** (22.9 %)
- Kapital gesamt: 2000 $ → **1803.71 $** (-9.8 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**
- Monate à 30 Tage (alle Märkte zusammen): **874**, davon Konto verdoppelt: **0**, im Plus: 234, im Minus: 376
- Beste(r) Monat: +14.8 %, schlechteste(r) Monat: -13.2 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 2x | 8.20 % | −0.50 % | 88.9 % | 52 | 7 | 45 | 0 | 56.00 $ | 45 % |
| ETH | 2x | 8.20 % | −0.50 % | 98.8 % | 54 | 7 | 47 | 0 | 54.23 $ | 48 % |
| SOL | 2x | 8.20 % | −0.50 % | 99.5 % | 56 | 6 | 50 | 0 | 48.58 $ | 51 % |
| XRP | 2x | 8.20 % | −0.50 % | 98.8 % | 37 | 4 | 33 | 0 | 62.27 $ | 39 % |
| DOGE | 2x | 8.20 % | −0.50 % | 98.4 % | 42 | 7 | 35 | 0 | 69.11 $ | 35 % |
| TSLA | 2x | 6.20 % | −2.20 % | 99.3 % | 62 | 21 | 41 | 0 | 109.91 $ | 20 % |
| NVDA | 2x | 6.20 % | −2.20 % | 97.1 % | 60 | 17 | 43 | 0 | 85.08 $ | 19 % |
| AMD | 2x | 6.20 % | −2.20 % | 99.7 % | 68 | 20 | 48 | 0 | 85.72 $ | 20 % |
| COIN | 2x | 6.20 % | −2.20 % | 100.0 % | 71 | 15 | 56 | 0 | 63.94 $ | 39 % |
| MSTR | 2x | 6.20 % | −2.20 % | 99.9 % | 76 | 26 | 50 | 0 | 118.93 $ | 17 % |
| PLTR | 2x | 6.20 % | −2.20 % | 99.6 % | 70 | 21 | 49 | 0 | 89.94 $ | 24 % |
| EURUSD | 2x | 5.32 % | −2.48 % | 2.4 % | 31 | 0 | 5 | 26 | 84.34 $ | 17 % |
| USDJPY | 2x | 5.32 % | −2.48 % | 8.9 % | 30 | 1 | 9 | 20 | 91.52 $ | 10 % |
| GBPJPY | 2x | 5.32 % | −2.48 % | 6.3 % | 29 | 2 | 8 | 19 | 94.83 $ | 14 % |
| GOLD | 2x | 5.70 % | −2.40 % | 51.3 % | 36 | 15 | 16 | 5 | 139.69 $ | 18 % |
| SILVER | 2x | 5.70 % | −2.40 % | 88.2 % | 53 | 21 | 31 | 1 | 128.00 $ | 24 % |
| OIL | 2x | 5.70 % | −2.40 % | 89.5 % | 41 | 14 | 25 | 2 | 109.39 $ | 12 % |
| SPX500 | 2x | 5.65 % | −2.45 % | 24.7 % | 35 | 4 | 13 | 18 | 108.27 $ | 9 % |
| NSDQ100 | 2x | 5.65 % | −2.45 % | 53.4 % | 40 | 10 | 20 | 10 | 113.76 $ | 14 % |
| GER40 | 2x | 5.65 % | −2.45 % | 28.6 % | 34 | 6 | 16 | 12 | 90.19 $ | 17 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 720 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
