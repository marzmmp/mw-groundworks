#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the M&W GroundWorks static site."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from content import (BIZ, SERVICES, FAMILIES, TOWNS_KEY, TOWNS_MORE, TOWNS_EDGE,
                     CALENDAR, MONTHS, FAQ, PROCESS, CLIENT_TODO)
from icons import ico

ROOT = os.path.join(os.path.dirname(__file__), "..", "website")
TEL = BIZ["phone_display"]
TELH = "tel:" + BIZ["phone_href"]
SMS = "sms:" + BIZ["phone_href"]

NAV = [("index.html", "Home"), ("services.html", "Services"),
       ("work.html", "Our Work"), ("service-area.html", "Service Area"),
       ("about.html", "About"), ("logos.html", "Brand")]


# ────────────────────────────────────────────────────────────── schema
def ld_business():
    return {
        "@context": "https://schema.org",
        "@type": ["GeneralContractor", "LocalBusiness"],
        "@id": BIZ["url"] + "/#business",
        "additionalType": "https://en.wikipedia.org/wiki/Landscaping",
        "name": BIZ["name"],
        "url": BIZ["url"] + "/",
        "logo": BIZ["url"] + "/assets/logos/01-groundline-badge.svg",
        "image": BIZ["url"] + "/assets/logos/02-the-cut.svg",
        "description": ("Land clearing, brush clearing, retaining walls, masonry, decks, "
                        "junk removal, mowing and property maintenance across Jefferson "
                        "County, Missouri."),
        "telephone": BIZ["phone_e164"],
        "priceRange": "$$",
        "address": {"@type": "PostalAddress", "addressRegion": "MO",
                    "addressLocality": BIZ["seat"], "addressCountry": "US"},
        "areaServed": ([{"@type": "AdministrativeArea",
                         "name": "Jefferson County, Missouri"}]
                       + [{"@type": "City", "name": t} for t in TOWNS_KEY]),
        "serviceArea": {"@type": "GeoCircle",
                        "geoMidpoint": {"@type": "GeoCoordinates",
                                        "latitude": 38.2306, "longitude": -90.5626},
                        "geoRadius": "48280"},
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday",
                          "Friday", "Saturday"],
            "opens": "07:00", "closes": "18:00"}],
        "hasOfferCatalog": {
            "@type": "OfferCatalog", "name": "Land & Property Services",
            "itemListElement": [
                {"@type": "Offer",
                 "itemOffered": {"@type": "Service", "name": s["name"]}}
                for s in SERVICES]},
    }


def ld_service(s):
    return {
        "@context": "https://schema.org", "@type": "Service",
        "@id": f"{BIZ['url']}/services.html#{s['slug']}",
        "serviceType": s["name"],
        "name": f"{s['name']} in Jefferson County, MO",
        "description": s["short"],
        "provider": {"@id": BIZ["url"] + "/#business"},
        "areaServed": {"@type": "AdministrativeArea",
                       "name": "Jefferson County, Missouri"},
    }


def ld_breadcrumb(page, label):
    items = [{"@type": "ListItem", "position": 1, "name": "Home",
              "item": BIZ["url"] + "/"}]
    if page != "index.html":
        items.append({"@type": "ListItem", "position": 2, "name": label,
                      "item": f"{BIZ['url']}/{page}"})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": items}


def ld_faq():
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}}
                           for q, a in FAQ]}


# ────────────────────────────────────────────────────────────── shell
def head(page, title, desc, extra_ld=None):
    lds = [ld_business(), ld_breadcrumb(page, title)]
    if extra_ld:
        lds.extend(extra_ld)
    blocks = "".join(
        f'<script type="application/ld+json">{json.dumps(x, separators=(",", ":"))}</script>'
        for x in lds)
    full = f"{title} | {BIZ['name']}" if page != "index.html" else \
        f"{BIZ['name']} — Land Clearing, Retaining Walls & Property Services | Jefferson County, MO"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0B0F0C">
<link rel="canonical" href="{BIZ['url']}/{'' if page == 'index.html' else page}">
<link rel="icon" href="assets/logos/favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BIZ['name']}">
<meta property="og:title" content="{full}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{BIZ['url']}/assets/logos/02-the-cut.svg">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="assets/fonts/barlow-condensed-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/barlow-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/style.css">
<noscript><style>[data-rv]{{opacity:1!important;transform:none!important}}</style></noscript>
{blocks}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def nav(page):
    cur = ' aria-current="page"'
    li = "".join(
        f'<li><a href="{h}"{cur if h == page else ""}>{t}</a></li>'
        for h, t in NAV)
    return f"""<header class="nav">
<div class="nav-in">
  <a class="nav-logo" href="index.html" aria-label="{BIZ['name']} — home">
    <img src="assets/logos/nav-lockup.svg" alt="{BIZ['name']}" width="309" height="92">
  </a>
  <button class="burger" aria-expanded="false" aria-controls="nav-links" aria-label="Menu">
    <span></span><span></span><span></span>
  </button>
  <ul class="nav-links" id="nav-links">
    {li}
    <li class="nav-cta"><a class="btn btn-primary" href="contact.html">Free Estimate</a></li>
  </ul>
  <a class="nav-tel" href="{TELH}">{ico('phone', 18)}{TEL}</a>
</div>
</header>
<nav class="actionbar" aria-label="Quick contact">
  <a class="ab-call" href="{TELH}">{ico('phone', 18)}Call</a>
  <a class="ab-quote" href="contact.html">{ico('msg', 18)}Free Quote</a>
</nav>
<main id="main">
"""


def footer():
    svc = "".join(f'<li><a href="services.html#{s["slug"]}">{s["name"]}</a></li>'
                  for s in SERVICES[:6])
    area = "".join(f'<li><a href="service-area.html">{t}, MO</a></li>' for t in TOWNS_KEY[:6])
    return f"""</main>
<footer class="foot">
<div class="wrap-wide">
  <div class="foot-grid">
    <div>
      <img class="foot-logo" src="assets/logos/nav-lockup.svg" alt="{BIZ['name']}" width="309" height="92">
      <p style="color:var(--bone-mute);font-size:.96rem;max-width:34ch">
        Land clearing, hardscape and property maintenance across {BIZ['county']}, {BIZ['state']}.
        {BIZ['tagline']}
      </p>
      <a class="foot-tel" href="{TELH}">{TEL}</a>
      <p style="color:var(--bone-mute);font-size:.9rem;margin-top:.4rem">{BIZ['hours']}</p>
      <div class="btn-row mt-3">
        <a class="btn btn-primary" href="contact.html">Get a Free Estimate</a>
      </div>
    </div>
    <div><h3>Services</h3><ul>{svc}<li><a href="services.html">All services</a></li></ul></div>
    <div><h3>Service Area</h3><ul>{area}<li><a href="service-area.html">Full area</a></li></ul></div>
    <div><h3>Company</h3><ul>
      <li><a href="about.html">About</a></li>
      <li><a href="work.html">Our Work</a></li>
      <li><a href="service-area.html">Seasonal Calendar</a></li>
      <li><a href="logos.html">Brand &amp; Logo</a></li>
      <li><a href="contact.html">Contact</a></li>
      <li><a href="{SMS}">Text us</a></li>
    </ul></div>
  </div>
  <div class="foot-bot">
    <span>&copy; <span data-year></span> {BIZ['legal']}. {BIZ['county']}, {BIZ['state']}.</span>
    <span>{BIZ['descriptor']} &middot; {BIZ['tagline']}</span>
  </div>
</div>
</footer>
<script src="assets/js/main.js" defer></script>
</body>
</html>"""


