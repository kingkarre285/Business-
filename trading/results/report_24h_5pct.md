# Backtest: mindestens 5 % netto pro Trade

Erstellt: 2026-10-02 08:23 UTC · Kursdaten: eToro, OneHour-Kerzen, 2026-07-24 bis 2026-10-02

## Regeln

- Ziel: +5 % auf den Einsatz **nach Kosten**, innerhalb von 24 Stunden
- Stop-Loss: −2 % des Einsatzes; Einsatz pro Trade: 40 % des Kontos
- Hebel: höchstens 1x (ohne Hebel)
- Risiko pro Trade: 1.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Breakout über das Hoch / unter das Tief der letzten 24 Stunden
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **621**, davon Ziel erreicht: **27** (4.3 %)
- Kapital gesamt: 2000 $ → **1852.78 $** (-7.4 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**
- Kalenderwochen (alle Märkte zusammen): **137**, davon Konto verdoppelt: **0**, im Plus: 52, im Minus: 85
- Beste Woche: +2.6 %, schlechteste Woche: -9.6 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 1x | 7.04 % | −0.50 % | 1.1 % | 36 | 0 | 26 | 10 | 75.45 $ | 25 % |
| ETH | 1x | 7.04 % | −0.50 % | 3.4 % | 34 | 0 | 28 | 6 | 75.35 $ | 25 % |
| SOL | 1x | 7.04 % | −0.50 % | 10.1 % | 41 | 2 | 33 | 6 | 74.52 $ | 26 % |
| XRP | 1x | 7.04 % | −0.50 % | 16.4 % | 42 | 1 | 34 | 7 | 74.64 $ | 25 % |
| DOGE | 1x | 7.04 % | −0.50 % | 14.5 % | 39 | 3 | 33 | 3 | 75.69 $ | 24 % |
| TSLA | 1x | 5.33 % | −2.20 % | 6.6 % | 28 | 1 | 8 | 19 | 94.86 $ | 5 % |
| NVDA | 1x | 5.33 % | −2.20 % | 2.0 % | 28 | 0 | 5 | 23 | 100.41 $ | 4 % |
| AMD | 1x | 5.33 % | −2.20 % | 14.6 % | 32 | 3 | 13 | 16 | 99.02 $ | 4 % |
| COIN | 1x | 5.33 % | −2.20 % | 32.4 % | 38 | 6 | 22 | 10 | 90.18 $ | 10 % |
| MSTR | 1x | 5.33 % | −2.20 % | 38.3 % | 33 | 7 | 20 | 6 | 97.85 $ | 5 % |
| PLTR | 1x | 5.33 % | −2.20 % | 13.9 % | 30 | 2 | 10 | 18 | 97.63 $ | 5 % |
| EURUSD | 1x | 5.03 % | −2.48 % | 0.0 % | 24 | 0 | 0 | 24 | 100.18 $ | 0 % |
| USDJPY | 1x | 5.03 % | −2.48 % | 0.0 % | 26 | 0 | 0 | 26 | 101.08 $ | 0 % |
| GBPJPY | 1x | 5.03 % | −2.48 % | 0.0 % | 27 | 0 | 0 | 27 | 100.25 $ | 1 % |
| GOLD | 1x | 5.12 % | −2.40 % | 0.0 % | 26 | 0 | 0 | 26 | 100.64 $ | 1 % |
| SILVER | 1x | 5.12 % | −2.40 % | 4.7 % | 25 | 0 | 9 | 16 | 96.25 $ | 5 % |
| OIL | 1x | 5.12 % | −2.40 % | 6.1 % | 29 | 2 | 7 | 20 | 101.99 $ | 5 % |
| SPX500 | 1x | 5.07 % | −2.45 % | 0.0 % | 27 | 0 | 0 | 27 | 99.34 $ | 1 % |
| NSDQ100 | 1x | 5.07 % | −2.45 % | 0.0 % | 27 | 0 | 0 | 27 | 96.73 $ | 3 % |
| GER40 | 1x | 5.07 % | −2.45 % | 0.0 % | 29 | 0 | 0 | 29 | 100.73 $ | 1 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 24 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
