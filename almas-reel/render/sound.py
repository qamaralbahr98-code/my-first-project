"""Score and sound effects for the Almas reel, following section 4.9 and the per-card sound notes.

Chapters 1-3 tension bed (100 BPM, minor, sub-bass pulse, ticking hi-hat), chapter 4 low drone only,
chapter 5 build to the Article 12 penalty card, chapter 6 near-silence -> piano note -> low strings,
chapters 7-8 warm piano with light percussion, resolving and hard-stopping on the last frame of C24.
"""
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))
from izz_video import music as m                       # noqa: E402  (synth helpers from the first video)

SR = m.SR
rng = np.random.default_rng(11)
NO_SFX = {"C07", "C08", "C11", "C12"}   # fairness: no sound effects on Hariri or the Kurdistan24 speaker


def nt(semi, octave=0, base=73.42):      # D2 = 73.42 Hz
    return base * 2 ** ((semi + 12 * octave) / 12)


def sub_pulse(g=1.0):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    fr = 48 + 40 * np.exp(-t * 25)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 7) * g


def hat(g=1.0):
    n = int(0.05 * SR)
    t = np.arange(n) / SR
    return m.bp(rng.standard_normal(n), 6000, 14000) * np.exp(-t * 90) * g


def shaker(g=1.0):
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    return m.bp(rng.standard_normal(n), 3500, 9000) * np.sin(np.pi * t / t[-1]) ** 2 * g


def soft_kick(g=1.0):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    fr = 60 + 70 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 10) * g


def piano(freq, dur, g=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k, a in enumerate([1.0, 0.45, 0.22, 0.12, 0.06], start=1):
        f = freq * k * (1 + 0.0004 * k * k)
        out += a * np.sin(2 * np.pi * f * t) * np.exp(-t * (1.1 + 0.8 * k))
    hammer = m.lp(rng.standard_normal(n), 2500) * np.exp(-t * 80) * 0.05
    return (out + hammer) * np.minimum(1, t / 0.004) * m.env_adsr(n, 0.004, 0.1, 1, min(0.4, dur / 3)) * g


def impact(g=1.0, low=40):
    n = int(2.2 * SR)
    t = np.arange(n) / SR
    fr = low + 60 * np.exp(-t * 12)
    body = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 2.2)
    thud = m.lp(rng.standard_normal(n), 300) * np.exp(-t * 14) * 0.6
    return (body + thud) * g


def whoosh(dur=0.45, g=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    out = np.zeros(n)
    for i in range(8):                                   # band sweeping upwards
        a, b = int(i * n / 8), int((i + 1) * n / 8)
        lo = 300 + 5000 * (i / 8) ** 1.6
        out[a:b] = m.bp(noise, lo, lo * 2.5)[a:b]
    return out * np.sin(np.pi * t / dur) ** 1.5 * g


def reverse_swell(dur=1.2, g=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return m.bp(rng.standard_normal(n), 3000, 12000) * (t / dur) ** 3 * g


def tick(g=1.0):
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2400 * t) * 0.6 + m.bp(rng.standard_normal(n), 2000, 7000) * 0.4) * np.exp(-t * 160) * g


def shutter(g=1.0):
    out = np.zeros(int(0.16 * SR))
    for t0 in (0.0, 0.07):
        c = m.bp(rng.standard_normal(int(0.04 * SR)), 1500, 8000) * np.exp(-np.arange(int(0.04 * SR)) / SR * 120)
        i = int(t0 * SR)
        out[i:i + len(c)] += c
    return out * g


def swipe(g=1.0):
    return whoosh(0.3, g) * 0.6


