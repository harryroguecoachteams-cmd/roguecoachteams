"""Long-form sales page for the 90-day sprint. Not linked from the site nav or footer,
marked noindex: it is the page Rogue Coach Teams sends in outreach.

Edit the copy here, then:  python _build/gen_offer.py   (writes offer.html)
"""
import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chrome
from chrome import CAL, icon

GUARANTEE_PCT = "100%"        # confirmed by Harsh 30 Sep 2026: 100% money-back guarantee
LEADS = "200"
YT_VALUE = "$900+"

def li(items):
    return "\n".join(f"            <li>{x}</li>" for x in items)

def item(n, ico, title, what, gets, why, d=0):
    dl = f' style="--d:{d}ms"' if d else ""
    return f"""
        <article class="card item rise"{dl}>
          <div class="item__n">{n:02d}</div>
          <span class="ico">{icon(ico)}</span>
          <h3>{title}</h3>
          <p>{what}</p>
          <p class="kicker" style="margin-top:18px">What you get</p>
          <ul class="ticks">
{li(gets)}
          </ul>
          <p class="item__why"><b>Why it matters.</b> {why}</p>
        </article>"""

ITEMS = [
 ("layout", "Your website, built for booked calls",
  "A clean, fast site written and designed around your offer. Not a template with your logo on it.",
  ["Home, about, offer, blog and contact pages, written for you",
   "Mobile-friendly, search-ready and connected to your calendar",
   "Opt-in and email list wired in from day one",
   "Every login and file handed over to you"],
  "People check you out before they book. If the site is weak, every other effort leaks."),
 ("target", "Offer and positioning workshop",
  "A 45 to 60 minute kickoff where we pin down who you help, what you sell and how you say it.",
  ["A sharpened offer and niche statement",
   "Your voice, topics and messaging pillars in a short brand mini-kit",
   "Targets for calls and leads, plus a short backlog for the 90 days"],
  "Everything after this is built on it. Vague offers get vague results."),
 ("funnel", "Lead magnet and funnel",
  "A free resource that earns the email address, and the pages that turn a visitor into a conversation.",
  ["Lead magnet: outline, copy and design",
   "Opt-in page and thank-you page",
   "Booking step connected to your calendar",
   "Tracking so you can see what converts"],
  "Traffic without a funnel is just noise. This is where strangers become leads."),
 ("mail", "Email sequences",
  "Emails written in your voice that warm people up and invite them to book.",
  ["A nurture sequence and a pitch sequence, written and scheduled",
   "Automations for follow-up and reminders",
   "Monthly tuning based on opens, clicks and replies"],
  "Most buyers are not ready on day one. Email is how you stay in the room until they are."),
 ("play", "Video editing (our specialty)",
  "You record, we edit. Long-form video turned into polished clips and posts, on schedule.",
  ["Long-form video edited: cuts, captions, sound clean-up, thumbnails",
   "Short clips and reels cut from the same recording",
   "Ready to post on YouTube, LinkedIn and Instagram"],
  "Video is the fastest way to build trust, and it is the part most coaches never finish. We finish it for you."),
 ("megaphone", "Social media posting",
  "A steady authority presence on LinkedIn and Instagram without you living on the apps.",
  ["Posts, story graphics and captions written and designed for you",
   "Posting and scheduling handled",
   "A cadence you can hold, repurposed to multiply reach"],
  "Consistency is what makes people remember you. We keep it going while you coach."),
 ("mic", "Podcast interviews and features",
  "We pitch you to podcast hosts and publications so your expertise reaches audiences that already trust someone else.",
  ["A target list of shows and outlets that fit your niche",
   "Pitch emails and your guest one-sheet written for you",
   "Outreach, follow-ups and booking handled",
   "Prep notes before each interview"],
  "A single good interview puts you in front of an audience you would spend months building yourself."),
 ("link", "Joint venture partnerships",
  "A joint venture (JV) is when someone with your ideal audience promotes your offer to it. We find them and open the door.",
  ["A shortlist of partners who serve the same people you do",
   "Outreach scripts and warm introductions",
   "Partnership calls and follow-ups managed for you"],
  "Partners bring warm, pre-sold leads. It is the quickest route to a full calendar without ad spend."),
 ("zap", "Automations and tech setup",
  "The plumbing that makes everything run without you babysitting it.",
  ["Calendar, forms, email and CRM connected",
   "Light tech assistance and checks before go-live",
   "Simple how-to guides for the parts you will touch"],
  "Leads that fall through the cracks cost more than any tool. This closes the cracks."),
 ("pulse", "Weekly iteration and monthly reporting",
  "We ship weekly, review what is working and change what is not.",
  ["Edits turned around in 24 to 48 hours",
   "A monthly report in plain English",
   "Regular check-ins so you always know where things stand"],
  "The first version is never the best one. Fast tuning is what compounds results."),
 ("package", "Handover, so you own it all",
  "At the end you keep everything and can run it without us.",
  ["Every file, login and asset in your name",
   "Handover guides for each system",
   "A 30-day support window after the 90 days"],
  "We are not building something you have to rent from us. You own your assets."),
]

