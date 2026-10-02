# Scanner und Backtest für eToro

Prüft die Regel „mindestens X % netto pro Trade innerhalb von 24 Stunden“
mit echten eToro-Kursdaten. Es werden **keine Trades ausgeführt**, das Skript liest nur Kurse.

## Ausführen

```bash
python3 -m trading.run                                     # 24 Stunden, Stundenkerzen
python3 -m trading.run --horizon 168 --interval FourHours  # 1 Woche, 4-Stunden-Kerzen
python3 -m trading.run --horizon 720 --interval OneDay     # 1 Monat, Tageskerzen (ca. 4 Jahre)
python3 -m trading.run --target 10                         # anderes Ziel, z. B. 10 % netto
python3 -m trading.run --cached                            # gespeicherte Kurse wiederverwenden

# 3 % Ziel, Stop bei 1,5 %, ohne Hebel, 1 % Risiko pro Trade, 1 Woche
python3 -m trading.run --target 3 --stop 1.5 --max-leverage 1 --risk 1 \
    --horizon 168 --interval FourHours
```

Der Bericht landet in `results/report_<Stunden>h_<Ziel>pct.md`.

Außerhalb der Claude-Code-Cloud müssen `ETORO_API_KEY` und `ETORO_USER_KEY` gesetzt sein.
Nur Python 3.10+ ist nötig, zusätzliche Pakete braucht es nicht.

## Einstellungen

Alles steht in `config.py`: Mindestgewinn (`MIN_NET_PROFIT_PCT`), Zeitfenster,
Stop-Loss, Einsatz pro Trade, Märkte, Hebel und geschätzte Kosten.

## Dateien

- `analysis.py`: Scanner (theoretische Obergrenze) und Backtest mit den Einstiegsregeln `breakout`, `trend` und `pullback` (Option `--strategy`)
- `etoro_client.py`: Lesezugriff auf die eToro-Kursdaten
- `walkforward.py`: wählt jeden Monat Markt und Strategie neu, nur anhand der Vergangenheit (`python3 -m trading.walkforward --cached`)
- `run.py`: führt alles aus und schreibt `results/report_<Stunden>h_<Ziel>pct.md`

## Demo-Bot

Handelt die beste Walk-Forward-Variante im **eToro-Demokonto**: Er wählt monatlich die
5 besten Kombinationen aus Markt und Strategie (letzte 6 Monate), riskiert 1 % des Kontos
pro Trade, nutzt Hebel 2x, Ziel +10 % / Stop −5 % auf den Einsatz und schließt spätestens nach 30 Tagen.

```bash
python3 -m trading.bot              # Probelauf: zeigt nur, was der Bot tun würde
python3 -m trading.bot --execute    # Orders im Demokonto ausführen
```

Der Bot ruft ausschließlich Demo-Adressen der eToro-API auf und fasst nur Positionen an,
die er selbst eröffnet hat. Zustand und Protokoll liegen in `bot/state.json` und `bot/log.md`.
