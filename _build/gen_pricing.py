"""Generates pricing.html — the 12 fixed-price services.

The data below is the single source of truth for prices and PayPal links.
Every `pay` id was checked live before it was written here; re-check with
    curl -sLo /dev/null -w '%{http_code}' https://www.paypal.com/ncp/payment/<id>
"""
import io
import os

CATS = [
    ("all", "Everything"),
    ("brand", "Brand"),
    ("web", "Web &amp; funnels"),
    ("content", "Content"),
    ("authority", "Authority"),
    ("leads", "Leads"),
    ("systems", "Systems"),
]

SERVICES = [
    dict(cat="leads", kind="Leads", name="Lead generation", price=99, pay="S2QFSV3EMCFNW",
         blurb="Validated JV partners plus targeted outreach that fills your calendar with "
               "warm, referral-style leads.",
         deliv=["Partner list and intros", "Outreach scripts", "Booking support"],
         turn="First intros in 7–10 days"),
    dict(cat="brand", kind="Clarity", name="Branding", price=149, pay="DJSY3VC97ER8E",
         blurb="Niche, signature offer and a simple brand kit, so your message lands the "
               "first time someone reads it.",
         deliv=["Niche and offer clarity", "Mini brand kit: logo, colors, fonts",
                "Messaging cheatsheet"],
         turn="7–10 business days"),
    dict(cat="content", kind="Retention", name="Community &amp; engagement", price=149,
         pay="F4ASTDHPEMTHQ",
         blurb="WhatsApp, Discord or Facebook groups set up with rituals and prompts that "
               "keep clients active and renewing.",
         deliv=["Platform setup", "90-day prompt bank", "Moderator SOP"],
         turn="5–7 business days"),
    dict(cat="web", kind="Convert", name="Funnel page", price=199, pay="ED99CV55L2UYS",
         blurb="A landing page built to convert for webinars, challenges or lead magnets. "
               "Copy and design included.",
         deliv=["Wireframe and copy", "Hero, proof and CTA blocks",
                "Integrations: forms and calendars"],
         turn="7 days"),
    dict(cat="content", kind="Organic", name="Marketing &amp; SEO", price=199,
         pay="HXVTF2A2R34NU",
         blurb="Foundational SEO and a content plan so the right clients can find you "
               "without paid ads.",
         deliv=["Site health fixes", "10 keyword pages", "30-day content plan"],
         turn="10 business days"),
    dict(cat="content", kind="Growth", name="Social media growth", price=249,
         pay="FW8EDE63LV366",
         blurb="Daily posts, stories and an engagement cadence that builds authority and "
               "attracts the right audience.",
         deliv=["30-day content plan", "20 posts + 8 carousels", "Engagement SOP"],
         turn="7–10 business days"),
    dict(cat="systems", kind="Systems", name="Automation systems", price=249,
         pay="P6HRFDW67YKFU",
         blurb="Email sequences, onboarding, payments and CRM wired clean, so delivery runs "
               "without you in the middle of it.",
         deliv=["3–5 core automations", "Templates and tagging", "Tested end to end"],
         turn="7–10 business days"),
    dict(cat="web", kind="Credibility", name="Coaching website", price=299,
         pay="C6XU2T7NSPCUG",
         blurb="A 7-page, SEO-ready site designed for trust and conversion. Launch fast, "
               "then iterate weekly.",
         deliv=["7 pages plus a blog index", "SEO basics and analytics",
                "Lead capture and calendar"],
         turn="14 days"),
    dict(cat="authority", kind="Authority", name="Authority &amp; PR", price=299,
         pay="SUYLTUARJ9GPG",
         blurb="Media features, interviews and bylines that raise your status and make JV "
               "partners easier to win.",
         deliv=["Angle and pitch kit", "Outlet and host shortlist",
                "Outreach and scheduling"],
         turn="First pitches in 7 days"),
    dict(cat="systems", kind="Delivery", name="Course / membership setup", price=299,
         pay="V3WNJ79DYABSL",
         blurb="Launch your program with clean modules, gated access, seamless payment and "
               "email integration.",
         deliv=["Structure and pages", "Checkout and access", "Onboarding emails"],
         turn="7–10 business days"),
    dict(cat="authority", kind="Media", name="Podcast launch", price=299, was=349,
         pay="94BW74KEDTTN2",
         blurb="Concept, setup and distribution, so you show up weekly where your prospects "
               "already listen.",
         deliv=["10-episode plan and templates", "Cover, trailer, feeds",
                "Guest booking pipeline"],
         turn="10 business days"),
    dict(cat="authority", kind="Flagship", name="Book publishing", price=699,
         pay="XFSKVB5G8SVDU",
         blurb="Turn your IP into a published book that opens doors to PR, JV partnerships "
               "and premium clients.",
         deliv=["Outline and manuscript support", "Cover and interior design",
                "Publishing and distribution"],
         turn="6–8 weeks, expedite available"),
]

