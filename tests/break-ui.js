// break-ui: dati peggiori realistici per audioClaB (solo per prove, non va online). Uso: python3 -m http.server 8765 && node tests/break-ui.js
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
const URL = 'http://127.0.0.1:8765/index.html';
const OUT = process.env.OUT || require('node:os').tmpdir();
const js = fs.readFileSync(path.join(__dirname, '..', 'script.js'), 'utf8');
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');

const tiktok = list => js.replace(/const TIKTOK_VIDEO = \[[\s\S]*?\];/, 'const TIKTOK_VIDEO = ' + JSON.stringify(list) + ';');
const ids = ['7624145377213697302', '7601620674410679575', '7538869704849476886', '7683078825760017696', '7686006121168932129', '7688060615427968288', '7685270446626901281', '7686445708735434016', '7691248692480822561'];
const link = id => 'https://www.tiktok.com/@audioclab/video/' + id;

// nomi e testi lunghi ma plausibili (un nuovo membro, un ruolo composto, un articolo con titolo lungo)
const worstHtml = html
  .replace('<b>Andrea Bruno</b>batteria', '<b>Maria Concetta Santangelo-Privitera</b>batteria e percussioni')
  .replace('<b>Gianfranco Alberti</b>voce', '<b>Gianfranco Alberti</b>voce e chitarra acustica')
  .replace('<span class="rows__name">Debora Lombardo</span><span class="rows__value">pianoforte e tastiere</span>', '<span class="rows__name">Debora Lombardo Santangelo-Privitera</span><span class="rows__value">pianoforte, tastiere e cori</span>')
  .replace("L'estate siciliana di MAD Concerti si accende con audioClaB", "L’estate siciliana di MAD Concerti si accende con audioClaB – Claudio Baglioni Live Experience: cinque date tra Roccalumera, Linguaglossa, Riposto, Trecastagni e Fiumefreddo");

const states = {
  demo: { js },
  'tiktok-0': { js: tiktok([]) },
  'tiktok-1': { js: tiktok([link(ids[0])]) },
  'tiktok-3': { js: tiktok(ids.slice(0, 3).map(link)) },
  'tiktok-5': { js: tiktok(ids.slice(0, 5).map(link)) },
  'tiktok-9-e-link-rotti': { js: tiktok([...ids.map(link), 'https://vm.tiktok.com/ZNabc123/', 'non è un link']) },
  'testi-lunghi': { js, html: worstHtml },
};

(async () => {
  const b = await chromium.launch();
  for (const [name, st] of Object.entries(states)) {
    for (const [w, h, zoom] of [[1440, 900, 1], [768, 1024, 1], [320, 568, 1], [390, 844, 2]]) {
      const p = await b.newPage({ viewport: { width: w, height: h } });
      await p.route('**/script.js', r => r.fulfill({ body: st.js, contentType: 'text/javascript' }));
      if (st.html) await p.route('**/index.html', r => r.fulfill({ body: st.html, contentType: 'text/html' }));
      const errs = []; p.on('pageerror', e => errs.push(e.message));
      await p.goto(URL); await p.waitForTimeout(500);
      if (zoom !== 1) await p.addStyleTag({ content: 'html{font-size:200% !important} :root{--t-body:32px;--t-small:28px;--t-card:36px}' });
      await p.waitForTimeout(300);
      const r = await p.evaluate(() => {
        const vw = document.documentElement.clientWidth, out = [];
        if (document.documentElement.scrollWidth > vw + 1) out.push('scroll orizzontale ' + document.documentElement.scrollWidth);
        const tt = document.querySelectorAll('#video .tt');
        const vis = [...tt].filter(x => x.getBoundingClientRect().width > 0);
        out.push('tiktok: ' + tt.length + ' creati, ' + vis.length + ' visibili' + (document.querySelector('#tiktok-2') && !document.querySelector('#tiktok-2').hidden ? ', seconda fila visibile' : ''));
        const rows = new Set(vis.map(x => Math.round(x.getBoundingClientRect().top)));
        if (vis.length && rows.size) out.push('file di video: ' + rows.size);
        // testo che esce dal suo contenitore
        for (const el of document.querySelectorAll('.mus-nome, .rows__name, .rows__value, .stampa__lista a, .stampa__lista span')) {
          const r = el.getBoundingClientRect(), pr = el.parentElement.getBoundingClientRect();
          if (el.scrollWidth > el.clientWidth + 1 || r.right > pr.right + 1 || r.left < pr.left - 1) out.push('esce: ' + el.textContent.trim().slice(0, 40));
        }
        // nomi sotto le strisce: righe e sovrapposizioni
        const names = [...document.querySelectorAll('.mus-nome')].map(n => n.getBoundingClientRect());
        for (let i = 1; i < names.length; i++) { const a = names[i - 1], c = names[i]; if (Math.abs(a.top - c.top) < 2 && a.right > c.left + 1) out.push('nomi sovrapposti ' + i); }
        const maxH = Math.max(...names.map(n => n.height));
        out.push('nomi alti fino a ' + Math.round(maxH) + 'px');
        return out;
      });
      console.log(`${name.padEnd(22)} ${w}x${h}${zoom > 1 ? ' zoom200' : ''}: ${r.join(' | ')}${errs.length ? ' | ERRORI JS: ' + errs.join('; ') : ''}`);
      if ((name === 'testi-lunghi' || name === 'tiktok-5' || name === 'tiktok-1') && (w === 320 || w === 1440)) {
        const sec = name.startsWith('tiktok') ? '#video' : '#band';
        await p.evaluate(() => { const n = document.querySelector('header.nav'); if (n) n.style.display = 'none'; });
        await p.locator(sec).screenshot({ path: path.join(OUT, `${name}-${w}.png`) });
      }
      await p.close();
    }
  }
  await b.close();
})();
