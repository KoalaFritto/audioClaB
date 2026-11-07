#!/usr/bin/env python3
"""VALSORDA Ep. 1 – ENGLISH flat vector version (rules format).

1. legge la voce (ElevenLabs con 'alignment' oppure Edge TTS con 'words')
2. costruisce la timeline (scene agganciate alle parole del narratore) e il sound design
3. fa disegnare a Chromium (Playwright) le scene SVG di scene.html, fotogramma per fotogramma
4. monta video + audio con ffmpeg

Uso:
    python3 genera_flat.py --vo voce-provvisoria --out ep-01-flat.mp4 [--tempo 1.0] [--frames 3,10,20]
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import genera_ep01 as g  # noqa: E402  sound design condiviso
import genera_ep01_v2 as v2  # noqa: E402  boom, whoosh, riser, heartbeat

SR, FPS = g.SR, 30
DISPLAY = {"nineteen": "1976.", "seventy-six.": "", "forty-eight": "48"}
RNG = np.random.default_rng(7)


def load_vo(vo_dir, key, tempo):
    d = json.load(open(os.path.join(vo_dir, key + ".json"), encoding="utf-8"))
    af = f"atempo={tempo}" if abs(tempo - 1) > 1e-3 else "anull"
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", os.path.join(vo_dir, key + ".mp3"), "-af", af,
                          "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
    if "words" in d:
        words = [[w, s / tempo, e / tempo] for w, s, e in d["words"]]
    else:  # ElevenLabs
        al = d["alignment"]
        words, cur, cs, pe = [], "", None, 0
        for ch, s, e in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
            if ch.isspace():
                if cur:
                    words.append([cur, cs / tempo, pe / tempo])
                cur, cs = "", None
            else:
                cs = s if cs is None else cs
                cur += ch
                pe = e
        if cur:
            words.append([cur, cs / tempo, pe / tempo])
    # rifila il silenzio iniziale
    idx = np.where(np.abs(audio) > 0.01)[0]
    lead = max(0, idx[0] - 600) if len(idx) else 0
    audio = audio[lead: (idx[-1] + 2400) if len(idx) else None]
    off = lead / SR
    words = [[w, max(0, s - off), max(0, e - off)] for w, s, e in words]
    return audio, words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tempo", type=float, default=1.0)
    ap.add_argument("--frames", default=None, help="solo questi secondi, salvati come PNG accanto a --out")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    keys = ["N1", "N2", "N2b", "N3", "N4", "N5a", "N5b", "N6", "W", "N7", "N8"]
    vo = {k: load_vo(a.vo, k, a.tempo) for k in keys}

    def vd(k):
        return len(vo[k][0]) / SR

    gaps = {"N1": 0.6, "N2": 0.35, "N2b": 0.4, "N3": 0.3, "N4": 0.5, "N5a": 0.5, "N5b": 1.9, "N6": 0.45, "W": 0.4, "N7": 1.1, "N8": 0.3}
    T, t = {}, 0.0
    for k in keys:
        t += gaps[k]
        T[k] = t
        t += vd(k)
    T["bell"] = T["N5a"] + vd("N5a") + 0.12
    T["end"] = t + 2.0
    dur = T["end"]

    def wt(k, word, nth=0):
        wl = word.lower().strip(".,:?!…")
        hits = [w for w in vo[k][1] if (w[0].lower().strip(".,:?!…") == wl) if len(wl) <= 2] or \
               [w for w in vo[k][1] if w[0].lower().strip(".,:?!…").startswith(wl)]
        return T[k] + hits[nth][1]

    # ---- scene (id definiti in scene.html)
    shots = [
        (0.0, "lago"),
        (T["N2"] - 0.1, "camminata"),
        (wt("N2", "paid"), "notifica"),
        (wt("N2", "before"), "diga"),
        (T["N2b"] - 0.1, "regole"),
        (T["N3"] - 0.1, "rec"),
        (T["N4"] - 0.15, "riascolto"),
        (wt("N4", "footsteps"), "passi"),
        (T["N5a"] - 0.1, "campanile"),
        (T["N6"] - 0.1, "porta"),
        (wt("N6", "headphones"), "cuffie"),
        (T["W"] - 0.05, "sussurro"),
        (T["N7"] - 0.3, "bivio"),
        (wt("N7", "A:"), "sceltaA"),
        (wt("N7", "B:"), "sceltaB"),
        (T["N8"] - 0.1, "finale"),
    ]
    booms = [T["N2b"] - 0.1, T["N3"] - 0.1, wt("N4", "footsteps"), T["N6"] - 0.1, wt("N7", "A:"), wt("N7", "B:"), T["N8"] - 0.1]
    whooshes = [s[0] - 0.25 for s in shots[1:] if s[0] not in booms and s[1] not in ("sussurro",)]

    # ---- audio
    print(f"Durata {dur:.1f} s · audio…", flush=True)
    mix = g.Mix(dur)
    n = mix.n
    tt = np.arange(n) / SR
    vo_bus = np.zeros(n)
    for k in keys:
        if k == "W":
            continue
        x = vo[k][0]
        i = int(T[k] * SR)
        vo_bus[i:i + len(x)] += x[: n - i]
    vo_bus *= 0.9 / np.max(np.abs(vo_bus))
    venv = np.convolve(np.abs(vo_bus), np.ones(4800) / 4800, mode="same")
    duck = 1 - 0.55 * np.clip(venv * 12, 0, 1)
    dr = g.drone(n, 0)
    denv = np.interp(tt, [0, 3, T["N4"], T["bell"], T["W"] - 0.05, T["W"], T["N7"] - 0.3, T["N7"], dur],
                     [0.45, 0.55, 0.7, 0.9, 1.0, 0.0, 0.0, 0.55, 0.55])
    mix.dry += dr * denv * duck * 0.42
    wd = g.wind(n)
    wenv = np.interp(tt, [0, T["W"] - 0.05, T["W"], T["N7"], dur], [0.6, 0.5, 0, 0.3, 0.3])
    mix.add(wd * duck * wenv, 0, 0.4, -0.3)
    mix.add(wd[::-1] * duck * wenv, 0, 0.4, 0.3)
    # acqua che si ritira nell'intro
    water = g.fft_filter(RNG.standard_normal(int(4 * SR)), lo=150, hi=1800) * np.hanning(int(4 * SR))
    mix.add(water, 0.0, 0.25, 0.0, wet=0.4)
    for tb in booms:
        mix.add(v2.boom(), tb, 0.5, 0.0, wet=0.2)
    for tw in whooshes:
        mix.add(v2.whoosh(), max(0, tw), 0.15, RNG.uniform(-0.4, 0.4), wet=0.3)
    # passi di Greta mentre cammina
    t = T["N2"]
    while t < wt("N2", "paid") - 0.2:
        mix.add(g.step_mud(), t, 0.16, 0.0, wet=0.15)
        t += 0.55
    # passi tutt'intorno: registro anche dove compaiono le impronte
    steps = []
    t0 = wt("N4", "footsteps") + 0.3
    stop = wt("N4", "exactly") + 0.3
    for pan, st in [(-0.9, 0.0), (0.85, 0.3), (-0.5, 0.75), (0.6, 1.15), (-0.8, 1.55), (0.95, 1.85), (0.1, 2.2)]:
        t = t0 + st
        per = RNG.uniform(0.5, 0.7)
        while t < stop:
            mix.add(g.step_mud(0.7), t, RNG.uniform(0.14, 0.24), pan, wet=0.35)
            steps.append([round(t, 3), pan])
            t += per
    mix.add(g.step_mud(1.3), stop - 0.15, 0.4, -0.1, wet=0.2)
    steps.append([round(stop - 0.15, 3), 0.0])
    # campana
    mix.add(v2.riser(2.0), T["bell"] - 2.0, 0.2, 0.0)
    b = g.bell(174, 9, 1.0)
    mix.add(b, T["bell"], 0.8, 0.0, wet=0.75)
    mix.add(g.fft_filter(b, hi=200), T["bell"], 0.6, 0.0)
    mix.add(v2.boom(2.5), T["bell"], 0.55, 0.0)
    for _ in range(16):
        mix.add(g.drip(), RNG.uniform(1, T["W"]), RNG.uniform(0.04, 0.09), RNG.uniform(-0.9, 0.9), wet=0.8)
    mix.add(g.crackle(0.3), T["W"] - 0.3, 0.15, 0.6)
    t = T["N7"] + 0.2
    while t < dur - 0.4:
        mix.add(v2.heartbeat(), t, 0.55, 0.0)
        mix.add(v2.heartbeat(), t + 0.27, 0.35, 0.0)
        t += 0.95
    irL, irR = g.make_ir(3.0, 2.6, 5000, 1), g.make_ir(3.0, 2.6, 5000, 2)
    out = mix.dry.copy()
    out[0] += g.conv(mix.send[0], irL) * 0.55
    out[1] += g.conv(mix.send[1], irR) * 0.55
    gcut = np.interp(tt, [T["W"] - 0.08, T["W"] - 0.02, T["N7"] - 0.4, T["N7"]], [1, 0.03, 0.03, 1])
    out *= gcut
    wbuf = np.zeros(n)
    wx = g.whisperize(vo["W"][0]) * 0.5 + vo["W"][0] / np.max(np.abs(vo["W"][0])) * 0.6
    wx /= np.max(np.abs(wx))
    iw = int(T["W"] * SR)
    wbuf[iw:iw + len(wx)] = wx[: n - iw]
    out[1] += (wbuf + g.conv(wbuf, irR) * 0.45) * 0.55
    out[0] += (wbuf * 0.05 + g.conv(wbuf, irL) * 0.12) * 0.55
    out += (vo_bus + g.conv(vo_bus, irL) * 0.06) * 0.95
    out = np.tanh(out * 1.3) / np.tanh(1.3)
    out *= 0.89 / np.max(np.abs(out))
    work = tempfile.mkdtemp(prefix="flat_")
    wav_path = os.path.join(work, "a.wav")
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((out.T * 32767).astype(np.int16).tobytes())
    mono = out.mean(0)
    nfr = int(dur * FPS)
    amp = [float(np.sqrt(np.mean(mono[int(i / FPS * SR): int((i + 1) / FPS * SR)] ** 2))) for i in range(nfr)]
    mx = max(amp) or 1
    amp = [round(x / mx, 3) for x in amp]

    # ---- sottotitoli (gruppi max 3 parole)
    caps = []
    for k in keys:
        if k in ("W", "N8"):
            continue
        ws, cur = vo[k][1], []
        groups = []
        for w in ws:
            cur.append(w)
            if len(cur) == 3 or w[0][-1] in ".,?!…" or len(" ".join(x[0] for x in cur)) > 16:
                groups.append(cur)
                cur = []
        if cur:
            groups.append(cur)
        for grp in groups:
            disp_all = [DISPLAY.get(w[0], w[0]).upper() for w in grp]
            disp = [d for d in disp_all if d]
            for i, w in enumerate(grp):
                s = T[k] + w[1]
                e = T[k] + (grp[i + 1][1] if i + 1 < len(grp) else w[2] + 0.25)
                idx = sum(1 for d in disp_all[:i + 1] if d) - 1
                caps.append({"s": round(s, 3), "e": round(e, 3), "w": disp, "i": max(0, idx)})

    tl = {
        "dur": dur, "fps": FPS, "T": {k: round(v, 3) for k, v in T.items()},
        "shots": [{"t": round(s, 3), "id": i} for s, i in shots],
        "booms": [round(b, 3) for b in booms], "steps": steps, "caps": caps, "amp": amp,
        "mark": {"stanotte": round(wt("N1", "Tonight"), 3), "silenzio": round(wt("N3", "silence"), 3),
                 "fermano": round(wt("N4", "stop..."), 3), "vuoto": round(wt("N5b", "empty"), 3),
                 "luce": round(wt("N6", "light"), 3), "passi7": round(wt("N7", "footsteps"), 3),
                 "riascolta": round(T["N4"], 3), "passi": round(wt("N4", "footsteps"), 3),
                 "r1": round(wt("N2b", "One"), 3), "r2": round(wt("N2b", "Two"), 3), "r3": round(wt("N2b", "Three", 1), 3)},
    }
    tl_path = os.path.join(work, "timeline.json")
    json.dump(tl, open(tl_path, "w"))

    # ---- render
    frames_dir = os.path.join(work, "frames")
    os.makedirs(frames_dir)
    only = [int(float(x) * FPS) for x in a.frames.split(",")] if a.frames else []
    cmd = ["node", os.path.join(HERE, "render.js"), os.path.join(HERE, "scene.html"), tl_path, frames_dir,
           str(a.workers), ",".join(map(str, only))]
    print("Render…", flush=True)
    subprocess.run(cmd, check=True)
    if only:
        for f in sorted(os.listdir(frames_dir)):
            shutil.copy(os.path.join(frames_dir, f), a.out.replace(".png", "_" + f))
        print("Fotogrammi salvati", flush=True)
        return
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(frames_dir, "%05d.jpg"),
                    "-i", wav_path, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-af", "loudnorm=I=-14:TP=-1.0:LRA=11", "-ar", "48000",
                    "-shortest", "-movflags", "+faststart", a.out], check=True)
    shutil.rmtree(work, ignore_errors=True)
    print("Fatto", a.out, flush=True)


if __name__ == "__main__":
    main()
