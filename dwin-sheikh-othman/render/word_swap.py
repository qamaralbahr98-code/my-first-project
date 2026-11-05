"""Free fix for one mispronounced word: swap it for the same word, correctly spoken by the same voice elsewhere.

    python3 render/word_swap.py <base> "<base text>" <donor> "<donor text>" <needle> <out.wav>

Both takes are aligned locally (MMS forced aligner). The word is cut at the quietest point near each aligned edge,
the donor word is pitch-matched (median F0, rubberband) and loudness-matched to the word it replaces, and joined
with 12 ms crossfades. Works at the takes' own speed (tempo 1.0); v2_audio applies the film tempo afterwards.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from align import align  # noqa: E402
from splice import SR, join, load, quietest, rms_db, save  # noqa: E402


def f0_median(x):
    """Median F0 (Hz) of the voiced 40 ms frames, by normalised autocorrelation (75-300 Hz)."""
    n, hop = int(0.04 * SR), int(0.01 * SR)
    lo, hi = int(SR / 300), int(SR / 75)
    out = []
    for a in range(0, len(x) - n, hop):
        fr = x[a:a + n] - x[a:a + n].mean()
        if np.sqrt((fr ** 2).mean()) < 0.01:
            continue
        ac = np.correlate(fr, fr, "full")[n - 1:]
        ac = ac / (ac[0] + 1e-12)
        k = lo + int(np.argmax(ac[lo:hi]))
        if ac[k] > 0.5:
            out.append(SR / k)
    return float(np.median(out)) if out else None


def pitch(x, ratio):
    if abs(np.log2(ratio) * 12) < 0.4:
        return x
    raw = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af",
                          f"rubberband=pitch={ratio:.5f}:formant=preserved", "-f", "f32le", "-"],
                         input=x.astype(np.float32).tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def word_span(path, text, needle):
    x = load(path)
    tmp = Path("/tmp") / f"ws_{Path(path).stem}.wav"
    save(tmp, x)
    ws = align(tmp, text.split(), "ar")
    i = next(k for k, w in enumerate(ws) if needle in w["text"])
    w = ws[i]
    a = quietest(x, w["start"] - 0.06, w["start"] + 0.03, 0.005)
    b = quietest(x, w["end"] - 0.03, w["end"] + 0.07, 0.005)
    return x, a, b


def swap(base, base_text, donor, donor_text, needle):
    x, a, b = word_span(base, base_text, needle)
    y, c, d = word_span(donor, donor_text, needle)
    old = x[int(a * SR):int(b * SR)]
    new = y[int(c * SR):int(d * SR)]
    fo, fn = f0_median(old), f0_median(new)
    if fo and fn:
        new = pitch(new, fo / fn)
    new = new * 10 ** ((rms_db(old) - rms_db(new)) / 20)
    out = join(join(x[:int(a * SR)], new, 0.012), x[int(b * SR):], 0.012)
    info = dict(cut=(round(a, 3), round(b, 3)), donor=(round(c, 3), round(d, 3)), f0_old=fo and round(fo, 1),
                f0_donor=fn and round(fn, 1), dur_old=round(b - a, 3), dur_new=round(len(new) / SR, 3))
    return out, info


if __name__ == "__main__":
    a = sys.argv[1:]
    out, info = swap(a[0], a[1], a[2], a[3], a[4])
    save(a[5], out)
    print(info)
