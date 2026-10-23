"""Dwin quote card (4:5, 1080x1350) with a round portrait, in Sorani, Kurmanji and Arabic.

    python3 news/quote_card.py news/bakkar-gaze
reads <folder>/photo.jpg and <folder>/texts.json ({lang: {name, paras: [...]}}), writes <folder>/dwin_<lang>.jpg
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_news import CREAM, GOLD, GREEN, H, LANG, W, font, logo, tw, wrap   # noqa: E402


def portrait(path, d):
    """Square crop around the face, made round, with a gold ring."""
    im = Image.open(path).convert("RGB")
    s = int(min(im.size) * 0.80)
    cx, cy = int(im.width * 0.56), int(im.height * 0.46)
    box = (max(0, cx - s // 2), max(0, cy - s // 2))
    im = im.crop((box[0], box[1], box[0] + s, box[1] + s)).resize((d, d), Image.LANCZOS)
    m = Image.new("L", (d * 4, d * 4), 0)
    ImageDraw.Draw(m).ellipse([0, 0, d * 4 - 1, d * 4 - 1], fill=255)
    m = m.resize((d, d), Image.LANCZOS)
    out = Image.new("RGBA", (d + 16, d + 16), (0, 0, 0, 0))
    ImageDraw.Draw(out).ellipse([0, 0, d + 15, d + 15], fill=GOLD + (255,))
    im = im.convert("RGBA")
    im.putalpha(m)
    out.alpha_composite(im, (8, 8))
    return out


def background():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.clip(1 - np.sqrt(((xx - W * 0.5) / 900) ** 2 + ((yy - 260) / 700) ** 2), 0, 1) ** 2
    base = np.array(GREEN, np.float32)
    light = np.array((30, 70, 52), np.float32)
    arr = base + (light - base) * g[..., None]
    return Image.fromarray(arr.astype(np.uint8)).convert("RGBA")


def card(folder, key, texts):
    L, T = LANG[key], texts[key]
    rtl = L["dir"] == "rtl"
    img = background()
    d = ImageDraw.Draw(img)
    k = L["k"]

    # logo top-left
    lg = logo(L["logo"], dark=True)
    lw = 140
    lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    img.alpha_composite(lg, (40, 40))

    # round portrait, centred, and the name under it
    pd = 300
    por = portrait(folder / "photo.jpg", pd)
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse([W / 2 - pd / 2 - 4, 74, W / 2 + pd / 2 + 20, 74 + pd + 24], fill=(0, 0, 0, 120))
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14)))
    img.alpha_composite(por, (int(W / 2 - por.width / 2), 60))
    nf = font(L["font"], int(52 * k))
    d.text((W / 2, 60 + por.height + 70), T["name"], font=nf, fill=GOLD, anchor="ms", direction=L["dir"],
           language=L["lang"], stroke_width=1, stroke_fill=GOLD)

    # quote: fit both paragraphs into the box, shrinking the size if needed
    margin = 80
    top, bottom = 60 + por.height + 120, H - 120
    maxw = W - 2 * margin
    size = int(42 * k)
    while True:
        f = font(L["font"], size)
        lh = int(size * (1.6 if rtl else 1.42))
        blocks = [wrap(p, f, L, maxw) for p in T["paras"]]
        total = sum(len(b) for b in blocks) * lh + (len(blocks) - 1) * int(lh * 0.55)
        if total <= bottom - top or size <= 26:
            break
        size -= 1
    y = top + (bottom - top - total) / 2 + size
    qf = font("Montserrat-Regular.ttf", 140)
    d.text((W - margin + 10, top - 20) if rtl else (margin - 10, top - 20), "”" if rtl else "“", font=qf,
           fill=GOLD + (110,), anchor="rm" if rtl else "lm")
    for bi, b in enumerate(blocks):
        for line in b:
            d.text((W / 2, y), line, font=f, fill=CREAM, anchor="ms", direction=L["dir"], language=L["lang"],
                   stroke_width=1 if size >= 34 else 0, stroke_fill=CREAM)
            y += lh
        y += int(lh * 0.55)

    # footer
    d.line([(margin, H - 78), (W - margin, H - 78)], fill=GOLD + (120,), width=1)
    ff = font("Montserrat-Regular.ttf" if key == "kmr" else L["font"], int(28 * k))
    d.text((W / 2, H - 40), L["channel"], font=ff, fill=GOLD, anchor="ms")

    out = folder / f"dwin_{key}.jpg"
    img.convert("RGB").save(out, quality=94)
    return out, size


if __name__ == "__main__":
    folder = Path(sys.argv[1]).resolve()
    texts = json.loads((folder / "texts.json").read_text(encoding="utf-8"))
    for key in ("ckb", "kmr", "ar"):
        print(*card(folder, key, texts))
