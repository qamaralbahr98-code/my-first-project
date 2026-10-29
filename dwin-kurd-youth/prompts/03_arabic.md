# Dwin Vox-style explainer — Arabic (RTL)

## 1. Role and goal
You are a senior motion designer and video editor. Build an 8.5-minute Vox-style explainer in Arabic on belonging among Kurdish youth in Syria during and after the revolution. Tone: professional, calm, balanced, NOT nationalist, NOT against any group. The video explains; it does not campaign.

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
- Font: Aljazeera (fallback Noto Naskh Arabic). Shape text with a real engine (Playwright/Chromium or HarfBuzz) — never draw Arabic-script glyphs one by one.
- Direction RTL: mirror all layouts; timeline bar runs right→left; text reveals and wipes move right→left; charts start from the right.
- Palette: paper #EFE8DC, ink #1B1B1B, dark slide #111418, accent saffron #E8A33D, muted red #B5483A, muted green #4F7C5A (accent use only, never as a flag).
- Look: paper grain overlay (8%), cut-out photos with 6 px white border and soft shadow, 2.5D parallax on photos, ink-drawn arrows/circles, film grain on archival scenes.
- Captions: burned-in, 2 lines max, 46 px, white on 70% black box, word-level highlight in saffron. Also export .srt from `subtitles/`.
- Transitions: paper-slide push (default), hard cut to dark slide for chapter cards, whip-pan whoosh between real footage, match cut S02→S32 (the '1962' callback).
- 'Text behind person' (S04, S32): segment the subject with rembg / MediaPipe Selfie Segmentation, layer: background → giant title → subject matte → captions.
- Tool / lower-third labels: rounded tag, 28 px, icon + text, slides in from the reading side.
- Chapter cards (dark slides) at S04, S11, S16, S23, S27: number + chapter name, 2.5 s, low boom hit.

## 4. Voice and music
- Voice: one calm, warm, mid-low native Arabic narrator (Modern Standard Arabic, Levantine-neutral). ElevenLabs v3 supports Arabic: a deep calm documentary voice, stability ~55%, style low.
- Music: royalty-free, no vocals. Act 1 (S01–S10): soft piano + low strings; Act 2 (S11–S22): light pulse, curious; Act 3 (S23–S29): sparse, thoughtful; S30–S33: warm build, 1 s silence before 'we are here', then soft resolve. Duck −18 dB under voice.
- SFX (subtle): paper slide, stamp, pencil scratch, typewriter tick, soft click on checklist, whoosh.

## 5. Scene by scene (total ≈ 8.5 min)

### S01 · 1 Hook · 00:00:00 · 16.3s
**Style:** dark slide + slow push-in
**Visual:** Young person seen from behind on a rooftop at dusk over a Jazira town. Kinetic caption builds word by word. Paper grain overlay.
**Files:** A01_rooftop_from_behind.jpg → MOTION M1
**Source line:** —
**Narration:**
```
تخيّل أن تولد في بلدك، وتكبر فيه، وتتكلّم لغته… ثم تكتشف أن الدولة لا تعترف بوجودك على الورق. هذه لم تكن قصة خيالية، بل حياة عشرات الآلاف من الكرد في سوريا.
```
**On-screen text:**
```
مولودٌ هنا… وغير موجود على الورق
```

### S02 · 1 Hook · 00:00:16 · 12.8s
**Style:** magazine big number + stamp sound
**Visual:** Giant year '1962' slams in, then the counter rolls to 120,000. Blank paper document (AI, labelled illustration) with a red ink circle drawn by hand.
**Files:** A02_blank_paper_document.jpg
**Source line:** Arab News PK, Jan 2026
**Narration:**
```
في عام ألف وتسعمئة واثنين وستين، أجرت السلطات إحصاءً استثنائيًا في محافظة الحسكة. وبنتيجته، جُرِّد أكثر من مئة وعشرين ألف كردي من الجنسية السورية.
```
**On-screen text:**
```
١٩٦٢ | أكثر من ١٢٠٬٠٠٠ كردي بلا جنسية
```

