#!/usr/bin/env python3
"""Original, royalty-free instrumental cues for the documentary (synthesised: ney, oud, string pad,
piano, daf, wind). Maqam Kurd on D. Output: assets/music/*.mp3   Run: python3 tools/make_music.py"""
import numpy as np, subprocess, pathlib
from scipy.signal import butter, sosfilt, lfilter, fftconvolve
from scipy.io import wavfile
SR = 44100
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets/music"; OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(7)
KURD = [0, 1, 3, 5, 7, 8, 10]
def deg(d, base=62):  # scale degree -> midi (D4 = 62)
    o, i = divmod(d, 7); return base + KURD[i] + 12 * o
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)
def env(n, a, r, sustain=1.0):
    e = np.ones(n) * sustain; A = min(int(a * SR), n); R = min(int(r * SR), n - A)
    e[:A] = np.linspace(0, sustain, A) if A else e[:A]
    if R: e[n - R:] = np.linspace(sustain, 0, R) * (e[n - R] / sustain if sustain else 1)
    return e

class Track:
    def __init__(self, sec): self.L = np.zeros(int(sec * SR) + SR * 4); self.R = np.zeros_like(self.L); self.sec = sec
    def add(self, x, t, gain=1.0, pan=0.0):
        i = int(t * SR); x = x[: max(0, len(self.L) - i)]
        self.L[i:i + len(x)] += x * gain * np.sqrt(0.5 * (1 - pan)); self.R[i:i + len(x)] += x * gain * np.sqrt(0.5 * (1 + pan))

def ney(m, dur, vib=True):
    n = int(dur * SR); t = np.arange(n) / SR; f0 = hz(m)
    vd = np.clip((t - 0.35) / 0.6, 0, 1) * 0.006 if vib else 0
    f = f0 * (1 + vd * np.sin(2 * np.pi * 5.2 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(ph) + 0.28 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph) + 0.04 * np.sin(4 * ph)
    breath = bp(rng.standard_normal(n), f0 * 1.2, min(f0 * 5, 9000)) * 0.35
    e = env(n, 0.22, min(0.5, dur * 0.4))
    chiff = np.exp(-t / 0.06) * 0.6
    return lp((tone * 0.8 + breath * (0.4 + chiff)) * e, 5000)

def pad(midis, dur, bright=1400):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for m in midis:
        for det in (-0.07, 0.0, 0.08):
            f = hz(m + det)
            for k in range(1, 7): x += np.sin(2 * np.pi * f * k * t + rng.uniform(0, 6.28)) / k
    x *= (1 + 0.15 * np.sin(2 * np.pi * 0.17 * t))
    return lp(x, bright) * env(n, min(2.5, dur / 3), min(2.5, dur / 3)) / (len(midis) * 6)

def oud(m, dur=1.6, bright=0.5):
    f = hz(m); N = int(SR / f); n = int(dur * SR)
    burst = np.zeros(n); burst[:N] = lp(rng.uniform(-1, 1, N), 2500 + 3000 * bright)[:N]
    a = np.zeros(N + 2); a[0] = 1; a[N] = -0.4975; a[N + 1] = -0.4975
    y = lfilter([1.0], a, burst)
    return lp(hp(y, 80), 4200) * env(n, 0.002, 0.25)

def piano(m, dur=4.0):
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(m); x = np.zeros(n)
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + 0.0004 * k * k)
        x += np.sin(2 * np.pi * fk * t) * np.exp(-t * (0.5 + 0.45 * k)) / k ** 1.4
    return x * env(n, 0.004, 0.6) * 0.6

def doum(gain=1.0):
    n = int(0.6 * SR); t = np.arange(n) / SR
    f = 55 + 65 * np.exp(-t / 0.05); ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.28)
    skin = lp(rng.standard_normal(n), 500) * np.exp(-t / 0.03) * 0.5
    return (body + skin) * gain

def tek(gain=0.35):
    n = int(0.25 * SR); t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 1800, 6000) * np.exp(-t / 0.045) * gain

def drone(midis, dur, gain=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for m in midis:
        f = hz(m)
        for k, a in ((1, 1), (2, .5), (3, .25), (4, .12), (5, .06)):
            x += a * np.sin(2 * np.pi * f * k * t + rng.uniform(0, 6.28)) * (1 + 0.2 * np.sin(2 * np.pi * (0.05 + 0.02 * k) * t))
    return lp(x, 900) * env(n, 4, 4) * gain / len(midis)

def wind(dur, gain=0.5):
    n = int(dur * SR); t = np.arange(n) / SR
    w = bp(rng.standard_normal(n), 250, 1600)
    mod = 0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * t) * np.sin(2 * np.pi * 0.023 * t + 1)
    return w * mod * env(n, 3, 3) * gain

