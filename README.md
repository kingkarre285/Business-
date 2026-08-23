# Kalodata Product Sniper

Automatisiertes Aufspüren von Winning Products aus Kalodata-Daten (TikTok Shop):
Export einlesen → harte Filter → gewichtetes Scoring → Verlauf vergleichen →
Alarm bei Breakouts.

Der Kern läuft mit **reiner Standardbibliothek** (Python 3.9+) — keine Installation
von pandas o.ä. nötig.

```
Kalodata-Export ──┐
                  ├──► Filter ──► Scoring ──► Verlaufsvergleich ──► Alarm + Report
Kalodata-API   ───┘                             (data/state.json)   (Telegram/…)
```

## Schnellstart

```bash
git clone <dieses-repo> && cd Business-
python -m kalodata_sniper demo          # Beispieldaten erzeugen und Lauf zeigen
python -m kalodata_sniper init          # config.json anlegen
```

Dann in Kalodata unter **Products** die Filter setzen, exportieren und die Datei
nach `data/` legen:

```bash
python -m kalodata_sniper run
```

Ausgabe: Top-Kandidaten im Terminal, `reports/latest.html` zum Durchklicken,
`reports/sniper_<datum>.csv` zur Weiterverarbeitung.

## Datenquellen

**1. CSV/XLSX-Export (Standard, robust)**
Kalodata → Products → Filter → Export. Die Spaltennamen sind egal: das Mapping
in `kalodata_sniper/sources/csv_source.py` erkennt englische und deutsche Header,
`camelCase`-Felder sowie Varianten wie „Revenue last 7 days". Unbekannte Spalten
werden ignoriert, nicht als Fehler behandelt.

**2. Live-Abruf mit eigener Session (optional, vollautomatisch)**
Kalodata hat keine öffentliche API. Der Client in `sources/api_source.py` spricht
die interne Web-API mit **deinem eigenen** Session-Cookie an — also genau die
Daten, die dir im Browser ohnehin angezeigt werden.

```bash
export KALODATA_COOKIE='<cookie-header aus DevTools → Network → Request Headers>'
python -m kalodata_sniper probe-api      # zeigt, welche Felder wirklich kommen
```

Danach in der Config `source.type` auf `"api"` setzen. Interne APIs ändern sich
ohne Ankündigung — deshalb sind Endpunkt, Methode und Parameter konfigurierbar,
und `probe-api` zeigt dir die tatsächliche Antwort. Bricht der Abruf, funktioniert
der CSV-Weg unverändert weiter.

> **Wichtig:** Der Cookie gehört in eine Umgebungsvariable bzw. ein GitHub-Secret,
> nie ins Repo. Prüfe die Kalodata-Nutzungsbedingungen deines Tarifs, bevor du den
> automatischen Abruf aktivierst; der Client fragt bewusst seitenweise mit Pause ab.

## Wie der Score entsteht

Zwei Stufen — erst K.-o.-Filter, dann Bewertung. Nur was die Filter passiert,
taucht überhaupt auf.

| Baustein | Gewicht | Was gemessen wird |
|---|---|---|
| `momentum` | 3.0 | Umsatzsprung ggü. eigenem letztem Snapshot (Fallback: Wachstumsfeld des Exports) |
| `opportunity` | 2.0 | Provision in Geld pro Verkauf (Preis × Provisionssatz) |
| `traction` | 1.5 | absoluter Umsatz, logarithmisch — Nachfrage ist bewiesen |
| `competition` | 2.0 | wenige Creator = noch Platz im Markt |
| `efficiency` | 1.0 | Umsatz je Creator bzw. GPM |
| `freshness` | 1.5 | junges Listing / erst kurz im eigenen Radar |

Zwei Designentscheidungen, die den Unterschied machen:

* **Fehlende Daten werden nicht als 0 bestraft.** Liefert ein Export keine
  Creator-Zahl, fliegt der Baustein aus der Gewichtung, statt den Score zu drücken.
* **Momentum kommt aus dem eigenen Verlauf.** Verglichen wird gegen den jüngsten
  Snapshot, der mindestens `scoring.momentum_lookback_hours` (Standard 12 h) alt
  ist. Dadurch setzt ein zweiter Lauf mit derselben Exportdatei das Wachstum nicht
  auf 0 — genau das ist der Unterschied zwischen „Liste sortieren" und „Breakout
  erkennen".

Score eines einzelnen Produkts aufschlüsseln:

```bash
python -m kalodata_sniper explain "Sunset Lamp"
```

