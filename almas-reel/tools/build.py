#!/usr/bin/env python3
"""Build the three language prompts and timed card files from script/master.json.

Usage:
    python3 tools/build.py          # check + build
    python3 tools/build.py --check  # only run the checks

Source of truth: script/master.json (content) and script/brand.json (colours, fonts).
Generated (do not edit by hand): prompts/*.md, script/cards.*.json, facts/fact_check.md
"""
import json, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
M = json.loads((ROOT / "script/master.json").read_text(encoding="utf-8"))
B = json.loads((ROOT / "script/brand.json").read_text(encoding="utf-8"))
LANGS = {
    "ckb": {"name": "Kurdish Sorani", "file": "01_sorani.md", "dir": "rtl", "align": "right", "script": "Arabic script (Sorani orthography)"},
    "kmr": {"name": "Kurdish Kurmanji", "file": "02_kurmanji.md", "dir": "ltr", "align": "left", "script": "Latin script (Hawar alphabet)"},
    "ar":  {"name": "Arabic", "file": "03_arabic.md", "dir": "rtl", "align": "right", "script": "Arabic script (Modern Standard Arabic)"},
}
MAX_CHARS = {"ckb": 36, "kmr": 40, "ar": 36}
FLASH = 0.5
STYLE_NAMES = {"A": "stacked boxes", "B": "big number", "C": "Dwin position", "S": "sources", "E": "end card"}


# ---------------------------------------------------------------- checks
def check():
    errors, warnings = [], []
    fact_ids = {f["id"] for f in M["facts"]}
    chapters = {c["id"] for c in M["chapters"]}
    seen = set()
    last_ch = 0
    for c in M["cards"]:
        cid = c["id"]
        if cid in seen: errors.append(f"{cid}: duplicate id")
        seen.add(cid)
        if c["chapter"] not in chapters: errors.append(f"{cid}: unknown chapter {c['chapter']}")
        if c["chapter"] < last_ch: errors.append(f"{cid}: chapters out of order")
        last_ch = c["chapter"]
        if c["style"] not in STYLE_NAMES: errors.append(f"{cid}: unknown style {c['style']}")
        for lang in LANGS:
            lines = c["text"].get(lang)
            if not lines: errors.append(f"{cid}: missing {lang} text"); continue
            if len(lines) > 4: errors.append(f"{cid}/{lang}: more than 4 lines")
            if c.get("highlight") is not None and c["highlight"] >= len(lines):
                errors.append(f"{cid}/{lang}: highlight index {c['highlight']} out of range")
            for ln in lines:
                if c["style"] in "AB" and len(ln) > MAX_CHARS[lang]:
                    warnings.append(f"{cid}/{lang}: line is {len(ln)} chars (> {MAX_CHARS[lang]}), font will auto-shrink: {ln}")
        for r in c.get("fact_refs", []):
            if r not in fact_ids: errors.append(f"{cid}: unknown fact ref {r}")
        if c["style"] in "AB" and not c.get("fact_refs"):
            errors.append(f"{cid}: news card without fact_refs")
        # opinion must be labelled and must not cite news facts as opinion
        if "F17" in c.get("fact_refs", []) and c["style"] != "C" and c["id"] != "C17":
            errors.append(f"{cid}: opinion fact F17 used outside a Style C card")
        if c["style"] == "C" and c.get("tag") != "position_tag":
            errors.append(f"{cid}: Style C card must carry the 'Dwin's position' tag")
    return errors, warnings


# ---------------------------------------------------------------- timing
def card_duration(c, lang):
    if c.get("fixed_duration"): return c["fixed_duration"]
    words = sum(len(l.split()) for l in c["text"][lang])
    d = 1.6 + 0.38 * words
    if len(c["text"][lang]) >= 3: d += 0.4
    if c["style"] == "C": d += 0.8          # let the position breathe
    if c["chapter"] == 4: d += 0.5          # quotes: give the viewer time
    return round(min(max(d, 3.2), 6.8), 1)


def timeline(lang):
    t, out, prev_ch = 0.0, [], None
    flash_ch = {c["id"] for c in M["chapters"] if c["flash_before"]}
    for c in M["cards"]:
        if c["chapter"] != prev_ch and c["chapter"] in flash_ch and out:
            t += FLASH
        d = card_duration(c, lang)
        out.append({**c, "start": round(t, 1), "end": round(t + d, 1), "duration": d,
                    "flash_before": c["chapter"] != prev_ch and c["chapter"] in flash_ch and bool(out)})
        t += d
        prev_ch = c["chapter"]
    return out, round(t, 1)


