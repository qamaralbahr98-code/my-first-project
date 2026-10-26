"""Thumbnail, loudness pass (-14 LUFS, -1.5 dBTP), mux picture + sound, embed the thumbnail as cover.

  python3 -m vox.finish ar
"""
import json
import re
import shutil
import subprocess
from pathlib import Path
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
    if strip.width > room + 20:
        strip = strip.resize((int(room + 20), int(strip.height * (room + 20) / strip.width)), Image.LANCZOS)
    paste(f, strip, (x - strip.width + 20) if L.rtl else x - 20, 660)
    paste(f, kit.logo(lang, False, 150, 1.0), W - 190 if L.rtl else 40, 36)    # the portrait takes the other corner
    f.convert("RGB").save(path, quality=93)
    return path


def measure(path):
    """(integrated LUFS, true peak dBTP) of the audio of a file, measured after decoding."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-map", "0:a", "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    i = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r)[-1])
    tp = float(re.findall(r"True peak:\s+Peak:\s+(-?[\d.]+|-inf) dBFS", r)[-1])
    return i, tp


def loudnorm(src, dst, target=-14.0, max_tp=-1.2):
    """Two-pass loudnorm to -14 LUFS (to a WAV), then gain + peak limiter, encoded to AAC and measured again;
    gain and limiter ceiling are adjusted until the encoded file is within 0.2 LU of -14 and its true peak is at or
    under max_tp (AAC can overshoot a few transients by 1-2 dB)."""
    a = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af",
                        "loudnorm=I=-14:TP=-2:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", a, re.S).group(0))
    norm = ("loudnorm=I=-14:TP=-2:LRA=11:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:"
            "measured_thresh={input_thresh}:offset={target_offset}:linear=true:print_format=summary").format(**m)
    mid = Path(dst).with_suffix(".norm.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-af", norm + ",aresample=48000", "-c:a", "pcm_f32le",
                    str(mid)], check=True)
    gain, ceiling = 0.0, -2.5
    for k in range(6):
        af = f"volume={gain:.2f}dB,alimiter=limit={10 ** (ceiling / 20):.4f}:attack=1:release=50:level=disabled"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mid), "-af", af, "-ar", "48000", "-c:a", "aac",
                        "-b:a", "192k", str(dst)], check=True)
        i, tp = measure(dst)
        print(f"gain {gain:+.2f} dB, ceiling {ceiling:.1f} dBFS -> {i:.2f} LUFS, {tp:.2f} dBTP")
        ok_i, ok_tp = abs(i - target) <= 0.2, tp <= max_tp
        if ok_i and ok_tp:
            break
        if not ok_tp:
            ceiling -= (tp - max_tp) + 0.3
        if not ok_i:
            gain += target - i
    mid.unlink()


def remux_audio(lang):
    """Replace only the sound of a finished video (keeps the encoded picture), then re-embed the cover."""
    b = PROJ / "build" / lang
    aac = b / "audio" / "mix.m4a"
    loudnorm(b / "audio" / "mix.wav", aac)
    final = OUT / f"dwin_sheikh_said_{lang}_16x9_v01.mp4"
    thumb = OUT / f"dwin_sheikh_said_{lang}_thumbnail.jpg"
    tmp = b / "video" / "remux.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(b / "video" / "muxed.mp4"), "-i", str(aac), "-map", "0:v:0",
                    "-map", "1:a", "-c", "copy", "-shortest", "-movflags", "+faststart", str(tmp)], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(tmp), "-i", str(thumb), "-map", "0", "-map", "1", "-c", "copy",
                    "-c:v:1", "mjpeg", "-disposition:v:1", "attached_pic", "-movflags", "+faststart", str(final)], check=True)
    tmp.unlink()
    print(final, "%.2f LUFS, %.2f dBTP" % measure(final))


def main(lang):
    b = PROJ / "build" / lang
    OUT.mkdir(exist_ok=True)
    thumb = OUT / f"dwin_sheikh_said_{lang}_thumbnail.jpg"
    thumbnail(lang, thumb)
    aac = b / "audio" / "mix.m4a"
    loudnorm(b / "audio" / "mix.wav", aac)
    tmp = b / "video" / "muxed.mp4"
    # the master parts are near-lossless (~18 Mbit/s with grain); the delivery file is capped at 6 Mbit/s
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(b / "video" / "picture.mp4"), "-i", str(aac), "-map", "0:v",
                    "-map", "1:a", "-c:v", "libx264", "-preset", "faster", "-crf", "22", "-maxrate", "6M", "-bufsize",
                    "12M", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(tmp)],
                   check=True)
    final = OUT / f"dwin_sheikh_said_{lang}_16x9_v01.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(tmp), "-i", str(thumb), "-map", "0", "-map", "1", "-c", "copy",
                    "-c:v:1", "mjpeg", "-disposition:v:1", "attached_pic", "-movflags", "+faststart", str(final)], check=True)
    shutil.copy(b / f"{lang}_synced.srt", OUT / f"dwin_sheikh_said_{lang}.srt")
    print(final)


if __name__ == "__main__":
    if "--remux-audio" in sys.argv:
        remux_audio(sys.argv[1])
    else:
        main(sys.argv[1])
