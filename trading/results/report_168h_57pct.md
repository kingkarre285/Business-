# Backtest: mindestens 57 % netto pro Trade

Erstellt: 2026-10-02 08:23 UTC · Kursdaten: eToro, FourHours-Kerzen, 2026-01-08 bis 2026-10-02

## Regeln

- Ziel: +57 % auf den Einsatz **nach Kosten**, innerhalb von 168 Stunden
- Stop-Loss: −50 % des Einsatzes; Einsatz pro Trade: 100 % des Kontos
- Hebel: jeweils der für Privatkunden maximal erlaubte (ESMA)
- Risiko pro Trade: 50.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Breakout über das Hoch / unter das Tief der letzten 168 Stunden
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **364**, davon Ziel erreicht: **56** (15.4 %)
- Kapital gesamt: 2000 $ → **569.40 $** (-71.5 %)
- Märkte mit Totalverlust (< 1 % übrig): **5 von 20**
- Kalenderwochen (alle Märkte zusammen): **586**, davon Konto verdoppelt: **4**, im Plus: 132, im Minus: 199
- Beste Woche: +152.2 %, schlechteste Woche: -100.0 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 2x | 30.78 % | −23.00 % | 0.0 % | 15 | 0 | 0 | 15 | 81.55 $ | 28 % |
| ETH | 2x | 30.78 % | −23.00 % | 2.8 % | 14 | 0 | 0 | 14 | 93.28 $ | 23 % |
| SOL | 2x | 30.78 % | −23.00 % | 2.6 % | 15 | 0 | 1 | 14 | 39.56 $ | 75 % |
| XRP | 2x | 30.78 % | −23.00 % | 4.6 % | 16 | 1 | 0 | 15 | 62.28 $ | 39 % |
| DOGE | 2x | 30.78 % | −23.00 % | 4.2 % | 11 | 1 | 1 | 9 | 59.77 $ | 63 % |
| TSLA | 5x | 11.91 % | −9.70 % | 9.2 % | 21 | 1 | 1 | 19 | 8.12 $ | 92 % |
| NVDA | 5x | 11.91 % | −9.70 % | 3.9 % | 21 | 0 | 3 | 18 | 1.54 $ | 99 % |
| AMD | 5x | 11.91 % | −9.70 % | 43.2 % | 20 | 5 | 6 | 9 | 14.51 $ | 99 % |
| COIN | 5x | 11.91 % | −9.70 % | 42.3 % | 18 | 4 | 8 | 6 | 0.74 $ | 99 % |
| MSTR | 5x | 11.91 % | −9.70 % | 46.8 % | 21 | 8 | 7 | 6 | 42.89 $ | 84 % |
| PLTR | 5x | 11.91 % | −9.70 % | 25.8 % | 19 | 4 | 6 | 9 | 10.82 $ | 96 % |
| EURUSD | 30x | 1.99 % | −1.65 % | 1.3 % | 19 | 0 | 0 | 19 | 18.90 $ | 85 % |
| USDJPY | 30x | 1.99 % | −1.65 % | 12.7 % | 21 | 2 | 2 | 17 | 37.07 $ | 85 % |
| GBPJPY | 20x | 2.94 % | −2.48 % | 5.1 % | 18 | 1 | 1 | 16 | 60.03 $ | 71 % |
| GOLD | 20x | 3.09 % | −2.40 % | 68.4 % | 24 | 11 | 9 | 4 | 16.24 $ | 99 % |
| SILVER | 10x | 5.94 % | −4.90 % | 68.0 % | 24 | 8 | 12 | 4 | 0.95 $ | 100 % |
| OIL | 10x | 5.94 % | −4.90 % | 85.2 % | 4 | 0 | 4 | 0 | 0.00 $ | 100 % |
| SPX500 | 20x | 3.04 % | −2.45 % | 20.5 % | 20 | 2 | 3 | 15 | 19.44 $ | 90 % |
| NSDQ100 | 20x | 3.04 % | −2.45 % | 53.0 % | 21 | 5 | 10 | 6 | 0.95 $ | 100 % |
| GER40 | 20x | 3.04 % | −2.45 % | 32.4 % | 22 | 3 | 7 | 12 | 0.75 $ | 99 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 168 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
