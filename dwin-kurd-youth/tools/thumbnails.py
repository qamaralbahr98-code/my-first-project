"""Concept A thumbnails ("text behind person"): YouTube 1280x720 + Shorts/Reels cover 1080x1920, ar/ckb/kmr.
    python3 tools/thumbnails.py      (needs thumbnails/A01_rooftop_from_behind_mask.png from rembg u2net_human_seg)
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
CREAM, SAFFRON, DARK = (239, 232, 220), (232, 163, 61), (17, 20, 24)
T = {
    "ar": dict(title="الانتماء", tag="الشباب الكرد في سوريا", font="Aljazeera.ttf", dir="rtl", lang="ar", logo="arabic"),
    "ckb": dict(title="پێوەبەستبوون", tag="گەنجانی کورد لە سووریا", font="Speda.ttf", dir="rtl", lang="ckb", logo="sorani"),
    "kmr": dict(title="AÎDBÛN", tag="Ciwanên Kurd li Sûriyeyê", font="Montserrat-Bold.ttf", dir="ltr", lang="ku", logo="kurmanji"),
}


def font(name, size):
    return ImageFont.truetype(str(REPO / "fonts" / name), size, layout_engine=ImageFont.Layout.RAQM)


def text_img(text, f, fill, d, lang, stroke=0):
    box = ImageDraw.Draw(Image.new("L", (8, 8))).textbbox((0, 0), text, font=f, direction=d, language=lang, stroke_width=stroke)
    im = Image.new("RGBA", (box[2] - box[0] + 40, box[3] - box[1] + 40), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((20 - box[0], 20 - box[1]), text, font=f, fill=fill, direction=d, language=lang,
                            stroke_width=stroke, stroke_fill=fill)
    return im


def shadowed(im, r=10, a=150):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(im.getchannel("A").point(lambda v: v * a // 255))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(r)), (0, 4))
    out.alpha_composite(im)
    return out


def logo(key, w):
    lg = Image.open(REPO / "brand" / f"logo_{key}.png").convert("RGBA")
    a = np.asarray(lg).astype(np.float32)
    olive = (a[..., 0] - a[..., 2]) < 32
    a[olive, :3] = CREAM
    a[~olive, :3] = (201, 164, 92)
    lg = Image.fromarray(a.astype(np.uint8), "RGBA")
    return lg.resize((w, int(lg.height * w / lg.width)), Image.LANCZOS)


def cover(im, W, H, fx, fy):
    s = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * s + 1), int(im.height * s + 1)), Image.LANCZOS)
    x = int(min(max(0, im.width * fx - W / 2), im.width - W))
    y = int(min(max(0, im.height * fy - H / 2), im.height - H))
    return im.crop((x, y, x + W, y + H))


def make(key, W, H):
    L = T[key]
    photo = Image.open(ROOT / "assets" / "A01_rooftop_from_behind.jpg").convert("RGB")
    mask = Image.open(ROOT / "thumbnails" / "A01_rooftop_from_behind_mask.png").convert("L")
    if L["dir"] == "ltr":                      # person on the side opposite the text
        photo, mask = photo.transpose(Image.FLIP_LEFT_RIGHT), mask.transpose(Image.FLIP_LEFT_RIGHT)
    vert = H > W
    fx = 0.5 if vert else 0.5
    fy = 0.55
    bg = cover(photo, W, H, fx, fy).convert("RGBA")
    m = cover(mask.convert("RGB"), W, H, fx, fy).convert("L").filter(ImageFilter.GaussianBlur(1))
    # darken slightly for contrast, more at the top
    a = np.asarray(bg).astype(np.float32)
    g = (1 - np.linspace(0.45, 0.0, H)[:, None, None])
    a[..., :3] *= g * 0.95
    bg = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    person = bg.copy()
    person.putalpha(m)
    # head top of the person -> title baseline a little below it so the head overlaps the letters
    ys = np.where(np.asarray(m) > 128)[0]
    head = int(ys.min()) if len(ys) else int(H * 0.4)
    f = ImageDraw.Draw(bg)
    year = text_img("1962", font("Montserrat-Bold.ttf", int(W * (0.36 if not vert else 0.42))), CREAM + (38,), "ltr", "en")
    bg.alpha_composite(year, ((W - year.width) // 2, int(H * (0.02 if not vert else 0.10))))
    size = int(W * (0.17 if not vert else 0.2))
    tf = font(L["font"], size)
    title = text_img(L["title"], tf, CREAM + (255,), L["dir"], L["lang"], 2)
    maxw = (W - 620 if L["dir"] == "rtl" else W - 230) if not vert else W - 80
    if title.width > maxw:
        title = title.resize((maxw, int(title.height * maxw / title.width)), Image.LANCZOS)
    title = shadowed(title, 12, 170)
    if vert:
        ty = max(int(H * 0.22), head - int(title.height * 0.82))
    else:
        ty = max(150, head + int(title.height * 0.55) - title.height)
    rtl = L["dir"] == "rtl"
    tx = (W - 50 - title.width) if (rtl and not vert) else (170 if not vert else (W - title.width) // 2)
    bg.alpha_composite(title, (tx, ty))
    bg.alpha_composite(person)                    # the person in front of the title
    # saffron tag above the title
    gf = font(L["font"], int(W * (0.032 if not vert else 0.05)))
    tag = text_img(L["tag"], gf, DARK + (255,), L["dir"], L["lang"])
    pill = Image.new("RGBA", (tag.width + 10, tag.height - 6), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle([0, 0, pill.width - 1, pill.height - 1], 12, fill=SAFFRON + (255,))
    pill.alpha_composite(tag, (5, -3))
    py = ty - pill.height + int(title.height * 0.12)
    px = (W - 60 - pill.width) if (rtl and not vert) else (185 if not vert else (W - pill.width) // 2)
    bg.alpha_composite(shadowed(pill, 6, 120), (px, py))
    lg = logo(L["logo"], int(W * (0.085 if not vert else 0.16)))
    bg.alpha_composite(lg, (int(W * 0.03), int(H * (0.04 if not vert else 0.08))))
    out = ROOT / "thumbnails" / f"thumb_{key}_{'9x16' if vert else '16x9'}.jpg"
    bg.convert("RGB").save(out, quality=92)
    return out


if __name__ == "__main__":
    for k in ("ar", "ckb", "kmr"):
        print(make(k, 1280, 720), make(k, 1080, 1920))
