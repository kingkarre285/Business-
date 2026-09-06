#!/usr/bin/env python3
"""
Listet alle vorläufigen Angaben auf, die vor dem Livegang geprüft werden müssen.

Aufruf im Projektordner:

    python3 werkzeuge/platzhalter-pruefen.py

Gefunden werden zwei Arten von Stellen:

  1. Angaben, die mit class="platzhalter" markiert sind – also eingesetzte
     Beispielwerte wie Honorare, Sprechzeiten oder Wartezeiten.
  2. Text in eckigen Klammern, etwa [Name des Versicherers eintragen].

Nach dem Ersetzen eines Wertes bitte auch das umschließende
<span class="platzhalter">…</span> entfernen, damit die Liste kürzer wird.

Wer die Stellen lieber im Browser sehen möchte: In assets/css/style.css
gibt es eine auskommentierte Regel, die alle Platzhalter gelb hervorhebt.
"""

import os
import re
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATEIEN = sorted(
    [d for d in os.listdir('.') if d.endswith('.html') or d.endswith('.php')]
)

MARKIERT = re.compile(r'<span class="platzhalter">(.*?)</span>', re.S)
KLAMMER = re.compile(r'\[([^\]\n]{3,80})\]')

# Klammern mit diesen Zeichen stammen aus Programmcode, nicht aus dem Text
CODEZEICHEN = ('\'', '"', '$', '_', '\\')

# Diese Klammerausdrücke gehören zum Inhalt
AUSNAHMEN = ('PTV 11',)


def sauber(text: str) -> str:
    text = re.sub(r'<[^>]+>', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def main() -> None:
    gesamt = 0

    for datei in DATEIEN:
        inhalt = open(datei, encoding='utf-8').read()
        # Kommentare ausblenden – dort stehen Hinweise, keine Seiteninhalte.
        # Der PHP-Block ebenso: dort sind eckige Klammern Array-Zugriffe.
        # Ersetzt wird durch gleich viele Zeilenumbrüche, damit die
        # Zeilennummern der übrigen Fundstellen weiterhin stimmen.
        def leeren(m):
            return '\n' * m.group(0).count('\n')

        text = re.sub(r'<!--.*?-->', leeren, inhalt, flags=re.S)
        text = re.sub(r'<\?php.*?\?>', leeren, text, flags=re.S)

        treffer = []
        markierte_bereiche = []

        for m in MARKIERT.finditer(text):
            zeile = text[:m.start()].count('\n') + 1
            markierte_bereiche.append((m.start(), m.end()))
            treffer.append((zeile, 'Beispielwert', sauber(m.group(1))))

        for m in KLAMMER.finditer(text):
            if any(z in m.group(1) for z in CODEZEICHEN):
                continue
            if any(a in m.group(1) for a in AUSNAHMEN):
                continue
            # Klammern innerhalb einer bereits gezählten Markierung überspringen
            if any(a <= m.start() < b for a, b in markierte_bereiche):
                continue
            zeile = text[:m.start()].count('\n') + 1
            treffer.append((zeile, 'offen', m.group(1)))

        if treffer:
            print(f'\n{datei}')
            for zeile, art, text in sorted(treffer):
                kennzeichen = '·' if art == 'Beispielwert' else '!'
                print(f'  {kennzeichen} Zeile {zeile:>4}  {text[:70]}')
            gesamt += len(treffer)

    print()
    if gesamt:
        print(f'{gesamt} Stellen zu prüfen.')
        print('  ·  eingesetzter Beispielwert – bitte durch den richtigen ersetzen')
        print('  !  noch gar nicht ausgefüllt')
        sys.exit(1)

    print('Keine offenen Platzhalter gefunden.')


if __name__ == '__main__':
    main()