def notice(key, extra=""):
    return (f'<div class="notice">{ico("alert", 20)}<div><b>Before this goes live</b>'
            f'{CLIENT_TODO[key]}{extra}</div></div>')


def ph(label, note, ratio="4/3", icon="camera", cls=""):
    return (f'<div class="ph {cls}" style="aspect-ratio:{ratio}"><div class="ph-in">'
            f'{ico(icon, 40)}<b>{label}</b><span>{note}</span></div></div>')


# ────────────────────────────────────────────────────────── components
def trust_bar():
    items = [("pin", f"{BIZ['county']} based"), ("check", "Free estimates"),
             ("clock", "Same-day callback"), ("truck", "Debris hauled off")]
    li = "".join(f"<li>{ico(i, 17)}{t}</li>" for i, t in items)
    return f'<div class="trust"><div class="wrap-wide"><ul>{li}</ul></div></div>'


def service_card(s, i):
    return f"""<a class="svc" href="services.html#{s['slug']}" data-rv="{i}">
  <span class="svc-ico">{ico(s['icon'], 46)}</span>
  <h3>{s['name']}</h3><p>{s['short']}</p>
  <span class="more">See details <span>{ico('arrow', 14)}</span></span>
</a>"""


def calendar_block():
    rows = ['<div class="cal-row head"><div class="cal-lbl">Service</div>'
            '<div class="cal-months">'
            + "".join(f"<span>{m}</span>" for m in MONTHS) + "</div></div>"]
    for label, months in CALENDAR:
        cells = "".join(
            f'<i class="{"peak" if v == 2 else "on" if v == 1 else ""}"></i>'
            for v in months)
        rows.append(f'<div class="cal-row"><div class="cal-lbl">{label}</div>'
                    f'<div class="cal-months">{cells}</div></div>')
    key = (f'<div class="cal-key">'
           f'<span><b style="background:var(--amber-500)"></b>Peak season</span>'
           f'<span><b style="background:var(--moss-600)"></b>In season</span>'
           f'<span><b style="background:rgba(242,237,225,.12)"></b>Off season</span>'
           f'</div>')
    return f'<div class="cal">{"".join(rows)}</div>{key}'


def before_after(idx, before_label, after_label, caption):
    """A real, working comparison slider driven by generated SVG scenes so the
    control is demonstrably functional before the client's photos arrive."""
    import brand as Bd
    wild = (f'<svg viewBox="0 0 800 500" preserveAspectRatio="xMidYMid slice">'
            f'<rect width="800" height="500" fill="{Bd.INK_800}"/>'
            f'<path d="{Bd.brush_silhouette(-20, 820, 430, 250, seed=idx * 7 + 3, density=30)}" fill="{Bd.MOSS_900}"/>'
            f'<path d="{Bd.brush_silhouette(-20, 820, 470, 190, seed=idx * 7 + 9, density=24)}" fill="{Bd.MOSS_800}"/>'
            f'<path d="{Bd.conifer(120 + idx * 95, 470, 240 + idx * 40, 130)}" fill="{Bd.MOSS_900}"/>'
            f'<path d="{Bd.hardwood(430 - idx * 130, 470, 300 - idx * 46, 240 - idx * 40)}" fill="{Bd.MOSS_800}"/>'
            f'<path d="{Bd.conifer(660 - idx * 40, 470, 190 + idx * 55, 105 + idx * 25)}" fill="{Bd.MOSS_900}"/>'
            f'<rect y="470" width="800" height="30" fill="{Bd.MOSS_900}"/></svg>')
    clean = (f'<svg viewBox="0 0 800 500" preserveAspectRatio="xMidYMid slice">'
             f'<rect width="800" height="500" fill="{Bd.INK_850}"/>'
             f'<path d="M0,470 H800 V{418 + idx * 14} H{300 - idx * 110} '
             f'L{200 - idx * 60},{400 + idx * 12} H0 Z" fill="{Bd.MOSS_700}"/>'
             f'<rect y="466" width="800" height="34" fill="{Bd.MOSS_600}"/>'
             f'<path d="{Bd.hardwood(620 - idx * 180, 420, 220 - idx * 55, 170 - idx * 40)}" fill="{Bd.MOSS_600}"/>'
             f'<g opacity=".5">'
             + "".join(f'<rect x="{x}" y="{420 + (x % 3) * 2}" width="2" height="50" fill="{Bd.MOSS_500}"/>'
                       for x in range(30, 800, 46))
             + f'</g></svg>')
    return f"""<figure style="margin:0" data-rv="{idx}">
  <div class="ba" style="--pos:52%">
    <div class="lyr bef">{wild}</div>
    <div class="lyr aft">{clean}</div>
    <span class="ba-tag l">{before_label}</span>
    <span class="ba-tag r">{after_label}</span>
    <input type="range" min="0" max="100" value="52"
           aria-label="Reveal the after image: {caption}">
    <span class="ba-handle" aria-hidden="true"></span>
  </div>
  <figcaption style="margin-top:.75rem;color:var(--bone-mute);font-size:.94rem">{caption}</figcaption>
</figure>"""


