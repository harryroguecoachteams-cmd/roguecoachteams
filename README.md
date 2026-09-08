# Rogue Coach Teams — website

A static rebuild of roguecoachteams.com. Plain HTML, CSS and vanilla JS — no
framework, no build step, no npm. Open any `.html` file over http and it runs.

Built to the **Rogue Coach Teams Brand Guidelines v1.0**: Midnight `#0B0F1A` and
Graphite `#151A23` surfaces, Gold `#FBBF24` accent, Inter, pill buttons, 20–24px
radii and soft gold glows instead of hard shadows.

---

## ⚠️ The domain is currently parked

As of 7 September 2026 the nameservers for `roguecoachteams.com` point at
GoDaddy (`NS29/NS30.DOMAINCONTROL.COM`) and the domain resolves to a GoDaddy
parking lander. **Visitors see a parking page, not the site.**

The old WordPress install is untouched and still served by the origin host at
`209.74.67.50`, with a valid SSL.com certificate through March 2027. Nothing was
lost — only DNS changed.

To point the domain at this site once it is deployed to GitHub Pages, in the
GoDaddy DNS panel:

| Type  | Name  | Value                                  |
|-------|-------|----------------------------------------|
| A     | `@`   | `185.199.108.153`                      |
| A     | `@`   | `185.199.109.153`                      |
| A     | `@`   | `185.199.110.153`                      |
| A     | `@`   | `185.199.111.153`                      |
| CNAME | `www` | `<owner>.github.io`                    |

Then add a `CNAME` file containing `roguecoachteams.com` at the repo root and
enable **Enforce HTTPS** in the repo's Pages settings.

---

## Pages

| File | What it is |
|---|---|
| `index.html` | Home — hero, Maria's video testimonial, the 5-step engine, work, services, pricing summary, FAQ |
| `about.html` | The layoff story, principles, mission, the seven-person crew |
| `services.html` | The two ways to start, and how the work runs |
| `sprint.html` | The 90-day sprint, three packages with live PayPal checkout |
| `pricing.html` | Twelve individual fixed-price services, filterable, each with checkout |
| `contact.html` | Contact form plus the Calendly booking route |
| `insights.html` | Article index |
| `coaching-scams.html`, `authority-building-for-coaches.html`, `joint-ventures-for-coaches.html` | The three posts, ported from WordPress |

## Live integrations

**Calendly** — every "Book a 15-min call" points at
`https://calendly.com/roguecoachteams/rebel-strategy-call`.

**PayPal** — checkout uses PayPal's no-code payment links, one per product.
Every link below returned HTTP 200 when this site was built. They open PayPal's
own hosted checkout, so no client id, SDK or secret is exposed in the page.

| Product | Price | Link id |
|---|---|---|
| Sprint — Starter | $900 | `4Q5NZZP7S2XRS` |
| Sprint — Growth | $1,800 | `4J6W58KC66ZNL` |
| Sprint — All-in-one | $3,600 | `FFKADUKFFGGMJ` |
| Lead generation | $99 | `S2QFSV3EMCFNW` |
| Branding | $149 | `DJSY3VC97ER8E` |
| Community & engagement | $149 | `F4ASTDHPEMTHQ` |
| Funnel page | $199 | `ED99CV55L2UYS` |
| Marketing & SEO | $199 | `HXVTF2A2R34NU` |
| Social media growth | $249 | `FW8EDE63LV366` |
| Automation systems | $249 | `P6HRFDW67YKFU` |
| Coaching website | $299 | `C6XU2T7NSPCUG` |
| Authority & PR | $299 | `SUYLTUARJ9GPG` |
| Course / membership setup | $299 | `V3WNJ79DYABSL` |
| Podcast launch | $299 (was $349) | `94BW74KEDTTN2` |
| Book publishing | $699 | `XFSKVB5G8SVDU` |

Re-check any of them with:

```bash
curl -sLo /dev/null -w '%{http_code}\n' https://www.paypal.com/ncp/payment/<id>
```

Prices and links live in one place — `_build/gen_pricing.py`. Edit there and
re-run it rather than hand-editing `pricing.html`.

**Contact form** — currently composes the enquiry and opens the visitor's mail
client, so it works with no backend and cannot silently drop a lead. To make it
send in the background instead, deploy `_setup/lead-endpoint.gs` as an Apps
Script web app and put the `/exec` URL into `LEAD_ENDPOINT` at the top of the
contact-form section in `assets/js/site.js`. The existing "RCT payments log"
script cannot be used as-is: it implements `doGet` only and returns 405 on POST.

## Known follow-ups

- **PayPal business name still reads "Rouge Coach Teams"** on checkout and
  receipts. That is a typo in the PayPal account settings, not in this code, and
  it can only be fixed from the PayPal dashboard.
- The three short text testimonials on the home page (Maya R., Elena P.,
  David K.) were carried over from the old site. Maria's is the only one with a
  verifiable source attached. Worth confirming or replacing them.

## Regenerating

```bash
python _build/gen_pricing.py    # rewrites pricing.html from the price table
python _build/gen_articles.py   # rewrites the 3 articles + insights.html
```

`_build/posts.json` is the WordPress REST payload the articles are built from.

## Checking it before you ship

Serve the folder over http, open any page, then in the browser console:

```js
const src = await (await fetch('_build/audit.js')).text(); (0, eval)(src);
await audit.responsive();   // 120 probes: 10 pages x 12 widths
await audit.contrast();     // every text node, WCAG AA
```

`audit.js` keeps its own hand-maintained `PAGES` list. **Add every new page to
it in the same commit that creates the page**, and check the probe count in the
output against pages × widths before trusting a clean result.

## How the motion works

One idea, used deliberately rather than everywhere:

- **The signal line** is the signature. A flat, dashed, silent stretch that
  finds a rhythm and then climbs — a coach's visibility over time. It draws
  itself once in the hero on load, and once more above the closing CTA on
  scroll. Nothing else on the site animates a path.
- **One reveal pattern** (`.rise`) for scroll entrances, fired once, via a
  single IntersectionObserver at `threshold: 0` — a fractional threshold never
  fires for elements taller than the viewport.
- **A hero load sequence** (`.lift`) staggered with a `--d` custom property.
- Count-ups, hover lifts, and the accordion. That is the whole list.

Every hidden state is scoped to `html.js`, and the inline script in each
`<head>` removes that class again if `site.js` has not run within 2.5 seconds.
So a blocked or broken script degrades to a plain, fully visible page rather
than a blank one. `prefers-reduced-motion: reduce` disables all of it.
