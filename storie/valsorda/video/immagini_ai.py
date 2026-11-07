"""Genera le immagini cinematografiche 9:16 (Flux via pollinations.ai, gratuito).
Esegui dentro la cartella di destinazione (es. assets/ep01/img) con PYTHONHASHSEED=0 per avere gli stessi seed.
"""
import sys, time, urllib.parse, subprocess, os
STYLE = ", cinematic film still, night, horror atmosphere, cold blue teal color grading, volumetric fog, 35mm photo, photorealistic, highly detailed, dark, moody"
SHOTS = {
 "01_paese": "ruins of a small italian alpine stone village emerging from a drained reservoir lake bed, cracked mud everywhere, enormous concrete dam wall in the background, moonlight, a stone bell tower in the middle of the ruins",
 "02_campanile_lago": "aerial view of an old church bell tower and stone houses sticking out of a muddy drained lake, puddles reflecting moonlight, mountains around",
 "03_greta_spalle": "young woman seen from behind wearing big studio headphones and a headlamp, holding a boom microphone with a furry windscreen, standing in a muddy street between ruined stone houses covered in dried algae",
 "04_registratore": "close-up of a portable field audio recorder in a woman's hands, red REC light glowing, small screen with audio waveform, muddy background, shallow depth of field",
 "05_impronte": "close-up of fresh bare footprints in wet mud circling around a pair of boots, lit by a flashlight beam, nobody there",
 "06_strada": "empty muddy narrow street between ruined stone houses, thick fog at the end of the street, flashlight beam, ominous, nobody visible",
 "07_greta_volto": "close-up side profile of a young woman with headphones listening intently, frightened eyes, face lit by a headlamp, darkness behind her",
 "08_campanile_vuoto": "low angle view of an old stone bell tower with empty arches and no bell, night sky with moon behind, mist, ominous",
 "09_porta": "old wooden church door at night with warm candle light leaking from the gap under the door, muddy stone steps, dried algae on the walls",
 "10_cuffie": "extreme close-up of studio headphones on a young woman's ear, strands of wet hair, darkness, a faint warm light reflected",
 "11_auto": "a small car parked alone at the edge of a drained lake, seen from far away in the dark, muddy footprints leading towards it, fog, moonlight",
 "12_dentro": "inside a dark flooded old church, candles burning on a muddy altar, overturned wooden pews, warm light and deep shadows",
}
for name, p in SHOTS.items():
    out = f"{name}.jpg"
    if os.path.exists(out) and os.path.getsize(out) > 20000:
        continue
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(p + STYLE) + "?width=1080&height=1920&model=flux&nologo=true&seed=" + str(abs(hash(name)) % 10000)
    for attempt in range(4):
        r = subprocess.run(["curl", "-sS", "-o", out, "-w", "%{http_code}", "--max-time", "150", url], capture_output=True, text=True)
        if r.stdout == "200" and os.path.getsize(out) > 20000:
            print("ok", name, flush=True); break
        print("retry", name, r.stdout, r.stderr[:100], flush=True); time.sleep(10 * (attempt + 1))
    time.sleep(3)
