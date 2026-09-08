"""Ports the three WordPress posts into static article pages plus insights.html.

Source is posts.json, pulled from the live WP REST API. The WP markup carries
Elementor/Gutenberg wrappers, inline <style> blocks and per-element classes that
would fight site.css, so everything is stripped back to semantic HTML and
restyled by the .prose rules.

Re-run:  python _build/gen_articles.py
"""
import html
import io
import json
import os
import re
import urllib.request
import ssl
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(os.path.join(HERE, ".."))
IMGDIR = os.path.join(SITE, "assets", "img", "blog")
ORIGIN = "https://209.74.67.50"          # domain is parked; origin still serves
HOST = "roguecoachteams.com"
CTX = ssl._create_unverified_context()

CAL = "https://calendly.com/roguecoachteams/rebel-strategy-call"

NAV = """      <a href="services.html">Services</a>
      <a href="pricing.html">Pricing</a>
      <a href="about.html">About</a>
      <a href="insights.html">Insights</a>
      <a href="contact.html">Contact</a>"""

META = {
    "coaching-scams": dict(
        slug="coaching-scams",
        title="The $43,000 lie: how high-ticket coaching agencies burn coaches",
        kicker="Scam watch",
        desc="An inside look at the high-ticket coaching agency playbook, what it "
             "actually costs coaches, and how to tell a real partner from a pitch.",
    ),
    "authority-building-for-coaches": dict(
        slug="authority-building-for-coaches",
        title="Authority building for coaches: from another coach to the coach",
        kicker="Authority",
        desc="Practical strategies to build genuine authority as a coach, so the right "
             "clients arrive already convinced instead of needing to be sold.",
    ),
    "joint-ventures-for-coaches": dict(
        slug="joint-ventures-for-coaches",
        title="Joint ventures for coaches: how partnerships grow you faster",
        kicker="Joint ventures",
        desc="How joint ventures let coaches amplify reach, share resources and win warm "
             "introductions without spending a cent on ads.",
    ),
}

KEEP = {"p", "h2", "h3", "h4", "ul", "ol", "li", "blockquote", "a", "strong", "b",
        "em", "i", "img", "figure", "figcaption", "br", "details", "summary",
        "table", "thead", "tbody", "tr", "th", "td", "aside"}


def fetch(url, dest):
    req = urllib.request.Request(url)
    req.add_header("Host", HOST)
    req.add_header("User-Agent", "Mozilla/5.0")
    data = urllib.request.urlopen(req, context=CTX, timeout=60).read()
    io.open(dest, "wb").write(data)
    return len(data)


def localize_images(body, slug):
    """Copy every remote image next to the site so no page depends on a host we
    do not control — the WP uploads (served from the origin IP, since the domain
    is parked) and the Unsplash covers the posts hotlink."""
    os.makedirs(IMGDIR, exist_ok=True)

    for m in set(re.findall(r'https://roguecoachteams\.com(/wp-content/uploads/[^"\'\s>]+)', body)):
        name = re.sub(r"[^A-Za-z0-9._-]", "-", m.rsplit("/", 1)[-1])
        dest = os.path.join(IMGDIR, name)
        if not os.path.exists(dest):
            try:
                n = fetch(ORIGIN + m, dest)
                print(f"    img {name} ({n // 1024}K)")
            except Exception as e:
                print(f"    MISS {name}: {e}")
                continue
        body = body.replace("https://roguecoachteams.com" + m, "assets/img/blog/" + name)

    for i, url in enumerate(dict.fromkeys(re.findall(r'https://images\.unsplash\.com/[^"\'\s>]+', body))):
        name = f"{slug}-cover-{i + 1}.jpg" if i else f"{slug}-cover.jpg"
        dest = os.path.join(IMGDIR, name)
        if not os.path.exists(dest):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                data = urllib.request.urlopen(req, timeout=60).read()
                io.open(dest, "wb").write(data)
                print(f"    cover {name} ({len(data) // 1024}K)")
            except Exception as e:
                print(f"    MISS {name}: {e}")
                continue
        body = body.replace(url, "assets/img/blog/" + name)

    return body


VOID = {"img", "br", "hr"}


