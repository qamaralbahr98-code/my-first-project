"""Build the edit timeline from the recorded narration: scene start/end, audio placement, subtitle cues.

Scene length = (chapter card) + lead-in + its narration clip(s) + a short tail. Subtitle cues use the
ElevenLabs word timings, so they follow the actual voice.
"""
import json
import re
import sys
from pathlib import Path

PROJ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJ / "render"))
import vo_split  # noqa: E402

CARD = 2.2           # chapter card length
PRE = 0.45           # silence before a scene's narration
GAP_AQ = 0.30        # between a narrator lead-in and the quote voice
POST = 0.55          # after a scene's narration
EXTRA = {"S01": ("pre", 1.6), "S43": ("post", 3.2), "S45": ("post", 1.2), "S51": ("post", 1.0),
         "S53": ("post", 1.6), "S03": ("post", 0.6), "S37": ("post", 0.5), "S52": ("post", 0.6)}
END_CARD = 6.0
QUOTE_SCALE = 1 / (0.971 * 0.97)   # vo_split slows the quote voice by this factor


def load_master():
    return json.loads((PROJ / "script" / "master.json").read_text(encoding="utf-8"))


def build(lang):
    m = load_master()
    plan = json.loads((PROJ / "build" / lang / "vo_plan.json").read_text(encoding="utf-8"))
    parts = json.loads((PROJ / "build" / lang / "vo" / "parts.json").read_text())
    segs_by_scene = {}
    for g in plan["segments"]:
        segs_by_scene.setdefault(g["scene"], []).append(g)
    chapters = {c["id"]: c for c in m["chapters"]}
    first_in_chapter = {}
    for s in m["scenes"]:
        first_in_chapter.setdefault(s["chapter"], s["id"])

    scenes, t = [], 0.0
    for s in m["scenes"]:
        sid = s["id"]
        card = CARD if (first_in_chapter[s["chapter"]] == sid and chapters[s["chapter"]].get("title")) else 0.0
        pre, post = PRE, POST
        if sid in EXTRA:
            k, v = EXTRA[sid]
            if k == "pre":
                pre = v
            else:
                post = v
        audio, a = [], card + pre
        for i, g in enumerate(segs_by_scene.get(sid, [])):
            if i:
                a += GAP_AQ
            d = parts[g["id"]]["dur"]
            audio.append(dict(seg=g["id"], voice=g["voice"], start=round(a, 3), dur=d, text=g["text"]))
            a += d
        dur = (a + post) if audio else END_CARD
        scenes.append(dict(id=sid, chapter=s["chapter"], kind=s["kind"], start=round(t, 3), dur=round(dur, 3),
                           card=card, chapter_title=chapters[s["chapter"]].get("title"),
                           ost=s["ost"][lang], audio=audio))
        t += dur
    return dict(lang=lang, total=round(t, 3), scenes=scenes)


# ------------------------------------------------------------------ subtitles
def _batch_offsets(lang, plan):
    """Re-run the deterministic split to know where each part sits inside its batch recording."""
    vo = PROJ / "build" / lang / "vo"
    offs = {}
    for b in plan["batches"]:
        af = "asetrate=48000*0.971,aresample=48000,atempo=0.97" if b["voice"] == "quote" else None
        x = vo_split.load(vo / f"{b['name']}_t1.mp3", af)
        parts, _, _ = vo_split.split(x, len(b["segs"]))
        for seg, (a, e, g) in zip(b["segs"], parts):
            offs[seg] = (b["name"], a - 0.06, b["voice"])
    return offs


def _seg_words(lang, plan):
    """Words (with times in the original batch recording) for each segment."""
    vo = PROJ / "build" / lang / "vo"
    out = {}
    for b in plan["batches"]:
        words = json.loads((vo / f"{b['name']}_words.json").read_text(encoding="utf-8"))["words"]
        groups, cur, i = [], [], 0
        while i < len(words):
            w = words[i]
            if w["text"] == "[long" and i + 1 < len(words) and words[i + 1]["text"] == "pause]":
                groups.append(cur)
                cur = []
                i += 2
                continue
            if not (w["text"].startswith("[") or w["text"].endswith("]")):
                cur.append(w)
            i += 1
        groups.append(cur)
        for seg, g in zip(b["segs"], [g for g in groups if g]):
            out[seg] = g
    return out


