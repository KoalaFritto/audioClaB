#!/usr/bin/env python3
"""ROOM 9 – Part 1. Flat vector interactive Reel (English).

Riusa il motore di VALSORDA (sound design, caricamento voce, render Chromium).
Uso:
    python3 genera_room9.py --vo voice --out room9-ep01.mp4 [--tempo 1.05] [--frames 3,10]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VALS = os.path.join(HERE, "..", "..", "valsorda", "video")
sys.path.insert(0, VALS)
sys.path.insert(0, os.path.join(VALS, "flat"))
import genera_ep01 as g  # noqa: E402
import genera_ep01_v2 as v2  # noqa: E402
from genera_flat import load_vo  # noqa: E402

SR, FPS = g.SR, 30
RNG = np.random.default_rng(9)
DISPLAY = {("N3", "one"): "1:12,", ("N3", "twelve,"): "", ("N6", "three"): "3:07,", ("N6", "oh"): "", ("N6", "seven,"): "",
           ("N5", "Three"): "3", ("R1", "nine"): "9", ("N1", "nine"): "9", ("N1", "eight"): "8", ("N3", "nine."): "9."}
SCARY = {"NINE", "9", "9.", "EIGHT", "8", "RING.", "RING", "KNOCKS.", "NORA.", "LENS.", "YOURSELF", "AWAY.", "NINTH", "DOESN'T", "EXIST.", "BUZZES."}


# ----------------------------------------------------------------------------- sfx
def env_ar(n, a, r):
    t = np.arange(n) / SR
    return (1 - np.exp(-t / a)) * np.exp(-t / r)


def ring_burst(d=0.38):
    n = int(d * SR)
    t = np.arange(n) / SR
    clap = (np.sin(2 * np.pi * 20 * t) > 0).astype(float)
    s = (np.sin(2 * np.pi * 1180 * t) + .7 * np.sin(2 * np.pi * 1530 * t) + .3 * np.sin(2 * np.pi * 2350 * t)) * (0.35 + 0.65 * clap)
    s *= np.minimum(1, t / .01) * np.minimum(1, (d - t) / .03)
    return s / np.max(np.abs(s))


def buzz(d=0.32):
    n = int(d * SR)
    t = np.arange(n) / SR
    s = np.sign(np.sin(2 * np.pi * 165 * t)) * 0.6 + np.sin(2 * np.pi * 330 * t) * 0.3
    s = g.fft_filter(s, hi=900) * np.minimum(1, t / .01) * np.minimum(1, (d - t) / .02)
    return s / np.max(np.abs(s))


def knock():
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * (95 + 40 * np.exp(-t / .02)) * t) * np.exp(-t / .07)
    s += g.fft_filter(RNG.standard_normal(n), lo=200, hi=1800) * np.exp(-t / .012) * 0.8
    return s / np.max(np.abs(s))


def lock_clack():
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    s = g.fft_filter(RNG.standard_normal(n), lo=1500, hi=7000) * np.exp(-t / .01)
    t2 = np.clip(t - .09, 0, None)
    s += (g.fft_filter(RNG.standard_normal(n), lo=900, hi=5000) * np.exp(-t2 / .015)) * (t > .09)
    s += np.sin(2 * np.pi * 1870 * t2) * np.exp(-t2 / .12) * 0.25 * (t > .09)
    return s / np.max(np.abs(s))


def hum(n):
    t = np.arange(n) / SR
    s = 0.5 * np.sin(2 * np.pi * 120 * t) + 0.25 * np.sin(2 * np.pi * 240 * t) + 0.12 * np.sin(2 * np.pi * 360 * t)
    s += g.fft_filter(RNG.standard_normal(n), lo=2000, hi=6000) * 0.05
    return s


def rain(n):
    s = g.fft_filter(RNG.standard_normal(n), lo=700, hi=7000)
    drops = np.zeros(n)
    for i in RNG.integers(0, n - 400, n // 900):
        drops[i:i + 300] += np.exp(-np.arange(300) / 40) * RNG.uniform(.2, 1)
    return s * 0.6 + g.fft_filter(drops * RNG.standard_normal(n), lo=1500) * 0.8


def static(d):
    n = int(d * SR)
    return g.fft_filter(RNG.standard_normal(n), lo=1200, hi=9000) * np.minimum(1, np.arange(n) / 300) * np.minimum(1, (n - np.arange(n)) / 300)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tempo", type=float, default=1.05)
    ap.add_argument("--frames", default=None)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    keys = ["N1", "N2", "R1", "R2", "R3", "N3", "N4", "N5", "N6", "N7", "V", "N8", "N9", "N10"]
    vo = {k: load_vo(a.vo, k, a.tempo) for k in keys}

    def vd(k):
        return len(vo[k][0]) / SR

    gaps = {"N1": 0.5, "N2": 0.4, "R1": 0.5, "R2": 0.35, "R3": 0.35, "N3": 0.7, "N4": 0.3, "N5": 2.6, "N6": 0.6,
            "N7": 1.3, "V": 1.0, "N8": 0.6, "N9": 0.8, "N10": 0.4}
    T, t = {}, 0.0
    for k in keys:
        t += gaps[k]
        T[k] = t
        t += vd(k)
    T["end"] = t + 2.2
    dur = T["end"]

    def wt(k, word, nth=0):
        wl = word.lower().strip(".,:?!…")
        hits = [w for w in vo[k][1] if w[0].lower().strip(".,:?!…") == wl] or \
               [w for w in vo[k][1] if w[0].lower().strip(".,:?!…").startswith(wl)]
        return T[k] + hits[nth][1]

    M = {
        "ringStart": wt("N3", "lights") + 0.2, "ringStop": wt("N4", "stops") + 0.15, "buzz": wt("N4", "buzzes"),
        "lock": wt("N5", "locks") + 0.25, "knock": wt("N6", "knocks") + 0.2, "nametag": wt("N7", "Nora."),
        "woman": wt("N7", "woman"), "turn": wt("N8", "turns"), "lens": wt("N8", "lens"),
        "A": wt("N9", "A:"), "B": wt("N9", "B:"), "note": wt("N2", "note."),
    }
    shots = [
        (0.0, "motel", "11:52 PM"),
        (T["N2"] - 0.1, "desk", "11:58 PM"),
        (M["note"] - 0.05, "note", "11:59 PM"),
        (T["N3"] - 0.15, "switchboard", "1:12 AM"),
        (M["buzz"] - 0.05, "textmsg", "1:13 AM"),
        (T["N5"] - 0.1, "lock", "3:00 AM"),
        (T["N6"] - 0.1, "knock", "3:07 AM"),
        (T["N7"] - 0.1, "cctv", "3:07 AM"),
        (T["V"] - 0.3, "voice", "3:08 AM"),
        (T["N8"] - 0.1, "turn", "3:08 AM"),
        (T["N9"] - 0.1, "choice", "3:08 AM"),
        (T["N10"] - 0.1, "finale", "3:08 AM"),
    ]
    booms = [T["R1"] - 0.05, M["ringStart"], M["buzz"], M["knock"], M["nametag"], M["lens"], T["N10"] - 0.1]

    # ---- audio
    print(f"Durata {dur:.1f} s · audio…", flush=True)
    mix = g.Mix(dur)
    n = mix.n
    tt = np.arange(n) / SR
    vo_bus = np.zeros(n)
    for k in keys:
        if k == "V":
            continue
        x = vo[k][0]
        i = int(T[k] * SR)
        vo_bus[i:i + len(x)] += x[: n - i]
    vo_bus *= 0.9 / np.max(np.abs(vo_bus))
    venv = np.convolve(np.abs(vo_bus), np.ones(4800) / 4800, mode="same")
    duck = 1 - 0.55 * np.clip(venv * 12, 0, 1)
    dr = g.drone(n, 0)
    denv = np.interp(tt, [0, T["R1"], T["N3"], T["N6"], T["V"] - 0.4, T["V"] - 0.3, T["N8"], T["N8"] + 0.5, dur],
                     [0.35, 0.5, 0.6, 0.8, 0.95, 0.0, 0.0, 0.9, 0.7])
    mix.dry += dr * denv * duck * 0.42
    rn = rain(n)
    renv = np.interp(tt, [0, T["N2"], T["N2"] + .5, T["V"] - .3, T["V"], T["N8"], dur], [1, 1, .45, .45, .25, .45, .45])
    mix.add(rn * renv * duck, 0, 0.12, -0.3)
    mix.add(rn[::-1] * renv * duck, 0, 0.12, 0.3)
    mix.add(hum(n) * np.interp(tt, [0, T["N2"], dur], [.6, .35, .35]), 0, 0.05, 0.0)
    for tb in booms:
        mix.add(v2.boom(), tb, 0.5, 0.0, wet=0.2)
    for s0, sid, _ in shots[1:]:
        if s0 not in booms and sid not in ("voice",):
            mix.add(v2.whoosh(), max(0, s0 - 0.25), 0.14, RNG.uniform(-0.4, 0.4), wet=0.3)
    # squilli della stanza 9 (nove)
    rings, t = [], M["ringStart"]
    step = (M["ringStop"] - M["ringStart"]) / 9
    for i in range(9):
        mix.add(ring_burst(min(0.38, step * 0.6)), t, 0.32, 0.15, wet=0.25)
        rings.append(round(t, 3))
        t += step
    mix.add(buzz(), M["buzz"], 0.5, 0.0)
    mix.add(buzz(), M["buzz"] + 0.45, 0.5, 0.0)
    mix.add(lock_clack(), M["lock"], 0.55, -0.1, wet=0.25)
    knocks = [M["knock"] + i * 0.36 for i in range(3)] + [T["N7"] + 0.2 + i * 0.36 for i in range(3)]
    for kt in knocks:
        mix.add(knock(), kt, 0.75, 0.0, wet=0.3)
    mix.add(static(0.5), T["N7"] - 0.1, 0.12, 0.0)
    mix.add(static(0.35), M["lens"], 0.2, 0.0)
    mix.add(v2.riser(1.8), M["lens"] - 1.8, 0.18, 0.0)
    t = T["N9"] + 0.2
    while t < dur - 0.4:
        mix.add(v2.heartbeat(), t, 0.5, 0.0)
        mix.add(v2.heartbeat(), t + 0.27, 0.32, 0.0)
        t += 0.92
    irL, irR = g.make_ir(2.4, 1.8, 5000, 1), g.make_ir(2.4, 1.8, 5000, 2)
    out = mix.dry.copy()
    out[0] += g.conv(mix.send[0], irL) * 0.5
    out[1] += g.conv(mix.send[1], irR) * 0.5
    gcut = np.interp(tt, [T["V"] - 0.4, T["V"] - 0.3, T["N8"] - 0.2, T["N8"] + 0.3], [1, 0.05, 0.05, 1])
    out *= gcut
    # voce dietro la porta: attutita, un filo di stanza
    vbuf = np.zeros(n)
    vx = g.fft_filter(vo["V"][0], lo=180, hi=2300)
    vx /= np.max(np.abs(vx))
    iv = int(T["V"] * SR)
    vbuf[iv:iv + len(vx)] = vx[: n - iv]
    vr = g.conv(vbuf, irL) * 0.25
    out[0] += (vbuf + vr) * 0.62
    out[1] += (vbuf * 0.8 + g.conv(vbuf, irR) * 0.25) * 0.62
    out += (vo_bus + g.conv(vo_bus, irL) * 0.05) * 0.95
    out = np.tanh(out * 1.3) / np.tanh(1.3)
    out *= 0.89 / np.max(np.abs(out))
    work = tempfile.mkdtemp(prefix="room9_")
    wav_path = os.path.join(work, "a.wav")
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((out.T * 32767).astype(np.int16).tobytes())

    # ---- sottotitoli (la voce dietro la porta compare come testo, non come sottotitolo)
    caps = []
    for k in keys:
        if k in ("N10",):
            continue
        groups, cur = [], []
        for w in vo[k][1]:
            cur.append(w)
            if len(cur) == 3 or w[0][-1] in ".,?!…" or len(" ".join(x[0] for x in cur)) > 16:
                groups.append(cur)
                cur = []
        if cur:
            groups.append(cur)
        for grp in groups:
            disp_all = [DISPLAY.get((k, w[0]), w[0]).upper() for w in grp]
            disp = [d for d in disp_all if d]
            if not disp:
                continue
            for i, w in enumerate(grp):
                s = T[k] + w[1]
                e = T[k] + (grp[i + 1][1] if i + 1 < len(grp) else w[2] + 0.25)
                idx = max(0, sum(1 for d in disp_all[:i + 1] if d) - 1)
                caps.append({"s": round(s, 3), "e": round(e, 3), "w": disp, "i": idx, "v": k == "V"})

    tl = {"dur": dur, "fps": FPS, "T": {k: round(v, 3) for k, v in T.items()}, "M": {k: round(v, 3) for k, v in M.items()},
          "shots": [{"t": round(s, 3), "id": i, "clock": c} for s, i, c in shots], "booms": [round(b, 3) for b in booms],
          "rings": rings, "knocks": [round(k, 3) for k in knocks], "caps": caps, "scary": sorted(SCARY)}
    tl_path = os.path.join(work, "timeline.json")
    json.dump(tl, open(tl_path, "w"))
    frames_dir = os.path.join(work, "frames")
    os.makedirs(frames_dir)
    only = [int(float(x) * FPS) for x in a.frames.split(",")] if a.frames else []
    print("Render…", flush=True)
    subprocess.run(["node", os.path.join(VALS, "flat", "render.js"), os.path.join(HERE, "scene.html"), tl_path, frames_dir,
                    str(a.workers), ",".join(map(str, only))], check=True)
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
