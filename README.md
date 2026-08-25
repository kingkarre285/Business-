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

## Wie die Treffer bei dir ankommen

Zwei Kanäle, beide automatisch:

**Telegram** — der Push. Sobald ein Treffer die Schwelle reißt, kommt die Spitze
aufs Handy, mit Link zur vollen Ansicht.

```bash
export TELEGRAM_BOT_TOKEN=...   # von @BotFather: /newbot
export TELEGRAM_CHAT_ID=...     # eigene ID: dem Bot schreiben, dann
                                # https://api.telegram.org/bot<TOKEN>/getUpdates
python -m kalodata_sniper test-notify
```

Telegram ist standardmäßig aktiv; ohne gesetzte Variablen meldet der Lauf das,
statt still zu scheitern.

**Die Seite** — die Rangliste zum Durchsehen. Feste Adresse, aktualisiert sich
bei jedem Lauf selbst, weil die GitHub Action sie nach GitHub Pages schiebt:

```
https://<dein-name>.github.io/<repo>/
```

Einmalig einschalten: Repo → Settings → Pages → Source auf **GitHub Actions**.
Die Adresse landet automatisch in jedem Telegram-Push (`SNIPER_REPORT_URL`).

Lokal liegen dieselben Dateien in `reports/`: `latest.html` (Ansicht),
`artifact.html` (dieselbe Seite ohne äußere Dokument-Tags, zum Einbetten oder
Veröffentlichen), `sniper_<datum>.csv` (Tabelle).

> Was **nicht** geht: eine als Claude-Artifact veröffentlichte Seite kann sich
> nicht selbst nachladen — eine veröffentlichte Seite hat keinen Zugang zu deinem
> Rechner oder zum Cronjob. Sie zeigt den Stand des Laufs, aus dem sie erzeugt
> wurde. Für „aktualisiert sich von allein" ist GitHub Pages der Weg.

### Was in der Ansicht steckt

Ablesewerte des Laufs oben, darunter die Rangliste — Score als Balken, Provision
je Verkauf, Wettbewerbsdichte, und rechts eine Sparkline des Umsatzverlaufs. Auf
dem Handy stapeln sich die Zeilen.

Zwei Details, die nicht Geschmack sind:

* **Richtung steht nie nur in der Farbe.** Jede Sparkline trägt Pfeil und
  vorzeichenbehaftete Prozentzahl (`▲ +110 %`). Ohne das wäre der Verlauf für
  rot-grün-schwache Leser eine Ratesache.
* **Steigend/fallend sind Grün und Violett**, nicht Grün und Rot. Die
  Farbprüfung (`dataviz`-Validator) hat Grün↔Orange bei ΔE 2.3 unter Protanopie
  durchfallen lassen — praktisch ununterscheidbar. Violett kommt auf ΔE 8.6.

## Datenquellen

**1. CSV/XLSX-Export (Standard, robust)**
Kalodata → Products → Filter → Export. Die Spaltennamen sind egal: das Mapping
in `kalodata_sniper/sources/csv_source.py` erkennt englische und deutsche Header,
`snake_case`- und `camelCase`-Felder sowie Varianten wie „Revenue last 7 days".
Unbekannte Spalten werden ignoriert, nicht als Fehler behandelt.

Das Mapping läuft in zwei Durchgängen — exakte Treffer zuerst, unscharfe nur für
danach noch freie Felder. Ohne diese Reihenfolge würde `product_number` (Anzahl
Produkte in einem Video) per Teiltreffer auf „product" das Namensfeld belegen,
bevor `product_title` überhaupt drankommt. Mehrdeutige Felder bleiben lieber
unzugeordnet, als falsch zugeordnet zu werden.

**2. Offizielle Open API (vollautomatisch)**
Kalodata Open Center → API-Key erzeugen. Der Vertrag laut Doku:

| | |
|---|---|
| Basis-URL | `https://www.kalodata.com/openapi/v1/tiktok/…` |
| Methode | immer **POST + JSON** |
| Auth | Secret-Key im Header |
| Pflichtfelder | `region`, `language`, `currency`, `date_range` |
| Rate-Limit | 100 Requests / 10 Sekunden |

```bash
export KALODATA_API_KEY='...'
python -m kalodata_sniper probe-api      # ein Aufruf, zeigt Feld-Mapping
```

`probe-api` kostet genau einen Request und zeigt dir, welche Antwortfelder auf
welches Produktfeld gemappt wurden — plus die nicht zugeordneten. Passt alles,
in der Config `source.type` auf `"api"` setzen.

