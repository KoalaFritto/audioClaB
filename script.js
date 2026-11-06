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