def quote_form(bone=False):
    tiles = "".join(
        f'<div class="tile"><input type="radio" id="need-{s["slug"]}" name="need" '
        f'value="{s["name"]}" data-req="need"><label for="need-{s["slug"]}">'
        f'{ico(s["icon"], 26)}{s["name"]}</label></div>'
        for s in SERVICES)
    towns = "".join(f'<option value="{t}">{t}</option>' for t in TOWNS_KEY + TOWNS_MORE)
    return f"""<form class="quote" data-steps novalidate>
  <div class="qbar" aria-hidden="true"></div>
  <p class="qcount" role="status" aria-live="polite"></p>

  <div class="qstep on">
    <fieldset>
      <legend>What do you need done?</legend>
      <div class="tiles">{tiles}</div>
      <p class="err" data-err="need">Pick one so we know who to send.</p>
    </fieldset>
    <div class="qnav"><button type="button" class="btn btn-primary" data-next>
      Next {ico('arrow', 16)}</button></div>
  </div>

  <div class="qstep">
    <fieldset>
      <legend>Where's the property?</legend>
      <div class="field">
        <label for="q-town">Town <span class="hint">— Jefferson County and nearby</span></label>
        <select id="q-town" name="town" data-req="town">
          <option value="">Choose a town…</option>{towns}
          <option value="Other">Somewhere else — I'll explain</option>
        </select>
        <p class="err" data-err="town">Let us know roughly where you are.</p>
      </div>
      <div class="field">
        <label for="q-size">Roughly how big? <span class="hint">— optional</span></label>
        <select id="q-size" name="size">
          <option value="">Not sure</option>
          <option>Small yard / under ¼ acre</option>
          <option>¼ – 1 acre</option>
          <option>1 – 5 acres</option>
          <option>5 – 20 acres</option>
          <option>20+ acres</option>
        </select>
      </div>
      <div class="field">
        <label for="q-detail">Anything we should know? <span class="hint">— optional</span></label>
        <textarea id="q-detail" name="detail"
          placeholder="Access, slope, how long it's been growing, deadlines…"></textarea>
      </div>
    </fieldset>
    <div class="qnav">
      <button type="button" class="btn btn-ghost" data-prev>Back</button>
      <button type="button" class="btn btn-primary" data-next>Next {ico('arrow', 16)}</button>
    </div>
  </div>

  <div class="qstep">
    <fieldset>
      <legend>How do we reach you?</legend>
      <div class="field">
        <label for="q-name">Name</label>
        <input type="text" id="q-name" name="name" autocomplete="name" data-req="name">
        <p class="err" data-err="name">We'll need a name.</p>
      </div>
      <div class="field">
        <label for="q-phone">Phone <span class="hint">— we'll call or text back same day</span></label>
        <input type="tel" id="q-phone" name="phone" inputmode="tel"
               autocomplete="tel" placeholder="(314) 555-0123" data-req="phone">
        <p class="err" data-err="phone">A 10-digit phone number, please.</p>
      </div>
      <div class="field">
        <label for="q-email">Email <span class="hint">— optional</span></label>
        <input type="email" id="q-email" name="email" inputmode="email" autocomplete="email">
      </div>
    </fieldset>
    <div class="qnav">
      <button type="button" class="btn btn-ghost" data-prev>Back</button>
      <button type="submit" class="btn btn-primary">Send my request</button>
    </div>
    <p style="font-size:.86rem;color:var(--bone-mute);margin-top:1rem">
      Or skip the form — call or text <a href="{TELH}" style="color:var(--amber-400)">{TEL}</a>.
    </p>
  </div>

  <div class="qdone" hidden>
    {ico('check', 64)}
    <h3>Request sent</h3>
    <p style="color:var(--bone-mute);max-width:44ch;margin-inline:auto">
      We'll get back to you the same day. If it's urgent, call
      <a href="{TELH}" style="color:var(--amber-400)">{TEL}</a>.
    </p>
  </div>
</form>"""


