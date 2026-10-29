# Dwin Vox-style explainer — Kurdish Sorani (RTL)

## 1. Role and goal
You are a senior motion designer and video editor. Build an 9.1-minute Vox-style explainer in Kurdish Sorani on belonging among Kurdish youth in Syria during and after the revolution. Tone: professional, calm, balanced, NOT nationalist, NOT against any group. The video explains; it does not campaign.

## 2. Editorial rules
- Use narration and on-screen text EXACTLY as written below. Do not translate, shorten or 'fix' them.
- Every number/claim shows a small source line (bottom corner, 60% opacity) from the scene's `Source` field.
- Never fake real records with AI (decrees, IDs, official posts, protest footage). AI images get a small 'illustration' tag.
- No AI images of real people's faces. AI people are always seen from behind, in silhouette or as hands.
- Protest/clash footage: no graphic violence, blur minors' faces, credit the agency in the lower-third.
- No sources slide at the end. Sources go in the description only.

## 3. Technical spec
- Master 1920×1080, 24 fps, H.264 high, AAC 48 kHz, −14 LUFS integrated, true peak −1 dB.
- Second export 1080×1920 (9:16): reframe each scene (centre-crop photos, re-layout graphics vertically, captions move to the lower third, safe zone 250 px bottom / 150 px top).
- Shield logo TOP-LEFT on EVERY scene in every language (fixed brand rule, not mirrored), 90 px high, 40 px margin, 85% opacity.
- Font: Speda (fallback Noto Naskh Arabic). Shape text with a real engine (Playwright/Chromium or HarfBuzz) — never draw Arabic-script glyphs one by one.
- Direction RTL: mirror all layouts; timeline bar runs right→left; text reveals and wipes move right→left; charts start from the right.
- Palette: paper #EFE8DC, ink #1B1B1B, dark slide #111418, accent saffron #E8A33D, muted red #B5483A, muted green #4F7C5A (accent use only, never as a flag).
- Look: paper grain overlay (8%), cut-out photos with 6 px white border and soft shadow, 2.5D parallax on photos, ink-drawn arrows/circles, film grain on archival scenes.
- Captions: burned-in, 2 lines max, 46 px, white on 70% black box, word-level highlight in saffron. Also export .srt from `subtitles/`.
- Transitions: paper-slide push (default), hard cut to dark slide for chapter cards, whip-pan whoosh between real footage, match cut S02→S32 (the '1962' callback).
- 'Text behind person' (S04, S32): segment the subject with rembg / MediaPipe Selfie Segmentation, layer: background → giant title → subject matte → captions.
- Tool / lower-third labels: rounded tag, 28 px, icon + text, slides in from the reading side.
- Chapter cards (dark slides) at S04, S11, S16, S23, S27: number + chapter name, 2.5 s, low boom hit.

## 4. Voice and music
- Voice: one calm, warm, mid-low narrator, native Kurdish Sorani, measured pace, no drama. Human narrator recommended (ElevenLabs has no official Kurdish support).
- Music: royalty-free, no vocals. Act 1 (S01–S10): soft piano + low strings; Act 2 (S11–S22): light pulse, curious; Act 3 (S23–S29): sparse, thoughtful; S30–S33: warm build, 1 s silence before 'we are here', then soft resolve. Duck −18 dB under voice.
- SFX (subtle): paper slide, stamp, pencil scratch, typewriter tick, soft click on checklist, whoosh.

## 5. Scene by scene (total ≈ 9.1 min)

### S01 · 1 Hook · 00:00:00 · 14.3s
**Style:** dark slide + slow push-in
**Visual:** Young person seen from behind on a rooftop at dusk over a Jazira town. Kinetic caption builds word by word. Paper grain overlay.
**Files:** A01_rooftop_from_behind.jpg → MOTION M1
**Source line:** —
**Narration:**
```
وێنا بکە لە وڵاتی خۆت لەدایک ببیت، تێیدا گەورە ببیت… پاشان بزانیت دەوڵەت لەسەر کاغەز بوونت ناناسێت. ئەمە چیرۆکی خەیاڵی نییە، ژیانی دەیان هەزار کوردی سووریا بوو.
```
**On-screen text:**
```
لێرە لەدایکبووە… بەڵام لەسەر کاغەز نییە
```

