#!/usr/bin/env python3
"""Genera il Reel dell'Ep. 1 di VALSORDA (9:16, 1080x1920, 30 fps).

Tutto e' procedurale: immagini disegnate in numpy/PIL, sound design sintetizzato,
voce narrante con Piper TTS (voce italiana it_IT-paola-medium).

Uso:
    python3 genera_ep01.py --voce /percorso/it_IT-paola-medium.onnx --out ep-01.mp4 [--anteprima]
"""
import argparse
import math
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SR = 48000
W, H = 1080, 1920
FPS = 30
FONT_DIR = "/usr/share/fonts/opentype/inter"
RNG = np.random.default_rng(1976)


# ----------------------------------------------------------------------------- audio utils
def fft_filter(x, lo=None, hi=None, order=2):
    n = len(x)
    N = 1 << (n - 1).bit_length()
    X = np.fft.rfft(x, N)
    f = np.fft.rfftfreq(N, 1 / SR)
    m = np.ones_like(f)
    if hi:
        m /= np.sqrt(1 + (f / hi) ** (2 * order))
    if lo:
        m /= np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    return np.fft.irfft(X * m, N)[:n]


def conv(x, ir):
    n = len(x) + len(ir) - 1
    N = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[: len(x)]


def make_ir(dur, decay, hi, seed):
    r = np.random.default_rng(seed)
    t = np.arange(int(dur * SR)) / SR
    ir = r.standard_normal(len(t)) * np.exp(-t * 6.9 / decay)
    ir = fft_filter(ir, hi=hi)
    ir[: int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
    return ir / np.sqrt(np.sum(ir ** 2))


def read_wav(path):
    with wave.open(path) as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768
    if ch > 1:
        data = data.reshape(-1, ch).mean(1)
    if sr != SR:
        t_old = np.arange(len(data)) / sr
        t_new = np.arange(int(len(data) * SR / sr)) / SR
        data = np.interp(t_new, t_old, data)
    return data


def tts(model, text, length_scale=1.12):
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    subprocess.run(
        [sys.executable, "-m", "piper", "-m", model, "-f", path,
         "--length-scale", str(length_scale), "--sentence-silence", "0.35"],
        input=text.encode("utf-8"), check=True, capture_output=True)
    x = read_wav(path)
    os.remove(path)
    # rifila i silenzi iniziali/finali
    env = np.abs(x) > 0.01
    idx = np.where(env)[0]
    x = x[max(0, idx[0] - 800): idx[-1] + 2400]
    return x


class Mix:
    def __init__(self, dur):
        self.n = int(dur * SR)
        self.dry = np.zeros((2, self.n))
        self.send = np.zeros((2, self.n))

    def add(self, sig, t, gain=1.0, pan=0.0, wet=0.0):
        i = int(t * SR)
        if i >= self.n:
            return
        sig = sig[: self.n - i]
        a = (pan + 1) * math.pi / 4
        gl, gr = math.cos(a) * gain, math.sin(a) * gain
        self.dry[0, i:i + len(sig)] += sig * gl * (1 - wet * 0.5)
        self.dry[1, i:i + len(sig)] += sig * gr * (1 - wet * 0.5)
        if wet:
            self.send[0, i:i + len(sig)] += sig * gl * wet
            self.send[1, i:i + len(sig)] += sig * gr * wet


# ----------------------------------------------------------------------------- sound design
def bell(f0=174.0, dur=8.0, bright=1.0):
    t = np.arange(int(dur * SR)) / SR
    partials = [(0.5, 1.0, 7.5), (1.0, 0.75, 5.5), (1.19, 0.55, 4.2), (1.5, 0.35, 3.6),
                (2.0, 0.55, 3.0), (2.51, 0.22, 2.0), (2.66, 0.2, 1.8), (3.01, 0.18, 1.5),
                (4.07, 0.12 * bright, 1.0), (5.43, 0.06 * bright, 0.6), (6.8, 0.04 * bright, 0.4)]
    s = np.zeros_like(t)
    for r, a, d in partials:
        f = f0 * r
        s += a * (np.sin(2 * np.pi * f * t + RNG.random() * 6) +
                  0.6 * np.sin(2 * np.pi * f * 1.0023 * t + RNG.random() * 6)) * np.exp(-t / d)
    strike = fft_filter(RNG.standard_normal(len(t)), lo=1500) * np.exp(-t / 0.015) * 0.6 * bright
    s += strike
    s *= 1 - np.exp(-t / 0.002)
    return s / np.max(np.abs(s))


def step_mud(heavy=1.0):
    d = 0.45
    t = np.arange(int(d * SR)) / SR
    n1 = RNG.standard_normal(len(t))
    env1 = (1 - np.exp(-t / 0.006)) * np.exp(-t / 0.06)
    s = fft_filter(n1, lo=60, hi=700) * env1 * 2.5
    t2 = np.clip(t - 0.08 - RNG.random() * 0.05, 0, None)
    env2 = (t2 > 0) * (1 - np.exp(-t2 / 0.01)) * np.exp(-t2 / 0.07)
    suck = fft_filter(RNG.standard_normal(len(t)), lo=250, hi=1800) * env2
    s += suck * 0.9
    s += np.sin(2 * np.pi * (55 + 20 * RNG.random()) * t) * np.exp(-t / 0.035) * 0.8 * heavy
    return s / np.max(np.abs(s))


def drip():
    d = 0.12
    t = np.arange(int(d * SR)) / SR
    f = 900 + 900 * np.exp(-t / 0.01)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / 0.025) * (1 - np.exp(-t / 0.001))


def click():
    t = np.arange(int(0.03 * SR)) / SR
    return fft_filter(RNG.standard_normal(len(t)), lo=1200) * np.exp(-t / 0.003)


