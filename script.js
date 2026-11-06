/* audioClaB: lettore dei brani, video YouTube al clic e lista dei concerti. */

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
   Incolla qui i link dei video TikTok da mostrare, dal più visto in giù (ne compaiono al massimo 4):
     'https://www.tiktok.com/@audioclab/video/7xxxxxxxxxxxxxxxxxx',
   Con l'elenco vuoto la sezione mostra il profilo @audioclab incorporato da TikTok. */
const TIKTOK_VIDEO = [
  'https://www.tiktok.com/@audioclab/video/7624145377213697302', // Io dal mare
  'https://www.tiktok.com/@audioclab/video/7601620674410679575', // Trecastagni, 7 febbraio 2026
  'https://www.tiktok.com/@audioclab/video/7538869704849476886', // Adesso la pubblicità
  'https://www.tiktok.com/@audioclab/video/7683078825760017696', // Piedimonte, 12 settembre 2026
];

(function tiktok() {
  const box = document.getElementById('tiktok');
  if (!box) return;
  const ids = TIKTOK_VIDEO
    .map(v => String(v).match(/(\d{15,})/))
    .filter(Boolean)
    .map(m => m[1])
    .slice(0, 4);

  function mount() {
    box.textContent = '';
    if (ids.length) {
      box.classList.add('tiktok--video');
      ids.forEach((id, i) => {
        const card = document.createElement('div');
        card.className = 'frame frame--video tt';
        const f = document.createElement('iframe');
        f.src = 'https://www.tiktok.com/player/v1/' + id + '?description=1&music_info=1&rel=0';
        f.title = 'Video TikTok degli audioClaB ' + (i + 1);
        f.loading = 'lazy';
        f.allow = 'fullscreen; encrypted-media; picture-in-picture';
        card.appendChild(f);
        box.appendChild(card);
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

/* ------------------------------------------------------------------ LETTORE */
(function lettore() {
  const audio = document.getElementById('audio');
  const tracks = [...document.querySelectorAll('.track')];
  const seek = document.querySelector('.player__seek');
  const now = document.querySelector('.player__now');
  const time = document.querySelector('.player__time');
  const heroPlay = document.querySelector('.hero-play');
  if (!audio || !tracks.length) return;
  let current = -1;

  const mmss = s => {
    if (!isFinite(s)) return '0:00';
    s = Math.max(0, Math.floor(s));
    return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
  };

  function render() {
    const playing = !audio.paused;
    tracks.forEach((t, i) => t.setAttribute('aria-pressed', String(i === current && playing)));
    if (heroPlay) heroPlay.classList.toggle('is-playing', current === 0 && playing);
    if (current >= 0) now.textContent = tracks[current].querySelector('.rows__name').textContent;
    seek.disabled = current < 0;
  }

  function progress() {
    const d = audio.duration;
    const p = d ? audio.currentTime / d : 0;
    seek.value = Math.round(p * 1000);
    seek.style.setProperty('--pct', (p * 100).toFixed(2) + '%');
    time.textContent = mmss(audio.currentTime) + ' / ' + mmss(d);
  }

  function play(i) {
    if (i === current) {
      audio.paused ? audio.play() : audio.pause();
      return;
    }
    current = i;
    audio.src = tracks[i].dataset.src;
    audio.play().catch(() => {});
    render();
  }

  tracks.forEach((t, i) => t.addEventListener('click', () => play(i)));
  if (heroPlay) heroPlay.addEventListener('click', () => play(Number(heroPlay.dataset.track) || 0));

  seek.addEventListener('input', () => {
    if (audio.duration) audio.currentTime = (seek.value / 1000) * audio.duration;
    progress();
  });

  audio.addEventListener('play', render);
  audio.addEventListener('pause', render);
  audio.addEventListener('timeupdate', progress);
  audio.addEventListener('loadedmetadata', progress);
  audio.addEventListener('ended', () => {
    if (current < tracks.length - 1) play(current + 1);
    else { render(); }
  });
})();

/* ------------------------------------------------------------------ YOUTUBE
   La miniatura resta un'immagine finché non la clicchi: il player di YouTube si carica solo allora. */
document.querySelectorAll('[data-yt]').forEach(btn => {
  btn.addEventListener('click', () => {
    const f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(btn.dataset.yt) + '?autoplay=1&rel=0';
    f.title = btn.getAttribute('aria-label') || 'Video YouTube';
    f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
    f.allowFullscreen = true;
    btn.replaceWith(f);
  });
});

/* un solo media alla volta: se parte un video si ferma la musica, e viceversa */
document.addEventListener('play', e => {
  document.querySelectorAll('audio, video').forEach(m => { if (m !== e.target && !m.paused) m.pause(); });
}, true);

/* l'anno nel footer */
document.querySelectorAll('[data-anno]').forEach(el => { el.textContent = new Date().getFullYear(); });
