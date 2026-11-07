#!/usr/bin/env python3
"""VALSORDA Ep. 1 – versione "stile Reel virale".

Immagini cinematografiche AI (Ken Burns + tagli rapidi), narratore ElevenLabs (Adam),
sottotitoli grandi parola-per-parola con evidenziazione, colpi di basso sui tagli,
etichetta PARTE 1, schermata finale divisa con le due scelte.

Uso:
    python3 genera_ep01_v2.py --img CARTELLA_IMMAGINI --vo CARTELLA_VOCE --out ep-01.mp4
La cartella voce contiene N1.mp3/N1.json ... (audio + allineamento caratteri di ElevenLabs).
"""
import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import genera_ep01 as g  # noqa: E402  (riuso sound design e utility testo)

SR, W, H, FPS = g.SR, g.W, g.H, g.FPS
RNG = np.random.default_rng(48)
TEMPO = 1.06  # narrazione leggermente piu' veloce, ritmo da Reel
YELLOW = (255, 212, 0)
DISPLAY = {"millenovecentosettantasei.": "1976.", "quarantotto": "48", "Uno:": "1:", "Due:": "2:"}


# ----------------------------------------------------------------------------- input
def load_vo(vo_dir, key):
    d = json.load(open(os.path.join(vo_dir, key + ".json"), encoding="utf-8"))
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", os.path.join(vo_dir, key + ".mp3"),
                          "-af", f"atempo={TEMPO}", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, np.int16).astype(np.float64) / 32768
    al = d["alignment"]
    chars, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    words, cur, cs = [], "", None
    for c, s, e in zip(chars, st, en):
        if c.isspace():
            if cur:
                words.append([cur, cs / TEMPO, pe / TEMPO])
            cur, cs = "", None
        else:
            if cs is None:
                cs = s
            cur += c
            pe = e
    if cur:
        words.append([cur, cs / TEMPO, pe / TEMPO])
    return audio, words


def load_img(path):
    im = Image.open(path).convert("RGB")
    im = im.resize((int(W * 1.25), int(H * 1.25)), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    return im


# ----------------------------------------------------------------------------- sfx
def boom(dur=1.6):
    t = np.arange(int(dur * SR)) / SR
    f = 30 + 45 * np.exp(-t / 0.12)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t / 0.55) * (1 - np.exp(-t / 0.004))
    s += g.fft_filter(RNG.standard_normal(len(t)), hi=400) * np.exp(-t / 0.05) * 0.8
    return s / np.max(np.abs(s))


def whoosh(dur=0.45):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = RNG.standard_normal(n)
    out = np.zeros(n)
    k = 8
    for i in range(k):  # sweep a bande
        a, b = i * n // k, (i + 1) * n // k
        fc = 300 * (12 ** (i / (k - 1)))
        out[a:b] = g.fft_filter(x, lo=fc * 0.6, hi=fc * 1.6)[a:b]
    env = np.sin(np.pi * t / dur) ** 2
    return out * env / np.max(np.abs(out * env))