# ────────────────────────────────────────────────────────────── pages
def page_index():
    cards = "".join(service_card(s, i) for i, s in enumerate(SERVICES))
    cbm = "".join(f"""<div data-rv="{i}">
      <span class="n">{f['n']}</span><h3>{f['title']}</h3><p>{f['blurb']}</p>
      <ul>{''.join(f'<li>{s["name"]}</li>' for s in SERVICES if s['family'] == k)}</ul>
    </div>""" for i, (k, f) in enumerate(FAMILIES.items()))
    steps = "".join(f'<div class="step" data-rv="{i}"><h3>{t}</h3><p>{d}</p></div>'
                    for i, (t, d) in enumerate(PROCESS))
    towns = "".join(f'<span class="town key">{t}</span>' for t in TOWNS_KEY) + \
            "".join(f'<span class="town">{t}</span>' for t in TOWNS_MORE[:10])

    return head("index.html",
                "Home",
                f"Land clearing, brush clearing, retaining walls, masonry, decks, junk "
                f"removal and mowing across {BIZ['county']}, {BIZ['state']}. Free "
                f"estimates — call or text {TEL}.",
                [ld_faq()] + [ld_service(s) for s in SERVICES[:3]]) + nav("index.html") + f"""

<section class="hero">
  <canvas class="hero-canvas" id="hero3d" aria-hidden="true"></canvas>
  <div class="hero-in">
    <div class="wrap-wide">
      <p class="eyebrow">{BIZ['county']}, {BIZ['state']}</p>
      <h1>We take it back<span class="accent">to workable ground.</span></h1>
      <p class="hero-strap">Clear <i></i> Build <i></i> Maintain</p>
      <p class="hero-sub">
        Land clearing, retaining walls, masonry, decks, junk removal and mowing —
        one crew for the whole property, from the first cut to the standing schedule.
      </p>
      <div class="btn-row">
        <a class="btn btn-primary" href="contact.html">Get a free estimate</a>
        <a class="btn btn-ghost" href="{TELH}">{ico('phone', 18)}{TEL}</a>
      </div>
      <p class="hero-note">{ico('clock', 16)} Call or text — we get back to you the same day.</p>
    </div>
  </div>
  <button type="button" class="hero-scroll" id="hero-scroll" aria-label="Scroll to what we do">Scroll</button>
  <div class="preset-switch" id="preset-switch" role="group" aria-label="Preview the hero at another time of day">
    <span>Time of day</span>
    <button type="button" id="tod-live" aria-pressed="true">Live</button>
    <input type="range" id="tod-hour" min="0" max="23.5" step="0.5" value="12"
           aria-label="Preview hour">
    <span class="tval" id="tod-label" role="status" aria-live="polite">Live</span>
  </div>
</section>

{trust_bar()}

<section class="pad">
  <div class="wrap-wide">
    <div class="shead">
      <div>
        <p class="eyebrow">Three things, done properly</p>
        <h2>Clear. Build. Maintain.</h2>
        <p class="lede">Most properties need all three eventually. Most contractors
          only do one. That gap is where jobs stall, and it's why we run the whole line.</p>
      </div>
      <a class="btn btn-ghost" href="services.html">All services</a>
    </div>
    <div class="cbm">{cbm}</div>
  </div>
</section>

<section class="pad bg-850">
  <div class="wrap-wide">
    <div class="shead">
      <div><p class="eyebrow">What we do</p><h2>Nine services, one number</h2></div>
    </div>
    <div class="svc-grid">{cards}</div>
  </div>
</section>

<section class="pad">
  <div class="wrap-wide">
    <div class="shead">
      <div><p class="eyebrow">The difference</p><h2>Before &amp; after</h2>
      <p class="lede">Drag the handle. On clearing work the transformation
        <em>is</em> the product — which is why the photos matter more than the words.</p></div>
    </div>
    <div class="grid-2">
      {before_after(0, "Before", "After", "Overgrown residential lot — cleared, graded and hauled off.")}
      {before_after(1, "Before", "After", "Fence line reclaimed from honeysuckle and cedar encroachment.")}
    </div>
    <div class="mt-4">{notice('photos')}</div>
  </div>
</section>

<section class="pad bg-bone">
  <div class="wrap-wide">
    <div class="shead">
      <div><p class="eyebrow">How it works</p><h2>No mystery, no runaround</h2></div>
    </div>
    <div class="steps">{steps}</div>
  </div>
</section>

<section class="pad bg-850">
  <div class="wrap-wide">
    <div class="shead">
      <div><p class="eyebrow">Timing</p><h2>The right work, the right month</h2>
        <p class="lede">Missouri ground dictates the schedule. Clearing in frozen
          January soil beats clearing in April mud every time — and we'll tell you
          when waiting saves you money.</p></div>
      <a class="btn btn-ghost" href="service-area.html">Service area &amp; seasons</a>
    </div>
    {calendar_block()}
  </div>
</section>

<section class="pad">
  <div class="wrap-wide">
    <div class="shead">
      <div><p class="eyebrow">Where we work</p><h2>{BIZ['county']}, {BIZ['state']}</h2>
        <p class="lede">From the Arnold subdivisions to the back forty in Grubville.
          Highlighted towns are our core area.</p></div>
      <a class="btn btn-ghost" href="service-area.html">Full list</a>
    </div>
    <div class="towns">{towns}</div>
  </div>
</section>

<section class="pad bg-moss">
  <div class="wrap">
    <div class="tc" style="max-width:60ch;margin-inline:auto">
      <h2>Tell us what you're looking at.</h2>
      <p class="lede mx mt-2" style="color:var(--bone-dim)">
        Free estimate, same-day callback, and a written scope before anything starts.
      </p>
      <div class="btn-row mt-3" style="justify-content:center">
        <a class="btn btn-primary" href="contact.html">Get a free estimate</a>
        <a class="btn btn-ghost" href="{SMS}">{ico('msg', 18)}Text us a photo</a>
      </div>
    </div>
  </div>
</section>

<section class="pad">
  <div class="wrap">
    <p class="eyebrow">Questions</p>
    <h2 style="margin-bottom:2rem">Straight answers</h2>
    <div class="faq">
      {''.join(f'<details{" open" if i == 0 else ""}><summary>{q}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(FAQ))}
    </div>
  </div>
</section>

<script type="module">
  import {{ mountHeroGrass }} from './assets/js/hero-grass.js';
  const c = document.getElementById('hero3d');
  const api = c ? mountHeroGrass(c, {{ preset: 'dusk' }}) : null;
  window.__heroApi = api;
  // Day-cycle scrubber — preview only. Delete this block and the
  // .preset-switch markup once you're happy with it.
  const slider = document.getElementById('tod-hour');
  const liveBtn = document.getElementById('tod-live');
  const label = document.getElementById('tod-label');
  const fmt = (h) => {{
    const hh = Math.floor(h), mm = Math.round((h - hh) * 60);
    const ap = hh < 12 ? 'am' : 'pm';
    const h12 = hh % 12 === 0 ? 12 : hh % 12;
    return h12 + ':' + String(mm).padStart(2, '0') + ap;
  }};
  if (api && slider) {{
    const goLive = () => {{
      api.goLive();
      liveBtn.setAttribute('aria-pressed', 'true');
      const sh = api.siteHour();
      slider.value = String(Math.round(sh * 2) / 2);
      label.textContent = fmt(sh) + ' \u00b7 ' + api.describeLook();
    }};
    slider.addEventListener('input', () => {{
      const h = parseFloat(slider.value);
      api.previewHour(h);
      liveBtn.setAttribute('aria-pressed', 'false');
      label.textContent = fmt(h) + ' \u00b7 ' + api.describeLook();
    }});
    liveBtn.addEventListener('click', goLive);
    goLive();
  }}
  // Scroll cue actually scrolls.
  const sc = document.getElementById('hero-scroll');
  if (sc) sc.addEventListener('click', () => {{
    const next = document.querySelector('.hero') &&
      document.querySelector('.hero').nextElementSibling;
    const target = next && next.nextElementSibling ? next.nextElementSibling : next;
    if (target) target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
  }});
</script>
""" + footer()


def page_services():
    fam_nav = "".join(
        f'<a class="btn btn-ghost" href="#{k}">{f["title"]}</a>' for k, f in FAMILIES.items())
    blocks = []
    for k, f in FAMILIES.items():
        items = [s for s in SERVICES if s["family"] == k]
        secs = []
        for i, s in enumerate(items):
            bl = "".join(f'<li>{ico("check", 19)}<span>{b}</span></li>' for b in s["bullets"])
            secs.append(f"""<article id="{s['slug']}" class="grid-2" data-rv="{i}"
                 style="align-items:start;padding-block:clamp(2rem,4vw,3.5rem);
                        border-top:1px solid rgba(242,237,225,.12)">
  <div>
    <span class="svc-ico" style="color:var(--moss-400)">{ico(s['icon'], 46)}</span>
    <h3 style="margin:.75rem 0 .75rem;font-size:clamp(1.8rem,3.4vw,2.5rem)">{s['name']}</h3>
    <p style="color:var(--bone-dim)">{s['body']}</p>
    <p style="color:var(--moss-400);font-size:.95rem;display:flex;gap:.5rem;align-items:flex-start">
      {ico('cal', 18)}<span>{s['season']}</span></p>
    <div class="btn-row mt-3">
      <a class="btn btn-primary" href="contact.html">Estimate for {s['name'].lower()}</a>
    </div>
  </div>
  <div>
    <ul class="chk">{bl}</ul>
    <div class="mt-3">{ph('Photo — ' + s['name'], 'Your own work, on your own machine. Landscape crop, 4:3.', '4/3')}</div>
  </div>
</article>""")
        blocks.append(f"""<section class="pad{' bg-850' if k == 'build' else ''}" id="{k}">
  <div class="wrap-wide">
    <p class="eyebrow">{f['n']} — {f['label']}</p>
    <h2>{f['title']}</h2>
    <p class="lede mt-2">{f['blurb']}</p>
    {''.join(secs)}
  </div>
</section>""")

    return head("services.html", "Services",
                f"All nine M&W GroundWorks services — land clearing, brush clearing, "
                f"ditch clearing, retaining walls, masonry, decks, mowing, junk removal "
                f"and property maintenance in {BIZ['county']}, {BIZ['state']}.",
                [ld_service(s) for s in SERVICES]) + nav("services.html") + f"""
<section class="pad-sm bg-850" style="padding-top:clamp(2.5rem,6vw,4.5rem)">
  <div class="wrap-wide">
    <p class="eyebrow">Services</p>
    <h1 style="font-size:clamp(2.6rem,7vw,5.5rem)">Everything from<br>the dirt up.</h1>
    <p class="lede mt-3">Nine services across three stages of a property's life.
      One crew, one number, one estimate — whether you need an acre cleared or
      a lawn mowed every other Tuesday.</p>
    <div class="btn-row mt-4">{fam_nav}</div>
  </div>
</section>
{trust_bar()}
{''.join(blocks)}
<section class="pad bg-moss">
  <div class="wrap tc">
    <h2>Not sure which one you need?</h2>
    <p class="lede mx mt-2" style="color:var(--bone-dim)">Describe it in plain
      language and we'll sort it out. Most properties need two or three of these anyway.</p>
    <div class="btn-row mt-3" style="justify-content:center">
      <a class="btn btn-primary" href="contact.html">Get a free estimate</a>
      <a class="btn btn-ghost" href="{TELH}">{ico('phone', 18)}{TEL}</a>
    </div>
  </div>
</section>
""" + footer()