CAL = "https://calendly.com/roguecoachteams/rebel-strategy-call"

NAV = """      <a href="services.html">Services</a>
      <a href="pricing.html">Pricing</a>
      <a href="about.html">About</a>
      <a href="insights.html">Insights</a>
      <a href="contact.html">Contact</a>"""


def head(title, desc, canon):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://roguecoachteams.com/{canon}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="icon" href="assets/img/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/site.css">
<script>
(function(d){{d.className+=' js';setTimeout(function(){{
  if(!document.body||!document.body.classList.contains('is-ready'))
    d.className=d.className.replace(' js','');}},2500);}})(document.documentElement);
</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<header class="hdr">
  <div class="wrap hdr__in">
    <a class="brand" href="index.html"><img src="assets/img/logo.png" alt="" width="34" height="34">Rogue Coach Teams</a>
    <nav class="nav" aria-label="Primary">
{NAV}
    </nav>
    <a class="btn btn--sm" href="{CAL}">Book a 15-min call</a>
    <button class="burger" type="button" aria-expanded="false" aria-controls="drawer" aria-label="Menu"><span></span></button>
  </div>
</header>

<nav class="drawer" id="drawer" aria-label="Mobile">
{NAV}
  <a class="btn" href="{CAL}">Book a 15-min call</a>
</nav>

<main id="main">
"""


FOOT = f"""</main>

<footer class="ftr">
  <div class="wrap">
    <div class="ftr__grid">
      <div>
        <a class="brand" href="index.html" style="margin-bottom:16px"><img src="assets/img/logo.png" alt="" width="34" height="34">Rogue Coach Teams</a>
        <p style="max-width:38ch">The lean growth team for coaches. Authority, partnerships and simple systems — built with you, and handed over to you.</p>
      </div>
      <div>
        <h4>Work with us</h4>
        <ul>
          <li><a href="services.html">Services</a></li>
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
    </div>
    <div class="ftr__base">
      <span>© 2026 Rogue Coach Teams. Built with intention, not with fluff.</span>
      <a href="mailto:roguecoachteams@gmail.com">roguecoachteams@gmail.com</a>
    </div>
  </div>
</footer>

