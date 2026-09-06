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
| `index.html` | Startseite: Angebotsübersicht, Arbeitsweise, Krisenhinweise |
| `psychotherapie.html` | Hauptseite: Verfahren, Anlässe, Formen, Ablauf, Kosten, FAQ |
| `coaching.html` | Coaching und Beratung ohne Krankheitsbezug |
| `adhs-diagnostik.html` | ADHS-Abklärung für Erwachsene |
| `ueber-mich.html` | Person, Werdegang, Qualifikationen |
| `kontakt.php` | Kontaktdaten, Anfahrt und Formular (verschickt die Anfrage per E-Mail) |
| `impressum.html` | Pflichtangaben – **muss ausgefüllt werden** |
| `datenschutz.html` | Datenschutzerklärung – **muss geprüft werden** |
| `404.html` | Fehlerseite |
| `.htaccess` | HTTPS-Umleitung, Sicherheits-Header, Caching |
| `robots.txt`, `sitemap.xml` | Für Suchmaschinen |
| `werkzeuge/` | Hilfsskripte für Fotos und Navigation |
| `assets/css/style.css` | Gesamtes Design |
| `assets/css/fonts.css` | Einbindung der Schriften |
| `assets/fonts/` | Nunito und Roboto als lokale Dateien |
| `assets/js/main.js` | Mobiles Menü (die Seite funktioniert auch ohne JavaScript) |
| `assets/img/favicon.svg` | Symbol im Browser-Tab |
| `assets/img/*.jpg` / `*.webp` | Bilder – derzeit Platzhalter, siehe Abschnitt 2 |

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

1. `coaching.html` kopieren und umbenennen, dann den Inhalt zwischen
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

Das Design ist an **loew-psychotherapie.de** angelehnt: kühles Blaugrau statt
warmer Töne, Mint als einzige Akzentfarbe, sehr viel Weißraum, eine kurze
Mint-Linie unter jeder Überschrift, Buttons als dunkelblaue Pillen in
Versalien. Schriften sind Roboto (Überschriften, kräftig) und Nunito Light
(Fließtext) – wie bei der Vorlage.

Die Schriften liegen **lokal** unter `assets/fonts/` und werden nicht von
Google geladen. Beide Lizenzen erlauben das ausdrücklich (Nunito: SIL Open
Font License, Roboto: Apache 2.0). Bitte binden Sie sie nicht versehentlich
wieder über die Google-Fonts-URL ein – genau das ist in Deutschland bereits
abgemahnt worden.

Zwei Farben weichen bewusst von der Vorlage ab: Fließtext und die kleinen
Labels sind etwas dunkler gehalten. Die Originalwerte liegen an der Grenze
des Lesbaren; bei einer Praxis-Website, die auch erschöpfte oder ältere
Menschen erreichen soll, ist der Kontrast wichtiger als die letzte Nuance.

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

### Inhalte anpassen

Die echten Praxisdaten sind bereits eingesetzt – Name, Anschrift, Telefon,
E-Mail, Kammer, Aufsichtsbehörde, Werdegang und Anfahrt stammen von
holm-psychotherapie.de. Offen sind noch:

- [ ] **Sprechzeiten und Telefonzeit.** Stehen als `[Bitte hier Ihre Zeiten
      eintragen]` in `kontakt.php`. Auf der alten Website waren keine Zeiten
      angegeben.
- [ ] **Honorare** (`[xxx] €`) in den Tabellen auf `psychotherapie.html`,
      `coaching.html` und `adhs-diagnostik.html`.
- [ ] **Wartezeit** in `psychotherapie.html` – und diese Angabe regelmäßig aktualisieren.
- [ ] **Umfang der ADHS-Diagnostik** in `adhs-diagnostik.html`: Anzahl der
      Termine und Zeitraum (`[x] Termine`, `[x] Wochen`).
- [ ] **Berufshaftpflichtversicherung** im Impressum (Versicherer und Geltungsbereich).
- [ ] **Bildnachweise** im Impressum, sobald die endgültigen Fotos feststehen.
- [ ] **Anschrift der KV Hessen** im Impressum gegenprüfen.
- [ ] **Sitzungsfrequenz prüfen:** Die alte Website nennt ein- bis zweimal
      wöchentlich und 24–100 Sitzungen. Die neuen Texte nennen die Regelwerte
      der Psychotherapie-Richtlinie. Bitte einmal durchlesen, ob das zu Ihrer
      Arbeitsweise passt.

### Bilder austauschen

Die vier Bilder sind **Platzhalter** von der alten Website. Zum Austauschen
einfach die Dateien in `assets/img/` überschreiben – die Dateinamen müssen
gleich bleiben, dann muss am HTML nichts geändert werden.

| Datei | Wo sie erscheint | Empfohlene Größe |
|---|---|---|
| `baum-kopf.jpg` | Startseite, neben der Hauptüberschrift | quadratisch, ab 900 × 900 px |
| `hero-meer.jpg` | Zitatband auf der Startseite | quer, ab 1800 × 1000 px |
| `raum.jpg` | „Wohin Sie kommen", Kontaktseite | quer, ab 1400 × 950 px |
| `portraet.jpg` | Über-mich-Seite | hoch, ab 800 × 1000 px |

Zu jeder `.jpg` gehört eine gleichnamige `.webp`. Moderne Browser laden die
WebP-Fassung, weil sie kleiner ist. Wenn Sie nur die JPEG austauschen, zeigen
diese Browser weiterhin das alte Bild – löschen Sie in dem Fall die zugehörige
`.webp`, dann greifen alle auf die JPEG zurück.

Am einfachsten: Schicken Sie mir die neuen Fotos, dann schneide ich sie zu,
verkleinere sie und lege beide Formate an. Alternativ erledigt das Skript
`werkzeuge/bilder-aufbereiten.py` die Umrechnung.

Die Bildbeschreibungen für Screenreader (`alt`-Texte) beschreiben die
jetzigen Motive und müssen beim Austausch mit angepasst werden.

## 3. Auf IONOS hochladen

1. Im IONOS-Kundenkonto unter **Hosting → SFTP/SSH** die Zugangsdaten ansehen
   (Server, Benutzername, Passwort).
2. Ein FTP-Programm installieren, zum Beispiel [FileZilla](https://filezilla-project.org)
   (kostenlos).
3. Verbinden – bitte **SFTP** wählen, nicht das unverschlüsselte FTP.
4. Auf dem Server in das Verzeichnis Ihrer Domain wechseln. Es heißt je nach
   Paket `/` oder `htdocs` oder trägt den Namen der Domain.
5. Hochladen: alle `.html`-Dateien, `kontakt.php`, `.htaccess`, `robots.txt`,
   `sitemap.xml` und den kompletten Ordner `assets`.

   **Nicht hochladen:** `README.md` und den Ordner `.git` – die gehören nicht
   ins Internet. (Die `.htaccess` sperrt sie zur Sicherheit zusätzlich.)

6. In den IONOS-Einstellungen prüfen, dass **PHP 8.x** aktiv ist.
7. Website aufrufen und das Formular einmal selbst testen.

> Die Datei `.htaccess` beginnt mit einem Punkt und wird von manchen FTP-Programmen
> ausgeblendet. In FileZilla: *Server → Versteckte Dateien anzeigen erzwingen*.

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
