# CLAUDE.md — Dwin reel project

This repo holds the script and production prompts for a Dwin vertical news reel (Sorani, Kurmanji, Arabic) about the Almas cream controversy and influencer advertising.

## Source of truth
- `script/master.json`: every card (on-screen text in `ckb`, `kmr`, `ar`), b-roll, sound, fact references, post captions, facts.
- `script/brand.json`: colours, fonts, channel names, taglines.
- Everything in `prompts/`, `script/cards.*.json` and `facts/fact_check.md` is generated. Never edit those by hand; edit the sources and run `python3 tools/build.py`.

## Rules (do not break)
1. **Never change on-screen text** (`text.ckb`, `text.kmr`, `text.ar`) unless the user asks for that exact change. Do not translate, shorten, re-break lines or "fix" wording on your own; if something looks wrong, say so and ask.
2. **Accuracy.** Claims from the HOKAR video (fake, made in Erbil, forged sticker) stay attributed and are never shown as established fact. Card C06 (not confirmed by lab or court) must stay in every version.
3. **Law.** Penalties are **Article 12** of Iraq Consumer Protection Law No. 1 of 2010, not Article 10.
4. **Opinion only in Style C** cards with the `position_tag`. Never name or accuse an individual in an opinion card.
5. **Fairness.** No mocking effects, highlights or sound effects on Fakhir Hariri or the Kurdistan24 speaker.
6. Every news card (Style A/B) needs `fact_refs` pointing to `facts` in `master.json`.
7. After any change: run `python3 tools/build.py`. It must finish without `ERROR` lines.

## Rendering notes (if asked to render)
- 1080 × 1920, 30 fps, H.264 `yuv420p`, AAC 48 kHz, −14 LUFS.
- Read timings and styles from `script/cards.<lang>.json`; layout, animation and safe zones are specified in section 4 of the matching prompt.
- RTL languages (`ckb`, `ar`) must be shaped by a real text engine (a browser via Playwright, or HarfBuzz/libraqm). Never draw Arabic-script text with a renderer that has no shaping; letters would come out disconnected.
- Fonts: Speda (Sorani), Montserrat (Kurmanji), Aljazeera (Arabic). If the brand font files are not in `fonts/`, use the fallbacks in `brand.json` and tell the user.
- Captions only: produce transparent PNG sequences or ProRes 4444 `.mov` overlays per card so the editor can place them over footage in CapCut or Premiere.

## Commit style
Short imperative messages, e.g. `Update Kurmanji text for C21`.
