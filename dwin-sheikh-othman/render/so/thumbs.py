"""YouTube thumbnails per THUMBNAILS.md ("The scholar and the name behind him"), plus the A/B alternative.

    python3 -m so.thumbs            -> thumbnails/thumb_{ar,ckb}_{16x9,9x16}.png (+ _alt)
P01a cut out with rembg (no change to the face), the title partly behind his shoulder, a gold name tag,
1922-1999 in thin gold, the hujra (A02) darkened to 45% and softly blurred, the logo top-left.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import base as B
from .base import CREAM, GOLD, INK, PROJ, T, kit, paste

TITLE = {"ar": "عالِمُ الحُجرة", "ckb": "زانای حوجرە"}
ALT = {"ar": "لم أرَ دولارًا في بيتي", "ckb": "دۆلارم لە ماڵەکەمدا نەبینی"}
NAME = {"ar": "الملا عثمان عبد العزيز", "ckb": "مامۆستا مەلا عوسمان عەبدولعەزیز"}
PORTRAIT = "P01a_sheikh_portrait.jpg"


def person():
    im = B.load(PORTRAIT)
    m = B.mask(PORTRAIT).resize(im.size, Image.LANCZOS)
    m = m.point(lambda v: 0 if v < 70 else (255 if v > 150 else int((v - 70) * 255 / 80))).filter(ImageFilter.GaussianBlur(1.2))
    im = kit.grade(im, sat=0.96, tint=(1.05, 1.0, 0.92))       # warm, dignified; no effect on the face shape
    lay = im.convert("RGBA")
    lay.putalpha(m)
    return lay.crop(lay.getbbox())


def background(W, H):
    bg = kit.cover(B.load("A02_hujra_interior_lamp.jpg"), W, H, 0.4, 0.5).filter(ImageFilter.GaussianBlur(5))
    bg = bg.convert("RGBA")
    return B.darken(B.vignette(bg, 0.6), 0.45)


def text(lang, s, size, colour, maxw):
    lines = B.text_lines(lang, s, size, maxw, colour)
    return B.stack(lines, 0.06, "center")


def shadow(im, r=14, a=170):
    return B.shadowed(im, r, (0, 6), a)


def make(lang, fmt, alt=False):
    W, H = (1920, 1080) if fmt == "16x9" else (1080, 1920)
    f = background(W, H)
    p = person()
    title = ALT[lang] if alt else TITLE[lang]
    if fmt == "16x9":
        ph = int(H * 1.02)
        p = p.resize((int(p.width * ph / p.height), ph), Image.LANCZOS)
        px, py = int(W * 0.30 - p.width / 2), H - ph + 20
        ti = shadow(text(lang, title, 200 if not alt else (132 if lang == "ar" else 112), CREAM, int(W * 0.56)))
        tx, ty = W * (0.675 if not alt else 0.70) - ti.width / 2, H * 0.47 - ti.height / 2
        paste(f, ti, tx, ty)
        f.alpha_composite(p, (px, py))                         # person over the letters (text behind him)
        tag = B.pill(lang, NAME[lang], 56, GOLD, INK)
        tgx, tgy = W * 0.675 - tag.width / 2, ty + ti.height - 10
        paste(f, shadow(tag, 8, 120), tgx - 24, tgy - 24)
        yr = T(lang, "1922–1999", 46, GOLD, False)
        paste(f, yr, W * 0.675 - yr.width / 2, tgy + tag.height + 22)
        lg = kit.logo(lang, True, 120, 1.0)
        paste(f, lg, 40, 36)
    else:
        ph = int(H * 0.44)
        p = p.resize((int(p.width * ph / p.height), ph), Image.LANCZOS)
        if p.width > W:
            p = p.crop(((p.width - W) // 2, 0, (p.width - W) // 2 + W, p.height))
        px, py = int(W / 2 - p.width / 2) - 30, int(H * 0.11)
        fade = np.ones(p.height, np.float32)
        n = int(p.height * 0.16)
        fade[-n:] = np.linspace(1, 0, n)
        a = (np.asarray(p.split()[3]).astype(np.float32) * fade[:, None]).astype(np.uint8)
        p.putalpha(Image.fromarray(a))
        cx = 70 + 430
        ti = shadow(text(lang, title, 170 if not alt else 118, CREAM, 860))
        ty = py + ph - ti.height * 0.30
        paste(f, ti, cx - ti.width / 2, ty)
        # the shoulders overlap the top of the title
        f.alpha_composite(p, (px, py))
        tag = B.fit_w(B.pill(lang, NAME[lang], 54, GOLD, INK), 860)
        tgy = ty + ti.height + 4
        paste(f, shadow(tag, 8, 120), cx - tag.width / 2 - 24, tgy - 24)
        yr = T(lang, "1922–1999", 46, GOLD, False)
        paste(f, yr, cx - yr.width / 2, tgy + tag.height + 22)
        lg = kit.logo(lang, True, 130, 1.0)
        paste(f, lg, 40, 160)
        assert tgy + tag.height + 22 + yr.height < H - 320, "text must stay above the bottom 320 px"
    out = PROJ / "thumbnails"
    out.mkdir(exist_ok=True)
    img = f.convert("RGB")
    if fmt == "16x9":
        img = img.resize((1280, 720), Image.LANCZOS)
    path = out / f"thumb_{lang}_{fmt}{'_alt' if alt else ''}_v02.png"
    img.save(path, optimize=True)
    if path.stat().st_size > 2_000_000:
        img.save(path.with_suffix(".jpg"), quality=90)
        path.unlink()
        path = path.with_suffix(".jpg")
    prev = img.copy()
    prev.thumbnail((160, 160 * img.height // img.width))
    prev.save(PROJ / "build" / f"preview_{lang}_{fmt}{'_alt' if alt else ''}.png")
    print(path, path.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    import sys
    langs = sys.argv[1:] or ["ar", "ckb"]
    for lang in langs:
        for fmt in ("16x9", "9x16"):
            make(lang, fmt)
            make(lang, fmt, alt=True)