# ------------------------------------------------------------------ build
def build(cards, events, total, out_wav):
    N = int(total * SR) + SR
    mus = np.zeros((2, N))
    sfx = np.zeros((2, N))

    def put(buf, sig, t0, g, pan=0.0):
        i = int(t0 * SR)
        if i < 0:
            sig, i = sig[-i:], 0
        j = min(N, i + len(sig))
        if j <= i:
            return
        buf[0, i:j] += sig[: j - i] * g * np.sqrt(0.5 * (1 - pan))
        buf[1, i:j] += sig[: j - i] * g * np.sqrt(0.5 * (1 + pan))

    by = {c["id"]: c for c in cards}
    ch = {}
    for c in cards:
        a, b = ch.get(c["chapter"], (c["start"], c["end"]))
        ch[c["chapter"]] = (min(a, c["start"] - (0.5 if c["flash_before"] else 0)), max(b, c["end"]))
    end_music = by["C24"]["end"]

    # --- chapters 1-3: tension bed
    t0, t1 = 0.0, ch[3][1]
    beat = 60 / 100
    prog = [0, -4, -2, -5]                     # D minor: i - VI - VII - v (in semitones from D)
    k, t = 0, t0
    c05 = by["C05"]
    while t < t1:
        in05 = c05["start"] <= t < c05["end"]
        put(mus, sub_pulse(), t, 0.55)
        if not in05:
            for s in range(4):
                put(mus, hat(), t + s * beat / 4, 0.10 if s % 2 else 0.05, 0.3)
        if k % 16 == 0 and t + 16 * beat <= t1 + 16 * beat:
            root = prog[(k // 16) % 4]
            dur = min(16 * beat, t1 - t + 0.5)
            p = m.pad([nt(root, -1), nt(root + 7, -1), nt(root + 3, 0)], dur, cut=700, detune=0.003)
            p *= m.env_adsr(len(p), 1.5, 0.1, 1, 1.5)
            # pad drops out under C05 ("pulse only")
            gate = np.ones(len(p))
            a, b = int((c05["start"] - t) * SR), int((c05["end"] - t) * SR)
            if b > 0 and a < len(p):
                a, b = max(0, a), min(len(p), b)
                gate[a:b] = 0.0
                f = int(0.3 * SR)
                if a - f > 0:
                    gate[a - f:a] = np.linspace(1, 0, f)
                if b + f < len(p):
                    gate[b:b + f] = np.linspace(0, 1, f)
            put(mus, p * gate, t, 0.30)
        t += beat
        k += 1
    # C07: light street ambience; C08: music ducks 4 dB
    c7 = by["C07"]
    amb = m.lp(rng.standard_normal(int((c7["end"] - c7["start"]) * SR)), 900)
    put(mus, amb * m.env_adsr(len(amb), 0.6, .1, 1, 0.6), c7["start"], 0.05)
    c8 = by["C08"]
    a, b = int(c8["start"] * SR), int(c8["end"] * SR)
    mus[:, a:b] *= 10 ** (-4 / 20)

    # --- chapter 4: low drone only (quieter: music -24 dB under the quote cards)
    a4, b4 = ch[4]
    dr = m.pad([nt(0, -1), nt(7, -1)], b4 - a4 + 0.6, cut=380, detune=0.002)
    put(mus, dr * m.env_adsr(len(dr), 0.8, .1, 1, 0.8), a4, 0.16)

    # --- chapter 5: pulse returns and builds; peak on the Article 12 penalty card (C16)
    a5, b5 = ch[5]
    c16 = by["C16"]
    peak = c16["start"] + (2 + 10 * (c16["highlight"] or 0)) / 30
    t, k = a5 + 0.5, 0
    while t < b5:
        u = min(1.0, (t - a5) / max(0.1, peak - a5))
        put(mus, sub_pulse(), t, 0.35 + 0.35 * u)
        if u > 0.35:
            for s in range(4):
                put(mus, hat(), t + s * beat / 4, (0.04 + 0.08 * u) * (1 if s % 2 else 0.6), 0.3)
        t += beat
        k += 1
    rise = m.pad([nt(0, -1), nt(3, 0), nt(7, 0), nt(10, 0)], b5 - a5, cut=500, detune=0.004)
    ramp = np.clip(np.linspace(0, 1, len(rise)) * (b5 - a5) / max(0.1, peak - a5), 0, 1) ** 1.5
    put(mus, rise * (0.25 + 0.75 * ramp) * m.env_adsr(len(rise), 1, .1, 1, 0.4), a5, 0.30)
    put(sfx, impact(1.0, 34), peak, 0.95)

    # --- chapter 6: near-silence, one low piano note, firm low strings, deep hit on the last word
    c17, c18, c19 = by["C17"], by["C18"], by["C19"]
    put(mus, piano(nt(0, -1), 4.0), c17["start"] + 0.1, 0.55)
    sw = m.pad([nt(0, -1), nt(7, -1), nt(3, 0)], c19["end"] - c18["start"], cut=600, detune=0.003)
    env = np.minimum(1, np.arange(len(sw)) / SR / 2.5) * m.env_adsr(len(sw), 0.01, .1, 1, 0.6)
    put(mus, sw * env, c18["start"], 0.40)
    last_word = c19["start"] + (2 + 10 * (len(c19["lines"]) - 1) + 10) / 30
    put(sfx, impact(0.9, 38), last_word, 0.8)

    # --- chapters 7-8: warm piano with light percussion; resolve and hard-stop at the end of C24
    a7 = by["C20"]["start"] - 0.2
    pb = 60 / 84
    chords = [[0, 4, 7], [7, 11, 14], [9, 12, 16], [5, 9, 12]]   # D - A - Bm - G
    t, k = a7, 0
    c23 = by["C23"]
    while t < end_music - 2 * pb:
        chd = chords[(k // 4) % 4]
        lift = 1.25 if c23["start"] <= t < c23["end"] else 1.0
        if k % 4 == 0:
            for j, s in enumerate(chd):
                put(mus, piano(nt(s, 1), 3.2), t + j * 0.012, 0.16 * lift, -0.2 + 0.2 * j)
            put(mus, piano(nt(chd[0], 0), 3.2), t, 0.20 * lift)
        put(mus, piano(nt(chd[k % 3], 2), 0.9), t + pb / 2, 0.06 * lift, 0.3)
        if k % 2 == 0:
            put(mus, soft_kick(), t, 0.22 * lift)
        put(mus, shaker(), t + pb / 2, 0.05 * lift, -0.3)
        t += pb
        k += 1
    for j, s in enumerate([0, 4, 7, 12]):                 # final D major chord, held to the end of C24
        put(mus, piano(nt(s, 1), end_music - t + 0.5), t + j * 0.015, 0.18)
    put(mus, piano(nt(0, 0), end_music - t + 0.5), t, 0.24)
    stop = int(end_music * SR)                            # hard stop on the last frame of C24
    fade = int(0.012 * SR)
    mus[:, stop - fade:stop] *= np.linspace(1, 0, fade)
    mus[:, stop:] = 0

    # --- sound effects
    for (tt, kind, cid) in events:
        if kind == "flash":
            put(sfx, whoosh(0.45), tt, 0.5)
            if cid != "C20":                               # C20: whoosh only
                put(sfx, impact(0.7, 45), tt + 0.25, 0.55)
        elif kind == "tick" and cid not in NO_SFX and by[cid]["style"] == "A":
            put(sfx, tick(), tt, 0.22, 0.2)
    put(sfx, sub_pulse(1.3), 1 / 30, 0.8)                                  # C01 sub hit on frame 1
    put(sfx, reverse_swell(1.2), by["C02"]["start"] - 1.2, 0.25)          # C02 reverse cymbal into the card
    c3 = by["C03"]
    put(sfx, impact(0.6, 55), c3["start"] + (2 + 10 * (c3["highlight"] or 0)) / 30, 0.45)
    c10 = by["C10"]
    hl = c10["highlight"] or 0
    t10 = c10["start"] + (2 + sum(2 + 4 * len(l.split()) for l in c10["lines"][:hl])) / 30
    put(sfx, impact(0.5, 60), t10, 0.30)
    put(sfx, swipe(), by["C21"]["start"] + 0.6, 0.5)
    c22 = by["C22"]
    put(sfx, shutter(), (c22["start"] + c22["end"]) / 2, 0.45)

    mix = m.reverb(mus[0], mus[1], seconds=2.2, mix=0.22)
    out = np.stack([mix[0][:N] + sfx[0], mix[1][:N] + sfx[1]])
    out[:, stop:] = sfx[:, stop:]                         # keep the hard stop (no reverb tail)
    out = out[:, : int(total * SR)]
    out = out / (np.max(np.abs(out)) or 1) * 0.9
    with wave.open(str(out_wav), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((out.T * 32767).astype(np.int16).tobytes())
    return out_wav


def master(in_wav, out_m4a):
    """Loudness to -14 LUFS integrated, true peak <= -1 dBTP, AAC 48 kHz 256 kbps."""
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(in_wav),
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000", "-c:a", "aac", "-b:a", "256k",
                    str(out_m4a)], check=True)
    return out_m4a
