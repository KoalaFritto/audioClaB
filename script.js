/* audioClaB: prossimi concerti da Facebook e video TikTok. */

/* ------------------------------------------------------------------ CONCERTI
   I prossimi concerti vengono dagli eventi della pagina Facebook audioClaB, con il widget ufficiale
   di Facebook (Page Plugin, scheda Eventi): basta creare l'evento su Facebook e compare anche qui.
   Il widget accetta una larghezza da 180 a 500 px: lo creiamo a misura della colonna e lo rifacciamo
   se la colonna cambia larghezza (telefono girato, finestra ridimensionata). */
(function concertiFacebook() {
  const box = document.getElementById('fb-eventi');
  if (!box) return;
  let larghezza = 0;

  function monta() {
    const w = Math.max(180, Math.min(500, Math.floor(box.clientWidth)));
    if (Math.abs(w - larghezza) < 20) return;
    larghezza = w;
    const h = window.innerWidth < 640 ? 480 : 380;
    const q = new URLSearchParams({
      href: box.dataset.pagina, tabs: 'events', width: String(w), height: String(h),
      small_header: 'true', adapt_container_width: 'true', hide_cover: 'true', show_facepile: 'false', locale: 'it_IT',
    });
    const f = document.createElement('iframe');
    f.src = 'https://www.facebook.com/plugins/page.php?' + q.toString();
    f.width = w; f.height = h;
    f.title = 'Prossimi concerti degli audioClaB su Facebook';
    f.loading = 'lazy';
    f.allow = 'encrypted-media; clipboard-write';
    box.replaceChildren(f);
  }

  monta();
  let t;
  window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(monta, 250); });
})();

/* ------------------------------------------------------------------ TIKTOK
   Incolla qui i link dei video TikTok da mostrare, dal più visto in giù. Sul computer compaiono a file
   complete di 4 (8 se ce ne sono almeno 8, altrimenti 4); su tablet e telefono i primi 4, due per riga.
   Usa il link completo del video (apri il video su tiktok.com e copia l'indirizzo), non quello corto
   vm.tiktok.com che dà il tasto Condividi dell'app:
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
  // ogni link deve contenere il numero del video (15 cifre o più); i link corti dell'app
  // (vm.tiktok.com/...) non lo contengono: vengono saltati con un avviso nella console
  const validi = [];
  for (const v of TIKTOK_VIDEO) {
    const m = String(v).match(/(\d{15,})/);
    if (m) validi.push(m[1]);
    else console.warn('TikTok: link saltato, non contiene il numero del video. Apri il video e copia il link completo (tiktok.com/@audioclab/video/...):', v);
  }
  // solo file complete da 4 video: 8, oppure 4, oppure quelli che ci sono se meno di 4
  const ids = validi.slice(0, validi.length >= 8 ? 8 : validi.length >= 4 ? 4 : validi.length);
  const box2 = document.getElementById('tiktok-2');
  // con 4 video o meno la sezione sta in uno schermo: niente seconda schermata vuota
  const sezione = box.closest('section');
  if (sezione) sezione.classList.toggle('g2', ids.length > 4);

  function mount() {
    box.textContent = '';
    if (ids.length) {
      box.classList.add('tiktok--video');
      if (box2) { box2.textContent = ''; box2.classList.add('tiktok--video'); box2.hidden = ids.length <= 4; }
      ids.forEach((id, i) => {
        const card = document.createElement('div');
        card.className = 'frame frame--video tt';
        const f = document.createElement('iframe');
        // niente partenza automatica né disco che gira: il video si muove solo quando lo avvii
        f.src = 'https://www.tiktok.com/player/v1/' + id + '?autoplay=0&loop=0&music_info=0&description=1&rel=0';
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