### S02 · 1 Hook · 00:00:14 · 12.8s
**Style:** magazine big number + stamp sound
**Visual:** Giant year '1962' slams in, then the counter rolls to 120,000. Blank paper document (AI, labelled illustration) with a red ink circle drawn by hand.
**Files:** A02_blank_paper_document.jpg
**Source line:** Arab News PK, Jan 2026
**Narration:**
```
لە ساڵی ١٩٦٢، دەسەڵات سەرژمێرییەکی نائاسایی لە پارێزگای حەسەکە ئەنجامدا. لە ئەنجامدا، زیاتر لە سەد و بیست هەزار کورد لە ڕەگەزنامەی سووری بێبەش کران.
```
**On-screen text:**
```
١٩٦٢ | زیاتر لە ١٢٠٬٠٠٠ کورد بێ ڕەگەزنامە
```

### S03 · 1 Hook · 00:00:27 · 19.3s
**Style:** dark slide, question in huge type
**Visual:** Cut to black. Question types in letter by letter with a soft typewriter tick. Faint crowd silhouettes behind.
**Files:** A13_crowd_silhouettes_dusk.jpg
**Source line:** —
**Narration:**
```
ئەمڕۆ، نەوەیەک کە زۆر دوای ئەو ساڵانە لەدایکبووە، شۆڕش و جەنگ و ئاوارەیی بینیوە، پرسیارێکی سادە و قورس دەکات: ئێمە سەر بە کوێین؟ ئەم ڤیدیۆیە باسی دروشم ناکات، باسی نەوەیەک دەکات کە بە ئارامی دەیەوێت خۆی بناسێنێت.
```
**On-screen text:**
```
ئێمە سەر بە کوێین؟
```

### S04 · 1 Hook · 00:00:46 · 6.3s
**Style:** TITLE CARD: text behind person
**Visual:** Title in giant type placed BEHIND the person (segmentation matte of A08 or M1). Slow parallax. Logo stays top corner.
**Files:** A08_young_woman_from_behind_sunrise.jpg
**Source line:** —
**Narration:**
```
پێوەبەستبوونی گەنجانی کورد لە سووریا… لە ماوەی شۆڕش و دوای ئەو.
```
**On-screen text:**
```
پێوەبەستبوون
گەنجانی کورد لە سووریا
```

### S05 · 2 Context · 00:00:52 · 16.8s
**Style:** animated map
**Visual:** Paper-texture map of Syria (Natural Earth). Dots light up: Hasakah, Qamishli, Kobani, Afrin, Aleppo, Damascus. City labels as lower-third tags.
**Files:** G01_map_syria_kurdish_areas (Claude Code), R10_kobani_city_view.jpg
**Source line:** Arab News PK, Jan 2026
**Narration:**
```
با لە بنەڕەتەوە دەست پێبکەین. نزیکەی دوو ملیۆن و نیو کورد لە سووریا دەژین، زۆربەیان لە باکوور و باکووری ڕۆژهەڵات: حەسەکە، قامیشلۆ، کۆبانی و عەفرین، لەگەڵ گەڕەکی گەورە لە حەلەب و دیمەشق.
```
**On-screen text:**
```
≈ ٢٫٥ ملیۆن کورد لە سووریا
```

### S06 · 2 Context · 00:01:09 · 15.3s
**Style:** two cut-out cards, split screen
**Visual:** Two paper cards slide in from opposite sides: 'ajanib' and 'maktoumeen'. Icons: house, briefcase, plane, rings, baby — each crossed by an ink line.
**Files:** A12_family_album_hands.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
سەرژمێریی ١٩٦٢ دوو توێژی دروستکرد: «بیانییەکان» کە بێ ڕەگەزنامە تۆمارکران، و «مەکتومەکان» کە هەرگیز تۆمار نەکران. بێ ناسنامە، خاوەنداریەتی، کار، گەشت و تەنانەت تۆمارکردنی هاوسەرگیری و منداڵیش قورس دەبێت.
```
**On-screen text:**
```
«بیانی» و «مەکتوم»
```

### S07 · 2 Context · 00:01:24 · 17.3s
**Style:** map + timeline bar
**Visual:** Timeline bar at bottom jumps to 1973. On the map a thin strip along the northern border fills with hatched ink. A blank village road sign (AI) has its name smudged.
**Files:** G01_map_syria_kurdish_areas (Claude Code), A04_blank_village_sign_wheat.jpg
**Source line:** Arab News PK, Jan 2026
**Narration:**
```
لە ساڵی ١٩٧٣، لە سەردەمی حافز ئەسەد، پرۆژەی «پشتێنەی عەرەبی» جێبەجێکرا: خێزانی عەرەب گوازرانەوە بۆ پشتێنەیەک بە درێژایی سنووری باکوور، و ناوی گوندە کوردییەکان گۆڕدرا. ئەمە سیاسەتی دەوڵەت بوو، نەک ناکۆکی نێوان دراوسێکان.
```
**On-screen text:**
```
١٩٧٣ | «پشتێنەی عەرەبی»
```

### S08 · 2 Context · 00:01:42 · 15.8s
**Style:** warm archival look
**Visual:** Old radio glowing in a kitchen at night, hands of a parent turning the dial. Film grain, vignette. Caption fades in like handwriting.
**Files:** A03_old_radio_kitchen_night.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
زمانیش، بۆ چەندین دەیە لە دەرەوەی قوتابخانە و فەرمانگە فەرمییەکان مایەوە. منداڵان لە ماڵ، لە گۆرانی و ڕادیۆوە فێری بوون. بەم شێوەیە وشەی کوردی خۆی بوو بە جۆرێک لە یادەوەری.
```
**On-screen text:**
```
زمانێک کە لە ماڵ فێردەبوو
```

