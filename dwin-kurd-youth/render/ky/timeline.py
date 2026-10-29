"""Edit timeline from the recorded narration: scene start/length, audio placement, word times, caption cues.

    python3 -m ky.timeline ar|ckb|kmr      (run from dwin-kurd-youth/render)
"""
import json
import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parents[2]

PRE, POST = 0.40, 0.55
CHAPTERS = {"S11": 1, "S16": 2, "S23": 3, "S27": 4}
CHAPTER_PRE = 2.0
EXTRA = {"S01": ("pre", 1.2), "S02": ("post", 0.6), "S03": ("post", 0.8), "S04": ("post", 1.6),
         "S10": ("post", 0.5), "S14": ("post", 0.9), "S19": ("post", 0.6), "S21": ("post", 0.8),
         "S30": ("post", 0.6), "S31": ("post", 0.8), "S32": ("post", 1.6), "S33": ("post", 1.2)}
END_CARD = 6.0


def build(lang):
    sj = json.loads((PROJ / "script" / "scenes.json").read_text(encoding="utf-8"))
    vo = PROJ / "build" / lang / "vo"
    parts = json.loads((vo / "parts.json").read_text())
    sw = json.loads((vo / "words.json").read_text(encoding="utf-8"))
    scenes, t = [], 0.0
    for s in sj["scenes"]:
        sid = s["id"]
        pre, post = PRE, POST
        if sid in CHAPTERS:
            pre = CHAPTER_PRE
        if sid in EXTRA:
            k, v = EXTRA[sid]
            if k == "pre":
                pre = v
            else:
                post = v
        d = parts[sid]["dur"]
        script = s[lang]["n"].split()
        rec = sw[sid]
        toks = script if len(script) == len(rec) else [w["text"] for w in rec]
        if len(script) != len(rec):
            print(f"note: {lang} {sid}: {len(rec)} recorded words vs {len(script)} in the script; using transcript")
        words = [dict(text=x, s=round(pre + w["start"], 3), e=round(pre + w["end"], 3)) for x, w in zip(toks, rec)]
        dur = pre + d + post
        scenes.append(dict(id=sid, start=round(t, 3), dur=round(dur, 3), ost=s[lang]["t"].split("\n"),
                           source=s.get("source", ""), chapter=CHAPTERS.get(sid),
                           audio=[dict(seg=sid, start=pre, dur=d)], words=words))
        t += dur
    scenes.append(dict(id="END", start=round(t, 3), dur=END_CARD, ost=[], source="", chapter=None, audio=[], words=[]))
    t += END_CARD
    return dict(lang=lang, total=round(t, 3), scenes=scenes)


def _chunks(words, maxc):
    """Caption chunks: one line of at most maxc characters, broken preferably at punctuation."""
    chunks, cur, n = [], [], 0
    for w in words:
        tx = w["text"]
        if cur and n + len(tx) + 1 > maxc:
            chunks.append(cur)
            cur, n = [], 0
        cur.append(w)
        n += len(tx) + 1
        if tx[-1] in ".؟?!:؛;،,…" and n > maxc * 0.55:
            chunks.append(cur)
            cur, n = [], 0
    if cur:
        if chunks and sum(len(w["text"]) + 1 for w in cur) < 10 and \
                sum(len(w["text"]) + 1 for w in chunks[-1]) + n <= maxc + 8:
            chunks[-1] += cur
        else:
            chunks.append(cur)
    return chunks


def captions(tl, maxc):
    cues = []
    for sc in tl["scenes"]:
        words = [dict(text=w["text"], s=round(sc["start"] + w["s"], 3), e=round(sc["start"] + w["e"], 3))
                 for w in sc["words"]]
        for ch in _chunks(words, maxc):
            cues.append(dict(start=round(ch[0]["s"] - 0.05, 3), end=round(ch[-1]["e"] + 0.3, 3), words=ch,
                             text=" ".join(w["text"] for w in ch), scene=sc["id"]))
    for i in range(len(cues) - 1):
        if cues[i]["end"] > cues[i + 1]["start"] - 0.03:
            cues[i]["end"] = round(cues[i + 1]["start"] - 0.03, 3)
    return cues


def _two_lines(text, maxc):
    if len(text) <= maxc:
        return [text]
    words = text.split(" ")
    best, bi = None, 1
    for i in range(1, len(words)):
        score = max(len(" ".join(words[:i])), len(" ".join(words[i:])))
        if best is None or score < best:
            best, bi = score, i
    return [" ".join(words[:bi]), " ".join(words[bi:])]


def write_srt(tl, path, maxc=42):
    """SRT for upload: up to two lines per cue."""
    cues = captions(tl, maxc * 2 - 10)

    def ts(x):
        ms = int(round(max(0, x) * 1000))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    Path(path).write_text("\n".join(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n" + "\n".join(_two_lines(c["text"], maxc))
                                    + "\n" for i, c in enumerate(cues, 1)), encoding="utf-8")


if __name__ == "__main__":
    lang = sys.argv[1]
    tl = build(lang)
    out = PROJ / "build" / lang
    (out / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    for fmt, maxc in (("16x9", 46), ("9x16", 26)):
        (out / f"cues_{fmt}.json").write_text(json.dumps(captions(tl, maxc), ensure_ascii=False, indent=1),
                                              encoding="utf-8")
    write_srt(tl, out / f"{lang}_synced.srt")
    print(f"{lang}: {len(tl['scenes'])} scenes, {tl['total']:.1f} s")
