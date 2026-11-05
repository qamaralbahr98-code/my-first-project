"""Edit timeline from the recorded narration: scene start/length, audio placement, word times, caption cues.

    python3 -m so.timeline ar|ckb      (run from dwin-sheikh-othman/render)

Inserted moments (CLAUDE.md): S33 opens on 7 s of the funeral clip at full level (with its subtitle);
the sheikh's lecture clip R10 stands alone between S34 and S35; S34 holds 1 s of silence before its last sentence.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

PROJ = Path(__file__).resolve().parents[2]

PRE, POST = 0.25, 0.40
# v3 (Arabic): the re-read Talabani sentences run 1.4 s longer; 60 ms less breath after each scene keeps it under 14:00
POST_LANG = {"ar": 0.34, "ckb": 0.40}
LEAD = 0.06


def quiet_before(wav, t0, t1):
    """Quietest 10 ms point of the pause between two words (where the S34 silence is inserted)."""
    sys.path.insert(0, str(PROJ / "render"))
    from splice import load, quietest
    return round(quietest(load(wav), t0, t1 + 0.02), 3)
CHAPTERS = {"S05": 2, "S16": 3, "S19": 4, "S27": 5, "S31": 6, "S33": 7}
CHAPTER_PRE = 1.6
FUNERAL_OPEN = 7.0                        # S33: first 7 s of R01 at full level
EXTRA = {"S01": ("pre", 0.9), "S04": ("post", 1.1), "S15": ("post", 0.8), "S18": ("post", 0.7), "S32": ("post", 0.6),
         "S35": ("post", 0.6)}
END_CARD = 3.5
R10_RANGE = {"ar": (0.0, 43.1), "ckb": (0.0, 43.1)}
LIMIT = 14 * 60 - 1                       # 14:00 is the hard maximum
S34_SPLIT = {"ar": "ووصيةُ", "ckb": "ئامۆژگاریی"}
# words that land the verdict stamp, per scene (first match in the scene's words)
VERDICT = {"S27": ("والوقائع", "ڕووداوەکان"), "S28": ("وهنا", "لێرەدا"), "S28b": ("والوقائع", "ڕووداوەکان"),
           "S29": ("والجواب", "وەڵامەکە"), "S30": ("وهذا", "ئەمە")}


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
        return None
    out, i = [], 0
    for x, n in zip(script, ns):
        out.append(dict(text=x, s=round(pre + rec[i]["start"], 3), e=round(pre + rec[i + n - 1]["end"], 3)))
        i += n
    return out


def chapter_titles(lang):
    md = (PROJ / "social" / f"youtube_{lang}.md").read_text(encoding="utf-8")
    lines = [re.sub(r"^\S+\s+", "", l).strip() for l in md.splitlines() if re.match(r"^\d{1,2}:\d{2}\s", l)]
    return {i + 1: t for i, t in enumerate(lines)}


def read_srt(path):
    out = []
    for b in re.split(r"\n\s*\n", Path(path).read_text(encoding="utf-8").strip()):
        ln = b.strip().splitlines()
        m = re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", ln[1])
        g = [int(x) for x in m.groups()]
        s = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        e = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        out.append(dict(s=s, e=e, text=" ".join(ln[2:]).strip()))
    return out


def clip_energy(name):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(PROJ / "assets" / name), "-f", "f32le", "-ac", "1", "-ar",
                          "16000", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)
    hop = 320                                     # 20 ms
    n = len(x) // hop
    e = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12)
    return np.convolve(e, np.ones(5) / 5, "same"), 0.02


def snap_cues(cues, name, win=1.2):
    """Align approximate cue boundaries to the quietest moment of the speech within +-win s."""
    e, hop = clip_energy(name)
    out = [dict(c) for c in cues]
    for i in range(len(out) - 1):
        b = out[i]["e"]
        a0, a1 = int(max(0, b - win) / hop), int(min(len(e) * hop, b + win) / hop)
        if a1 <= a0:
            continue
        k = a0 + int(np.argmin(e[a0:a1]))
        nb = round(k * hop, 2)
        if out[i]["s"] + 0.8 < nb < out[i + 1]["e"] - 0.8:
            out[i]["e"] = nb
            out[i + 1]["s"] = nb
    return out


def build(lang, r10=None):
    sj = json.loads((PROJ / "build" / "script.json").read_text(encoding="utf-8"))
    vo = PROJ / "build" / lang / "vo"
    # v2: narration parts after the fix pass, word times from the local forced aligner, caption text after edits
    pdir = vo / "parts_v2" if (vo / "parts_v2").exists() else vo / "parts"
    sw = json.loads((vo / ("aligned_v2.json" if (vo / "aligned_v2.json").exists() else "aligned.json")).read_text(encoding="utf-8"))
    caps = json.loads((vo / "captions_v2.json").read_text(encoding="utf-8")) if (vo / "captions_v2.json").exists() else {}

    def wav_dur(path):
        from scipy.io import wavfile
        sr, x = wavfile.read(str(path))
        return len(x) / sr
    titles = chapter_titles(lang)
    r10 = r10 or R10_RANGE[lang]
    scenes, t = [], 0.0
    for s in sj["scenes"]:
        sid = s["id"]
        pre, post = PRE, POST_LANG.get(lang, POST)
        if sid in CHAPTERS:
            pre = CHAPTER_PRE + 0.15
        if sid == "S33":
            pre = CHAPTER_PRE + FUNERAL_OPEN + 0.2
        if sid in EXTRA:
            k, v = EXTRA[sid]
            if k == "pre":
                pre = v
            else:
                post = v
        d = round(wav_dur(pdir / f"{sid}.wav"), 3)
        script = caps.get(sid, s[lang]["n"]).split()
        rec = sw[sid]
        assert len(script) == len(rec), (lang, sid, len(script), len(rec))
        # the highlight starts at the word onset, a little early (60 ms) and never late
        words = [dict(text=x, s=round(pre + max(0.0, w["start"] - LEAD), 3), e=round(pre + w["end"], 3))
                 for x, w in zip(script, rec)]
        audio = [dict(seg=sid, start=pre, dur=d, src=0.0)]
        if sid == "S34":                                   # 1 s of silence before the last sentence
            k = next(i for i, w in enumerate(words) if w["text"].startswith(S34_SPLIT[lang]))
            cut = quiet_before(pdir / f"{sid}.wav", rec[k - 1]["end"], rec[k]["start"])
            audio = [dict(seg=sid, start=pre, dur=cut, src=0.0), dict(seg=sid, start=pre + cut + 1.0, dur=d - cut, src=cut)]
            for w in words[k:]:
                w["s"] = round(w["s"] + 1.0, 3)
                w["e"] = round(w["e"] + 1.0, 3)
            d += 1.0
        dur = pre + d + post
        sc = dict(id=sid, part=s["part"], start=round(t, 3), dur=round(dur, 3), ost=s[lang]["t"].split("\n"),
                  source="" if s["source"] in ("—", "") else s["source"], chapter=CHAPTERS.get(sid),
                  chapter_title=titles.get(CHAPTERS.get(sid), ""), labels=s[lang]["labels"], audio=audio, words=words,
                  subs=[])
        if sid in VERDICT:
            key = VERDICT[sid][0 if lang == "ar" else 1]
            sc["verdict_t"] = next((w["s"] for w in words if w["text"].startswith(key)), pre + d * 0.3)
        if sid == "S33":
            sub = read_srt(PROJ / "subtitles" / "clips" / f"R01_funeral_{lang}.srt")[0]
            a = CHAPTER_PRE
            sc["subs"] = [dict(s=round(a + 0.1, 3), e=round(a + min(sub["e"], FUNERAL_OPEN - 0.1), 3), text=sub["text"])]
            sc["clip_open"] = [a, a + FUNERAL_OPEN]
        scenes.append(sc)
        t += dur
        if sid == "S34":                                   # the sheikh's own voice, standalone
            a, b = r10
            subs = snap_cues(read_srt(PROJ / "subtitles" / "clips" / f"R10_lecture_{lang}.srt"), "R10_lecture_prophet.mp4")
            subs = [dict(s=round(max(x["s"], a) - a + 0.4, 3), e=round(min(x["e"], b) - a + 0.4, 3), text=x["text"])
                    for x in subs if x["e"] > a + 0.3 and x["s"] < b]
            rd = (b - a) + 0.9
            scenes.append(dict(id="R10", part=7, start=round(t, 3), dur=round(rd, 3), ost=[], source="", chapter=None,
                               chapter_title="", labels="", audio=[], words=[], subs=subs, clip=[a, b]))
            t += rd
    scenes.append(dict(id="END", part=7, start=round(t, 3), dur=END_CARD, ost=[], source="", chapter=None,
                       chapter_title="", labels="", audio=[], words=[], subs=[]))
    t += END_CARD
    return dict(lang=lang, total=round(t, 3), scenes=scenes)


def _chunks(words, maxc):
    """Caption chunks of at most maxc characters, broken preferably at punctuation."""
    chunks, cur, n = [], [], 0
    for w in words:
        tx = w["text"]
        if cur and n + len(tx) + 1 > maxc:
            chunks.append(cur)
            cur, n = [], 0
        cur.append(w)
        n += len(tx) + 1
        if tx[-1] in ".؟?!:؛;،,…»" and n > maxc * 0.55:
            chunks.append(cur)
            cur, n = [], 0
    if cur:
        if chunks and sum(len(w["text"]) + 1 for w in cur) < 10 and \
                sum(len(w["text"]) + 1 for w in chunks[-1]) + n <= maxc + 8:
            chunks[-1] += cur
        else:
            chunks.append(cur)
    return chunks


def _split_sub(sub, maxc):
    """A clip subtitle longer than maxc is shown as consecutive parts, time shared by length."""
    words = sub["text"].split()
    if len(sub["text"]) <= maxc or "﴿" in sub["text"] and len(sub["text"]) <= maxc * 1.25:
        return [sub]
    parts, cur = [], []
    for w in words:
        if cur and len(" ".join(cur + [w])) > maxc:
            parts.append(" ".join(cur))
            cur = []
        cur.append(w)
    parts.append(" ".join(cur))
    tot = sum(len(p) for p in parts)
    out, s = [], sub["s"]
    for p in parts:
        e = s + (sub["e"] - sub["s"]) * len(p) / tot
        out.append(dict(s=round(s, 3), e=round(e, 3), text=p))
        s = e
    return out


def captions(tl, maxc):
    cues = []
    for sc in tl["scenes"]:
        words = [dict(text=w["text"], s=round(sc["start"] + w["s"], 3), e=round(sc["start"] + w["e"], 3))
                 for w in sc["words"]]
        subs = []
        for sb in sc.get("subs", []):
            for p in _split_sub(sb, maxc * 2 - 6):
                subs.append(dict(start=round(sc["start"] + p["s"], 3), end=round(sc["start"] + p["e"], 3),
                                 words=[], text=p["text"], scene=sc["id"], plain=True, quran="﴿" in p["text"]))
        cues += subs
        for ch in _chunks(words, maxc):
            cues.append(dict(start=round(ch[0]["s"] - 0.05, 3), end=round(ch[-1]["e"] + 0.3, 3), words=ch,
                             text=" ".join(w["text"] for w in ch), scene=sc["id"]))
    cues.sort(key=lambda c: c["start"])
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
    """SRT for upload: up to two lines per cue (narration and the clips' subtitles)."""
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
    if tl["total"] > LIMIT and lang == "ckb":
        tl = build(lang, (4.1, 43.1))                    # allowed by CLAUDE.md for the Sorani cut
    out = PROJ / "build" / lang
    (out / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    for fmt, maxc in (("16x9", 46), ("9x16", 26)):
        (out / f"cues_{fmt}.json").write_text(json.dumps(captions(tl, maxc), ensure_ascii=False, indent=1),
                                              encoding="utf-8")
    write_srt(tl, out / f"{lang}_synced.srt")
    m, s = divmod(tl["total"], 60)
    print(f"{lang}: {len(tl['scenes'])} scenes, {tl['total']:.1f} s = {int(m)}:{s:04.1f}"
          + ("  OVER LIMIT" if tl["total"] > LIMIT else ""))