class Cleaner(HTMLParser):
    """Rebuilds the post as semantic HTML.

    The posts are hand-built templates inside an Elementor HTML widget, so the
    class names are predictable:
      section.rc-hero   duplicates the title, subtitle and cover — the page
                        template supplies those, so the whole subtree is cut
                        (the cover image is lifted out first).
      div.rc-callout    a highlighted note  -> <aside>
      div.rc-card       a bordered panel    -> <aside>, never nested
      span.rc-check     a literal tick glyph -> dropped, .ticks draws its own
    Everything else structural is unwrapped; anything not in KEEP is dropped.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip = 0          # depth counter while inside rc-hero
        self.stack = []        # what we actually emitted, to close correctly
        self.aside = 0         # current <aside> nesting
        self.cover = None      # (src, alt) lifted out of the hero

    def _cls(self, attrs):
        return dict(attrs).get("class", "") or ""

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        cls = self._cls(attrs)
        a = dict(attrs)

        if self.skip:
            if tag == "img" and self.cover is None and "rc-cover" not in cls:
                self.cover = (a.get("src", ""), a.get("alt", ""))
            if tag not in VOID:
                self.skip += 1
            return

        if tag == "section" and "rc-hero" in cls:
            self.skip = 1
            return
        if tag == "span" and "rc-check" in cls:
            self.skip = 1
            return

        if tag in ("div", "section") and ("rc-callout" in cls or "rc-card" in cls):
            if self.aside == 0:
                self.out.append("<aside>")
                self.stack.append(("aside", tag))
                self.aside += 1
            else:
                self.stack.append((None, tag))
            return

        if tag in ("div", "section", "span", "header", "footer", "main", "article", "nav"):
            self.stack.append((None, tag))
            return

        if tag not in KEEP:
            if tag not in VOID:
                self.stack.append((None, tag))
            return

        keep = []
        for k, v in attrs:
            k = k.lower()
            if tag == "a" and k == "href":
                keep.append(f'href="{html.escape(v or "", quote=True)}"')
            elif tag == "img" and k in ("src", "alt", "width", "height"):
                keep.append(f'{k}="{html.escape(v or "", quote=True)}"')
        if tag == "img":
            keep.append('loading="lazy"')
        self.out.append(f"<{tag}{' ' + ' '.join(keep) if keep else ''}>")
        if tag not in VOID:
            self.stack.append((tag, tag))

    def handle_startendtag(self, tag, attrs):
        if tag.lower() in VOID:
            self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if self.skip:
            self.skip -= 1
            return
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, -1, -1):
            emitted, src = self.stack[i]
            if src == tag:
                if emitted:
                    self.out.append(f"</{emitted}>")
                    if emitted == "aside":
                        self.aside -= 1
                del self.stack[i:]
                return

    def handle_data(self, data):
        if self.skip:
            return
        if data.strip():
            self.out.append(html.escape(data, quote=False))
        elif self.out and not self.out[-1].endswith(" "):
            self.out.append(" ")

    def handle_comment(self, data):
        pass


def clean(body, slug):
    body = re.sub(r"(?is)<(style|script|noscript)[^>]*>.*?</\1>", "", body)
    body = localize_images(body, slug)

    c = Cleaner()
    c.feed(body)
    c.close()
    out = "".join(c.out)

    # any stray text that ended up outside a block gets its own paragraph
    out = re.sub(r"(?is)<h1[^>]*>.*?</h1>", "", out)
    out = re.sub(r"(?is)<p>\s*</p>", "", out)
    out = re.sub(r"(?is)<aside>\s*</aside>", "", out)
    # a wide table scrolls inside its own box; it must never scroll the page
    out = re.sub(r"(?is)(<table>.*?</table>)", r'<div class="scrollx">\1</div>', out)
    # the posts link to the old WP booking page, which is on the parked domain.
    # Every booking CTA on this site goes straight to Calendly instead.
    out = out.replace("https://roguecoachteams.com/rebel-strategy-call/", CAL)
    out = out.replace("https://roguecoachteams.com/rebel-strategy-call", CAL)
    out = re.sub(r">\s{2,}<", ">\n<", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip(), c.cover


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
<meta property="og:type" content="article">
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

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def pretty(date):
    y, m, d = date[:10].split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}"


posts = json.load(open(os.path.join(HERE, "posts.json"), encoding="utf8"))
index = []

for p in posts:
    meta = META.get(p["slug"])
    if not meta:
        print("skip (no metadata):", p["slug"])
        continue
    print("building", meta["slug"])
    body, cover = clean(p["content"]["rendered"], meta["slug"])
    title = meta["title"]
    date = p["date"][:10]

    lead = ""
    if cover and cover[0]:
        lead = (
            '      <img src="{}" alt="{}" loading="lazy" '
            'style="width:100%;border-radius:var(--r);border:1px solid var(--line);'
            'margin-bottom:40px">\n'
        ).format(cover[0], html.escape(cover[1] or "", quote=True))

    page = head(f"{title} — Rogue Coach Teams", meta["desc"], meta["slug"] + ".html") + f"""
  <section class="band band--tight">
    <div class="wrap wrap--narrow">
      <p class="label lift" style="--d:60ms">{meta['kicker']}</p>
      <h1 class="lift" style="--d:140ms">{title}</h1>
      <p class="tiny lift" style="--d:240ms;margin-top:20px">
        <time datetime="{date}">{pretty(date)}</time> · Rogue Coach Teams
      </p>
    </div>
  </section>

  <section class="band band--tight">
    <div class="wrap wrap--narrow">
{lead}      <div class="prose">
{body}
      </div>
    </div>
  </section>

  <section class="band band--tight">
    <div class="wrap wrap--narrow">
      <div class="finale">
        <h2>Want this handled rather than read about?</h2>
        <p class="lede">Fifteen minutes on your niche, your offer and the fastest honest path to 10–15 calls a month.</p>
        <div class="hero__cta">
          <a class="btn" href="{CAL}">Book a 15-min call <span class="arw" aria-hidden="true">↗</span></a>
          <a class="btn btn--ghost" href="insights.html">Read the others</a>
        </div>
      </div>
    </div>
  </section>
