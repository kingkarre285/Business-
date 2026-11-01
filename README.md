# Website Psychotherapie-Praxis

Fertige Website für eine Praxis für tiefenpsychologisch fundierte Psychotherapie.
Reines HTML, CSS und ein PHP-Kontaktformular – läuft ohne Änderungen auf jedem
IONOS-Webhosting-Paket.

**Bewusste Entscheidung:** Die Seite lädt nichts von fremden Servern – keine
Google Fonts, kein CDN, kein Tracking. Deshalb braucht sie **kein Cookie-Banner**.
Das ist bei Gesundheitsdaten der sauberste Weg und spart Ihnen dauerhaft Ärger.

---

## 1. Dateien im Überblick

| Datei | Inhalt |
|---|---|
| `index.html` | Startseite: Banner, Angebotsübersicht, Arbeitsweise, Krisenhinweise |
| `psychotherapie.html` | Hauptseite: Verfahren, Anlässe, Formen, Ablauf, Kosten, FAQ |
| `mental-health-coaching.html` | Mental Health Coaching, ohne Krankheitsbezug |
| `adhs-diagnostik.html` | ADHS-Abklärung für Erwachsene |
| `ueber-mich.html` | Person, Werdegang, Qualifikationen |
| `kontakt.php` | Kontaktdaten, Anfahrt und Formular (verschickt die Anfrage per E-Mail) |
| `impressum.html` | Pflichtangaben – **muss ausgefüllt werden** |
| `datenschutz.html` | Datenschutzerklärung – **muss geprüft werden** |
| `404.html` | Fehlerseite |
| `.htaccess` | HTTPS-Umleitung, Sicherheits-Header, Caching |
| `robots.txt`, `sitemap.xml` | Für Suchmaschinen |
| `werkzeuge/` | Hilfsskripte für Fotos, Navigation, Platzhalter und Upload |
| `assets/css/style.css` | Gesamtes Design |
| `assets/css/fonts.css` | Einbindung der Schriften |
| `assets/fonts/` | Nunito und Roboto als lokale Dateien |
| `assets/js/main.js` | Mobiles Menü (die Seite funktioniert auch ohne JavaScript) |
| `assets/img/favicon.svg` | Symbol im Browser-Tab |
| `assets/img/*.jpg` / `*.webp` | Fotos der Praxis, siehe Abschnitt 2 |

## 1a. Aufbau und Gewichtung

Die Angebote sind bewusst gestaffelt: **Psychotherapie** steht im Mittelpunkt –
eigener Menüpunkt an zweiter Stelle, auf der Startseite als breiter,
hervorgehobener Block. Die Möglichkeit, als **Selbstzahlerin oder Selbstzahler**
zu kommen, ist dabei durchgehend mitgedacht und nicht als Randnotiz behandelt.
Darunter folgen **Coaching** und **ADHS-Diagnostik** als gleichwertige, kleinere
Karten.

### Eine Seite hinzufügen (etwa das Flugangst-Seminar)

Auf der Startseite ist der Platz dafür schon vorbereitet: In `index.html`
steht im Abschnitt „Angebote" ein auskommentierter Block mit dem Kommentar
`PLATZ FÜR DAS FLUGANGST-SEMINAR`. Kommentarzeichen entfernen, Text einsetzen –
fertig.

Für eine eigene Unterseite:

1. `mental-health-coaching.html` kopieren und umbenennen, dann den Inhalt zwischen
   `<main id="inhalt">` und `</main>` ersetzen.
2. In `werkzeuge/navigation-aktualisieren.py` die Liste `NAVIGATION` ergänzen
   und die Datei zu `SEITEN` hinzufügen.
3. Im Projektordner ausführen:

   ```
   python3 werkzeuge/navigation-aktualisieren.py
   ```

   Damit erscheint der neue Menüpunkt auf **allen** Seiten – Sie müssen nicht
   jede Datei einzeln anfassen.
4. Die Seite in `sitemap.xml` eintragen (dort steht bereits ein vorbereiteter
   Block als Kommentar).

Führt der Link auf eine fremde Website statt auf eine eigene Unterseite,
genügt es, in `index.html` die Adresse einzutragen und
`target="_blank" rel="noopener"` zu ergänzen.

## 1b. Gestaltung

