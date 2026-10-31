# Dwin Vox-style explainer: «The Kurdish narrative» — Arabic (RTL)

## 1. Role and goal
You are a senior motion designer and documentary editor. Build an approximately 10.9-minute Vox-style explainer in Arabic about the Kurdish narrative: how Kurds tell their story and how it is told about them. The target length is 9–12 minutes, with 12:00 as the hard maximum.
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
- Font: Aljazeera (fallback Noto Naskh Arabic). Shape text with a real engine (Playwright/Chromium or HarfBuzz).
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
- Voice: one calm, warm, mid-low native Arabic narrator (Modern Standard Arabic). If using ElevenLabs, v3 supports Arabic: deep documentary voice, stability ~55%, style low.
- Music (royalty-free, no vocals):
  - S01–S04: low drone and wind, with a single duduk/ney note.
  - S05–S13: light strings with a soft frame-drum pulse.
  - S14–S18: tense, sparse.
  - S19–S22: near silence, with piano only.
  - S23–S32: curious pulse, with a soft pause on each verdict stamp.
  - S33–S39: warm build; 1 s of silence before the last line of S38, then a gentle resolve.
  - Duck the music −18 dB under the voice.
- SFX (subtle): paper slide, stamp, quill scratch, typewriter tick, soft click on checklists, whoosh, distant wind on the mountain scenes.

## 5. Scene by scene (estimated total ≈ 10.9 min)
Re-time every scene to the real narration audio. If the final cut runs over 12:00, shorten the pauses first, then trim S10 and S22 (marked optional).

### S01 · 1 Hook · 0:00 · 13.3s
**Style:** cold open, dark slide, mountain parallax
**Visual:** Mist rolls over Zagros ridges (M1). The proverb writes itself in giant type, letter by letter. Wind + low drone.
**Files:** A01_zagros_mountains_mist.jpg → MOTION M1
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
«ليس للكرد أصدقاء إلا الجبال». جملة يرددها الكرد في أربع دول، وبعشرات اللهجات. لكن السؤال: هل هي حقيقة تاريخية… أم قصة اعتدنا أن نرويها لأنفسنا؟
```
**On-screen text:**
```
«ليس للكرد أصدقاء إلا الجبال»
```

### S02 · 1 Hook · 0:13 · 19.3s
**Style:** magazine big number + map flash
**Visual:** Counter rolls to 30–40 million. A paper map of the region splits into four coloured state outlines (no flags).
**Files:** G01_region_map (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026) (estimates)
**Narration:**
```
نحو 30 إلى 40 مليون إنسان، موزّعين بين تركيا وإيران والعراق وسوريا. يُوصفون كثيرًا بأنهم أكبر شعب في العالم بلا دولة. والأرقام تقديرية، لأن معظم هذه الدول لا تسأل عن العِرق في إحصاءاتها.
```
**On-screen text:**
```
≈ 30–40 مليون | 4 دول
```

### S03 · 1 Hook · 0:32 · 13.8s
**Style:** dark slide, question
**Visual:** Black. An old book opens; pages flutter (M2). The question appears centre screen.
**Files:** A02_old_book_pages_wind.jpg → MOTION M2
**Source line:** —
**Narration:**
```
لكن هذا الفيديو لا يسأل: من يملك الأرض؟ بل يسأل: من يملك الحكاية؟ لأن الشعب الذي لا يروي قصته بنفسه، سيرويها عنه الآخرون… كما يريدون هم.
```
**On-screen text:**
```
من يملك الحكاية؟
```

### S04 · 1 Hook · 0:46 · 5.3s
**Style:** TITLE CARD: text behind person
**Visual:** Giant title BEHIND a person seen from behind on a ridge at sunrise (segmentation). Chapter ticks 1–7 appear on the timeline bar.
**Files:** A03_person_on_ridge_sunrise.jpg
**Source line:** —
**Narration:**
```
السردية الكردية: كيف يروي الكرد قصتهم… وكيف تُروى عنهم.
```
**On-screen text:**
```
السردية الكردية
```

### S05 · 2 Context · 0:51 · 16.3s
**Style:** CHAPTER: Context + definition card
**Visual:** Chapter card. Dictionary-style card: 'Narrative (n.)'. Three nested boxes animate: narration ⊂ story ⊂ narrative. Tool label: 'Lawrence Freedman | strategist'.
**Files:** G02_narrative_boxes (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
أولًا، ما السردية؟ ليست مجرد سرد للأحداث، بل الإطار الذي يختار به شعبٌ ما يتذكّره، وكيف يفسّر حاضره، وإلى أين يتّجه. هي معركة على المعنى، قبل أن تكون معركة على الأرض.
```
**On-screen text:**
```
السردية = معركة على المعنى
```

