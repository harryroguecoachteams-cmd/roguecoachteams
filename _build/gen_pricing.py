"""Generates pricing.html, the 12 fixed-price services.

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
         turn="First intros in 7 to 10 days"),
    dict(cat="brand", kind="Clarity", name="Branding", price=149, pay="DJSY3VC97ER8E",
         blurb="Niche, signature offer and a simple brand kit, so your message lands the "
               "first time someone reads it.",
         deliv=["Niche and offer clarity", "Mini brand kit: logo, colors, fonts",
                "Messaging cheatsheet"],
         turn="7 to 10 business days"),
    dict(cat="content", kind="Retention", name="Community &amp; engagement", price=149,
         pay="F4ASTDHPEMTHQ",
         blurb="WhatsApp, Discord or Facebook groups set up with rituals and prompts that "
               "keep clients active and renewing.",
         deliv=["Platform setup", "90-day prompt bank", "Moderator SOP"],
         turn="5 to 7 business days"),
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
         turn="7 to 10 business days"),
    dict(cat="systems", kind="Systems", name="Automation systems", price=249,
         pay="P6HRFDW67YKFU",
         blurb="Email sequences, onboarding, payments and CRM wired clean, so delivery runs "
               "without you in the middle of it.",
         deliv=["3 to 5 core automations", "Templates and tagging", "Tested end to end"],
         turn="7 to 10 business days"),
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
         turn="7 to 10 business days"),
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
         turn="6 to 8 weeks, expedite available"),
]

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chrome import CAL, icon, page  # noqa: E402

ICONS = {"brand": "compass", "web": "layout", "content": "pen", "authority": "award",
         "leads": "link", "systems": "flow"}


def card(s, i):
    was = f'<span class="svc__was">${s["was"]}</span>' if s.get("was") else ""
    deliv = "\n".join(f"              <li>{d}</li>" for d in s["deliv"])
    delay = f' style="--d:{(i % 3) * 70}ms"' if i % 3 else ""
    return f"""        <article class="card svc rise" data-cat="{s['cat']}"{delay}>
          <div class="svc__top">
            <span class="ico ico--sq">{icon(ICONS[s['cat']])}</span>
            <span class="svc__price">{was}${s['price']}</span>
          </div>
          <p class="kicker">{s['kind']}</p>
          <h3>{s['name']}</h3>
          <p>{s['blurb']}</p>
          <div class="svc__deliv">
            <p class="kicker">What you get</p>
            <ul class="ticks">
{deliv}
            </ul>
          </div>
          <p class="svc__turn">Turnaround: {s['turn']}</p>
          <a class="btn btn--ghost btn--wide" href="https://www.paypal.com/ncp/payment/{s['pay']}" rel="noopener">Buy for ${s['price']} {icon('arrow-up')}</a>
        </article>"""


chips = "\n".join(
    f'        <button class="fchip" type="button" data-filter="{c}"'
    f' aria-pressed="{"true" if c == "all" else "false"}">{label}</button>'
    for c, label in CATS
)
cards = "\n".join(card(s, i) for i, s in enumerate(SERVICES))
SPARK = icon("spark")
ARROW = icon("arrow")

body = f"""
  <section class="sec dark glow gridbg phero" aria-labelledby="price-h">
    <div class="wrap">
      <p class="eyebrow lift" style="--d:40ms">{SPARK}Individual services</p>
      <h1 id="price-h" class="lift" style="--d:120ms">Buy one thing.<br><span class="grad">Fixed scope, fixed price.</span></h1>
      <p class="lede lift" style="--d:240ms">
        No 90-day commitment. Pick the single lever you're missing, see exactly what it costs
        and what you get, and we'll ship it. If two or more would work better together,
        <a class="tlink" href="contact.html">ask for a bundle</a> and we'll price it as one.
      </p>
      <div class="cta-row lift" style="--d:340ms">
        <a class="btn" href="#catalogue">See all 12 services {icon('arrow-down')}</a>
        <a class="btn btn--ghost" href="sprint.html">Or compare the sprint</a>
      </div>
    </div>
  </section>

  <section class="sec light" id="catalogue" aria-labelledby="cat-h">
    <div class="wrap">
      <div class="head--split">
        <div class="rise">
          <p class="eyebrow">{SPARK}The catalogue</p>
          <h2 id="cat-h">Twelve builds.<br><span class="grad">Checkout on every one.</span></h2>
        </div>
        <div class="note rise" style="--d:100ms">
          <p>Every service is modular.</p>
          <p>Tell us what you'd swap and we'll re-scope and re-price it, with nothing hidden.
            Checkout runs on PayPal, by card or PayPal balance.</p>
        </div>
      </div>
      <div class="filters" role="group" aria-label="Filter services by type">
{chips}
      </div>
      <p class="shown">Showing <span data-shown>12 services</span></p>

      <div class="grid">
{cards}
      </div>
    </div>
  </section>

  <section class="sec light light--2" aria-labelledby="faq-h">
    <div class="wrap faqs">
      <div class="faqs__side rise">
        <p class="eyebrow">{SPARK}FAQ</p>
        <h2 id="faq-h">Questions,<br><span class="grad">answered.</span></h2>
        <p class="lede">Calls, custom scopes, credit toward the sprint, and how payment works.</p>
        <div class="advice">
          <b>Prefer to talk it through?</b>
          <p>Fifteen minutes, no pitch.</p>
          <a class="arrowlink" href="{CAL}">Book a 15-min call {ARROW}</a>
        </div>
      </div>
      <div class="acc rise" style="--d:100ms">
        <details>
          <summary>Do I need a call before I buy?</summary>
          <div class="acc__a">No. Every service above has a fixed scope and a working checkout. Buy it and we'll email you the intake questions the same business day. The call is there if you'd rather talk first.</div>
        </details>
        <details>
          <summary>What if I want to add or remove items?</summary>
          <div class="acc__a">Every service is modular. Tell us what you want to swap and we'll send an updated one-page scope and price. No hidden fees, and nothing starts until you say so.</div>
        </details>
        <details>
          <summary>Can I put this toward the 90-day sprint later?</summary>
          <div class="acc__a">Yes. If you move up to a <a href="sprint.html">sprint</a>, we credit the relevant work so you don't pay twice for the same thing.</div>
        </details>
        <details>
          <summary>How does payment work?</summary>
          <div class="acc__a">Checkout runs on PayPal, so you can pay by card or PayPal balance without an account. PayPal emails you the receipt and notifies us of the order.</div>
        </details>
      </div>
    </div>
  </section>

  <section class="sec dark glow glow--low cta" aria-labelledby="cta-h">
    <div class="wrap rise">
      <p class="eyebrow">{SPARK}Ready when you are</p>
      <h2 id="cta-h">Not sure which lever<br><span class="grad">you're missing?</span></h2>
      <p class="lede">That's the most common question we get, and it's a 15-minute answer. Bring what you have and we'll name the next step, even when it's the cheapest thing on this page.</p>
      <div class="cta-row" style="justify-content:center;margin-top:34px">
        <a class="btn" href="{CAL}">Book a 15-min call {ARROW}</a>
        <a class="btn btn--ghost" href="sprint.html">Compare the sprint packages</a>
      </div>
    </div>
  </section>
"""

out = page(
    "Individual services and prices | Rogue Coach Teams",
    "Twelve fixed-price builds for coaches, from $99: branding, website, funnel page, SEO, "
    "podcast launch, automations, JV lead generation and book publishing. Buy one thing, no retainer.",
    "pricing.html",
    body,
)

path = os.path.join(os.path.dirname(__file__), "..", "pricing.html")
io.open(path, "w", encoding="utf8", newline="\n").write(out)
print(f"wrote pricing.html, {len(SERVICES)} services, {len(out)} bytes")
