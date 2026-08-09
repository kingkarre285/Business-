<?php
/* ============================================================================
 * Kontaktformular – Praxis am Lindenhof
 * ----------------------------------------------------------------------------
 * Läuft auf jedem IONOS-Webhosting-Paket mit PHP 7.4 oder neuer.
 * Kein Framework, keine Datenbank, keine Cookies, keine Sessions.
 *
 * >>> HIER ANPASSEN: die vier Werte im Block "Konfiguration". <<<
 * ==========================================================================*/

/* --- Konfiguration -------------------------------------------------------- */

// Wohin sollen die Anfragen gehen?
$empfaenger = 'praxis@ihre-domain.de';

// Absenderadresse. MUSS eine Adresse Ihrer eigenen Domain sein, sonst
// stuft der Mailserver die Nachricht als Spam ein oder lehnt sie ab.
$absender = 'website@ihre-domain.de';

// Betreffzeile der Benachrichtigungs-E-Mail
$betreff = 'Neue Terminanfrage über die Website';

// Mindestzeit in Sekunden zwischen Seitenaufruf und Absenden (Bot-Bremse)
$mindestzeit = 3;

/* --- Verarbeitung --------------------------------------------------------- */

$fehler   = [];
$werte    = ['name' => '', 'email' => '', 'telefon' => '', 'erreichbar' => '', 'anliegen' => ''];
$gesendet = isset($_GET['status']) && $_GET['status'] === 'ok';

/**
 * Entfernt Zeilenumbrüche – verhindert das Einschleusen zusätzlicher
 * E-Mail-Header über Formularfelder (Header-Injection).
 */
function saubere_kopfzeile(string $wert): string
{
    return trim(str_replace(["\r", "\n", "%0a", "%0d"], '', $wert));
}

