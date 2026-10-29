# Dwin Vox-style explainer — Kurdish Kurmanji (LTR)

## 1. Role and goal
You are a senior motion designer and video editor. Build an 8.9-minute Vox-style explainer in Kurdish Kurmanji on belonging among Kurdish youth in Syria during and after the revolution. Tone: professional, calm, balanced, NOT nationalist, NOT against any group. The video explains; it does not campaign.

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
- Font: Montserrat (fallback Noto Sans). Shape text with a real engine (Playwright/Chromium or HarfBuzz) — never draw Arabic-script glyphs one by one.
- Direction LTR: timeline runs left→right; reveals move left→right.
- Palette: paper #EFE8DC, ink #1B1B1B, dark slide #111418, accent saffron #E8A33D, muted red #B5483A, muted green #4F7C5A (accent use only, never as a flag).
- Look: paper grain overlay (8%), cut-out photos with 6 px white border and soft shadow, 2.5D parallax on photos, ink-drawn arrows/circles, film grain on archival scenes.
- Captions: burned-in, 2 lines max, 46 px, white on 70% black box, word-level highlight in saffron. Also export .srt from `subtitles/`.
- Transitions: paper-slide push (default), hard cut to dark slide for chapter cards, whip-pan whoosh between real footage, match cut S02→S32 (the '1962' callback).
- 'Text behind person' (S04, S32): segment the subject with rembg / MediaPipe Selfie Segmentation, layer: background → giant title → subject matte → captions.
- Tool / lower-third labels: rounded tag, 28 px, icon + text, slides in from the reading side.
- Chapter cards (dark slides) at S04, S11, S16, S23, S27: number + chapter name, 2.5 s, low boom hit.

## 4. Voice and music
- Voice: one calm, warm, mid-low narrator, native Kurdish Kurmanji, measured pace, no drama. Human narrator recommended (ElevenLabs has no official Kurdish support).
- Music: royalty-free, no vocals. Act 1 (S01–S10): soft piano + low strings; Act 2 (S11–S22): light pulse, curious; Act 3 (S23–S29): sparse, thoughtful; S30–S33: warm build, 1 s silence before 'we are here', then soft resolve. Duck −18 dB under voice.
- SFX (subtle): paper slide, stamp, pencil scratch, typewriter tick, soft click on checklist, whoosh.

## 5. Scene by scene (total ≈ 8.9 min)

### S01 · 1 Hook · 00:00:00 · 15.8s
**Style:** dark slide + slow push-in
**Visual:** Young person seen from behind on a rooftop at dusk over a Jazira town. Kinetic caption builds word by word. Paper grain overlay.
**Files:** A01_rooftop_from_behind.jpg → MOTION M1
**Source line:** —
**Narration:**
```
Bifikire: tu li welatê xwe ji dayik dibî, lê mezin dibî… paşê tu dibînî ku dewlet li ser kaxezê hebûna te nas nake. Ev ne çîrokek xeyalî ye; ev jiyana bi deh hezaran Kurdên Sûriyeyê bû.
```
**On-screen text:**
```
Li vir ji dayik bûye… lê li ser kaxezê tune ye
```

### S02 · 1 Hook · 00:00:15 · 11.2s
**Style:** magazine big number + stamp sound
**Visual:** Giant year '1962' slams in, then the counter rolls to 120,000. Blank paper document (AI, labelled illustration) with a red ink circle drawn by hand.
**Files:** A02_blank_paper_document.jpg
**Source line:** Arab News PK, Jan 2026
**Narration:**
```
Di sala 1962an de, rayedaran li parêzgeha Hesekê serjimariyeke awarte kir. Di encamê de, zêdetirî sed û bîst hezar Kurd ji hemwelatiya Sûriyeyê bêpar man.
```
**On-screen text:**
```
1962 | Zêdetirî 120.000 Kurd bê hemwelatî
```

### S03 · 1 Hook · 00:00:27 · 18.7s
**Style:** dark slide, question in huge type
**Visual:** Cut to black. Question types in letter by letter with a soft typewriter tick. Faint crowd silhouettes behind.
**Files:** A13_crowd_silhouettes_dusk.jpg
**Source line:** —
**Narration:**
```
Îro, nifşek ku gelek piştî wan salan ji dayik bûye, şoreş, şer û koçberî dîtiye, pirsek hêsan û dijwar dike: Em aîdî ku derê ne? Ev vîdyo ne li ser dirûşman e; li ser nifşekî ye ku bi aramî dixwaze xwe pênase bike.
```
**On-screen text:**
```
Em aîdî ku derê ne?
```