```jsonc
"api": {
  "base_url": "https://www.kalodata.com",
  "auth": { "header": "secret-key", "prefix": "" },
  "endpoints": { "rank": "/openapi/v1/tiktok/product/list" },
  "request": {
    "region": "DE",           // US BR MX ID JP MY PH SG TH VN GB ES DE FR IT
    "language": "en-US",      // zh-CN en-US id-ID th-TH vi-VN es-ES ja-JP pt-BR ko-KR fr-FR
    "currency": "EUR",        // CNY USD IDR VND THB MYR JPY PHP GBP SGD MXN EUR BRL
    "date_range": "last7Day"  // oder "2026-08-01~2026-08-07" bzw. "2026-08"
  },
  "max_requests_per_run": 10, // hartes Budget
  "cache_ttl_minutes": 360    // Filter tunen ohne neue Credits
}
```

`date_range` nimmt auch Kurzformen: `7d` → `last7Day`, `30d` → `last30Day`,
Groß-/Kleinschreibung egal.

**Voreingestellt ist der deutsche Markt** (`region: DE`, `currency: EUR`). Eine
Einschränkung der API, die man kennen muss: **`de-DE` gibt es in der Sprachliste
nicht** — deutsche Marktdaten kommen mit englischen Textfeldern (Produkttitel,
Kategorien). Region und Währung sind davon unberührt.

Pro Lauf umschaltbar, ohne die Config anzufassen:

```bash
python -m kalodata_sniper run --region GB --currency GBP --date-range last30Day
```

> **Credits:** Die Open API rechnet nach Verbrauch ab. Drei Schutzschichten:
> Pflichtfelder werden **vor** dem Request gegen die erlaubten Werte geprüft (ein
> Tippfehler in `region` kostet so keinen Credit), ein hartes Requestbudget pro
> Lauf (`max_requests_per_run`) und ein Antwort-Cache auf der Platte — beim
> Nachjustieren der Filter wird dieselbe Antwort wiederverwendet statt neu bezahlt.
> Das Rate-Limit von 100/10 s hält der Client selbstständig ein.
> Der API-Key gehört in eine Umgebungsvariable bzw. ein GitHub-Secret, nie ins Repo.

Fehler werden übersetzt statt durchgereicht: 400 → Pflichtfeld prüfen,
401 → Header-Name falsch, 402 → Credits leer, 404 → Endpunktpfad, 429 → Rate-Limit.
Auch Fehlercodes im Body bei HTTP 200 werden erkannt.

## Aus Claude heraus bedienen (MCP)

Der Sniper läuft auch als MCP-Server — dann fragst du in Claude einfach
„zeig mir die Top-Produkte dieser Woche" statt einen Cronjob zu lesen.

```bash
claude mcp add kalodata-sniper -- python3 -m kalodata_sniper mcp
```

Oder die mitgelieferte `.mcp.json` verwenden (projektweit, wird von Claude Code
automatisch gefunden). Verfügbare Werkzeuge:

| Werkzeug | Zweck |
|---|---|
| `sniper_scan` | Lauf ausführen, Top-Kandidaten zurückgeben (`top`, `min_score`, `dry_run`) |
| `sniper_explain` | Score eines Produkts aufschlüsseln, inkl. Filtergründen |
| `sniper_watchlist` | Verlauf über mehrere Läufe (`sort: "trend"` zeigt die stärksten Anstiege) |
| `sniper_calibrate` | Filtervorschlag aus den Daten (`apply: true` schreibt ihn) |
| `sniper_config` | aktuelle Filter, Gewichte und Schwellen |
| `sniper_probe_api` | API-Anbindung prüfen (kostet einen Request) |

Der Server spricht JSON-RPC über stdio, ohne SDK-Abhängigkeit. Ein Detail, das
in der Praxis über Funktionieren oder Nicht-Funktionieren entscheidet: **stdout
gehört dem Protokoll**. Alles, was die Pipeline sonst ausgibt (inklusive
Console-Notifier), wird nach stderr umgeleitet — eine einzige Zeile Text auf
stdout würde die Verbindung zerlegen. Genau das prüft auch ein Test.

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
* **Momentum kommt aus drei Quellen, in dieser Reihenfolge:**
  1. **Eigener Verlauf** — Vergleich gegen den jüngsten Snapshot, der mindestens
     `scoring.momentum_lookback_hours` (Standard 12 h) alt ist. Zwei unabhängige
     Messungen, der belastbarste Indikator. Dass der Snapshot alt genug sein muss,
     verhindert, dass ein zweiter Lauf mit derselben Datei das Wachstum auf 0 setzt.
  2. **Tagesreihe `revenue_trend` der API** — zweite Hälfte gegen erste, längen­normiert.
     Damit gibt es Momentum schon beim **ersten** Lauf, ohne eigenen Verlauf.
  3. **Wachstumsfeld des Exports.**

  Das ist der Unterschied zwischen „Liste sortieren" und „Breakout erkennen".

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

### Filter kalibrieren statt raten

Die Standardwerte sind eine Annahme. Was im deutschen Markt normal ist, steht in
den Daten:

