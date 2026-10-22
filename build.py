"""Build the al-Izz ibn Abd al-Salam documentary videos.

    python3 build.py                 # all three languages
    python3 build.py arabic sorani   # just some
    python3 build.py --redraw        # force re-render of the shared picture track

Outputs go to ./output/: one MP4 per language (1920x1080, 24 fps, 60 s, music + captions)
and a title thumbnail per language.
"""
import subprocess
import sys
from pathlib import Path

from izz_video import music
from izz_video.captions import LANGS, parse_script, parse_titles, card_times, render_card, render_title
from izz_video.render import render_picture, frame_at
from izz_video.scenes import TOTAL

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
BUILD = ROOT / "build"
OUT = ROOT / "output"
FADE = 0.35


def build_language(key, picture, audio):
    script_file, _, _, _, label = LANGS[key]
    cards_dir = BUILD / "cards"
    cards_dir.mkdir(parents=True, exist_ok=True)
    cards = []
    for i, scene in enumerate(parse_script(SCRIPTS / script_file)):
        for j, (text, (t0, t1)) in enumerate(zip(scene["cards"], card_times(scene, TOTAL))):
            png = cards_dir / f"{key}_{i}_{j}.png"
            render_card(text, key, png)
            cards.append((png, t0, t1))

    inputs = ["-i", str(picture), "-i", str(audio)]
    chain, prev = [], "0:v"
    for k, (png, t0, t1) in enumerate(cards):
        d = t1 - t0
        inputs += ["-loop", "1", "-framerate", "24", "-t", f"{d:.3f}", "-i", str(png)]
        idx = k + 2
        chain.append(f"[{idx}:v]format=rgba,fade=t=in:st=0:d={FADE}:alpha=1,"
                     f"fade=t=out:st={d - FADE:.3f}:d={FADE}:alpha=1,setpts=PTS-STARTPTS+{t0:.3f}/TB[c{k}]")
        chain.append(f"[{prev}][c{k}]overlay=0:0:eof_action=pass[v{k}]")
        prev = f"v{k}"
    out = OUT / f"Izz_ibn_Abd_al-Salam_{label}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(chain),
           "-map", f"[{prev}]", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "26",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", str(TOTAL),
           "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    return out


def main(args):
    redraw = "--redraw" in args
    keys = [a for a in args if not a.startswith("--")] or list(LANGS)
    BUILD.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)

    wav = BUILD / "music.wav"
    music.render(wav)
    audio = BUILD / "music.m4a"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar", "48000", "-c:a", "aac", "-b:a", "192k", str(audio)], check=True)

    picture = BUILD / "picture.mp4"
    if redraw or not picture.exists():
        print("Rendering picture track (a few minutes)...")
        render_picture(picture)

    titles = parse_titles(SCRIPTS / "00_title_and_style.txt")
    thumb_frame = frame_at(53.0)
    for key in keys:
        out = build_language(key, picture, audio)
        render_title(titles[key], key, thumb_frame, OUT / f"Izz_ibn_Abd_al-Salam_{LANGS[key][4]}_thumbnail.jpg")
        print("Wrote", out)


if __name__ == "__main__":
    main(sys.argv[1:])