def crackle(dur):
    n = int(dur * SR)
    x = fft_filter(RNG.standard_normal(n), lo=900, hi=3500) * 1.5
    gate = np.repeat(RNG.random(n // 480 + 1) > 0.35, 480)[:n]
    tone = np.sin(2 * np.pi * 1200 * np.arange(n) / SR) * 0.15
    return (x * (0.4 + gate) + tone) * np.minimum(1, np.arange(n) / 400) * np.minimum(1, (n - np.arange(n)) / 400)


def whisperize(x):
    env = np.abs(x)
    k = int(0.012 * SR)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    noise = fft_filter(RNG.standard_normal(len(x)), lo=1400, hi=7000)
    hiss = noise * env * 6
    hiss /= np.max(np.abs(hiss))
    voiced = fft_filter(x, lo=500)
    voiced /= np.max(np.abs(voiced))
    voiced *= 0.75
    hiss *= 0.6
    y = hiss + voiced
    return y / np.max(np.abs(y))


def drone(n, t0):
    t = (np.arange(n) / SR) + t0
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t)
    s = (0.30 * np.sin(2 * np.pi * 41.2 * t) + 0.22 * np.sin(2 * np.pi * 41.55 * t) +
         0.12 * np.sin(2 * np.pi * 61.7 * t + 1) + 0.07 * np.sin(2 * np.pi * 82.4 * t) +
         0.03 * np.sin(2 * np.pi * 123.9 * t + 2)) * lfo
    s += fft_filter(RNG.standard_normal(n), hi=110) * 0.6
    return s


def wind(n):
    t = np.arange(n) / SR
    s = fft_filter(RNG.standard_normal(n), lo=80, hi=500) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.11 * t) *
                                                            np.sin(2 * np.pi * 0.043 * t + 1))
    s += fft_filter(RNG.standard_normal(n), lo=650, hi=900, order=4) * 0.25 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t))
    return s


def tape_stop(x, start, dur):
    """Rallenta il nastro fino a fermarlo a partire da 'start' secondi."""
    i0 = int(start * SR)
    n = int(dur * SR)
    out = x.copy()
    speed = np.linspace(1, 0, n) ** 1.6
    pos = i0 + np.cumsum(speed)
    for c in range(x.shape[0]):
        seg = np.interp(pos, np.arange(x.shape[1]), x[c])
        seg *= np.linspace(1, 0.0, n) ** 0.5
        out[c, i0:i0 + n] = seg[: max(0, min(n, x.shape[1] - i0))]
        out[c, i0 + n:] = 0
    return out


# ----------------------------------------------------------------------------- image utils
def fbm(w, h, octaves=5, base=3, seed=0, persistence=0.55):
    r = np.random.default_rng(seed)
    acc = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        gw = base * 2 ** o
        gh = max(2, int(gw * h / w) + 1)
        arr = (r.random((gh, gw)) * 255).astype(np.uint8)
        img = Image.fromarray(arr).resize((w, h), Image.BICUBIC)
        acc += amp * (np.asarray(img, np.float32) / 255)
        tot += amp
        amp *= persistence
    return acc / tot


def blur(arr, radius):
    out = np.empty_like(arr)
    for c in range(arr.shape[2]):
        im = Image.fromarray(np.clip(arr[..., c] * 255, 0, 255).astype(np.uint8))
        out[..., c] = np.asarray(im.filter(ImageFilter.GaussianBlur(radius)), np.float32) / 255
    return out


def to_arr(img):
    return np.asarray(img.convert("RGB"), np.float32) / 255


