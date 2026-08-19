# M&W GroundWorks — website & brand identity

Static site. No build step, no framework, no external requests at runtime.
Upload the contents of this folder to any host and it works.

---

## Quick start

Open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8000
# → http://localhost:8000
```

> **Serve it, don't double-click it.** The 3D hero is an ES module, and browsers
> block ES modules and web fonts on `file://` for security reasons. Any host —
> Netlify, Cloudflare Pages, Vercel, GitHub Pages, or ordinary shared hosting —
> works with zero configuration.

---

## What's here

```
index.html          Home
services.html       All nine services, grouped Clear / Build / Maintain
work.html           Before-and-after sliders + job photo gallery
service-area.html   Jefferson County towns + seasonal booking calendar
about.html          Company, process, equipment
contact.html        Multi-step quote form
logos.html          Brand deliverable — six logo concepts, palette, type
sitemap.xml         Ready for Google Search Console
robots.txt

assets/
  css/style.css     Whole design system, one file
  js/main.js        Nav, scroll reveals, slider, quote form
  js/logo3d.js      Three.js hero mark
  js/mw-path.js     The M&W letterform outline, shared by the 2D and 3D marks
  logos/*.svg       13 logo files — see below
  fonts/*.woff2     Barlow + Barlow Condensed, self-hosted
  vendor/           Three.js + SVGLoader
  video/            Animated logo stings (MP4 / WebM) + poster frames
```

---

## The logo files

Every letterform is **converted to outlines**, so these open correctly in
Illustrator, Affinity, Inkscape, Canva, a vinyl cutter or an embroidery
digitiser with no font installed anywhere.

| File | What it's for |
|---|---|
| `01-groundline-badge.svg` | **Recommended primary mark.** Truck doors, signage, apparel |
| `02-the-cut.svg` | Horizontal lockup — website header, cards, letterhead |
| `03-strata-stack.svg` | Social posts and ads |
| `04-bucket-mark.svg` | App icon, stamp, embroidery |
| `05-section-rule.svg` | Estimates, invoices, contracts |
| `06-the-seal.svg` | Hats, patches, round social avatars |
| `*-1c.svg` | One-colour versions — engraving, stencils, single-colour print |
| `favicon.svg` | Browser tab |
| `nav-lockup.svg` | Site header and footer |

Pick a direction and the rest of the set — reversed, greyscale, CMYK, EPS,
PNG at every size — gets built out from it.

---

## Before it goes live — five things

These are the *only* outstanding items. Everything else is finished.

1. **Photos.** Every image slot is a labelled placeholder cropped to the final
   layout. Real photos of your machines, your dirt and your finished walls drop
   straight in. This is by far the biggest single upgrade available to the site.
2. **Insurance wording.** Missouri has **no statewide licence** for landscaping
   or masonry, so "Licensed" is either meaningless or misleading here. Use
   **"Fully Insured"** on its own — and only once general liability coverage is
   confirmed. If you hold a Missouri Dept. of Agriculture Commercial Applicator
   licence (required if you spray brush killer on a customer's property for pay),
   name it specifically with the certificate number. That beats a vague badge.
3. **Reviews.** The review slots are empty by design. Connect a live Google
   review widget once the Business Profile has real reviews. Don't hand-write
   testimonials and don't add `aggregateRating` markup with invented numbers —
   Google issues manual actions for it, and the FTC's 2024 fake-review rule
   carries per-violation penalties.
4. **Numbers.** Years in business, properties finished and acres cleared are
   blank on the About page. Fill them with figures you can defend.
5. **The quote form** currently validates and confirms but doesn't send. See
   below.

---

## Connecting the quote form

The form in `contact.html` is fully working front-end: three steps, validation,
error states, focus management and a success screen. It just needs somewhere to
post. Pick whichever is easiest:

**Formspree / Basin / Web3Forms** — no server needed:

```html
<!-- in contact.html, on the <form> tag -->
<form class="quote" data-steps novalidate
      action="https://formspree.io/f/YOUR_ID" method="POST">
```

Then in `assets/js/main.js`, replace the simulated submit inside
`form.addEventListener('submit', …)` with a real one:

```js
fetch(form.action, { method: 'POST', body: new FormData(form),
                     headers: { Accept: 'application/json' } })
  .then(function (r) { if (!r.ok) throw new Error(r.status); showDone(); })
  .catch(function () {
    btn.disabled = false; btn.textContent = 'Send my request';
    alert('That didn\'t send. Please call (314) 634-6630.');
  });
```

**Netlify Forms** — add `netlify` and a hidden `form-name` field to the `<form>`
tag; Netlify handles the rest with no JavaScript changes.

Whichever you choose, forward submissions to a phone that gets checked. Research
on home-services leads is consistent: responding within five minutes rather than
thirty makes contact roughly **100× more likely**, and about **78% of customers
buy from whoever responds first**. The form is worth exactly as much as the
speed of the callback behind it.

---

## Local SEO checklist

Structured data is already on every page — `LocalBusiness` / `GeneralContractor`
with the full service catalogue, per-service `Service` nodes, `BreadcrumbList`
and `FAQPage`. Remaining setup is off-site:

- [ ] Register the domain and update `BIZ["url"]` in `tools/content.py`, then rebuild
- [ ] Create the Google Business Profile as a **service-area business** —
      address hidden, service areas set by town
- [ ] Primary GBP category: **Landscaper** or **Excavating contractor** (this is
      the single strongest ranking lever). Secondaries: Lawn care service, Land
      clearing service, Masonry contractor, Deck builder, Junk removal service
- [ ] Keep the name, address and phone **byte-identical** everywhere — site,
      schema, GBP, Facebook, Yelp, Angi, Bing Places, Apple Business Connect.
      "MO" vs "Missouri" and `(314) 634-6630` vs `314-634-6630` both count as
      mismatches to the aggregators
- [ ] Submit `sitemap.xml` in Google Search Console
- [ ] Post to the Business Profile weekly with real job photos

---

## Rebuilding

The HTML is generated, so shared markup only has to change in one place.

```bash
python3 tools/build_site.py     # regenerate all 7 pages + sitemap + robots
python3 tools/make_logos.py     # regenerate the 13 SVG logo files
node    tools/audit.js          # contrast, overflow, links, headings, tap targets
node    tools/interact.js       # 36 functional tests
node    tools/render_sting.js   # re-render the animated logo videos
```

Content lives in `tools/content.py` — services, towns, seasonal calendar, FAQ.
Edit there and rebuild; you never touch HTML by hand.

You can also just edit the HTML directly if you prefer. Nothing depends on the
build script at runtime.

---

## Accessibility & performance

Verified in-browser at 1440 / 834 / 390 px, not assumed:

- WCAG AA contrast on every text/background pair on every page (checked with
  alpha compositing, not just declared colours)
- One `h1` per page, no heading-level skips
- Skip link, visible focus rings, full keyboard operation
- 44px+ tap targets throughout
- `prefers-reduced-motion` fully respected — the 3D mark renders a static frame,
  all reveals are instant
- No horizontal overflow at any breakpoint
- No console errors
- `<noscript>` fallback so nothing is invisible without JavaScript
- Fonts and Three.js are self-hosted — **zero third-party requests**, so no
  Google Fonts call, no CDN, no tracking, and nothing to break when someone
  else's service goes down
- The hero's WebGL loop pauses when scrolled out of view or the tab is hidden
