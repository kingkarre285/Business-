#!/usr/bin/env python3
"""
Bündelt die Website zu einer einzelnen HTML-Datei zum Durchklicken.

Nützlich, um den Entwurf jemandem zu zeigen oder selbst durchzusehen, ohne
etwas hochzuladen: Schriften und Bilder werden in die Datei eingebettet, die
Seiten liegen hintereinander darin und eine Leiste oben schaltet zwischen
ihnen um.

Aufruf im Projektordner:

    python3 werkzeuge/vorschau-bauen.py

Ergebnis ist `vorschau.html` im Projektordner – eine einzelne Datei, die
sich per Doppelklick öffnen und per E-Mail verschicken lässt.

Die Datei ist ausdrücklich eine Vorschau und nicht das, was hochgeladen
wird: Sie trägt oben einen Entwurfshinweis, und das Kontaktformular
versendet darin nichts, weil kein PHP läuft.

Voraussetzung: pip install Pillow wird nicht gebraucht, aber PHP, damit die
Kontaktseite gerendert werden kann. Fehlt PHP, wird sie übersprungen.
"""

import base64
import os
import re
import shutil
import subprocess
import sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SEITEN = [
    ('index.html',           'Startseite'),
    ('psychotherapie.html',  'Psychotherapie'),
    ('coaching.html',        'Coaching'),
    ('adhs-diagnostik.html', 'ADHS-Diagnostik'),
    ('ueber-mich.html',      'Über mich'),
    ('kontakt.php',          'Kontakt'),
    ('impressum.html',       'Impressum'),
    ('datenschutz.html',     'Datenschutz'),
]

ZIELDATEI = 'vorschau.html'


def kennung(datei):
    return 's-' + datei.split('.')[0].replace('-', '')


def als_datenurl(pfad, typ):
    with open(pfad, 'rb') as f:
        return f'data:{typ};base64,' + base64.b64encode(f.read()).decode()


# --- Stylesheet mit eingebetteten Schriften ---------------------------------

css = open('assets/css/style.css', encoding='utf-8').read()
fonts = open('assets/css/fonts.css', encoding='utf-8').read()
for datei in sorted(os.listdir('assets/fonts')):
    fonts = fonts.replace(f'../fonts/{datei}',
                          als_datenurl(f'assets/fonts/{datei}', 'font/woff2'))
css = css.replace('@import url("fonts.css");', fonts)

# --- Bilder: je Motiv genügt die kleinere WebP-Fassung ----------------------

bilder = {}
for datei in sorted(os.listdir('assets/img')):
    if datei.endswith('.webp'):
        name = datei[:-5]
        bilder[name] = als_datenurl(f'assets/img/{datei}', 'image/webp')


# --- Seiteninhalte einsammeln -----------------------------------------------

def koerper(datei):
    """Liefert den Inhalt zwischen <body> und </body>, ohne Skriptverweise."""
    if datei.endswith('.php'):
        if not shutil.which('php'):
            return None
        roh = subprocess.run(['php', datei], capture_output=True, text=True).stdout
    else:
        roh = open(datei, encoding='utf-8').read()

    if '<body>' not in roh:
        return None
    inhalt = roh[roh.index('<body>') + 6:roh.index('</body>')]
    return re.sub(r'<script[^>]*></script>', '', inhalt)


def umschreiben(inhalt, datei, vorhandene):
    """Macht Kennungen eindeutig und lenkt Verweise auf die Vorschau um."""
    suffix = '-' + kennung(datei)

    for attribut in ('id', 'aria-controls', 'aria-labelledby', 'for'):
        inhalt = re.sub(rf'\b{attribut}="([\w-]+)"',
                        lambda m: f'{attribut}="{m.group(1)}{suffix}"', inhalt)

    inhalt = re.sub(r'href="#([\w-]+)"',
                    lambda m: f'href="#{m.group(1)}{suffix}"', inhalt)

    def seitenlink(m):
        ziel, anker = m.group(1), m.group(2) or ''
        if ziel not in vorhandene:
            return m.group(0)
        zusatz = f' data-anker="{anker[1:]}-{kennung(ziel)}"' if anker else ''
        return f'href="#" data-ziel="{kennung(ziel)}"{zusatz}'

    inhalt = re.sub(r'href="([\w.-]+\.(?:html|php))(#[\w-]+)?"', seitenlink, inhalt)

    # Nur eine Bildfassung einbetten, daher entfällt das <source>-Element
    inhalt = re.sub(r'\s*<source[^>]*>', '', inhalt)
    for name, datenurl in bilder.items():
        inhalt = inhalt.replace(f'assets/img/{name}.jpg', datenurl)
        inhalt = inhalt.replace(f'assets/img/{name}.svg', datenurl)

    return inhalt


inhalte = {}
for datei, _ in SEITEN:
    if not os.path.exists(datei):
        print(f'  übersprungen (fehlt): {datei}')
        continue
    roh = koerper(datei)
    if roh is None:
        print(f'  übersprungen (konnte nicht gelesen werden): {datei}')
        continue
    inhalte[datei] = roh

vorhandene = set(inhalte)
erste = next(iter(inhalte))

seiten_html = []
knoepfe = []
for datei, name in SEITEN:
    if datei not in inhalte:
        continue
    versteckt = '' if datei == erste else ' hidden'
    seiten_html.append(
        f'<div class="vorschau-seite" id="{kennung(datei)}" data-name="{name}"{versteckt}>\n'
        f'{umschreiben(inhalte[datei], datei, vorhandene)}\n</div>')
    aktiv = ' class="aktiv"' if datei == erste else ''
    knoepfe.append(
        f'      <button type="button" data-ziel="{kennung(datei)}"{aktiv}>{name}</button>')


