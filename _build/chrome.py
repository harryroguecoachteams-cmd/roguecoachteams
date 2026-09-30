"""Shared page chrome: <head>, the floating nav, the mobile drawer and the footer.

Used three ways:
  - gen_pricing.py and gen_articles.py import head() / HEADER / FOOTER directly
  - apply_chrome.py rewrites the marked blocks inside the hand-written pages:
        <!-- @head -->   ... <!-- /@head -->
        <!-- @header --> ... <!-- /@header -->
        <!-- @footer --> ... <!-- /@footer -->
Edit the nav or footer here, then run  python _build/apply_chrome.py
"""

CAL = "https://calendly.com/roguecoachteams/rebel-strategy-call"
EMAIL = "roguecoachteams@gmail.com"   # Harsh chose this one on 30 Sep 2026
WA_NUMBER = "13202911634"   # +1 (320) 291-1634, WhatsApp business; digits only with country code
SITE = "https://roguecoachteams.com/"

FONTS = ("https://fonts.googleapis.com/css2?family=Inter+Tight:wght@700;800"
         "&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap")


def icon(name, cls="i"):
    return f'<svg class="{cls}" aria-hidden="true"><use href="assets/icons.svg#{name}"/></svg>'


NAV_LINKS = [
    ("services.html", "Offers"),
    ("pricing.html", "Pricing"),
    ("about.html", "About"),
    ("insights.html", "Insights"),
    ("contact.html", "Contact"),
]


def head(title, desc, canon, image="assets/img/v2/fan-center.webp", noindex=False):
    canon_url = SITE + ("" if canon == "index.html" else canon)
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">{'<meta name="robots" content="noindex, nofollow">' if noindex else ''}
<link rel="canonical" href="{canon_url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{canon_url}">
<meta property="og:image" content="{SITE}{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0B0F1A">
<link rel="icon" href="assets/img/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css">
<script>
/* Reveal animations only apply when JS is alive. If site.js never runs,
   the flag is pulled back off and the page renders as plain markup. */
(function(d){{d.className+=' js';setTimeout(function(){{
  if(!document.body||!document.body.classList.contains('is-ready'))
    d.className=d.className.replace(' js','');}},2500);}})(document.documentElement);
</script>"""


def _nav(indent):
    pad = " " * indent
    return "\n".join(f'{pad}<a href="{h}">{t}</a>' for h, t in NAV_LINKS)


BRAND = ('<a class="brand" href="index.html" aria-label="Rogue Coach Teams, home">'
         '<img src="assets/img/v2/mark.png" alt="" width="40" height="20">'
         '<span>Rogue Coach Teams</span></a>')

HEADER = f"""<a class="skip" href="#main">Skip to content</a>

<div class="topbar">
  <header class="navbar">
    {BRAND}
    <nav class="nav" aria-label="Primary">
{_nav(6)}
    </nav>
    <a class="btn btn--sm" href="{CAL}">Book a call {icon('arrow')}</a>
    <button class="burger" type="button" aria-expanded="false" aria-controls="drawer" aria-label="Menu"><span></span></button>
  </header>
</div>

<nav class="drawer" id="drawer" aria-label="Mobile">
{_nav(2)}
  <a class="btn" href="{CAL}">Book a 15-min call {icon('arrow')}</a>
</nav>"""

WA_FOOT = (f'\n          <li><a href="https://wa.me/{WA_NUMBER}"><span class="ico">{icon("message")}</span>Chat on WhatsApp</a></li>'
           if WA_NUMBER else "")
WA_WIDGET = (f'\n<a class="wa" href="https://wa.me/{WA_NUMBER}?text=Hi%20Rogue%20Coach%20Teams" target="_blank" rel="noopener" '
             f'aria-label="Chat with us on WhatsApp"><svg class="i" aria-hidden="true"><use href="assets/icons.svg#message"/></svg>'
             f'<span>Chat on WhatsApp</span></a>' if WA_NUMBER else "")

FOOTER = f"""<footer class="ftr">
  <div class="wrap">
    <div class="ftr__grid">
      <div>
        {BRAND}
        <p class="ftr__tag">Authority first.<br><span>Built to book calls.</span></p>
        <p class="ftr__small">The lean growth team for coaches. Built with you, and handed over to you.</p>
      </div>
      <div>
        <h4>Work with us</h4>
        <ul>
          <li><a href="services.html">Offers</a></li>
          <li><a href="sprint.html">90-day sprint</a></li>
          <li><a href="pricing.html">Individual services</a></li>
          <li><a href="{CAL}">Book a call</a></li>
        </ul>
      </div>
      <div>
        <h4>Company</h4>
        <ul>
          <li><a href="about.html">About</a></li>
          <li><a href="index.html#work">Work</a></li>
          <li><a href="insights.html">Insights</a></li>
          <li><a href="contact.html">Contact</a></li>
        </ul>
      </div>
      <div class="ftr__contact">
        <h4>Contact</h4>
        <ul>
          <li><a href="mailto:{EMAIL}"><span class="ico">{icon('mail')}</span>{EMAIL}</a></li>
          <li><a href="{CAL}"><span class="ico">{icon('calendar')}</span>Book a 15-min call</a></li>{WA_FOOT}
        </ul>
      </div>
    </div>
    <div class="ftr__base">
      <span>&copy; 2026 Rogue Coach Teams. Built with intention, not with fluff.</span>
      <span>Lean growth team for coaches</span>
    </div>
  </div>
</footer>

{WA_WIDGET}
<script src="assets/js/site.js"></script>"""


def page(title, desc, canon, body, image="assets/img/v2/fan-center.webp", noindex=False):
    """A full page for the generators."""
    return f"""<!doctype html>
<html lang="en">
<head>
<!-- @head -->
{head(title, desc, canon, image, noindex)}
<!-- /@head -->
</head>
<body>
<!-- @header -->
{HEADER}
<!-- /@header -->

<main id="main">
{body}
</main>

<!-- @footer -->
{FOOTER}
<!-- /@footer -->
</body>
</html>
"""
