"""Original score + sound design, synthesised from scratch, laid on the narration timeline.

  python3 -m vox.sound ar        -> build/ar/audio/mix.wav (narration + music ducked + SFX, before loudness pass)

Music follows the chapter moods in script/master.json (chapters[].music), SFX follow scenes[].sfx.
Everything is numpy synthesis, so there are no licensing questions; maqam Kurd on D (D Eb F G A Bb C).
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

SR = 48000
PROJ = Path(__file__).resolve().parents[2]
rng = np.random.default_rng(11)

KURD = {"C,": -2, "D": 0, "Eb": 1, "F": 3, "G": 5, "A": 7, "Bb": 8, "C": 10, "D'": 12, "Eb'": 13, "F'": 15,
        "G'": 17, "A'": 19, "F#": 4, "E": 2, "B": 9, "C#": 11, "A,": -5, "Bb,": -4, "G,": -7}
D4 = 293.66


def f(note, octave=0):
    return D4 * 2 ** ((KURD[note] + 12 * octave) / 12)


# ------------------------------------------------------------------ dsp helpers
def lp(x, cut, order=2):
    return sosfilt(butter(order, min(cut, SR / 2 - 100), "low", fs=SR, output="sos"), x)


def hp(x, cut, order=2):
    return sosfilt(butter(order, cut, "high", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, min(hi, SR / 2 - 100)], "band", fs=SR, output="sos"), x)


def noise(sec):
    return rng.standard_normal(int(sec * SR))


def tt(sec):
    return np.arange(int(sec * SR)) / SR


def env(n, a, d, s, r):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    e = np.full(n, s, dtype=np.float64)
    a = min(a, n)
    if a:
        e[:a] = np.linspace(0, 1, a, endpoint=False)
    if a + d < n and d:
        e[a:a + d] = np.linspace(1, s, d, endpoint=False)
    if 0 < r < n:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def expd(sec, rate):
    return np.exp(-tt(sec) * rate)


def norm(x, peak=1.0):
    m = np.max(np.abs(x)) or 1.0
    return x / m * peak


def reverb_ir(seconds, bright=6000, seed=1):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    d = np.exp(-t * 6.9 / seconds)
    ir = np.stack([lp(r.standard_normal(n) * d, bright), lp(r.standard_normal(n) * d, bright)])
    return ir / np.sqrt((ir ** 2).sum(1, keepdims=True))


IR_HALL = reverb_ir(2.8, 5000, 1)
IR_ROOM = reverb_ir(0.9, 7000, 2)


def verb(st, ir, mix):
    """st: (2, n) -> wet/dry mix (output length n + len(ir))."""
    n = st.shape[1] + ir.shape[1]
    out = np.zeros((2, n))
    out[:, :st.shape[1]] = st * (1 - mix)
    for c in range(2):
        w = fftconvolve(st[c], ir[c])
        out[c, :len(w)] += w * mix * 1.6
    return out


def pan(x, p):
    return np.stack([x * np.sqrt(0.5 * (1 - p)), x * np.sqrt(0.5 * (1 + p))])


class Bus:
    def __init__(self, seconds):
        self.n = int(seconds * SR) + SR * 8
        self.x = np.zeros((2, self.n), np.float32)

    def put(self, sig, t0, gain=1.0, p=0.0):
        st = sig if sig.ndim == 2 else pan(sig, p)
        i = int(round(t0 * SR))
        if i < 0:
            st = st[:, -i:]
            i = 0
        j = min(self.n, i + st.shape[1])
        if j > i:
            self.x[:, i:j] += (st[:, : j - i] * gain).astype(np.float32)


# ------------------------------------------------------------------ instruments
def ney(freq, dur, vib=0.006, breath=0.18):
    n = int(dur * SR)
    t = np.arange(n) / SR
    v = vib * np.clip(t / 0.6, 0, 1)
    ph = 2 * np.pi * np.cumsum(freq * (1 + v * np.sin(2 * np.pi * 5.0 * t))) / SR
    tone = np.sin(ph) + 0.2 * np.sin(2 * ph) + 0.07 * np.sin(3 * ph)
    br = bp(rng.standard_normal(n), freq * 0.8, freq * 4) * breath
    e = env(n, 0.2, 0.2, 0.85, min(0.45, dur * 0.4))
    return (tone + br) * e


def pluck(freq, dur, bright=0.5, decay=0.996):
    n = int(dur * SR)
    period = max(2, int(SR / freq))
    buf = lp(rng.uniform(-1, 1, period), 1800 + bright * 4000)
    blocks = []
    for _ in range(n // period + 1):
        blocks.append(buf)
        buf = decay * 0.5 * (buf + np.roll(buf, -1))
    return lp(np.concatenate(blocks)[:n], 4200) * env(n, 0.002, 0.05, 1.0, 0.1)


def pad(freqs, dur, cut=1100, detune=0.004, trem=0.03):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for fr in freqs:
        for k, dt in enumerate((-detune, 0, detune)):
            ph = (fr * (1 + dt) * t + rng.random()) % 1.0
            out += (2 * ph - 1) * (0.7 if k == 1 else 0.5)
    out = lp(out / max(1, len(freqs) * 1.7), cut, 4)
    return out * (1 + trem * np.sin(2 * np.pi * 4.3 * t + rng.random() * 6))


def choir(freqs, dur):
    """Wordless 'aah' pad: saw stack through two vowel formants."""
    raw = pad(freqs, dur, cut=3500, detune=0.006, trem=0.02)
    return 0.6 * bp(raw, 650, 1100) + 0.4 * bp(raw, 1000, 1400) + 0.25 * lp(raw, 500)


def brass(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    ph = (freq * t) % 1.0
    saw = 2 * ph - 1
    cut = 300 + 900 * env(n, 0.35, 0.6, 0.55, 0.6)
    out = lp(saw, 900, 2) * 0.6 + lp(saw, 350, 2) * 0.6
    return out * env(n, 0.25, 0.3, 0.8, min(0.8, dur * 0.4)) * (0.5 + 0.5 * cut / 1200)


def piano(freq, dur=2.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = sum(np.sin(2 * np.pi * freq * k * t * (1 + 0.0004 * k * k)) * np.exp(-t * (1.6 + 1.1 * k)) / k
              for k in range(1, 7))
    hammer = bp(rng.standard_normal(n), 800, 4000) * np.exp(-t * 90) * 0.15
    return (out + hammer) * env(n, 0.003, 0.05, 1, 0.2)


def dum(g=1.0, low=55):
    t = tt(0.7)
    fr = low + 60 * np.exp(-t * 30)
    body = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 7)
    skin = lp(rng.standard_normal(len(t)), 900) * np.exp(-t * 40) * 0.4
    return (body + skin) * g


def tek(g=0.5):
    t = tt(0.15)
    return bp(rng.standard_normal(len(t)), 1800, 7000) * np.exp(-t * 45) * g


def daf(g=1.0):
    """Frame drum with jingles."""
    t = tt(1.0)
    jing = bp(rng.standard_normal(len(t)), 5000, 11000) * np.exp(-t * 9) * 0.35
    body = dum(1.0, 62)
    return np.pad(body, (0, len(t) - len(body))) * 0.9 * g + jing * g


def taiko(g=1.0):
    t = tt(1.6)
    fr = 42 + 50 * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 3.2)
    slap = lp(rng.standard_normal(len(t)), 1500) * np.exp(-t * 35) * 0.5
    return (body + slap) * g


def timpani(freq, g=1.0):
    t = tt(2.5)
    s = np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 1.5 * t) * np.exp(-t * 3)
    roll = lp(rng.standard_normal(len(t)), 400) * np.exp(-t * 6) * 0.3
    return (s * np.exp(-t * 1.6) + roll) * g


def tick_click(g=1.0, lo=2500, hi=7000, dec=300):
    t = tt(0.04)
    return bp(rng.standard_normal(len(t)), lo, hi) * np.exp(-t * dec) * g


# ------------------------------------------------------------------ sound effects
def whoosh(dur=0.6, lo=500, hi=4000):
    n = int(dur * SR)
    x = bp(rng.standard_normal(n), lo, hi)
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return x * e * 0.6


def rustle(dur=0.8, density=60):
    n = int(dur * SR)
    out = bp(rng.standard_normal(n), 2500, 9000) * 0.12
    for _ in range(int(density * dur)):
        i = rng.integers(0, max(1, n - 2000))
        k = int(rng.uniform(300, 1600))
        out[i:i + k] += bp(rng.standard_normal(k), 1500, 8000) * np.exp(-np.arange(k) / k * 5) * rng.uniform(0.2, 0.7)
    return out * env(n, 0.03, 0.1, 1, 0.15)


def slap():
    t = tt(0.3)
    return bp(rng.standard_normal(len(t)), 300, 3500) * np.exp(-t * 40) + np.sin(2 * np.pi * 110 * t) * np.exp(-t * 30) * 0.6


def tear(dur=0.9):
    n = int(dur * SR)
    out = np.zeros(n)
    i = 0
    while i < n - 800:
        k = int(rng.uniform(150, 700))
        out[i:i + k] += bp(rng.standard_normal(k), 1200, 7500) * rng.uniform(0.3, 1.0)
        i += int(rng.uniform(60, 400))
    return out * env(n, 0.05, 0.1, 1, 0.2) * 0.5


def scribble(dur=0.8, rate=8):
    t = tt(dur)
    stroke = 0.5 + 0.5 * np.abs(np.sin(np.pi * rate * t + rng.random() * 3))
    return bp(rng.standard_normal(len(t)), 2200, 7000) * stroke * env(len(t), 0.02, 0.1, 1, 0.1) * 0.35


def squeak(dur=0.32):
    t = tt(dur)
    fr = 1700 + 300 * t / dur + 60 * np.sin(2 * np.pi * 30 * t)
    s = np.sin(2 * np.pi * np.cumsum(fr) / SR) * 0.25 + bp(rng.standard_normal(len(t)), 2000, 6000) * 0.3
    return s * np.sin(np.pi * t / dur) ** 2 * 0.5


def pop():
    t = tt(0.09)
    fr = 900 - 400 * t / 0.09
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 45)


def snip():
    out = np.zeros(int(0.12 * SR))
    for at in (0.0, 0.05):
        c = tick_click(1.0, 2500, 9000, 150)
        i = int(at * SR)
        out[i:i + len(c)] += c
    return out


def pin_push():
    t = tt(0.25)
    return np.sin(2 * np.pi * 160 * t) * np.exp(-t * 35) * 0.8 + np.pad(tick_click(0.8, 3000, 8000), (0, len(t) - int(0.04 * SR)))


def stamp_thud():
    t = tt(0.5)
    body = np.sin(2 * np.pi * np.cumsum(70 + 80 * np.exp(-t * 40)) / SR) * np.exp(-t * 14)
    smack = lp(rng.standard_normal(len(t)), 1800) * np.exp(-t * 50) * 0.7
    return body + smack


def padlock():
    out = np.zeros(int(0.25 * SR))
    for at, g in ((0.0, 0.8), (0.07, 1.0)):
        t = tt(0.06)
        c = bp(rng.standard_normal(len(t)), 3000, 9000) * np.exp(-t * 160) + np.sin(2 * np.pi * 2600 * t) * np.exp(-t * 90) * 0.4
        i = int(at * SR)
        out[i:i + len(c)] += c * g
    return out


def typekey():
    t = tt(0.09)
    return bp(rng.standard_normal(len(t)), 1500, 6000) * np.exp(-t * 120) * 0.8 + np.sin(2 * np.pi * 180 * t) * np.exp(-t * 60) * 0.3


def boom():
    t = tt(3.0)
    fr = 38 + 40 * np.exp(-t * 6)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 1.4) + lp(rng.standard_normal(len(t)), 180) * np.exp(-t * 3) * 0.5


def swell(dur=1.6):
    n = int(dur * SR)
    x = lp(rng.standard_normal(n), 2500) * np.linspace(0, 1, n) ** 3
    return x * 0.6


def wind(dur, cut=500, depth=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    m = 1 + depth * np.sin(2 * np.pi * 0.13 * t + rng.random() * 6) * np.sin(2 * np.pi * 0.05 * t + 1)
    return lp(rng.standard_normal(n), cut) * m * env(n, 1.2, 0.1, 1, 1.5)


def birds(dur):
    out = np.zeros(int(dur * SR))
    for _ in range(int(dur / 1.6)):
        d = rng.uniform(0.18, 0.35)
        t = tt(d)
        fr = 3200 + 900 * np.sin(2 * np.pi * 14 * t) + 1500 * t / d
        b = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(np.pi * t / d) ** 2
        i = int(rng.uniform(0, dur - d) * SR)
        out[i:i + len(b)] += b * rng.uniform(0.3, 1)
    return out


def creak(dur=1.2):
    t = tt(dur)
    fr = 95 + 25 * np.sin(2 * np.pi * 0.7 * t) + rng.normal(0, 8, len(t)).cumsum() / SR * 30
    pulses = (np.sin(2 * np.pi * np.cumsum(fr) / SR) > 0.97).astype(float)
    return bp(pulses, 250, 2200) * env(len(t), 0.2, 0.1, 1, 0.3) * 3


def crackle(dur, rate=14):
    n = int(dur * SR)
    out = lp(rng.standard_normal(n), 1200) * 0.08
    for _ in range(int(rate * dur)):
        i = rng.integers(0, n - 600)
        k = int(rng.uniform(80, 500))
        out[i:i + k] += bp(rng.standard_normal(k), 1000, 7000) * np.exp(-np.arange(k) / k * 6) * rng.uniform(0.2, 1)
    return out * env(n, 0.5, 0.1, 1, 0.8)


def murmur(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 180, 700) * (1 + 0.4 * np.sin(2 * np.pi * 0.6 * t)) * env(n, 1, 0.1, 1, 1) * 0.5


def steps(dur, rate=1.8, lo=500, hi=5000):
    out = np.zeros(int(dur * SR))
    k = 0
    while (k + 1) / rate < dur:
        st = np.zeros(int(0.16 * SR))
        for _ in range(25):
            i = rng.integers(0, len(st) - 300)
            st[i:i + 250] += bp(rng.standard_normal(250), lo, hi) * rng.uniform(0.1, 0.5)
        st *= np.exp(-np.arange(len(st)) / len(st) * 3)
        i = int((k / rate + rng.normal(0, 0.02)) * SR)
        out[max(0, i):max(0, i) + len(st)] += st[: len(out) - max(0, i)]
        k += 1
    return out


def hooves(dur, rate=2.4, snow=False, gallop=True):
    out = np.zeros(int(dur * SR))
    pattern = (0, 0.09, 0.2, 0.28) if gallop else (0, 0.5)
    k = 0
    while k / rate < dur:
        for off in pattern:
            at = (k + off) / rate if not gallop else k / rate + off * 0.5
            i = int(at * SR)
            t = tt(0.12)
            h = np.sin(2 * np.pi * 130 * t) * np.exp(-t * 45) + bp(rng.standard_normal(len(t)), 300, 2500) * np.exp(-t * 60) * 0.6
            if snow:
                h += bp(rng.standard_normal(len(t)), 2000, 8000) * np.exp(-t * 25) * 0.4
            if i + len(h) < len(out):
                out[i:i + len(h)] += h * rng.uniform(0.6, 1)
        k += 1
    return out


def crickets(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for fr, rate, ph in ((4400, 2.6, 0), (4900, 3.1, 1.3)):
        gate = (np.sin(2 * np.pi * rate * t + ph) > 0.6) * (np.sin(2 * np.pi * 38 * t) > 0)
        out += np.sin(2 * np.pi * fr * t) * lp(gate.astype(float), 300)
    return out * 0.2 * env(n, 1, 0.1, 1, 1)


def rifle_far():
    t = tt(1.6)
    crack = lp(rng.standard_normal(len(t)), 1800) * np.exp(-t * 30)
    body = np.sin(2 * np.pi * 70 * t) * np.exp(-t * 12) * 0.6
    tail = lp(rng.standard_normal(len(t)), 600) * np.exp(-t * 3) * 0.25
    return crack + body + tail


def match():
    t = tt(0.9)
    strike = bp(rng.standard_normal(len(t)), 2000, 9000) * np.exp(-t * 12)
    flare = lp(rng.standard_normal(len(t)), 1500) * (1 - np.exp(-t * 8)) * np.exp(-t * 2) * 0.5
    return strike + flare


def telegraph(dur=1.6):
    out = np.zeros(int(dur * SR))
    at = 0.0
    while at < dur - 0.2:
        c = tick_click(1.0, 1500, 6000, 220)
        i = int(at * SR)
        out[i:i + len(c)] += c
        up = int((at + rng.choice([0.06, 0.18])) * SR)
        if up + len(c) < len(out):
            out[up:up + len(c)] += tick_click(0.6, 1200, 5000, 260)
        at += rng.choice([0.12, 0.24, 0.36])
    return out


def rise_tone(dur=1.0, f0=220, f1=520):
    t = tt(dur)
    fr = f0 + (f1 - f0) * t / dur
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(np.pi * t / dur) * 0.4


def bell(freq, dur=1.6):
    t = tt(dur)
    return sum(np.sin(2 * np.pi * freq * m * t) * np.exp(-t * (2 + 2 * k)) * a
               for k, (m, a) in enumerate(((1, 1), (2.76, 0.4), (5.4, 0.2), (8.9, 0.1)))) * 0.5


def battle_far(dur):
    n = int(dur * SR)
    out = lp(rng.standard_normal(n), 250) * 0.6
    for _ in range(int(dur * 1.5)):
        i = rng.integers(0, n - SR)
        out[i:i + int(1.6 * SR)] += lp(rifle_far(), 700)[: n - i] * rng.uniform(0.2, 0.7)
    return out * env(n, 1.5, 0.1, 1, 1.5)


def plane(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    u = t / dur
    fr = 72 * (1 + 0.06 * (0.5 - u))                                 # doppler-ish drop
    ph = (np.cumsum(fr) / SR) % 1.0
    buzz = lp(2 * ph - 1, 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 24 * t))
    a = np.exp(-((u - 0.55) / 0.28) ** 2)
    return buzz * a


def water(dur):
    n = int(dur * SR)
    out = bp(rng.standard_normal(n), 300, 2500) * 0.4
    for _ in range(int(dur * 18)):
        d = rng.uniform(0.02, 0.06)
        t = tt(d)
        fr = rng.uniform(300, 900) * (1 + t / d)
        b = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(np.pi * t / d)
        i = rng.integers(0, n - len(b))
        out[i:i + len(b)] += b * rng.uniform(0.1, 0.35)
    return out * env(n, 1, 0.1, 1, 1)


def chain():
    out = np.zeros(int(1.4 * SR))
    at = 0.0
    for k in range(7):
        t = tt(0.15)
        fr = rng.uniform(2200, 4200)
        c = (np.sin(2 * np.pi * fr * t) + 0.6 * np.sin(2 * np.pi * fr * 1.47 * t)) * np.exp(-t * 35) \
            + bp(rng.standard_normal(len(t)), 3000, 9000) * np.exp(-t * 80) * 0.5
        i = int(at * SR)
        out[i:i + len(c)] += c * (0.5 + 0.08 * k)
        at += rng.uniform(0.05, 0.11)
    t = tt(0.5)
    drop = lp(rng.standard_normal(len(t)), 900) * np.exp(-t * 18) + np.sin(2 * np.pi * 90 * t) * np.exp(-t * 14)
    i = int((at + 0.1) * SR)
    out[i:i + len(drop)] += drop[: len(out) - i]
    return out


def clang():
    t = tt(2.0)
    s = sum(np.sin(2 * np.pi * fr * t) * np.exp(-t * dk) for fr, dk in ((180, 2.5), (311, 3.2), (467, 4), (733, 5)))
    return lp(s, 1200) * 0.4 + lp(rng.standard_normal(len(t)), 800) * np.exp(-t * 20) * 0.5


def unlock():
    out = np.zeros(int(0.8 * SR))
    for at in (0.0, 0.18, 0.42):
        t = tt(0.12)
        c = bp(rng.standard_normal(len(t)), 1500, 6000) * np.exp(-t * 70) + np.sin(2 * np.pi * 900 * t) * np.exp(-t * 60) * 0.4
        i = int(at * SR)
        out[i:i + len(c)] += c
    return out


def room(dur):
    n = int(dur * SR)
    return bp(rng.standard_normal(n), 90, 380) * 0.5 * env(n, 0.8, 0.1, 1, 0.8)


def heartbeat(g=1.0):
    out = np.zeros(int(1.0 * SR))
    for at, a in ((0.0, 1.0), (0.24, 0.7)):
        t = tt(0.4)
        h = np.sin(2 * np.pi * np.cumsum(48 + 30 * np.exp(-t * 25)) / SR) * np.exp(-t * 12)
        i = int(at * SR)
        out[i:i + len(h)] += h * a
    return out * g


def gavel():
    t = tt(0.6)
    knock = bp(rng.standard_normal(len(t)), 500, 2500) * np.exp(-t * 60) + np.sin(2 * np.pi * 420 * t) * np.exp(-t * 40) * 0.6
    return knock + np.sin(2 * np.pi * 95 * t) * np.exp(-t * 20) * 0.5


S27_SHOTS = (0.33, 0.37, 0.41, 0.46, 0.48, 0.53, 0.57)      # also drives the muzzle-light flickers in scenes.S27

# ------------------------------------------------------------------ score
CHORDS_KURD = [("D", "A", "D'", "F"), ("Bb,", "F", "Bb", "D'"), ("G,", "D", "G", "Bb"), ("A,", "E", "A", "C#")]


def theme_notes(slow=1.0):
    """The film's theme (ney), maqam Kurd: rises to the fifth and returns."""
    seq = [("A", 0, 1.4), ("Bb", 0, 0.5), ("A", 0, 0.5), ("G", 0, 0.7), ("F", 0, 1.2), ("G", 0, 0.5), ("F", 0, 0.5),
           ("Eb", 0, 0.7), ("D", 0, 2.2), ("D", 0, 0.5), ("Eb", 0, 0.5), ("F", 0, 0.9), ("G", 0, 0.6), ("A", 0, 1.6),
           ("C", 0, 0.6), ("Bb", 0, 0.6), ("A", 0, 0.8), ("G", 0, 0.6), ("A", 0, 2.4)]
    t, out = 0.0, []
    for nt, o, d in seq:
        out.append((t, nt, o, d * slow))
        t += d * slow
    return out, t


