# MOTION.md: moving shots from stills (free, open source, no video AI)

Tools: `ffmpeg`, `rembg`, Depth Anything V2 Small (via `transformers`), `opencv-python`, `numpy`. If the depth model can't download, fall back to 2 layers: the rembg foreground plus a blurred background.

| ID | Still | Motion (6–8 s, 24 fps; also reframe to 1080×1920) |
|---|---|---|
| M1 | A01_mud_house_by_mosque.jpg | 2.5D push-in 1.00→1.08 toward the warm window. The window light breathes ±4%. The sky darkens slightly over the shot. |
| M2 | A02_hujra_interior_lamp.jpg | Slow lateral dolly (3%) with depth parallax. The oil-lamp flame flickers (a brightness and warp mask on the flame area), with dust particles in the light. |
| M3 | A10_mountain_pass_migration.jpg | Slow pull-out 1.10→1.00, with a mist layer drifting across. The line of people moves upward by 0.5% (a subtle walk). |
| M4 | A15_night_train_prayer_rug.jpg | Static camera with a gentle train sway (±0.4° rotation at 1.2 s), light streaks sliding across the window, and a soft rail sound. |

Portrait photos (people): 2.5D parallax. Cut the person out with rembg, move the background 1% and the person 2.5%, and enlarge them slightly. Never warp faces, never use AI face restoration on the sheikh's photos, and never animate mouths or eyes.

Every other still gets a Ken Burns move (1.00→1.05), paper grain and a vignette. Photos from before 1991 also get sepia, film grain and a 1 px gate weave.