### S03 · 1 Hook · 00:00:29 · 17.3s
**Style:** dark slide, question in huge type
**Visual:** Cut to black. Question types in letter by letter with a soft typewriter tick. Faint crowd silhouettes behind.
**Files:** A13_crowd_silhouettes_dusk.jpg
**Source line:** —
**Narration:**
```
واليوم، جيلٌ وُلد بعد تلك السنوات بكثير، عاش الثورة والحرب والنزوح، يطرح سؤالًا بسيطًا وصعبًا في آن: إلى أين ننتمي؟ هذا الفيديو ليس عن الشعارات، بل عن جيلٍ يحاول أن يعرّف نفسه بهدوء.
```
**On-screen text:**
```
إلى أين ننتمي؟
```

### S04 · 1 Hook · 00:00:46 · 5.3s
**Style:** TITLE CARD: text behind person
**Visual:** Title in giant type placed BEHIND the person (segmentation matte of A08 or M1). Slow parallax. Logo stays top corner.
**Files:** A08_young_woman_from_behind_sunrise.jpg
**Source line:** —
**Narration:**
```
الانتماء لدى الشباب الكرد في سوريا… خلال الثورة وبعدها.
```
**On-screen text:**
```
الانتماء
الشباب الكرد في سوريا
```

### S05 · 2 Context · 00:00:51 · 14.8s
**Style:** animated map
**Visual:** Paper-texture map of Syria (Natural Earth). Dots light up: Hasakah, Qamishli, Kobani, Afrin, Aleppo, Damascus. City labels as lower-third tags.
**Files:** G01_map_syria_kurdish_areas (Claude Code), R10_kobani_city_view.jpg
**Source line:** Arab News PK, Jan 2026
**Narration:**
```
لنبدأ من الأساس. يعيش في سوريا نحو مليونين ونصف مليون كردي، يتركّز معظمهم في الشمال والشمال الشرقي: الحسكة والقامشلي وكوباني وعفرين، إلى جانب أحياء كبيرة في حلب ودمشق.
```
**On-screen text:**
```
≈ ٢٫٥ مليون كردي في سوريا
```

### S06 · 2 Context · 00:01:06 · 14.3s
**Style:** two cut-out cards, split screen
**Visual:** Two paper cards slide in from opposite sides: 'ajanib' and 'maktoumeen'. Icons: house, briefcase, plane, rings, baby — each crossed by an ink line.
**Files:** A12_family_album_hands.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
إحصاء ألف وتسعمئة واثنين وستين صنع فئتين: «الأجانب» الذين سُجّلوا بلا جنسية، و«المكتومين» الذين لم يُسجَّلوا أصلًا. بلا هوية، يصعب التملّك والتوظيف والسفر، وحتى تسجيل الزواج والأطفال.
```
**On-screen text:**
```
«أجانب» و«مكتومون»
```

### S07 · 2 Context · 00:01:20 · 17.8s
**Style:** map + timeline bar
**Visual:** Timeline bar at bottom jumps to 1973. On the map a thin strip along the northern border fills with hatched ink. A blank village road sign (AI) has its name smudged.
**Files:** G01_map_syria_kurdish_areas (Claude Code), A04_blank_village_sign_wheat.jpg
**Source line:** Arab News PK, Jan 2026
**Narration:**
```
وفي عام ألف وتسعمئة وثلاثة وسبعين، في عهد حافظ الأسد، نُفّذ مشروع «الحزام العربي»: نُقلت عائلات عربية إلى شريط على طول الحدود الشمالية، وتغيّرت أسماء قرى كردية. كانت سياسة دولة، لا خلافًا بين جيران.
```
**On-screen text:**
```
١٩٧٣ | «الحزام العربي»
```

### S08 · 2 Context · 00:01:38 · 12.8s
**Style:** warm archival look
**Visual:** Old radio glowing in a kitchen at night, hands of a parent turning the dial. Film grain, vignette. Caption fades in like handwriting.
**Files:** A03_old_radio_kitchen_night.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
أما اللغة، فبقيت لعقود خارج المدرسة والدوائر الرسمية. تعلّمها الأطفال في البيوت، ومن الأغاني والراديو. وهكذا صارت الكلمة الكردية نفسها شكلًا من أشكال الذاكرة.
```
**On-screen text:**
```
لغةٌ تُتعلَّم في البيت
```

