# al-Izz ibn Abd al-Salam — Sultan of the Scholars

A 60-second illustrated documentary about al-Izz ibn Abd al-Salam (c. 1181–1262), generated entirely in code, in three languages:

| Version | Captions | Font |
|---|---|---|
| Arabic (Modern Standard) | right-to-left | Noto Naskh Arabic |
| Central Kurdish (Sorani) | right-to-left | Noto Sans Arabic |
| Northern Kurdish (Kurmanji, Latin) | left-to-right | Noto Sans |

Each version is 1920×1080, 24 fps, 60 seconds, with an original music score and timed lower-third captions. There is no narration.

## What's in the film

| Time | Scene | Picture |
|---|---|---|
| 0:00 | Hook | Dawn over Damascus, camera descending toward the Umayyad Mosque |
| 0:10 | Background | Candle-lit manuscript, then the scholar in silhouette on the minbar |
| 0:20 | Key fact 1 | Hilltop fortress at dusk, prison corridor, lone traveller heading south |
| 0:30 | Key fact 2 | Cairo and the Nile at golden hour, a courtroom, Mamluk emirs from behind |
| 0:40 | Impact | Chests of coins set on the council table, the army marching out at dawn |
| 0:50 | Closing | Sunset over Cairo's minarets, camera pulling back, fade to black |

Following the style notes, the scholar is only ever shown from behind or in silhouette. The imagery contains no text, and the only words on screen are the caption overlays.

The music is original, written in maqam Hijaz. A ney plays alone at the start, then an oud joins. Low strings bring tension, a frame drum sets the pulse, and the orchestra rises to a climax before a final soft ney.

## Project layout

```
scripts/            the original scripts (title, style notes, one file per language)
izz_video/
  scenes.py         the six scenes, drawn and animated shot by shot
  gfx.py            drawing helpers: gradients, glows, architecture, figures, camera, film grain
  music.py          the synthesised score
  captions.py       reads the scripts and draws the caption cards
  render.py         renders the shared picture track
build.py            builds everything into ./output/
```

The captions come straight from the `Card 1:` / `Card 2:` lines in `scripts/`. To change any wording, edit the script file and rebuild. Each scene's time is shared between its cards in proportion to their length.

## Building

Requirements: Python 3.10+, ffmpeg, and the Noto fonts (`fonts-noto-core` on Debian/Ubuntu).

```bash
pip install -r requirements.txt
python3 build.py                 # all three languages
python3 build.py kurmanji        # one language
python3 build.py --redraw        # re-render the picture after editing scenes.py
```

The picture track is shared by all languages and takes a few minutes to render. After that, each language takes well under a minute.

## Adding narration later

To add a voice-over, record each language as a 60-second audio file. Then mix it with `build/music.m4a` and swap it in as the audio input in `build_language()` in `build.py`, lowering the music under the voice.
