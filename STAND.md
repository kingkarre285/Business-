# Projektstand (Übergabe für neue Sitzungen)

Stand: 02.10.2026. Diese Datei fasst zusammen, was bisher entschieden und getestet wurde,
damit eine neue Claude-Sitzung nahtlos weitermachen kann.

## Ziel des Nutzers
- Automatischer Trading-Bot für **eToro**: Indizes, Rohstoffe, Aktien.
- Hebel und Short-Positionen sind ausdrücklich erlaubt.
- Interesse an **Scalping auf 1- bis 5-Minuten-Basis**.
- Zuerst **Demo**, später Echtgeld mit Limits.
- Broker: **nur eToro**. CMC Markets wurde verworfen (zu kompliziert, nur über MT4).
- **TradingView** soll als Connector für Analyse und News dazukommen, nicht für den Handel.

## Verbindungen
- **eToro-Connector** (`mcp.public-api.etoro.com`): verbunden, Demo- und Echtgeld-Rechte vorhanden.
  - Echtgeldkonto: 0 USD.
  - Demokonto: ca. 100.250 USD, davon 79.000 USD frei. Es kopiert zwei Trader: thomaspj und GlobalAlphaS.
- **eToro-API-Schlüssel**: in der Cloud-Umgebung als „Zugangsdaten“ hinterlegt.
  - Der Proxy hängt `x-api-key` und `x-user-key` automatisch an.
  - Der Code erkennt das per Testabruf (`data.has_etoro_keys()`).
- **TradingView-Connector** (`https://mcp.tradingview.com/mcp`): soll der Nutzer hinzufügen.
  - Kann Kurse (max. 5000 Kerzen), Screener, News, Wirtschaftskalender und Alarme.
  - Kann **nicht** handeln.
- Co-Invest (Liquid) und trader.dev passen nicht: andere Plattformen bzw. nur Krypto-Börsen.

## Code
- `etoro_bot/`: Bot mit den Modi `paper`, `demo` und `live`.
  - Live-Handel nur mit `ETORO_ALLOW_LIVE=yes`.
- `etoro_bot/data.py`: Kerzen von eToro (`/api/v1/data/instruments/{id}/candles`), Cache in `.cache/`.
  - Ohne Schlüssel wird Yahoo verwendet.
- `etoro_bot/scalp.py`: 5-Minuten-Scalping-Backtest.
  - Strategien: Pullback und Opening-Range-Breakout.
  - Kosten: eToro-Spread mal 2.
- `tradingview/scalp_test.pine`: dieselben Scalping-Strategien als Pine Script.
- `config.yaml`: aktuell `mode: paper`, `leverage: 2`, `allow_short: true`.
- `.github/workflows/trading-bot.yml`: täglicher Lauf auf GitHub Actions.
  - Läuft erst nach Merge in `main`.
  - Braucht die Secrets `ETORO_API_KEY` und `ETORO_USER_KEY`.

## Ergebnisse

### Tagesstrategie (Trendfolge SMA 20/50/200, RSI, ATR-Stops)
5 Jahre, Yahoo-Daten, ohne Spreads:

| Variante | Rendite |
|---|---|
| Nur Long, Hebel 1 | +6,8 % |
| **Nur Long, Hebel 2** | **+8,1 % (beste)** |
| Long + Short, Hebel 1 | +4,5 % |
| Long + Short, Hebel 2 | +5,5 % |
| Long + Short, Hebel 5 | +5,5 % |

Alle Varianten liegen deutlich unter Buy & Hold (S&P 500 +88 %).

### Scalping 5 Minuten
**eToro-Daten, 2 Jahre**, Risiko 0,5 %/Trade, Spread mal 2, Positionen werden vor Sitzungsende geschlossen:

| Markt | Strategie | Trades | Treffer | Rendite | max. DD |
|---|---|---|---|---|---|
| SPX500 | Pullback | 337 | 39 % | −22,9 % | 23,8 % |
| SPX500 | ORB | 515 | 46 % | **+7,3 %** | 8,0 % |
| NSDQ100 | Pullback | 338 | 44 % | −17,1 % | 18,3 % |
| NSDQ100 | ORB | 514 | 50 % | +0,5 % | 10,5 % |
| GER40 | Pullback | 398 | 46 % | −15,2 % | 19,2 % |
| GER40 | ORB | 500 | 43 % | −6,2 % | 14,0 % |
| GOLD | Pullback | 1010 | 46 % | −22,6 % | 24,2 % |
| OIL | Pullback | 1103 | 43 % | −67,2 % | 67,3 % |

**Fazit:**
- Die Pullback-Strategie ist unbrauchbar.
- Der ORB auf dem SPX500 ist das einzige positive Ergebnis. Das kann Zufall sein, weil er auf Nasdaq und DAX nicht funktioniert.
- Nächster sinnvoller Schritt: ORB auf dem SPX500 mit eToro-Daten **ab 2012** prüfen, also außerhalb der bisherigen Stichprobe.

## Offene Punkte
- Short-Positionen abschalten (Variante „Nur Long, Hebel 2“)? Der Nutzer hat noch nicht entschieden.
- Erste Demo-Trades (NSDQ100, MSFT, NVDA, je 15.000 USD) wurden am 01.10. vorbereitet, aber **nicht ausgeführt**.
  - Vor jeder Ausführung braucht es eine neue Vorschau und die Zustimmung des Nutzers.
- W-8BEN-Formular für US-Aktien: Ob es bei eToro hinterlegt ist, ist unklar.
- Pull Request nach `main` für den täglichen Bot: noch nicht erstellt.