def chapter_music(ch, dur, cues):
    """Return stereo (2, n) bed for one chapter. cues: dict of chapter-relative times for hits/peaks."""
    n = int(dur * SR)
    L = np.zeros((2, n))

    def put(sig, t0, g, p=0.0):
        st = sig if sig.ndim == 2 else pan(sig, p)
        i = int(t0 * SR)
        if i < 0:
            st, i = st[:, -i:], 0
        if i >= n:
            return
        j = min(n, i + st.shape[1])
        L[:, i:j] += st[:, : j - i] * g

    def drone(notes, g, cut=500, a=3, r=3):
        d = pad([f(x, o) for x, o in notes], dur, cut=cut, detune=0.002)
        put(d * env(len(d), a, 0.1, 1, r), 0, g)

    if ch == 1:                                   # cold open: drone, a single oud note, (wind is SFX)
        drone([("D", -2), ("A", -2)], 0.16, 380, 4, 3)
        for t0 in cues.get("oud", []):
            put(pluck(f("D", -1), 3.5, bright=0.3, decay=0.998), t0, 0.35, -0.2)
    elif ch in (2, 11):                           # warm strings + ney theme (ch 11: slower + choir)
        slow = 1.25 if ch == 11 else 1.0
        bar = 60 / 70 * 4 * slow
        k, t = 0, 0.0
        while t < dur - 1:
            ch_ = CHORDS_KURD[k % 4]
            cd = pad([f(x, -2 if i == 0 else -1) for i, x in enumerate(ch_)], bar + 0.6, cut=900)
            put(cd * env(len(cd), 0.8, 0.2, 1, 0.8), t, 0.20)
            if ch == 11:
                cc = choir([f(x, -1) for x in ch_[1:]], bar + 0.6)
                put(cc * env(len(cc), 1.2, 0.2, 1, 1.0), t, 0.30)
            for j in range(8):                    # oud arpeggio, eighths
                nt = [ch_[0], ch_[1], ch_[2], ch_[1], ch_[3], ch_[1], ch_[2], ch_[1]][j]
                if ch == 11 and j % 2:
                    continue
                put(pluck(f(nt, -1), 1.4, bright=0.35), t + j * bar / 8 + rng.normal(0, 0.005), 0.16, -0.35)
            t += bar
            k += 1
        notes, tl = theme_notes(slow)
        start = cues.get("theme", 3.0)
        while start + tl < dur - 0.5:
            for t0, nt, o, d in notes:
                put(ney(f(nt, o), d + 0.25), start + t0, 0.22, 0.15)
            start += tl + 6.0
    elif ch == 3:                                 # majestic: low strings, daf on downbeat, rising
        bar = 60 / 76 * 4
        k, t = 0, 0.0
        while t < dur - 1:
            ch_ = [("D", "A", "D'", "F"), ("Bb,", "F", "Bb", "D'"), ("C,", "G", "C", "Eb"), ("D", "A", "D'", "F")][k % 4]
            cd = pad([f(x, -2 if i == 0 else -1) for i, x in enumerate(ch_)], bar + 0.6, cut=900 + 120 * k)
            g = 0.18 + 0.02 * k
            put(cd * env(len(cd), 0.5, 0.2, 1, 0.6), t, g)
            put(daf(0.55), t, 0.5)
            put(dum(0.3), t + bar / 2, 0.35)
            t += bar
            k += 1
        for t0 in cues.get("hit", []):
            put(timpani(f("D", -3), 0.9), t0, 0.6)
    elif ch == 4:                                 # tension: ticking pulse, low brass, dissonant strings, 90 BPM
        beat = 60 / 90
        drone([("D", -2), ("Eb", -1), ("A", -2)], 0.13, 600)
        t = 0.0
        while t < dur:
            put(tick_click(0.5, 3000, 7000, 250), t, 0.5, 0.3)
            t += beat
        t = 0.0
        while t < dur - 2:
            put(brass(f("D", -2), beat * 3.6), t, 0.32)
            put(brass(f("Eb", -2), beat * 3.6), t + beat * 4, 0.28)
            t += beat * 8
        for t0 in cues.get("hit", []):
            put(brass(f("D", -3), 3.0), t0, 0.5)
    elif ch == 5:                                 # investigative pulse, muted percussion, building
        e8 = 60 / 100 / 2
        drone([("D", -2), ("A", -2)], 0.12, 500)
        pat = ["D", "D", "Eb", "D", "F", "D", "Eb", "C,"]
        t, k = 0.0, 0
        while t < dur:
            g = 0.10 + 0.10 * (t / dur)
            put(pluck(f(pat[k % 8], -1), 0.5, bright=0.15, decay=0.99), t, g, -0.2)
            if k % 4 == 2:
                put(tek(0.3), t, g * 1.5, 0.3)
            if k % 8 == 0:
                put(dum(0.4), t, g * 1.6)
            t += e8
            k += 1
    elif ch == 6:                                 # drums enter; urgent; hard hits on the clash
        beat = 60 / 112
        drone([("D", -2), ("A", -2), ("Eb", -1)], 0.12, 650)
        t, k = 0.0, 0
        stop = cues.get("silence", (None, None))
        while t < dur:
            if stop[0] is None or not (stop[0] <= t < stop[1]):
                if k % 4 in (0, 2):
                    put(dum(0.8), t, 0.40)
                if k % 4 == 3:
                    put(dum(0.6), t, 0.32)
                    put(dum(0.4), t + beat / 2, 0.3)
                put(tek(0.4), t + beat / 2, 0.3, 0.4)
            t += beat
            k += 1
        for t0 in cues.get("hit", []):
            put(taiko(1.0), t0, 0.7)
            put(timpani(f("D", -3)), t0, 0.5)
        if stop[0] is not None:
            i0, i1 = int(stop[0] * SR), int(stop[1] * SR)
            fade = np.ones(n)
            fade[i0:i1] = 0.0
            fade[max(0, i0 - 2400):i0] = np.linspace(1, 0, min(2400, i0))
            fade[i1:i1 + SR] = np.linspace(0, 1, len(fade[i1:i1 + SR]))
            L *= fade
    elif ch == 7:                                 # epic: daf + taiko + strings; peak at the gate; falls away
        beat = 60 / 96
        peak, lift = cues["peak"], cues["lift"]
        t, k = 0.0, 0
        while t < lift:
            g = 0.55 + 0.45 * min(1, t / peak) if t < peak else 1.0
            if k % 8 == 0:
                put(taiko(1.0), t, 0.55 * g)
            if k % 2 == 0:
                put(daf(0.6), t, 0.38 * g)
            put(tek(0.35), t + beat / 2, 0.22 * g, 0.4)
            if k % 4 == 0:
                ch_ = [("D", "A", "D'", "F"), ("Bb,", "F", "Bb", "D'"), ("C,", "G", "C", "Eb"), ("A,", "E", "A", "C#")][(k // 4) % 4]
                cd = pad([f(x, -2 if i == 0 else -1) for i, x in enumerate(ch_)], beat * 4 + 0.4, cut=900 + 900 * g)
                put(cd * env(len(cd), 0.15, 0.2, 1, 0.3), t, 0.2 * g)
            t += beat
            k += 1
        put(timpani(f("D", -3), 1.0), peak, 0.8)
        put(taiko(1.2), peak, 0.8)
        for t0, nt, d in ((peak, "D'", 1.6), (peak + 1.7, "C", 0.6), (peak + 2.3, "Bb", 0.6), (peak + 3.0, "A", 2.4)):
            put(ney(f(nt, 0), d + 0.25, vib=0.008), t0, 0.26, 0.15)
        low = pad([f("D", -3), f("D", -2)], dur - lift, cut=300)
        put(low * env(len(low), 0.6, 0.1, 1, 3), lift, 0.3)
    elif ch == 8:                                 # collapse: one sustained low note, heartbeat pulse
        drone([("D", -3), ("D", -2)], 0.24, 260, 1.5, 3)
        t = 1.0
        while t < dur - 1:
            put(heartbeat(0.9), t, 0.5)
            t += 1.25
    elif ch == 9:                                 # near silence, solo ney
        for t0, phrase in cues.get("ney", []):
            tt0 = t0
            for nt, o, d in phrase:
                put(ney(f(nt, o), d + 0.25, vib=0.007, breath=0.25), tt0, 0.2, 0.1)
                tt0 += d
    elif ch == 10:                                # slow mournful strings, no percussion
        prog = [("D", "A", "D'", "F"), ("G,", "D", "G", "Bb"), ("Bb,", "F", "Bb", "D'"), ("A,", "E", "A", "C#")]
        bar = 4.6
        t, k = 0.0, 0
        while t < dur - 0.5:
            ch_ = prog[k % 4]
            cd = pad([f(x, -2 if i == 0 else -1) for i, x in enumerate(ch_)], bar + 1.5, cut=800, trem=0.05)
            put(cd * env(len(cd), 1.5, 0.2, 1, 1.5), t, 0.26)
            t += bar
            k += 1
    elif ch == 12:                                # hopeful: warm strings + piano + light daf, rising
        prog = [("D", "F#", "A", "D'"), ("G,", "B", "D", "G"), ("Bb,", "F", "Bb", "D'"), ("A,", "C#", "E", "A")]
        bar = 60 / 72 * 4
        t, k = 0.0, 0
        verse = cues.get("verse", (None, None))
        while t < dur - 0.5:
            ch_ = prog[k % 4]
            rise = min(1.0, 0.6 + 0.4 * t / dur)
            cd = pad([f(x, -2 if i == 0 else -1) for i, x in enumerate(ch_)], bar + 0.8, cut=1000 + 700 * rise)
            put(cd * env(len(cd), 0.6, 0.2, 1, 0.8), t, 0.2 * rise)
            for j, x in enumerate((ch_[1], ch_[2], ch_[3], ch_[2])):
                put(piano(f(x, 0)), t + j * bar / 4, 0.16 * rise, -0.2)
            if verse[0] is None or not (verse[0] - 0.5 <= t < verse[1]):
                put(daf(0.35), t, 0.3 * rise)
                put(tek(0.3), t + bar / 2, 0.2 * rise, 0.3)
            t += bar
            k += 1
        if verse[0] is not None:
            i0, i1 = int(verse[0] * SR), int(verse[1] * SR)
            g = np.ones(n)
            ramp = int(0.8 * SR)
            g[i0:i1] = 0.3
            g[max(0, i0 - ramp):i0] = np.linspace(1, 0.3, min(ramp, i0))
            g[i1:i1 + ramp] = np.linspace(0.3, 1, len(g[i1:i1 + ramp]))
            L *= g
    elif ch == 13:                                # firm low strings, theme resolves, stop on the end card
        pos_end, final = cues["pos_end"], cues["final"]
        s = pad([f("D", -3), f("D", -2), f("A", -2), f("F", -1)], pos_end + 0.5, cut=700)
        put(s * env(len(s), 0.4, 0.2, 1, 0.6), 0, 0.3)
        fin = pad([f("D", -2), f("A", -2), f("D", -1), f("F", -1), f("A", -1)], dur - final, cut=1400)
        put(fin * env(len(fin), 0.8, 0.5, 0.85, 2.5), final, 0.3)
        for t0, nt, d in ((final + 0.3, "A", 1.2), (final + 1.5, "G", 0.6), (final + 2.1, "F", 0.6), (final + 2.7, "D", 3.4)):
            put(ney(f(nt, 0), d + 0.3, vib=0.007), t0, 0.22, 0.15)
        put(timpani(f("D", -3), 0.8), pos_end - 0.2, 0.5)
    return L


# ------------------------------------------------------------------ build
def load_parts(lang):
    out = {}
    d = PROJ / "build" / lang / "vo" / "parts"
    for p in sorted(d.glob("*.wav")):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                             capture_output=True, check=True).stdout
        out[p.stem] = np.frombuffer(raw, np.float32).astype(np.float64)
    return out


def build(lang, music_cached=False):
    tl = json.loads((PROJ / "build" / lang / "timeline.json").read_text(encoding="utf-8"))
    scenes = tl["scenes"]
    total = scenes[-1]["start"] + scenes[-1]["dur"]
    S = {s["id"]: s for s in scenes}

    def T(sid, tc=0.0):
        """Absolute time of content time tc in scene sid."""
        s = S[sid]
        return s["start"] + s["card"] + tc

    def D(sid):
        return S[sid]["dur"] - S[sid]["card"]

    def A(sid, k=0):
        a = S[sid]["audio"][k]
        return a["start"] - S[sid]["card"], a["dur"]

    voice, music, sfx = Bus(total), Bus(total), Bus(total)

    # ---- narration
    parts = load_parts(lang)
    for s in scenes:
        for a in s["audio"]:
            voice.put(parts[a["seg"]], s["start"] + a["start"], 1.0, 0.0)

    # ---- music, chapter by chapter
    chapters = {}
    for s in scenes:
        c = chapters.setdefault(s["chapter"], [s["start"], s["start"] + s["dur"]])
        c[1] = s["start"] + s["dur"]

    def rel(ch, sid, tc=0.0):
        return T(sid, tc) - chapters[ch][0]

    cues = {
        1: {"oud": [rel(1, "S01", 1.2), rel(1, "S03", 0.35)]},
        2: {"theme": rel(2, "S04", 0.6)},
        3: {"hit": [rel(3, "S08", D("S08") * 0.85)]},
        4: {"hit": [rel(4, "S11", D("S11") * 0.45)]},
        5: {},
        6: {"hit": [rel(6, "S27", D("S27") * 0.33)], "silence": (rel(6, "S27", D("S27") * 0.62), rel(6, "S28", 0.0))},
        7: {"peak": rel(7, "S36", D("S36") * 0.6), "lift": rel(7, "S37", D("S37") * 0.4)},
        8: {},
        9: {"ney": [(rel(9, "S41", 0.5), [("A", 0, 1.6), ("Bb", 0, 0.5), ("A", 0, 0.5), ("G", 0, 0.8), ("F", 0, 2.2)]),
                    (rel(9, "S41", 9.0), [("F", 0, 0.8), ("G", 0, 0.8), ("A", 0, 1.4), ("G", 0, 0.6), ("F", 0, 0.6), ("Eb", 0, 0.7), ("D", 0, 2.6)]),
                    (rel(9, "S43", A("S43")[0] + A("S43")[1] + 0.9), [("D", 0, 3.0)])]},
        10: {},
        11: {"theme": rel(11, "S47", 0.3)},
        12: {"verse": (rel(12, "S51", 0.0), rel(12, "S51", D("S51") * 0.55))},
        13: {"pos_end": rel(13, "S52", D("S52")), "final": rel(13, "S53", 0.0)},
    }
    gain = {1: 1.0, 2: 0.9, 3: 0.95, 4: 0.9, 5: 0.9, 6: 1.0, 7: 1.0, 8: 0.9, 9: 0.9, 10: 0.95, 11: 0.9, 12: 0.95, 13: 1.0}
    if music_cached:
        music = None
    for ch, (a, b) in ([] if music_cached else chapters.items()):
        dur = b - a + (0.0 if ch == 13 else 1.2)
        st = chapter_music(ch, dur, cues[ch])
        st = verb(st, IR_HALL, 0.3)
        n = st.shape[1]
        fade = np.ones(n)
        fi = int(1.0 * SR)
        fade[:fi] = np.linspace(0, 1, fi)
        if ch != 13:
            fo = int(2.2 * SR)
            end = int(dur * SR)
            fade[end - fo:end] = np.linspace(1, 0, fo)
            fade[end:] = 0
        music.put(st * fade * gain[ch], a, 1.0)
        print(f"music ch{ch}: {dur:.1f}s", flush=True)

    # ---- sound design
    def fx(sig, sid, tc, g=0.5, p=0.0, room_mix=0.18):
        st = verb(pan(sig, p), IR_ROOM, room_mix)
        sfx.put(st, T(sid, tc), g)

    # paper slide on every cut + a whoosh on chapter cards
    for i, s in enumerate(scenes[1:], 1):
        sfx.put(pan(rustle(0.45, 40) + whoosh(0.45, 600, 3500) * 0.6, 0.0), s["start"] - 0.02, 0.10)
        if s["card"]:
            sfx.put(pan(whoosh(0.9, 200, 1500), 0), s["start"], 0.18)
            sfx.put(pan(bell(f("D", 0), 2.0), 0), s["start"] + 0.2, 0.06)

    # S01 cold open
    fx(wind(D("S01") + 2.5, 450), "S01", 0, 0.16, -0.1, 0)
    fx(birds(D("S01")), "S01", 0.8, 0.03, 0.4, 0.3)
    fx(creak(1.3), "S01", A("S01")[0] + A("S01")[1] - 0.3, 0.12, 0.2)
    # S02 typewriter per word while the quote types; paper rustle
    fx(rustle(0.8), "S02", 0.2, 0.08)
    qs, qd = A("S02", 1)
    w0, w1 = qs + qd * 0.2, qs + qd * 0.5
    nw = sum(len(x.split()) for x in S["S02"]["ost"])
    for k in range(nw):
        fx(typekey(), "S02", w0 + (w1 - w0) * k / nw, 0.12, 0.2)
    # S03 boom + reverse swell + paper slap
    fx(swell(1.6), "S03", -1.25, 0.18)
    fx(boom(), "S03", 0.35, 0.55, 0, 0.3)
    fx(slap(), "S03", 0.15, 0.2)
    # S04 map whoosh, pin pop, pen scribble
    d4 = D("S04")
    fx(whoosh(0.7, 300, 2500), "S04", d4 * 0.22 - 0.3, 0.2)
    fx(pop(), "S04", d4 * 0.22 + 0.45, 0.3)
    fx(scribble(0.5), "S04", d4 * 0.22 + 0.7, 0.2)
    fx(whoosh(0.6, 400, 3000), "S04", d4 * 0.6 - 0.3, 0.12)
    # S05 pen lines, whoosh on route
    d5 = D("S05")
    fx(scribble(0.5, 5), "S05", d5 * 0.18 + 0.2, 0.18)
    fx(whoosh(1.2, 500, 3000), "S05", d5 * 0.36 + 0.4, 0.15)
    fx(scribble(0.5, 5), "S05", d5 * 0.7 + 0.5, 0.18)
    # S06 page turn, highlighter per word
    d6 = D("S06")
    fx(rustle(0.6), "S06", d6 * 0.42, 0.14)
    for i in range(3):
        fx(squeak(), "S06", d6 * 0.42 + 0.3 + i * d6 * 0.58 * 0.22 + 0.25, 0.12, 0.2)
    # S07 rewind whoosh with clock ticks, then a daf hit
    d7 = D("S07")
    for k in range(int(d7 * 0.42 / 0.12)):
        fx(tick_click(0.6), "S07", k * 0.12 * (1 - 0.3 * k / 40), 0.2, 0.3, 0.05)
    fx(whoosh(d7 * 0.42, 300, 2500)[::-1].copy(), "S07", 0, 0.2)
    fx(daf(1.0), "S07", d7 * 0.42, 0.45, 0, 0.3)
    # S08 daf on Jerusalem
    fx(daf(1.0), "S08", D("S08") * 0.85, 0.45, 0, 0.3)
    # S09 distant marching drums, paper slide
    for k in range(int(D("S09") / 0.6)):
        fx(lp(dum(0.5), 400), "S09", 0.3 + k * 0.6, 0.08, -0.3, 0.4)
    # S10 map unfold, highlighter
    fx(rustle(1.0, 80), "S10", 0.2, 0.12)
    for i in range(3):
        fx(squeak(0.4), "S10", D("S10") * 0.62 + i * 0.3, 0.1, 0.2)
    # S11 paper tear
    fx(tear(1.0), "S11", D("S11") * 0.45, 0.35, 0.1)
    # S12 newspaper rustle, thread snap
    fx(rustle(0.9), "S12", 0.1, 0.14)
    for k in range(5):
        fx(tick_click(1.0, 1500, 5000, 120), "S12", D("S12") * 0.80 + k * 0.03, 0.35, (k - 2) * 0.2)
    # S13 stamp thud, marker strike
    fx(stamp_thud(), "S13", D("S13") * 0.38, 0.55)
    fx(scribble(0.4, 3), "S13", D("S13") * 0.82, 0.3)
    # S14 padlocks
    for i in range(3):
        fx(padlock(), "S14", D("S14") * (0.45 + i * 0.15), 0.35, (1 - i) * 0.4)
    # S15 rumble, four stamps
    fx(lp(noise(5.0), 120) * env(int(5 * SR), 1, 0.1, 1, 1.5), "S15", 0.3, 0.25)
    for i in range(4):
        fx(stamp_thud(), "S15", D("S15") * (0.55 + i * 0.1), 0.4, (0.4 - i * 0.27))
    # S16 wind over fields, wooden knock
    fx(wind(D("S16") + 1, 700, 0.6), "S16", 0, 0.12, 0, 0)
    fx(gavel()[: int(0.3 * SR)] * 0.6, "S16", D("S16") * 0.62, 0.2)
    # S17 scissor snips, ledger stamp
    for i in range(7):
        fx(snip(), "S17", D("S17") * 0.3 + i * 0.35, 0.3, (i - 3) * 0.15)
    fx(stamp_thud(), "S17", D("S17") * 0.62 + 0.6, 0.5)
    # S18 pins, string
    fx(pin_push(), "S18", S["S18"]["audio"][0]["start"] - S["S18"]["card"] + 0.55, 0.4)
    fx(pin_push(), "S18", D("S18") * 0.3 + 0.45, 0.4)
    fx(whoosh(0.5, 1500, 6000), "S18", D("S18") * 0.55, 0.12)
    # S19 footsteps on gravel under the route, thump for the handshake
    d19 = D("S19")
    fx(steps(d19 * 0.3, 1.8), "S19", 0.6, 0.14, -0.2)
    fx(pin_push(), "S19", d19 * 0.5 + 0.65, 0.4)
    fx(lp(heartbeat(0.7)[: int(0.3 * SR)], 300), "S19", d19 * 0.5 + d19 * 0.5 * 0.45, 0.3)
    # S20 winter wind, room murmur, fire crackle
    fx(wind(D("S20") + 1, 600, 0.7), "S20", 0, 0.12, -0.2, 0)
    fx(murmur(D("S20")), "S20", 0.5, 0.06, 0.1, 0.3)
    fx(crackle(D("S20")), "S20", 0.3, 0.10, 0.3, 0.1)
    # S21 pins, envelope whoosh, seal thud
    d21 = D("S21")
    fx(pin_push(), "S21", 0.65, 0.4, 0.3)
    fx(pin_push(), "S21", 1.35, 0.4, 0.5)
    fx(whoosh(d21 * 0.32, 400, 3000), "S21", d21 * 0.5 + 0.3, 0.18, -0.3)
    fx(stamp_thud(), "S21", d21 * 0.5 + 0.3 + d21 * 0.5 * 0.65, 0.35, -0.4)
    # S22 horse trot under routes, pin pop at Aleppo
    d22 = D("S22")
    a22, dm = d22 * 0.4, d22 * 0.6
    fx(hooves(dm * 0.45, 2.0, gallop=False), "S22", a22 + dm * 0.2, 0.12, -0.2)
    fx(pop(), "S22", a22 + dm * 0.62, 0.3)
    # S23 pen circle, fire crackle
    fx(scribble(0.7, 4), "S23", D("S23") * 0.45, 0.25)
    fx(match(), "S23", D("S23") * 0.5, 0.2)
    fx(crackle(D("S23") * 0.5, 10), "S23", D("S23") * 0.5, 0.10, 0.2)
    # S24 hooves in snow, murmur at stops
    fx(hooves(D("S24") * 0.6, 1.4, snow=True, gallop=False), "S24", 0.3, 0.12, 0.1)
    fx(murmur(D("S24") * 0.6), "S24", 0.5, 0.05, 0, 0.3)
    # S25 group gallop, wind
    fx(hooves(D("S25") * 0.32, 2.6, snow=True), "S25", 0.0, 0.2, -0.1)
    fx(wind(D("S25") + 1, 500), "S25", 0, 0.1, 0.2, 0)
    # S26 night insects, boots
    fx(crickets(D("S26")), "S26", 0, 0.05, 0.3, 0.2)
    fx(steps(4.0, 2.2, 300, 4000), "S26", D("S26") * 0.42, 0.14, 0.2)
    # S27 distant rifle shots (low), then silence
    d27 = D("S27")
    for k in S27_SHOTS:
        fx(rifle_far(), "S27", d27 * k, 0.16, rng.uniform(-0.6, 0.6), 0.45)
    fx(crickets(d27 * 0.3), "S27", 0, 0.04, 0.3, 0.2)
    # S28 match strike, telegraph, gallop
    d28 = D("S28")
    fx(match(), "S28", 0.25, 0.28)
    fx(match(), "S28", d28 * 0.36 * 0.45, 0.2, 0.3)
    fx(telegraph(2.2), "S28", d28 * 0.66 + 0.2, 0.22, 0.2)
    fx(hooves(3.0, 2.6), "S28", d28 * 0.82, 0.16, -0.3)
    # S29 page rip, drum hit
    fx(tear(1.2), "S29", D("S29") * 0.5, 0.4)
    fx(taiko(1.0), "S29", D("S29") * 0.5, 0.45)
    # S30 newspaper flips, telegraph
    for k in range(3):
        fx(rustle(0.35, 70) + whoosh(0.35, 800, 5000) * 0.5, "S30", 0.2 + k * 0.35, 0.18, (k - 1) * 0.3)
    fx(telegraph(1.6), "S30", D("S30") * 0.45, 0.2, -0.2)
    # S31 bars grow with a rising tone, correction tick
    d31 = D("S31")
    fx(rise_tone(1.0, 220, 560), "S31", d31 * 0.18, 0.18)
    fx(rise_tone(1.0, 220, 330), "S31", d31 * 0.32, 0.18)
    fx(rise_tone(0.6, 330, 180), "S31", d31 * 0.62, 0.16)
    fx(tick_click(1.0, 1500, 4000, 200), "S31", d31 * 0.62 + 0.6, 0.3)
    # S32 soft map tones for each group
    for k, nt in enumerate(("D", "F", "A")):
        fx(bell(f(nt, 1)), "S32", D("S32") * (0.12 + k * 0.12), 0.08, (k - 1) * 0.4, 0.3)
    # S33 cavalry gallop rising
    h = hooves(D("S33"), 2.7) * np.linspace(0.3, 1, int(D("S33") * SR))
    fx(h, "S33", 0, 0.22, -0.1)
    # S34 arrows whoosh
    for k in (0.08, 0.2, 0.38):
        fx(whoosh(1.0, 400, 3000), "S34", D("S34") * k, 0.16, 0.2)
    fx(whoosh(1.3, 200, 2000), "S34", D("S34") * 0.6, 0.24)
    # S35 wind on stone, single low drum on the red X
    d35 = D("S35")
    fx(wind(d35 + 1, 800, 0.4), "S35", 0, 0.1, -0.2, 0)
    fx(taiko(0.9), "S35", d35 * 0.38 + 0.5 + d35 * 0.62 * 0.5, 0.45)
    # S36 far battle bed
    fx(battle_far(D("S36") * 0.6), "S36", D("S36") * 0.4, 0.14, 0, 0.5)
    # S37 wind
    fx(wind(D("S37") + 1, 500, 0.5), "S37", D("S37") * 0.4, 0.14, 0.2, 0)
    # S38 plane passing, low rumble
    d38 = D("S38")
    pl = plane(d38 * 0.45)
    pp = np.linspace(-0.8, 0.8, len(pl))
    sfx.put(np.stack([pl * np.sqrt(0.5 * (1 - pp)), pl * np.sqrt(0.5 * (1 + pp))]), T("S38", d38 * 0.55), 0.3)
    fx(lp(noise(d38), 120) * env(int(d38 * SR), 2, 0.1, 1, 2), "S38", 0, 0.2)
    # S39 river, chain
    d39 = D("S39")
    fx(water(d39 * 0.62), "S39", 0, 0.1, 0.2, 0.1)
    fx(chain(), "S39", d39 * 0.9, 0.35, 0, 0.3)
    # S40 room tone, metal door
    fx(room(D("S40")), "S40", 0, 0.12, 0, 0)
    fx(clang(), "S40", 0.4, 0.2, -0.4, 0.5)
    # S41 typewriter, room
    fx(room(D("S41")), "S41", 0, 0.1, 0, 0)
    qs, qd = A("S41")
    nw = sum(len(x.split()) for x in S["S41"]["ost"])
    for k in range(nw):
        fx(typekey(), "S41", qs + 0.2 + (qd * 0.22 - 0.2) * k / nw, 0.1, 0.2)
    # S42 corridor footsteps, unlock
    fx(steps(3.0, 1.6, 200, 3000), "S42", 0.0, 0.16, -0.3, 0.45)
    fx(unlock(), "S42", D("S42") * 0.3, 0.25, 0.2, 0.3)
    fx(room(D("S42")), "S42", 0, 0.1, 0, 0)
    # S43 room tone; heartbeat drum after the last word
    fx(room(D("S43")), "S43", 0, 0.12, 0, 0)
    qs, qd = A("S43")
    fx(heartbeat(1.0), "S43", qs + qd + 0.4, 0.55, 0, 0.3)
    nw = sum(len(x.split()) for x in S["S43"]["ost"])
    for k in range(nw):
        fx(typekey(), "S43", qs + 0.2 + (qd * 0.36 - 0.2) * k / nw, 0.09, 0.2)
    # S44 gavel, tick per mark (accelerating)
    d44 = D("S44")
    fx(gavel(), "S44", S["S44"]["audio"][0]["start"] - S["S44"]["card"] + 0.2, 0.45, 0, 0.3)
    for i in range(48):
        fx(tick_click(0.7, 2500, 7000, 300), "S44", d44 * 0.42 + (d44 * 0.38) * (i / 48) ** 0.7, 0.16, 0.2, 0.05)
    # S45 wind, the same creak, then silence
    fx(wind(D("S45"), 450), "S45", 0, 0.14, -0.1, 0)
    fx(creak(1.3), "S45", A("S45")[0] + A("S45")[1] - 0.2, 0.12, 0.2)
    # S46 distant fire, wind
    fx(crackle(D("S46") * 0.5, 9), "S46", 0, 0.08, 0.2, 0.3)
    fx(wind(D("S46"), 500), "S46", 0, 0.08, -0.2, 0)
    # S47/S48 typewriter on the pull-quote
    for sid, a_, b_ in (("S47", 0.3, 0.45), ("S48", 0.5, 0.92)):
        qs, qd = A(sid)
        nw = sum(len(x.split()) for x in S[sid]["ost"])
        for k in range(nw):
            fx(typekey(), sid, qs + qd * a_ + qd * (b_ - a_) * k / nw, 0.1, 0.2)
    # S50 counter ticks
    d50 = D("S50")
    for k in range(18):
        fx(tick_click(0.7, 2000, 6000, 250), "S50", d50 * 0.5 + d50 * 0.3 * (k / 18) ** 0.6, 0.14, 0.3)
    # S52 one deep hit at the end
    fx(taiko(1.2), "S52", D("S52") - 0.4, 0.5, 0, 0.3)
    # S54 sound logo
    fx(bell(f("D", 1), 3.0) + bell(f("A", 1), 3.0) * 0.6, "S54", 0.2, 0.12, 0, 0.4)
    for k, nt in enumerate(("D", "A", "D'")):
        fx(pluck(f(nt, -1), 2.0, 0.4), "S54", 0.3 + k * 0.25, 0.2, -0.2, 0.3)

    out = PROJ / "build" / lang / "audio"
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "stem_voice.npy", voice.x)
    np.save(out / "stem_sfx.npy", sfx.x)
    if music is not None:
        np.save(out / "stem_music.npy", music.x * np.float32(0.42))
    mix(lang)


