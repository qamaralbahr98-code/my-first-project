# Dwin Vox-style explainer: «The Kurdish narrative» — Kurdish Sorani (RTL)

## 1. Role and goal
You are a senior motion designer and documentary editor. Build an approximately 11.2-minute Vox-style explainer in Kurdish Sorani about the Kurdish narrative: how Kurds tell their story and how it is told about them. The target length is 9–12 minutes, with 12:00 as the hard maximum.
Tone: professional, calm and balanced. It must not be nationalist or sectarian, and must never be hostile to Arabs, Turks, Persians or any Kurdish party. The video explains and invites reflection; it does not campaign.
Editorial line (implicit, never stated as a slogan): the Kurdish story is told as part of the region's shared civilisation. It is open to coexistence with its neighbours, free of ideological extremism, and wary of dependence on distant powers; the region's future is in the hands of its own people. The last scene teases future episodes about these belongings. Do not add any extra lines that state the line outright.

## 2. Editorial rules
- Use narration and on-screen text EXACTLY as written. Do not translate, shorten or edit them.
- Numbers in the narration are written as digits; the narrator reads them as full words in the language (e.g. 1514 → the full year in words).
- Every fact or number shows a small source line from the scene's `Source` field (bottom corner, 24 px, 60% opacity).
- Never fake real records with AI: treaties, manuscripts, archival photos and news footage must be real. AI images get a small 'illustration' tag.
- No AI faces of real or historical people (Saladin, Khani, Qazi Muhammad, etc.). Use statues, manuscripts, real public-domain photos or calligraphy cards instead.
- No party flags, party logos or leader portraits as decoration. Atrocity scenes (S19–S20) use memorials only: no bodies and no graphic images.
- The Qur'anic verse (S29) is always shown in Arabic calligraphy; treat it respectfully, with no music hit on it.
- No sources slide at the end. Sources go in the YouTube description only.

## 3. Technical spec
- Master 1920×1080, 24 fps, H.264 high, AAC 48 kHz, −14 LUFS integrated, true peak −1 dB.
- Second export 1080×1920 (9:16): reframe each scene. Centre-crop photos, re-stack graphics vertically, put captions in the lower third, and keep safe zones of 250 px at the bottom and 150 px at the top.
- Shield logo TOP-LEFT on every scene in every language (fixed brand rule; never mirrored), 90 px high, 40 px margin, 85% opacity.
- Font: Speda (fallback Noto Naskh Arabic). Shape text with a real engine (Playwright/Chromium or HarfBuzz).
- Direction RTL: mirror every layout. The timeline bar runs right→left; reveals, wipes, card order and chart axes start from the right.
- Palette: paper #EFE8DC, ink #1B1B1B, dark slide #111418, saffron accent #E8A33D, muted red #B5483A, deep green #3F6B57. Accents only; never compose a flag.
- Look: paper grain overlay (8%), cut-outs with a 6 px white border and soft shadow, 2.5D parallax, hand-drawn ink arrows and circles, and film grain plus sepia on archival material.
- Persistent timeline bar (bottom, 6 px): 7 chapter ticks; the playhead shows the current era (year label) during S06–S13 and S33.
- Captions: burned in, 2 lines max, 46 px, cream on a 70% black box, word-level highlight in saffron. Also export the .srt from `subtitles/`.
- Transitions: paper-slide push (default); hard cut to a dark slide for chapter cards (S05, S14, S19, S27, S33, S37); whip-pan whoosh between real footage clips; match cut S01→S37 (same mountains).
- Text behind person (S04, S07 statue, S25, S38): segment the subject with rembg or MediaPipe. Layer order: background → giant title → subject matte → captions.
- Tool / lower-third labels: rounded tag, 28 px, icon + text, slides in from the reading side; used for names, places, dates and treaties.
- Moving stills: build M1–M4 as described in MOTION.md; every other still gets a Ken Burns move (1.00→1.05).

## 4. Voice, music and SFX
- Voice: one calm, warm, mid-low native Kurdish Sorani narrator at a measured pace with no drama. A human narrator is recommended, because ElevenLabs does not officially support Kurdish.
- Music (royalty-free, no vocals):
  - S01–S04: low drone and wind, with a single duduk/ney note.
  - S05–S13: light strings with a soft frame-drum pulse.
  - S14–S18: tense, sparse.
  - S19–S22: near silence, with piano only.
  - S23–S32: curious pulse, with a soft pause on each verdict stamp.
  - S33–S39: warm build; 1 s of silence before the last line of S38, then a gentle resolve.
  - Duck the music −18 dB under the voice.
- SFX (subtle): paper slide, stamp, quill scratch, typewriter tick, soft click on checklists, whoosh, distant wind on the mountain scenes.

## 5. Scene by scene (estimated total ≈ 11.2 min)
Re-time every scene to the real narration audio. If the final cut runs over 12:00, shorten the pauses first, then trim S10 and S22 (marked optional).

