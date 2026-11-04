# Dwin documentary explainer: Mulla Othman Abdulaziz — Arabic (RTL)

## 1. Role and goal
You are a senior documentary editor and motion designer. Build an approximately 13-minute Vox-style documentary explainer in Arabic on the life of the Kurdish scholar and leader Mulla Othman Abdulaziz al-Halabji (1922–1999), founder of the Islamic Movement in Iraqi Kurdistan. The target is 12–14 minutes, with 14:00 as the hard maximum.
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
- Font: Aljazeera (fallback Noto Naskh Arabic). Shape text with Playwright/Chromium or HarfBuzz.
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
- Voice: one calm, warm, mature male Arabic narrator (Modern Standard Arabic), documentary pace. If using ElevenLabs v3 (supports Arabic): a deep calm voice, stability ~55%, style low.
- Music (royalty-free, instrumental only, no vocals):
  - S01–S04: ney/duduk over a soft drone.
  - S05–S15: gentle strings and oud with a soft frame drum; near silence at S15.
  - S16–S18: sparse, thoughtful.
  - S19–S26: warm, steady pulse.
  - S27–S30: low and neutral, with a short pause after each verdict.
  - S31–S35: warm build, with 1 s of silence before the last sentence of S34.
  - Duck the music −18 dB under the voice; no music hits on Qur'an or prayer imagery.
- SFX (subtle): paper slide, page turn, key click (S07), stamp (verdicts), camera flashes (S22), train ambience (S25), wind on the mountain scenes.

## 5. Scene by scene (estimated total ≈ 13.1 min)
Re-time every scene to the real narration. If the final cut runs over 14:00, shorten the pauses first.

### S01 · 1 Hook · 0:00 · 18.3s
**Style:** cold open, dark slide, slow push-in
**Visual:** Mud-and-wood house wall beside a small mosque at dusk (A01, M1). Kinetic quote builds word by word. Soft wind, a single ney note.
**Files:** A01_mud_house_by_mosque.jpg → MOTION M1, P01a_sheikh_portrait.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
رجلٌ أسّس حركة، وقابل الملوك، وأخذ رئيسُ وزراء تركيا بيده إلى المنبر… لكن بيته في حلبجة كان من طين وخشب، ولم يرمّمه قط. وكان يقسم: والله حتى اليوم لم أرَ ورقة دولار واحدة في بيتي.
```
**On-screen text:**
```
«لم أرَ ورقة دولار واحدة في بيتي»
```

### S02 · 1 Hook · 0:18 · 18.3s
**Style:** real funeral footage + quote
**Visual:** Real footage/photos of the 1999 funeral procession; rose petals (A12) drift over the frame. Lower-third: 'Kurdistan Region — 3 days of mourning'.
**Files:** R01_funeral_1999.mp4, A12_rose_petals_street.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
وحين توفي في دمشق عام 1999، عبرت جنازته من مدينة إلى مدينة، والناس يلقون عليها الورود، وأعلن إقليم كردستان الحداد ثلاثة أيام. ومع ذلك قال أقرب الناس إليه: لم نعرف قدر شيخنا إلا حين فقدناه.
```
**On-screen text:**
```
«لم نعرف قدر شيخنا إلا حين فقدناه»
```

### S03 · 1 Hook · 0:36 · 11.3s
**Style:** dark slide, question
**Visual:** Black slide. The question types in. A faint archival photo of the sheikh fades behind it at 20%.
**Files:** P01b_sheikh_teaching.jpg
**Source line:** —
**Narration:**
```
فمن هو الملا عثمان عبد العزيز؟ وكيف صار عالمُ حُجرةٍ في قرية صغيرة مؤسّسًا لأول حركة إسلامية منظّمة في كردستان العراق؟
```
**On-screen text:**
```
من هو الملا عثمان عبد العزيز؟
```

### S04 · 1 Hook · 0:47 · 4.3s
**Style:** TITLE CARD: text behind person
**Visual:** Giant name placed BEHIND the sheikh's real portrait (segmentation matte of P01a). Years 1922–1999 under it. Slow parallax, low boom.
**Files:** P01a_sheikh_portrait.jpg
**Source line:** —
**Narration:**
```
الملا عثمان عبد العزيز الحلبجي… سيرةٌ جامعة.
```
**On-screen text:**
```
الملا عثمان عبد العزيز
1922 – 1999
```