# --- Nur für die Vorschau: Leiste und Umschaltung ---------------------------

VORSCHAU_CSS = '''
/* ===== Nur für die Vorschau – gehört nicht zur eigentlichen Website ===== */
.vorschau-leiste {
  position: sticky;
  top: 0;
  z-index: 500;
  background: #2b251e;
  color: #f2ece1;
  font-family: Roboto, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
}

.vorschau-leiste__innen {
  max-width: 78rem;
  margin-inline: auto;
  padding: .6rem 1.5rem .7rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: .4rem .9rem;
}

.vorschau-leiste__titel {
  font-size: .6875rem;
  letter-spacing: .16em;
  text-transform: uppercase;
  color: #a89881;
  margin-right: .4rem;
}

.vorschau-leiste nav { display: flex; flex-wrap: wrap; gap: .25rem; }

.vorschau-leiste button {
  font: inherit;
  font-size: .8125rem;
  color: #ddd2c1;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 50px;
  padding: .3rem .8rem;
  cursor: pointer;
}

.vorschau-leiste button:hover { color: #fff; border-color: rgba(255,255,255,.25); }

.vorschau-leiste button.aktiv {
  color: #2b251e;
  background: #c9a878;
  border-color: #c9a878;
}

.vorschau-leiste button:focus-visible { outline: 2px solid #c9a878; outline-offset: 2px; }

.vorschau-hinweis {
  background: #f6ead2;
  color: #6b5320;
  border-bottom: 1px solid #e5d3ab;
  font-family: Nunito, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
  font-size: .875rem;
  line-height: 1.5;
}

.vorschau-hinweis > div {
  max-width: 78rem;
  margin-inline: auto;
  padding: .7rem 1.5rem;
}

@media (max-width: 40rem) {
  .vorschau-leiste__innen,
  .vorschau-hinweis > div { padding-inline: 1rem; }
  .vorschau-leiste__titel { width: 100%; margin-bottom: .2rem; }
}
'''

VORSCHAU_JS = '''
(function () {
  "use strict";

  var seiten = [].slice.call(document.querySelectorAll(".vorschau-seite"));
  var knoepfe = [].slice.call(document.querySelectorAll(".vorschau-leiste button"));

  function zeige(kennung, anker) {
    seiten.forEach(function (s) { s.hidden = s.id !== kennung; });
    knoepfe.forEach(function (b) { b.classList.toggle("aktiv", b.dataset.ziel === kennung); });

    if (anker) {
      var ziel = document.getElementById(anker);
      if (ziel) { ziel.scrollIntoView({ block: "start" }); return; }
    }
    window.scrollTo(0, 0);
  }

  knoepfe.forEach(function (b) {
    b.addEventListener("click", function () { zeige(b.dataset.ziel); });
  });

  document.addEventListener("click", function (e) {
    var link = e.target.closest("a[data-ziel]");
    if (link) {
      e.preventDefault();
      zeige(link.dataset.ziel, link.dataset.anker);
      return;
    }

    var absenden = e.target.closest(".vorschau-seite button[type=submit]");
    if (absenden) {
      e.preventDefault();
      if (!absenden.parentNode.querySelector(".vorschau-formularhinweis")) {
        var meldung = document.createElement("p");
        meldung.className = "vorschau-formularhinweis";
        meldung.setAttribute("role", "status");
        meldung.style.cssText = "margin-top:1rem;padding:.8rem 1rem;background:#f6ead2;" +
          "border-left:3px solid #c9a878;border-radius:0 3px 3px 0;font-size:.9375rem;color:#6b5320;";
        meldung.textContent = "In dieser Vorschau wird nichts versendet. " +
          "Auf dem Server verschickt das Formular die Anfrage per E-Mail.";
        absenden.parentNode.insertBefore(meldung, absenden.nextSibling);
      }
    }
  });

  document.querySelectorAll(".vorschau-seite .nav-toggle").forEach(function (schalter) {
    schalter.addEventListener("click", function () {
      var nav = document.getElementById(schalter.getAttribute("aria-controls"));
      if (!nav) return;
      var offen = nav.classList.toggle("is-open");
      schalter.setAttribute("aria-expanded", offen ? "true" : "false");
    });
  });

  document.querySelectorAll("[data-current-year]").forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });
})();
'''

html = f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Praxis Holm – Seitenvorschau</title>
<style>
{css}
{VORSCHAU_CSS}
</style>
</head>
<body>

<div class="vorschau-leiste">
  <div class="vorschau-leiste__innen">
    <span class="vorschau-leiste__titel">Entwurf</span>
    <nav aria-label="Seiten der Vorschau">
{chr(10).join(knoepfe)}
    </nav>
  </div>
</div>

<div class="vorschau-hinweis">
  <div>
    <strong>Vorschau eines Entwurfs.</strong> Honorare, Sprechzeiten und
    Wartezeiten sind Beispielwerte und noch nicht bestätigt. Das
    Kontaktformular versendet hier nichts.
  </div>
</div>

{chr(10).join(seiten_html)}

<script>
{VORSCHAU_JS}
</script>
</body>
</html>
'''

open(ZIELDATEI, 'w', encoding='utf-8').write(html)
print(f'\n{ZIELDATEI}: {os.path.getsize(ZIELDATEI) // 1024} KB, {len(seiten_html)} Seiten')
print('Zum Ansehen die Datei im Browser öffnen.')
