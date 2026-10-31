#!/usr/bin/env python3
"""Build prompts/, subtitles/ and social/ from script/scenes.json.  Run: python3 tools/build.py"""
import json, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
D = json.load(open(ROOT / "script/scenes.json", encoding="utf-8"))
PAD = 0.8
L = {
 "ckb": dict(file="01_sorani", name="Kurdish Sorani", dir="RTL", font="Speda", fb="Noto Naskh Arabic", rate=2.2, channel="Dween - دوین"),
 "kmr": dict(file="02_kurmanji", name="Kurdish Kurmanji", dir="LTR", font="Montserrat", fb="Noto Sans", rate=2.5, channel="Dwîn - Kurmancî"),
 "ar":  dict(file="03_arabic", name="Arabic", dir="RTL", font="Aljazeera", fb="Noto Naskh Arabic", rate=2.0, channel="دوين - العربية"),
}
CHAP = {
 "ar": ["المقدمة", "السياق: من أين بدأت الحكاية؟", "جوهر المشكلة: سرديات لا سردية", "الأدلة: الذاكرة والتحالفات والحضارة", "السرديات المضادة: ماذا يصمد؟", "ما الذي على المحك؟", "الخاتمة: الجبال لا تكتب الحكايات"],
 "ckb": ["پێشەکی", "پاشخان: چیرۆکەکە لە کوێوە دەستی پێکرد؟", "کڕۆکی کێشەکە: گێڕانەوەکان نەک یەک گێڕانەوە", "بەڵگەکان: یادەوەری، هاوپەیمانی و شارستانیەت", "گێڕانەوە دژەکان: کامیان ڕاستە؟", "چی لە مەترسیدایە؟", "کۆتایی: چیاکان چیرۆک نانووسن"],
 "kmr": ["Destpêk", "Paşxane: Çîrok ji ku dest pê kir?", "Dilê pirsgirêkê: ne yek vegotin", "Delîl: bîranîn, hevpeymanî û şaristanî", "Vegotinên dijber: kîjan rast e?", "Çi di xeterê de ye?", "Dawî: çiya çîrokan nanivîsin"],
}
TITLE = {
 "ar": "السردية الكردية: من يملك الحكاية؟ | من صلاح الدين إلى لوزان إلى اليوم",
 "ckb": "گێڕانەوەی کوردی: چیرۆکەکە هی کێیە؟ | لە سەلاحەدینەوە بۆ لۆزان و ئەمڕۆ",
 "kmr": "Vegotina Kurdî: Çîrok ya kê ye? | Ji Selahedîn heta Lozanê û îro",
}
INTRO = {
 "ar": "«ليس للكرد أصدقاء إلا الجبال»… هل هي حقيقة تاريخية أم حكاية اعتدنا روايتها؟\nفي هذا الفيديو نشرح بهدوء كيف تشكّلت السردية الكردية: من الإمارات الكردية وصلاح الدين، إلى سيفر ولوزان، إلى تجارب تركيا وإيران والعراق وسوريا، ثم نختبر السرديات المضادة ونسأل: أيّ حكاية نريد أن نرويها لأبنائنا ولجيراننا؟\nهذه الحلقة بداية سلسلة عن الانتماء… تابعونا.",
 "ckb": "«کورد جگە لە چیاکان هیچ دۆستێکی نییە»… ڕاستییەکی مێژووییە یان چیرۆکێکە ڕاهاتووین بیگێڕینەوە؟\nلەم ڤیدیۆیەدا بە ئارامی ڕوونی دەکەینەوە گێڕانەوەی کوردی چۆن پێکهات: لە میرنشینە کوردییەکان و سەلاحەدینەوە، بۆ سیڤەر و لۆزان، بۆ ئەزموونەکانی تورکیا، ئێران، عێراق و سووریا، پاشان گێڕانەوە دژەکان تاقی دەکەینەوە و دەپرسین: چ چیرۆکێک بۆ منداڵ و دراوسێکانمان دەگێڕینەوە؟\nئەم ئەڵقەیە سەرەتای زنجیرەیەکە دەربارەی پێوەبەستبوون… بەدوامان بکەون.",
 "kmr": "«Ji çiyan pêve hevalên Kurdan tune ne»… Ma ev rastiyeke dîrokî ye, an çîrokek e ku em fêr bûne vebêjin?\nDi vê vîdyoyê de em bi aramî rave dikin ka vegotina Kurdî çawa çêbû: ji mîrektiyên Kurdî û Selahedîn, heta Sêvr û Lozanê, heta ezmûnên Tirkiye, Îran, Iraq û Sûriyeyê; paşê em vegotinên dijber diceribînin û dipirsin: Em ê ji zarok û cîranên xwe re kîjan çîrokê vebêjin?\nEv beş destpêka rêzeyekê ye li ser aîdbûnê… me bişopînin.",
}
TAGS = {
 "ar": "السردية الكردية, الكرد, القضية الكردية, تاريخ الكرد, صلاح الدين الأيوبي, معاهدة لوزان, معاهدة سيفر, سايكس بيكو, الكرد في سوريا, الكرد في العراق, الكرد في تركيا, الكرد في إيران, إقليم كردستان, مهاباد, حلبجة, الأنفال, أحمد خاني, سعيد النورسي, الهوية, الانتماء, التعايش, العالم الإسلامي, دوين, شرح, وثائقي",
 "ckb": "گێڕانەوەی کوردی, کورد, دۆزی کورد, مێژووی کورد, سەلاحەدینی ئەیووبی, لۆزان, سیڤەر, سایکس پیکۆ, کوردی سووریا, هەرێمی کوردستان, باکوور, ڕۆژهەڵات, مەهاباد, هەڵەبجە, ئەنفال, ئەحمەدی خانی, سەعیدی نوورسی, ناسنامە, پێوەبەستبوون, پێکەوەژیان, جیهانی ئیسلامی, دوین, Kurdish narrative, Kurdish history",
 "kmr": "Vegotina Kurdî, Kurd, Doza Kurdî, Dîroka Kurdan, Selahedînê Eyûbî, Peymana Lozanê, Peymana Sêvrê, Sykes Picot, Kurdên Sûriyeyê, Herêma Kurdistanê, Bakur, Rojhilat, Mehabad, Helebce, Enfal, Ehmedê Xanî, Mem û Zîn, Seîdê Nûrsî, nasname, aîdbûn, pêkvejiyan, cîhana îslamî, Dwîn, Kurdish history",
}
SOURCES = [
 "Main source: «السردية الكردية في الدول الأربع والعالم الإسلامي والعالم» — analytical study, 1st edition, 2026",
 "Human Rights Watch — Genocide in Iraq: The Anfal Campaign Against the Kurds (1993)",
 "David McDowall — A Modern History of the Kurds (2004)",
 "Martin van Bruinessen — Agha, Shaikh and State (1992)",
 "Benedict Anderson — Imagined Communities (1983)",
 "Reuters / AP — PKK dissolution announcement and weapons ceremony (May–July 2025)",
 "Al Jazeera English — Decree 13 (17 Jan 2026) and the SDF integration agreement (30 Jan 2026)",
]
SOCIAL = {
 "ar": dict(fb="«ليس للكرد أصدقاء إلا الجبال»… لكن الجبال لا تكتب الحكايات.\n\nمن صلاح الدين الأيوبي إلى معاهدة لوزان، ومن مهاباد إلى حلبجة، ومن أربيل إلى القامشلي: كيف تشكّلت السردية الكردية؟ ولماذا لا توجد حكاية كردية واحدة؟ وما الذي يصمد من السرديات المضادة؟\n\nفيديو هادئ ومتوازن، يسأل سؤالًا واحدًا: أيّ حكاية نريد أن نرويها لأبنائنا ولجيراننا؟\n\nشاهد الحلقة كاملة على يوتيوب، وشاركنا رأيك بهدوء 👇\n\n#السردية_الكردية #الكرد #تاريخ #التعايش #دوين",
            ig="الجبال لا تكتب الحكايات… الناس يكتبونها. 🏔️\nمن يملك الحكاية الكردية؟ حلقة جديدة بأسلوب شرح مبسّط ومتوازن.\nالرابط في البايو 🔗\n\n#السردية_الكردية #الكرد #كردستان #تاريخ #صلاح_الدين #لوزان #هوية #انتماء #التعايش #شرح #وثائقي #دوين"),
 "ckb": dict(fb="«کورد جگە لە چیاکان هیچ دۆستێکی نییە»… بەڵام چیاکان چیرۆک نانووسن.\n\nلە سەلاحەدینی ئەیووبییەوە بۆ پەیماننامەی لۆزان، لە مەهابادەوە بۆ هەڵەبجە، لە هەولێرەوە بۆ قامیشلۆ: گێڕانەوەی کوردی چۆن پێکهات؟ بۆچی یەک چیرۆکی کوردی نییە؟ و لە گێڕانەوە دژەکان چی ڕاستە؟\n\nڤیدیۆیەکی ئارام و هاوسەنگ کە یەک پرسیار دەکات: چ چیرۆکێک بۆ منداڵ و دراوسێکانمان دەگێڕینەوە؟\n\nئەڵقەی تەواو لە یوتیوب ببینە و بە ئارامی ڕای خۆت بنووسە 👇\n\n#گێڕانەوەی_کوردی #کورد #مێژوو #پێکەوەژیان #دوین",
             ig="چیاکان چیرۆک نانووسن… خەڵک دەینووسن. 🏔️\nچیرۆکی کورد هی کێیە؟ ئەڵقەیەکی نوێ بە شێوازی ڕوونکردنەوەی سادە و هاوسەنگ.\nلینک لە بایۆدایە 🔗\n\n#گێڕانەوەی_کوردی #کورد #کوردستان #مێژوو #سەلاحەدین #لۆزان #ناسنامە #پێوەبەستبوون #پێکەوەژیان #دوین"),
 "kmr": dict(fb="«Ji çiyan pêve hevalên Kurdan tune ne»… lê çiya çîrokan nanivîsin.\n\nJi Selahedînê Eyûbî heta Peymana Lozanê, ji Mehabadê heta Helebceyê, ji Hewlêrê heta Qamişloyê: Vegotina Kurdî çawa çêbû? Çima yek çîroka Kurdî tune ye? Û ji vegotinên dijber çi rast dimîne?\n\nVîdyoyeke aram û hevseng ku yek pirsê dike: Em ê ji zarok û cîranên xwe re kîjan çîrokê vebêjin?\n\nBeşa tevahî li YouTubeê temaşe bike û bi aramî ramana xwe binivîse 👇\n\n#VegotinaKurdî #Kurd #Dîrok #Pêkvejiyan #Dwîn",
             ig="Çiya çîrokan nanivîsin… mirov wan dinivîsin. 🏔️\nÇîroka Kurdan ya kê ye? Beşeke nû bi ravekirineke sade û hevseng.\nLînk di bioyê de ye 🔗\n\n#VegotinaKurdî #Kurd #Kurdistan #Dîrok #Selahedîn #Lozan #Nasname #Aîdbûn #Pêkvejiyan #Dwîn"),
}

