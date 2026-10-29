"""Loudness pass (-14 LUFS, TP <= -1.2 via iterative loudnorm, AAC 256k), mux picture + sound, cover thumbnail, SRT.

  python3 -m ky.finish ar 16x9
"""
import shutil
import subprocess
import sys

from .base import PROJ
from vox.finish import loudnorm

OUT = PROJ / "output"


def main(lang, fmt):
    b = PROJ / "build" / lang
    OUT.mkdir(exist_ok=True)
    aac = b / "audio" / "mix.m4a"
    if not aac.exists() or aac.stat().st_mtime < (b / "audio" / "mix.wav").stat().st_mtime:
        loudnorm(b / "audio" / "mix.wav", aac)
    vd = b / f"video_{fmt}"
    tmp = vd / "muxed.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(vd / "picture.mp4"), "-i", str(aac), "-map", "0:v",
                    "-map", "1:a", "-c:v", "libx264", "-preset", "faster", "-crf", "20", "-maxrate", "9M", "-bufsize",
                    "18M", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(tmp)], check=True)
    thumb = PROJ / "thumbnails" / f"thumb_{lang}_{fmt}.jpg"
    final = OUT / f"dwin_kurdish_youth_{lang}_{fmt}_v01.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(tmp), "-i", str(thumb), "-map", "0", "-map", "1", "-c", "copy",
                    "-c:v:1", "mjpeg", "-disposition:v:1", "attached_pic", "-movflags", "+faststart", str(final)],
                   check=True)
    shutil.copy(b / f"{lang}_synced.srt", OUT / f"dwin_kurdish_youth_{lang}.srt")
    print(final)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
