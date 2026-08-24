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

# JS: only files the production pages actually reference
mkdir -p dist/assets/js
REFS=$(cat "${PAGES[@]}" | grep -oE 'assets/(js|vendor)/[A-Za-z0-9._/-]+\.js' | sort -u || true)
for r in $REFS; do
  if [ -f "$r" ]; then
    mkdir -p "dist/$(dirname "$r")"
    cp "$r" "dist/$r"
  fi
done

# no video ships: nothing references it and it is 4.1MB
if [ -d dist/assets/video ]; then rm -rf dist/assets/video; fi

echo "dist/ built — $(find dist -type f | wc -l | tr -d ' ') files, $(du -sh dist | cut -f1)"
echo "js included: ${REFS:-none}"

# guardrails: fail loudly rather than quietly shipping a regression
fail=0
grep -q 'data-endpoint="https://' dist/contact.html || { echo "FAIL: contact form endpoint is empty"; fail=1; }
grep -qE 'hero3d|preset-switch|tod-hour' dist/index.html && { echo "FAIL: dev hero artefacts present"; fail=1; }
[ -e dist/logos.html ] && { echo "FAIL: logos.html would be published"; fail=1; }
[ -e dist/sting.html ] && { echo "FAIL: sting.html would be published"; fail=1; }
[ -e dist/assets/video ] && { echo "FAIL: video would be published"; fail=1; }
[ -e dist/404.html ] || { echo "FAIL: 404.html missing"; fail=1; }
find dist/assets/img -iname '*.jpg' | grep -q . && { echo "FAIL: JPEG masters would be published"; fail=1; }
grep -qE 'href="[A-Za-z0-9._/-]+\.html"' dist/index.html && { echo "FAIL: internal .html links (cost a 308 hop)"; fail=1; }

[ "$fail" -eq 0 ] && echo "guardrails: all pass" || { echo "guardrails: FAILED"; exit 1; }
