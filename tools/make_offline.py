#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build double-clickable, fully self-contained copies of the site pages.

Browsers block ES modules and web fonts on file:// for security reasons, which
is why the normal site needs a web server. This inlines everything — fonts as
base64, CSS inline, and Three.js pre-bundled to a classic script — so the pages
open straight from the desktop with the 3D logo working and no internet.
"""
import base64
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
SITE = os.path.join(ROOT, "website")
OUT = os.path.join(ROOT, "preview-offline")
os.makedirs(OUT, exist_ok=True)

PAGES = ["index.html", "services.html", "work.html", "service-area.html",
         "about.html", "contact.html", "logos.html"]


def b64(path, mime):
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def build():
    with open(os.path.join(SITE, "assets/css/style.css")) as f:
        css = f.read()
    # inline the fonts the stylesheet references
    for m in set(re.findall(r"url\('\.\./fonts/([^']+)'\)", css)):
        css = css.replace(f"url('../fonts/{m}')",
                          f"url({b64(os.path.join(SITE, 'assets/fonts', m), 'font/woff2')})")

    with open(os.path.join(SITE, "assets/js/main.js")) as f:
        mainjs = f.read()
    with open("/tmp/bundle.js") as f:
        bundle = f.read()
    # the bundled classic script has no import.meta.url, so hand the grass
    # shader its blade textures explicitly, inlined as data URIs
    tex = ("<script>window.__MW_GRASS_TEX={"
           f"diffuse:'{b64(os.path.join(SITE, 'assets/img/blade_diffuse.jpg'), 'image/jpeg')}',"
           f"alpha:'{b64(os.path.join(SITE, 'assets/img/blade_alpha.jpg'), 'image/jpeg')}'"
           "};</script>")

    logos = {}
    for n in os.listdir(os.path.join(SITE, "assets/logos")):
        if n.endswith(".svg"):
            logos["assets/logos/" + n] = b64(
                os.path.join(SITE, "assets/logos", n), "image/svg+xml")

    for page in PAGES:
        with open(os.path.join(SITE, page)) as f:
            h = f.read()

        h = h.replace('<link rel="stylesheet" href="assets/css/style.css">',
                      f"<style>{css}</style>")
        h = h.replace('<link rel="preload" href="assets/fonts/barlow-condensed-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin>', "")
        h = h.replace('<link rel="preload" href="assets/fonts/barlow-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>', "")
        for src, uri in logos.items():
            h = h.replace(f'"{src}"', f'"{uri}"')
        h = h.replace('<script src="assets/js/main.js" defer></script>',
                      f"<script>{mainjs}</script>")

        # module script -> pre-bundled classic script
        boot = (tex + "<script>" + bundle + "</script>\n<script>(function(){"
                "var h=document.getElementById('hero3d');"
                "if(h&&window.__mountHeroGrass)window.__mountHeroGrass(h);"
                "var d=document.getElementById('logo3d-demo');"
                "if(d&&window.__mountLogo3D)window.__mountLogo3D(d);})();</script>")
        # lambda repl: the bundle contains regex escapes that re.sub would
        # try to interpret in a string replacement
        h = re.sub(r'<script type="module">\s*import \{ mount(?:LogoGrass|HeroGrass|Logo3D) \}.*?</script>',
                   lambda _m: boot, h, flags=re.S)

        # cross-page links point at the offline copies
        for p in PAGES:
            h = h.replace(f'href="{p}"', f'href="{p.replace(".html", "")}-offline.html"')

        banner = (
            '<div style="position:fixed;left:0;right:0;bottom:0;z-index:9999;'
            'background:#E8A33D;color:#0B0F0C;font:600 13px/1.4 system-ui,sans-serif;'
            'padding:9px 16px;text-align:center">'
            'Offline preview &mdash; everything is embedded in this one file. '
            'The real site in the ZIP is smaller and faster; upload that one.</div>')
        h = h.replace("</body>", banner + "</body>")

        out = os.path.join(OUT, page.replace(".html", "-offline.html"))
        with open(out, "w") as f:
            f.write(h)
        print(f"{os.path.getsize(out)/1024/1024:>6.1f} MB  {os.path.basename(out)}")


if __name__ == "__main__":
    build()
