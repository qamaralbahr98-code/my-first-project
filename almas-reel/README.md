# Dwin reel: Almas cream and influencer ads

Three ready-to-use video prompts (Sorani, Kurmanji, Arabic) for a Dwin text-driven news reel based on the article **"Fake Cream, Real Victims: Influencer Ads and Consumer Rights in Kurdistan"** (2026-10-23).

The prompts are written in English. Only the text that appears on screen is in Kurdish Sorani, Kurdish Kurmanji or Arabic.

| Language | Prompt | Timed cards (for tools) | Length |
| --- | --- | --- | --- |
| Kurdish Sorani | `prompts/01_sorani.md` | `script/cards.ckb.json` | ~2:23 |
| Kurdish Kurmanji | `prompts/02_kurmanji.md` | `script/cards.kmr.json` | ~2:34 |
| Arabic | `prompts/03_arabic.md` | `script/cards.ar.json` | ~2:21 |

## What the reel does
1. **Hook:** a cream advertised by famous faces; a viral video says it is fake; the price.
2. **The accusation** (HOKAR video), clearly marked as a claim, plus a card saying it is **not yet confirmed** by a lab or court.
3. **The official warning** (Kurdistan24 report on whitening pills).
4. **The response** (Fakhir Hariri, quoted fairly in his own words).
5. **The law:** Iraq Consumer Protection Law No. 1 of 2010, Articles 1, 3, 7, 9 and 12.
6. **Dwin's position:** a labelled condemnation of everyone who misleads people with unchecked ads.
7. **Protect yourself:** four practical actions.
8. **Close:** "Before you buy, ask: who checked it?", sources and the Dwin end card. The last shot loops to the first.

## Important correction
The source article says the penalties are in **Article 10**. In the official law text they are in **Article 12** (Article 10 is about the consumer council's staff). The prompts use Article 12. Details: `facts/fact_check.md`.

## How to use

**Without code:** open the prompt for your language, copy all of it, and give it to your editor or to an AI video/editing assistant together with the three source clips (HOKAR reel, Kurdistan24 reel, Fakhir Hariri's clarification video).

**With Claude Code:** open this folder in Claude Code and ask, for example:
- "Render the Sorani reel from `script/cards.ckb.json`."
- "Make transparent caption overlays (PNG sequence) for every Arabic card so I can drop them into CapCut."
- "Change the Kurmanji text of card C21, then rebuild."

`CLAUDE.md` tells Claude Code the rules of this project.

## Editing
Edit only `script/master.json` (content) and `script/brand.json` (colours, fonts), then run:

```bash
python3 tools/build.py
```

This checks every card (all three languages present, line lengths, fact references, opinion only in labelled cards) and regenerates `prompts/`, `script/cards.*.json` and `facts/fact_check.md`.

**Before the first video:** put Dwin's official colour codes into `script/brand.json`. The current values are placeholders.

## Put it on GitHub
```bash
git remote add origin https://github.com/<your-account>/dwin-almas-reel.git
git push -u origin main
```

## Folder map
```
prompts/            the three prompts (generated)
script/master.json  all content: cards in 3 languages, b-roll, sound, facts
script/brand.json   Dwin colours, fonts, channel names, taglines
script/cards.*.json timed cards per language (generated)
facts/fact_check.md every fact, its status and where it is used (generated)
source/article.txt  the original article
tools/build.py      checks + build
```

## Rendered videos (made with Claude)
The three finished reels are in `output/`:

| Language | File |
| --- | --- |
| Kurdish Sorani | `output/dwin_almas_ckb_v01.mp4` |
| Kurdish Kurmanji | `output/dwin_almas_kmr_v01.mp4` |
| Arabic | `output/dwin_almas_ar_v01.mp4` |

To rebuild after editing the script (`python3 tools/build.py` first), run:

```bash
python3 render/make.py            # all three
python3 render/make.py kmr        # one language
python3 render/reel.py ar --preview 5 30 90   # contact sheet of a few moments, in build/
```

- `render/reel.py`: picture. Reads `script/cards.<lang>.json` and follows section 4 of the prompts (styles A/B/C/S/E, tags, highlights, word-by-word animation, white flashes, credits, logo, safe zones, grade). Arabic-script text is shaped with libraqm.
- `render/sound.py`: original score following the chapter cues, plus the sound effects listed on the cards. Mastered to -14 LUFS.
- `render/assets.py`: footage crops from `footage/` (the screenshots of the HOKAR, Kurdistan24 and Hariri videos) and simple drawn shots for cards that have no footage.
- Fonts come from `../fonts/` (Speda, Montserrat, Aljazeera); logos from `../brand/`.

What differs from the prompt:
- Footage is **still frames** from the three videos (screenshots), not the video clips. Swap in the real clips for a richer edit.
- HOKAR's own speech-bubble caption (which names Fakhir Hariri and calls the cream fake as a fact) is cropped out, per editorial rule 2.
- Shots the prompt asks you to film yourself (lab, pharmacy, phone, receipt, complaint form, gavel) are simple drawn illustrations in the brand colours. The law cards (C13–C15) use a drawn document, not the real PDF, so they also carry the "illustrative" label.
- Brand fonts are the Regular weights, slightly emboldened, because only those files were supplied.
- Logo on dark backgrounds: the olive lettering is switched to cream (per `brand.json`: "cream text").
