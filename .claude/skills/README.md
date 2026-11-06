# Skill video social per ELEVATORI S.R.L.

Skill per Claude Code, scaricate da GitHub e selezionate per creare contenuti video per
Instagram e Facebook per ELEVATORI S.R.L. (https://elevatorisrl.com).
Claude Code le carica automaticamente da `.claude/skills/` quando apri questo progetto.

**Da dove partire:** chiedi a Claude, ad esempio, *"Crea un Reel per ELEVATORI S.R.L. su un
ammodernamento prima/dopo"*. La skill `elevatori-social-video` sceglie le skill giuste.
La prima volta viene lanciata `brand-profile` per compilare i dati reali dell'azienda.

## Skill incluse

| Skill | Fonte | Licenza | A cosa serve |
|---|---|---|---|
| elevatori-social-video | creata per questo progetto | MIT | Regia: instrada le richieste e applica le regole del brand |
| brand-profile, voice-builder | [social-media-skills/skills](https://github.com/social-media-skills/skills) @f28cef2 | MIT | Profilo e tono di voce del brand |
| reels-script, short-form-video-script, hook-writer, scripting-and-storyboarding | social-media-skills/skills | MIT | Script di Reel e video brevi, ganci, storyboard |
| caption-writer, hashtag-strategy, instagram-seo | social-media-skills/skills | MIT | Caption, hashtag, ricerca su Instagram |
| facebook-strategy, instagram-growth, instagram-reels-publishing | social-media-skills/skills | MIT | Strategia e pubblicazione Facebook/Instagram |
| before-after-and-transformation, behind-the-scenes-and-founder, social-proof-and-testimonials, educational-content-and-how-to | social-media-skills/skills | MIT | Formati di contenuto (prima/dopo, dietro le quinte, testimonianze, tutorial) |
| content-pillars, content-calendar, batch-content-plan | social-media-skills/skills | MIT | Piano editoriale |
| captions-and-clipping, cross-platform-repurposing, platform-specs-and-validation, thumbnail-design | social-media-skills/skills | MIT | Sottotitoli, riuso, formati, copertine |
| ai-video, capcut | social-media-skills/skills | MIT | Video generati con AI, montaggio in CapCut |
| video, social, ad-creative | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) @96798cf | MIT | Produzione video, strategia social, creatività per ads |
| remotion-ads | [Maartenlouis/remotion-ads](https://github.com/Maartenlouis/remotion-ads) @8c77946 | MIT | Video pubblicitari Reels 9:16 e caroselli 4:5 con Remotion, voce e sottotitoli |
| ad-promo, walkthrough-tour, captions, reframing, shortform-strategist, brand-guardian, caption-styling | [vidmoat/skills](https://github.com/vidmoat/skills) @f914f79 | Apache-2.0 (script) + CC-BY-4.0 (testi) | Tecnica di montaggio: spot, tour di un impianto, sottotitoli, riformattazione, coerenza brand |

I testi delle licenze sono in `../skills-licenses/`.

## Da installare a parte (nessun file di licenza nel repository, quindi non copiate qui)

- **Skill ufficiali Remotion** ([remotion-dev/skills](https://github.com/remotion-dev/skills)), utili
  insieme a `remotion-ads`: `npx skills add remotion-dev/skills`.
  Remotion richiede una licenza aziendale a pagamento per le aziende oltre una certa dimensione:
  verifica su https://www.remotion.dev/docs/license prima dell'uso commerciale.

## Chiavi API (facoltative)

Alcuni script di `remotion-ads` usano servizi esterni e leggono le chiavi da variabili d'ambiente:
`ELEVENLABS_API_KEY` (voce), `GEMINI_API_KEY` (voce Gemini), `SUNO_API_KEY` / `BROWSER_USE_API_KEY`
(musica). Non salvare mai le chiavi nel repository.

## Da completare

Il sito https://elevatorisrl.com non era raggiungibile durante l'installazione: servizi, zona,
contatti, colori e logo vanno inseriti nel profilo brand (`brand-profile.md`) alla prima esecuzione.
