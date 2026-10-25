"""Score + sound design for the oil-spill explainer, synthesised from scratch and laid on the narration timeline.

  python3 -m oil.sound ckb      -> build/ckb/audio/mix.wav  (narration + ducked underscore + SFX; loudness pass in finish)

Music: tense minimal news underscore, 96 BPM, low synth pulse, D minor, no vocals; about -20 dB under the narration,
a little higher in the gaps; it resolves on the last scene. SFX follow the brief (waves, pin pops, ticks, low booms,
seagulls far away, satellite beep, ship horn); no explosion sounds.
"""
import json
import sys

import numpy as np
from scipy.io import wavfile

from . import base as B
from .base import PROJ
from vox import sound as V          # instruments and DSP helpers of the Sheikh Said project
from vox.sound import SR, Bus, bp, env, expd, hp, lp, tt

rng = np.random.default_rng(23)
BPM = 96
BEAT = 60 / BPM
D2 = 73.42


def hz(semi, base=D2):
    return base * 2 ** (semi / 12)


# ------------------------------------------------------------------ instruments
def pulse_note(freq, dur=0.26, cut=520):
    t = tt(dur)
    ph = (freq * t) % 1.0
    saw = 2 * ph - 1
    sub = np.sin(2 * np.pi * freq / 2 * t)
    x = lp(saw, cut, 2) * 0.55 + sub * 0.5
    return x * np.exp(-t * 9) * env(len(t), 0.004, 0.02, 1, 0.04)


def hat(g=0.25):
    t = tt(0.05)
    return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t * 140) * g


def kick(g=0.6):
    t = tt(0.4)
    fr = 48 + 70 * np.exp(-t * 35)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 9) * g


def low_boom(g=1.0):
    """Deep sub hit (not an explosion: no noise burst, no debris)."""
    t = tt(2.6)
    fr = 34 + 22 * np.exp(-t * 5)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 1.5) * env(len(t), 0.01, 0.1, 1, 0.6) * g


def waves(dur, period=6.5, seed=0):
    r = np.random.default_rng(seed)
    n = int(dur * SR)
    t = np.arange(n) / SR
    ph = r.random() * 6
    swell = np.clip(np.sin(2 * np.pi * t / period + ph), 0, None) ** 2.2
    wash = np.clip(np.sin(2 * np.pi * t / period + ph - 0.7), 0, None) ** 3
    body = lp(r.standard_normal(n), 650) * (0.25 + 0.9 * swell)
    hiss = bp(r.standard_normal(n), 1800, 7000) * wash * 0.35
    st = np.stack([body + hiss * 0.9, lp(r.standard_normal(n), 650) * (0.25 + 0.9 * swell) + hiss])
    return st * env(n, 0.8, 0.1, 1, 1.2)[None, :] * 0.5


def seagull(g=0.3):
    out = []
    for k in range(int(rng.integers(2, 4))):
        d = rng.uniform(0.22, 0.38)
        t = tt(d)
        fr = 1500 + 700 * np.sin(np.pi * t / d) - 500 * t / d + 40 * np.sin(2 * np.pi * 28 * t)
        ph = 2 * np.pi * np.cumsum(fr) / SR
        s = (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)) * np.sin(np.pi * t / d) ** 1.5
        out.append(bp(s, 900, 5000))
        out.append(np.zeros(int(rng.uniform(0.05, 0.15) * SR)))
    return np.concatenate(out) * g


def shovel(g=0.5):
    t = tt(0.55)
    scrape = bp(rng.standard_normal(len(t)), 900, 5000) * (np.sin(np.pi * t / 0.55) ** 2)
    thump = lp(rng.standard_normal(len(t)), 300) * np.exp(-t * 18) * 0.6
    return (scrape * 0.6 + thump) * g