def boom(dur=3.0):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 38 + 40 * np.exp(-t / 0.12); ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t / 0.9) + lp(rng.standard_normal(n), 200) * np.exp(-t / 0.08) * 0.3)

def reverb(L, R, wet=0.3, rt=2.6):
    n = int(rt * SR); t = np.arange(n) / SR; out = []
    for sig, seed in ((L, 1), (R, 2)):
        ir = np.random.default_rng(seed).standard_normal(n) * np.exp(-t * 6.9 / rt)
        ir = lp(ir, 5000); ir /= np.sqrt(np.sum(ir ** 2))
        out.append(sig * (1 - wet) + fftconvolve(sig, ir)[: len(sig)] * wet * 1.4)
    return out

def phrase(tr, start, notes, beat, gain=0.5, pan=0.15, base=74 - 12):
    t = start
    for d, b in notes:
        if d is not None: tr.add(ney(deg(d, base), b * beat * 1.05), t, gain, pan)
        t += b * beat
    return t

def arp(tr, start, chord, bars, bpm, gain=0.35, pan=-0.25, pattern=(0, 1, 2, 1, 0, 2, 1, 2)):
    step = 60 / bpm / 2; t = start
    for _ in range(bars):
        for i, p in enumerate(pattern):
            if p is not None: tr.add(oud(chord[p] - 12 + (12 if i == 4 else 0), 1.4, 0.5), t, gain * (1.0 if i % 4 == 0 else 0.7), pan)
            t += step
    return t

def daf(tr, start, bars, bpm, gain=0.5, pattern="D.tDt.t."):  # 8 eighths per bar
    step = 60 / bpm / 2; t = start
    for _ in range(bars):
        for c in pattern:
            if c == "D": tr.add(doum(), t, gain, -0.05)
            elif c == "t": tr.add(tek(), t, gain, 0.2)
            t += step

def render(tr, name, wet=0.32, fade=4.0, loud=-18):
    L, R = reverb(tr.L, tr.R, wet)
    n = int(tr.sec * SR); L, R = L[:n], R[:n]
    f = np.ones(n); fi = int(1.5 * SR); fo = int(fade * SR)
    f[:fi] = np.linspace(0, 1, fi); f[-fo:] = np.linspace(1, 0, fo)
    st = np.stack([L * f, R * f], 1); st /= (np.max(np.abs(st)) + 1e-9) / 0.8
    wav = OUT / f"{name}.wav"; wavfile.write(wav, SR, st.astype(np.float32))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", f"loudnorm=I={loud}:TP=-2:LRA=11", "-ar", "44100",
                    "-codec:a", "libmp3lame", "-b:a", "192k", str(OUT / f"{name}.mp3")], check=True)
    wav.unlink(); print(name, f"{tr.sec:.0f}s")

Dm, Bb, Gm, Cm, Eb = (62, 65, 69), (58, 62, 65), (55, 58, 62), (60, 63, 67), (58, 63, 67)

# 1 Opening (S01–S04): wind, low drone, solo ney
tr = Track(62); tr.add(wind(62, 0.45), 0); tr.add(drone([38, 45], 62, 0.9), 0)
phrase(tr, 4, [(4, 3), (5, 1.5), (4, 1.5), (3, 2.5), (2, 2), (3, 1), (4, 4), (None, 2), (4, 1.5), (6, 1.5), (5, 2), (4, 1), (3, 1), (2, 2), (1, 2), (0, 6)], 1.25, 0.55)
tr.add(boom(4), 57, 0.9)
render(tr, "01_opening_S01-S04", wet=0.4)

# 2 His life (S05–S14): strings pad + oud + soft daf, ney phrases
bpm = 72; bar = 60 / bpm * 4
prog = [Dm, Bb, Gm, Dm, Dm, Eb, Cm, Dm]
L2 = 228; tr = Track(L2); t = 0.0; i = 0
while t < L2 - bar:
    ch = prog[i % len(prog)]; tr.add(pad(ch, bar * 2 + 2, 1300), t, 0.55); t += bar * 2; i += 1