items_html = "".join(item(i + 1, ico, t, w, g, y, (i % 2) * 80) for i, (ico, t, w, g, y) in enumerate(ITEMS))

PAY = {"Starter": "https://www.paypal.com/ncp/payment/4Q5NZZP7S2XRS",
       "Growth": "https://www.paypal.com/ncp/payment/4J6W58KC66ZNL",
       "All-in-one": "https://www.paypal.com/ncp/payment/FFKADUKFFGGMJ"}


def tier(name, sub, price, feat, points, btn_ghost):
    cls = " tier--feat" if feat else ""
    badge = '<span class="badge">Most chosen</span>' if feat else ""
    b = "btn btn--ghost btn--wide" if btn_ghost else "btn btn--wide"
    return f"""
        <article class="card tier{cls} rise">
          <div class="tier__top"><h3>{name}</h3>{badge}</div>
          <p class="tier__sub">{sub}</p>
          <div class="tier__price">{price}</div>
          <p class="tier__per">One payment · 90 days</p>
          <ul class="ticks">
{li(points)}
          </ul>
          <a class="{b}" href="{PAY[name]}" rel="noopener">Buy {name}, {price} {icon('arrow')}</a>
          <p class="tier__note">Secure checkout on PayPal. <a class="tlink" href="{CAL}">Prefer to talk first? Book a call.</a></p>
        </article>"""

TIERS = (
  tier("Starter", "Get visible and launch", "$897", False,
       ["Social media authority: 45 posts across LinkedIn and Instagram",
        "Video editing of your long-form video into short clips",
        "Lead magnet funnel and 5 nurture emails",
        "5-page website included",
        "Unlimited edits, 48-hour turnaround, monthly report"], True)
  + tier("Growth", "Leads on demand", "$1,797", True,
         ["Everything in Starter, scaled up: 60 posts, sales funnel, 7-email sequence",
          "Video editing: short clips plus long-form edits",
          "Podcast interviews and partner outreach: 30 warm leads, handled for you",
          "Launch planning, priority 24 to 48 hour turnaround",
          "5-page website in the first 90 days, if needed"], False)
  + tier("All-in-one", "Done-for-you growth team", "$3,600", False,
         ["Premium social: 90 posts, reels and weekly stories",
          "Full video editing, long-form and short-form",
          "Advanced funnels and 10+ email automations",
          "Podcast and partner lead flow: 45 warm leads, plus partnership management",
          "2 full launch campaigns, monthly growth calls, quarterly roadmap"], True)
)

FAQ = [
 ("Why do you ask for 90 days?",
  "Because that is how long the system takes to build and start showing up. We build your website, offer, lead magnet, funnel and email sequences, then start posting and reaching out on top of that. Nobody can honestly promise results in 30 days. In 90 days, we can."),
 ("What happens after the 90 days?",
  "You choose. 90 days is the minimum we ask for. After that you can continue with us month to month, with no long commitment, or take everything and run it yourself."),
 ("What does the lead promise mean?",
  f"We commit to delivering {LEADS} leads for your business within the 90 days, sized to your niche and offer, through our podcast and joint venture partners. On the call we will confirm what counts as a lead for you, so the promise is clear on both sides."),
 ("What is the guarantee?",
  f"If we do not deliver what this page promises within the 90 days, you get a {GUARANTEE_PCT} money-back refund. We are asking for your commitment, so we put ours in writing."),
 ("Do I need a website already?", "No. A website is included. If you already have one, we improve it instead of rebuilding it."),
 ("How much of my time does it need?", "A kickoff workshop of 45 to 60 minutes, a short weekly check-in, and recording your videos. We handle the rest."),
 ("Do I own everything?", "Yes. Every file, login and asset is yours at handover."),
]
faq_html = "\n".join(f"""        <details>
          <summary>{q}</summary>
          <div class="acc__a">{a}</div>
        </details>""" for q, a in FAQ)