### S09 · 2 Context · 00:01:57 · 19.8s
**Style:** timeline + counter
**Visual:** Timeline jumps to 2011. Counter rolls to ≈104,000. Then a suitcase at a bus station (AI) as the music darkens.
**Files:** A06_suitcase_bus_station.jpg
**Source line:** UNHCR (via Arab News PK)
**Narration:**
```
پاشان ساڵی ٢٠١١ هات. لەگەڵ دەستپێکی شۆڕش، فەرمانی ژمارە ٤٩ دەرچوو، و نزیکەی سەد و چوار هەزار کەس تا ناوەڕاستی ٢٠١٣ ڕەگەزنامەیان وەرگرت. بەڵام ئەو جەنگەی دوای ئەوە هات، ئاوارەیی و کۆچی هێنا، و ژیانی نەوەیەکی تەواوی گۆڕی.
```
**On-screen text:**
```
٢٠١١ | فەرمانی ٤٩ ← ≈١٠٤٬٠٠٠ ڕەگەزنامە
```

### S10 · 2 Context · 00:02:17 · 15.8s
**Style:** real footage + lower-third
**Visual:** Real footage: Damascus crowds Dec 2024, then the Decree 13 announcement. Lower-third label with date. Whoosh transition between the two.
**Files:** R07_damascus_dec2024_crowds.mp4, R03_decree13_announcement.mp4
**Source line:** Al Jazeera English, 17 Jan 2026
**Narration:**
```
لە کانوونی یەکەمی ٢٠٢٤، ڕژێمی ئەسەد ڕووخا. لە ١٦ی کانوونی دووەمی ٢٠٢٦ـیش، سەرۆک ئەحمەد شەرع فەرمانی ژمارە ١٣ی تایبەت بە مافەکانی کوردی ڕاگەیاند. لەناکاو، پرسیارە کۆنەکە بوو بە پرسیارێکی کردەیی.
```
**On-screen text:**
```
١٢/٢٠٢٤ ← ١٦/١/٢٠٢٦ | فەرمانی ١٣
```

### S11 · 3 Core problem · 00:02:33 · 16.3s
**Style:** CHAPTER: dark slide + portrait cut-out
**Visual:** Chapter card 'The core problem'. Real public-domain portrait of Karl Mannheim as a paper cut-out with tool label 'Karl Mannheim | sociologist'.
**Files:** R09_karl_mannheim_portrait.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
کۆمەڵناس کارل مانهایم دەیگوت نەوە تەنها بە تەمەن ناناسرێت، بەڵکو بەو ڕووداوە گەورانەی کە پێکەوە لە تەمەنی پێگەیشتندا دەیانژین. گەنجانی کورد ئەمڕۆ نەوەیەکن کە لە ناو دڵی شۆڕش و جەنگدا پێکهاتوون.
```
**On-screen text:**
```
نەوە = ئەزموونی هاوبەش
```

### S12 · 3 Core problem · 00:02:49 · 16.3s
**Style:** triptych magazine layout
**Visual:** Three vertical panels reveal one by one: ruined street (AI), suitcase/map with lines Qamishli–Erbil–Berlin, phone glow. Icons and labels.
**Files:** A06_suitcase_bus_station.jpg, A05_phone_in_hands_music.jpg → MOTION M3
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
سێ هێز ئەم نەوەیەیان داڕشت: جەنگ کە ئاسایشی کردە پرسیارێکی ڕۆژانە، کۆچ کە خێزانەکانی لە نێوان قامیشلۆ و هەولێر و بەرلیندا پەرتکرد، و جیهانی دیجیتاڵ کە بوو بە گۆڕەپانێکی نوێی دەربڕین.
```
**On-screen text:**
```
جەنگ · کۆچ · دیجیتاڵ
```