### S09 · 2 Context · 00:01:51 · 18.8s
**Style:** timeline + counter
**Visual:** Timeline jumps to 2011. Counter rolls to ≈104,000. Then a suitcase at a bus station (AI) as the music darkens.
**Files:** A06_suitcase_bus_station.jpg
**Source line:** UNHCR (via Arab News PK)
**Narration:**
```
ثم جاء عام ألفين وأحد عشر. مع بداية الثورة، صدر المرسوم تسعة وأربعون، وتجنّس بموجبه نحو مئة وأربعة آلاف شخص حتى منتصف ألفين وثلاثة عشر. لكن الحرب التي تلت جلبت النزوح والهجرة، وغيّرت حياة جيل كامل.
```
**On-screen text:**
```
٢٠١١ | المرسوم ٤٩ ← ≈١٠٤٬٠٠٠ مُجنَّس
```

### S10 · 2 Context · 00:02:10 · 18.3s
**Style:** real footage + lower-third
**Visual:** Real footage: Damascus crowds Dec 2024, then the Decree 13 announcement. Lower-third label with date. Whoosh transition between the two.
**Files:** R07_damascus_dec2024_crowds.mp4, R03_decree13_announcement.mp4
**Source line:** Al Jazeera English, 17 Jan 2026
**Narration:**
```
في كانون الأول ألفين وأربعة وعشرين، سقط نظام الأسد. وفي السادس عشر من كانون الثاني ألفين وستة وعشرين، أعلن الرئيس أحمد الشرع المرسوم رقم ثلاثة عشر الخاص بحقوق الكرد. فجأة، صار السؤال القديم سؤالًا عمليًا.
```
**On-screen text:**
```
١٢/٢٠٢٤ ← ١٦/١/٢٠٢٦ | المرسوم ١٣
```

### S11 · 3 Core problem · 00:02:28 · 15.8s
**Style:** CHAPTER: dark slide + portrait cut-out
**Visual:** Chapter card 'The core problem'. Real public-domain portrait of Karl Mannheim as a paper cut-out with tool label 'Karl Mannheim | sociologist'.
**Files:** R09_karl_mannheim_portrait.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
عالم الاجتماع كارل مانهايم كان يقول إن الجيل لا يُعرَّف بالعمر فقط، بل بالأحداث الكبرى التي يعيشها معًا في سنّ التكوين. والشباب الكرد اليوم جيلٌ تشكّل في قلب الثورة والحرب.
```
**On-screen text:**
```
الجيل = تجربة مشتركة
```

### S12 · 3 Core problem · 00:02:44 · 13.8s
**Style:** triptych magazine layout
**Visual:** Three vertical panels reveal one by one: ruined street (AI), suitcase/map with lines Qamishli–Erbil–Berlin, phone glow. Icons and labels.
**Files:** A06_suitcase_bus_station.jpg, A05_phone_in_hands_music.jpg → MOTION M3
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
ثلاث قوى صاغت هذا الجيل: الحرب التي جعلت الأمان سؤالًا يوميًا، والهجرة التي فرّقت العائلات بين القامشلي وأربيل وبرلين، والفضاء الرقمي الذي صار ساحة جديدة للتعبير.
```
**On-screen text:**
```
الحرب · الهجرة · الفضاء الرقمي
```

### S13 · 3 Core problem · 00:02:58 · 15.8s
**Style:** UI mock + echo effect
**Visual:** Hands holding a phone (AI); generic, invented app UI (no real brand) with Kurdish song cards. Then the frame duplicates into echoing mirrored copies (echo chamber).
**Files:** A05_phone_in_hands_music.jpg, A05_phone_in_hands_music.jpg → MOTION M3
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
على الشاشات، عادت اللغة الكردية إلى الحياة: أغانٍ، وصفحات، ودروس، ونقاشات بين شباب لم يلتقوا قط. لكن الفضاء نفسه قد يتحوّل إلى غرف صدى، يسمع فيها كل طرف صوته فقط.
```
**On-screen text:**
```
مساحة للّغة… أو غرفة صدى؟
```

### S14 · 3 Core problem · 00:03:13 · 14.3s
**Style:** Venn diagram, ink drawn
**Visual:** Two circles draw themselves: 'Kurdish' and 'Syrian'. The overlap fills and reads 'Kurdish Syrian'. A key labelled 'equal citizenship' unlocks the overlap.
**Files:** G02_venn_identity (Claude Code)
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
وهنا جوهر المسألة: هل يجب أن يختار الشاب بين أن يكون كرديًا وأن يكون سوريًا؟ الدراسة تقول: لا. الهوية المزدوجة «كردي سوري» ممكنة… بشرط واحد: مواطنة متساوية.
```
**On-screen text:**
```
كردي سوري = ممكن ← بشرط المواطنة المتساوية
```

