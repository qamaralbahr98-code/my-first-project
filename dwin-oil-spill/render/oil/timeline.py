"""Edit timeline from the recorded narration: scene start/length, audio placement, word times, subtitle cues.

    python3 -m oil.timeline ckb|kmr      (run from dwin-oil-spill/render)
"""
import json
import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJ / "render"))
import vo_split  # noqa: E402

PRE, POST = 0.45, 0.55
EXTRA = {"S01": ("post", 2.4), "S07": ("post", 0.7), "S10": ("post", 0.6), "S11": ("post", 0.8), "S12": ("post", 1.0),
         "S13": ("post", 1.0), "S14": ("post", 1.6)}
END_CARD = 4.5


def _batch_offsets(lang, plan):
    vo = PROJ / "build" / lang / "vo"
    offs = {}
    for b in plan["batches"]:
        x = vo_split.load(vo / f"{b['name']}_t1.mp3")
        parts, _, _ = vo_split.split(x, len(b["segs"]))
        for seg, (a, e, g) in zip(b["segs"], parts):
            offs[seg] = a - 0.06
    return offs


def _seg_words(lang, plan):
    vo = PROJ / "build" / lang / "vo"
    out = {}
    for b in plan["batches"]:
        words = json.loads((vo / f"{b['name']}_words.json").read_text(encoding="utf-8"))["words"]
        groups, cur, i = [], [], 0
        while i < len(words):
            w = words[i]
            if w["text"] == "[long" and i + 1 < len(words) and words[i + 1]["text"] == "pause]":
                groups.append(cur)
                cur, i = [], i + 2
                continue
            cur.append(w)
            i += 1
        groups.append(cur)
        for seg, g in zip(b["segs"], [g for g in groups if g]):
            out[seg] = g
    return out


def build(lang):
    sc = json.loads((PROJ / "script" / "scenes.json").read_text(encoding="utf-8"))
    plan = json.loads((PROJ / "build" / lang / "vo_plan.json").read_text(encoding="utf-8"))
    parts = json.loads((PROJ / "build" / lang / "vo" / "parts.json").read_text())
    offs, sw = _batch_offsets(lang, plan), _seg_words(lang, plan)
    text = {g["id"]: g["text"] for g in plan["segments"]}
    scenes, t = [], 0.0
    for s in sc["scenes"]:
        sid = s["id"]
        pre, post = PRE, POST
        if sid in EXTRA:
            k, v = EXTRA[sid]
            pre, post = (v, post) if k == "pre" else (pre, v)
        d = parts[sid]["dur"]
        script = text[sid].split()
        rec = sw.get(sid, [])
        if len(rec) == len(script):
            words = [dict(text=x, s=round(pre + max(0.0, w["start"] - offs[sid]), 3),
                          e=round(pre + max(0.0, w["end"] - offs[sid]), 3)) for x, w in zip(script, rec)]
        else:                                    # spread by characters if the alignment does not match the script
            tot = sum(len(x) + 1 for x in script)
            acc, words = 0, []
            for x in script:
                s0 = d * acc / tot
                acc += len(x) + 1
                words.append(dict(text=x, s=round(pre + s0, 3), e=round(pre + d * acc / tot, 3)))
        dur = pre + d + post
        scenes.append(dict(id=sid, kind=s["kind"], start=round(t, 3), dur=round(dur, 3), ost=s["ost"][lang],
                           audio=[dict(seg=sid, start=pre, dur=d, text=text[sid])], words=words,
                           images=[i.format(lang=lang) for i in s["images"]]))
        t += dur
    scenes.append(dict(id="END", kind="end", start=round(t, 3), dur=END_CARD, ost=[], audio=[], words=[], images=[]))
    t += END_CARD
    return dict(lang=lang, total=round(t, 3), scenes=scenes)


def _chunks(words, maxc):
    chunks, cur, n = [], [], 0
    for w in words:
        tx = w["text"]
        if cur and n + len(tx) + 1 > maxc * 2:
            chunks.append(cur)
            cur, n = [], 0
        cur.append(w)
        n += len(tx) + 1
        if tx[-1] in ".؟?!:؛;" and n > maxc * 0.9:
            chunks.append(cur)
            cur, n = [], 0
    if cur:
        if chunks and sum(len(w["text"]) + 1 for w in cur) < 12 and \
                sum(len(w["text"]) + 1 for w in chunks[-1]) + n <= maxc * 2 + 10:
            chunks[-1] += cur
        else:
            chunks.append(cur)
    return chunks


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


def subtitles(tl, maxc=34):
    cues = []
    for sc in tl["scenes"]:
        words = [dict(text=w["text"], s=sc["start"] + w["s"], e=sc["start"] + w["e"]) for w in sc["words"]]
        for ch in _chunks(words, maxc):
            cues.append(dict(start=round(ch[0]["s"] - 0.05, 3), end=round(ch[-1]["e"] + 0.25, 3),
                             lines=_two_lines(" ".join(w["text"] for w in ch), maxc), scene=sc["id"]))
    for i in range(len(cues) - 1):
        if cues[i]["end"] > cues[i + 1]["start"] - 0.04:
            cues[i]["end"] = round(cues[i + 1]["start"] - 0.04, 3)
    return cues


def write_srt(cues, path):
    def ts(x):
        ms = int(round(x * 1000))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    Path(path).write_text("\n".join(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n" + "\n".join(c["lines"]) + "\n"
                                    for i, c in enumerate(cues, 1)), encoding="utf-8")


if __name__ == "__main__":
    lang = sys.argv[1]
    tl = build(lang)
    out = PROJ / "build" / lang
    (out / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    cues = subtitles(tl)
    (out / "cues.json").write_text(json.dumps(cues, ensure_ascii=False, indent=1), encoding="utf-8")
    write_srt(cues, out / f"{lang}_synced.srt")
    print(f"{lang}: {len(tl['scenes'])} scenes, {tl['total']:.1f} s, {len(cues)} cues")
