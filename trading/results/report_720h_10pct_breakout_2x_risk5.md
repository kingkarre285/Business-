# Backtest: mindestens 10 % netto pro Trade (breakout)

Erstellt: 2026-10-02 08:29 UTC · Kursdaten: eToro, OneDay-Kerzen, 2022-09-02 bis 2026-10-02

## Regeln

- Ziel: +10 % auf den Einsatz **nach Kosten**, innerhalb von 720 Stunden
- Stop-Loss: −5 % des Einsatzes; Einsatz pro Trade: 100 % des Kontos
- Hebel: höchstens 2x
- Risiko pro Trade: 5.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Breakout über das Hoch / unter das Tief des Zeitfensters davor (720 Stunden)
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **977**, davon Ziel erreicht: **224** (22.9 %)
- Kapital gesamt: 2000 $ → **1644.19 $** (-17.8 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**
- Monate à 30 Tage (alle Märkte zusammen): **874**, davon Konto verdoppelt: **0**, im Plus: 234, im Minus: 376
- Beste(r) Monat: +39.5 %, schlechteste(r) Monat: -30.2 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 2x | 8.20 % | −0.50 % | 88.9 % | 52 | 7 | 45 | 0 | 22.02 $ | 79 % |
| ETH | 2x | 8.20 % | −0.50 % | 98.8 % | 54 | 7 | 47 | 0 | 20.28 $ | 81 % |
| SOL | 2x | 8.20 % | −0.50 % | 99.5 % | 56 | 6 | 50 | 0 | 15.43 $ | 85 % |
| XRP | 2x | 8.20 % | −0.50 % | 98.8 % | 37 | 4 | 33 | 0 | 29.33 $ | 71 % |
| DOGE | 2x | 8.20 % | −0.50 % | 98.4 % | 42 | 7 | 35 | 0 | 37.53 $ | 67 % |
| TSLA | 2x | 6.20 % | −2.20 % | 99.3 % | 62 | 21 | 41 | 0 | 113.14 $ | 44 % |
| NVDA | 2x | 6.20 % | −2.20 % | 97.1 % | 60 | 17 | 43 | 0 | 60.40 $ | 44 % |
| AMD | 2x | 6.20 % | −2.20 % | 99.7 % | 68 | 20 | 48 | 0 | 60.23 $ | 47 % |
| COIN | 2x | 6.20 % | −2.20 % | 100.0 % | 71 | 15 | 56 | 0 | 29.56 $ | 72 % |
| MSTR | 2x | 6.20 % | −2.20 % | 99.9 % | 76 | 26 | 50 | 0 | 134.40 $ | 37 % |
| PLTR | 2x | 6.20 % | −2.20 % | 99.6 % | 70 | 21 | 49 | 0 | 67.39 $ | 54 % |
| EURUSD | 2x | 5.32 % | −2.48 % | 2.4 % | 31 | 0 | 5 | 26 | 64.63 $ | 37 % |
| USDJPY | 2x | 5.32 % | −2.48 % | 8.9 % | 30 | 1 | 9 | 20 | 78.90 $ | 24 % |
| GBPJPY | 2x | 5.32 % | −2.48 % | 6.3 % | 29 | 2 | 8 | 19 | 86.09 $ | 32 % |
| GOLD | 2x | 5.70 % | −2.40 % | 51.3 % | 36 | 15 | 16 | 5 | 216.23 $ | 40 % |
| SILVER | 2x | 5.70 % | −2.40 % | 88.2 % | 53 | 21 | 31 | 1 | 168.57 $ | 50 % |
| OIL | 2x | 5.70 % | −2.40 % | 89.5 % | 41 | 14 | 25 | 2 | 117.06 $ | 30 % |
| SPX500 | 2x | 5.65 % | −2.45 % | 24.7 % | 35 | 4 | 13 | 18 | 118.11 $ | 22 % |
| NSDQ100 | 2x | 5.65 % | −2.45 % | 53.4 % | 40 | 10 | 20 | 10 | 130.44 $ | 33 % |
| GER40 | 2x | 5.65 % | −2.45 % | 28.6 % | 34 | 6 | 16 | 12 | 74.43 $ | 39 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 720 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