def voronoi_cracks(w, h, n_seeds, seed, crack_w=3.0):
    r = np.random.default_rng(seed)
    sw, sh = w // 2, h // 2
    pts = r.random((n_seeds, 2)) * [sw, sh]
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    d1 = np.full((sh, sw), 1e9, np.float32)
    d2 = np.full((sh, sw), 1e9, np.float32)
    for px, py in pts:
        d = np.sqrt((xx - px) ** 2 + (yy - py) ** 2)
        m = d < d1
        d2 = np.where(m, d1, np.minimum(d2, d))
        d1 = np.where(m, d, d1)
    edge = d2 - d1
    crack = np.clip(1 - edge / crack_w, 0, 1)
    curl = np.clip(d1 / 40, 0, 1)
    crack = np.asarray(Image.fromarray((crack * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR), np.float32) / 255
    curl = np.asarray(Image.fromarray((curl * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR), np.float32) / 255
    return crack, curl


def mud_texture(w, h, seed, n_seeds=160):
    crack, curl = voronoi_cracks(w, h, n_seeds, seed)
    n = fbm(w, h, 6, 4, seed + 1)
    fine = fbm(w, h, 3, 60, seed + 2)
    base = np.array([0.36, 0.31, 0.25], np.float32)
    shade = (0.55 + 0.45 * n) * (0.75 + 0.25 * fine) * (0.85 + 0.15 * (1 - curl))
    img = base * shade[..., None]
    img *= (1 - 0.92 * crack[..., None])
    # alghe secche: macchie verdastre
    alg = np.clip((fbm(w, h, 4, 6, seed + 3) - 0.58) * 6, 0, 1)
    img = img * (1 - alg[..., None] * 0.5) + alg[..., None] * np.array([0.16, 0.19, 0.12]) * 0.5
    return img


def radial_mask(w, h, cx, cy, rx, ry, power=2.0):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
    return np.exp(-d ** (power / 2))


def sky(w, h, seed, top=(0.02, 0.03, 0.05), bottom=(0.07, 0.09, 0.12)):
    g = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    s = np.array(top, np.float32) * (1 - g) + np.array(bottom, np.float32) * g
    s = np.broadcast_to(s, (h, w, 3)).copy()
    clouds = fbm(w, h, 5, 2, seed)
    s *= (0.7 + 0.6 * clouds[..., None])
    return s


# ----------------------------------------------------------------------------- scenes (static backgrounds)
MARGIN = 80  # margine per il movimento di camera a mano


def scene_mud():
    w, h = W + 2 * MARGIN, H + 2 * MARGIN
    img = mud_texture(w, h, 11)
    # impronte di stivale
    d = ImageDraw.Draw(im := Image.new("L", (w, h), 0))
    for i, (x, y) in enumerate([(470, 1750), (650, 1450), (460, 1150), (640, 860)]):
        d.ellipse([x - 55, y - 120, x + 55, y + 120], fill=120)
        d.ellipse([x - 45, y + 90, x + 45, y + 170], fill=90)
    fp = np.asarray(im.filter(ImageFilter.GaussianBlur(14)), np.float32)[..., None] / 255
    img *= 1 - fp * 0.55
    return img


def house(draw, x, y_base, w, h, roof=True, broken=False, col=10):
    draw.rectangle([x, y_base - h, x + w, y_base], fill=col)
    if roof and not broken:
        draw.polygon([(x - 12, y_base - h), (x + w / 2, y_base - h - w * 0.45), (x + w + 12, y_base - h)], fill=col)
    if broken:
        draw.polygon([(x, y_base - h), (x + w * 0.3, y_base - h - 40), (x + w * 0.55, y_base - h + 30),
                      (x + w * 0.8, y_base - h - 20), (x + w, y_base - h)], fill=col)


def scene_dam():
    w, h = W + 520, H + 2 * MARGIN
    img = sky(w, h, 21)
    yy = np.arange(h)[:, None]
    # diga: grande muro di cemento
    dam_top = 520 + 30 * np.sin(np.linspace(0, math.pi, w))[None, :]
    dam_bot = 1180
    concrete = 0.16 + 0.10 * fbm(w, h, 5, 6, 22)
    lines = (np.sin(yy / 9.0) > 0.96) * 0.03
    dam = ((yy > dam_top) & (yy < dam_bot)).astype(np.float32)
    dam_col = (concrete - lines)[..., None] * np.array([0.85, 0.92, 1.0])
    # luce lunare dall'alto sul muro
    dam_col *= (1.15 - 0.6 * ((yy - 520) / 700).clip(0, 1))[..., None]
    img = img * (1 - dam[..., None]) + dam_col * dam[..., None]
    # linea dell'acqua di 48 anni: segno scuro orizzontale
    stain = ((yy > 640) & (yy < 1180)).astype(np.float32) * 0.45
    img *= (1 - dam[..., None] * stain[..., None] * 0.35)
    # fondo lago fangoso
    mud = mud_texture(w, h, 23, 260) * 0.45
    ground = (yy > 1180).astype(np.float32)[..., None]
    persp = ((yy - 1180) / (h - 1180)).clip(0, 1)[..., None]
    img = img * (1 - ground) + mud * ground * (0.35 + 0.9 * persp)
    # case in rovina in silhouette
    sil = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(sil)
    xs = 30
    r = np.random.default_rng(24)
    while xs < w - 100:
        hw = int(r.integers(110, 220))
        hh = int(r.integers(150, 330))
        house(d, xs, 1330 + int(r.integers(-20, 30)), hw, hh, roof=r.random() > 0.3, broken=r.random() > 0.5, col=255)
        xs += hw + int(r.integers(10, 70))
    # campanile
    d.rectangle([w * 0.62, 820, w * 0.62 + 90, 1340], fill=255)
    d.polygon([(w * 0.62 - 6, 820), (w * 0.62 + 45, 740), (w * 0.62 + 96, 820)], fill=255)
    silm = np.asarray(sil, np.float32)[..., None] / 255
    win = Image.new("L", (w, h), 0)
    dw = ImageDraw.Draw(win)
    for _ in range(70):
        x, y = r.integers(30, w - 30), r.integers(1060, 1300)
        dw.rectangle([x, y, x + 18, y + 28], fill=255)
    winm = np.asarray(win, np.float32)[..., None] / 255 * silm
    house_col = np.array([0.035, 0.035, 0.04]) * (0.7 + 0.6 * fbm(w, h, 4, 8, 25)[..., None])
    img = img * (1 - silm) + house_col * silm
    img *= 1 - winm * 0.8
    # nebbia bassa
    fog = np.exp(-((yy - 1260) / 140.0) ** 2).astype(np.float32) * (0.5 + 0.5 * fbm(w, h, 4, 3, 26))
    img += fog[..., None] * np.array([0.10, 0.12, 0.14]) * 0.9
    return img


def scene_street():
    w, h = W + 2 * MARGIN, H + 2 * MARGIN
    img = sky(w, h, 31, (0.015, 0.02, 0.03), (0.05, 0.06, 0.08))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    vx, vy = w / 2, 930
    # strada fangosa in prospettiva
    road = (yy > vy).astype(np.float32)
    mud = mud_texture(w, h, 32, 220)
    persp = ((yy - vy) / (h - vy)).clip(0, 1)
    img = img * (1 - road[..., None]) + mud * (0.15 + 0.85 * persp[..., None]) * road[..., None] * 0.6
    # facciate laterali in prospettiva
    lay = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(lay)
    edge = Image.new("L", (w, h), 0)
    de = ImageDraw.Draw(edge)
    r = np.random.default_rng(33)
    for side in (-1, 1):
        x_near = vx + side * w * 0.62
        x_far = vx + side * 70
        d.polygon([(x_far, vy - 120), (x_near, -200), (x_near, h + 50), (x_far, vy + 25)], fill=255)
        # finestre e porte in prospettiva
        for k in range(9):
            f0 = k / 9
            f1 = f0 + 0.06
            def P(f, v):
                x = x_far + (x_near - x_far) * f ** 1.6
                top = (vy - 120) + (-200 - (vy - 120)) * f ** 1.6
                bot = (vy + 25) + (h + 50 - (vy + 25)) * f ** 1.6
                return (x, top + (bot - top) * v)
            for v0, v1 in ((0.25, 0.42), (0.55, 0.85) if k % 3 == 0 else (0.5, 0.65)):
                de.polygon([P(f0, v0), P(f1, v0), P(f1, v1), P(f0, v1)], fill=255)
    lm = np.asarray(lay, np.float32)[..., None] / 255
    em = np.asarray(edge.filter(ImageFilter.GaussianBlur(1)), np.float32)[..., None] / 255
    wall = np.array([0.065, 0.06, 0.055]) * (0.35 + 1.0 * fbm(w, h, 6, 5, 34)[..., None]) * (0.7 + 0.5 * fbm(w, h, 3, 40, 36)[..., None])
    stain = np.clip((yy - 700) / 900, 0, 1)[..., None]
    wall *= 1 - 0.5 * stain * fbm(w, h, 3, 20, 35)[..., None]
    img = img * (1 - lm) + wall * lm
    img *= 1 - em * lm * 0.85
    # nebbia in fondo alla strada
    fog = radial_mask(w, h, vx, vy, 520, 160).astype(np.float32)
    img += fog[..., None] * np.array([0.09, 0.10, 0.12])
    return img


def scene_tower():
    w, h = W + 2 * MARGIN, H + 600
    img = sky(w, h, 41, (0.03, 0.04, 0.07), (0.06, 0.07, 0.10))
    r = np.random.default_rng(42)
    for _ in range(140):  # stelle tra le nuvole
        x, y = r.integers(0, w), r.integers(0, int(h * 0.6))
        img[y, x] += 0.25 * r.random()
    moon = radial_mask(w, h, w * 0.5, 330, 420, 420).astype(np.float32)
    img += moon[..., None] * np.array([0.16, 0.19, 0.26])
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    cx = w / 2
    tw = 420
    top = 260
    d.rectangle([cx - tw / 2, top, cx + tw / 2, h], fill=255)
    d.polygon([(cx - tw / 2 - 20, top), (cx, top - 230), (cx + tw / 2 + 20, top)], fill=255)
    # archi della cella campanaria (vuoti)
    holes = Image.new("L", (w, h), 0)
    dh = ImageDraw.Draw(holes)
    for ax in (cx - 105, cx + 105):
        dh.rectangle([ax - 70, top + 170, ax + 70, top + 480], fill=255)
        dh.ellipse([ax - 70, top + 100, ax + 70, top + 240], fill=255)
    # finestrella e cornici
    dh.rectangle([cx - 25, top + 820, cx + 25, top + 930], fill=255)
    m = np.asarray(mask, np.float32)[..., None] / 255
    hm = np.asarray(holes, np.float32)[..., None] / 255
    yy = np.arange(h)[:, None, None]
    stone = np.array([0.20, 0.18, 0.16]) * (0.45 + 0.9 * fbm(w, h, 6, 6, 43)[..., None])
    bricks = ((np.sin(yy / 14.0) > 0.93) * 0.35)
    stone *= 1 - bricks
    # luce della frontale dal basso
    lightup = np.clip((yy - 300) / (h - 300), 0, 1) ** 2.2
    stone *= (0.30 + 1.5 * lightup)
    stone *= 1 - 0.5 * np.clip((yy - 1300) / 900, 0, 1) * fbm(w, h, 3, 10, 44)[..., None]  # alghe/umidita'
    tower = m * (1 - hm)
    img = img * (1 - tower) + stone * tower
    # interno degli archi leggermente piu' scuro del cielo (profondita')
    img *= 1 - hm * m * 0.25
    return img


def scene_door():
    w, h = W + 2 * MARGIN, H + 2 * MARGIN
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    wall = np.array([0.22, 0.20, 0.17]) * (0.5 + 0.8 * fbm(w, h, 6, 5, 51)[..., None])
    blocks = ((np.sin(yy / 22.0) > 0.95) | (np.sin(xx / 40.0 + (np.floor(yy / 44) % 2) * 1.6) > 0.985))
    wall *= 1 - blocks[..., None] * 0.4
    img = wall
    cx = w / 2
    x0, x1, y0, y1 = cx - 270, cx + 270, 560, 1560
    door = Image.new("L", (w, h), 0)
    dd = ImageDraw.Draw(door)
    dd.rectangle([x0, y0 + 270, x1, y1], fill=255)
    dd.ellipse([x0, y0, x1, y0 + 540], fill=255)
    dm = np.asarray(door, np.float32)[..., None] / 255
    wood = np.array([0.20, 0.12, 0.07]) * (0.5 + 0.7 * fbm(w, h, 5, 3, 52)[..., None])
    grain = 0.85 + 0.15 * np.sin(xx / 3.0 + 8 * fbm(w, h, 3, 4, 53))[..., None]
    wood *= grain
    planks = (np.abs(((xx - x0) % 90) - 0) < 4)[..., None]
    wood *= 1 - planks * 0.75
    # borchie
    st = Image.new("L", (w, h), 0)
    ds = ImageDraw.Draw(st)
    for yb in (900, 1200, 1450):
        ds.rectangle([x0 + 10, yb - 14, x1 - 10, yb + 14], fill=180)
        for xb in np.arange(x0 + 45, x1 - 20, 90):
            ds.ellipse([xb - 9, yb - 9, xb + 9, yb + 9], fill=255)
    ds.ellipse([x1 - 150, 1080, x1 - 70, 1160], outline=255, width=10)
    stm = np.asarray(st, np.float32)[..., None] / 255
    wood = wood * (1 - stm) + np.array([0.09, 0.08, 0.07]) * stm
    img = img * (1 - dm) + wood * dm
    # cornice di pietra
    fr = Image.new("L", (w, h), 0)
    df = ImageDraw.Draw(fr)
    df.arc([x0 - 40, y0 - 40, x1 + 40, y0 + 580], 180, 360, fill=255, width=40)
    df.rectangle([x0 - 40, y0 + 270, x0, y1], fill=255)
    df.rectangle([x1, y0 + 270, x1 + 40, y1], fill=255)
    frm = np.asarray(fr, np.float32)[..., None] / 255
    img = img * (1 - frm) + np.array([0.27, 0.25, 0.22]) * (0.6 + 0.6 * fbm(w, h, 4, 8, 54)[..., None]) * frm
    # gradini e fango
    steps = (yy > y1).astype(np.float32)[..., None]
    mud = mud_texture(w, h, 55, 200) * 0.8
    img = img * (1 - steps) + mud * steps
    img *= 1 - ((np.abs(yy - (y1 + 120)) < 4) | (np.abs(yy - (y1 + 260)) < 4))[..., None] * 0.6
    # umidita' alla base e linea dell'acqua
    img *= 1 - 0.35 * np.clip((yy - 600) / 900, 0, 1)[..., None] * fbm(w, h, 3, 12, 56)[..., None]
    # luce calda sotto la porta (layer separato, intensita' animata)
    glow = np.zeros((h, w, 3), np.float32)
    strip = ((yy > y1 - 14) & (yy < y1 + 2) & (xx > x0 + 6) & (xx < x1 - 6)).astype(np.float32)
    warm = np.array([1.0, 0.62, 0.25], np.float32)
    glow += strip[..., None] * warm * 1.6
    spill = radial_mask(w, h, cx, y1 + 30, 330, 120).astype(np.float32) * (yy > y1 - 4)
    glow += spill[..., None] * warm * 0.55
    glow = blur(glow, 6) + strip[..., None] * warm * 0.9
    return img, glow


# ----------------------------------------------------------------------------- text
_font_cache = {}


def font(name, size):
    k = (name, size)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    return _font_cache[k]


_text_cache = {}


def text_layer(lines, size=56, fname="Inter-SemiBold.otf", fill=(255, 255, 255), stroke=5,
               spacing=14, align="center", box=None, tracking=0):
    key = (tuple(lines), size, fname, fill, stroke, spacing, align, box, tracking)
    if key in _text_cache:
        return _text_cache[key]
    f = font(fname, size)
    pad = 30
    widths, heights = [], []
    for ln in lines:
        if tracking:
            wsum = sum(f.getlength(c) + tracking for c in ln) - tracking
        else:
            wsum = f.getlength(ln)
        widths.append(int(wsum))
        b = f.getbbox("Ag")
        heights.append(b[3] - b[1])
    tw = max(widths) + 2 * pad
    th = sum(heights) + spacing * (len(lines) - 1) + 2 * pad
    im = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if box:
        d.rounded_rectangle([0, 0, tw - 1, th - 1], radius=24, fill=box)
    y = pad
    for ln, lw, lh in zip(lines, widths, heights):
        x = (tw - lw) / 2 if align == "center" else pad
        if tracking:
            for c in ln:
                d.text((x, y - f.getbbox("Ag")[1]), c, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 230))
                x += f.getlength(c) + tracking
        else:
            d.text((x, y - f.getbbox("Ag")[1]), ln, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 230))
        y += lh + spacing
    arr = np.asarray(im, np.float32) / 255
    _text_cache[key] = arr
    return arr


