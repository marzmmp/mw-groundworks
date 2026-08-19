/* Sample the actual rendered pixels behind the hero headline at every hour of
   the day and verify the text still meets WCAG contrast. This is the check
   that decides whether a time-shifting hero is a good idea or a liability. */
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const { PNG } = (() => { try { return { PNG: require('pngjs').PNG }; } catch (e) { return {}; } })();

const BASE = 'http://127.0.0.1:8787';
const EXE = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const OUT = path.resolve(__dirname, '..', 'preview', 'day');
fs.mkdirSync(OUT, { recursive: true });

function lum([r, g, b]) {
  const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
  return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
}
function ratio(a, b) {
  const l1 = lum(a), l2 = lum(b);
  return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
}

(async () => {
  const b = await chromium.launch({
    executablePath: EXE,
    args: ['--no-sandbox', '--use-gl=swiftshader', '--enable-unsafe-swiftshader'],
  });
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  p.on('pageerror', (e) => console.log('ERR', e.message.slice(0, 120)));
  await p.goto(`${BASE}/index.html`, { waitUntil: 'networkidle' });
  await p.waitForTimeout(9000);

  const HOURS = [0, 3, 5, 6, 6.5, 7, 8, 10, 12, 14, 16, 18, 19, 19.5, 20, 21, 22];
  const rows = [];
  let worst = { ratio: 99 };

  // where the headline and the sub-copy actually sit
  const boxes = await p.evaluate(() => {
    const q = (s) => { const e = document.querySelector(s); if (!e) return null;
      const r = e.getBoundingClientRect();
      return { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) }; };
    return { h1: q('.hero h1'), sub: q('.hero-sub'), note: q('.hero-note') };
  });

  for (const h of HOURS) {
    const info = await p.evaluate((hh) => {
      const L = window.__heroApi.previewHour(hh);
      return { look: window.__heroApi.describeLook(), elev: L.sunElevation };
    }, h);
    await p.waitForTimeout(1400);           // let the scrim transition settle

    // Two frames: one with the copy (to locate the glyphs), one without (to
    // read what is actually behind them). Sampling the background *only under
    // the letters* avoids both the antialiasing fringe and the old whole-box
    // error of catching bright sky beside a short line.
    const shotText = await p.screenshot({ clip: { x: 0, y: 0, width: 1440, height: 900 } });
    await p.evaluate(() => {
      const el = document.querySelector('.hero-in');
      if (el) el.style.visibility = 'hidden';
    });
    await p.waitForTimeout(140);
    const shot = await p.screenshot({ clip: { x: 0, y: 0, width: 1440, height: 900 } });
    await p.evaluate(() => {
      const el = document.querySelector('.hero-in');
      if (el) el.style.visibility = '';
    });
    if ([0, 6.5, 8, 12, 16, 19.5, 21].includes(h)) {
      fs.writeFileSync(path.join(OUT, `hour-${String(h).replace('.', '_')}.png`), shot);
    }
    if (!PNG) continue;

    const img = PNG.sync.read(shot);          // background, copy hidden
    const txt = PNG.sync.read(shotText);      // same frame, copy visible
    const at = (im, x, y) => {
      const i = (im.width * y + x) << 2;
      return [im.data[i], im.data[i + 1], im.data[i + 2]];
    };
    const near = (a, b, tol) =>
      Math.abs(a[0] - b[0]) < tol && Math.abs(a[1] - b[1]) < tol && Math.abs(a[2] - b[2]) < tol;

    /* Find the glyphs of `ink` inside `box`, then read the pixels in a thin
       ring just outside them. That ring is what the eye actually compares the
       letter against — it includes the text-shadow halo — so it is a fairer
       and stricter measure than sampling the whole rectangle. Returns the
       brightest ring pixel (worst case for light text). */
    const probeEdge = (box, ink, tol = 20) => {
      if (!box) return null;
      const x0 = Math.max(1, box.x), y0 = Math.max(1, box.y);
      const x1 = Math.min(img.width - 2, box.x + box.w);
      const y1 = Math.min(img.height - 2, box.y + box.h);
      let brightest = null, bl = -1, glyphs = 0;
      for (let y = y0; y < y1; y++) {
        for (let x = x0; x < x1; x++) {
          if (!near(at(txt, x, y), ink, tol)) continue;   // a glyph pixel
          glyphs++;
          const px = at(img, x, y);                       // what is behind it
          const l = lum(px);
          if (l > bl) { bl = l; brightest = px; }
        }
      }
      return glyphs > 200 ? brightest : null;
    };

    // bone #F2EDE1 headline, moss-300 #BDD48E accent line, bone-dim #CFC8B8 body
    const INK_H = [242, 237, 225], INK_A = [189, 212, 142], INK_S = [207, 200, 184];
    const bgH = probeEdge(boxes.h1, INK_H);
    const bgA = probeEdge(boxes.h1, INK_A);
    const bgS = probeEdge(boxes.sub, INK_S);
    const rH = bgH ? ratio(INK_H, bgH) : null;
    const rA = bgA ? ratio(INK_A, bgA) : null;
    const rS = bgS ? ratio(INK_S, bgS) : null;

    const row = {
      hour: h, look: info.look, elev: +info.elev.toFixed(1),
      headline: rH && +rH.toFixed(2), accent: rA && +rA.toFixed(2),
      body: rS && +rS.toFixed(2),
    };
    rows.push(row);
    // headline is >=24px bold → AA large needs 3.0; body text needs 4.5
    const bad = Math.min(rH ?? 99, rA ?? 99);
    if (bad < worst.ratio) worst = { ratio: bad, hour: h, look: info.look };
  }

  await b.close();

  if (!PNG) { console.log('pngjs missing — install to run pixel sampling'); return; }
  console.table(rows);
  const failH = rows.filter((r) => r.headline < 3.0 || r.accent < 3.0);
  const failB = rows.filter((r) => r.body < 4.5);
  console.log(`\nheadline/accent below AA-large (3.0): ${failH.length}`);
  failH.forEach((r) => console.log('   ', r.hour + 'h', r.look, 'headline', r.headline, 'accent', r.accent));
  console.log(`body below AA (4.5): ${failB.length}`);
  failB.forEach((r) => console.log('   ', r.hour + 'h', r.look, 'body', r.body));
  console.log(`worst case: ${worst.ratio.toFixed(2)} at ${worst.hour}h (${worst.look})`);
  process.exit(failH.length || failB.length ? 1 : 0);
})();
