"""Thumbnails, loudness pass (-14 LUFS, -1.5 dBTP), mux picture + sound, embed the thumbnail as cover.

  python3 -m oil.finish ckb 16x9
"""
import json
import re
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

from . import base as B
from .base import CREAM, GOLD, INK, PAPER, PROJ, kit, paste
from .render import SIZES

OUT = PROJ / "output"


def thumbnail(lang, fmt, path):
    W, H = SIZES[fmt]
    vert = H > W
    sj = json.loads((PROJ / "script" / "scenes.json").read_text(encoding="utf-8"))
    title = sj["title"][lang]
    big_num = [s for s in sj["scenes"] if s["id"] == "S06"][0]["ost"][lang][0]      # ≈ 160 کم²
    f = Image.new("RGBA", (W, H), INK + (255,))
    if vert:
        a = kit.cover(B.load("I01_oil_price_screen.jpg"), W, H // 2, 0.7, 0.4).convert("RGBA")
        b = kit.cover(B.load("I02_oil_on_sand_closeup.jpg"), W, H // 2, 0.5, 0.62).convert("RGBA")
        f.paste(a, (0, 0))
        f.paste(b, (0, H // 2))
        ImageDraw.Draw(f).rectangle([0, H // 2 - 3, W, H // 2 + 2], fill=CREAM + (255,))
    else:
        a = kit.cover(B.load("I01_oil_price_screen.jpg"), W // 2, H, 0.62, 0.45).convert("RGBA")
        b = kit.cover(B.load("I02_oil_on_sand_closeup.jpg"), W // 2, H, 0.5, 0.6).convert("RGBA")
        f.paste(a, (0, 0))
        f.paste(b, (W // 2, 0))
        ImageDraw.Draw(f).rectangle([W // 2 - 3, 0, W // 2 + 2, H], fill=CREAM + (255,))
    f = B.darken(f, 0.8)
    # title card: two lines, large
    words = title.split(" ")
    best = min(range(1, len(words)), key=lambda i: abs(len(" ".join(words[:i])) - len(" ".join(words[i:]))))
    lines = [" ".join(words[:best]), " ".join(words[best:])]
    size = 118 if vert else 128
    maxw = W - (130 if vert else 520)
    ims = [B.fit_w(B.T(lang, s, size, INK, True, 2), maxw) for s in lines]
    lh = int(ims[0].height * 0.8)
    cw = max(i.width for i in ims) + 100
    ch = lh * len(ims) + 80
    card = Image.new("RGBA", (cw, ch), PAPER + (255,))
    for j, li in enumerate(ims):
        card.alpha_composite(li, ((cw - li.width) // 2, int(40 + j * lh - li.height * 0.1)))
    ImageDraw.Draw(card).rectangle([0, ch - 16, cw, ch], fill=GOLD + (255,))
    from .scenes import shadowed
    card = shadowed(card, 16, (12, 16), 130)
    cy = H / 2 - (40 if not vert else 60)
    paste(f, card, W / 2 - card.width / 2, cy - card.height / 2)
    num = B.strip_img(lang, big_num, 92 if not vert else 84, INK, GOLD, pad=(34, 12), rot=-2)
    paste(f, num, W / 2 - num.width / 2, cy + card.height / 2 - 30)
    lg = kit.logo(lang, True, 120 if not vert else 110, 1.0)
    paste(f, lg, 46, 40 if not vert else 300)
    pill = kit.pill(kit.Lang(lang, "rtl" if lang == "ckb" else "ltr"), sj["label_illustration"][lang], 26,
                    fill=(22, 20, 18), fg=CREAM)
    paste(f, pill, W - 40 - pill.width, (H - 40 - pill.height) if not vert else 300, 0.75)
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
    print(r.stderr[-600:])


def main(lang, fmt):
    b = PROJ / "build" / lang
    OUT.mkdir(exist_ok=True)
    thumb = OUT / f"dwin_oil_spill_{lang}_{fmt}_thumbnail.jpg"
    thumbnail(lang, fmt, thumb)
    aac = b / "audio" / "mix.m4a"
    if not aac.exists() or aac.stat().st_mtime < (b / "audio" / "mix.wav").stat().st_mtime:
        loudnorm(b / "audio" / "mix.wav", aac)
    vd = b / f"video_{fmt}"
    tmp = vd / "muxed.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(vd / "picture.mp4"), "-i", str(aac), "-map", "0:v",
                    "-map", "1:a", "-c:v", "libx264", "-preset", "faster", "-crf", "21", "-maxrate", "8M", "-bufsize",
                    "16M", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(tmp)],
                   check=True)
    final = OUT / f"dwin_oil_spill_{lang}_{fmt}_v01.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(tmp), "-i", str(thumb), "-map", "0", "-map", "1", "-c", "copy",
                    "-c:v:1", "mjpeg", "-disposition:v:1", "attached_pic", "-movflags", "+faststart", str(final)],
                   check=True)
    shutil.copy(b / f"{lang}_synced.srt", OUT / f"dwin_oil_spill_{lang}.srt")
    print(final)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