### S04 · 1 Hook · 00:00:45 · 5.8s
**Style:** TITLE CARD: text behind person
**Visual:** Title in giant type placed BEHIND the person (segmentation matte of A08 or M1). Slow parallax. Logo stays top corner.
**Files:** A08_young_woman_from_behind_sunrise.jpg
**Source line:** —
**Narration:**
```
Aîdbûna ciwanên Kurd li Sûriyeyê… di dema şoreşê de û piştî wê.
```
**On-screen text:**
```
AÎDBÛN
Ciwanên Kurd li Sûriyeyê
```

### S05 · 2 Context · 00:00:51 · 15.4s
**Style:** animated map
**Visual:** Paper-texture map of Syria (Natural Earth). Dots light up: Hasakah, Qamishli, Kobani, Afrin, Aleppo, Damascus. City labels as lower-third tags.
**Files:** G01_map_syria_kurdish_areas (Claude Code), R10_kobani_city_view.jpg
**Source line:** Arab News PK, Jan 2026
**Narration:**
```
Em ji bingehê dest pê bikin. Li Sûriyeyê nêzîkî du milyon û nîv Kurd dijîn; piraniya wan li bakur û bakurê rojhilat in: Hesekê, Qamişlo, Kobanî û Efrîn, digel taxên mezin li Helebê û Şamê.
```
**On-screen text:**
```
≈ 2,5 milyon Kurd li Sûriyeyê
```

### S06 · 2 Context · 00:01:06 · 15.0s
**Style:** two cut-out cards, split screen
**Visual:** Two paper cards slide in from opposite sides: 'ajanib' and 'maktoumeen'. Icons: house, briefcase, plane, rings, baby — each crossed by an ink line.
**Files:** A12_family_album_hands.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
Serjimariya 1962an du kom çêkirin: «biyanî», yên ku bê hemwelatî hatin tomarkirin, û «mektûm», yên ku qet nehatin tomarkirin. Bê nasname, xwedîtiya milk, kar, rêwîtî û heta tomarkirina zewac û zarokan jî dijwar dibe.
```
**On-screen text:**
```
«Biyanî» û «Mektûm»
```

### S07 · 2 Context · 00:01:21 · 16.6s
**Style:** map + timeline bar
**Visual:** Timeline bar at bottom jumps to 1973. On the map a thin strip along the northern border fills with hatched ink. A blank village road sign (AI) has its name smudged.
**Files:** G01_map_syria_kurdish_areas (Claude Code), A04_blank_village_sign_wheat.jpg
**Source line:** Arab News PK, Jan 2026
**Narration:**
```
Di sala 1973an de, di dema Hafiz Esed de, projeya «Kembera Erebî» hat bicihanîn: malbatên Ereb li ser xeteke dirêj a sînorê bakur hatin bicihkirin, û navên gundên Kurdî hatin guhertin. Ev siyaseta dewletê bû, ne nakokiya cîranan.
```
**On-screen text:**
```
1973 | «Kembera Erebî»
```

### S08 · 2 Context · 00:01:38 · 14.1s
**Style:** warm archival look
**Visual:** Old radio glowing in a kitchen at night, hands of a parent turning the dial. Film grain, vignette. Caption fades in like handwriting.
**Files:** A03_old_radio_kitchen_night.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
Ziman jî bi dehsalan li derveyî dibistan û saziyên fermî ma. Zarokan ew li malê, ji stran û radyoyê fêr bûn. Bi vî awayî, peyva Kurdî bi xwe bû cureyek ji bîranînê.
```
**On-screen text:**
```
Zimanek ku li malê dihat fêrbûn
```

