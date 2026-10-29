# MOTION.md — moving clips made from stills (free and open source; no video-AI service)

Claude Code builds every moving shot from the ChatGPT stills using free, open-source tools from GitHub and PyPI.

## Tools
- `ffmpeg` for zoom, pan, grain and export.
- `rembg` (github.com/danielgatis/rembg) to cut the person or foreground out of the background.
- Depth Anything V2 Small (github.com/DepthAnything/Depth-Anything-V2, via `pip install transformers torch`) to make a depth map for 2.5D parallax.
- `opencv-python` and `numpy` to displace layers per frame by depth.
- If the depth model can't download, fall back to 2 layers (rembg foreground plus a slightly blurred background), with the layers moving at different speeds.

## The four shots (each 6–8 s, 24 fps, 1920×1080, plus a 1080×1920 reframe)
| ID | Source still | Motion |
|---|---|---|
| M1 | A01_rooftop_from_behind.jpg | 2.5D dolly-in: background zooms 1.00→1.06, the person (rembg layer) zooms 1.00→1.12, warm light leak drifting across. Used in S01 and S32. In S32 the title sits between the background and the person layer. |
| M2 | A11_jazira_olive_wheat_landscape.jpg | Slow lateral pan 3% plus depth parallax. Animate "wind" with a gentle sine displacement on the bottom 40% (wheat) only, at amplitude 2–3 px and period 2 s. |
| M3 | A05_phone_in_hands_music.jpg | Slow push-in 1.00→1.08, a screen-glow flicker (brightness ±4% on the screen area), then the echo effect in S13: 3 offset copies at 30% opacity. |
| M4 | A09_crossroads_paths.jpg | Fake drone rise: zoom out 1.15→1.00 with a slight 1° rotation; then light each path with a soft saffron glow mask (path 1 in S27, 2 in S28, 3 in S29). |

## Every other still
Ken Burns (zoom 1.00→1.05 over the scene length, alternating direction per scene), 8% paper grain, and a soft vignette. Archival-look scenes (S08) get film grain plus a 1-px frame jitter.

## Optional (only if you want real AI motion later)
Free tiers that need no install, with daily credits: Kling AI, Hailuo (MiniMax), Pika and Google Gemini/Veo. Upload the same still and use image-to-video with the M1–M4 motion text as the prompt. Name the outputs `AV01_*.mp4`…`AV04_*.mp4`, and Claude Code will prefer them over M1–M4.
