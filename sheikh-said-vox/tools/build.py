#!/usr/bin/env python3
"""Build the Vox-style production prompts, narration scripts, subtitles and asset list
from script/master.json + script/brand.json.

Usage:
    python3 tools/build.py          # check + build
    python3 tools/build.py --check  # checks only

Generated (never edit by hand): prompts/*.md, script/scenes.*.json, vo/*.txt,
subtitles/*.srt, assets/ASSETS.md, facts/fact_check.md
"""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
M = json.loads((ROOT / "script/master.json").read_text(encoding="utf-8"))
B = json.loads((ROOT / "script/brand.json").read_text(encoding="utf-8"))

LANGS = {
    "ckb": {"name": "Kurdish Sorani", "file": "01_sorani.md", "dir": "rtl", "script": "Arabic script, Sorani orthography", "wps": 2.2, "sub_chars": 40},
    "kmr": {"name": "Kurdish Kurmanji", "file": "02_kurmanji.md", "dir": "ltr", "script": "Latin script, Hawar alphabet", "wps": 2.3, "sub_chars": 42},
    "ar":  {"name": "Arabic", "file": "03_arabic.md", "dir": "rtl", "script": "Arabic script, Modern Standard Arabic", "wps": 2.1, "sub_chars": 40},
}
PAD = 0.8          # breathing room after each VO line (s)
CHAPTER_CARD = 2.0 # chapter title card length (s)
QUOTE_SLOW = 0.88  # quotes are read slower
OST_MAX = {"ckb": 46, "kmr": 48, "ar": 46}


# ------------------------------------------------------------------ checks
def check():
    errs, warns = [], []
    fids = {f["id"] for f in M["facts"]}
    aids = {a["id"] for a in M["assets"]}
    chs = {c["id"] for c in M["chapters"]}
    seen, last = set(), 0
    for s in M["scenes"]:
        i = s["id"]
        if i in seen: errs.append(f"{i}: duplicate id")
        seen.add(i)
        if s["chapter"] not in chs: errs.append(f"{i}: unknown chapter")
        if s["chapter"] < last: errs.append(f"{i}: chapter order")
        last = s["chapter"]
        for lang in LANGS:
            if s["kind"] != "end" and not s["vo"].get(lang): errs.append(f"{i}/{lang}: missing VO")
            if not s["ost"].get(lang): errs.append(f"{i}/{lang}: missing on-screen text")
            for ln in s["ost"].get(lang, []):
                if len(ln) > OST_MAX[lang]: warns.append(f"{i}/{lang}: on-screen line {len(ln)} chars: {ln}")
        for r in s.get("facts", []):
            if r not in fids: errs.append(f"{i}: unknown fact {r}")
        for a in s.get("assets", []):
            if a not in aids: errs.append(f"{i}: unknown asset {a}")
        if s["kind"] not in ("end", "title", "position") and not s.get("facts"):
            errs.append(f"{i}: scene without facts")
        if "F36" in s.get("facts", []) and s["kind"] != "position":
            errs.append(f"{i}: opinion fact F36 outside the position card")
        if s["kind"] == "position" and s.get("tag") != "position_tag":
            errs.append(f"{i}: position card needs position_tag")
        if re.search(r"\b10\b", s["vo_en"]) and "Article 10" in s["vo_en"]:
            errs.append(f"{i}: check article number")
    for i in ("S05", "S17", "S31"):
        pass
    return errs, warns


# ------------------------------------------------------------------ timing
def duration(s, lang):
    if s.get("fixed_duration"): return s["fixed_duration"]
    words = len(s["vo"][lang].split())
    rate = LANGS[lang]["wps"] * (QUOTE_SLOW if s["voice"] == "quote" else 1)
    return round(max(words / rate + PAD, 3.0), 1)


def timeline(lang):
    titled = {c["id"] for c in M["chapters"] if c["title"]}
    t, out, prev = 0.0, [], None
    for s in M["scenes"]:
        card = s["chapter"] != prev and s["chapter"] in titled
        if card: t += CHAPTER_CARD
        d = duration(s, lang)
        out.append({**s, "chapter_card": card, "start": round(t, 1), "end": round(t + d, 1), "duration": d})
        t += d
        prev = s["chapter"]
    return out, round(t, 1)


def ts(x, srt=False):
    if srt:
        total_ms = int(round(x * 1000))
        h, rem = divmod(total_ms, 3_600_000); m, rem = divmod(rem, 60_000); sec, ms = divmod(rem, 1000)
        return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"
    h, r = divmod(x, 3600); m, sec = divmod(r, 60)
    return f"{int(m):02d}:{sec:04.1f}"


