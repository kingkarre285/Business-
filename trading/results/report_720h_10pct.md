# Backtest: mindestens 10 % netto pro Trade (breakout)

Erstellt: 2026-10-02 08:27 UTC · Kursdaten: eToro, OneDay-Kerzen, 2022-09-02 bis 2026-10-02

## Regeln

- Ziel: +10 % auf den Einsatz **nach Kosten**, innerhalb von 720 Stunden
- Stop-Loss: −5 % des Einsatzes; Einsatz pro Trade: 20 % des Kontos
- Hebel: höchstens 1x (ohne Hebel)
- Risiko pro Trade: 1.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Breakout über das Hoch / unter das Tief des Zeitfensters davor (720 Stunden)
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **786**, davon Ziel erreicht: **174** (22.1 %)
- Kapital gesamt: 2000 $ → **1957.20 $** (-2.1 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**
- Monate à 30 Tage (alle Märkte zusammen): **874**, davon Konto verdoppelt: **0**, im Plus: 238, im Minus: 335
- Beste(r) Monat: +4.8 %, schlechteste(r) Monat: -3.3 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 1x | 13.20 % | −3.00 % | 56.4 % | 39 | 10 | 28 | 1 | 93.51 $ | 9 % |
| ETH | 1x | 13.20 % | −3.00 % | 87.3 % | 43 | 12 | 31 | 0 | 94.78 $ | 11 % |
| SOL | 1x | 13.20 % | −3.00 % | 93.6 % | 43 | 12 | 31 | 0 | 94.84 $ | 6 % |
| XRP | 1x | 13.20 % | −3.00 % | 81.3 % | 33 | 9 | 24 | 0 | 95.55 $ | 7 % |
| DOGE | 1x | 13.20 % | −3.00 % | 93.4 % | 38 | 9 | 29 | 0 | 90.85 $ | 11 % |
| TSLA | 1x | 11.20 % | −4.70 % | 81.3 % | 44 | 16 | 28 | 0 | 102.56 $ | 9 % |
| NVDA | 1x | 11.20 % | −4.70 % | 67.8 % | 45 | 14 | 28 | 3 | 102.96 $ | 7 % |
| AMD | 1x | 11.20 % | −4.70 % | 79.4 % | 53 | 17 | 34 | 2 | 101.98 $ | 8 % |
| COIN | 1x | 11.20 % | −4.70 % | 95.7 % | 59 | 13 | 46 | 0 | 81.26 $ | 19 % |
| MSTR | 1x | 11.20 % | −4.70 % | 95.1 % | 62 | 21 | 40 | 1 | 103.53 $ | 9 % |
| PLTR | 1x | 11.20 % | −4.70 % | 86.8 % | 55 | 17 | 36 | 2 | 93.49 $ | 10 % |
| EURUSD | 1x | 10.32 % | −4.98 % | 0.0 % | 30 | 0 | 0 | 30 | 96.75 $ | 4 % |
| USDJPY | 1x | 10.32 % | −4.98 % | 0.6 % | 27 | 0 | 1 | 26 | 98.87 $ | 2 % |
| GBPJPY | 1x | 10.32 % | −4.98 % | 1.1 % | 27 | 0 | 0 | 27 | 98.19 $ | 4 % |
| GOLD | 1x | 10.70 % | −4.90 % | 14.2 % | 29 | 3 | 10 | 16 | 102.32 $ | 5 % |
| SILVER | 1x | 10.70 % | −4.90 % | 46.6 % | 35 | 10 | 19 | 6 | 101.97 $ | 13 % |
| OIL | 1x | 10.70 % | −4.90 % | 44.5 % | 29 | 7 | 12 | 10 | 106.61 $ | 4 % |
| SPX500 | 1x | 10.65 % | −4.95 % | 3.5 % | 32 | 1 | 5 | 26 | 102.38 $ | 2 % |
| NSDQ100 | 1x | 10.65 % | −4.95 % | 12.6 % | 34 | 2 | 11 | 21 | 97.18 $ | 5 % |
| GER40 | 1x | 10.65 % | −4.95 % | 4.3 % | 29 | 1 | 8 | 20 | 97.64 $ | 4 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 720 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