def page_work():
    tiles = []
    specs = [("Land clearing — before", "Wide shot of the lot as found. Landscape, 4:3.", "4/3", ""),
             ("Land clearing — after", "Same angle, same lens, after the clear. This pairing sells the job.", "4/3", ""),
             ("Retaining wall", "Raking light, late afternoon. Show the full run and the drainage.", "3/4", "tall"),
             ("Masonry detail", "Close on joints and coursing. Proves the craft.", "4/3", ""),
             ("Deck build", "Include the slope. Flat-lot decks are commodity work.", "4/3", ""),
             ("The machine at work", "Skid steer mid-cut, mud on the tracks. The single most valuable photo you own.", "4/3", ""),
             ("Ditch clearing", "Before/after of the same culvert.", "4/3", ""),
             ("Junk removal", "Loaded trailer, cleared yard behind it.", "3/4", "tall"),
             ("The crew", "Faces sell trust. One good group shot beats ten stock images.", "4/3", "")]
    for label, note, ratio, cls in specs:
        tiles.append(ph(label, note, ratio, "camera", cls))

    return head("work.html", "Our Work",
                f"Recent land clearing, retaining wall, masonry and property work "
                f"by {BIZ['name']} in {BIZ['county']}, {BIZ['state']}.") + nav("work.html") + f"""
<section class="pad-sm bg-850" style="padding-top:clamp(2.5rem,6vw,4.5rem)">
  <div class="wrap-wide">
    <p class="eyebrow">Our work</p>
    <h1 style="font-size:clamp(2.6rem,7vw,5.5rem)">The proof<br>is the property.</h1>
    <p class="lede mt-3">Anyone can write "quality workmanship." Here's the alternative.</p>
  </div>
</section>
{trust_bar()}

<section class="pad">
  <div class="wrap-wide">
    <div class="shead">
      <div><p class="eyebrow">Drag to compare</p><h2>Before &amp; after</h2></div>
    </div>
    <div class="grid-2">
      {before_after(0, "As found", "Finished", "Half-acre residential lot, cleared and graded.")}
      {before_after(1, "As found", "Finished", "Treeline pushed back off the fence row.")}
    </div>
  </div>
</section>

<section class="pad bg-850">
  <div class="wrap-wide">
    <div class="shead">
      <div><p class="eyebrow">Gallery</p><h2>Job photos</h2>
      <p class="lede">Every slot below is sized and cropped for the final layout —
        drop real photos in and the page is finished.</p></div>
    </div>
    <div class="gal">{''.join(tiles)}</div>
    <div class="mt-4">{notice('photos')}</div>
  </div>
</section>

<section class="pad">
  <div class="wrap-wide">
    <div class="shead"><div><p class="eyebrow">What people say</p><h2>Reviews</h2></div></div>
    <div class="grid-3">
      {''.join(f'''<div class="ph" style="aspect-ratio:auto;min-height:190px">
        <div class="ph-in">{ico('star', 40)}<b>Google review slot</b>
        <span>Live Google reviews render here once the Business Profile has them.</span></div></div>''' for _ in range(3))}
    </div>
    <div class="mt-4">{notice('reviews')}</div>
  </div>
</section>

<section class="pad bg-moss">
  <div class="wrap tc">
    <h2>Want your property in here?</h2>
    <div class="btn-row mt-3" style="justify-content:center">
      <a class="btn btn-primary" href="contact.html">Get a free estimate</a>
      <a class="btn btn-ghost" href="{TELH}">{ico('phone', 18)}{TEL}</a>
    </div>
  </div>
</section>
""" + footer()


def page_area():
    key = "".join(f'<span class="town key">{t}</span>' for t in TOWNS_KEY)
    more = "".join(f'<span class="town">{t}</span>' for t in TOWNS_MORE)
    edge = "".join(f'<span class="town">{t}</span>' for t in TOWNS_EDGE)
    return head("service-area.html", "Service Area",
                f"M&W GroundWorks serves Arnold, Festus, Hillsboro, Imperial, High Ridge, "
                f"House Springs, De Soto, Cedar Hill, Pevely and the rest of "
                f"{BIZ['county']}, {BIZ['state']}.") + nav("service-area.html") + f"""
<section class="pad-sm bg-850" style="padding-top:clamp(2.5rem,6vw,4.5rem)">
  <div class="wrap-wide">
    <p class="eyebrow">Service area</p>
    <h1 style="font-size:clamp(2.6rem,7vw,5.5rem)">All of<br>{BIZ['county']}.</h1>
    <p class="lede mt-3">226,000 people across 656 square miles of Ozark foothills,
      river bluffs and subdivision. We cover the whole thing — the quarter-acre lot
      in Arnold and the twenty acres off a gravel road in Grubville.</p>
  </div>
</section>
{trust_bar()}

<section class="pad">
  <div class="wrap-wide">
    <div class="grid-2" style="align-items:start">
      <div>
        <p class="eyebrow">Core area</p>
        <h2>Where we are most weeks</h2>
        <div class="towns mt-3">{key}</div>
        <p class="eyebrow mt-5">Also serving</p>
        <div class="towns mt-2">{more}</div>
        <p class="eyebrow mt-5">Just outside the county</p>
        <div class="towns mt-2">{edge}</div>
        <p class="mt-3" style="color:var(--bone-mute);font-size:.95rem">
          Close to the line but not on the list? Call anyway — {BIZ['seat']} to
          downtown St. Louis is about forty minutes, and we travel.</p>
      </div>
      <div>
        {ph('Service area map', 'Embed a Google Map centred on Jefferson County with the service radius drawn. 4:3.', '4/3', 'pin')}
        <div class="mt-3">{notice('address')}</div>
      </div>
    </div>
  </div>
</section>

<section class="pad bg-850">
  <div class="wrap-wide">
    <div class="shead">
      <div><p class="eyebrow">Seasonal calendar</p><h2>When to book what</h2>
      <p class="lede">Missouri seasonality, not a generic template. Booking the
        right work in the right window is the cheapest way to save money on it.</p></div>
    </div>
    {calendar_block()}
    <div class="grid-3 mt-5">
      <div><h3 style="color:var(--moss-400);font-size:clamp(1.1rem,1.6vw,1.3rem)">{ico('leaf', 20)} Spring — Mar to May</h3>
        <p style="color:var(--bone-mute);font-size:.96rem">Clean-ups, mulch, and the
          first cuts of the season. Worst window for land clearing — the ground is mud
          and equipment ruts it.</p></div>
      <div><h3 style="color:var(--moss-400);font-size:clamp(1.1rem,1.6vw,1.3rem)">{ico('mower', 20)} Summer — Jun to Aug</h3>
        <p style="color:var(--bone-mute);font-size:.96rem">Mowing settles into rhythm
          as fescue slows in the heat. Prime season for walls, masonry and decks.</p></div>
      <div><h3 style="color:var(--moss-400);font-size:clamp(1.1rem,1.6vw,1.3rem)">{ico('trees', 20)} Fall &amp; winter — Sep to Feb</h3>
        <p style="color:var(--bone-mute);font-size:.96rem">Aerate and overseed in early
          September, leaves off by November — then clearing season opens. Frozen ground,
          dormant growth, clear sightlines.</p></div>
    </div>
  </div>
</section>

<section class="pad bg-moss">
  <div class="wrap tc">
    <h2>In the county? Let's talk.</h2>
    <div class="btn-row mt-3" style="justify-content:center">
      <a class="btn btn-primary" href="contact.html">Get a free estimate</a>
      <a class="btn btn-ghost" href="{TELH}">{ico('phone', 18)}{TEL}</a>
    </div>
  </div>
</section>
""" + footer()


