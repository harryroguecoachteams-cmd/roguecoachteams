"""Refresh the shared head, nav and footer inside every hand-written page.

The hand-written pages are the source of truth for their own content. Only the
blocks between these markers are rewritten, from chrome.py:
    <!-- @head --> ... <!-- /@head -->       (title and description are kept)
    <!-- @header --> ... <!-- /@header -->
    <!-- @footer --> ... <!-- /@footer -->

Run:  python _build/apply_chrome.py
"""
import html
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chrome  # noqa: E402

SITE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PAGES = ["index.html", "about.html", "services.html", "sprint.html", "contact.html", "offer.html"]


def block(name, text, new):
    pat = re.compile(r"(<!-- @%s -->)\s*.*?\s*(<!-- /@%s -->)" % (name, name), re.S)
    if not pat.search(text):
        raise SystemExit(f"missing @{name} markers")
    return pat.sub(lambda m: m.group(1) + "\n" + new + "\n" + m.group(2), text, count=1)


for name in PAGES:
    path = os.path.join(SITE, name)
    src = io.open(path, encoding="utf8").read()
    title = html.unescape(re.search(r"<title>(.*?)</title>", src, re.S).group(1))
    desc = html.unescape(re.search(r'<meta name="description" content="(.*?)">', src, re.S).group(1))
    img = re.search(r'<meta property="og:image" content="https://roguecoachteams.com/(.*?)">', src)
    img = img.group(1) if img else "assets/img/v2/fan-center.webp"
    out = block("head", src, chrome.head(html.escape(title, quote=False),
                                         html.escape(desc, quote=True), name, img,
                                         noindex='content="noindex' in src))
    out = block("header", out, chrome.HEADER)
    out = block("footer", out, chrome.FOOTER)
    if out != src:
        io.open(path, "w", encoding="utf8", newline="\n").write(out)
        print("updated", name)
    else:
        print("unchanged", name)
