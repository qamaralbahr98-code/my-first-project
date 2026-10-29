"""Score + SFX for the Kurdish-youth explainer, synthesised and laid on the narration timeline.

  python3 -m ky.sound ar      -> build/ar/audio/mix.wav

Act 1 (S01–S10) soft piano + low strings; Act 2 (S11–S22) light pulse; Act 3 (S23–S29) sparse;
S30–S33 warm build, 1 s of silence before 'we are here', then a soft resolve. Music ducked under the voice.
"""
import json
import sys

import numpy as np
from scipy.io import wavfile

from .base import PROJ
from vox import sound as V
from vox.sound import SR, Bus, env, hp, lp, tt

sys.path.insert(0, str(PROJ.parent / "dwin-oil-spill" / "render"))
from oil.sound import rms, pulse_note, hat, kick, low_boom, tick  # noqa: E402

rng = np.random.default_rng(31)
A2 = 110.0


def hz(semi, base=A2):
    return base * 2 ** (semi / 12)


# A minor / C major colour: Am F C G
PROG = [(0, [12, 15, 19]), (-4, [8, 12, 15]), (3, [15, 19, 22]), (-2, [10, 14, 17])]


def score(total, S):
    bus = Bus(total)
    beat = 60 / 84
    bar = 4 * beat
    a2, a3, a4, a5 = S["S11"]["start"], S["S23"]["start"], S["S30"]["start"], S["S33"]["start"]
    here = S["S32"]["start"] + S["S32"]["here"]
    t, k = 0.0, 0
    while t < total - 1:
        root, vo = PROG[k % 4]
        act = 1 if t < a2 else 2 if t < a3 else 3 if t < a4 else 4
        dur = 2 * bar
        if act == 4 and here - 1.3 < t + dur and t < here + 0.2:   # silence before 'we are here'
            t = here + 0.2
            continue
        pd = V.pad([hz(s) for s in vo], dur + 1.0, cut=700 if act in (1, 3) else 1000, trem=0.02)
        g = {1: 0.22, 2: 0.18, 3: 0.14, 4: 0.28}[act]
        bus.put(pd * g * env(len(pd), 0.8, 0.1, 1, 1.0), t, 1.0, -0.1)
        bus.put(V.pad([hz(root - 12)], dur + 1.0, cut=260) * 0.25 * env(int((dur + 1) * SR), 0.6, 0.1, 1, 1.0), t, 1.0)
        if act in (1, 4):          # piano arpeggio
            notes = [vo[0], vo[1], vo[2], vo[1] + 12] if act == 1 else [vo[0] + 12, vo[1] + 12, vo[2] + 12, vo[0] + 24]
            for j in range(8 if act == 4 else 4):
                tn = t + j * (bar / (4 if act == 4 else 2))
                bus.put(V.piano(hz(notes[j % 4]), 2.0) * (0.16 if act == 1 else 0.13), tn, 1.0, 0.2 * ((j % 3) - 1))
        if act == 2:               # light curious pulse
            for e8 in range(16):
                tn = t + e8 * beat / 2
                bus.put(pulse_note(hz(root), 0.22, 520) * 0.18 * (1 if e8 % 2 == 0 else 0.6), tn, 1.0)
                if e8 % 4 == 2:
                    bus.put(hat(0.07), tn, 1.0, 0.3)
        if act == 3:               # sparse: one piano note per bar
            for j in range(2):
                bus.put(V.piano(hz(vo[2] + 12), 2.6) * 0.12, t + j * bar + 0.1, 1.0, 0.3)
        t += dur
        k += 1
    # resolve on the end card
    rdur = total - a5 + 1
    res = V.pad([hz(12), hz(16), hz(19), hz(24)], rdur, cut=1200, trem=0.02)
    bus.put(res * 0.3 * env(len(res), 1.0, 0.2, 1, 3.0), a5, 1.0)
    return bus


def load_parts(lang):
    import subprocess
    out = {}
    for p in sorted((PROJ / "build" / lang / "vo" / "parts").glob("*.wav")):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                             capture_output=True, check=True).stdout
        out[p.stem] = np.frombuffer(raw, np.float32).astype(np.float64)
    return out


