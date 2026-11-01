#!/usr/bin/env python3
"""
Legt den Ordner an, der auf den Server hochgeladen wird.

Aufruf im Projektordner:

    python3 werkzeuge/paket-bauen.py

Daraus entsteht der Ordner `hochladen/` mit genau den Dateien, die auf den
Webserver gehören – und zwar in der Reihenfolge, in der sie hochgeladen
werden sollen:

    hochladen/1-zuerst/    alle Seiten, Bilder, Schriften
    hochladen/2-zuletzt/   nur die .htaccess

Der Grund für die Teilung: Solange die alte .htaccess auf dem Server liegt,
ist weiterhin die alte Website zu sehen. Die neuen Dateien liegen dann nur
daneben und stören nichts. Erst die neue .htaccess schaltet um. Geht etwas
schief, bringt die alte .htaccess die alte Seite sofort zurück.

Nicht mitgenommen werden README.md, CLAUDE.md, der Ordner werkzeuge, die
Vorschaudatei und alles aus .git – das gehört nicht ins Internet.
"""

import os
import shutil
import subprocess
import sys

PROJEKT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJEKT)

ZIELORDNER = 'hochladen'

# Einzelne Dateien, die auf den Server gehören
DATEIEN = ['kontakt.php', 'robots.txt', 'sitemap.xml']

# Ordner, die vollständig mitkommen
ORDNER = ['assets']

# Diese Datei schaltet um und wird deshalb getrennt abgelegt
UMSCHALTER = '.htaccess'

HINWEIS = """\
So wird hochgeladen
===================

Mit FileZilla per SFTP verbinden (Zugangsdaten im IONOS-Konto unter
Hosting > SFTP/SSH) und in das Verzeichnis der Domain wechseln.

Schritt 1
---------
Den gesamten *Inhalt* von "1-zuerst" hochladen – also die Dateien und den
Ordner assets, nicht den Ordner "1-zuerst" selbst.

Danach ist im Browser weiterhin die alte Website zu sehen. Das ist richtig
so: Die neuen Dateien liegen nur daneben.

Schritt 2
---------
Vorher die bisherige .htaccess vom Server herunterladen und aufheben. Das
ist der Rückweg.

Dann die .htaccess aus "2-zuletzt" hochladen. Ab diesem Moment ist die neue
Seite online.

Die Datei beginnt mit einem Punkt und wird von manchen FTP-Programmen
ausgeblendet. In FileZilla:
Server > Versteckte Dateien anzeigen erzwingen.

Schritt 3: prüfen
-----------------
- Startseite aufrufen
- Adresse ohne www eingeben: leitet sie auf www um?
- http:// eingeben: springt sie auf https://?
- jede Seite über das Menü anklicken
- Kontaktformular abschicken und nachsehen, ob die E-Mail ankommt
- eine alte Adresse testen, etwa /kontakt/
- eine erfundene Adresse eingeben: es muss die eigene 404-Seite kommen

Wenn etwas nicht stimmt
-----------------------
Die alte .htaccess wieder hochladen. Die alte Seite ist sofort zurück,
ihre Dateien liegen ja noch alle auf dem Server.
"""


def pruefung() -> None:
    """Warnt vor Beispielwerten, hält den Bau aber nicht auf."""
    skript = os.path.join('werkzeuge', 'platzhalter-pruefen.py')
    if not os.path.exists(skript):
        return

    ergebnis = subprocess.run([sys.executable, skript],
                              capture_output=True, text=True)
    if ergebnis.returncode == 0:
        return

    letzte = [z for z in ergebnis.stdout.splitlines() if 'zu prüfen' in z]
    print()
    print('  ACHTUNG: ' + (letzte[0].strip() if letzte
                           else 'Es stehen noch Beispielwerte in den Seiten.'))
    print('  Vor dem Livegang bitte ersetzen. Die Liste zeigt:')
    print('      python3 werkzeuge/platzhalter-pruefen.py')


def main() -> None:
    zuerst = os.path.join(ZIELORDNER, '1-zuerst')
    zuletzt = os.path.join(ZIELORDNER, '2-zuletzt')

    if os.path.exists(ZIELORDNER):
        shutil.rmtree(ZIELORDNER)
    os.makedirs(zuerst)
    os.makedirs(zuletzt)

    anzahl = 0

    seiten = sorted(d for d in os.listdir('.') if d.endswith('.html')
                    and d != 'vorschau.html')
    for datei in seiten + DATEIEN:
        if not os.path.exists(datei):
            print(f'  fehlt, übersprungen: {datei}')
            continue
        shutil.copy2(datei, os.path.join(zuerst, datei))
        anzahl += 1

    for ordner in ORDNER:
        if not os.path.isdir(ordner):
            print(f'  fehlt, übersprungen: {ordner}/')
            continue
        ziel = os.path.join(zuerst, ordner)
        shutil.copytree(ordner, ziel)
        anzahl += sum(len(d) for _, _, d in os.walk(ziel))

    if os.path.exists(UMSCHALTER):
        shutil.copy2(UMSCHALTER, os.path.join(zuletzt, UMSCHALTER))
        anzahl += 1
    else:
        print(f'  ACHTUNG: {UMSCHALTER} fehlt – ohne sie schaltet nichts um.')

    with open(os.path.join(ZIELORDNER, 'LIESMICH.txt'), 'w',
              encoding='utf-8') as f:
        f.write(HINWEIS)

    groesse = sum(os.path.getsize(os.path.join(w, d))
                  for w, _, ds in os.walk(ZIELORDNER) for d in ds)

    print(f'\n{ZIELORDNER}/ angelegt: {anzahl} Dateien, '
          f'{groesse // 1024} KB')
    print(f'  {zuerst}/   zuerst hochladen (Inhalt, nicht den Ordner selbst)')
    print(f'  {zuletzt}/  danach – schaltet die Seite um')
    print(f'\nDie Kurzanleitung steht in {ZIELORDNER}/LIESMICH.txt')

    pruefung()


if __name__ == '__main__':
    main()
