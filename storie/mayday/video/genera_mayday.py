#!/usr/bin/env python3
"""MAYDAY – Part 1. Flat vector interactive Reel (English, survival adventure).

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
DISPLAY = {("N2", "Nine"): "9", ("N2", "Twenty-one"): "21", ("N3", "two"): "2:47", ("N3", "forty-seven"): "", ("N8", "nine"): "9", ("N1", "three."): "3."}
SCARY = {"CRACKS", "9", "EMPTY.", "MAYDAY,", "MAYDAY.", "STILL", "STORM.", "CREW.", "WATER.", "ANYONE.", "LIGHTS"}


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


def sea(n):
    t = np.arange(n) / SR
    swell = 0.55 + 0.45 * np.sin(2 * np.pi * 0.11 * t) * np.sin(2 * np.pi * 0.047 * t + 1)
    s = g.fft_filter(RNG.standard_normal(n), lo=60, hi=700) * swell
    s += g.fft_filter(RNG.standard_normal(n), lo=1500, hi=6000) * 0.25 * np.clip(swell - 0.5, 0, 1)
    return s


def wave_hit():
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    s = g.fft_filter(RNG.standard_normal(n), lo=80, hi=3000) * (1 - np.exp(-t / .05)) * np.exp(-t / .6)
    return s / np.max(np.abs(s))


def crack():
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    s = g.fft_filter(RNG.standard_normal(n), lo=1200, hi=8000) * np.exp(-t / .008)
    s += g.fft_filter(RNG.standard_normal(n), lo=200, hi=1500) * np.exp(-np.clip(t - .03, 0, None) / .12) * (t > .03) * .6
    return s / np.max(np.abs(s))


def gush(d):
    n = int(d * SR)
    t = np.arange(n) / SR
    s = g.fft_filter(RNG.standard_normal(n), lo=300, hi=3500) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 7 * t)))
    return s * np.minimum(1, t / .05) * np.minimum(1, (d - t) / .4)


def radar_ping():
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1450 * t) * np.exp(-t / .25) * (1 - np.exp(-t / .002))


def ding():
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    a = np.sin(2 * np.pi * 1318 * t) * np.exp(-t / .12)
    b = np.sin(2 * np.pi * 1760 * t) * np.exp(-np.clip(t - .11, 0, None) / .15) * (t > .11)
    return (a + b) / 2


def groan(d=2.5):
    n = int(d * SR)
    t = np.arange(n) / SR
    f = 55 + 8 * np.sin(2 * np.pi * 0.7 * t)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sign(np.sin(2 * np.pi * np.cumsum(f * 2.01) / SR))
    s = g.fft_filter(s, hi=600) * np.sin(np.pi * t / d) ** 2
    return s / np.max(np.abs(s))


def radio_fx(x):
    y = g.fft_filter(x, lo=320, hi=2800)
    y = np.tanh(y / (np.max(np.abs(y)) + 1e-9) * 2.5)
    y += g.fft_filter(RNG.standard_normal(len(y)), lo=1000, hi=5000) * 0.08
    return y / np.max(np.abs(y))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--tempo", type=float, default=1.05)
    ap.add_argument("--frames", default=None)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    keys = ["N1", "N2", "N3", "RADIO", "N4", "N5", "N6", "N7", "N8", "N9"]
    vo = {k: load_vo(a.vo, k, a.tempo) for k in keys}

    def vd(k):
        return len(vo[k][0]) / SR

    gaps = {"N1": 0.5, "N2": 0.6, "N3": 0.8, "RADIO": 0.5, "N4": 0.5, "N5": 0.4, "N6": 3.4, "N7": 0.5, "N8": 0.8, "N9": 0.4}
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
        "wave": wt("N1", "wave"), "crack": wt("N1", "cracks") + 0.1, "radio": wt("N3", "radio"),
        "msg": T["N5"] + vd("N5") + 0.5, "reply": T["N5"] + vd("N5") + 1.7, "lights": wt("N6", "lights"),
        "still": wt("N6", "still"), "rope": wt("N7", "rope"), "crates": wt("N7", "crates"),
        "A": wt("N8", "A:"), "B": wt("N8", "B:"),
    }
    shots = [
        (0.0, "maraIntro", "4:12 PM"),
        (wt("N1", "Then") - 0.05, "sea", "4:12 PM"),
        (T["N2"] - 0.1, "chart", "4:13 PM"),
        (T["N3"] - 0.15, "cabin", "2:47 AM"),
        (T["RADIO"] - 0.1, "radio", "2:47 AM"),
        (T["N4"] - 0.1, "radar", "2:48 AM"),
        (T["N5"] - 0.1, "satphone", "2:49 AM"),
        (T["N6"] - 0.1, "ship", "2:53 AM"),
        (M["rope"] - 0.05, "ladder", "2:54 AM"),
        (M["crates"] - 0.05, "crates", "2:54 AM"),
        (T["N8"] - 0.1, "choice", "2:54 AM"),
        (T["N9"] - 0.1, "finale", "2:54 AM"),
    ]
    booms = [M["wave"], M["crack"], T["RADIO"] - 0.1, M["reply"], M["lights"], M["crates"], T["N9"] - 0.1]

    # ---- audio
    print(f"Durata {dur:.1f} s · audio…", flush=True)
    mix = g.Mix(dur)
    n = mix.n
    tt = np.arange(n) / SR
    vo_bus = np.zeros(n)
    for k in keys:
        if k == "RADIO":
            continue
        x = vo[k][0]
        i = int(T[k] * SR)
        vo_bus[i:i + len(x)] += x[: n - i]
    vo_bus *= 0.9 / np.max(np.abs(vo_bus))
    venv = np.convolve(np.abs(vo_bus), np.ones(4800) / 4800, mode="same")
    duck = 1 - 0.55 * np.clip(venv * 12, 0, 1)
    dr = g.drone(n, 0)
    denv = np.interp(tt, [0, T["N3"], T["RADIO"], T["N5"], M["lights"], T["N8"], dur], [0.3, 0.4, 0.7, 0.75, 1.0, 0.8, 0.7])
    mix.dry += dr * denv * duck * 0.42
    se = sea(n)
    senv = np.interp(tt, [0, T["N3"] - .2, T["N3"], T["N6"] - .2, T["N6"], T["N8"], dur], [1, 1, .45, .45, 1.1, .7, .6])
    mix.add(se * senv * duck, 0, 0.3, -0.25)
    mix.add(se[::-1] * senv * duck, 0, 0.3, 0.25)
    mix.add(g.wind(n) * np.interp(tt, [0, T["N6"] - .2, T["N6"], dur], [.4, .3, .8, .6]) * duck, 0, 0.3, 0.0)
    for tb in booms:
        mix.add(v2.boom(), tb, 0.45, 0.0, wet=0.2)
    for s0, sid, _ in shots[1:]:
        if s0 not in booms:
            mix.add(v2.whoosh(), max(0, s0 - 0.25), 0.14, RNG.uniform(-0.4, 0.4), wet=0.3)
    mix.add(wave_hit(), M["wave"] - 0.2, 0.8, 0.0, wet=0.3)
    mix.add(crack(), M["crack"], 0.7, 0.1, wet=0.2)
    mix.add(gush(2.6), M["crack"] + 0.1, 0.35, 0.1, wet=0.2)
    rings = []
    t = T["N4"] + 0.2
    while t < T["N5"] - 0.2:
        mix.add(radar_ping(), t, 0.25, 0.0, wet=0.5)
        rings.append(round(t, 3))
        t += 1.6
    mix.add(ding(), M["msg"], 0.4, 0.0)
    mix.add(ding(), M["reply"], 0.45, 0.0)
    mix.add(groan(3.0), M["still"] - 0.5, 0.5, 0.0, wet=0.5)
    mix.add(groan(2.0), M["rope"], 0.35, -0.3, wet=0.5)
    mix.add(static(0.4), T["RADIO"] - 0.45, 0.25, 0.0)
    mix.add(static(0.3), T["RADIO"] + vd("RADIO") + 0.05, 0.25, 0.0)
    radio_bed = g.fft_filter(RNG.standard_normal(int((vd("RADIO") + 0.6) * SR)), lo=800, hi=5000)
    mix.add(radio_bed, T["RADIO"] - 0.3, 0.05, 0.0)
    mix.add(v2.riser(1.8), M["lights"] - 1.8, 0.18, 0.0)
    knocks = []
    t = T["N8"] + 0.2
    while t < dur - 0.4:
        mix.add(v2.heartbeat(), t, 0.5, 0.0)
        mix.add(v2.heartbeat(), t + 0.27, 0.32, 0.0)
        t += 0.92
    irL, irR = g.make_ir(2.4, 1.8, 5000, 1), g.make_ir(2.4, 1.8, 5000, 2)
    out = mix.dry.copy()
    out[0] += g.conv(mix.send[0], irL) * 0.5
    out[1] += g.conv(mix.send[1], irR) * 0.5
    rbuf = np.zeros(n)
    rx = radio_fx(vo["RADIO"][0])
    ir_ = int(T["RADIO"] * SR)
    rbuf[ir_:ir_ + len(rx)] = rx[: n - ir_]
    out[0] += (rbuf + g.conv(rbuf, irL) * 0.15) * 0.5
    out[1] += (rbuf + g.conv(rbuf, irR) * 0.15) * 0.5
    out += (vo_bus + g.conv(vo_bus, irL) * 0.05) * 0.95
    out = np.tanh(out * 1.3) / np.tanh(1.3)
    out *= 0.89 / np.max(np.abs(out))
    work = tempfile.mkdtemp(prefix="mayday_")
    wav_path = os.path.join(work, "a.wav")
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((out.T * 32767).astype(np.int16).tobytes())

    # ---- sottotitoli (la voce dietro la porta compare come testo, non come sottotitolo)
    caps = []
    for k in keys:
        if k in ("N9",):
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
                caps.append({"s": round(s, 3), "e": round(e, 3), "w": disp, "i": idx, "v": k == "RADIO"})

    tl = {"dur": dur, "fps": FPS, "T": {k: round(v, 3) for k, v in T.items()}, "M": {k: round(v, 3) for k, v in M.items()},
          "shots": [{"t": round(s, 3), "id": i, "clock": c} for s, i, c in shots], "booms": [round(b, 3) for b in booms],
          "pings": rings, "caps": caps, "scary": sorted(SCARY)}
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