arp(tr, bar * 2, Dm, 1, bpm); t = bar * 2
for k in range(int((L2 - bar * 3) // (bar * 2))):
    ch = prog[(k + 1) % len(prog)]; arp(tr, t, ch, 2, bpm, 0.32); t += bar * 2
daf(tr, bar * 8, int((L2 - bar * 10) / bar), bpm, 0.32, "D...t.t.")
for st in (bar * 6, bar * 22, bar * 38, bar * 54):
    if st < L2 - 20: phrase(tr, st, [(4, 1), (5, .5), (4, .5), (3, 1), (2, 1), (3, 2), (None, 1), (2, 1), (1, .5), (2, .5), (0, 3)], 60 / bpm * 2, 0.4)
render(tr, "02_life_S05-S14", wet=0.3)

# 2b Halabja (S15): near silence, low drone + three piano notes
tr = Track(32); tr.add(drone([38], 32, 0.5), 0)
for tt, m in ((3, 62), (10, 65), (18, 63), (25, 62)): tr.add(piano(m, 6), tt, 0.5, 0.1)
render(tr, "03_halabja_S15", wet=0.5, fade=6, loud=-26)

# 3 The big question (S16–S18): sparse piano over drone
tr = Track(58); tr.add(drone([38, 45], 58, 0.6), 0)
notes = [(2, 62), (5.5, 65), (9, 69), (13, 63), (18, 62), (22, 70), (26, 69), (31, 65), (36, 63), (41, 62), (47, 57), (52, 62)]
for tt, m in notes: tr.add(piano(m, 5), tt, 0.55, -0.1 if m % 2 else 0.1)
render(tr, "04_question_S16-S18", wet=0.45, loud=-21)

# 4 Evidence (S19–S26): warm, steady pulse
bpm = 84; bar = 60 / bpm * 4; L4 = 232; tr = Track(L4)
prog = [Dm, Gm, Bb, Cm, Dm, Eb, Cm, Dm]; t = 0.0; i = 0
while t < L4 - bar:
    tr.add(pad(prog[i % 8], bar * 2 + 2, 1600), t, 0.5); t += bar * 2; i += 1
t = bar * 2; k = 0
while t < L4 - bar * 3: arp(tr, t, prog[(k + 1) % 8], 2, bpm, 0.3, pattern=(0, 2, 1, 2, 0, 2, 1, None)); t += bar * 2; k += 1
daf(tr, bar * 4, int((L4 - bar * 6) / bar), bpm, 0.38, "D.tDt.t.")
for st in (bar * 12, bar * 36, bar * 60):
    if st < L4 - 25: phrase(tr, st, [(4, 1), (4, .5), (5, .5), (6, 1), (5, 1), (4, 2), (3, 1), (4, 1), (2, 2), (None, 1), (3, .5), (2, .5), (1, 1), (0, 3)], 60 / bpm * 2, 0.36)
render(tr, "05_evidence_S19-S26", wet=0.28)

# 5 Criticisms (S27–S30): low, neutral, soft heartbeat pulse with gaps
L5 = 165; tr = Track(L5); tr.add(drone([38, 45], L5, 0.55), 0)
t = 4.0
while t < L5 - 6:
    tr.add(doum(0.9), t, 0.35); tr.add(doum(0.6), t + 0.32, 0.25); t += 1.6
    if int(t) % 30 in (0, 1): t += 3.2   # breathing pauses after verdicts
for tt, m in ((8, 62), (20, 63), (36, 62), (52, 58), (70, 62), (88, 63), (104, 62), (122, 58), (140, 62)): tr.add(piano(m, 6), tt, 0.4)
render(tr, "06_criticisms_S27-S30", wet=0.35, loud=-20)

# 6 Ending (S31–S35): warm build, then resolve
bpm = 76; bar = 60 / bpm * 4; L6 = 172; tr = Track(L6)
prog = [Dm, Bb, Cm, Dm, Gm, Eb, Cm, Dm]; t = 0.0; i = 0
while t < L6 - bar:
    tr.add(pad(prog[i % 8], bar * 2 + 2, 1200 + 40 * i), t, 0.45 + 0.02 * min(i, 10)); t += bar * 2; i += 1
t = bar * 4; k = 0
while t < L6 - bar * 6: arp(tr, t, prog[(k + 2) % 8], 2, bpm, 0.26 + 0.01 * k); t += bar * 2; k += 1
daf(tr, bar * 12, int((L6 - bar * 18) / bar), bpm, 0.3, "D...t.t.")
phrase(tr, bar * 8, [(4, 2), (5, 1), (6, 1), (7, 2), (6, 1), (5, 1), (4, 2), (3, 2), (4, 4)], 60 / bpm * 2, 0.4)
phrase(tr, bar * 26, [(7, 2), (6, 1), (5, 1), (4, 2), (3, 1), (2, 1), (1, 2), (0, 6)], 60 / bpm * 2, 0.42)
tr.add(drone([38, 45, 50], 30, 0.7), L6 - 32)
render(tr, "07_ending_S31-S35", wet=0.34, fade=8)

# Stingers
tr = Track(4); tr.add(boom(4), 0.05, 1.0); render(tr, "08_chapter_boom", wet=0.35, fade=1.5, loud=-16)
tr = Track(2.5); tr.add(doum(1.2), 0.05, 0.8); tr.add(tek(0.5), 0.05, 0.6); render(tr, "09_verdict_stamp", wet=0.2, fade=0.8, loud=-16)
