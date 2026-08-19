/* Functional tests: reveal completeness, quote form flow, before/after
   slider, mobile nav, and keyboard accessibility. */
const { chromium } = require('playwright');
const path = require('path');
const BASE = 'http://127.0.0.1:8787';
const EXE = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

let pass = 0, fail = 0;
function t(name, ok, extra) {
  (ok ? pass++ : fail++);
  console.log(`${ok ? ' PASS' : '*FAIL'}  ${name}${extra ? '  — ' + extra : ''}`);
}

(async () => {
  const b = await chromium.launch({ executablePath: EXE, args: ['--no-sandbox', '--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });

  // ---------- reveal completeness on every page, desktop + mobile ----------
  for (const vp of [{ w: 1440, h: 900, n: 'desktop' }, { w: 390, h: 844, n: 'mobile' }]) {
    const ctx = await b.newContext({ viewport: { width: vp.w, height: vp.h } });
    for (const p of ['index.html', 'services.html', 'work.html', 'service-area.html', 'about.html', 'contact.html', 'logos.html']) {
      const page = await ctx.newPage();
      await page.goto(`${BASE}/${p}`, { waitUntil: 'networkidle' });
      await page.evaluate(async () => {
        const step = window.innerHeight * 0.6;
        for (let y = 0; y < document.body.scrollHeight; y += step) {
          window.scrollTo(0, y); await new Promise(r => setTimeout(r, 120));
        }
        window.scrollTo(0, document.body.scrollHeight);
      });
      await page.waitForTimeout(1200);
      const hidden = await page.evaluate(() => Array.from(document.querySelectorAll('[data-rv]'))
        .filter(e => getComputedStyle(e).opacity !== '1')
        .map(e => e.tagName + '.' + String(e.className).slice(0, 24)));
      t(`reveal complete — ${p} @${vp.n}`, hidden.length === 0, hidden.slice(0, 4).join(', '));
      await page.close();
    }
    await ctx.close();
  }

  // ---------- quote form ----------
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  await page.goto(`${BASE}/contact.html`, { waitUntil: 'networkidle' });

  t('form starts on step 1', await page.locator('.qstep').first().evaluate(e => e.classList.contains('on')));
  t('step counter reads 1 of 3', (await page.locator('.qcount').innerText()).toLowerCase().includes('1 of 3'));

  // blocked without a selection
  await page.locator('[data-next]').first().click();
  t('blocks advance with no service picked', await page.locator('[data-err="need"]').evaluate(e => e.classList.contains('on')));

  await page.locator('#need-land-clearing').check({ force: true });
  await page.locator('.qstep.on [data-next]').click();
  await page.waitForTimeout(200);
  t('advances to step 2', (await page.locator('.qcount').innerText()).toLowerCase().includes('2 of 3'));

  await page.locator('.qstep.on [data-next]').click();
  t('blocks advance with no town', await page.locator('[data-err="town"]').evaluate(e => e.classList.contains('on')));

  await page.selectOption('#q-town', 'Hillsboro');
  await page.locator('.qstep.on [data-next]').click();
  await page.waitForTimeout(200);
  t('advances to step 3', (await page.locator('.qcount').innerText()).toLowerCase().includes('3 of 3'));

  // back preserves state
  await page.locator('.qstep.on [data-prev]').click();
  await page.waitForTimeout(150);
  t('back button works', (await page.locator('.qcount').innerText()).toLowerCase().includes('2 of 3'));
  t('selection preserved on back', await page.locator('#q-town').inputValue() === 'Hillsboro');
  await page.locator('.qstep.on [data-next]').click();
  await page.waitForTimeout(200);

  await page.fill('#q-name', 'Test Owner');
  await page.fill('#q-phone', '314555');
  await page.locator('[type=submit]').click();
  await page.waitForTimeout(200);
  t('rejects a short phone number', await page.locator('[data-err="phone"]').evaluate(e => e.classList.contains('on')));

  await page.fill('#q-phone', '(314) 555-0123');
  await page.locator('[type=submit]').click();
  await page.waitForTimeout(1100);
  t('shows success state on valid submit', await page.locator('.qdone').isVisible());

  // ---------- before/after slider ----------
  await page.goto(`${BASE}/work.html`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(600);
  const ba = page.locator('.ba').first();
  const before = await ba.evaluate(e => getComputedStyle(e).getPropertyValue('--pos'));
  await ba.locator('input[type=range]').fill('88');
  await page.waitForTimeout(150);
  const after = await ba.evaluate(e => getComputedStyle(e).getPropertyValue('--pos'));
  t('slider moves the clip position', before.trim() !== after.trim(), `${before.trim()} -> ${after.trim()}`);
  t('slider layers have painted content', await ba.evaluate(e => {
    const s = e.querySelectorAll('.lyr svg');
    return s.length === 2 && Array.from(s).every(x => x.getBoundingClientRect().height > 40);
  }));
  t('slider is keyboard reachable', await ba.locator('input[type=range]').evaluate(e => {
    e.focus(); return document.activeElement === e;
  }));

  // ---------- mobile nav ----------
  const m = await b.newContext({ viewport: { width: 390, height: 844 } });
  const mp = await m.newPage();
  await mp.goto(`${BASE}/index.html`, { waitUntil: 'networkidle' });
  t('burger visible on mobile', await mp.locator('.burger').isVisible());
  t('menu closed initially', !(await mp.locator('#nav-links').evaluate(e => e.classList.contains('open'))));
  await mp.locator('.burger').click();
  await mp.waitForTimeout(300);
  t('burger opens the menu', await mp.locator('#nav-links').evaluate(e => e.classList.contains('open')));
  t('aria-expanded updates', (await mp.locator('.burger').getAttribute('aria-expanded')) === 'true');
  await mp.keyboard.press('Escape');
  await mp.waitForTimeout(250);
  t('Escape closes the menu', !(await mp.locator('#nav-links').evaluate(e => e.classList.contains('open'))));
  t('sticky call/quote bar present', await mp.locator('.actionbar').isVisible());

  // ---------- keyboard / skip link ----------
  await page.goto(`${BASE}/index.html`, { waitUntil: 'networkidle' });
  await page.keyboard.press('Tab');
  t('skip link is the first tab stop', await page.evaluate(() => document.activeElement.classList.contains('skip')));
  t('focus ring is visible', await page.evaluate(() => {
    const s = getComputedStyle(document.activeElement);
    return s.outlineStyle !== 'none' || s.backgroundColor !== 'rgba(0, 0, 0, 0)';
  }));

  // ---------- reduced motion ----------
  const rm = await b.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
  const rp = await rm.newPage();
  await rp.goto(`${BASE}/index.html`, { waitUntil: 'networkidle' });
  await rp.waitForTimeout(900);
  const stillHidden = await rp.evaluate(() => Array.from(document.querySelectorAll('[data-rv]')).filter(e => getComputedStyle(e).opacity !== '1').length);
  t('reduced-motion reveals everything immediately', stillHidden === 0, `${stillHidden} hidden`);

  await b.close();
  console.log(`\n${pass} passed, ${fail} failed`);
  process.exit(fail ? 1 : 0);
})();
