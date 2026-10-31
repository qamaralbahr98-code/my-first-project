# Dwin Vox-style explainer: «The Kurdish narrative» — Kurdish Kurmanji (LTR)

## 1. Role and goal
You are a senior motion designer and documentary editor. Build an approximately 11.6-minute Vox-style explainer in Kurdish Kurmanji about the Kurdish narrative: how Kurds tell their story and how it is told about them. The target length is 9–12 minutes, with 12:00 as the hard maximum.
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
- Font: Montserrat (fallback Noto Sans). Shape text with a real engine (Playwright/Chromium or HarfBuzz).
- Direction LTR: the timeline runs left→right; reveals move left→right.
- Palette: paper #EFE8DC, ink #1B1B1B, dark slide #111418, saffron accent #E8A33D, muted red #B5483A, deep green #3F6B57. Accents only; never compose a flag.
- Look: paper grain overlay (8%), cut-outs with a 6 px white border and soft shadow, 2.5D parallax, hand-drawn ink arrows and circles, and film grain plus sepia on archival material.
- Persistent timeline bar (bottom, 6 px): 7 chapter ticks; the playhead shows the current era (year label) during S06–S13 and S33.
- Captions: burned in, 2 lines max, 46 px, cream on a 70% black box, word-level highlight in saffron. Also export the .srt from `subtitles/`.
- Transitions: paper-slide push (default); hard cut to a dark slide for chapter cards (S05, S14, S19, S27, S33, S37); whip-pan whoosh between real footage clips; match cut S01→S37 (same mountains).
- Text behind person (S04, S07 statue, S25, S38): segment the subject with rembg or MediaPipe. Layer order: background → giant title → subject matte → captions.
- Tool / lower-third labels: rounded tag, 28 px, icon + text, slides in from the reading side; used for names, places, dates and treaties.
- Moving stills: build M1–M4 as described in MOTION.md; every other still gets a Ken Burns move (1.00→1.05).

## 4. Voice, music and SFX
- Voice: one calm, warm, mid-low native Kurdish Kurmanji narrator at a measured pace with no drama. A human narrator is recommended, because ElevenLabs does not officially support Kurdish.
- Music (royalty-free, no vocals):
  - S01–S04: low drone and wind, with a single duduk/ney note.
  - S05–S13: light strings with a soft frame-drum pulse.
  - S14–S18: tense, sparse.
  - S19–S22: near silence, with piano only.
  - S23–S32: curious pulse, with a soft pause on each verdict stamp.
  - S33–S39: warm build; 1 s of silence before the last line of S38, then a gentle resolve.
  - Duck the music −18 dB under the voice.
- SFX (subtle): paper slide, stamp, quill scratch, typewriter tick, soft click on checklists, whoosh, distant wind on the mountain scenes.

## 5. Scene by scene (estimated total ≈ 11.6 min)
Re-time every scene to the real narration audio. If the final cut runs over 12:00, shorten the pauses first, then trim S10 and S22 (marked optional).

