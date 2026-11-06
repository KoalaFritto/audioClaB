// Controllo responsive di audioClaB su 25 dispositivi. Uso: python3 -m http.server 8765 && node tests/responsive.js
const path = require('node:path');
const { chromium } = require('playwright');

const targetUrl = process.env.TARGET_URL || 'http://127.0.0.1:8765/audioClaB.html';
const out = process.env.PW_ARTIFACT_DIR || '/tmp';
const shots = (process.env.SHOTS || '').split(',').filter(Boolean);

const devices = [
  ['iphone-se-1', 320, 568, true], ['galaxy-s9', 360, 740, true], ['iphone-se', 375, 667, true],
  ['iphone-15', 390, 844, true], ['pixel-7', 412, 915, true], ['iphone-pro-max', 430, 932, true],
  ['land-se-1', 568, 320, true], ['land-se', 667, 375, true], ['land-iphone', 844, 390, true], ['land-max', 932, 430, true],
  ['tablet-small', 600, 960, true], ['ipad-mini', 768, 1024, true], ['ipad', 810, 1080, true], ['ipad-air', 820, 1180, true],
  ['ipad-pro', 1024, 1366, true], ['ipad-land', 1024, 768, true], ['ipad-air-land', 1180, 820, true], ['ipad-pro-land', 1366, 1024, true],
  ['laptop-720', 1280, 720, false], ['laptop', 1366, 768, false], ['mac', 1440, 900, false], ['fhd-scaled', 1536, 864, false],
  ['fhd', 1920, 1080, false], ['qhd', 2560, 1440, false], ['ultrawide', 3440, 1440, false],
];

(async () => {
  const browser = await chromium.launch({ headless: true });
  let problems = 0;
  try {
    for (const [name, width, height, touch] of devices) {
      const ctx = await browser.newContext({ viewport: { width, height }, hasTouch: touch, isMobile: touch && width < 1024, deviceScaleFactor: 1 });
      const page = await ctx.newPage();
      await page.goto(targetUrl, { waitUntil: 'load' });
      // scorre fino in fondo per far partire i caricamenti pigri
      await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += innerHeight / 2) { scrollTo(0, y); await new Promise(r => setTimeout(r, 40)); } scrollTo(0, 0); });
      await page.waitForTimeout(300);
      const r = await page.evaluate(() => {
        const vw = document.documentElement.clientWidth;
        const issues = [];
        if (document.documentElement.scrollWidth > vw + 1) issues.push(`scroll orizzontale: ${document.documentElement.scrollWidth} > ${vw}`);
        // contenuto che esce dalla sua sezione
        for (const sec of document.querySelectorAll('main > section, footer.closing')) {
          const b = sec.getBoundingClientRect();
          let maxBottom = 0;
          for (const el of sec.querySelectorAll('h1,h2,h3,p,li,a,button,img,iframe,.frame,blockquote,input,video')) {
            const r = el.getBoundingClientRect();
            if (!r.width || !r.height || getComputedStyle(el).visibility === 'hidden') continue;
            if (el.closest('.nav__menu, [hidden]')) continue;
            maxBottom = Math.max(maxBottom, r.bottom);
          }
          const over = maxBottom - b.bottom;
          if (over > 2) issues.push(`#${sec.id || sec.className.split(' ')[0]}: il contenuto esce di ${Math.round(over)}px (sezione alta ${Math.round(b.height)})`);
        }
        // elementi fuori dallo schermo a destra o tagliati
        for (const el of document.querySelectorAll('main *, footer *, header .nav__bar > *')) {
          const r = el.getBoundingClientRect();
          if (!r.width || el.closest('.nav__menu')) continue;
          const cs = getComputedStyle(el);
          if (cs.position === 'fixed' || cs.display === 'none') continue;
          if (r.right > vw + 1 && !el.closest('.close__media, .hero__media, .frame, .wall')) { issues.push(`fuori a destra: ${el.tagName.toLowerCase()}.${[...el.classList].join('.')} fino a ${Math.round(r.right)}`); break; }
        }
        // testo più piccolo di 13px
        const small = [...document.querySelectorAll('main p, main li, main a, main span, footer p, footer a')].filter(e => e.childNodes.length && e.textContent.trim() && parseFloat(getComputedStyle(e).fontSize) < 13 && e.getBoundingClientRect().width);
        if (small.length) issues.push(`testo sotto 13px: ${small.length} (${small[0].textContent.trim().slice(0, 30)})`);
        // bersagli touch sotto 40px
        const tiny = [...document.querySelectorAll('main button, main a.btn, header .btn, header button, .track, .yt__play')].filter(e => { const r = e.getBoundingClientRect(); return r.width && (r.height < 40 || r.width < 40); });
        if (tiny.length) issues.push(`bersagli piccoli: ${tiny.map(e => e.className.split(' ')[0] + ' ' + Math.round(e.getBoundingClientRect().width) + 'x' + Math.round(e.getBoundingClientRect().height)).slice(0, 3).join(', ')}`);
        return { issues, h: document.body.scrollHeight };
      });
      problems += r.issues.length;
      console.log(`${name.padEnd(15)} ${String(width).padStart(4)}x${String(height).padEnd(5)} ${r.issues.length ? 'PROBLEMI' : 'ok'}  pagina ${r.h}px`);
      r.issues.forEach(i => console.log('     - ' + i));
      if (shots.includes(name)) await page.screenshot({ path: path.join(out, `resp-${name}.png`), fullPage: true });
      await ctx.close();
    }
  } finally {
    await browser.close();
  }
  console.log(`\n${problems} problemi in totale`);
})();
