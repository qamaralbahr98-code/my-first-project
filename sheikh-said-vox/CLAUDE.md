# CLAUDE.md — Dwin Vox documentary: Sheikh Said Piran

## Source of truth
- `script/master.json`: chapters, 54 scenes (narration `vo` and on-screen text `ost` in `ckb`, `kmr`, `ar`), visuals, sound, assets, facts, post descriptions.
- `script/brand.json`: colours, fonts, channel names, taglines.
- Generated (never edit by hand): `prompts/`, `vo/`, `subtitles/`, `script/scenes.*.json`, `assets/ASSETS.md`, `facts/fact_check.md`. Run `python3 tools/build.py` after any change; it must finish without `ERROR` lines.

## Rules
1. Never change narration or on-screen text unless the user asks for that exact change. Never translate, paraphrase or "fix" Kurdish or Arabic on your own; flag doubts instead.
2. Keep every fact from the source article (all of them are already in `script/master.json`). Do not cut scenes without asking.
3. Numbers: keep the "statistic of the time" label and the historians' estimate together (S31). Never reintroduce "200 thousand horsemen".
4. Opinion only in S52 (kind `position`, Dwin position tag). No individual or nation is attacked; the critique is of policies and propaganda.
5. No sources slide at the end of the video. Sources live in the description and `facts/fact_check.md`.
6. Images: use the pack in `assets/images/` (each scene lists its files). Archival photos stay black-and-white/sepia; AI images and paintings carry the illustration label, colourised photos the colourised label; any new AI image of a real person must be labelled the same way; no execution or gore imagery. The calendar in S23/S29 has one file per language (`_ckb`, `_kmr`, `_ar`).
7. Every scene keeps its `facts` and `assets` links.

## Rendering notes
- 1920 × 1080, 24 fps; optional 1080 × 1920 cut-down. H.264 `yuv420p`, AAC 48 kHz, −14 LUFS.
- Arabic-script text (`ckb`, `ar`) must be shaped by a real engine (browser via Playwright, or HarfBuzz/libraqm). Fonts: Speda (Sorani), Montserrat (Kurmanji), Aljazeera (Arabic), Noto fallbacks; Qur'an verse in a Naskh/Thuluth font with full harakat.
- Look: parchment paper world, torn-paper cut-outs, 2.5D parallax, ink annotations, gold highlights, animated dotted map routes, case board for chapters 5–6. Section 4 of each prompt has the full spec.
- Re-sync `subtitles/*.srt` to the recorded narration before burning in.

## Commit style
Short imperative messages, e.g. `Tighten Arabic narration in S37`.
