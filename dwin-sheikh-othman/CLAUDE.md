# CLAUDE.md — Dwin documentary: Mulla Othman Abdulaziz (ckb, ar)

Task: produce two videos from `prompts/01_sorani.md` and `prompts/02_arabic.md`. Each needs a 16:9 master (1920×1080, 24 fps) and a 9:16 version (1080×1920). The target is 12–14 min, never over 14:00. This is a standalone documentary.

Order of work:
1. Check `assets/` and `assets/people/` against `ASSETS.md` and report what is missing. If a person's photo is missing, use a calligraphic name card; never generate a face.
2. Build every G* graphic and the moving stills M1–M4 as described in `MOTION.md`.
3. Re-time every scene to `vo/<lang>.wav`, and re-time `subtitles/<lang>.srt` to match.
4. Render the 16:9 version, then the 9:16 version, for each language.
5. AFTER each video is done: create its YouTube thumbnails in BOTH formats, following `THUMBNAILS.md`.
6. Update the chapter timestamps in `social/youtube_<lang>.md` to the final edit.

Rules:
- Use the narration and on-screen text exactly as written. Never translate or edit them.
- The prompts in `prompts/` are FINAL and approved by the author. Follow them exactly, including every scene (S22b, S28b, S31b) and the fact notes in section 8. Stay professional and moderate: add no labels, captions or footage beyond what the prompts specify, with ONE exception: the extra people photos in `ASSETS.md` section A2. Place each one only in its mapped scene, as a small real-photo cut-out with a name label; skip it if the file is missing.
- R08 (grave) is not available: use the fallback written in `ASSETS.md`.
- Original clips (keep their ORIGINAL sound; never dub them):
  - `assets/R01_funeral_1999.mp4` (17.5 s, a eulogy poem over the funeral). In S02, keep its sound low (−22 dB) under the narration. At the START of S33, play its first 7 s at full level with the subtitle, then bring the narration in and duck the clip to −20 dB. Remove the «IMK TV» watermark and the bottom caption band («گۆڕستانی گۆلان») by cropping or blurring. Subtitles: `subtitles/clips/R01_funeral_ar.srt` (Arabic version) / `R01_funeral_ckb.srt` (Sorani version).
  - `assets/R10_lecture_prophet.mp4` (43 s, the sheikh's own voice speaking about the Prophet ﷺ). Insert it as a standalone moment BETWEEN S34 and S35: full screen, no narration, music faded out, original sound at full level. Arabic version: Arabic subtitles only from `subtitles/clips/R10_lecture_ar.srt` (translation; no voice-over). Sorani version: `subtitles/clips/R10_lecture_ckb.srt`. If the Sorani cut would pass 14:00, use only 4.1–43.1 s.
  - Subtitle timings for the clips are approximate; align each line to the speech.
- `assets/R01b_funeral_1999_photo.jpg` is an extra still from the funeral; use it in S02/S33 between video shots. The cloth over the coffin carries calligraphy, so keep it as it is (it is part of the event, not a party logo added by us).
- `assets/people/P17_zubair_with_brothers.jpg` shows Zubair with his two brothers; use the whole photo in S24.
- There is no photo of the father (P02); skip it.
- AUTHOR APPROVAL: the people photos marked `_restored` (AI-restored copies of real archival photos) are approved by the author and may be used. Still never generate NEW AI images of any real person.
- People photos are named by the author (in `assets/people/`). How to use them:
  - The only single portrait of the sheikh is `P01a_sheikh_portrait.jpg`. Use it for EVERY cut-out and every "text behind person" shot of the sheikh (S04, S16, S32, S34).
  - `P01b`–`P01g` and `P13` are GROUP photos that include the sheikh. Use them full-frame with slow Ken Burns moves wherever the prompt lists P01b/P01c/P13, and spread P01d–P01g over S09, S19, S22, S25 and S32–S34 as extra shots of him. Never cut one person out of a group photo, and never point at or label a single face in it.
  - `P01d_sheikh_with_sheikh_osman_naqshbandi.jpg`: use it as a general shot of the sheikh, with no extra name label (Sheikh Osman Naqshbandi is not part of the prompt).
  - `P09_mulla_ali_abdulaziz.jpg` and `P20_irfan_ali_abdulaziz.jpg` have flags behind the person: blur or crop the background.
  - `P13_erbakan_with_sheikh.jpg` has a flag at its right edge: crop it out.
  - `P21_saddam_hussein.jpg` shows a rifle being fired: use only a tight head-and-shoulders crop with no part of the weapon visible, small and desaturated, about 2 s (S28). If that is not possible, skip it.
  - `P19_salahaddin_bahaaddin.jpg`: use it in S31 as a separate small card beside the tree («مسارات أخرى»), not drawn as a branch (see ASSETS.md A2).
- Final asset list (the author will not send more):
  - P16 (1989 photo with Ahmad Jibril) is NOT available: in S22b use calligraphic name cards for the four names, in the caption order, with no faces.
  - R03 (Sanandaj) is not available: in S14 use the map pin on G01 only.
  - R06 (Halabja street) is not available: in S20 use R02_halabja_pris_village.jpg at 30% behind the quote card.
  - D02 (Bukhari commentary) is not available: in S26 show D01 only; the on-screen text stays as written.
  - D03 and D04 are not available: use the intact envelope (A17) and the signed-paper icon, as the prompt already allows.
  - R09_uprising_1991.jpg shows armed men; because the prompt forbids armed footage, crop it to faces and landscape so no weapon is visible.
  - R04_halabja_monument.jpg has a flag at the left edge: crop it out.
  - AI images (A01–A19) are 1672×941: upscale to 1920×1080 with Lanczos.
- Put the shield logo top-left on every scene. Both languages are RTL: mirror the layouts and the timeline.
- Fonts: Aljazeera (ar), Speda (ckb). Shape text with Playwright/Chromium or HarfBuzz.
- Text behind a person: use a rembg or MediaPipe matte of a real photo.
- Real photos first. No AI faces, no AI "restoration" of the sheikh's face, and no fake documents. AI images get an "illustration" tag.
- Music: use the original tracks in `assets/music/` as mapped in `assets/music/MUSIC.md` (one cue per section, plus the chapter boom and the verdict stamp).
- No flags, party logos, armed footage or victim images. No sources slide at the end.
- In the 9:16 version, keep the logo and text clear of the Instagram/TikTok buttons and caption area.
- To change content, edit the prompts directly, then run `python3 tools/make_srt.py` to refresh the subtitles, `script/scenes.json` and the YouTube chapters.