# ------------------------------------------------------------------ subtitles
def wrap(sentence, maxc):
    lines, cur = [], ""
    for w in sentence.split():
        if cur and len(cur) + len(w) + 1 > maxc:
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur: lines.append(cur)
    # balance the last two lines so no line is a lonely word
    if len(lines) >= 2 and len(lines[-1]) < maxc * 0.35:
        words = (lines[-2] + " " + lines[-1]).split()
        half = len(" ".join(words)) / 2
        a, b = [], []
        for w in words:
            (a if len(" ".join(a + [w])) <= half + 4 or not a else b).append(w)
        lines[-2:] = [" ".join(a), " ".join(b)]
    return lines


def chunks(text, maxc):
    """Subtitle cards: never mix two sentences in one card, max 2 lines, no orphan words."""
    sentences = [s for s in re.split(r"(?<=[\.\!\?؟»:])\s+", text) if s]
    cards = []
    for snt in sentences:
        lines = wrap(snt, maxc)
        for i in range(0, len(lines), 2):
            cards.append(lines[i:i + 2])
    # merge a 1-line card of a short sentence with the previous 1-line card
    out = []
    for c in cards:
        if out and len(out[-1]) == 1 and len(c) == 1 and len(out[-1][0]) + len(c[0]) < maxc * 1.6:
            out[-1] = out[-1] + c
        else:
            out.append(c)
    return ["\n".join(c) for c in out]


def srt(lang):
    scenes, _ = timeline(lang)
    n, lines = 1, []
    for s in scenes:
        text = s["vo"][lang]
        if not text: continue
        cs = chunks(text, LANGS[lang]["sub_chars"])
        total = sum(len(c) for c in cs)
        t = s["start"] + 0.15
        span = s["duration"] - PAD + 0.3
        for c in cs:
            d = span * len(c) / total
            lines += [str(n), f"{ts(t, True)} --> {ts(t + d - 0.05, True)}", c, ""]
            n += 1; t += d
    return "\n".join(lines)