### S09 · 2 Context · 00:01:52 · 16.6s
**Style:** timeline + counter
**Visual:** Timeline jumps to 2011. Counter rolls to ≈104,000. Then a suitcase at a bus station (AI) as the music darkens.
**Files:** A06_suitcase_bus_station.jpg
**Source line:** UNHCR (via Arab News PK)
**Narration:**
```
Paşê sala 2011an hat. Bi destpêka şoreşê re, Biryarnameya 49 derket, û heta nîvê 2013an nêzîkî sed û çar hezar kesan hemwelatî wergirtin. Lê şerê ku li pey hat, koçberî û penaberî anî, û jiyana nifşekî tevahî guhert.
```
**On-screen text:**
```
2011 | Biryarname 49 → ≈104.000 hemwelatî
```

### S10 · 2 Context · 00:02:09 · 14.6s
**Style:** real footage + lower-third
**Visual:** Real footage: Damascus crowds Dec 2024, then the Decree 13 announcement. Lower-third label with date. Whoosh transition between the two.
**Files:** R07_damascus_dec2024_crowds.mp4, R03_decree13_announcement.mp4
**Source line:** Al Jazeera English, 17 Jan 2026
**Narration:**
```
Di Kanûna 2024an de, rejîma Esed hilweşiya. Û di 16ê Çileya 2026an de, serok Ehmed Şer'e Biryarnameya hejmar 13 a li ser mafên Kurdan ragihand. Ji nişka ve, pirsa kevn bû pirseke pratîkî.
```
**On-screen text:**
```
12/2024 → 16/1/2026 | Biryarname 13
```

### S11 · 3 Core problem · 00:02:23 · 17.5s
**Style:** CHAPTER: dark slide + portrait cut-out
**Visual:** Chapter card 'The core problem'. Real public-domain portrait of Karl Mannheim as a paper cut-out with tool label 'Karl Mannheim | sociologist'.
**Files:** R09_karl_mannheim_portrait.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
Civaknas Karl Mannheim digot ku nifş ne tenê bi temenê tê pênasekirin, lê bi bûyerên mezin ên ku bi hev re di temenê gihîştinê de dijîn. Ciwanên Kurd îro nifşek in ku di nava dilê şoreş û şer de çêbûne.
```
**On-screen text:**
```
Nifş = ezmûna hevpar
```

### S12 · 3 Core problem · 00:02:41 · 14.6s
**Style:** triptych magazine layout
**Visual:** Three vertical panels reveal one by one: ruined street (AI), suitcase/map with lines Qamishli–Erbil–Berlin, phone glow. Icons and labels.
**Files:** A06_suitcase_bus_station.jpg, A05_phone_in_hands_music.jpg → MOTION M3
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
Sê hêzan ev nifş şikil dan: şer, ku ewlehî kir pirseke rojane; koçberî, ku malbat di navbera Qamişlo, Hewlêr û Berlînê de belav kirin; û qada dîjîtal, ku bû meydaneke nû ya derbirînê.
```
**On-screen text:**
```
Şer · Koçberî · Dîjîtal
```

### S13 · 3 Core problem · 00:02:55 · 14.6s
**Style:** UI mock + echo effect
**Visual:** Hands holding a phone (AI); generic, invented app UI (no real brand) with Kurdish song cards. Then the frame duplicates into echoing mirrored copies (echo chamber).
**Files:** A05_phone_in_hands_music.jpg, A05_phone_in_hands_music.jpg → MOTION M3
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
Li ser ekranan, zimanê Kurdî vegeriya jiyanê: stran, rûpel, ders û nîqaş di navbera ciwanên ku qet hevdu nedîtine. Lê heman qad dikare bibe odeya dengvedanê, ku her alî tenê dengê xwe dibihîze.
```
**On-screen text:**
```
Cihek ji bo ziman… an odeya dengvedanê?
```

### S14 · 3 Core problem · 00:03:10 · 12.9s
**Style:** Venn diagram, ink drawn
**Visual:** Two circles draw themselves: 'Kurdish' and 'Syrian'. The overlap fills and reads 'Kurdish Syrian'. A key labelled 'equal citizenship' unlocks the overlap.
**Files:** G02_venn_identity (Claude Code)
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
Li vir dilê mijarê ye: Gelo divê ciwan di navbera Kurdbûn û Sûrîbûnê de hilbijêre? Lêkolîn dibêje: Na. Nasnameya dualî «Kurdê Sûrî» gengaz e… bi yek şertî: hemwelatiya wekhev.
```
**On-screen text:**
```
Kurdê Sûrî = gengaz → bi şertê hemwelatiya wekhev
```