### S13 · 3 Core problem · 00:03:06 · 16.8s
**Style:** UI mock + echo effect
**Visual:** Hands holding a phone (AI); generic, invented app UI (no real brand) with Kurdish song cards. Then the frame duplicates into echoing mirrored copies (echo chamber).
**Files:** A05_phone_in_hands_music.jpg, A05_phone_in_hands_music.jpg → MOTION M3
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
لەسەر شاشەکان، زمانی کوردی ژیانی گەڕایەوە: گۆرانی، پەڕە، وانە و گفتوگۆ لە نێوان گەنجانێک کە هەرگیز یەکتریان نەبینیوە. بەڵام هەمان جیهان دەکرێت ببێتە ژووری دەنگدانەوە، کە هەر لایەک تەنها دەنگی خۆی ببیستێت.
```
**On-screen text:**
```
شوێنێک بۆ زمان… یان ژووری دەنگدانەوە؟
```

### S14 · 3 Core problem · 00:03:22 · 13.3s
**Style:** Venn diagram, ink drawn
**Visual:** Two circles draw themselves: 'Kurdish' and 'Syrian'. The overlap fills and reads 'Kurdish Syrian'. A key labelled 'equal citizenship' unlocks the overlap.
**Files:** G02_venn_identity (Claude Code)
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
لێرەدایە کڕۆکی پرسەکە: ئایا گەنج دەبێت لە نێوان کوردبوون و سووریبووندا هەڵبژێرێت؟ توێژینەوەکە دەڵێت: نەخێر. ناسنامەی دووانەی «کوردی سووری» دەکرێت… بە یەک مەرج: هاووڵاتیبوونی یەکسان.
```
**On-screen text:**
```
کوردی سووری = دەکرێت ← بە مەرجی هاووڵاتیبوونی یەکسان
```

### S15 · 3 Core problem · 00:03:36 · 20.8s
**Style:** split-screen diverging paths
**Visual:** Split screen: left path dims and leads to a departing bus; right path brightens into a classroom. Arrows drawn in ink.
**Files:** A09_crossroads_paths.jpg, A07_empty_classroom.jpg
**Source line:** —
**Narration:**
```
بۆچی ئەمە گرنگە؟ چونکە ئەو گەنجەی هەست بە دوورخستنەوە دەکات، کشانەوە دەکات، کۆچ دەکات یان دادەخرێت. بەڵام ئەوەی هەست دەکات جێگەی هەیە، بنیات دەنێت و بەشداری دەکات. پێوەبەستبوون تەنها هەست نییە؛ ئەوەیە کە دیاری دەکات نەوەیەکی تەواو دەمێنێتەوە یان دەڕوات.
```
**On-screen text:**
```
دوورخستنەوە ← کشانەوە | دانپێدانان ← بەشداری
```

### S16 · 4 Evidence · 00:03:57 · 16.8s
**Style:** CHAPTER: Evidence + qualitative scale
**Visual:** Chapter card 'Evidence'. Three stacked speech bubbles of decreasing size: 'Kurdish' (large), 'Kurdish Syrian' (medium), 'Syrian' (small). Footnote tag: 'qualitative study — not survey percentages'.
**Files:** G03_self_definition_bubbles (Claude Code)
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
ئەم گەنجانە چۆن خۆیان دەناسێنن؟ بەپێی توێژینەوەکە، زۆربەیان بە سادەیی دەڵێن: «من کوردم». هەندێکیان دەڵێن: «کوردی سووریم». و کەمێکیان تەنها دەڵێن «سووریم». ئەوەی دیارە ئەوەیە کە ناسنامە جێگیر نییە، لەگەڵ بارودۆخدا دەگۆڕێت.
```
**On-screen text:**
```
زۆربەیان: کورد · هەندێک: کوردی سووری · کەم: سووری
```

### S17 · 4 Evidence · 00:04:13 · 12.8s
**Style:** quote card
**Visual:** Dark quote card, big quotation marks, highlighted phrase. Background: hands writing Kurdish letters in a notebook (AI).
**Files:** A10_hands_writing_notebook.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
زمانیش شوێنێکی تایبەتی هەیە. توێژینەوەکە بەکارهێنانی کوردی بە «بەرگرییەکی هێمایی» وەسف دەکات: نەک چەک، بەڵکو ڕێگەیەکی ئارام بۆ گوتنی: ئێمە لێرەین، و یادەوەریمان هەیە.
```
**On-screen text:**
```
زمان = «بەرگریی هێمایی»
```