### S01 · 1 Hook · 0:00 · 16.8s
**Style:** cold open, dark slide, mountain parallax
**Visual:** Mist rolls over Zagros ridges (M1). The proverb writes itself in giant type, letter by letter. Wind + low drone.
**Files:** A01_zagros_mountains_mist.jpg → MOTION M1
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
«Ji çiyan pêve hevalên Kurdan tune ne». Gotinek e ku Kurd li çar welatan û bi dehan zaravayan dubare dikin. Lê pirs ev e: Gelo ev rastiyeke dîrokî ye… an çîrokek e ku em fêr bûne ji xwe re vebêjin?
```
**On-screen text:**
```
«Ji çiyan pêve hevalên Kurdan tune ne»
```

### S02 · 1 Hook · 0:16 · 20.0s
**Style:** magazine big number + map flash
**Visual:** Counter rolls to 30–40 million. A paper map of the region splits into four coloured state outlines (no flags).
**Files:** G01_region_map (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026) (estimates)
**Narration:**
```
Nêzîkî 30 heta 40 milyon mirov, di navbera Tirkiye, Îran, Iraq û Sûriyeyê de belav bûne. Pir caran wekî mezintirîn gelê bê dewlet ê cîhanê tên binavkirin. Hejmar texmînî ne, ji ber ku piraniya van dewletan di serjimariyên xwe de li ser etnîkê napirsin.
```
**On-screen text:**
```
≈ 30–40 milyon | 4 welat
```

### S03 · 1 Hook · 0:36 · 14.4s
**Style:** dark slide, question
**Visual:** Black. An old book opens; pages flutter (M2). The question appears centre screen.
**Files:** A02_old_book_pages_wind.jpg → MOTION M2
**Source line:** —
**Narration:**
```
Lê ev vîdyo napirse: Ax ya kê ye? Dipirse: Çîrok ya kê ye? Ji ber ku gelê ku çîroka xwe bi xwe venebêje, yên din wê jê re vedibêjin… bi awayê ku ew dixwazin.
```
**On-screen text:**
```
Çîrok ya kê ye?
```

### S04 · 1 Hook · 0:51 · 6.0s
**Style:** TITLE CARD: text behind person
**Visual:** Giant title BEHIND a person seen from behind on a ridge at sunrise (segmentation). Chapter ticks 1–7 appear on the timeline bar.
**Files:** A03_person_on_ridge_sunrise.jpg
**Source line:** —
**Narration:**
```
Vegotina Kurdî: Kurd çîroka xwe çawa vedibêjin… û çîroka wan çawa tê gotin.
```
**On-screen text:**
```
VEGOTINA KURDÎ
```

### S05 · 2 Context · 0:57 · 18.0s
**Style:** CHAPTER: Context + definition card
**Visual:** Chapter card. Dictionary-style card: 'Narrative (n.)'. Three nested boxes animate: narration ⊂ story ⊂ narrative. Tool label: 'Lawrence Freedman | strategist'.
**Files:** G02_narrative_boxes (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Pêşî, vegotin çi ye? Ne tenê gotina bûyeran e, lê çarçoveya ku gelek pê hildibijêre çi bi bîr bîne, îroya xwe çawa şîrove bike û ber bi ku ve here. Ew şerê li ser wateyê ye, berî ku bibe şerê li ser axê.
```
**On-screen text:**
```
Vegotin = şerê li ser wateyê
```

