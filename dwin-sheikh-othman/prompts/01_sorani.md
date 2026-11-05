# Dwin documentary explainer: Mulla Othman Abdulaziz — Kurdish Sorani (RTL)

## 1. Role and goal
You are a senior documentary editor and motion designer. Build an approximately 14-minute Vox-style documentary explainer in Kurdish Sorani on the life of the Kurdish scholar and leader Mulla Othman Abdulaziz al-Halabji (1922–1999), founder of the Islamic Movement in Iraqi Kurdistan. The target is 12–14 minutes, with 14:00 as the hard maximum.
Tone: dignified, calm and reverent toward the scholar, but professional and fair. Facts and criticisms are presented honestly; there is no sectarian, partisan or nationalist edge, and no hostility toward any party or people.
Editorial line (implicit, never stated): the film is made by people who value faith, knowledge and moral example. Let the viewer feel this through the choice of moments (teaching, night prayer, asceticism, peacemaking, gentle da'wah) and the respectful pacing. Do not add slogans or lines that state it outright.
This is a single, standalone documentary; there is no 'next episode' teaser.

## 2. Editorial rules
- Use narration and on-screen text EXACTLY as written. Do not translate, shorten or edit them.
- Numbers are written as digits; the narrator reads them as words.
- Photo-driven documentary: use the real photos of the sheikh and the other people (assets/people/) as much as possible. Cut-outs, slow Ken Burns moves, archival grain and name labels. Use AI images only for places and moods.
- Never create AI images of the sheikh or any real person, and never fake documents (the Brotherhood letter, the 1994 MoU, election papers). If a real photo of a person is missing, use a name card (calligraphic name + years) instead of a face.
- AI images get a small 'illustration' tag. Every fact shows a small source line from the scene's `Source` field (bottom corner, 24 px, 60% opacity).
- Halabja 1988: the memorial only, never images of victims. No party flags, party logos or armed footage. Ansar al-Islam is named in text only, never shown.
- No sources slide at the end. Sources go in the YouTube description only.

## 3. Technical spec
- Master 1920×1080, 24 fps, H.264 high, AAC 48 kHz, −14 LUFS integrated, true peak −1 dB.
- Second export 1080×1920 (9:16): reframe every scene. Faces stay in the upper-middle; captions sit in the lower third, above Instagram's caption area. Keep logo and text clear of the right-side like/comment buttons (safe zone: 150 px top, 320 px bottom, 140 px right).
- Shield logo TOP-LEFT on every scene (fixed brand rule; never mirrored), 90 px high, 40 px margin, 85% opacity.
- Font: Speda (fallback Noto Naskh Arabic). Shape text with Playwright/Chromium or HarfBuzz.
- Direction RTL: mirror every layout. The timeline bar runs right→left; reveals, wipes, two-panel order and chart axes start from the right.
- Palette: paper #EFE8DC, ink #1B1B1B, dark slide #10161A, gold #C9A24A (accent), deep green #2F5D50, muted red #9E4A3C (only for the verdict ✗).
- Look: paper grain (8%), cut-outs with a 6 px cream border and soft shadow, 2.5D parallax on portraits, ink-drawn underlines, and sepia plus film grain on photos before 1991.
- Persistent timeline bar (bottom, 6 px): 1922 → 1999, with the playhead year label visible during S05–S15 and S31.
- Captions: burned in, 2 lines max, 46 px, cream on a 70% black box, word-level highlight in gold. Also export the .srt from `subtitles/`.
- Quote cards: dark background, large gold quotation marks, quote text in the brand font, attribution as a small label. Quotes from the sheikh appear on screen exactly as in the 'On-screen text' block.
- Transitions: paper-slide push (default); hard cut to a dark slide for chapter cards (S05, S16, S19, S27, S31, S33); a soft cross-dissolve on the emotional beats (S15, S24, S34); and the opening quote (S02) returns as a callback in S35.
- Text behind person (S04, S22, S32, S34): segment the subject with rembg or MediaPipe. Layer order: background → giant title → person matte → captions.
- Name / tool labels: a rounded tag, 28 px, with name + role (for example 'Amjad al-Zahawi | scholar, Baghdad'), sliding in from the right.
- Moving stills: build M1–M4 as described in MOTION.md; every other still gets a Ken Burns move (1.00→1.05).

## 4. Voice, music and SFX
- Voice: one calm, warm, mature male Sorani narrator, documentary pace. A human narrator is recommended, because ElevenLabs does not officially support Kurdish.
- Music (royalty-free, instrumental only, no vocals):
  - S01–S04: ney/duduk over a soft drone.
  - S05–S15: gentle strings and oud with a soft frame drum; near silence at S15.
  - S16–S18: sparse, thoughtful.
  - S19–S26: warm, steady pulse.
  - S27–S30: low and neutral, with a short pause after each verdict.
  - S31–S35: warm build, with 1 s of silence before the last sentence of S34.
  - Duck the music −18 dB under the voice; no music hits on Qur'an or prayer imagery.
- SFX (subtle): paper slide, page turn, key click (S07), stamp (verdicts), camera flashes (S22), train ambience (S25), wind on the mountain scenes.

## 5. Scene by scene (estimated total ≈ 13.7 min)
Re-time every scene to the real narration. If the final cut runs over 14:00, shorten the pauses first.

### S01 · 1 Hook · 0:00 · 19.0s
**Style:** cold open, dark slide, slow push-in
**Visual:** Mud-and-wood house wall beside a small mosque at dusk (A01, M1). Kinetic quote builds word by word. Soft wind, a single ney note.
**Files:** A01_mud_house_by_mosque.jpg → MOTION M1, P01a_sheikh_portrait.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
پیاوێک بزووتنەوەیەکی دامەزراند، لەگەڵ پاشاکان دانیشت، و سەرۆک وەزیرانی تورکیا دەستی گرت و بردییە سەر مینبەر… بەڵام ماڵەکەی لە هەڵەبجە لە قوڕ و دار بوو، و هەرگیز نۆژەنی نەکردەوە. سوێندی دەخوارد: بەخوا تا ئەمڕۆ یەک پارچە دۆلارم لە ماڵەکەمدا نەبینیوە.
```
**On-screen text:**
```
«تا ئەمڕۆ یەک پارچە دۆلارم لە ماڵەکەمدا نەبینیوە»
```

### S02 · 1 Hook · 0:19 · 19.4s
**Style:** real funeral footage + quote
**Visual:** Real footage/photos of the 1999 funeral procession; rose petals (A12) drift over the frame. Lower-third: 'Kurdistan Region — 3 days of mourning'.
**Files:** R01_funeral_1999.mp4, A12_rose_petals_street.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
کاتێک لە ساڵی 1999 لە دیمەشق کۆچی دوایی کرد، تەرمەکەی لە شارێکەوە بۆ شارێکی تر دەگوازرایەوە و خەڵک گوڵیان بەسەردا دەڕشت، و هەرێمی کوردستان سێ ڕۆژ ماتەمینی ڕاگەیاند. لەگەڵ ئەوەشدا نزیکترین کەسەکانی گوتیان: قەدری مامۆستامان نەزانی تا لەدەستمان دا.
```
**On-screen text:**
```
«قەدری مامۆستامان نەزانی تا لەدەستمان دا»
```

### S03 · 1 Hook · 0:38 · 11.3s
**Style:** dark slide, question
**Visual:** Black slide. The question types in. A faint archival photo of the sheikh fades behind it at 20%.
**Files:** P01b_sheikh_teaching.jpg
**Source line:** —
**Narration:**
```
کەواتە مامۆستا مەلا عوسمان عەبدولعەزیز کێ بوو؟ و چۆن زانایەکی حوجرەی گوندێکی بچووک بوو بە دامەزرێنەری یەکەم بزووتنەوەی ئیسلامیی ڕێکخراو لە کوردستانی عێراق؟
```
**On-screen text:**
```
مامۆستا مەلا عوسمان عەبدولعەزیز کێ بوو؟
```

### S04 · 1 Hook · 0:50 · 4.0s
**Style:** TITLE CARD: text behind person
**Visual:** Giant name placed BEHIND the sheikh's real portrait (segmentation matte of P01a). Years 1922–1999 under it. Slow parallax, low boom.
**Files:** P01a_sheikh_portrait.jpg
**Source line:** —
**Narration:**
```
مامۆستا مەلا عوسمان عەبدولعەزیزی هەڵەبجەیی… ژیاننامەیەکی گشتگیر.
```
**On-screen text:**
```
مامۆستا مەلا عوسمان عەبدولعەزیز
1922 – 1999
```

### S05 · 2 Context · 0:54 · 18.5s
**Style:** CHAPTER: Context + map
**Visual:** Chapter card. Paper map zooms to Halabja; pin on Prîsî Serû village. Real village/Hawraman landscape photo as a cut-out.
**Files:** R02_halabja_pris_village.jpg, G01_map_halabja (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
لە ساڵی 1922 لە گوندی پریسی سەروو، نزیک هەڵەبجە، لە ماڵێکی زانستیدا لەدایک بوو. باوکی، مەلا عەبدولعەزیز، مامۆستای مزگەوتی گوندەکە بوو و حوجرەیەکی هەبوو کە فەقێکانی تێدا بە شێوازی کلاسیکی کوردی دەیانخوێند. هەموو شتێک لەوێوە دەستی پێکرد.
```
**On-screen text:**
```
1922 | پریسی سەروو — هەڵەبجە
```

### S06 · 2 Context · 1:12 · 10.8s
**Style:** explainer card + tool label
**Visual:** Hujra interior (A02, M2) with an oil lamp and stacked books. Tool label slides in: 'Hujra = the Kurdish mosque school'. Small icons: grammar · logic · fiqh · usul → ijaza.
**Files:** A02_hujra_interior_lamp.jpg → MOTION M2, A03_students_books_from_behind.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
حوجرە بۆ چەندین سەدە قوتابخانەی مزگەوتی کوردی بووە: فەقێ لە نێوان گوند و زانایاندا دەگەڕێت، کتێب لە دوای کتێب، تا ئیجازە وەردەگرێت.
```
**On-screen text:**
```
حوجرە = قوتابخانەی مزگەوتی کوردی
```

### S07 · 2 Context · 1:23 · 27.6s
**Style:** quote card, warm archival
**Visual:** Close-up of an old iron key on a wooden shelf (A04). Quote card in saffron. Portrait cut-out of Mulla Salih al-Kabir if provided (P03).
**Files:** A04_old_key_on_books.jpg, P03_mulla_salih_kabir.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
لای باوکی خوێندی، پاشان لای ئامۆزاکەی مەلا ساڵحی گەورە، و هەموو خوێندنەکەی لە ناو کوردستاندا بوو. کاتێک تەندروستیی باوکی لاواز بوو، ویستی دوای هەفتەیەک تاقیی بکاتەوە، بەڵام کوڕەکە داوای کرد هەر ئێستا تاقی بکرێتەوە. لە قورسترین شوێنەکاندا پرسیاری لێکرد و وەڵامی دایەوە، باوکی ناوچەوانی ماچ کرد و کلیلی حوجرەکەی دایە دەستی و گوتی: لە ئەمڕۆوە تۆ لە جێگەی منیت.
```
**On-screen text:**
```
«لە ئەمڕۆوە تۆ لە جێگەی منیت»
```

### S08 · 2 Context · 1:51 · 26.3s
**Style:** story beat + book stack graphic
**Visual:** A stack of classical book spines grows (graphic, titles as labels: Jam' al-Jawami', al-Mutawwal, Sharh al-Mawaqif…). Then a wheat mill (A05). Cut-out of Sheikh Muhammad al-Khal (P04) with tool label.
**Files:** A05_wheat_mill.jpg, P04_sheikh_muhammad_khal.jpg, G02_book_stack (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
دوای کۆچی باوکی، خێزانەکەی لە ئاشێکی گەنم بەخێو دەکرد، بۆیە چوو بۆ سلێمانی بۆ تاقیکردنەوەیەکی فەرمی کە مووچەی پێدەدرا. بە ڕیشێکی گەنج و مێزەرێکی کوردییەوە چووە لای شێخ محەممەدی خاڵ، و داوای کرد لە کتێبەکانی کۆتایی تاقی بکرێتەوە نەک سەرەتا. لیژنەی زانایان لە هەموو زانستێک پرسیاریان لێکرد، تا یەکێکیان گوتی: ئەمە فەقێ نییە… لە ئێمە زاناترە.
```
**On-screen text:**
```
«ئەمە فەقێ نییە… لە ئێمە زاناترە»
```

### S09 · 2 Context · 2:17 · 18.1s
**Style:** big number + calligraphy
**Visual:** Counter rolls to 57. Then a Qur'an on a wooden stand (A06), soft window light. Real photo of the sheikh teaching (P01b) as a cut-out.
**Files:** A06_quran_on_stand.jpg, P01b_sheikh_teaching.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
پاشان پەنجا و حەوت ساڵی بێ وەستان وانەی گوتەوە. هەموو قورئانی لەبەر بوو، و دەیگوت: لە تەمەنمدا جگە لە جوزئی عەمما بۆ تاقیکردنەوەیەک هیچم لەبەر نەکرد، بەڵام ئەوانی تر لە خزمەتی قورئاندا ژیام تا هەمووی لەگەڵمدا لەبەر بوو.
```
**On-screen text:**
```
57 ساڵ وانەگوتنەوە
```

### S10 · 2 Context · 2:35 · 18.1s
**Style:** timeline + portrait cut-outs
**Visual:** Timeline bar jumps to 1954. Cut-outs of Amjad al-Zahawi (P05) and Mohammed Mahmoud al-Sawwaf (P06) slide in from Baghdad on the map; arrow to Halabja. Tool labels with names.
**Files:** P05_amjad_zahawi.jpg, P06_muhammad_sawwaf.jpg, G01_map_halabja (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
لە ساڵی 1954، زانا ئەمجەد زەهاوی و شێخ محەممەد مەحمود سەوواف لە بەغداوە سەردانی هەڵەبجەیان کرد. لە کۆبوونەوەیەکدا لەگەڵ زانایانی شارەکە، سەرپەرشتیی بانگەواز لە کوردستان درا بە مەلا ساڵح و مەلا عوسمان. لێرەوە کاری بانگەوازیی ڕێکخراو دەستی پێکرد.
```
**On-screen text:**
```
1954 | سەرەتای بانگەوازی ڕێکخراو
```

### S11 · 2 Context · 2:53 · 15.3s
**Style:** dark slide + map arrow south
**Visual:** Dark slide 'The first ordeal'. Map arrow Halabja → Nasiriyah (south). A barred window shadow (A07) crosses the frame.
**Files:** A07_prison_window_shadow.jpg, G01_map_halabja (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
دوای کودەتای 1958، زانایانی کوردستان بەرەنگاری هەڵمەتی شیوعییە دەسەڵاتدارەکان دژی دروشمەکانی ئیسلام بوونەوە، بۆیە مەلا ساڵح و مەلا عوسمان زیندانی کران و چەند مانگێک بۆ ناسرییە دوورخرانەوە. ئەوە یەکەم تاقیکردنەوەی سەخت بوو.
```
**On-screen text:**
```
1959 | یەکەم تاقیکردنەوە: دوورخستنەوە بۆ ناسرییە
```

### S12 · 2 Context · 3:08 · 19.9s
**Style:** two-panel magazine spread
**Visual:** Left panel 1970: cut-out of Mulla Mustafa Barzani (P07) + label 'Union of Religious Scholars'. Right panel 1974: cut-out of King Faisal (P08) + label 'Kurdish delegation to Saudi Arabia'. Panels mirror for RTL.
**Files:** P07_mulla_mustafa_barzani.jpg, P08_king_faisal.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
دوای ڕێککەوتنی ئۆتۆنۆمی لە 1970، مەلا مستەفا بارزانی ڕەزامەندیی دا لەسەر پڕۆژەکەی «یەکێتیی زانایانی ئایینی ئیسلامی لە کوردستان»، و مامۆستا بوو بە ئەندامی سەرکردایەتی و بەرپرسی سلێمانی. لە 1974 سەرۆکایەتیی شاندێکی کوردی کرد بۆ سعودیە و لەگەڵ پاشا فەیسەڵ کۆبووەوە.
```
**On-screen text:**
```
1970 | یەکێتیی زانایان · 1974 | دیدار لەگەڵ پاشا فەیسەڵ
```

### S13 · 2 Context · 3:28 · 25.8s
**Style:** dark slide, three stacked labels
**Visual:** Dark slide 'The second ordeal'. Three labels stack one by one: prison · hunger strike · the first pages of the tafsir. Desert road to Samawah (A08). Handwritten-page texture (A09) at the end.
**Files:** A08_desert_road_samawah.jpg, A09_handwritten_pages_lamp.jpg, P09_mulla_ali_abdulaziz.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
لە 1976، لەگەڵ خێزانەکەی زیاتر لە ساڵێک زیندانی کرا، پاشان بۆ سەماوە دوورخرانەوە. لە زینداندا لەگەڵ زیندانیانی کورد و عەرەب مانی لە خواردن گرت، و ڕێگەی دەدا بەوانەی برسێتی شەکەتی کردبوون ڕۆژووەکەیان بشکێنن. کۆتاییەکەی ڕێککەوتن بوو، و بەپێی گێڕانەوەکان یەکەم مانگرتنی سەرکەوتوو بوو لە زیندانەکانی عێراق. هەر لەوێشدا دەستی کرد بە تەفسیری قورئان بە کوردی.
```
**On-screen text:**
```
1976 | زیندان · مانگرتن · سەرەتای تەفسیر
```

### S14 · 2 Context · 3:54 · 27.2s
**Style:** map migration arrows + real photo
**Visual:** Map: arrows from Halabja to the Iranian border, then a pin on Sanandaj. Silhouettes crossing a mountain pass (A10, M3). The founding name appears as a large magazine headline.
**Files:** A10_mountain_pass_migration.jpg → MOTION M3, R03_sanandaj_city.jpg, G01_map_halabja (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
لە 1987، حکومەت هەڵمەتێکی کردە سەر هەڵەبجە و دەوروبەری. مامۆستا حەزی دەکرد لە ناوخۆ بمێنێتەوە، و تەنها کاتێک کۆچی کرد کە هیچ ڕێگەیەکی تر نەمابوو. لەگەڵ زانایانی هەڵەبجە و خەڵکەکە بەرەو سنووری ئێران ڕۆیشت، و لە شاری سنە ڕێککەوتن لەسەر یەکخستنی گرووپە ئیسلامییە کوردییەکان لە یەک ڕێکخراودا کرا: «بزووتنەوەی ئیسلامی لە کوردستانی عێراق»، و مەلا عوسمان ڕابەری بوو.
```
**On-screen text:**
```
1987 | دامەزراندنی بزووتنەوەی ئیسلامی لە کوردستانی عێراق
```

### S15 · 2 Context · 4:21 · 17.6s
**Style:** memorial, near silence
**Visual:** Real photo of the Halabja Monument (R04), slow push-in. Music drops to near silence. Date and number appear softly, no graphic images.
**Files:** R04_halabja_monument.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
چەند مانگێک دواتر، لە 16ی ئازاری 1988، ڕژێم هەڵەبجەی بە چەکی کیمیایی بۆردومان کرد و نزیکەی پێنج هەزار هاووڵاتیی مەدەنی گیانیان لەدەستدا. شاری مامۆستا و خەڵک و فەقێکانی. کارەساتەکە بوو بە بەشێک لە یادەوەری و گوتاری بزووتنەوەکە.
```
**On-screen text:**
```
16ی ئازاری 1988 | هەڵەبجە ≈ 5,000 مەدەنی
```

### S16 · 3 Core problem · 4:39 · 11.3s
**Style:** CHAPTER: Core problem + split screen
**Visual:** Chapter card. Split screen: left the quiet hujra (A02), right a mountain front at dusk (A11). A thin line joins them with the sheikh's cut-out (P01a) in the middle.
**Files:** A02_hujra_interior_lamp.jpg, A11_mountain_front_dusk.jpg, P01a_sheikh_portrait.jpg
**Source line:** —
**Narration:**
```
لێرەدا پرسیارە ڕاستەقینەکە دەست پێدەکات: چۆن پیاوێک ئارامیی حوجرە و سەختیی بەرە پێکەوە کۆدەکاتەوە؟ فیقه و سیاسەت؟ پێوەبەستبوونی ئیسلامی و تایبەتمەندیی گەلە کوردەکەی؟
```
**On-screen text:**
```
حوجرە و بەرە · ئیسلام و کوردایەتی
```

### S17 · 3 Core problem · 4:50 · 12.2s
**Style:** Venn diagram, ink drawn
**Visual:** Two pairs of circles draw themselves: tradition + revival, Islamic + Kurdish. The overlaps glow saffron; the words 'respect' and 'dispute' appear on either side.
**Files:** G03_venn_movement (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
بزووتنەوەکەی، نەریتی سوننیی کوردی و بەئاگاهاتنەوەی نوێ، و ڕەهەندی ئیسلامی و کوردیی کۆکردەوە. هەر ئەم کۆکردنەوەیەش وای کرد هەم جێگەی ڕێز بێت… هەم جێگەی ناکۆکی.
```
**On-screen text:**
```
کلاسیک + بەئاگاهاتنەوە · ئیسلامی + کوردی
```

### S18 · 3 Core problem · 5:02 · 19.9s
**Style:** dark slide, kinetic type
**Visual:** Black slide. A branching tree diagram briefly shows one trunk splitting into branches; then the question lands.
**Files:** G04_legacy_tree (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
بۆچی ئەمڕۆ گرنگە؟ چونکە میراتەکەی دوای کۆچی دوایی بەسەر چەند ڕێکخراوێکدا دابەش بوو، کە لە نزیکی لە ڕێبازەکەیەوە جیاوازن. و چونکە ئەو پرسیارەی ژیانی پێوە بەسەر برد هێشتا لە ئارادایە: چۆن زانا لە سیاسەتدا نموونە دەبێت بێ ئەوەی ڕۆحی خۆی لەدەست بدات؟
```
**On-screen text:**
```
زانا چۆن لە سیاسەتدا زانا دەمێنێتەوە؟
```

### S19 · 4 Evidence · 5:22 · 36.3s
**Style:** CHAPTER: Evidence + uprising and truce
**Visual:** Chapter card. Real photos of the 1991 uprising (R09) as cut-outs. Paper map of the front: a gold 'pause' icon appears over it during the negotiations, then lifts; small pins mark the garrisons taken. Last beat: real 1992 election photo if provided (R05). No numbers, percentages or charts on screen.
**Files:** R09_uprising_1991.jpg, R05_election_1992.jpg, G01_map_halabja (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
با سەیری ڕووداوەکان بکەین. لە ڕاپەڕینی 1991دا بزووتنەوەکە و ڕێکخستنەکانی و جەماوەرەکەی ڕۆڵێکی کاریگەریان هەبوو. پاشان بەرەی کوردستانی چووە ناو دانوستان لەگەڵ حکومەتی عێراق، بزووتنەوەکە بەشداری تێدا نەکرد، بەڵام مامۆستا فەرمانی بە هێزەکانی دا هەموو کردەوەکانیان دژی حکومەت ڕابگرن تا دانوستانەکان کۆتایی دێن. کاتێک کۆتایی هات، چالاکییەکانی دەست پێکردەوە و دەستی بەسەر چەند سەربازگە و بارەگایەکی حکومیدا گرت. لە 1992یش «لیستی ئیسلامی» لە یەکەم هەڵبژاردنی هەرێمدا بەشداری کرد، و مامۆستا بۆ سەرکردایەتیی بزووتنەوەی ڕزگاریخوازی کورد خۆی کاندید کرد.
```
**On-screen text:**
```
1991 | ڕاپەڕین · ئاگربەست بە درێژایی دانوستان
```

### S20 · 4 Evidence · 5:59 · 17.6s
**Style:** quote card on dark
**Visual:** Dark quote card, large quotation marks, the line highlighted word by word. Background: a quiet street in Halabja (real, R06) at 30%.
**Files:** R06_halabja_street.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
پاشان ساڵانی شەڕی ناوخۆی کورد هات. بە هەوادارانی دەگوت: «دەخیلتانم، پێنج سەد دەخیل، شەڕ هەڵمەگیرسێنن، ئەگەر کوڕێکی کورد بکوژرێت ئەوە موسوڵمانە». کاتێک لە 1994 پێکدادان ڕوویدا، دەیگوت: ڕازی نیم خوێنی کورد بە دەستی کورد بڕژێت.
```
**On-screen text:**
```
«ئەگەر کوڕێکی کورد بکوژرێت… ئەوە موسوڵمانە»
```

### S21 · 4 Evidence · 6:16 · 22.2s
**Style:** two portraits + handshake graphic
**Visual:** Counter: 500+. Then two real cut-outs side by side: the sheikh (P01c) and Jalal Talabani (P11); a crescent icon marks 'first day of Ramadan'; a signed-paper icon. Cut-out of Masoud Barzani (P12) as the host, with a tool label.
**Files:** P01c_sheikh_older.jpg, P11_jalal_talabani.jpg, P12_masoud_barzani.jpg, D04_mou_1994.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
ژمارەی کوژراوانی نێوان بزووتنەوەکە و یەکێتیی نیشتمانیی کوردستان گەیشتە زیاتر لە پێنج سەد. مامۆستا هەوڵی نێوەندگیریی دا و جەلال تاڵەبانی پێشوازیی کرد، و شاندی نێوەندگیر نزیکەی مانگێک میوانی مەسعود بارزانی بوو. لە یەکەم ڕۆژی ڕەمەزاندا، مامۆستا عوسمان و جەلال تاڵەبانی یاداشتی تێگەیشتنیان واژۆ کرد و ئاشتی کرا.
```
**On-screen text:**
```
+500 کوژراو ← یەکەم ڕۆژی ڕەمەزان: ئاشتی
```

### S22 · 4 Evidence · 6:38 · 30.8s
**Style:** real photos + text behind person
**Visual:** Real photo of the sheikh with Necmettin Erbakan (P13) or at the 1996 conference. '50+' in giant type behind them. Then the Turkish parliament building (R07) with camera-flash SFX. Last beat: cut-out of Yusuf al-Qaradawi (P14) with a warm quote tag.
**Files:** P13_erbakan_with_sheikh.jpg, R07_turkish_parliament.jpg, P14_yusuf_qaradawi.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
ئامادەبوونی لە جیهانی ئیسلامیدا فراوان بوو. لە 1996، لە کۆنگرەی «فاتیحین» لە تورکیا، بە ئامادەبوونی نوێنەری زیاتر لە پەنجا وڵات و ڕێکخراو، سەرۆک وەزیران نەجمەدین ئەربەکان خۆی دەستی دەگرت و دەیبردە سەر مینبەر. کاتێک بە جلوبەرگی ئایینیی کوردییەوە بردییە ناو پەرلەمانی تورکیا، فەرمانبەران پەنجەرەکانیان کردەوە تا وێنەی بگرن. لە ئیماراتیش، شێخ یوسف قەرەزاوی بە پەلە بەرەو ڕووی ڕۆیشت و گوتی: «مامۆستامان، پێش ئەوەی بتبینین خۆشمان ویستی».
```
**On-screen text:**
```
1996 | ئەربەکان · کۆنگرەی فاتیحین · +50 وڵات
```

### S22b · 4 Evidence · 7:09 · 37.6s
**Style:** two-panel spread + real group photo with name labels
**Visual:** First beat: a soft paper map with two thin lines, Kurdistan and Palestine, labelled 'دوو گەلی بێ دەوڵەت'. A calligraphic name card 'سەلاحەدینی ئەیووبی' (no face). Then the real 1989 photo (P16) with a slow Ken Burns; name tags slide in from the right in the order of the original caption. Do not mirror this photo. No flags, logos or armed imagery.
**Files:** P16_ahmad_jibril_meeting_1989.jpg (= IMG_2999.jpeg)
**Name labels (in the photo, from right to left):** 1 کاک محەممەد، کوڕی مەلا عەلی · 2 مەلا عەلی عەبدولعەزیز · 3 ئەحمەد جیبریل · 4 مامۆستا مەلا عوسمان عەبدولعەزیز
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
فەلەستین لە دڵیدا ئامادە بوو. کورد و فەلەستینییەکان دوو گەلی بێ دەوڵەتن، ماوەیەکی درێژ تامی داگیرکاری و دابەشکردنیان چەشتووە، و کورد وەک دۆزی برایەک سەیری دۆزەکەیان دەکرد. مامۆستا بە خاکی یەکەم قیبلە و میعراجی پێغەمبەر ﷺ دەیزانی، و بیری دەخستەوە کە ئازادکەری دووەمی، سەلاحەدینی ئەیووبی، کورد بووە. چەند مانگێک دوای ڕاگەیاندنی بزووتنەوەی حەماس، نوێنەرەکەی چاوی پێکەوت، و دیدارەکانی لەگەڵ بزووتنەوە فەلەستینییەکان دووبارە بوونەوە. لە 1989یش لەگەڵ ئەحمەد جیبریل، ئەمینداری گشتیی بەرەی میللی بۆ ئازادکردنی فەلەستین – سەرکردایەتیی گشتی، کۆبووەوە.
```
**On-screen text:**
```
«دوو گەلی بێ دەوڵەت» · 1989 | دیدار لەگەڵ ئەحمەد جیبریل
```

### S23 · 4 Evidence · 7:47 · 17.6s
**Style:** story beat, intimate
**Visual:** A dim room lit by one bulb; a small generator in the corner (A13). The quote lands in two beats.
**Files:** A13_dim_room_generator.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
لە ماڵەوەش، جگە لە مووچەی ئەوقاف هیچ داهاتێکی نەبوو. کارەبا هەفتەی دوو ڕۆژ دەهات، یاوەرەکەی پێشنیاری کرد مۆلیدەیەکی بچووک بکڕێت. پرسی: دەتوانیت بۆ هەموو برایانی بارەگاکە بکڕیت؟ گوتی: نەخێر. گوتی: «بۆ هەمووان بکڕە… یان بۆ منیش مەیکڕە».
```
**On-screen text:**
```
«بۆ هەمووان بکڕە… یان بۆ منیش مەیکڕە»
```

### S24 · 4 Evidence · 8:04 · 21.7s
**Style:** quiet beat
**Visual:** Close-up of an old cloth-merchant's ledger and a few coins (A14). Then a real photo of the sheikh in old age (P01c), slow push-in.
**Files:** A14_merchant_ledger_coins.jpg, P01c_sheikh_older.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
ئەگەر مووچەکەی پێش کۆتایی مانگ تەواو ببوایە، دە دینار لە بازرگانێکی قوماش قەرز دەکرد، و کاتێک مووچەی نوێ دەهات یەکەم کاری دانەوەی قەرزەکە بوو. کاتێک کوڕەکەی زوبەیر شەهید بوو، و بزووتنەوەکە ویستی ئەوەی بە خێزانی شەهیدان دەدرێت بیدات بە خێزانەکەی، ڕەتی کردەوە و گوتی: پارەم ناوێت.
```
**On-screen text:**
```
«پارەم ناوێت»
```

### S25 · 4 Evidence · 8:26 · 20.3s
**Style:** night train
**Visual:** Night train interior: a folded prayer rug on a seat by the window, lights streaking outside (A15, M4). Label 'Ankara → Istanbul'.
**Files:** A15_night_train_prayer_rug.jpg → MOTION M4
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
لە گەنجییەوە نوێژی شەوی بەردەوام بوو، لە ماڵ و لە سەفەردا. یاوەرەکەی گوتی سێ مانگ لەگەڵیدا گەشتی کرد و یەک شەویشی لێ نەچوو. لە شەمەندەفەرێکدا لە نێوان ئەنقەرە و ئەستەنبوڵ، چاوەڕێی گەیشتن بە هوتێلەکەی نەکرد، هەستا دەستنوێژی گرت و لە شەمەندەفەرەکەدا نوێژی کرد.
```
**On-screen text:**
```
نوێژی شەو… تەنانەت لە شەمەندەفەردا
```

### S26 · 4 Evidence · 8:46 · 26.7s
**Style:** book stack + checklist
**Visual:** Real photo of the 10-volume Kurdish tafsir on a shelf (D01) and the Bukhari commentary (D02). Volumes count up 1→10. Earlier, a soft 'wall' graphic that does not crack.
**Files:** D01_tafsir_10_volumes.jpg, D02_bukhari_sharh.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
لەگەڵ ئەوانەی لە ئایین دوورکەوتبوونەوە نەرم و میهرەبان بوو. شوێنکەوتووانی تایەفەیەکی ناوچەیی کە باوەڕیان بە ئیسلام نەبوو هاتن، داوایان کرد مارەی منداڵەکانیان بە شەریعەت ببڕێت، گوتی: مارەیان بۆ دەبڕین، و دیواری شەرمی نێوانیان و ئیسلام مەشکێنن، چونکە ئەگەر شکا ناگەڕێتەوە. تەفسیرێکی قورئانی بە کوردی لە دە بەرگدا بەجێهێشت، و دوو بەرگ لە شەرحی سەحیحی بوخاری بە کوردی.
```
**On-screen text:**
```
تەفسیری کوردی: 10 بەرگ · شەرحی بوخاری: 2 بەرگ
```

### S27 · 5 Counterarguments · 9:13 · 33.1s
**Style:** CHAPTER: Criticisms + verdict stamp ✗
**Visual:** Chapter card. Criticism written on a torn paper strip; verdict stamp ✗ 'ijtihad, not defection'. A doorway (A16) where the sheikh 'stood' (no person shown). Same verdict template for all criticisms.
**Files:** A16_old_doorway_pawe.jpg, A17_old_envelope_intact.jpg, D03_mb_letter.jpg, G06_verdict_cards (Claude Code), P14_yusuf_qaradawi.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
ئێستا، ڕەخنەکان. یەکەمیان: «لە کۆمەڵی ئیخوان دەرچوو و ڕیزەکانی پەرتکرد». ڕووداوەکان دەڵێن جیابوونەوەکە دوو هۆکاری هەبوو: ڕەوتێکی نەتەوەیی عەرەبی لە ناو کۆمەڵەکەدا بەرز بووەوە، و باڵێکی ناوی بەرەنگاربوونەوەی ڕژێمی بەعسی ڕەتکردەوە. کاتێک داوایان لێکرد دەست لە سەرکردایەتیی بەرگری هەڵبگرێت، گوتی: ئەمە لای من ئەرکێکی شەرعییە، ئەم گەلە ستەمی زۆری لێکراوە و ناتوانم وازی لێبهێنم. گێڕانەوەی دڕاندنی نامەکەش نزیکەکانی ڕەتی دەکەنەوە و نامەکە پارێزراوە. قەرەزاوییش پێی گوت: هیچ ڕەخنەیەکمان لە ئیجتیهادەکەت نییە.
```
**On-screen text:**
```
«ڕیزی پەرتکرد»؟ ✗ ئیجتیهاد بوو نەک دەرچوون
```

### S28 · 5 Counterarguments · 9:46 · 27.6s
**Style:** verdict ◐ + map links
**Visual:** Verdict ◐ 'support yes, dependence no'. Map with thin lines from Halabja to Riyadh, Ankara, Tehran (no flags). Cut-out of Abdulqadir Tawhidi (P15) with tool label.
**Files:** G06_verdict_cards (Claude Code), P15_abdulqadir_tawhidi.jpg, G01_map_halabja (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
دووەم: «بزووتنەوەکە کارتێک بوو لە دەستی ئێران». لێرەدا بەشێکی ڕاستە: ڕژێمی سەددام دوژمنی هاوبەش بوو، و بزووتنەوەکە بەڕاستی سوودی لە پشتیوانیی ئێران وەرگرت. بەڵام بڕیار سەربەخۆ مایەوە: پەیوەندییەکانی لەگەڵ سعودیە بەردەوام بوو، لەگەڵ ئەربەکان و قەرەزاوی پەیوەندیی هەبوو، و لە فەقێکانی قوتابخانەی هەڵەبجە کەسانێک هەبوون کە خۆیان چەکیان دژی ڕژێمی ئێران هەڵگرت، وەک عەبدولقادر تەوحیدی لە 1984.
```
**On-screen text:**
```
«کارتی ئێران»؟ ◐ پشتیوانی بەڵێ… پاشکۆیەتی نەخێر
```

### S28b · 5 Counterarguments · 10:14 · 45.8s
**Style:** verdict ✗ + two evidence cards
**Visual:** Same verdict template. Card 1: calligraphic name card 'لەیس شوبەیلات | سیاسەتمەداری ئیسلامی، ئوردن' (no face) with the label 'تاران 1989'. Card 2: a map pin on Qush Tepe; two simple truck icons wait while a counter runs 0→36 hours, then turn back. Last beat: an empty archive drawer (A19), 'not one document'. Never show or fake a document.
**Files:** G06_verdict_cards (Claude Code), G01_map_halabja (Claude Code), A19_empty_archive_drawer.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
سێیەم: «بزووتنەوەکە پارە و چەکی لە حکومەتی عێراق وەرگرتووە». ڕووداوەکان شتێکی تر دەڵێن. لە 1989، لە تاران، چەند سەرکردەیەکی ئیسلامیی ئوردنی، لەوانە لەیس شوبەیلات، پێشنیاریان کرد لە نێوان ئەو و سەرکردایەتیی عێراقدا نێوەندگیری بکەن، بەڵام ڕەتی کردەوە. لە شەڕی ناوخۆشدا حکومەت دوو بارهەڵگری چەک و تەقەمەنی نارد بۆ سنووری قوشتەپە تا بزووتنەوەکە وەریانبگرێت، مامۆستا ڕەتی کردەوە، و دوای سی و شەش کاتژمێر چاوەڕوانی گەڕێنرانەوە. نزیکەکانی تەحەددا دەکەن کە یەک بەڵگەنامە دەربکەوێت کە بزووتنەوەکە لە سەردەمی ئەودا پارە یان چەکی لە حکومەت وەرگرتبێت، و هەر کەسێک بە نهێنی یان دوای کۆچی ئەو کاری وای کردبێت، بەرپرسیارێتییەکەی تەنها لە ئەستۆی خۆیەتی.
```
**On-screen text:**
```
«پشتیوانی لە بەغداوە»؟ ✗ یەک بەڵگەنامەش نییە
```

### S29 · 5 Counterarguments · 11:00 · 20.3s
**Style:** verdict ✗ + method card
**Visual:** Verdict ✗. The legacy tree's trunk only, labelled with the sheikh's method: 'نە تەکفیر · نە زیادەڕۆیی'. No group names, logos or footage on screen.
**Files:** G04_legacy_tree (Claude Code), G06_verdict_cards (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
چوارەم: «بزووتنەوەی چەکدار دەرگای بۆ توندڕەوی کردەوە». وەڵامەکە لە ڕێبازی مامۆستا خۆیدایە: لەسەر بیروباوەڕی زۆرینەی زانایان بوو، کەسی بە کافر نەدەزانی، سووکایەتیی بە ئایینی کەس نەدەکرد، و بەلای بەشداریکردن لە دامەزراوەکانی هەرێمدا دەچوو. چەند کۆمەڵێکی تریش لە بزووتنەوەکە دەرچوون، لەوانە «ئیسلاح» و «ئەنسارولئیسلام».
```
**On-screen text:**
```
«دەرگای توندڕەوی»؟ ✗ نە تەکفیر نە زیادەڕۆیی
```

### S30 · 5 Counterarguments · 11:20 · 19.4s
**Style:** verdict ◐
**Visual:** Verdict ◐ 'yes… and a peacemaker'. Callback to the peace scene: the signed-paper icon returns.
**Files:** G06_verdict_cards (Claude Code), D04_mou_1994.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
پێنجەم: «لایەنێک بوو لە شەڕی ناوخۆی کورد». ئەمە وەک ڕووداو ڕاستە: بزووتنەوەکە لایەن بوو، و زیاتر لە پێنج سەد کەس کوژران. بەڵام هەڵوێستی مامۆستا ڕوون بوو: هەستی دەکرد بەرپرسە لە هەر بریندارێک، و خۆی هەوڵی نێوەندگیریی دا تا ئاشتی واژۆ کرا.
```
**On-screen text:**
```
«لایەنی شەڕ»؟ ◐ بەڵێ… و دروستکەری ئاشتی
```

### S31 · 6 Stakes · 11:39 · 24.4s
**Style:** CHAPTER: Stakes + legacy tree
**Visual:** Chapter card. The legacy tree grows branches with labels (no logos): mother Islamic Movement · Islamic Unity Movement (1999) · Islamic Group → Justice Group (2001/2021). Real photo of his grave in Halabja (R08) at the root.
**Files:** R08_sheikh_grave_halabja.jpg, G04_legacy_tree (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
مامۆستا لە 12ی ئایاری 1999 لە دیمەشق کۆچی دوایی کرد و لە هەڵەبجە بەخاک سپێردرا. دوای ئەو، میراتەکەی لە چەند ڕێکخراوێکدا درێژەی کێشا: بزووتنەوەی ئیسلامیی دایک کە هێشتا کار دەکات، بزووتنەوەی یەکگرتنی ئیسلامی، و کۆمەڵی ئیسلامی کە بوو بە «کۆمەڵی دادگەری»، لەگەڵ ڕێڕەوی تر. هەموویان لە نزیکی لە ڕێبازەکەیەوە جیاوازن.
```
**On-screen text:**
```
12ی ئایاری 1999 | میراتێک بەسەر ڕێکخراوەکاندا دابەش بوو
```

### S31b · 6 Stakes · 12:04 · 26.3s
**Style:** map + three pillars, then a split
**Visual:** Paper map of the Kurdistan Region. Three equal pillars rise (دادوەری · جێبەجێکردن · یاسادانان) with smaller blocks joining around them. Then the map slowly cracks into two halves. No party colours, flags or logos.
**Files:** G07_shared_admin_map (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
ڕۆڵەکانی ئەم ئەزموونە پێیان وایە ئەو یازدە ساڵەی دوای ڕاپەڕین هەلێکی زێڕین بوو بۆ بەڕێوەبردنێکی هاوبەش: سێ هێزە سەرەکییەکە دەسەڵاتەکانی دادوەری، جێبەجێکردن و یاسادانان وەربگرن، و پێکهاتەکانی تریش بەپێی قەبارەی خۆیان بەشداری بکەن، تا ببێتە بناغەیەکی پتەو بۆ بەشداریکردن لە پرۆسەی سیاسیی عێراقدا. بەڵام ئەوەی ڕوویدا دابەشکردن بوو، کە دابەشبوونی ئەمڕۆی لێکەوتەوە… و هەمووان باجەکەیان دا.
```
**On-screen text:**
```
هەڵە مێژووییەکە: دابەشکردن لە جیاتی بەڕێوەبردنی هاوبەش
```

### S32 · 6 Stakes · 12:30 · 19.0s
**Style:** portrait + text behind person
**Visual:** Real portrait of the sheikh (P01a) with the line in giant type behind him. Warm grade.
**Files:** P01a_sheikh_portrait.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
ئەمە بۆ ئێمە چی دەگەیەنێت؟ واتە مامۆستا نموونەیەکی لە هەر ڕێکخراوێک گەورەتری بەجێهێشت: زانایەک کە کاتێک چووە ناو سیاسەت حوجرەی بەجێنەهێشت، پێوەبەستبوونی ئیسلامیی لەگەڵ تایبەتمەندیی گەلە کوردەکەی کۆکردەوە، و تەنانەت لای نەیارانیشی جێگەی ڕێز مایەوە، چونکە ئەوەی دەیگوتەوە خۆی دەیژیا.
```
**On-screen text:**
```
ئەوەی دەیگوتەوە خۆی دەیژیا
```

### S33 · 7 Closing · 12:49 · 21.7s
**Style:** CHAPTER: Closing + funeral callback
**Visual:** Chapter card. Callback to the opening: real funeral footage (R01), then a map where cities light up one by one: Halabja · Erbil · Pawe · Sanandaj · Marivan · Damascus · London.
**Files:** R01_funeral_1999.mp4, G01_map_halabja (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
ڕۆژی بەڕێکردنی تەرمەکەی، خەڵک لە شارێکەوە بۆ شارێکی تر ڕژانە سەر شەقامەکان، و مەجلیسی پرسە لە هەڵەبجە و هەولێر، لە پاوە و سنە و مەریوان، و لە دیمەشق و لەندەن ساز کرا. یەکێک لە ناسیاوانی گوتی: لە خزمەتیدا بووم، جگە لە قسەی خێر هیچم لێ نەبیست.
```
**On-screen text:**
```
«جگە لە قسەی خێر هیچم لێ نەبیست»
```

### S34 · 7 Closing · 13:11 · 14.0s
**Style:** text behind person, slow
**Visual:** Real portrait (P01b or P01c). The testimony in giant type behind him. 1 s of silence before the last sentence.
**Files:** P01b_sheikh_teaching.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
وەک پیاو ژیا… و وەک پیاو کۆچی کرد. و ئامۆژگاریی نزیکترین کەسی بۆ نەوەکان: ئەگەر زانایەکی چاکی لەخواترس لە ناوتاندا دەرکەوت، بە دەستێکی بەهێز بیگرن، و هەرگیز وازی لێمەهێنن.
```
**On-screen text:**
```
«بە دەستێکی بەهێز بیگرن»
```

### S35 · 7 Closing · 13:25 · 15.3s
**Style:** dawn + end card
**Visual:** Dawn over Hawraman / Halabja (A18, slow). Final question centred (callback to the opening quote). Then the Dwin end card (logo, channel name). No sources slide.
**Files:** A18_dawn_hawraman.jpg, dwin_logo.png
**Source line:** —
**Narration:**
```
ڕەحمەتی خودا لەسەر مامۆستا مەلا عوسمان عەبدولعەزیز. پرسیارەکە بۆ ئێمەیە: چەند زانایەکی چاک ئەمڕۆ لە ناوماندا هەیە… کە قەدری نازانین تا لەدەستی نەدەین؟ بە ئارامی بۆمان بنووسە: چی لە ژیانی فێربوویت؟
```
**On-screen text:**
```
چەند زانا لە ناوماندا هەیە قەدری نازانین؟
```

## 6. After the video is finished: thumbnails (required)
When the Kurdish Sorani video is final, ALSO create its YouTube thumbnails in both formats, following THUMBNAILS.md:
- `thumbnails/thumb_ckb_16x9.png` (1280×720, <2 MB)
- `thumbnails/thumb_ckb_9x16.png` (1080×1920, Shorts/Reels cover)

## 7. Publishing texts
Ready in `social/youtube_ckb.md` and `social/facebook_instagram_ckb.md`. After the final edit, update the chapter timestamps (the first must stay at 0:00).

## 8. Fact notes
- The ijaza year is disputed in the sources (1935 is inconsistent with a 1922 birth), so the video gives no year for it.
- The claim that he was removed from the leadership near the end of his life is unverified and left out. The oral story about Salahaddin Bahaaddin's subscriptions is also left out.
- 'First successful hunger strike in Iraqi prisons' is attributed ('according to the account').
- 1992 election: no vote counts, percentages or thresholds appear anywhere in the film, because the author regards the published results as unreliable (the election was marred by fraud). The film only says the Islamic List took part and the sheikh stood as a candidate.
- S29: Islah and Ansar al-Islam are named only, with no description or characterisation.
- S28b: the Tehran 1989 offer and the Qush Tepe trucks come from the movement's own account. A remark attributed to Tariq Aziz about the other side receiving support is left out, in line with the no-hostility rule.
- S22b: the Hamas and Ahmad Jibril meetings come from the movement's own account; the photo's name order follows the author's caption.
- S31b is presented as the view of the movement's people ('يرى أبناء هذه التجربة'), not as the narrator's verdict.