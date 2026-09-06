#!/usr/bin/env python3
"""
Bereitet eigene Fotos für die Website auf.

Das Skript schneidet ein Foto mittig auf das benötigte Seitenverhältnis zu,
verkleinert es und legt es zweifach ab: als JPEG und als kleineres WebP.

Aufruf:

    python3 werkzeuge/bilder-aufbereiten.py portraet ~/Bilder/mein-foto.jpg

Der erste Wert ist der Bildplatz (siehe Tabelle unten), der zweite der Pfad
zum eigenen Foto. Die fertigen Dateien landen in assets/img/.

Alle Bildplätze auf einmal ersetzen:

    python3 werkzeuge/bilder-aufbereiten.py --alle ordner-mit-fotos/

Dazu müssen die Fotos in diesem Ordner so heißen wie die Bildplätze,
also portraet.jpg, raum.jpg und so weiter.

Voraussetzung ist die Bibliothek Pillow:

    pip install Pillow
"""

import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit('Die Bibliothek Pillow fehlt. Bitte zuerst installieren:\n\n'
             '    pip install Pillow\n')

# Bildplatz: (Breite, Höhe, JPEG-Qualität)
BILDPLAETZE = {
    'baum-kopf': (900, 900, 86),    # Startseite, neben der Hauptüberschrift
    'hero-meer': (1800, 1000, 82),  # Zitatband auf der Startseite
    'raum':      (1400, 950, 82),   # "Wohin Sie kommen", Ablauf-Seite
    'portraet':  (800, 1000, 88),   # Über-mich-Seite
}

ZIELORDNER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          'assets', 'img')


def aufbereiten(bildplatz: str, quelldatei: str) -> None:
    """Schneidet zu, verkleinert und speichert als JPEG und WebP."""
    if bildplatz not in BILDPLAETZE:
        sys.exit(f'Unbekannter Bildplatz "{bildplatz}".\n'
                 f'Möglich sind: {", ".join(sorted(BILDPLAETZE))}')

    if not os.path.exists(quelldatei):
        sys.exit(f'Datei nicht gefunden: {quelldatei}')

    breite, hoehe, qualitaet = BILDPLAETZE[bildplatz]
    bild = Image.open(quelldatei)

    # Drehung aus den EXIF-Daten anwenden, sonst liegen Handyfotos quer
    try:
        from PIL import ImageOps
        bild = ImageOps.exif_transpose(bild)
    except Exception:
        pass

    bild = bild.convert('RGB')

    if bild.width < breite or bild.height < hoehe:
        # Nicht hochrechnen – stattdessen das größte Rechteck im Zielverhältnis
        # nehmen, das noch in das Originalfoto passt.
        verkleinerung = min(bild.width / breite, bild.height / hoehe)
        breite = int(breite * verkleinerung)
        hoehe = int(hoehe * verkleinerung)
        print(f'  Hinweis: Das Foto ist mit {bild.width} × {bild.height} px kleiner '
              f'als empfohlen. Es wird auf {breite} × {hoehe} px zugeschnitten '
              f'statt hochgerechnet – hochrechnen würde es nur unscharf machen.')

    # Mittig auf das Zielverhältnis beschneiden
    ziel = breite / hoehe
    ist = bild.width / bild.height
    if ist > ziel:
        neue_breite = int(bild.height * ziel)
        links = (bild.width - neue_breite) // 2
        bild = bild.crop((links, 0, links + neue_breite, bild.height))
    else:
        neue_hoehe = int(bild.width / ziel)
        oben = (bild.height - neue_hoehe) // 2
        bild = bild.crop((0, oben, bild.width, oben + neue_hoehe))

    bild = bild.resize((breite, hoehe), Image.LANCZOS)

    os.makedirs(ZIELORDNER, exist_ok=True)
    jpg = os.path.join(ZIELORDNER, bildplatz + '.jpg')
    webp = os.path.join(ZIELORDNER, bildplatz + '.webp')
    bild.save(jpg, 'JPEG', quality=qualitaet, optimize=True, progressive=True)
    bild.save(webp, 'WEBP', quality=qualitaet, method=6)

    print(f'  {bildplatz}: {breite} × {hoehe} px  '
          f'(JPEG {os.path.getsize(jpg) // 1024} KB, '
          f'WebP {os.path.getsize(webp) // 1024} KB)')


def main() -> None:
    argumente = sys.argv[1:]

    if not argumente or argumente[0] in ('-h', '--hilfe', '--help'):
        print(__doc__)
        print('Bildplätze:\n')
        for name, (b, h, _) in BILDPLAETZE.items():
            print(f'  {name:12} {b} × {h} px')
        return

    if argumente[0] == '--alle':
        if len(argumente) < 2:
            sys.exit('Bitte den Ordner mit den Fotos angeben.')
        ordner = argumente[1]
        gefunden = 0
        for name in BILDPLAETZE:
            for endung in ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'):
                pfad = os.path.join(ordner, name + endung)
                if os.path.exists(pfad):
                    aufbereiten(name, pfad)
                    gefunden += 1
                    break
        if not gefunden:
            print(f'Im Ordner {ordner} wurde kein passend benanntes Foto gefunden.')
            print('Erwartet werden: ' + ', '.join(n + '.jpg' for n in BILDPLAETZE))
        return

    if len(argumente) < 2:
        sys.exit('Aufruf: python3 werkzeuge/bilder-aufbereiten.py <bildplatz> <foto>')

    aufbereiten(argumente[0], argumente[1])
    print('\nNicht vergessen: den alt-Text im HTML anpassen, '
          'damit die Bildbeschreibung wieder zum Motiv passt.')


if __name__ == '__main__':
    main()