### S06 · 2 Context · 1:08 · 16.3s
**Style:** manuscript cut-outs + timeline
**Visual:** Real manuscript page of Sharafnama (cut-out, white border). Timeline bar ticks: 10th–12th c. emirates. Dots on map: Diyarbakır (Marwanids), Ganja (Shaddadids), Dinawar (Hasanwayhids).
**Files:** R01_sharafnama_manuscript.jpg, G01_region_map (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
والكرد ليسوا طارئين على التاريخ. ذكرهم المسعودي وابن الأثير وياقوت الحموي، وكتب شرفخان البدليسي تاريخ إماراتهم في «شرفنامه» عام 1597. وقامت لهم إمارات، كالمروانية في ديار بكر، والشدادية، والحسنوية.
```
**On-screen text:**
```
«شرفنامه» 1597 | إمارات كردية
```

### S07 · 2 Context · 1:24 · 16.8s
**Style:** hero cut-out, text behind statue
**Visual:** Real photo of the Saladin statue (Damascus or Erbil) cut out; '1187' behind it. Map arrow to Hattin and Jerusalem.
**Files:** R02_saladin_statue.jpg, R03_jerusalem_old_city.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
وذروة هذا الحضور كانت مع صلاح الدين الأيوبي، ابن تكريت ذو الأصل الكردي، الذي أسّس الدولة الأيوبية، وانتصر في حطّين عام 1187، وحرّر القدس. ولم يقدّم نفسه زعيمًا قوميًا، بل قائدًا للمسلمين.
```
**On-screen text:**
```
1187 | حطّين والقدس
```

### S08 · 2 Context · 1:41 · 15.8s
**Style:** painting cut-out + map split
**Visual:** Real Safavid-era mural of Chaldiran (public domain) as a cut-out. Map: a line splits the Kurdish areas; emirate names pop up: Botan, Baban, Soran, Ardalan.
**Files:** R04_chaldiran_mural.jpg, G01_region_map (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
عام 1514، في معركة چالدران، انحاز معظم أمراء الكرد إلى العثمانيين بتأثير العالم إدريس البدليسي. فنالوا حكمًا شبه ذاتي دام نحو ثلاثة قرون، ازدهرت فيه إمارات بوتان وبابان وسوران وأردلان.
```
**On-screen text:**
```
1514 | چالدران ← 3 قرون من الحكم الذاتي
```

### S09 · 2 Context · 1:56 · 15.8s
**Style:** quote card on parchment
**Visual:** Parchment quote card with a quill drawing the line. Real manuscript page of Mem û Zîn as background (blurred). Tool label: 'Ahmad Khani | poet, 1651–1707'.
**Files:** R05_mem_u_zin_manuscript.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
وفي ظل تلك الإمارات كتب أحمد خاني ملحمته «مم و زين» عام 1692. وفي مقدّمتها تساءل بحسرة: لو كان لنا سلطان… لكان حظّنا من الزمان أعلى من غيرنا.
```
**On-screen text:**
```
«لو كان لنا سلطان…» — أحمد خاني
```

### S10 · 2 Context · 2:12 · 17.8s · OPTIONAL CUT
**Style:** timeline + portrait cut-outs
**Visual:** Timeline ticks 1839 → 1847 → 1880. Ink stamp 'centralisation' falls on the emirate names. Real portrait of Bedirxan Beg if available (public domain).
**Files:** R06_bedirxan_beg_portrait.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
لكن إصلاحات القرن التاسع عشر أنهت تلك الإمارات، وفرضت حكم المركز المباشر. ثار أمراء وشيوخ، كبدرخان بك عام 1847، والشيخ عبيد الله النهري عام 1880. ومن هنا بدأ وعيٌ كرديٌّ جديد يتشكّل.
```
**On-screen text:**
```
1847 · 1880 | نهاية الإمارات
```

### S11 · 2 Context · 2:30 · 15.3s
**Style:** real document + ink highlight
**Visual:** Real scan of the Treaty of Sèvres text (Wikimedia). Articles 62–64 highlighted with a saffron marker, then the page greys out with the stamp 'never applied'.
**Files:** R07_treaty_of_sevres_page.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
ثم انهارت الدولة العثمانية. وفي عام 1920، نصّت معاهدة سيفر، في موادها من 62 إلى 64، على حكم ذاتي للكرد، وإمكانية الاستقلال لاحقًا. لكنها لم تُطبَّق قط.
```
**On-screen text:**
```
1920 | سيفر: وعدٌ لم يُطبَّق
```

### S12 · 2 Context · 2:45 · 21.8s
**Style:** archival photo + split-screen parallel
**Visual:** Real photo of the Lausanne Conference delegates (1922–23). Then split screen: 'Lausanne' in Kurdish memory | 'Sykes–Picot' in Arab memory — same scissors icon cutting a map.
**Files:** R08_lausanne_conference_1923.jpg, G01_region_map (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
وبعد ثلاث سنوات، حلّت محلّها معاهدة لوزان عام 1923. لم تذكر الكرد، ورسمت حدودًا وزّعتهم بين أربع دول. في الذاكرة الكردية صار هذا «الجرح المؤسِّس»: تقسيمٌ فُرض من فوق، دون أن يُسأل أهل المنطقة… تمامًا كما تتذكّر الذاكرة العربية سايكس–بيكو.
```
**On-screen text:**
```
1923 | لوزان = «الجرح المؤسِّس»
```

### S13 · 2 Context · 3:07 · 24.3s
**Style:** 4-panel magazine grid
**Visual:** Four cards flip one by one (order mirrors for RTL): Turkey · Iran · Iraq · Syria, each with population estimate and one keyword. Real city photos as card backgrounds: Diyarbakır walls, Sanandaj, Erbil Citadel, Qamishli.
**Files:** R09_diyarbakir_walls.jpg, R10_sanandaj_city.jpg, R11_erbil_citadel.jpg, R12_qamishli_street.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026) (estimates)
**Narration:**
```
ومنذ ذلك الحين، عاش الكرد أربع تجارب مختلفة: في تركيا إنكارٌ طويل ثم مسار سلام، وفي إيران مساحة ثقافية مع تضييق سياسي، وفي العراق إقليم فيدرالي معترف به دستوريًا منذ 2005، وفي سوريا إحصاء 1962 ثم الإدارة الذاتية، ثم مرحلة جديدة بعد 2024.
```
**On-screen text:**
```
تركيا 15–20 م · إيران 8–12 م · العراق 6–7 م · سوريا 2–3 م
```

### S14 · 3 Core problem · 3:31 · 14.3s
**Style:** CHAPTER: Core problem + shattered mirror
**Visual:** Chapter card. One word 'Kurdish narrative' cracks into four shards, each showing a label: classic nationalist · revolutionary left · liberal-reformist · Islamic.
**Files:** A04_cracked_mirror.jpg, G03_four_currents (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
وهنا المشكلة الحقيقية: لا توجد سردية كردية واحدة. هناك عائلة من السرديات تتداخل وتتنافس: قومية تقليدية، ويسارية ثورية، وليبرالية إصلاحية، وإسلامية. كلٌّ منها يروي «الكردي» بطريقة مختلفة.
```
**On-screen text:**
```
ليست سردية واحدة… بل سرديات
```

### S15 · 3 Core problem · 3:46 · 14.3s
**Style:** Venn: what unites / what divides
**Visual:** Left column 'unites' (language, Nowruz, shared memory) glows warm; right column 'divides' (the goal: state? autonomy? 'democratic nation'?) in cool grey. Real Nowruz fire photo behind the left column.
**Files:** R13_nowruz_fire_akre.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
وما يجمعها قليلٌ لكنه عميق: اللغة، ونوروز، وذاكرة الألم المشتركة. أما ما يفرّقها فكبير: هل الهدف دولة؟ أم حكم ذاتي؟ أم «أمّة ديمقراطية» بلا دولة؟ لا إجماع.
```
**On-screen text:**
```
يجمعها: اللغة · نوروز · الذاكرة
يفرّقها: الهدف
```

### S16 · 3 Core problem · 4:00 · 10.3s
**Style:** dialect tree diagram
**Visual:** Animated tree: Kurdish → Kurmanji · Sorani · Zazaki · Gorani · Southern. Two speech bubbles fail to meet, then a bridge word in Arabic/Turkish connects them.
**Files:** G04_dialect_tree (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
حتى اللغة نفسها موزّعة بين لهجات، أبرزها الكرمانجية والسورانية. وقد يحتاج كرديان أحيانًا إلى العربية أو التركية ليتفاهما مباشرة.
```
**On-screen text:**
```
كرمانجية · سورانية · زازاكية · گورانية · جنوبية
```

### S17 · 3 Core problem · 4:10 · 14.3s
**Style:** string board / connections
**Visual:** Detective-style string board: three party pins connect with red threads to three capitals (Ankara · Tehran · Washington). Threads tangle; a label: 'each alliance → a different story'. No party logos or flags.
**Files:** G05_alliance_board (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
والأخطر: التحالفات الخارجية. طرفٌ يستند إلى أنقرة، وآخر إلى طهران، وثالث إلى واشنطن. وكل تحالف يلوّن الحكاية بلون مختلف، ثم يتحوّل لاحقًا إلى تهمة في يد الخصوم.
```
**On-screen text:**
```
أنقرة · طهران · واشنطن ← حكايات متناقضة
```

### S18 · 3 Core problem · 4:25 · 11.8s
**Style:** dark slide, kinetic type
**Visual:** Black slide. Line 1 types in; line 2 lands with a soft boom.
**Files:** — (graphics only)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
لماذا يهمّ هذا؟ لأن القضية التي لا تملك سرديتها، تذوب حتى لو امتلكت كل مقوّمات البقاء. ولأن من يكتب الحكاية… يرسم المستقبل.
```
**On-screen text:**
```
من يكتب الحكاية… يرسم المستقبل
```

### S19 · 4 Evidence · 4:36 · 18.8s
**Style:** CHAPTER: Evidence + range chart
**Visual:** Chapter card. Range bar drawn to scale: 50,000 ——— 182,000, labelled 'estimates differ by source'. Real photo: Anfal memorial / Amna Suraka, Sulaymaniyah.
**Files:** R14_amna_suraka_museum.jpg, G06_anfal_range_chart (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026); Human Rights Watch, Genocide in Iraq (1993)
**Narration:**
```
لننظر إلى الأدلة. أولًا، الذاكرة. حملة الأنفال في العراق بين 1986 و1989، قُتل فيها ما بين 50 ألفًا و182 ألف إنسان، بحسب المصدر. وفي 2007، صنّفتها المحكمة الجنائية العراقية العليا إبادةً جماعية.
```
**On-screen text:**
```
الأنفال 1986–1989 | 50–182 ألف ضحية
```

### S20 · 4 Evidence · 4:55 · 21.3s
**Style:** memorial photo + quote tag
**Visual:** Real photo of the Halabja Monument. Then a map pin on Dersim with a quote tag (Erdoğan, 2011). Respectful, slow, no graphic images.
**Files:** R15_halabja_monument.jpg, R16_dersim_landscape.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
وفي 16 آذار 1988، قُصفت حلبجة بالسلاح الكيميائي، فقُتل نحو 5 آلاف إنسان. وفي ديرسم بتركيا، بين 1937 و1938، قُتل الآلاف، ووصفها أردوغان عام 2011 بأنها «من أكثر الحوادث مأساوية في تاريخنا المعاصر».
```
**On-screen text:**
```
حلبجة 1988 ≈ 5,000 | ديرسم 1937–38
```

### S21 · 4 Evidence · 5:17 · 15.3s
**Style:** archival photo + countdown
**Visual:** Real archival photo of Mahabad 1946 (public domain). A calendar counter runs 11 months, then the image fades to sepia. Tool label: 'outside protection → 11 months'.
**Files:** R17_mahabad_republic_1946.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
وفي إيران، قامت جمهورية مهاباد عام 1946 بقيادة قاضي محمد، تحت حماية سوفييتية. عاشت 11 شهرًا فقط، ثم انهارت حين انسحب السوفييت، وأُعدم قاضي محمد.
```
**On-screen text:**
```
مهاباد 1946 | حماية خارجية ← 11 شهرًا
```

### S22 · 4 Evidence · 5:32 · 9.8s · OPTIONAL CUT
**Style:** timeline with broken links
**Visual:** Timeline: 1975 → chain link snaps. Map arrow Iran→Iraq disappears. Tool label: 'Algiers Agreement, 1975'.
**Files:** G07_broken_chain (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
والقصة تكرّرت. ففي 1975، وبعد اتفاقية الجزائر بين العراق وإيران، سُحب الدعم عن ثورة الملا مصطفى البارزاني، فانهارت.
```
**On-screen text:**
```
1975 | اتفاقية الجزائر ← انهيار الثورة
```

### S23 · 4 Evidence · 5:42 · 17.3s
**Style:** pattern timeline + quote card
**Visual:** Horizontal timeline of five dots: 1975 · 1991 · 2003 · 2014 · 2019. Dots turn from green to grey. Quote card: «a tactical partner, not a strategic ally». Real footage of convoys leaving NE Syria, Oct 2019 (news, credited).
**Files:** R18_us_withdrawal_2019.mp4
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
أما الولايات المتحدة، فتقول الدراسة إنها تعاملت مع الكرد «شريكًا تكتيكيًا» لا «حليفًا استراتيجيًا»: دعمٌ في 1991، وتحالفٌ في الحرب على داعش، ثم انسحابٌ في 2019 وصفه كثير من الكرد بالخذلان.
```
**On-screen text:**
```
«شريك تكتيكي… لا حليف استراتيجي»
```

### S24 · 4 Evidence · 5:59 · 20.3s
**Style:** magazine portrait wall
**Visual:** Magazine spread: tall cut-out cards with names and one-line labels (no faces for medieval scholars — use manuscript/calligraphy cards; real photo only for Said Nursi). Big pull-quote in saffron.
**Files:** R19_said_nursi_portrait.jpg, A05_islamic_manuscript_library.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
وفي المقابل، هناك دليلٌ من نوع آخر: الكرد لم يكونوا على هامش الحضارة الإسلامية، بل في مركزها. ابن الصلاح الشهرزوري في علوم الحديث، وأبو الفداء الأيوبي في التاريخ والجغرافيا، والشيخ خالد النقشبندي، وبديع الزمان سعيد النورسي في القرن العشرين.
```
**On-screen text:**
```
«لسنا طارئين على هذا الفضاء الحضاري… نحن من بُناته»
```

### S25 · 4 Evidence · 6:19 · 16.3s
**Style:** archival + text behind subject
**Visual:** Real archival photo of Sheikh Said and companions, 1925 (public domain), cut-out. Words 'Naqshbandi · Qadiri' behind the figures. Then a calm photo of a Sufi tekke courtyard (real).
**Files:** R20_sheikh_said_1925.jpg, R21_tekke_courtyard.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
بل إن ثورات كبرى، كثورة الشيخ عبيد الله النهري، وثورة الشيخ سعيد بيران عام 1925، قادها شيوخ من الطريقة النقشبندية. الدين لم يكن خصمًا للهوية الكردية، بل كان جزءًا من نسيجها.
```
**On-screen text:**
```
الدين: جزءٌ من النسيج… لا خصم
```

### S26 · 4 Evidence · 6:36 · 24.8s
**Style:** aerial + mosaic of communities
**Visual:** Real aerial/drone footage of Erbil Citadel. Mosaic tiles light up: Kurds · Arabs · Turkmen · Christians. Then a second row: Sunni · Feyli Shia · Alevi · Yazidi · Kakai · Christian.
**Files:** R22_erbil_citadel_aerial.mp4, R11_erbil_citadel.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
ومن الأدلة أيضًا: إقليم كردستان العراق، الذي يعمل بمؤسساته منذ أكثر من 20 عامًا داخل دولة فيدرالية، وأربيل التي يعيش فيها الكرد والعرب والتركمان والمسيحيون. والمجتمع الكردي نفسه متنوّع: سنّة، وشيعة فيليون، وعلويون، وإيزيديون، وكاكائيون، ومسيحيون. تنوّعٌ هو ثراء… واختبار لأي سردية تريد أن تجمع الناس.
```
**On-screen text:**
```
شراكة ممكنة · تنوّع = ثراء + اختبار
```

### S27 · 5 Counterarguments · 7:00 · 24.8s
**Style:** CHAPTER: Counter-narratives + verdict stamp ◐
**Visual:** Chapter card. Claim on a torn paper strip; verdict stamp lands ◐ 'partly'. Bar: 92.73% 'yes' → isolation icons (closed airspace, borders). Same verdict template for S27–S32.
**Files:** R23_referendum_2017.jpg, G08_verdict_cards (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
والآن، السرديات المضادة. أولها: «القضية الكردية مشروع انفصالي يهدّد وحدة الدول». هل تصمد؟ جزئيًا فقط. نعم، في استفتاء 2017 صوّت نحو 93 في المئة بـ«نعم»، لكنه عُزل إقليميًا ودوليًا ولم يُطبَّق. وفي المقابل، أثبتت تجربة الإقليم أن الحكم الذاتي داخل الدولة لم يُفكّك العراق.
```
**On-screen text:**
```
«انفصالية»؟ ◐ جزئيًا
```

### S28 · 5 Counterarguments · 7:25 · 21.3s
**Style:** verdict ◐ + split
**Visual:** Verdict ◐. Split card: left 'the generalisation falls' (grey ✗), right 'the lesson stays' (saffron ✓) with mini-timeline Mahabad 1946 · Algiers 1975 · 2019.
**Files:** G08_verdict_cards (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
الثانية: «الكرد أداةٌ بيد قوى خارجية». وهنا الحقيقة مزدوجة. التعميم يسقط: فتهمة العمالة كثيرًا ما استُخدمت لتبرير القمع، وكل دول المنطقة تتحالف مع الخارج. لكن الدرس يبقى: الرهان على البعيد كلّف الكرد مرارًا، من مهاباد إلى الجزائر إلى 2019.
```
**On-screen text:**
```
«أداة بيد الخارج»؟ ◐ التعميم يسقط… والدرس يبقى
```

### S29 · 5 Counterarguments · 7:46 · 21.3s
**Style:** verdict ✗ + calligraphy
**Visual:** Verdict ✗ on 'contradiction'. Then the Qur'anic verse (49:13) in elegant Arabic calligraphy on paper, gold ink, with the translation line underneath in ckb/kmr. Calm nasheed-free ambient.
**Files:** A06_calligraphy_desk.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026); Qur'an 49:13
**Narration:**
```
الثالثة: «الكرد مسلمون قبل أن يكونوا كردًا، والقومية استيراد غربي يفتّت الأمة». يرد علماء كرد، ومنهم النورسي، بأن التنوّع آية من آيات الله: «وجعلناكم شعوبًا وقبائل لتعارفوا». الاعتراف بالهوية لا يناقض الإسلام… ما يناقضه هو العصبية والظلم، من أي طرف كان.
```
**On-screen text:**
```
«وجعلناكم شعوبًا وقبائل لتعارفوا»
```

### S30 · 5 Counterarguments · 8:08 · 13.3s
**Style:** verdict ✗
**Visual:** Verdict ✗. A stereotype label 'tribal' peels off a photo of a modern Erbil/Sulaymaniyah university campus (real).
**Files:** R24_university_campus_kurdistan.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
الرابعة: «الكرد عنفٌ وقبائلية». وتستشهد بالاقتتال بين الحزبين الكرديين الرئيسيين في التسعينيات. لكن كل المجتمعات عرفت صراعات داخلية، واختزال شعبٍ كامل في القبيلة تنميطٌ مرفوض.
```
**On-screen text:**
```
«عنف وقبائلية»؟ ✗ تنميط
```

### S31 · 5 Counterarguments · 8:21 · 17.3s
**Style:** verdict ◐
**Visual:** Verdict ◐. A puzzle with missing pieces; label: 'divisions = partly the result of partition and repression'. Switzerland example as a small tool label.
**Files:** G08_verdict_cards (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
الخامسة: «الكرد منقسمون، فلا مقوّمات لهم». هذه تصمد جزئيًا كتشخيص: الانقسام حقيقي. لكنها تسقط كحكمٍ نهائي، فالتنوّع لا يمنع بناء كيان متماسك، والانقسامات في جزء كبير منها نتاج التقسيم والقمع، لا طبيعة الشعب.
```
**On-screen text:**
```
«بلا مقوّمات»؟ ◐ تشخيص صحيح… حكم خاطئ
```

### S32 · 5 Counterarguments · 8:38 · 24.8s
**Style:** verdict ✗ + news footage
**Visual:** Verdict ✗ on 'only arms bring rights'. Counter: 40,000+. Then real news footage of the July 2025 weapons-burning ceremony near Sulaymaniyah (credited, no logos).
**Files:** R25_pkk_weapons_ceremony_2025.mp4
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026); Reuters / AP, May–July 2025
**Narration:**
```
وهناك سردية من الداخل أيضًا: أن الحقوق لا تُنال إلا بالسلاح. لكن التاريخ القريب يقول شيئًا آخر. الصراع المسلّح في تركيا كلّف أكثر من 40 ألف قتيل بحسب الأرقام الرسمية، وفي 2025 أعلن حزب العمال الكردستاني حلّ نفسه، وبدأ مسارٌ جديد ما زال يتشكّل.
```
**On-screen text:**
```
+40,000 قتيل ← 2025: إعلان الحل
```

### S33 · 6 Stakes · 9:03 · 21.8s
**Style:** CHAPTER: Stakes + real footage
**Visual:** Chapter card. Real footage: Damascus Dec 2024, then the Jan 2026 signing / decree coverage. Lower-third with dates. Timeline bar reaches 'now'.
**Files:** R26_damascus_dec2024.mp4, R27_syria_jan2026_agreement.mp4
**Source line:** Al Jazeera English, 17 & 30 Jan 2026
**Narration:**
```
وماذا عن اليوم؟ في سوريا، وبعد سقوط النظام في كانون الأول 2024، صدر في كانون الثاني 2026 المرسوم 13 الذي اعترف بالكردية لغةً وطنية، واتُّفق على دمج قوات سوريا الديمقراطية في مؤسسات الدولة. الطريق ما زال في أوّله.
```
**On-screen text:**
```
سوريا 2026 | المرسوم 13 + اتفاق الدمج
```

### S34 · 6 Stakes · 9:25 · 17.3s
**Style:** two doors, dark slide
**Visual:** Two doors on a dark slide: left door cold blue 'enmity', right door warm 'partnership'. The camera pushes toward the warm door (M3).
**Files:** A07_two_doors_corridor.jpg → MOTION M3
**Source line:** —
**Narration:**
```
ماذا يعني هذا لنا؟ يعني أن المنطقة تدخل مرحلة يُعاد فيها رسم الحكايات. والسؤال لم يعد فقط: ماذا يريد الكرد؟ بل: أيّ حكاية يروونها عن أنفسهم وعن جيرانهم؟ حكاية عداء… أم حكاية شراكة؟
```
**On-screen text:**
```
حكاية عداء… أم حكاية شراكة؟
```

### S35 · 6 Stakes · 9:42 · 16.3s
**Style:** 4 scenario cards
**Visual:** Four cards slide in like a magazine contents page: 1 status quo · 2 gradual wider recognition · 3 escalation (red, everyone loses) · 4 regional repositioning. Card 2 stays highlighted.
**Files:** G09_scenario_cards (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
الدراسة ترسم أربعة سيناريوهات: استمرار الوضع القائم، أو اعترافٌ تدريجي أوسع، أو تصعيدٌ يخسر فيه الجميع، أو تحوّلٌ إقليمي كبير يفتح صيغة جديدة. وأيّها يتحقق يتوقف جزئيًا على الحكاية التي نختارها.
```
**On-screen text:**
```
1 الوضع القائم · 2 اعتراف أوسع · 3 تصعيد · 4 تحوّل إقليمي
```

### S36 · 6 Stakes · 9:59 · 18.3s
**Style:** animated checklist over landscape
**Visual:** Checklist ticks over a wide shot of a shared market/bazaar (real, Erbil or Diyarbakır). Last line lands bigger, in saffron.
**Files:** R28_bazaar_erbil_or_diyarbakir.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
وتوصي الدراسة بسرديةٍ تتجاوز الحزبية، وتُدين العنف ضد المدنيين من أي طرف، وتحاور العرب والترك والفرس بوصفهم جيرانًا وشركاء لا أعداء، وتستند إلى رصيد الكرد في الحضارة الإسلامية. سرديةٌ يكتبها أبناء المنطقة… لا حسابات البعيدين.
```
**On-screen text:**
```
✓ فوق الحزبية ✓ ضد العنف ✓ جيران لا أعداء ✓ رصيد حضاري
يكتبها أبناء المنطقة
```

### S37 · 7 Closing · 10:17 · 9.3s
**Style:** CHAPTER: Closing — callback to S01
**Visual:** Chapter card. Callback: the same mountains as S01 (M1), now at golden hour. Text fades in quietly.
**Files:** A01_zagros_mountains_mist.jpg → MOTION M1
**Source line:** —
**Narration:**
```
ربما كانت الجبال صديقة الكرد الوحيدة يومًا ما. لكن الجبال لا تكتب الحكايات… الناس هم من يكتبونها.
```
**On-screen text:**
```
الجبال لا تكتب الحكايات
```

### S38 · 7 Closing · 10:26 · 14.3s
**Style:** text behind people, warm grade
**Visual:** Silhouettes of a group of young people walking together at dusk toward a town (A08). Final line in giant type behind them. 1 s silence before the last two words.
**Files:** A08_group_walking_dusk.jpg → MOTION M4
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
وتنتهي الدراسة بأملٍ بسيط: أن يكون للكرد أصدقاء من البشر، لا من الجبال وحدها. والأقرب إلى ذلك ليسوا البعيدين… بل الجيران الذين يتشاركون معهم الأرض والتاريخ والإيمان.
```
**On-screen text:**
```
أصدقاء من البشر… لا من الجبال وحدها
```

### S39 · 7 Closing · 10:40 · 14.3s
**Style:** dark slide + teaser end card
**Visual:** Black slide, the question. Then end card: logo, channel name, 'Next: belongings' teaser tag, subscribe/comment prompt. No sources slide.
**Files:** dwin_logo.png
**Source line:** —
**Narration:**
```
فأيّ حكاية سنرويها لأبنائنا؟ في الحلقات القادمة، سنتحدّث أكثر عن هذه الانتماءات: الكردي، والإسلامي، والإقليمي… وكيف يمكن أن تجتمع في رؤية واحدة. شاركنا رأيك بهدوء في التعليقات.
```
**On-screen text:**
```
أيّ حكاية سنرويها لأبنائنا؟
قريبًا: الانتماءات
```

## 6. After the video is finished: thumbnails (required)
When the Arabic video is final, ALSO create its YouTube thumbnails in both formats, following THUMBNAILS.md:
- `thumbnails/thumb_ar_16x9.png` (1280×720, <2 MB)
- `thumbnails/thumb_ar_9x16.png` (1080×1920, Shorts/Reels cover)
Use the brand font, the logo top-left, and text in this language only. Render them with Playwright and check them at phone size (160 px wide).

## 7. Publishing texts
Ready in `social/youtube_ar.md` and `social/facebook_instagram_ar.md`. After the final edit, update the chapter timestamps there to the real times; the first chapter must stay at 0:00.

## 8. Fact notes
- Population figures are estimates (no ethnic census in most states); always show them as ranges.
- Anfal deaths: 50,000–182,000 depending on the source; Iraqi High Tribunal genocide ruling 2007.
- Mulla Jami is listed as Kurdish in the study, but he was Persian, so he was removed. Ibn al-Athir is cited as a historian who wrote about Kurds, not as a Kurd.
- The study ends before the 2025 PKK dissolution announcement and the Jan 2026 Syria agreements; both were added from news sources.
- The Ahmad Khani line in S09 is a paraphrase from the study's Arabic rendering, not a verse translation.