def ts(x):
    m, s = divmod(x, 60)
    return f"{int(m):02d}:{s:04.1f}"


# ---------------------------------------------------------------- prompt text
def spec(lang):
    L, F, C = LANGS[lang], B["fonts"][lang], B["colors"]
    lbl = M["labels"]
    edge = "right" if L["dir"] == "rtl" else "left"
    return f"""## 4. Technical specification

### 4.1 Format and export
- 9:16 vertical, **1080 × 1920**, **30 fps**, progressive.
- Export H.264 (High profile), 12–16 Mbps VBR, `yuv420p`, AAC 48 kHz stereo 256 kbps, `+faststart`.
- Integrated loudness **−14 LUFS**, true peak ≤ −1 dBTP.
- Deliver one master file per language: `dwin_almas_{lang}_v01.mp4`.

### 4.2 Brand and typography ({L['name']})
- Language and script: **{L['name']}**, {L['script']}. Text direction **{L['dir'].upper()}**, captions **{L['align']}-aligned**.
- Font: **{F['name']} {F['weight']}**; if unavailable, **{F['fallback']}**. Before rendering, confirm the font draws these letters correctly: `{F['must_render']}`.
- Digits: Western (0–9) exactly as written in the script. Never convert numbers.
- Do **not** add tatweel/kashida stretching, emojis or decorative symbols to the on-screen text.
- Colours (from `script/brand.json`): gold `{C['gold']}`, dark green `{C['green']}`, cream `{C['cream']}`, dark text `{C['text_dark']}`, white `{C['text_light']}`.
- Dwin logo top-left on every shot except the end card: width 110 px, 60 px from the top and 48 px from the left, 85% opacity, no animation.

### 4.3 Caption styles
- **Style A — stacked boxes (news facts).** Each line sits on its own solid box sized to its text; boxes touch (no gap), square corners, no shadow, no outline. Line 1: dark text on a **gold** box. Other lines: dark text on **cream** boxes. Padding 18 px horizontal × 8 px vertical. A 14 × 14 px gold square sits at the top outer corner of the stack. The **highlighted line** (named on each card) gets a 5 px gold underline the width of its text.
- **Style B — big number.** No boxes. White text, 20% larger than Style A, centred, over a darkened shot (−40% exposure behind the text). The highlighted line gets a 6 px gold underline.
- **Style C — Dwin's position (opinion).** Full-screen dark green `{C['green']}` background (b-roll at most 15% visible behind it). Cream text, centred, 15% larger than Style A. A small gold pill tag above the text reads **{lbl['position_tag'][lang]}**. This style is used **only** for Dwin's own opinion so viewers can always tell opinion from reporting.
- **Style S — sources.** Dark green background, cream text, 70% of Style A size, centred.
- **Style E — end card.** Dark green background, Dwin logo centred (40% of width), channel name and tagline under it in cream.
- **Tags.** Cards marked with a tag show a small pill above the stack (11 px radius, gold outline, cream text, 60% of caption size): *claim tag* = **{lbl['claim_tag'][lang]}**, *unverified tag* = **{lbl['unverified_tag'][lang]}**. Footage marked *illustrative* shows **{lbl['illustrative'][lang]}** in small cream text at 60% opacity, bottom-{edge} corner of the safe area.

### 4.4 Caption size and line breaks
- Base size 56 px (Style A). If a line is wider than 900 px, shrink that card's font in 2 px steps down to a minimum of 46 px. Never re-break or rewrite lines: the line breaks in this script are final.
- Line height 1.35. Maximum 4 lines per card.

### 4.5 Caption animation
1. Frame 0: the gold corner square (or tag) pops in (scale 0 → 100%, 3 frames, ease-out).
2. Line 1 box wipes in from the reading side ({'right → left' if L['dir'] == 'rtl' else 'left → right'}) over 6 frames.
3. Words appear one by one: each word fades 0 → 100% over 4 frames, 4 frames apart.
4. Each next line starts when the previous line's last word is visible.
5. Hold until 8 frames before the card's end, then fade out with a 6 px blur over 8 frames.
6. Style B and C: whole lines fade up (10 frames each), no word-by-word.

### 4.6 Layout and safe zones (1080 × 1920)
- Keep empty: top 220 px (logo only), bottom 420 px, right 140 px (platform buttons).
- Style A stack: anchored to the **{edge}** side, {'right edge 160 px from the right' if L['dir'] == 'rtl' else 'left edge 80 px from the left'}; vertical centre of the stack at y = 1180 px.
- Style B, C, S: centred horizontally, vertical centre at y = 960 px.

### 4.7 Footage, grade, motion and transitions
- Use the source clips named on each card. Mute their original audio unless the card says otherwise.
- Every shot has slow motion of its own: push-in 100 → 106% over the shot, or a slow pan. No shaky zooms.
- Cuts land on the music beat; average shot 2–3 s; each card may hold 1–3 shots.
- Grade: saturation −25%, contrast +10, shadows −10, soft vignette 20%. Chapter 7 (advice) is brighter and warmer: saturation −10%, no vignette.
- **White flash** between chapters ({FLASH} s, shown in the timeline): fade to white over 0.25 s, hold 2 frames, fade into the next shot over 0.2 s. The caption of the outgoing card fades out with the flash.
- **Fairness rule for quoted people:** Fakhir Hariri's clip (chapter 4) and the Kurdistan24 speaker are shown unaltered: no slow-motion, freeze-frames, filters, zoom-punches, sound effects or emojis on their faces.
- Blur the faces of private individuals who are not part of the story (shoppers, passers-by).
- The last shot of C24 ends on the **exact first frame of C01** so the reel loops seamlessly.

### 4.8 Source credits
- When a clip from another outlet is on screen, show its credit vertically along the {edge} edge (rotated 90°), 22 px, white at 55% opacity, 40 px from the edge, centred vertically. Credits are listed per card.

### 4.9 Music and sound
- One royalty-free score with no vocals, edited to these cues by chapter:
  - Chapters 1–3 *tension*: dark investigative bed, 96–104 BPM, minor key, sub-bass pulse, ticking hi-hat.
  - Chapter 4 *tension_low*: drums out; low drone only while quotes are on screen.
  - Chapter 5 *tension_build*: pulse returns and builds; peak on the Article 12 penalty card.
  - Chapter 6 *resolve*: near-silence, one low piano note, then firm low strings.
  - Chapters 7–8 *hope / hope_end*: warm piano with light percussion; resolves on a final chord and hard-stops on the last frame of C24.
- SFX: whoosh + low boom on every white flash; a soft tick when each Style A line appears; other cues are listed per card. Never use cartoon, laugh, boo or cash-register sounds.
- Mix: music −20 dB under captions, −24 dB under the two quote cards; SFX peaks around −10 dBFS.
"""


