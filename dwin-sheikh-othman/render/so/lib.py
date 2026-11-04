"""The 33 scenes of the Kurdish-youth explainer. Each scene(c, t) returns an RGBA frame of c.W x c.H.

Layout is mirrored for RTL (ar, ckb). All on-screen text is the scene's `t` text from script/scenes.json, split
at its own separators; the few extra labels (chapter names, tags) are in LABELS below.
"""
import math
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import base as B
from .base import (CREAM, DARK, GREEN, INK, PAPER, RED, SAFFRON, T, clamp01, ease, ease_out, back_out, kit, paste,
                   strips)
from vox import geo

LABELS = {
    "chapter": {
        1: {"ar": "المشكلة الجوهرية", "ckb": "کێشە سەرەکییەکە", "kmr": "Pirsgirêka bingehîn"},
        2: {"ar": "الأدلة", "ckb": "بەڵگەکان", "kmr": "Delîl"},
        3: {"ar": "الاعتراضات", "ckb": "ڕەخنەکان", "kmr": "Îtiraz"},
        4: {"ar": "ما الذي على المحك؟", "ckb": "چی لە مەترسیدایە؟", "kmr": "Çi di xeterê de ye?"},
    },
    "mannheim": {"ar": "كارل مانهايم | عالم اجتماع", "ckb": "کارل مانهایم | کۆمەڵناس", "kmr": "Karl Mannheim | civaknas"},
    "venn": {"ar": ("كردي", "سوري"), "ckb": ("کورد", "سووری"), "kmr": ("Kurd", "Sûrî")},
    "qual": {"ar": "دراسة نوعية — ليست نسبًا إحصائية", "ckb": "توێژینەوەی چۆنایەتی — نەک ڕێژەی ڕاپرسی",
             "kmr": "Lêkolîna kalîteyî — ne rêjeyên anketê"},
    "differ": {"ar": "المصادر تختلف", "ckb": "سەرچاوەکان جیاوازن", "kmr": "Çavkanî ji hev cuda ne"},
    "kadmin": {"ar": "الإدارة الكردية", "ckb": "ئیدارەی کوردی", "kmr": "Rêveberiya Kurdî"},
    "subscribe": {"ar": "اشترك وشاركنا رأيك في التعليقات", "ckb": "سەبسکرایب بکە و بیروڕات بنووسە",
                  "kmr": "Abone bibe û ramana xwe binivîse"},
    "channel": {"ar": "دوين - العربية", "ckb": "Dween - دوین", "kmr": "Dwîn - Kurmancî"},
    "cities": {
        "hasakah": {"ar": "الحسكة", "ckb": "حەسەکە", "kmr": "Hesekê"},
        "qamishli": {"ar": "القامشلي", "ckb": "قامیشلۆ", "kmr": "Qamişlo"},
        "kobani": {"ar": "كوباني", "ckb": "کۆبانی", "kmr": "Kobanî"},
        "afrin": {"ar": "عفرين", "ckb": "عەفرین", "kmr": "Efrîn"},
        "aleppo": {"ar": "حلب", "ckb": "حەلەب", "kmr": "Heleb"},
        "damascus": {"ar": "دمشق", "ckb": "دیمەشق", "kmr": "Şam"},
        "erbil": {"ar": "أربيل", "ckb": "هەولێر", "kmr": "Hewlêr"},
        "berlin": {"ar": "برلين", "ckb": "بەرلین", "kmr": "Berlîn"},
    },
}
# credit line for each real clip (lower-third)
CREDITS = {
    "R03_decree13_announcement.mp4": "Syrian Presidency",
    "R04_nowruz_qamishli_2026.mp4": "Nowruz 2026 · Qamishli",
    "R05_student_protests_sep2026.mp4": "News footage · Sep 2026",
    "R06_aleppo_jan2026_news.mp4": "Viory / Mirror Now",
    "R07_damascus_dec2024_crowds.mp4": "BBC News",
    "R10_kobani_city_view.mp4": "Kobani",
    "R09_karl_mannheim_portrait.jpg": "Public domain",
}
PLACES = {"hasakah": (36.50, 40.75), "qamishli": (37.05, 41.22), "kobani": (36.89, 38.35), "afrin": (36.51, 36.87),
          "aleppo": (36.20, 37.16), "damascus": (33.51, 36.29), "erbil": (36.19, 44.01), "berlin": (52.52, 13.40)}
EAST = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
WEST = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def lab(key, lang):
    return LABELS[key][lang]


def digits(c, s):
    return str(s).translate(EAST) if c.lang in ("ar", "ckb") else str(s)


def split(text, *seps):
    for s in seps:
        if s in text:
            return [p.strip() for p in text.split(s)]
    return [text.strip()]


NUM = re.compile(r"[\d٠-٩][\d٠-٩٬.,]*")


def counter_text(text, u):
    """Roll the first number in `text` from 0 to its value (u in 0..1), keeping its digits and separator."""
    m = NUM.search(text)
    if not m:
        return text
    tok = m.group(0)
    sep = "٬" if "٬" in tok else ("." if re.search(r"\.\d{3}", tok.translate(WEST)) else ",")
    raw = tok.translate(WEST).replace("٬", "").replace(",", "").replace(".", "")
    if not raw.isdigit():
        return text
    val = int(raw)
    v = int(round(val * ease_out(u)))
    s = f"{v:,}".replace(",", sep) if len(raw) > 3 else str(v)
    if any(ch in "٠١٢٣٤٥٦٧٨٩" for ch in tok):
        s = s.translate(EAST)
    return text[:m.start()] + s + text[m.end():]


# ------------------------------------------------------------------ shared pieces
def big_text(c, text, size, colour=CREAM, maxw=None, bold=True):
    maxw = maxw or c.W - 2 * c.margin
    return c.get(("big", text, size, colour, maxw), lambda: B.stack(B.text_lines(c.lang, text, size, maxw, colour, bold),
                                                                     0.12, "center"))


def headline(c, f, text, t, t0, size, cy, colour=CREAM, maxw=None, mode="fade", dur=0.6):
    im = big_text(c, text, size, colour, maxw)
    k = clamp01((t - t0) / dur)
    if k <= 0:
        return None
    x, y = c.W / 2 - im.width / 2, cy - im.height / 2
    if mode == "wipe":
        paste(f, kit.wipe(im, ease(k), c.rtl), x, y)
    elif mode == "slam":
        s = 1 + 0.5 * (1 - back_out(k, 1.6))
        im2 = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
        paste(f, im2, c.W / 2 - im2.width / 2, cy - im2.height / 2, clamp01(k * 3))
    else:
        paste(f, im, x, y + (1 - ease_out(k)) * 26, ease(k))
    return (x, y, x + im.width, y + im.height)


def tag(c, f, text, t, t0, x=None, y=None, size=None, fill=SAFFRON, fg=INK, side=None):
    """Rounded tool tag; slides in from the reading side."""
    size = size or (30 if c.vert else 28)
    im = c.get(("tag", text, size, fill, fg), lambda: B.pill(c.lang, text, size, fill, fg))
    k = ease_out((t - t0) / 0.45)
    if k <= 0:
        return
    rtl = c.rtl if side is None else side == "right"
    if x is None:
        x = (c.W - c.margin - im.width) if rtl else c.margin
    dx = (1 - k) * 120 * (1 if rtl else -1)
    paste(f, im, x + dx, y, clamp01(k * 1.5))
    return im


def timeline_bar(c, f, t, year, t_jump, years=(1962, 1973, 2011, 2024, 2026), y=None, frm=None):
    """Timeline bar running in reading direction; the marker jumps to `year` at t_jump."""
    y = y or (c.cap_top - 70)
    x0, x1 = c.margin + 20, c.W - c.margin - 20
    span = years[-1] - years[0]

    def X(yr):
        u = (yr - years[0]) / span
        u = 0.08 + 0.84 * u ** 0.55
        return x1 - (x1 - x0) * u if c.rtl else x0 + (x1 - x0) * u
    lay = Image.new("RGBA", (c.W, 140), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([x0 - 24, 26, x1 + 24, 118], 18, fill=(17, 20, 24, 200))
    d.line([(x0, 72), (x1, 72)], fill=CREAM + (200,), width=4)
    frm = frm if frm is not None else years[0]
    k = ease((t - t_jump) / 0.7)
    cur = frm + (year - frm) * k
    for yr in years:
        xx = X(yr)
        on = yr <= cur + 0.01
        d.ellipse([xx - 9, 63, xx + 9, 81], fill=(SAFFRON if on else CREAM) + (255,))
        im = T(c.lang, digits(c, yr), 26, SAFFRON if abs(yr - year) < 0.5 and k > 0.95 else CREAM, True)
        paste(lay, im, xx - im.width / 2, 78)
    xm = X(frm) + (X(year) - X(frm)) * k
    d.polygon([(xm - 14, 40), (xm + 14, 40), (xm, 60)], fill=SAFFRON + (255,))
    paste(f, lay, 0, y - 60, clamp01(t / 0.4))


def ink_layer(c):
    return Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))


def lower_strip(c, f, lines, t, t0, stagger=0.4, size=None, y=None, colours=None, bgs=None, times=None, out=None):
    """OST strips above the caption band (16:9: reading-start side; 9:16: centred)."""
    size = size or (50 if c.vert else 50)
    hs = [B.strip_img(c.lang, s, size).height - 2 for s in lines]
    yy = y if y is not None else c.cap_top - 30 - sum(hs)
    return strips(c, f, lines, t, t0, y=yy, size=size, stagger=stagger, colours=colours, bgs=bgs, times=times, out=out)