**Aufbau** und Typografie sind an **loew-psychotherapie.de** angelehnt: sehr
viel Weißraum, eine kurze Akzentlinie unter jeder Überschrift, Schaltflächen
als Pillen in Versalien. Schriften sind Roboto (Überschriften, kräftig) und
Nunito Light (Fließtext) – wie bei der Vorlage.

**Die Farbwelt ist dagegen warm**, nicht kühl wie dort – und die Grundfarbe
der Seite ist ein **Beige, kein Weiß**. Vier Flächenebenen geben Tiefe:

| Ebene | Farbe | Wo |
|---|---|---|
| Karten | `#fdfaf4` | Karten, Eingabefelder – heller als der Grund |
| Grundton | `#f4ebdd` | die Seite selbst |
| Wechselfläche | `#ebdfcb` | jeder zweite Abschnitt |
| Dunkel | `#3d352c` | Fußzeile, Bildband, Schaltflächen |

Dazu Sand (`#c9a878`) für Linien und das Wortzeichen sowie Terrakotta
(`#8a5535`) für hervorgehobenen Text.

Die Schwarzweißbilder sind in dieselbe Palette getönt – reines Weiß im Bild
würde auf dem beigen Grund als heller Kasten auffallen. Dafür gibt es
`werkzeuge/bilder-toenen.py`; die Zielfarben stehen oben im Skript und
müssen mitgeändert werden, wenn Sie die Palette anpassen.

Die Schriften liegen **lokal** unter `assets/fonts/` und werden nicht von
Google geladen. Beide Lizenzen erlauben das ausdrücklich (Nunito: SIL Open
Font License, Roboto: Apache 2.0). Bitte binden Sie sie nicht versehentlich
wieder über die Google-Fonts-URL ein – genau das ist in Deutschland bereits
abgemahnt worden.

Alle Textfarben sind auf Kontrast geprüft und erfüllen mindestens die
WCAG-Stufe AA: Fließtext 5,7:1, kleine Labels 5,0:1, Überschriften 10,2:1.
Bei einer Praxis-Website, die auch erschöpfte oder ältere Menschen erreichen
soll, ist Lesbarkeit wichtiger als die letzte Nuance. Der sandfarbene Akzent
ist deshalb ausschließlich für Linien und Flächen gedacht, nie für Text.

Alle Farben stehen gesammelt im Block `:root` ganz oben in `style.css`.

---

## 2. Vor dem Onlinestellen: Checkliste

### Unbedingt erforderlich

- [ ] **Impressum durchlesen.** Anschrift, Kammer, Aufsichtsbehörde und
      berufsrechtliche Regelungen sind eingetragen. Offen: die
      Berufshaftpflichtversicherung und die Bildnachweise. Ein unvollständiges
      Impressum ist abmahnfähig.
- [ ] **Datenschutzerklärung prüfen.** Verantwortliche Stelle und Aufsichtsbehörde
      (Hessischer Beauftragter für Datenschutz) sind eingetragen. Offen: die
      Speicherdauer der Logfiles bei IONOS und das Datum unter „Stand".
- [ ] **Auftragsverarbeitungsvertrag mit IONOS abschließen.** Im IONOS-Kundenkonto
      unter „Vertrag zur Auftragsverarbeitung“. Muss vor dem Livegang stehen.
- [ ] **Absenderpostfach anlegen** und die Werte in `kontakt.php` prüfen (Abschnitt 4).
- [ ] **SSL-Zertifikat bei IONOS aktivieren** (im Paket enthalten, ein Klick).

### Vorläufige Angaben ersetzen

Die echten Praxisdaten sind eingesetzt – Name, Anschrift, Telefon, E-Mail,
Kammer, Aufsichtsbehörde, Werdegang und Anfahrt.

Honorare, Sprechzeiten und Wartezeiten enthalten dagegen **Beispielwerte**,
damit die Seite vollständig aussieht. Diese Werte sind plausibel, aber
erfunden – sie müssen vor dem Livegang ersetzt werden.

**Alle betroffenen Stellen auflisten:**

```
python3 werkzeuge/platzhalter-pruefen.py
```

Das Skript nennt Datei und Zeilennummer und unterscheidet zwischen
eingesetzten Beispielwerten (`·`) und noch gar nicht ausgefüllten Stellen (`!`).

**Im Browser sichtbar machen:** In `assets/css/style.css` steht am Anfang von
Abschnitt 10 eine auskommentierte Regel. Aktivieren Sie sie, werden alle
vorläufigen Angaben gelb hervorgehoben – praktisch für einen letzten Rundgang
durch die Seiten. Danach wieder auskommentieren.

