"""Local pronunciation check (no paid API): which reading of one word does the audio match better?

    python3 render/pron_check.py <audio> "<sentence text>" <word-substring> <good-roman> <bad-roman> [tempo]

Aligns the sentence with the MMS forced aligner (align.py), cuts the target word (+-40 ms) and compares the CTC
log-likelihood of two romanised readings, e.g. halabja vs halabaja, attalabani vs attalibani. margin < 0 = good.
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).parent))
from align import align, model  # noqa: E402


def load16(path, tempo=1.0):
    af = [] if tempo == 1.0 else ["-af", f"atempo={tempo}"]
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path)] + af + ["-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def nll(em, s):
    m, tok = model()
    voc = tok.get_vocab()
    ids = torch.tensor([[voc[c] for c in s if c in voc]], dtype=torch.long)
    return torch.nn.functional.ctc_loss(em, ids, torch.tensor([em.shape[0]]), torch.tensor([ids.shape[1]]),
                                        blank=voc.get("<blank>", 0), reduction="sum").item()


def check(audio, text, needle, good, bad, tempo=1.0):
    m, tok = model()
    x = load16(audio, tempo)
    tmp = Path("/tmp") / "pron_check.wav"
    from scipy.io import wavfile
    wavfile.write(str(tmp), 16000, x.astype(np.float32))
    ws = align(tmp, text.split(), "ar")
    out = []
    for w in ws:
        if needle not in w["text"].replace("َ", "").replace("ْ", "").replace("ّ", "") and needle not in w["text"]:
            continue
        a, b = int((w["start"] - 0.04) * 16000), int((w["end"] + 0.04) * 16000)
        seg = torch.from_numpy(x[max(0, a):b])[None]
        with torch.inference_mode():
            em = torch.log_softmax(m(seg).logits, -1)[0][:, None, :]
        g, bd = nll(em, good), nll(em, bad)
        out.append(dict(word=w["text"], start=w["start"], good=round(g, 2), bad=round(bd, 2), margin=round(g - bd, 2),
                        ok=g < bd))
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    for r in check(a[0], a[1], a[2], a[3], a[4], float(a[5]) if len(a) > 5 else 1.0):
        print(("OK  " if r["ok"] else "BAD ") + f"{r['word']} @{r['start']:.2f}s  {a[3]} {r['good']}  {a[4]} {r['bad']}  "
              f"margin {r['margin']:+.2f}")
