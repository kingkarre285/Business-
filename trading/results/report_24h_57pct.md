# Backtest: mindestens 57 % netto pro Trade

Erstellt: 2026-10-02 08:23 UTC · Kursdaten: eToro, OneHour-Kerzen, 2026-07-24 bis 2026-10-02

## Regeln

- Ziel: +57 % auf den Einsatz **nach Kosten**, innerhalb von 24 Stunden
- Stop-Loss: −50 % des Einsatzes; Einsatz pro Trade: 100 % des Kontos
- Hebel: jeweils der für Privatkunden maximal erlaubte (ESMA)
- Risiko pro Trade: 50.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Breakout über das Hoch / unter das Tief der letzten 24 Stunden
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **521**, davon Ziel erreicht: **6** (1.2 %)
- Kapital gesamt: 2000 $ → **1221.75 $** (-38.9 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**
- Kalenderwochen (alle Märkte zusammen): **137**, davon Konto verdoppelt: **1**, im Plus: 54, im Minus: 83
- Beste Woche: +132.0 %, schlechteste Woche: -66.9 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 2x | 30.54 % | −23.00 % | 0.0 % | 26 | 0 | 0 | 26 | 28.57 $ | 71 % |
| ETH | 2x | 30.54 % | −23.00 % | 0.0 % | 24 | 0 | 0 | 24 | 24.74 $ | 75 % |
| SOL | 2x | 30.54 % | −23.00 % | 0.0 % | 22 | 0 | 0 | 22 | 68.44 $ | 36 % |
| XRP | 2x | 30.54 % | −23.00 % | 0.0 % | 26 | 0 | 0 | 26 | 48.11 $ | 52 % |
| DOGE | 2x | 30.54 % | −23.00 % | 0.0 % | 24 | 0 | 0 | 24 | 31.71 $ | 68 % |
| TSLA | 5x | 11.73 % | −9.70 % | 0.0 % | 26 | 0 | 0 | 26 | 21.30 $ | 79 % |
| NVDA | 5x | 11.73 % | −9.70 % | 0.0 % | 24 | 0 | 0 | 24 | 45.92 $ | 68 % |
| AMD | 5x | 11.73 % | −9.70 % | 0.2 % | 30 | 0 | 0 | 30 | 40.27 $ | 66 % |
| COIN | 5x | 11.73 % | −9.70 % | 4.5 % | 28 | 1 | 0 | 27 | 19.28 $ | 86 % |
| MSTR | 5x | 11.73 % | −9.70 % | 10.1 % | 26 | 2 | 2 | 22 | 29.01 $ | 87 % |
| PLTR | 5x | 11.73 % | −9.70 % | 2.9 % | 26 | 1 | 0 | 25 | 131.83 $ | 48 % |
| EURUSD | 30x | 1.93 % | −1.65 % | 0.0 % | 24 | 0 | 0 | 24 | 106.58 $ | 26 % |
| USDJPY | 30x | 1.93 % | −1.65 % | 2.1 % | 27 | 1 | 0 | 26 | 161.11 $ | 29 % |
| GBPJPY | 20x | 2.88 % | −2.48 % | 0.0 % | 27 | 0 | 0 | 27 | 101.45 $ | 26 % |
| GOLD | 20x | 2.97 % | −2.40 % | 4.3 % | 26 | 1 | 0 | 25 | 81.66 $ | 58 % |
| SILVER | 10x | 5.82 % | −4.90 % | 3.2 % | 24 | 0 | 3 | 21 | 5.73 $ | 95 % |
| OIL | 10x | 5.82 % | −4.90 % | 3.3 % | 28 | 0 | 0 | 28 | 76.68 $ | 68 % |
| SPX500 | 20x | 2.92 % | −2.45 % | 0.0 % | 27 | 0 | 0 | 27 | 61.76 $ | 47 % |
| NSDQ100 | 20x | 2.92 % | −2.45 % | 0.2 % | 27 | 0 | 0 | 27 | 12.45 $ | 88 % |
| GER40 | 20x | 2.92 % | −2.45 % | 0.0 % | 29 | 0 | 0 | 29 | 125.15 $ | 29 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 24 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