def build(lang):
    tl = json.loads((PROJ / "build" / lang / "timeline.json").read_text(encoding="utf-8"))
    scenes, total = tl["scenes"], tl["total"]
    S = {s["id"]: s for s in scenes}
    w32 = [w for w in S["S32"]["words"] if w["text"].startswith(("نحن", "ئێمە", "Em"))]
    S["S32"]["here"] = w32[-1]["s"] if w32 else S["S32"]["dur"] * 0.8
    voice, sfx = Bus(total), Bus(total)
    parts = load_parts(lang)
    for s in scenes:
        for a in s["audio"]:
            voice.put(parts[a["seg"]], s["start"] + a["start"], 1.0, 0.0)

    def put(sig, sid, tc, g=1.0, p=0.0):
        sfx.put(sig, S[sid]["start"] + tc, g, p)

    for s in scenes[1:]:
        if s.get("chapter"):
            put(low_boom(0.8), s["id"], 0.0)
        elif s["id"] not in ("S03", "S33", "END"):
            sfx.put(V.rustle(0.45, 40) * 0.5, s["start"] - 0.02, 0.5, 0.2)
    put(V.swell(1.6) * 0.5, "S01", 0.0)
    w = S["S02"]["words"]
    put(V.stamp_thud() * 0.8, "S02", (w[2]["s"] if len(w) > 2 else 0.6))
    put(V.scribble(1.0, 9) * 0.5, "S02", S["S02"]["dur"] * 0.7)
    for j in range(14):                           # typewriter ticks for the question
        put(V.typekey() * 0.35, "S03", S["S03"]["dur"] * 0.5 + j * 0.07)
    put(V.whoosh(0.8, 300, 3000) * 0.4, "S04", 0.3)
    put(V.whoosh(0.5, 400, 4000) * 0.5, "S10", S["S10"]["dur"] * 0.33)
    for sid in ("S23", "S24", "S25", "S26"):
        put(V.stamp_thud() * 0.7, sid, S[sid]["dur"] * 0.3 + (2.0 if sid == "S23" else 0))
    n = 5
    a0, a1 = S["S19"]["audio"][0]["start"], S["S19"]["audio"][0]["start"] + S["S19"]["audio"][0]["dur"]
    for i in range(n):
        put(V.tick_click(0.5), "S19", a0 + (a1 - a0) * (0.08 + 0.84 * i / n) + 0.1)
    put(V.scribble(1.0, 8) * 0.45, "S14", S["S14"]["dur"] * 0.3)
    for i in range(int(S["S29"]["dur"])):
        put(tick(0.12), "S29", 0.5 + i)
    mus = score(total, S)
    out = PROJ / "build" / lang / "audio"
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "stem_voice.npy", voice.x)
    np.save(out / "stem_sfx.npy", sfx.x)
    np.save(out / "stem_music.npy", mus.x)
    mix(lang)


MUSIC_UNDER_DB, MUSIC_GAP_DB, SFX_DB = -18.0, -12.0, -10.0


def mix(lang):
    out = PROJ / "build" / lang / "audio"
    tl = json.loads((PROJ / "build" / lang / "timeline.json").read_text(encoding="utf-8"))
    end = int(tl["total"] * SR)
    vx = np.load(out / "stem_voice.npy")[:, :end].astype(np.float32)
    v = vx[0].astype(np.float64)
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
    mr = rms(mus[0][mus[0] != 0])
    fr_ = rms(fx[0][np.abs(fx[0]) > 1e-4])
    under = 10 ** (MUSIC_UNDER_DB / 20) * vr / mr
    gap = 10 ** (MUSIC_GAP_DB / 20) * vr / mr
    mg = (gap + (under - gap) * g).astype(np.float32)
    sg = (10 ** (SFX_DB / 20) * vr / fr_) * (1 - 0.35 * g)
    m = vx + mus * mg + fx * sg.astype(np.float32)
    fo = int(1.5 * SR)
    m[:, -fo:] *= np.linspace(1, 0, fo, dtype=np.float32)
    m = m * np.float32(0.8 / float(np.abs(m).max()))
    m = np.tanh(m * np.float32(1.05)) / np.float32(1.05)
    wavfile.write(out / "mix.wav", SR, m.T.astype(np.float32))
    print(f"wrote {out / 'mix.wav'} {tl['total']:.1f}s")


if __name__ == "__main__":
    build(sys.argv[1])
