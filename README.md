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
| `index.html` | Startseite: Anliegen, Arbeitsweise, Ablauf, Krisenhinweise |
| `ueber-mich.html` | Person, Werdegang, Qualifikationen |
| `leistungen.html` | Therapieverfahren, weitere Angebote, FAQ |
| `ablauf-kosten.html` | Weg in die Therapie, Kassen, Honorare, Ausfallregelung |
| `kontakt.php` | Kontaktdaten, Anfahrt und Formular (verschickt die Anfrage per E-Mail) |
| `impressum.html` | Pflichtangaben – **muss ausgefüllt werden** |
| `datenschutz.html` | Datenschutzerklärung – **muss geprüft werden** |
| `404.html` | Fehlerseite |
| `.htaccess` | HTTPS-Umleitung, Sicherheits-Header, Caching |
| `robots.txt`, `sitemap.xml` | Für Suchmaschinen |
| `assets/css/style.css` | Gesamtes Design |
| `assets/js/main.js` | Mobiles Menü (die Seite funktioniert auch ohne JavaScript) |
| `assets/img/favicon.svg` | Symbol im Browser-Tab |

---

## 2. Vor dem Onlinestellen: Checkliste

### Unbedingt erforderlich

- [ ] **Impressum ausfüllen.** Alle `[eckigen Klammern]` in `impressum.html` ersetzen.
      Als Heilberuf brauchen Sie zusätzlich: Berufsbezeichnung, verleihenden Staat,
      zuständige Kammer, Aufsichtsbehörde (KV) und die berufsrechtlichen Regelungen.
      Ein unvollständiges Impressum ist abmahnfähig.
- [ ] **Datenschutzerklärung prüfen.** Platzhalter in `datenschutz.html` ersetzen,
      besonders Hoster, Speicherdauer der Logfiles und die zuständige
      Landesdatenschutzbehörde.
- [ ] **Auftragsverarbeitungsvertrag mit IONOS abschließen.** Im IONOS-Kundenkonto
      unter „Vertrag zur Auftragsverarbeitung“. Muss vor dem Livegang stehen.
- [ ] **E-Mail-Adressen in `kontakt.php` eintragen** (siehe Abschnitt 4).
- [ ] **SSL-Zertifikat bei IONOS aktivieren** (im Paket enthalten, ein Klick).

### Inhalte anpassen

Suchen und ersetzen Sie in **allen** Dateien:

| Suchen | Ersetzen durch |
|---|---|
| `Praxis am Lindenhof` | Ihren Praxisnamen |
| `Dr. phil. Anna Muster` | Ihren Namen mit Titel |
| `Musterstraße 12` | Ihre Straße |
| `12345 Musterstadt` | PLZ und Ort |
| `030 1234567` | Ihre Telefonnummer (auch in den `tel:`-Links: `+49301234567`) |
| `praxis@ihre-domain.de` | Ihre E-Mail-Adresse |
| `www.ihre-domain.de` | Ihre Domain |

Danach noch durchgehen:

- [ ] **Telefonzeiten und Sprechzeiten** (auf Startseite und Kontaktseite)
- [ ] **Werdegang und Qualifikationen** in `ueber-mich.html` – nur tatsächlich
      Vorhandenes nennen, Berufsbezeichnungen sind gesetzlich geschützt
- [ ] **Honorare** in der Tabelle in `ablauf-kosten.html` (`[xxx] €`)
- [ ] **Wartezeit** in `leistungen.html` – und diese Angabe regelmäßig aktualisieren
- [ ] **Anfahrtsbeschreibung** in `kontakt.php`
- [ ] **Porträtfoto** als `assets/img/portraet.jpg` ablegen (ca. 800 × 1000 px)
      und in `ueber-mich.html` den Platzhalter-Block durch das auskommentierte
      `<img>`-Tag ersetzen
- [ ] **Bildnachweise** im Impressum ergänzen
- [ ] Die Kommentare `<!-- ANPASSEN: ... -->` im Quelltext abarbeiten

> **Tipp:** Alle Stellen finden Sie mit der Suchfunktion Ihres Editors –
> suchen Sie nach `Muster`, `ihre-domain`, `[` und `ANPASSEN`.

---

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
$empfaenger = 'praxis@ihre-domain.de';   // wohin die Anfragen gehen
$absender   = 'website@ihre-domain.de';  // Absender der Benachrichtigung
$betreff    = 'Neue Terminanfrage über die Website';
$mindestzeit = 3;                        // Sekunden – Bremse gegen Bots
```

**Wichtig:** `$absender` muss eine E-Mail-Adresse **Ihrer eigenen Domain** sein
und im IONOS-Konto tatsächlich existieren. Eine fremde Adresse (etwa `@gmail.com`)
lässt der Mailserver nicht durch oder die Nachricht landet im Spam. Legen Sie
dafür im IONOS-Konto ein Postfach oder eine Weiterleitung `website@ihre-domain.de` an.

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
