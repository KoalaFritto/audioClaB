"""Genera la narrazione con ElevenLabs (Adam) + timestamp per i sottotitoli.
Esegui dentro la cartella di destinazione (es. assets/ep01/voce). Serve la chiave ElevenLabs
(in questo ambiente viene iniettata dal proxy; altrove sostituisci "proxy-injected" con la tua chiave).
Uso: python3 ../../voce_elevenlabs.py [CHIAVE_BATTUTA ...]
"""
import json, base64, urllib.request, sys, os
ADAM = "pNInz6obpgDQGcFmaJgB"
LILY = "pFZP5JQG7iQjIQuC4Bku"
LINES = [
 ("N1", ADAM, "Questo paese è rimasto sott'acqua per quarantotto anni. Stanotte... è tornato fuori."),
 ("N2", ADAM, "Greta registra suoni per il cinema. La pagano per una cosa sola: registrare il silenzio di Valsorda, prima che all'alba richiudano la diga."),
 ("N3", ADAM, "Ma appena accende il microfono... il silenzio non c'è."),
 ("N4", ADAM, "Riascolta la registrazione. Ci sono dei passi. Intorno a lei. E si fermano... esattamente quando si ferma lei."),
 ("N5a", ADAM, "Poi, suona una campana."),
 ("N5b", ADAM, "Ma il campanile è vuoto. La campana l'hanno portata via nel millenovecentosettantasei."),
 ("N6", ADAM, "Sotto la porta della chiesa, si accende una luce. E nelle cuffie, una voce sussurra il suo nome."),
 ("W", LILY, "Greta..."),
 ("N7", ADAM, "Cosa deve fare Greta? Uno: entrare in chiesa. Due: tornare alla macchina. Ma i passi... vengono da lì."),
 ("N8", ADAM, "Scrivilo nei commenti. Nella parte due, farà quello che sceglie la maggioranza."),
]
only = sys.argv[1:]
for key, voice, text in LINES:
    if only and key not in only: continue
    if os.path.exists(key + ".json") and not only: continue
    settings = {"stability": 0.45, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True, "speed": 0.95}
    if key == "W":
        settings = {"stability": 0.25, "similarity_boost": 0.7, "style": 0.6, "use_speaker_boost": False, "speed": 0.8}
    body = json.dumps({"text": text, "model_id": "eleven_multilingual_v2", "language_code": "it", "voice_settings": settings}).encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_128",
                                 data=body, headers={"xi-api-key": "proxy-injected", "Content-Type": "application/json"})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=120))
    except urllib.error.HTTPError as e:
        print(key, e.code, e.read()[:300]); continue
    open(key + ".mp3", "wb").write(base64.b64decode(d["audio_base64"]))
    json.dump({"text": text, "alignment": d.get("alignment")}, open(key + ".json", "w"), ensure_ascii=False)
    print("ok", key, len(text), flush=True)