def page_about():
    return head("about.html", "About",
                f"{BIZ['name']} is a locally owned land and property services company "
                f"based in {BIZ['county']}, {BIZ['state']}.") + nav("about.html") + f"""
<section class="pad-sm bg-850" style="padding-top:clamp(2.5rem,6vw,4.5rem)">
  <div class="wrap-wide">
    <p class="eyebrow">About</p>
    <h1 style="font-size:clamp(2.6rem,7vw,5.5rem)">Local outfit.<br>Whole property.</h1>
    <p class="lede mt-3">{BIZ['name']} works one county. That's on purpose —
      we know which subdivisions have clay that won't drain, which back roads a
      trailer can't turn around on, and which month the ground will hold a machine.</p>
  </div>
</section>
{trust_bar()}

<section class="pad">
  <div class="wrap-wide">
    <div class="grid-2" style="align-items:start">
      <div>
        <p class="eyebrow">Why one crew for all of it</p>
        <h2>The gap most people fall into</h2>
        <p style="color:var(--bone-dim)">A property that needs clearing usually needs
          grading after. A yard that needs a wall usually needs the slope fixed first.
          A lot you just bought needs all three plus a mowing schedule once it's done.</p>
        <p style="color:var(--bone-dim)">Splitting that across three contractors is how
          jobs stall — everyone waits on someone else, and nobody owns the finish. We run
          clear, build and maintain under one roof so there's one number to call and one
          person accountable for the result.</p>
        <ul class="chk mt-3">
          <li>{ico('check', 19)}<span>One estimate covering the whole scope</span></li>
          <li>{ico('check', 19)}<span>Debris hauled off, not left stacked</span></li>
          <li>{ico('check', 19)}<span>We tell you when a job needs a permit — before you commit</span></li>
          <li>{ico('check', 19)}<span>We'll tell you when waiting a season saves you money</span></li>
          <li>{ico('check', 19)}<span>You walk the finished job with us before we leave</span></li>
        </ul>
      </div>
      <div>
        {ph('The owner + the truck', 'One good portrait with the truck and the logo on it. This outperforms every stock photo on the internet. 4:3.', '4/3')}
        <div class="mt-3">{ph('The crew', 'Group shot on a finished job. 4:3.', '4/3')}</div>
      </div>
    </div>
  </div>
</section>

<section class="pad bg-850">
  <div class="wrap-wide">
    <div class="shead"><div><p class="eyebrow">By the numbers</p><h2>Ask us anything</h2></div></div>
    <div class="stats">
      <div class="stat"><b>—</b><span>Years working the county</span></div>
      <div class="stat"><b>—</b><span>Properties finished</span></div>
      <div class="stat"><b>—</b><span>Acres cleared</span></div>
      <div class="stat"><b>9</b><span>Services under one roof</span></div>
    </div>
    <div class="mt-3">{notice('stats')}</div>
    <div class="mt-3">{notice('insurance')}</div>
  </div>
</section>

<section class="pad">
  <div class="wrap-wide">
    <div class="shead"><div><p class="eyebrow">Equipment</p><h2>What shows up</h2>
      <p class="lede">Naming real machines beats every adjective. Replace these with
        the actual makes and models on your trailer.</p></div></div>
    <div class="grid-3">
      {''.join(f'''<div class="ph" style="aspect-ratio:auto;min-height:170px"><div class="ph-in">
        {ico('truck', 40)}<b>{n}</b><span>Photo + make/model. Real spec sells the job.</span>
      </div></div>''' for n in ['Skid steer + mulching head', 'Mini excavator', 'Dump trailer'])}
    </div>
  </div>
</section>

<section class="pad bg-moss">
  <div class="wrap tc">
    <h2>Let's go look at it.</h2>
    <p class="lede mx mt-2" style="color:var(--bone-dim)">Free estimate, on site, same-day callback.</p>
    <div class="btn-row mt-3" style="justify-content:center">
      <a class="btn btn-primary" href="contact.html">Get a free estimate</a>
      <a class="btn btn-ghost" href="{TELH}">{ico('phone', 18)}{TEL}</a>
    </div>
  </div>
</section>
""" + footer()