<script src="assets/js/site.js"></script>
</body>
</html>
"""


def card(s):
    was = f'<span class="svc__was">${s["was"]}</span>' if s.get("was") else ""
    deliv = "\n".join(f"            <li>{d}</li>" for d in s["deliv"])
    return f"""        <article class="svc" data-cat="{s['cat']}">
          <div class="svc__top">
            <span class="svc__kind">{s['kind']}</span>
            <span class="svc__price">{was}${s['price']}</span>
          </div>
          <h3>{s['name']}</h3>
          <p>{s['blurb']}</p>
          <div class="svc__deliv">
            <p class="label label--mute label--plain" style="margin:16px 0 8px">What you get</p>
            <ul class="ticks">
{deliv}
            </ul>
          </div>
          <p class="svc__turn">Turnaround: {s['turn']}</p>
          <a class="btn btn--ghost btn--wide" href="https://www.paypal.com/ncp/payment/{s['pay']}" rel="noopener">
            Buy for ${s['price']} <span class="arw" aria-hidden="true">↗</span>
          </a>
        </article>"""


chips = "\n".join(
    f'        <button class="chip" type="button" data-filter="{c}"'
    f'{" aria-pressed=\"true\"" if c == "all" else " aria-pressed=\"false\""}>{label}</button>'
    for c, label in CATS
)
cards = "\n".join(card(s) for s in SERVICES)

body = f"""
  <section class="band band--tight">
    <div class="wrap">
      <p class="label lift" style="--d:60ms">Individual services</p>
      <h1 class="lift" style="--d:140ms">Buy one thing.<br>Fixed scope, fixed price.</h1>
      <p class="lede lift" style="--d:240ms;margin-top:24px;max-width:56ch">
        No 90-day commitment. Pick the single lever you're missing, see exactly what it costs
        and what you get, and we'll ship it. If two or more would work better together,
        <a class="tlink" href="contact.html">ask for a bundle</a> and we'll price it as one.
      </p>
    </div>
  </section>

  <section class="band band--tight">
    <div class="wrap">
      <div class="filters" role="group" aria-label="Filter services by type">
{chips}
      </div>
      <p class="tiny" style="margin:-18px 0 30px">Showing <span data-shown>12 services</span></p>

      <div class="grid">
{cards}
      </div>

      <p class="tiny" style="margin-top:32px;max-width:74ch">
        Every service is modular. Tell us what you'd swap and we'll re-scope and re-price it,
        with nothing hidden. Prefer to talk it through?
        <a class="tlink" href="{CAL}">Book 15 minutes</a>.
      </p>
    </div>
  </section>

  <section class="band band--alt band--edge">
    <div class="wrap wrap--narrow">
      <h2 style="margin-bottom:36px">Questions, answered</h2>
      <div class="faq">
        <details>
          <summary>Do I need a call before I buy?</summary>
          <div class="faq__a">No. Every service above has a fixed scope and a working checkout — buy it and we'll email you the intake questions the same business day. The call is there if you'd rather talk first.</div>
        </details>
        <details>
          <summary>What if I want to add or remove items?</summary>
          <div class="faq__a">Every service is modular. Tell us what you want to swap and we'll send an updated one-page scope and price. No hidden fees, and nothing starts until you say so.</div>
        </details>
        <details>
          <summary>Can I put this toward the 90-day sprint later?</summary>
          <div class="faq__a">Yes. If you move up to a <a href="sprint.html">sprint</a>, we credit the relevant work so you don't pay twice for the same thing.</div>
        </details>
        <details>
          <summary>How does payment work?</summary>
          <div class="faq__a">Checkout runs on PayPal, so you can pay by card or PayPal balance without an account. PayPal emails you the receipt and notifies us of the order.</div>
        </details>
      </div>
    </div>
  </section>

  <section class="band band--tight">
    <div class="wrap">
      <div class="finale rise">
        <h2>Not sure which lever is the one you're missing?</h2>
        <p class="lede">That's the most common question we get, and it's a 15-minute answer. Bring what you have and we'll name the next step — even when it's the cheapest thing on this page.</p>
        <div class="hero__cta">
          <a class="btn" href="{CAL}">Book a 15-min call <span class="arw" aria-hidden="true">↗</span></a>
          <a class="btn btn--ghost" href="sprint.html">Compare the sprint packages</a>
        </div>
      </div>
    </div>
  </section>
"""

out = head(
    "Individual services and prices — Rogue Coach Teams",
    "Twelve fixed-price builds for coaches, from $99: branding, website, funnel page, SEO, "
    "podcast launch, automations, JV lead generation and book publishing. Buy one thing, no retainer.",
    "pricing.html",
) + body + FOOT

path = os.path.join(os.path.dirname(__file__), "..", "pricing.html")
io.open(path, "w", encoding="utf8").write(out)
print(f"wrote pricing.html — {len(SERVICES)} services, {len(out)} bytes")
