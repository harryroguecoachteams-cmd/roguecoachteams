"""Package the static site for the existing WordPress install at roguecoachteams.com.

The live site keeps its WordPress URLs (slugs). Each new page is served from a prebuilt
HTML file by the mu-plugin _wp/rct-static-pages.php; this script rewrites the file names
to the WordPress slugs and moves assets under /rct-v2/.

    python _build/wpbuild.py            -> _wp/rct-v2.zip  (pages/ + assets/, extract into public_html)
    python _build/wpbuild.py --offer    -> also includes offer.html at /offer/
"""
import io
import os
import re
import shutil
import sys
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "_wp")
SITE = "https://roguecoachteams.com"
BASE = "/rct-v2"

# static file -> WordPress path (unchanged from the current live site)
MAP = {
    "index.html": "/",
    "services.html": "/services/",
    "sprint.html": "/services/90-day-sprint/",
    "pricing.html": "/services/individual-pricing/",
    "about.html": "/about-us/",
    "contact.html": "/contact-us/",
    "insights.html": "/blog/",
    "coaching-scams.html": "/coaching-scams/",
    "authority-building-for-coaches.html": "/authority-building-for-coaches/",
    "joint-ventures-for-coaches.html": "/joint-ventures-for-coaches/",
}
if "--offer" in sys.argv:
    MAP["offer.html"] = "/offer/"

LINK = re.compile(r'(href|content)="((?:%s)?/?)([a-z0-9-]+\.html)(#[^"]*)?"' % re.escape(SITE))


def fix_links(t):
    def rep(m):
        attr, pre, name, frag = m.group(1), m.group(2), m.group(3), m.group(4) or ""
        if name not in MAP and name != "offer.html":
            return m.group(0)
        path = MAP.get(name, "/offer/")
        if pre.startswith("http"):
            return '%s="%s%s%s"' % (attr, SITE, path, frag)
        if attr == "content":
            return m.group(0)
        return '%s="%s%s"' % (attr, path, frag)
    t = LINK.sub(rep, t)
    # assets: relative and absolute
    t = t.replace(SITE + "/assets/", SITE + BASE + "/assets/")
    t = re.sub(r'(?<![\w/.:-])assets/', BASE + "/assets/", t)
    return t


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    pages = os.path.join(OUT, "rct-v2", "pages")
    os.makedirs(pages)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "rct-v2", "assets"))
    left = []
    for name in MAP:
        src = io.open(os.path.join(ROOT, name), encoding="utf8").read()
        out = fix_links(src)
        for m in re.finditer(r'(?:href|src)="([^"]*\.html[^"]*)"', out):
            if not m.group(1).startswith("http") or SITE in m.group(1):
                left.append((name, m.group(1)))
        io.open(os.path.join(pages, name), "w", encoding="utf8", newline="\n").write(out)
    if left:
        print("UNMAPPED LINKS:", left[:10])
    zpath = os.path.join(OUT, "rct-v2.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, _, fs in os.walk(os.path.join(OUT, "rct-v2")):
            for f in fs:
                full = os.path.join(dp, f)
                z.write(full, os.path.relpath(full, OUT).replace("\\", "/"))
    print("built", len(MAP), "pages ->", zpath, round(os.path.getsize(zpath) / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