### S15 · 3 Core problem · 00:03:28 · 18.3s
**Style:** split-screen diverging paths
**Visual:** Split screen: left path dims and leads to a departing bus; right path brightens into a classroom. Arrows drawn in ink.
**Files:** A09_crossroads_paths.jpg, A07_empty_classroom.jpg
**Source line:** —
**Narration:**
```
لماذا يهمّ هذا؟ لأن الشاب الذي يشعر بالإقصاء ينسحب، أو يهاجر، أو ينغلق. أما الذي يشعر بأن له مكانًا، فيبني ويشارك. الانتماء ليس عاطفة فقط؛ إنه ما يحدّد إن كان جيلٌ كامل سيبقى أو سيرحل.
```
**On-screen text:**
```
إقصاء ← انسحاب | اعتراف ← مشاركة
```

### S16 · 4 Evidence · 00:03:46 · 14.8s
**Style:** CHAPTER: Evidence + qualitative scale
**Visual:** Chapter card 'Evidence'. Three stacked speech bubbles of decreasing size: 'Kurdish' (large), 'Kurdish Syrian' (medium), 'Syrian' (small). Footnote tag: 'qualitative study — not survey percentages'.
**Files:** G03_self_definition_bubbles (Claude Code)
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
كيف يعرّف هؤلاء الشباب أنفسهم؟ بحسب الدراسة، يقول معظمهم ببساطة: «أنا كردي». بعضهم يقول: «كردي سوري». وقلّةٌ تكتفي بـ«سوري». والملاحظ أن الهوية ليست ثابتة، بل تتغيّر مع الظروف.
```
**On-screen text:**
```
معظمهم: كردي · بعضهم: كردي سوري · قلّة: سوري
```

### S17 · 4 Evidence · 00:04:01 · 11.3s
**Style:** quote card
**Visual:** Dark quote card, big quotation marks, highlighted phrase. Background: hands writing Kurdish letters in a notebook (AI).
**Files:** A10_hands_writing_notebook.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
واللغة تحتلّ مكانًا خاصًا. تصف الدراسة استخدام الكردية بأنه «مقاومة رمزية»: ليس سلاحًا، بل طريقة هادئة للقول: نحن هنا، ولنا ذاكرة.
```
**On-screen text:**
```
اللغة = «مقاومة رمزية»
```

