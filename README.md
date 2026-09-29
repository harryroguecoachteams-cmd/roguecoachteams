# Rogue Coach Teams, website (v2 redesign)

A static build of roguecoachteams.com. Plain HTML, CSS and vanilla JS: no
framework, no npm. Open any `.html` file over http and it runs.

**v2** (branch `redesign`, September 2026) keeps every page, link, price and
checkout from v1 and changes the layout language, modelled on the structure of
shinrustudio.com but kept on the RCT brand:

- a floating pill nav, detached from the top of the page
- bands that alternate between Midnight `#0B0F1A` and a warm paper `#F8F6F1`
- mono eyebrow chips, and one gold-to-orange gradient line in every heading
- real client sites shown in browser frames (the fanned hero, the gallery,
  Maria's before and after)
- one timeline card for the five-step engine, numbered problem cards,
  outcome cards, FAQ accordion cards and a two-card closing CTA

Brand guidelines v1.0 still rule: Inter / Inter Tight, Gold `#FBBF24`, pill
buttons, 20 to 28px radii, soft gold glow instead of hard shadows. On the light
bands the accent drops to amber `#A84D08` so text stays above WCAG AA.

---

## The domain

`roguecoachteams.com` still serves the old WordPress site from `209.74.67.50`.
Nothing here is live on the domain until DNS is pointed at GitHub Pages. In
the DNS panel for the domain:

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
| `index.html` | Home: hero with three client sites, the problem, the engine, Maria's video and before/after, work gallery, three lanes, two ways to start, the crew, client words, FAQ |
| `about.html` | The layoff story, the first meetup, eight principles, mission, the team, the promise |
| `services.html` | The two paths, why this crew, how the work runs, FAQ |
| `sprint.html` | The 90-day sprint, timeline, three packages with live PayPal checkout |
| `pricing.html` | Twelve fixed-price services, filterable, each with checkout (generated) |
| `contact.html` | Contact form plus the Calendly route |
| `insights.html` | Article index (generated) |
| `coaching-scams.html`, `authority-building-for-coaches.html`, `joint-ventures-for-coaches.html` | The three posts, ported from WordPress (generated) |

## How the files fit together

| File | Role |
|---|---|
| `assets/css/site.css` | The whole design system. Components read colours from the band they sit in (`.dark` / `.light`), so one card works on both. |
| `assets/icons.svg` | Line-icon sprite, used as `<svg class="i"><use href="assets/icons.svg#name"/></svg>` |
| `assets/js/site.js` | Nav, drawer, scroll reveals, count-ups, video, filters, contact form |
| `assets/img/v2/` | Hero fan crops, Maria's before/after, the logo mark |
| `_build/chrome.py` | The shared `<head>`, nav, drawer and footer. Single source for all pages. |
| `_build/apply_chrome.py` | Rewrites the `<!-- @head -->`, `<!-- @header -->`, `<!-- @footer -->` blocks in the hand-written pages |
| `_build/gen_pricing.py` | Builds `pricing.html` from the price table |
| `_build/gen_articles.py` | Builds the 3 articles and `insights.html` from `_build/posts.json` |

## Regenerating

```bash
python _build/apply_chrome.py   # after editing the nav or footer in chrome.py
python _build/gen_pricing.py    # after editing prices or PayPal links
python _build/gen_articles.py   # after editing posts.json or the article template
```

Edit `index.html`, `about.html`, `services.html`, `sprint.html` and
`contact.html` directly, but only outside the marked chrome blocks. Never
hand-edit `pricing.html`, `insights.html` or the three article pages.

## Live integrations

**Calendly.** Every "Book a call" points at
`https://calendly.com/roguecoachteams/rebel-strategy-call`.

**PayPal.** Checkout uses PayPal's no-code payment links, one per product. They
open PayPal's own hosted checkout, so no client id, SDK or secret is in the page.

| Product | Price | Link id |
|---|---|---|
| Sprint, Starter | $900 | `4Q5NZZP7S2XRS` |
| Sprint, Growth | $1,800 | `4J6W58KC66ZNL` |
| Sprint, All-in-one | $3,600 | `FFKADUKFFGGMJ` |
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

**Contact form.** Composes the enquiry and opens the visitor's mail client, so
it works with no backend and cannot silently drop a lead. To send in the
background instead, deploy `_setup/lead-endpoint.gs` as an Apps Script web app
and put the `/exec` URL into `LEAD_ENDPOINT` in `assets/js/site.js`.

## Known follow-ups

- **PayPal business name still reads "Rouge Coach Teams"** on checkout and
  receipts. That is a typo in the PayPal account settings, fixable only from
  the PayPal dashboard.
- The three short text testimonials on the home page (Maya R., Elena P.,
  David K.) were carried over from the old site. Maria's is the only one with a
  verifiable source. Confirm or replace them before go-live.

## Checking it before you ship

Serve the folder over http, open any page, then in the browser console:

```js
const src = await (await fetch('_build/audit.js')).text(); (0, eval)(src);
await audit.responsive();   // pages x widths overflow probes
await audit.contrast();     // every text node, WCAG AA
```

`audit.contrast()` reports gradient heading text (`.grad`) as a failure because
its colour is transparent; the gradient itself is 7:1 or better on midnight and
4.7:1 or better on paper.

## How the motion works

- **The signal line** is the signature carried over from v1: a flat, dashed,
  silent stretch that finds a rhythm and climbs. It draws once above the
  problem cards and once above the closing CTA.
- **The hero fan**: three client sites dealt in on load.
- **One reveal pattern** (`.rise`) for scroll entrances, fired once through a
  single IntersectionObserver at `threshold: 0`.
- **Gallery frames** scroll their screenshot on hover.

Every hidden state is scoped to `html.js`, and the inline script in each
`<head>` removes that class again if `site.js` has not run within 2.5 seconds,
so a blocked script degrades to a fully visible page. `prefers-reduced-motion`
disables all of it.
