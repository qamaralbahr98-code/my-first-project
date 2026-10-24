"""Thumbnail, loudness pass (-14 LUFS, -1.5 dBTP), mux picture + sound, embed the thumbnail as cover.

  python3 -m vox.finish ar
"""
import json
import re
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

from . import kit
from .kit import CREAM, GOLD, INK, RED, W, H, paste
from .shots import img

PROJ = kit.PROJ
OUT = PROJ / "output"


def thumbnail(lang, path):
    tl = json.loads((PROJ / "build" / lang / "timeline.json").read_text(encoding="utf-8"))
    ost = {s["id"]: s["ost"] for s in tl["scenes"]}
    sj = json.loads((PROJ / "script" / f"scenes.{lang}.json").read_text(encoding="utf-8"))
    L = kit.Lang(lang, sj["direction"])
    f = kit.paper(W, H, seed=77).copy()
    por = kit.cutout(kit.fit(kit.sepia(img("Sheikh_Said_Archival_Sepia_Portrait.jpg"), 0.85), h=900), torn=True, seed=5)
    px = 70 if L.rtl else W - 70 - por.width
    paste(f, por, px, (H - por.height) / 2 + 10)
    d = ImageDraw.Draw(f, "RGBA")
    name, years, tag = ost["S03"]
    x = W - 90 if L.rtl else 90
    room = W - 90 - (px + por.width + 50 if L.rtl else W - px + 50)
    big = kit.line_img(L.key, L.dir, name, 150, INK, 4)[0]
    if big.width > room:
        big = big.resize((int(room), int(big.height * room / big.width)), Image.LANCZOS)
    bx = x - big.width if L.rtl else x
    paste(f, big, bx, 250)
    kit.ink_line(d, kit.resample(kit.wobble_line([(bx + 10, 250 + big.height * 0.9), (bx + big.width - 10, 250 + big.height * 0.92)], 3), 6), 1, RED, 9)
    yrs = kit.line_img(L.key, L.dir, years, 96, GOLD, 3)[0]
    paste(f, yrs, x - yrs.width if L.rtl else x, 470)
    strip = kit.label_strip(L, tag, 74, CREAM, RED, pad=(34, 14), rot=-2)
    paste(f, strip, (x - strip.width + 20) if L.rtl else x - 20, 660)
    paste(f, kit.logo(lang, False, 150, 1.0), W - 190 if L.rtl else 40, 36)    # the portrait takes the other corner
    f.convert("RGB").save(path, quality=93)
    return path


def loudnorm(src, dst):
    a = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", a, re.S).group(0))
    af = ("loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:"
          "measured_thresh={input_thresh}:offset={target_offset}:linear=true:print_format=summary").format(**m)
    r = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-i", str(src), "-af", af, "-ar", "48000", "-c:a", "aac",
                        "-b:a", "192k", str(dst)], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr[-2000:])
    print(r.stderr[-700:])


def main(lang):
    b = PROJ / "build" / lang
    OUT.mkdir(exist_ok=True)
    thumb = OUT / f"dwin_sheikh_said_{lang}_thumbnail.jpg"
    thumbnail(lang, thumb)
    aac = b / "audio" / "mix.m4a"
    loudnorm(b / "audio" / "mix.wav", aac)
    tmp = b / "video" / "muxed.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(b / "video" / "picture.mp4"), "-i", str(aac), "-map", "0:v",
                    "-map", "1:a", "-c", "copy", "-shortest", "-movflags", "+faststart", str(tmp)], check=True)
    final = OUT / f"dwin_sheikh_said_{lang}_16x9_v01.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(tmp), "-i", str(thumb), "-map", "0", "-map", "1", "-c", "copy",
                    "-c:v:1", "mjpeg", "-disposition:v:1", "attached_pic", "-movflags", "+faststart", str(final)], check=True)
    shutil.copy(b / f"{lang}_synced.srt", OUT / f"dwin_sheikh_said_{lang}.srt")
    print(final)


if __name__ == "__main__":
    main(sys.argv[1])