def editorial(lang):
    return """## 2. Editorial rules (non-negotiable)
1. **Use the on-screen text exactly as written** in section 5: same words, same line breaks, same digits, same punctuation. Do not translate, shorten, add or "improve" anything. If something seems wrong, stop and flag it; do not fix it silently.
2. **Attribute every claim.** That the Almas cream is fake, was made in Erbil and carried a forged sticker are **claims from the HOKAR video**, not confirmed by a lab result or a court ruling. Never show them as established facts: no "FAKE" stamps, red crosses, prison bars or similar graphics on the product or on any person.
3. **Fairness.** Fakhir Hariri's own response gets two full cards (C11–C12), quoted in his words, shown without mockery. Rasul Abdulkhaliq is shown by name only; his official title is unconfirmed.
4. **The law, exactly.** Iraq Consumer Protection Law No. 1 of 2010: Art. 1 (who is an advertiser), Art. 3 (scope), Art. 6 (compensation through the courts), Art. 7 (verify before advertising), Art. 9 (no fraud or deception), **Art. 12 (penalties: at least 3 months' prison and/or at least 1,000,000 dinars)**. The source article cited Article 10 for the penalties; that is a mistake in the article (Art. 10 is about council staff). Use Article 12.
5. **Opinion is labelled.** Dwin's condemnation of misleading advertising appears only in the Style C cards (C17–C19), tagged as Dwin's position. It condemns the *practice* and *everyone* who misleads people with unchecked ads; it does not name or accuse any individual.
6. **Show the gaps.** C06 (claims not yet confirmed) is mandatory and must never be cut, even in a short version.
7. **Credits.** Every reused clip carries its source credit while on screen.
"""


