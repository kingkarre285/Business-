#!/usr/bin/env python3
"""
Hält Navigation und Fußzeile auf allen Seiten gleich.

Die Website besteht aus einzelnen HTML-Dateien, die jeweils ihre eigene
Navigation enthalten. Damit beim Hinzufügen einer Seite nicht acht Dateien
von Hand geändert werden müssen, trägt dieses Skript den Kopf- und
Fußbereich überall neu ein.

So fügen Sie eine Seite hinzu – zum Beispiel das Flugangst-Seminar:

  1. Die neue Datei anlegen, etwa flugangst-seminar.html. Am einfachsten
     kopieren Sie coaching.html und ersetzen den Inhalt zwischen
     <main id="inhalt"> und </main>.
  2. Unten in der Liste NAVIGATION den Eintrag ergänzen.
  3. Im Projektordner ausführen:

         python3 werkzeuge/navigation-aktualisieren.py

  4. Die Seite zusätzlich in sitemap.xml eintragen.

Das Skript ändert ausschließlich Navigation und Fußzeile. Die eigentlichen
Seiteninhalte bleiben unangetastet.
"""

import os, re, sys

# Immer im Projektordner arbeiten, egal von wo das Skript aufgerufen wird
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- Navigation: die Reihenfolge spiegelt die Gewichtung der Angebote -------
NAVIGATION = [
    ('index.html',           'Startseite'),
    ('psychotherapie.html',  'Psychotherapie'),
    ('coaching.html',        'Coaching'),
    ('adhs-diagnostik.html', 'ADHS-Diagnostik'),
    ('ueber-mich.html',      'Über mich'),
    ('kontakt.php',          'Kontakt'),
]

# Sobald die Seite zum Flugangst-Seminar steht, hier ergänzen:
#     ('flugangst-seminar.html', 'Flugangst-Seminar'),
# und anschließend werkzeuge/navigation-aktualisieren.py ausführen.

PRAXIS = 'Psychotherapiepraxis Jessica Holm'
UNTERTITEL = 'Tiefenpsychologisch fundierte Psychotherapie'


def kopf(aktuell: str, praefix: str = '') -> str:
    punkte = []
    for datei, name in NAVIGATION:
        aktiv = ' aria-current="page"' if datei == aktuell else ''
        punkte.append(
            f'        <li><a class="nav__link" href="{praefix}{datei}"{aktiv}>{name}</a></li>')
    liste = '\n'.join(punkte)
    return f'''<a class="skip-link" href="#inhalt">Zum Inhalt springen</a>

<header class="site-header">
  <div class="container site-header__inner">
    <a class="brand" href="{praefix}index.html">
      <span class="brand__mark" aria-hidden="true">jh.</span>
      <span class="brand__text">
        <span class="brand__name">{PRAXIS}</span>
        <span class="brand__sub">{UNTERTITEL}</span>
      </span>
    </a>

    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="hauptnavigation">
      <span class="nav-toggle__bars" aria-hidden="true"></span>
      <span>Menü</span>
    </button>

    <nav class="nav" id="hauptnavigation" aria-label="Hauptnavigation">
      <ul class="nav__list">
{liste}
      </ul>
      <a class="btn btn--primary" href="{praefix}kontakt.php">Termin anfragen</a>
    </nav>
  </div>
</header>

'''


def fuss(praefix: str = '') -> str:
    seiten = '\n'.join(
        f'          <li><a href="{praefix}{datei}">{name}</a></li>'
        for datei, name in NAVIGATION if datei != 'index.html')
    return f'''<footer class="site-footer">
  <div class="container">
    <div class="footer__grid">
      <div>
        <p class="footer__title">{PRAXIS}</p>
        <p class="text-sm" style="opacity: 0.85;">
          Dipl.-Psych. Jessica Holm<br>
          Psychologische Psychotherapeutin<br>
          {UNTERTITEL}
        </p>
      </div>

      <div>
        <p class="footer__title">Kontakt</p>
        <ul class="footer__list">
          <li>Sömmerringstraße 23<br>60322 Frankfurt am Main</li>
          <li><a href="tel:+491716581464">0171 6581464</a></li>
          <li><a href="mailto:kontakt@holm-psychotherapie.de">kontakt@holm-psychotherapie.de</a></li>
        </ul>
      </div>

      <div>
        <p class="footer__title">Seiten</p>
        <ul class="footer__list">
{seiten}
          <li><a href="{praefix}impressum.html">Impressum</a></li>
          <li><a href="{praefix}datenschutz.html">Datenschutz</a></li>
        </ul>
      </div>
    </div>

    <div class="footer__bottom">
      <span>&copy; <span data-current-year>2026</span> {PRAXIS}</span>
      <span>Diese Website verwendet keine Cookies und kein Tracking.</span>
    </div>
  </div>
</footer>

'''


def seite(datei: str, titel: str, beschreibung: str, inhalt: str,
          kanonisch: str = None, extra_kopf: str = '') -> None:
    """Schreibt eine vollständige Seite von Grund auf (wird selten gebraucht)."""
    kanonisch = kanonisch or datei
    html = f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titel}</title>
<meta name="description" content="{beschreibung}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://www.holm-psychotherapie.de/{kanonisch}">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/css/style.css">
{extra_kopf}</head>
<body>

{kopf(datei)}<main id="inhalt">
{inhalt}
</main>

{fuss()}<script src="assets/js/main.js" defer></script>
</body>
</html>
'''
    open(datei, 'w', encoding='utf-8').write(html)
    print('  geschrieben:', datei)


def navigation_erneuern(datei: str) -> None:
    """Tauscht Kopf- und Fußbereich einer bestehenden Seite aus."""
    s = open(datei, encoding='utf-8').read()
    praefix = '/' if datei == '404.html' else ''
    neuer_kopf = kopf(datei, praefix)
    neuer_fuss = fuss(praefix)

    s = re.sub(r'<a class="skip-link".*?</header>\n\n', neuer_kopf, s, flags=re.S)

    # Die Fehlerseite hat eine verkürzte Fußzeile – die bleibt unangetastet
    if '<div class="footer__grid">' in s:
        s = re.sub(r'<footer class="site-footer">.*?</footer>\n\n', neuer_fuss, s, flags=re.S)

    open(datei, 'w', encoding='utf-8').write(s)
    print('  Navigation erneuert:', datei)


# ---------------------------------------------------------------------------

SEITEN = ['index.html', 'psychotherapie.html', 'coaching.html',
          'adhs-diagnostik.html', 'ueber-mich.html', 'kontakt.php',
          'impressum.html', 'datenschutz.html', '404.html']


def main() -> None:
    fehlend = [d for d in SEITEN if not os.path.exists(d)]
    if fehlend:
        print('Diese Dateien fehlen und werden übersprungen:', ', '.join(fehlend))

    for datei in SEITEN:
        if os.path.exists(datei):
            navigation_erneuern(datei)

    nicht_gelistet = [d for d, _ in NAVIGATION if not os.path.exists(d)]
    if nicht_gelistet:
        print('\nAchtung: In NAVIGATION stehen Seiten, die es noch nicht gibt:',
              ', '.join(nicht_gelistet))
        print('Die Links im Menü würden ins Leere führen.')
        sys.exit(1)

    print('\nFertig. Bitte nicht vergessen: neue Seiten auch in sitemap.xml eintragen.')


if __name__ == '__main__':
    main()