def page_contact():
    return head("contact.html", "Contact",
                f"Get a free estimate from {BIZ['name']}. Call or text {TEL}, "
                f"or send a few details and we'll get back to you the same day.",
                [ld_faq()]) + nav("contact.html") + f"""
<section class="pad-sm bg-850" style="padding-top:clamp(2.5rem,6vw,4.5rem)">
  <div class="wrap-wide">
    <p class="eyebrow">Free estimate</p>
    <h1 style="font-size:clamp(2.6rem,7vw,5rem)">Tell us what<br>you're looking at.</h1>
  </div>
</section>

<section class="pad">
  <div class="wrap-wide">
    <div class="grid-2" style="align-items:start">
      <div>
        <p class="eyebrow">Fastest way</p>
        <h2 style="font-size:clamp(1.8rem,3.4vw,2.4rem)">Call or text</h2>
        <a class="foot-tel" href="{TELH}" style="font-size:clamp(2.2rem,5vw,3.2rem);margin-top:.5rem">{TEL}</a>
        <p style="color:var(--bone-mute)">{BIZ['hours']}</p>
        <div class="btn-row mt-3">
          <a class="btn btn-primary" href="{TELH}">{ico('phone', 18)}Call now</a>
          <a class="btn btn-ghost" href="{SMS}">{ico('msg', 18)}Text a photo</a>
        </div>
        <ul class="chk mt-4">
          <li>{ico('clock', 19)}<span><strong>Same-day callback.</strong> Most home-services
            leads go to whoever answers first — we try to be that.</span></li>
          <li>{ico('camera', 19)}<span><strong>Send a photo.</strong> For overgrown lots we can
            often give you a ballpark before we ever drive out.</span></li>
          <li>{ico('check', 19)}<span><strong>Free estimates,</strong> in writing, with the
            scope spelled out.</span></li>
          <li>{ico('pin', 19)}<span><strong>{BIZ['county']} and the edges of it.</strong>
            Not sure you're in range? Ask.</span></li>
        </ul>
        <div class="mt-4">{notice('insurance')}</div>
      </div>
      <div>
        <p class="eyebrow">Or send details</p>
        <h2 style="font-size:clamp(1.8rem,3.4vw,2.4rem);margin-bottom:1.25rem">Request a quote</h2>
        {quote_form()}
      </div>
    </div>
  </div>
</section>

<section class="pad bg-850">
  <div class="wrap">
    <p class="eyebrow">Questions</p>
    <h2 style="margin-bottom:2rem">Before you call</h2>
    <div class="faq">
      {''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in FAQ)}
    </div>
  </div>
</section>
""" + footer()


