// Disegna i fotogrammi di scene.html con Chromium headless.
// node render.js scene.html timeline.json cartella_out [workers] [lista_frame]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [html, tlPath, outDir, workersArg, onlyArg] = process.argv.slice(2);
  const tl = JSON.parse(fs.readFileSync(tlPath, 'utf8'));
  const total = Math.floor(tl.dur * tl.fps);
  const only = onlyArg ? onlyArg.split(',').filter(Boolean).map(Number) : null;
  const frames = only && only.length ? only : [...Array(total).keys()];
  const workers = Math.max(1, Math.min(parseInt(workersArg || '4', 10), frames.length));
  const browser = await chromium.launch();
  let done = 0;
  const t0 = Date.now();
  async function worker(w) {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
    await page.goto('file://' + path.resolve(html));
    await page.evaluate((d) => window.setTimeline(d), tl);
    await page.evaluate(() => document.fonts.ready);
    for (let i = w; i < frames.length; i += workers) {
      const f = frames[i];
      await page.evaluate((t) => window.render(t), f / tl.fps);
      await page.screenshot({ path: path.join(outDir, String(f).padStart(5, '0') + '.jpg'), type: 'jpeg', quality: 93 });
      done++;
      if (done % 150 === 0) console.log(`  ${done}/${frames.length} (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
    }
    await page.close();
  }
  await Promise.all([...Array(workers).keys()].map(worker));
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
