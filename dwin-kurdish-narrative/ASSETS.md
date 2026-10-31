# Assets: download or create, then put them all in `assets/` with these exact names

Images must be at least 1920 px wide. Clips must be MP4, 1080p, 8–20 s each. Write the credit for each real item in `assets/credits.txt` (file name, publisher, link); Claude Code reads it to make the on-screen credit tags.

## A. Real material (28 items; download, never generate with AI)

### Historical documents and archival images (most are on Wikimedia Commons, public domain)
| File | What | Where |
|---|---|---|
| R01_sharafnama_manuscript.jpg | A page from a Sharafnama manuscript (Sharaf Khan Bidlisi, 1597) | Wikimedia Commons: "Sharafnama" |
| R02_saladin_statue.jpg | The Saladin statue (Damascus, by the Citadel), or the statue in Erbil | Wikimedia Commons / Unsplash |
| R03_jerusalem_old_city.jpg | Jerusalem Old City / Al-Aqsa compound, wide view | Wikimedia Commons / Unsplash |
| R04_chaldiran_mural.jpg | The Battle of Chaldiran mural, Chehel Sotoun, Isfahan | Wikimedia Commons: "Battle of Chaldiran" |
| R05_mem_u_zin_manuscript.jpg | A page from a Mem û Zîn manuscript (Ahmad Khani) | Wikimedia Commons: "Mem û Zîn" |
| R06_bedirxan_beg_portrait.jpg | An engraving or portrait of Bedirxan Beg, emir of Botan (if none is found, use a Botan/Cizre landscape) | Wikimedia Commons |
| R07_treaty_of_sevres_page.jpg | A page of the Treaty of Sèvres text (1920) | Wikimedia Commons: "Treaty of Sèvres" |
| R08_lausanne_conference_1923.jpg | Lausanne Conference delegates, 1922–23 | Wikimedia Commons: "Conference of Lausanne" |
| R17_mahabad_republic_1946.jpg | Archival photo of the Republic of Mahabad, 1946 | Wikimedia Commons: "Republic of Mahabad" |
| R19_said_nursi_portrait.jpg | Photo of Said Nursi | Wikimedia Commons |
| R20_sheikh_said_1925.jpg | Archival photo of Sheikh Said and companions, 1925 | Wikimedia Commons: "Sheikh Said rebellion" |

### Places (Wikimedia Commons, Unsplash, Pexels)
| File | What |
|---|---|
| R09_diyarbakir_walls.jpg | The Diyarbakır city walls |
| R10_sanandaj_city.jpg | Sanandaj (or Mahabad) city view |
| R11_erbil_citadel.jpg | Erbil Citadel |
| R12_qamishli_street.jpg | A Qamishli street |
| R13_nowruz_fire_akre.jpg | Nowruz fires on the hills (Akre/Aqrah or Duhok) |
| R14_amna_suraka_museum.jpg | Amna Suraka museum, Sulaymaniyah (exterior) |
| R15_halabja_monument.jpg | Halabja Monument |
| R16_dersim_landscape.jpg | Tunceli/Dersim landscape (Munzur valley) |
| R21_tekke_courtyard.jpg | Courtyard of a Sufi tekke or khanqah in Kurdistan (for example Biyare or Tawela), no close faces |
| R24_university_campus_kurdistan.jpg | A university campus in Erbil or Sulaymaniyah |
| R28_bazaar_erbil_or_diyarbakir.jpg | Erbil Qaysari bazaar or a Diyarbakır market, wide shot |

### News footage and photos (news agencies; crop out channel logos and credit the agency)
| File | What | Where |
|---|---|---|
| R18_us_withdrawal_2019.mp4 | US convoys leaving northeast Syria, Oct 2019 | AP / Reuters / AFP |
| R22_erbil_citadel_aerial.mp4 | Drone shot of Erbil Citadel | Pexels / Pixabay (free) |
| R23_referendum_2017.jpg | Voting in the Kurdistan Region referendum, Sept 2017 | Wikimedia Commons / AFP |
| R25_pkk_weapons_ceremony_2025.mp4 | Weapons-burning ceremony near Sulaymaniyah, July 2025 | Reuters / AP |
| R26_damascus_dec2024.mp4 | Crowds in Damascus, Dec 2024 | Reuters / AP |
| R27_syria_jan2026_agreement.mp4 | Coverage of Decree 13 or the SDF integration agreement, Jan 2026 | SANA / Reuters / AP |