def framed_clip(c, f, name, t, t_clip=None, w=None, cy=None, loop=False, prep=None, start=0.0):
    """Real footage in a cut-out paper frame (16:9) or on a blurred copy of itself (9:16)."""
    w = w or (1000 if c.vert else 1440)
    h = int(w * 9 / 16) // 2 * 2
    cl = B.clip(c, name, h, start=start)
    fr = cl.at(t if t_clip is None else t_clip, loop)
    if fr.width != w:
        fr = fr.resize((w, h), Image.BILINEAR) if abs(fr.width - w) > 2 else fr
    if prep:
        fr = prep(fr)
    cy = cy or (c.H * 0.42 if c.vert else c.H * 0.46)
    x, y = c.W / 2 - fr.width / 2, cy - fr.height / 2
    bd = 8
    frame = Image.new("RGBA", (fr.width + 2 * bd, fr.height + 2 * bd), CREAM + (255,))
    frame.alpha_composite(fr, (bd, bd))
    sh = B.shadowed(frame, 14, (10, 14), 120)
    paste(f, sh, x - bd - 42, y - bd - 42)
    c.credit = CREDITS.get(name)
    return (x, y, x + fr.width, y + fr.height)


def clip_bg(c, name, t, dark=0.55, blur=0, loop=True, sat=1.0):
    """Full-bleed real footage (cover), darkened, optionally blurred."""
    h = c.H if not c.vert else c.H
    cl = B.clip(c, name, 540 if blur else min(1080, h), start=0.0)
    fr = cl.at(t, loop)
    s = max(c.W / fr.width, c.H / fr.height)
    fr = fr.resize((int(fr.width * s) + 1, int(fr.height * s) + 1), Image.BILINEAR)
    fr = fr.crop(((fr.width - c.W) // 2, (fr.height - c.H) // 2, (fr.width - c.W) // 2 + c.W, (fr.height - c.H) // 2 + c.H))
    if blur:
        fr = fr.filter(ImageFilter.GaussianBlur(blur))
    if sat != 1.0:
        fr = B.grade(fr, sat=sat)
    c.credit = CREDITS.get(name)
    return B.darken(fr, dark)


def vert_bg_from_clip(c, name, t):
    """9:16 background: the clip blurred and dark behind the framed clip."""
    return clip_bg(c, name, t, dark=0.35, blur=18)


# ------------------------------------------------------------------ motion shots (MOTION.md)
def person_layer(c, name, key):
    """RGBA person cut (rembg matte) at the 'big' resolution of the photo."""
    def build():
        im = B._big(c, name)
        m = B.mask(name).resize(im.size, Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
        lay = im.convert("RGBA")
        lay.putalpha(m)
        return lay
    return c.get(("person", name, key), build)


def m1(c, t, D, title=None, title_t0=None, title_size=None, z_bg=(1.0, 1.06), z_p=(1.0, 1.12), name="A01_rooftop_from_behind.jpg",
       anchor=(0.36, 0.95), leak=True, title_y=None):
    """2.5D dolly-in: background and person (rembg) zoom at different speeds; optional title between them."""
    im = B._big(c, name)
    u = B.prog(t, D)
    ax, ay = anchor
    if c.vert:
        ax = 0.36 if "A01" in name else 0.62
    cam_bg = B.Cam(im.width, im.height, u, z_bg[0], z_bg[1], (ax, 0.55), (ax, 0.55), (c.W, c.H))
    f = cam_bg.view(im).convert("RGBA")
    if title:
        lay = person_layer(c, name, "p")
        cam_p = B.Cam(im.width, im.height, u, z_p[0], z_p[1], (ax, 0.55), (ax, 0.55), (c.W, c.H))
        f = B.darken(f, 0.82)
        size = title_size or (230 if not c.vert else 200)
        k = ease_out((t - title_t0) / 0.9)
        if k > 0:
            ti = big_text(c, title, size, CREAM, c.W - 120)
            ty = title_y if title_y is not None else (c.H * (0.30 if not c.vert else 0.34))
            paste(f, ti, c.W / 2 - ti.width / 2, ty - ti.height / 2 + (1 - k) * 40, k)
        f.alpha_composite(cam_p.view(lay))
    else:
        lay = person_layer(c, name, "p")
        cam_p = B.Cam(im.width, im.height, u, z_p[0], z_p[1], (ax, 0.55), (ax, 0.55), (c.W, c.H))
        f.alpha_composite(cam_p.view(lay))
    if leak:
        f = light_leak(c, f, t)
    c.illustration()
    return B.grain(B.vignette(f, 0.5), t, 8)


def light_leak(c, f, t):
    g = c.get(("leak",), lambda: B.radial_img(int(c.W * 0.9), int(c.H * 0.9), SAFFRON))
    x = -c.W * 0.4 + (t * 40) % (c.W * 1.6)
    paste(f, g, x, -c.H * 0.25, 0.22)
    return f


def m3(c, t, D, echo=0.0):
    """Phone push-in 1.00->1.08, screen glow flicker, optional echo copies."""
    name = "A05_phone_in_hands_music.jpg"
    f, cam = B.photo(c, name, t, D, (1.0, 1.08), (0.47, 0.45), (0.47, 0.45))
    fl = 1 + 0.04 * math.sin(t * 7.1) * math.sin(t * 2.3 + 1)
    box = (0.36, 0.12, 0.69, 0.80)
    im = B._big(c, name)
    x0, y0 = cam.pt(box[0] * im.width, box[1] * im.height)
    x1, y1 = cam.pt(box[2] * im.width, box[3] * im.height)
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    reg = f.crop((x0, y0, x1, y1))
    reg = B.grade(reg, (fl, fl, fl))
    f.paste(reg, (x0, y0))
    if echo > 0:
        base = f.copy()
        for k, (dx, dy) in enumerate(((60, -30), (-70, 40), (120, 60))):
            a = clamp01(echo * 3 - k) * 0.3
            if a > 0:
                sh = base.transpose(Image.FLIP_LEFT_RIGHT) if k == 1 else base
                sc = 0.92 - 0.06 * k
                sm = sh.resize((int(c.W * sc), int(c.H * sc)), Image.BILINEAR)
                paste(f, sm, c.W / 2 - sm.width / 2 + dx * echo, c.H / 2 - sm.height / 2 + dy * echo, a)
    return B.grain(B.vignette(f, 0.5), t, 8), (x0, y0, x1, y1)


PATHS = [[(0.50, 0.46), (0.62, 0.36), (0.78, 0.25), (0.98, 0.10)],      # 1: to the upper right
         [(0.50, 0.46), (0.36, 0.45), (0.18, 0.42), (0.00, 0.40)],      # 2: to the left
         [(0.50, 0.46), (0.56, 0.62), (0.66, 0.82), (0.74, 1.00)]]      # 3: down


def m4(c, t, D, glow=None, glow_t0=0.0, zoom=(1.15, 1.0), rot=(1.0, 0.0), cool=0.0, numbers=True):
    """Fake drone rise over the crossroads: zoom out with a slight rotation; one path glows saffron."""
    name = "A09_crossroads_paths.jpg"
    im = B._big(c, name, k=1.35)
    u = B.prog(t, D)
    z = zoom[0] + (zoom[1] - zoom[0]) * u
    a = rot[0] + (rot[1] - rot[0]) * u
    cam = B.Cam(im.width, im.height, 0.0, z, z, (0.5, 0.48), (0.5, 0.48), (c.W, c.H))
    big = c.get(("m4view",), lambda: None)
    f = cam.view(im)
    if abs(a) > 0.01:
        f = f.rotate(a, resample=Image.BILINEAR, expand=False).resize((c.W, c.H))
        f = f.crop((int(c.W * 0.02), int(c.H * 0.02), int(c.W * 0.98), int(c.H * 0.98))).resize((c.W, c.H), Image.BILINEAR)
    f = f.convert("RGBA")
    if cool:
        f = B.grade(f, (1 - 0.12 * cool, 1 - 0.02 * cool, 1 + 0.1 * cool), 1 - 0.3 * cool)
    if glow:
        k = ease((t - glow_t0) / 1.2)
        if k > 0:
            lay = ink_layer(c)
            d = ImageDraw.Draw(lay)
            pts = [cam.pt(x * im.width, y * im.height) for x, y in PATHS[glow - 1]]
            pts = kit.resample(pts, 6)
            pp = kit.partial(pts, k)
            if len(pp) > 1:
                d.line(pp, fill=SAFFRON + (230,), width=34, joint="curve")
            glow_im = lay.filter(ImageFilter.GaussianBlur(18))
            f.alpha_composite(glow_im)
            f.alpha_composite(glow_im)
            lay2 = ink_layer(c)
            if len(pp) > 1:
                ImageDraw.Draw(lay2).line(pp, fill=(255, 226, 170, 210), width=8, joint="curve")
            f.alpha_composite(lay2.filter(ImageFilter.GaussianBlur(2)))
    if numbers:
        for i, p in enumerate(PATHS):
            x, y = cam.pt(p[2][0] * im.width, p[2][1] * im.height)
            on = glow == i + 1
            r = 34
            disc = Image.new("RGBA", (2 * r + 4, 2 * r + 4), (0, 0, 0, 0))
            ImageDraw.Draw(disc).ellipse([2, 2, 2 * r + 2, 2 * r + 2], fill=(SAFFRON if on else CREAM) + (240,),
                                         outline=INK + (255,), width=3)
            n = T(c.lang, digits(c, i + 1), 40, INK, True)
            paste(disc, n, disc.width / 2 - n.width / 2, disc.height / 2 - n.height / 2)
            paste(f, disc, x - r, y - r, clamp01(t / 0.6))
    c.illustration()
    return B.grain(B.vignette(f, 0.45), t, 7)


def m2(c, t, D):
    """Slow lateral pan 3% with depth parallax and wind on the wheat (bottom 40%)."""
    name = "A11_jazira_olive_wheat_landscape.jpg"
    im = B._big(c, name, k=1.25)
    u = B.prog(t, D)
    cx = 0.485 + 0.03 * u if not c.rtl else 0.515 - 0.03 * u
    cam = B.Cam(im.width, im.height, 0.0, 1.06, 1.06, (cx, 0.5), (cx, 0.5), (c.W, c.H))
    f = np.asarray(cam.view(im)).copy()
    H, W = f.shape[:2]
    y0 = int(H * 0.6)
    ys = np.arange(y0, H)
    depth = (ys - y0) / (H - y0)
    amp = 1.5 + 1.5 * depth
    xs = np.arange(W)
    for j, y in enumerate(ys[::2]):
        sh = int(round(amp[j * 2] * math.sin(2 * math.pi * (t / 2.0) + y * 0.035) + 0.6 * math.sin(t * 4.3 + y * 0.11)))
        if sh:
            f[y:y + 2] = np.roll(f[y:y + 2], sh, axis=1)
    out = Image.fromarray(f).convert("RGBA")
    c.illustration()
    return B.grain(B.vignette(out, 0.45), t, 7)


# ------------------------------------------------------------------ chapter card
def chapter_card(c, n, t):
    f = B.dark_bg(c, 5)
    num = c.get(("chnum", n), lambda: T(c.lang, digits(c, f"0{n}" if c.lang == "kmr" else n), 200 if not c.vert else 220,
                                        SAFFRON, True))
    title = LABELS["chapter"][n][c.lang]
    k = ease_out(t / 0.5)
    cy = c.H * 0.45
    paste(f, num, c.W / 2 - num.width / 2, cy - num.height + 30 - (1 - k) * 30, k)
    ti = big_text(c, title, 96 if not c.vert else 88, CREAM)
    paste(f, kit.wipe(ti, ease((t - 0.25) / 0.6), c.rtl), c.W / 2 - ti.width / 2, cy + 50)
    d = ImageDraw.Draw(f)
    w = int(260 * ease((t - 0.4) / 0.6))
    if w > 2:
        yy = cy + 50 + ti.height + 30
        d.line([(c.W / 2 - w / 2, yy), (c.W / 2 + w / 2, yy)], fill=SAFFRON + (255,), width=6)
    return f


# ------------------------------------------------------------------ scenes
def s01(c, t):
    f = m1(c, t, c.D, z_bg=(1.0, 1.06), z_p=(1.0, 1.12))
    f = B.darken(f, 0.8 + 0.2 * clamp01(t / 1.0))
    ost = c.ost[0]
    t0 = c.at("مولودٌ", "لەدایک", "dayik", default=c.frac(0.1))
    headline(c, f, ost, t, max(1.0, t0 - 0.5), 76 if not c.vert else 70, c.H * (0.2 if not c.vert else 0.27),
             mode="wipe", dur=1.4)
    return f


def s02(c, t):
    f = B.paper_bg(c, t, c.D, 2)
    year, rest = split(c.ost[0], "|")[:2] if "|" in c.ost[0] else (c.ost[0], "")
    # blank document cut-out with a red ink circle
    w = 760 if not c.vert else 860
    doc = B.cut(c, "A02_blank_paper_document.jpg", w=w, border=10, rot=-3 if c.rtl else 3, seed=2)
    cx = c.mx(c.W * 0.70) if not c.vert else c.W / 2
    cy = c.H * 0.47 if not c.vert else c.H * 0.62
    box = B.place(f, doc, cx, cy, t, 0.15, "right" if c.rtl else "left")
    c.illustration()
    t_y = c.at("ألف", "١٩٦٢", "1962", default=c.frac(0.05))
    yx = c.mx(c.W * 0.28) if not c.vert else c.W / 2
    yy = c.H * 0.36 if not c.vert else c.H * 0.25
    im = c.get(("year", year), lambda: T(c.lang, year, 300 if not c.vert else 280, INK, True))
    k = clamp01((t - t_y) / 0.35)
    if k > 0:
        s = 1 + 0.6 * (1 - back_out(k, 1.8))
        im2 = im.resize((int(im.width * s), int(im.height * s)), Image.BILINEAR)
        paste(f, im2, yx - im2.width / 2, yy - im2.height / 2, clamp01(k * 3))
    t_n = c.at("مئة", "سەد", "sed", default=c.frac(0.6))
    if rest and t > t_n - 0.6:
        u = clamp01((t - t_n + 0.3) / 1.6)
        txt = counter_text(rest, u)
        size = 64 if not c.vert else 58
        s_im = B.strip_img(c.lang, txt, size, CREAM, INK)
        s_im = B.fit_w(s_im, (c.W * 0.48 if not c.vert else c.W - 60))
        paste(f, s_im, yx - s_im.width / 2, yy + im.height * 0.45, ease_out((t - t_n + 0.6) / 0.5))
    if box:
        lay = ink_layer(c)
        d = ImageDraw.Draw(lay)
        x0, y0, x1, y1 = box
        p = clamp01((t - (t_n + 0.4)) / 1.2)
        if p > 0:
            kit.ink_line(d, kit.ellipse_pts((x0 + 90, y0 + 90, x1 - 90, y1 - 120), seed=4), p, RED, 9)
            f.alpha_composite(lay)
    return f


def s03(c, t):
    bg = c.get(("s03bg",), lambda: None)
    f, _ = B.kenburns(c, "A13_crowd_silhouettes_dusk.jpg", t, c.D, dark=0.22, label=True)
    q = c.ost[0]
    t0 = c.at("إلى", "ئێمە", "Em", default=c.frac(0.5))
    im = big_text(c, q, 150 if not c.vert else 120, CREAM)
    n = max(1, len(q))
    k = clamp01((t - t0) / (0.06 * n))
    steps = math.floor(k * n) / n
    if steps > 0:
        paste(f, kit.wipe(im, steps, c.rtl), c.W / 2 - im.width / 2, c.H * 0.42 - im.height / 2)
    return f


def s04(c, t):
    lines = c.ost
    f = m1(c, t, c.D, title=lines[0], title_t0=0.3, title_size=300 if not c.vert else 230,
           name="A08_young_woman_from_behind_sunrise.jpg", z_bg=(1.0, 1.05), z_p=(1.0, 1.09), anchor=(0.6, 0.9),
           leak=False, title_y=c.H * (0.30 if not c.vert else 0.30))
    if len(lines) > 1:
        sub = big_text(c, lines[1], 64 if not c.vert else 58, INK)
        st = B.strip_img(c.lang, lines[1], 60 if not c.vert else 54, INK, SAFFRON)
        k = ease_out((t - 1.2) / 0.6)
        paste(f, st, c.W / 2 - st.width / 2, c.H * (0.52 if not c.vert else 0.18) + (1 - k) * 30, k)
    return f


def syria_map(c, w, h):
    def build():
        span = 14.0 if not c.vert else 8.4
        v = geo.View(38.9, 34.9, span, w, h)
        im = geo.base_map(v, rivers=("euphrates", "tigris"), highlight=["Syria"], seed=4)
        return im, v
    return c.get(("syria", w, h), build)


def city(c, f, v, key, t, t0, colour=RED, label=True, off=(0, 0), size=None):
    x, y = v.xy(*PLACES[key])
    k = back_out((t - t0) / 0.4, 2.0)
    if k <= 0:
        return
    lay = ink_layer(c)
    d = ImageDraw.Draw(lay)
    r = 11 * k
    d.ellipse([x - r - 5, y - r - 5, x + r + 5, y + r + 5], fill=CREAM + (220,))
    d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(colour) + (255,))
    f.alpha_composite(lay)
    if label:
        name = LABELS["cities"][key][c.lang]
        im = c.get(("city", name, size), lambda: B.strip_img(c.lang, name, size or (34 if not c.vert else 36), INK, CREAM,
                                                          pad=(14, 4)))
        paste(f, im, x - im.width / 2 + off[0], y - im.height - 14 + off[1], clamp01(k))


def s05(c, t):
    mp, v = syria_map(c, c.W, c.H)
    u = B.prog(t, c.D)
    cam = B.Cam(c.W, c.H, u, 1.0, 1.04, (0.5, 0.5), (0.52, 0.45), (c.W, c.H))
    f = cam.view(mp).convert("RGBA")

    class V2:
        def xy(self, lat, lon):
            return cam.pt(*v.xy(lat, lon))
    vv = V2()
    keys = [("hasakah", "الحسكة", "حەسەکە", "Hesekê"), ("qamishli", "والقامشلي", "قامیشلۆ", "Qamişlo"),
            ("kobani", "وكوباني", "کۆبانی", "Kobanî"), ("afrin", "وعفرين", "عەفرین", "Efrîn"),
            ("aleppo", "حلب", "حەلەب", "Helebê"), ("damascus", "ودمشق", "دیمەشق", "Şamê")]
    offs = {"qamishli": (40, 0), "hasakah": (-30, 60), "kobani": (0, 0), "afrin": (-30, 0), "aleppo": (10, 62)}
    for key, a, b, k in keys:
        city(c, f, vv, key, t, c.at(a, b, k), off=offs.get(key, (0, 0)))
    lower_strip(c, f, [c.ost[0]], t, c.frac(0.05), y=c.top if not c.vert else c.top + 40)
    # Kobani city view inset at the end
    t_in = c.frac(0.82)
    if t > t_in and not c.vert:
        w = 520
        h = int(w * 9 / 16) // 2 * 2
        cl = B.clip(c, "R10_kobani_city_view.mp4", h)
        fr = cl.at(t - t_in)
        fr = fr.resize((w, h))
        card = Image.new("RGBA", (w + 12, h + 12), CREAM + (255,))
        card.alpha_composite(fr, (6, 6))
        paste(f, B.shadowed(card, 10), c.mx(c.W - 620) - (w if c.rtl else 0) - 30, c.H * 0.55 - 40, ease((t - t_in) / 0.4))
        c.credit = CREDITS["R10_kobani_city_view.mp4"]
    return f


def icon(kind, s, colour=INK):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = tuple(colour) + (255,)
    w = max(3, s // 14)
    if kind == "house":
        d.polygon([(s * .15, s * .5), (s * .5, s * .18), (s * .85, s * .5)], outline=col, width=w)
        d.rectangle([s * .25, s * .5, s * .75, s * .85], outline=col, width=w)
    elif kind == "briefcase":
        d.rounded_rectangle([s * .15, s * .35, s * .85, s * .82], 6, outline=col, width=w)
        d.rectangle([s * .38, s * .2, s * .62, s * .35], outline=col, width=w)
    elif kind == "plane":
        d.polygon([(s * .1, s * .55), (s * .9, s * .35), (s * .95, s * .42), (s * .3, s * .65)], outline=col, width=w)
        d.polygon([(s * .45, s * .5), (s * .35, s * .2), (s * .45, s * .2), (s * .6, s * .45)], outline=col, width=w)
    elif kind == "rings":
        d.ellipse([s * .12, s * .3, s * .58, s * .76], outline=col, width=w)
        d.ellipse([s * .42, s * .3, s * .88, s * .76], outline=col, width=w)
    elif kind == "baby":
        d.ellipse([s * .35, s * .12, s * .65, s * .42], outline=col, width=w)
        d.rounded_rectangle([s * .28, s * .45, s * .72, s * .88], 14, outline=col, width=w)
    return im


def s06(c, t):
    f, _ = B.kenburns(c, "A12_family_album_hands.jpg", t, c.D, dark=0.4)
    terms = re.findall(r"«[^»]+»", c.ost[0]) or [c.ost[0]]
    ws = [("ar", "«الأجانب»", "«بیانییەکان»", "«biyanî»"), ("ar", "و«المكتومين»", "«مەکتومەکان»", "«mektûm»")]
    cw, ch = (640, 520) if not c.vert else (820, 430)
    kinds = ["house", "briefcase", "plane", "rings", "baby"]
    t_icons = c.at("بلا", "بێ", "Bê", nth=1 if c.lang == "ar" else 0, default=c.frac(0.55))
    for i, term in enumerate(terms[:2]):
        t0 = c.at(ws[i][1], ws[i][2], ws[i][3], default=c.frac(0.1 + 0.3 * i))
        def build(term=term):
            cd = B.card(cw, ch, CREAM)
            ti = T(c.lang, term, 84 if not c.vert else 74, INK, True)
            ti = B.fit_w(ti, cw - 60)
            cd.alpha_composite(ti, (cw // 2 - ti.width // 2, 40))
            ImageDraw.Draw(cd).line([(60, 70 + ti.height), (cw - 60, 70 + ti.height)], fill=SAFFRON + (255,), width=5)
            return cd
        cd = c.get(("s06card", i), build).copy()
        s = 96 if not c.vert else 84
        n = len(kinds)
        gap = (cw - 80 - n * s) / (n - 1)
        d = ImageDraw.Draw(cd)
        for j, kd in enumerate(kinds):
            ic = icon(kd, s)
            x = 40 + j * (s + gap)
            y = ch - s - (80 if not c.vert else 50)
            ka = clamp01((t - t_icons - j * 0.25) / 0.3)
            if ka > 0:
                paste(cd, ic, x, y, ka)
                kx = clamp01((t - t_icons - j * 0.25 - 0.3) / 0.3)
                if kx > 0:
                    kit.ink_line(d, [(x - 6, y + s + 6), (x + s + 6, y - 6)], kx, RED, 8)
        rot = -2 if i == 0 else 2
        cd = B.shadowed(cd.rotate(rot, resample=Image.BICUBIC, expand=True), 12)
        if not c.vert:
            cx = c.mx(c.W * (0.28 if i == 0 else 0.72))
            cy = c.H * 0.42
            frm = ("right" if c.rtl else "left") if i == 0 else ("left" if c.rtl else "right")
        else:
            cx, cy = c.W / 2, c.H * (0.30 if i == 0 else 0.60)
            frm = "right" if i == 0 else "left"
        B.place(f, cd, cx, cy, t, t0 - 0.3, frm)
    return f


BORDER = [(40.05, 36.80), (40.5, 36.98), (40.85, 37.08), (41.2, 37.07), (41.55, 37.08), (41.85, 37.14), (42.2, 37.30),
          (42.36, 37.11)]


def s07(c, t):
    mp, v = syria_map(c, c.W, c.H)
    f = mp.copy().convert("RGBA")
    t_strip = c.at("نُقلت", "خێزانی", "malbatên", default=c.frac(0.35))
    p = ease((t - t_strip) / 2.2)
    if p > 0:
        top = [v.xy(la + 0.0, lo) for lo, la in BORDER]
        bot = [v.xy(la - 0.17, lo) for lo, la in BORDER][::-1]
        n = len(top)
        m = max(2, int(round(n * p)))
        poly = top[:m] + [v.xy(BORDER[m - 1][1] - 0.17, BORDER[m - 1][0])] + bot[n - m:]
        lay = ink_layer(c)
        d = ImageDraw.Draw(lay)
        d.polygon(poly, fill=RED + (70,))
        mask = Image.new("L", (c.W, c.H), 0)
        ImageDraw.Draw(mask).polygon(poly, fill=255)
        hat = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
        hd = ImageDraw.Draw(hat)
        for k in range(-c.H, c.W, 14):
            hd.line([(k, c.H), (k + c.H, 0)], fill=RED + (200,), width=3)
        z = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
        z.paste(hat, (0, 0), mask)
        lay.alpha_composite(z)
        f.alpha_composite(lay)
    for key in ("hasakah", "qamishli"):
        city(c, f, v, key, t, 0.3, colour=INK, off=(40, 0) if key == "qamishli" else (-20, 60))
    t_sign = c.at("وتغيّرت", "ناوی", "navên", default=c.frac(0.65))
    sign = B.cut(c, "A04_blank_village_sign_wheat.jpg", w=560 if not c.vert else 700, border=10, rot=2, seed=7)
    if not c.vert:
        B.place(f, sign, c.mx(c.W * 0.22), c.H * 0.5, t, t_sign, "bottom")
    else:
        B.place(f, sign, c.W / 2, c.H * 0.68, t, t_sign, "bottom")
    if t > t_sign:
        c.illustration()
    parts = split(c.ost[0], "|")
    lower_strip(c, f, parts, t, 0.5, y=c.top)
    timeline_bar(c, f, t, 1973, 0.3, frm=1962)
    return f


def s08(c, t):
    f, _ = B.kenburns(c, "A03_old_radio_kitchen_night.jpg", t, c.D, z=(1.02, 1.08), dark=0.92, grain_amt=16)
    j = (int(t * 24) * 7919) % 3 - 1
    if j:
        f = f.transform(f.size, Image.AFFINE, (1, 0, j, 0, 1, (int(t * 24) * 104729) % 3 - 1), Image.BILINEAR)
    f = B.grade(f, (1.04, 0.98, 0.88), 0.85)
    t0 = c.at("تعلّمها", "منداڵان", "Zarokan", default=c.frac(0.45))
    k = ease((t - t0) / 1.2)
    if k > 0:
        im = big_text(c, c.ost[0], 80 if not c.vert else 72, CREAM)
        paste(f, im, c.W / 2 - im.width / 2, c.H * (0.2 if not c.vert else 0.25), k)
    return f


def s09(c, t):
    parts = split(c.ost[0], "|")
    t_bag = c.at("لكن", "بەڵام", "Lê", default=c.frac(0.6))
    if t < t_bag:
        f = B.paper_bg(c, t, c.D, 9)
        timeline_bar(c, f, t, 2011, 0.2, frm=1973, y=c.H * (0.30 if not c.vert else 0.28))
        if len(parts) > 1:
            t_n = c.at("مئة", "سەد", "sed", default=c.frac(0.3))
            u = clamp01((t - t_n + 0.2) / 1.8)
            txt = counter_text(parts[1], u) if t > t_n - 0.3 else parts[1].split("←")[0].split("→")[0]
            im = big_text(c, txt, 110 if not c.vert else 86, INK, c.W - 160)
            paste(f, im, c.W / 2 - im.width / 2, c.H * 0.50 - im.height / 2, ease((t - 0.6) / 0.5))
        yr = c.get(("s09yr",), lambda: T(c.lang, parts[0], 120, SAFFRON, True))
        paste(f, yr, c.W / 2 - yr.width / 2, c.H * (0.12 if not c.vert else 0.14), ease(t / 0.5))
        return f
    tt = t - t_bag
    f, _ = B.kenburns(c, "A06_suitcase_bus_station.jpg", tt, c.D - t_bag, z=(1.0, 1.07), dark=0.85)
    f = B.grade(f, (0.95, 0.95, 1.02), 0.8 - 0.3 * clamp01(tt / 3))
    lower_strip(c, f, [parts[0]], tt, 0.2, y=c.top)
    return f


def footage_fx(fr):
    return fr


def s10(c, t):
    t_sw = c.at("وفي", "لە", "Û", nth=0 if c.lang != "ckb" else 1, default=c.frac(0.33))
    a, b = "R07_damascus_dec2024_crowds.mp4", "R03_decree13_announcement.mp4"
    name, tc = (a, t + 2.0) if t < t_sw else (b, t - t_sw + 0.5)
    if c.vert:
        f = vert_bg_from_clip(c, name, tc)
    else:
        f = B.paper_bg(c, t, c.D, 10, tone=(30, 32, 36))
    box = framed_clip(c, f, name, t, tc)
    # whip-pan blur around the switch
    dt = t - t_sw
    if -0.18 < dt < 0.18:
        k = 1 - abs(dt) / 0.18
        f = f.filter(ImageFilter.BoxBlur(int(2 + 30 * k)))
    parts = split(c.ost[0], "|")
    dates = split(parts[0], "←", "→")
    lab_t = dates[0] if t < t_sw else (dates[1] if len(dates) > 1 else dates[0])
    y = box[3] + (30 if not c.vert else 40)
    tag(c, f, lab_t, t, 0.4 if t < t_sw else t_sw + 0.3, y=y)
    if t > t_sw and len(parts) > 1:
        lower_strip(c, f, [parts[1]], t, t_sw + 0.6, y=c.top - 60 if not c.vert else box[1] - 140)
    return f


def s11(c, t):
    f = B.dark_bg(c, 11)
    port = c.get(("mannheim",), lambda: kit.cutout(kit.fit(kit.sepia(B.load("R09_karl_mannheim_portrait.jpg"), 0.9), h=560),
                                                   torn=True, border=12, seed=11))
    cx = c.mx(c.W * 0.30) if not c.vert else c.W / 2
    cy = c.H * 0.45 if not c.vert else c.H * 0.33
    B.place(f, port, cx, cy, t, 0.2, "bottom")
    c.credit = CREDITS["R09_karl_mannheim_portrait.jpg"]
    tg = tag(c, f, lab("mannheim", c.lang), t, 0.9, x=None if c.vert else (cx - 190 if not c.rtl else cx - 190),
             y=cy + port.height / 2 - 20)
    t_eq = c.at("والشباب", "گەنجانی", "Ciwanên", default=c.frac(0.55))
    im = big_text(c, c.ost[0], 100 if not c.vert else 84, CREAM, c.W * 0.5 if not c.vert else c.W - 120)
    k = ease((t - (c.at("الأحداث", "ڕووداوە", "bûyerên", default=c.frac(0.3)) - 0.2)) / 0.8)
    if k > 0:
        x = c.mx(c.W * 0.70) - im.width / 2 if not c.vert else c.W / 2 - im.width / 2
        y = c.H * 0.40 if not c.vert else c.H * 0.62
        paste(f, kit.wipe(im, k, c.rtl), x, y)
    return f


def panel_bounds(c, i, n=3):
    if not c.vert:
        gw = 18
        w = (c.W - 2 * 60 - (n - 1) * gw) / n
        x = 60 + i * (w + gw)
        if c.rtl:
            x = c.W - x - w
        return int(x), 150, int(w), int(c.cap_top - 60 - 150)
    gh = 16
    top, bot = 250, c.cap_top - 40
    h = (bot - top - (n - 1) * gh) / n
    return 50, int(top + i * (h + gh)), c.W - 100, int(h)


def s12(c, t):
    f = B.paper_bg(c, t, c.D, 12)
    labels = split(c.ost[0], "·", "•")
    keys = [("الحرب", "جەنگ", "şer"), ("والهجرة", "کۆچ", "koçberî"), ("والفضاء", "جیهانی", "qada")]
    for i in range(3):
        x, y, w, h = panel_bounds(c, i)
        t0 = c.at(*keys[i], default=c.frac(0.2 + 0.25 * i)) - 0.4
        k = ease_out((t - t0) / 0.6)
        if k <= 0:
            continue
        tc = t - t0
        if i == 0:
            cl = B.clip(c, "R06_aleppo_jan2026_news.mp4", h if not c.vert else int(w * 9 / 16) + 2, start=4.0)
            fr = cl.at(tc)
            s = max(w / fr.width, h / fr.height)
            fr = fr.resize((int(fr.width * s) + 1, int(fr.height * s) + 1), Image.BILINEAR)
            im = fr.crop(((fr.width - w) // 2, (fr.height - h) // 2, (fr.width - w) // 2 + w, (fr.height - h) // 2 + h))
            im = B.grade(im, sat=0.6)
            c.credit = CREDITS["R06_aleppo_jan2026_news.mp4"]
        elif i == 1:
            im = B.photo_box(c, "A06_suitcase_bus_station.jpg", w, h, tc, c.D, (1.05, 1.1))
            d = ImageDraw.Draw(im)
            pts = [(w * 0.2, h * 0.65), (w * 0.5, h * 0.45), (w * 0.82, h * 0.25)] if not c.rtl else \
                  [(w * 0.8, h * 0.65), (w * 0.5, h * 0.45), (w * 0.18, h * 0.25)]
            p = clamp01((tc - 0.6) / 2.0)
            kit.dotted(d, kit.curve(pts[0], pts[1], 0.15) + kit.curve(pts[1], pts[2], 0.15), p, SAFFRON, 5, 16)
            for j, key in enumerate(("qamishli", "erbil", "berlin")):
                if p * 2 >= j * 1.0 - 0.05:
                    x0, y0 = pts[j]
                    d.ellipse([x0 - 9, y0 - 9, x0 + 9, y0 + 9], fill=CREAM + (255,), outline=INK + (255,), width=3)
                    nm = T(c.lang, LABELS["cities"][key][c.lang], 30, CREAM, True)
                    paste(im, nm, x0 - nm.width / 2, y0 + 10)
            c.illustration()
        else:
            im = B.photo_box(c, "A05_phone_in_hands_music.jpg", w, h, tc, c.D, (1.0, 1.08), (0.5, 0.45), (0.5, 0.45))
            c.illustration()
        im = B.darken(im, 0.92)
        if i < len(labels):
            lb = B.strip_img(c.lang, labels[i], 44 if not c.vert else 42, INK, SAFFRON)
            paste(im, lb, w / 2 - lb.width / 2, h - lb.height - 16)
        fr2 = Image.new("RGBA", (w + 10, h + 10), CREAM + (255,))
        fr2.alpha_composite(im, (5, 5))
        paste(f, B.shadowed(fr2, 8, (6, 8), 90), x - 5 - 24, y - 5 - 24 + (1 - k) * 60, k)
    return f


def s13(c, t):
    t_echo = c.at("لكن", "بەڵام", "Lê", default=c.frac(0.55))
    echo = clamp01((t - t_echo) / 2.0)
    f, scr = m3(c, t, c.D, echo)
    c.illustration()
    # invented app UI: song cards floating over the screen
    x0, y0, x1, y1 = scr
    for k in range(3):
        tk = 0.8 + k * 0.5
        a = ease((t - tk) / 0.5) * (1 - echo * 0.6)
        if a <= 0:
            continue
        cw, ch = int((x1 - x0) * 0.9), 70
        cd = B.card(cw, ch, (250, 246, 238), 14)
        d = ImageDraw.Draw(cd)
        d.rounded_rectangle([10, 10, 60, 60], 10, fill=(SAFFRON, GREEN, RED)[k] + (255,))
        nt = T("kmr", "♪", 40, CREAM, True) if False else None
        d.text((24, 16), "", fill=INK)
        d.rounded_rectangle([76, 18, cw - 40, 30], 5, fill=(40, 40, 40, 200))
        d.rounded_rectangle([76, 40, cw * 0.6, 50], 5, fill=(120, 120, 120, 180))
        yy = y0 + (y1 - y0) * (0.15 + 0.2 * k) + math.sin(t * 1.3 + k) * 6
        xx = (x0 + x1) / 2 - cw / 2 + (c.W * 0.22 if not c.vert else 0) * (1 if not c.rtl else -1) * (1 if k % 2 else 0.6)
        paste(f, B.shadowed(cd, 8, (4, 6), 80), xx - 24, yy - 24, a)
    lower_strip(c, f, [c.ost[0]], t, c.frac(0.15), y=c.top - 20)
    return f


def s14(c, t):
    f = B.paper_bg(c, t, c.D, 14)
    ka, ks = LABELS["venn"][c.lang]
    if not c.vert:
        cy, r, dx = c.H * 0.45, 260, 170
    else:
        cy, r, dx = c.H * 0.40, 230, 140
    c1x, c2x = (c.W / 2 + dx, c.W / 2 - dx) if c.rtl else (c.W / 2 - dx, c.W / 2 + dx)
    t1 = c.at("كرديًا", "کوردبوون", "Kurdbûn", default=c.frac(0.2))
    t2 = c.at("سوريًا", "سووریبووندا", "Sûrîbûnê", default=c.frac(0.3))
    t_over = c.at("المزدوجة", "دووانەی", "dualî", default=c.frac(0.6))
    t_key = c.at("بشرط", "مەرج", "şertî", default=c.frac(0.8))
    lay = ink_layer(c)
    d = ImageDraw.Draw(lay)
    po = ease((t - t_over) / 0.8)
    if po > 0:
        ov = Image.new("L", (c.W, c.H), 0)
        m1_ = Image.new("L", (c.W, c.H), 0)
        ImageDraw.Draw(m1_).ellipse([c1x - r, cy - r, c1x + r, cy + r], fill=255)
        m2_ = Image.new("L", (c.W, c.H), 0)
        ImageDraw.Draw(m2_).ellipse([c2x - r, cy - r, c2x + r, cy + r], fill=255)
        from PIL import ImageChops
        ov = ImageChops.multiply(m1_, m2_).point(lambda v: int(v * 0.8 * po))
        fill = Image.new("RGBA", (c.W, c.H), SAFFRON + (255,))
        fill.putalpha(ov)
        lay.alpha_composite(fill)
    for (x, t0, seed) in ((c1x, t1, 1), (c2x, t2, 2)):
        p = clamp01((t - t0 + 0.3) / 1.0)
        if p > 0:
            kit.ink_line(d, kit.ellipse_pts((x - r, cy - r, x + r, cy + r), 1.03, seed), p, INK, 7)
    f.alpha_composite(lay)
    for (x, lbl, t0, sgn) in ((c1x, ka, t1, 1), (c2x, ks, t2, -1)):
        im = c.get(("venn", lbl), lambda lbl=lbl: T(c.lang, lbl, 64 if not c.vert else 56, INK, True))
        xx = x + sgn * (r * 0.45) * (1 if (x > c.W / 2) else -1) * sgn
        xx = x + (r * 0.42 if x > c.W / 2 else -r * 0.42)
        paste(f, im, xx - im.width / 2, cy - im.height / 2, ease((t - t0) / 0.5))
    parts = split(c.ost[0], "=")
    if po > 0.5:
        both = parts[0]
        im = c.get(("venn_both",), lambda: T(c.lang, both, 40 if not c.vert else 36, INK, True))
        paste(f, im, c.W / 2 - im.width / 2, cy - im.height / 2, po)
    rest = parts[1] if len(parts) > 1 else ""
    pieces = split(rest, "←", "→")
    if len(pieces) > 1:
        lower_strip(c, f, [pieces[0]], t, t_over + 0.6, y=cy + r + 20, size=46)
        st = tag(c, f, "🔑" if False else pieces[1], t, t_key, y=cy + r + 110 if not c.vert else cy + r + 120,
                 x=None)
    return f


def s15(c, t):
    f = B.paper_bg(c, t, c.D, 15)
    parts = split(c.ost[0], "|")
    t_a = c.at("الشاب", "ئەو", "ciwanê", default=c.frac(0.2))
    t_b = c.at("أما", "بەڵام", "Lê", default=c.frac(0.55))
    for i, (name, t0) in enumerate((("A06_suitcase_bus_station.jpg", t_a), ("A07_empty_classroom.jpg", t_b))):
        if not c.vert:
            w, h = c.W // 2 - 90, c.cap_top - 260
            x = c.mx(60 + i * (w + 60)) - (w if c.rtl else 0)
            y = 150
        else:
            w, h = c.W - 100, (c.cap_top - 300) // 2 - 20
            x, y = 50, 220 + i * (h + 40)
        k = ease_out((t - t0 + 0.4) / 0.6)
        if k <= 0:
            continue
        im = B.photo_box(c, name, w, h, t, c.D, (1.0, 1.06))
        if i == 0:
            im = B.grade(im, (0.8, 0.82, 0.9), 0.4 + 0.6 * (1 - clamp01((t - t0) / 2)))
        else:
            im = B.grade(im, (1.0 + 0.12 * clamp01((t - t0) / 2),) * 3, 1.0)
        if i < len(parts):
            ar = split(parts[i], "←", "→")
            lb = B.strip_img(c.lang, parts[i], 44 if not c.vert else 42, INK, SAFFRON if i else CREAM)
            lb = B.fit_w(lb, w - 20)
            paste(im, lb, w / 2 - lb.width / 2, h - lb.height - 20)
        fr = Image.new("RGBA", (w + 12, h + 12), CREAM + (255,))
        fr.alpha_composite(im, (6, 6))
        paste(f, B.shadowed(fr, 10), x - 6 - 30, y - 6 - 30, k)
        c.illustration()
    return f


def bubble(c, text, size, w):
    im = T(c.lang, text, size, INK, True)
    w = max(w, im.width + 80)
    h = int(im.height * 0.95) + 50
    out = Image.new("RGBA", (w + 10, h + 50), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    d.rounded_rectangle([0, 0, w, h], h // 2.5, fill=CREAM + (255,), outline=INK + (255,), width=4)
    tx = w * (0.78 if c.rtl else 0.22)
    d.polygon([(tx - 18, h - 2), (tx + 18, h - 2), (tx + (14 if c.rtl else -14), h + 40)], fill=CREAM + (255,))
    d.line([(tx - 18, h - 1), (tx + (14 if c.rtl else -14), h + 40), (tx + 18, h - 1)], fill=INK + (255,), width=4)
    out.alpha_composite(im, (int(w / 2 - im.width / 2), int(h / 2 - im.height / 2)))
    return out


def s16(c, t):
    f = B.paper_bg(c, t, c.D, 16)
    items = split(c.ost[0], "·", "•")
    keys = [("معظمهم", "زۆربەیان", "piraniya"), ("بعضهم", "هەندێکیان", "Hinek"), ("وقلّةٌ", "کەمێکیان", "hindikek")]
    sizes = [96, 70, 50] if not c.vert else [80, 60, 44]
    y = 170 if not c.vert else 330
    for i, it in enumerate(items[:3]):
        b = c.get(("bub", i), lambda it=it, i=i: bubble(c, it, sizes[i], 300))
        t0 = c.at(*keys[i], default=c.frac(0.15 + 0.2 * i))
        x = c.W / 2 - b.width / 2 + (60 * i if not c.rtl else -60 * i) * (0 if c.vert else 1)
        B.place(f, B.shadowed(b, 8, (5, 7), 70), x + b.width / 2, y + b.height / 2, t, t0 - 0.2, "bottom", dist=200)
        y += b.height + (16 if not c.vert else 30)
    tag(c, f, lab("qual", c.lang), t, c.frac(0.75), y=y + 10, fill=INK, fg=CREAM, size=26)
    return f


def s17(c, t):
    f, _ = B.kenburns(c, "A10_hands_writing_notebook.jpg", t, c.D, dark=0.45)
    cw, ch = (1300, 520) if not c.vert else (980, 620)
    cd = c.get(("q17",), lambda: B.card(cw, ch, (24, 26, 30), 16))
    k = ease_out((t - 0.3) / 0.6)
    x, y = c.W / 2 - cw / 2, c.H * (0.42 if not c.vert else 0.42) - ch / 2
    paste(f, cd, x, y + (1 - k) * 40, 0.92 * k)
    q = T("ar" if c.lang != "kmr" else "kmr", "«" if c.rtl else "“", 260, SAFFRON, True)
    paste(f, q, x + (cw - q.width - 30 if c.rtl else 30), y - 60, k)
    ost = c.ost[0]
    m = re.search(r"«[^»]+»", ost)
    t_hi = c.at("«مقاومة", "«بەرگرییەکی", "«berxwedaneke", default=c.frac(0.4))
    im = big_text(c, ost, 92 if not c.vert else 80, CREAM, cw - 120)
    paste(f, im, c.W / 2 - im.width / 2, y + ch / 2 - im.height / 2 + 20, ease((t - 0.6) / 0.6))
    if m:
        hi = m.group(0)
        p = clamp01((t - t_hi) / 0.8)
        if p > 0:
            hm = big_text(c, hi, 92 if not c.vert else 80, SAFFRON, cw - 120)
            # overlay the highlighted phrase in saffron on its position: re-render the line with colour runs
            pre, post = ost[:m.start()], ost[m.end():]
            line = c.get(("q17hl",), lambda: _colour_line(c, [(pre, CREAM), (hi, SAFFRON), (post, CREAM)],
                                                         92 if not c.vert else 80, cw - 120))
            if line is not None:
                paste(f, line, c.W / 2 - line.width / 2, y + ch / 2 - line.height / 2 + 20, p)
    return f


def _colour_line(c, runs, size, maxw):
    """One line made of differently coloured runs (shaped separately, joined in reading order)."""
    ims = [(T(c.lang, s.strip(), size, col, True), s) for s, col in runs if s.strip()]
    sp = size * 0.28
    order = ims[::-1] if c.rtl else ims
    w = int(sum(i.width - 12 for i, _ in order) + sp * (len(order) - 1) + 12)
    h = max(i.height for i, _ in order)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = 0
    for im, _ in order:
        out.alpha_composite(im, (int(x), (h - im.height) // 2))
        x += im.width - 12 + sp
    if out.width > maxw:
        return None
    return out


def s18(c, t):
    f = B.paper_bg(c, t, c.D, 18)
    if not c.vert:
        w, h = c.W // 2 - 60, c.cap_top - 200
        x = c.W - 60 - w if c.rtl else 60
        im = B.photo_box(c, "A15_village_mosque_dawn.jpg", w, h, t, c.D, (1.0, 1.06))
        fr = Image.new("RGBA", (w + 12, h + 12), CREAM + (255,))
        fr.alpha_composite(im, (6, 6))
        paste(f, B.shadowed(fr, 10), x - 36, 130 - 36, ease(t / 0.5))
        col = (60, c.W // 2 - 20) if c.rtl else (c.W // 2 + 20, c.W - 60)
        ytop = 260
    else:
        w, h = c.W - 100, 620
        im = B.photo_box(c, "A15_village_mosque_dawn.jpg", w, h, t, c.D, (1.0, 1.06))
        fr = Image.new("RGBA", (w + 12, h + 12), CREAM + (255,))
        fr.alpha_composite(im, (6, 6))
        paste(f, B.shadowed(fr, 10), 50 - 36, 230 - 36, ease(t / 0.5))
        col = (60, c.W - 60)
        ytop = 940
    c.illustration()
    head, rest = (split(c.ost[0], ":") + [""])[:2]
    items = split(rest, "·", "•")
    t_a = c.at("الحضور", "ئامادەیی", "Hebûna", default=c.frac(0.2))
    t_b = c.at("ليس", "ئەوە", "ne", nth=0, default=c.frac(0.6))
    strips(c, f, [head], t, 0.5, col=col, y=ytop - 110, size=60, colours=[INK], bgs=[SAFFRON], align="center" if c.vert else None)
    for i, (it, t0, mark, colr) in enumerate(((items[0] if items else "", t_a, "✓", GREEN),
                                              (items[1] if len(items) > 1 else "", t_b, "✗", RED))):
        if not it:
            continue
        line = f"{mark} {it}" if not c.rtl else f"{mark} {it}"
        im = c.get(("s18", i), lambda line=line, colr=colr: B.strip_img(c.lang, line, 52 if not c.vert else 48, INK, CREAM))
        im = B.fit_w(im, col[1] - col[0])
        k = ease_out((t - t0) / 0.5)
        if k > 0:
            xx = col[1] - im.width if c.rtl else col[0]
            if c.vert:
                xx = c.W / 2 - im.width / 2
            paste(f, im, xx + (1 - k) * (60 if c.rtl else -60), ytop + 40 + i * 120, k)
    return f


def s19(c, t):
    f = clip_bg(c, "R04_nowruz_qamishli_2026.mp4", t, dark=0.38, blur=6, sat=0.8)
    items = c.ost
    n = len(items)
    t0s = [c.frac(0.08 + 0.84 * i / n) for i in range(n)]
    size = 54 if not c.vert else 50
    y = 170 if not c.vert else 330
    for i, it in enumerate(items):
        k = ease_out((t - t0s[i]) / 0.45)
        im = c.get(("chk", i), lambda it=it: B.strip_img(c.lang, it, size, INK, CREAM))
        im = B.fit_w(im, c.W - 2 * c.margin)
        if k > 0:
            x = (c.W - c.margin - im.width) if c.rtl else c.margin
            if c.vert:
                x = c.W / 2 - im.width / 2
            paste(f, im, x + (1 - k) * (120 if c.rtl else -120), y, k)
        y += im.height + (8 if not c.vert else 22)
    return f


def s20(c, t):
    name = "R06_aleppo_jan2026_news.mp4"
    f = vert_bg_from_clip(c, name, t) if c.vert else B.paper_bg(c, t, c.D, 20, tone=(30, 32, 36))
    box = framed_clip(c, f, name, t)
    t_q = c.at("«خطوة", "«هەنگاوی", "«gava", default=c.frac(0.65))
    k = ease_out((t - t_q) / 0.5)
    if k > 0:
        q = c.get(("q20",), lambda: B.strip_img(c.lang, c.ost[0], 96 if not c.vert else 86, INK, SAFFRON, rot=-2))
        paste(f, q, c.W / 2 - q.width / 2, box[3] - q.height / 2 + (1 - k) * 40, k)
        tag(c, f, lab("kadmin", c.lang), t, t_q + 0.3, y=box[3] + q.height / 2 + 10, fill=CREAM)
    return f


def s21(c, t):
    f = B.paper_bg(c, t, c.D, 21)
    lines = c.ost
    x0, x1 = c.margin + 40, c.W - c.margin - 40
    maxv = 600
    span = x1 - x0

    def X(v):
        return x1 - span * v / maxv if c.rtl else x0 + span * v / maxv
    if not c.vert:
        ys = [330, 600]
        axis_y = 760
        bh = 90
    else:
        ys = [560, 920]
        axis_y = 1150
        bh = 110
    d = ImageDraw.Draw(f)
    pa = ease(t / 0.8)
    d.line([(x0, axis_y), (x0 + (x1 - x0) * pa, axis_y)] if not c.rtl else [(x1, axis_y), (x1 - (x1 - x0) * pa, axis_y)],
           fill=INK + (255,), width=3)
    for v in range(0, maxv + 1, 100):
        if pa >= v / maxv:
            xx = X(v)
            d.line([(xx, axis_y - 10), (xx, axis_y + 10)], fill=INK + (255,), width=3)
            im = T(c.lang, digits(c, v), 28, INK, True)
            paste(f, im, xx - im.width / 2, axis_y + 12)
    t_h = c.at("سجلات", "تۆمارەکانی", "tomarên", default=c.frac(0.2))
    t_a = c.at("منظمة", "ڕێکخراوی", "Rêxistina", default=c.frac(0.6))
    # Hasakah registry: bar to 517
    p = ease((t - t_h - 0.3) / 1.6)
    if p > 0:
        xa, xb = X(0), X(517 * p)
        d.rectangle([min(xa, xb), ys[0], max(xa, xb), ys[0] + bh], fill=RED + (230,))
    # Amnesty range band 200-360
    p2 = ease((t - t_a - 0.3) / 1.2)
    if p2 > 0:
        xa, xb = X(200), X(200 + 160 * p2)
        lay = ink_layer(c)
        dl = ImageDraw.Draw(lay)
        dl.rectangle([min(xa, xb), ys[1], max(xa, xb), ys[1] + bh], fill=SAFFRON + (170,))
        for k in range(int(min(xa, xb)), int(max(xa, xb)), 16):
            dl.line([(k, ys[1] + bh), (k + bh * 0.6, ys[1])], fill=INK + (90,), width=2)
        dl.rectangle([min(xa, xb), ys[1], max(xa, xb), ys[1] + bh], outline=INK + (255,), width=3)
        f.alpha_composite(lay)
    for i, (ln, t0) in enumerate(zip(lines[:2], (t_h, t_a))):
        im = c.get(("s21l", i), lambda ln=ln: B.fit_w(B.strip_img(c.lang, ln, 46 if not c.vert else 40, INK, CREAM),
                                                     c.W - 2 * c.margin))
        k = ease_out((t - t0) / 0.5)
        if k > 0:
            x = (x1 + 30 - im.width) if c.rtl else x0 - 30
            if c.vert:
                x = c.W / 2 - im.width / 2
            paste(f, im, x, ys[i] - im.height - 10, k)
    return f


def blur_faces(fr):
    """Pixelate + blur every detected face (YuNet, OpenCV zoo)."""
    import cv2
    arr = np.asarray(fr.convert("RGB")).copy()
    det = _face_det(arr.shape[1], arr.shape[0])
    _, faces = det.detect(cv2.cvtColor(arr, cv2.COLOR_RGB2BGR))
    for fc in (faces if faces is not None else []):
        x, y, w, h = [int(v) for v in fc[:4]]
        x0, y0 = max(0, x - w // 3), max(0, y - h // 3)
        x1, y1 = min(arr.shape[1], x + w + w // 3), min(arr.shape[0], y + h + h // 3)
        if x1 - x0 < 4 or y1 - y0 < 4:
            continue
        roi = arr[y0:y1, x0:x1]
        roi = cv2.resize(cv2.resize(roi, (max(1, (x1 - x0) // 9), max(1, (y1 - y0) // 9))), (x1 - x0, y1 - y0),
                         interpolation=cv2.INTER_NEAREST)
        arr[y0:y1, x0:x1] = cv2.GaussianBlur(roi, (0, 0), 5)
    return Image.fromarray(arr).convert("RGBA")


_FD = {}


def _face_det(w, h):
    if (w, h) not in _FD:
        import cv2
        _FD[(w, h)] = cv2.FaceDetectorYN.create(str(B.CACHE / "yunet.onnx"), "", (w, h), 0.6, 0.3, 5000)
    return _FD[(w, h)]


def s22(c, t):
    name = "R05_student_protests_sep2026.mp4"
    t_cls = c.at("الدراسة", "توێژینەوەکە", "Lêkolîn", default=c.frac(0.6))
    lines = c.ost
    if t < t_cls:
        f = vert_bg_from_clip(c, name, t) if c.vert else B.paper_bg(c, t, c.D, 22, tone=(30, 32, 36))
        box = framed_clip(c, f, name, t, prep=blur_faces, start=0.0)
        if c.vert:
            f = f  # background is already blurred
        lower_strip(c, f, [lines[0]], t, 0.4, y=box[3] - 110 if not c.vert else box[3] + 40)
        return f
    tt = t - t_cls
    f, _ = B.kenburns(c, "A07_empty_classroom.jpg", tt, c.D - t_cls, dark=0.55)
    if len(lines) > 1:
        headline(c, f, lines[1], tt, 0.2, 96 if not c.vert else 80, c.H * 0.38)
    tag(c, f, "⚠ " + lab("differ", c.lang), tt, 0.7, y=c.H * 0.38 + 120, fill=SAFFRON)
    return f


def verdict(c, t, bg=None, extra=None):
    ost = c.ost[0]
    m = re.match(r"(.*?[؟?])\s*([✗◐✓])\s*(.*)", ost)
    claim, mark, verd = (m.group(1), m.group(2), m.group(3)) if m else (ost, "", "")
    if bg:
        f = bg
    else:
        f = B.paper_bg(c, t, c.D, 23)
    cy = c.H * (0.36 if not c.vert else 0.34)
    strip = c.get(("vclaim",), lambda: B.strip_img(c.lang, claim, 92 if not c.vert else 76, INK, CREAM, pad=(40, 22), rot=-1.5))
    strip = B.fit_w(strip, c.W - 80)
    k = ease_out((t - 0.3) / 0.6)
    paste(f, strip, c.W / 2 - strip.width / 2 + (1 - k) * (200 if c.rtl else -200), cy - strip.height / 2, k)
    t_v = c.at("هل", "ئایا", "Ma", default=c.frac(0.3)) if c.id == "S23" else c.frac(0.28)
    if c.id == "S24":
        t_v = c.at("هذا", "ئەمە", "Ev", default=c.frac(0.3))
    if c.id == "S25":
        t_v = c.at("هذا", "ئەمە", "Ev", default=c.frac(0.3))
    if c.id == "S26":
        t_v = c.at("الدراسة", "توێژینەوەکە", "Lêkolîn", default=c.frac(0.45))
    kv = clamp01((t - t_v) / 0.3)
    if kv > 0 and mark:
        colr = RED if mark == "✗" else SAFFRON
        st = c.get(("vstamp", mark), lambda: _stamp(c, mark, verd, colr))
        s = 1 + 0.7 * (1 - back_out(kv, 2.0))
        im = st.resize((int(st.width * s), int(st.height * s)), Image.BILINEAR)
        paste(f, im, c.W / 2 - im.width / 2, cy + strip.height / 2 + 40 + st.height / 2 - im.height / 2, clamp01(kv * 3))
    if extra:
        extra(f, t, t_v)
    return f


def _stamp(c, mark, verd, colr):
    mk = T("kmr", mark, 120, colr, True)
    tx = B.fit_w(T(c.lang, verd, 72 if not c.vert else 62, colr, True), c.W - 300)
    w = mk.width + tx.width + 90
    h = max(mk.height, tx.height) + 30
    im = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([4, 4, w - 5, h - 5], 18, outline=tuple(colr) + (235,), width=8, fill=CREAM + (210,))
    order = [(mk, 0), (tx, 1)]
    if c.rtl:
        order = order[::-1]
    x = 30
    for piece, _ in order:
        im.alpha_composite(piece, (int(x), int(h / 2 - piece.height / 2)))
        x += piece.width + 10
    a = np.asarray(im).copy()
    n = np.random.default_rng(3).random(a.shape[:2])
    a[..., 3] = (a[..., 3] * np.where(n < 0.12, 0.5, 1.0)).astype(np.uint8)
    return Image.fromarray(a, "RGBA").rotate(-4, resample=Image.BICUBIC, expand=True)


def s23(c, t):
    return verdict(c, t)


def s24(c, t):
    if not c.vert:
        f = B.paper_bg(c, t, c.D, 24)
        w, h = c.W // 2 - 80, 420
        for i, name in enumerate(("A07_empty_classroom.jpg",)):
            pass
        im = B.photo_box(c, "A07_empty_classroom.jpg", c.W, c.H, t, c.D, (1.0, 1.05))
        f = B.darken(im, 0.5)
    else:
        f, _ = B.kenburns(c, "A07_empty_classroom.jpg", t, c.D, dark=0.5)
    c.illustration()
    return verdict(c, t, bg=f)


def scale_icon(tilt, s=200):
    im = Image.new("RGBA", (s * 2, s + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, top = s, 30
    d.line([(cx, top), (cx, s)], fill=INK + (255,), width=6)
    d.polygon([(cx - 50, s + 20), (cx + 50, s + 20), (cx, s - 20)], fill=INK + (255,))
    a = math.radians(tilt)
    L = s * 0.8
    x0, y0 = cx - L * math.cos(a), top + 20 - L * math.sin(a)
    x1, y1 = cx + L * math.cos(a), top + 20 + L * math.sin(a)
    d.line([(x0, y0), (x1, y1)], fill=INK + (255,), width=6)
    for (x, y) in ((x0, y0), (x1, y1)):
        d.line([(x, y), (x - 40, y + 70)], fill=INK + (255,), width=3)
        d.line([(x, y), (x + 40, y + 70)], fill=INK + (255,), width=3)
        d.chord([x - 50, y + 40, x + 50, y + 100], 0, 180, fill=SAFFRON + (255,), outline=INK + (255,))
    return im


def s25(c, t):
    def extra(f, t, t_v):
        tilt = 7 * ease((t - t_v - 0.3) / 1.5) * (1 if c.rtl else -1) + math.sin(t * 2) * 0.8
        sc = scale_icon(tilt, 150 if not c.vert else 170)
        y = c.H * 0.62 if not c.vert else c.H * 0.58
        paste(f, sc, c.W / 2 - sc.width / 2, y, ease((t - 0.8) / 0.6))
    return verdict(c, t, extra=extra)


def s26(c, t):
    a = B.photo_box(c, "A15_village_mosque_dawn.jpg", c.W, c.H, t, c.D, (1.0, 1.05))
    b = B.photo_box(c, "A10_hands_writing_notebook.jpg", c.W, c.H, t, c.D, (1.05, 1.0))
    u = clamp01((t - c.frac(0.4)) / 3.0)
    f = Image.blend(a, b, ease(u) * 0.55)
    f = B.darken(f, 0.5)
    c.illustration()
    return verdict(c, t, bg=f)


def scen(c, t, n, keys):
    parts = split(c.ost[0], "|")
    cool = 1.0 if n == 2 else 0.0
    f = m4(c, t, c.D, glow=n, glow_t0=c.at(*keys, default=c.frac(0.1)), zoom=(1.15, 1.0) if n == 1 else (1.02, 1.0),
           rot=(1.0, 0.0) if n == 1 else (0.0, 0.0), cool=cool * clamp01(t / 1.5))
    lower_strip(c, f, parts, c.frac(0.0) if False else t, c.at(*keys, default=c.frac(0.1)) - 0.2, y=c.top - 20,
                colours=[INK, INK], bgs=[SAFFRON, CREAM])
    return f


def s27(c, t):
    return scen(c, t, 1, ("الأول", "یەکەم", "yekem"))


def s28(c, t):
    return scen(c, t, 2, ("الثاني", "دووەم", "duyem"))


def s29(c, t):
    t_sw = c.frac(0.35)
    if t < t_sw:
        return scen(c, t, 3, ("والثالث", "سێیەم", "sêyem"))
    tt = t - t_sw
    f, _ = B.kenburns(c, "A14_waiting_by_window.jpg", tt, c.D - t_sw, z=(1.0, 1.06), dark=0.92)
    f = B.grade(f, (0.97, 0.98, 1.02), 0.85)
    parts = split(c.ost[0], "|")
    lower_strip(c, f, parts, tt, 0.0 - 1, y=c.top - 20, colours=[INK, INK], bgs=[SAFFRON, CREAM])
    # the clock tick: a small clock icon
    return f


def s30(c, t):
    f = m2(c, t, c.D)
    f = B.grade(f, (1.05, 1.0, 0.92))
    lines = c.ost
    t1 = c.at("إن", "ئەگەر", "Heke", 0, default=c.frac(0.2))
    t2 = c.at("وإن", "ئەگەر", "Heke", 0 if c.lang == "ar" else 1, default=c.frac(0.55))
    for i, (ln, t0) in enumerate(zip(lines[:2], (t1, t2))):
        headline(c, f, ln, t, t0, 84 if not c.vert else 72, c.H * ((0.22 + 0.17 * i) if not c.vert else (0.24 + 0.14 * i)))
    return f


def puzzle(c, text, w, h, tab_side, colr):
    im = Image.new("RGBA", (w + 80, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0 = 40
    d.rounded_rectangle([x0, 0, x0 + w, h - 1], 16, fill=tuple(colr) + (255,), outline=INK + (255,), width=4)
    r = h * 0.16
    cy = h / 2
    if tab_side == "right":
        d.ellipse([x0 + w - r, cy - r, x0 + w + r, cy + r], fill=tuple(colr) + (255,), outline=INK + (255,), width=4)
        d.rectangle([x0 + w - r - 2, cy - r + 4, x0 + w - 2, cy + r - 4], fill=tuple(colr) + (255,))
    else:
        d.ellipse([x0 - r, cy - r, x0 + r, cy + r], fill=CREAM + (0,), outline=INK + (255,), width=4)
    tx = B.fit_w(T(c.lang, text, 58 if not c.vert else 52, INK, True), w - 60)
    im.alpha_composite(tx, (int(x0 + w / 2 - tx.width / 2), int(cy - tx.height / 2)))
    return im


def s31(c, t):
    f = B.paper_bg(c, t, c.D, 31)
    parts = split(c.ost[0], "+")
    if len(parts) < 2:
        headline(c, f, c.ost[0], t, 0.4, 90, c.H * 0.4, INK)
        return f
    t_a = c.at("يحفظ", "بپارێزێت", "biparêze", default=c.frac(0.6))
    t_b = c.at("مصالح", "بەرژەوەندیی", "berjewendiyên", default=c.frac(0.8))
    t_l = t_b + 0.8
    if not c.vert:
        w, h = 640, 220
        lock = ease((t - t_l) / 0.6)
        gap = 140 * (1 - lock) + 10
        cy = c.H * 0.42
        first_x = c.W / 2 + (gap / 2 + w / 2) if c.rtl else c.W / 2 - (gap / 2 + w / 2)
        second_x = c.W / 2 - (gap / 2 + w / 2) if c.rtl else c.W / 2 + (gap / 2 + w / 2)
        pa = c.get(("pz", 0), lambda: puzzle(c, parts[0], w, h, "left" if c.rtl else "right", CREAM))
        pb = c.get(("pz", 1), lambda: puzzle(c, parts[1], w, h, "right" if c.rtl else "left", SAFFRON))
        B.place(f, B.shadowed(pa, 8), first_x, cy, t, t_a - 0.3, "right" if c.rtl else "left")
        B.place(f, B.shadowed(pb, 8), second_x, cy, t, t_b - 0.3, "left" if c.rtl else "right")
        plus = T("kmr", "+", 110, INK, True)
        paste(f, plus, c.W / 2 - plus.width / 2, cy - 260, ease((t - t_b) / 0.4))
    else:
        w, h = 820, 220
        lock = ease((t - t_l) / 0.6)
        pa = c.get(("pz", 0), lambda: puzzle(c, parts[0], w, h, "right", CREAM))
        pb = c.get(("pz", 1), lambda: puzzle(c, parts[1], w, h, "left", SAFFRON))
        B.place(f, B.shadowed(pa, 8), c.W / 2, c.H * 0.30, t, t_a - 0.3, "top")
        B.place(f, B.shadowed(pb, 8), c.W / 2, c.H * 0.30 + h + 60 * (1 - lock) + 20, t, t_b - 0.3, "bottom")
        plus = T("kmr", "+", 110, INK, True)
        paste(f, plus, c.W / 2 - plus.width / 2, c.H * 0.30 + h / 2 + 10, ease((t - t_b) / 0.4) * (1 - lock))
    return f


def s32(c, t):
    yr = "١٩٦٢" if c.lang in ("ar", "ckb") else "1962"
    t_end = 1.6
    t_here = c.at("نحن", "ئێمە", "Em", default=c.frac(0.85))
    if t < t_end:
        f = B.dark_bg(c, 32)
        im = c.get(("yr32",), lambda: T(c.lang, yr, 300 if not c.vert else 280, CREAM, True))
        paste(f, im, c.W / 2 - im.width / 2, c.H * 0.4 - im.height / 2, 1 - ease((t - 0.8) / 0.8))
        return f
    tt = t - t_end
    f = m1(c, tt, c.D - t_end, title=c.ost[0], title_t0=t_here - t_end, title_size=300 if not c.vert else 170, title_y=c.H * 0.2,
           z_bg=(1.0, 1.05), z_p=(1.0, 1.12))
    k = 1 - ease(tt / 0.8)
    if k > 0:
        paste(f, Image.new("RGBA", (c.W, c.H), DARK + (255,)), 0, 0, k)
    return f


def s33(c, t):
    f = B.dark_bg(c, 33)
    t0 = c.at("أيّ", "چ", "çi", default=c.frac(0.2))
    headline(c, f, c.ost[0], t, t0, 140 if not c.vert else 110, c.H * 0.42, CREAM, mode="wipe", dur=1.2)
    return f


def end(c, t):
    f = B.dark_bg(c, 34)
    lg = c.get(("endlogo",), lambda: kit.logo(c.lang, True, 220 if not c.vert else 260, 1.0))
    k = ease_out(t / 0.8)
    cy = c.H * 0.36
    paste(f, lg, c.W / 2 - lg.width / 2, cy - lg.height / 2 + (1 - k) * 30, k)
    ch = c.get(("endch",), lambda: T(c.lang, lab("channel", c.lang), 64, CREAM, True))
    paste(f, ch, c.W / 2 - ch.width / 2, cy + lg.height / 2 + 30, ease((t - 0.5) / 0.6))
    sb = c.get(("endsb",), lambda: B.pill(c.lang, lab("subscribe", c.lang), 40, SAFFRON, INK))
    paste(f, sb, c.W / 2 - sb.width / 2, cy + lg.height / 2 + 150, ease((t - 1.0) / 0.6))
    return f


SCENES = {f"S{i:02d}": globals()[f"s{i:02d}"] for i in range(1, 34)}
SCENES["END"] = end
