/* Kleine Helfer – die Seite funktioniert auch vollständig ohne JavaScript. */
(function () {
  "use strict";

  /* --- Mobile Navigation ------------------------------------------------ */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("hauptnavigation");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    // Menü mit Escape schließen
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });

    // Beim Wechsel zur Desktop-Breite zurücksetzen
    var mq = window.matchMedia("(min-width: 56.0625rem)");
    var reset = function (e) {
      if (e.matches) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      }
    };
    if (mq.addEventListener) {
      mq.addEventListener("change", reset);
    } else if (mq.addListener) {
      mq.addListener(reset);
    }
  }

  /* --- Jahreszahl im Fußbereich ----------------------------------------- */
  var years = document.querySelectorAll("[data-current-year]");
  for (var i = 0; i < years.length; i++) {
    years[i].textContent = String(new Date().getFullYear());
  }

  /* --- Fokus auf Formular-Rückmeldung ----------------------------------- */
  var msg = document.querySelector(".form-message");
  if (msg) {
    msg.setAttribute("tabindex", "-1");
    msg.focus({ preventScroll: false });
  }
})();
