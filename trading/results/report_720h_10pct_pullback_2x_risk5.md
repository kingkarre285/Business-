# Backtest: mindestens 10 % netto pro Trade (pullback)

Erstellt: 2026-10-02 08:29 UTC · Kursdaten: eToro, OneDay-Kerzen, 2022-09-02 bis 2026-10-02

## Regeln

- Ziel: +10 % auf den Einsatz **nach Kosten**, innerhalb von 720 Stunden
- Stop-Loss: −5 % des Einsatzes; Einsatz pro Trade: 100 % des Kontos
- Hebel: höchstens 2x
- Risiko pro Trade: 5.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Rücksetzer: Long bei RSI(14) < 30 über dem 200-Perioden-Schnitt; Short bei RSI(14) > 70 darunter
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **48**, davon Ziel erreicht: **12** (25.0 %)
- Kapital gesamt: 2000 $ → **1976.38 $** (-1.2 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**
- Monate à 30 Tage (alle Märkte zusammen): **874**, davon Konto verdoppelt: **0**, im Plus: 13, im Minus: 17
- Beste(r) Monat: +12.2 %, schlechteste(r) Monat: -22.7 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 2x | 8.20 % | −0.50 % | 88.9 % | 4 | 1 | 3 | 0 | 96.03 $ | 10 % |
| ETH | 2x | 8.20 % | −0.50 % | 98.8 % | 5 | 0 | 5 | 0 | 77.31 $ | 23 % |
| SOL | 2x | 8.20 % | −0.50 % | 99.5 % | 4 | 1 | 3 | 0 | 96.16 $ | 14 % |
| XRP | 2x | 8.20 % | −0.50 % | 98.8 % | 2 | 0 | 2 | 0 | 90.25 $ | 10 % |
| DOGE | 2x | 8.20 % | −0.50 % | 98.4 % | 9 | 1 | 8 | 0 | 74.57 $ | 30 % |
| TSLA | 2x | 6.20 % | −2.20 % | 99.3 % | 4 | 2 | 2 | 0 | 112.44 $ | 10 % |
| NVDA | 2x | 6.20 % | −2.20 % | 97.1 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| AMD | 2x | 6.20 % | −2.20 % | 99.7 % | 2 | 2 | 0 | 0 | 124.19 $ | 0 % |
| COIN | 2x | 6.20 % | −2.20 % | 100.0 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| MSTR | 2x | 6.20 % | −2.20 % | 99.9 % | 7 | 2 | 5 | 0 | 96.72 $ | 19 % |
| PLTR | 2x | 6.20 % | −2.20 % | 99.6 % | 1 | 1 | 0 | 0 | 111.68 $ | 0 % |
| EURUSD | 2x | 5.32 % | −2.48 % | 2.4 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| USDJPY | 2x | 5.32 % | −2.48 % | 8.9 % | 4 | 0 | 2 | 2 | 96.92 $ | 10 % |
| GBPJPY | 2x | 5.32 % | −2.48 % | 6.3 % | 1 | 0 | 1 | 0 | 94.90 $ | 5 % |
| GOLD | 2x | 5.70 % | −2.40 % | 51.3 % | 2 | 1 | 1 | 0 | 105.49 $ | 5 % |
| SILVER | 2x | 5.70 % | −2.40 % | 88.2 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| OIL | 2x | 5.70 % | −2.40 % | 89.5 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| SPX500 | 2x | 5.65 % | −2.45 % | 24.7 % | 1 | 0 | 1 | 0 | 94.08 $ | 6 % |
| NSDQ100 | 2x | 5.65 % | −2.45 % | 53.4 % | 1 | 1 | 0 | 0 | 110.64 $ | 0 % |
| GER40 | 2x | 5.65 % | −2.45 % | 28.6 % | 1 | 0 | 1 | 0 | 95.00 $ | 5 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 720 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