# ------------------------------------------------------------------ prompt
def spec(lang):
    L, F, C = LANGS[lang], B["fonts"][lang], B["colors"]
    lab = M["labels"]
    side = "right" if L["dir"] == "rtl" else "left"
    return f"""## 4. Technical specification

### 4.1 Format
- Master: **16:9, 1920 × 1080, 24 fps**, progressive. Deliver `dwin_sheikh_said_{lang}_16x9_v01.mp4`.
- Optional vertical cut-down for Reels/TikTok: 1080 × 1920; reframe each shot (photos centred, maps re-laid out vertically); keep every on-screen text inside the central 1080 × 1350 area.
- Export H.264 High, 16–20 Mbps VBR, `yuv420p`, AAC 48 kHz stereo 320 kbps, `+faststart`. Loudness **−14 LUFS** integrated, true peak ≤ −1 dBTP.

### 4.2 The Vox look (apply to every scene)
- **Paper world:** everything lives on warm parchment paper (`#EFE6D4` base, subtle fibre texture, soft shadows). Photos are cut out with torn or straight paper edges and a 4–6 px drop shadow, as if pinned to a desk.
- **Archival treatment:** historic photos are restored (dust removal, gentle sharpening), kept in their original sepia/black-and-white. Never colourise them. Add 2.5D parallax (separate subject from background) with slow pushes of 3–6% per shot.
- **Annotations:** hand-drawn ink circles, arrows and underlines that draw on (8–12 frames); gold highlighter strokes behind key words; red ink only for loss, ban and betrayal.
- **Maps:** clean vector maps (Natural Earth) printed on the paper; rivers in muted blue, borders in thin dashed ink; animated dotted routes (2 px dots, gold) that draw along the path; pins drop with a small bounce; labels write on.
- **Data:** bar charts and counters drawn on paper, bars to scale, numbers in bold; uncertain or attributed numbers always carry their label on screen.
- **Case board:** chapters 5–6 use a dark cork board with pinned paper notes and red/gold string to show who connects to whom.
- **Pull-quotes:** large quote marks in gold, the quote typed word by word, the speaker's portrait behind at 15–20% opacity.
- **Transitions:** paper slide, paper tear, page turn and match-cuts on shapes. No flashy digital wipes. Light leaks and film grain (6–8%) on everything.
- **Image labels:** every AI-generated image and every painting shows **{lab['illustration'][lang]}**; every colourised photo shows **{lab['colourised'][lang]}** (small, bottom-{side} corner, 60% opacity). Never present an AI image or a painting as a real photograph. Each scene below names its images and label.
- **Image quality:** all images are at least 2048 px on the long side (small AI images were upscaled 4× with Real-ESRGAN; archival photos were enlarged without AI so no detail is invented). Most images are portrait or square: use them as pinned paper cut-outs with parallax, or crop to 16:9 only where the subject allows; never stretch.
- **Violence:** imply, don't show. No executions, bodies, blood or weapons in close-up. Use sound, light flickers and ink effects instead.

### 4.3 Typography ({L['name']})
- Language and script: **{L['name']}**, {L['script']}; direction **{L['dir'].upper()}**.
- Font: **{F['name']} {F['weight']}** (fallback **{F['fallback']}**). Check these letters render correctly before rendering: `{F['must_render']}`.
- The Qur'anic verse in S51 is set in a proper Arabic Naskh/Thuluth font with full vowel marks, exactly as written.
- Digits: Western (0–9) exactly as in the script.
- Sizes on 1920 × 1080: chapter titles 96 px, on-screen labels 54 px, dates 64 px, quotes 60 px, map labels 30 px, subtitles 40 px.
- Colours (`script/brand.json`): ink `#1E1A16`, gold `{C['gold']}`, dark green `{C['green']}`, cream `{C['cream']}`, red ink `#9E2B25`.

### 4.4 Chapter cards
- {CHAPTER_CARD:.0f} s each: big chapter number in gold, chapter title in ink on a fresh sheet of paper that slides in. Titles are listed in section 5.

### 4.5 Narration (audio)
- One narrator per language: male, 35–55, warm, calm and authoritative, like a documentary storyteller; conversational pace (about {L['wps']} words per second), clear diction, no exaggerated drama.
- **Quote voice:** the Sheikh's words (scenes marked *quote*) are read by a second, older male voice, slower and lower, with a light room reverb. Lines spoken by Turkish officers or İsmet Pasha are read by the narrator in a neutral tone: no foreign accents, no caricature.
- Recording: 48 kHz / 24-bit WAV, quiet room, pop filter; edit breaths, de-ess, light compression; narration peaks around −6 dBFS before the mix.
- The narration text is in `vo/{lang}_narration.txt` (one block per scene). Read it exactly; do not paraphrase.
- If you use text-to-speech instead of a human narrator, choose a voice that pronounces {L['name']} natively and have a native speaker approve every line before the edit.

### 4.6 Music and sound
- Royalty-free cinematic score with regional colour (tembûr, oud, ney, daf, strings); no lyrics. Chapter moods are listed with each chapter in section 5.
- Music sits at −20 dB under narration (−24 dB under quotes) and rises to −12 dB in gaps.
- Sound design (per scene in section 5): paper slides, pen and highlighter, typewriter for quotes, map whooshes and pin pops, horses, wind, room tones. Never use cheap cartoon sounds. No call to prayer as background music.

### 4.7 Subtitles
- Burn in subtitles for social versions using `subtitles/{lang}.srt` (timed to the narration estimate; re-sync to the final recording). 40 px, cream text on a 60% black box, bottom centre, max 2 lines.
- Keep subtitles and on-screen labels from overlapping: labels sit in the upper two thirds.

### 4.8 Branding
- Dwin logo top-{'left'} at 90 px wide, 70% opacity, on every scene except chapter cards and the end card.
- **No sources slide at the end.** Sources go in the post description and in `facts/fact_check.md`. Photo credits for licensed images go in the description too (or as tiny 18 px credits on the image if the licence requires it).
"""


def editorial():
    return """## 2. Editorial rules (non-negotiable)
1. **Use the narration and on-screen text exactly as written** in section 5. Do not translate, shorten, add or "improve". If something seems wrong, stop and flag it.
2. **Everything in the article is in the script.** Do not cut scenes. If you must shorten, ask first.
3. **Numbers stay honest.** The article's "600,000 vs 100,000" is shown as *a statistic of the time* and followed straight away by the historians' estimate (about 10,000 at Amed). The article's "200 thousand horsemen" at Lice is deliberately left out (not credible). Dates follow the article; where other sources differ (the Piran clash, the capture date), the script avoids exact days.
4. **Quotes are attributed.** Sheikh Said's sayings carry the "attributed" tag; the prison dialogue is told as the article tells it.
5. **Respect for all peoples.** The film honours Kurdish courage and the Kurds' place in the Islamic ummah. It never insults Turks or Arabs as peoples. The criticism is of policies of denial, not of nations.
6. **Opinion is labelled.** Dwin's condemnation appears only in the position card (S52), with the Dwin position tag, and names no individual or group.
7. **No sources slide at the end.** Credits and sources go in the description.
"""