### S15 · 3 Core problem · 00:03:23 · 20.8s
**Style:** split-screen diverging paths
**Visual:** Split screen: left path dims and leads to a departing bus; right path brightens into a classroom. Arrows drawn in ink.
**Files:** A09_crossroads_paths.jpg, A07_empty_classroom.jpg
**Source line:** —
**Narration:**
```
Çima ev girîng e? Ji ber ku ciwanê ku xwe dûrxistî hîs dike, vedikişe, koç dike an xwe digire. Lê yê ku hîs dike cihê wî heye, ava dike û beşdar dibe. Aîdbûn ne tenê hest e; ew e ku diyar dike gelo nifşek tevahî dimîne an diçe.
```
**On-screen text:**
```
Dûrxistin → vekişîn | Naskirin → beşdarî
```

### S16 · 4 Evidence · 00:03:44 · 17.9s
**Style:** CHAPTER: Evidence + qualitative scale
**Visual:** Chapter card 'Evidence'. Three stacked speech bubbles of decreasing size: 'Kurdish' (large), 'Kurdish Syrian' (medium), 'Syrian' (small). Footnote tag: 'qualitative study — not survey percentages'.
**Files:** G03_self_definition_bubbles (Claude Code)
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
Ev ciwan xwe çawa pênase dikin? Li gorî lêkolînê, piraniya wan bi sadeyî dibêjin: «Ez Kurd im». Hinek dibêjin: «Kurdê Sûrî me». Û hindikek tenê dibêjin «Sûrî me». Ya balkêş ew e ku nasname ne sabît e; li gorî rewşê diguhere.
```
**On-screen text:**
```
Piranî: Kurd · Hinek: Kurdê Sûrî · Hindik: Sûrî
```

### S17 · 4 Evidence · 00:04:02 · 12.9s
**Style:** quote card
**Visual:** Dark quote card, big quotation marks, highlighted phrase. Background: hands writing Kurdish letters in a notebook (AI).
**Files:** A10_hands_writing_notebook.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
Ziman jî cihekî taybet digire. Lêkolîn bikaranîna Kurdî wekî «berxwedaneke sembolîk» pênase dike: ne çek, lê rêyeke aram ji bo gotinê: Em li vir in, û bîranîna me heye.
```
**On-screen text:**
```
Ziman = «berxwedana sembolîk»
```