""" + FOOT

    io.open(os.path.join(SITE, meta["slug"] + ".html"), "w", encoding="utf8").write(page)
    excerpt = re.sub(r"<[^>]+>", " ", p["excerpt"]["rendered"])
    excerpt = html.unescape(re.sub(r"\s+", " ", excerpt)).strip()
    index.append((date, meta, excerpt))

# ---------------------------------------------------------------- index page
index.sort(reverse=True)
cards = "\n".join(f"""        <a class="post" href="{m['slug']}.html">
          <time datetime="{d}">{m['kicker']} · {pretty(d)}</time>
          <h3>{m['title']}</h3>
          <p>{ex[:190].rsplit(' ', 1)[0]}…</p>
        </a>""" for d, m, ex in index)

page = head("Insights — Rogue Coach Teams",
            "Field notes on authority, joint ventures and the parts of the coaching "
            "industry nobody puts in the sales page.",
            "insights.html") + f"""
  <section class="band band--tight">
    <div class="wrap">
      <p class="label lift" style="--d:60ms">Insights</p>
      <h1 class="lift" style="--d:140ms;max-width:16ch">What we've learned, written down.</h1>
      <p class="lede lift" style="--d:240ms;margin-top:24px">
        Field notes on authority, partnerships, and the parts of the coaching industry that
        don't make it into anyone's sales page. Written by the people doing the work.
      </p>
    </div>
  </section>

  <section class="band band--tight">
    <div class="wrap">
      <div class="grid rise">
{cards}
      </div>
    </div>
  </section>

  <section class="band band--tight">
    <div class="wrap">
      <div class="finale rise">
        <h2>Prefer the short version, out loud?</h2>
        <p class="lede">Book fifteen minutes and we'll apply all of this to your specific situation instead.</p>
        <div class="hero__cta">
          <a class="btn" href="{CAL}">Book a 15-min call <span class="arw" aria-hidden="true">↗</span></a>
          <a class="btn btn--ghost" href="services.html">See the services</a>
        </div>
      </div>
    </div>
  </section>
""" + FOOT

io.open(os.path.join(SITE, "insights.html"), "w", encoding="utf8").write(page)
print(f"wrote insights.html — {len(index)} articles")
