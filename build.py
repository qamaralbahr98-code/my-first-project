"""Build the al-Izz ibn Abd al-Salam documentary videos.

    python3 build.py                 # all three languages
    python3 build.py arabic sorani   # just some
    python3 build.py --redraw        # force re-render of the shared picture track

Outputs go to ./output/: one MP4 per language (1920x1080, 24 fps: thumbnail opening, 60 s film, 6 s Dwin end card,
music + captions, Dwin logo top-left, thumbnail embedded as cover) and a branded thumbnail per language.
Brand assets live in ./brand (logos, portrait, medallion) and ./fonts (Aljazeera, Speda, Montserrat).

Narration: put a recording of the whole script in ./narration/ named arabic.*, sorani.* or
kurmanji.* (mp3, m4a, wav...), read with a clear pause between scenes. It is cut at those
pauses, each part is placed at its scene, the music is lowered under the voice, and the
captions follow the voice. Languages without a narration file keep music only.
"""
import subprocess
import sys
from pathlib import Path

from izz_video import music
from izz_video.captions import LANGS, parse_script, parse_titles, card_times, render_card
from izz_video.brand import corner_badge, end_card, thumbnail
from izz_video.render import render_picture, frame_at
from izz_video.scenes import TOTAL
from izz_video.narration import build_voice_track, mix

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
BUILD = ROOT / "build"
OUT = ROOT / "output"
FADE = 0.35
END = 6.0          # seconds of Dwin end card after the film
INTRO = 2.2        # seconds the thumbnail is shown at the start (dissolving into the film)
XF = 0.8           # length of that dissolve


def find_narration(key):
    folder = ROOT / "narration"
    hits = sorted(folder.glob(f"{key}.*")) if folder.exists() else []
    return hits[0] if hits else None


def build_language(key, picture, audio, thumb):
    script_file, _, _, _, label = LANGS[key]
    cards_dir = BUILD / "cards"
    cards_dir.mkdir(parents=True, exist_ok=True)
    scenes = parse_script(SCRIPTS / script_file)
    narration = find_narration(key)
    if narration:
        timing = build_voice_track(narration, BUILD / f"voice_{key}.wav")
        audio = mix(audio, BUILD / f"voice_{key}.wav", BUILD / f"mix_{key}.m4a")
        for scene, tm in zip(scenes, timing):  # captions follow the spoken line
            scene["start"], scene["end"] = tm["start"] - 0.35, tm["end"] + 0.6
        print(f"  {label}: narration from {narration.name}")
    cards = []
    for i, scene in enumerate(scenes):
        for j, (text, (t0, t1)) in enumerate(zip(scene["cards"], card_times(scene, TOTAL))):
            png = cards_dir / f"{key}_{i}_{j}.png"
            render_card(text, key, png)
            cards.append((png, t0, t1))

    badge = corner_badge(key, BUILD / f"badge_{key}.png")
    card = end_card(key, BUILD / f"endcard_{key}.jpg")
    inputs = ["-i", str(picture), "-i", str(audio), "-i", str(BUILD / "outro.wav"),
              "-loop", "1", "-framerate", "24", "-t", str(END), "-i", str(card),
              "-loop", "1", "-framerate", "24", "-t", str(TOTAL), "-i", str(badge),
              "-loop", "1", "-framerate", "24", "-t", str(INTRO), "-i", str(thumb)]
    base = 6                                   # card PNG inputs start after these six
    chain, prev = [], "0:v"
    for k, (png, t0, t1) in enumerate(cards):
        d = t1 - t0
        inputs += ["-loop", "1", "-framerate", "24", "-t", f"{d:.3f}", "-i", str(png)]
        idx = k + base
        chain.append(f"[{idx}:v]format=rgba,fade=t=in:st=0:d={FADE}:alpha=1,"
                     f"fade=t=out:st={d - FADE:.3f}:d={FADE}:alpha=1,setpts=PTS-STARTPTS+{t0:.3f}/TB[c{k}]")
        chain.append(f"[{prev}][c{k}]overlay=0:0:eof_action=pass[v{k}]")
        prev = f"v{k}"
    # Dwin logo in the top-left corner for the whole film, fading with the picture
    chain.append(f"[4:v]format=rgba,fade=t=in:st=0.6:d=0.8:alpha=1,"
                 f"fade=t=out:st={TOTAL - 1.6:.2f}:d=1.4:alpha=1[logo]")
    chain.append(f"[{prev}][logo]overlay=0:0:eof_action=pass,trim=duration={TOTAL},setpts=PTS-STARTPTS,"
                 f"fps=24,format=yuv420p,setsar=1,settb=1/24[film]")
    # opening: the thumbnail, dissolving into the film (the film's sound starts with the dissolve)
    chain.append("[5:v]scale=1920:1080,fps=24,format=yuv420p,setsar=1,settb=1/24[intro]")
    chain.append(f"[intro][film]xfade=transition=fade:duration={XF}:offset={INTRO - XF}[opened]")
    # end card: fades up from black, holds, fades out
    chain.append(f"[3:v]fps=24,format=yuv420p,setsar=1,settb=1/24,fade=t=in:st=0:d=0.8,fade=t=out:st={END - 0.9}:d=0.9[end]")
    lead = int(round((INTRO - XF) * 1000))
    chain.append(f"[1:a]atrim=0:{TOTAL},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
                 f"adelay={lead}|{lead}[a1]")
    chain.append("[2:a]aformat=sample_rates=48000:channel_layouts=stereo[a2]")
    chain.append("[opened][a1][end][a2]concat=n=2:v=1:a=1[vout][aout]")
    out = OUT / f"Izz_ibn_Abd_al-Salam_{label}.mp4"
    body = BUILD / f"body_{key}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(chain),
           "-map", "[vout]", "-map", "[aout]", "-c:v", "libx264", "-preset", "slow", "-crf", "26",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(body)]
    subprocess.run(cmd, check=True)
    # second, quick pass: embed the thumbnail as the file's cover image (no re-encode)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(body), "-i", str(thumb),
                    "-map", "0", "-map", "1", "-c", "copy", "-disposition:v:1", "attached_pic",
                    "-movflags", "+faststart", str(out)], check=True)
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

    music.render_outro(BUILD / "outro.wav", END)
    titles = parse_titles(SCRIPTS / "00_title_and_style.txt")
    thumb_bg = frame_at(53.0)
    for key in keys:
        thumb = thumbnail(key, titles[key], thumb_bg, OUT / f"Izz_ibn_Abd_al-Salam_{LANGS[key][4]}_thumbnail.jpg")
        out = build_language(key, picture, audio, thumb)
        print("Wrote", out)


if __name__ == "__main__":
    main(sys.argv[1:])
