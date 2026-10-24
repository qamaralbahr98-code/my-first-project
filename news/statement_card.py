"""Dwin full-bleed statement card (4:5, 1080x1350): the photo fills the whole poster.

    python3 news/statement_card.py news/pire-government
reads <folder>/photo.jpg and <folder>/texts.json ({lang: {tag, quote, name, who}}), writes <folder>/dwin_<lang>.jpg
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_news import CREAM, GOLD, GREEN, H, LANG, W, font, logo, tw, wrap   # noqa: E402


def full_bleed(path, cx):
    """Crop the photo to 4:5 around x = cx (fraction) and fill the poster; sharpen and add fine grain."""
    im = Image.open(path).convert("RGB")
    cw = min(im.width, int(im.height * W / H))
    x0 = int(min(max(0, im.width * cx - cw / 2), im.width - cw))
    im = im.crop((x0, 0, x0 + cw, im.height))
    im = im.resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(3, 90, 2))
    a = np.asarray(im).astype(np.float32)
    a += np.random.default_rng(2).normal(0, 3.0, a.shape[:2])[..., None]   # grain hides the enlargement softness
    # dark green gradient over the lower part (text area) and a soft top-left shade for the logo
    y = np.linspace(0, 1, H)[:, None, None]
    g = np.clip((y - 0.40) / 0.38, 0, 1) ** 1.2 * 0.93
    a = a * (1 - g) + np.array(GREEN, np.float32) * g
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    s = (np.clip(1 - np.sqrt(((xx - 110) / 340) ** 2 + ((yy - 140) / 360) ** 2), 0, 1) ** 1.3 * 0.65)[..., None]
    a = a * (1 - s) + np.array(GREEN, np.float32) * s
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def card(folder, key, texts):
    L, T = LANG[key], texts[key]
    rtl = L["dir"] == "rtl"
    k = L["k"]
    img = full_bleed(folder / "photo.jpg", texts.get("_crop_x", 0.5))
    d = ImageDraw.Draw(img)
    margin = 70
    edge = W - margin if rtl else margin
    anc = "rs" if rtl else "ls"

    lg = logo(L["logo"], dark=True)
    lw = 150
    lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    img.alpha_composite(lg, (40, 40))

    # quote: big, fitted to at most 4 lines
    size = int(66 * k)
    while True:
        qf = font(L["font"], size)
        lines = wrap("«" + T["quote"] + "»", qf, L, W - 2 * margin)
        if len(lines) <= 4 or size <= 40:
            break
        size -= 2
    lh = int(size * (1.5 if rtl else 1.3))
    nf = font(L["font"], int(48 * k))
    wf = font(L["font"], int(28 * k))
    who = wrap(T["who"], wf, L, W - 2 * margin)
    # height of everything below the tag's top edge, measured the same way it is drawn
    block = 60 + size + len(lines) * lh + 10 + int(50 * k) + int(44 * k) + (len(who) - 1) * int(42 * k) + int(12 * k)
    y = H - 100 - block

    # tag pill
    tf = font(L["font"], int(30 * k))
    pw = tw(T["tag"], tf, L) + 44
    x0, x1 = (edge - pw, edge) if rtl else (edge, edge + pw)
    d.rounded_rectangle([x0, y, x1, y + 52], 12, fill=GOLD)
    d.text(((x0 + x1) / 2, y + 26), T["tag"], font=tf, fill=GREEN, anchor="mm", direction=L["dir"], language=L["lang"])
    y += 60 + size

    for line in lines:
        d.text((edge, y), line, font=qf, fill=CREAM, anchor=anc, direction=L["dir"], language=L["lang"],
               stroke_width=2, stroke_fill=CREAM)
        y += lh
    y += 10
    d.rectangle([(edge - 140, y - 20), (edge, y - 16)] if rtl else [(edge, y - 20), (edge + 140, y - 16)], fill=GOLD)
    y += int(50 * k)
    d.text((edge, y), T["name"], font=nf, fill=GOLD, anchor=anc, direction=L["dir"], language=L["lang"],
           stroke_width=1, stroke_fill=GOLD)
    y += int(44 * k)
    for line in who:
        d.text((edge, y), line, font=wf, fill=CREAM, anchor=anc, direction=L["dir"], language=L["lang"])
        y += int(42 * k)

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