def traffic(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    m = 0.7 + 0.3 * np.sin(2 * np.pi * 0.09 * t + 1.3)
    return lp(rng.standard_normal(n), 220) * m * env(n, 1.0, 0.1, 1, 1.0) * 0.6


def horn(dur=2.8, freq=58):
    t = tt(dur)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 4.5 * t)
    ph = 2 * np.pi * np.cumsum(freq * vib) / SR
    x = sum(np.sin(k * ph) / k for k in range(1, 9))
    x = lp(x, 600, 2) * env(len(t), 0.4, 0.3, 0.85, 1.0)
    return x


def drone(dur, freq=D2 / 2):
    t = tt(dur)
    x = np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(2 * np.pi * freq * 2.003 * t) + 0.15 * np.sin(2 * np.pi * freq * 3 * t)
    return x * env(len(t), 1.5, 0.1, 1, 1.5) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.2 * t))


def beep(freq=1850, g=0.25):
    out = np.zeros(int(0.5 * SR))
    for at in (0.0, 0.16):
        t = tt(0.07)
        b = np.sin(2 * np.pi * freq * t) * env(len(t), 0.003, 0.01, 1, 0.02)
        i = int(at * SR)
        out[i:i + len(b)] += b
    return out * g


def blip(g=0.3):
    t = tt(0.25)
    return np.sin(2 * np.pi * (420 - 120 * t / 0.25) * t) * np.exp(-t * 16) * g


def underwater(dur):
    n = int(dur * SR)
    x = lp(rng.standard_normal(n), 380) * 0.8
    for _ in range(int(dur * 3)):
        d = rng.uniform(0.03, 0.08)
        t = tt(d)
        fr = rng.uniform(500, 1400) * (1 + 2 * t / d)
        b = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(np.pi * t / d) * 0.15
        i = int(rng.uniform(0, dur - d) * SR)
        x[i:i + len(b)] += b
    return x * env(n, 0.6, 0.1, 1, 0.8)


def tick(g=0.5):
    return V.tick_click(g, 2500, 7500, 320)


# ------------------------------------------------------------------ score
# chord roots (semitones above D) and pad voicings per 4 bars: Dm - Bb - Gm - A(sus4)
PROG = [(0, [0, 3, 7, 14]), (-4, [-4, 0, 3, 10]), (5, [5, 8, 12, 15]), (7, [7, 12, 14, 19])]


