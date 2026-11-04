"""Sound for the documentary: narration, the original clips' own sound, the supplied music cues, SFX.

  python3 -m so.sound ar      -> build/ar/audio/mix.wav

Music (assets/music/MUSIC.md): one cue per section, cross-faded 2 s, ducked -18 dB under the voice; chapter boom on
every chapter card, the soft stamp on every verdict. No music in the Qur'an and prayer moments (S09's Qur'an shot,
S25), none under the sheikh's own lecture (R10), and 1 s of silence before the last sentence of S34.
Clips keep their original sound: R01 at -22 dB under S02, at full level for the first 7 s of S33 then -20 dB;
R10 at full level.
"""
import json
import subprocess
import sys

import numpy as np
from scipy.io import wavfile

from .base import PROJ
from .timeline import CHAPTER_PRE
from vox import sound as V
from vox.sound import SR, Bus, env, hp, lp, bp

rng = np.random.default_rng(31)
MUS = PROJ / "assets" / "music"
CUES = [("01_opening_S01-S04.mp3", "S01", "S05"), ("02_life_S05-S14.mp3", "S05", "S15"),
        ("03_halabja_S15.mp3", "S15", "S16"), ("04_question_S16-S18.mp3", "S16", "S19"),
        ("05_evidence_S19-S26.mp3", "S19", "S27"), ("06_criticisms_S27-S30.mp3", "S27", "S31"),
        ("07_ending_S31-S35.mp3", "S31", None)]
BOOM_01 = 56.9                     # the low boom inside cue 01 lands on the title card (S04)


def load(path, a=None, b=None):
    cmd = ["ffmpeg", "-v", "error"]
    if a is not None:
        cmd += ["-ss", str(a)]
    if b is not None:
        cmd += ["-t", str(b - (a or 0))]
    cmd += ["-i", str(path), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).T.astype(np.float64)


def mono_best(x):
    """Some archive clips carry the sound in one channel only: keep the stronger channel, centred."""
    k = int(np.argmax([rms(x[0]), rms(x[1])]))
    if rms(x[1 - k]) < 0.5 * rms(x[k]):
        return np.vstack([x[k], x[k]]) * 0.7071
    return x


def rms(x):
    x = x[np.abs(x) > 1e-4] if np.any(np.abs(x) > 1e-4) else x
    return float(np.sqrt(np.mean(x ** 2) + 1e-12))


def fades(x, a=0.02, b=0.02):
    x = x.copy()
    na, nb = int(a * SR), int(b * SR)
    if na:
        x[..., :na] *= np.linspace(0, 1, na)
    if nb:
        x[..., -nb:] *= np.linspace(1, 0, nb)
    return x