def wrap(text, fname, size, max_w):
    f = font(fname, size)
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if f.getlength(t) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def blit(frame, layer, cx, cy, alpha=1.0):
    if alpha <= 0.01:
        return
    lh, lw = layer.shape[:2]
    x0, y0 = int(cx - lw / 2), int(cy - lh / 2)
    fx0, fy0 = max(0, x0), max(0, y0)
    fx1, fy1 = min(W, x0 + lw), min(H, y0 + lh)
    if fx1 <= fx0 or fy1 <= fy0:
        return
    sub = layer[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0]
    a = sub[..., 3:4] * alpha
    frame[fy0:fy1, fx0:fx1] = frame[fy0:fy1, fx0:fx1] * (1 - a) + sub[..., :3] * a


# ----------------------------------------------------------------------------- main
LINES = {
    "L1": "Mi chiamo Greta, registro suoni per i film. Stanotte sono a Valsorda: un paese che è stato sott'acqua per quarantotto anni.",
    "L2": "Hanno svuotato il lago per dei lavori. All'alba richiudono la diga. Mi pagano per registrare il silenzio di un paese morto.",
    "L3": "Il problema è che qui, il silenzio, il microfono non lo trova.",
    "L4": "Ho riascoltato gli ultimi due minuti.",
    "L5": "Il campanile è vuoto. La campana l'hanno portata via nel settantasei.",
    "L6": "E poi, nelle cuffie, qualcuno ha detto il mio nome.",
    "L7": "Cosa faccio? Ditemelo voi: scrivete uno, o due, nei commenti. Io faccio quello che sceglie la maggioranza.",
}
SUBS = {  # testo dei sottotitoli (con i numeri scritti in cifre)
    "L5": "Il campanile è vuoto. La campana l'hanno portata via nel '76.",
    "L7": "Cosa faccio? Ditemelo voi: scrivete 1 o 2 nei commenti. Io faccio quello che sceglie la maggioranza.",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voce", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--anteprima", action="store_true", help="render veloce a bassa qualita'")
    ap.add_argument("--frame", default=None, help="salva solo i fotogrammi a questi secondi, es. 1,5,12 (png)")
    a = ap.parse_args()

    print("Voce narrante…", flush=True)
    voice = {k: tts(a.voce, v) for k, v in LINES.items()}
    whisper_src = tts(a.voce, "Greta…", length_scale=1.7)
    whisper = whisperize(whisper_src)

    def vd(k):
        return len(voice[k]) / SR

    # ---- timeline
    T = {}
    T["bell1"] = 0.95
    T["S1"] = 2.3
    T["L1"] = T["S1"] + 0.35
    T["S2"] = T["L1"] + vd("L1") + 0.35
    T["L2"] = T["S2"] + 0.3
    T["S3"] = T["L2"] + vd("L2") + 0.4
    T["L3"] = T["S3"] + 0.3
    T["S4"] = T["L3"] + vd("L3") + 0.9
    T["L4"] = T["S4"] + 0.5
    T["play"] = T["L4"] + vd("L4") + 0.35
    T["steps_stop"] = T["play"] + 4.6
    T["S5"] = T["steps_stop"] + 1.0
    T["L5"] = T["S5"] + 0.4
    T["bell2"] = T["L5"] + vd("L5") + 0.45
    T["S6"] = T["bell2"] + 2.4
    T["L6"] = T["S6"] + 0.35
    T["crackle"] = T["L6"] + vd("L6") + 0.4
    T["whisper"] = T["crackle"] + 0.25
    T["S7"] = T["whisper"] + len(whisper) / SR + 1.1
    T["L7"] = T["S7"] + 0.3
    T["stop"] = T["L7"] + vd("L7") + 0.5
    T["end"] = T["stop"] + 1.6
    dur = T["end"]
    print(f"Durata: {dur:.1f} s", flush=True)
    print("  " + "  ".join(f"{k}={v:.1f}" for k, v in T.items()), flush=True)

    # ---- audio
    print("Sound design…", flush=True)
    mix = Mix(dur)
    n = mix.n
    # drone: sale lentamente, si interrompe di colpo al sussurro, torna piano sul CTA
    dr = drone(n, 0)
    tt = np.arange(n) / SR
    denv = np.interp(tt, [0, 2.3, T["S3"], T["play"], T["bell2"], T["whisper"] - 0.05, T["whisper"], T["S7"], T["S7"] + 1.5, dur],
                     [0, 0.25, 0.4, 0.55, 0.7, 0.85, 0, 0, 0.35, 0.35])
    mix.dry += dr * denv * 0.5
    wd = wind(n)
    wenv = np.interp(tt, [0, 2.3, 2.8, T["S4"], T["play"], T["steps_stop"], T["S6"], T["whisper"], T["S7"], dur],
                     [0, 0, 0.5, 0.5, 0.35, 0.0, 0.3, 0.0, 0.0, 0.2])
    mix.add(wd * wenv, 0, 0.5, -0.2)
    mix.add(wd[::-1] * wenv, 0, 0.5, 0.25)
    # campana 1 (lontana) e 2 (vicina)
    b1 = fft_filter(bell(174, 7, 0.6), hi=1400)
    mix.add(b1, T["bell1"], 0.35, 0.1, wet=1.0)
    b2 = bell(174, 9, 1.0)
    mix.add(b2, T["bell2"], 0.75, 0.0, wet=0.7)
    mix.add(fft_filter(b2, hi=200), T["bell2"], 0.6, 0.0)  # corpo grave
    # frontale che si accende
    mix.add(click(), T["S1"], 0.5, 0.2)
    # passi di Greta nel fango (dal vivo)
    t = T["S1"] + 0.6
    while t < T["S3"] - 0.3:
        mix.add(step_mud(), t, 0.22, RNG.uniform(-0.15, 0.15), wet=0.15)
        t += RNG.uniform(0.62, 0.75)
    # gocce
    for _ in range(26):
        tdrip = RNG.uniform(2.5, T["S6"])
        mix.add(drip(), tdrip, RNG.uniform(0.05, 0.12), RNG.uniform(-0.9, 0.9), wet=0.8)
    # click di play
    mix.add(click(), T["play"] - 0.1, 0.4, 0.1)
    # riascolto: passi tutt'intorno, sempre di piu', che si fermano di colpo
    walkers = [(-0.9, 0.0), (0.8, 0.4), (-0.4, 1.1), (0.55, 1.7), (-0.75, 2.3), (0.95, 2.6), (0.2, 3.0)]
    for pan, start in walkers:
        t = T["play"] + start
        per = RNG.uniform(0.55, 0.8)
        while t < T["steps_stop"] - 0.05:
            mix.add(step_mud(0.6), t, RNG.uniform(0.16, 0.3), pan + RNG.uniform(-0.05, 0.05), wet=0.35)
            t += per * RNG.uniform(0.95, 1.05)
    # ultimo passo, vicinissimo, che coincide con lo stop
    mix.add(step_mud(1.2), T["steps_stop"] - 0.3, 0.5, -0.1, wet=0.2)
    # walkie-talkie + sussurro nel canale destro
    mix.add(crackle(0.35), T["crackle"], 0.18, 0.6)
    # battito sordo sul CTA
    t = T["S7"] + 0.6
    while t < T["end"]:
        mix.add(fft_filter(step_mud(1.5), hi=150), t, 0.45, 0.0)
        mix.add(fft_filter(step_mud(1.5), hi=150), t + 0.28, 0.3, 0.0)
        t += 1.05
    # voce narrante (vicina al microfono, poco riverbero)
    for k in LINES:
        v = fft_filter(voice[k], lo=90, hi=7500)
        v = v / np.max(np.abs(v))
        mix.add(v, T[k], 0.62, -0.02, wet=0.12)
    # riverbero
    irL = make_ir(3.2, 2.8, 5000, 1)
    irR = make_ir(3.2, 2.8, 5000, 2)
    out = mix.dry.copy()
    out[0] += conv(mix.send[0], irL) * 0.55
    out[1] += conv(mix.send[1], irR) * 0.55
    # taglio netto di tutto al momento del sussurro ("la musica si interrompe di colpo")
    gcut = np.interp(tt, [T["whisper"] - 0.1, T["whisper"] - 0.03, T["S7"] - 0.2, T["S7"] + 0.1], [1, 0.04, 0.04, 1])
    out *= gcut
    # sussurro: quasi solo canale destro, vicinissimo, con un filo di riverbero
    wbuf = np.zeros(n)
    iw = int(T["whisper"] * SR)
    wbuf[iw:iw + len(whisper)] = whisper[: n - iw]
    wrev = conv(wbuf, irR) * 0.35
    out[1] += (wbuf + wrev) * 0.55
    out[0] += (wbuf * 0.06 + conv(wbuf, irL) * 0.12) * 0.55
    out = tape_stop(out, T["stop"], dur - T["stop"])
    out = np.tanh(out * 1.2) / np.tanh(1.2)
    out *= 0.89 / np.max(np.abs(out))
    tmpdir = tempfile.mkdtemp()
    wav_path = os.path.join(tmpdir, "audio.wav")
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes((out.T * 32767).astype(np.int16).tobytes())
    mono = out.mean(0)

    # ---- sottotitoli: spezzati in blocchi, tempi proporzionali ai caratteri
    subs = []
    for k in LINES:
        txt = SUBS.get(k, LINES[k])
        words = txt.split()
        chunks, cur = [], []
        for w_ in words:
            cur.append(w_)
            if len(" ".join(cur)) > 26 or w_.endswith((".", "?", ":")):
                chunks.append(" ".join(cur))
                cur = []
        if cur:
            chunks.append(" ".join(cur))
        total = sum(len(c) for c in chunks)
        t0, d0 = T[k], vd(k)
        for c in chunks:
            dd = d0 * len(c) / total
            subs.append((t0, t0 + dd, c))
            t0 += dd

    # ---- immagini
    print("Sfondi…", flush=True)
    bg_mud = scene_mud()
    bg_mud_blur = blur(bg_mud * 0.6, 10)
    bg_dam = scene_dam()
    bg_street = scene_street()
    bg_tower = scene_tower()
    bg_door, glow_door = scene_door()
    lamp = radial_mask(W * 2, H * 2, W, H, 520, 640, 2.2).astype(np.float32)[..., None]
    lamp_col = np.array([1.0, 0.96, 0.88], np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vign = np.clip(1 - 0.75 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2), 0, 1)[..., None] ** 1.3
    grains = [RNG.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(12)]
    grains = [np.asarray(Image.fromarray(((g * 40 + 128).clip(0, 255)).astype(np.uint8)).resize((W, H), Image.BILINEAR),
                         np.float32)[..., None] / 255 - 0.5 for g in grains]
    fur = Image.new("RGBA", (520, 300), (0, 0, 0, 0))
    dfur = ImageDraw.Draw(fur)
    for _ in range(5000):
        x, y = RNG.normal(260, 110), RNG.normal(160, 55)
        ang = RNG.uniform(0, 2 * math.pi)
        ln = RNG.uniform(8, 26)
        c = int(RNG.uniform(40, 110))
        dfur.line([x, y, x + math.cos(ang) * ln, y + math.sin(ang) * ln], fill=(c, c, c - 5, 255), width=2)
    fur = np.asarray(fur.filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255

    def shake(t, amt=1.0):
        return (amt * (28 * math.sin(t * 1.3) + 13 * math.sin(t * 3.7 + 1) + 5 * math.sin(t * 9.1)),
                amt * (22 * math.sin(t * 1.1 + 2) + 11 * math.sin(t * 4.3) + 4 * math.sin(t * 8.3 + 3)))

    def crop(bg, ox, oy):
        bh, bw = bg.shape[:2]
        x = int(np.clip((bw - W) / 2 + ox, 0, bw - W))
        y = int(np.clip((bh - H) / 2 + oy, 0, bh - H))
        return bg[y:y + H, x:x + W]

    def lamp_at(dx, dy):
        x = int(np.clip(W / 2 - dx, 0, W))
        y = int(np.clip(H / 2 - dy, 0, H))
        return lamp[y:y + H, x:x + W]

    def wave_strip(frame, t, x0, y0, wdt, hgt, color, span=2.5, playhead=False, gain=3.0):
        i1 = int(t * SR)
        i0 = max(0, i1 - int(span * SR))
        seg = mono[i0:i1]
        if len(seg) < 10:
            return
        bins = np.array_split(seg, 240)
        amps = np.array([np.max(np.abs(b)) if len(b) else 0 for b in bins])
        im = Image.new("RGBA", (wdt, hgt), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        bw = wdt / 240
        off = 240 - len(amps)
        for j, am in enumerate(amps):
            hh = max(1.5, min(1.0, am * gain) * hgt / 2)
            x = (j + off) * bw
            d.rectangle([x, hgt / 2 - hh, x + max(1.5, bw * 0.45), hgt / 2 + hh], fill=color)
        if playhead:
            d.rectangle([wdt - 4, 0, wdt, hgt], fill=(255, 60, 50, 255))
        arr = np.asarray(im, np.float32) / 255
        blit(frame, arr, x0 + wdt / 2, y0 + hgt / 2)

    def fade(t, a, b, fi=0.35, fo=0.35):
        if t < a or t > b:
            return 0.0
        return min(1.0, (t - a) / fi if fi else 1, (b - t) / fo if fo else 1)

    sub_layers = {}

    def draw_subs(frame, t):
        for s0, s1, txt in subs:
            if s0 <= t < s1 + 0.15:
                if txt not in sub_layers:
                    sub_layers[txt] = text_layer(wrap(txt, "Inter-SemiBold.otf", 60, 960), 60, stroke=6)
                blit(frame, sub_layers[txt], W / 2, 1330, 1.0)
                break

    total_frames = int(dur * FPS)
    frames = range(total_frames)
    if a.frame is not None:
        frames = [int(float(x) * FPS) for x in a.frame.split(",")]
    print(f"Render {len(frames)} fotogrammi…", flush=True)
    ff = None
    if a.frame is None:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", str(FPS), "-i", "-", "-i", wav_path, "-c:v", "libx264",
               "-preset", "veryfast" if a.anteprima else "slow", "-crf", "28" if a.anteprima else "19",
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", a.out]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    countdown = text_layer(["ALBA TRA 6h 10m"], 40, "Inter-Bold.otf", (255, 236, 200), 0, box=(10, 10, 12, 170), tracking=3)
    for fi in frames:
        t = fi / FPS
        rng_f = np.random.default_rng(fi)
        flick = 1 + 0.035 * rng_f.standard_normal()
        if t < T["S1"]:
            # ---------------- gancio: nero + forma d'onda
            frame = np.zeros((H, W, 3), np.float32) + 0.01
            k = max(0.0, 1 - abs(t - T["bell1"]) * 1.2) if t >= T["bell1"] - 0.05 else 0
            im = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            pts = []
            for x in range(0, W, 6):
                env = math.exp(-((x - W / 2) / 260) ** 2)
                y = 150 + (k * 120 * env * math.sin(x * 0.18 + t * 40) if k else 0) + rng_f.normal(0, 1.2)
                pts.append((x, y))
            d.line(pts, fill=(230, 60, 50, 255), width=4)
            blit(frame, np.asarray(im, np.float32) / 255, W / 2, 1060)
            blit(frame, text_layer(["METTI LE CUFFIE."], 92, "Inter-Black.otf", stroke=0, tracking=2), W / 2, 820,
                 fade(t, 0.15, T["S1"], 0.25, 0.2))
        elif t < T["S2"]:
            # ---------------- fango alla luce della frontale
            ts = t - T["S1"]
            dx, dy = shake(t, 1.0)
            base = crop(bg_mud, dx, dy - ts * 40)
            on = min(1.0, ts / 0.08)
            lm = lamp_at(dx * 0.6, dy * 0.6)
            frame = base * (0.05 + 1.35 * lm * lamp_col * on) * flick
            blit(frame, text_layer(["VALSORDA"], 128, "Inter-Black.otf", stroke=0, tracking=18), W / 2, 380,
                 fade(t, T["S1"] + 0.6, T["S2"] - 0.3, 0.6, 0.4))
            blit(frame, text_layer(["sommersa dal 1976"], 46, "Inter-Medium.otf", (220, 220, 220), 0, tracking=4), W / 2, 500,
                 fade(t, T["S1"] + 1.1, T["S2"] - 0.3, 0.6, 0.4))
        elif t < T["S3"]:
            # ---------------- diga e paese in rovina, panoramica
            ts = (t - T["S2"]) / (T["S3"] - T["S2"])
            dx, dy = shake(t, 0.5)
            base = crop(bg_dam, -250 + 500 * ts + dx, dy)
            lm = lamp_at(dx * 0.5, -500 + dy * 0.5)
            frame = base * (0.9 + 0.7 * lm * lamp_col) * flick
            blit(frame, countdown, W / 2, 190, fade(t, T["L2"] + 1.5, T["end"], 0.4, 0.01))
        elif t < T["S4"]:
            # ---------------- registratore in REC
            ts = t - T["S3"]
            dx, dy = shake(t, 0.35)
            base = crop(bg_mud_blur, dx, dy)
            frame = base * (0.25 + 0.8 * lamp_at(0, 200)) * flick
            ox, oy = dx * 0.5, dy * 0.5
            im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.rounded_rectangle([170 + ox, 560 + oy, 910 + ox, 1240 + oy], 70, fill=(22, 22, 24, 255), outline=(60, 60, 64, 255), width=4)
            d.rounded_rectangle([230 + ox, 640 + oy, 850 + ox, 1060 + oy], 18, fill=(18, 26, 20, 255), outline=(80, 90, 80, 255), width=3)
            for i_, (bx, by) in enumerate([(320, 1150), (540, 1150), (760, 1150)]):
                d.ellipse([bx - 55 + ox, by - 55 + oy, bx + 55 + ox, by + 55 + oy], fill=(38, 38, 42, 255), outline=(70, 70, 74, 255), width=3)
            d.ellipse([540 - 40 + ox, 1150 - 40 + oy, 540 + 40 + ox, 1150 + 40 + oy], fill=(170, 30, 30, 255))
            arr = np.asarray(im, np.float32) / 255
            blit(frame, arr, W / 2, H / 2)
            blit(frame, fur, W / 2 + ox, 470 + oy)
            lcd_on = (int(t * 2) % 2 == 0)
            rec = text_layer(["● REC"], 46, "Inter-Bold.otf", (255, 60, 50) if lcd_on else (90, 30, 30), 0)
            blit(frame, rec, 340 + ox, 700 + oy)
            secs = int(23 * 3600 + 37 * 60 + 2 + ts)
            tc = f"{secs // 3600:02d}:{secs // 60 % 60:02d}:{secs % 60:02d}"
            blit(frame, text_layer([tc], 46, "Inter-SemiBold.otf", (170, 230, 170), 0), 700 + ox, 700 + oy)
            blit(frame, text_layer(["48 kHz · 24 bit"], 28, "Inter-Medium.otf", (120, 170, 120), 0), 540 + ox, 1015 + oy)
            wave_strip(frame, t, int(260 + ox), int(760 + oy), 560, 220, (150, 230, 150, 255), span=3.0, gain=1.6)
            blit(frame, countdown, W / 2, 190)
        elif t < T["S5"]:
            # ---------------- strada vuota, inquadratura fissa + riascolto
            dx, dy = shake(t, 0.12)
            base = crop(bg_street, dx, dy)
            lm = lamp_at(dx, -120 + dy)
            frame = base * (0.35 + 0.9 * lm * lamp_col) * flick
            if t >= T["play"] - 0.1:
                blit(frame, text_layer(["▶  RIASCOLTO 23:38"], 44, "Inter-Bold.otf", (255, 255, 255), 0, box=(170, 25, 20, 210)), W / 2, 330)
                im_bg = np.zeros((260, 860, 4), np.float32)
                im_bg[..., 3] = 0.55
                blit(frame, im_bg, W / 2, 1600)
                wave_strip(frame, min(t, T["steps_stop"] + 0.6), 110, 1480, 860, 240, (255, 255, 255, 255), span=3.0,
                           playhead=True, gain=1.8)
            blit(frame, countdown, W / 2, 190)
        elif t < T["S6"]:
            # ---------------- campanile vuoto, tilt verso l'alto, rintocco
            ts = (t - T["S5"]) / (T["S6"] - T["S5"])
            hit = max(0.0, 1 - (t - T["bell2"]) * 2.5) if t >= T["bell2"] else 0
            dx, dy = shake(t, 0.6 + 2.0 * hit)
            base = crop(bg_tower, dx, 260 - 520 * min(1, ts * 1.4) + dy)
            frame = base * (1 + 0.15 * hit) * flick
            if 0 <= t - T["bell2"] < 0.1:
                frame = frame * 0.4 + 0.6
            blit(frame, countdown, W / 2, 190)
        elif t < T["S7"]:
            # ---------------- porta della chiesa con luce che respira
            ts = t - T["S6"]
            dx, dy = shake(t, 0.4)
            base = crop(bg_door, dx, dy + 60 - ts * 12)
            gl = crop(glow_door, dx, dy + 60 - ts * 12)
            breathe = 0.65 + 0.35 * math.sin(ts * 2.1) + 0.08 * rng_f.standard_normal()
            lm = lamp_at(dx * 0.4, 120 + dy * 0.4)
            frame = base * (0.08 + 0.9 * lm * lamp_col) * flick + gl * breathe
            if T["crackle"] <= t < T["whisper"] + 1.2:
                # disturbo radio: righe orizzontali
                for _ in range(6):
                    y = rng_f.integers(0, H - 20)
                    frame[y:y + rng_f.integers(2, 14)] += 0.25 * rng_f.random()
                blit(frame, text_layer(["CANALE 4 · OTTAVIO"], 34, "Inter-Bold.otf", (255, 220, 150), 0, box=(15, 15, 15, 200), tracking=2),
                     W / 2, 330, 1.0)
            blit(frame, countdown, W / 2, 190)
        else:
            # ---------------- CTA: fermo immagine + voto
            ts = t - T["S7"]
            base = crop(bg_door, 0, 60)
            gl = crop(glow_door, 0, 60)
            breathe = 0.6 + 0.4 * math.sin(ts * 1.4)
            frame = (base * (0.05 + 0.5 * lamp_at(0, 120) * lamp_col) + gl * breathe) * 0.55
            if t > T["stop"]:
                k = (t - T["stop"]) / (T["end"] - T["stop"])
                frame *= (1 - k) ** 1.5
                sh = int(40 * k * math.sin(t * 50))
                frame = np.roll(frame, sh, axis=1)
            al = fade(t, T["S7"] + 0.2, T["end"], 0.4, 0.5)
            blit(frame, text_layer(["COSA FACCIO?"], 96, "Inter-Black.otf", stroke=0, tracking=3), W / 2, 470, al)
            o1 = text_layer(["1  ·  ENTRO IN CHIESA"], 60, "Inter-Bold.otf", (255, 255, 255), 0, box=(150, 90, 30, 225))
            o2 = text_layer(["2  ·  TORNO ALL'AUTO"], 60, "Inter-Bold.otf", (255, 255, 255), 0, box=(30, 60, 110, 225))
            blit(frame, o1, W / 2, 660, fade(t, T["S7"] + 0.6, T["end"], 0.3, 0.5))
            blit(frame, o2, W / 2, 830, fade(t, T["S7"] + 0.9, T["end"], 0.3, 0.5))
            blit(frame, text_layer(["(ma i passi sono da quella parte)"], 38, "Inter-Medium.otf", (230, 210, 200), 0), W / 2, 930,
                 fade(t, T["S7"] + 1.3, T["end"], 0.3, 0.5))
            blit(frame, text_layer(["SCRIVILO NEI COMMENTI  ↓"], 46, "Inter-Bold.otf", (255, 236, 200), 0, tracking=2), W / 2, 1090,
                 fade(t, T["S7"] + 1.8, T["end"], 0.3, 0.5) * (0.75 + 0.25 * math.sin(t * 5)))
            blit(frame, countdown, W / 2, 190, al)
        draw_subs(frame, t)
        # post: grana, vignetta, toni freddi
        frame = frame * vign + grains[fi % len(grains)] * 0.12
        frame = frame * np.array([0.94, 1.0, 1.06], np.float32)
        out8 = (np.clip(frame, 0, 1) ** (1 / 1.08) * 255).astype(np.uint8)
        if ff:
            ff.stdin.write(out8.tobytes())
        else:
            Image.fromarray(out8).save(a.out.replace(".png", f"_{t:05.1f}.png"))
        if fi % 150 == 0:
            print(f"  {fi}/{total_frames}", flush=True)
    if ff:
        ff.stdin.close()
        ff.wait()
    print("Fatto:", a.out, flush=True)


if __name__ == "__main__":
    main()