def strategy():
    return """## 3. How the message is delivered
- **Cold open (S01–S03):** start at the end, dawn on 29 June 1925, and his unshaken words. The viewer must want to know how a scholar got there.
- **Who he was (ch. 2):** a Naqshbandi scholar, not a warlord: faith first.
- **The ummah frame (ch. 3):** for Arab and Turkish viewers, establish early that Kurds were always at the heart of the Muslim world: Salahuddin, Gallipoli, the War of Independence. This makes the broken promise (ch. 4) feel like a betrayal of brotherhood, not an ethnic quarrel.
- **Causes as a list (ch. 4):** each cause gets its own beat, graphic and sound, so the viewer counts them.
- **Investigation (ch. 5):** the case board turns the secret organisation into a detective story.
- **Action (ch. 6–7):** maps and cavalry; tension peaks at the Mardin Gate.
- **Dignity (ch. 8–10):** betrayal, then the prison dialogue: the emotional heart. Slow down, near silence.
- **Legacy and bridge (ch. 11–12):** his words, then the message to the ummah today, closing with Qur'an 49:13.
- **Position and close (ch. 13):** Dwin's labelled condemnation of misleading propaganda; bookend with his portrait; end card.
"""


def scene_block(s, lang):
    L = LANGS[lang]
    out = []
    head = f"### {s['id']} · {ts(s['start'])}–{ts(s['end'])} ({s['duration']} s) · {s['kind']}"
    if s["voice"] == "quote": head += " · **quote voice**"
    out.append(head)
    out.append("")
    if s["vo"][lang]:
        out.append(f"**Narration ({L['name']})** — read exactly:")
        out += ["", "```text", s["vo"][lang], "```"]
    out.append(f"**On-screen text** — {len(s['ost'][lang])} line(s), copy exactly:")
    out += ["", "```text", *s["ost"][lang], "```"]
    if s.get("tag"): out.append(f"- Tag on screen: **{M['labels'][s['tag']][lang]}**")
    if s["vo_en"]: out.append(f"- Meaning (English, editor only): {s['vo_en']}")
    for i, v in enumerate(s["visual"], 1): out.append(f"- Visual {i}: {v}")
    if s.get("assets"): out.append(f"- Assets: {', '.join(s['assets'])} (see `assets/ASSETS.md`)")
    IM = {i["file"]: i for i in M.get("images", [])}
    for f in s.get("images", []):
        i = IM[f]
        if i.get("lang") and i["lang"] != lang: continue
        lab = {"ai": M["labels"]["illustration"][lang], "painting": M["labels"]["illustration"][lang],
               "colourised": M["labels"]["colourised"][lang]}.get(i["type"])
        line = f"- Image: `{f}` ({i['type']}" + (f"; on-screen label **{lab}**" if lab else "") + ")"
        if i["note"]: line += f" — {i['note']}"
        out.append(line)
    out.append(f"- Sound: {s['sfx']}")
    if s.get("facts"): out.append(f"- Fact check: {', '.join(s['facts'])}")
    out.append("")
    return "\n".join(out)