### S18 · 4 Evidence · 00:04:12 · 18.3s
**Style:** two-column magazine spread
**Visual:** Village mosque dome at dawn (AI) left; right column: 'social presence ✓ / political determinant ✗'. Respectful, calm.
**Files:** A15_village_mosque_dawn.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
وماذا عن الدين؟ الحضور الديني واضح في المجتمع الكردي، من الطريقة النقشبندية إلى المشيخة الخزنوية. لكن الدراسة تلاحظ أن الدين ليس هو ما يحدّد الهوية السياسية لدى الشباب؛ إنه جزء من الحياة، لا عنوانها السياسي.
```
**On-screen text:**
```
الدين: حاضر اجتماعيًا · ليس محدِّدًا سياسيًا
```

### S19 · 4 Evidence · 00:04:30 · 19.3s
**Style:** animated checklist
**Visual:** Five checkmarks tick in one by one over real Nowruz footage (blurred, darkened). Each item gets a soft click.
**Files:** R04_nowruz_qamishli_2026.mp4
**Source line:** Al Jazeera English, 17 Jan 2026
**Narration:**
```
المرسوم ثلاثة عشر جاء بخطوات ملموسة: الاعتراف بالكردية لغةً وطنية يُسمح بتدريسها في المدارس، وجعل عيد نوروز عطلة رسمية مدفوعة، وإلغاء آثار إحصاء ألف وتسعمئة واثنين وستين، ومنح الجنسية للمتضرّرين بمن فيهم المكتومون، وحظر التمييز العرقي واللغوي.
```
**On-screen text:**
```
✓ الكردية لغة وطنية
✓ نوروز عطلة رسمية
✓ إلغاء آثار إحصاء ١٩٦٢
✓ الجنسية للمكتومين
✓ حظر التمييز
```

### S20 · 4 Evidence · 00:04:50 · 13.3s
**Style:** real footage + quote tag
**Visual:** Short real news footage from Aleppo Jan 2026 (no graphic images), then a quote tag «first step» with label 'Kurdish administration'.
**Files:** R06_aleppo_jan2026_news.mp4
**Source line:** Al Jazeera English, 17 Jan 2026
**Narration:**
```
جاء المرسوم بعد اشتباكات في حلب أودت بحياة ثلاثة وعشرين شخصًا على الأقل. ورحّبت به الإدارة الكردية، لكنها وصفته بأنه «خطوة أولى»، لا نهاية الطريق.
```
**On-screen text:**
```
«خطوة أولى»
```

### S21 · 4 Evidence · 00:05:03 · 25.3s
**Style:** bar chart drawn to scale
**Visual:** Horizontal chart to scale: Amnesty 2005 estimate as a range band 200k–360k; Hasakah registry 1962–2011 bar 517k with footnote 'includes descendants'. Bars grow with a pencil sound.
**Files:** G04_stateless_chart (Claude Code)
**Source line:** Arab News PK, Jan 2026; Amnesty International, 2005
**Narration:**
```
ولفهم حجم ما يحاول المرسوم إصلاحه: تشير سجلات الحسكة إلى أكثر من خمسمئة وسبعة عشر ألف شخص بلا جنسية بين عامي ألف وتسعمئة واثنين وستين وألفين وأحد عشر، مع احتساب الأبناء والأحفاد. وكانت منظمة العفو الدولية قد قدّرت العدد عام ألفين وخمسة بما بين مئتي ألف وثلاثمئة وستين ألفًا.
```
**On-screen text:**
```
سجلات الحسكة ١٩٦٢–٢٠١١: +٥١٧ ألف (مع الأحفاد)
العفو الدولية ٢٠٠٥: ٢٠٠–٣٦٠ ألف
```

### S22 · 4 Evidence · 00:05:28 · 19.3s
**Style:** real footage + 'sources differ' tag
**Visual:** Real footage of the Sept 2026 student protests (from news agency, credited). Yellow tool tag: 'Sources differ: study 3 · SANA 2'.
**Files:** R05_student_protests_sep2026.mp4, A07_empty_classroom.jpg
**Source line:** Hawar News; Syria TV; SANA, Sep 2026
**Narration:**
```
لكن القانون شيء، والصف الدراسي شيء آخر. في أيلول ألفين وستة وعشرين، قاطع طلاب في الحسكة والقامشلي وكوباني المدارس احتجاجًا على تقليص حصص الكردية. الدراسة تتحدّث عن ثلاث حصص أسبوعيًا، فيما تحدّثت وكالة سانا الرسمية عن حصّتين.
```
**On-screen text:**
```
أيلول ٢٠٢٦ | احتجاجات طلابية
٢–٣ حصص كردية أسبوعيًا
```

### S23 · 5 Counterarguments · 00:05:48 · 17.3s
**Style:** CHAPTER: Counterarguments + verdict stamp
**Visual:** Chapter card 'Counterarguments'. Claim written on a torn paper strip; a verdict stamp lands: ✗ 'as a generalisation'. Same template for S23–S26.
**Files:** G05_verdict_cards (Claude Code)
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
الاعتراض الأول: «الهوية الكردية مشروع انفصالي». هل يصمد؟ ليس كتعميم. الدراسة تُظهر أن معظم الشباب يطلبون الاعتراف داخل المواطنة، وأن الانتماء لديهم قابل للتفاوض. توجد أصوات أكثر تشدّدًا، لكنها لا تمثّل الصورة كلها.
```
**On-screen text:**
```
«انفصالي»؟ ✗ كتعميم
```