### S01 · 1 Hook · 0:00 · 14.9s
**Style:** cold open, dark slide, mountain parallax
**Visual:** Mist rolls over Zagros ridges (M1). The proverb writes itself in giant type, letter by letter. Wind + low drone.
**Files:** A01_zagros_mountains_mist.jpg → MOTION M1
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
«کورد جگە لە چیاکان هیچ دۆستێکی نییە». ڕستەیەکە کورد لە چوار وڵات و بە دەیان شێوەزار دووبارەی دەکەنەوە. بەڵام پرسیارەکە ئەمەیە: ئایا ڕاستییەکی مێژووییە… یان چیرۆکێکە کە ڕاهاتووین بۆ خۆمانی بگێڕینەوە؟
```
**On-screen text:**
```
«کورد جگە لە چیاکان هیچ دۆستێکی نییە»
```

### S02 · 1 Hook · 0:14 · 19.0s
**Style:** magazine big number + map flash
**Visual:** Counter rolls to 30–40 million. A paper map of the region splits into four coloured state outlines (no flags).
**Files:** G01_region_map (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026) (estimates)
**Narration:**
```
نزیکەی 30 بۆ 40 ملیۆن مرۆڤ، دابەشبوون لە نێوان تورکیا، ئێران، عێراق و سووریا. زۆرجار وەک گەورەترین گەلی بێ دەوڵەت لە جیهاندا وەسف دەکرێن. ژمارەکان خەمڵاندنن، چونکە زۆربەی ئەم وڵاتانە لە سەرژمێرییەکانیاندا پرسیار لە نەتەوە ناکەن.
```
**On-screen text:**
```
≈ 30–40 ملیۆن | 4 وڵات
```

### S03 · 1 Hook · 0:33 · 12.6s
**Style:** dark slide, question
**Visual:** Black. An old book opens; pages flutter (M2). The question appears centre screen.
**Files:** A02_old_book_pages_wind.jpg → MOTION M2
**Source line:** —
**Narration:**
```
بەڵام ئەم ڤیدیۆیە ناپرسێت: زەوی هی کێیە؟ دەپرسێت: چیرۆکەکە هی کێیە؟ چونکە ئەو گەلەی خۆی چیرۆکی خۆی نەگێڕێتەوە، کەسانی تر بۆی دەگێڕنەوە… بەو شێوەیەی خۆیان دەیانەوێت.
```
**On-screen text:**
```
چیرۆکەکە هی کێیە؟
```

### S04 · 1 Hook · 0:46 · 6.3s
**Style:** TITLE CARD: text behind person
**Visual:** Giant title BEHIND a person seen from behind on a ridge at sunrise (segmentation). Chapter ticks 1–7 appear on the timeline bar.
**Files:** A03_person_on_ridge_sunrise.jpg
**Source line:** —
**Narration:**
```
گێڕانەوەی کوردی: کورد چۆن چیرۆکی خۆیان دەگێڕنەوە… و چۆن چیرۆکیان لەسەر دەگێڕدرێتەوە.
```
**On-screen text:**
```
گێڕانەوەی کوردی
```

### S05 · 2 Context · 0:52 · 16.3s
**Style:** CHAPTER: Context + definition card
**Visual:** Chapter card. Dictionary-style card: 'Narrative (n.)'. Three nested boxes animate: narration ⊂ story ⊂ narrative. Tool label: 'Lawrence Freedman | strategist'.
**Files:** G02_narrative_boxes (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
سەرەتا، گێڕانەوە چییە؟ تەنها گێڕانەوەی ڕووداوەکان نییە، بەڵکو ئەو چوارچێوەیەیە کە گەلێک پێی هەڵدەبژێرێت چی لەبیر بێت، چۆن ئێستای خۆی لێکبداتەوە، و بەرەو کوێ بڕوات. شەڕێکە لەسەر مانا، پێش ئەوەی شەڕ بێت لەسەر زەوی.
```
**On-screen text:**
```
گێڕانەوە = شەڕ لەسەر مانا
```