MUSIC_DB = {1: 9.0, 2: 7.0, 3: 7.0, 4: 5.5, 5: 10.0, 6: 7.0, 7: 6.0, 8: 7.0, 9: 7.0, 10: 11.0, 11: 7.0, 12: 9.5, 13: 7.5}


def mix(lang):
    """Music ducked under the voice, SFX lightly ducked, soft limiter -> mix.wav (loudness pass happens in finish)."""
    out = PROJ / "build" / lang / "audio"
    tl = json.loads((PROJ / "build" / lang / "timeline.json").read_text(encoding="utf-8"))
    total = tl["scenes"][-1]["start"] + tl["scenes"][-1]["dur"]
    end = int(total * SR)
    vx = np.load(out / "stem_voice.npy")[:, :end]
    v = vx[0].astype(np.float64)
    e = np.sqrt(np.maximum(lp(v ** 2, 6), 0.0))
    ref = np.percentile(e[e > 1e-4], 60) if np.any(e > 1e-4) else 1.0
    e = np.clip(e / ref, 0, 1)
    att, rel_ = np.exp(-1 / (0.05 * SR / 64)), np.exp(-1 / (0.6 * SR / 64))
    es = e[::64]
    g = np.zeros_like(es)
    acc = 0.0
    for i, x in enumerate(es):
        acc = att * acc + (1 - att) * x if x > acc else rel_ * acc + (1 - rel_) * x
        g[i] = acc
    g = np.interp(np.arange(end), np.arange(len(g)) * 64, g).astype(np.float32)
    vpk = float(np.percentile(np.abs(v[np.abs(v) > 1e-3]), 99.5))
    del v, e
    m = vx * np.float32(0.5 / vpk)
    del vx
    mus = np.load(out / "stem_music.npy")[:, :end]
    # music bus level per chapter (dB): sits ~17 dB under the voice while it speaks, comes up in the gaps
    bounds = {}
    for sc in tl["scenes"]:
        c = bounds.setdefault(sc["chapter"], [sc["start"], sc["start"] + sc["dur"]])
        c[1] = sc["start"] + sc["dur"]
    pts_t, pts_g = [], []
    for ch_, (a, b) in sorted(bounds.items()):
        gdb = MUSIC_DB.get(ch_, 7.0)
        pts_t += [a + 0.5, b - 0.5]
        pts_g += [gdb, gdb]
    lvl = np.interp(np.arange(mus.shape[1]) / SR, pts_t, pts_g)
    lvl = (10 ** (lvl / 20)).astype(np.float32)
    m[:, :mus.shape[1]] += mus * lvl * (1 - 0.55 * g[:mus.shape[1]])
    del mus
    fx = np.load(out / "stem_sfx.npy")[:, :end]
    m[:, :fx.shape[1]] += fx * np.float32(0.8) * (1 - 0.30 * g[:fx.shape[1]])
    del fx
    fo = int(0.8 * SR)
    m[:, -fo:] *= np.linspace(1, 0, fo, dtype=np.float32)
    m = np.tanh(m * np.float32(1.1)) / np.float32(1.1)
    assert np.isfinite(m).all()
    wavfile.write(out / "mix.wav", SR, m.T.astype(np.float32))
    print("wrote", out / "mix.wav", f"{total:.1f}s")


if __name__ == "__main__":
    if "--mix" in sys.argv:
        mix(sys.argv[1])
    else:
        build(sys.argv[1], music_cached="--reuse-music" in sys.argv)