Jede vorläufige Angabe steht im HTML in einem
`<span class="platzhalter">…</span>`. Wenn Sie den Wert ersetzen, entfernen Sie
bitte auch dieses `span` – dann wird die Prüfliste kürzer.

**Diese Beispielwerte stecken drin:**

| Wo | Angabe | Eingesetzt |
|---|---|---|
| `psychotherapie.html` | Wartezeit Therapieplatz / Sprechstunde | 6 bzw. 2 Wochen |
| `psychotherapie.html` | Erstgespräch, Einzelsitzung | je 110 € |
| `psychotherapie.html` | Ausfallhonorar | 80 € |
| `mental-health-coaching.html` | Doppelsitzung 100 Min | 340 €, aus den 180 € abgeleitet |
| `mental-health-coaching.html` | Ausfallhonorar | 130 €, aus den 180 € abgeleitet |
| `mental-health-coaching.html` | Umsatzsteuerhinweis | „inklusive“ |
| `adhs-diagnostik.html` | Vorgespräch | 110 € |
| `adhs-diagnostik.html` | Gesamtpaket, Umfang | 690 €, 3–4 Termine über 4 Wochen |
| `kontakt.php` | Telefonzeit | Di und Do, 12–13 Uhr |
| `kontakt.php` | Sprechzeiten | Mo–Do 9–18, Fr 9–13 Uhr |
| `datenschutz.html` | Logfile-Speicherdauer | 7 Tage |
| `datenschutz.html` | Löschfrist unbeantworteter Anfragen | sechs Monate |
| `datenschutz.html` | Serverstandort, Stand | Deutschland, September 2026 |
| `impressum.html` | Berufshaftpflichtversicherung | noch offen |
| `impressum.html` | Bildnachweise | noch offen |

Drei Hinweise zu den Beträgen:

**Das Coaching-Honorar steht fest: 180 €** für das Erstgespräch und für jede
Sitzung von 50 Minuten. Diese beiden Beträge sind bestätigt und daher nicht
mehr als Beispielwert markiert. Doppelsitzung und Ausfallhonorar sind aus den
180 € abgeleitet und noch zu bestätigen.

**Die 110 € orientieren sich an der GOP.** Die Ziffer 870 für eine Einzelsitzung
von 50 Minuten ergibt beim 2,3-fachen Satz rund 100 €. Für Selbstzahler sind
Sie in der Preisgestaltung frei.

**Coaching ist umsatzsteuerpflichtig**, anders als eine Heilbehandlung nach
§ 4 Nr. 14 UStG. Unter der Honorartabelle steht derzeit „inklusive der
gesetzlichen Umsatzsteuer“. Bitte prüfen Sie, ob das für Sie zutrifft oder ob
die Kleinunternehmerregelung nach § 19 UStG greift – im zweiten Fall muss der
Satz weg und stattdessen ein entsprechender Hinweis stehen. Falls Sie
umsatzsteuerpflichtig sind, gehört zusätzlich die USt-IdNr. ins Impressum.

Weitere offene Punkte:

- [ ] **Anschrift der KV Hessen** im Impressum gegenprüfen.
- [ ] **Sitzungsfrequenz prüfen:** Die alte Website nennt ein- bis zweimal
      wöchentlich und 24–100 Sitzungen. Die neuen Texte nennen die Regelwerte
      der Psychotherapie-Richtlinie. Bitte einmal durchlesen, ob das zu Ihrer
      Arbeitsweise passt.

### Bilder austauschen

Es sind **echte Fotos der Praxis** eingebunden. Zum Austauschen die Dateien
in `assets/img/` überschreiben – die Dateinamen müssen gleich bleiben, dann
muss am HTML nichts geändert werden.

| Datei | Wo sie erscheint | Motiv |
|---|---|---|
| `banner` | Banner oben auf der Startseite | Vorhang, Wand und Sofalehne |
| `praxis-sofa` | Zitatband auf der Startseite | Sofa mit Bild und Pflanze |
| `praxis-licht` | zurzeit nirgends – Quelle für `banner` | Fenster mit Lichteinfall |
| `praxis-sessel` | „Ein Raum, der trägt", Psychotherapie-Seite | Sessel mit Bilderwand |
| `praxis-bilderwand` | „Wo wir arbeiten", Coaching-Seite | Bilderwand mit Blumen |
| `praxis-wartebereich` | „Wohin Sie kommen", Kontaktseite | Wartebereich mit zwei Sesseln |
| `portraet` | Über-mich-Seite | Porträtfoto |