### S18 · 4 Evidence · 00:04:15 · 17.9s
**Style:** two-column magazine spread
**Visual:** Village mosque dome at dawn (AI) left; right column: 'social presence ✓ / political determinant ✗'. Respectful, calm.
**Files:** A15_village_mosque_dawn.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
Û ol? Hebûna olî di civaka Kurdî de diyar e, ji terîqeta Neqşebendî heta şêxtiya Xeznewî. Lê lêkolîn dibîne ku ol ne ew e ku nasnameya siyasî ya ciwanan diyar dike; ew beşek ji jiyanê ye, ne sernavê wê yê siyasî.
```
**On-screen text:**
```
Ol: civakî heye · ne diyarker a siyasî
```

### S19 · 4 Evidence · 00:04:32 · 17.9s
**Style:** animated checklist
**Visual:** Five checkmarks tick in one by one over real Nowruz footage (blurred, darkened). Each item gets a soft click.
**Files:** R04_nowruz_qamishli_2026.mp4
**Source line:** Al Jazeera English, 17 Jan 2026
**Narration:**
```
Biryarnameya 13 gavên berbiçav anîn: naskirina Kurdî wekî zimanekî neteweyî ku dikare li dibistanan were xwendin, kirina Newrozê betlaneyeke fermî ya bi mûçe, rakirina şopên serjimariya 1962an, dayîna hemwelatiyê ji bo zirardîtiyan û mektûman jî, û qedexekirina cudakariya etnîkî û zimanî.
```
**On-screen text:**
```
✓ Kurdî zimanê neteweyî
✓ Newroz betlaneya fermî
✓ Rakirina serjimariya 1962
✓ Hemwelatî ji bo mektûman
✓ Qedexeya cudakariyê
```

### S20 · 4 Evidence · 00:04:50 · 13.3s
**Style:** real footage + quote tag
**Visual:** Short real news footage from Aleppo Jan 2026 (no graphic images), then a quote tag «first step» with label 'Kurdish administration'.
**Files:** R06_aleppo_jan2026_news.mp4
**Source line:** Al Jazeera English, 17 Jan 2026
**Narration:**
```
Biryarname piştî pevçûnên li Helebê hat ku herî kêm bîst û sê kes tê de mirin. Rêveberiya Kurdî pêşwazî lê kir, lê got ew «gava yekem» e, ne dawiya rê.
```
**On-screen text:**
```
«Gava yekem»
```

### S21 · 4 Evidence · 00:05:04 · 25.0s
**Style:** bar chart drawn to scale
**Visual:** Horizontal chart to scale: Amnesty 2005 estimate as a range band 200k–360k; Hasakah registry 1962–2011 bar 517k with footnote 'includes descendants'. Bars grow with a pencil sound.
**Files:** G04_stateless_chart (Claude Code)
**Source line:** Arab News PK, Jan 2026; Amnesty International, 2005
**Narration:**
```
Ji bo têgihîştina mezinahiya tiştê ku biryarname dixwaze çareser bike: tomarên Hesekê nîşan didin ku di navbera 1962 û 2011an de zêdetirî pênc sed û hevdeh hezar kes bê hemwelatî bûn, bi zarok û neviyan re. Rêxistina Efûyê ya Navneteweyî di 2005an de hejmar di navbera du sed hezar û sê sed û şêst hezaran de texmîn kiribû.
```
**On-screen text:**
```
Tomarên Hesekê 1962–2011: +517 hezar (bi neviyan re)
Amnesty 2005: 200–360 hezar
```

### S22 · 4 Evidence · 00:05:29 · 19.1s
**Style:** real footage + 'sources differ' tag
**Visual:** Real footage of the Sept 2026 student protests (from news agency, credited). Yellow tool tag: 'Sources differ: study 3 · SANA 2'.
**Files:** R05_student_protests_sep2026.mp4, A07_empty_classroom.jpg
**Source line:** Hawar News; Syria TV; SANA, Sep 2026
**Narration:**
```
Lê qanûn tiştek e, pola dibistanê tiştekî din e. Di Îlona 2026an de, xwendekarên li Hesekê, Qamişlo û Kobaniyê dibistan boykot kirin, ji bo protestokirina kêmkirina dersên Kurdî. Lêkolîn behsa sê dersan di hefteyê de dike, lê ajansa fermî SANA behsa du dersan kir.
```
**On-screen text:**
```
Îlon 2026 | Protestoyên xwendekaran
2–3 dersên Kurdî di hefteyê de
```

### S23 · 5 Counterarguments · 00:05:48 · 18.3s
**Style:** CHAPTER: Counterarguments + verdict stamp
**Visual:** Chapter card 'Counterarguments'. Claim written on a torn paper strip; a verdict stamp lands: ✗ 'as a generalisation'. Same template for S23–S26.
**Files:** G05_verdict_cards (Claude Code)
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
Îtiraza yekem: «Nasnameya Kurdî projeyeke cudabûnê ye». Ma rast e? Wekî giştandin, na. Lêkolîn nîşan dide ku piraniya ciwanan di nava hemwelatiyê de naskirinê dixwazin, û aîdbûna wan li ser danûstandinê vekirî ye. Dengên tundtir hene, lê ew ne tevahiya wêneyê ne.
```
**On-screen text:**
```
«Cudabûn»? ✗ wekî giştandin
```

### S24 · 5 Counterarguments · 00:06:06 · 12.9s
**Style:** verdict card ✗
**Visual:** Same verdict template. Background: empty classroom (AI) next to protest still. Equation 'text ≠ practice' written in ink.
**Files:** A07_empty_classroom.jpg
**Source line:** Hawar News; Syria TV; SANA, Sep 2026
**Narration:**
```
Îtiraza duyem: «Biryarnameyê pirsgirêk çareser kir». Ev rast nayê. Protestoyên Îlonê nîşan didin ku dûrahiya navbera nivîs û bicihanînê hîn mezin e, li dibistan, dezgeh û hûrguliyên jiyana rojane.
```
**On-screen text:**
```
«Pirsgirêk qediya»? ✗ Nivîs ≠ bicihanîn
```