def prompt(lang):
    L = LANGS[lang]
    scenes, total = timeline(lang)
    ch = {c["id"]: c for c in M["chapters"]}
    h = f"""# Dwin Vox-style documentary prompt — {L['name']} — Sheikh Said Piran

> Generated by `tools/build.py` from `script/master.json`. Edit the sources, not this file.
> Timed data: `script/scenes.{lang}.json` · Narration: `vo/{lang}_narration.txt` · Subtitles: `subtitles/{lang}.srt` · Assets: `assets/ASSETS.md`

**Title (on-screen language):** {M['project']['titles'][lang]}
**Estimated length:** {ts(total)} ({total} s), {len(scenes)} scenes, {len(M['chapters'])} chapters. Final length follows the recorded narration.
**Source:** {M['project']['source_article_note']}; sources are listed in `facts/fact_check.md`.

## 1. Role and goal
You are the senior editor, motion designer and sound designer of **Dwin** ({B['channels'][lang]}). Produce a **Vox-style explainer documentary with narration** in **{L['name']}** about Sheikh Said Piran (1865–1925): who he was, why he rose up, how the revolt unfolded, his betrayal, his dignity in prison and his execution.

Focus: the **history and the courage of the Kurds**, and a clear message, especially for Arab and Turkish viewers, that **the Kurds have always stood with the Islamic ummah** and still do. The film must be visually rich (mostly archival photos, maps and animated paper graphics) and attractive from the first second.

This prompt is in English. **Only the narration and the on-screen text are in {L['name']}.**

"""
    body = [h, editorial(), strategy(), spec(lang), f"## 5. Scene-by-scene script ({L['name']})\n",
            "Timings are estimates from the narration length; re-time to the recorded voice. Chapter cards are included in the timings.\n"]
    cur = None
    for s in scenes:
        if s["chapter"] != cur:
            cur = s["chapter"]; c = ch[cur]
            t = f" — chapter card: **{c['title'][lang]}**" if c["title"] else ""
            body.append(f"\n---\n\n#### Chapter {cur}: {c['name_en']}{t}\n\n*Music:* {c['music']}\n")
        body.append(scene_block(s, lang))
    body.append(f"""## 6. Post description ({L['name']})

```text
{M['post_caption'][lang]}
```

## 7. Quality checklist
- [ ] Narration recorded exactly from `vo/{lang}_narration.txt`, approved by a native {L['name']} speaker.
- [ ] Every on-screen line matches section 5 character for character.
- [ ] Font renders all special letters; the Qur'anic verse has correct vowel marks.
- [ ] "Statistic of the time" label and historians' estimate both visible in S31.
- [ ] Illustration label on every AI image and painting; colourised label on every colourised photo.
- [ ] The language-specific calendar images are used in S23 and S29.
- [ ] No executions, bodies or blood on screen.
- [ ] Position tag on S52 only; no sources slide at the end.
- [ ] Subtitles re-synced to the final narration; no overlap with on-screen labels.
- [ ] Loudness −14 LUFS, true peak ≤ −1 dBTP.
- [ ] Image licences checked (`assets/ASSETS.md`); required credits in the description.

## 8. Facts behind the scenes
""")
    for f in M["facts"]:
        body.append(f"- **{f['id']}** — {f['claim_en']} *({f['status']}; {f['source']})*")
    return "\n".join(body) + "\n"


def narration(lang):
    scenes, total = timeline(lang)
    out = [f"# {LANGS[lang]['name']} narration — Sheikh Said Piran (Dwin)", f"# Estimated {ts(total)}. [Q] = quote voice. Read exactly as written.", ""]
    for s in scenes:
        if not s["vo"][lang]: continue
        tag = "[Q] " if s["voice"] == "quote" else ""
        out += [f"## {s['id']} {tag}", s["vo"][lang], ""]
    return "\n".join(out)


def assets_md():
    used = {}
    for s in M["scenes"]:
        for a in s.get("assets", []): used.setdefault(a, []).append(s["id"])
    rows = ["# Assets", "", "Images and footage the edit needs. Your image pack goes in `assets/images/`.", "",
            "| ID | What | File / where to find it | Licence note | Used in |", "| --- | --- | --- | --- | --- |"]
    for a in M["assets"]:
        rows.append(f"| {a['id']} | {a['what']} | {a.get('file') or a['where']} | {a['license']} | {', '.join(used.get(a['id'], []))} |")
    rows += ["", "## Provided image pack (`assets/images/`)", "",
             "Labels: AI images and paintings show the illustration label on screen; colourised photos show the colourised label; archival photos need none.", "",
             "| File | Type | Size | Scenes | Note |", "| --- | --- | --- | --- | --- |"]
    for i in M.get("images", []):
        rows.append(f"| `{i['file']}` | {i['type']} | {i['size']} | {', '.join(i['scenes'])} | {i['note']} |")
    missing = [x["id"] for x in M["scenes"] if not x.get("images") and x["kind"] not in ("map", "data", "doc", "title", "position", "end", "quote")]
    rows += ["", "Scenes that still need picture material (beyond drawn maps and graphics): " + (", ".join(missing) or "none")]
    return "\n".join(rows) + "\n"


