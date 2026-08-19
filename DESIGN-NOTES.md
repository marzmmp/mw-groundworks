# M&W GroundWorks — design & engineering notes

Everything a new session needs to pick this up without re-deriving it.

---

## The business (all verified — do not embellish)

- **M&W GroundWorks** · (314) 634-6630
  *(314 is St. Louis City; the county itself is 636/573. A 636 number as a
  secondary display number would read more local — but never swap the primary.)*
- **Jefferson County, Missouri.** County seat Hillsboro. Pop. ~226,700 (2020),
  656 sq mi, 82.2% owner-occupied, median home value $237,200.
  Coordinates used throughout: **38.2306, -90.5626**. Timezone America/Chicago.
- **Nine services:** land clearing, brush clearing, ditch clearing, retaining
  walls, brick & masonry, decks/outdoor construction, lawn care & yard
  management, junk removal, general property maintenance.
- **Tagline:** "Clear. Build. Maintain." — maps 1:1 to the three service
  families and is structural throughout the site, not decoration.

---

## Design system

**Palette — sampled from the client's own existing logo files, not invented.**

| Token | Hex | Use |
|---|---|---|
| ink-900 | `#0B0F0C` | Page base |
| ink-850 | `#101610` | Alternating sections |
| bone | `#F2EDE1` | Primary text, the M&W wordmark |
| bone-dim | `#CFC8B8` | Secondary text |
| bone-mute | `#9A9382` | Tertiary text |
| moss-500 | `#7A9A3E` | The brand green |
| moss-400 | `#9AB85F` | Eyebrows, small accents |
| moss-300 | `#BDD48E` | Hero accent line *(moss-400 fails contrast there)* |
| moss-800 | `#33461B` | Section fills, trust bar |
| **amber-500** | `#E8A33D` | **Calls to action only** |

Amber is reserved exclusively for actions. The moment it appears as decoration
it stops meaning "press this."

**Type:** Barlow Condensed (display) / Barlow (body), self-hosted woff2. Chosen
because Barlow Condensed is the closest live typeface to the lettering already
in the client's logos — the system reads as a sharpening of what they have.

**Spacing:** 8pt scale, `--s1` … `--s8`.

---

## Architecture

```
website/
  *.html              generated — never hand-edit
  assets/css/style.css    whole design system, one file
  assets/js/
    main.js           nav, scroll reveals, before/after slider, quote form
    hero-grass.js     the hero scene (composes the two below)
    grass.js          GENERATED — instanced grass shader
    daycycle.js       solar position + interpolated looks
    mark3d.js         the extruded M&W mark
    mw-path.js        the M&W letterform outline
  assets/fonts/       self-hosted woff2
  assets/img/         blade textures for the grass
  assets/vendor/      Three.js + SVGLoader
  assets/logos/       13 SVGs, letterforms converted to outlines
tools/
  build_site.py       generates all 7 pages + sitemap + robots
  content.py          ALL copy, services, towns, seasonal calendar, FAQ
  make_grass_module.py  generates grass.js from the original shader source
  make_logos.py       generates the 13 logo SVGs
  make_offline.py     builds the single-file previews
  audit.js / interact.js / daylight_check.js   the test suite
```

The logo SVGs and the 3D mark share one source of geometry (`mw-path.js`), so
the printed logo and the animated one are literally the same letterforms.

---

## The hero day cycle

`daycycle.js` runs a NOAA solar-position algorithm from a UTC instant plus the
business's lat/lon. Because it's anchored to the *place*, a visitor in Sydney
sees Missouri's sky. Verified with a Sydney-timezone browser context.

Six looks keyed by **sun elevation**, not clock hour — night (-18°), twilight
(-6°), dusk (0°), goldenHour (8°), morning (22°), daylight (55°) — smoothstep
interpolated between. Colours are mixed in squared space so dark→bright ramps
don't go muddy. Seasons work for free.

Each look also carries a **`scrim` value** → `--scrim-k` CSS var → multiplies
the hero overlay's alpha. This is what makes the whole idea viable instead of a
legibility disaster.

### Non-obvious things learned the hard way

- **Golden hour needs a *heavier* scrim than midday.** A low sun blooms straight
  through the copy column. Average sky brightness is the wrong signal. Before
  this was fixed, golden hour measured **1.18:1** on the accent line — worse
  than noon by a wide margin.
- **The scrim must have no straight edge.** The first version used a horizontal
  gradient with a shoulder in it; that shoulder read as the image being sliced,
  and it landed on the M. It's now a single wide ellipse anchored on the copy,
  plus text-shadow halos on the type so the panel can stay soft.