def build(lang):
    tl = json.loads((PROJ / "build" / lang / "timeline.json").read_text(encoding="utf-8"))
    scenes, total = tl["scenes"], tl["total"]
    S = {s["id"]: s for s in scenes}
    voice, clips, sfx, mus = Bus(total), Bus(total), Bus(total), Bus(total)
    parts = {}
    for s in scenes:
        for a in s["audio"]:
            if a["seg"] not in parts:
                parts[a["seg"]] = load(PROJ / "build" / lang / "vo" / "parts" / f"{a['seg']}.wav")[0]
            x = parts[a["seg"]]
            i0, i1 = int(a.get("src", 0) * SR), int((a.get("src", 0) + a["dur"]) * SR)
            voice.put(fades(x[i0:i1], 0.01, 0.03), s["start"] + a["start"], 1.0, 0.0)
    vr = rms(voice.x[0])

    # ---- the clips' own sound
    r01 = mono_best(load(PROJ / "assets" / "R01_funeral_1999.mp4"))
    r01 *= vr / rms(r01)
    g22, g20 = 10 ** (-22 / 20), 10 ** (-20 / 20)
    s2 = S["S02"]
    seg = r01[:, int(0.5 * SR):int(min(r01.shape[1] / SR, 0.5 + s2["dur"] * 0.6) * SR)]
    clips.put(fades(seg, 0.6, 1.5) * g22, s2["start"])
    s33 = S["S33"]
    o0, o1 = s33.get("clip_open", [CHAPTER_PRE, CHAPTER_PRE + 7.0])
    g = np.ones(r01.shape[1])
    k0, k1 = int((o1 - o0) * SR), int((o1 - o0 + 0.8) * SR)
    g[k0:k1] = np.linspace(1, g20, k1 - k0)
    g[k1:] = g20
    clips.put(fades(r01 * g, 0.3, 2.0), s33["start"] + o0)
    r = S["R10"]
    a, b = r["clip"]
    r10 = mono_best(load(PROJ / "assets" / "R10_lecture_prophet.mp4", a, b))
    r10 *= vr / rms(r10) * 1.12            # the sheikh's own voice, at full level
    clips.put(fades(r10, 0.4, 0.6), r["start"] + 0.4)

    # ---- music: one cue per section
    ids = [s["id"] for s in scenes]
    for name, a_id, b_id in CUES:
        t0 = S[a_id]["start"]
        t1 = S[b_id]["start"] if b_id else total
        x = load(MUS / name)
        L = x.shape[1] / SR
        off = 0.0
        if name.startswith("01"):
            off = max(0.0, BOOM_01 - (S["S04"]["start"] - t0))
        if name.startswith("07"):
            off = max(0.0, L - (t1 - t0) - 0.5)          # resolve on the end card
        need = (t1 - t0) + 2.0
        seg = x[:, int(off * SR):]
        while seg.shape[1] / SR < need:                     # loop with a cross-fade when a cue is short
            n = int(2.0 * SR)
            tail = seg[:, -n:] * np.linspace(1, 0, n)
            head = x[:, :n] * np.linspace(0, 1, n)
            seg = np.concatenate([seg[:, :-n], tail + head, x[:, n:]], axis=1)
        seg = seg[:, :int(need * SR)]
        seg = fades(seg, 0.0 if name.startswith("01") and off == 0 else 2.0, 2.0)
        mus.put(seg, t0 - (1.0 if a_id != "S01" else 0.0))
    # gates: Qur'an and prayer moments, the lecture, the silence in S34, a pause after each verdict
    gate = np.ones(mus.n)

    def hole(t_a, t_b, depth=0.0, ramp=0.8):
        ia, ib = int(t_a * SR), int(t_b * SR)
        ra = int(ramp * SR)
        gate[ia:ib] = np.minimum(gate[ia:ib], depth)
        if ia - ra > 0:
            gate[ia - ra:ia] = np.minimum(gate[ia - ra:ia], np.linspace(1, depth, ra))
        gate[ib:ib + ra] = np.minimum(gate[ib:ib + ra], np.linspace(depth, 1, ra))
    s9 = S["S09"]
    hole(s9["start"] + s9["dur"] * 0.30, s9["start"] + s9["dur"] * 0.78, 0.0, 1.0)
    s25 = S["S25"]
    hole(s25["start"] + 0.2, s25["start"] + s25["dur"] - 0.2, 0.0, 1.2)
    hole(r["start"] - 0.3, r["start"] + r["dur"] + 0.3, 0.0, 1.2)
    s34 = S["S34"]
    if len(s34["audio"]) > 1:
        a1 = s34["audio"][0]
        hole(s34["start"] + a1["start"] + a1["dur"], s34["audio"][1]["start"] + s34["start"], 0.0, 0.25)
    for sid in ("S27", "S28", "S28b", "S29", "S30"):
        tv = S[sid]["start"] + S[sid].get("verdict_t", 2.0)
        hole(tv + 0.2, tv + 1.4, 0.25, 0.3)
    mus.x *= gate[None, :].astype(np.float32)

    # ---- chapter boom and verdict stamp (supplied), SFX
    boom = load(MUS / "08_chapter_boom.mp3")
    stamp = load(MUS / "09_verdict_stamp.mp3")
    for s in scenes:
        if s.get("chapter"):
            sfx.put(boom * 1.2, s["start"])
    for sid in ("S27", "S28", "S28b", "S29", "S30"):
        sfx.put(stamp * 1.1, S[sid]["start"] + S[sid].get("verdict_t", 2.0))
    hard = {"S03", "S05", "S16", "S19", "S27", "S31", "S33", "R10", "END", "S15", "S24", "S34", "S35", "S04"}
    for s in scenes[1:]:
        if s["id"] not in hard:
            sfx.put(V.rustle(0.45, 40) * 0.45, s["start"] - 0.02, 1.0, 0.2)

    def at(sid, word_ar, word_ckb, default=0.5):
        s = S[sid]
        key = word_ar if lang == "ar" else word_ckb
        for w in s["words"]:
            if key in w["text"]:
                return s["start"] + w["s"]
        return s["start"] + s["dur"] * default
    sfx.put(V.wind(S["S01"]["dur"] + 1, 420, 0.5) * 0.30, 0.0)
    sfx.put(V.unlock() * 0.7, at("S07", "مفاتيح", "کلیلی", 0.7))
    for j in range(5):
        sfx.put(V.rustle(0.25, 30) * 0.35, at("S08", "كتب", "کتێبەکانی", 0.5) + j * 0.35)
    s14 = S["S14"]
    sfx.put(V.wind(s14["dur"] * 0.45, 600, 0.6) * 0.35, s14["start"])
    s16 = S["S16"]
    sfx.put(V.wind(s16["dur"], 500, 0.4) * 0.18, s16["start"] + CHAPTER_PRE, 1.0, -0.4)
    t_par = at("S22", "البرلمان", "پەرلەمانی", 0.5) - 0.3 + 1.0
    for k in range(6):
        sfx.put(V.tick_click(0.9, 2000, 9000, 150) + 0 * 0, t_par + 0.35 * k + (k % 2) * 0.12, 1.0, 0.3 * ((k % 3) - 1))
    tr_len = s25["dur"]
    rumble = lp(rng.standard_normal(int(tr_len * SR)), 160) * 0.8 * env(int(tr_len * SR), 1.0, 0.1, 1, 1.0)
    clack = np.zeros(int(tr_len * SR))
    for k in np.arange(0.4, tr_len - 0.3, 1.2):
        for dt in (0.0, 0.14):
            i = int((k + dt) * SR)
            c = V.tick_click(0.9, 300, 2200, 60)
            clack[i:i + len(c)] += c[:len(clack) - i] * 0.6
    sfx.put(rumble + clack, s25["start"])
    sfx.put(V.room(S["S09"]["dur"] * 0.5) * 0.25, S["S09"]["start"] + S["S09"]["dur"] * 0.3)
    s35 = S["S35"]
    sfx.put(V.wind(s35["dur"], 380, 0.4) * 0.2, s35["start"])

    out = PROJ / "build" / lang / "audio"
    out.mkdir(parents=True, exist_ok=True)
    np.save(out / "stem_voice.npy", voice.x)
    np.save(out / "stem_clips.npy", clips.x)
    np.save(out / "stem_sfx.npy", sfx.x)
    np.save(out / "stem_music.npy", mus.x)
    mix(lang)