### S24 · 5 Counterarguments · 00:06:05 · 13.3s
**Style:** verdict card ✗
**Visual:** Same verdict template. Background: empty classroom (AI) next to protest still. Equation 'text ≠ practice' written in ink.
**Files:** A07_empty_classroom.jpg
**Source line:** Hawar News; Syria TV; SANA, Sep 2026
**Narration:**
```
الاعتراض الثاني: «المرسوم حلّ المشكلة». هذا لا يصمد. احتجاجات أيلول تُظهر أن المسافة بين النص والتطبيق ما زالت كبيرة، في المدارس والدوائر وتفاصيل الحياة اليومية.
```
**On-screen text:**
```
«انتهت المشكلة»؟ ✗ النص ≠ التطبيق
```

### S25 · 5 Counterarguments · 00:06:18 · 15.3s
**Style:** verdict card ◐
**Visual:** Half-filled verdict stamp ◐ 'partly holds'. A balance scale icon tilts slightly.
**Files:** G05_verdict_cards (Claude Code)
**Source line:** Al Jazeera English, 17 Jan 2026
**Narration:**
```
الاعتراض الثالث: «الاعتراف شكلي فقط». هذا يصمد جزئيًا. القوانين تحتاج إلى ممارسة ومؤسسات كي تصبح حقيقة. لكن استعادة الجنسية لمن حُرموا منها تغيير قانوني فعلي، يمسّ حياة أشخاص حقيقيين.
```
**On-screen text:**
```
«شكلي فقط»؟ ◐ يصمد جزئيًا
```

### S26 · 5 Counterarguments · 00:06:34 · 15.8s
**Style:** verdict card ◐
**Visual:** Verdict ◐. Background: village mosque at dawn (A15) blending into hands writing (A10) — both together, calm.
**Files:** A15_village_mosque_dawn.jpg, A10_hands_writing_notebook.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
الاعتراض الرابع: «الرابطة الدينية تكفي، ولا حاجة لهوية قومية». الدراسة لا تؤيّد هذا ولا تعاديه: الدين حاضر في حياة كثير من الشباب، لكنه لا يُلغي حاجتهم إلى الاعتراف بلغتهم وذاكرتهم.
```
**On-screen text:**
```
«الدين يكفي»؟ ◐ حاضر… لكنه لا يُغني عن الاعتراف
```

### S27 · 6 Stakes · 00:06:49 · 15.3s
**Style:** CHAPTER: Stakes + three doors
**Visual:** Chapter card 'What's at stake'. Drone shot of a crossroads (animated still); three paths labelled 1-2-3; path 1 glows.
**Files:** A09_crossroads_paths.jpg → MOTION M4
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
فإلى أين يمكن أن تتجه الأمور؟ ترسم الدراسة ثلاثة سيناريوهات. الأول: الانفتاح والاندماج، حيث تتحوّل خطوات مثل المرسوم ثلاثة عشر إلى ممارسة يومية، ويشعر الشاب الكردي بأنه شريك كامل.
```
**On-screen text:**
```
السيناريو ١ | الانفتاح والاندماج
```

### S28 · 6 Stakes · 00:07:05 · 13.8s
**Style:** same layout, path 2 glows
**Visual:** Path 2 glows; colour grade cools; a door closing sound (soft).
**Files:** A09_crossroads_paths.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
الثاني: الانغلاق والحماية. إذا شعر الشباب بأن الوعود لا تتحقّق، كما في احتجاجات المدارس، فقد ينكفئون نحو هوية دفاعية مغلقة، ترى في الآخر خطرًا لا شريكًا.
```
**On-screen text:**
```
السيناريو ٢ | الانغلاق والحماية
```

### S29 · 6 Stakes · 00:07:18 · 12.3s
**Style:** same layout, path 3 glows
**Visual:** Path 3 glows; a person sits on a bench by a window, waiting (AI, from behind). Clock tick under music.
**Files:** A14_waiting_by_window.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
والثالث: الانتظار وإعادة الترتيب. جيلٌ يراقب، لا يقطع مع أحد ولا يلتزم بالكامل، ينتظر أن يرى ماذا سيحدث على الأرض قبل أن يقرّر.
```
**On-screen text:**
```
السيناريو ٣ | الانتظار وإعادة الترتيب
```

