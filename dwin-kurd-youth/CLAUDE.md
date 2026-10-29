# CLAUDE.md — Dwin Vox explainer: Kurdish youth belonging in Syria (ckb, kmr, ar)

Task: produce three videos from `prompts/01_sorani.md`, `02_kurmanji.md`, `03_arabic.md`; each in 16:9 (1920×1080, 24 fps) and 9:16 (1080×1920).
- Assets: the user puts the files listed in `ASSETS.md` into `assets/` with those exact names. Build every G* graphic yourself (maps from Natural Earth on GitHub).
- Narration WAVs are in `vo/<lang>.wav` when provided. Re-time scenes to the real audio, and re-time `subtitles/<lang>.srt` too.
- Narration and on-screen text: use exactly as written. Never translate or edit the text.
- Shield logo top-left on every scene, in all languages. ar and ckb are RTL: mirror the layouts and the timeline direction. kmr is LTR.
- Fonts: Aljazeera (ar), Speda (ckb), Montserrat (kmr). Shape text with Playwright/Chromium or HarfBuzz.
- "Text behind person": segment the subject with rembg or MediaPipe.
- AI images get an "illustration" tag; real footage gets an agency credit; no AI faces of real people. No sources slide at the end.
- Moving shots: build M1–M4 and Ken Burns motion as described in MOTION.md (no paid video AI).
- Thumbnails: the user makes them; descriptions are in THUMBNAILS.md.
- To change content, edit `script/scenes.json`, then run `python3 tools/build.py`.