- **`tipColor` can't retint the grass.** The blade tips are dominated by the
  diffuse photo texture. There's a `uGrade` uniform — the one deliberate
  addition to the reference shader — that multiplies the final colour. Each
  look carries a `grade`.
- **Fit the mark by measuring, not by assuming.** The mark sits nearer the
  camera than the focal plane, so world-unit estimates under-predict its
  on-screen size badly. `fitMark()` projects the real bounding box and solves
  for the scale. An earlier version lost this code entirely and used a fixed
  scale — it looked fine on desktop and was badly cropped on phones.

### Performance

The scene is fill-bound: hundreds of thousands of alpha-tested blade fragments.
Rather than sniff the user agent, `hero-grass.js` measures its own frame time
and steps down a ladder — pixel ratio first (biggest win per unit of visual
loss), then blade density via `geometry.instanceCount`, which is free to change
and thins the field uniformly because blades are generated in random order. A
single frame over 150ms drops straight to the floor tier instead of creeping.

Verified under software rendering: 55k → 9.9k blades and 1.0 → 3.9fps within
about four seconds, still composed.

---

## Other traps already fixed — don't reintroduce

- **The WebGL loop starves IntersectionObserver.** Its callbacks coalesce to the
  final scroll position, so fast scrolling skipped elements and left content
  permanently invisible. Scroll reveals now use a synchronous
  timestamp-throttled rect sweep with no lower bound, plus a 6s failsafe and a
  `<noscript>` fallback.
- **`.nav-links a` / `.foot a` (0,1,1) out-specify `.btn-*` (0,1,0)** and were
  repainting button text to 1.29:1. Guard rules sit at the end of the stylesheet.
- **The single-file build has no `import.meta.url`.** Grass textures are injected
  via `window.__MW_GRASS_TEX` as data URIs in that build.

---

## Compliance — deliberately not asserted

Missouri has **no statewide licence** for landscaping or masonry; only
electrical is licensed at state level. "Licensed" is therefore either
meaningless or misleading here.

The site never claims: licences, bonding, BBB accreditation, Google Guaranteed,
Angi Certified, ISA/NCMA/ICPI credentials, review counts, `aggregateRating`,
years in business, or job counts. Each renders as a visible amber placeholder
notice instead — see `CLIENT_TODO` in `tools/content.py`.

Genuine differentiators that *are* surfaced, because they're true and useful:
Jefferson County land-disturbance permit thresholds (~5,000 sq ft / 1 acre /
5 ft cut-or-fill), retaining walls over 4 ft needing a PE stamp in this region,
and the MDA Commercial Applicator licence required if they spray brush killer
for pay.

**Please don't add trust badges or testimonials to make the page feel fuller.**

---

## Verification status

| Check | Result |
|---|---|
| `audit.js` | 0 console errors, 0 overflow, 0 contrast fails, 0 link/heading issues, 0 undersized taps |
| `interact.js` | 36/36 |
| `daylight_check.js` | 17/17 hours pass WCAG AA · worst case 7.95:1 vs a 3.0 requirement |
| Breakpoints | 1440 / 834 / 430 / 390 / 360 |
| Offline single-file build | 0 errors from `file://` |

`daylight_check.js` masks where the glyphs actually are and reads the background
directly beneath them. An earlier version sampled the whole text block and was
catching bright sky *beside* short lines — it under-reported by roughly 2×.

---

## Open items

1. **Pick a logo direction** → build out the full set from it. *(Blocking.)*
2. **Decide on the day cycle** — keep live or pin — then delete the
   `#preset-switch` markup in `build_site.py` and `.preset-switch` in the CSS.
3. **Real job photos.** Every image is a labelled, correctly-cropped placeholder.
   This is the single biggest upgrade available to the site.
4. Confirm general liability insurance before publishing any badge.
5. Wire the quote form to a backend — recipe in `website/README.md`.
6. Fill the blank About stats with defensible numbers.
7. Register the domain, update `BIZ["url"]` in `content.py`, rebuild, and set up
   the Google Business Profile as a service-area business (primary category:
   Landscaper or Excavating contractor).
8. Optional: re-render the MP4 logo stings with the grass field behind the mark —
   `tools/render_sting.js` still uses the older low-poly terrain scene.

---

## Credits

The grass shader is a port of the **pmndrs `grass-shader` example**
(github.com/pmndrs/examples), supplied by the client via GetLayers. The GLSL is
lifted verbatim; only the surrounding plumbing was rewritten so the field could
share a scene with the mark, be tinted from the brand palette, and scale to the
device. The `uGrade` uniform is the only shader-level addition.
