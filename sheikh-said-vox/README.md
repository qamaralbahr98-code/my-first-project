# Dwin documentary: Sheikh Said Piran (1865–1925), Vox style

A narrated, Vox-style explainer documentary for Dwin in three languages (Kurdish Sorani, Kurdish Kurmanji, Arabic), based on a Sorani article about Sheikh Said Piran, checked and extended with external historical sources.

The prompts are in English. Only the narration and the on-screen text are in Sorani, Kurmanji or Arabic.

| Language | Prompt | Narration | Subtitles | Timed data | Est. length |
| --- | --- | --- | --- | --- | --- |
| Kurdish Sorani | `prompts/01_sorani.md` | `vo/ckb_narration.txt` | `subtitles/ckb.srt` | `script/scenes.ckb.json` | ~11 min |
| Kurdish Kurmanji | `prompts/02_kurmanji.md` | `vo/kmr_narration.txt` | `subtitles/kmr.srt` | `script/scenes.kmr.json` | ~12 min |
| Arabic | `prompts/03_arabic.md` | `vo/ar_narration.txt` | `subtitles/ar.srt` | `script/scenes.ar.json` | ~10 min |

Lengths are estimates from word counts; the recorded narration decides the final length.

## Story (13 chapters, 54 scenes)
1. **Cold open:** Amed, dawn, 29 June 1925; his words "I never regret what I did for the sake of God".
2. **The scholar of Palu:** birth (1865 / 1281 AH), Naqshbandi family, Khinis, father and mother.
3. **Kurds and the ummah:** Salahuddin and Jerusalem; Kurds beside Turks from Gallipoli to the War of Independence; the Sèvres promise.
4. **The broken promise:** Lausanne; abolition of the Caliphate; one-nation constitution; Kurdish banned; deportations; land seizure and famine; trade cut and taxes.
5. **The secret plan:** Azadi; Yusuf Ziya; the Palu meeting; Sheikh Mahmud Hafid and Simko Shikak; League of Nations memo; Ali Riza to Amed and Aleppo; 21 March (Newroz) chosen; the January tour; 5 February to Piran.
6. **Piran, the spark:** the detachment; the clash; Lice taken; an early start; martial law and İsmet Pasha.
7. **The siege of Amed:** the numbers (with honest labels); the communities; the commanders; the negotiation; the Mardin Gate; the siege lifted.
8. **Betrayal:** armies from north and south; capture on the Murat bridge through Qasim Beg Jibran's betrayal.
9. **In prison:** the dialogue with the officers and İsmet Pasha: "I am a Kurd…".
10. **The last journey:** the trial; 29 June 1925; villages burned; Said Nursi exiled.
11. **Words that remain:** his sayings.
12. **One ummah:** from Salahuddin to Sheikh Said; the Kurdistan Region hosting 1.8 million displaced people; Qur'an 49:13.
13. **Dwin's position and close:** a labelled condemnation of propaganda that misleads people and sets Muslim against Muslim; end card. **No sources slide.**

## Accuracy notes (details in `facts/fact_check.md`)
- Every fact in the article is in the script.
- The article's "200 thousand horsemen" (Lice) is left out as not credible.
- The article's "600,000 vs 100,000" is shown as "a statistic of the time", followed by historians' estimate (~10,000 fighters at Amed).
- Where sources disagree on exact days (the Piran clash, the capture), the script avoids exact dates.
- To confirm before publishing: the name of Sheikh Said's brother at Lice ("شێخ تایەر" in the article), and the licences of the images you use.

## Assets
`assets/ASSETS.md` lists every image and footage item, and the image pack in `assets/images/` (40 files: your 34 images, cleaned and upscaled, plus 6 redrawn calendar graphics) with the scene each one belongs to, its on-screen label and any problem to fix first.

## Editing with Claude Code
Edit only `script/master.json` (content) and `script/brand.json` (colours, fonts), then run:

```bash
python3 tools/build.py
```

The build checks every scene (three languages present, facts and assets linked, opinion only in the labelled card) and regenerates the prompts, narration scripts, subtitles, asset list and fact check.

Example requests for Claude Code:
- "Render the Arabic chapter cards and quote cards as 1920×1080 PNGs from `script/scenes.ar.json`."
- "Build an animated map for chapter 5 (Khinis → Piran → Lice) in the Vox paper style."
- "Shorten the Kurmanji narration of S31 to under 25 words, then rebuild."

## Put it on GitHub
```bash
git init -b main && git add . && git commit -m "Initial commit"
git remote add origin https://github.com/<your-account>/dwin-sheikh-said-vox.git
git push -u origin main
```
