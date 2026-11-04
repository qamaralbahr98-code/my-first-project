"""v2 fix pass on the narration (v1 parts are kept untouched).

    python3 render/v2_audio.py ar|ckb

Reads build/fix/edits.json and writes build/<lang>/vo/parts_v2/<scene>.wav plus build/<lang>/vo/captions_v2.json
(the caption text of every changed scene). Operations per scene:
  cut      remove the words first..last, cut at the quietest point of the pause on each side (free)
  replace  swap one sentence (first..last word) for a regenerated take, cut at the pauses, 15 ms crossfades,
           loudness matched to the sentence it replaces, the same pause lengths kept on both sides
  caption  token replacements in the caption text only (the audio is not touched)
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from splice import SR, cut, join, load, quietest, rms_db, save, trim_silence, words  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TEMPO = {"ar": 1.06, "ckb": 1.05}


def find(ws, tok, start=0):
    for i in range(start, len(ws)):
        if ws[i]["text"] == tok or ws[i]["text"].startswith(tok):
            return i
    raise KeyError(tok)


def bounds(x, ws, i, j):
    """Cut points around words i..j: the quietest moment of the pause before i and after j."""
    a = quietest(x, ws[i - 1]["end"], ws[i]["start"] + 0.02) if i > 0 else 0.0
    b = quietest(x, ws[j]["end"] - 0.02, ws[j + 1]["start"]) if j + 1 < len(ws) else len(x) / SR
    return a, b


def lead_trail(x, ws, i, j, a, b):
    return max(0.0, ws[i]["start"] - a), max(0.0, b - ws[j]["end"])


def main(lang):
    edits = json.loads((ROOT / "build" / "fix" / "edits.json").read_text(encoding="utf-8")).get(lang, {})
    vo = ROOT / "build" / lang / "vo"
    out = vo / "parts_v2"
    out.mkdir(exist_ok=True)
    script = {s["id"]: s for s in json.loads((ROOT / "build" / "script.json").read_text(encoding="utf-8"))["scenes"]}
    caps, log = {}, []
    for wav in sorted((vo / "parts").glob("*.wav")):
        shutil.copy(wav, out / wav.name)
    for sid, ops in edits.items():
        x = load(vo / "parts" / f"{sid}.wav")
        ws = words(lang, sid)
        text = script[sid][lang]["n"].split()
        # apply from the end of the scene backwards so earlier times stay valid
        ops_sorted = sorted(ops.get("audio", []), key=lambda o: -find(ws, o["first"]))
        for op in ops_sorted:
            if op.get("pending"):
                continue
            i = find(ws, op["first"])
            j = find(ws, op["last"], i)
            a, b = bounds(x, ws, i, j)
            if op["op"] == "cut":
                x = cut(x, a, b)
                log.append(f"{lang} {sid}: cut {op['first']}..{op['last']} ({a:.2f}-{b:.2f} s, {b - a:.2f} s)")
                text = text[:i] + text[j + 1:]
            elif op["op"] == "replace":
                new = trim_silence(load(ROOT / op["file"], TEMPO[lang]), -45, 0.0)
                lead, trail = lead_trail(x, ws, i, j, a, b)
                old = x[int(ws[i]["start"] * SR):int(ws[j]["end"] * SR)]
                new = new * 10 ** ((rms_db(old) - rms_db(new)) / 20)
                seg = np.concatenate([np.zeros(int(lead * SR)), new, np.zeros(int(trail * SR))])
                x = join(join(x[:int(a * SR)], seg), x[int(b * SR):])
                log.append(f"{lang} {sid}: replaced {op['first']}..{op['last']} ({a:.2f}-{b:.2f} s) with {op['file']} "
                           f"({len(seg) / SR:.2f} s)")
        for old_tok, new_tok in ops.get("caption", []):
            joined = " ".join(text).replace(old_tok, new_tok)
            text = joined.split()
        save(out / f"{sid}.wav", x)
        caps[sid] = " ".join(text)
    (vo / "captions_v2.json").write_text(json.dumps(caps, ensure_ascii=False, indent=1), encoding="utf-8")
    (ROOT / "build" / "fix" / f"audio_log_{lang}.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log) or f"{lang}: no audio edits")


if __name__ == "__main__":
    main(sys.argv[1])
