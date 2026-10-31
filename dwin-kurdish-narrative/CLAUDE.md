# CLAUDE.md — Dwin Vox explainer: «The Kurdish narrative» (ckb, kmr, ar)

Task: produce three videos from `prompts/01_sorani.md`, `02_kurmanji.md` and `03_arabic.md`. Each needs a 16:9 master (1920×1080, 24 fps) and a 9:16 version (1080×1920). The target length is 9–12 min; never go over 12:00.

Order of work:
1. Check `assets/` against `ASSETS.md`. Report missing files before rendering. Build every G* graphic yourself; maps come from Natural Earth data on GitHub.
2. Build the moving stills M1–M4 as described in `MOTION.md`. If `AV01–AV04` exist, use those instead.
3. Re-time every scene to `vo/<lang>.wav`, and re-time `subtitles/<lang>.srt` to match.
4. Render the 16:9 version, then the 9:16 version, for each language.
5. AFTER each video is done: create its thumbnails in BOTH formats, following `THUMBNAILS.md`.
6. Update the chapter timestamps in `social/youtube_<lang>.md` to the final edit.

Rules:
- Use the narration and on-screen text exactly as written. Never translate or edit the text.
- Put the shield logo top-left on every scene in all languages. ar and ckb are RTL: mirror the layouts and the timeline. kmr is LTR.
- Fonts: Aljazeera (ar), Speda (ckb), Montserrat (kmr). Shape text with Playwright/Chromium or HarfBuzz.
- Text behind a person: segment the subject with rembg or MediaPipe.
- AI images get an "illustration" tag. Real material gets a credit taken from `assets/credits.txt`.
- No AI faces of real or historical people. No flags or party logos. No graphic violence. No sources slide at the end.
- To change content, edit `tools/make_scenes.py` (or `script/scenes.json`), then run `python3 tools/build.py`.