def _chunks(words, maxc):
    """Split a word list into subtitle chunks of at most two lines of ~maxc characters, breaking at punctuation."""
    chunks, cur, n = [], [], 0
    for w in words:
        t = w["text"]
        if cur and n + len(t) + 1 > maxc * 2:
            chunks.append(cur)
            cur, n = [], 0
        cur.append(w)
        n += len(t) + 1
        if t[-1] in ".؟?!:؛;" and n > maxc * 0.9:
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
        a, b = " ".join(words[:i]), " ".join(words[i:])
        score = max(len(a), len(b))
        if best is None or score < best:
            best, bi = score, i
    return [" ".join(words[:bi]), " ".join(words[bi:])]


def subtitles(lang, tl, maxc=40):
    plan = json.loads((PROJ / "build" / lang / "vo_plan.json").read_text(encoding="utf-8"))
    offs = _batch_offsets(lang, plan)
    sw = _seg_words(lang, plan)
    cues = []
    for sc in tl["scenes"]:
        for a in sc["audio"]:
            words = sw.get(a["seg"], [])
            batch, src0, voice = offs[a["seg"]]
            scale = QUOTE_SCALE if voice == "quote" else 1.0
            base = sc["start"] + a["start"]
            # the text shown is the script text, word for word; timings come from the aligned words
            script_words = a["text"].split()
            if 0 < len(words) < len(script_words) and \
                    [w["text"] for w in words] == script_words[:len(words)]:
                # the recording stops early (S43: the last sentence was refused by the TTS filter):
                # time the spoken words from the voice, show the rest as text right after them
                spoken = [dict(text=x, s=base + max(0.0, w["start"] * scale - src0),
                               e=base + max(0.0, w["end"] * scale - src0)) for x, w in zip(script_words, words)]
                t_end = spoken[-1]["e"] + 0.15
                rest = script_words[len(words):]
                tail = [dict(text=x, s=t_end, e=t_end + 1.8) for x in rest]
                words = spoken + tail
            elif len(script_words) != len(words):
                # fall back: spread the script words over the clip by character count
                tot = sum(len(x) + 1 for x in script_words)
                acc, words = 0, []
                for x in script_words:
                    s0 = a["dur"] * acc / tot
                    acc += len(x) + 1
                    words.append(dict(text=x, s=base + s0, e=base + a["dur"] * acc / tot))
            else:
                words = [dict(text=x, s=base + max(0.0, w["start"] * scale - src0), e=base + max(0.0, w["end"] * scale - src0))
                         for x, w in zip(script_words, words)]
            for ch in _chunks(words, maxc):
                text = " ".join(w["text"] for w in ch)
                cues.append(dict(start=round(ch[0]["s"] - 0.05, 3), end=round(ch[-1]["e"] + 0.25, 3),
                                 lines=_two_lines(text, maxc), scene=sc["id"]))
    for i in range(len(cues) - 1):          # no overlaps
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
    out = []
    for i, c in enumerate(cues, 1):
        out.append(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n" + "\n".join(c["lines"]) + "\n")
    Path(path).write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) > 1 else "ar"
    tl = build(lang)
    out = PROJ / "build" / lang
    (out / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    cues = subtitles(lang, tl)
    (out / "cues.json").write_text(json.dumps(cues, ensure_ascii=False, indent=1), encoding="utf-8")
    write_srt(cues, out / f"{lang}_synced.srt")
    print(f"{lang}: {len(tl['scenes'])} scenes, {tl['total']:.1f} s ({tl['total'] / 60:.1f} min), {len(cues)} cues")
