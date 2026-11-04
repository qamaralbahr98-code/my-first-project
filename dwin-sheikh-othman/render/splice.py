"""Audio cut / splice helpers for the v2 fix pass: cut at silence, 15 ms crossfade, loudness matched to the neighbours."""
import json
import subprocess
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
XF = 0.015


def load(path, tempo=1.0):
    af = [] if tempo == 1.0 else ["-af", f"atempo={tempo}"]
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path)] + af + ["-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def save(path, x):
    from scipy.io import wavfile
    wavfile.write(str(path), SR, x.astype(np.float32))


def rms_db(x):
    x = x[np.abs(x) > 1e-4]
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12) if len(x) else -120.0


def quietest(x, t0, t1, win=0.01):
    """Time of the lowest 10 ms energy between t0 and t1 (the natural pause)."""
    a, b = int(max(0, t0) * SR), int(min(len(x) / SR, t1) * SR)
    if b - a < int(win * SR) * 2:
        return (t0 + t1) / 2
    h = int(win * SR)
    seg = x[a:b]
    n = len(seg) // h
    e = (seg[:n * h].reshape(n, h) ** 2).mean(1)
    k = int(np.argmin(np.convolve(e, np.ones(3) / 3, "same")))
    return (a + k * h + h / 2) / SR


def join(a, b, xf=XF):
    n = int(xf * SR)
    if len(a) < n or len(b) < n:
        return np.concatenate([a, b])
    w = np.linspace(0, 1, n)
    mid = a[-n:] * (1 - w) + b[:n] * w
    return np.concatenate([a[:-n], mid, b[n:]])


def cut(x, ta, tb, xf=XF):
    """Remove [ta, tb) (seconds) with a short crossfade."""
    return join(x[:int(ta * SR)], x[int(tb * SR):], xf)


def splice(x, ta, tb, new, xf=XF, ref=None):
    """Replace [ta, tb) by `new`, loudness matched to the replaced audio (or to `ref`)."""
    old = x[int(ta * SR):int(tb * SR)] if ref is None else ref
    g = 10 ** ((rms_db(old) - rms_db(new)) / 20)
    return join(join(x[:int(ta * SR)], new * g, xf), x[int(tb * SR):], xf)


def trim_silence(x, thr_db=-45, pad=0.06):
    h = int(0.01 * SR)
    n = len(x) // h
    e = 20 * np.log10(np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-12)
    on = np.where(e > e.max() + thr_db)[0]
    if not len(on):
        return x
    a, b = max(0, on[0] * h - int(pad * SR)), min(len(x), (on[-1] + 1) * h + int(pad * SR))
    y = x[a:b].copy()
    f = int(0.005 * SR)
    y[:f] *= np.linspace(0, 1, f)
    y[-f:] *= np.linspace(1, 0, f)
    return y


def words(lang, sid):
    return json.loads((ROOT / "build" / lang / "vo" / "aligned.json").read_text(encoding="utf-8"))[sid]
