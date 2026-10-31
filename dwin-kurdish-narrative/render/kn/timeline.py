"""Edit timeline from the recorded narration: scene start/length, audio placement, word times, caption cues.

    python3 -m ky.timeline ar|ckb|kmr      (run from dwin-kurd-youth/render)
"""
import json
import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parents[2]

PRE, POST = 0.40, 0.55
CHAPTERS = {"S05": 2, "S14": 3, "S19": 4, "S27": 5, "S33": 6, "S37": 7}
CHAPTER_PRE = 1.8
EXTRA = {"S01": ("pre", 1.0), "S04": ("post", 1.4), "S18": ("post", 0.8), "S29": ("post", 0.8),
         "S38": ("post", 1.2), "S39": ("post", 1.0)}
END_CARD = 6.0


def align(script, rec, pre):
    """Script tokens timed by character fraction against the recorded words (numbers are spoken as words)."""
    import bisect
    rc = [len(w["text"]) + 1 for w in rec]
    tot_r = float(sum(rc))
    cum, acc = [], 0.0
    for c in rc:
        cum.append(acc / tot_r)
        acc += c
    sc = [len(x) + 1 for x in script]
    tot_s = float(sum(sc))

    def at(f):
        i = max(0, min(len(rec) - 1, bisect.bisect_right(cum, f) - 1))
        w = rec[i]
        span = rc[i] / tot_r
        u = min(1.0, max(0.0, (f - cum[i]) / span)) if span else 0
        return w["start"] + (w["end"] - w["start"]) * u
    out, acc = [], 0.0
    for x, c in zip(script, sc):
        s0 = at(acc / tot_s)
        acc += c
        e0 = at(min(0.9999, (acc - 1) / tot_s))
        out.append(dict(text=x, s=round(pre + s0, 3), e=round(pre + max(e0, s0 + 0.05), 3)))
    return out


def expand_align(script, rec, pre, lang):
    """Each script token covers as many recorded words as its spoken form (digits -> number words)."""
    sys.path.insert(0, str(PROJ / "render"))
    from vo_plan import speak
    ns = [max(1, len(speak(x, lang).split())) for x in script]
    if sum(ns) != len(rec):
        print(f"note: {lang}: {sum(ns)} expanded vs {len(rec)} recorded; char alignment")
        return None
    out, i = [], 0
    for x, n in zip(script, ns):
        out.append(dict(text=x, s=round(pre + rec[i]["start"], 3), e=round(pre + rec[i + n - 1]["end"], 3)))
        i += n
    return out


def chapter_titles(lang):
    import re
    md = (PROJ / "social" / f"youtube_{lang}.md").read_text(encoding="utf-8")
    lines = [re.sub(r"^\S+\s+", "", l).strip() for l in md.splitlines() if re.match(r"^\d{1,2}:\d{2}\s", l)]
    return {i + 1: t for i, t in enumerate(lines)}


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
        if len(script) == len(rec):
            words = [dict(text=x, s=round(pre + w["start"], 3), e=round(pre + w["end"], 3)) for x, w in zip(script, rec)]
        else:
            words = expand_align(script, rec, pre, lang) or align(script, rec, pre)
        dur = pre + d + post
        scenes.append(dict(id=sid, start=round(t, 3), dur=round(dur, 3), ost=s[lang]["t"].split("\n"),
                           source=s.get("source", ""), chapter=CHAPTERS.get(sid),
                           chapter_title=chapter_titles(lang).get(CHAPTERS.get(sid), ""),
                           audio=[dict(seg=sid, start=pre, dur=d)], words=words))
        t += dur
    scenes.append(dict(id="END", start=round(t, 3), dur=END_CARD, ost=[], source="", chapter=None, chapter_title="", audio=[], words=[]))
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