def page_logos():
    CONCEPTS = [
        ("01-groundline-badge.svg", "01-groundline-badge-1c.svg", "Groundline Badge",
         "The recommendation. The horizon inside the badge starts wild on the left "
         "and ends graded on the right, with an amber blade line marking the cut — "
         "the entire business described in one shape, before anyone reads a word. "
         "Reduces cleanly to the badge alone for a truck door or a hat.",
         ["Primary mark", "Truck door", "Signage", "Apparel"], False),
        ("02-the-cut.svg", "02-the-cut-1c.svg", "The Cut — horizontal lockup",
         "The workhorse. Built for the width of a website header, a business card and "
         "the side of a trailer. The square icon detaches and works alone as an avatar "
         "or app icon.",
         ["Website header", "Business card", "Letterhead", "Trailer"], False),
        ("03-strata-stack.svg", None, "Strata Stack",
         "Makes the tagline structural instead of decorative. Three bars read "
         "simultaneously as a soil cross-section and as the three service families. "
         "Strongest on social and in ads where the words carry the message.",
         ["Social", "Ads", "Yard sign"], False),
        ("04-bucket-mark.svg", "04-bucket-mark-1c.svg", "Bucket Mark",
         "The W sits on an excavator bucket's tooth row. The most ownable idea in the "
         "set and the one that survives smallest — it is the basis for the favicon.",
         ["App icon", "Favicon", "Stamp", "Embroidery"], False),
        ("05-section-rule.svg", "05-section-rule-dark.svg", "Section Rule",
         "The quiet one, for estimates, invoices and contracts. Hairline rules under "
         "the wordmark read as a survey section cut. Signals that the paperwork is as "
         "considered as the work.",
         ["Estimates", "Invoices", "Letterhead"], True),
        ("06-the-seal.svg", "06-the-seal-1c.svg", "The Seal",
         "Circular, so it embroiders on a cap without distortion, stamps cleanly, and "
         "holds up as a round social avatar.",
         ["Hats", "Patches", "Social avatar", "Stamp"], False),
    ]
    cards = []
    for i, (f, alt, name, why, tags, on_bone) in enumerate(CONCEPTS):
        scale = "".join(
            f'<figure><img src="assets/logos/{f}" style="height:{h}px;width:auto" '
            f'alt=""><figcaption>{h}px</figcaption></figure>' for h in (120, 64, 32))
        altbtn = (f'<a class="btn btn-ghost" href="assets/logos/{alt}" download '
                  f'style="padding:.6rem 1rem;font-size:.85rem">One-colour SVG</a>' if alt else "")
        cards.append(f"""<div class="logo-card" data-rv="{i}">
  <div class="logo-view{' on-bone' if on_bone else ''}">
    <img src="assets/logos/{f}" alt="{name} logo concept for {BIZ['name']}">
  </div>
  <div class="scaletest">{scale}
    <p style="margin:0 0 0 auto;align-self:center;color:var(--bone-mute);font-size:.86rem;max-width:22ch">
      Scale test — every mark must still read at 32px.</p>
  </div>
  <div class="logo-meta">
    <h3>{name}</h3><p>{why}</p>
    <div class="tags">{''.join(f'<span>{t}</span>' for t in tags)}</div>
    <div class="btn-row mt-3">
      <a class="btn btn-moss" href="assets/logos/{f}" download
         style="padding:.6rem 1rem;font-size:.85rem">Download SVG</a>{altbtn}
    </div>
  </div>
</div>""")

    SW = [("Ink", "#0B0F0C", "Base. Every page sits on this."),
          ("Bone", "#F2EDE1", "Primary text and the M&W wordmark."),
          ("Moss", "#7A9A3E", "The brand green, sampled from your existing logos."),
          ("Moss Deep", "#33461B", "Section fills and the trust bar."),
          ("Amber", "#E8A33D", "Every call to action. Nothing else."),
          ("Bone Mute", "#9A9382", "Secondary copy.")]
    sw = "".join(f'<div class="sw"><div class="chip" style="background:{hexv}"></div>'
                 f'<div class="info"><b>{n}</b><code>{hexv}</code>'
                 f'<p style="margin:.4rem 0 0;color:var(--bone-mute);font-size:.8rem">{d}</p>'
                 f'</div></div>' for n, hexv, d in SW)

    return head("logos.html", "Brand",
                f"Logo concepts, colour palette and typography for {BIZ['name']}.") \
        + nav("logos.html") + f"""
<section class="pad-sm bg-850" style="padding-top:clamp(2.5rem,6vw,4.5rem)">
  <div class="wrap-wide">
    <p class="eyebrow">Identity</p>
    <h1 style="font-size:clamp(2.4rem,6.5vw,5rem)">Six directions,<br>one system.</h1>
    <p class="lede mt-3">Every mark below is a real vector file with the letterforms
      converted to outlines — no font needed to open them, and no quality loss at any
      size, from a favicon to a billboard.</p>
  </div>
</section>

<section class="pad">
  <div class="wrap-wide">
    <p class="eyebrow">Starting point</p>
    <h2>What the current logos get right — and what breaks</h2>
    <div class="grid-2 mt-4" style="align-items:start">
      <div>
        <h3 style="color:var(--moss-400);margin-bottom:.75rem;font-size:1.3rem">Worth keeping</h3>
        <ul class="chk">
          <li>{ico('check', 19)}<span>The olive/moss green. It's distinctive and it's yours —
            every colour on this site was sampled straight out of your existing files.</span></li>
          <li>{ico('check', 19)}<span>Heavy condensed capitals for M&amp;W. Correct register
            for land work; the typography here matches it deliberately.</span></li>
          <li>{ico('check', 19)}<span>The badge instinct. A contained shape is right for a
            trade business — it stamps, patches and reads on a door.</span></li>
          <li>{ico('check', 19)}<span>"Clear · Build · Maintain." Strong three-beat line.
            It's structural throughout the new system.</span></li>
        </ul>
      </div>
      <div>
        <h3 style="color:var(--amber-500);margin-bottom:.75rem;font-size:1.3rem">What breaks</h3>
        <ul class="chk">
          <li>{ico('alert', 19)}<span><strong>The icon strip is a service list, not a logo.</strong>
            Six tiny pictograms plus four lines of type disappear below about two inches —
            which is most of where a logo actually lives.</span></li>
          <li>{ico('alert', 19)}<span><strong>The cabin illustration says log-home builder.</strong>
            It points at the one thing you don't do.</span></li>
          <li>{ico('alert', 19)}<span><strong>Three competing type treatments</strong> in one
            mark. Nothing is allowed to be the loudest thing.</span></li>
          <li>{ico('alert', 19)}<span><strong>No single ownable mark.</strong> Nothing you can
            stamp alone on a hat, a favicon or a truck bed. Every concept below fixes that.</span></li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="pad bg-850">
  <div class="wrap-wide">
    <div class="shead"><div><p class="eyebrow">Concepts</p><h2>Six marks</h2>
      <p class="lede">Ranked. Concept 01 is the recommendation; 02 is the one you'll
        use most often day to day.</p></div></div>
    <div class="grid-2" style="gap:var(--s3)">{''.join(cards)}</div>
  </div>
</section>

<section class="pad">
  <div class="wrap-wide">
    <div class="shead"><div><p class="eyebrow">Motion</p><h2>The 3D mark</h2>
      <p class="lede">The extrusion below is built from the same letterform outlines as
        the flat logos, so the 3D version and the print version are literally the same
        geometry. It's live on the home page hero.</p></div></div>
    <div style="aspect-ratio:16/9;background:var(--ink-950);border:1px solid rgba(242,237,225,.14);
                border-radius:var(--r-md);overflow:hidden;position:relative">
      <canvas id="logo3d-demo" style="width:100%;height:100%;display:block"></canvas>
    </div>
    <p style="color:var(--bone-mute);font-size:.92rem;margin-top:.75rem">
      Bone faces, moss edges, amber blade. The terrain underneath grades itself flat over
      the first few seconds — clearing, in motion. Pauses when off screen, and renders a
      static frame for anyone with reduced-motion enabled.</p>
  </div>
</section>

<section class="pad bg-850">
  <div class="wrap-wide">
    <div class="grid-2" style="align-items:start">
      <div>
        <p class="eyebrow">Palette</p><h2 style="margin-bottom:1.5rem">Six colours</h2>
        <div class="swatches">{sw}</div>
        <p style="color:var(--bone-mute);font-size:.92rem;margin-top:1rem">
          Amber is reserved for actions. The moment it appears somewhere decorative,
          it stops meaning "click this."</p>
      </div>
      <div>
        <p class="eyebrow">Typography</p><h2 style="margin-bottom:1.5rem">Two faces</h2>
        <div style="border:1px solid rgba(242,237,225,.14);border-radius:var(--r-md);padding:var(--s3)">
          <p style="font-family:var(--font-display);font-weight:700;font-size:3.6rem;
                    line-height:.95;text-transform:uppercase;margin:0">Barlow<br>Condensed</p>
          <p style="color:var(--bone-mute);font-size:.92rem;margin-top:.75rem">
            Headlines, buttons, labels. Chosen because it is the closest live typeface
            to the lettering already in your logos — so the new system reads as a
            sharpening of what you have, not a replacement.</p>
        </div>
        <div style="border:1px solid rgba(242,237,225,.14);border-radius:var(--r-md);
                    padding:var(--s3);margin-top:1rem">
          <p style="font-size:1.5rem;margin:0">Barlow — body copy</p>
          <p style="color:var(--bone-mute);font-size:.92rem;margin-top:.75rem">
            Same family, normal width. Set at 17px with 1.65 line height for comfortable
            reading on a phone in a truck.</p>
        </div>
        <p style="color:var(--bone-mute);font-size:.86rem;margin-top:1rem">
          Both are open-licence and self-hosted on this site — no Google Fonts request,
          no external dependency, no tracking.</p>
      </div>
    </div>
  </div>
</section>

<section class="pad bg-moss">
  <div class="wrap tc">
    <h2>Pick a direction and we'll build it out.</h2>
    <p class="lede mx mt-2" style="color:var(--bone-dim)">
      The chosen mark gets the full set — colour, one-colour, reversed, favicon,
      social avatar, and print-ready files.</p>
  </div>
</section>

<script type="module">
  import {{ mountLogo3D }} from './assets/js/logo3d.js';
  const c = document.getElementById('logo3d-demo');
  if (c) mountLogo3D(c, {{ terrain: true }});
</script>
""" + footer()


# ────────────────────────────────────────────────────────────── write
PAGES = {
    "index.html": page_index,
    "services.html": page_services,
    "work.html": page_work,
    "service-area.html": page_area,
    "about.html": page_about,
    "contact.html": page_contact,
    "logos.html": page_logos,
}


def main():
    sys.path.insert(0, os.path.dirname(__file__))
    for name, fn in PAGES.items():
        html = fn()
        p = os.path.join(ROOT, name)
        with open(p, "w") as f:
            f.write(html)
        print(f"{os.path.getsize(p):>8,}  {name}")

    # robots + sitemap
    urls = "".join(
        f"<url><loc>{BIZ['url']}/{'' if n == 'index.html' else n}</loc>"
        f"<changefreq>monthly</changefreq>"
        f"<priority>{'1.0' if n == 'index.html' else '0.8'}</priority></url>"
        for n in PAGES)
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                + urls + "</urlset>")
    with open(os.path.join(ROOT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {BIZ['url']}/sitemap.xml\n")
    print("          sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
