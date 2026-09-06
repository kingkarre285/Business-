# Hinweise für Claude

## Anrede

Den Nutzer immer **duzen**, nie siezen.

## Projekt

Website für eine Praxis für tiefenpsychologisch fundierte Psychotherapie.
Statisches HTML/CSS mit PHP-Kontaktformular, ausgelegt auf IONOS-Webhosting.

Aufbau angelehnt an loew-psychotherapie.de: viel Weißraum, Akzentlinie unter
Überschriften, Roboto und Nunito (lokal eingebunden).

Die Farbwelt ist auf ausdrücklichen Wunsch **warm** gehalten, und die
Grundfarbe der Seite ist ein **Beige, kein Weiß** (`#f4ebdd`). Dazu dunkles
Warmbraun und ein sandfarbener Akzent. Alle Farben stehen im Block `:root` in
`assets/css/style.css`.

Schwarzweißbilder werden mit `werkzeuge/bilder-toenen.py` in dieselbe Palette
getönt, damit sie auf dem Beige nicht als weiße Kästen auffallen.

Grundregel für dieses Projekt: **keine externen Ressourcen** – keine Schriften,
Karten, Skripte oder Trackingdienste von fremden Servern. Nur so bleibt die
Seite ohne Cookie-Banner zulässig. Details in `README.md`.
