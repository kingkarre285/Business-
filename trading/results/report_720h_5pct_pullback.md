# Backtest: mindestens 5 % netto pro Trade (pullback)

Erstellt: 2026-10-02 08:27 UTC · Kursdaten: eToro, OneDay-Kerzen, 2022-09-02 bis 2026-10-02

## Regeln

- Ziel: +5 % auf den Einsatz **nach Kosten**, innerhalb von 720 Stunden
- Stop-Loss: −2 % des Einsatzes; Einsatz pro Trade: 40 % des Kontos
- Hebel: höchstens 1x (ohne Hebel)
- Risiko pro Trade: 1.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Rücksetzer: Long bei RSI(14) < 30 über dem 200-Perioden-Schnitt; Short bei RSI(14) > 70 darunter
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **48**, davon Ziel erreicht: **12** (25.0 %)
- Kapital gesamt: 2000 $ → **1995.18 $** (-0.2 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**
- Monate à 30 Tage (alle Märkte zusammen): **874**, davon Konto verdoppelt: **0**, im Plus: 13, im Minus: 17
- Beste(r) Monat: +2.4 %, schlechteste(r) Monat: -4.9 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 1x | 8.20 % | −0.50 % | 88.9 % | 4 | 1 | 3 | 0 | 99.36 $ | 2 % |
| ETH | 1x | 8.20 % | −0.50 % | 98.8 % | 5 | 0 | 5 | 0 | 95.08 $ | 5 % |
| SOL | 1x | 8.20 % | −0.50 % | 99.5 % | 4 | 1 | 3 | 0 | 99.39 $ | 3 % |
| XRP | 1x | 8.20 % | −0.50 % | 98.8 % | 2 | 0 | 2 | 0 | 98.01 $ | 2 % |
| DOGE | 1x | 8.20 % | −0.50 % | 98.4 % | 9 | 1 | 8 | 0 | 94.56 $ | 7 % |
| TSLA | 1x | 6.20 % | −2.20 % | 99.3 % | 4 | 2 | 2 | 0 | 102.62 $ | 2 % |
| NVDA | 1x | 6.20 % | −2.20 % | 97.1 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| AMD | 1x | 6.20 % | −2.20 % | 99.7 % | 2 | 2 | 0 | 0 | 104.63 $ | 0 % |
| COIN | 1x | 6.20 % | −2.20 % | 100.0 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| MSTR | 1x | 6.20 % | −2.20 % | 99.9 % | 7 | 2 | 5 | 0 | 99.64 $ | 4 % |
| PLTR | 1x | 6.20 % | −2.20 % | 99.6 % | 1 | 1 | 0 | 0 | 102.34 $ | 0 % |
| EURUSD | 1x | 5.32 % | −2.48 % | 2.4 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| USDJPY | 1x | 5.32 % | −2.48 % | 8.9 % | 4 | 0 | 2 | 2 | 99.45 $ | 2 % |
| GBPJPY | 1x | 5.32 % | −2.48 % | 6.3 % | 1 | 0 | 1 | 0 | 98.98 $ | 1 % |
| GOLD | 1x | 5.70 % | −2.40 % | 51.3 % | 2 | 1 | 1 | 0 | 101.19 $ | 1 % |
| SILVER | 1x | 5.70 % | −2.40 % | 88.2 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| OIL | 1x | 5.70 % | −2.40 % | 89.5 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| SPX500 | 1x | 5.65 % | −2.45 % | 24.7 % | 1 | 0 | 1 | 0 | 98.82 $ | 1 % |
| NSDQ100 | 1x | 5.65 % | −2.45 % | 53.4 % | 1 | 1 | 0 | 0 | 102.13 $ | 0 % |
| GER40 | 1x | 5.65 % | −2.45 % | 28.6 % | 1 | 0 | 1 | 0 | 99.00 $ | 1 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 720 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