/** Kurzform für die sichere Ausgabe von Text in HTML. */
function h(?string $wert): string
{
    return htmlspecialchars((string) $wert, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    foreach ($werte as $feld => $_) {
        $werte[$feld] = isset($_POST[$feld]) ? trim((string) $_POST[$feld]) : '';
    }

    $honeypot   = isset($_POST['website']) ? trim((string) $_POST['website']) : '';
    $zeitstempel = isset($_POST['ts']) ? (int) $_POST['ts'] : 0;
    $einwilligung = isset($_POST['einwilligung']);

    // 1. Bot-Prüfungen. Bots füllen unsichtbare Felder aus und sind zu schnell.
    $istBot = ($honeypot !== '') || ($zeitstempel > 0 && (time() - $zeitstempel) < $mindestzeit);

    // 2. Inhaltliche Prüfung
    if ($werte['name'] === '' || mb_strlen($werte['name']) < 2) {
        $fehler['name'] = 'Bitte geben Sie Ihren Namen an.';
    }

    if ($werte['email'] === '' && $werte['telefon'] === '') {
        $fehler['email'] = 'Bitte hinterlassen Sie eine E-Mail-Adresse oder eine Telefonnummer, damit ich Sie erreichen kann.';
    } elseif ($werte['email'] !== '' && !filter_var($werte['email'], FILTER_VALIDATE_EMAIL)) {
        $fehler['email'] = 'Diese E-Mail-Adresse scheint nicht zu stimmen.';
    }

    if ($werte['anliegen'] === '' || mb_strlen($werte['anliegen']) < 10) {
        $fehler['anliegen'] = 'Bitte schreiben Sie ein paar Worte zu Ihrem Anliegen.';
    } elseif (mb_strlen($werte['anliegen']) > 3000) {
        $fehler['anliegen'] = 'Bitte fassen Sie sich etwas kürzer (höchstens 3000 Zeichen).';
    }

    if (!$einwilligung) {
        $fehler['einwilligung'] = 'Ohne Ihre Einwilligung darf ich die Anfrage leider nicht verarbeiten.';
    }

    // 3. Versand
    if (!$fehler) {

        if ($istBot) {
            // Bots bekommen dieselbe Rückmeldung wie Menschen – nur ohne Versand.
            header('Location: kontakt.php?status=ok', true, 303);
            exit;
        }

        $absenderName = saubere_kopfzeile($werte['name']);
        $replyTo      = saubere_kopfzeile($werte['email']);

        $text = "Neue Anfrage über das Kontaktformular\n"
              . str_repeat('=', 40) . "\n\n"
              . "Name:        " . $werte['name'] . "\n"
              . "E-Mail:      " . ($werte['email'] !== '' ? $werte['email'] : '– nicht angegeben –') . "\n"
              . "Telefon:     " . ($werte['telefon'] !== '' ? $werte['telefon'] : '– nicht angegeben –') . "\n"
              . "Erreichbar:  " . ($werte['erreichbar'] !== '' ? $werte['erreichbar'] : '– keine Angabe –') . "\n\n"
              . "Anliegen:\n"
              . str_repeat('-', 40) . "\n"
              . $werte['anliegen'] . "\n"
              . str_repeat('-', 40) . "\n\n"
              . "Eingegangen am " . date('d.m.Y \u\m H:i') . " Uhr\n";

        $headers = [
            'From: ' . ($absenderName !== '' ? '=?UTF-8?B?' . base64_encode($absenderName) . '?= ' : '') . '<' . $absender . '>',
            'Content-Type: text/plain; charset=UTF-8',
            'Content-Transfer-Encoding: 8bit',
            'MIME-Version: 1.0',
            'X-Mailer: PHP/' . phpversion(),
        ];

        if ($replyTo !== '' && filter_var($replyTo, FILTER_VALIDATE_EMAIL)) {
            $headers[] = 'Reply-To: ' . $replyTo;
        }

        $betreffKodiert = '=?UTF-8?B?' . base64_encode($betreff) . '?=';

        $erfolg = @mail(
            $empfaenger,
            $betreffKodiert,
            $text,
            implode("\r\n", $headers),
            '-f' . $absender
        );

        if ($erfolg) {
            // Weiterleitung nach dem Absenden, damit ein Neuladen der Seite
            // die Anfrage nicht ein zweites Mal verschickt.
            header('Location: kontakt.php?status=ok', true, 303);
            exit;
        }

        $fehler['versand'] = 'Die Nachricht konnte technisch nicht versendet werden. '
                           . 'Bitte rufen Sie stattdessen an oder schreiben Sie direkt an praxis@ihre-domain.de.';
    }
}
?>
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kontakt &amp; Terminanfrage | Praxis am Lindenhof</title>
<meta name="description" content="Terminanfrage und Kontakt zur Praxis am Lindenhof in Musterstadt. Telefonzeiten, Anfahrt und Kontaktformular.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://www.ihre-domain.de/kontakt.php">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>

<a class="skip-link" href="#inhalt">Zum Inhalt springen</a>

<header class="site-header">
  <div class="container site-header__inner">
    <a class="brand" href="index.html">
      <span class="brand__mark" aria-hidden="true">l.</span>
      <span class="brand__text">
        <span class="brand__name">Praxis am Lindenhof</span>
        <span class="brand__sub">Tiefenpsychologisch fundierte Psychotherapie</span>
      </span>
    </a>

    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="hauptnavigation">
      <span class="nav-toggle__bars" aria-hidden="true"></span>
      <span>Menü</span>
    </button>

    <nav class="nav" id="hauptnavigation" aria-label="Hauptnavigation">
      <ul class="nav__list">
        <li><a class="nav__link" href="index.html">Startseite</a></li>
        <li><a class="nav__link" href="ueber-mich.html">Über mich</a></li>
        <li><a class="nav__link" href="leistungen.html">Leistungen</a></li>
        <li><a class="nav__link" href="ablauf-kosten.html">Ablauf &amp; Kosten</a></li>
        <li><a class="nav__link" href="kontakt.php" aria-current="page">Kontakt</a></li>
      </ul>
      <a class="btn btn--primary" href="#formular">Termin anfragen</a>
    </nav>
  </div>
</header>

<main id="inhalt">

  <section class="section">
    <div class="container">
      <div class="section__head">
        <span class="eyebrow">Kontakt</span>
        <h1>Terminanfrage</h1>
        <p class="lead">
          Der erste Schritt ist oft der schwerste. Ein Anruf oder ein paar Zeilen
          genügen – alles Weitere besprechen wir in Ruhe.
        </p>
      </div>

      <div class="grid grid--2" style="gap: 3rem; align-items: start;">

        <!-- ============ Formular ============ -->
        <div id="formular">

          <?php if ($gesendet): ?>
            <div class="form-message form-message--ok" role="status">
              <h2 style="font-size: 1.1875rem; margin-bottom: 0.5rem;">Ihre Anfrage ist angekommen.</h2>
              <p>
                Vielen Dank für Ihr Vertrauen. Ich melde mich in der Regel
                innerhalb von <strong>drei Werktagen</strong> bei Ihnen.
              </p>
              <p class="mb-0">
                Sollten Sie in der Zwischenzeit dringend Unterstützung brauchen,
                wenden Sie sich bitte an die <a href="#notfall">Krisenstellen weiter unten</a>.
              </p>
            </div>
          <?php else: ?>

            <?php if ($fehler): ?>
              <div class="form-message form-message--error" role="alert">
                <p><strong>Bitte prüfen Sie noch einmal:</strong></p>
                <ul class="mb-0">
                  <?php foreach ($fehler as $meldung): ?>
                    <li><?= h($meldung) ?></li>
                  <?php endforeach; ?>
                </ul>
              </div>
            <?php endif; ?>

            <form class="form" method="post" action="kontakt.php#formular" novalidate>

              <!-- Bot-Falle: für Menschen unsichtbar, bitte nicht entfernen -->
              <div class="hp-field" aria-hidden="true">
                <label for="website">Website (bitte frei lassen)</label>
                <input type="text" id="website" name="website" tabindex="-1" autocomplete="off">
              </div>
              <input type="hidden" name="ts" value="<?= time() ?>">

              <div class="form__row">
                <label for="name">Name <span aria-hidden="true">*</span><span class="visually-hidden">(Pflichtfeld)</span></label>
                <input type="text" id="name" name="name" autocomplete="name" required
                       value="<?= h($werte['name']) ?>"
                       <?= isset($fehler['name']) ? 'aria-invalid="true"' : '' ?>>
              </div>

              <div class="form__row form__row--split">
                <div>
                  <label for="email">E-Mail</label>
                  <input type="email" id="email" name="email" autocomplete="email"
                         value="<?= h($werte['email']) ?>"
                         <?= isset($fehler['email']) ? 'aria-invalid="true"' : '' ?>>
                </div>
                <div>
                  <label for="telefon">Telefon</label>
                  <input type="tel" id="telefon" name="telefon" autocomplete="tel"
                         value="<?= h($werte['telefon']) ?>">
                </div>
              </div>
              <p class="text-sm text-muted" style="margin-top: -0.75rem;">
                Eines von beiden genügt. Ein Rückruf ist oft der schnellste Weg.
              </p>

              <div class="form__row">
                <label for="erreichbar">
                  Wann sind Sie gut erreichbar?
                  <span class="label-hint">Zum Beispiel: werktags nachmittags, kein Rückruf ins Büro</span>
                </label>
                <input type="text" id="erreichbar" name="erreichbar"
                       value="<?= h($werte['erreichbar']) ?>">
              </div>

              <div class="form__row">
                <label for="anliegen">
                  Ihr Anliegen <span aria-hidden="true">*</span><span class="visually-hidden">(Pflichtfeld)</span>
                  <span class="label-hint">
                    Ein bis zwei Sätze reichen völlig. Bitte schreiben Sie hier
                    <strong>keine</strong> ausführlichen Angaben zu Diagnosen oder
                    Ihrer Krankengeschichte – E-Mail ist dafür kein sicherer Weg.
                    Dafür ist das persönliche Gespräch da.
                  </span>
                </label>
                <textarea id="anliegen" name="anliegen" required
                          <?= isset($fehler['anliegen']) ? 'aria-invalid="true"' : '' ?>><?= h($werte['anliegen']) ?></textarea>
              </div>

              <div class="form__row">
                <div class="form__consent">
                  <input type="checkbox" id="einwilligung" name="einwilligung" value="ja" required
                         <?= isset($_POST['einwilligung']) ? 'checked' : '' ?>>
                  <label for="einwilligung">
                    Ich bin damit einverstanden, dass die von mir angegebenen Daten
                    zur Bearbeitung meiner Anfrage gespeichert und verarbeitet werden.
                    Die <a href="datenschutz.html">Datenschutzerklärung</a> habe ich
                    zur Kenntnis genommen. Diese Einwilligung kann ich jederzeit
                    formlos widerrufen. <span aria-hidden="true">*</span>
                  </label>
                </div>
              </div>

              <button type="submit" class="btn btn--primary">Anfrage absenden</button>

              <p class="text-sm text-muted" style="margin-top: 1rem;">
                <span aria-hidden="true">*</span> Pflichtfeld. Die Übertragung erfolgt
                verschlüsselt über HTTPS.
              </p>
            </form>

          <?php endif; ?>
        </div>

        <!-- ============ Kontaktdaten ============ -->
        <aside>
          <div class="card">
            <h2 style="font-size: 1.1875rem;">Praxis</h2>
            <dl class="data-list">
              <dt>Adresse</dt>
              <dd>
                Musterstraße 12<br>
                12345 Musterstadt<br>
                <span class="text-sm text-muted">2. Obergeschoss, Aufzug vorhanden</span>
              </dd>

              <dt>Telefon</dt>
              <dd><a href="tel:+49301234567">030 1234567</a></dd>

              <dt>Telefonzeit</dt>
              <dd>Dienstag &amp; Donnerstag<br>12:00–13:00 Uhr</dd>

              <dt>E-Mail</dt>
              <dd><a href="mailto:praxis@ihre-domain.de">praxis@ihre-domain.de</a></dd>
            </dl>

            <hr style="margin: 1.5rem 0;">

            <h3 style="font-size: 1.0625rem;">Sprechzeiten</h3>
            <dl class="data-list text-sm">
              <dt>Mo – Do</dt>
              <dd>09:00 – 18:00 Uhr</dd>
              <dt>Freitag</dt>
              <dd>09:00 – 13:00 Uhr</dd>
            </dl>
            <p class="text-sm text-muted" style="margin-top: 1rem; margin-bottom: 0;">
              Termine ausschließlich nach Vereinbarung.
            </p>
          </div>

          <div class="card" style="margin-top: 1.5rem;">
            <h3 style="font-size: 1.0625rem;">Anfahrt</h3>
            <p class="text-sm">
              <strong>Öffentlich:</strong> U-Bahn-Linie [x], Station [Name],
              zwei Minuten Fußweg. Buslinien [x] und [y] halten direkt vor dem Haus.
            </p>
            <p class="text-sm">
              <strong>Mit dem Auto:</strong> Parkplätze in der [Straße], Parkhaus
              [Name] in 200 Metern Entfernung.
            </p>
            <p class="text-sm mb-0">
              <strong>Barrierefreiheit:</strong> Das Haus verfügt über einen Aufzug.
              Bitte geben Sie mir vorab Bescheid, wenn Sie besondere Unterstützung
              benötigen.
            </p>
            <!-- HINWEIS ZUM DATENSCHUTZ: Eine eingebettete Google Maps oder OpenStreetMap
                 Karte lädt Daten von fremden Servern und überträgt die IP-Adresse Ihrer
                 Besucher dorthin. Das wäre ohne vorherige Einwilligung (Cookie-Banner)
                 nicht zulässig. Empfehlung: statt Einbettung ein statisches Bild des
                 Kartenausschnitts mit einem Textlink zur Routenplanung verwenden. -->
          </div>
        </aside>

      </div>
    </div>
  </section>

  <!-- ============ Notfall ============ -->
  <section class="section section--tight" id="notfall">
    <div class="container container--narrow">
      <div class="notice notice--urgent">
        <h2 style="font-size: 1.1875rem; margin-bottom: 0.5rem;">Wichtig: keine Notfallversorgung</h2>
        <p>
          Anfragen über dieses Formular werden nicht täglich und nicht rund um die
          Uhr gelesen. Wenn Sie akut Hilfe brauchen oder daran denken, sich das
          Leben zu nehmen, wenden Sie sich bitte sofort an:
        </p>
        <ul class="mb-0">
          <li><strong>Telefonseelsorge:</strong> 0800 111 0 111 oder 0800 111 0 222 – kostenlos, anonym, rund um die Uhr</li>
          <li><strong>Ärztlicher Bereitschaftsdienst:</strong> 116 117</li>
          <li><strong>Notruf / Rettungsdienst:</strong> 112</li>
          <li>Die psychiatrische Ambulanz einer Klinik in Ihrer Nähe – ohne Termin, Tag und Nacht</li>
        </ul>
      </div>
    </div>
  </section>

</main>

<footer class="site-footer">
  <div class="container">
    <div class="footer__grid">
      <div>
        <p class="footer__title">Praxis am Lindenhof</p>
        <p class="text-sm" style="opacity: 0.85;">
          Dr. phil. Anna Muster<br>
          Psychologische Psychotherapeutin<br>
          Tiefenpsychologisch fundierte Psychotherapie
        </p>
      </div>

      <div>
        <p class="footer__title">Kontakt</p>
        <ul class="footer__list">
          <li>Musterstraße 12<br>12345 Musterstadt</li>
          <li><a href="tel:+49301234567">030 1234567</a></li>
          <li><a href="mailto:praxis@ihre-domain.de">praxis@ihre-domain.de</a></li>
        </ul>
      </div>

      <div>
        <p class="footer__title">Seiten</p>
        <ul class="footer__list">
          <li><a href="ueber-mich.html">Über mich</a></li>
          <li><a href="leistungen.html">Leistungen</a></li>
          <li><a href="ablauf-kosten.html">Ablauf &amp; Kosten</a></li>
          <li><a href="kontakt.php">Kontakt</a></li>
          <li><a href="impressum.html">Impressum</a></li>
          <li><a href="datenschutz.html">Datenschutz</a></li>
        </ul>
      </div>
    </div>

    <div class="footer__bottom">
      <span>&copy; <span data-current-year>2026</span> Praxis am Lindenhof</span>
      <span>Diese Website verwendet keine Cookies und kein Tracking.</span>
    </div>
  </div>
</footer>

<script src="assets/js/main.js" defer></script>
</body>
</html>
