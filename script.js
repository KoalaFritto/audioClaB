/* audioClaB: lista dei concerti e video TikTok. */

/* ------------------------------------------------------------------ CONCERTI
   Per aggiungere una data scrivi una riga qui sotto e salva:
     { data: '2026-12-20', ora: '21:30', locale: 'Nome del locale', citta: 'Catania', link: 'https://...' },
   Le date già passate spariscono da sole; senza date compare il messaggio "Nessuna data in programma". */
const CONCERTI = [
];

(function concerti() {
  const lista = document.getElementById('lista-concerti');
  const vuoto = document.getElementById('concerti-vuoto');
  if (!lista) return;
  const oggi = new Date(); oggi.setHours(0, 0, 0, 0);
  const fmt = new Intl.DateTimeFormat('it-IT', { weekday: 'short', day: 'numeric', month: 'long', year: 'numeric' });
  const prossimi = CONCERTI
    .map(c => ({ ...c, quando: new Date(c.data + 'T00:00:00') }))
    .filter(c => !isNaN(c.quando) && c.quando >= oggi)
    .sort((a, b) => a.quando - b.quando);
  for (const c of prossimi) {
    const li = document.createElement('li');
    const nome = document.createElement('span');
    nome.className = 'rows__name';
    if (c.link) {
      const a = document.createElement('a');
      a.href = c.link; a.target = '_blank'; a.rel = 'noopener'; a.textContent = c.locale;
      nome.appendChild(a);
    } else nome.textContent = c.locale;
    const dove = document.createElement('p');
    dove.textContent = c.citta;
    const val = document.createElement('span');
    val.className = 'rows__value';
    val.textContent = fmt.format(c.quando) + (c.ora ? ', ' + c.ora : '');
    li.append(nome, val, dove);
    lista.appendChild(li);
  }
  if (vuoto) vuoto.hidden = prossimi.length > 0;
})();

/* ------------------------------------------------------------------ TIKTOK
   Incolla qui i link dei video TikTok da mostrare, dal più visto in giù (ne compaiono al massimo 8:
   4 per fila sul computer, i primi 4 su tablet e telefono):
     'https://www.tiktok.com/@audioclab/video/7xxxxxxxxxxxxxxxxxx',
   Con l'elenco vuoto la sezione mostra il profilo @audioclab incorporato da TikTok. */
const TIKTOK_VIDEO = [
  'https://www.tiktok.com/@audioclab/video/7624145377213697302', // Io dal mare (43.500 visualizzazioni)
  'https://www.tiktok.com/@audioclab/video/7601620674410679575', // Trecastagni, 7 febbraio 2026 (15.900)
  'https://www.tiktok.com/@audioclab/video/7538869704849476886', // Adesso la pubblicità (10.600)
  'https://www.tiktok.com/@audioclab/video/7683078825760017696', // Piedimonte, 12 settembre 2026 (3.010)
  'https://www.tiktok.com/@audioclab/video/7686006121168932129', // Augusta (1.126)
  'https://www.tiktok.com/@audioclab/video/7688060615427968288', // Mai tacere, Piazza Duomo Augusta (981)
  'https://www.tiktok.com/@audioclab/video/7685270446626901281', // Momenti del 12 settembre (909)
  'https://www.tiktok.com/@audioclab/video/7686445708735434016', // La vita è adesso (766)
];

(function tiktok() {
  const box = document.getElementById('tiktok');
  if (!box) return;
  const ids = TIKTOK_VIDEO
    .map(v => String(v).match(/(\d{15,})/))
    .filter(Boolean)
    .map(m => m[1])
    .slice(0, 8);
  const box2 = document.getElementById('tiktok-2');

  function mount() {
    box.textContent = '';
    if (ids.length) {
      box.classList.add('tiktok--video');
      if (box2) { box2.textContent = ''; box2.classList.add('tiktok--video'); box2.hidden = ids.length <= 4; }
      ids.forEach((id, i) => {
        const card = document.createElement('div');
        card.className = 'frame frame--video tt';
        const f = document.createElement('iframe');
        f.src = 'https://www.tiktok.com/player/v1/' + id + '?description=1&music_info=1&rel=0';
        f.title = 'Video TikTok degli audioClaB ' + (i + 1);
        f.loading = 'lazy';
        f.allow = 'fullscreen; encrypted-media; picture-in-picture';
        card.appendChild(f);
        (i >= 4 && box2 ? box2 : box).appendChild(card);
      });
      return;
    }
    // il profilo ufficiale (codice di incorporamento dato da TikTok)
    const q = document.createElement('blockquote');
    q.className = 'tiktok-embed';
    q.cite = 'https://www.tiktok.com/@' + box.dataset.profilo;
    q.dataset.uniqueId = box.dataset.profilo;
    q.dataset.embedType = 'creator';
    const sec = document.createElement('section');
    const a = document.createElement('a');
    a.href = q.cite + '?refer=creator_embed'; a.target = '_blank'; a.rel = 'noopener';
    a.textContent = '@' + box.dataset.profilo;
    sec.appendChild(a); q.appendChild(sec); box.appendChild(q);
    const s = document.createElement('script');
    s.async = true; s.src = 'https://www.tiktok.com/embed.js';
    document.body.appendChild(s);
  }

  // i video hanno già loading="lazy"; il profilo incorporato si carica solo quando la sezione sta per entrare nello schermo
  if (ids.length) mount();
  else if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      if (entries.some(e => e.isIntersecting)) { io.disconnect(); mount(); }
    }, { rootMargin: '600px 0px' });
    io.observe(box);
  } else mount();
})();

/* l'anno nel footer */
document.querySelectorAll('[data-anno]').forEach(el => { el.textContent = new Date().getFullYear(); });
