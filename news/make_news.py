"""Dwin quote card (4:5, 1080x1350) in Sorani, Kurmanji and Arabic.

    python3 news/make_news.py news/zaidi-dollar
reads <folder>/photo.jpg and the TEXTS below, writes <folder>/dwin_<lang>.jpg
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = Path(__file__).resolve().parent.parent
W, H = 1080, 1350
GREEN, GOLD, CREAM = (15, 42, 31), (201, 164, 92), (245, 238, 220)

LANG = {
    "ckb": dict(font="Speda.ttf", dir="rtl", lang="ckb", logo="sorani", tag="هەواڵ", channel="Dween - دوین", k=1.0),
    "kmr": dict(font="Montserrat-Regular.ttf", dir="ltr", lang="ku", logo="kurmanji", tag="Nûçe",
                channel="Dwîn - Kurmancî", k=1.0),
    "ar": dict(font="Aljazeera.ttf", dir="rtl", lang="ar", logo="arabic", tag="خبر", channel="دوين - العربية", k=1.2),
}

TEXTS = {
    "ckb": dict(name="عەلی زەیدی", title="سەرۆک ئەنجومەنی وەزیرانی عێڕاق",
                quote="بەهێواشی كاردەكەین و لەماوەی داهاتوودا بەهای دۆلار بۆ 155 هەزار دينارو خوارتریش "
                      "دادەبەزێنین لەڕێی خستەڕووی كاش."),
    "kmr": dict(name="Elî Zeydî", title="Serokê Encûmena Wezîran a Iraqê",
                quote="Em hêdî hêdî kar dikin û di dema pêş de em ê bihayê dolarê daxin 155 hezar dînar "
                      "û kêmtir jî, bi rêya dabînkirina pereyê kaş."),
    "ar": dict(name="علي الزيدي", title="رئيس مجلس الوزراء العراقي",
               quote="نعمل بهدوء، وخلال المرحلة المقبلة سنخفّض سعر الدولار إلى 155 ألف دينار وأقل، "
                     "من خلال ضخّ الكاش."),
}


def font(name, size):
    return ImageFont.truetype(str(REPO / "fonts" / name), size, layout_engine=ImageFont.Layout.RAQM)


def tw(text, fnt, L):
    return ImageDraw.Draw(Image.new("L", (8, 8))).textlength(text, font=fnt, direction=L["dir"], language=L["lang"])


def wrap(text, fnt, L, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if tw(t, fnt, L) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + ([cur] if cur else [])


def logo(key, dark):
    if dark:
        p = REPO / "almas-reel" / "build" / f"logo_dark_{key}.png"
        if p.exists():
            return Image.open(p).convert("RGBA")
        sys.path.insert(0, str(REPO / "almas-reel" / "render"))
        from assets import logo_dark
        return logo_dark(key).convert("RGBA")
    return Image.open(REPO / "brand" / f"logo_{key}.png").convert("RGBA")


def card(folder, key):
    L, T = LANG[key], TEXTS[key]
    rtl = L["dir"] == "rtl"
    img = Image.new("RGB", (W, H), GREEN)

    # photo on top, fading into the green panel
    ph = Image.open(folder / "photo.jpg").convert("RGB")
    ph = ph.resize((W, int(ph.height * W / ph.width)), Image.LANCZOS)
    top_crop = int(ph.height * 0.10)
    ph = ph.crop((0, top_crop, W, top_crop + 820))
    img.paste(ph, (0, 0))
    fade = np.zeros((H, W, 1), np.float32)
    y = np.arange(H)[:, None, None]
    fade = np.clip((y - 560) / 260, 0, 1)
    arr = np.asarray(img).astype(np.float32)
    arr = arr * (1 - fade) + np.array(GREEN, np.float32) * fade
    img = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)

    margin = 70
    edge = W - margin if rtl else margin
    anchor_l = "rs" if rtl else "ls"

    # news tag pill
    tf = font(L["font"], int(30 * L["k"]))
    pw = tw(L["tag"], tf, L) + 44
    py = 690
    x0, x1 = (edge - pw, edge) if rtl else (edge, edge + pw)
    d.rounded_rectangle([x0, py, x1, py + 52], 12, fill=GOLD)
    d.text(((x0 + x1) / 2, py + 26), L["tag"], font=tf, fill=GREEN, anchor="mm", direction=L["dir"],
           language=L["lang"])

    # name (gold) and title (cream)
    nf = font(L["font"], int(70 * L["k"]))
    d.text((edge, py + 135), T["name"], font=nf, fill=GOLD, anchor=anchor_l, direction=L["dir"], language=L["lang"],
           stroke_width=2, stroke_fill=GOLD)
    tf2 = font(L["font"], int(36 * L["k"]))
    d.text((edge, py + 195), T["title"], font=tf2, fill=CREAM, anchor=anchor_l, direction=L["dir"],
           language=L["lang"])
    # gold rule
    d.rectangle([(edge - 140, py + 225), (edge, py + 229)] if rtl else [(edge, py + 225), (edge + 140, py + 229)],
                fill=GOLD)

    # quote
    qsize = int(50 * L["k"])
    qf = font(L["font"], qsize)
    lines = wrap("«" + T["quote"] + "»", qf, L, W - 2 * margin)
    while len(lines) > 5 and qsize > 38:
        qsize -= 2
        qf = font(L["font"], qsize)
        lines = wrap("«" + T["quote"] + "»", qf, L, W - 2 * margin)
    lh = int(qsize * (1.62 if rtl else 1.38))
    yq = py + 300
    for i, line in enumerate(lines):
        d.text((edge, yq + i * lh), line, font=qf, fill=CREAM, anchor=anchor_l, direction=L["dir"],
               language=L["lang"], stroke_width=1, stroke_fill=CREAM)

    # footer: channel name
    ff = font("Montserrat-Regular.ttf" if key == "kmr" else L["font"], int(28 * L["k"]))
    d.line([(margin, H - 78), (W - margin, H - 78)], fill=GOLD + (120,), width=1)
    d.text((W / 2, H - 40), L["channel"], font=ff, fill=GOLD, anchor="ms", direction=None if key == "kmr" else None)

    # logo top-left, no background box: the photo corner is softly darkened so the gold/cream logo reads
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dist = np.sqrt(((xx - 110) / 330) ** 2 + ((yy - 140) / 360) ** 2)
    a = (np.clip(1 - dist, 0, 1) ** 1.3 * 0.72)[..., None]
    arr = np.asarray(img.convert("RGB")).astype(np.float32)
    arr = arr * (1 - a) + np.array(GREEN, np.float32) * a
    img = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
    lg = logo(L["logo"], dark=True)
    lw = 150
    lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    sh = Image.new("RGBA", lg.size, (0, 0, 0, 0))
    sh.putalpha(lg.getchannel("A").point(lambda v: int(v * 0.35)))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)), (42, 44))
    img.alpha_composite(lg, (40, 40))

    out = folder / f"dwin_{key}.jpg"
    img.convert("RGB").save(out, quality=94)
    return out


if __name__ == "__main__":
    folder = Path(sys.argv[1]).resolve()
    for k in LANG:
        print(card(folder, k))