### S18 · 4 Evidence · 00:04:26 · 17.8s
**Style:** two-column magazine spread
**Visual:** Village mosque dome at dawn (AI) left; right column: 'social presence ✓ / political determinant ✗'. Respectful, calm.
**Files:** A15_village_mosque_dawn.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
ئەی ئایین؟ ئامادەیی ئایینی لە کۆمەڵگەی کوردیدا ڕوونە، لە تەریقەتی نەقشبەندییەوە تا شێخایەتی خەزنەوی. بەڵام توێژینەوەکە تێبینی دەکات کە ئایین ئەوە نییە کە ناسنامەی سیاسیی گەنجان دیاری بکات؛ بەشێکە لە ژیان، نەک ناونیشانی سیاسیی.
```
**On-screen text:**
```
ئایین: ئامادەیی کۆمەڵایەتی · نەک دیاریکەری سیاسی
```

### S19 · 4 Evidence · 00:04:44 · 20.3s
**Style:** animated checklist
**Visual:** Five checkmarks tick in one by one over real Nowruz footage (blurred, darkened). Each item gets a soft click.
**Files:** R04_nowruz_qamishli_2026.mp4
**Source line:** Al Jazeera English, 17 Jan 2026
**Narration:**
```
فەرمانی ١٣ هەنگاوی بەرجەستەی هێنا: دانپێدانان بە کوردی وەک زمانێکی نیشتمانی کە دەکرێت لە قوتابخانەکان بخوێندرێت، کردنی نەورۆز بە پشووی فەرمیی بە مووچە، هەڵوەشاندنەوەی ئاسەوارەکانی سەرژمێریی ١٩٦٢، پێدانی ڕەگەزنامە بە زیانلێکەوتووان لەوانەش مەکتومەکان، و قەدەغەکردنی جیاکاریی نەتەوەیی و زمانی.
```
**On-screen text:**
```
✓ کوردی زمانی نیشتمانی
✓ نەورۆز پشووی فەرمی
✓ هەڵوەشاندنەوەی سەرژمێریی ١٩٦٢
✓ ڕەگەزنامە بۆ مەکتومەکان
✓ قەدەغەکردنی جیاکاری
```

### S20 · 4 Evidence · 00:05:04 · 14.3s
**Style:** real footage + quote tag
**Visual:** Short real news footage from Aleppo Jan 2026 (no graphic images), then a quote tag «first step» with label 'Kurdish administration'.
**Files:** R06_aleppo_jan2026_news.mp4
**Source line:** Al Jazeera English, 17 Jan 2026
**Narration:**
```
فەرمانەکە دوای پێکدادانێک لە حەلەب هات کە لانیکەم بیست و سێ کەسی کردە قوربانی. ئیدارەی کوردی پێشوازیی لێکرد، بەڵام وەسفی کرد بە «هەنگاوی یەکەم»، نەک کۆتایی ڕێگا.
```
**On-screen text:**
```
«هەنگاوی یەکەم»
```

### S21 · 4 Evidence · 00:05:19 · 26.8s
**Style:** bar chart drawn to scale
**Visual:** Horizontal chart to scale: Amnesty 2005 estimate as a range band 200k–360k; Hasakah registry 1962–2011 bar 517k with footnote 'includes descendants'. Bars grow with a pencil sound.
**Files:** G04_stateless_chart (Claude Code)
**Source line:** Arab News PK, Jan 2026; Amnesty International, 2005
**Narration:**
```
بۆ تێگەیشتن لە قەبارەی ئەوەی فەرمانەکە دەیەوێت چاکی بکاتەوە: تۆمارەکانی حەسەکە ئاماژە بە زیاتر لە پێنج سەد و حەڤدە هەزار کەسی بێ ڕەگەزنامە دەکەن لە نێوان ١٩٦٢ و ٢٠١١، بە ژماردنی منداڵ و نەوەکانیشەوە. ڕێکخراوی لێبووردنی نێودەوڵەتیش لە ٢٠٠٥ ژمارەکەی بە نێوان دوو سەد هەزار و سێ سەد و شەست هەزار خەمڵاندبوو.
```
**On-screen text:**
```
تۆمارەکانی حەسەکە ١٩٦٢–٢٠١١: +٥١٧ هەزار (لەگەڵ نەوەکان)
لێبووردنی نێودەوڵەتی ٢٠٠٥: ٢٠٠–٣٦٠ هەزار
```

### S22 · 4 Evidence · 00:05:45 · 21.8s
**Style:** real footage + 'sources differ' tag
**Visual:** Real footage of the Sept 2026 student protests (from news agency, credited). Yellow tool tag: 'Sources differ: study 3 · SANA 2'.
**Files:** R05_student_protests_sep2026.mp4, A07_empty_classroom.jpg
**Source line:** Hawar News; Syria TV; SANA, Sep 2026
**Narration:**
```
بەڵام یاسا شتێکە و پۆلی خوێندن شتێکی تر. لە ئەیلوولی ٢٠٢٦، قوتابیان لە حەسەکە، قامیشلۆ و کۆبانی قوتابخانەکانیان بایکۆت کرد، وەک ناڕەزایی بەرامبەر کەمکردنەوەی وانەکانی کوردی. توێژینەوەکە باسی سێ وانە لە هەفتەیەکدا دەکات، لە کاتێکدا ئاژانسی فەرمیی سانا باسی دوو وانەی کرد.
```
**On-screen text:**
```
ئەیلوولی ٢٠٢٦ | ناڕەزایی قوتابیان
٢–٣ وانەی کوردی لە هەفتەیەکدا
```

### S23 · 5 Counterarguments · 00:06:07 · 18.3s
**Style:** CHAPTER: Counterarguments + verdict stamp
**Visual:** Chapter card 'Counterarguments'. Claim written on a torn paper strip; a verdict stamp lands: ✗ 'as a generalisation'. Same template for S23–S26.
**Files:** G05_verdict_cards (Claude Code)
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
ڕەخنەی یەکەم: «ناسنامەی کوردی پڕۆژەیەکی جیابوونەوەیە». ئایا ڕاستە؟ وەک گشتاندن، نەخێر. توێژینەوەکە نیشانی دەدات کە زۆربەی گەنجان داوای دانپێدانان دەکەن لە ناو هاووڵاتیبووندا، و پێوەبەستبوونیان شیاوی گفتوگۆیە. دەنگی توندتر هەیە، بەڵام هەموو وێنەکە نیشان نادات.
```
**On-screen text:**
```
«جیابوونەوە»؟ ✗ وەک گشتاندن
```

