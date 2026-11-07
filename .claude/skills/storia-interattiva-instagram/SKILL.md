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

## Stile video: flat vector interattivo (formato di riferimento dell'utente)

È lo stile scelto dall'utente sul modello di un Reel di riferimento. Per il disegno usa la skill **animation-studio** in stile **Flat Vector** (`references/styles/flatvector.md`). Il formato da rispettare è questo:
- **Grafica:** flat vector pulito, con palette indaco e blu notte limitata, forme piene a 2-3 piani di colore, niente contorni scuri. I personaggi sono **senza volto** (silhouette, viste di spalle o di profilo) e ognuno ha un colore focale: Greta ha l'impermeabile arancione.
- **HUD in alto a sinistra:** "● PARTE N" in rosso, l'**ora della storia** in grande (avanza di un minuto ogni 10-12 s) e il **battito cardiaco** ("♥ 72 bpm") che sale con la tensione fino a circa 150 sul colpo di scena.
- **Il telefono come strumento narrativo:** mani che tengono lo smartphone con l'interfaccia vera (schermata di blocco con notifica, chat, app di registrazione, mappa). Lo status bar mostra "Nessun servizio" quando serve isolamento.
- **Sottotitoli:** Inter Black in maiuscolo, bianchi, con la parola pronunciata in **rosso**, 1-3 parole alla volta, a circa 2/3 dell'altezza.
- **Gancio:** un riquadro bianco con il titolo-shock nei primi secondi (es. "IL PAESE RIEMERSO / DOPO 48 ANNI").
- **Scelta:** "COSA DEVE FARE …?" con due pillole, **A** blu e **B** arancione, ciascuna con la lettera in un cerchio bianco. Il narratore le legge come "Opzione A… Opzione B…".
- **Finale:** fondo scuro con alone rosso, "PARTE 2" grande in rosso, "SEGUI PER LA PARTE 2" in una pillola con contorno, le pillole A/B piccole e "SCRIVILO **NEI COMMENTI**".
- **Suono:** drone sotto la voce, colpo di basso e flash sui tagli importanti, whoosh sugli altri, silenzio totale prima del sussurro, battito cardiaco sul finale.
- **Voce:** **Marco Deep** (ElevenLabs, voice id `13Cuh3NuYvWOVQtLbRN8`, `eleven_multilingual_v2`, lingua `it`), che è la scelta dell'utente. I sussurri dei personaggi si fanno con Luna (`BZc8d1MPTdZkyGbE9Sin`). L'endpoint `with-timestamps` dà i tempi per i sottotitoli.

**Procedura per risparmiare crediti:** prima il copione approvato, poi le anteprime dei fotogrammi in locale (gratis). La voce ElevenLabs si genera **una sola volta** per episodio, con tutte le battute insieme. Non rigenerare le battute per prova.

Il motore di riferimento è in `storie/valsorda/video/flat/`: `genera_flat.py` gestisce timeline, sound design e montaggio, `scene.html` contiene le scene SVG deterministiche (`renderFrame`) e `render.js` cattura i fotogrammi con Chromium. Per un nuovo episodio si copia la cartella, si riscrivono le battute e le scene di `scene.html`, e si lascia invariato il resto (HUD, sottotitoli, pillole, finale).

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