### S30 · 6 Stakes · 00:07:31 · 17.3s
**Style:** direct address, warm grade
**Visual:** Wheat field in wind (animated still), golden light. Two lines of text appear, one per audience.
**Files:** A11_jazira_olive_wheat_landscape.jpg → MOTION M2, A11_jazira_olive_wheat_landscape.jpg
**Source line:** —
**Narration:**
```
ماذا يعني هذا لك؟ إن كنت شابًا كرديًا، فهويتك ليست قيدًا عليك ولا تهمةً ضدك. وإن كنت سوريًا من خلفية أخرى، فإن اعتراف جارك بلغته لا ينتقص من بلدك؛ بل يجعله أوسع للجميع.
```
**On-screen text:**
```
هويتك ليست تهمة
اعتراف جارك لا ينتقص منك
```

### S31 · 6 Stakes · 00:07:48 · 14.3s
**Style:** equation card
**Visual:** Clean equation on paper: 'particular identities kept + shared interests built'. Puzzle pieces lock together.
**Files:** G06_equation_card (Claude Code)
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
خلاصة الدراسة واضحة: الشباب الكرد ليسوا متلقّين لهوية جاهزة، بل منتجون لها. والعامل الحاسم ليس الشعار، بل إطار وطني يحفظ الخصوصيات، ويبني في الوقت نفسه مصالح مشتركة.
```
**On-screen text:**
```
خصوصيات محفوظة + مصالح مشتركة
```

### S32 · 7 Closing · 00:08:02 · 12.8s
**Style:** callback: 1962 → now, text behind person
**Visual:** Callback to S02: '1962' fades; the rooftop person (M1 shot) is pushed in slowly (still no face). Final line in giant type BEHIND the person. Music swells, then silence for 1 s.
**Files:** A01_rooftop_from_behind.jpg → MOTION M1, A16_bridge_at_dusk.jpg
**Source line:** —
**Narration:**
```
في عام ألف وتسعمئة واثنين وستين، قيل لعشرات الآلاف: أنتم غير موجودين. وبعد أكثر من ستين عامًا، يجيب أحفادهم بهدوء، بلغتهم، وبأسمائهم: نحن هنا.
```
**On-screen text:**
```
نحن هنا.
```

### S33 · 7 Closing · 00:08:15 · 15.3s
**Style:** dark slide + end card
**Visual:** Black slide, question centred. Then end card: logo, channel name, subscribe/comment prompt. No sources slide.
**Files:** dwin_logo.png
**Source line:** —
**Narration:**
```
والسؤال الآن ليس لهم وحدهم، بل لنا جميعًا: أيّ وطنٍ نريد، وطنٌ يطلب منك أن تنسى من أنت… أم وطنٌ يتّسع لك كما أنت؟ شاركنا رأيك بهدوء في التعليقات.
```
**On-screen text:**
```
أيّ وطنٍ نريد؟
```

## 6. YouTube post
**Title:** الانتماء لدى الشباب الكرد في سوريا: من «غير موجود» إلى «نحن هنا»

**Description:** كيف يعرّف الشباب الكرد في سوريا أنفسهم بعد الثورة وسقوط النظام والمرسوم ١٣؟ شرح هادئ ومتوازن: من إحصاء ١٩٦٢ إلى احتجاجات المدارس في أيلول ٢٠٢٦، والسيناريوهات الثلاثة للمستقبل.

Sources:
- Shvan Ibrahim — study on belonging among Kurdish youth in Syria during the revolution (5 Oct 2026) — main source
- Al Jazeera English — Syria's al-Sharaa issues decree recognising Kurdish rights (17 Jan 2026)
- Arab News PK — background on the 1962 census, statelessness and the Arab Belt (Jan 2026)
- Amnesty International — Kurds in the Syrian Arab Republic one year after the March 2004 events (2005)
- UNHCR figures on Decree 49 naturalisations (to mid-2013), as reported by Arab News PK
- Hawar News / Syria TV / SANA — Kurdish-language teaching and the September 2026 student protests
- Karl Mannheim — 'The Problem of Generations' (1928)

**Channel:** دوين - العربية
**Thumbnails:** see THUMBNAILS.md.

## 7. Fact notes
- Decree 13 announced 16 Jan 2026 by President Ahmad al-Sharaa (implementation from 29 Jan).
- Kurdish classes per week: the study says 3, SANA says 2 → shown as '2–3' with a 'sources differ' tag.
- 517,000 (Hasakah registry) includes descendants; not comparable 1:1 with the 120,000 stripped in 1962.
- Self-definitions (S16) are qualitative findings, not survey percentages — never invent percentages.