### S25 · 5 Counterarguments · 00:06:19 · 18.3s
**Style:** verdict card ◐
**Visual:** Half-filled verdict stamp ◐ 'partly holds'. A balance scale icon tilts slightly.
**Files:** G05_verdict_cards (Claude Code)
**Source line:** Al Jazeera English, 17 Jan 2026
**Narration:**
```
Îtiraza sêyem: «Naskirin tenê formel e». Ev beşek rast e. Qanûn ji bo ku bibin rastî, pêdivî bi pratîk û saziyan heye. Lê vegerandina hemwelatiyê ji bo yên ku jê bêpar mabûn, guhertineke qanûnî ya rastîn e ku jiyana mirovên rastîn digire.
```
**On-screen text:**
```
«Tenê formel»? ◐ beşek rast e
```

### S26 · 5 Counterarguments · 00:06:37 · 16.2s
**Style:** verdict card ◐
**Visual:** Verdict ◐. Background: village mosque at dawn (A15) blending into hands writing (A10) — both together, calm.
**Files:** A15_village_mosque_dawn.jpg, A10_hands_writing_notebook.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
Îtiraza çaremîn: «Girêdana olî bes e, pêdivî bi nasnameya neteweyî nîne». Lêkolîn ne piştgirî dike ne dijberî: ol di jiyana gelek ciwanan de heye, lê ew hewcedariya wan bi naskirina ziman û bîranîna wan ji holê ranake.
```
**On-screen text:**
```
«Ol bes e»? ◐ heye… lê cihê naskirinê nagire
```

### S27 · 6 Stakes · 00:06:53 · 16.2s
**Style:** CHAPTER: Stakes + three doors
**Visual:** Chapter card 'What's at stake'. Drone shot of a crossroads (animated still); three paths labelled 1-2-3; path 1 glows.
**Files:** A09_crossroads_paths.jpg → MOTION M4
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
Îcar tişt dikarin ber bi ku ve biçin? Lêkolîn sê senaryoyan xêz dike. Ya yekem: vebûn û entegrasyon, ku tê de gavên wekî Biryarnameya 13 dibin pratîka rojane, û ciwanê Kurd hîs dike ku hevparekî tam e.
```
**On-screen text:**
```
Senaryo 1 | Vebûn û entegrasyon
```

### S28 · 6 Stakes · 00:07:10 · 16.6s
**Style:** same layout, path 2 glows
**Visual:** Path 2 glows; colour grade cools; a door closing sound (soft).
**Files:** A09_crossroads_paths.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
Ya duyem: girtin û parastin. Heke ciwan hîs bikin ku soz bi cih nayên, wekî di protestoyên dibistanan de, dibe ku ber bi nasnameyeke parastinê ya girtî ve vekişin, ku yê din wekî xetere dibîne, ne wekî hevpar.
```
**On-screen text:**
```
Senaryo 2 | Girtin û parastin
```

### S29 · 6 Stakes · 00:07:26 · 17.9s
**Style:** same layout, path 3 glows
**Visual:** Path 3 glows; a person sits on a bench by a window, waiting (AI, from behind). Clock tick under music.
**Files:** A14_waiting_by_window.jpg
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
Û ya sêyem: li benda man û ji nû ve rêxistin. Nifşek ku temaşe dike, ne bi kesî re qut dike ne jî bi tevahî girê dide, li bendê ye ku bibîne li ser erdê çi dibe berî ku biryarê bide.
```
**On-screen text:**
```
Senaryo 3 | Li bendê man û rêxistina nû
```

### S30 · 6 Stakes · 00:07:44 · 22.1s
**Style:** direct address, warm grade
**Visual:** Wheat field in wind (animated still), golden light. Two lines of text appear, one per audience.
**Files:** A11_jazira_olive_wheat_landscape.jpg → MOTION M2, A11_jazira_olive_wheat_landscape.jpg
**Source line:** —
**Narration:**
```
Ev ji bo te tê çi wateyê? Heke tu ciwanekî Kurd î, nasnameya te ne zincîr e li ser te, ne jî tawanbarî ye li dijî te. Heke tu Sûriyekî ji paşxaneyeke din î, naskirina zimanê cîranê te tiştekî ji welatê te kêm nake; berevajî, wî ji bo herkesî firehtir dike.
```
**On-screen text:**
```
Nasnameya te ne tawan e
Naskirina cîranê te ji te kêm nake
```