**Am einfachsten geht es mit dem Skript** – es schneidet zu, verkleinert und
legt beide Dateiformate an:

```
python3 werkzeuge/bilder-aufbereiten.py praxis-sofa ~/Bilder/neues-foto.jpg
```

Die Zielmaße und die Ausschnittlage jedes Bildplatzes stehen oben im Skript
in `BILDPLAETZE`. Die Lage bestimmt, welcher Teil eines Hochformats erhalten
bleibt: `0.0` oben, `0.5` mittig, `1.0` unten.

Zu jeder `.jpg` gehört eine gleichnamige `.webp`; moderne Browser laden die
kleinere WebP-Fassung. Wenn Sie eine Datei von Hand austauschen, denken Sie
an beide – sonst zeigen manche Browser weiterhin das alte Bild.

Die Bildbeschreibungen für Screenreader (`alt`-Texte) im HTML beschreiben die
jetzigen Motive und müssen beim Austausch mitgeändert werden.

**Noch offen – das Bannerbild.** Der Platz `banner` ist auf 2400 × 900 px
ausgelegt, weil das Band über die ganze Bildschirmbreite läuft. Das jetzige
Bild ist aus `praxis-licht.jpg` entstanden und hat nur 1080 × 405 px, weil
die Vorlage nicht größer vorliegt. Auf einem breiten Monitor rechnet der
Browser es hoch und es wirkt dort weich. Da auf dem Banner keine Schrift
liegt und es nicht abgedunkelt ist, sieht man das – es ist die
auffälligste offene Stelle der Seite. Mit der Originaldatei der Fotografin
ist es mit einem Aufruf behoben:

```
python3 werkzeuge/bilder-aufbereiten.py banner ~/Bilder/original.jpg
```

Geeignet ist ein ruhiges Querformat, das auch als flacher Streifen noch
etwas zeigt. Wie hoch der Streifen ist, hängt von der Fensterbreite ab:
etwa ein Viertel davon, höchstens 30rem. Der Ausschnitt sitzt mittig,
etwas über der Bildmitte – zu ändern über die Lage im Skript und
`object-position` bei `.banner img` in `style.css`.

`praxis-licht.jpg` bleibt im Ordner, obwohl es gerade auf keiner Seite
erscheint: Es ist die Vorlage für das Bannerbild.

**Noch offen – das Porträtfoto.** Es stammt von der alten Website und liegt
nur in 356 × 399 px vor. Auf modernen Bildschirmen wirkt es dadurch etwas
weich – falls die Originaldatei der Fotografin existiert, lohnt sich der
Austausch. Außerdem gehören die Bildnachweise ins Impressum.

### Die Seite vorab ansehen

```
python3 werkzeuge/vorschau-bauen.py
```

Das bündelt alle Seiten samt Schriften und Bildern in eine einzelne Datei
`vorschau.html`, die sich per Doppelklick öffnen und weitergeben lässt –
ohne Webserver und ohne die Seite online zu stellen. Oben schaltet eine
Leiste zwischen den Seiten um; ein Hinweisstreifen weist die Datei als
Entwurf aus.

## 3. Die alte Seite auf IONOS ablösen

Auf der Domain läuft bisher eine andere Website. Der Umstieg ist so
aufgebaut, dass er in **einem Moment** passiert und sich mit **einer einzigen
Datei zurücknehmen** lässt, falls etwas nicht stimmt.

### 3.1 Vorher erledigen

- Die Checkliste aus Abschnitt 2 abarbeiten. Vor allem: keine Beispielwerte
  mehr bei Honoraren und Sprechzeiten.
- **SSL-Zertifikat aktivieren**, falls noch nicht geschehen. Die `.htaccess`
  erzwingt HTTPS – ohne Zertifikat ist die Seite danach nicht erreichbar.
- **PHP 8.x** einstellen (IONOS: Hosting → PHP-Einstellungen).
- Das Absenderpostfach anlegen (Abschnitt 4).
- Prüfen, ob es sich um ein **Managed-WordPress-Paket** handelt. Dort lässt
  sich nicht einfach eigenes HTML ablegen; das Paket muss dann erst auf
  normales Webhosting umgestellt werden. Beim gewöhnlichen Webhosting-Paket
  mit SFTP-Zugang ist alles in Ordnung.

