"""Dwin branding: corner logo, end card and thumbnails, one set per language."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from .gfx import W, H
from .captions import LANGS, font_path

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "brand"

CREAM = (246, 239, 224)
GOLD = (150, 118, 60)
OLIVE = (92, 98, 78)
INK = (52, 44, 36)
LATIN_FONT = "Montserrat-Regular.ttf"

CHANNELS = {
    "sorani": {
        "name": [("Dween", "ltr"), (" - ", "ltr"), ("دوین", "rtl")],
        "follow": "بەدوامان بکەون",
        "links": [("Facebook", "facebook.com/share/19ur8TtTet"), ("Telegram", "t.me/dween_krd_breaking")],
    },
    "kurmanji": {
        "name": [("Dwîn - Kurmancî", "ltr")],
        "follow": "Me bişopînin",
        "links": [("Facebook", "facebook.com/dwin.kurmanci")],
    },
    "arabic": {
        "name": [("دوين - العربية", "rtl")],
        "follow": "تابعونا",
        "links": [("Facebook", "facebook.com/dween.arabic")],
    },
}


def _font(name, size):
    return ImageFont.truetype(font_path(name), size, layout_engine=ImageFont.Layout.RAQM)


def _lang_font(key, size):
    return _font(LANGS[key][1], size)


def _text_w(font, text, direction, lang=None):
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    return probe.textlength(text, font=font, direction=direction, language=lang)


def logo(key):
    return Image.open(BRAND / f"logo_{key}.png").convert("RGBA")


# ---------------------------------------------------------------- corner logo
def corner_badge(key, out_path, height=190, margin=34):
    """Full-frame transparent PNG with the logo (no background) in the top-left corner."""
    lg = logo(key)
    lg = lg.resize((int(lg.width * (height - 28) / lg.height), height - 28), Image.LANCZOS)
    # no badge: the logo sits straight on the picture (transparent background),
    # with only a soft shadow that follows its own shape so it stays readable on bright scenes
    x, y = margin, margin
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a = lg.getchannel("A")
    sh = Image.new("RGBA", lg.size, (0, 0, 0, 0))
    sh.putalpha(a.point(lambda v: int(v * 0.75)))
    sh_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh_layer.alpha_composite(sh, (x + 3, y + 4))
    img.alpha_composite(sh_layer.filter(ImageFilter.GaussianBlur(5)))
    img.alpha_composite(lg, (x, y))
    img.save(out_path)
    return out_path


# ---------------------------------------------------------------- end card
def _paper(size):
    """Warm cream paper background with a soft vignette."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    v = 1 - 0.16 * np.clip(d - 0.3, 0, 1) ** 1.5
    rng = np.random.default_rng(3)
    grain = rng.normal(0, 2.2, (h, w)).astype(np.float32)
    arr = np.stack([np.full((h, w), c, np.float32) * v + grain for c in CREAM], axis=2)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def _draw_runs(d, cx, y, runs, key, size, fill):
    """Draw a line made of runs in different scripts, centred on cx, baseline at y."""
    pieces = []
    for text, direction in runs:
        f = _lang_font(key, size) if direction == "rtl" else _font(LATIN_FONT if key != "kurmanji" else LANGS[key][1], size)
        pieces.append((text, direction, f, _text_w(f, text, direction)))
    total = sum(p[3] for p in pieces)
    x = cx - total / 2
    for text, direction, f, w in pieces:
        d.text((x, y), text, font=f, fill=fill, anchor="ls", direction=direction)
        x += w