def score(total, S):
    """Underscore bus (stereo) and an intensity curve. S: scene dict."""
    bus = Bus(total)
    bar = 4 * BEAT
    t_main = S["S02"]["start"] - 0.2
    t_hi = S["S10"]["start"]
    t_end = S["S14"]["start"]
    end = total
    # intro (S01): boom + held pad, no pulse yet
    bus.put(V.pad([hz(12), hz(15), hz(19)], t_main + 1.0, cut=700, trem=0.02) * 0.32, 0.0, 1.0)
    # main groove
    t = t_main
    k = 0
    while t < t_end - 0.01:
        root, vo = PROG[(k // 4) % 4]
        if k % 4 == 0:
            dur = min(4 * bar, t_end - t) + 1.2
            pd = V.pad([hz(12 + s) for s in vo], dur, cut=850 if t < t_hi else 1300, trem=0.025)
            bus.put(pd * 0.26 * env(len(pd), 0.6, 0.1, 1, 1.0), t, 1.0, -0.15)
        hi = t >= t_hi
        for e8 in range(8):                           # 8th-note bass pulse
            tn = t + e8 * BEAT / 2
            if tn >= t_end:
                break
            acc = 1.0 if e8 % 2 == 0 else 0.62
            bus.put(pulse_note(hz(root), 0.26, 620 if hi else 480) * 0.42 * acc, tn, 1.0, 0.0)
            if hi and e8 % 2 == 1:
                bus.put(pulse_note(hz(root + 12), 0.18, 900) * 0.16, tn, 1.0, 0.25)
        for s16 in range(16):                         # clock-like hats
            tn = t + s16 * BEAT / 4
            if tn >= t_end:
                break
            g = (0.16 if s16 % 4 == 2 else 0.07) * (1.3 if hi else 1.0)
            bus.put(hat(g), tn, 1.0, 0.35)
        for b4 in (0, 2):                             # soft kick on 1 and 3
            tn = t + b4 * BEAT
            if tn < t_end:
                bus.put(kick(0.5 if hi else 0.38), tn, 1.0, 0.0)
        t += bar
        k += 1
    # resolution (S14 + end card): D major, pulse dissolves
    rdur = end - t_end + 1.0
    res = V.pad([hz(12), hz(16), hz(19), hz(24)], rdur, cut=1100, trem=0.02)
    bus.put(res * 0.32 * env(len(res), 0.8, 0.2, 1, 3.0), t_end - 0.3, 1.0)
    bus.put(V.pad([hz(0), hz(7)], rdur, cut=300) * 0.3 * env(int(rdur * SR), 0.5, 0.2, 1, 3.0), t_end - 0.3, 1.0)
    for j in range(6):                                # last pulses fade out
        tn = t_end + j * BEAT / 2
        bus.put(pulse_note(hz(0), 0.26, 420) * 0.4 * (1 - j / 6), tn, 1.0)
    return bus


# ------------------------------------------------------------------ build
def ctx(sc, lang):
    return B.Ctx(sc, lang, (1920, 1080), {}, {})


def build(lang):
    tl = json.loads((PROJ / "build" / lang / "timeline.json").read_text(encoding="utf-8"))
    scenes = tl["scenes"]
    total = tl["total"]
    S = {s["id"]: s for s in scenes}
    C = {s["id"]: ctx(s, lang) for s in scenes}
    voice, sfx = Bus(total), Bus(total)
    parts = load_parts(lang)
    for s in scenes:
        for a in s["audio"]:
            voice.put(parts[a["seg"]], s["start"] + a["start"], 1.0, 0.0)

    def at(sid, tc):
        return S[sid]["start"] + tc

    def put(sig, sid, tc, g=1.0, p=0.0):
        sfx.put(sig, at(sid, tc), g, p)

    # transitions: paper slide between scenes
    for s in scenes[1:]:
        if s["id"] != "END":
            sfx.put(V.rustle(0.45, 40) * 0.5, s["start"] - 0.02, 0.5, 0.2 if lang == "ckb" else -0.2)
    # S01 hook: low boom on the cut, waves, a gull far away, whoosh for the title
    c = C["S01"]
    put(low_boom(0.9), "S01", 0.05)
    put(waves(S["S01"]["dur"] + 0.6, seed=1), "S01", 0.0, 0.55)
    put(seagull(0.10), "S01", 3.6, 1.0, 0.6)
    put(V.whoosh(0.7, 400, 3000) * 0.5, "S01", c.a1 - 0.25)
    # S02: card slides in, map, pin pop
    c = C["S02"]
    put(V.rustle(0.6, 50) * 0.6, "S02", 0.25)
    put(V.whoosh(0.5, 300, 2500) * 0.4, "S02", c.at("ڕژانی", "rijandina") - 0.3)
    put(V.pop() * 0.6, "S02", c.at("گەیشتۆتە", "gihîştiye") + 0.05)
    # S03: wind, distant traffic, three pin pops
    c = C["S03"]
    put(V.wind(S["S03"]["dur"] + 0.5, 700, 0.6) * 0.35, "S03", 0.0, 1.0, -0.2)
    put(traffic(S["S03"]["dur"] + 0.5) * 0.5, "S03", 0.0, 1.0, 0.2)
    for w, p in (("شارقە", "Şarîqe"), ("عەجمان", "Ecman"), ("ئوم", "Ummulqeywîn")):
        put(V.pop() * 0.5, "S03", c.at(w, p) + 0.05, 1.0, 0.3)
    # S04: one soft stamp per closure + map pin pops
    c = C["S04"]
    for w, p in (("ئوم", "Ummulqeywîn"), ("حەمرییە", "Hemriye"), ("ڕەئس", "Rasulxeyme")):
        t0 = c.at(w, p)
        put(V.pop() * 0.45, "S04", t0 + 0.05)
        put(V.stamp_thud() * 0.55, "S04", t0 + 0.32)
    # S05: waves, shovels on sand, gulls far away
    put(waves(S["S05"]["dur"] + 0.6, seed=5), "S05", 0.0, 0.55)
    for k in range(6):
        put(shovel(0.35), "S05", 0.9 + k * 1.55 + rng.uniform(-0.2, 0.2), 1.0, rng.uniform(-0.5, 0.5))
    put(seagull(0.09), "S05", 2.5, 1.0, -0.6)
    put(seagull(0.07), "S05", 7.4, 1.0, 0.5)
    # S06: counter ticks with the growing slick, low swell, dashed line
    c = C["S06"]
    t160 = c.at("160", "160")
    g0, g1 = 0.5, t160 + 1.4
    n = 0
    for k in range(60):
        u = (k / 59)
        tk = g0 + (g1 - g0) * np.sqrt(u)
        put(tick(0.35), "S06", tk, 1.0, 0.1)
        n += 1
    put(V.swell(1.6) * 0.45, "S06", g1 - 1.5)
    put(low_boom(0.35), "S06", g1)
    put(V.scribble(0.9, 10) * 0.6, "S06", c.at("25", "25"))
    for k in range(10):                               # pitches filling in
        put(tick(0.18), "S06", c.at("واتە", "ango") + k * 0.12, 1.0, -0.2)
    # S07: ship horn far away, low drone, card
    c = C["S07"]
    put(drone(S["S07"]["dur"] + 0.6) * 0.32, "S07", 0.0)
    put(V.verb(V.pan(horn(3.2), -0.3), V.IR_HALL, 0.5) * 0.28, "S07", 0.6)
    put(V.rustle(0.5, 40) * 0.5, "S07", c.at("«جێم", "«Gem") - 0.35)
    put(V.pop() * 0.4, "S07", c.at("پاناما", "Panamayê"))
    # S08: satellite beep, whoosh with the scan
    c = C["S08"]
    ts = c.at("کۆپەرنیکۆس", "Copernicus")
    put(beep(1850, 0.22), "S08", ts - 0.3, 1.0, 0.2)
    put(V.whoosh(2.2, 600, 5000) * 0.35, "S08", ts - 0.6)
    # S09: water at the mangroves, then underwater ambience
    c = C["S09"]
    tB = c.at("بەردە", "zinarên") - 0.25
    put(waves(tB + 0.8, period=4.5, seed=9) * 0.5, "S09", 0.0)
    put(underwater(S["S09"]["dur"] - tB + 0.6) * 0.5, "S09", tB)
    # S10: map whoosh on the zoom out, low pulse, soft blips for the markers
    c = C["S10"]
    put(V.whoosh(3.4, 200, 2500) * 0.6, "S10", 0.2)
    put(low_boom(0.4), "S10", 3.6)
    tp = c.at("کەشتییەکان", "keştî")
    for i in range(len(B.PULSES)):
        put(blip(0.22), "S10", tp + i * 0.22, 1.0, rng.uniform(-0.6, 0.6))
    # S11: 28 ticks, low boom on 28
    c = C["S11"]
    t28 = c.at("28", "28")
    for i in range(28):
        put(tick(0.4), "S11", t28 + i / 28 * 1.7, 1.0, (i % 7 - 3) / 6)
    put(low_boom(0.85), "S11", t28 + 1.72)
    # S12: eleven soft ticks
    c = C["S12"]
    t11 = c.at("11", "11")
    for i in range(11):
        put(tick(0.4), "S12", t11 + i * 0.14 + 0.05, 1.0, (i - 5) / 7)
    # S13: ticks for the red ships, low swell
    c = C["S13"]
    t30 = c.at("30", "30")
    for j in range(31):
        put(tick(0.25), "S13", t30 + j * 0.065, 1.0, rng.uniform(-0.6, 0.6))
    put(V.swell(1.8) * 0.4, "S13", c.at("3.5", "3.5") - 0.4)
    # S14: last wave
    put(waves(S["S14"]["dur"] + 2.0, period=7.5, seed=14), "S14", 0.0, 0.6)
    put(seagull(0.07), "S14", 5.0, 1.0, 0.5)
    mus = score(total, S)
    out = PROJ / "build" / lang / "audio"
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "stem_voice.npy", voice.x)
    np.save(out / "stem_sfx.npy", sfx.x)
    np.save(out / "stem_music.npy", mus.x)
    mix(lang)


def load_parts(lang):
    import subprocess
    out = {}
    d = PROJ / "build" / lang / "vo" / "parts"
    for p in sorted(d.glob("*.wav")):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                             capture_output=True, check=True).stdout
        out[p.stem] = np.frombuffer(raw, np.float32).astype(np.float64)
    return out