### S31 · 6 Stakes · 00:08:06 · 15.8s
**Style:** equation card
**Visual:** Clean equation on paper: 'particular identities kept + shared interests built'. Puzzle pieces lock together.
**Files:** G06_equation_card (Claude Code)
**Source line:** Shvan Ibrahim, study on Kurdish youth belonging in Syria (5 Oct 2026)
**Narration:**
```
Encama lêkolînê zelal e: ciwanên Kurd ne wergirên nasnameyeke amade ne, lê hilberînerên wê ne. Faktora diyarker ne dirûşm e, lê çarçoveyeke niştimanî ye ku taybetmendiyan biparêze û di heman demê de berjewendiyên hevpar ava bike.
```
**On-screen text:**
```
Taybetmendiyên parastî + berjewendiyên hevpar
```

### S32 · 7 Closing · 00:08:22 · 15.4s
**Style:** callback: 1962 → now, text behind person
**Visual:** Callback to S02: '1962' fades; the rooftop person (M1 shot) is pushed in slowly (still no face). Final line in giant type BEHIND the person. Music swells, then silence for 1 s.
**Files:** A01_rooftop_from_behind.jpg → MOTION M1, A16_bridge_at_dusk.jpg
**Source line:** —
**Narration:**
```
Di sala 1962an de, ji bi deh hezaran re hat gotin: Hûn tune ne. Piştî zêdetirî şêst salan, neviyên wan bi aramî, bi zimanê xwe û bi navên xwe bersiv didin: Em li vir in.
```
**On-screen text:**
```
Em li vir in.
```

### S33 · 7 Closing · 00:08:37 · 19.1s
**Style:** dark slide + end card
**Visual:** Black slide, question centred. Then end card: logo, channel name, subscribe/comment prompt. No sources slide.
**Files:** dwin_logo.png
**Source line:** —
**Narration:**
```
Niha pirs ne tenê ji bo wan e, ji bo me hemûyan e: Em çi welatî dixwazin? Welatek ku ji te dixwaze tu ji bîr bikî tu kî yî… an welatek ku te wekî xwe hildigire? Bi aramî ramana xwe di şîroveyan de binivîse.
```
**On-screen text:**
```
Em çi welatî dixwazin?
```

## 6. YouTube post
**Title:** Aîdbûna ciwanên Kurd li Sûriyeyê: ji «tune ye» heta «em li vir in»

**Description:** Ciwanên Kurd li Sûriyeyê piştî şoreş, hilweşîna rejîmê û Biryarnameya 13 xwe çawa pênase dikin? Ravekirineke aram û hevseng: ji serjimariya 1962an heta protestoyên dibistanan di Îlona 2026an de, û sê senaryoyên pêşerojê.

Sources:
- Shvan Ibrahim — study on belonging among Kurdish youth in Syria during the revolution (5 Oct 2026) — main source
- Al Jazeera English — Syria's al-Sharaa issues decree recognising Kurdish rights (17 Jan 2026)
- Arab News PK — background on the 1962 census, statelessness and the Arab Belt (Jan 2026)
- Amnesty International — Kurds in the Syrian Arab Republic one year after the March 2004 events (2005)
- UNHCR figures on Decree 49 naturalisations (to mid-2013), as reported by Arab News PK
- Hawar News / Syria TV / SANA — Kurdish-language teaching and the September 2026 student protests
- Karl Mannheim — 'The Problem of Generations' (1928)

**Channel:** Dwîn - Kurmancî
**Thumbnails:** see THUMBNAILS.md.

## 7. Fact notes
- Decree 13 announced 16 Jan 2026 by President Ahmad al-Sharaa (implementation from 29 Jan).
- Kurdish classes per week: the study says 3, SANA says 2 → shown as '2–3' with a 'sources differ' tag.
- 517,000 (Hasakah registry) includes descendants; not comparable 1:1 with the 120,000 stripped in 1962.
- Self-definitions (S16) are qualitative findings, not survey percentages — never invent percentages.