def words(t): return sum(3 if re.fullmatch(r"[\d,.%٫٬+–-]+", x) else 1 for x in t.split())
def dur(t, r): return round(words(t) / r + PAD, 1)
def ts(sec, srt=True):
    ms = int(round(sec * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}" if srt else (f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}")

def build(lang):
    C = L[lang]; sc = D["scenes"]; rtl = C["dir"] == "RTL"
    starts, t = [], 0.0
    for s in sc: starts.append(t); t += dur(s[lang]["n"], C["rate"])
    total = t
    chapters, seen = [], set()
    for s, st in zip(sc, starts):
        k = s["part"]
        if k not in seen: seen.add(k); chapters.append((st, CHAP[lang][int(k[0]) - 1]))
    chap_txt = "\n".join(f"{ts(a, False)} {b}" for a, b in chapters)
    o = [f"# Dwin Vox-style explainer: «The Kurdish narrative» — {C['name']} ({C['dir']})", "",
     "## 1. Role and goal",
     f"You are a senior motion designer and documentary editor. Build an approximately {total/60:.1f}-minute Vox-style explainer in {C['name']} about the Kurdish narrative: how Kurds tell their story and how it is told about them. The target length is 9–12 minutes, with 12:00 as the hard maximum.",
     "Tone: professional, calm and balanced. It must not be nationalist or sectarian, and must never be hostile to Arabs, Turks, Persians or any Kurdish party. The video explains and invites reflection; it does not campaign.",
     "Editorial line (implicit, never stated as a slogan): the Kurdish story is told as part of the region's shared civilisation. It is open to coexistence with its neighbours, free of ideological extremism, and wary of dependence on distant powers; the region's future is in the hands of its own people. The last scene teases future episodes about these belongings. Do not add any extra lines that state the line outright.", "",
     "## 2. Editorial rules",
     "- Use narration and on-screen text EXACTLY as written. Do not translate, shorten or edit them.",
     "- Numbers in the narration are written as digits; the narrator reads them as full words in the language (e.g. 1514 → the full year in words).",
     "- Every fact or number shows a small source line from the scene's `Source` field (bottom corner, 24 px, 60% opacity).",
     "- Never fake real records with AI: treaties, manuscripts, archival photos and news footage must be real. AI images get a small 'illustration' tag.",
     "- No AI faces of real or historical people (Saladin, Khani, Qazi Muhammad, etc.). Use statues, manuscripts, real public-domain photos or calligraphy cards instead.",
     "- No party flags, party logos or leader portraits as decoration. Atrocity scenes (S19–S20) use memorials only: no bodies and no graphic images.",
     "- The Qur'anic verse (S29) is always shown in Arabic calligraphy; treat it respectfully, with no music hit on it.",
     "- No sources slide at the end. Sources go in the YouTube description only.", "",
     "## 3. Technical spec",
     "- Master 1920×1080, 24 fps, H.264 high, AAC 48 kHz, −14 LUFS integrated, true peak −1 dB.",
     "- Second export 1080×1920 (9:16): reframe each scene. Centre-crop photos, re-stack graphics vertically, put captions in the lower third, and keep safe zones of 250 px at the bottom and 150 px at the top.",
     "- Shield logo TOP-LEFT on every scene in every language (fixed brand rule; never mirrored), 90 px high, 40 px margin, 85% opacity.",
     f"- Font: {C['font']} (fallback {C['fb']}). Shape text with a real engine (Playwright/Chromium or HarfBuzz).",
     f"- Direction {C['dir']}: " + ("mirror every layout. The timeline bar runs right→left; reveals, wipes, card order and chart axes start from the right." if rtl else "the timeline runs left→right; reveals move left→right."),
     "- Palette: paper #EFE8DC, ink #1B1B1B, dark slide #111418, saffron accent #E8A33D, muted red #B5483A, deep green #3F6B57. Accents only; never compose a flag.",
     "- Look: paper grain overlay (8%), cut-outs with a 6 px white border and soft shadow, 2.5D parallax, hand-drawn ink arrows and circles, and film grain plus sepia on archival material.",
     "- Persistent timeline bar (bottom, 6 px): 7 chapter ticks; the playhead shows the current era (year label) during S06–S13 and S33.",
     "- Captions: burned in, 2 lines max, 46 px, cream on a 70% black box, word-level highlight in saffron. Also export the .srt from `subtitles/`.",
     "- Transitions: paper-slide push (default); hard cut to a dark slide for chapter cards (S05, S14, S19, S27, S33, S37); whip-pan whoosh between real footage clips; match cut S01→S37 (same mountains).",
     "- Text behind person (S04, S07 statue, S25, S38): segment the subject with rembg or MediaPipe. Layer order: background → giant title → subject matte → captions.",
     "- Tool / lower-third labels: rounded tag, 28 px, icon + text, slides in from the reading side; used for names, places, dates and treaties.",
     "- Moving stills: build M1–M4 as described in MOTION.md; every other still gets a Ken Burns move (1.00→1.05).", "",
     "## 4. Voice, music and SFX",
     ("- Voice: one calm, warm, mid-low native Arabic narrator (Modern Standard Arabic). If using ElevenLabs, v3 supports Arabic: deep documentary voice, stability ~55%, style low."
      if lang == "ar" else f"- Voice: one calm, warm, mid-low native {C['name']} narrator at a measured pace with no drama. A human narrator is recommended, because ElevenLabs does not officially support Kurdish."),
     "- Music (royalty-free, no vocals):",
     "  - S01–S04: low drone and wind, with a single duduk/ney note.",
     "  - S05–S13: light strings with a soft frame-drum pulse.",
     "  - S14–S18: tense, sparse.",
     "  - S19–S22: near silence, with piano only.",
     "  - S23–S32: curious pulse, with a soft pause on each verdict stamp.",
     "  - S33–S39: warm build; 1 s of silence before the last line of S38, then a gentle resolve.",
     "  - Duck the music −18 dB under the voice.",
     "- SFX (subtle): paper slide, stamp, quill scratch, typewriter tick, soft click on checklists, whoosh, distant wind on the mountain scenes.", "",
     f"## 5. Scene by scene (estimated total ≈ {total/60:.1f} min)",
     "Re-time every scene to the real narration audio. If the final cut runs over 12:00, shorten the pauses first, then trim S10 and S22 (marked optional).", ""]
    srt = []
    for i, (s, st) in enumerate(zip(sc, starts), 1):
        d = dur(s[lang]["n"], C["rate"])
        opt = " · OPTIONAL CUT" if s["id"] in ("S10", "S22") else ""
        o += [f"### {s['id']} · {s['part']} · {ts(st, False)} · {d}s{opt}", f"**Style:** {s['style']}", f"**Visual:** {s['visual']}",
              f"**Files:** {', '.join(s['assets']) or '— (graphics only)'}", f"**Source line:** {s['source'] or '—'}",
              "**Narration:**", "```", s[lang]["n"], "```", "**On-screen text:**", "```", s[lang]["t"], "```", ""]
        srt += [str(i), f"{ts(st)} --> {ts(st + d - 0.2)}", s[lang]["n"], ""]
    o += ["## 6. After the video is finished: thumbnails (required)",
          f"When the {C['name']} video is final, ALSO create its YouTube thumbnails in both formats, following THUMBNAILS.md:",
          f"- `thumbnails/thumb_{lang}_16x9.png` (1280×720, <2 MB)",
          f"- `thumbnails/thumb_{lang}_9x16.png` (1080×1920, Shorts/Reels cover)",
          "Use the brand font, the logo top-left, and text in this language only. Render them with Playwright and check them at phone size (160 px wide).", "",
          "## 7. Publishing texts",
          f"Ready in `social/youtube_{lang}.md` and `social/facebook_instagram_{lang}.md`. After the final edit, update the chapter timestamps there to the real times; the first chapter must stay at 0:00.", "",
          "## 8. Fact notes",
          "- Population figures are estimates (no ethnic census in most states); always show them as ranges.",
          "- Anfal deaths: 50,000–182,000 depending on the source; Iraqi High Tribunal genocide ruling 2007.",
          "- Mulla Jami is listed as Kurdish in the study, but he was Persian, so he was removed. Ibn al-Athir is cited as a historian who wrote about Kurds, not as a Kurd.",
          "- The study ends before the 2025 PKK dissolution announcement and the Jan 2026 Syria agreements; both were added from news sources.",
          "- The Ahmad Khani line in S09 is a paraphrase from the study's Arabic rendering, not a verse translation."]
    (ROOT / f"prompts/{C['file']}.md").write_text("\n".join(o), encoding="utf-8")
    (ROOT / f"subtitles/{lang}.srt").write_text("\n".join(srt), encoding="utf-8")
    yt = [f"# YouTube — {C['name']}", "", "## Title", TITLE[lang], "", "## Description", INTRO[lang], "",
          {"ar": "الفصول:", "ckb": "بەشەکان:", "kmr": "Beş:"}[lang], chap_txt, "",
          {"ar": "المصادر:", "ckb": "سەرچاوەکان:", "kmr": "Çavkanî:"}[lang]] + [f"- {x}" for x in SOURCES] + \
         ["", f"{C['channel']}", "", "## Tags", TAGS[lang], "",
          "_Chapter times are estimates from the script; update them to the final edit before publishing._"]
    (ROOT / f"social/youtube_{lang}.md").write_text("\n".join(yt), encoding="utf-8")
    so = [f"# Facebook & Instagram — {C['name']}", "", "## Facebook", SOCIAL[lang]["fb"], "", "## Instagram (Reels / post)", SOCIAL[lang]["ig"]]
    (ROOT / f"social/facebook_instagram_{lang}.md").write_text("\n".join(so), encoding="utf-8")
    return total

if __name__ == "__main__":
    for d in ("prompts", "subtitles", "social", "thumbnails"): (ROOT / d).mkdir(exist_ok=True)
    for k in L: print(k, f"{build(k)/60:.1f} min")