### 3.2 Die Dateien holen

Im GitHub-Repository oben links auf den Zweig
`claude/psychotherapy-practice-homepage-7ozcxi` umschalten, dann
**Code → Download ZIP**. Das Archiv entpacken.

### 3.3 Die alte Seite sichern

**Nicht überspringen.** Auch wenn alles gut geht, ist das die Rückfahrkarte.

1. Im FTP-Programm den **gesamten bisherigen Inhalt** des Domainverzeichnisses
   herunterladen und beiseitelegen.
2. Falls eine Datenbank dazugehört (bei WordPress immer): im IONOS-Konto unter
   **Datenbanken → phpMyAdmin** die Datenbank exportieren und die Datei
   ebenfalls aufheben.
3. Die bisherige `.htaccess` getrennt aufbewahren – die wird gleich
   überschrieben und ist der schnellste Rückweg.

### 3.4 Hochladen

Damit nicht versehentlich das Falsche auf den Server kommt, legt ein Skript
den Upload-Ordner an:

```
python3 werkzeuge/paket-bauen.py
```

Daraus entsteht:

```
hochladen/1-zuerst/    alle Seiten, Bilder, Schriften
hochladen/2-zuletzt/   nur die .htaccess
hochladen/LIESMICH.txt eine Kurzfassung dieser Anleitung
```

`README.md`, `CLAUDE.md`, der Ordner `werkzeuge` und `.git` sind darin nicht
enthalten – die gehören nicht ins Internet. Stehen noch Beispielwerte in den
Seiten, warnt das Skript am Ende.

