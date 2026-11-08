const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1080 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.resolve(__dirname, 'profilo.html'));
  await p.evaluate(() => document.fonts.ready);
  for (const k of ['door', 'mono', 'keyhole']) {
    await p.evaluate((k) => window.draw(k), k);
    await p.screenshot({ path: path.resolve(__dirname, `profilo-${k}.png`) });
  }
  await b.close();
})();
