/* Render the animated logo sting to MP4 by seeking the same Three.js scene
   the website uses, frame by frame, then stitching with ffmpeg. */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
const os = require('os');

const BASE = 'http://127.0.0.1:8787';
const EXE = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const OUT = path.resolve(__dirname, '..', 'website', 'assets', 'video');
fs.mkdirSync(OUT, { recursive: true });

const FPS = 30, DUR = 3.6;
const FORMATS = [
  { name: 'logo-sting-16x9', w: 1920, h: 1080 },
  { name: 'logo-sting-1x1', w: 1080, h: 1080 },
  { name: 'logo-sting-9x16', w: 1080, h: 1920 },
];

const ONLY = process.argv[2];
(async () => {
  const b = await chromium.launch({
    executablePath: EXE,
    args: ['--no-sandbox', '--use-gl=swiftshader', '--enable-unsafe-swiftshader',
      '--hide-scrollbars', '--force-device-scale-factor=1'],
  });

  for (const f of FORMATS.filter(x => !ONLY || x.name.includes(ONLY))) {
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'sting-'));
    const page = await b.newPage({ viewport: { width: f.w, height: f.h }, deviceScaleFactor: 1 });
    page.on('pageerror', e => console.log('ERR', e.message));
    await page.goto(`${BASE}/sting.html`, { waitUntil: 'networkidle' });
    await page.waitForFunction(() => window.__ready === true, null, { timeout: 20000 });
    await page.waitForTimeout(700);

    const total = Math.round(FPS * DUR);
    for (let i = 0; i < total; i++) {
      const t = i / FPS;
      await page.evaluate((tt) => window.__seek(tt), t);
      await page.screenshot({
        path: path.join(tmp, String(i).padStart(4, '0') + '.png'),
        animations: 'disabled',
      });
    }
    await page.close();

    const mp4 = path.join(OUT, f.name + '.mp4');
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS),
      '-i', path.join(tmp, '%04d.png'),
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '19',
      '-pix_fmt', 'yuv420p', '-movflags', '+faststart', mp4]);

    // poster frame from the last frame
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error',
      '-i', path.join(tmp, String(total - 1).padStart(4, '0') + '.png'),
      '-vf', 'scale=' + Math.min(f.w, 1200) + ':-1',
      path.join(OUT, f.name + '-poster.jpg')]);

    // small looping webm for web use
    if (f.name === 'logo-sting-16x9') {
      execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS),
        '-i', path.join(tmp, '%04d.png'), '-c:v', 'libvpx-vp9', '-b:v', '0',
        '-crf', '36', '-vf', 'scale=1280:-2', '-an',
        path.join(OUT, f.name + '.webm')]);
    }

    fs.rmSync(tmp, { recursive: true, force: true });
    const kb = (fs.statSync(mp4).size / 1024).toFixed(0);
    console.log(`${f.name}.mp4  ${f.w}x${f.h}  ${total} frames  ${kb} KB`);
  }
  await b.close();
})();
