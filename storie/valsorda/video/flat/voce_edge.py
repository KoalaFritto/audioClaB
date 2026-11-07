#!/usr/bin/env python3
"""Voce narrante PROVVISORIA (Microsoft Edge TTS, gratuita, italiana nativa) con tempi parola per parola.
Scrive <KEY>.mp3 + <KEY>.json ({"text", "words": [[parola, inizio_s, fine_s], ...]}) nella cartella indicata.
Uso: python3 voce_edge.py CARTELLA_OUT
"""
import asyncio, json, os, ssl, sys
import edge_tts
import edge_tts.communicate as c

ca = os.environ.get("SSL_CERT_FILE")
if ca and hasattr(c, "_SSL_CTX"):
    c._SSL_CTX = ssl.create_default_context(cafile=ca)

NARR = ("it-IT-DiegoNeural", "-6%", "-6Hz")
WHISP = ("it-IT-IsabellaNeural", "-35%", "-2Hz")
LINES = [
    ("N1", NARR, "Questo paese è rimasto sott'acqua per quarantotto anni. Stanotte... è tornato fuori."),
    ("N2", NARR, "Greta registra suoni per il cinema. La pagano per una cosa sola: registrare il silenzio di Valsorda, prima che all'alba richiudano la diga."),
    ("N3", NARR, "Ma appena accende il microfono... il silenzio non c'è."),
    ("N4", NARR, "Riascolta la registrazione. Ci sono dei passi. Intorno a lei. E si fermano... esattamente quando si ferma lei."),
    ("N5a", NARR, "Poi, suona una campana."),
    ("N5b", NARR, "Ma il campanile è vuoto. La campana l'hanno portata via nel millenovecentosettantasei."),
    ("N6", NARR, "Sotto la porta della chiesa, si accende una luce. E nelle cuffie, una voce sussurra il suo nome."),
    ("W", WHISP, "Greta..."),
    ("N7", NARR, "Cosa deve fare Greta? Uno: entrare in chiesa. Due: tornare alla macchina. Ma i passi... vengono da lì."),
    ("N8", NARR, "Scrivilo nei commenti. Nella parte due, farà quello che sceglie la maggioranza."),
]


async def one(out, key, voice, text):
    v, rate, pitch = voice
    com = edge_tts.Communicate(text, v, rate=rate, pitch=pitch, boundary="WordBoundary")
    audio, words = bytearray(), []
    async for ch in com.stream():
        if ch["type"] == "audio":
            audio += ch["data"]
        elif ch["type"] == "WordBoundary":
            s = ch["offset"] / 1e7
            words.append([ch["text"], s, s + ch["duration"] / 1e7])
    open(os.path.join(out, key + ".mp3"), "wb").write(audio)
    # riattacca la punteggiatura del testo alle parole (Edge la omette)
    toks, j = text.split(), 0
    for w in words:
        while j < len(toks) and w[0].lower() not in toks[j].lower():
            j += 1
        if j < len(toks):
            w[0] = toks[j]
            j += 1
    json.dump({"text": text, "words": words}, open(os.path.join(out, key + ".json"), "w"), ensure_ascii=False)
    print("ok", key, len(words), "parole")


async def main(out):
    for k, v, t in LINES:
        await one(out, k, v, t)

asyncio.run(main(sys.argv[1]))
