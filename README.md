# eToro-Trading-Bot

Ein vollautomatischer Trading-Bot für **Indizes, Rohstoffe und Aktien**, der über die eToro-API handeln kann.

> ⚠️ **Risikohinweis:** Trading kann zum Totalverlust führen. Der Bot ist keine Anlageberatung, und vergangene Ergebnisse (Backtest) garantieren keine zukünftigen Gewinne. Setze nur Geld ein, dessen Verlust du verkraften kannst.

## Modi (`mode` in `config.yaml`)

| Modus | Was passiert | Voraussetzung |
|-------|--------------|---------------|
| `paper` (Standard) | Simulierter Handel mit echten Marktpreisen. Der Kontostand wird in `state/paper_state.json` gespeichert. | keine |
| `demo` | Handel im virtuellen eToro-Konto | eToro-API-Keys für das **virtuelle** Konto |
| `live` | **Echtes Geld** | API-Keys für das **echte** Konto, verifiziertes Konto (KYC) und `ETORO_ALLOW_LIVE=yes` |

**Empfehlung:** Lass den Bot zuerst einige Wochen im Modus `paper` laufen. Schalte erst dann auf `live` um, und zwar mit kleinem Kapital.

## Strategie

Trendfolge auf Tageskerzen:
- **Kauf**: SMA 20 liegt über SMA 50, der Kurs liegt über SMA 200, und der RSI ist unter 70 (der Markt ist nicht überkauft).
- **Verkauf**: SMA 20 fällt unter SMA 50, oder Stop-Loss bzw. Take-Profit wird erreicht.
- **Stop-Loss** liegt 2 × ATR unter dem Einstieg, **Take-Profit** 4 × ATR darüber.
- Der Bot geht nur Long-Positionen ein und nutzt keinen Hebel.

## Risikolimits

- Jeder Trade riskiert höchstens 1 % des Kapitals bis zum Stop-Loss.
- Eine Position ist höchstens 15 % des Kapitals groß.
- Es sind höchstens 6 Positionen gleichzeitig offen.
- Ab 3 % Tagesverlust eröffnet der Bot an diesem Tag keine neuen Trades mehr.

Alle Werte lassen sich in `config.yaml` anpassen. Dort steht auch die Watchlist.

## Lokal benutzen

```bash
pip install -r requirements.txt
python -m etoro_bot backtest 5y   # Strategie auf 5 Jahren Historie testen
python -m etoro_bot run           # einen Handelsdurchlauf ausführen
python -m etoro_bot status        # Papier-Konto anzeigen
python -m etoro_bot find "Gold"   # eToro-Instrument-ID suchen (API-Keys nötig)
```

## Automatisch laufen lassen (GitHub Actions)

Der Workflow `.github/workflows/trading-bot.yml` läuft Montag bis Freitag um 21:30 UTC, also nach US-Börsenschluss. Danach speichert er den Kontostand und das Log (`state/trades.log`) im Repository.

1. Merge diesen Branch in `main`. Zeitgesteuerte Workflows laufen nur auf dem Standard-Branch.
2. Im Modus `paper` sind keine weiteren Schritte nötig.
3. Für `demo` oder `live` brauchst du API-Keys:
   1. Erstelle die Keys bei eToro unter *Settings → Trading → API Key Management*.
   2. Lege sie im Repository unter *Settings → Secrets and variables → Actions* als Secrets an: `ETORO_API_KEY` und `ETORO_USER_KEY`.
   3. Nur für `live`: Lege zusätzlich die Variable `ETORO_ALLOW_LIVE` mit dem Wert `yes` an.
4. Trage für jedes Instrument die `instrument_id` in `config.yaml` ein. Du findest sie mit `python -m etoro_bot find`.

## Hinweis zur API

eToro dokumentiert nicht alle Antwortformate seiner API. Der Client wertet die Antworten deshalb tolerant aus. Prüfe beim ersten Lauf im Modus `demo` oder `live` das Log genau, bevor du dich auf den Bot verlässt.
