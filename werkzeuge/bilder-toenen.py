#!/usr/bin/env python3
"""
Tönt ein Schwarzweißbild in die warmen Farben der Website ein.

Reines Schwarzweiß wirkt auf dem beigen Grund wie ein aufgesetzter weißer
Kasten. Dieses Skript bildet die Graustufen stattdessen auf die Palette ab:
Schwarz wird zum dunklen Warmbraun, Weiß zum beigen Seitengrund.
Das Bild fügt sich dadurch nahtlos ein.

Aufruf im Projektordner:

    python3 werkzeuge/bilder-toenen.py assets/img/baum-kopf.jpg

Die Datei wird ersetzt; die zugehörige .webp wird mit erzeugt. Sinnvoll nur
für Schwarzweißaufnahmen – Farbfotos verlieren dabei ihre Farben.

Voraussetzung: pip install Pillow
"""

import os
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit('Die Bibliothek Pillow fehlt. Bitte zuerst installieren:\n\n'
             '    pip install Pillow\n')

# Die Endpunkte entsprechen --c-accent-dark und --c-bg aus style.css
DUNKEL = (43, 37, 30)      # #2b251e
HELL = (244, 235, 221)     # #f4ebdd


def toenen(pfad: str) -> None:
    if not os.path.exists(pfad):
        sys.exit(f'Datei nicht gefunden: {pfad}')

    bild = Image.open(pfad).convert('L')

    # Für jeden der 256 Graustufenwerte die Zielfarbe berechnen
    tabelle = []
    for kanal in range(3):
        tabelle += [
            round(DUNKEL[kanal] + (HELL[kanal] - DUNKEL[kanal]) * wert / 255)
            for wert in range(256)
        ]

    getoent = bild.convert('RGB')
    getoent = getoent.point(tabelle)

    basis = os.path.splitext(pfad)[0]
    getoent.save(basis + '.jpg', 'JPEG', quality=86, optimize=True, progressive=True)
    getoent.save(basis + '.webp', 'WEBP', quality=86, method=6)

    print(f'  {os.path.basename(basis)}: getönt '
          f'({os.path.getsize(basis + ".jpg") // 1024} KB JPEG, '
          f'{os.path.getsize(basis + ".webp") // 1024} KB WebP)')


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--hilfe', '--help'):
        print(__doc__)
        return

    for pfad in sys.argv[1:]:
        toenen(pfad)


if __name__ == '__main__':
    main()