MUSIC_UNDER_DB, MUSIC_GAP_DB, SFX_DB = -18.0, -9.0, -12.0


def mix(lang):
    out = PROJ / "build" / lang / "audio"
    tl = json.loads((PROJ / "build" / lang / "timeline.json").read_text(encoding="utf-8"))
    end = int(tl["total"] * SR)
    vx = np.load(out / "stem_voice.npy")[:, :end].astype(np.float32)
    cl = np.load(out / "stem_clips.npy")[:, :end].astype(np.float32)
    v = (vx[0] + cl[0]).astype(np.float64)
    e = np.sqrt(np.maximum(lp(v ** 2, 6), 0.0))
    active = e > (np.percentile(e[e > 1e-5], 50) * 0.25)
    vr = rms(vx[0])
    es = active[::64].astype(np.float64)
    att, rel_ = np.exp(-1 / (0.05 * SR / 64)), np.exp(-1 / (0.8 * SR / 64))
    g = np.zeros_like(es)
    acc = 0.0
    for i, x in enumerate(es):
        acc = att * acc + (1 - att) * x if x > acc else rel_ * acc + (1 - rel_) * x
        g[i] = acc
    g = np.interp(np.arange(end), np.arange(len(g)) * 64, g).astype(np.float32)
    mus = np.load(out / "stem_music.npy")[:, :end].astype(np.float32)
    fx = np.load(out / "stem_sfx.npy")[:, :end].astype(np.float32)
    mr = rms(mus[0])
    fr_ = rms(fx[0])
    under = 10 ** (MUSIC_UNDER_DB / 20) * vr / mr
    gap = 10 ** (MUSIC_GAP_DB / 20) * vr / mr
    mg = (gap + (under - gap) * g).astype(np.float32)
    sg = (10 ** (SFX_DB / 20) * vr / fr_) * (1 - 0.3 * g)
    m = vx + cl + mus * mg + fx * sg.astype(np.float32)
    fo = int(1.5 * SR)
    m[:, -fo:] *= np.linspace(1, 0, fo, dtype=np.float32)
    m = m * np.float32(0.8 / float(np.abs(m).max()))
    m = np.tanh(m * np.float32(1.05)) / np.float32(1.05)
    wavfile.write(out / "mix.wav", SR, m.T.astype(np.float32))
    print(f"wrote {out / 'mix.wav'} {tl['total']:.1f}s")


if __name__ == "__main__":
    build(sys.argv[1])
