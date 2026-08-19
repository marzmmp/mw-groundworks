M&W GROUNDWORKS — HANDOFF PACKAGE
=================================

FOR CLAUDE DESIGN (or any AI/developer picking this up):

  1. Open  START-HERE-PROMPT.md  and paste its contents as your first message.
  2. Attach this whole zip.

That's it. Everything else is explained in DESIGN-NOTES.md.


WHAT'S IN HERE
--------------
START-HERE-PROMPT.md    the prompt to paste. Start here.
DESIGN-NOTES.md         architecture, design tokens, traps, open items.
website/                the real site. Seven pages. Serve it, don't
                        double-click it (see below).
tools/                  the generators and the test suite. The HTML is
                        GENERATED — edit tools/content.py, not the HTML.
single-file/index.html  self-contained copy that opens with no server.
                        For looking at only; do not publish it.
original-shader/        the grass shader source this was built from.
MW-GroundWorks-Logo-Concepts.html   the six logo directions. Double-click it.


TO RUN IT
---------
    cd website
    python3 -m http.server 8000
    ...then open http://localhost:8000

A web server is required. Opening index.html straight off the disk will look
broken — browsers block web fonts and 3D code on file:// URLs. That's a
security rule, not a bug, and it disappears once the files are hosted.

To put it online right now: go to netlify.com/drop and drag the "website"
folder onto the page. Free, no account, live in about ten seconds.


TO REBUILD / TEST
-----------------
    python3 tools/build_site.py          regenerate all 7 pages
    python3 tools/make_logos.py          regenerate the 13 logo SVGs
    python3 tools/make_grass_module.py   regenerate the grass shader module

    node tools/audit.js                  contrast, overflow, links, a11y
    node tools/interact.js               36 functional tests
    node tools/daylight_check.js         legibility at 17 hours of the day

The three test scripts need the site served on port 8787, plus:
    npm i playwright pngjs
All three pass as shipped. Please keep them passing.
