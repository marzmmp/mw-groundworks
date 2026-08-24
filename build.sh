#!/usr/bin/env bash
# Assemble the deployable site into dist/.
#
# Why this exists: the repo root also holds brand-test pages, a large unused
# video and 3D helper scripts. Deploying the root republishes all of it, which
# is how logos.html and sting.html ended up publicly reachable. dist/ is the
# only thing that should ever be uploaded.
#
#   ./build.sh && npx wrangler pages deploy dist --project-name=mw-groundworks
set -euo pipefail
cd "$(dirname "$0")"

PAGES=(index.html about.html services.html work.html service-area.html contact.html 404.html)
META=(_headers _redirects robots.txt sitemap.xml)

rm -rf dist
mkdir -p dist/assets

for f in "${PAGES[@]}"; do cp "$f" "dist/$f"; done
for f in "${META[@]}"; do [ -f "$f" ] && cp "$f" "dist/$f"; done

for d in css fonts logos; do
  [ -d "assets/$d" ] && cp -R "assets/$d" "dist/assets/$d"
done

# images: WebP only — the JPEG originals stay in the repo as masters
mkdir -p dist/assets/img
find assets/img -type f ! -iname '*.jpg' ! -iname '*.jpeg' -print0 \
  | while IFS= read -r -d '' f; do
      mkdir -p "dist/$(dirname "$f")"
      cp "$f" "dist/$f"
    done

# The two grass shader textures ship as-is: they are the fallback behind the
# inlined data URIs, and a fallback that 404s is not a fallback.
cp assets/img/blade_diffuse.jpg dist/assets/img/
cp assets/img/blade_alpha.jpg dist/assets/img/

# JS: only files the production pages actually reference
mkdir -p dist/assets/js
# Follow the import graph transitively. Scanning only the HTML would ship
# hero-grass.js without the four modules it imports, and the hero would 404.
python3 - "${PAGES[@]}" <<'PYRESOLVE'
import os, re, shutil, sys

pages = sys.argv[1:]
ref = re.compile(r'assets/(?:js|vendor)/[A-Za-z0-9._/-]+\.js')
imp = re.compile(
    r"""(?:from\s*|import\s*)['"]([^'"]+\.js)['"]"""
)

queue = []
for p in pages:
    if os.path.isfile(p):
        with open(p, encoding='utf-8', errors='replace') as fh:
            queue += ref.findall(fh.read())

seen = set()
while queue:
    rel = os.path.normpath(queue.pop())
    if rel in seen or not os.path.isfile(rel):
        continue
    seen.add(rel)
    with open(rel, encoding='utf-8', errors='replace') as fh:
        body = fh.read()
    base = os.path.dirname(rel)
    for target in imp.findall(body):
        if target.startswith('.'):
            queue.append(os.path.normpath(os.path.join(base, target)))

for rel in sorted(seen):
    dest = os.path.join('dist', rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy2(rel, dest)

print(f"  js graph: {len(seen)} modules shipped")
PYRESOLVE

# Pages Functions: the same-origin lead endpoint ships with the assets
if [ -d functions ]; then cp -R functions dist/functions; fi

# no video ships: nothing references it and it is 4.1MB
if [ -d dist/assets/video ]; then rm -rf dist/assets/video; fi

echo "dist/ built — $(find dist -type f | wc -l | tr -d ' ') files, $(du -sh dist | cut -f1)"
echo "js: hero grass scene + main.js"

# guardrails: fail loudly rather than quietly shipping a regression
fail=0
grep -q 'data-endpoint="/api/quote"' dist/contact.html || { echo "FAIL: contact form endpoint not wired"; fail=1; }
[ -f dist/assets/js/hero-grass.js ] || { echo "FAIL: hero module missing from dist"; fail=1; }
[ -f dist/assets/vendor/three.module.js ] || { echo "FAIL: three.js missing from dist"; fail=1; }
grep -q 'id="hero3d"' dist/index.html || { echo "FAIL: hero canvas missing from home page"; fail=1; }
[ -f dist/functions/api/quote.js ] || { echo "FAIL: lead endpoint missing from dist"; fail=1; }
[ -f dist/functions/_middleware.js ] || { echo "FAIL: www-to-apex middleware missing from dist"; fail=1; }
[ -e dist/logos.html ] && { echo "FAIL: logos.html would be published"; fail=1; }
[ -e dist/sting.html ] && { echo "FAIL: sting.html would be published"; fail=1; }
[ -e dist/assets/video ] && { echo "FAIL: video would be published"; fail=1; }
[ -e dist/404.html ] || { echo "FAIL: 404.html missing"; fail=1; }
# blade_*.jpg are shader textures, not photographic masters: they are the
# fallback for the inlined data URIs, so they are meant to ship.
find dist/assets/img -iname '*.jpg' ! -iname 'blade_*.jpg' | grep -q . && { echo "FAIL: JPEG masters would be published"; fail=1; }
grep -qE 'href="[A-Za-z0-9._/-]+\.html"' dist/index.html && { echo "FAIL: internal .html links (cost a 308 hop)"; fail=1; }

# Every asset path referenced from shipped JS must exist in dist/.
#
# This guardrail exists because the hero grass shipped with its blade textures
# stripped. grass.js asked for assets/img/blade_alpha.jpg; the image step
# publishes WebP only, so it 404'd, the alpha channel sampled as 0, and the
# fragment shader's `if (alpha < 0.15) discard` threw away all 190000 blades.
# The page still looked plausible -- a green hill under a working sky -- so
# nothing caught it. Comments are stripped before scanning, so prose mentioning
# a path does not trip it.
missing=0
for js in dist/assets/js/*.js; do
  refs=$(sed -e 's://.*::' "$js" \
         | grep -oE "assets/(img|vendor|video)/[A-Za-z0-9._/-]+\.[a-z0-9]+" \
         | sort -u || true)   # grep exits 1 on no match, and the script
                              # runs under set -e -o pipefail
  for ref in $refs; do
    if [ ! -f "dist/$ref" ]; then
      echo "FAIL: $(basename "$js") references $ref, which is not in dist/"
      missing=1
    fi
  done
done
[ "$missing" = "1" ] && fail=1

if [ "$fail" -eq 0 ]; then
  echo "guardrails: all pass"
else
  echo "guardrails: FAILED"
  exit 1
fi