def strategy():
    return """## 3. How the message is delivered
- **Hook in 3 seconds (C01–C03):** a familiar situation (a famous face sells a cream), the shock (a video says it is fake) and one concrete number (the price).
- **Three voices, in order:** the accuser (HOKAR), the authority (Kurdistan24), the advertiser (Fakhir Hariri). The viewer hears every side before the law speaks.
- **The law as the turning point (C13–C16):** short, numbered articles; the penalty card is the emotional peak.
- **Then Dwin speaks (C17–C19):** a clear, labelled condemnation of misleading advertising as a practice.
- **End with power for the viewer (C20–C24):** four practical actions and one question to remember: *Before you buy, ask: who checked it?*
- **Loop:** the last shot returns to the first, so the reel replays.
- **Sound off works:** the story must make complete sense with the sound off, from captions alone.
"""


def card_block(c, lang):
    lines = c["text"][lang]
    hl = c.get("highlight")
    tag = c.get("tag")
    fence_text = "\n".join(lines)
    out = [f"### {c['id']} · {ts(c['start'])}–{ts(c['end'])} ({c['duration']} s) · Chapter {c['chapter']} · Style {c['style']} ({STYLE_NAMES[c['style']]})"]
    if c.get("flash_before"):
        out.append(f"*White flash ({FLASH} s) before this card.*")
    out.append("")
    out.append(f"**On-screen text** — {len(lines)} line(s), copy exactly:")
    out.append("")
    out.append("```text")
    out.append(fence_text)
    out.append("```")
    extras = []
    if hl is not None: extras.append(f"highlighted line: **{hl + 1}** (`{lines[hl]}`)")
    if tag: extras.append(f"tag: **{M['labels'][tag][lang]}**")
    if c.get("illustrative"): extras.append(f"illustrative label: **{M['labels']['illustrative'][lang]}**")
    if extras: out.append("- " + "; ".join(extras))
    out.append(f"- Meaning (English, for the editor only, not on screen): {c['meaning_en']}")
    for i, b in enumerate(c["broll"], 1):
        out.append(f"- Shot {i}: {b}")
    if c.get("credit"): out.append(f"- Source credit on screen: **{c['credit']}**")
    out.append(f"- Sound: {c['sfx']}")
    if c.get("editor_note"): out.append(f"- Editor note: {c['editor_note']}")
    if c.get("fact_refs"): out.append(f"- Fact check refs: {', '.join(c['fact_refs'])}")
    out.append("")
    return "\n".join(out)


def prompt(lang):
    L = LANGS[lang]
    cards, total = timeline(lang)
    title = M["project"]["titles"][lang]
    header = f"""# Dwin reel prompt — {L['name']} — Almas cream and influencer ads

> Generated by `tools/build.py` from `script/master.json`. Edit the source files, not this file.
> Machine-readable version with the same timings: `script/cards.{lang}.json`.

**Working title (on-screen language):** {title}
**Length:** about {ts(total)} ({total} s), {len(cards)} cards, 8 chapters.
**Source:** "{M['project']['title_en']}" ({M['project']['article_date']}), `source/article.txt`.

## 1. Role and goal
You are the senior video editor and motion designer of **Dwin** ({B['channels'][lang]}). Produce a finished vertical news reel in **{L['name']}** that explains the Almas cream controversy accurately, gives every side its voice, shows what Iraqi consumer-protection law says about advertisers, clearly condemns misleading advertising as Dwin's labelled position, and leaves viewers with practical steps to protect themselves.

The story is told by **caption cards over b-roll, music and sound effects. There is no narrator.** This prompt is in English; **only the on-screen text is in {L['name']}**.

"""
    body = [header, editorial(lang), strategy(), spec(lang)]
    body.append(f"## 5. Card-by-card script ({L['name']})\n")
    body.append("Timings assume the reading speed above; you may stretch any card by up to 0.5 s to land a cut on the beat, but never shorten a card below its listed duration.\n")
    ch_names = {c["id"]: c["name_en"] for c in M["chapters"]}
    cur = None
    for c in cards:
        if c["chapter"] != cur:
            cur = c["chapter"]
            body.append(f"\n---\n\n#### Chapter {cur} — {ch_names[cur]}\n")
        body.append(card_block(c, lang))
    body.append(f"""## 6. Post caption ({L['name']})

```text
{M['post_caption'][lang]}
```

## 7. Quality checklist before publishing
- [ ] Every on-screen line matches section 5 character for character (compare against `script/cards.{lang}.json`).
- [ ] The font renders all special letters correctly; nothing is shown as boxes or disconnected letters.
- [ ] Claim tag on C04, unverified tag on C06, position tag on C17–C19.
- [ ] No "fake" graphics on the product or on any person; Fakhir Hariri's clips are unaltered.
- [ ] Article numbers: 1, 3, 7, 9 and **12** (not 10).
- [ ] Source credits visible on every reused clip; illustrative labels on C06 and C16 footage.
- [ ] Captions stay inside the safe zones on a real phone (Instagram, Facebook, TikTok previews).
- [ ] Watched once with sound off: the story is complete from captions alone.
- [ ] Loudness −14 LUFS, true peak ≤ −1 dBTP; music hard-stops on the last frame of C24.
- [ ] The reel loops cleanly from C24 back to C01.

## 8. Facts behind the cards
""")
    for f in M["facts"]:
        body.append(f"- **{f['id']}** — {f['claim_en']} *({f['status']}; {f['source']})*")
    return "\n".join(body) + "\n"


