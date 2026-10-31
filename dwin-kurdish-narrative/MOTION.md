# MOTION.md: moving shots made from stills (free, open source, no paid video AI)

Tools: `ffmpeg`, `rembg` (github.com/danielgatis/rembg), Depth Anything V2 Small (github.com/DepthAnything/Depth-Anything-V2, via `transformers`), `opencv-python`, `numpy`.
If the depth model can't download, fall back to 2 layers: the rembg foreground plus a slightly blurred background, with the two layers moving at different speeds.

| ID | Still | Motion (6–8 s, 24 fps, 1920×1080, plus a 1080×1920 reframe) |
|---|---|---|
| M1 | A01_zagros_mountains_mist.jpg | 2.5D parallax from the depth map. The far ridges move 1%, the near ridges 4%. Add an animated mist layer (a soft noise texture drifting 2% per second, 25% opacity). In S01 the grade is cold blue; in S37 the same move is graded golden (the match cut). |
| M2 | A02_old_book_pages_wind.jpg | Slow push-in from 1.00 to 1.08. Add a gentle page-flutter warp on the top-right page area (sine displacement, 3 px, 1.5 s period) and floating dust particles. |
| M3 | A07_two_doors_corridor.jpg | A dolly toward the warm door: zoom 1.00→1.15 with the anchor on the right door (mirror it for RTL only if the image is mirrored), plus a light-leak flicker of ±5% from the warm door. |
| M4 | A08_group_walking_dusk.jpg | The rembg group layer moves 1.5% upward and scales 1.00→1.04 (walking away from camera); the background zooms 1.00→1.02, and the sky gets a slow gradient shift. In S38 the title sits between the background and the group layer. |

Every other still gets a Ken Burns move (1.00→1.05, alternating direction per scene), 8% paper grain and a soft vignette. Archival photos (R06, R08, R17, R20) also get film grain, a 1 px gate weave and a sepia tint.