### S05 · 2 Context · 0:52 · 18.8s
**Style:** CHAPTER: Context + map
**Visual:** Chapter card. Paper map zooms to Halabja; pin on Prîsî Serû village. Real village/Hawraman landscape photo as a cut-out.
**Files:** R02_halabja_pris_village.jpg, G01_map_halabja (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
وُلد عام 1922 في قرية پريسي سەرو قرب حلبجة، في بيت علم. كان أبوه الملا عبد العزيز مدرّس مسجد القرية، وصاحب «حُجرة» يدرس فيها طلبة العلم على الطريقة الكردية التقليدية. هناك بدأ كل شيء.
```
**On-screen text:**
```
1922 | پريسي سەرو — حلبجة
```

### S06 · 2 Context · 1:11 · 10.3s
**Style:** explainer card + tool label
**Visual:** Hujra interior (A02, M2) with an oil lamp and stacked books. Tool label slides in: 'Hujra = the Kurdish mosque school'. Small icons: grammar · logic · fiqh · usul → ijaza.
**Files:** A02_hujra_interior_lamp.jpg → MOTION M2, A03_students_books_from_behind.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
والحُجرة هي مدرسة المسجد الكردي منذ قرون: يتنقّل فيها «الفقيه» بين القرى والعلماء، كتابًا بعد كتاب، حتى ينال الإجازة.
```
**On-screen text:**
```
الحُجرة = مدرسة المسجد الكردية
```

### S07 · 2 Context · 1:21 · 24.8s
**Style:** quote card, warm archival
**Visual:** Close-up of an old iron key on a wooden shelf (A04). Quote card in saffron. Portrait cut-out of Mulla Salih al-Kabir if provided (P03).
**Files:** A04_old_key_on_books.jpg, P03_mulla_salih_kabir.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
درس على أبيه، ثم على ابن عمه الملا صالح الكبير، وكان تحصيله العلمي كله داخل كردستان. وحين ضعفت صحة أبيه، أراد أن يمتحنه بعد أسبوع، فطلب الابن أن يُمتحن في الحال. سأله في أصعب المواضع فأجاب، فقبّل الأب جبينه وسلّمه مفاتيح الحُجرة وقال: من اليوم أنت في مكاني.
```
**On-screen text:**
```
«من اليوم أنت في مكاني»
```

### S08 · 2 Context · 1:46 · 25.3s
**Style:** story beat + book stack graphic
**Visual:** A stack of classical book spines grows (graphic, titles as labels: Jam' al-Jawami', al-Mutawwal, Sharh al-Mawaqif…). Then a wheat mill (A05). Cut-out of Sheikh Muhammad al-Khal (P04) with tool label.
**Files:** A05_wheat_mill.jpg, P04_sheikh_muhammad_khal.jpg, G02_book_stack (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
بعد وفاة أبيه صار يعيل الأسرة من طاحونٍ للحنطة، فذهب إلى السليمانية لامتحان رسمي يمنح راتبًا. دخل على الشيخ محمد الخال بلحية فتيّة وعمامة كردية، وطلب أن يُمتحن في كتب المنتهين لا المبتدئين. سألته لجنة العلماء في كل علم، حتى قال أحدهم: هذا ليس فقيهًا… بل هو أعلم منّا.
```
**On-screen text:**
```
«هذا ليس فقيهًا… بل هو أعلم منّا»
```

### S09 · 2 Context · 2:11 · 16.3s
**Style:** big number + calligraphy
**Visual:** Counter rolls to 57. Then a Qur'an on a wooden stand (A06), soft window light. Real photo of the sheikh teaching (P01b) as a cut-out.
**Files:** A06_quran_on_stand.jpg, P01b_sheikh_teaching.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
ثم جلس للتدريس سبعًا وخمسين سنة متواصلة. وكان يحفظ القرآن كاملًا، ويقول: لم أحفظ في عمري غير جزء عمّ لامتحان، أما الباقي فقد عشتُ في خدمة القرآن حتى حُفظ معي كله.
```
**On-screen text:**
```
57 سنة من التدريس
```

### S10 · 2 Context · 2:27 · 18.3s
**Style:** timeline + portrait cut-outs
**Visual:** Timeline bar jumps to 1954. Cut-outs of Amjad al-Zahawi (P05) and Mohammed Mahmoud al-Sawwaf (P06) slide in from Baghdad on the map; arrow to Halabja. Tool labels with names.
**Files:** P05_amjad_zahawi.jpg, P06_muhammad_sawwaf.jpg, G01_map_halabja (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
وفي عام 1954، زار حلبجة العلّامة أمجد الزهاوي والشيخ محمد محمود الصوّاف من بغداد. وفي لقاء مع علمائها، أُسند الإشراف على الدعوة في كردستان إلى الملا صالح والملا عثمان. ومن هنا بدأ العمل الدعوي المنظّم.
```
**On-screen text:**
```
1954 | بداية الدعوة المنظّمة
```

### S11 · 2 Context · 2:46 · 13.8s
**Style:** dark slide + map arrow south
**Visual:** Dark slide 'The first ordeal'. Map arrow Halabja → Nasiriyah (south). A barred window shadow (A07) crosses the frame.
**Files:** A07_prison_window_shadow.jpg, G01_map_halabja (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
وبعد انقلاب 1958، تصدّى علماء كردستان لحملات الشيوعيين المتنفّذين على شعائر الإسلام، فسُجن الملا صالح والملا عثمان ونُفيا إلى الناصرية عدة أشهر. كانت تلك المحنة الأولى.
```
**On-screen text:**
```
1959 | المحنة الأولى: النفي إلى الناصرية
```

### S12 · 2 Context · 2:59 · 19.8s
**Style:** two-panel magazine spread
**Visual:** Left panel 1970: cut-out of Mulla Mustafa Barzani (P07) + label 'Union of Religious Scholars'. Right panel 1974: cut-out of King Faisal (P08) + label 'Kurdish delegation to Saudi Arabia'. Panels mirror for RTL.
**Files:** P07_mulla_mustafa_barzani.jpg, P08_king_faisal.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
وبعد اتفاق الحكم الذاتي عام 1970، وافق الملا مصطفى البارزاني على مشروعه «اتحاد علماء الدين الإسلامي في كردستان»، وصار الشيخ عضوًا في القيادة ومسؤولًا عن السليمانية. وفي 1974 ترأس وفدًا كرديًا إلى السعودية، وقابل الملك فيصل.
```
**On-screen text:**
```
1970 | اتحاد العلماء · 1974 | لقاء الملك فيصل
```

### S13 · 2 Context · 3:19 · 24.3s
**Style:** dark slide, three stacked labels
**Visual:** Dark slide 'The second ordeal'. Three labels stack one by one: prison · hunger strike · the first pages of the tafsir. Desert road to Samawah (A08). Handwritten-page texture (A09) at the end.
**Files:** A08_desert_road_samawah.jpg, A09_handwritten_pages_lamp.jpg, P09_mulla_ali_abdulaziz.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
وفي 1976، سُجن مع عائلته أكثر من سنة، ثم نُفوا إلى السماوة. في السجن أعلن إضرابًا عن الطعام مع سجناء كرد وعرب، وكان يأذن لمن أنهكه الجوع بأن يفطر. وانتهى الأمر باتفاق، فكان، بحسب الرواية، أول إضراب ينجح في سجون العراق. وهناك أيضًا بدأ تفسير القرآن بالكردية.
```
**On-screen text:**
```
1976 | السجن · الإضراب · بداية التفسير
```

### S14 · 2 Context · 3:43 · 26.8s
**Style:** map migration arrows + real photo
**Visual:** Map: arrows from Halabja to the Iranian border, then a pin on Sanandaj. Silhouettes crossing a mountain pass (A10, M3). The founding name appears as a large magazine headline.
**Files:** A10_mountain_pass_migration.jpg → MOTION M3, R03_sanandaj_city.jpg, G01_map_halabja (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
وفي 1987، شنّت الحكومة حملة على حلبجة وما حولها. وكان الشيخ يحبّ أن يبقى في الداخل، فلم يهاجر إلا حين لم يبقَ خيار. عبر مع علماء حلبجة والأهالي نحو الحدود الإيرانية، وفي مدينة سنندج اتُّفق على دمج المجموعات الإسلامية الكردية في تنظيم واحد: «الحركة الإسلامية في كردستان العراق»، وكان الملا عثمان مرشدها.
```
**On-screen text:**
```
1987 | تأسيس الحركة الإسلامية في كردستان العراق
```

### S15 · 2 Context · 4:10 · 15.3s
**Style:** memorial, near silence
**Visual:** Real photo of the Halabja Monument (R04), slow push-in. Music drops to near silence. Date and number appear softly, no graphic images.
**Files:** R04_halabja_monument.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
وبعد أشهر، في 16 آذار 1988، قصف النظام حلبجة بالسلاح الكيميائي، فقُتل نحو خمسة آلاف مدني. مدينةُ الشيخ وأهله وطلابه. وصارت المجزرة جزءًا من ذاكرة الحركة وخطابها.
```
**On-screen text:**
```
16 آذار 1988 | حلبجة ≈ 5,000 مدني
```

### S16 · 3 Core problem · 4:26 · 11.8s
**Style:** CHAPTER: Core problem + split screen
**Visual:** Chapter card. Split screen: left the quiet hujra (A02), right a mountain front at dusk (A11). A thin line joins them with the sheikh's cut-out (P01a) in the middle.
**Files:** A02_hujra_interior_lamp.jpg, A11_mountain_front_dusk.jpg, P01a_sheikh_portrait.jpg
**Source line:** —
**Narration:**
```
وهنا يبدأ السؤال الحقيقي: كيف يجمع رجلٌ واحد بين هدوء الحُجرة وقسوة الجبهة؟ بين الفقه والسياسة؟ بين انتمائه الإسلامي وخصوصية شعبه الكردي؟
```
**On-screen text:**
```
الحُجرة والجبهة · الإسلام والكردية
```

### S17 · 3 Core problem · 4:37 · 12.8s
**Style:** Venn diagram, ink drawn
**Visual:** Two pairs of circles draw themselves: tradition + revival, Islamic + Kurdish. The overlaps glow saffron; the words 'respect' and 'dispute' appear on either side.
**Files:** G03_venn_movement (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
فالحركة التي أسّسها جمعت بين التقليد السنّي الكردي والصحوة الحديثة، وبين البعد الإسلامي والبعد الكردي. وهذا الجمع هو ما جعله محلّ تقدير… ومحلّ خلاف.
```
**On-screen text:**
```
تقليد + صحوة · إسلامي + كردي
```

### S18 · 3 Core problem · 4:50 · 17.3s
**Style:** dark slide, kinetic type
**Visual:** Black slide. A branching tree diagram briefly shows one trunk splitting into branches; then the question lands.
**Files:** G04_legacy_tree (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
ولماذا يهمّنا اليوم؟ لأن إرثه توزّع بعد وفاته على تنظيمات عدّة، تتفاوت في قربها من منهجه. ولأن السؤال الذي عاشه ما زال مطروحًا: كيف يكون العالِم قدوةً في السياسة دون أن يفقد روحه؟
```
**On-screen text:**
```
كيف يبقى العالِم عالِمًا في السياسة؟
```

### S19 · 4 Evidence · 5:07 · 33.0s
**Style:** CHAPTER: Evidence + uprising and truce
**Visual:** Chapter card. Real photos of the 1991 uprising (R09) as cut-outs. Paper map of the front: a gold 'pause' icon appears over it during the negotiations, then lifts; small pins mark the garrisons taken. Last beat: real 1992 election photo if provided (R05). No numbers, percentages or charts on screen.
**Files:** R09_uprising_1991.jpg, R05_election_1992.jpg, G01_map_halabja (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
لننظر إلى الوقائع. في انتفاضة 1991 كان للحركة وتنظيماتها وجمهورها دورٌ فاعل. ثم دخلت الجبهة الكردستانية في مفاوضات مع الحكومة العراقية، فلم تشارك الحركة فيها، لكن الشيخ أمر قواتها بوقف كل عملياتها ضد الحكومة حتى تنتهي المفاوضات. فلما انتهت استأنفت نشاطها، وسيطرت على عدد من المعسكرات والمقرّات الحكومية. وفي 1992 شاركت «القائمة الإسلامية» في أول انتخابات للإقليم، وترشّح الشيخ لقيادة الحركة التحررية الكردية.
```
**On-screen text:**
```
1991 | الانتفاضة · هدنةٌ طوال المفاوضات
```

### S20 · 4 Evidence · 5:40 · 18.8s
**Style:** quote card on dark
**Visual:** Dark quote card, large quotation marks, the line highlighted word by word. Background: a quiet street in Halabja (real, R06) at 30%.
**Files:** R06_halabja_street.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
ثم جاءت سنوات الاقتتال الكردي الداخلي. وكان يقول لأتباعه: «دخيلٌ خمسمئة دخيل، لا تشعلوا شجارًا، فإن قُتل ولدٌ كردي فهو مسلم». وحين وقعت المواجهة عام 1994، كان يقول: لا أرضى أن يُسفك دم كردي بيد كردي.
```
**On-screen text:**
```
«إن قُتل ولدٌ كردي… فهو مسلم»
```

### S21 · 4 Evidence · 5:59 · 20.8s
**Style:** two portraits + handshake graphic
**Visual:** Counter: 500+. Then two real cut-outs side by side: the sheikh (P01c) and Jalal Talabani (P11); a crescent icon marks 'first day of Ramadan'; a signed-paper icon. Cut-out of Masoud Barzani (P12) as the host, with a tool label.
**Files:** P01c_sheikh_older.jpg, P11_jalal_talabani.jpg, P12_masoud_barzani.jpg, D04_mou_1994.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
وبلغ عدد القتلى بين الحركة والاتحاد الوطني الكردستاني أكثر من خمسمئة. فسعى الشيخ إلى وساطةٍ رحّب بها جلال الطالباني، وأقام وفدُها شهرًا في ضيافة مسعود البارزاني. وفي أول يوم من رمضان، وقّع الشيخ عثمان وجلال الطالباني مذكرة التفاهم، وتمّ الصلح.
```
**On-screen text:**
```
+500 قتيل ← أول رمضان: الصلح
```

### S22 · 4 Evidence · 6:20 · 30.3s
**Style:** real photos + text behind person
**Visual:** Real photo of the sheikh with Necmettin Erbakan (P13) or at the 1996 conference. '50+' in giant type behind them. Then the Turkish parliament building (R07) with camera-flash SFX. Last beat: cut-out of Yusuf al-Qaradawi (P14) with a warm quote tag.
**Files:** P13_erbakan_with_sheikh.jpg, R07_turkish_parliament.jpg, P14_yusuf_qaradawi.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
وكان حضوره في العالم الإسلامي واسعًا. ففي 1996، في مؤتمر «الفاتحين» بتركيا، بحضور ممثلين عن أكثر من خمسين دولة ومنظمة، كان رئيس الوزراء نجم الدين أربكان يأخذ بيده بنفسه ويصعد به إلى المنبر. وحين أدخله البرلمان التركي بزيّه الكردي الديني، فتح الموظفون النوافذ ليلتقطوا له الصور. وفي الإمارات، أسرع إليه الشيخ يوسف القرضاوي قائلًا: «شيخنا، أحببناك قبل أن نراك».
```
**On-screen text:**
```
1996 | أربكان · مؤتمر الفاتحين · +50 دولة
```

### S22b · 4 Evidence · 6:50 · 34.0s
**Style:** two-panel spread + real group photo with name labels
**Visual:** First beat: a soft paper map with two thin lines, Kurdistan and Palestine, labelled 'شعبان بلا دولة'. A calligraphic name card 'صلاح الدين الأيوبي' (no face). Then the real 1989 photo (P16) with a slow Ken Burns; name tags slide in from the right in the order of the original caption. Do not mirror this photo. No flags, logos or armed imagery.
**Files:** P16_ahmad_jibril_meeting_1989.jpg (= IMG_2999.jpeg)
**Name labels (in the photo, from right to left):** 1 كاك محمد، نجل الملا علي · 2 الملا علي عبد العزيز · 3 أحمد جبريل · 4 الشيخ عثمان عبد العزيز
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
وكانت فلسطين حاضرةً في قلبه. فالكرد والفلسطينيون شعبان بلا دولة، ذاقا الاحتلال والتقسيم طويلًا، وكان الكرد ينظرون إلى قضيتها كقضية أخ. وكان الشيخ يراها أرض القبلة الأولى ومعراج النبي ﷺ، ويذكّر بأن محرّرها الثاني صلاح الدين الأيوبي كان كرديًا. وبعد أشهر من إعلان حركة حماس، التقاه ممثلها، وتكرّرت لقاءاته بالحركات الفلسطينية. وفي 1989 التقى أحمد جبريل، الأمين العام للجبهة الشعبية لتحرير فلسطين – القيادة العامة.
```
**On-screen text:**
```
«شعبان بلا دولة» · 1989 | لقاء أحمد جبريل
```

### S23 · 4 Evidence · 7:24 · 20.3s
**Style:** story beat, intimate
**Visual:** A dim room lit by one bulb; a small generator in the corner (A13). The quote lands in two beats.
**Files:** A13_dim_room_generator.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
أما في بيته، فلم يكن له مورد غير راتب الأوقاف. وكانت الكهرباء تأتي يومين في الأسبوع، فاقترح مرافقه شراء مولّد صغير. فسأله: هل تستطيع أن تشتري لكل الإخوة في المقرّ؟ قال: لا. فقال: «اشترِ للجميع… أو لا تشترِ لي».
```
**On-screen text:**
```
«اشترِ للجميع… أو لا تشترِ لي»
```

### S24 · 4 Evidence · 7:45 · 19.8s
**Style:** quiet beat
**Visual:** Close-up of an old cloth-merchant's ledger and a few coins (A14). Then a real photo of the sheikh in old age (P01c), slow push-in.
**Files:** A14_merchant_ledger_coins.jpg, P01c_sheikh_older.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
وإذا نفد راتبه قبل آخر الشهر، استلف عشرة دنانير من تاجر قماش، فإذا جاء الراتب كان أول ما يفعله ردّ الدين. وحين استشهد ابنه زبير، وجاءت الحركة تدفع لأسرته ما تدفعه لأسر الشهداء، رفض وقال: لا أريد المال.
```
**On-screen text:**
```
«لا أريد المال»
```

### S25 · 4 Evidence · 8:04 · 18.3s
**Style:** night train
**Visual:** Night train interior: a folded prayer rug on a seat by the window, lights streaking outside (A15, M4). Label 'Ankara → Istanbul'.
**Files:** A15_night_train_prayer_rug.jpg → MOTION M4
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
ولازم قيام الليل منذ شبابه، في الحضر والسفر. قال مرافقه إنه سافر معه ثلاثة أشهر فلم تفته ليلة واحدة. وفي قطارٍ بين أنقرة وإسطنبول، لم ينتظر حتى يصل إلى الفندق، فقام يتوضّأ ويصلّي في القطار.
```
**On-screen text:**
```
قيام الليل… حتى في القطار
```

### S26 · 4 Evidence · 8:23 · 24.3s
**Style:** book stack + checklist
**Visual:** Real photo of the 10-volume Kurdish tafsir on a shelf (D01) and the Bukhari commentary (D02). Volumes count up 1→10. Earlier, a soft 'wall' graphic that does not crack.
**Files:** D01_tafsir_10_volumes.jpg, D02_bukhari_sharh.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
وكان رفيقًا بمن ابتعد عن الدين. جاءه أتباعُ طائفةٍ محلية لا يدينون بالإسلام، يطلبون عقد نكاح أبنائهم على الشريعة، فقال: نعقد لهم، ولا تكسروا جدار الحياء بينهم وبين الإسلام، فإنه إن انكسر لم يعد. وترك تفسيرًا للقرآن بالكردية في عشرة مجلدات، ومجلدين من شرح صحيح البخاري بالكردية.
```
**On-screen text:**
```
تفسير بالكردية: 10 مجلدات · شرح البخاري: مجلدان
```

### S27 · 5 Counterarguments · 8:47 · 32.8s
**Style:** CHAPTER: Criticisms + verdict stamp ✗
**Visual:** Chapter card. Criticism written on a torn paper strip; verdict stamp ✗ 'ijtihad, not defection'. A doorway (A16) where the sheikh 'stood' (no person shown). Same verdict template for all criticisms.
**Files:** A16_old_doorway_pawe.jpg, A17_old_envelope_intact.jpg, D03_mb_letter.jpg, G06_verdict_cards (Claude Code), P14_yusuf_qaradawi.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
والآن، الانتقادات. أولها: «خرج على جماعة الإخوان وشقّ الصف». والوقائع تقول إن للافتراق سببين: نزعةٌ قومية عربية تصاعدت داخل الجماعة، ورفضُ جناحٍ فيها لمقاومة نظام البعث. وحين طُلب منه أن يتخلّى عن قيادة المقاومة قال: هذا عندي واجب شرعي، وهذا الشعب أُثقل بالظلم ولا يمكنني تركه. أما رواية أنه مزّق رسالتهم فينفيها المقرّبون منه، والرسالة محفوظة. وقال له القرضاوي: ليس لنا نقدٌ على اجتهادك.
```
**On-screen text:**
```
«شقّ الصف»؟ ✗ اجتهادٌ لا خروج
```

### S28 · 5 Counterarguments · 9:20 · 24.8s
**Style:** verdict ◐ + map links
**Visual:** Verdict ◐ 'support yes, dependence no'. Map with thin lines from Halabja to Riyadh, Ankara, Tehran (no flags). Cut-out of Abdulqadir Tawhidi (P15) with tool label.
**Files:** G06_verdict_cards (Claude Code), P15_abdulqadir_tawhidi.jpg, G01_map_halabja (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
الثاني: «كانت الحركة ورقةً بيد إيران». وهنا جزءٌ صحيح: نظام صدام كان عدوًا مشتركًا، والحركة استفادت فعلًا من الدعم الإيراني. لكن القرار بقي مستقلًا: صلاته بالسعودية استمرت، وارتبط بأربكان والقرضاوي، ومن تلاميذ مدرسة حلبجة من حمل السلاح على النظام الإيراني نفسه، كعبد القادر توحيدي عام 1984.
```
**On-screen text:**
```
«ورقة بيد إيران»؟ ◐ دعمٌ نعم… تبعيةٌ لا
```

### S28b · 5 Counterarguments · 9:45 · 43.5s
**Style:** verdict ✗ + two evidence cards
**Visual:** Same verdict template. Card 1: calligraphic name card 'ليث شبيلات | سياسي إسلامي، الأردن' (no face) with the label 'طهران 1989'. Card 2: a map pin on Qush Tepe; two simple truck icons wait while a counter runs 0→36 hours, then turn back. Last beat: an empty archive drawer (A19), 'not one document'. Never show or fake a document.
**Files:** G06_verdict_cards (Claude Code), G01_map_halabja (Claude Code), A19_empty_archive_drawer.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
الثالث: «أخذت الحركة مالًا وسلاحًا من الحكومة العراقية». والوقائع تقول غير ذلك. ففي 1989، في طهران، عرض عليه قادةٌ إسلاميون أردنيون، منهم ليث شبيلات، أن يتوسّطوا بينه وبين القيادة العراقية، فرفض. وفي الاقتتال الداخلي أرسلت الحكومة شاحنتين من السلاح والذخيرة إلى حدود قوش تبه لتتسلّمهما الحركة، فرفض الشيخ، وبعد ست وثلاثين ساعة من الانتظار أُعيدتا. ويتحدّى المقرّبون منه أن تظهر وثيقة واحدة على أن الحركة في عهده أخذت من الحكومة مالًا أو سلاحًا، ومن فعل ذلك سرًّا أو بعد وفاته فالمسؤولية عليه وحده.
```
**On-screen text:**
```
«دعمٌ من بغداد»؟ ✗ لا وثيقة واحدة
```

### S29 · 5 Counterarguments · 10:28 · 21.0s
**Style:** verdict ✗ + method card
**Visual:** Verdict ✗. The legacy tree's trunk only, labelled with the sheikh's method: 'لا تكفير · لا غلوّ'. No group names, logos or footage on screen.
**Files:** G04_legacy_tree (Claude Code), G06_verdict_cards (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
الرابع: «الحركة المسلّحة فتحت الباب للتشدّد». والجواب في منهج الشيخ نفسه: كان على عقيدة جمهور العلماء، لا يكفّر أحدًا، ولا يستهين بدين أحد، وكان يميل إلى المشاركة في مؤسسات الإقليم. وقد ظهرت من الحركة جماعاتٌ أخرى، منها «الإصلاح» و«أنصار الإسلام».
```
**On-screen text:**
```
«بابٌ للتشدّد»؟ ✗ لا تكفير ولا غلوّ
```

### S30 · 5 Counterarguments · 10:49 · 18.8s
**Style:** verdict ◐
**Visual:** Verdict ◐ 'yes… and a peacemaker'. Callback to the peace scene: the signed-paper icon returns.
**Files:** G06_verdict_cards (Claude Code), D04_mou_1994.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
الخامس: «كان طرفًا في الاقتتال الكردي». وهذا صحيح كواقعة: الحركة كانت طرفًا، وسقط أكثر من خمسمئة قتيل. لكن موقف الشيخ كان واضحًا: كان يشعر بأنه مسؤول عن كل جريح، وسعى بنفسه إلى الوساطة حتى وُقّع الصلح.
```
**On-screen text:**
```
«طرفٌ في الاقتتال»؟ ◐ نعم… وصانعٌ للصلح
```

### S31 · 6 Stakes · 11:08 · 23.8s
**Style:** CHAPTER: Stakes + legacy tree
**Visual:** Chapter card. The legacy tree grows branches with labels (no logos): mother Islamic Movement · Islamic Unity Movement (1999) · Islamic Group → Justice Group (2001/2021). Real photo of his grave in Halabja (R08) at the root.
**Files:** R08_sheikh_grave_halabja.jpg, G04_legacy_tree (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
توفي الشيخ في دمشق في 12 أيار 1999، ودُفن في حلبجة. ومن بعده امتدّ إرثه في تنظيمات عدّة: الحركة الإسلامية الأم التي ما زالت تعمل، وحركة الوحدة الإسلامية، والجماعة الإسلامية التي صارت «جماعة العدل»، إلى جانب مسارات أخرى. تتفاوت كلها في قربها من منهجه.
```
**On-screen text:**
```
12 أيار 1999 | إرثٌ توزّع على تنظيمات
```

### S31b · 6 Stakes · 11:32 · 27.5s
**Style:** map + three pillars, then a split
**Visual:** Paper map of the Kurdistan Region. Three equal pillars rise (قضائية · تنفيذية · تشريعية) with smaller blocks joining around them. Then the map slowly cracks into two halves. No party colours, flags or logos.
**Files:** G07_shared_admin_map (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
ويرى أبناء هذه التجربة أن السنوات الإحدى عشرة التي أعقبت الانتفاضة كانت فرصةً ذهبية لإدارة مشتركة: تتولّى فيها القوى الثلاث الرئيسة السلطات القضائية والتنفيذية والتشريعية، وتشارك فيها سائر المكوّنات بحسب حجمها، فتكون أساسًا متينًا للمشاركة في العملية السياسية في العراق. لكن ما جرى كان تقاسمًا، أورث الانقسام القائم اليوم… ودفع الجميع ثمنه.
```
**On-screen text:**
```
الخطأ التاريخي: تقاسمٌ بدل إدارة مشتركة
```

### S32 · 6 Stakes · 11:59 · 19.8s
**Style:** portrait + text behind person
**Visual:** Real portrait of the sheikh (P01a) with the line in giant type behind him. Warm grade.
**Files:** P01a_sheikh_portrait.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
فماذا يعني هذا لنا؟ يعني أن الشيخ ترك نموذجًا أكبر من أي تنظيم: عالمٌ لم يترك الحُجرة حين دخل السياسة، وجمع الانتماء الإسلامي إلى جانب خصوصية شعبه الكردي، وبقي محترمًا حتى عند خصومه، لأنه عاش ما كان يعلّمه.
```
**On-screen text:**
```
عاش ما كان يعلّمه
```

### S33 · 7 Closing · 12:19 · 18.8s
**Style:** CHAPTER: Closing + funeral callback
**Visual:** Chapter card. Callback to the opening: real funeral footage (R01), then a map where cities light up one by one: Halabja · Erbil · Pawe · Sanandaj · Marivan · Damascus · London.
**Files:** R01_funeral_1999.mp4, G01_map_halabja (Claude Code)
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
يوم جنازته، خرج الناس إلى الشوارع من مدينة إلى مدينة، وأُقيمت مجالس العزاء في حلبجة وأربيل، وفي پاوە وسنندج ومريوان، وفي دمشق ولندن. وقال أحد عارفيه: كنتُ في خدمته، فما سمعتُ منه قطّ إلا كلمة خير.
```
**On-screen text:**
```
«ما سمعتُ منه قطّ إلا كلمة خير»
```

### S34 · 7 Closing · 12:38 · 12.3s
**Style:** text behind person, slow
**Visual:** Real portrait (P01b or P01c). The testimony in giant type behind him. 1 s of silence before the last sentence.
**Files:** P01b_sheikh_teaching.jpg
**Source line:** Biography of Mulla Othman Abdulaziz (compiled study, 2026)
**Narration:**
```
عاش رجلًا… ومات رجلًا. ووصيةُ أقرب الناس إليه للأجيال: إن ظهر فيكم عالمٌ صالحٌ خاشعٌ لله، فأمسكوا به بيدٍ قوية، ولا تتركوه أبدًا.
```
**On-screen text:**
```
«فأمسكوا به بيدٍ قوية»
```

### S35 · 7 Closing · 12:50 · 14.3s
**Style:** dawn + end card
**Visual:** Dawn over Hawraman / Halabja (A18, slow). Final question centred (callback to the opening quote). Then the Dwin end card (logo, channel name). No sources slide.
**Files:** A18_dawn_hawraman.jpg, dwin_logo.png
**Source line:** —
**Narration:**
```
رحم الله الملا عثمان عبد العزيز. والسؤال لنا نحن: كم من عالمٍ صالحٍ بيننا اليوم… لا نعرف قدره إلا حين نفقده؟ شاركنا بهدوء: ماذا تعلّمتَ من سيرته؟
```
**On-screen text:**
```
كم من عالمٍ بيننا لا نعرف قدره؟
```

## 6. After the video is finished: thumbnails (required)
When the Arabic video is final, ALSO create its YouTube thumbnails in both formats, following THUMBNAILS.md:
- `thumbnails/thumb_ar_16x9.png` (1280×720, <2 MB)
- `thumbnails/thumb_ar_9x16.png` (1080×1920, Shorts/Reels cover)

## 7. Publishing texts
Ready in `social/youtube_ar.md` and `social/facebook_instagram_ar.md`. After the final edit, update the chapter timestamps (the first must stay at 0:00).

## 8. Fact notes
- The ijaza year is disputed in the sources (1935 is inconsistent with a 1922 birth), so the video gives no year for it.
- The claim that he was removed from the leadership near the end of his life is unverified and left out. The oral story about Salahaddin Bahaaddin's subscriptions is also left out.
- 'First successful hunger strike in Iraqi prisons' is attributed ('according to the account').
- 1992 election: no vote counts, percentages or thresholds appear anywhere in the film, because the author regards the published results as unreliable (the election was marred by fraud). The film only says the Islamic List took part and the sheikh stood as a candidate.
- S29: Islah and Ansar al-Islam are named only, with no description or characterisation.
- S28b: the Tehran 1989 offer and the Qush Tepe trucks come from the movement's own account. A remark attributed to Tariq Aziz about the other side receiving support is left out, in line with the no-hostility rule.
- S22b: the Hamas and Ahmad Jibril meetings come from the movement's own account; the photo's name order follows the author's caption.
- S31b is presented as the view of the movement's people ('يرى أبناء هذه التجربة'), not as the narrator's verdict.