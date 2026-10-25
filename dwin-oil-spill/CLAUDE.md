# CLAUDE.md — Dwin oil-spill Vox explainer (Sorani + Kurmanji)

Task: create the two videos described in `prompts/01_sorani.md` and `prompts/02_kurmanji.md`.

- All images are in `assets/images/`; each scene in the prompts lists its exact files. Only `I17_dwin_logo.png` must be added by the user.
- Narration and on-screen text: use them exactly as written. Never translate or change Kurdish text.
- Output: 1920×1080 24 fps master + 1080×1920 version, H.264, AAC 48 kHz, −14 LUFS.
- Kurdish Sorani (RTL) must be shaped by a real text engine (browser/Playwright or HarfBuzz). Fonts: Speda / Montserrat, fallback Noto.
- AI photos and diagrams (I12) carry the "illustration" label; numbers show their source line; no sources slide at the end.
- To change content: edit `script/scenes.json`, then run `python3 tools/build.py`.
