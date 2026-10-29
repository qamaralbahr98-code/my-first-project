#!/usr/bin/env python3
"""Build prompts/*.md and subtitles from script/scenes.json. Run: python3 tools/build.py"""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.load(open(ROOT / "script/scenes.json", encoding="utf-8"))
LANGS = {
 "ckb": dict(file="01_sorani", name="Kurdish Sorani", dir="RTL", font="Speda", rate=2.0, channel="Dween - دوین"),
 "kmr": dict(file="02_kurmanji", name="Kurdish Kurmanji", dir="LTR", font="Montserrat", rate=2.4, channel="Dwîn - Kurmancî"),
 "ar":  dict(file="03_arabic", name="Arabic", dir="RTL", font="Aljazeera", rate=2.0, channel="دوين - العربية"),
}
PAD = 0.8
TITLES = {
 "ar": "الانتماء لدى الشباب الكرد في سوريا: من «غير موجود» إلى «نحن هنا»",
 "ckb": "پێوەبەستبوونی گەنجانی کورد لە سووریا: لە «بوونت نییە» بۆ «ئێمە لێرەین»",
 "kmr": "Aîdbûna ciwanên Kurd li Sûriyeyê: ji «tune ye» heta «em li vir in»",
}
DESC = {
 "ar": "كيف يعرّف الشباب الكرد في سوريا أنفسهم بعد الثورة وسقوط النظام والمرسوم ١٣؟ شرح هادئ ومتوازن: من إحصاء ١٩٦٢ إلى احتجاجات المدارس في أيلول ٢٠٢٦، والسيناريوهات الثلاثة للمستقبل.",
 "ckb": "گەنجانی کورد لە سووریا دوای شۆڕش، ڕووخانی ڕژێم و فەرمانی ١٣ چۆن خۆیان دەناسێنن؟ ڕوونکردنەوەیەکی ئارام و هاوسەنگ: لە سەرژمێریی ١٩٦٢ەوە تا ناڕەزایی قوتابخانەکان لە ئەیلوولی ٢٠٢٦، و سێ سیناریۆی داهاتوو.",
 "kmr": "Ciwanên Kurd li Sûriyeyê piştî şoreş, hilweşîna rejîmê û Biryarnameya 13 xwe çawa pênase dikin? Ravekirineke aram û hevseng: ji serjimariya 1962an heta protestoyên dibistanan di Îlona 2026an de, û sê senaryoyên pêşerojê.",
}
SOURCES = [
 "Shvan Ibrahim — study on belonging among Kurdish youth in Syria during the revolution (5 Oct 2026) — main source",
 "Al Jazeera English — Syria's al-Sharaa issues decree recognising Kurdish rights (17 Jan 2026)",
 "Arab News PK — background on the 1962 census, statelessness and the Arab Belt (Jan 2026)",
 "Amnesty International — Kurds in the Syrian Arab Republic one year after the March 2004 events (2005)",
 "UNHCR figures on Decree 49 naturalisations (to mid-2013), as reported by Arab News PK",
 "Hawar News / Syria TV / SANA — Kurdish-language teaching and the September 2026 student protests",
 "Karl Mannheim — 'The Problem of Generations' (1928)",
]

def dur(text, rate): return round(len(text.split()) / rate + PAD, 1)