def fact_md():
    used = {}
    for s in M["scenes"]:
        for r in s.get("facts", []): used.setdefault(r, []).append(s["id"])
    rows = ["# Fact check", "", "| ID | Fact | Status | Source | Scenes |", "| --- | --- | --- | --- | --- |"]
    for f in M["facts"]:
        rows.append(f"| {f['id']} | {f['claim_en']} | {f['status']} | {f['source']} | {', '.join(used.get(f['id'], []))} |")
    rows += ["", "## Corrections and choices",
             "- **200 thousand horsemen (article, Lice, 11 Feb):** omitted. Not credible; historians estimate about 10,000 rebels at the height of the siege.",
             "- **600,000 vs 100,000 (article):** kept, labelled 'a statistic of the time', followed by the historians' estimate.",
             "- **Piran clash date:** article implies the night of 5 February; other sources give 8 or 13 February. The script says 'that same night' without a date.",
             "- **Capture date:** article says end of April; some sources say mid-April. The script keeps the article's wording.",
             "- **Execution:** 29 June 1925 in Diyarbakır (article and most sources). One French source gives 4 September; not used.",
             "- **Sheikh Said's brother at Lice:** spelled 'شێخ تایەر' in the article; confirm the name before publishing.",
             "- **Mountain name in the article (p.5):** unclear in the scan; omitted.",
             "", "## External sources used",
             "- Les Clés du Moyen-Orient, 'La révolte de Sheikh Said (13 février – 27 avril 1925)': https://www.lesclesdumoyenorient.com/La-revolte-de-Sheikh-Said-13-fevrier-27-avril-1925-entre-nationalisme-islamisme-3338.html",
             "- Executed Today, '1925: Sheikh Said Piran, Kurdish rebel': https://www.executedtoday.com/tag/caliphate/",
             "- KRG–UN joint press statement, 30 Aug 2014 (ReliefWeb): https://reliefweb.int/report/iraq/joint-press-statement-krg-united-nations-kurdistan-region-iraq-kr-i-most-affected-recent",
             "- Iraq Business News, 'KRG calls for urgent help…', 1 Feb 2017: https://www.iraq-businessnews.com/2017/02/01/krg-calls-for-urgent-help-to-avert-humanitarian-catastrophe/",
             "- Robert Olson, The Emergence of Kurdish Nationalism and the Sheikh Said Rebellion, 1880–1925 (UBC Press): https://ubcpress.ca/the-emergence-of-kurdish-nationalism-and-the-sheikh-said-rebellion-1880-1925",
             "- Treaty of Sèvres (1920), Part III Section III, Articles 62–64; Treaty of Lausanne (24 July 1923).",
             "- Qur'an 49:13 (al-Hujurat)."]
    return "\n".join(rows) + "\n"


def main():
    errs, warns = check()
    for w in warns: print("warning:", w)
    for e in errs: print("ERROR:", e)
    if errs: sys.exit(1)
    if "--check" in sys.argv: print("checks passed"); return
    for d in ("prompts", "vo", "subtitles", "facts", "assets"): (ROOT / d).mkdir(exist_ok=True)
    for lang, L in LANGS.items():
        scenes, total = timeline(lang)
        (ROOT / "prompts" / L["file"]).write_text(prompt(lang), encoding="utf-8")
        (ROOT / "vo" / f"{lang}_narration.txt").write_text(narration(lang), encoding="utf-8")
        (ROOT / "subtitles" / f"{lang}.srt").write_text(srt(lang), encoding="utf-8")
        data = {"lang": lang, "language": L["name"], "direction": L["dir"], "total_seconds": total, "format": M["project"]["format"],
                "brand": {"colors": B["colors"], "font": B["fonts"][lang], "channel": B["channels"][lang]},
                "chapters": [{"id": c["id"], "name_en": c["name_en"], "title": c["title"][lang] if c["title"] else None, "music": c["music"]} for c in M["chapters"]],
                "scenes": [{"id": s["id"], "chapter": s["chapter"], "chapter_card": s["chapter_card"], "start": s["start"], "end": s["end"],
                            "kind": s["kind"], "voice": s["voice"], "narration": s["vo"][lang], "on_screen": s["ost"][lang],
                            "tag": M["labels"][s["tag"]][lang] if s.get("tag") else None, "visual": s["visual"], "assets": s.get("assets", []),
                            "sfx": s["sfx"], "facts": s.get("facts", [])} for s in scenes],
                "post_description": M["post_caption"][lang]}
        (ROOT / "script" / f"scenes.{lang}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{lang}: {len(scenes)} scenes, {ts(total)} -> prompts/{L['file']}")
    (ROOT / "assets" / "ASSETS.md").write_text(assets_md(), encoding="utf-8")
    (ROOT / "facts" / "fact_check.md").write_text(fact_md(), encoding="utf-8")
    print("assets/ASSETS.md, facts/fact_check.md written")


if __name__ == "__main__":
    main()
