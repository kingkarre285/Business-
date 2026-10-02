# Backtest: mindestens 5 % netto pro Trade

Erstellt: 2026-10-02 08:25 UTC · Kursdaten: eToro, OneDay-Kerzen, 2022-09-02 bis 2026-10-02

## Regeln

- Ziel: +5 % auf den Einsatz **nach Kosten**, innerhalb von 720 Stunden
- Stop-Loss: −2 % des Einsatzes; Einsatz pro Trade: 40 % des Kontos
- Hebel: höchstens 1x (ohne Hebel)
- Risiko pro Trade: 1.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Breakout über das Hoch / unter das Tief der letzten 720 Stunden
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **977**, davon Ziel erreicht: **224** (22.9 %)
- Kapital gesamt: 2000 $ → **1889.27 $** (-5.5 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**
- Monate à 30 Tage (alle Märkte zusammen): **874**, davon Konto verdoppelt: **0**, im Plus: 234, im Minus: 376
- Beste(r) Monat: +7.2 %, schlechteste(r) Monat: -6.8 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 1x | 8.20 % | −0.50 % | 88.9 % | 52 | 7 | 45 | 0 | 75.15 $ | 26 % |
| ETH | 1x | 8.20 % | −0.50 % | 98.8 % | 54 | 7 | 47 | 0 | 73.97 $ | 27 % |
| SOL | 1x | 8.20 % | −0.50 % | 99.5 % | 56 | 6 | 50 | 0 | 70.00 $ | 30 % |
| XRP | 1x | 8.20 % | −0.50 % | 98.8 % | 37 | 4 | 33 | 0 | 79.14 $ | 22 % |
| DOGE | 1x | 8.20 % | −0.50 % | 98.4 % | 42 | 7 | 35 | 0 | 83.45 $ | 19 % |
| TSLA | 1x | 6.20 % | −2.20 % | 99.3 % | 62 | 21 | 41 | 0 | 105.65 $ | 10 % |
| NVDA | 1x | 6.20 % | −2.20 % | 97.1 % | 60 | 17 | 43 | 0 | 92.87 $ | 10 % |
| AMD | 1x | 6.20 % | −2.20 % | 99.7 % | 68 | 20 | 48 | 0 | 93.36 $ | 10 % |
| COIN | 1x | 6.20 % | −2.20 % | 100.0 % | 71 | 15 | 56 | 0 | 80.51 $ | 21 % |
| MSTR | 1x | 6.20 % | −2.20 % | 99.9 % | 76 | 26 | 50 | 0 | 110.10 $ | 9 % |
| PLTR | 1x | 6.20 % | −2.20 % | 99.6 % | 70 | 21 | 49 | 0 | 95.67 $ | 13 % |
| EURUSD | 1x | 5.32 % | −2.48 % | 2.4 % | 31 | 0 | 5 | 26 | 91.91 $ | 9 % |
| USDJPY | 1x | 5.32 % | −2.48 % | 8.9 % | 30 | 1 | 9 | 20 | 95.76 $ | 5 % |
| GBPJPY | 1x | 5.32 % | −2.48 % | 6.3 % | 29 | 2 | 8 | 19 | 97.49 $ | 7 % |
| GOLD | 1x | 5.70 % | −2.40 % | 51.3 % | 36 | 15 | 16 | 5 | 118.72 $ | 10 % |
| SILVER | 1x | 5.70 % | −2.40 % | 88.2 % | 53 | 21 | 31 | 1 | 113.88 $ | 13 % |
| OIL | 1x | 5.70 % | −2.40 % | 89.5 % | 41 | 14 | 25 | 2 | 105.07 $ | 6 % |
| SPX500 | 1x | 5.65 % | −2.45 % | 24.7 % | 35 | 4 | 13 | 18 | 104.28 $ | 5 % |
| NSDQ100 | 1x | 5.65 % | −2.45 % | 53.4 % | 40 | 10 | 20 | 10 | 107.07 $ | 7 % |
| GER40 | 1x | 5.65 % | −2.45 % | 28.6 % | 34 | 6 | 16 | 12 | 95.21 $ | 9 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 720 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