def rms(x):
    return float(np.sqrt(np.mean(x.astype(np.float64) ** 2)) + 1e-12)


MUSIC_UNDER_DB = -20.0      # under the narration
MUSIC_GAP_DB = -12.0        # in the pauses
SFX_DB = -9.0               # SFX bus relative to the voice


def mix(lang):
    out = PROJ / "build" / lang / "audio"
    tl = json.loads((PROJ / "build" / lang / "timeline.json").read_text(encoding="utf-8"))
    end = int(tl["total"] * SR)
    vx = np.load(out / "stem_voice.npy")[:, :end].astype(np.float32)
    v = vx[0].astype(np.float64)
    # voice activity envelope (0..1), fast attack, slow release
    e = np.sqrt(np.maximum(lp(v ** 2, 6), 0.0))
    active = e > (np.percentile(e[e > 1e-5], 50) * 0.25)
    vr = rms(v[active])
    es = active[::64].astype(np.float64)
    att, rel_ = np.exp(-1 / (0.04 * SR / 64)), np.exp(-1 / (0.7 * SR / 64))
    g = np.zeros_like(es)
    acc = 0.0
    for i, x in enumerate(es):
        acc = att * acc + (1 - att) * x if x > acc else rel_ * acc + (1 - rel_) * x
        g[i] = acc
    g = np.interp(np.arange(end), np.arange(len(g)) * 64, g).astype(np.float32)
    mus = np.load(out / "stem_music.npy")[:, :end].astype(np.float32)
    fx = np.load(out / "stem_sfx.npy")[:, :end].astype(np.float32)
    mr = rms(mus[0][mus[0] != 0]) if np.any(mus[0]) else 1.0
    fr_ = rms(fx[0][np.abs(fx[0]) > 1e-4]) if np.any(fx[0]) else 1.0
    under = 10 ** (MUSIC_UNDER_DB / 20) * vr / mr
    gap = 10 ** (MUSIC_GAP_DB / 20) * vr / mr
    mg = (gap + (under - gap) * g).astype(np.float32)
    sg = (10 ** (SFX_DB / 20) * vr / fr_) * (1 - 0.35 * g)
    m = vx + mus * mg + fx * sg.astype(np.float32)
    fo = int(1.2 * SR)
    m[:, -fo:] *= np.linspace(1, 0, fo, dtype=np.float32)
    pk = float(np.abs(m).max())
    m = m * np.float32(0.8 / pk)
    m = np.tanh(m * np.float32(1.05)) / np.float32(1.05)
    assert np.isfinite(m).all()
    wavfile.write(out / "mix.wav", SR, m.T.astype(np.float32))
    sp = active[:end]
    print(f"wrote {out / 'mix.wav'}  {tl['total']:.1f}s  music under voice "
          f"{20 * np.log10(rms((mus * mg)[0][sp]) / rms(vx[0][sp])):.1f} dB")


if __name__ == "__main__":
    if "--mix" in sys.argv:
        mix(sys.argv[1])
    else:
        build(sys.argv[1])