Mit [FileZilla](https://filezilla-project.org) per **SFTP** verbinden
(Zugangsdaten: IONOS → Hosting → SFTP/SSH) und in das Verzeichnis der Domain
wechseln – je nach Paket `/`, `htdocs` oder der Domainname.

Jetzt den **Inhalt** von `1-zuerst` hochladen, nicht den Ordner selbst.

Solange die alte `.htaccess` noch liegt, ist weiterhin die alte Seite zu
sehen. Die neuen Dateien liegen nur daneben.

### 3.5 Umschalten

Jetzt die `.htaccess` aus `2-zuletzt` hochladen. Ab diesem Moment ist die
neue Seite online: Darin steht `DirectoryIndex index.html index.php`, und
damit gewinnt `index.html` gegen die `index.php` der alten Installation.

> Die Datei `.htaccess` beginnt mit einem Punkt und wird von manchen
> FTP-Programmen ausgeblendet. In FileZilla:
> *Server → Versteckte Dateien anzeigen erzwingen*.

### 3.6 Prüfen

- Startseite aufrufen – kommt die neue Seite?
- Adresse ohne `www` eingeben: leitet sie auf `www` um?
- `http://` eingeben: springt sie auf `https://`?
- Jede Seite über das Menü einmal anklicken.
- Das **Kontaktformular abschicken** und nachsehen, ob die E-Mail ankommt.
- Eine alte Adresse testen, etwa `/kontakt/` – sie muss auf `kontakt.php`
  weiterleiten.
- Eine erfundene Adresse eingeben, etwa `/gibtsnicht` – es muss die eigene
  404-Seite kommen.

### 3.7 Falls etwas nicht stimmt

Die alte `.htaccess` wieder hochladen. Die alte Seite ist sofort zurück, denn
deren Dateien liegen ja noch alle da.

### 3.8 Aufräumen – erst nach ein paar Wochen

Die alten Dateien stören nicht, sie sind nur nicht mehr erreichbar. Wenn die
neue Seite eine Weile stabil läuft:

- Die Dateien der alten Installation löschen (bei WordPress: `wp-admin`,
  `wp-includes`, `wp-content`, `wp-config.php`, `index.php`, `xmlrpc.php`
  und was sonst nicht zur neuen Seite gehört).
- Die alte Datenbank löschen – der Export liegt ja gesichert.

Danach die Sitemap in der **Google Search Console** neu einreichen
(`https://www.holm-psychotherapie.de/sitemap.xml`), damit Google die neuen
Adressen zügig aufnimmt.

---

## 4. Kontaktformular einrichten

Ganz oben in `kontakt.php` stehen vier Werte:

```php
$empfaenger = 'kontakt@holm-psychotherapie.de';   // wohin die Anfragen gehen
$absender   = 'website@holm-psychotherapie.de';  // Absender der Benachrichtigung
$betreff    = 'Neue Terminanfrage über die Website';
$mindestzeit = 3;                        // Sekunden – Bremse gegen Bots
```

**Wichtig:** `$absender` muss eine E-Mail-Adresse **Ihrer eigenen Domain** sein
und im IONOS-Konto tatsächlich existieren. Eine fremde Adresse (etwa `@gmail.com`)
lässt der Mailserver nicht durch oder die Nachricht landet im Spam. Legen Sie
dafür im IONOS-Konto ein Postfach oder eine Weiterleitung
`website@holm-psychotherapie.de` an.

> **Hinweis:** Im alten Impressum stand `kontakt@holm-therapie.de`, auf der
> Kontaktseite dagegen `kontakt@holm-psychotherapie.de`. Ich habe durchgehend
> die zweite Adresse eingetragen. Falls das falsch ist, bitte einmal global
> ersetzen.

**Wenn keine E-Mails ankommen:**

1. Spam-Ordner prüfen.
2. Prüfen, ob `$absender` wirklich zur Domain gehört und das Postfach existiert.
3. In den IONOS-PHP-Einstellungen sicherstellen, dass `mail()` nicht deaktiviert ist.
4. Kommt weiterhin nichts an, ist SMTP-Versand die robustere Lösung
   (Bibliothek PHPMailer mit den IONOS-SMTP-Zugangsdaten) – sagen Sie Bescheid,
   dann rüste ich das nach.

### Wie das Formular gegen Spam geschützt ist

- **Honeypot:** ein für Menschen unsichtbares Feld. Bots füllen es aus und werden
  aussortiert.
- **Zeitprüfung:** Wer das Formular in unter drei Sekunden abschickt, ist kein Mensch.
- **Header-Bereinigung:** Zeilenumbrüche in Eingaben werden entfernt, damit niemand
  über das Formular eigene E-Mail-Header einschleusen kann.
- Kein Captcha – ein Google-reCAPTCHA würde Daten Ihrer Besucher an Google
  übertragen und wäre ohne Einwilligungsbanner nicht zulässig.

### Datensparsamkeit

Das Formular fragt bewusst **keine** Gesundheitsdaten ab und weist die Besucher
ausdrücklich darauf hin, keine Diagnosen oder Krankengeschichten hineinzuschreiben.
E-Mail ist kein sicherer Kanal für solche Angaben. Bitte behalten Sie diesen
Hinweis bei.

---

## 5. Lokal ansehen und ändern

Zum reinen Ansehen genügt ein Doppelklick auf `index.html`. Das Formular braucht
allerdings PHP. Mit einem installierten PHP starten Sie im Projektordner:

```bash
php -S localhost:8000
```

Dann im Browser `http://localhost:8000` öffnen.

Farben und Schriftgrößen liegen gesammelt ganz oben in `assets/css/style.css`
im Block `:root` – dort ändern Sie das Erscheinungsbild der gesamten Seite an
einer einzigen Stelle.

---

## 6. Wenn Sie später etwas hinzufügen

Sobald Sie externe Dienste einbinden, ändert sich die Rechtslage:

| Ergänzung | Folge |
|---|---|
| Google Maps, YouTube, Vimeo | Einwilligungsbanner nötig; besser: statisches Bild plus Textlink |
| Google Fonts vom Google-Server | Abmahnrisiko; Schriften stattdessen lokal einbinden |
| Google Analytics, Matomo mit Cookies | Einwilligungsbanner nötig |
| Online-Terminbuchung | Auftragsverarbeitungsvertrag mit dem Anbieter nötig |
| Newsletter | Double-Opt-in und eigener Abschnitt in der Datenschutzerklärung |

In allen Fällen muss zusätzlich die `Content-Security-Policy` in der `.htaccess`
erweitert werden – sonst blockiert der Browser die neuen Inhalte.

---

## 7. Rechtlicher Hinweis

Impressum und Datenschutzerklärung sind sorgfältig erstellte **Vorlagen**, keine
Rechtsberatung. Für Heilberufe gelten besondere Anforderungen (Heilmittelwerbegesetz,
Berufsordnung der Kammer, Schweigepflicht). Lassen Sie beide Texte vor dem Livegang
einmalig von Ihrer Psychotherapeutenkammer oder einer Fachanwältin für IT-Recht
prüfen – viele Kammern bieten diese Prüfung für Mitglieder kostenlos an.