```
LED Sunset Projector Lamp
  Score 73.0/100
  Bausteine (Anteil am Score):
    momentum      1.00 ####################  Gewicht 3 -> 27.3 Pkt
    competition   0.26 #####                 Gewicht 2 ->  4.8 Pkt
    ...
```

## Konfiguration

Alles in `config.json` (Vorlage: `config.example.json`). Die wichtigsten Stellschrauben:

```jsonc
"filters": {
  "price_min": 8, "price_max": 150,   // Preisband mit gesunder Marge
  "revenue_min": 3000,                // Nachfrage muss bewiesen sein
  "commission_min": 0.10,             // unter 10% lohnt der Aufwand selten
  "rating_min": 4.0,                  // Retourenrisiko begrenzen
  "creators_max": 500,                // ab hier ist der Markt dicht
  "categories_include": [],           // leer = alle Kategorien
  "keywords_exclude": ["gift card"]
},
"alerts": {
  "min_score": 70,                    // ab wann alarmiert wird
  "only_new_or_rising": true,         // nur Neuzugänge oder Score-Anstiege
  "cooldown_hours": 24,               // gleicher Treffer nicht öfter
  "max_per_run": 10
}
```

Zu wenige Treffer? `revenue_min` senken oder `creators_max` erhöhen.
Zu viele? `min_score` hoch, `commission_min` hoch.

## Alarme

Unterstützt: `console`, `telegram`, `discord`, `slack`, `webhook` (Roh-JSON für
n8n/Make/Zapier). Zugangsdaten kommen ausschließlich aus Umgebungsvariablen.

```bash
export TELEGRAM_BOT_TOKEN=...   # von @BotFather
export TELEGRAM_CHAT_ID=...     # eigene Chat-ID
python -m kalodata_sniper test-notify
```

In der Config beim gewünschten Kanal `"enabled": true` setzen. Ein defekter Kanal
bricht den Lauf nicht ab — die anderen senden trotzdem, der Fehler wird gemeldet.

## Automatisierung

**GitHub Actions** (`.github/workflows/sniper.yml`) läuft zweimal täglich, sichert
die Reports als Artefakt und schreibt den Verlauf zurück ins Repo. Nötige Secrets:
`KALODATA_COOKIE` (nur für den API-Modus), `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.

**Cron auf einem Server:**

```cron
0 */6 * * * cd /pfad/zum/repo && /usr/bin/python3 -m kalodata_sniper run >> sniper.log 2>&1
```

**Dauerlauf im Vordergrund:**

```bash
python -m kalodata_sniper watch --interval 3600
```

## Befehle

| Befehl | Zweck |
|---|---|
| `run` | Ein Durchlauf. `--dry-run` schreibt nichts, `--no-alerts` sendet nicht |
| `watch --interval 3600` | Dauerlauf im festen Takt |
| `explain "<name>"` | Score-Aufschlüsselung eines Produkts inkl. Filtergründen |
| `state --top 10` | Verlauf inspizieren, `--reset` löscht ihn |
| `probe-api` | API-Antwort testen und gelieferte Felder auflisten |
| `test-notify` | Testnachricht an alle aktiven Kanäle |
| `demo` | Beispieldaten erzeugen und Lauf zeigen |
| `init` | Standard-Config schreiben |

## Tests

```bash
python -m unittest discover -s tests -v    # 42 Tests, keine externen Abhängigkeiten
```

## Aufbau

```
kalodata_sniper/
  cli.py            Kommandozeile
  pipeline.py       laden → bewerten → Verlauf → melden → berichten
  scoring.py        Filter, Normierungskurven, Momentum, Alarmauswahl
  state.py          Verlaufsspeicher (atomar geschrieben, robust gegen Defekte)
  config.py         Defaults + Deep-Merge der eigenen Config
  models.py         Product / ScoredProduct
  notify.py         Telegram, Discord, Slack, Webhook, Console
  report.py         HTML-, CSV- und JSON-Report
  sources/
    csv_source.py   Export-Parsing mit unscharfem Spalten-Mapping
    api_source.py   optionaler Live-Abruf mit eigener Session
```

## Grenzen, ehrlich gesagt

* Der Score ist eine **Vorauswahl, keine Kaufentscheidung** — Versandzeiten,
  Lizenzthemen und Creator-Fit prüft er nicht.
* Der API-Modus hängt an einer internen, undokumentierten Schnittstelle und kann
  jederzeit brechen. Der CSV-Weg ist der verlässliche.
* Momentum braucht mindestens zwei Läufe im Abstand von `momentum_lookback_hours`.
  Der erste Lauf bewertet nur den Status quo.
