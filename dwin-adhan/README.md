# series_adhan: production package (ar / ckb / kmr)

Same structure and workflow as `series_istighfar`. Read `source_content.md` first (what the video contains), then `script_master.md`.

## Folder structure

```
series_adhan/
├── README.md  source_content.md  script_master.md
├── manifest.json            9 scenes, all type=card
├── elevenlabs.csv           27 rows (9 scenes x 3 languages)
├── assets_to_buy.csv        everything MISSING
├── locales/  ar.json  ckb.json  kmr.json
├── assets/   scene01.jpg … scene09.jpg
│   ├── brand/  logo_shield.png  Aljazeera.ttf  Speda.ttf  Montserrat.ttf
│   └── music/  music_reflective.mp3  music_hopeful.mp3  music_resolve.mp3
├── audio/ ar/ ckb/ kmr/     sceneNN.mp3 (generated)
├── tools/                   scripts Claude Code will write
└── out/                     final renders: adhan_{lang}.mp4
```

## Decisions needed

1. **Angle:** you gave none for this video. I assumed *reflection, not proof*; the source calls it a miracle, the script does not. Tell me if you want the source's stronger framing (I would keep the school-variation counterargument either way).
2. **Spoken audio is not transcribed.** Paste a transcript to align the script with what the speaker actually says.
3. **Timeline:** no dates in the source, so `timeline` is `null`. Hide the bar.
4. **Assets:** all MISSING. Do not reuse the clip's footage (another creator's, plus a third-party reactor).
5. **ckb / kmr** are drafts: native review needed. Confirm ElevenLabs supports both before generating (not verified).
6. **Length:** ~75-90 s; the source is 140 s.

## NEEDS SOURCE before publishing

| Scene | Claim | Why |
|---|---|---|
| 03 | adhan = 50 words | my count of the 15-phrase wording; cite the wording's source and name the school |
| 04 | 50 prayers first prescribed at Isra, reduced to 5 | not on screen; cite the Isra and Mi'raj hadith (Bukhari / Muslim) with exact reference |
| 05 | 17 daily rak'ahs | correct for residence prayers; cite fiqh source |
| 06 | 17 distinct letters | depends on the counting rule; state it |
| 07 | wording varies by school; Fajr adds a phrase | verified numerically (72 / 58 words), but name schools and cite |

## Claude Code steps

Identical to `series_istighfar/README.md`; just change the folder and the render names:

```bash
cd series_adhan
export ELEVENLABS_API_KEY="your_key"
claude
```
1. "Read README.md, manifest.json, locales/*.json and elevenlabs.csv. Check every scene id appears in all three locales and in elevenlabs.csv. Report mismatches; change nothing."
2. "Write tools/generate_audio.py: read elevenlabs.csv, call ElevenLabs TTS with ELEVENLABS_API_KEY, save to output_file, skip existing, accept --lang."
3. Replace the `VOICE_ID_*_PLACEHOLDER` values, then `python tools/generate_audio.py --lang ar` (test scene01 first), then `ckb`, `kmr`.
4. "Write tools/measure_durations.py: ffprobe every audio/{lang}/sceneNN.mp3, write durations.json (seconds and frames at 24 fps, ceil)." Run it.
5. "Scaffold a Remotion project in video/: 1920x1080, 24 fps, one composition per language, reading manifest.json, locales/{lang}.json, durations.json. Scene length = audio length. Beige paper background, shield logo top-left on every scene, torn-edge photo card, headline in a highlight box, timeline hidden when null. Fonts: ar=Aljazeera, ckb=Speda, kmr=Montserrat. ar and ckb RTL (mirror layout), kmr LTR. Mix audio + music by music_mood with ducking. Missing asset → grey placeholder labelled MISSING."
6. `cd video && npx remotion studio`, then `npx remotion render adhan-ar ../out/adhan_ar.mp4` (and `-ckb`, `-kmr`).
7. "List every scene still using a MISSING placeholder and every scene flagged needs_source in manifest.json."

Assumption: Remotion is the renderer; swap if you use another.