### S06 · 2 Context · 1:15 · 17.2s
**Style:** manuscript cut-outs + timeline
**Visual:** Real manuscript page of Sharafnama (cut-out, white border). Timeline bar ticks: 10th–12th c. emirates. Dots on map: Diyarbakır (Marwanids), Ganja (Shaddadids), Dinawar (Hasanwayhids).
**Files:** R01_sharafnama_manuscript.jpg, G01_region_map (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Kurd di dîrokê de ne nû ne. Mesûdî, Îbn Esîr û Yaqûtê Hemewî behsa wan kirine, û Şerefxanê Bidlîsî di sala 1597an de dîroka mîrektiyên wan di «Şerefname»yê de nivîsand. Mîrektiyên wan jî hebûn, wekî Merwanî li Amedê, Şeddadî û Hesenweyhî.
```
**On-screen text:**
```
«Şerefname» 1597 | Mîrektiyên Kurdî
```

### S07 · 2 Context · 1:32 · 18.0s
**Style:** hero cut-out, text behind statue
**Visual:** Real photo of the Saladin statue (Damascus or Erbil) cut out; '1187' behind it. Map arrow to Hattin and Jerusalem.
**Files:** R02_saladin_statue.jpg, R03_jerusalem_old_city.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Lûtkeya vê hebûnê bi Selahedînê Eyûbî re bû, kurê Tikrîtê û bi eslê xwe Kurd, ku Dewleta Eyûbî damezrand, di sala 1187an de li Hittînê bi ser ket û Qudsê azad kir. Wî xwe wekî serokekî neteweyî nedida nasîn, lê wekî serokê misilmanan.
```
**On-screen text:**
```
1187 | Hittîn û Quds
```

### S08 · 2 Context · 1:50 · 17.2s
**Style:** painting cut-out + map split
**Visual:** Real Safavid-era mural of Chaldiran (public domain) as a cut-out. Map: a line splits the Kurdish areas; emirate names pop up: Botan, Baban, Soran, Ardalan.
**Files:** R04_chaldiran_mural.jpg, G01_region_map (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Di sala 1514an de, di şerê Çaldiranê de, piraniya mîrên Kurd bi bandora zanayê Îdrîsê Bidlîsî ketin aliyê Osmaniyan. Bi vî awayî nêzîkî sê sedsalan xweseriyeke nîv-serbixwe bi dest xistin, ku tê de mîrektiyên Botan, Baban, Soran û Erdelan geş bûn.
```
**On-screen text:**
```
1514 | Çaldiran → 3 sedsal xweserî
```

### S09 · 2 Context · 2:07 · 16.0s
**Style:** quote card on parchment
**Visual:** Parchment quote card with a quill drawing the line. Real manuscript page of Mem û Zîn as background (blurred). Tool label: 'Ahmad Khani | poet, 1651–1707'.
**Files:** R05_mem_u_zin_manuscript.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Di bin siya wan mîrektiyan de, Ehmedê Xanî di sala 1692an de destana «Mem û Zîn» nivîsand. Di pêşgotina wê de bi xem dipirse: Ger padîşahekî me hebûya… bextê me di zeman de ji yên din bilindtir dibû.
```
**On-screen text:**
```
«Ger padîşahekî me hebûya…» — Ehmedê Xanî
```

### S10 · 2 Context · 2:23 · 18.0s · OPTIONAL CUT
**Style:** timeline + portrait cut-outs
**Visual:** Timeline ticks 1839 → 1847 → 1880. Ink stamp 'centralisation' falls on the emirate names. Real portrait of Bedirxan Beg if available (public domain).
**Files:** R06_bedirxan_beg_portrait.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Lê reformên sedsala nozdehan dawî li wan mîrektiyan anîn û desthilatdariya rasterast a navendê ferz kirin. Mîr û şêx serî hildan, wekî Bedirxan Beg di 1847an de û Şêx Ubeydullahê Nehrî di 1880an de. Ji vir şiyariyeke Kurdî ya nû dest pê kir.
```
**On-screen text:**
```
1847 · 1880 | Dawiya mîrektiyan
```

### S11 · 2 Context · 2:41 · 13.6s
**Style:** real document + ink highlight
**Visual:** Real scan of the Treaty of Sèvres text (Wikimedia). Articles 62–64 highlighted with a saffron marker, then the page greys out with the stamp 'never applied'.
**Files:** R07_treaty_of_sevres_page.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Paşê Dewleta Osmanî hilweşiya. Di sala 1920an de, Peymana Sêvrê di xalên 62 heta 64an de behsa xweseriya Kurdan û îhtimala serxwebûnê ya paşerojê kir. Lê ew qet nehat bicihanîn.
```
**On-screen text:**
```
1920 | Sêvr: soza ku bi cih nehat
```

### S12 · 2 Context · 2:55 · 23.6s
**Style:** archival photo + split-screen parallel
**Visual:** Real photo of the Lausanne Conference delegates (1922–23). Then split screen: 'Lausanne' in Kurdish memory | 'Sykes–Picot' in Arab memory — same scissors icon cutting a map.
**Files:** R08_lausanne_conference_1923.jpg, G01_region_map (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Piştî sê salan, Peymana Lozanê di 1923an de cihê wê girt. Navê Kurdan negot û sînorek xêz kir ku ew li ser çar dewletan parve kirin. Di bîranîna Kurdî de ev bû «birîna damezrîner»: parvekirinek ku ji jor ve hat ferzkirin, bêyî ku ji gelê herêmê bê pirsîn… tam wekî ku bîranîna Erebî Sykes–Picot bi bîr tîne.
```
**On-screen text:**
```
1923 | Lozan = «birîna damezrîner»
```

### S13 · 2 Context · 3:18 · 20.8s
**Style:** 4-panel magazine grid
**Visual:** Four cards flip one by one (order mirrors for RTL): Turkey · Iran · Iraq · Syria, each with population estimate and one keyword. Real city photos as card backgrounds: Diyarbakır walls, Sanandaj, Erbil Citadel, Qamishli.
**Files:** R09_diyarbakir_walls.jpg, R10_sanandaj_city.jpg, R11_erbil_citadel.jpg, R12_qamishli_street.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026) (estimates)
**Narration:**
```
Ji wê demê ve, Kurdan çar ezmûnên cuda jiyan: li Tirkiyeyê înkareke dirêj û paşê rêya aştiyê; li Îranê qadeke çandî bi tengasiya siyasî re; li Iraqê herêmeke federal ku ji 2005an ve bi destûrê hatiye naskirin; û li Sûriyeyê serjimariya 1962an, paşê xweseriya rêveberiyê, paşê qonaxeke nû piştî 2024an.
```
**On-screen text:**
```
Tirkiye 15–20 m · Îran 8–12 m · Iraq 6–7 m · Sûriye 2–3 m
```

### S14 · 3 Core problem · 3:39 · 16.0s
**Style:** CHAPTER: Core problem + shattered mirror
**Visual:** Chapter card. One word 'Kurdish narrative' cracks into four shards, each showing a label: classic nationalist · revolutionary left · liberal-reformist · Islamic.
**Files:** A04_cracked_mirror.jpg, G03_four_currents (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Û pirsgirêka rastîn li vir e: Yek vegotineke Kurdî tune ye. Malbateke vegotinan heye ku tevlihev dibin û pêşbaziyê dikin: neteweyî ya klasîk, çepgir a şoreşger, lîberal a reformxwaz û îslamî. Her yek «Kurd» bi awayekî cuda vedibêje.
```
**On-screen text:**
```
Ne yek vegotin… lê vegotin
```

### S15 · 3 Core problem · 3:55 · 16.0s
**Style:** Venn: what unites / what divides
**Visual:** Left column 'unites' (language, Nowruz, shared memory) glows warm; right column 'divides' (the goal: state? autonomy? 'democratic nation'?) in cool grey. Real Nowruz fire photo behind the left column.
**Files:** R13_nowruz_fire_akre.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Tiştê ku wan dicivîne hindik e lê kûr e: ziman, Newroz û bîranîna hevpar a êşê. Lê tiştê ku wan ji hev dixe mezin e: Armanc dewlet e? An xweserî? An «neteweya demokratîk» bê dewlet? Lihevkirin tune ye.
```
**On-screen text:**
```
Dicivîne: ziman · Newroz · bîranîn
Ji hev dixe: armanc
```

### S16 · 3 Core problem · 4:11 · 13.6s
**Style:** dialect tree diagram
**Visual:** Animated tree: Kurdish → Kurmanji · Sorani · Zazaki · Gorani · Southern. Two speech bubbles fail to meet, then a bridge word in Arabic/Turkish connects them.
**Files:** G04_dialect_tree (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Heta ziman bi xwe jî li ser çend zaravayan belav bûye; ya herî diyar Kurmancî û Soranî ne. Carinan du Kurd hewceyî Erebî an Tirkî dibin da ku rasterast hevdu fêm bikin.
```
**On-screen text:**
```
Kurmancî · Soranî · Zazakî · Goranî · Başûrî
```

### S17 · 3 Core problem · 4:25 · 13.6s
**Style:** string board / connections
**Visual:** Detective-style string board: three party pins connect with red threads to three capitals (Ankara · Tehran · Washington). Threads tangle; a label: 'each alliance → a different story'. No party logos or flags.
**Files:** G05_alliance_board (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Ya herî xeternak: hevpeymaniyên derveyî. Aliyek xwe dispêre Enqereyê, yekî din Tehranê, yê sêyem jî Waşingtonê. Her hevpeymanî çîrokê bi rengekî cuda boyax dike, û paşê di destê dijberan de dibe tawanbarî.
```
**On-screen text:**
```
Enqere · Tehran · Waşington → çîrokên dijber
```

### S18 · 3 Core problem · 4:38 · 13.6s
**Style:** dark slide, kinetic type
**Visual:** Black slide. Line 1 types in; line 2 lands with a soft boom.
**Files:** — (graphics only)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Çima ev girîng e? Ji ber ku doza ku vegotina wê tune be, dihele, heta ku hemû şertên mayînê jî hebin. Û ji ber ku yê ku çîrokê dinivîse… pêşerojê xêz dike.
```
**On-screen text:**
```
Yê ku çîrokê dinivîse… pêşerojê xêz dike
```

### S19 · 4 Evidence · 4:52 · 21.6s
**Style:** CHAPTER: Evidence + range chart
**Visual:** Chapter card. Range bar drawn to scale: 50,000 ——— 182,000, labelled 'estimates differ by source'. Real photo: Anfal memorial / Amna Suraka, Sulaymaniyah.
**Files:** R14_amna_suraka_museum.jpg, G06_anfal_range_chart (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026); Human Rights Watch, Genocide in Iraq (1993)
**Narration:**
```
Em li delîlan binêrin. Pêşî, bîranîn. Di kampanyaya Enfalê de li Iraqê di navbera 1986 û 1989an de, li gorî çavkaniyê, di navbera 50 hezar û 182 hezar mirovan de hatin kuştin. Di 2007an de Dadgeha Bilind a Tawanan a Iraqê ew wekî jenosîd binav kir.
```
**On-screen text:**
```
Enfal 1986–1989 | 50–182 hezar qurban
```

### S20 · 4 Evidence · 5:14 · 22.4s
**Style:** memorial photo + quote tag
**Visual:** Real photo of the Halabja Monument. Then a map pin on Dersim with a quote tag (Erdoğan, 2011). Respectful, slow, no graphic images.
**Files:** R15_halabja_monument.jpg, R16_dersim_landscape.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Di 16ê Adara 1988an de, Helebce bi çekên kîmyewî hat bombebarankirin û nêzîkî 5 hezar mirov mirin. Û li Dêrsimê li Tirkiyeyê, di navbera 1937 û 1938an de, bi hezaran kes hatin kuştin; Erdogan di 2011an de got ew «yek ji bûyerên herî trajîk ên dîroka me ya nêzîk» e.
```
**On-screen text:**
```
Helebce 1988 ≈ 5.000 | Dêrsim 1937–38
```

### S21 · 4 Evidence · 5:36 · 14.8s
**Style:** archival photo + countdown
**Visual:** Real archival photo of Mahabad 1946 (public domain). A calendar counter runs 11 months, then the image fades to sepia. Tool label: 'outside protection → 11 months'.
**Files:** R17_mahabad_republic_1946.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Li Îranê, Komara Mehabadê di 1946an de bi serokatiya Qazî Mihemed û di bin parastina Sovyetê de hat damezrandin. Tenê 11 mehan jiya, paşê dema Sovyet vekişiya hilweşiya, û Qazî Mihemed hat îdamkirin.
```
**On-screen text:**
```
Mehabad 1946 | parastina derveyî → 11 meh
```

### S22 · 4 Evidence · 5:51 · 11.6s · OPTIONAL CUT
**Style:** timeline with broken links
**Visual:** Timeline: 1975 → chain link snaps. Map arrow Iran→Iraq disappears. Tool label: 'Algiers Agreement, 1975'.
**Files:** G07_broken_chain (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Û çîrok dubare bû. Di 1975an de, piştî Peymana Cezayîrê di navbera Iraq û Îranê de, piştgirî ji şoreşa Mela Mistefa Barzanî hat kişandin, û şoreş hilweşiya.
```
**On-screen text:**
```
1975 | Peymana Cezayîrê → hilweşîna şoreşê
```

### S23 · 4 Evidence · 6:02 · 17.2s
**Style:** pattern timeline + quote card
**Visual:** Horizontal timeline of five dots: 1975 · 1991 · 2003 · 2014 · 2019. Dots turn from green to grey. Quote card: «a tactical partner, not a strategic ally». Real footage of convoys leaving NE Syria, Oct 2019 (news, credited).
**Files:** R18_us_withdrawal_2019.mp4
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Derbarê Dewletên Yekbûyî de jî, lêkolîn dibêje ku wê bi Kurdan re wekî «hevparekî taktîkî» tevgeriyaye, ne wekî «hevpeymanekî stratejîk»: piştgirî di 1991an de, hevpeymanî di şerê DAIŞê de, paşê vekişînek di 2019an de ku gelek Kurdan jê re got bêbextî.
```
**On-screen text:**
```
«Hevparê taktîkî… ne hevpeymanê stratejîk»
```

### S24 · 4 Evidence · 6:20 · 19.2s
**Style:** magazine portrait wall
**Visual:** Magazine spread: tall cut-out cards with names and one-line labels (no faces for medieval scholars — use manuscript/calligraphy cards; real photo only for Said Nursi). Big pull-quote in saffron.
**Files:** R19_said_nursi_portrait.jpg, A05_islamic_manuscript_library.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Li hember vê, delîleke ji cureyekî din heye: Kurd ne li ser kenarê şaristaniya îslamî bûn, lê li navenda wê bûn. Îbn Salahê Şarezorî di zanista hedîsê de, Ebulfîdayê Eyûbî di dîrok û erdnîgariyê de, Mewlana Xalidê Neqşebendî, û Bediuzzaman Seîdê Nûrsî di sedsala bîstan de.
```
**On-screen text:**
```
«Em di vê qada şaristanî de ne nû ne… em ji avakerên wê ne»
```

### S25 · 4 Evidence · 6:39 · 15.6s
**Style:** archival + text behind subject
**Visual:** Real archival photo of Sheikh Said and companions, 1925 (public domain), cut-out. Words 'Naqshbandi · Qadiri' behind the figures. Then a calm photo of a Sufi tekke courtyard (real).
**Files:** R20_sheikh_said_1925.jpg, R21_tekke_courtyard.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Bi rastî, serhildanên mezin, wekî serhildana Şêx Ubeydullahê Nehrî û serhildana Şêx Seîdê Pîran di 1925an de, ji aliyê şêxên terîqeta Neqşebendî ve hatin birêvebirin. Ol ne dijminê nasnameya Kurdî bû, lê beşek ji tevna wê bû.
```
**On-screen text:**
```
Ol: beşek ji tevnê… ne dijmin
```

### S26 · 4 Evidence · 6:54 · 26.4s
**Style:** aerial + mosaic of communities
**Visual:** Real aerial/drone footage of Erbil Citadel. Mosaic tiles light up: Kurds · Arabs · Turkmen · Christians. Then a second row: Sunni · Feyli Shia · Alevi · Yazidi · Kakai · Christian.
**Files:** R22_erbil_citadel_aerial.mp4, R11_erbil_citadel.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Delîleke din jî: Herêma Kurdistanê ya Iraqê, ku zêdetirî 20 sal in bi saziyên xwe di nava dewleteke federal de dixebite, û Hewlêr ku Kurd, Ereb, Tirkmen û Xiristiyan tê de dijîn. Civaka Kurdî bi xwe jî pirreng e: Sunnî, Şîeyên Feylî, Elewî, Êzidî, Kakeyî û Xiristiyan. Pirrengiyek ku dewlemendî ye… û ceribandinek e ji bo her vegotinê ku dixwaze mirovan bicivîne.
```
**On-screen text:**
```
Hevparî gengaz e · pirrengî = dewlemendî + ceribandin
```

### S27 · 5 Counterarguments · 7:21 · 24.8s
**Style:** CHAPTER: Counter-narratives + verdict stamp ◐
**Visual:** Chapter card. Claim on a torn paper strip; verdict stamp lands ◐ 'partly'. Bar: 92.73% 'yes' → isolation icons (closed airspace, borders). Same verdict template for S27–S32.
**Files:** R23_referendum_2017.jpg, G08_verdict_cards (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Niha, vegotinên dijber. Ya yekem: «Doza Kurdî projeyeke cudabûnê ye û yekîtiya dewletan dixe xeterê». Ma rast e? Tenê beşek. Erê, di referandûma 2017an de nêzîkî %93 «erê» gotin, lê ew ji aliyê herêmî û navneteweyî ve hat îzolekirin û nehat bicihanîn. Li hember vê, ezmûna herêmê nîşan da ku xweserî di nava dewletê de Iraq perçe nekir.
```
**On-screen text:**
```
«Cudabûn»? ◐ beşek
```

### S28 · 5 Counterarguments · 7:46 · 23.2s
**Style:** verdict ◐ + split
**Visual:** Verdict ◐. Split card: left 'the generalisation falls' (grey ✗), right 'the lesson stays' (saffron ✓) with mini-timeline Mahabad 1946 · Algiers 1975 · 2019.
**Files:** G08_verdict_cards (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Ya duyem: «Kurd amûrek in di destê hêzên derveyî de». Li vir rastî dualî ye. Giştandin rast nayê: tawanbariya xizmetkariyê pir caran ji bo rewakirina zordariyê hatiye bikaranîn, û hemû dewletên herêmê bi derve re hevpeymanî dikin. Lê ders dimîne: xwe spartina yên dûr gelek caran li Kurdan biha ketiye, ji Mehabadê heta Cezayîrê heta 2019an.
```
**On-screen text:**
```
«Amûra derve»? ◐ giştandin nayê… ders dimîne
```

### S29 · 5 Counterarguments · 8:09 · 27.2s
**Style:** verdict ✗ + calligraphy
**Visual:** Verdict ✗ on 'contradiction'. Then the Qur'anic verse (49:13) in elegant Arabic calligraphy on paper, gold ink, with the translation line underneath in ckb/kmr. Calm nasheed-free ambient.
**Files:** A06_calligraphy_desk.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026); Qur'an 49:13
**Narration:**
```
Ya sêyem: «Kurd berî ku Kurd bin misilman in, û neteweperwerî îthaleke rojavayî ye ku ummetê perçe dike». Zanayên Kurd, ji wan Nûrsî, bersiv didin ku pirrengî ayetek ji ayetên Xwedê ye: «Me hûn kirin gel û eşîr da ku hûn hevdu nas bikin». Naskirina nasnameyê ne dijî îslamê ye… ya ku dijî wê ye, kevneperestiya eşîrî û zilm e, ji kîjan aliyî dibe bila bibe.
```
**On-screen text:**
```
«وجعلناكم شعوبًا وقبائل لتعارفوا»
Me hûn kirin gel û eşîr da ku hûn hevdu nas bikin
```

### S30 · 5 Counterarguments · 8:36 · 17.6s
**Style:** verdict ✗
**Visual:** Verdict ✗. A stereotype label 'tribal' peels off a photo of a modern Erbil/Sulaymaniyah university campus (real).
**Files:** R24_university_campus_kurdistan.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Ya çaremîn: «Kurd tundî û eşîrtî ne». Ew şerê navxweyî yê di navbera du partiyên sereke yên Kurd de di salên nodî de wekî delîl nîşan didin. Lê hemû civakan nakokiyên navxweyî dîtine, û kurtkirina gelekî tevahî bo eşîrê qalibgirtineke nayê qebûlkirin.
```
**On-screen text:**
```
«Tundî û eşîrtî»? ✗ qalibgirtin
```

### S31 · 5 Counterarguments · 8:54 · 21.2s
**Style:** verdict ◐
**Visual:** Verdict ◐. A puzzle with missing pieces; label: 'divisions = partly the result of partition and repression'. Switzerland example as a small tool label.
**Files:** G08_verdict_cards (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Ya pêncemîn: «Kurd parçebûyî ne, ji ber vê yekê şert û mercên wan tune ne». Ev wekî teşxîs beşek rast e: parçebûn rastî ye. Lê wekî biryara dawî nayê, ji ber ku pirrengî nahêle ku saziyeke yekgirtî neyê avakirin, û parçebûn bi piranî encama parvekirin û zordariyê ne, ne xwezaya gel.
```
**On-screen text:**
```
«Bê şert û merc»? ◐ teşxîs rast… biryar şaş
```

### S32 · 5 Counterarguments · 9:15 · 21.2s
**Style:** verdict ✗ + news footage
**Visual:** Verdict ✗ on 'only arms bring rights'. Counter: 40,000+. Then real news footage of the July 2025 weapons-burning ceremony near Sulaymaniyah (credited, no logos).
**Files:** R25_pkk_weapons_ceremony_2025.mp4
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026); Reuters / AP, May–July 2025
**Narration:**
```
Vegotineke ji hundir jî heye: ku maf tenê bi çekan tên bidestxistin. Lê dîroka nêzîk tiştekî din dibêje. Şerê çekdarî li Tirkiyeyê, li gorî hejmarên fermî, zêdetirî 40 hezar kes kuştin, û di 2025an de PKKê belavkirina xwe ragihand, û rêyeke nû dest pê kir ku hîn jî çêdibe.
```
**On-screen text:**
```
+40.000 kuştî → 2025: ragihandina belavbûnê
```

### S33 · 6 Stakes · 9:36 · 18.4s
**Style:** CHAPTER: Stakes + real footage
**Visual:** Chapter card. Real footage: Damascus Dec 2024, then the Jan 2026 signing / decree coverage. Lower-third with dates. Timeline bar reaches 'now'.
**Files:** R26_damascus_dec2024.mp4, R27_syria_jan2026_agreement.mp4
**Source line:** Al Jazeera English, 17 & 30 Jan 2026
**Narration:**
```
Û îro? Li Sûriyeyê, piştî hilweşîna rejîmê di Kanûna 2024an de, di Çileya 2026an de Biryarnameya 13 derket ku Kurdî wekî zimanekî neteweyî nas kir, û li ser tevlîkirina HSDê di saziyên dewletê de lihevkirin çêbû. Rê hîn di destpêkê de ye.
```
**On-screen text:**
```
Sûriye 2026 | Biryarname 13 + lihevkirina tevlîbûnê
```

### S34 · 6 Stakes · 9:54 · 20.8s
**Style:** two doors, dark slide
**Visual:** Two doors on a dark slide: left door cold blue 'enmity', right door warm 'partnership'. The camera pushes toward the warm door (M3).
**Files:** A07_two_doors_corridor.jpg → MOTION M3
**Source line:** —
**Narration:**
```
Ev ji bo me tê çi wateyê? Tê wê wateyê ku herêm dikeve qonaxeke ku tê de çîrok ji nû ve tên xêzkirin. Pirs êdî ne tenê ev e: Kurd çi dixwazin? Lê ev e: Ew li ser xwe û cîranên xwe çi çîrokê vedibêjin? Çîroka dijminahiyê… an çîroka hevpariyê?
```
**On-screen text:**
```
Çîroka dijminahiyê… an çîroka hevpariyê?
```

### S35 · 6 Stakes · 10:15 · 18.8s
**Style:** 4 scenario cards
**Visual:** Four cards slide in like a magazine contents page: 1 status quo · 2 gradual wider recognition · 3 escalation (red, everyone loses) · 4 regional repositioning. Card 2 stays highlighted.
**Files:** G09_scenario_cards (Claude Code)
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Lêkolîn çar senaryoyan xêz dike: domandina rewşa heyî, an naskirineke berfirehtir a gav bi gav, an tundbûneke ku tê de her kes winda dike, an guherîneke herêmî ya mezin ku formûleke nû vedike. Kîjan bi cih bibe, beşek girêdayî wê çîrokê ye ku em hildibijêrin.
```
**On-screen text:**
```
1 Rewşa heyî · 2 Naskirina berfireh · 3 Tundbûn · 4 Guherîna herêmî
```

### S36 · 6 Stakes · 10:34 · 20.8s
**Style:** animated checklist over landscape
**Visual:** Checklist ticks over a wide shot of a shared market/bazaar (real, Erbil or Diyarbakır). Last line lands bigger, in saffron.
**Files:** R28_bazaar_erbil_or_diyarbakir.jpg
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Lêkolîn vegotineke pêşniyar dike ku ji partîtiyê derbas bibe, tundiya li dijî sivîlan ji her aliyî şermezar bike, bi Ereb, Tirk û Farisan re wekî cîran û hevparan ne dijminan diyalogê bike, û xwe bispêre mîrata Kurdan di şaristaniya îslamî de. Vegotineke ku zarokên herêmê dinivîsin… ne hesabên yên dûr.
```
**On-screen text:**
```
✓ Ji partîtiyê derbas ✓ Dijî tundiyê ✓ Cîran ne dijmin ✓ Mîrata şaristanî
Zarokên herêmê dinivîsin
```

### S37 · 7 Closing · 10:55 · 6.8s
**Style:** CHAPTER: Closing — callback to S01
**Visual:** Chapter card. Callback: the same mountains as S01 (M1), now at golden hour. Text fades in quietly.
**Files:** A01_zagros_mountains_mist.jpg → MOTION M1
**Source line:** —
**Narration:**
```
Dibe ku rojekê çiya tenê hevalên Kurdan bûn. Lê çiya çîrokan nanivîsin… mirov wan dinivîsin.
```
**On-screen text:**
```
Çiya çîrokan nanivîsin
```

### S38 · 7 Closing · 11:02 · 15.6s
**Style:** text behind people, warm grade
**Visual:** Silhouettes of a group of young people walking together at dusk toward a town (A08). Final line in giant type behind them. 1 s silence before the last two words.
**Files:** A08_group_walking_dusk.jpg → MOTION M4
**Source line:** Study: «The Kurdish Narrative in the Four States, the Islamic World and the World» (1st ed., 2026)
**Narration:**
```
Lêkolîn bi hêviyeke sade diqede: ku hevalên Kurdan ji mirovan hebin, ne tenê ji çiyan. Û yên herî nêzîk ne yên dûr in… lê ew cîran in ku ax, dîrok û îman bi wan re parve dikin.
```
**On-screen text:**
```
Heval ji mirovan… ne tenê ji çiyan
```

### S39 · 7 Closing · 11:17 · 18.4s
**Style:** dark slide + teaser end card
**Visual:** Black slide, the question. Then end card: logo, channel name, 'Next: belongings' teaser tag, subscribe/comment prompt. No sources slide.
**Files:** dwin_logo.png
**Source line:** —
**Narration:**
```
Îcar em ê ji zarokên xwe re kîjan çîrokê vebêjin? Di beşên bê de, em ê bêtir li ser van aîdbûnan biaxivin: Kurdî, îslamî û herêmî… û ka ew çawa dikarin di yek dîtinê de bicivin. Bi aramî ramana xwe di şîroveyan de binivîse.
```
**On-screen text:**
```
Em ê ji zarokên xwe re kîjan çîrokê vebêjin?
Zû: Aîdbûn
```

## 6. After the video is finished: thumbnails (required)
When the Kurdish Kurmanji video is final, ALSO create its YouTube thumbnails in both formats, following THUMBNAILS.md:
- `thumbnails/thumb_kmr_16x9.png` (1280×720, <2 MB)
- `thumbnails/thumb_kmr_9x16.png` (1080×1920, Shorts/Reels cover)
Use the brand font, the logo top-left, and text in this language only. Render them with Playwright and check them at phone size (160 px wide).

## 7. Publishing texts
Ready in `social/youtube_kmr.md` and `social/facebook_instagram_kmr.md`. After the final edit, update the chapter timestamps there to the real times; the first chapter must stay at 0:00.

## 8. Fact notes
- Population figures are estimates (no ethnic census in most states); always show them as ranges.
- Anfal deaths: 50,000–182,000 depending on the source; Iraqi High Tribunal genocide ruling 2007.
- Mulla Jami is listed as Kurdish in the study, but he was Persian, so he was removed. Ibn al-Athir is cited as a historian who wrote about Kurds, not as a Kurd.
- The study ends before the 2025 PKK dissolution announcement and the Jan 2026 Syria agreements; both were added from news sources.
- The Ahmad Khani line in S09 is a paraphrase from the study's Arabic rendering, not a verse translation.