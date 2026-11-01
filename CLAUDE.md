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

Eingebunden sind echte Fotos der Praxis. Neue Bilder mit
`werkzeuge/bilder-aufbereiten.py` auf die Zielmaße bringen; die Bildplätze
stehen oben im Skript. Für etwaige Schwarzweißmotive gibt es
`werkzeuge/bilder-toenen.py`, damit sie auf dem Beige nicht als weiße Kästen
auffallen.

Mit `werkzeuge/vorschau-bauen.py` entsteht eine einzelne `vorschau.html` zum
Durchklicken – praktisch, um dem Nutzer den Stand zu zeigen.

Grundregel für dieses Projekt: **keine externen Ressourcen** – keine Schriften,
Karten, Skripte oder Trackingdienste von fremden Servern. Nur so bleibt die
Seite ohne Cookie-Banner zulässig. Details in `README.md`.