### S24 · 5 Counterarguments · 00:06:25 · 15.3s
**Style:** verdict card ✗
**Visual:** Same verdict template. Background: empty classroom (AI) next to protest still. Equation 'text ≠ practice' written in ink.
**Files:** A07_empty_classroom.jpg
**Source line:** Hawar News; Syria TV; SANA, Sep 2026
**Narration:**
```
ڕەخنەی دووەم: «فەرمانەکە کێشەکەی چارەسەر کرد». ئەمە ڕاست نییە. ناڕەزاییەکانی ئەیلوول نیشانی دەدەن کە دووری نێوان دەق و جێبەجێکردن هێشتا گەورەیە، لە قوتابخانە و فەرمانگەکان و وردەکاریی ژیانی ڕۆژانەدا.
```
**On-screen text:**
```
«کێشەکە کۆتایی هات»؟ ✗ دەق ≠ جێبەجێکردن
```

### S25 · 5 Counterarguments · 00:06:41 · 17.8s
**Style:** verdict card ◐
**Visual:** Half-filled verdict stamp ◐ 'partly holds'. A balance scale icon tilts slightly.
**Files:** G05_verdict_cards (Claude Code)
**Source line:** Al Jazeera English, 17 Jan 2026
**Narration:**
```
ڕەخنەی سێیەم: «دانپێدانانەکە تەنها ڕووکەشە». ئەمە بەشێکی ڕاستە. یاساکان پێویستیان بە کردار و دامەزراوە هەیە تا ببنە ڕاستی. بەڵام گەڕاندنەوەی ڕەگەزنامە بۆ ئەوانەی لێی بێبەش کرابوون، گۆڕانێکی یاسایی ڕاستەقینەیە کە ژیانی خەڵکی ڕاستەقینە دەگرێتەوە.
```
**On-screen text:**
```
«تەنها ڕووکەش»؟ ◐ بەشێکی ڕاستە
```

