# Backtest: mindestens 3 % netto pro Trade (pullback)

Erstellt: 2026-10-02 08:27 UTC · Kursdaten: eToro, OneDay-Kerzen, 2022-09-02 bis 2026-10-02

## Regeln

- Ziel: +3 % auf den Einsatz **nach Kosten**, innerhalb von 720 Stunden
- Stop-Loss: −2 % des Einsatzes; Einsatz pro Trade: 67 % des Kontos
- Hebel: höchstens 1x (ohne Hebel)
- Risiko pro Trade: 1.0 % des Kontos (Einsatz × Stop-Loss)
- Einstieg: Rücksetzer: Long bei RSI(14) < 30 über dem 200-Perioden-Schnitt; Short bei RSI(14) > 70 darunter
- Startkapital je Markt: 100 $

## Ergebnis gesamt

- Trades: **25**, davon Ziel erreicht: **7** (28.0 %)
- Kapital gesamt: 2000 $ → **2000.70 $** (+0.0 %)
- Märkte mit Totalverlust (< 1 % übrig): **0 von 20**
- Monate à 30 Tage (alle Märkte zusammen): **874**, davon Konto verdoppelt: **0**, im Plus: 7, im Minus: 11
- Beste(r) Monat: +2.5 %, schlechteste(r) Monat: -3.0 %

## Je Markt

| Markt | Hebel | nötige Kursbewegung | Stop bei | Ziel überhaupt möglich* | Trades | Ziel | Stop | Zeit | Endkapital | max. Rückgang |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 1x | 6.20 % | Kosten > Stop | 95.9 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| ETH | 1x | 6.20 % | Kosten > Stop | 99.5 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| SOL | 1x | 6.20 % | Kosten > Stop | 99.8 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| XRP | 1x | 6.20 % | Kosten > Stop | 100.0 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| DOGE | 1x | 6.20 % | Kosten > Stop | 99.9 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| TSLA | 1x | 4.20 % | −1.20 % | 100.0 % | 5 | 1 | 4 | 0 | 98.50 $ | 4 % |
| NVDA | 1x | 4.20 % | −1.20 % | 99.9 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| AMD | 1x | 4.20 % | −1.20 % | 100.0 % | 2 | 1 | 1 | 0 | 101.48 $ | 1 % |
| COIN | 1x | 4.20 % | −1.20 % | 100.0 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| MSTR | 1x | 4.20 % | −1.20 % | 100.0 % | 7 | 1 | 6 | 0 | 96.60 $ | 5 % |
| PLTR | 1x | 4.20 % | −1.20 % | 100.0 % | 1 | 0 | 1 | 0 | 99.00 $ | 1 % |
| EURUSD | 1x | 3.32 % | −1.48 % | 14.9 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| USDJPY | 1x | 3.32 % | −1.48 % | 46.6 % | 4 | 1 | 2 | 1 | 101.12 $ | 2 % |
| GBPJPY | 1x | 3.32 % | −1.48 % | 34.8 % | 1 | 0 | 1 | 0 | 98.97 $ | 1 % |
| GOLD | 1x | 3.70 % | −1.40 % | 76.9 % | 2 | 1 | 1 | 0 | 101.38 $ | 1 % |
| SILVER | 1x | 3.70 % | −1.40 % | 98.6 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| OIL | 1x | 3.70 % | −1.40 % | 98.6 % | 0 | 0 | 0 | 0 | 100.00 $ | 0 % |
| SPX500 | 1x | 3.65 % | −1.45 % | 62.6 % | 1 | 1 | 0 | 0 | 102.32 $ | 0 % |
| NSDQ100 | 1x | 3.65 % | −1.45 % | 85.6 % | 1 | 1 | 0 | 0 | 102.35 $ | 0 % |
| GER40 | 1x | 3.65 % | −1.45 % | 68.1 % | 1 | 0 | 1 | 0 | 99.00 $ | 1 % |

\* Anteil aller Zeitpunkte, ab denen sich der Kurs innerhalb von 720 h weit genug bewegt hat, **mit perfekter Vorhersage der Richtung** und ohne Rücksicht auf den Stop. Das ist die theoretische Obergrenze, die keine Strategie erreicht.

Kosten sind Schätzwerte (siehe `trading/config.py`). Vergangene Ergebnisse sind keine Garantie für die Zukunft.