def ts(sec):
    ms = int(round(sec * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def build(lang, L):
    sc = D["scenes"]; total = sum(dur(s[lang]["n"], L["rate"]) for s in sc)
    o = [f"# Dwin Vox-style explainer — {L['name']} ({L['dir']})", "",
     "## 1. Role and goal",
     f"You are a senior motion designer and video editor. Build an {total/60:.1f}-minute Vox-style explainer in {L['name']} on belonging among Kurdish youth in Syria during and after the revolution. Tone: professional, calm, balanced, NOT nationalist, NOT against any group. The video explains; it does not campaign.", "",
     "## 2. Editorial rules",
     "- Use narration and on-screen text EXACTLY as written below. Do not translate, shorten or 'fix' them.",
     "- Every number/claim shows a small source line (bottom corner, 60% opacity) from the scene's `Source` field.",
     "- Never fake real records with AI (decrees, IDs, official posts, protest footage). AI images get a small 'illustration' tag.",
     "- No AI images of real people's faces. AI people are always seen from behind, in silhouette or as hands.",
     "- Protest/clash footage: no graphic violence, blur minors' faces, credit the agency in the lower-third.",
     "- No sources slide at the end. Sources go in the description only.", "",
     "## 3. Technical spec",
     "- Master 1920×1080, 24 fps, H.264 high, AAC 48 kHz, −14 LUFS integrated, true peak −1 dB.",
     "- Second export 1080×1920 (9:16): reframe each scene (centre-crop photos, re-layout graphics vertically, captions move to the lower third, safe zone 250 px bottom / 150 px top).",
     "- Shield logo TOP-LEFT on EVERY scene in every language (fixed brand rule, not mirrored), 90 px high, 40 px margin, 85% opacity.",
     f"- Font: {L['font']} (fallback Noto {'Naskh Arabic' if L['dir']=='RTL' else 'Sans'}). Shape text with a real engine (Playwright/Chromium or HarfBuzz) — never draw Arabic-script glyphs one by one.",
     f"- Direction {L['dir']}: " + ("mirror all layouts; timeline bar runs right→left; text reveals and wipes move right→left; charts start from the right." if L['dir']=='RTL' else "timeline runs left→right; reveals move left→right."),
     "- Palette: paper #EFE8DC, ink #1B1B1B, dark slide #111418, accent saffron #E8A33D, muted red #B5483A, muted green #4F7C5A (accent use only, never as a flag).",
     "- Look: paper grain overlay (8%), cut-out photos with 6 px white border and soft shadow, 2.5D parallax on photos, ink-drawn arrows/circles, film grain on archival scenes.",
     "- Captions: burned-in, 2 lines max, 46 px, white on 70% black box, word-level highlight in saffron. Also export .srt from `subtitles/`.",
     "- Transitions: paper-slide push (default), hard cut to dark slide for chapter cards, whip-pan whoosh between real footage, match cut S02→S32 (the '1962' callback).",
     "- 'Text behind person' (S04, S32): segment the subject with rembg / MediaPipe Selfie Segmentation, layer: background → giant title → subject matte → captions.",
     "- Tool / lower-third labels: rounded tag, 28 px, icon + text, slides in from the reading side.",
     "- Chapter cards (dark slides) at S04, S11, S16, S23, S27: number + chapter name, 2.5 s, low boom hit.", "",
     "## 4. Voice and music",
     "- Voice: one calm, warm, mid-low narrator, native " + L['name'] + ", measured pace, no drama. Human narrator recommended (ElevenLabs has no official Kurdish support)." if lang!="ar" else "- Voice: one calm, warm, mid-low native Arabic narrator (Modern Standard Arabic, Levantine-neutral). ElevenLabs v3 supports Arabic: a deep calm documentary voice, stability ~55%, style low.",
     "- Music: royalty-free, no vocals. Act 1 (S01–S10): soft piano + low strings; Act 2 (S11–S22): light pulse, curious; Act 3 (S23–S29): sparse, thoughtful; S30–S33: warm build, 1 s silence before 'we are here', then soft resolve. Duck −18 dB under voice.",
     "- SFX (subtle): paper slide, stamp, pencil scratch, typewriter tick, soft click on checklist, whoosh.", "",
     f"## 5. Scene by scene (total ≈ {total/60:.1f} min)", ""]
    t = 0; srt = []
    for i, s in enumerate(sc, 1):
        d = dur(s[lang]["n"], L["rate"])
        o += [f"### {s['id']} · {s['part']} · {ts(t)[:8]} · {d}s", f"**Style:** {s['style']}", f"**Visual:** {s['visual']}",
              f"**Files:** {', '.join(s['assets'])}", f"**Source line:** {s['source'] or '—'}", "**Narration:**", "```", s[lang]["n"], "```",
              "**On-screen text:**", "```", s[lang]["t"], "```", ""]
        srt += [str(i), f"{ts(t)} --> {ts(t+d-0.2)}", s[lang]["n"], ""]
        t += d
    o += ["## 6. YouTube post", f"**Title:** {TITLES[lang]}", "", f"**Description:** {DESC[lang]}", "", "Sources:"] + [f"- {x}" for x in SOURCES] + \
         ["", f"**Channel:** {L['channel']}", f"**Thumbnails:** see THUMBNAILS.md.", "",
          "## 7. Fact notes", "- Decree 13 announced 16 Jan 2026 by President Ahmad al-Sharaa (implementation from 29 Jan).",
          "- Kurdish classes per week: the study says 3, SANA says 2 → shown as '2–3' with a 'sources differ' tag.",
          "- 517,000 (Hasakah registry) includes descendants; not comparable 1:1 with the 120,000 stripped in 1962.",
          "- Self-definitions (S16) are qualitative findings, not survey percentages — never invent percentages."]
    (ROOT / f"prompts/{L['file']}.md").write_text("\n".join(o), encoding="utf-8")
    (ROOT / f"subtitles/{lang}.srt").write_text("\n".join(srt), encoding="utf-8")
    return total

if __name__ == "__main__":
    (ROOT / "prompts").mkdir(exist_ok=True); (ROOT / "subtitles").mkdir(exist_ok=True)
    for k, L in LANGS.items(): print(k, f"{build(k, L)/60:.1f} min")
