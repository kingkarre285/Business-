# Backtest: mindestens 5 % netto pro Trade

Erstellt: 2026-10-02 08:23 UTC · Kursdaten: eToro, FourHours-Kerzen, 2026-01-08 bis 2026-10-02

## Regeln

- Ziel: +5 % auf den Einsatz **nach Kosten**, innerhalb von 168 Stunden
- Stop-Loss: −2 % des Einsatzes; Einsatz pro Trade: 40 % des Kontos
- Hebel: höchstens 1x (ohne Hebel)
- Risiko pro Trade: 1.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Breakout über das Hoch / unter das Tief der letzten 168 Stunden
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **556**, davon Ziel erreicht: **80** (14.4 %)
- Kapital gesamt: 2000 $ → **1835.08 $** (-8.2 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**
- Kalenderwochen (alle Märkte zusammen): **609**, davon Konto verdoppelt: **0**, im Plus: 112, im Minus: 269
- Beste Woche: +4.2 %, schlechteste Woche: -4.9 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 1x | 7.28 % | −0.50 % | 23.4 % | 33 | 2 | 29 | 2 | 78.00 $ | 22 % |
| ETH | 1x | 7.28 % | −0.50 % | 42.8 % | 33 | 0 | 32 | 1 | 73.16 $ | 27 % |
| SOL | 1x | 7.28 % | −0.50 % | 53.4 % | 37 | 3 | 33 | 1 | 75.78 $ | 24 % |
| XRP | 1x | 7.28 % | −0.50 % | 52.1 % | 37 | 1 | 36 | 0 | 71.03 $ | 29 % |
| DOGE | 1x | 7.28 % | −0.50 % | 60.5 % | 25 | 3 | 22 | 0 | 85.30 $ | 16 % |
| TSLA | 1x | 5.51 % | −2.20 % | 68.5 % | 30 | 4 | 25 | 1 | 83.73 $ | 16 % |
| NVDA | 1x | 5.51 % | −2.20 % | 58.5 % | 27 | 3 | 18 | 6 | 89.34 $ | 11 % |
| AMD | 1x | 5.51 % | −2.20 % | 91.0 % | 30 | 7 | 23 | 0 | 91.37 $ | 11 % |
| COIN | 1x | 5.51 % | −2.20 % | 91.8 % | 34 | 9 | 25 | 0 | 92.45 $ | 9 % |
| MSTR | 1x | 5.51 % | −2.20 % | 96.9 % | 35 | 13 | 22 | 0 | 104.49 $ | 6 % |
| PLTR | 1x | 5.51 % | −2.20 % | 76.5 % | 31 | 9 | 22 | 0 | 94.89 $ | 8 % |
| EURUSD | 1x | 5.09 % | −2.48 % | 0.0 % | 19 | 0 | 0 | 19 | 98.49 $ | 2 % |
| USDJPY | 1x | 5.09 % | −2.48 % | 1.5 % | 21 | 0 | 2 | 19 | 98.09 $ | 3 % |
| GBPJPY | 1x | 5.09 % | −2.48 % | 0.0 % | 17 | 0 | 1 | 16 | 100.24 $ | 2 % |
| GOLD | 1x | 5.24 % | −2.40 % | 23.5 % | 21 | 5 | 7 | 9 | 105.70 $ | 4 % |
| SILVER | 1x | 5.24 % | −2.40 % | 75.4 % | 30 | 9 | 18 | 3 | 102.03 $ | 5 % |
| OIL | 1x | 5.24 % | −2.40 % | 90.0 % | 30 | 10 | 19 | 1 | 101.28 $ | 6 % |
| SPX500 | 1x | 5.19 % | −2.45 % | 1.4 % | 19 | 0 | 3 | 16 | 99.11 $ | 3 % |
| NSDQ100 | 1x | 5.19 % | −2.45 % | 15.7 % | 22 | 0 | 11 | 11 | 96.54 $ | 9 % |
| GER40 | 1x | 5.19 % | −2.45 % | 8.2 % | 25 | 2 | 8 | 15 | 94.05 $ | 6 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 168 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
