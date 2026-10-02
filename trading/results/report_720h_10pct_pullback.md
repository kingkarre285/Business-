# Backtest: mindestens 10 % netto pro Trade (pullback)

Erstellt: 2026-10-02 08:27 UTC · Kursdaten: eToro, OneDay-Kerzen, 2022-09-02 bis 2026-10-02

## Regeln

- Ziel: +10 % auf den Einsatz **nach Kosten**, innerhalb von 720 Stunden
- Stop-Loss: −5 % des Einsatzes; Einsatz pro Trade: 20 % des Kontos
- Hebel: höchstens 1x (ohne Hebel)
- Risiko pro Trade: 1.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Rücksetzer: Long bei RSI(14) < 30 über dem 200-Perioden-Schnitt; Short bei RSI(14) > 70 darunter
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **44**, davon Ziel erreicht: **10** (22.7 %)
- Kapital gesamt: 2000 $ → **1994.51 $** (-0.3 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**
- Monate à 30 Tage (alle Märkte zusammen): **874**, davon Konto verdoppelt: **0**, im Plus: 15, im Minus: 16
- Beste(r) Monat: +2.2 %, schlechteste(r) Monat: -4.0 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 1x | 13.20 % | −3.00 % | 56.4 % | 3 | 2 | 1 | 0 | 103.15 $ | 1 % |
| ETH | 1x | 13.20 % | −3.00 % | 87.3 % | 4 | 0 | 4 | 0 | 96.01 $ | 4 % |
| SOL | 1x | 13.20 % | −3.00 % | 93.6 % | 4 | 1 | 3 | 0 | 99.08 $ | 3 % |
| XRP | 1x | 13.20 % | −3.00 % | 81.3 % | 2 | 0 | 2 | 0 | 98.01 $ | 2 % |
| DOGE | 1x | 13.20 % | −3.00 % | 93.4 % | 8 | 1 | 7 | 0 | 95.21 $ | 6 % |
| TSLA | 1x | 11.20 % | −4.70 % | 81.3 % | 4 | 1 | 3 | 0 | 99.06 $ | 3 % |
| NVDA | 1x | 11.20 % | −4.70 % | 67.8 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| AMD | 1x | 11.20 % | −4.70 % | 79.4 % | 2 | 0 | 2 | 0 | 97.80 $ | 2 % |
| COIN | 1x | 11.20 % | −4.70 % | 95.7 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| MSTR | 1x | 11.20 % | −4.70 % | 95.1 % | 6 | 2 | 4 | 0 | 100.16 $ | 4 % |
| PLTR | 1x | 11.20 % | −4.70 % | 86.8 % | 1 | 1 | 0 | 0 | 102.11 $ | 0 % |
| EURUSD | 1x | 10.32 % | −4.98 % | 0.0 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| USDJPY | 1x | 10.32 % | −4.98 % | 0.6 % | 4 | 0 | 1 | 3 | 99.78 $ | 1 % |
| GBPJPY | 1x | 10.32 % | −4.98 % | 1.1 % | 1 | 0 | 1 | 0 | 98.99 $ | 1 % |
| GOLD | 1x | 10.70 % | −4.90 % | 14.2 % | 2 | 1 | 1 | 0 | 101.05 $ | 1 % |
| SILVER | 1x | 10.70 % | −4.90 % | 46.6 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| OIL | 1x | 10.70 % | −4.90 % | 44.5 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| SPX500 | 1x | 10.65 % | −4.95 % | 3.5 % | 1 | 0 | 0 | 1 | 100.29 $ | 0 % |
| NSDQ100 | 1x | 10.65 % | −4.95 % | 12.6 % | 1 | 0 | 0 | 1 | 101.76 $ | 0 % |
| GER40 | 1x | 10.65 % | −4.95 % | 4.3 % | 1 | 1 | 0 | 0 | 102.06 $ | 0 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 720 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
