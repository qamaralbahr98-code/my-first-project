"""Cut each ElevenLabs recording into its parts and save one WAV per part.

A batch was read with "[long pause]" between parts, so the n-1 longest pauses are the cuts.
    python3 render/vo_split.py ar [--take n04=2 ...]
Writes build/<lang>/vo/parts/<seg>.wav (48 kHz mono, trimmed) and build/<lang>/vo/parts.json.
The quote voice is made a little lower and slower and gets a light room reverb.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SR = 48000
# Quote voice treatment, as used in the delivered videos. The takes are 44.1 kHz, so "asetrate=48000*0.971"
# actually raises the pitch by about one semitone and, with atempo, makes the clip ~2.5% shorter (it was meant to be
# half a semitone lower and 6% slower). timeline.py measures the real time scale for the subtitles.
QUOTE_AF = "asetrate=48000*0.971,aresample=48000,atempo=0.97"


def load(path, af=None):
    cmd = ["ffmpeg", "-v", "error", "-i", str(path)]
    if af:
        cmd += ["-af", af]
    cmd += ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).copy()


def save(path, x):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-c:a", "pcm_s24le", str(path)], input=x.astype(np.float32).tobytes(), check=True)


def regions(x, frame=0.02, gap=0.30):
    n = int(frame * SR)
    k = len(x) // n
    db = 20 * np.log10(np.sqrt(np.mean(x[: k * n].reshape(k, n) ** 2, axis=1) + 1e-12))
    th = max(np.percentile(db, 95) - 34, -58)
    on = db > th
    out, s = [], None
    for i, v in enumerate(on):
        if v and s is None:
            s = i
        elif not v and s is not None:
            out.append([s * frame, i * frame])
            s = None
    if s is not None:
        out.append([s * frame, k * frame])
    merged = []
    for r in out:
        if merged and r[0] - merged[-1][1] < gap:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    return [r for r in merged if r[1] - r[0] > 0.10]


def split(x, n):
    regs = regions(x)
    if len(regs) < n:
        raise ValueError(f"only {len(regs)} spoken parts, expected {n}")
    gaps = sorted(range(len(regs) - 1), key=lambda i: regs[i + 1][0] - regs[i][1], reverse=True)[: n - 1]
    cuts = sorted(gaps)
    parts, s = [], 0
    for c in cuts:
        parts.append((regs[s][0], regs[c][1], regs[c + 1][0] - regs[c][1]))
        s = c + 1
    parts.append((regs[s][0], regs[-1][1], None))
    # smallest gap that was cut vs largest gap that was not: a healthy split has a clear margin
    kept = [regs[i + 1][0] - regs[i][1] for i in range(len(regs) - 1) if i not in cuts]
    cut = [regs[i + 1][0] - regs[i][1] for i in cuts]
    return parts, (min(cut) if cut else None), (max(kept) if kept else 0)


def reverb(x, wet=0.16):
    """Light small-room reverb: a few early reflections plus a short decaying noise tail."""
    rng = np.random.default_rng(7)
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    ir = rng.normal(0, 1, n) * np.exp(-t / 0.22)
    ir[: int(0.012 * SR)] = 0
    for d, g in ((0.017, 0.5), (0.029, 0.35), (0.043, 0.25)):
        ir[int(d * SR)] += g * 8
    ir /= np.sqrt(np.sum(ir ** 2))
    y = np.convolve(x, ir)[: len(x) + n]
    out = np.zeros(len(y), np.float32)
    out[: len(x)] = x
    return out + wet * y


def main():
    lang = sys.argv[1]
    takes = dict(a.split("=") for a in sys.argv[2:] if "=" in a)
    vo = ROOT / "build" / lang / "vo"
    plan = json.loads((ROOT / "build" / lang / "vo_plan.json").read_text(encoding="utf-8"))
    (vo / "parts").mkdir(exist_ok=True)
    info = {}
    for b in plan["batches"]:
        t = takes.get(b["name"], "1")
        src = vo / f"{b['name']}_t{t}.mp3"
        af = QUOTE_AF if b["voice"] == "quote" else None
        x = load(src, af)
        parts, cutmin, keptmax = split(x, len(b["segs"]))
        flag = "" if cutmin is None or cutmin > keptmax + 0.15 else "  <-- CHECK SPLIT"
        print(f"{b['name']} take {t}: cut gaps >= {cutmin}, other gaps <= {keptmax:.2f}{flag}")
        for seg, (a, e, g) in zip(b["segs"], parts):
            y = x[max(0, int((a - 0.06) * SR)): int((e + 0.12) * SR)]
            fade = int(0.01 * SR)
            y[:fade] *= np.linspace(0, 1, fade)
            y[-fade:] *= np.linspace(1, 0, fade)
            if b["voice"] == "quote":
                y = reverb(y)
            save(vo / "parts" / f"{seg}.wav", y)
            info[seg] = dict(batch=b["name"], take=int(t), dur=round(len(y) / SR, 3), voice=b["voice"])
            print(f"   {seg:5s} {len(y) / SR:6.2f}s")
    (vo / "parts.json").write_text(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
