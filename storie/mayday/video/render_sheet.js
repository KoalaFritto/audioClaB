// Scheda personaggio di Mara (PNG 1080x1920)
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.resolve(__dirname, 'scene.html'));
  await p.evaluate(() => window.setTimeline({ dur: 1, fps: 30, T: { N2: 0 }, M: {}, shots: [{ t: 0, id: 'sheet', clock: '' }], booms: [], caps: [], scary: [] }));
  await p.evaluate(() => document.fonts.ready);
  await p.evaluate(() => window.render(0.5));
  await p.screenshot({ path: path.resolve(__dirname, '..', 'mara-character-sheet.png') });
  await b.close();
})();
