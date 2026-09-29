/* =====================================================================
   Rogue Coach Teams, site.js
   No framework, no build step. Everything degrades to a working page
   with JS off: content is in the HTML, links are real hrefs, and the
   contact form falls back to email.
   ===================================================================== */
(function () {
  "use strict";

  var CAL_LINK = "https://calendly.com/roguecoachteams/rebel-strategy-call";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------------------------------------------- header + drawer */
  var hdr = document.querySelector(".topbar");
  if (hdr) {
    var onScroll = function () {
      hdr.classList.toggle("is-stuck", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  var burger = document.querySelector(".burger");
  var drawer = document.querySelector(".drawer");
  if (burger && drawer) {
    burger.addEventListener("click", function () {
      var open = burger.getAttribute("aria-expanded") === "true";
      burger.setAttribute("aria-expanded", String(!open));
      drawer.classList.toggle("is-open", !open);
      document.body.style.overflow = !open ? "hidden" : "";
    });
    drawer.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        burger.setAttribute("aria-expanded", "false");
        drawer.classList.remove("is-open");
        document.body.style.overflow = "";
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && drawer.classList.contains("is-open")) {
        burger.setAttribute("aria-expanded", "false");
        drawer.classList.remove("is-open");
        document.body.style.overflow = "";
        burger.focus();
      }
    });
  }

  /* ------------------------------------------- scroll reveal (once only) */
  /* Threshold stays at 0 with a bottom-margin trigger line: a threshold of
     0.2 never fires for elements taller than the viewport. */
  var revealables = document.querySelectorAll(".rise, [data-count], .signal--scroll");

  function activate(el) {
    el.classList.add("is-in");
    if (el.hasAttribute("data-count")) countUp(el);
    if (el.classList.contains("signal--scroll")) el.classList.add("is-live");
  }

  if ("IntersectionObserver" in window && !reduced) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          activate(en.target);
          io.unobserve(en.target);
        });
      },
      { root: null, threshold: 0, rootMargin: "0px 0px -12% 0px" }
    );
    revealables.forEach(function (el) {
      io.observe(el);
    });
  } else {
    revealables.forEach(activate);
  }

  /* --------------------------------------------- signal line: path length */
  /* Each path sets its own dash length so the draw reads at any width. */
  document.querySelectorAll(".signal__path").forEach(function (p) {
    var len = 1200;
    try {
      len = Math.ceil(p.getTotalLength());
    } catch (e) {
      /* getTotalLength throws in some headless contexts; the fallback is fine */
    }
    p.style.setProperty("--len", len);
  });

  /* The hero signal draws on load; scroll copies wait for the observer. */
  document.querySelectorAll(".signal--load").forEach(function (s) {
    s.classList.add("is-live");
  });

  /* ------------------------------------------------------------ count up */
  function countUp(el) {
    var target = parseFloat(el.getAttribute("data-count"));
    if (isNaN(target)) return;
    var prefix = el.getAttribute("data-prefix") || "";
    var suffix = el.getAttribute("data-suffix") || "";
    /* The suffix sits in an <em> so it can take the accent colour. */
    function paint(v) {
      el.innerHTML = prefix + v + (suffix ? "<em>" + suffix + "</em>" : "");
    }
    if (reduced) {
      paint(target);
      return;
    }
    var dur = 1100;
    var t0 = null;
    function frame(t) {
      if (t0 === null) t0 = t;
      var k = Math.min(1, (t - t0) / dur);
      var eased = 1 - Math.pow(1 - k, 3);
      var v = Math.round(target * eased);
      paint(v);
      if (k < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  /* ------------------------------------------------- hero load sequence */
  /* Fires unconditionally on the next frame. The animation uses fill:forwards,
     so it still lands correctly if the tab was in the background while it ran,
     and the hero is never left invisible waiting for an event. */
  requestAnimationFrame(function () {
    document.body.classList.add("is-ready");
  });

  /* ------------------------------------------------------ video playback */
  document.querySelectorAll("[data-video]").forEach(function (card) {
    var btn = card.querySelector(".vid__play");
    var vid = card.querySelector("video");
    if (!btn || !vid) return;
    btn.addEventListener("click", function () {
      vid.setAttribute("controls", "");
      card.classList.add("is-playing");
      btn.remove();
      vid.play();
      vid.focus();
    });
  });

  /* ------------------------------------------- service catalogue filters */
  var chips = document.querySelectorAll(".fchip[data-filter]");
  var cards = document.querySelectorAll(".svc[data-cat]");
  var countOut = document.querySelector("[data-shown]");

  if (chips.length && cards.length) {
    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        var want = chip.getAttribute("data-filter");
        chips.forEach(function (c) {
          c.setAttribute("aria-pressed", String(c === chip));
        });
        var shown = 0;
        cards.forEach(function (card) {
          var hit = want === "all" || card.getAttribute("data-cat") === want;
          card.classList.toggle("is-hidden", !hit);
          if (hit) shown++;
        });
        if (countOut) {
          countOut.textContent =
            shown + (shown === 1 ? " service" : " services");
        }
      });
    });
  }

  /* --------------------------------------------------------- contact form */
  /* Lead delivery has two modes.
     - LEAD_ENDPOINT "" (default): the form composes the whole enquiry and
       hands it to the visitor's mail client. No backend, nothing to break,
       and the message is never lost.
     - LEAD_ENDPOINT set to a URL that answers POST: the form posts JSON and
       falls back to the mail client if the request fails.
     See _setup/lead-endpoint.gs for a drop-in Apps Script that adds the POST
     handler the current "RCT payments log" script does not have. Paste it,
     redeploy, put the /exec URL below, and the form goes silent-send. */
  var LEAD_ENDPOINT = "";
  var LEAD_EMAIL = "roguecoachteams@gmail.com";

  var form = document.querySelector("[data-lead-form]");
  if (form) {
    var note = form.querySelector("[data-note]");
    var submit = form.querySelector("[type=submit]");

    var say = function (msg, kind) {
      if (!note) return;
      note.hidden = false;
      note.className = "formnote formnote--" + kind;
      note.innerHTML = msg;
      note.focus();
    };

    var mailtoFor = function (data) {
      var body =
        "Name: " + data.name + "\n" +
        "Email: " + data.email + "\n" +
        (data.goal ? "Interested in: " + data.goal + "\n" : "") +
        "\n" + data.message + "\n";
      return (
        "mailto:" + LEAD_EMAIL +
        "?subject=" + encodeURIComponent("Website enquiry from " + data.name) +
        "&body=" + encodeURIComponent(body)
      );
    };

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var data = Object.fromEntries(new FormData(form).entries());

      if (!data.name || !data.email || !data.message) {
        say("Add your name, email and a short message so we can reply.", "err");
        return;
      }

      var link = mailtoFor(data);

      if (!LEAD_ENDPOINT) {
        window.location.href = link;
        say(
          "Your email app is opening with the message ready to send. " +
            "If nothing happened, <a class=\"tlink\" href=\"" + link + "\">open it here</a> " +
            "or write to <b>" + LEAD_EMAIL + "</b>.",
          "ok"
        );
        return;
      }

      var label = submit ? submit.textContent : "";
      if (submit) {
        submit.disabled = true;
        submit.textContent = "Sending…";
      }

      fetch(LEAD_ENDPOINT, {
        method: "POST",
        mode: "no-cors",
        headers: { "Content-Type": "text/plain;charset=utf-8" },
        body: JSON.stringify(
          Object.assign({ type: "lead", source: "roguecoachteams.com" }, data)
        )
      })
        .then(function () {
          form.reset();
          say(
            "Thanks, your message is in. We reply within 24 to 48 hours. " +
              'Want it faster? <a class="tlink" href="' + CAL_LINK +
              '">Book a 15-min call</a>.',
            "ok"
          );
        })
        .catch(function () {
          say(
            'That did not go through. <a class="tlink" href="' + link +
              '">Send it by email instead</a>.',
            "err"
          );
        })
        .then(function () {
          if (submit) {
            submit.disabled = false;
            submit.textContent = label;
          }
        });
    });
  }


  /* -------------------------------------------------- current nav marker */
  var here = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".nav a, .drawer a").forEach(function (a) {
    var href = a.getAttribute("href") || "";
    if (href === here || (here === "index.html" && href === "./")) {
      a.setAttribute("aria-current", "page");
    }
  });
})();