### S26 · 5 Counterarguments · 00:06:59 · 16.8s
**Style:** verdict card ◐
**Visual:** Verdict ◐. Background: village mosque at dawn (A15) blending into hands writing (A10) — both together, calm.
**Files:** A15_village_mosque_dawn.jpg, A10_hands_writing_notebook.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
ڕەخنەی چوارەم: «پەیوەندیی ئایینی بەسە، پێویست بە ناسنامەی نەتەوەیی ناکات». توێژینەوەکە نە پشتگیری دەکات نە دژایەتی: ئایین لە ژیانی زۆر لە گەنجاندا ئامادەیە، بەڵام پێویستییان بە دانپێدانان بە زمان و یادەوەرییان ناسڕێتەوە.
```
**On-screen text:**
```
«ئایین بەسە»؟ ◐ ئامادەیە… بەڵام جێگەی دانپێدانان ناگرێتەوە
```

### S27 · 6 Stakes · 00:07:15 · 15.3s
**Style:** CHAPTER: Stakes + three doors
**Visual:** Chapter card 'What's at stake'. Drone shot of a crossroads (animated still); three paths labelled 1-2-3; path 1 glows.
**Files:** A09_crossroads_paths.jpg → MOTION M4
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
کەواتە کارەکان بەرەو کوێ دەچن؟ توێژینەوەکە سێ سیناریۆ دەکێشێت. یەکەم: کرانەوە و تێکەڵبوون، کە تێیدا هەنگاوی وەک فەرمانی ١٣ دەبنە کرداری ڕۆژانە، و گەنجی کورد هەست دەکات هاوبەشێکی تەواوە.
```
**On-screen text:**
```
سیناریۆی ١ | کرانەوە و تێکەڵبوون
```

### S28 · 6 Stakes · 00:07:31 · 15.3s
**Style:** same layout, path 2 glows
**Visual:** Path 2 glows; colour grade cools; a door closing sound (soft).
**Files:** A09_crossroads_paths.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
دووەم: داخران و پاراستن. ئەگەر گەنجان هەست بکەن بەڵێنەکان جێبەجێ نابن، وەک لە ناڕەزاییەکانی قوتابخانەدا، لەوانەیە بەرەو ناسنامەیەکی بەرگریکاری داخراو بکشێنەوە، کە ئەوی تر وەک مەترسی ببینێت نەک هاوبەش.
```
**On-screen text:**
```
سیناریۆی ٢ | داخران و پاراستن
```

### S29 · 6 Stakes · 00:07:46 · 14.8s
**Style:** same layout, path 3 glows
**Visual:** Path 3 glows; a person sits on a bench by a window, waiting (AI, from behind). Clock tick under music.
**Files:** A14_waiting_by_window.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
سێیەم: چاوەڕوانی و ڕێکخستنەوە. نەوەیەک کە چاودێری دەکات، نە لەگەڵ کەس دەپچڕێت نە بە تەواوی پابەند دەبێت، چاوەڕێ دەکات ببینێت لەسەر زەوی چی ڕوودەدات پێش ئەوەی بڕیار بدات.
```
**On-screen text:**
```
سیناریۆی ٣ | چاوەڕوانی و ڕێکخستنەوە
```

### S30 · 6 Stakes · 00:08:01 · 17.8s
**Style:** direct address, warm grade
**Visual:** Wheat field in wind (animated still), golden light. Two lines of text appear, one per audience.
**Files:** A11_jazira_olive_wheat_landscape.jpg → MOTION M2, A11_jazira_olive_wheat_landscape.jpg
**Source line:** —
**Narration:**
```
ئەمە بۆ تۆ چی دەگەیەنێت؟ ئەگەر گەنجێکی کوردیت، ناسنامەکەت نە کۆتە بۆت نە تۆمەتە دژت. ئەگەر سوورییەکیت لە پاشخانێکی ترەوە، دانپێدانان بە زمانی دراوسێکەت هیچ لە وڵاتەکەت کەم ناکاتەوە؛ بەڵکو بۆ هەمووان فراوانتری دەکات.
```
**On-screen text:**
```
ناسنامەکەت تۆمەت نییە
دانپێدانان بە دراوسێکەت لە تۆ کەم ناکاتەوە
```

