"""Local forced alignment (no paid API): MMS-300m CTC forced aligner + uroman romanisation, torchaudio forced_align.

    python3 render/align.py <lang> [seg ...]      -> build/<lang>/vo/aligned.json  {seg: [{text, start, end}, ...]}

Works on the per-scene narration parts (build/<lang>/vo/parts/<seg>.wav, already at the film's tempo) and the
script tokens of each scene (digits are spoken as words: their romanised spoken form is aligned, the token keeps
its written form). Words with Kurdish letters or ZWNJ stay one token.
"""
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch
import torchaudio
from torchaudio.functional import forced_align, merge_tokens

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
from vo_plan import speak  # noqa: E402

MODEL = "MahmoudAshraf/mms-300m-1130-forced-aligner"
AR_NUM = None


@lru_cache(maxsize=1)
def model():
    from transformers import AutoModelForCTC, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(MODEL)
    m = AutoModelForCTC.from_pretrained(MODEL).eval()
    return m, tok


@lru_cache(maxsize=1)
def romaniser():
    import uroman
    return uroman.Uroman()


def ar_number_words(n):
    """Arabic spoken form of a number, for alignment only (the caption keeps the digits)."""
    ones = ["", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة"]
    teens = ["عشرة", "أحد عشر", "اثنا عشر", "ثلاثة عشر", "أربعة عشر", "خمسة عشر", "ستة عشر", "سبعة عشر", "ثمانية عشر", "تسعة عشر"]
    tens = ["", "", "عشرون", "ثلاثون", "أربعون", "خمسون", "ستون", "سبعون", "ثمانون", "تسعون"]
    hund = ["", "مئة", "مئتان", "ثلاثمئة", "أربعمئة", "خمسمئة", "ستمئة", "سبعمئة", "ثمانمئة", "تسعمئة"]
    parts = []
    th, r = divmod(n, 1000)
    if th == 1:
        parts.append("ألف")
    elif th == 2:
        parts.append("ألفان")
    elif th:
        parts.append(ar_number_words(th) + " آلاف")
    h, r = divmod(r, 100)
    if h:
        parts.append(hund[h])
    if 10 <= r < 20:
        parts.append(teens[r - 10])
    else:
        t, u = divmod(r, 10)
        if u and t:
            parts.append(f"{ones[u]} و{tens[t]}")
        elif u:
            parts.append(ones[u])
        elif t:
            parts.append(tens[t])
    return " و".join(p for p in parts if p)


def spoken(token, lang):
    t = token.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    if lang == "ar":
        return re.sub(r"\d[\d,]*", lambda m: ar_number_words(int(m.group(0).replace(",", ""))), t)
    return speak(t, lang)


def norm(roman):
    roman = roman.lower().replace("’", "'")
    roman = re.sub(r"[^a-z' ]", " ", roman)
    return re.sub(r"\s+", " ", roman).strip()


def align(wav_path, tokens, lang):
    m, tok = model()
    import subprocess
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav_path), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    wav = torch.from_numpy(np.frombuffer(raw, np.float32).copy())[None]
    ur = romaniser()
    rom = [norm(ur.romanize_string(spoken(x, lang))) or "a" for x in tokens]
    vocab = tok.get_vocab()
    star = vocab.get("<star>")
    blank = vocab.get("<blank>", 0)
    ids, owner = [], []
    for i, r in enumerate(rom):
        for ch in r.replace(" ", ""):
            if ch in vocab:
                ids.append(vocab[ch])
                owner.append(i)
    with torch.inference_mode():
        emis = []
        step = 16000 * 30
        x = wav[0]
        for a in range(0, len(x), step):
            chunk = x[a:a + step + 1600]
            out = m(chunk[None]).logits
            k = int(round(step / 320)) if a + step < len(x) else out.shape[1]
            emis.append(out[0, :k])
        em = torch.log_softmax(torch.cat(emis)[None], dim=-1)
    targets = torch.tensor([ids], dtype=torch.int32)
    ali, scores = forced_align(em, targets, blank=blank)
    spans = merge_tokens(ali[0], scores[0].exp(), blank=blank)
    frame = 320 / 16000
    res = [dict(text=t, start=None, end=None) for t in tokens]
    for sp, o in zip(spans, owner):
        s, e = sp.start * frame, sp.end * frame
        if res[o]["start"] is None:
            res[o]["start"] = s
        res[o]["end"] = e
    # tokens with nothing alignable (punctuation only): take the neighbour's edge
    for i, r in enumerate(res):
        if r["start"] is None:
            prev = res[i - 1]["end"] if i else 0.0
            r["start"] = r["end"] = prev
    return [dict(text=r["text"], start=round(r["start"], 3), end=round(r["end"], 3)) for r in res]


def main(lang, segs=None):
    sj = {s["id"]: s for s in json.loads((ROOT / "build" / "script.json").read_text(encoding="utf-8"))["scenes"]}
    vo = ROOT / "build" / lang / "vo"
    out = vo / "aligned.json"
    done = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    for sid in segs or list(sj):
        wav = vo / "parts" / f"{sid}.wav"
        if not wav.exists():
            continue
        text = sj[sid][lang].get("tts_caption", sj[sid][lang]["n"])
        done[sid] = align(wav, text.split(), lang)
        print(lang, sid, len(done[sid]), "words", flush=True)
        out.write_text(json.dumps(done, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:] or None)