BODY = f"""
  <section class="sec dark glow gridbg phero phero--split" aria-labelledby="offer-h">
    <div class="wrap">
      <div class="inner">
        <div>
          <p class="eyebrow lift" style="--d:40ms">{icon('spark')}The 90-day sprint</p>
          <h1 id="offer-h" class="lift" style="--d:120ms">A full growth system<br><span class="grad">in 90 days.</span></h1>
          <p class="lede lift" style="--d:240ms">
            Website, funnel, video editing, social, podcast interviews and partner outreach, built and
            run for you in 90 days. Plus {LEADS} leads delivered, and a refund guarantee if we fall short.
          </p>
          <div class="cta-row lift" style="--d:340ms">
            <a class="btn" href="{CAL}">Book a 15-min call {icon('arrow')}</a>
            <a class="btn btn--ghost" href="#included">See everything included {icon('arrow-down')}</a>
          </div>
        </div>
        <div class="card card--gold glance lift" style="--d:440ms">
          <p class="kicker">At a glance</p>
          <ul class="ticks">
            <li><strong>From $897</strong>, one payment, 90 days</li>
            <li><strong>{LEADS} leads</strong> delivered in 90 days</li>
            <li><strong>{GUARANTEE_PCT} money-back guarantee</strong> if we do not deliver</li>
            <li><strong>Video editing included</strong>, our specialty</li>
            <li><strong>You own everything</strong> at handover</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <section class="sec light" id="why90" aria-labelledby="why90-h">
    <div class="wrap">
      <div class="head rise">
        <p class="eyebrow">{icon('spark')}Why 90 days</p>
        <h2 id="why90-h">Nobody delivers results in 30 days.<br><span class="grad">We can in 90.</span></h2>
        <p class="lede">
          This is the minimum commitment we ask for, and here is the honest reason. A real growth
          system is several things that have to be built in order, then given time to be seen.
        </p>
      </div>
      <div class="grid">
        <article class="card rise">
          <span class="pill">Weeks 1 to 4</span>
          <h3>We build the foundation</h3>
          <ul class="ticks">
            <li>Your website and your offer</li>
            <li>Your lead magnet, funnel and email sequences</li>
            <li>Tracking and automations</li>
          </ul>
        </article>
        <article class="card rise" style="--d:80ms">
          <span class="pill">Weeks 5 to 8</span>
          <h3>We start showing up</h3>
          <ul class="ticks">
            <li>Video, social posts and email going out every week</li>
            <li>Podcast pitches and partner outreach begin</li>
            <li>First interviews and conversations land</li>
          </ul>
        </article>
        <article class="card rise" style="--d:160ms">
          <span class="pill">Weeks 9 to 12</span>
          <h3>It compounds</h3>
          <ul class="ticks">
            <li>Everything working together, visible and searchable</li>
            <li>Leads and booked calls arriving</li>
            <li>Tuning what works, then handover</li>
          </ul>
        </article>
      </div>
      <p class="rise" style="margin:32px auto 0;max-width:68ch;text-align:center;font-size:1.05rem">
        <b>After the 90 days you are free to go.</b> If you want to keep going with us, you can
        continue month to month. No long contract, no lock-in.
      </p>
    </div>
  </section>

  <section class="sec dark glow glow--side" id="included" aria-labelledby="included-h">
    <div class="wrap">
      <div class="head rise">
        <p class="eyebrow">{icon('spark')}Everything included</p>
        <h2 id="included-h">Every line item,<br><span class="grad">explained.</span></h2>
        <p class="lede">What each part is, exactly what you get, and why it is in the package.</p>
      </div>
      <div class="grid grid--2 items">{items_html}
      </div>
    </div>
  </section>

  <section class="sec light" id="bonuses" aria-labelledby="bonus-h">
    <div class="wrap">
      <div class="head rise">
        <p class="eyebrow">{icon('spark')}Fast-action bonuses</p>
        <h2 id="bonus-h">Start this month and<br><span class="grad">get two bonuses.</span></h2>
      </div>
      <div class="grid grid--2">
        <article class="card card--gold rise">
          <span class="badge">Bonus 1 &middot; worth {YT_VALUE}</span>
          <span class="ico" style="margin:18px 0">{icon('play')}</span>
          <h3>YouTube launch pack</h3>
          <p>We turn your long-form video into a channel that is ready to post, free.</p>
          <ul class="ticks">
            <li>Your long-form videos edited and finished</li>
            <li>Shorts cut from the same recordings</li>
            <li>A full 90-day content schedule, ready to follow</li>
          </ul>
        </article>
        <article class="card card--gold rise" style="--d:80ms">
          <span class="badge">Bonus 2 &middot; the lead promise</span>
          <span class="ico" style="margin:18px 0">{icon('target')}</span>
          <h3>{LEADS} leads in 90 days</h3>
          <p>We do not only build the system, we fill it. Through our podcast and joint venture
            partners we deliver {LEADS} leads for your business within the 90 days, sized to your niche
            and offer.</p>
        </article>
      </div>
    </div>
  </section>

  <section class="sec dark glow" id="guarantee" aria-labelledby="guar-h">
    <div class="wrap" style="max-width:860px">
      <div class="head rise" style="text-align:center;margin-inline:auto">
        <p class="eyebrow">{icon('shield')}Our guarantee</p>
        <h2 id="guar-h">We ask for 90 days.<br><span class="grad">We put ours on the line.</span></h2>
        <p class="lede">
          If we do not deliver what is promised on this page within the 90 days, you get a
          {GUARANTEE_PCT} refund. You are committing your time and your money. We commit to the result.
        </p>
      </div>
    </div>
  </section>

  <section class="sec light" id="packages" aria-labelledby="pk-h">
    <div class="wrap">
      <div class="head rise">
        <p class="eyebrow">{icon('spark')}Pick your package</p>
        <h2 id="pk-h">Same playbook.<br><span class="grad">Choose the scope.</span></h2>
        <p class="lede">One payment, 90 days, then month to month if you want more. All three carry the guarantee and both bonuses.</p>
      </div>
      <div class="tiers">{TIERS}
      </div>
      <p class="tiny rise" style="margin:32px auto 0;max-width:74ch;text-align:center">
        Not sure which one? Book the 15-minute call and we will tell you the smallest package that
        gets you what you want.
      </p>
    </div>
  </section>

  <section class="sec light light--2" aria-labelledby="faq-h">
    <div class="wrap faqs">
      <div class="faqs__side rise">
        <p class="eyebrow">{icon('spark')}FAQ</p>
        <h2 id="faq-h">Before<br><span class="grad">you decide.</span></h2>
        <div class="advice">
          <b>Rather ask a person?</b>
          <p>Fifteen minutes, no pitch.</p>
          <a class="arrowlink" href="{CAL}">Book a 15-min call {icon('arrow')}</a>
        </div>
      </div>
      <div class="acc rise" style="--d:100ms">
{faq_html}
      </div>
    </div>
  </section>

  <section class="sec dark glow glow--low cta" aria-labelledby="cta-h">
    <div class="wrap">
      <div class="rise">
        <p class="eyebrow">{icon('spark')}Ready when you are</p>
        <h2 id="cta-h">Let's build it<br><span class="grad">in 90 days.</span></h2>
        <p class="lede">Fifteen minutes with the people who would do the work. We will tell you honestly whether the sprint fits.</p>
        <div class="cta-row" style="margin-top:32px">
          <a class="btn" href="{CAL}">Book a 15-min call {icon('arrow')}</a>
        </div>
      </div>
    </div>
  </section>
"""

TITLE = "The 90-day sprint | Rogue Coach Teams"
DESC = "Website, funnel, video editing, social, podcast interviews and partner outreach, built for you in 90 days, with leads delivered and a refund guarantee."

out = chrome.page(TITLE, DESC, "offer.html", BODY, noindex=True)
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "offer.html")
io.open(path, "w", encoding="utf8", newline="\n").write(out)
print("wrote offer.html", len(out), "bytes")