# ---------------------------------------------------------------- outputs
def fact_check():
    rows = ["# Fact check", "", "Every card points to one or more facts below. Status shows how each fact is supported.", "",
            "| ID | Fact | Status | Source | Used on cards |", "| --- | --- | --- | --- | --- |"]
    used = {}
    for c in M["cards"]:
        for r in c.get("fact_refs", []): used.setdefault(r, []).append(c["id"])
    for f in M["facts"]:
        rows.append(f"| {f['id']} | {f['claim_en']} | {f['status']} | {f['source']} | {', '.join(used.get(f['id'], []))} |")
    rows += ["", "## Law source", "- Iraq Consumer Protection Law No. 1 of 2010, official Arabic text: https://alp.unescwa.org/sites/default/files/2021-09/Iraq_Law1_y2010_Consumer_Protection_AR.pdf",
             "- Correction: the source article attributes the penalties to Article 10. In the official text the penalties are in **Article 12** (first paragraph punishes violations of Article 9). Article 10 concerns the consumer council's staff.",
             "", "## Still to confirm before publishing",
             "- Rasul Abdulkhaliq's official title (not stated in the clips).",
             "- Whether any official lab result or court ruling on the Almas cream has been issued since 2026-10-23. If one exists, update C04–C06 and F03–F06."]
    return "\n".join(rows) + "\n"


def main():
    errors, warnings = check()
    for w in warnings: print("warning:", w)
    for e in errors: print("ERROR:", e)
    if errors: sys.exit(1)
    if "--check" in sys.argv: print("checks passed"); return
    (ROOT / "prompts").mkdir(exist_ok=True); (ROOT / "facts").mkdir(exist_ok=True)
    for lang, L in LANGS.items():
        cards, total = timeline(lang)
        (ROOT / "prompts" / L["file"]).write_text(prompt(lang), encoding="utf-8")
        data = {"lang": lang, "language": L["name"], "direction": L["dir"], "total_seconds": total,
                "format": M["project"]["format"], "brand": {"colors": B["colors"], "font": B["fonts"][lang], "channel": B["channels"][lang]},
                "labels": {k: v[lang] for k, v in M["labels"].items()},
                "cards": [{"id": c["id"], "chapter": c["chapter"], "start": c["start"], "end": c["end"], "style": c["style"],
                           "flash_before": c["flash_before"], "lines": c["text"][lang], "highlight": c.get("highlight"),
                           "tag": M["labels"][c["tag"]][lang] if c.get("tag") else None,
                           "illustrative": bool(c.get("illustrative")), "credit": c.get("credit"),
                           "broll": c["broll"], "sfx": c["sfx"], "fact_refs": c.get("fact_refs", [])} for c in cards],
                "post_caption": M["post_caption"][lang]}
        (ROOT / "script" / f"cards.{lang}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{lang}: {len(cards)} cards, {total} s -> prompts/{L['file']}")
    (ROOT / "facts" / "fact_check.md").write_text(fact_check(), encoding="utf-8")
    print("facts/fact_check.md written")


if __name__ == "__main__":
    main()