def end_card(key, out_path):
    ch = CHANNELS[key]
    direction, lang = LANGS[key][2], LANGS[key][3]
    img = _paper((W, H))
    lg = logo(key)
    lh = 520
    lg = lg.resize((int(lg.width * lh / lg.height), lh), Image.LANCZOS)
    img.alpha_composite(lg, ((W - lg.width) // 2, 70))
    d = ImageDraw.Draw(img)
    # thin gold rule
    d.line([(W / 2 - 300, 655), (W / 2 + 300, 655)], fill=GOLD + (255,), width=2)
    _draw_runs(d, W / 2, 735, ch["name"], key, 62, INK + (255,))
    # follow us + links
    ff = _lang_font(key, 40)
    fw = _text_w(ff, ch["follow"], direction, lang)
    d.text((W / 2 - fw / 2, 815), ch["follow"], font=ff, fill=GOLD + (255,), anchor="ls", direction=direction,
           language=lang)
    lf = _font(LATIN_FONT, 38)
    lab = _font(LATIN_FONT, 30)
    y = 885
    for label, url in ch["links"]:
        gap = 26
        lw, uw = _text_w(lab, label.upper(), "ltr"), _text_w(lf, url, "ltr")
        x = W / 2 - (lw + gap + uw) / 2
        d.text((x, y), label.upper(), font=lab, fill=OLIVE + (255,), anchor="ls")
        d.text((x + lw + gap, y), url, font=lf, fill=INK + (255,), anchor="ls")
        y += 64
    img.convert("RGB").save(out_path, quality=95)
    return out_path


# ---------------------------------------------------------------- thumbnail
def _cutout_portrait(path):
    """Turn the white-paper sketch into a cut-out: white becomes transparent, edges feathered."""
    im = Image.open(path).convert("RGB")
    im = im.resize((im.width * 3, im.height * 3), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 80, 2))
    a = np.asarray(im).astype(np.float32)
    whiteness = a.min(axis=2)
    alpha = np.clip((242 - whiteness) / 40.0, 0, 1)
    m = Image.fromarray((alpha * 255).astype(np.uint8))
    m = m.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(14))   # fill gaps inside the sketch
    m = m.point(lambda v: 255 if v > 150 else 0).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(4))
    alpha = np.asarray(m).astype(np.float32) / 255
    h0, w0 = alpha.shape
    alpha = alpha.copy()
    alpha[int(0.62 * h0):, int(0.74 * w0):] = 0                                     # signature + loose shoulder sketch
    a = a * 0.93 + np.array([12, 6, 0], np.float32) * 0.07                       # tone the paper white down a touch
    h, w = alpha.shape
    ys = np.linspace(0, 1, h)[:, None]
    alpha *= np.clip((1 - ys) / 0.18, 0, 1)                              # fade out at the bottom
    xs = np.linspace(0, 1, w)[None, :]
    alpha *= np.clip(xs / 0.06, 0, 1) * np.clip((1 - xs) / 0.06, 0, 1)
    rgba = np.dstack([a, alpha * 255]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def _text_block(img, key, lines, cx, top, max_w):
    """Title lines (text, size, colour) centred on cx, with a soft dark glow behind for legibility."""
    direction, lang = LANGS[key][2], LANGS[key][3]
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    txt = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dg, dt = ImageDraw.Draw(glow), ImageDraw.Draw(txt)
    y = top
    for text, size, colour in lines:
        f = _lang_font(key, size)
        while _text_w(f, text, direction, lang) > max_w and size > 40:
            size -= 4
            f = _lang_font(key, size)
        y += int(size * (1.25 if direction == "rtl" else 1.1))
        stroke = max(2, size // 28)   # embolden the regular weight a little
        dg.text((cx, y), text, font=f, fill=(0, 0, 0, 230), anchor="ms", direction=direction, language=lang,
                stroke_width=stroke + 10, stroke_fill=(0, 0, 0, 230))
        dt.text((cx, y), text, font=f, fill=colour, anchor="ms", direction=direction, language=lang,
                stroke_width=stroke, stroke_fill=colour)
        y += int(size * 0.35)
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(18)))
    img.alpha_composite(txt)


def thumbnail(key, title, background, out_path):
    """16:9 thumbnail: scholar portrait, calligraphy medallion, title in the brand font, corner logo."""
    img = background.convert("RGB").resize((W, H)).filter(ImageFilter.GaussianBlur(3)).convert("RGBA")
    shade = Image.new("RGBA", (W, H), (20, 12, 10, 120))
    img.alpha_composite(shade)
    # warm light behind the portrait
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - 560) / 700) ** 2 + ((yy - 520) / 620) ** 2)
    glow = np.zeros((H, W, 4), np.uint8)
    glow[..., :3] = (255, 196, 120)
    glow[..., 3] = (np.clip(1 - d, 0, 1) ** 2 * 120).astype(np.uint8)
    img.alpha_composite(Image.fromarray(glow, "RGBA"))

    portrait = _cutout_portrait(BRAND / "portrait.png")
    ph = 1060
    portrait = portrait.resize((int(portrait.width * ph / portrait.height), ph), Image.LANCZOS)
    img.alpha_composite(portrait, (560 - portrait.width // 2, H - ph + 40))

    med = Image.open(BRAND / "medallion.png").convert("RGBA")
    ms = 560
    med = med.resize((ms, ms), Image.LANCZOS)
    mshadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mx, my = 1390 - ms // 2, 70
    ImageDraw.Draw(mshadow).ellipse([mx + 10, my + 18, mx + ms + 10, my + ms + 18], fill=(0, 0, 0, 150))
    img.alpha_composite(mshadow.filter(ImageFilter.GaussianBlur(22)))
    img.alpha_composite(med, (mx, my))

    parts = [p.strip() for p in title.split("…") if p.strip()]
    big, small = (112, 84) if key == "arabic" else (96, 70)
    if key == "arabic":                       # Aljazeera's space is narrow; open the words up
        parts = [p.replace(" ", "  ") for p in parts]
    lines = [(parts[0], big, (255, 244, 222, 255))]
    if len(parts) > 1:
        lines.append((parts[1], small, (240, 190, 100, 255)))
    _text_block(img, key, lines, 1390, 650, 900)

    badge = Image.open(corner_badge(key, BRAND.parent / "build" / f"badge_thumb_{key}.png", height=230, margin=30))
    img.alpha_composite(badge)
    img.convert("RGB").save(out_path, quality=93)
    return out_path
