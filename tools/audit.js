/* Render + audit every page: console errors, layout overflow, contrast,
   link integrity, heading order, tap-target size, and screenshots. */
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');

const SITE = path.resolve(__dirname, '..', 'website');
const OUT = path.resolve(__dirname, '..', 'shots');
const BASE = process.env.BASE || 'http://127.0.0.1:8787';
fs.mkdirSync(OUT, { recursive: true });

const PAGES = ['index.html', 'services.html', 'work.html', 'service-area.html',
  'about.html', 'contact.html', 'logos.html'];
const VIEWS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'tablet', width: 834, height: 1112 },
  { name: 'mobile', width: 390, height: 844 },
];

function parse(c) { const m = (c || '').match(/[\d.]+/g); return m ? m.map(Number) : null; }
// composite a possibly-translucent colour over an opaque backdrop
function over(fg, bg) {
  const f = parse(fg), b = parse(bg);
  if (!f) return bg; const a = f.length > 3 ? f[3] : 1;
  if (a >= 1) return `rgb(${f[0]}, ${f[1]}, ${f[2]})`;
  return `rgb(${f.slice(0,3).map((v,i)=>Math.round(v*a + b[i]*(1-a))).join(', ')})`;
}
function lum(hex) {
  const m = hex.match(/\d+(\.\d+)?/g).map(Number);
  const [r, g, b] = m.slice(0, 3).map(v => {
    v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
function ratio(a, b) {
  const l1 = lum(a), l2 = lum(b);
  return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
}

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--no-sandbox', '--use-gl=swiftshader', '--enable-unsafe-swiftshader'],
  });
  const report = { errors: [], overflow: [], contrast: [], links: [], headings: [], taps: [], webgl: {} };

  for (const view of VIEWS) {
    const ctx = await browser.newContext({ viewport: { width: view.width, height: view.height }, deviceScaleFactor: 1 });
    for (const p of PAGES) {
      const page = await ctx.newPage();
      const errs = [];
      page.on('console', m => { if (m.type() === 'error') errs.push(`${p} [${view.name}] ${m.text()}`); });
      page.on('pageerror', e => errs.push(`${p} [${view.name}] PAGEERROR ${e.message}`));
      await page.goto(BASE + '/' + p, { waitUntil: 'networkidle' });
      await page.waitForTimeout(view.name === 'desktop' ? 2600 : 1200);
      await page.evaluate(async () => {
        const H = document.body.scrollHeight, step = window.innerHeight * 0.8;
        for (let y = 0; y < H; y += step) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 90)); }
        window.scrollTo(0, 0); await new Promise(r => setTimeout(r, 400));
      });
      await page.waitForTimeout(500);
      report.errors.push(...errs);

      // horizontal overflow
      const ov = await page.evaluate(() => {
        const vw = document.documentElement.clientWidth;
        const bad = [];
        document.querySelectorAll('body *').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.width === 0 && r.height === 0) return;
          if (r.right > vw + 1.5 || r.left < -1.5) {
            const st = getComputedStyle(el);
            if (st.position === 'fixed') return;
            bad.push({ tag: el.tagName.toLowerCase(), cls: el.className && String(el.className).slice(0, 46), right: Math.round(r.right), left: Math.round(r.left) });
          }
        });
        return { vw, scrollW: document.documentElement.scrollWidth, bad: bad.slice(0, 8) };
      });
      if (ov.scrollW > ov.vw + 1) report.overflow.push({ page: p, view: view.name, ...ov });

      if (view.name === 'desktop') {
        // contrast sample of visible text
        const samples = await page.evaluate(() => {
          const out = [];
          const seen = new Set();
          document.querySelectorAll('p,a,li,h1,h2,h3,h4,span,label,summary,figcaption,legend,code,b').forEach(el => {
            if (!el.textContent.trim()) return;
            const r = el.getBoundingClientRect();
            if (r.width < 4 || r.height < 4) return;
            const st = getComputedStyle(el);
            if (st.visibility === 'hidden' || st.opacity === '0') return;
            // walk up for an opaque background
            const stack = []; let n = el, bg = 'rgb(11, 15, 12)';
            while (n) { const c = getComputedStyle(n).backgroundColor;
              if (c && !c.startsWith('rgba(0, 0, 0, 0')) stack.unshift(c); n = n.parentElement; }
            bg = stack.length ? stack.join('|') : 'rgb(11, 15, 12)';
            const key = st.color + '|' + bg + '|' + st.fontSize + '|' + st.fontWeight;
            if (seen.has(key)) return; seen.add(key);
            out.push({ color: st.color, bg, size: parseFloat(st.fontSize), weight: st.fontWeight, sample: el.textContent.trim().slice(0, 40), tag: el.tagName });
          });
          return out;
        });
        samples.forEach(s => {
          let bg = 'rgb(11, 15, 12)';
          String(s.bg).split('|').forEach(layer => { bg = over(layer, bg); });
          s.bg = bg;
          const cr = ratio(over(s.color, bg), bg);
          const large = s.size >= 24 || (s.size >= 18.66 && parseInt(s.weight) >= 700);
          const need = large ? 3.0 : 4.5;
          if (cr < need) report.contrast.push({ page: p, ...s, ratio: +cr.toFixed(2), need });
        });

        // links
        const links = await page.evaluate(() => Array.from(document.querySelectorAll('a[href]'))
          .map(a => ({ href: a.getAttribute('href'), text: a.textContent.trim().slice(0, 30), hasLabel: !!(a.textContent.trim() || a.getAttribute('aria-label')) })));
        links.forEach(l => {
          if (!l.hasLabel) report.links.push({ page: p, issue: 'no accessible name', href: l.href });
          if (l.href.startsWith('#') || l.href.startsWith('tel:') || l.href.startsWith('sms:') || l.href.startsWith('http')) return;
          const [f, hash] = l.href.split('#');
          if (f && !fs.existsSync(path.join(SITE, f))) report.links.push({ page: p, issue: 'missing target', href: l.href });
        });

        // heading order
        const hs = await page.evaluate(() => Array.from(document.querySelectorAll('h1,h2,h3,h4,h5,h6')).map(h => +h.tagName[1]));
        let h1 = hs.filter(x => x === 1).length;
        if (h1 !== 1) report.headings.push({ page: p, issue: `h1 count = ${h1}` });
        for (let i = 1; i < hs.length; i++) if (hs[i] - hs[i - 1] > 1) report.headings.push({ page: p, issue: `h${hs[i - 1]} -> h${hs[i]} skip` });

        // webgl canvas actually painted?
        const cv = await page.$('canvas');
        if (cv) {
          const box = await cv.boundingBox();
          const dims = await page.evaluate(() => { const c = document.querySelector('canvas'); return { w: c.width, h: c.height }; });
          const buf = await cv.screenshot();
          // count distinct colours: a live WebGL scene has many, a blank canvas ~1
          const sig = new Set();
          for (let i = 0; i < buf.length - 3; i += 997) sig.add(buf[i] + ',' + buf[i + 1] + ',' + buf[i + 2]);
          report.webgl[p] = { ok: sig.size > 30, colours: sig.size, cssW: Math.round(box.width), bufW: dims.w, bufH: dims.h };
        }
      }

      if (view.name === 'mobile') {
        const taps = await page.evaluate(() => {
          const bad = [];
          document.querySelectorAll('a,button,input,select,summary').forEach(el => {
            const r = el.getBoundingClientRect();
            if (r.width < 2 || r.height < 2) return;
            if (getComputedStyle(el).opacity === '0') return;
            if (r.height < 40 && el.closest('.nav-links, .actionbar, .btn-row, form')) {
              bad.push({ tag: el.tagName, t: el.textContent.trim().slice(0, 22), h: Math.round(r.height) });
            }
          });
          return bad.slice(0, 10);
        });
        taps.forEach(t => report.taps.push({ page: p, ...t }));
      }

      await page.screenshot({ path: path.join(OUT, `${p.replace('.html', '')}-${view.name}.png`), fullPage: view.name === 'desktop' });
      await page.close();
    }
    await ctx.close();
  }
  await browser.close();
  fs.writeFileSync(path.join(__dirname, '..', 'audit.json'), JSON.stringify(report, null, 1));

  const n = o => Array.isArray(o) ? o.length : Object.keys(o).length;
  console.log('console errors :', n(report.errors));
  report.errors.slice(0, 12).forEach(e => console.log('   ', e));
  console.log('overflow       :', n(report.overflow));
  report.overflow.forEach(o => console.log('   ', o.page, o.view, o.scrollW + '>' + o.vw, JSON.stringify(o.bad.slice(0, 3))));
  console.log('contrast fails :', n(report.contrast));
  report.contrast.slice(0, 14).forEach(c => console.log('   ', c.page, c.ratio + '<' + c.need, c.size + 'px', c.color, 'on', c.bg, '|', c.sample));
  console.log('link issues    :', n(report.links));
  report.links.slice(0, 10).forEach(l => console.log('   ', l.page, l.issue, l.href));
  console.log('heading issues :', n(report.headings));
  report.headings.slice(0, 10).forEach(h => console.log('   ', h.page, h.issue));
  console.log('small taps     :', n(report.taps));
  report.taps.slice(0, 10).forEach(t => console.log('   ', t.page, t.tag, t.h + 'px', t.t));
  console.log('webgl          :', JSON.stringify(report.webgl));
})();