def riser(dur=2.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = g.fft_filter(RNG.standard_normal(n), lo=800, hi=6000)
    f = 120 * 2 ** (t / dur * 3)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3
    env = (t / dur) ** 2.5
    s = (noise * 0.7 + tone) * env
    return s / np.max(np.abs(s))


def heartbeat():
    s = g.fft_filter(g.step_mud(1.5), hi=140)
    return s / np.max(np.abs(s))


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--img", required=True)
    ap.add_argument("--vo", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--frame", default=None)
    a = ap.parse_args()

    keys = ["N1", "N2", "N3", "N4", "N5a", "N5b", "N6", "W", "N7", "N8"]
    vo = {k: load_vo(a.vo, k) for k in keys}

    def vd(k):
        return len(vo[k][0]) / SR

    # ---- timeline voce
    gaps = {"N1": 0.15, "N2": 0.35, "N3": 0.3, "N4": 0.55, "N5a": 0.5, "N5b": 1.9, "N6": 0.45, "W": 0.35, "N7": 1.0, "N8": 0.3}
    T, t = {}, 0.0
    for k in keys:
        t += gaps[k]
        T[k] = t
        t += vd(k)
    T["bell"] = T["N5a"] + vd("N5a") + 0.12
    T["end"] = t + 1.6
    dur = T["end"]

    def wt(k, word, nth=0):
        """istante (s) in cui inizia la parola 'word' nella battuta k"""
        hits = [w for w in vo[k][1] if w[0].lower().strip(".,:?!…").startswith(word.lower())]
        return T[k] + hits[nth][1]

    print(f"Durata: {dur:.1f} s", flush=True)

    # ---- piano delle inquadrature: (inizio, immagine, effetto)
    shots = [
        (0.0, "01_paese", "in"),
        (wt("N1", "Stanotte"), "02_campanile_lago", "in"),
        (T["N2"] - 0.1, "03_greta_spalle", "drift"),
        (wt("N2", "registrare"), "06_strada", "in"),
        (T["N3"] - 0.1, "04_registratore", "in"),
        (T["N4"] - 0.15, "07_greta_volto", "in"),
        (wt("N4", "passi"), "05_impronte", "fast"),
        (wt("N4", "Intorno"), "03_greta_spalle", "fast"),
        (wt("N4", "esattamente"), "07_greta_volto", "fast"),
        (T["N5a"] - 0.1, "08_campanile_vuoto", "tilt"),
        (wt("N5b", "portata"), "01_paese", "in"),
        (T["N6"] - 0.1, "09_porta", "in"),
        (wt("N6", "cuffie"), "10_cuffie", "in"),
        (T["N7"] - 0.25, "07_greta_volto", "in"),
        (wt("N7", "Uno"), "09_porta", "fast"),
        (wt("N7", "Due"), "11_auto", "fast"),
        (wt("N7", "passi"), "05_impronte", "fast"),
        (T["N8"] - 0.1, "SPLIT", "split"),
    ]
    booms = [wt("N1", "Stanotte"), T["N3"] - 0.1, wt("N4", "passi"), T["N6"] - 0.1, wt("N7", "Uno"), wt("N7", "Due"), T["N8"] - 0.1]
    whooshes = [s[0] - 0.3 for s in shots[1:] if s[0] not in booms]

    # ---- audio
    print("Audio…", flush=True)
    mix = g.Mix(dur)
    n = mix.n
    tt = np.arange(n) / SR
    # voce
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
    # ambiente
    dr = g.drone(n, 0)
    denv = np.interp(tt, [0, 3, T["N4"], T["bell"], T["W"] - 0.05, T["W"], T["N7"] - 0.3, T["N7"], dur], [0.5, 0.6, 0.75, 0.9, 1.0, 0.0, 0.0, 0.6, 0.6])
    mix.dry += dr * denv * duck * 0.42
    wd = g.wind(n)
    mix.add(wd * duck * np.interp(tt, [0, T["W"] - 0.05, T["W"], T["N7"], dur], [0.6, 0.5, 0, 0.3, 0.3]), 0, 0.4, -0.3)
    mix.add(wd[::-1] * duck * np.interp(tt, [0, T["W"] - 0.05, T["W"], T["N7"], dur], [0.6, 0.5, 0, 0.3, 0.3]), 0, 0.4, 0.3)
    for tb in booms:
        mix.add(boom(), tb, 0.55, 0.0, wet=0.2)
    for tw in whooshes:
        mix.add(whoosh(), max(0, tw), 0.16, RNG.uniform(-0.4, 0.4), wet=0.3)
    # passi tutt'intorno dopo "Ci sono dei passi"
    t0 = wt("N4", "passi") + 0.35
    stop = wt("N4", "esattamente") + 0.35
    for pan, st in [(-0.9, 0.0), (0.85, 0.3), (-0.5, 0.8), (0.6, 1.2), (-0.8, 1.6), (0.95, 1.9)]:
        t = t0 + st
        per = RNG.uniform(0.5, 0.7)
        while t < stop:
            mix.add(g.step_mud(0.7), t, RNG.uniform(0.14, 0.24), pan, wet=0.35)
            t += per
    mix.add(g.step_mud(1.3), stop - 0.15, 0.4, -0.1, wet=0.2)
    # riser + campana
    r = riser(2.0)
    mix.add(r, T["bell"] - 2.0, 0.22, 0.0)
    b = g.bell(174, 9, 1.0)
    mix.add(b, T["bell"], 0.8, 0.0, wet=0.75)
    mix.add(g.fft_filter(b, hi=200), T["bell"], 0.6, 0.0)
    mix.add(boom(2.5), T["bell"], 0.6, 0.0)
    # gocce
    for _ in range(18):
        mix.add(g.drip(), RNG.uniform(1, T["W"]), RNG.uniform(0.04, 0.09), RNG.uniform(-0.9, 0.9), wet=0.8)
    # walkie + battito sul finale
    mix.add(g.crackle(0.3), T["W"] - 0.3, 0.15, 0.6)
    t = T["N7"] + 0.2
    while t < dur - 0.4:
        mix.add(heartbeat(), t, 0.55, 0.0)
        mix.add(heartbeat(), t + 0.27, 0.35, 0.0)
        t += 0.95
    irL, irR = g.make_ir(3.0, 2.6, 5000, 1), g.make_ir(3.0, 2.6, 5000, 2)
    out = mix.dry.copy()
    out[0] += g.conv(mix.send[0], irL) * 0.55
    out[1] += g.conv(mix.send[1], irR) * 0.55
    # taglio netto per il sussurro, poi sussurro (Lily) nel canale destro
    gcut = np.interp(tt, [T["W"] - 0.08, T["W"] - 0.02, T["N7"] - 0.4, T["N7"]], [1, 0.03, 0.03, 1])
    out *= gcut
    wbuf = np.zeros(n)
    wx = g.fft_filter(vo["W"][0], lo=250)
    wx /= np.max(np.abs(wx))
    iw = int(T["W"] * SR)
    wbuf[iw:iw + len(wx)] = wx[: n - iw]
    out[1] += (wbuf + g.conv(wbuf, irR) * 0.45) * 0.55
    out[0] += (wbuf * 0.05 + g.conv(wbuf, irL) * 0.12) * 0.55
    # voce narrante al centro, con un filo di stanza
    vrev = g.conv(vo_bus, irL) * 0.06
    out += (vo_bus + vrev) * 0.95
    out = np.tanh(out * 1.3) / np.tanh(1.3)
    out *= 0.89 / np.max(np.abs(out))
    tmp = tempfile.mkdtemp()
    wav_path = os.path.join(tmp, "a.wav")
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((out.T * 32767).astype(np.int16).tobytes())

    # ---- sottotitoli: gruppi di max 3 parole, parola corrente in giallo
    groups = []
    for k in keys:
        if k in ("W", "N8"):
            continue
        ws = vo[k][1]
        cur = []
        for w in ws:
            cur.append(w)
            if len(cur) == 3 or w[0][-1] in ".,?!…" or len(" ".join(x[0] for x in cur)) > 16:
                groups.append((k, cur))
                cur = []
        if cur:
            groups.append((k, cur))
    cap_items = []  # (t_start, t_end, words(display), idx)
    for k, ws in groups:
        disp = [DISPLAY.get(w[0], w[0]).upper() for w in ws]
        for i, w in enumerate(ws):
            s = T[k] + w[1]
            e = T[k] + (ws[i + 1][1] if i + 1 < len(ws) else w[2] + 0.25)
            cap_items.append((s, e, tuple(disp), i))
    cap_cache = {}

    def caption_layer(words, idx):
        key = (words, idx)
        if key in cap_cache:
            return cap_cache[key]
        f = g.font("Inter-Black.otf", 86)
        space = f.getlength(" ")
        widths = [f.getlength(w) for w in words]
        lines, cur, cw = [], [], 0
        for i, wdt in enumerate(widths):
            if cur and cw + space + wdt > 950:
                lines.append(cur)
                cur, cw = [], 0
            cur.append(i)
            cw += (space if cw else 0) + wdt
        lines.append(cur)
        lh = 104
        im = Image.new("RGBA", (1040, lh * len(lines) + 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for li, line in enumerate(lines):
            tw = sum(widths[i] for i in line) + space * (len(line) - 1)
            x = (1040 - tw) / 2
            for i in line:
                col = YELLOW if i == idx else (255, 255, 255)
                d.text((x, 20 + li * lh), words[i], font=f, fill=col, stroke_width=9, stroke_fill=(0, 0, 0))
                x += widths[i] + space
        arr = np.asarray(im, np.float32) / 255
        cap_cache[key] = arr
        return arr

    # ---- immagini
    names = sorted({s[1] for s in shots if s[1] != "SPLIT"} | {"09_porta", "11_auto"})
    imgs = {nm: load_img(os.path.join(a.img, nm + ".jpg")) for nm in names}
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vign = (np.clip(1 - 0.6 * (((xx - W / 2) / (W * 0.8)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2), 0, 1) ** 1.2)[..., None]
    grains = [np.asarray(Image.fromarray((RNG.normal(128, 30, (H // 2, W // 2))).clip(0, 255).astype(np.uint8)).resize((W, H)),
                         np.float32)[..., None] / 255 - 0.5 for _ in range(10)]
    # luce calda sotto la porta (posizione relativa all'immagine 09)
    door_glow = g.radial_mask(W, H, W * 0.5, H * 0.78, 260, 70).astype(np.float32)[..., None] * np.array([1.0, 0.6, 0.25], np.float32)

    def render_img(nm, p, effect, tshot, local_t):
        im = imgs[nm]
        iw_, ih_ = im.size
        if effect == "fast":
            z = 1.12 + 0.18 * p
        elif effect == "tilt":
            z = 1.2
        elif effect == "drift":
            z = 1.14 + 0.04 * p
        else:
            z = 1.12 + 0.10 * p
        cw, ch = iw_ / 1.25 / z * 1.25, ih_ / 1.25 / z * 1.25
        cx, cy = iw_ / 2, ih_ / 2
        if effect == "drift":
            cx += (p - 0.5) * (iw_ - cw) * 0.6
        if effect == "tilt":
            cy = ih_ / 2 + (0.5 - p) * (ih_ - ch) * 0.4
        box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
        return np.asarray(im.resize((W, H), Image.BILINEAR, box=box), np.float32) / 255

    def shot_at(t):
        idx = 0
        for i, s in enumerate(shots):
            if t >= s[0]:
                idx = i
        s0 = shots[idx][0]
        s1 = shots[idx + 1][0] if idx + 1 < len(shots) else dur
        return idx, s0, s1

    part_pill = g.text_layer(["VALSORDA · PARTE 1"], 34, "Inter-Bold.otf", (255, 255, 255), 0, box=(0, 0, 0, 150), tracking=3)
    hook_box = g.text_layer(["IL PAESE RIEMERSO", "DOPO 48 ANNI"], 62, "Inter-Black.otf", (10, 10, 10), 0, box=(255, 255, 255, 245), spacing=6)
    opt1 = g.text_layer(["1 · ENTRA IN CHIESA"], 62, "Inter-Black.otf", (255, 255, 255), 0, box=(160, 95, 25, 235))
    opt2 = g.text_layer(["2 · TORNA ALLA MACCHINA"], 62, "Inter-Black.otf", (255, 255, 255), 0, box=(25, 70, 140, 235))
    ask = g.text_layer(["COSA DEVE FARE GRETA?"], 70, "Inter-Black.otf", (255, 255, 255), 8)
    comm = g.text_layer(["COMMENTA  1  O  2  ↓"], 64, "Inter-Black.otf", YELLOW, 8)
    rec = g.text_layer(["● REC"], 44, "Inter-Bold.otf", (255, 50, 40), 6)

    frames = range(int(dur * FPS))
    ff = None
    if a.frame:
        frames = [int(float(x) * FPS) for x in a.frame.split(",")]
    else:
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                               "-r", str(FPS), "-i", "-", "-i", wav_path, "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                               "-maxrate", "8M", "-bufsize", "16M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                               "-shortest", "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
    print(f"Render {len(frames)} fotogrammi…", flush=True)
    for fi in frames:
        t = fi / FPS
        idx, s0, s1 = shot_at(t)
        nm, eff = shots[idx][1], shots[idx][2]
        p = (t - s0) / max(0.01, s1 - s0)
        if nm == "SPLIT":
            top = render_img("09_porta", 0.3 + 0.2 * p, "in", s0, t - s0)
            bot = render_img("11_auto", 0.3 + 0.2 * p, "in", s0, t - s0)
            frame = np.concatenate([top[H // 4: H // 4 + H // 2], bot[H // 4: H // 4 + H // 2]], axis=0) * 0.8
            frame[H // 2 - 3:H // 2 + 3] = 0
        else:
            frame = render_img(nm, p, eff, s0, t - s0)
            if nm == "09_porta":
                frame = frame + door_glow * (0.55 + 0.3 * math.sin(t * 3.1) + 0.1 * RNG.standard_normal())
        # scossa sulla campana e sul sussurro
        hit = max(0.0, 1 - (t - T["bell"]) * 1.6) if t >= T["bell"] else 0
        if hit > 0:
            sx, sy = int(30 * hit * math.sin(t * 61)), int(24 * hit * math.cos(t * 47))
            frame = np.roll(np.roll(frame, sx, 1), sy, 0)
            if t - T["bell"] < 0.08:
                frame = frame * 0.3 + 0.7
        if T["W"] <= t < T["N7"] - 0.4:
            frame = frame * np.array([1.15, 0.75, 0.75], np.float32) * (0.7 + 0.3 * math.sin(t * 9))
        # flash sui colpi di basso
        for tb in booms:
            if 0 <= t - tb < 0.07:
                frame = frame * 0.4 + 0.6 * (t - tb < 0.035)
        frame = frame * vign + grains[fi % 10] * 0.09
        # testi
        if nm != "SPLIT":
            g.blit(frame, part_pill, W / 2, 200, 1.0)
        if t < T["N2"] - 0.1:
            g.blit(frame, hook_box, W / 2, 420, min(1, (T["N2"] - 0.1 - t) / 0.2))
        if nm == "04_registratore":
            g.blit(frame, rec, 200, 330, 1.0 if int(t * 2) % 2 == 0 else 0.25)
        if wt("N7", "Uno") <= t < wt("N7", "Due"):
            g.blit(frame, opt1, W / 2, 420, 1.0)
        if wt("N7", "Due") <= t < wt("N7", "passi"):
            g.blit(frame, opt2, W / 2, 420, 1.0)
        if nm == "SPLIT":
            g.blit(frame, ask, W / 2, 170, 1.0)
            g.blit(frame, opt1, W / 2, H // 2 - 110, 1.0)
            g.blit(frame, opt2, W / 2, H // 2 + 110, 1.0)
            g.blit(frame, comm, W / 2, 1420 + 14 * math.sin(t * 6), 1.0)
        else:
            for cs, ce, words, wi in cap_items:
                if cs <= t < ce:
                    pop = 1.0 + 0.06 * max(0, 1 - (t - cs) * 8)
                    layer = caption_layer(words, wi)
                    if pop > 1.001:
                        hh, ww = layer.shape[:2]
                        layer = np.asarray(Image.fromarray((layer * 255).astype(np.uint8), "RGBA").resize(
                            (int(ww * pop), int(hh * pop)), Image.BILINEAR), np.float32) / 255
                    g.blit(frame, layer, W / 2, 1200, 1.0)
                    break
        out8 = (np.clip(frame, 0, 1) * 255).astype(np.uint8)
        if ff:
            ff.stdin.write(out8.tobytes())
        else:
            Image.fromarray(out8).save(a.out.replace(".png", f"_{t:05.1f}.png"))
        if fi % 300 == 0:
            print(f"  {fi}", flush=True)
    if ff:
        ff.stdin.close()
        ff.wait()
    print("Fatto", a.out, flush=True)


if __name__ == "__main__":
    main()