```bash
python -m kalodata_sniper calibrate            # Vorschlag ansehen
python -m kalodata_sniper calibrate --apply    # übernehmen
```

```
Filter                 aktuell     vorgeschlagen
------------------------------------------------
revenue_min              €3.0K            €94.0K *
commission_min           10.0%             15.0% *
creators_max               500               298 *

Kandidaten aktuell:       12 von 15
Kandidaten nach Vorschlag: 4 von 15
```

Nicht jeder Filter wird für sich gesetzt — sechs Filter multiplizieren sich, und
einzeln plausible Perzentilwerte ergeben kombiniert oft fast nichts. Stattdessen
wird die gemeinsame *Strenge* so eingeregelt, dass etwa ein Viertel der Produkte
durchkommt (`--target` verschiebt die Quote). Dabei wiegt zu streng schwerer als
zu locker: ein Filtersatz ohne Treffer ist wertlos, ein etwas zu weiter nur
unschärfer.

Von Hand: zu wenige Treffer → `revenue_min` senken oder `creators_max` erhöhen.
Zu viele → `min_score` und `commission_min` hoch.

## Alarme

Unterstützt: `console`, `telegram` (an), `discord`, `slack`, `webhook` (Roh-JSON
für n8n/Make/Zapier). Zugangsdaten kommen ausschließlich aus Umgebungsvariablen,
nie aus der Config-Datei.

Jede Nachricht enthält den Link zur vollen Ansicht, sobald `output.report_url`
oder `SNIPER_REPORT_URL` gesetzt ist. Ein defekter Kanal bricht den Lauf nicht ab
— die anderen senden trotzdem, der Fehler wird gemeldet.

Nur was neu ist oder deutlich gestiegen ist, löst aus (`only_new_or_rising`),
und derselbe Treffer nicht öfter als alle `cooldown_hours`. Sonst schickt dir
jeder Lauf dieselben zehn Produkte.

## Automatisierung

**GitHub Actions** (`.github/workflows/sniper.yml`) läuft zweimal täglich, sichert
die Reports als Artefakt und schreibt den Verlauf zurück ins Repo. Nötige Secrets:
`KALODATA_API_KEY` (nur für den API-Modus), `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
Die Action veröffentlicht den Report zusätzlich auf GitHub Pages und schreibt den
Verlauf zurück ins Repo.

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
| `run` | Ein Durchlauf. `--dry-run` schreibt nichts, `--no-alerts` sendet nicht, `--region`/`--currency`/`--date-range` überschreiben den Abruf |
| `watch --interval 3600` | Dauerlauf im festen Takt |
| `explain "<name>"` | Score-Aufschlüsselung eines Produkts inkl. Filtergründen |
| `calibrate` | Filterwerte aus echten Daten ableiten, `--apply` übernimmt sie |
| `state --top 10` | Verlauf inspizieren, `--reset` löscht ihn |
| `probe-api` | Einen API-Aufruf machen und das Feld-Mapping prüfen |
| `test-notify` | Testnachricht an alle aktiven Kanäle |
| `demo` | Beispieldaten erzeugen und Lauf zeigen |
| `mcp` | Als MCP-Server über stdio laufen |
| `init` | Standard-Config schreiben |

## Tests

```bash
python -m unittest discover -s tests -v    # 106 Tests, keine externen Abhängigkeiten
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
  calibrate.py      Filterschwellen aus echten Daten ableiten
  mcp_server.py     MCP-Server (JSON-RPC über stdio) fuer Claude & Co.
  notify.py         Telegram, Discord, Slack, Webhook, Console
  report.py         HTML-, CSV- und JSON-Report
  sources/
    csv_source.py   Export-Parsing mit unscharfem Spalten-Mapping
    api_source.py   offizielle Open API: Budget, Cache, Feld-Mapping
```

## Grenzen, ehrlich gesagt

* Der Score ist eine **Vorauswahl, keine Kaufentscheidung** — Versandzeiten,
  Lizenzthemen und Creator-Fit prüft er nicht.
* Der Pfad des Product-Listen-Endpoints (`/openapi/v1/tiktok/product/list`) und
  die Namen von `page`/`page_size` sind analog zum dokumentierten
  `video/detail`-Endpoint gesetzt, aber nicht gegen die Doku verifiziert. Ein
  `probe-api`-Aufruf klärt das; Abweichungen sind reine Config-Werte.
* Die Feldnamen des Product-Moduls sind aus dem Video-Modul abgeleitet
  (`sales_volumn`, `product_gpm`, `creator_number`, `revenue_trend`). Weicht das
  Product-Modul ab, zeigt `probe-api` genau, was nicht zugeordnet wurde.
* Momentum braucht mindestens zwei Läufe im Abstand von `momentum_lookback_hours`.
  Der erste Lauf bewertet nur den Status quo.
