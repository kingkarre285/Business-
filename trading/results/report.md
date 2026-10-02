# Backtest: mindestens 57 % netto pro Trade

Erstellt: 2026-10-02 08:07 UTC · Kursdaten: eToro, OneHour-Kerzen, 2026-07-24 bis 2026-10-02

## Regeln

- Ziel: +57 % auf den Einsatz **nach Kosten**, innerhalb von 24 Stunden
- Stop-Loss: −50 % des Einsatzes; Einsatz pro Trade: 100 % des Kontos
- Hebel: jeweils der für Privatkunden maximal erlaubte (ESMA)
- Einstieg: Breakout über das Hoch / unter das Tief der letzten 24 Stunden
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **521**, davon Ziel erreicht: **6** (1.2 %)
- Kapital gesamt: 2000 $ → **1290.32 $** (-35.5 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 2x | 30.50 % | −23.00 % | 0.0 % | 26 | 0 | 0 | 26 | 29.11 $ | 71 % |
| ETH | 2x | 30.50 % | −23.00 % | 0.0 % | 24 | 0 | 0 | 24 | 25.23 $ | 75 % |
| SOL | 2x | 30.50 % | −23.00 % | 0.0 % | 22 | 0 | 0 | 22 | 69.60 $ | 35 % |
| XRP | 2x | 30.50 % | −23.00 % | 0.0 % | 26 | 0 | 0 | 26 | 48.51 $ | 51 % |
| DOGE | 2x | 30.50 % | −23.00 % | 0.0 % | 24 | 0 | 0 | 24 | 32.34 $ | 68 % |
| TSLA | 5x | 11.70 % | −9.70 % | 0.0 % | 26 | 0 | 0 | 26 | 22.17 $ | 78 % |
| NVDA | 5x | 11.70 % | −9.70 % | 0.0 % | 24 | 0 | 0 | 24 | 47.40 $ | 68 % |
| AMD | 5x | 11.70 % | −9.70 % | 0.2 % | 30 | 0 | 0 | 30 | 41.91 $ | 65 % |
| COIN | 5x | 11.70 % | −9.70 % | 4.5 % | 28 | 1 | 0 | 27 | 20.10 $ | 85 % |
| MSTR | 5x | 11.70 % | −9.70 % | 10.2 % | 26 | 2 | 2 | 22 | 31.58 $ | 87 % |
| PLTR | 5x | 11.70 % | −9.70 % | 2.9 % | 26 | 1 | 0 | 25 | 135.51 $ | 48 % |
| EURUSD | 30x | 1.92 % | −1.65 % | 0.0 % | 24 | 0 | 0 | 24 | 115.07 $ | 25 % |
| USDJPY | 30x | 1.92 % | −1.65 % | 2.1 % | 27 | 1 | 0 | 26 | 170.09 $ | 28 % |
| GBPJPY | 20x | 2.87 % | −2.48 % | 0.0 % | 27 | 0 | 0 | 27 | 105.38 $ | 25 % |
| GOLD | 20x | 2.95 % | −2.40 % | 4.6 % | 26 | 1 | 0 | 25 | 90.16 $ | 55 % |
| SILVER | 10x | 5.80 % | −4.90 % | 3.3 % | 24 | 0 | 3 | 21 | 6.01 $ | 95 % |
| OIL | 10x | 5.80 % | −4.90 % | 3.4 % | 28 | 0 | 0 | 28 | 80.19 $ | 67 % |
| SPX500 | 20x | 2.90 % | −2.45 % | 0.0 % | 27 | 0 | 0 | 27 | 68.64 $ | 42 % |
| NSDQ100 | 20x | 2.90 % | −2.45 % | 0.2 % | 27 | 0 | 0 | 27 | 14.06 $ | 86 % |
| GER40 | 20x | 2.90 % | −2.45 % | 0.0 % | 29 | 0 | 0 | 29 | 137.25 $ | 28 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 24 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
