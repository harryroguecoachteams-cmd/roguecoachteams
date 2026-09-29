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
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.abspath(os.path.join(HERE, ".."))
IMGDIR = os.path.join(SITE, "assets", "img", "blog")
ORIGIN = "https://209.74.67.50"          # domain is parked; origin still serves
HOST = "roguecoachteams.com"
CTX = ssl._create_unverified_context()

CAL = "https://calendly.com/roguecoachteams/rebel-strategy-call"

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
    do not control: the WP uploads (served from the origin IP, since the domain
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
      section.rc-hero   duplicates the title, subtitle and cover; the page
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


def strip_dashes(text):
    """No em or en dashes anywhere on the site. Ranges read "to", a figure label
    takes a colon, and any other dash becomes a comma."""
    dash = "[\u2013\u2014]"
    text = re.sub(r"(?<=[0-9Kk])\s*" + dash + r"\s*(?=[$0-9])", " to ", text)
    text = re.sub(r"(Figure [0-9.]+)\s*" + dash + r"\s*", r"\1: ", text)
    text = re.sub(r"\s*" + dash + r"\s*", ", ", text)
    return text


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
    out = strip_dashes(out)
    out = re.sub(r">\s{2,}<", ">\n<", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip(), c.cover


sys.path.insert(0, HERE)
from chrome import icon, page  # noqa: E402

SPARK = icon("spark")
ARROW = icon("arrow")


MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def pretty(date):
    y, m, d = date[:10].split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}"


posts = json.load(open(os.path.join(HERE, "posts.json"), encoding="utf8"))
index = []
CAL = "https://calendly.com/roguecoachteams/rebel-strategy-call"

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
    cover_src = cover[0] if cover and cover[0] else ""
    if cover_src:
        lead = (
            '      <img class="cover rise" src="{}" alt="{}" width="1600" height="900">\n'
        ).format(cover_src, html.escape(cover[1] or "", quote=True))

    body_html = f"""
  <section class="sec dark glow gridbg phero" aria-labelledby="post-h">
    <div class="wrap">
      <p class="eyebrow lift" style="--d:40ms">{SPARK}{meta['kicker']}</p>
      <h1 id="post-h" class="lift" style="--d:120ms;max-width:20ch;font-size:clamp(2.2rem,1.2rem + 3.4vw,3.9rem)">{title}</h1>
      <p class="phero__meta lift" style="--d:240ms"><time datetime="{date}">{pretty(date)}</time> · Rogue Coach Teams</p>
    </div>
  </section>

  <section class="sec light">
    <div class="wrap wrap--narrow">
{lead}      <div class="prose">
{body}
      </div>
    </div>
  </section>

  <section class="sec dark glow glow--low cta" aria-labelledby="cta-h">
    <div class="wrap rise">
      <p class="eyebrow">{SPARK}Ready when you are</p>
      <h2 id="cta-h">Want this handled<br><span class="grad">rather than read about?</span></h2>
      <p class="lede">Fifteen minutes on your niche, your offer and the fastest honest path to 10 to 15 calls a month.</p>
      <div class="cta-row" style="justify-content:center;margin-top:34px">
        <a class="btn" href="{CAL}">Book a 15-min call {ARROW}</a>
        <a class="btn btn--ghost" href="insights.html">Read the others</a>
      </div>
    </div>
  </section>
"""
    image = cover_src if cover_src.startswith("assets/") else "assets/img/v2/fan-center.webp"
    out = page(f"{title} | Rogue Coach Teams", meta["desc"], meta["slug"] + ".html",
               body_html, image)
    io.open(os.path.join(SITE, meta["slug"] + ".html"), "w", encoding="utf8", newline="\n").write(out)
    excerpt = re.sub(r"<[^>]+>", " ", p["excerpt"]["rendered"])
    excerpt = strip_dashes(html.unescape(re.sub(r"\s+", " ", excerpt)).strip())
    index.append((date, meta, excerpt, cover_src))

# ---------------------------------------------------------------- index page
index.sort(key=lambda t: t[0], reverse=True)
cards = []
for n, (d, m, ex, cov) in enumerate(index):
    img = (f'<img src="{cov}" alt="" loading="lazy" width="1600" height="1000">' if cov else "")
    delay = f' style="--d:{n * 80}ms"' if n else ""
    cards.append(f"""        <a class="card post rise" href="{m['slug']}.html"{delay}>
          {img}
          <div class="post__b">
            <time datetime="{d}">{m['kicker']} · {pretty(d)}</time>
            <h3>{m['title']}</h3>
            <p>{html.escape(m['desc'], quote=False)}</p>
            <span class="arrowlink">Read the article {ARROW}</span>
          </div>
        </a>""")

body_html = f"""
  <section class="sec dark glow gridbg phero" aria-labelledby="ins-h">
    <div class="wrap">
      <p class="eyebrow lift" style="--d:40ms">{SPARK}Insights</p>
      <h1 id="ins-h" class="lift" style="--d:120ms">What we've learned,<br><span class="grad">written down.</span></h1>
      <p class="lede lift" style="--d:240ms">
        Field notes on authority, partnerships, and the parts of the coaching industry that
        don't make it into anyone's sales page. Written by the people doing the work.
      </p>
    </div>
  </section>

  <section class="sec light" aria-label="Articles">
    <div class="wrap">
      <div class="grid">
{chr(10).join(cards)}
      </div>
    </div>
  </section>

  <section class="sec dark glow glow--low cta" aria-labelledby="cta-h">
    <div class="wrap rise">
      <p class="eyebrow">{SPARK}Ready when you are</p>
      <h2 id="cta-h">Prefer the short version,<br><span class="grad">out loud?</span></h2>
      <p class="lede">Book fifteen minutes and we'll apply all of this to your specific situation instead.</p>
      <div class="cta-row" style="justify-content:center;margin-top:34px">
        <a class="btn" href="{CAL}">Book a 15-min call {ARROW}</a>
        <a class="btn btn--ghost" href="services.html">See the services</a>
      </div>
    </div>
  </section>
"""

out = page("Insights | Rogue Coach Teams",
           "Field notes on authority building, joint ventures and the coaching-agency playbook, "
           "written by the people doing the work.",
           "insights.html", body_html)
io.open(os.path.join(SITE, "insights.html"), "w", encoding="utf8", newline="\n").write(out)
print(f"wrote insights.html, {len(index)} articles")
