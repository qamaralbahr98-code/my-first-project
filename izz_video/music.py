"""Original 60-second score, synthesised from scratch.

Follows the audio cues in the scripts:
  0-10  soft ney melody + morning ambience
  10-20 gentle oud joins the ney
  20-30 tension builds with low strings
  30-40 steady frame-drum pulse
  40-50 orchestra rises
  50-60 orchestral climax, then a soft ney fade-out

Everything is in maqam Hijaz on D (D Eb F# G A Bb C D).
"""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
DUR = 60.0
N = int(SR * DUR)
D4 = 293.66
rng = np.random.default_rng(7)

# Hijaz scale degrees as semitones above the tonic
HIJAZ = {"D": 0, "Eb": 1, "F#": 4, "G": 5, "A": 7, "Bb": 8, "C": 10, "D'": 12,
         "Eb'": 13, "F#'": 16, "G'": 17, "A'": 19, "C,": -2, "A,": -5, "Bb,": -4, "G,": -7}


def f(note, octave=0):
    return D4 * 2 ** ((HIJAZ[note] + 12 * octave) / 12)


def lp(x, cut, order=2):
    return sosfilt(butter(order, cut, "low", fs=SR, output="sos"), x)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "band", fs=SR, output="sos"), x)


def env_adsr(n, a, d, s, r):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    e = np.full(n, s, dtype=np.float64)
    a = min(a, n)
    e[:a] = np.linspace(0, 1, a, endpoint=False)
    if a + d < n:
        e[a:a + d] = np.linspace(1, s, d, endpoint=False)
    if r > 0 and n > r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def add(buf, sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


# ---------------------------------------------------------------- instruments
def ney(freq, dur, vib=0.006, breath=0.18):
    n = int(dur * SR)
    t = np.arange(n) / SR
    vib_amt = vib * np.clip(t / 0.6, 0, 1)            # vibrato grows into the note
    phase = 2 * np.pi * np.cumsum(freq * (1 + vib_amt * np.sin(2 * np.pi * 5.2 * t))) / SR
    tone = np.sin(phase) + 0.18 * np.sin(2 * phase) + 0.06 * np.sin(3 * phase)
    noise = bp(rng.standard_normal(n), freq * 0.8, min(freq * 4, 15000)) * breath
    e = env_adsr(n, 0.18, 0.2, 0.85, min(0.35, dur * 0.4))
    chiff = np.exp(-t * 25) * bp(rng.standard_normal(n), 1500, 6000) * 0.25
    return (tone + noise) * e + chiff


def pluck(freq, dur, bright=0.5, decay=0.996):
    """Karplus-Strong string: an oud-like pluck."""
    n = int(dur * SR)
    period = int(SR / freq)
    buf = rng.uniform(-1, 1, period)
    buf = lp(buf, 2000 + bright * 5000)
    blocks = []
    for _ in range(n // period + 1):  # block-wise Karplus-Strong (fast, near-identical sound)
        blocks.append(buf)
        buf = decay * 0.5 * (buf + np.roll(buf, -1))
    out = lp(np.concatenate(blocks)[:n], 4500)
    return out * env_adsr(n, 0.002, 0.05, 1.0, 0.08)


def pad(freqs, dur, cut=1200, detune=0.004):
    """String-section pad: detuned saws, low-passed."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for fr in freqs:
        for k, dt in enumerate((-detune, 0, detune)):
            ph = (fr * (1 + dt) * t + rng.random()) % 1.0
            saw = 2 * ph - 1
            out += saw * (0.7 if k == 1 else 0.5)
    out /= max(1, len(freqs) * 1.7)
    out = lp(out, cut, 4)
    trem = 1 + 0.04 * np.sin(2 * np.pi * 4.5 * t + rng.random() * 6)
    return out * trem


def dum(gain=1.0):
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    fr = 55 + 60 * np.exp(-t * 30)
    body = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 7)
    skin = lp(rng.standard_normal(n), 900) * np.exp(-t * 40) * 0.4
    return (body + skin) * gain


def tek(gain=0.5):
    n = int(0.15 * SR)
    t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 1800, 7000) * np.exp(-t * 45) * gain


def timpani(freq, gain=1.0):
    n = int(2.5 * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 1.5 * t) * np.exp(-t * 3)
    roll = lp(rng.standard_normal(n), 400) * np.exp(-t * 6) * 0.3
    return (s * np.exp(-t * 1.6) + roll) * gain


def bird(dur=0.35):
    n = int(dur * SR)
    t = np.arange(n) / SR
    fr = 3200 + 900 * np.sin(2 * np.pi * 14 * t) + 1500 * t / dur
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(np.pi * t / dur) ** 2


# ---------------------------------------------------------------- arrangement
def compose():
    L = np.zeros(N)
    R = np.zeros(N)

    def put(sig, t0, gain, pan=0.0):
        add(L, sig, t0, gain * np.sqrt(0.5 * (1 - pan)))
        add(R, sig, t0, gain * np.sqrt(0.5 * (1 + pan)))

    # ---- morning ambience (0-11): soft wind + a few distant birds
    wind = lp(rng.standard_normal(int(12 * SR)), 500) * 0.5
    wind *= env_adsr(len(wind), 2.0, 0.1, 1.0, 3.0)
    put(wind, 0, 0.07, -0.2)
    put(lp(rng.standard_normal(int(12 * SR)), 450) * env_adsr(int(12 * SR), 2, .1, 1, 3), 0, 0.06, 0.3)
    for t0, p in [(1.2, -0.6), (1.6, -0.6), (3.9, 0.5), (6.3, -0.3), (6.7, -0.3), (8.8, 0.6)]:
        put(bird(0.25 + rng.random() * 0.2), t0, 0.035, p)

    # soft drone under everything until the climax
    drone = pad([f("D", -2), f("A", -2)], 52, cut=500, detune=0.002) * env_adsr(int(52 * SR), 4, .1, 1, 4)
    put(drone, 0, 0.13)

    # ---- ney (scene 1 solo, then over the oud)
    ney_line = [
        # (time, note, octave, dur)
        (0.8, "A", 0, 2.2), (3.0, "Bb", 0, 0.5), (3.5, "A", 0, 0.5), (4.0, "G", 0, 0.6),
        (4.6, "F#", 0, 1.4), (6.2, "G", 0, 0.5), (6.7, "F#", 0, 0.5), (7.2, "Eb", 0, 0.6),
        (7.8, "D", 0, 2.4),
        (11.0, "D", 0, 0.6), (11.6, "Eb", 0, 0.6), (12.2, "F#", 0, 1.2), (13.6, "G", 0, 0.6),
        (14.2, "A", 0, 1.8), (16.2, "Bb", 0, 0.5), (16.7, "A", 0, 0.5), (17.2, "G", 0, 0.7),
        (17.9, "F#", 0, 0.6), (18.5, "G", 0, 1.6),
    ]
    for t0, nt, octv, d in ney_line:
        put(ney(f(nt, octv), d + 0.25), t0, 0.33, 0.15)

    # ---- oud (10-50): arpeggiated plucks
    oud_pattern = ["D", "A", "D'", "A", "F#", "A", "Eb", "D"]
    tempo = 0.375  # eighth notes at 80 bpm
    t = 10.0
    i = 0
    while t < 49.5:
        nt = oud_pattern[i % len(oud_pattern)]
        if 20 <= t < 30:  # darker in the tension scene
            nt = ["D", "Eb", "D", "C,", "D", "Eb", "F#", "Eb"][i % 8]
        octv = -1
        g = 0.30 * min(1.0, (t - 10) / 2.5)
        put(pluck(f(nt, octv), 1.2, bright=0.4 + 0.3 * rng.random()), t + rng.normal(0, 0.006), g, -0.35)
        # tremolo double-stroke on downbeats
        if i % 4 == 0 and t >= 12:
            put(pluck(f(nt, octv), 0.8, bright=0.3), t + tempo / 2, g * 0.55, -0.35)
        t += tempo
        i += 1

    # ---- low strings, tension (20-40)
    s1 = pad([f("D", -2), f("A", -2), f("Eb", -1)], 11, cut=700) * env_adsr(int(11 * SR), 4, .1, 1, 1.5)
    put(s1, 19.5, 0.55, -0.1)
    s1b = pad([f("D", -2), f("A", -2), f("C", -1), f("F#", -1)], 11, cut=800) * env_adsr(int(11 * SR), 1.5, .1, 1, 1.5)
    put(s1b, 29.5, 0.45, 0.1)
    # pulsing low cello notes in scene 3
    for k in range(13):
        tt = 20 + k * 0.75
        n = int(0.7 * SR)
        cel = pad([f("D", -2)], 0.7, cut=600) * env_adsr(n, 0.05, 0.2, 0.6, 0.3)
        put(cel, tt, 0.5 * (0.6 + 0.4 * k / 12))

    # ---- frame drum (30-57)
    beat = 0.75
    t = 30.0
    k = 0
    while t < 57.5:
        bar_pos = k % 4
        g = 0.55 if t < 40 else 0.65 if t < 50 else 0.8
        if bar_pos in (0, 2):
            put(dum(), t, g)
        if bar_pos == 3:
            put(dum(), t, g * 0.7)
            put(dum(), t + beat / 2, g * 0.5)
        put(tek(), t + beat / 2, g * 0.45, 0.4)
        if t >= 40 and bar_pos == 1:
            put(tek(), t, g * 0.35, -0.4)
        t += beat
        k += 1

    # ---- orchestra rises (40-50) and climax (50-57)
    rise = pad([f("D", -1), f("A", -1), f("D", 0), f("F#", 0)], 10.5, cut=1600)
    rise *= np.linspace(0.3, 1.0, len(rise)) * env_adsr(len(rise), 1.0, .1, 1, 0.5)
    put(rise, 40, 0.42)
    climax = pad([f("D", -2), f("D", -1), f("A", -1), f("D", 0), f("F#", 0), f("A", 0)], 9.5, cut=2600)
    climax *= env_adsr(len(climax), 0.4, 1.0, 0.85, 4.5)
    put(climax, 50, 0.6)
    for tt, fr, g in [(40, f("D", -2), 0.5), (45, f("A", -3), 0.5), (48.5, f("D", -2), 0.4),
                      (49.25, f("D", -2), 0.5), (50, f("D", -2), 0.9), (54, f("A", -3), 0.6)]:
        put(timpani(fr), tt, g)

    # high ney theme over the climax, then a soft solo fade-out
    for t0, nt, octv, d in [(44.0, "A", 0, 1.4), (45.5, "Bb", 0, 0.7), (46.2, "A", 0, 0.7),
                            (47.0, "G", 0, 0.8), (47.9, "F#", 0, 1.8),
                            (50.2, "D'", 0, 1.6), (52.0, "C", 0, 0.6), (52.6, "Bb", 0, 0.6),
                            (53.3, "A", 0, 1.8), (55.3, "G", 0, 0.6), (55.9, "F#", 0, 0.8)]:
        put(ney(f(nt, octv), d + 0.25, vib=0.008), t0, 0.36, 0.15)
    last = ney(f("D", 0), 3.6, vib=0.007, breath=0.25)
    last *= np.linspace(1, 0, len(last)) ** 1.5
    put(last, 56.4, 0.30, 0.15)

    return L, R


def reverb(L, R, seconds=2.6, mix=0.28):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    decay = np.exp(-t * 6.9 / seconds)
    irL = rng.standard_normal(n) * decay
    irR = rng.standard_normal(n) * decay
    irL, irR = lp(irL, 6000), lp(irR, 6000)
    irL /= np.sqrt(np.sum(irL ** 2))
    irR /= np.sqrt(np.sum(irR ** 2))
    wL = fftconvolve(L, irL)[: len(L)]
    wR = fftconvolve(R, irR)[: len(R)]
    return L * (1 - mix) + wL * mix * 2.2, R * (1 - mix) + wR * mix * 2.2


def render(path):
    import wave
    L, R = compose()
    # overall dynamic arc: quiet opening, building to the climax at 50s
    pts_t = [0, 9, 11, 19, 21, 29, 31, 39, 41, 50, 60]
    pts_g = [0.55, 0.55, 0.62, 0.62, 0.95, 0.95, 0.9, 0.9, 1.0, 1.0, 1.0]
    auto = np.interp(np.arange(N) / SR, pts_t, pts_g)
    L, R = L * auto, R * auto
    L, R = reverb(L, R)
    # master fades
    fade_in = int(1.0 * SR)
    for ch in (L, R):
        ch[:fade_in] *= np.linspace(0, 1, fade_in)
        ch[-int(0.5 * SR):] *= np.linspace(1, 0, int(0.5 * SR))
    st = np.stack([L, R], axis=1)
    st = np.tanh(st / np.max(np.abs(st)) * 1.4) / np.tanh(1.4) * 0.89  # gentle limiter
    pcm = (st * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return path


if __name__ == "__main__":
    import sys
    render(sys.argv[1] if len(sys.argv) > 1 else "music.wav")


def render_outro(path, seconds=6.0):
    """A short, quiet closing phrase for the end card: soft drone, a few oud notes, one held ney note."""
    import wave
    n = int(seconds * SR)
    L, R = np.zeros(n), np.zeros(n)

    def put(sig, t0, gain, pan=0.0):
        add(L, sig, t0, gain * np.sqrt(0.5 * (1 - pan)))
        add(R, sig, t0, gain * np.sqrt(0.5 * (1 + pan)))

    drone = pad([f("D", -2), f("A", -2), f("D", -1)], seconds, cut=650, detune=0.002)
    put(drone * env_adsr(len(drone), 1.2, .1, 1, 2.0), 0, 0.22)
    for t0, nt in [(0.6, "D"), (1.05, "A"), (1.5, "D'"), (2.3, "F#"), (2.75, "Eb"), (3.2, "D")]:
        put(pluck(f(nt, -1), 1.6, bright=0.4), t0, 0.26, -0.3)
    last = ney(f("A", 0), 2.6, vib=0.006, breath=0.2)
    put(last * np.linspace(1, 0, len(last)) ** 1.3, 3.0, 0.22, 0.15)
    L, R = reverb(L, R, seconds=2.4, mix=0.32)
    fade = np.ones(n)
    fade[: int(0.5 * SR)] = np.linspace(0, 1, int(0.5 * SR))
    fade[-int(1.6 * SR):] = np.linspace(1, 0, int(1.6 * SR)) ** 1.5
    st = np.stack([L * fade, R * fade], axis=1)
    st = st / (np.max(np.abs(st)) or 1) * 0.35
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
    return path