### S06 · 2 Context · 1:09 · 16.7s
**Style:** manuscript cut-outs + timeline
**Visual:** Real manuscript page of Sharafnama (cut-out, white border). Timeline bar ticks: 10th–12th c. emirates. Dots on map: Diyarbakır (Marwanids), Ganja (Shaddadids), Dinawar (Hasanwayhids).
**Files:** R01_sharafnama_manuscript.jpg, G01_region_map (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
کورد لە مێژوودا تازە نین. مەسعوودی، ئیبن ئەسیر و یاقووتی حەمەوی باسیان کردوون، و شەرەفخانی بەدلیسی لە ساڵی 1597 مێژووی میرنشینەکانیانی لە «شەرەفنامە»دا نووسیەوە. میرنشینیشیان هەبوو، وەک مەروانی لە دیاربەکر، شەدادی و حەسنەوەیی.
```
**On-screen text:**
```
«شەرەفنامە» 1597 | میرنشینە کوردییەکان
```

### S07 · 2 Context · 1:25 · 18.1s
**Style:** hero cut-out, text behind statue
**Visual:** Real photo of the Saladin statue (Damascus or Erbil) cut out; '1187' behind it. Map arrow to Hattin and Jerusalem.
**Files:** R02_saladin_statue.jpg, R03_jerusalem_old_city.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
لووتکەی ئەم ئامادەبوونە لەگەڵ سەلاحەدینی ئەیووبی بوو، کوڕی تکریت و بە ڕەچەڵەک کورد، کە دەوڵەتی ئەیووبی دامەزراند، لە ساڵی 1187 لە حەتتین سەرکەوت و قودسی ئازاد کرد. خۆی وەک سەرکردەیەکی نەتەوەیی نەناساند، بەڵکو وەک سەرکردەی موسوڵمانان.
```
**On-screen text:**
```
1187 | حەتتین و قودس
```

### S08 · 2 Context · 1:43 · 16.3s
**Style:** painting cut-out + map split
**Visual:** Real Safavid-era mural of Chaldiran (public domain) as a cut-out. Map: a line splits the Kurdish areas; emirate names pop up: Botan, Baban, Soran, Ardalan.
**Files:** R04_chaldiran_mural.jpg, G01_region_map (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
لە ساڵی 1514، لە شەڕی چاڵدێران، زۆربەی میرە کوردەکان بە کاریگەریی زانا ئیدریسی بەدلیسی پاڵپشتی عوسمانییەکانیان کرد. لە ئەنجامدا نزیکەی سێ سەدە نیمچە-خۆبەڕێوەبەرییان بەدەستهێنا، کە تێیدا میرنشینەکانی بۆتان، بابان، سۆران و ئەردەڵان گەشەیان کرد.
```
**On-screen text:**
```
1514 | چاڵدێران ← 3 سەدە خۆبەڕێوەبەری
```

### S09 · 2 Context · 2:00 · 15.8s
**Style:** quote card on parchment
**Visual:** Parchment quote card with a quill drawing the line. Real manuscript page of Mem û Zîn as background (blurred). Tool label: 'Ahmad Khani | poet, 1651–1707'.
**Files:** R05_mem_u_zin_manuscript.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
لە سایەی ئەو میرنشینانەدا ئەحمەدی خانی لە ساڵی 1692 داستانی «مەم و زین»ی نووسی. لە پێشەکییەکەیدا بە خەفەتەوە دەڵێت: ئەگەر پاشایەکمان هەبووایە… بەختمان لە ڕۆژگاردا لە هی کەسانی تر بەرزتر دەبوو.
```
**On-screen text:**
```
«ئەگەر پاشایەکمان هەبووایە…» — ئەحمەدی خانی
```

### S10 · 2 Context · 2:16 · 19.0s · OPTIONAL CUT
**Style:** timeline + portrait cut-outs
**Visual:** Timeline ticks 1839 → 1847 → 1880. Ink stamp 'centralisation' falls on the emirate names. Real portrait of Bedirxan Beg if available (public domain).
**Files:** R06_bedirxan_beg_portrait.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
بەڵام چاکسازییەکانی سەدەی نۆزدەهەم کۆتاییان بەو میرنشینانە هێنا و دەسەڵاتی ڕاستەوخۆی ناوەندیان سەپاند. میر و شێخەکان ڕاپەڕین، وەک بەدرخان بەگ لە 1847 و شێخ عوبەیدوڵڵای نەهری لە 1880. لێرەوە هۆشیارییەکی نوێی کوردی دەستی بە پێکهاتن کرد.
```
**On-screen text:**
```
1847 · 1880 | کۆتایی میرنشینەکان
```

### S11 · 2 Context · 2:35 · 14.4s
**Style:** real document + ink highlight
**Visual:** Real scan of the Treaty of Sèvres text (Wikimedia). Articles 62–64 highlighted with a saffron marker, then the page greys out with the stamp 'never applied'.
**Files:** R07_treaty_of_sevres_page.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
پاشان دەوڵەتی عوسمانی ڕووخا. لە ساڵی 1920، پەیماننامەی سیڤەر لە مادەکانی 62 تا 64دا باسی خۆبەڕێوەبەری بۆ کورد و ئەگەری سەربەخۆیی لە داهاتوودا کرد. بەڵام هەرگیز جێبەجێ نەکرا.
```
**On-screen text:**
```
1920 | سیڤەر: بەڵێنێک کە جێبەجێ نەکرا
```

### S12 · 2 Context · 2:49 · 23.1s
**Style:** archival photo + split-screen parallel
**Visual:** Real photo of the Lausanne Conference delegates (1922–23). Then split screen: 'Lausanne' in Kurdish memory | 'Sykes–Picot' in Arab memory — same scissors icon cutting a map.
**Files:** R08_lausanne_conference_1923.jpg, G01_region_map (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
سێ ساڵ دواتر، پەیماننامەی لۆزان لە 1923 جێگەی گرتەوە. ناوی کوردی نەهێنا و سنوورێکی کێشا کە کوردی بەسەر چوار وڵاتدا دابەش کرد. لە یادەوەریی کوردیدا ئەمە بوو بە «برینی دامەزرێنەر»: دابەشکردنێک لە سەرەوە سەپێنرا، بێ ئەوەی پرس بە خەڵکی ناوچەکە بکرێت… هەروەک چۆن یادەوەریی عەرەبی سایکس–پیکۆی لەبیرە.
```
**On-screen text:**
```
1923 | لۆزان = «برینی دامەزرێنەر»
```

### S13 · 2 Context · 3:12 · 22.2s
**Style:** 4-panel magazine grid
**Visual:** Four cards flip one by one (order mirrors for RTL): Turkey · Iran · Iraq · Syria, each with population estimate and one keyword. Real city photos as card backgrounds: Diyarbakır walls, Sanandaj, Erbil Citadel, Qamishli.
**Files:** R09_diyarbakir_walls.jpg, R10_sanandaj_city.jpg, R11_erbil_citadel.jpg, R12_qamishli_street.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026) (estimates)
**Narration:**
```
لەو کاتەوە، کورد چوار ئەزموونی جیاوازیان ژیاوە: لە تورکیا نکۆڵیکردنێکی درێژ و پاشان ڕێگای ئاشتی، لە ئێران بۆشاییەکی کەلتووری لەگەڵ تەنگپێهەڵچنینی سیاسی، لە عێراق هەرێمێکی فیدراڵی کە لە 2005ەوە بە دەستوور دانی پێدانراوە، و لە سووریا سەرژمێریی 1962، پاشان خۆبەڕێوەبەری، پاشان قۆناغێکی نوێ دوای 2024.
```
**On-screen text:**
```
تورکیا 15–20 م · ئێران 8–12 م · عێراق 6–7 م · سووریا 2–3 م
```

### S14 · 3 Core problem · 3:34 · 14.9s
**Style:** CHAPTER: Core problem + shattered mirror
**Visual:** Chapter card. One word 'Kurdish narrative' cracks into four shards, each showing a label: classic nationalist · revolutionary left · liberal-reformist · Islamic.
**Files:** A04_cracked_mirror.jpg, G03_four_currents (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
لێرەدایە کێشە ڕاستەقینەکە: یەک گێڕانەوەی کوردی نییە. خێزانێک لە گێڕانەوە هەیە کە تێکەڵ دەبن و ڕکابەری دەکەن: نەتەوەیی کلاسیکی، چەپی شۆڕشگێڕ، لیبراڵی چاکسازیخواز و ئیسلامی. هەریەکەیان «کورد» بە شێوەیەکی جیاواز دەگێڕێتەوە.
```
**On-screen text:**
```
یەک گێڕانەوە نییە… بەڵکو گێڕانەوەکان
```

### S15 · 3 Core problem · 3:49 · 14.0s
**Style:** Venn: what unites / what divides
**Visual:** Left column 'unites' (language, Nowruz, shared memory) glows warm; right column 'divides' (the goal: state? autonomy? 'democratic nation'?) in cool grey. Real Nowruz fire photo behind the left column.
**Files:** R13_nowruz_fire_akre.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
ئەوەی کۆیان دەکاتەوە کەمە بەڵام قووڵە: زمان، نەورۆز و یادەوەریی هاوبەشی ئازار. بەڵام ئەوەی جیایان دەکاتەوە گەورەیە: ئامانج دەوڵەتە؟ یان خۆبەڕێوەبەری؟ یان «نەتەوەی دیموکراتیک» بێ دەوڵەت؟ هیچ کۆدەنگییەک نییە.
```
**On-screen text:**
```
کۆیان دەکاتەوە: زمان · نەورۆز · یادەوەری
جیایان دەکاتەوە: ئامانج
```

### S16 · 3 Core problem · 4:03 · 13.1s
**Style:** dialect tree diagram
**Visual:** Animated tree: Kurdish → Kurmanji · Sorani · Zazaki · Gorani · Southern. Two speech bubbles fail to meet, then a bridge word in Arabic/Turkish connects them.
**Files:** G04_dialect_tree (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
تەنانەت زمانەکەش بەسەر چەند شێوەزارێکدا دابەش بووە، دیارترینیان کرمانجی و سۆرانی. هەندێک جار دوو کورد پێویستیان بە عەرەبی یان تورکی دەبێت بۆ ئەوەی ڕاستەوخۆ لە یەکتر تێبگەن.
```
**On-screen text:**
```
کرمانجی · سۆرانی · زازاکی · گۆرانی · باشووری
```

### S17 · 3 Core problem · 4:16 · 14.9s
**Style:** string board / connections
**Visual:** Detective-style string board: three party pins connect with red threads to three capitals (Ankara · Tehran · Washington). Threads tangle; a label: 'each alliance → a different story'. No party logos or flags.
**Files:** G05_alliance_board (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
مەترسیدارتر: هاوپەیمانییە دەرەکییەکان. لایەنێک پشت بە ئەنقەرە دەبەستێت، یەکێکی تر بە تاران، و سێیەمیان بە واشنتن. هەر هاوپەیمانییەک چیرۆکەکە بە ڕەنگێکی جیاواز ڕەنگ دەکات، و پاشان دەبێتە تۆمەتێک لە دەستی نەیاران.
```
**On-screen text:**
```
ئەنقەرە · تاران · واشنتن ← چیرۆکی دژبەیەک
```

### S18 · 3 Core problem · 4:31 · 11.3s
**Style:** dark slide, kinetic type
**Visual:** Black slide. Line 1 types in; line 2 lands with a soft boom.
**Files:** — (graphics only)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
بۆچی ئەمە گرنگە؟ چونکە ئەو دۆزەی گێڕانەوەی خۆی نییە، دەتوێتەوە تەنانەت ئەگەر هەموو مەرجەکانی مانەوەشی هەبێت. و چونکە ئەوەی چیرۆکەکە دەنووسێت… داهاتوو دەکێشێت.
```
**On-screen text:**
```
ئەوەی چیرۆک دەنووسێت… داهاتوو دەکێشێت
```

### S19 · 4 Evidence · 4:42 · 21.3s
**Style:** CHAPTER: Evidence + range chart
**Visual:** Chapter card. Range bar drawn to scale: 50,000 ——— 182,000, labelled 'estimates differ by source'. Real photo: Anfal memorial / Amna Suraka, Sulaymaniyah.
**Files:** R14_amna_suraka_museum.jpg, G06_anfal_range_chart (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026); Human Rights Watch, Genocide in Iraq (1993)
**Narration:**
```
با سەیری بەڵگەکان بکەین. یەکەم، یادەوەری. شاڵاوی ئەنفال لە عێراق لە نێوان 1986 و 1989، بەپێی سەرچاوە، لە نێوان 50 هەزار بۆ 182 هەزار مرۆڤی کردە قوربانی. لە 2007 دادگای باڵای تاوانەکانی عێراق وەک جینۆساید پۆلێنی کرد.
```
**On-screen text:**
```
ئەنفال 1986–1989 | 50–182 هەزار قوربانی
```

### S20 · 4 Evidence · 5:04 · 22.2s
**Style:** memorial photo + quote tag
**Visual:** Real photo of the Halabja Monument. Then a map pin on Dersim with a quote tag (Erdoğan, 2011). Respectful, slow, no graphic images.
**Files:** R15_halabja_monument.jpg, R16_dersim_landscape.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
لە 16ی ئازاری 1988، هەڵەبجە بە چەکی کیمیایی بۆردومان کرا و نزیکەی 5 هەزار مرۆڤ گیانیان لەدەستدا. لە دێرسیمی تورکیاش، لە نێوان 1937 و 1938، هەزاران کەس کوژران، و ئەردۆغان لە 2011 وەسفی کرد بە «یەکێک لە تراژیدیترین ڕووداوەکانی مێژووی نزیکمان».
```
**On-screen text:**
```
هەڵەبجە 1988 ≈ 5,000 | دێرسیم 1937–38
```

### S21 · 4 Evidence · 5:26 · 16.7s
**Style:** archival photo + countdown
**Visual:** Real archival photo of Mahabad 1946 (public domain). A calendar counter runs 11 months, then the image fades to sepia. Tool label: 'outside protection → 11 months'.
**Files:** R17_mahabad_republic_1946.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
لە ئێران، کۆماری مەهاباد لە 1946 بە سەرکردایەتیی قازی محەممەد و لە ژێر پاراستنی سۆڤیەتدا دامەزرا. تەنها 11 مانگ ژیا، پاشان کاتێک سۆڤیەت کشایەوە ڕووخا، و قازی محەممەد لە سێدارە درا.
```
**On-screen text:**
```
مەهاباد 1946 | پاراستنی دەرەکی ← 11 مانگ
```

### S22 · 4 Evidence · 5:43 · 11.7s · OPTIONAL CUT
**Style:** timeline with broken links
**Visual:** Timeline: 1975 → chain link snaps. Map arrow Iran→Iraq disappears. Tool label: 'Algiers Agreement, 1975'.
**Files:** G07_broken_chain (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
و چیرۆکەکە دووبارە بووەوە. لە 1975، دوای ڕێککەوتنی جەزائیر لە نێوان عێراق و ئێران، پشتیوانی لە شۆڕشی مەلا مستەفا بارزانی کێشرایەوە، و شۆڕشەکە ڕووخا.
```
**On-screen text:**
```
1975 | ڕێککەوتنی جەزائیر ← ڕووخانی شۆڕش
```

### S23 · 4 Evidence · 5:54 · 17.2s
**Style:** pattern timeline + quote card
**Visual:** Horizontal timeline of five dots: 1975 · 1991 · 2003 · 2014 · 2019. Dots turn from green to grey. Quote card: «a tactical partner, not a strategic ally». Real footage of convoys leaving NE Syria, Oct 2019 (news, credited).
**Files:** R18_us_withdrawal_2019.mp4
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
سەبارەت بە ئەمریکاش، توێژینەوەکە دەڵێت وەک «هاوبەشێکی تاکتیکی» مامەڵەی لەگەڵ کورد کردووە، نەک «هاوپەیمانێکی ستراتیژی»: پشتیوانی لە 1991، هاوپەیمانی لە شەڕی داعشدا، پاشان کشانەوەیەک لە 2019 کە زۆر لە کورد بە پشتبەردان وەسفیان کرد.
```
**On-screen text:**
```
«هاوبەشی تاکتیکی… نەک هاوپەیمانی ستراتیژی»
```

### S24 · 4 Evidence · 6:12 · 18.1s
**Style:** magazine portrait wall
**Visual:** Magazine spread: tall cut-out cards with names and one-line labels (no faces for medieval scholars — use manuscript/calligraphy cards; real photo only for Said Nursi). Big pull-quote in saffron.
**Files:** R19_said_nursi_portrait.jpg, A05_islamic_manuscript_library.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
لە بەرامبەردا، بەڵگەیەکی جۆرێکی تر هەیە: کورد لە پەراوێزی شارستانیەتی ئیسلامیدا نەبوون، بەڵکو لە ناوەندیدا بوون. ئیبن سەلاحی شارەزووری لە زانستی فەرموودەدا، ئەبولفیدای ئەیووبی لە مێژوو و جوگرافیادا، مەولانا خالیدی نەقشبەندی، و بەدیعوززەمان سەعیدی نوورسی لە سەدەی بیستەمدا.
```
**On-screen text:**
```
«ئێمە لەم بۆشاییە شارستانییەدا تازە نین… ئێمە لە بنیاتنەرانین»
```

### S25 · 4 Evidence · 6:30 · 14.4s
**Style:** archival + text behind subject
**Visual:** Real archival photo of Sheikh Said and companions, 1925 (public domain), cut-out. Words 'Naqshbandi · Qadiri' behind the figures. Then a calm photo of a Sufi tekke courtyard (real).
**Files:** R20_sheikh_said_1925.jpg, R21_tekke_courtyard.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
تەنانەت ڕاپەڕینە گەورەکان، وەک ڕاپەڕینی شێخ عوبەیدوڵڵای نەهری و ڕاپەڕینی شێخ سەعیدی پیران لە 1925، شێخانی تەریقەتی نەقشبەندی سەرکردایەتییان کرد. ئایین دوژمنی ناسنامەی کوردی نەبوو، بەڵکو بەشێک بوو لە ڕایەڵەکەی.
```
**On-screen text:**
```
ئایین: بەشێک لە ڕایەڵە… نەک دوژمن
```

### S26 · 4 Evidence · 6:44 · 26.3s
**Style:** aerial + mosaic of communities
**Visual:** Real aerial/drone footage of Erbil Citadel. Mosaic tiles light up: Kurds · Arabs · Turkmen · Christians. Then a second row: Sunni · Feyli Shia · Alevi · Yazidi · Kakai · Christian.
**Files:** R22_erbil_citadel_aerial.mp4, R11_erbil_citadel.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
یەکێکی تر لە بەڵگەکان: هەرێمی کوردستانی عێراق، کە زیاتر لە 20 ساڵە بە دامەزراوەکانییەوە لە ناو دەوڵەتێکی فیدراڵیدا کار دەکات، و هەولێر کە کورد، عەرەب، تورکمان و مەسیحی تێیدا دەژین. کۆمەڵگەی کوردیش خۆی هەمەڕەنگە: سوننە، شیعەی فەیلی، عەلەوی، ئێزیدی، کاکەیی و مەسیحی. هەمەڕەنگییەک کە دەوڵەمەندییە… و تاقیکردنەوەیە بۆ هەر گێڕانەوەیەک کە دەیەوێت خەڵک کۆبکاتەوە.
```
**On-screen text:**
```
هاوبەشی دەکرێت · هەمەڕەنگی = دەوڵەمەندی + تاقیکردنەوە
```

### S27 · 5 Counterarguments · 7:10 · 24.4s
**Style:** CHAPTER: Counter-narratives + verdict stamp ◐
**Visual:** Chapter card. Claim on a torn paper strip; verdict stamp lands ◐ 'partly'. Bar: 92.73% 'yes' → isolation icons (closed airspace, borders). Same verdict template for S27–S32.
**Files:** R23_referendum_2017.jpg, G08_verdict_cards (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
ئێستا، گێڕانەوە دژەکان. یەکەمیان: «دۆزی کورد پڕۆژەیەکی جیابوونەوەیە و یەکێتیی دەوڵەتان دەخاتە مەترسییەوە». ئایا ڕاستە؟ تەنها بەشێکی. بەڵێ، لە ڕیفراندۆمی 2017 نزیکەی 93%ی دەنگدەران «بەڵێ»یان دا، بەڵام بە شێوەی هەرێمی و نێودەوڵەتی گۆشەگیر کرا و جێبەجێ نەکرا. لە بەرامبەردا، ئەزموونی هەرێم سەلماندی کە خۆبەڕێوەبەری لە ناو دەوڵەتدا عێراقی لەتوپەت نەکرد.
```
**On-screen text:**
```
«جیابوونەوە»؟ ◐ بەشێکی
```

### S28 · 5 Counterarguments · 7:35 · 22.2s
**Style:** verdict ◐ + split
**Visual:** Verdict ◐. Split card: left 'the generalisation falls' (grey ✗), right 'the lesson stays' (saffron ✓) with mini-timeline Mahabad 1946 · Algiers 1975 · 2019.
**Files:** G08_verdict_cards (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
دووەمیان: «کورد ئامرازێکن لە دەستی هێزە دەرەکییەکاندا». لێرەدا ڕاستییەکە دوولایەنەیە. گشتاندنەکە ڕاست نییە: تۆمەتی بەکرێگیراوی زۆرجار بۆ پاساودانی سەرکوت بەکارهاتووە، و هەموو دەوڵەتانی ناوچەکە هاوپەیمانییان لەگەڵ دەرەوە هەیە. بەڵام وانەکە دەمێنێت: پشتبەستن بە دوورەکان چەندین جار کوردی گران کەوتووە، لە مەهابادەوە بۆ جەزائیر بۆ 2019.
```
**On-screen text:**
```
«ئامرازی دەرەوە»؟ ◐ گشتاندن ڕاست نییە… وانەکە دەمێنێت
```

### S29 · 5 Counterarguments · 7:57 · 25.8s
**Style:** verdict ✗ + calligraphy
**Visual:** Verdict ✗ on 'contradiction'. Then the Qur'anic verse (49:13) in elegant Arabic calligraphy on paper, gold ink, with the translation line underneath in ckb/kmr. Calm nasheed-free ambient.
**Files:** A06_calligraphy_desk.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026); Qur'an 49:13
**Narration:**
```
سێیەمیان: «کورد پێش ئەوەی کورد بن موسوڵمانن، و نەتەوەیی هاوردەیەکی ڕۆژئاواییە کە ئوممەت پارچە دەکات». زانایانی کورد، لەوانە نوورسی، وەڵام دەدەنەوە کە هەمەڕەنگی نیشانەیەکە لە نیشانەکانی خوا: «وجعلناكم شعوبًا وقبائل لتعارفوا» — کردووینن بە گەل و هۆز تا یەکتر بناسن. دانپێدانان بە ناسنامە دژی ئیسلام نییە… ئەوەی دژیەتی دەمارگیری و ستەمە، لە هەر لایەکەوە بێت.
```
**On-screen text:**
```
«وجعلناكم شعوبًا وقبائل لتعارفوا»
کردووینن بە گەل و هۆز تا یەکتر بناسن
```

### S30 · 5 Counterarguments · 8:23 · 14.9s
**Style:** verdict ✗
**Visual:** Verdict ✗. A stereotype label 'tribal' peels off a photo of a modern Erbil/Sulaymaniyah university campus (real).
**Files:** R24_university_campus_kurdistan.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
چوارەمیان: «کورد توندوتیژی و هۆزگەرین». بەڵگە بە شەڕی ناوخۆی نێوان دوو پارتە سەرەکییە کوردییەکە لە نەوەدەکاندا دەهێننەوە. بەڵام هەموو کۆمەڵگەکان ململانێی ناوخۆیان بینیوە، و کورتکردنەوەی گەلێکی تەواو بۆ هۆز، وێنەسازییەکی ڕەتکراوەیە.
```
**On-screen text:**
```
«توندوتیژی و هۆزگەری»؟ ✗ وێنەسازی
```

### S31 · 5 Counterarguments · 8:38 · 19.0s
**Style:** verdict ◐
**Visual:** Verdict ◐. A puzzle with missing pieces; label: 'divisions = partly the result of partition and repression'. Switzerland example as a small tool label.
**Files:** G08_verdict_cards (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
پێنجەمیان: «کورد دابەشبوون، کەواتە هیچ مەرجێکیان نییە». ئەمە وەک دەستنیشانکردن بەشێکی ڕاستە: دابەشبوون ڕاستییە. بەڵام وەک حوکمی کۆتایی ڕاست نییە، چونکە هەمەڕەنگی ڕێگر نییە لە بنیاتنانی قەوارەیەکی یەکگرتوو، و دابەشبوونەکان بە بەشێکی زۆر بەرهەمی دابەشکردن و سەرکوتن، نەک سروشتی گەل.
```
**On-screen text:**
```
«بێ مەرج»؟ ◐ دەستنیشانکردن ڕاستە… حوکم هەڵەیە
```

### S32 · 5 Counterarguments · 8:57 · 24.4s
**Style:** verdict ✗ + news footage
**Visual:** Verdict ✗ on 'only arms bring rights'. Counter: 40,000+. Then real news footage of the July 2025 weapons-burning ceremony near Sulaymaniyah (credited, no logos).
**Files:** R25_pkk_weapons_ceremony_2025.mp4
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026); Reuters / AP, May–July 2025
**Narration:**
```
گێڕانەوەیەکیش لە ناوەوە هەیە: کە ماف تەنها بە چەک بەدەست دێت. بەڵام مێژووی نزیک شتێکی تر دەڵێت. ململانێی چەکداری لە تورکیا، بەپێی ژمارە فەرمییەکان، زیاتر لە 40 هەزار کوژراوی لێکەوتەوە، و لە 2025 پارتی کرێکارانی کوردستان هەڵوەشاندنەوەی خۆی ڕاگەیاند، و ڕێگایەکی نوێ دەستی پێکرد کە هێشتا لە پێکهاتندایە.
```
**On-screen text:**
```
+40,000 کوژراو ← 2025: ڕاگەیاندنی هەڵوەشاندنەوە
```

### S33 · 6 Stakes · 9:21 · 21.3s
**Style:** CHAPTER: Stakes + real footage
**Visual:** Chapter card. Real footage: Damascus Dec 2024, then the Jan 2026 signing / decree coverage. Lower-third with dates. Timeline bar reaches 'now'.
**Files:** R26_damascus_dec2024.mp4, R27_syria_jan2026_agreement.mp4
**Source line:** Al Jazeera English, 17 & 30 Jan 2026
**Narration:**
```
ئەی ئەمڕۆ؟ لە سووریا، دوای ڕووخانی ڕژێم لە کانوونی یەکەمی 2024، لە کانوونی دووەمی 2026 فەرمانی 13 دەرچوو کە دانی بە کوردیدا نا وەک زمانێکی نیشتمانی، و ڕێککەوتن کرا لەسەر تێکەڵکردنی هێزەکانی سووریای دیموکرات لە دامەزراوەکانی دەوڵەتدا. ڕێگاکە هێشتا لە سەرەتایە.
```
**On-screen text:**
```
سووریا 2026 | فەرمانی 13 + ڕێککەوتنی تێکەڵبوون
```

### S34 · 6 Stakes · 9:42 · 16.7s
**Style:** two doors, dark slide
**Visual:** Two doors on a dark slide: left door cold blue 'enmity', right door warm 'partnership'. The camera pushes toward the warm door (M3).
**Files:** A07_two_doors_corridor.jpg → MOTION M3
**Source line:** —
**Narration:**
```
ئەمە بۆ ئێمە چی دەگەیەنێت؟ واتە ناوچەکە دەچێتە قۆناغێکەوە کە تێیدا چیرۆکەکان دووبارە دەکێشرێنەوە. پرسیارەکە ئیتر تەنها ئەوە نییە: کورد چییان دەوێت؟ بەڵکو: چ چیرۆکێک لەسەر خۆیان و دراوسێکانیان دەگێڕنەوە؟ چیرۆکی دوژمنایەتی… یان چیرۆکی هاوبەشی؟
```
**On-screen text:**
```
چیرۆکی دوژمنایەتی… یان چیرۆکی هاوبەشی؟
```

### S35 · 6 Stakes · 9:59 · 16.3s
**Style:** 4 scenario cards
**Visual:** Four cards slide in like a magazine contents page: 1 status quo · 2 gradual wider recognition · 3 escalation (red, everyone loses) · 4 regional repositioning. Card 2 stays highlighted.
**Files:** G09_scenario_cards (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
توێژینەوەکە چوار سیناریۆ دەکێشێت: بەردەوامبوونی دۆخی ئێستا، یان دانپێدانانێکی فراوانتری قۆناغ بە قۆناغ، یان تەشەنەسەندنێک کە هەمووان تێیدا دەدۆڕێن، یان گۆڕانێکی گەورەی هەرێمی کە شێوازێکی نوێ دەکاتەوە. کامیان ڕوودەدات، بەشێکی پەیوەستە بەو چیرۆکەی هەڵیدەبژێرین.
```
**On-screen text:**
```
1 دۆخی ئێستا · 2 دانپێدانانی فراوانتر · 3 تەشەنەسەندن · 4 گۆڕانی هەرێمی
```

### S36 · 6 Stakes · 10:15 · 22.6s
**Style:** animated checklist over landscape
**Visual:** Checklist ticks over a wide shot of a shared market/bazaar (real, Erbil or Diyarbakır). Last line lands bigger, in saffron.
**Files:** R28_bazaar_erbil_or_diyarbakir.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
توێژینەوەکە ڕاسپاردەی گێڕانەوەیەک دەکات کە لە سەروو حزبایەتییەوە بێت، توندوتیژی دژی مەدەنییەکان لە هەر لایەکەوە بێت ئیدانە بکات، لەگەڵ عەرەب، تورک و فارس وەک دراوسێ و هاوبەش گفتوگۆ بکات نەک دوژمن، و پشت بە سەرمایەی کورد لە شارستانیەتی ئیسلامیدا ببەستێت. گێڕانەوەیەک کە ڕۆڵەکانی ناوچەکە دەینووسن… نەک حیساباتی دوورەکان.
```
**On-screen text:**
```
✓ سەروو حزبایەتی ✓ دژی توندوتیژی ✓ دراوسێ نەک دوژمن ✓ سەرمایەی شارستانی
ڕۆڵەکانی ناوچەکە دەینووسن
```

### S37 · 7 Closing · 10:38 · 6.7s
**Style:** CHAPTER: Closing — callback to S01
**Visual:** Chapter card. Callback: the same mountains as S01 (M1), now at golden hour. Text fades in quietly.
**Files:** A01_zagros_mountains_mist.jpg → MOTION M1
**Source line:** —
**Narration:**
```
لەوانەیە ڕۆژێک چیاکان تاکە دۆستی کورد بووبن. بەڵام چیاکان چیرۆک نانووسن… خەڵک دەینووسن.
```
**On-screen text:**
```
چیاکان چیرۆک نانووسن
```

### S38 · 7 Closing · 10:45 · 14.0s
**Style:** text behind people, warm grade
**Visual:** Silhouettes of a group of young people walking together at dusk toward a town (A08). Final line in giant type behind them. 1 s silence before the last two words.
**Files:** A08_group_walking_dusk.jpg → MOTION M4
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
توێژینەوەکە بە هیوایەکی سادە کۆتایی دێت: کورد دۆستی لە مرۆڤەکان هەبێت، نەک تەنها لە چیاکان. و نزیکترینیان دوورەکان نین… بەڵکو ئەو دراوسێیانەن کە زەوی، مێژوو و ئیمانیان لەگەڵدا هاوبەشە.
```
**On-screen text:**
```
دۆست لە مرۆڤەکان… نەک تەنها لە چیاکان
```

### S39 · 7 Closing · 10:59 · 15.3s
**Style:** dark slide + teaser end card
**Visual:** Black slide, the question. Then end card: logo, channel name, 'Next: belongings' teaser tag, subscribe/comment prompt. No sources slide.
**Files:** dwin_logo.png
**Source line:** —
**Narration:**
```
کەواتە چ چیرۆکێک بۆ منداڵەکانمان دەگێڕینەوە؟ لە ئەڵقەکانی داهاتوودا، زیاتر باسی ئەم پێوەبەستبوونانە دەکەین: کوردی، ئیسلامی و هەرێمی… و چۆن دەتوانن لە یەک دیدگادا کۆببنەوە. بە ئارامی ڕای خۆت لە کۆمێنتەکاندا بنووسە.
```
**On-screen text:**
```
چ چیرۆکێک بۆ منداڵەکانمان دەگێڕینەوە؟
بەم زووانە: پێوەبەستبوونەکان
```

## 6. After the video is finished: thumbnails (required)
When the Kurdish Sorani video is final, ALSO create its YouTube thumbnails in both formats, following THUMBNAILS.md:
- `thumbnails/thumb_ckb_16x9.png` (1280×720, <2 MB)
- `thumbnails/thumb_ckb_9x16.png` (1080×1920, Shorts/Reels cover)
Use the brand font, the logo top-left, and text in this language only. Render them with Playwright and check them at phone size (160 px wide).

## 7. Publishing texts
Ready in `social/youtube_ckb.md` and `social/facebook_instagram_ckb.md`. After the final edit, update the chapter timestamps there to the real times; the first chapter must stay at 0:00.

## 8. Fact notes
- Population figures are estimates (no ethnic census in most states); always show them as ranges.
- Anfal deaths: 50,000–182,000 depending on the source; Iraqi High Tribunal genocide ruling 2007.
- Mulla Jami is listed as Kurdish in the study, but he was Persian, so he was removed. Ibn al-Athir is cited as a historian who wrote about Kurds, not as a Kurd.
- The study ends before the 2025 PKK dissolution announcement and the Jan 2026 Syria agreements; both were added from news sources.
- The Ahmad Khani line in S09 is a paraphrase from the study's Arabic rendering, not a verse translation.