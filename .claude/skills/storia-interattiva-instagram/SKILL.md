---
name: storia-interattiva-instagram
description: Crea serie di Reel/Storie Instagram interattive horror e d'avventura in cui il pubblico sceglie cosa succede scrivendolo nei commenti, e il video successivo esegue la scelta più votata. Usala quando l'utente vuole ideare una nuova serie "scegli tu cosa fare", scrivere l'episodio 1 o il prossimo episodio, contare i voti dai commenti, scrivere caption/commento fissato, oppure tenere traccia della trama e dei bivi.
---

# Storia interattiva Instagram (horror / avventura, "decidete voi nei commenti")

Formato: una serie di Reel verticali brevi. Ogni episodio finisce su un **bivio**:
il pubblico vota nei commenti, e l'episodio successivo **mostra davvero** la scelta più votata.
Il motore delle visualizzazioni è il ciclo: *cliffhanger → commenti → follow per vedere com'è andata*.

Scrivi tutto in italiano, salvo diversa richiesta dell'utente.

## Prima di scrivere

1. Cerca un file `storie/<nome-serie>/bibbia.md`. Se esiste, leggilo: contiene personaggi,
   regole del mondo, stato attuale, scelte passate e voti. **Non contraddirlo mai.**
2. Se non esiste e si tratta di una serie nuova, chiedi (o scegli tu se l'utente lascia fare):
   - genere/tono: horror psicologico, found footage, mistero, survival, avventura, dark fantasy;
   - stile di produzione: faceless con voce narrante, POV in prima persona girato col telefono,
     attore in camera, immagini/video generati con AI, animazione;
   - durata episodio (consigliato 30–60 s) e frequenza (consigliato ogni 24–48 h).
   Poi crea la bibbia partendo da `references/bibbia-template.md`.

## Struttura di ogni episodio

Usa questa scaletta (tempi per un Reel da ~45 s):

| Tempo | Blocco | Cosa deve fare |
|---|---|---|
| 0–2 s | **Gancio** | Immagine o frase che blocca lo scroll. Mai iniziare con "Ciao" o con un logo. Es.: "Sono le 3:17. Qualcuno ha appena bussato… dall'interno dell'armadio." |
| 2–5 s | **Contesto lampo** | Chi, dove, cosa c'è in gioco, in una riga. Dall'episodio 2: recap di 3 s + "Avete scelto **X** (62%)". |
| 5–35 s | **Escalation** | 2–3 battute che alzano la tensione. Ogni 4–6 s un cambiamento (suono, inquadratura, rivelazione). |
| 35–42 s | **Bivio** | Ferma l'azione nel momento peggiore. Presenta 2 opzioni (max 3), chiare, brevi, entrambe allettanti e rischiose. |
| 42–45 s | **CTA** | "Scrivi **1** o **2** nei commenti. Domani faccio quello che sceglie la maggioranza." Testo a schermo + voce. |

Regole per i bivi:
- Le opzioni devono essere **azioni**, non opinioni: "Apri la porta" / "Scappa dalla finestra".
- Etichette da digitare in 1 tasto: `1`/`2`, `A`/`B`, oppure emoji (🚪 / 🪟). Scrivi sempre l'etichetta anche a schermo.
- Nessuna opzione "ovviamente giusta": se una è chiaramente sicura vince sempre e la storia si appiattisce.
- Ogni tanto inserisci un'opzione "trappola" o un costo nascosto: rende le scelte memorabili.
- Ogni 4–6 episodi prevedi un mini-finale o una svolta grande, così chi arriva dopo ha un motivo per recuperare.

## Gestire i rami senza esplodere

Non scrivere tutto l'albero in anticipo. Usa la struttura **"a collo di bottiglia"**:
i rami divergono per 1–2 episodi e poi riconvergono su eventi chiave già pianificati
(il colpo di scena centrale, il luogo finale). Le scelte cambiano *come* ci si arriva,
cosa si perde (oggetti, alleati, salute) e il tono del finale.

Nella bibbia tieni uno **stato** semplice: inventario, alleati vivi/morti, indizi trovati,
"livello di pericolo". Le conseguenze delle scelte passate devono **tornare** negli episodi
successivi: è ciò che fa sentire il pubblico ascoltato.

## Tono horror adatto a Instagram

- Paura per **suggestione**, non per sangue: suoni, silenzi, cose intraviste, dettagli fuori posto.
- Niente gore esplicito, autolesionismo, violenza realistica su persone reali, luoghi o persone reali
  accusati di fatti inventati. Se la storia è finzione e sembra "vera" (found footage),
  aggiungi in caption un'indicazione tipo "storia di finzione".
- Jumpscare: massimo uno per episodio, mai nei primi 2 secondi (fa scappare, non trattiene).
- Il sound design vale metà dell'effetto: indica sempre suoni e musica nel copione.

## Output da consegnare per ogni episodio

Produci sempre questo pacchetto (usa `references/episodio-template.md`):

1. **Titolo episodio** e numero (es. "Ep. 3 – La cantina").
2. **Copione a tempi**: per ogni blocco → inquadratura/visual, voce narrante, testo a schermo, suoni/musica.
3. **Shot list** pronta da girare (o prompt per generatori video/immagini AI, se lo stile è AI).
4. **Testo a schermo del bivio** con le etichette di voto.
5. **Caption** (prima riga = gancio, poi CTA di voto, poi "Ep. precedente nel profilo / in evidenza").
6. **Commento da fissare**: regole di voto + scadenza ("Votazioni chiuse domani alle 18").
7. **Copertina/thumbnail**: testo breve (3–5 parole) e immagine suggerita, coerente con la serie.
8. 5–10 hashtag pertinenti (es. #storiahorror #sceglitu #creepypasta #horroritalia #pov).
9. **Note di continuità**: cosa aggiornare nella bibbia.

Dopo aver scritto l'episodio, aggiorna `storie/<nome-serie>/bibbia.md`
(stato, bivio aperto, opzioni) e salva il copione in `storie/<nome-serie>/ep-XX.md`.

## Stile video (quello dei Reel horror più visti)

Se l'utente chiede il video, producilo in questo stile:
- **Immagini:** fotogrammi cinematografici realistici generati con l'AI (9:16), tutti con la stessa palette (es. blu/verde freddo, nebbia, notte). Su ogni immagine va un movimento lento (zoom o pan, effetto Ken Burns) e si taglia ogni 2–3 s. Nei momenti di tensione i tagli arrivano a ogni frase.
- **Narratore:** una voce maschile profonda in terza persona, con frasi brevi al presente e pause ("Stanotte... è tornato fuori."). La voce più usata per questi video è **Adam di ElevenLabs** (modello `eleven_multilingual_v2`, lingua `it`). Le battute dei personaggi, come i sussurri, vanno con una seconda voce.
- **Sottotitoli:** grandi, in maiuscolo e bold, al centro, 1–3 parole alla volta, con la parola pronunciata in giallo e un piccolo "pop" quando appare.
- **Suono:** un colpo di basso (boom) e un flash sui tagli importanti, whoosh sugli altri tagli, un riser prima dello spavento e un drone scuro sotto la voce, abbassato quando parla il narratore. Prima della battuta più spaventosa va un silenzio totale.
- **Grafica fissa:** in alto l'etichetta "SERIE · PARTE N"; nei primi 2–3 s un riquadro bianco con il gancio scritto.
- **Finale:** schermo diviso con le due scelte (1 sopra, 2 sotto), "COMMENTA 1 O 2 ↓" che pulsa e il battito cardiaco. Dura 4–5 s, e nella Parte 2 va mostrato di nuovo per primo il risultato.
- **Durata:** 55–70 s. Nessun testo importante negli ultimi 400 px in basso, coperti dall'interfaccia di Instagram.

Il generatore di riferimento è in `storie/valsorda/video/`: `immagini_ai.py` crea le immagini, `voce_elevenlabs.py` crea la voce e i timestamp, `genera_ep01_v2.py` fa il montaggio. Puoi copiarli e adattarli per i nuovi episodi.

## Dopo la pubblicazione: contare i voti

Quando l'utente incolla o esporta i commenti, conta i voti con lo script:

```bash
python3 .claude/skills/storia-interattiva-instagram/scripts/conta_voti.py commenti.txt --opzioni 1 2
```

- Formato accettato: una riga per commento, `utente: testo` (oppure solo il testo; in quel caso
  non si possono scartare i voti doppi). Opzioni alternative: `--opzioni A B` o emoji `--opzioni 🚪 🪟`.
- Lo script conta **un voto per utente** (vale il primo), ignora i commenti ambigui che citano
  più opzioni e stampa percentuali e vincitore.
- Pareggio: decidi con la regola scritta nel commento fissato (es. vince l'opzione più rischiosa,
  oppure spareggio in una Storia con sondaggio). Annota il risultato nella bibbia.
- Segnala all'utente 2–3 commenti divertenti o creativi da citare nel prossimo episodio
  ("@utente aveva ragione…"): aumenta i commenti futuri.

## Episodio successivo

- Apri con: recap in 3 s + "Avete scelto X con il Y%". Mostra subito la conseguenza (non rimandarla).
- Se ha vinto l'opzione "sbagliata", fai pagare il prezzo in modo visibile ma lascia la storia viva.
- Se un'idea dai commenti è migliore delle opzioni, puoi integrarla come sorpresa, citando chi l'ha avuta.
- Chiudi con un nuovo bivio e rinnova la CTA.

## Idee di serie (punti di partenza)

- Notte da solo in un ospedale abbandonato, girata col telefono (found footage).
- Messaggi da un numero sconosciuto che sa cosa stai facendo.
- Escursione in montagna: la nebbia scende e il sentiero non è più quello della mappa.
- Ascensore che si ferma a un piano che non esiste.
- Avventura: mappa trovata in soffitta, ogni episodio una tappa e un enigma che il pubblico risolve.
- Survival: il pubblico decide come gestire cibo, batteria del telefono e alleati.

Proponi idee originali: non ricalcare personaggi, titoli o trame di film, serie o videogiochi esistenti.