### S31 · 6 Stakes · 00:08:19 · 15.3s
**Style:** equation card
**Visual:** Clean equation on paper: 'particular identities kept + shared interests built'. Puzzle pieces lock together.
**Files:** G06_equation_card (Claude Code)
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
ئەنجامی توێژینەوەکە ڕوونە: گەنجانی کورد وەرگری ناسنامەیەکی ئامادە نین، بەڵکو بەرهەمهێنەرین. فاکتەری یەکلاکەرەوە دروشم نییە، بەڵکو چوارچێوەیەکی نیشتمانییە کە تایبەتمەندییەکان بپارێزێت، و لە هەمان کاتدا بەرژەوەندیی هاوبەش بنیات بنێت.
```
**On-screen text:**
```
تایبەتمەندیی پارێزراو + بەرژەوەندیی هاوبەش
```

### S32 · 7 Closing · 00:08:34 · 15.8s
**Style:** callback: 1962 → now, text behind person
**Visual:** Callback to S02: '1962' fades; the rooftop person (M1 shot) is pushed in slowly (still no face). Final line in giant type BEHIND the person. Music swells, then silence for 1 s.
**Files:** A01_rooftop_from_behind.jpg → MOTION M1, A16_bridge_at_dusk.jpg
**Source line:** —
**Narration:**
```
لە ساڵی ١٩٦٢، بە دەیان هەزار کەس گوترا: ئێوە بوونتان نییە. دوای زیاتر لە شەست ساڵ، نەوەکانیان بە ئارامی، بە زمانی خۆیان و بە ناوی خۆیان وەڵام دەدەنەوە: ئێمە لێرەین.
```
**On-screen text:**
```
ئێمە لێرەین.
```

### S33 · 7 Closing · 00:08:50 · 16.8s
**Style:** dark slide + end card
**Visual:** Black slide, question centred. Then end card: logo, channel name, subscribe/comment prompt. No sources slide.
**Files:** dwin_logo.png
**Source line:** —
**Narration:**
```
ئێستا پرسیارەکە تەنها بۆ ئەوان نییە، بۆ هەموومانە: چ نیشتمانێکمان دەوێت؟ نیشتمانێک کە داوات لێبکات بیر بچێتەوە کێیت… یان نیشتمانێک کە وەک خۆت جێگەت بکاتەوە؟ بە ئارامی بیروڕای خۆت لە کۆمێنتەکاندا بنووسە.
```
**On-screen text:**
```
چ نیشتمانێکمان دەوێت؟
```

## 6. YouTube post
**Title:** پێوەبەستبوونی گەنجانی کورد لە سووریا: لە «بوونت نییە» بۆ «ئێمە لێرەین»

**Description:** گەنجانی کورد لە سووریا دوای شۆڕش، ڕووخانی ڕژێم و فەرمانی ١٣ چۆن خۆیان دەناسێنن؟ ڕوونکردنەوەیەکی ئارام و هاوسەنگ: لە سەرژمێریی ١٩٦٢ەوە تا ناڕەزایی قوتابخانەکان لە ئەیلوولی ٢٠٢٦، و سێ سیناریۆی داهاتوو.

Sources:
- Shvan Ibrahim — study on belonging among Kurdish youth in Syria during the revolution (5 Oct 2026) — main source
- Al Jazeera English — Syria's al-Sharaa issues decree recognising Kurdish rights (17 Jan 2026)
- Arab News PK — background on the 1962 census, statelessness and the Arab Belt (Jan 2026)
- Amnesty International — Kurds in the Syrian Arab Republic one year after the March 2004 events (2005)
- UNHCR figures on Decree 49 naturalisations (to mid-2013), as reported by Arab News PK
- Hawar News / Syria TV / SANA — Kurdish-language teaching and the September 2026 student protests
- Karl Mannheim — 'The Problem of Generations' (1928)

**Channel:** Dween - دوین
**Thumbnails:** see THUMBNAILS.md.

## 7. Fact notes
- Decree 13 announced 16 Jan 2026 by President Ahmad al-Sharaa (implementation from 29 Jan).
- Kurdish classes per week: the study says 3, SANA says 2 → shown as '2–3' with a 'sources differ' tag.
- 517,000 (Hasakah registry) includes descendants; not comparable 1:1 with the 120,000 stripped in 1962.
- Self-definitions (S16) are qualitative findings, not survey percentages — never invent percentages.