**One "find real" prompt for all of them (paste into ChatGPT with browsing, or into Perplexity):**
> I am making a documentary explainer. For each item below, find a real, properly licensed source and give the direct URL, publisher, date, licence (public domain / CC / editorial) and the exact credit line to show on screen. Prefer Wikimedia Commons for historical items and original news agencies for footage. Never suggest AI-generated images. Items: (1) Sharafnama manuscript page; (2) Saladin statue in Damascus or Erbil; (3) Jerusalem Old City wide view; (4) Chaldiran battle mural, Chehel Sotoun; (5) Mem û Zîn manuscript page; (6) portrait of Bedirxan Beg of Botan; (7) Treaty of Sèvres text page; (8) Lausanne Conference 1922–23 delegates photo; (9) Diyarbakır walls; (10) Sanandaj city; (11) Erbil Citadel; (12) Qamishli street; (13) Nowruz fires in Akre; (14) Amna Suraka museum; (15) Halabja Monument; (16) Dersim/Munzur landscape; (17) Republic of Mahabad 1946 photo; (18) US convoys leaving NE Syria Oct 2019 video; (19) Said Nursi photo; (20) Sheikh Said 1925 photo; (21) Sufi tekke courtyard in Kurdistan; (22) Erbil Citadel drone video (free stock); (23) Kurdistan referendum voting 2017; (24) university campus in Erbil or Sulaymaniyah; (25) PKK weapons-burning ceremony July 2025 video; (26) Damascus crowds Dec 2024 video; (27) Syria Decree 13 or SDF integration agreement Jan 2026 video; (28) Erbil or Diyarbakır bazaar.

## B. AI images (8; make them in ChatGPT one at a time)
Add this to the end of EVERY prompt:
*"Single photograph, one frame only, no collage, no grid, no split screen, no text, no letters, no watermark, no flags, no logos, no recognisable faces, cinematic 16:9, 1920×1080, natural documentary colour, subtle film grain."*

| File | Prompt |
|---|---|
| A01_zagros_mountains_mist.jpg | Layered Zagros mountain ridges at dawn with mist in the valleys, a tiny stone village on a slope, cold blue light turning gold on the peaks, vast and quiet. |
| A02_old_book_pages_wind.jpg | An old leather-bound book lying open on a wooden table by a window, its pages lifting in the wind, warm side light, dust in the air, with no readable writing. |
| A03_person_on_ridge_sunrise.jpg | One person seen from behind standing on a rocky mountain ridge at sunrise, wearing a simple jacket, looking over valleys, centred, with lots of empty sky above the head (for a title placed behind the person). |
| A04_cracked_mirror.jpg | An antique round mirror on a dark wall, cracked into four large pieces, each piece reflecting a slightly different mountain landscape, moody light. |
| A05_islamic_manuscript_library.jpg | An old Islamic manuscript library with wooden shelves, stacked handwritten books and an open manuscript under lamplight; the script is blurred and unreadable, warm and scholarly. |
| A06_calligraphy_desk.jpg | A calligrapher's desk from above: reed pens, an ink pot, gold ink, blank cream paper and soft daylight, with no letters written yet. |
| A07_two_doors_corridor.jpg | A long, dim corridor ending in two old wooden doors side by side: the left door in cold blue shadow, the right door lit by warm golden light leaking through its gaps. |
| A08_group_walking_dusk.jpg | A group of five young people seen from behind, walking together on a hill road toward a town at dusk, silhouettes against an orange sky, with a feeling of togetherness and calm. |

## C. AI video: none needed
Claude Code animates A01, A02, A07 and A08 itself with free tools (see `MOTION.md`). If you want, you can also run those four images through a free image-to-video tool (Kling, Hailuo, Pika or Gemini/Veo) using the motion text in `MOTION.md`, and save the results as `AV01_*.mp4`…`AV04_*.mp4`. Claude Code will use them instead.

## D. Made by Claude Code (nothing needed from you)
G01 region map (Natural Earth) · G02 narrative boxes · G03 four currents · G04 dialect tree · G05 alliance string board · G06 Anfal range chart (to scale) · G07 broken chain · G08 verdict cards ✗/◐ · G09 scenario cards · chapter cards · timeline bar · captions · thumbnails (after the video).

## E. From you
- `dwin_logo.png`: the shield logo, transparent PNG
- `vo/ckb.wav`, `vo/kmr.wav`, `vo/ar.wav`: narration
- One music track (optional; otherwise Claude Code picks one from a royalty-free library)

**Total: 28 real items and 8 AI images, plus the logo, narration and music.**
