"""The 38 scenes of the Mulla Othman Abdulaziz documentary, plus the lecture clip (R10) and the end card.

Each scene(c, t) returns an RGBA frame of c.W x c.H. Both languages are RTL: reading starts on the right.
On-screen text is the scene's `t` block from the prompts; labels are names/places/words from the narration.
Group photos (P01b-P01g, P13, P17) are only shown full; P01a is the only cut-out of the sheikh.
"""
import math
import itertools
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import base as B
from .base import CREAM, DARK, GOLD, GREEN, INK, PAPER, RED, T, clamp01, ease, ease_out, back_out, kit, paste
from .lib import person_layer, _stamp
from vox import geo

# ------------------------------------------------------------------ crops (CLAUDE.md: no flags, no weapons)
P07 = "P07_mulla_mustafa_barzani.jpg#0.05,0.0,0.95,0.46"        # head only, no ammunition belts
P21 = "P21_saddam_hussein.jpg#0.60,0.17,0.92,0.62"             # head and shoulders, the rifle is outside
P13 = "P13_erbakan_with_sheikh.jpg#0.0,0.0,0.94,1.0"           # flag at the right edge cut off
R04 = "R04_halabja_monument.jpg#0.28,0.0,1.0,1.0"               # flags at the left edge cut off
R09A = "R09_uprising_1991.jpg#0.0,0.0,0.48,0.30"                # landscape and road, no weapon
R09B = "R09_uprising_1991.jpg#0.20,0.31,0.39,0.52"              # one face, no weapon
P09 = "P09_mulla_ali_abdulaziz.jpg#0.22,0.0,1.0,1.0"            # desk flag cut off
P20 = "P20_irfan_ali_abdulaziz.jpg#0.50,0.0,1.0,1.0"            # background removed by the matte below
P19 = "P19_salahaddin_bahaaddin.jpg#0.08,0.06,1.0,1.0"
P16 = "P16_ahmad_jibril_meeting_1989.jpg"                         # v2: the author's 1989 photo
P22 = "P22_with_masoud_barzani_jalal_talabani.jpg"               # v2: the author's photo with both leaders
R01_CROP = "760:378:78:0"                                       # funeral clip without 'IMK TV' and the caption band

PLACES = {
    "halabja": (35.18, 45.99), "pris": (35.24, 46.08), "sulaymaniyah": (35.56, 45.43), "baghdad": (33.34, 44.40),
    "nasiriyah": (31.05, 46.26), "samawah": (31.32, 45.28), "sanandaj": (35.31, 47.00), "ankara": (39.93, 32.85),
    "istanbul": (41.01, 28.98), "damascus": (33.51, 36.29), "riyadh": (24.71, 46.68), "tehran": (35.69, 51.39),
    "erbil": (36.19, 44.01), "pawe": (35.04, 46.36), "marivan": (35.52, 46.18), "qushtapa": (36.00, 44.03),
    "border": (35.17, 46.20), "palestine": (31.85, 35.20), "kurdistan": (37.0, 42.5),
}
NAMES = {
    "halabja": ("حلبجة", "هەڵەبجە"), "sulaymaniyah": ("السليمانية", "سلێمانی"), "baghdad": ("بغداد", "بەغدا"),
    "nasiriyah": ("الناصرية", "ناسرییە"), "samawah": ("السماوة", "سەماوە"), "sanandaj": ("سنندج", "سنە"),
    "ankara": ("أنقرة", "ئەنقەرە"), "damascus": ("دمشق", "دیمەشق"), "riyadh": ("الرياض", "ڕیاز"),
    "tehran": ("طهران", "تاران"), "erbil": ("أربيل", "هەولێر"), "pawe": ("پاوە", "پاوە"), "marivan": ("مريوان", "مەریوان"),
    "london": ("لندن", "لەندەن"), "qushtapa": ("قوشتبة", "قوشتەپە"), "border": ("الحدود الإيرانية", "سنووری ئێران"),
    "palestine": ("فلسطين", "فەلەستین"), "kurdistan": ("كردستان", "کوردستان"),
}


def nm(c, key):
    return NAMES[key][0 if c.lang == "ar" else 1]


def ost(c, i=0):
    return c.ost[i] if i < len(c.ost) else ""


def parts(text, sep):
    return [p.strip() for p in text.split(sep)] if sep in text else [text.strip()]


def sepia(im):
    return kit.sepia(im, 0.8)


def warm(im):
    return kit.grade(im, sat=0.95, tint=(1.06, 1.0, 0.9))


def desat(im):
    return kit.grade(im, sat=0.15, contrast=0.95)


# ------------------------------------------------------------------ photos
def cover(c, t, name, z=(1.0, 1.05), f0=(0.5, 0.5), f1=None, prep=None, dark=1.0, old=False, D=None, t0=0.0, vf=None,
          vig=0.5, grain=7.0):
    """Full-bleed still with a slow move; 9:16 uses the focus point vf. AI images get the illustration tag."""
    D = D or c.D
    f1 = f1 or f0
    if c.vert and vf:
        f0 = f1 = vf
    im = B._big(c, name, prep=prep if not old else (prep or sepia))
    u = B.prog(t - t0, D)
    cam = B.Cam(im.width, im.height, u, z[0], z[1], f0, f1, (c.W, c.H))
    if old:                                            # 1 px gate weave on archive photos
        n = int(t * 24)
        cam.x0 = max(0, cam.x0 + ((n * 37) % 3 - 1))
        cam.y0 = max(0, cam.y0 + ((n * 53) % 3 - 1))
    f = cam.view(im).convert("RGBA")
    if name.startswith("A"):
        c.illustration()
    f = B.vignette(f, vig)
    if dark < 1:
        f = B.darken(f, dark)
    return B.grain(f, t, grain + (5 if old else 0))


def pcard(c, name, w=None, h=None, prep=None, rot=0.0, border=6):
    """Real photo as a cut-out: 6 px cream border, soft shadow."""
    def build():
        im = B.load(name)
        if prep:
            im = prep(im)
        co = kit.cutout(kit.fit(im, w, h), torn=False, border=border, seed=3)
        return co.rotate(rot, resample=Image.BICUBIC, expand=True) if rot else co
    return c.get(("pcard", name, w, h, rot, prep.__name__ if prep else None), build)


def mcard(c, name, w, h, prep=None, bg=(52, 50, 46)):
    """Person matte (rembg) on a plain card: removes flags or emblems behind the person."""
    def build():
        im = B.load(name)
        if prep:
            im = prep(im)
        m = B.mask(name).resize(im.size, Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.0))
        base = Image.new("RGB", im.size, bg)
        g = B.radial_img(im.width, im.height, (88, 84, 76), 1.4)
        base = base.convert("RGBA")
        base.alpha_composite(g)
        base.paste(im, (0, 0), m)
        co = kit.cutout(kit.fit(base.convert("RGB"), w, h), torn=False, border=6, seed=4)
        return co
    return c.get(("mcard", name, w, h), build)


def show(c, f, im, cx, cy, t, t0, frm="right", out=None, a=1.0):
    """Place a card with a slide-in; optional fade-out time."""
    if t < t0:
        return None
    k = 1.0 if out is None else clamp01((out - t) / 0.4)
    if k <= 0:
        return None
    return B.place(f, im, cx, cy, t, t0, frm, a * k, dist=500)


def ntag(c, f, text, t, t0, x, y, align="center", size=None, fill=GOLD, fg=INK, out=None):
    """Name / tool label: rounded tag sliding in from the right."""
    size = size or (30 if c.vert else 28)
    im = c.get(("ntag", text, size, fill, fg), lambda: B.pill(c.lang, text, size, fill, fg))
    if c.vert:
        im = c.get(("ntagfit", text, size), lambda: B.fit_w(im, c.tw))
    k = ease_out((t - t0) / 0.45)
    if k <= 0:
        return None
    a = clamp01(k * 1.5) * (1.0 if out is None else clamp01((out - t) / 0.35))
    xx = {"center": x - im.width / 2, "right": x - im.width, "left": x}[align]
    if c.vert:
        xx = min(max(xx, 70), c.W - 140 - im.width)
    paste(f, im, xx + (1 - k) * 90, y, a)
    return (xx, y, xx + im.width, y + im.height)


def wrap_img(c, text, size, colour, maxw, bold=True, gap=0.12):
    return c.get(("wrap", text, size, colour, maxw), lambda: B.stack(B.text_lines(c.lang, text, size, maxw, colour, bold),
                                                                      gap, "center"))


def ost_card(c, text, size=None, maxw=None, fg=INK, bg=CREAM, rot=-1.0):
    """On-screen text on a paper strip (wraps when longer than the safe width)."""
    size = size or (50 if c.vert else 54)
    maxw = maxw or (c.tw - 60)

    def build():
        lines = B.text_lines(c.lang, text, size, maxw, fg)
        st = B.stack(lines, 0.1, "center")
        w, h = st.width + 60, st.height + 26
        out = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
        sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle([16, 18, 16 + w, 18 + h], fill=(0, 0, 0, 80))
        out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
        ImageDraw.Draw(out).rectangle([12, 12, 12 + w, 12 + h], fill=tuple(bg) + (255,))
        out.alpha_composite(st, (12 + 30, 12 + 10))
        return out.rotate(rot, resample=Image.BICUBIC, expand=True) if rot else out
    return c.get(("ostcard", text, size, maxw, fg, bg, rot), build)


def show_ost(c, f, text, t, t0, cy=None, size=None, fg=INK, bg=CREAM, out=None, rot=-1.0, x=None):
    im = ost_card(c, text, size, None, fg, bg, rot)
    k = ease_out((t - t0) / 0.5)
    if k <= 0:
        return None
    a = clamp01(k * 1.6) * (1.0 if out is None else clamp01((out - t) / 0.35))
    cy = cy if cy is not None else (c.top + 40 if not c.vert else 410)
    x = c.cx if x is None else x
    paste(f, im, x - im.width / 2, cy - im.height / 2 + (1 - k) * 26, a)
    return (x - im.width / 2, cy - im.height / 2, x + im.width / 2, cy + im.height / 2)


def quote(c, f, text, t, t0, cy=None, size=None, maxw=None, hl=None, alpha=0.93):
    """Dark quote card, large gold quotation mark, quote text in cream; hl=(ta, tb) lights the words in gold."""
    size = size or (64 if not c.vert else 54)
    maxw = maxw or (c.W - 420 if not c.vert else c.tw - 80)
    words = text.split()
    nhi = len(words) if hl is None else int(round(len(words) * clamp01((t - hl[0]) / max(0.3, hl[1] - hl[0]))))

    def lines_for(k):
        ims = [T(c.lang, w, size, GOLD if i < k and hl is not None else CREAM, True) for i, w in enumerate(words)]
        sp = size * 0.28
        lines, cur, cw = [], [], 0
        for im in ims:
            if cur and cw + im.width - 12 + sp > maxw:
                lines.append(cur)
                cur, cw = [], 0
            cur.append(im)
            cw += im.width - 12 + sp
        lines.append(cur)
        out = []
        for ln in lines:
            order = ln[::-1]
            w = int(sum(i.width - 12 for i in order) + sp * (len(order) - 1) + 12)
            h = max(i.height for i in order)
            li = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            x = 0
            for i in order:
                li.alpha_composite(i, (int(x), (h - i.height) // 2))
                x += i.width - 12 + sp
            out.append(li)
        return B.stack(out, 0.14, "center")
    body = c.get(("qbody", text, size, maxw, nhi if hl else -1), lambda: lines_for(nhi))
    cw, ch = body.width + 150, body.height + 120
    card = c.get(("qcard", text, size, maxw), lambda: B.card(cw, ch, (16, 20, 24), 18))
    k = ease_out((t - t0) / 0.6)
    if k <= 0:
        return None
    cy = cy if cy is not None else (c.H * 0.42 if not c.vert else 760)
    x, y = c.cx - cw / 2, cy - ch / 2 + (1 - k) * 30
    paste(f, card, x, y, alpha * k)
    q = c.get(("qmark",), lambda: T("ar", "«", 200, GOLD, True))
    paste(f, q, x + cw - q.width * 0.75, y - q.height * 0.42, k)
    paste(f, kit.wipe(body, ease((t - t0 - 0.2) / 0.9), True), c.cx - body.width / 2, y + 60)
    return (x, y, x + cw, y + ch)


def headline(c, f, text, t, t0, size, cy, colour=CREAM, maxw=None, dur=0.9, shadow=True):
    maxw = maxw or c.tw
    im = c.get(("hl", text, size, colour, maxw, shadow),
               lambda: B.shadowed(wrap_img(c, text, size, colour, maxw), 12, (0, 6), 150) if shadow else
               wrap_img(c, text, size, colour, maxw))
    k = clamp01((t - t0) / dur)
    if k <= 0:
        return None
    paste(f, kit.wipe(im, ease(k), True), c.cx - im.width / 2, cy - im.height / 2)
    return im


def crossfade(c, t, shots, xf=0.6):
    """shots = [(t_start, fn(t)), ...] in time order; cross-dissolve xf seconds into each new shot."""
    i = 0
    for j, (ts, _) in enumerate(shots):
        if t >= ts:
            i = j
    ts, fn = shots[i]
    f = fn(t)
    if i > 0 and t - ts < xf:
        g = shots[i - 1][1](t)
        f = Image.blend(g, f, ease((t - ts) / xf))
    return f


# ------------------------------------------------------------------ the map (G01)
VIEWS = {   # lon_c, lat_c, lon_span (16:9); 9:16 uses span * 0.62
    "local": (46.2, 35.35, 3.4),
    "iraq": (45.3, 33.2, 13.0),
    "bagh": (45.0, 34.4, 7.0),
    "region": (40.5, 34.0, 26.0),
    "pal": (40.0, 34.6, 16.0),
    "krg": (44.6, 36.0, 6.2),
    "krg_q": (41.9, 36.0, 6.2),     # v2, S28b 16:9: Qushtapa sits right of the verdict cards, not under them
    "krg_qv": (44.6, 36.55, 6.2),   # v2, S28b 9:16: Qushtapa sits below them
}


def gmap(c, key, scale=1.25):
    def build():
        lon, lat, span = VIEWS[key]
        if c.vert:
            span *= 0.62
        w, h = int(c.W * scale), int(c.H * scale)
        v = geo.View(lon, lat, span * scale, w, h)
        img = geo.base_map(v, rivers=("euphrates", "tigris"), highlight=["Iraq"], seed=5, border_w=2)
        return img, v
    return c.get(("gmap", key), build)


def map_frame(c, t, key, z=(1.0, 1.0), f0=(0.5, 0.5), f1=None, D=None, t0=0.0):
    img, v = gmap(c, key)
    u = B.prog(t - t0, D or c.D)
    cam = B.Cam(img.width, img.height, u, z[0], z[1], f0, f1 or f0, (c.W, c.H))
    f = cam.view(img).convert("RGBA")

    def xy(place):
        lat, lon = PLACES[place]
        return cam.pt(*v.xy(lat, lon))
    return f, xy, cam, v


def city(c, f, x, y, label, t, t0, colour=RED, below=False, size=None, glow=False, side=None):
    if t < t0:
        return
    k = ease_out((t - t0) / 0.4)
    d = ImageDraw.Draw(f)
    r = 9 + (4 if glow else 0)
    if glow:
        g = c.get(("cglow",), lambda: B.radial_img(120, 120, GOLD, 1.6))
        paste(f, g, x - 60, y - 60, 0.9 * k)
    d.ellipse([x - r * k, y - r * k, x + r * k, y + r * k], fill=tuple(colour) + (255,), outline=CREAM + (255,), width=3)
    size = size or (30 if c.vert else 28)
    im = c.get(("cityl", label, size), lambda: B.pill(c.lang, label, size, (28, 30, 34), CREAM))
    if side in ("left", "right"):                          # v2: beside the dot, for crowded clusters
        xx = x - r - 10 - im.width if side == "left" else x + r + 10
        paste(f, im, xx, y - im.height / 2, k)
        return
    yy = y + 16 if below else y - im.height - 14
    paste(f, im, x - im.width / 2, yy, k)


def arrow(c, f, a, b, t, t0, dur=1.0, colour=RED, width=6, bend=0.18, dashed=False):
    p = ease((t - t0) / dur)
    if p <= 0:
        return
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    pts = kit.curve(a, b, bend, 60)
    if dashed:
        kit.dotted(d, pts, p, colour, 4.5, 16)
    else:
        kit.ink_line(d, pts, p, colour, width)
    if p > 0.96:
        kit.arrow_head(d, pts[-4], pts[-1], colour, 24, width)
    f.alpha_composite(lay)


# ------------------------------------------------------------------ icons
def icon(kind, s, colour=INK, fill=None):
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = tuple(colour) + (255,)
    w = max(3, s // 22)
    if kind == "book":
        d.rounded_rectangle([s * .18, s * .2, s * .82, s * .82], 6, outline=col, width=w, fill=fill and tuple(fill) + (255,))
        d.line([(s * .3, s * .2), (s * .3, s * .82)], fill=col, width=w)
    elif kind == "scroll":
        d.rounded_rectangle([s * .2, s * .26, s * .8, s * .74], 8, outline=col, width=w, fill=fill and tuple(fill) + (255,))
        for k in range(3):
            d.line([(s * .32, s * (.4 + .1 * k)), (s * .68, s * (.4 + .1 * k))], fill=col, width=max(2, w - 2))
        d.ellipse([s * .62, s * .6, s * .78, s * .76], fill=tuple(RED) + (255,))
    elif kind == "crescent":
        d.ellipse([s * .15, s * .15, s * .85, s * .85], fill=col)
        d.ellipse([s * .32, s * .08, s * .98, s * .74], fill=(0, 0, 0, 0))
        im2 = Image.new("RGBA", (s, s), (0, 0, 0, 0))
        d2 = ImageDraw.Draw(im2)
        d2.ellipse([s * .15, s * .15, s * .85, s * .85], fill=col)
        m = Image.new("L", (s, s), 255)
        ImageDraw.Draw(m).ellipse([s * .33, s * .06, s * 1.0, s * .73], fill=0)
        im2.putalpha(Image.fromarray(np.minimum(np.asarray(im2.split()[3]), np.asarray(m))))
        return im2
    elif kind == "paper":                         # signed paper
        d.rectangle([s * .22, s * .12, s * .78, s * .88], fill=CREAM + (255,), outline=col, width=w)
        for k in range(4):
            d.line([(s * .32, s * (.26 + .1 * k)), (s * .68, s * (.26 + .1 * k))], fill=col, width=max(2, w - 2))
        pts = [(s * (.32 + .05 * k), s * (.74 + (.03 if k % 2 else -.03))) for k in range(8)]
        d.line(pts, fill=tuple(GREEN) + (255,), width=w)
    elif kind == "truck":
        d.rectangle([s * .08, s * .32, s * .62, s * .68], fill=col)
        d.polygon([(s * .62, s * .42), (s * .8, s * .42), (s * .92, s * .56), (s * .92, s * .68), (s * .62, s * .68)], fill=col)
        for x in (.22, .48, .8):
            d.ellipse([s * (x - .08), s * .62, s * (x + .08), s * .78], fill=(60, 60, 60, 255), outline=CREAM + (255,), width=2)
    elif kind == "pause":
        d.ellipse([0, 0, s - 1, s - 1], fill=tuple(GOLD) + (235,))
        d.rectangle([s * .34, s * .28, s * .44, s * .72], fill=INK + (255,))
        d.rectangle([s * .56, s * .28, s * .66, s * .72], fill=INK + (255,))
    elif kind == "flag_pin":
        d.ellipse([s * .3, s * .3, s * .7, s * .7], fill=col)
    return im


# ------------------------------------------------------------------ chapter card / end card
def chapter_card(c, n, t):
    f = B.dark_bg(c, 5)
    num = c.get(("chnum", n), lambda: T(c.lang, str(n).translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")),
                                        180, GOLD, True))
    title = c.sc.get("chapter_title", "")
    k = ease_out(t / 0.45)
    cy = c.H * 0.42 if not c.vert else 820
    paste(f, num, c.cx - num.width / 2, cy - num.height + 30 - (1 - k) * 24, k)
    if title:
        ti = wrap_img(c, title, 78 if not c.vert else 66, CREAM, c.tw)
        paste(f, kit.wipe(ti, ease((t - 0.2) / 0.55), True), c.cx - ti.width / 2, cy + 50)
        w = int(240 * ease((t - 0.35) / 0.5))
        if w > 2:
            yy = cy + 50 + ti.height + 26
            ImageDraw.Draw(f).line([(c.cx - w / 2, yy), (c.cx + w / 2, yy)], fill=GOLD + (255,), width=5)
    return f


def end(c, t):
    f = B.dark_bg(c, 40)
    lg = c.get(("endlogo",), lambda: kit.logo(c.lang, True, 230 if not c.vert else 280, 1.0))
    k = ease_out(t / 0.8)
    cy = c.H * 0.40
    paste(f, lg, c.W / 2 - lg.width / 2, cy - lg.height / 2 + (1 - k) * 30, k)
    name = {"ar": "دوين - العربية", "ckb": "Dween - دوین"}[c.lang]
    ch = c.get(("endch",), lambda: T(c.lang, name, 64, CREAM, True))
    paste(f, ch, c.W / 2 - ch.width / 2, cy + lg.height / 2 + 30, ease((t - 0.5) / 0.6))
    return f


# ------------------------------------------------------------------ motion stills M1-M4 (MOTION.md)
def m1(c, t):
    """A01: push-in 1.00 -> 1.08 toward the warm window; the window light breathes +-4%; the sky darkens."""
    name = "A01_mud_house_by_mosque.jpg"
    im = B._big(c, name)
    u = B.prog(t, c.D)
    foc = (0.70, 0.52) if not c.vert else (0.72, 0.52)
    cam = B.Cam(im.width, im.height, u, 1.0, 1.08, (0.55, 0.5) if not c.vert else foc, foc, (c.W, c.H))
    f = cam.view(im).convert("RGBA")
    wx, wy = cam.pt(0.755 * im.width, 0.535 * im.height)
    glow = c.get(("m1glow",), lambda: B.radial_img(360, 300, (255, 186, 96), 1.8))
    br = 0.5 + 0.04 * math.sin(t * 2 * math.pi / 3.2) + 0.02 * math.sin(t * 7.1)
    paste(f, glow, wx - 180, wy - 150, br)
    sky = c.get(("m1sky",), lambda: Image.fromarray(np.dstack([np.zeros((c.H, c.W, 3), np.uint8),
                                                              (np.clip(1 - np.linspace(0, 1, c.H) / 0.45, 0, 1) * 255)
                                                              .astype(np.uint8)[:, None].repeat(c.W, 1)]), "RGBA"))
    paste(f, sky, 0, 0, 0.35 * u)
    c.illustration()
    return B.grain(B.vignette(f, 0.55), t, 7)


def m2(c, t, D=None, t0=0.0):
    """A02: slow lateral dolly (3%) with a 2-layer parallax; the lamp flame flickers; dust in the window light."""
    name = "A02_hujra_interior_lamp.jpg"
    D = D or c.D
    im = B._big(c, name, k=1.25)
    u = B.prog(t - t0, D)
    fx = 0.30 if c.vert else 0.5
    cam = B.Cam(im.width, im.height, u, 1.04, 1.04, (fx - 0.015, 0.5), (fx + 0.015, 0.5), (c.W, c.H))
    bg = cam.view(im).convert("RGBA")
    camf = B.Cam(im.width, im.height, u, 1.04, 1.04, (fx - 0.03, 0.5), (fx + 0.03, 0.5), (c.W, c.H))
    fg = camf.view(im).convert("RGBA")
    m = c.get(("m2mask",), lambda: Image.fromarray((np.clip((np.linspace(0, 1, c.H) - 0.55) / 0.15, 0, 1) * 255)
                                                    .astype(np.uint8)[:, None].repeat(c.W, 1)))
    bg.paste(fg, (0, 0), m)
    fx_, fy_ = camf.pt(0.255 * im.width, 0.43 * im.height)
    fl = 0.55 + 0.12 * math.sin(t * 13.0) * math.sin(t * 5.3 + 1) + 0.06 * math.sin(t * 29.0)
    glow = c.get(("m2glow",), lambda: B.radial_img(300, 300, (255, 176, 80), 2.2))
    paste(bg, glow, fx_ - 150, fy_ - 165, fl)
    rng = np.random.default_rng(7)
    d = ImageDraw.Draw(bg)
    wx, wy = cam.pt(0.85 * im.width, 0.2 * im.height)
    for k in range(70):
        x0 = wx - rng.uniform(100, 700)
        y0 = wy + rng.uniform(0, 520)
        x = x0 + 18 * math.sin(t * 0.4 + k)
        y = y0 + ((t * rng.uniform(4, 12) + k * 9) % 60) - 30
        r = rng.uniform(1.0, 2.4)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 232, 190, int(rng.uniform(40, 120))))
    c.illustration()
    return B.grain(B.vignette(bg, 0.5), t, 7)


def m3(c, t, D=None, t0=0.0):
    """A10: pull-out 1.10 -> 1.00, drifting mist, the line of people rises by 0.5%."""
    name = "A10_mountain_pass_migration.jpg"
    D = D or c.D
    im = B._big(c, name)
    u = B.prog(t - t0, D)
    foc = (0.55, 0.55) if not c.vert else (0.62, 0.55)
    cam = B.Cam(im.width, im.height, u, 1.10, 1.0, foc, foc, (c.W, c.H))
    f = cam.view(im).convert("RGBA")
    band = c.get(("m3band",), lambda: _band_mask(c, im, cam))
    sh = int(round(-0.005 * c.H * u))
    if sh:
        moved = f.transform(f.size, Image.AFFINE, (1, 0, 0, 0, 1, -sh), resample=Image.BILINEAR)
        f.paste(moved, (0, 0), band)
    f.alpha_composite(_mist(c, t))
    c.illustration()
    return B.grain(B.vignette(f, 0.5), t, 7)


def _band_mask(c, im, cam):
    pts = [(0.03, 0.75), (0.25, 0.62), (0.5, 0.52), (0.75, 0.44), (0.97, 0.37)]
    m = Image.new("L", (c.W, c.H), 0)
    d = ImageDraw.Draw(m)
    xy = [cam.pt(x * im.width, y * im.height) for x, y in pts]
    d.line(xy, fill=255, width=int(c.H * 0.07))
    return m.filter(ImageFilter.GaussianBlur(14))


def _mist(c, t):
    m = c.get(("mist",), lambda: _mist_layer(c))
    x = -((t * c.W * 0.018) % c.W)
    lay = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
    lay.alpha_composite(m, (int(x), int(c.H * 0.30)))
    lay.alpha_composite(m, (int(x) + c.W, int(c.H * 0.30)))
    return lay


def _mist_layer(c):
    rng = np.random.default_rng(3)
    w, h = c.W // 4, c.H // 4
    n = np.zeros((h, w), np.float32)
    for sc, amp in ((8, 1.0), (24, 0.7), (64, 0.5)):
        a = rng.normal(0, 1, (max(2, h // sc), max(2, w // sc))).astype(np.float32)
        n += np.asarray(Image.fromarray(a).resize((w, h), Image.BICUBIC)) * amp
    n = np.clip((n - n.min()) / (n.max() - n.min()), 0, 1) ** 1.8
    arr = np.zeros((h, w, 4), np.uint8)
    arr[..., :3] = 238
    arr[..., 3] = (n * 120).astype(np.uint8)
    return Image.fromarray(arr, "RGBA").resize((c.W, int(c.H * 0.7)), Image.BICUBIC)


def m4(c, t):
    """A15: static camera, gentle train sway (+-0.4 deg at 1.2 s), light streaks sliding across the window."""
    name = "A15_night_train_prayer_rug.jpg"
    im = B._big(c, name, k=1.12)
    foc = (0.5, 0.5) if not c.vert else (0.62, 0.5)
    cam = B.Cam(im.width, im.height, 0.0, 1.03, 1.03, foc, foc, (c.W, c.H))
    f = cam.view(im).convert("RGBA")
    x0, y0 = cam.pt(0.43 * im.width, 0.05 * im.height)
    x1, y1 = cam.pt(0.90 * im.width, 0.43 * im.height)
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(5)
    for k in range(9):
        yy = y0 + (y1 - y0) * rng.uniform(0.35, 0.9)
        L = rng.uniform(80, 260)
        sp = rng.uniform(500, 900)
        xx = x1 - ((t * sp + k * 300) % ((x1 - x0) + L + 400)) + 200
        col = (255, 220, 150) if k % 3 else (190, 220, 255)
        d.line([(xx, yy), (xx + L, yy)], fill=col + (int(rng.uniform(90, 170)),), width=int(rng.uniform(3, 7)))
    lay = lay.filter(ImageFilter.GaussianBlur(4))
    win = Image.new("L", f.size, 0)
    ImageDraw.Draw(win).rectangle([x0, y0, x1, y1], fill=255)
    lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.split()[3]), np.asarray(win))))
    f.alpha_composite(lay)
    ang = 0.4 * math.sin(2 * math.pi * t / 1.2)
    f = f.rotate(ang, resample=Image.BICUBIC, center=(c.W / 2, c.H * 0.9))
    f = cam.view(im).convert("RGBA") if f.getbbox() is None else f
    c.illustration()
    out = B.vignette(f, 0.6)
    return B.grain(out, t, 7)


# ------------------------------------------------------------------ text behind person (P01a / P13)
def behind(c, t, name, title, t0, size, ty, prep=warm, bgfn=None, dark=0.85, z=(1.0, 1.04), foc=(0.5, 0.42),
           shift=(0.0, 0.0), sub=None, sub_t0=None, gold=False, side=False):
    """Background -> giant title -> person matte (2.5D: background 1%, person 2.5%).
    side=True: the person sits on the left third (16:9) / lower half (9:16), the title on the reading side behind him."""
    im = B._big(c, name, prep=prep)
    u = B.prog(t, c.D)
    if c.vert:
        foc = (foc[0], 0.40)
    cam_bg = B.Cam(im.width, im.height, u, z[0], z[0] + 0.01, foc, foc, (c.W, c.H))
    if bgfn is not None:
        f = bgfn(t)
    else:
        f = B.darken(cam_bg.view(im).convert("RGBA"), dark)
    k = ease_out((t - t0) / 1.0)
    tx = c.cx
    maxw = c.tw + 80
    if side and not c.vert:
        # v2: the wider Noto glyphs ran behind his head and hid letters; keep the title in the free side
        tx, maxw = c.W * 0.655, 940
    ti = c.get(("bh", title, size, maxw), lambda: _title_img(c, title, size, GOLD if gold else CREAM, maxw))
    if k > 0:
        paste(f, ti, tx - ti.width / 2, ty - ti.height / 2 + (1 - k) * 36, k)
    lay = c.get(("bhlay", name, prep.__name__ if prep else None), lambda: _person(c, name, prep))
    cam_p = B.Cam(im.width, im.height, u, z[0], z[1], foc, (foc[0] + shift[0], foc[1] - 0.012 + shift[1]), (c.W, c.H))
    pv = cam_p.view(lay)
    if side:
        dx, dy = (-int(c.W * 0.24), int(c.H * 0.04)) if not c.vert else (0, int(c.H * 0.28))
        f.alpha_composite(pv, (dx, dy)) if dx >= 0 and dy >= 0 else f.alpha_composite(pv.crop((max(0, -dx), max(0, -dy), pv.width, pv.height)), (max(0, dx), max(0, dy)))
    else:
        f.alpha_composite(pv)
    if sub:
        st = c.get(("bhsub", sub), lambda: B.shadowed(T(c.lang, sub, 58 if not c.vert else 52, GOLD, True), 8, (0, 4), 160))
        a = ease((t - (sub_t0 if sub_t0 is not None else t0 + 0.6)) / 0.6)
        tb = ti.getbbox() or (0, 0, ti.width, ti.height)
        sb = c.get(("bhsubbb", sub), lambda: st.split()[3].point(lambda v: 255 if v > 100 else 0).getbbox())
        if not c.vert:
            sy = ty + 230
            gap = (sy - st.height / 2 + sb[1]) - (ty - ti.height / 2 + tb[3])
            sy += max(0.0, 20 - gap)                       # keep the years clear of the name
            paste(f, st, tx - st.width / 2, sy - st.height / 2, a)
        else:
            sy = 300
            gap = (ty - ti.height / 2 + tb[1]) - (sy - st.height / 2 + sb[3])
            sy -= max(0.0, 30 - gap)                       # the years sit above the name in 9:16
            paste(f, st, c.cx - st.width / 2, sy - st.height / 2, a)
    return B.grain(B.vignette(f, 0.45), t, 6)


def _title_img(c, title, size, colour, maxw):
    """Giant title: one line if it fits at >= 86% size, else the most balanced split (no orphan word)."""
    words = title.split()
    n = len(B.text_lines(c.lang, title, size, maxw))
    if n == 2:
        w1 = T(c.lang, title, size, colour).width
        if w1 * 0.86 <= maxw:
            s = int(size * maxw / w1)
            return B.stack([T(c.lang, title, s, colour)], 0.12, "center")
    best = None
    if 1 < n <= len(words):
        for cuts in itertools.combinations(range(1, len(words)), n - 1):
            idx = (0,) + cuts + (len(words),)
            lines = [" ".join(words[idx[i]:idx[i + 1]]) for i in range(n)]
            ws = [T(c.lang, x, size, colour).width for x in lines]
            if max(ws) <= maxw and (best is None or max(ws) < best[0]):
                best = (max(ws), lines)
    if best is None:
        return wrap_img(c, title, size, colour, maxw)
    return B.stack([T(c.lang, x, size, colour) for x in best[1]], 0.12, "center")


def _person(c, name, prep):
    im = B._big(c, name, prep=prep)
    m = B.mask(name).resize(im.size, Image.LANCZOS)
    m = m.point(lambda v: 0 if v < 70 else (255 if v > 150 else int((v - 70) * 255 / 80))).filter(ImageFilter.GaussianBlur(1.2))
    lay = im.convert("RGBA")
    lay.putalpha(m)
    return lay


def glow_bg(c, t, seed=3, colour=(120, 92, 48)):
    f = B.dark_bg(c, seed)
    g = c.get(("gbg", colour), lambda: B.radial_img(int(c.W * 1.2), int(c.H * 1.0), colour, 1.5))
    paste(f, g, c.W / 2 - g.width / 2, c.H * 0.45 - g.height / 2, 0.75)
    return f


# ------------------------------------------------------------------ G graphics
def book_stack(c, f, t, t0, cx, base_y, n_show, titles):
    """G02: classical book spines stacking up, titles as labels."""
    cols = [(110, 52, 40), (47, 93, 80), (70, 56, 42), (120, 90, 50), (60, 70, 90), (98, 40, 46)]
    w = 560 if not c.vert else 500
    hh = 64 if not c.vert else 60
    for i in range(n_show):
        k = back_out((t - t0 - i * 0.35) / 0.5, 1.3)
        if k <= 0:
            continue
        y = base_y - (i + 1) * (hh + 6) - (1 - k) * 120
        off = ((i * 37) % 5 - 2) * 10
        sp = c.get(("spine", i), lambda i=i: _spine(c, w - (i % 3) * 30, hh, cols[i % len(cols)],
                                                   titles[i] if i < len(titles) else ""))
        paste(f, sp, cx - sp.width / 2 + off, y, clamp01(k * 2))


def _spine(c, w, h, col, title):
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([10, 10, w + 10, h + 10], 8, fill=(0, 0, 0, 90))
    d.rounded_rectangle([4, 4, w + 4, h + 4], 8, fill=tuple(col) + (255,))
    for x in (40, w - 32):
        d.line([(x, 8), (x, h)], fill=GOLD + (220,), width=4)
    if title:
        tx = T("ar", title, int(h * 0.5), (240, 222, 170), True)
        im.alpha_composite(tx, (int(4 + w / 2 - tx.width / 2), int(4 + h / 2 - tx.height / 2)))
    return im


def tree(c, f, t, root, branches, t0=0.0, grow=1.0, trunk_label=None, trunk_only=False, colour=INK, height=None):
    """G04: legacy tree. branches = [(label, t_appear)], drawn in reading order from the right."""
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rx, ry = root
    top = ry - (height * c.H if height else (430 if not c.vert else 520))
    p = ease((t - t0) / 0.9)
    kit.ink_line(d, [(rx, ry), (rx, ry - (ry - top) * p)], 1.0, colour, 12)
    tips = []
    n = len(branches)
    for i, (lab, ta) in enumerate(branches):
        if trunk_only:
            break
        q = ease((t - ta) / 0.8) * grow
        if q <= 0:
            tips.append(None)
            continue
        if not c.vert:
            span = 1300
            u = 0.5 if n == 1 else i / (n - 1)
            tx = rx + span / 2 - span * u
            ty = top - 10 - (50 if i % 2 else 0)
        else:
            tx = rx + (230 if i % 2 == 0 else -230)
            ty = top - 40 + i * 150 - 260
        start = (rx, top + 80 + i * 25)
        pts = kit.curve(start, (tx, ty), 0.16 * (1 if tx < rx else -1), 40)
        kit.ink_line(d, pts, q, colour, 7)
        tips.append((tx, ty, q))
    f.alpha_composite(lay)
    labs = []
    for (lab, ta), tip in zip(branches, tips):
        if not tip or not lab:
            labs.append(None)
            continue
        tx, ty, q = tip
        im = c.get(("tlab", lab), lambda lab=lab: B.fit_w(B.strip_img(c.lang, lab, 36 if not c.vert else 34, INK, CREAM),
                                                           520 if not c.vert else c.tw))
        x = tx - im.width / 2
        if c.vert:
            x = min(max(x, 60), c.W - 140 - im.width)
        paste(f, im, x, ty - im.height - 6, clamp01(q * 2 - 1))
        labs.append((x, ty - im.height - 6, x + im.width, ty - 6))
    if trunk_label:
        im = c.get(("trunkl", trunk_label), lambda: B.strip_img(c.lang, trunk_label, 56 if not c.vert else 48, CREAM, GREEN))
        paste(f, im, rx - im.width / 2, (ry + top) / 2 - im.height / 2, ease((t - t0 - 0.6) / 0.5))
    return top, labs


def name_card(c, name, w=None, sub=None, size=None):  # noqa: C901
    """Calligraphic name card for a person without a photo (no face)."""
    w = w or (560 if not c.vert else 700)

    def build():
        nmi = B.fit_w(T(c.lang, name, size or (64 if not c.vert else 60), GOLD, True), w - 60)
        sbi = B.fit_w(T(c.lang, sub, 32, CREAM, False), w - 60) if sub else None
        h = nmi.height + (sbi.height + 20 if sbi else 0) + 80
        im = B.card(w, h, (22, 26, 30), 16, GOLD)
        d = ImageDraw.Draw(im)
        d.line([(w * 0.3, 26), (w * 0.7, 26)], fill=GOLD + (160,), width=2)
        d.line([(w * 0.3, h - 26), (w * 0.7, h - 26)], fill=GOLD + (160,), width=2)
        im.alpha_composite(nmi, (int(w / 2 - nmi.width / 2), 36))
        if sbi:
            im.alpha_composite(sbi, (int(w / 2 - sbi.width / 2), 36 + nmi.height + 6))
        return B.shadowed(im, 10, (6, 10), 110)
    return c.get(("namecard", name, sub, w, size), build)


def verdict(c, t, bg, t_v=None, cy=None):
    """G06: the claim on a torn strip; the stamp (x or half) lands at t_v."""
    text = ost(c)
    m = re.match(r"(.*?[؟?])\s*([✗◐✓])\s*(.*)", text)
    claim, mark, verd = (m.group(1), m.group(2), m.group(3)) if m else (text, "", "")
    f = bg
    cy = cy or (c.H * 0.30 if not c.vert else 520)
    strip = c.get(("vclaim",), lambda: B.fit_w(kit.cutout(_claim_img(c, claim), torn=True, border=0, seed=2), c.tw + 40))
    k = ease_out((t - 0.3) / 0.6)
    paste(f, strip, c.cx - strip.width / 2 + (1 - k) * 200, cy - strip.height / 2, k)
    t_v = t_v if t_v is not None else c.sc.get("verdict_t", c.frac(0.3))
    kv = clamp01((t - t_v) / 0.3)
    if kv > 0 and mark:
        colr = RED if mark == "✗" else GOLD
        # v2: capped in 16:9 so the long Sorani S28 verdict leaves room for the photo card beside it
        st = c.get(("vstamp", mark), lambda: B.fit_w(_stamp(c, mark, verd, colr), c.tw + 20 if c.vert else 960))
        s = 1 + 0.7 * (1 - back_out(kv, 2.0))
        im = st.resize((int(st.width * s), int(st.height * s)), Image.BILINEAR)
        paste(f, im, c.cx - im.width / 2, cy + strip.height / 2 + 10 + st.height / 2 - im.height / 2, clamp01(kv * 3))
    return f, cy + strip.height / 2


def _claim_img(c, claim):
    tx = T(c.lang, claim, 84 if not c.vert else 66, INK, True)
    im = Image.new("RGB", (tx.width + 90, tx.height + 40), (236, 228, 210))
    im.paste(tx, (45, 14), tx)
    return im


def veil(f, a=0.55):
    return B.darken(f, 1 - a)


# ================================================================== scenes
def s01(c, t):
    f = m1(c, t)
    t_house = c.at("لكن", "بەڵام", default=c.frac(0.35))
    # the man: the only single portrait of the sheikh, as a cut-out, before the house takes over
    card = pcard(c, "P01a_sheikh_portrait.jpg", h=420 if not c.vert else 460, prep=warm, rot=2.0)
    show(c, f, card, c.W * 0.72 if not c.vert else c.cx, c.H * 0.42 if not c.vert else 620, t, 0.8, "right",
         out=t_house)
    # kinetic quote, word by word with the oath
    words = ost(c).split()
    ta = c.at("والله", "بەخوا", default=c.frac(0.7))
    tb = c.a1 - 0.2
    n = int(math.ceil(len(words) * clamp01((t - ta) / max(0.5, tb - ta))))
    if n > 0:
        shown = " ".join(words[:n])
        im = c.get(("s01q", n), lambda: B.shadowed(wrap_img(c, shown, 74 if not c.vert else 60, CREAM, c.tw), 12, (0, 6), 160))
        paste(f, im, c.cx - im.width / 2, (c.H * 0.24 if not c.vert else 470) - im.height / 2)
    return f


def _petals(c, f, t, n=46):
    rng = np.random.default_rng(12)
    d = ImageDraw.Draw(f)
    for k in range(n):
        x0 = rng.uniform(0, c.W)
        sp = rng.uniform(30, 70)
        y = (rng.uniform(-c.H, c.H) + t * sp) % (c.H + 80) - 40
        x = x0 + 30 * math.sin(t * rng.uniform(0.5, 1.2) + k)
        r = rng.uniform(7, 14)
        a = rng.uniform(0, math.pi)
        col = (176, 32, 44) if k % 3 else (240, 232, 226)
        pts = [(x + r * math.cos(a + q) * (1 if q < 3 else 0.5), y + r * 0.6 * math.sin(a + q)) for q in np.linspace(0, 2 * math.pi, 9)]
        d.polygon(pts, fill=col + (int(rng.uniform(150, 230)),))


def funeral_clip(c, t_clip, dark=1.0):
    """R01 (cropped, no watermark/caption band) full-bleed (16:9) or framed on its own blur (9:16)."""
    cl = B.clip(c, "R01_funeral_1999.mp4", 540, crop=R01_CROP)
    fr = cl.at(t_clip)
    if not c.vert:
        bg = kit.cover(fr.convert("RGB"), c.W // 4, c.H // 4).resize((c.W, c.H), Image.BILINEAR)
        f = B.darken(bg.filter(ImageFilter.GaussianBlur(6)).convert("RGBA"), 0.4)
        fw = 1560
        im = fr.resize((fw, int(fr.height * fw / fr.width)), Image.LANCZOS)
        fr2 = Image.new("RGBA", (im.width + 12, im.height + 12), CREAM + (255,))
        fr2.alpha_composite(im, (6, 6))
        paste(f, B.shadowed(fr2, 12, (6, 10), 120), c.W / 2 - fr2.width / 2 - 36, c.H * 0.45 - fr2.height / 2 - 36)
    else:
        bg = kit.cover(fr.convert("RGB"), c.W // 4, c.H // 4).resize((c.W, c.H), Image.BILINEAR)
        f = B.darken(bg.filter(ImageFilter.GaussianBlur(6)).convert("RGBA"), 0.45)
        fw = c.W - 40
        im = fr.resize((fw, int(fr.height * fw / fr.width)), Image.BILINEAR)
        fr2 = Image.new("RGBA", (im.width + 12, im.height + 12), CREAM + (255,))
        fr2.alpha_composite(im, (6, 6))
        paste(f, B.shadowed(fr2, 12, (6, 10), 120), 20 - 36, 640 - fr2.height / 2 - 36)
    return B.grain(B.darken(f, dark), t_clip, 6)


def s02(c, t):
    q_t = c.at("نعرف", "قەدری", default=c.frac(0.72)) - 0.3
    t_ph = c.frac(0.45)
    shots = [(0.0, lambda tt: funeral_clip(c, tt + 0.5)),
             (t_ph, lambda tt: cover(c, tt, "R01b_funeral_1999_photo.jpg", (1.04, 1.0), (0.5, 0.5), D=c.D - t_ph, t0=t_ph,
                                     vf=(0.45, 0.5)))]
    f = crossfade(c, t, shots)
    if t > q_t:
        f = veil(f, 0.45 * ease((t - q_t) / 0.6))
    _petals(c, f, t)
    lt = c.at("الحداد", "ماتەمینی", default=c.frac(0.45))
    ntag(c, f, c.lab("إقليم كردستان — الحداد ثلاثة أيام", "هەرێمی کوردستان — سێ ڕۆژ ماتەمینی"), t, lt - 0.3,
         c.W - c.margin if not c.vert else c.cx, c.cap_top - 70 if not c.vert else 1200, "right" if not c.vert else "center",
         size=34, out=q_t)
    quote(c, f, ost(c), t, q_t, cy=c.H * 0.40 if not c.vert else 760)
    return f


def s03(c, t):
    f = B.dark_bg(c, 3)
    ph = c.get(("s03ph",), lambda: kit.cover(B.load("P01b_sheikh_teaching.jpg"), c.W, c.H, 0.62, 0.4).convert("RGBA"))
    paste(f, B.grain(ph, t, 0), 0, 0, 0.20 * ease(t / 1.2))
    text = ost(c)
    n = int(len(text) * clamp01((t - 0.4) / 2.2))
    if n > 0:
        shown = text[:n]
        im = c.get(("s03t", n), lambda: wrap_img(c, shown, 92 if not c.vert else 74, CREAM, c.tw))
        paste(f, im, c.cx - im.width / 2, c.H * 0.44 - im.height / 2 if not c.vert else 760)
    return f


def s04(c, t):
    title, years = ost(c, 0), ost(c, 1)
    return behind(c, t, "P01a_sheikh_portrait.jpg", title, 0.2, 150 if not c.vert else 100,
                  c.H * 0.40 if not c.vert else 450, bgfn=lambda tt: glow_bg(c, tt, 4),
                  foc=(0.5, 0.45), z=(1.0, 1.035), sub=years, sub_t0=0.9, side=True)


def s05(c, t):
    f, xy, cam, v = map_frame(c, t, "local", (1.0, 1.25), (0.5, 0.5), (0.48, 0.52))
    x, y = xy("halabja")
    city(c, f, x, y, nm(c, "halabja"), t, 0.6, INK, below=True)
    t_pin = c.at("قرية", "گوندی", default=c.frac(0.15))
    px, py = xy("pris")
    kit.map_pin(f, px, py, t - t_pin, RED, 1.2)
    show_ost(c, f, ost(c), t, c.a0 + 0.2, cy=c.top + 10 if not c.vert else 420)
    t_ph = c.at("بيت", "ماڵێکی", default=c.frac(0.3))
    card = pcard(c, "R02_halabja_pris_village.jpg", w=640 if not c.vert else 760, rot=-2)
    show(c, f, card, c.W * 0.28 if not c.vert else c.cx, c.H * 0.58 if not c.vert else 1040, t, t_ph, "left")
    return B.grain(f, t, 5)


def s06(c, t):
    t_st = c.at("«الفقيه»", "فەقێ", default=c.frac(0.4))
    f = crossfade(c, t, [(0.0, lambda tt: m2(c, tt)),
                         (t_st, lambda tt: cover(c, tt, "A03_students_books_from_behind.jpg", (1.0, 1.05), (0.5, 0.5),
                                                 D=c.D - t_st, t0=t_st, vf=(0.5, 0.5)))])
    show_ost(c, f, ost(c), t, c.a0 + 0.1, cy=c.top + 10 if not c.vert else 430, fg=INK, bg=GOLD)
    # small icons: four books -> the ijaza
    t_ic = c.at("كتابًا", "کتێب", default=c.frac(0.55))
    s = 96 if not c.vert else 100
    gap = 26
    n = 4
    total = (n + 1) * s + n * gap + 80
    x = c.cx + total / 2 - s
    yy = c.H * 0.66 if not c.vert else 1100
    panel = c.get(("s06pan",), lambda: B.card(total + 40, s + 40, (20, 22, 26), 16))
    paste(f, panel, c.cx - (total + 40) / 2, yy - 20, 0.8 * ease((t - t_ic + 0.3) / 0.4))
    for i in range(n):
        k = ease_out((t - t_ic - i * 0.3) / 0.35)
        if k > 0:
            paste(f, c.get(("ic_book", i), lambda: icon("book", s, CREAM, (120 - i * 15, 60 + i * 10, 46))), x, yy + (1 - k) * 20, k)
        x -= s + gap
    t_ij = c.at("الإجازة", "ئیجازە", default=c.frac(0.85))
    ka = ease((t - t_ij + 0.6) / 0.4)
    if ka > 0:
        d = ImageDraw.Draw(f)
        d.line([(x + s + gap - 6, yy + s / 2), (x + s + 20, yy + s / 2)], fill=GOLD + (255,), width=5)
        paste(f, c.get(("ic_scroll",), lambda: icon("scroll", s, CREAM, (236, 222, 190))), x - 30, yy, ka)
        ntag(c, f, c.lab("الإجازة", "ئیجازە"), t, t_ij - 0.4, x - 30 + s / 2, yy + s + 30)
    return f


def s07(c, t):
    f = cover(c, t, "A04_old_key_on_books.jpg", (1.0, 1.06), (0.42, 0.4), (0.38, 0.35), dark=0.92, vf=(0.38, 0.4))
    t_p = c.at("صالح", "ساڵحی", default=c.frac(0.1))
    q_t = c.at("اليوم", "ئەمڕۆوە", default=c.frac(0.85)) - 0.5
    card = pcard(c, "P03_mulla_salih_kabir.jpg", h=480 if not c.vert else 520, prep=sepia, rot=-2)
    bx = show(c, f, card, c.W * 0.78 if not c.vert else c.cx, c.H * 0.45 if not c.vert else 700, t, t_p, "right",
              out=q_t)
    if bx:
        ntag(c, f, c.lab("الملا صالح الكبير", "مەلا ساڵحی گەورە"), t, t_p + 0.5, (bx[0] + bx[2]) / 2, bx[3] - 40,
             out=q_t)
    if t > q_t:
        f = veil(f, 0.4 * ease((t - q_t) / 0.5))
    quote(c, f, ost(c), t, q_t)
    return f


def s08(c, t):
    t_go = c.at("فذهب", "چوو", default=c.frac(0.2))
    t_book = c.at("كتب", "کتێبەکانی", default=c.frac(0.5))
    q_t = c.at("هذا", "ئەمە", default=c.frac(0.85)) - 0.3

    def paper(tt):
        return B.paper_bg(c, tt, c.D, 8)
    f = crossfade(c, t, [(0.0, lambda tt: cover(c, tt, "A05_wheat_mill.jpg", (1.0, 1.06), (0.6, 0.5), D=t_go + 1,
                                                vf=(0.7, 0.5))), (t_go, paper)])
    if t >= t_go:
        card = pcard(c, "P04_sheikh_muhammad_khal.jpg", h=500 if not c.vert else 460, prep=sepia, rot=1.5)
        px, py = (c.W * 0.75, c.H * 0.44) if not c.vert else (c.cx, 600)
        bx = show(c, f, card, px, py, t, t_go + 0.2, "right")
        if bx:
            ntag(c, f, c.lab("الشيخ محمد الخال | السليمانية", "شێخ محەممەدی خاڵ | سلێمانی"), t, t_go + 0.7,
                 (bx[0] + bx[2]) / 2, bx[3] - 40)
        titles = ["جمع الجوامع", "المطوّل", "شرح المواقف", "", ""]
        book_stack(c, f, t, t_book, c.W * 0.30 if not c.vert else c.cx, c.H * 0.80 if not c.vert else 1330,
                   5, titles)
    if t > q_t:
        f = veil(f, 0.55 * ease((t - q_t) / 0.5))
    quote(c, f, ost(c), t, q_t)
    return f


def s09(c, t):
    t_q = max(c.at("القرآن", "قورئانی", default=c.frac(0.35)), c.a0 + 5.5)
    t_d = c.at("عشتُ", "ژیام", default=c.frac(0.75))
    shots = [(0.0, lambda tt: cover(c, tt, "P01b_sheikh_teaching.jpg", (1.0, 1.05), (0.6, 0.45), D=t_q + 0.6,
                                    dark=0.6, vf=(0.66, 0.4))),
             (t_q, lambda tt: cover(c, tt, "A06_quran_on_stand.jpg", (1.0, 1.04), (0.4, 0.5), D=t_d - t_q + 0.6, t0=t_q,
                                    vf=(0.32, 0.5))),
             (t_d, lambda tt: cover(c, tt, "P01d_sheikh_with_sheikh_osman_naqshbandi.jpg", (1.0, 1.05), (0.5, 0.45),
                                    D=c.D - t_d, t0=t_d, vf=(0.45, 0.45)))]
    f = crossfade(c, t, shots, 0.8)
    # counter rolls to 57 over the first shot
    text = ost(c)
    kk = clamp01((t - c.a0) / 1.6)
    a = ease((t - c.a0 + 0.2) / 0.3) * clamp01((t_q - t) / 0.4)
    if a > 0:
        m = re.search(r"\d+", text)
        val = int(m.group(0))
        cur = int(round(val * ease_out(kk)))
        num = c.get(("s09n", cur), lambda: T(c.lang, str(cur), 230 if not c.vert else 200, GOLD, True))
        rest = c.get(("s09r",), lambda: T(c.lang, text[m.end():].strip(), 70 if not c.vert else 62, CREAM, True))
        cy = c.H * 0.42 if not c.vert else 700
        paste(f, B.shadowed(num, 10, (0, 5), 160), c.cx - num.width / 2 - 30, cy - num.height / 2 - 60, a)
        paste(f, B.shadowed(rest, 8, (0, 4), 160), c.cx - rest.width / 2 - 24, cy + num.height / 2 - 40, a)
    return f


def s10(c, t):
    f, xy, cam, v = map_frame(c, t, "bagh", (1.0, 1.06), (0.5, 0.5))
    bx, by = xy("baghdad")
    hx, hy = xy("halabja")
    city(c, f, bx, by, nm(c, "baghdad"), t, 0.4, INK, below=True)
    city(c, f, hx, hy, nm(c, "halabja"), t, 0.6, RED)
    t_go = c.at("زار", "سەردانی", default=c.frac(0.15))
    arrow(c, f, (bx, by), (hx, hy), t, t_go, 1.4, GOLD, 7, -0.2)
    t5 = c.at("أمجد", "ئەمجەد", default=c.frac(0.1))
    t6 = c.at("الصوّاف", "سەوواف", default=c.frac(0.25))
    hh = 330 if not c.vert else 290
    for i, (nmf, lab, ta) in enumerate((("P05_amjad_zahawi.jpg", c.lab("أمجد الزهاوي | بغداد", "ئەمجەد زەهاوی | بەغدا"), t5),
                                       ("P06_muhammad_sawwaf.jpg", c.lab("محمد محمود الصوّاف | بغداد",
                                                                         "محەممەد مەحمود سەوواف | بەغدا"), t6))):
        card = pcard(c, nmf, h=hh, prep=sepia, rot=(-2, 2)[i])
        if not c.vert:
            px, py = c.W * (0.18 + 0.2 * i), c.H * 0.56
        else:
            px, py = c.cx + (215 if i == 0 else -215), 1080
        b = show(c, f, card, px, py, t, ta, "left")
        if b:
            ntag(c, f, lab, t, ta + 0.4, (b[0] + b[2]) / 2, b[3] - 36, size=24 if c.vert else 26)
    show_ost(c, f, ost(c), t, c.a0 + 0.1, cy=c.top + 10 if not c.vert else 420)
    return B.grain(f, t, 5)


def _bars(c, f, t, t0, dur, a=0.55):
    """Barred-window shadow sweeping across the frame."""
    p = (t - t0) / dur
    if p <= 0 or p >= 1.3:
        return
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0 = c.W * (1.2 - 1.5 * p)
    for k in range(7):
        x = x0 + k * 90
        d.polygon([(x, 0), (x + 34, 0), (x - 260 + 34, c.H), (x - 260, c.H)], fill=(0, 0, 0, int(255 * a)))
    f.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10)))


def s11(c, t):
    t_map = c.at("فسُجن", "زیندانی", default=c.frac(0.45)) - 0.4
    t_exile = c.at("ونُفيا", "دوورخرانەوە", default=c.frac(0.65))
    t_end = c.at("كانت", "ئەوە", default=c.frac(0.85))
    if t < t_map:
        f = B.dark_bg(c, 11)
        show_ost(c, f, ost(c), t, 0.2, cy=c.H * 0.45 if not c.vert else 700, size=62 if not c.vert else 52)
        return f
    if t < t_end:
        f, xy, cam, v = map_frame(c, t, "iraq", (1.0, 1.05), (0.5, 0.5), D=t_end - t_map, t0=t_map)
        hx, hy = xy("halabja")
        nx, ny = xy("nasiriyah")
        city(c, f, hx, hy, nm(c, "halabja"), t, t_map + 0.2, INK)
        city(c, f, nx, ny, nm(c, "nasiriyah"), t, t_exile + 0.6, RED, below=True)
        arrow(c, f, (hx, hy), (nx, ny), t, t_exile - 0.2, 1.3, RED, 7, 0.22)
        _bars(c, f, t, t_map + 0.3, (t_end - t_map) * 0.9, 0.35)
        show_ost(c, f, ost(c), t, t_map, cy=c.top + 10 if not c.vert else 430, size=48 if not c.vert else 44)
        return B.grain(f, t, 5)
    f = cover(c, t, "A07_prison_window_shadow.jpg", (1.0, 1.05), (0.55, 0.5), D=c.D - t_end, t0=t_end, vf=(0.6, 0.5))
    show_ost(c, f, ost(c), t, t_end, cy=c.top + 10 if not c.vert else 430, size=48 if not c.vert else 44)
    return f


def s12(c, t):
    f = B.paper_bg(c, t, c.D, 12)
    p1, p2 = parts(ost(c), "·") + [""] * (2 - len(parts(ost(c), "·")))
    t2 = c.at("1974", "1974", default=c.frac(0.6))
    panels = [("P07", P07, p1, c.lab("الملا مصطفى البارزاني", "مەلا مستەفا بارزانی"), c.a0),
              ("P08", "P08_king_faisal.jpg", p2, c.lab("الملك فيصل", "پاشا فەیسەڵ"), t2 - 0.3)]
    for i, (key, nmf, lab_ost, lab_name, ta) in enumerate(panels):
        if not c.vert:
            cx, cy, hh = c.W * (0.73 - 0.46 * i), c.H * 0.46, 470
        else:
            cx, cy, hh = c.cx, 560 + i * 560, 380
        card = pcard(c, nmf, h=hh, prep=sepia, rot=(-1.5, 1.5)[i])
        b = show(c, f, card, cx, cy, t, ta, "right")
        if b:
            ntag(c, f, lab_name, t, ta + 0.5, cx, b[3] - 40)
            st = ost_card(c, lab_ost, 48 if not c.vert else 44)
            k = ease_out((t - ta - 0.3) / 0.5)
            yy = b[1] - st.height + 30 if not c.vert else b[1] - st.height + 30
            paste(f, st, cx - st.width / 2, yy, k)
    return B.grain(f, t, 5)


def s13(c, t):
    t_road = c.at("السماوة", "سەماوە", default=c.frac(0.2))
    t_taf = c.at("تفسير", "تەفسیری", default=c.frac(0.85))
    t_jail = c.at("سُجن", "زیندانی", default=c.frac(0.05))
    t_hs = c.at("إضرابًا", "مانی", default=c.frac(0.35))
    shots = [(0.0, lambda tt: B.dark_bg(c, 13)),
             (t_road, lambda tt: cover(c, tt, "A08_desert_road_samawah.jpg", (1.0, 1.06), (0.5, 0.5), D=t_taf - t_road + 0.6,
                                       t0=t_road, dark=0.8)),
             (t_taf, lambda tt: cover(c, tt, "A09_handwritten_pages_lamp.jpg", (1.0, 1.05), (0.5, 0.5), D=c.D - t_taf,
                                      t0=t_taf, dark=0.85, vf=(0.55, 0.5)))]
    f = crossfade(c, t, shots, 0.7)
    head, rest = parts(ost(c), "|")[0], parts(ost(c), "|")[-1]
    items = parts(rest, "·")
    show_ost(c, f, head + " |", t, 0.2, cy=c.top + 10 if not c.vert else 430, fg=INK, bg=GOLD)
    times = [t_jail, t_hs, t_taf]
    for i, it in enumerate(items):
        ta = times[i] if i < len(times) else c.frac(0.3 * i)
        show_ost(c, f, it, t, ta, cy=(c.top + 130 + i * 110) if not c.vert else 520 + i * 120, size=50 if not c.vert else 46,
                 rot=(-1.5, 1.0, -0.6)[i % 3])
    card = mcard(c, P09, 340 if not c.vert else 380, 260 if not c.vert else 300)
    b = show(c, f, card, c.W * 0.22 if not c.vert else c.cx, c.H * 0.52 if not c.vert else 1060, t, t_jail + 0.3, "left",
             out=t_road + 0.2)
    if b:
        ntag(c, f, c.lab("الملا علي عبد العزيز", "مەلا عەلی عەبدولعەزیز"), t, t_jail + 0.8, (b[0] + b[2]) / 2, b[3] - 36,
             out=t_road + 0.2)
    return f


def s14(c, t):
    t_map = c.at("عبر", "ڕۆیشت", default=c.frac(0.4)) - 0.3
    t_san = c.at("سنندج", "سنە", default=c.frac(0.6))
    t_hl = c.at("«الحركة", "«بزووتنەوەی", default=c.frac(0.8)) - 0.3
    if t < t_map:
        f = m3(c, t, D=t_map + 0.6)
        show_ost(c, f, ost(c).split("|")[0].strip(), t, c.a0, cy=c.top + 10 if not c.vert else 430, fg=INK, bg=GOLD)
        return f
    f, xy, cam, v = map_frame(c, t, "local", (1.0, 1.08), (0.5, 0.5), D=c.D - t_map, t0=t_map)
    hx, hy = xy("halabja")
    bx, by = xy("border")
    sx, sy = xy("sanandaj")
    city(c, f, hx, hy, nm(c, "halabja"), t, t_map + 0.1, INK, below=True)
    arrow(c, f, (hx, hy), (bx, by), t, t_map + 0.4, 1.0, RED, 7, -0.1, dashed=True)
    ntag(c, f, nm(c, "border"), t, t_map + 1.1, bx, by - 70, size=26)
    arrow(c, f, (bx, by), (sx, sy), t, t_san - 0.8, 1.0, RED, 7, -0.2, dashed=True)
    kit.map_pin(f, sx, sy, t - t_san, RED, 1.2)
    city(c, f, sx, sy, nm(c, "sanandaj"), t, t_san + 0.2, RED, below=True)
    if t > t_hl:
        f = veil(f, 0.35 * ease((t - t_hl) / 0.5))
    show_ost(c, f, ost(c), t, t_hl, cy=c.H * 0.30 if not c.vert else 520, size=60 if not c.vert else 50)
    return B.grain(f, t, 5)


def s15(c, t):
    f = cover(c, t, R04, (1.0, 1.08), (0.32, 0.48), (0.32, 0.44), dark=0.8, vf=(0.32, 0.45), vig=0.6)
    a = ease((t - c.a0 - 0.6) / 1.4)
    if a > 0:
        im = c.get(("s15",), lambda: B.shadowed(wrap_img(c, ost(c), 60 if not c.vert else 52, CREAM, c.tw, False),
                                                12, (0, 6), 170))
        paste(f, im, c.cx - im.width / 2, (c.H * 0.16 if not c.vert else 420) - im.height / 2, a)
    return f


def s16(c, t):
    f = Image.new("RGBA", (c.W, c.H), DARK + (255,))
    if not c.vert:
        w = c.W // 2
        right = cover(c, t, "A02_hujra_interior_lamp.jpg", (1.0, 1.04), (0.3, 0.5), dark=0.8).crop((c.W // 4, 0, c.W // 4 + w, c.H))
        left = cover(c, t, "A11_mountain_front_dusk.jpg", (1.04, 1.0), (0.4, 0.5), dark=0.8).crop((c.W // 4, 0, c.W // 4 + w, c.H))
        f.paste(left, (0, 0))
        f.paste(right, (w, 0))
        p1, p2 = (w + w / 2, c.H * 0.5), (w / 2, c.H * 0.5)
    else:
        h = c.H // 2
        top = cover(c, t, "A02_hujra_interior_lamp.jpg", (1.0, 1.04), (0.3, 0.5), dark=0.8).crop((0, c.H // 4, c.W, c.H // 4 + h))
        bot = cover(c, t, "A11_mountain_front_dusk.jpg", (1.04, 1.0), (0.4, 0.5), dark=0.8).crop((0, c.H // 4, c.W, c.H // 4 + h))
        f.paste(top, (0, 0))
        f.paste(bot, (0, h))
        p1, p2 = (c.cx, h * 0.5), (c.cx, h * 1.5)
    c.illustration()
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0))
    kit.ink_line(ImageDraw.Draw(lay), kit.curve(p1, p2, 0.0, 40), ease((t - 0.5) / 1.0), GOLD, 5)
    f.alpha_composite(lay)
    card = pcard(c, "P01a_sheikh_portrait.jpg", h=380 if not c.vert else 400, prep=warm)
    show(c, f, card, (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, t, 0.8, "bottom")
    a, b = (parts(ost(c), "·") + [""])[:2]
    show_ost(c, f, a, t, c.a0, cy=c.top - 10 if not c.vert else 410)
    t2 = c.at("انتمائه", "پێوەبەستبوونی", default=c.frac(0.7))
    show_ost(c, f, b, t, t2, cy=c.cap_top - 70 if not c.vert else 1290, fg=INK, bg=GOLD)
    return f


def s17(c, t):
    f = B.paper_bg(c, t, c.D, 17)
    a, b = (parts(ost(c), "·") + [""])[:2]
    pairs = [parts(a, "+"), parts(b, "+")]
    t2 = c.at("البعد", "ڕەهەندی", default=c.frac(0.45))
    times = [c.a0 + 0.2, t2]
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    r = 150 if not c.vert else 150
    centres = []
    for i in range(2):
        if not c.vert:
            cx, cy = c.W * (0.70 - 0.40 * i), c.H * 0.50
        else:
            cx, cy = c.cx, 600 + i * 520
        centres.append((cx, cy))
        p = ease((t - times[i]) / 1.0)
        if p <= 0:
            continue
        for j in range(2):
            ox = (r * 0.6) * (1 if j == 0 else -1)
            ov = Image.new("RGBA", f.size, (0, 0, 0, 0))
            if p >= 1:
                ImageDraw.Draw(ov).ellipse([cx + ox - r, cy - r, cx + ox + r, cy + r], fill=(GOLD if j else GREEN) + (40,))
                lay.alpha_composite(ov)
            kit.ink_line(d, kit.ellipse_pts([cx + ox - r, cy - r, cx + ox + r, cy + r], 1.05, seed=i * 2 + j), p, INK, 6)
        gl = ease((t - times[i] - 1.0) / 0.6)
        if gl > 0:
            g = c.get(("vglow",), lambda: B.radial_img(int(r * 0.9), int(r * 1.6), GOLD, 1.2))
            paste(lay, g, cx - g.width / 2, cy - g.height / 2, 0.85 * gl)
    f.alpha_composite(lay)
    for i, pr in enumerate(pairs):
        cx, cy = centres[i]
        k = ease_out((t - times[i] - 0.5) / 0.5)
        if k <= 0:
            continue
        for j, word in enumerate(pr[:2]):
            ox = (r * 0.95) * (1 if j == 0 else -1)
            im = c.get(("vw", word), lambda word=word: T(c.lang, word, 46 if not c.vert else 42, INK, True))
            paste(f, im, cx + ox - im.width / 2, cy - im.height / 2, k)
        if not c.vert:
            plus = c.get(("vplus",), lambda: T(c.lang, "+", 60, GOLD, True))
            paste(f, plus, cx - plus.width / 2, cy - plus.height / 2, k)
    for word_ar, word_ckb, side in (("تقدير", "ڕێز", 0), ("خلاف", "ناکۆکی", 1)):
        ta = c.at(word_ar, word_ckb, default=c.frac(0.8 + 0.1 * side))
        lab = c.lab("محلّ " + word_ar, "جێگەی " + word_ckb)
        x = c.W * (0.88 if side == 0 else 0.12) if not c.vert else c.cx + (250 if side == 0 else -250)
        y = c.H * 0.80 if not c.vert else 1310
        ntag(c, f, lab, t, ta - 0.1, x, y, fill=GREEN if side == 0 else RED, fg=CREAM, size=34 if not c.vert else 30)
    return B.grain(f, t, 5)


def s18(c, t):
    f = B.dark_bg(c, 18)
    t_tree = c.at("إرثه", "میراتەکەی", default=c.frac(0.15))
    t_q = c.at("كيف", "چۆن", default=c.frac(0.7)) - 0.3
    k = clamp01((t_q - t) / 0.5)
    if k > 0 and t > t_tree - 0.3:
        lay = Image.new("RGBA", f.size, (0, 0, 0, 0))
        tree(c, lay, t, (c.cx, c.H * 0.86 if not c.vert else 1300),
             [("", t_tree + 0.6 + 0.25 * i) for i in range(4)], t0=t_tree - 0.2, colour=CREAM)
        paste(f, lay, 0, 0, k * 0.9)
    headline(c, f, ost(c), t, t_q, 96 if not c.vert else 74, c.H * 0.45 if not c.vert else 760, GOLD)
    return f


def s19(c, t):
    t_neg = c.at("مفاوضات", "دانوستان", default=c.frac(0.25)) - 0.5
    t_end = c.at("فلما", "کاتێک", default=c.frac(0.55))
    t_pins = c.at("وسيطرت", "بەسەر", default=c.frac(0.62))
    t_el = c.at("1992", "1992یش", default=c.frac(0.75)) - 0.3
    if t < t_neg:
        f = B.paper_bg(c, t, c.D, 19, tone=(60, 58, 54))
        f = B.darken(f, 0.55)
        a = pcard(c, R09A, w=980 if not c.vert else 900, prep=sepia, rot=-1.5)
        show(c, f, a, c.W * 0.42 if not c.vert else c.cx, c.H * 0.42 if not c.vert else 640, t, 0.3, "left")
        b = pcard(c, R09B, h=330 if not c.vert else 380, prep=sepia, rot=3)
        show(c, f, b, c.W * 0.80 if not c.vert else c.cx + 170, c.H * 0.56 if not c.vert else 1020, t, 1.2, "right")
        show_ost(c, f, parts(ost(c), "·")[0], t, c.a0, cy=c.top - 10 if not c.vert else 410, fg=INK, bg=GOLD)
        return B.grain(f, t, 6)
    if t < t_el:
        f, xy, cam, v = map_frame(c, t, "krg", (1.0, 1.06), (0.5, 0.5), D=t_el - t_neg, t0=t_neg)
        f.alpha_composite(geo.area_tint(v, "krg", GOLD, 40) if False else Image.new("RGBA", f.size, (0, 0, 0, 0)))
        # the front: a gold pause icon while the negotiations last, then it lifts
        s = 150
        pa = ease((t - t_neg - 0.3) / 0.4) * (1 - ease((t - t_end) / 0.6))
        if pa > 0:
            ic = c.get(("pause",), lambda: icon("pause", s))
            paste(f, ic, c.cx - s / 2, c.H * 0.45 - s / 2 - (1 - pa) * 20 if not c.vert else 700 - s / 2, pa)
        for i, (la, lo) in enumerate(((36.35, 43.15), (35.47, 44.39), (36.19, 44.01), (35.56, 45.43), (36.87, 42.99),
                                      (35.85, 45.10))):
            img, vv = gmap(c, "krg")
            x, y = cam.pt(*vv.xy(la, lo))
            kit.map_pin(f, x, y, t - (t_pins + 0.35 * i), GREEN, 0.9)
        show_ost(c, f, ost(c), t, t_neg + 0.2, cy=c.top - 10 if not c.vert else 410)
        return B.grain(f, t, 5)
    f = cover(c, t, "R05_election_1992.jpg", (1.0, 1.05), (0.5, 0.45), D=c.D - t_el, t0=t_el, dark=0.95, vf=(0.12, 0.55))
    return f


def s20(c, t):
    f = B.dark_bg(c, 20)
    bg = cover(c, t, "R02_halabja_pris_village.jpg", (1.0, 1.05), (0.5, 0.5), vf=(0.5, 0.5))
    paste(f, bg, 0, 0, 0.30)
    ta = c.at("قُتل", "کوردیش", default=c.frac(0.45)) - 0.4
    if c.lang == "ckb":
        ta = c.at("ئەگەر", "ئەگەر", default=c.frac(0.45)) - 0.3
    tb = c.at("مسلم»", "موسوڵمانە»", default=c.frac(0.6)) + 0.3
    quote(c, f, ost(c), t, c.a0 + 0.2, hl=(ta, tb))
    return f


def s21(c, t):
    f = B.paper_bg(c, t, c.D, 21)
    a, b = (parts(ost(c), "←") + [""])[:2]
    t_pe = c.at("فسعى", "هەوڵی", default=c.frac(0.3)) - 0.2
    t_ram = c.at("رمضان،", "ڕەمەزاندا", default=c.frac(0.8)) - 0.6
    # 500+ counter first
    if t < t_pe + 0.4:
        k = clamp01((t - c.a0) / 1.6)
        txt = re.sub(r"\d+", lambda m: str(int(int(m.group(0)) * ease_out(k))), a)
        im = c.get(("s21c", txt), lambda: T(c.lang, txt, 150 if not c.vert else 120, RED, True))
        paste(f, im, c.cx - im.width / 2, c.H * 0.42 - im.height / 2 if not c.vert else 640, clamp01((t_pe + 0.4 - t) / 0.4))
        return B.grain(f, t, 5)
    # the real photo with Masoud Barzani and Jalal Talabani (attached by the author) on the mediation line
    pw, ph = (1060, 612) if not c.vert else (1000, 577)
    cy = c.H * 0.41 if not c.vert else 640
    bx = photo_frame(c, f, P22, pw, ph, c.cx, cy, t, t_pe + 0.1, D=c.D - t_pe)
    if bx:
        ntag(c, f, c.lab("مع مسعود بارزاني وجلال طالباني", "لەگەڵ مەسعود بارزانی و جەلال تاڵەبانی"), t, t_pe + 0.6,
             c.cx, bx[3] + 10, size=30 if not c.vert else 30, out=t_ram if not c.vert else None)
    ka = ease_out((t - t_ram) / 0.5)
    if ka > 0:
        cr = c.get(("cres",), lambda: icon("crescent", 110, GOLD))
        pp = c.get(("paper",), lambda: icon("paper", 120, INK))
        y = c.H * 0.79 if not c.vert else 1220
        st = ost_card(c, b, 46 if not c.vert else 42, None, INK, CREAM, -1)
        x = c.cx + st.width / 2 + 20
        paste(f, cr, x, y - 55, ka)
        paste(f, st, c.cx - st.width / 2, y - st.height / 2, ka)
        paste(f, pp, c.cx - st.width / 2 - 140, y - 60, ease_out((t - t_ram - 0.8) / 0.5))
    return B.grain(f, t, 5)


def photo_frame(c, f, name, w, h, cx, cy, t, t0, D=None, z=(1.0, 1.04)):
    """A real photo in a cream frame with a slow Ken Burns move inside (the frame keeps every face in view)."""
    if t < t0:
        return None
    im = B.photo_box(c, name, w, h, t - t0, D or c.D, z)
    fr = Image.new("RGBA", (w + 12, h + 12), CREAM + (255,))
    fr.alpha_composite(im, (6, 6))
    k = ease_out((t - t0) / 0.6)
    out = B.shadowed(fr, 12, (6, 10), 120)
    pad = 36
    x, y = cx - fr.width / 2, cy - fr.height / 2
    paste(f, out, x - pad, y - pad + (1 - k) * 30, k)
    return (x, y, x + fr.width, y + fr.height)


def _flashes(c, f, t, t0, n=5):
    for k in range(n):
        tk = t0 + 0.35 * k + (k % 2) * 0.12
        a = clamp01(1 - abs(t - tk) / 0.09)
        if a > 0:
            g = c.get(("flash",), lambda: B.radial_img(int(c.W * 0.9), int(c.H * 0.9), (255, 255, 250), 1.4))
            x = c.W * (0.2 + 0.15 * ((k * 3) % 5))
            paste(f, g, x - g.width / 2, c.H * 0.4 - g.height / 2, 0.8 * a)


def s22(c, t):
    t_par = c.at("البرلمان", "پەرلەمانی", default=c.frac(0.5)) - 0.3
    t_q = c.at("القرضاوي", "قەرەزاوی", default=c.frac(0.78)) - 0.4
    t_50 = c.at("خمسين", "پەنجا", default=c.frac(0.2))
    if t < t_par:
        big = re.search(r"\+?\d+", ost(c).split("·")[-1])
        title = big.group(0) if big else "+50"
        f = behind(c, t, P13, title, t_50 - 0.4, 440 if not c.vert else 330, c.H * 0.20 if not c.vert else 560,
                   prep=None, dark=0.75, foc=(0.5, 0.5), z=(1.0, 1.04), gold=True)
        show_ost(c, f, ost(c), t, c.a0 + 0.2, cy=c.cap_top - 60 if not c.vert else 1280, size=44 if not c.vert else 40)
        return f
    if t < t_q:
        f = cover(c, t, "R07_turkish_parliament.jpg", (1.0, 1.06), (0.5, 0.5), D=t_q - t_par + 0.6, t0=t_par, dark=0.9,
                  vf=(0.5, 0.5))
        _flashes(c, f, t, t_par + 1.0, 6)
        return f
    f = cover(c, t, "P01f_sheikh.jpg", (1.0, 1.05), (0.5, 0.4), D=c.D - t_q, t0=t_q, dark=0.55, vf=(0.55, 0.4))
    card = pcard(c, "P14_yusuf_qaradawi.jpg", h=360 if not c.vert else 380, rot=-2)
    bx = show(c, f, card, c.W * 0.76 if not c.vert else c.cx, c.H * 0.44 if not c.vert else 640, t, t_q + 0.1, "right")
    if bx:
        ntag(c, f, c.lab("الشيخ يوسف القرضاوي", "شێخ یوسف قەرەزاوی"), t, t_q + 0.5, (bx[0] + bx[2]) / 2, bx[3] - 36)
        qt = c.lab("«شيخنا، أحببناك قبل أن نراك»", "«مامۆستامان، پێش ئەوەی بتبینین خۆشمان ویستی»")
        st = ost_card(c, qt, 44 if not c.vert else 40, (c.W * 0.5 if not c.vert else c.tw - 40), INK, GOLD, 1.0)
        k = ease_out((t - t_q - 1.0) / 0.5)
        x = c.W * 0.36 if not c.vert else c.cx
        y = c.H * 0.48 if not c.vert else 1050
        paste(f, st, x - st.width / 2, y - st.height / 2, k)
    return f


def s22b(c, t):
    a, b = (parts(ost(c), "·") + [""])[:2]
    t_sal = c.at("صلاح", "سەلاحەدینی", default=c.frac(0.4)) - 0.3
    t_89 = c.at("1989", "1989یش", default=c.frac(0.8)) - 0.4
    if t < t_89:
        f, xy, cam, v = map_frame(c, t, "pal", (1.0, 1.04), (0.5, 0.5), D=t_89 + 0.5)
        lay = Image.new("RGBA", f.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        img, vv = gmap(c, "pal")
        ring = [cam.pt(*p) for p in geo._smooth(vv.ring(geo.AREAS["kurdistan"]) + vv.ring(geo.AREAS["kurdistan"])[:1], 5)]
        p1 = ease((t - 0.4) / 1.4)
        kit.ink_line(d, kit.resample(ring, 6), p1, GOLD, 4)
        pal = [(34.25, 31.2), (34.6, 32.4), (35.1, 33.1), (35.6, 32.7), (35.5, 31.5), (35.0, 29.6), (34.5, 30.4)]
        pr = [cam.pt(*vv.xy(la, lo)) for lo, la in pal]
        kit.ink_line(d, kit.resample(pr + pr[:1], 5), ease((t - 0.9) / 1.2), GOLD, 4)
        f.alpha_composite(lay)
        kx, ky = xy("kurdistan")
        px, py = xy("palestine")
        city(c, f, kx, ky, nm(c, "kurdistan"), t, 1.0, GREEN, glow=False)
        city(c, f, px, py, nm(c, "palestine"), t, 1.3, GREEN, below=True)
        show_ost(c, f, a, t, c.at("شعبان", "گەلی", default=c.frac(0.1)) - 0.2, cy=c.top - 10 if not c.vert else 410,
                 fg=INK, bg=GOLD)
        if t > t_sal:
            card = name_card(c, c.lab("صلاح الدين الأيوبي", "سەلاحەدینی ئەیووبی"))
            k = ease_out((t - t_sal) / 0.5)
            paste(f, card, c.cx - card.width / 2, (c.H * 0.62 if not c.vert else 1080) - card.height / 2 + (1 - k) * 30,
                  k * clamp01((t_89 - 0.6 - t) / 0.4 + 1))
        return B.grain(f, t, 5)
    f = glow_bg(c, t, 22, (60, 66, 58))
    labels = [x.strip() for x in re.split(r"\s*·\s*", c.sc.get("labels", "")) if x.strip()]
    labels = [re.sub(r"^\d+\s+", "", x) for x in labels]
    show_ost(c, f, b, t, t_89, cy=c.top - 10 if not c.vert else 410, fg=INK, bg=GOLD)
    # the real 1989 photo (not mirrored), slow Ken Burns; name tags in the order of the original caption, right to left
    pw, ph = (900, 614) if not c.vert else (1000, 683)
    cy = c.H * 0.50 if not c.vert else 830
    bx = photo_frame(c, f, P16, pw, ph, c.cx, cy, t, t_89 + 0.2, D=c.D - t_89, z=(1.0, 1.035))
    if bx:
        ntag(c, f, c.lab("لقاء مع أحمد جبريل", "دیدار لەگەڵ ئەحمەد جیبریل"), t, t_89 + 0.6, bx[2] - 20, bx[1] + 18,
             "right", size=28, fill=(28, 30, 34), fg=CREAM)
        xs = [0.80, 0.62, 0.43, 0.22]                     # where each person stands in the photo, right to left
        for i, lab in enumerate(labels[:4]):
            lx = bx[0] + 6 + (bx[2] - bx[0] - 12) * xs[i]
            ly = bx[3] - (70 if i % 2 == 0 else 122)
            ntag(c, f, lab, t, t_89 + 1.0 + 0.45 * i, lx, ly, size=22 if not c.vert else 22)
    return f


def s23(c, t):
    f = cover(c, t, "A13_dim_room_generator.jpg", (1.0, 1.06), (0.55, 0.5), dark=0.85, vf=(0.72, 0.5))
    q = ost(c)
    q1, q2 = (parts(q, "…") + [""])[:2]
    t1 = c.at("«اشترِ", "«بۆ", default=c.frac(0.8)) - 0.2
    t2 = c.at("أو", "یان", nth=0, default=t1 + 1.0)
    if t2 < t1:
        t2 = t1 + 1.0
    if t > t1:
        f = veil(f, 0.4 * ease((t - t1) / 0.5))
    y = c.H * 0.34 if not c.vert else 640
    a = headline(c, f, q1 + "…", t, t1, 76 if not c.vert else 62, y, CREAM)
    headline(c, f, q2, t, t2, 76 if not c.vert else 62, y + (120 if not c.vert else 130), GOLD)
    return f


def s24(c, t):
    t_z = c.at("زبير", "زوبەیر", default=c.frac(0.5)) - 0.4
    t_p = c.at("رفض", "ڕەتی", default=c.frac(0.8)) - 0.6
    shots = [(0.0, lambda tt: cover(c, tt, "A14_merchant_ledger_coins.jpg", (1.0, 1.06), (0.5, 0.55), D=t_z + 0.6, vf=(0.55, 0.5))),
             (t_z, lambda tt: cover(c, tt, "P17_zubair_with_brothers.jpg", (1.0, 1.05), (0.5, 0.45), D=t_p - t_z + 0.8, t0=t_z,
                                    vf=(0.5, 0.45))),
             (t_p, lambda tt: cover(c, tt, "P01c_sheikh_older.jpg", (1.0, 1.08), (0.65, 0.4), (0.68, 0.36), D=c.D - t_p, t0=t_p,
                                    dark=0.8, vf=(0.68, 0.4)))]
    f = crossfade(c, t, shots, 0.9)
    if t_z <= t < t_p:
        ntag(c, f, c.lab("ابنه زبير", "کوڕەکەی زوبەیر"), t, t_z + 0.5, c.W - c.margin if not c.vert else c.cx,
             c.cap_top - 80 if not c.vert else 1240, "right" if not c.vert else "center", size=32)
    t_q = c.at("المال", "پارەم", default=c.frac(0.92)) - 0.5
    headline(c, f, ost(c), t, t_q, 96 if not c.vert else 80, c.H * 0.24 if not c.vert else 470, CREAM)
    return f


def s25(c, t):
    f = m4(c, t)
    ntag(c, f, c.lab("أنقرة ← إسطنبول", "ئەنقەرە ← ئەستەنبوڵ"), t, c.at("أنقرة", "ئەنقەرە", default=c.frac(0.6)) - 0.2,
         c.W - c.margin if not c.vert else c.cx, c.H * 0.70 if not c.vert else 1150, "right" if not c.vert else "center",
         size=36, fill=(28, 30, 34), fg=CREAM)
    headline(c, f, ost(c), t, c.a0 + 0.3, 80 if not c.vert else 64, c.H * 0.20 if not c.vert else 430, CREAM)
    return f


def _wall(c, f, t, t0, cx, cy):
    """A soft wall of bricks that holds (does not crack)."""
    k = ease((t - t0) / 2.6)
    if k <= 0:
        return
    bw, bh = (110, 52) if not c.vert else (96, 46)
    rows, cols = 6, 9 if not c.vert else 7
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0 = cx - cols * bw / 2
    y0 = cy + rows * bh / 2
    nshow = int(rows * cols * k)
    i = 0
    for r in range(rows):
        for q in range(cols):
            if i >= nshow:
                break
            off = bw / 2 if r % 2 else 0
            x = x0 + q * bw + off - bw / 4
            y = y0 - (r + 1) * bh
            d.rounded_rectangle([x, y, x + bw - 8, y + bh - 8], 6, fill=(214, 196, 166, 255), outline=(150, 126, 96, 255), width=2)
            i += 1
    f.alpha_composite(lay)


def s26(c, t):
    t_tf = c.at("وترك", "تەفسیرێکی", default=c.frac(0.6)) - 0.4
    if t < t_tf:
        f = B.paper_bg(c, t, c.D, 26)
        _wall(c, f, t, c.a0 + 0.3, c.cx, c.H * 0.5 if not c.vert else 800)
        tg = c.at("جدار", "دیواری", default=c.frac(0.35))
        ga = ease((t - tg) / 0.8)
        if ga > 0:
            g = c.get(("wglow",), lambda: B.radial_img(900, 500, GOLD, 1.6))
            paste(f, g, c.cx - 450, (c.H * 0.5 if not c.vert else 800) - 250, 0.45 * ga)
            _wall(c, f, t, -10, c.cx, c.H * 0.5 if not c.vert else 800)
        return B.grain(f, t, 5)
    f = B.paper_bg(c, t, c.D, 27, tone=(60, 56, 50))
    f = B.darken(f, 0.6)
    card = pcard(c, "D01_tafsir_10_volumes.jpg", h=560 if not c.vert else 600, rot=-1)
    show(c, f, card, c.W * 0.66 if not c.vert else c.cx, c.H * 0.45 if not c.vert else 690, t, t_tf + 0.1, "right")
    k = clamp01((t - t_tf - 0.6) / 2.2)
    n = max(1, int(round(10 * ease_out(k)))) if k > 0 else 0
    if n:
        num = c.get(("s26n", n), lambda: T(c.lang, str(n), 200 if not c.vert else 170, GOLD, True))
        x = c.W * 0.24 if not c.vert else c.cx
        y = c.H * 0.36 if not c.vert else 1120
        paste(f, B.shadowed(num, 8, (0, 4), 160), x - num.width / 2 - 24, y - num.height / 2 - 24)
    for i, p in enumerate(parts(ost(c), "·")):
        show_ost(c, f, p, t, t_tf + 1.0 + i * c.at("البخاري", "بوخاری", default=c.frac(0.9)) * 0 + i * 1.6,
                 cy=(c.H * 0.62 + i * 100) if not c.vert else 1240 + i * 0, x=c.W * 0.26 if not c.vert else c.cx,
                 size=44 if not c.vert else 40, out=None if (not c.vert or i == 1) else t_tf + 2.6)
    return B.grain(f, t, 5)


def crit_bg(c, t, name, dark=0.45, vf=(0.5, 0.5)):
    return cover(c, t, name, (1.0, 1.04), (0.5, 0.5), dark=dark, vf=vf)


def s27(c, t):
    t_env = c.at("رسالتهم", "نامەکەش", default=c.frac(0.7)) - 0.3
    t_q = c.at("القرضاوي:", "قەرەزاوییش", default=c.frac(0.88)) - 0.3
    bg = crossfade(c, t, [(0.0, lambda tt: crit_bg(c, tt, "A16_old_doorway_pawe.jpg", 0.5, (0.35, 0.5))),
                          (t_env, lambda tt: crit_bg(c, tt, "A17_old_envelope_intact.jpg", 0.55, (0.45, 0.6)))], 0.8)
    f, yb = verdict(c, t, bg)
    if t > t_q:
        card = pcard(c, "P14_yusuf_qaradawi.jpg", h=300 if not c.vert else 320, rot=2)
        bx = show(c, f, card, c.W * 0.84 if not c.vert else c.cx, c.H * 0.64 if not c.vert else 1120, t, t_q, "right")
        if bx:
            ntag(c, f, c.lab("القرضاوي", "قەرەزاوی"), t, t_q + 0.4, (bx[0] + bx[2]) / 2, bx[3] - 36)
    return f


def s28(c, t):
    f, xy, cam, v = map_frame(c, t, "region", (1.0, 1.05), (0.55, 0.5))
    f = B.darken(f, 0.9)
    hx, hy = xy("halabja")
    city(c, f, hx, hy, nm(c, "halabja"), t, 0.3, RED, below=True)
    t_links = c.at("صلاته", "پەیوەندییەکانی", default=c.frac(0.5)) - 0.3
    for i, key in enumerate(("riyadh", "ankara", "tehran")):
        x, y = xy(key)
        ta = t_links + 0.5 * i
        arrow(c, f, (hx, hy), (x, y), t, ta, 1.0, GOLD, 4, 0.15 * (1 if i % 2 else -1), dashed=True)
        city(c, f, x, y, nm(c, key), t, ta + 0.8, INK, below=key != "ankara")
    f, yb = verdict(c, t, f)
    t_sd = c.at("صدام", "سەددام", default=c.frac(0.3)) - 0.2
    card = pcard(c, P21, h=200 if not c.vert else 220, prep=desat, rot=-2)
    bx = show(c, f, card, c.W * 0.14 if not c.vert else c.cx - 230, c.H * 0.70 if not c.vert else 1180, t, t_sd, "left",
              out=t_sd + 2.3)
    if bx:
        ntag(c, f, c.lab("نظام صدام", "ڕژێمی سەددام"), t, t_sd + 0.3, (bx[0] + bx[2]) / 2, bx[3] - 32, size=24,
             fill=(40, 40, 40), fg=CREAM, out=t_sd + 2.3)
    t_tw = c.at("توحيدي", "تەوحیدی", default=c.frac(0.9)) - 0.6
    card = pcard(c, "P15_abdulqadir_tawhidi.jpg", h=250 if not c.vert else 300, rot=2)
    # v2: right-aligned to the safe margin so it never covers the (wider, Sorani) verdict strip
    bx = show(c, f, card, c.W - 70 - card.width / 2 if not c.vert else c.cx, c.H * 0.66 if not c.vert else 1130, t, t_tw,
              "right")
    if bx:
        ntag(c, f, c.lab("عبد القادر توحيدي | 1984", "عەبدولقادر تەوحیدی | 1984"), t, t_tw + 0.4, (bx[0] + bx[2]) / 2,
             bx[3] - 36)
    return B.grain(f, t, 5)


def s28b(c, t):
    t_c1 = c.at("1989،", "1989،", default=c.frac(0.15)) - 0.3
    t_c2 = c.at("الاقتتال", "شەڕی", default=c.frac(0.45)) - 0.3
    t_dr = c.at("ويتحدّى", "نزیکەکانی", default=c.frac(0.72)) - 0.3
    if t < t_c2:
        bg = B.darken(B.paper_bg(c, t, c.D, 28, tone=(70, 66, 60)), 0.6)
    elif t < t_dr:
        bg, xy, cam, v = map_frame(c, t, "krg_qv" if c.vert else "krg_q", (1.0, 1.05), (0.45, 0.5), D=t_dr - t_c2, t0=t_c2)
        bg = B.darken(bg, 0.85)
    else:
        bg = crit_bg(c, t, "A19_empty_archive_drawer.jpg", 0.55, (0.4, 0.55))
    f, yb = verdict(c, t, bg, t_v=c.sc.get("verdict_t"))
    if t_c1 <= t < t_c2:
        card = name_card(c, c.lab("ليث شبيلات", "لەیس شوبەیلات"), sub=c.lab("سياسي إسلامي، الأردن",
                                                                           "سیاسەتمەداری ئیسلامی، ئوردن"),
                         w=460 if not c.vert else None, size=54 if not c.vert else None)
        k = ease_out((t - t_c1) / 0.5)
        # v2: right-aligned to the safe margin and a little lower, clear of the (wider) verdict stamp
        x = c.W - 64 - card.width / 2 if not c.vert else c.cx
        y = c.H * 0.72 if not c.vert else 1090
        paste(f, card, x - card.width / 2, y - card.height / 2 + (1 - k) * 30, k)
        ntag(c, f, c.lab("طهران 1989", "تاران 1989"), t, t_c1 + 0.5, x, y + card.height / 2 - 10, fill=(28, 30, 34),
             fg=CREAM)
    elif t_c2 <= t < t_dr:
        qx, qy = xy("qushtapa")
        kit.map_pin(f, qx, qy, t - t_c2 - 0.4, RED, 1.2)
        city(c, f, qx, qy + 6, nm(c, "qushtapa"), t, t_c2 + 0.7, RED, below=True)
        t_wait = c.at("ست", "سی", default=c.frac(0.6)) - 1.5
        back = ease((t - (t_wait + 2.6)) / 1.0)
        for i in range(2):
            tr = c.get(("truck",), lambda: icon("truck", 130, INK))
            if back > 0:
                tr = tr.transpose(Image.FLIP_LEFT_RIGHT)
            x = qx + 110 + i * 150 + back * 500
            paste(f, tr, x - 65, qy - 80, ease_out((t - t_c2 - 0.8 - 0.3 * i) / 0.5) * (1 - clamp01(back * 1.4 - 0.4)))
        h = int(round(36 * ease_out(clamp01((t - t_wait) / 2.4))))
        if t > t_wait:
            txt = c.lab(f"{h} ساعة", f"{h} کاتژمێر")
            im = c.get(("hrs", h), lambda: B.pill(c.lang, txt, 46, GOLD, INK))
            paste(f, im, c.cx - im.width / 2, c.H * 0.80 if not c.vert else 1235)
    return f


def s29(c, t):
    bg = B.darken(B.paper_bg(c, t, c.D, 29, tone=(58, 60, 56)), 0.7)
    f, yb = verdict(c, t, bg)
    lab = c.lab("لا تكفير · لا غلوّ", "نە تەکفیر · نە زیادەڕۆیی")
    t_tr = c.at("كان", "لەسەر", default=c.frac(0.3)) - 0.2
    if t > t_tr:
        lay = Image.new("RGBA", f.size, (0, 0, 0, 0))
        tree(c, lay, t, (c.cx, c.H * 0.84 if not c.vert else 1340), [], t0=t_tr, trunk_label=lab, trunk_only=True,
             colour=CREAM, height=0.30 if not c.vert else 0.28)
        f.alpha_composite(lay)
    return f


def s30(c, t):
    bg = B.darken(B.paper_bg(c, t, c.D, 30, tone=(58, 60, 56)), 0.7)
    f, yb = verdict(c, t, bg)
    t_p = c.at("الصلح.", "ئاشتی", default=c.frac(0.85)) - 0.8
    k = ease_out((t - t_p) / 0.5)
    if k > 0:
        pp = c.get(("paper2",), lambda: icon("paper", 200, INK))
        paste(f, pp, c.cx - 100, (c.H * 0.70 if not c.vert else 1100) - 100 + (1 - k) * 30, k)
    return f


def _s31_wide(c, t):
    f = B.paper_bg(c, t, c.D, 31)
    root = (c.cx, c.H * 0.83 if not c.vert else 1290)
    # root: dawn over Hawraman (no grave photo exists), with the place name
    rc = pcard(c, "A18_dawn_hawraman.jpg", w=420 if not c.vert else 440)
    c.illustration()
    show(c, f, rc, root[0], root[1], t, c.a0, "bottom")
    ntag(c, f, nm(c, "halabja"), t, c.a0 + 0.4, root[0], root[1] + rc.height / 2 - 70, fill=(28, 30, 34), fg=CREAM)
    t1 = c.at("الأم", "دایک", default=c.frac(0.4))
    t2 = c.at("الوحدة", "یەکگرتنی", default=c.frac(0.5))
    t3 = c.at("والجماعة", "کۆمەڵی", default=c.frac(0.62))
    t4 = c.at("مسارات", "ڕێڕەوی", default=c.frac(0.8))
    br = [(c.lab("الحركة الإسلامية الأم", "بزووتنەوەی ئیسلامیی دایک"), t1),
          (c.lab("حركة الوحدة الإسلامية (1999)", "بزووتنەوەی یەکگرتنی ئیسلامی (1999)"), t2),
          (c.lab("الجماعة الإسلامية ← جماعة العدل (2001/2021)", "کۆمەڵی ئیسلامی ← کۆمەڵی دادگەری (2001/2021)"), t3)]
    top, labs = tree(c, f, t, (root[0], root[1] - rc.height / 2 + 20), br, t0=c.a0 + 0.3,
                     height=0.34 if not c.vert else None)
    show_ost(c, f, ost(c), t, c.a0 + 0.2, cy=c.top - 30 if not c.vert else 390, size=46 if not c.vert else 42)
    # extra people photos (ASSETS.md A2), small cut-outs with a name label next to their branch
    people = [(P20, c.lab("عرفان علي عبد العزيز", "عیرفان عەلی عەبدولعەزیز"), 0, t1 + 0.5, True),
              ("P10_mulla_siddiq_abdulaziz.jpg", c.lab("الملا صديق عبد العزيز", "مەلا سدیق عەبدولعەزیز"), 1, t2 + 0.5, False),
              ("P18_ali_bapir.jpg", c.lab("علي بابير", "عەلی باپیر"), 2, t3 + 0.6, False)]
    for nmf, lab, bi, ta, matte in people:
        if bi >= len(labs) or labs[bi] is None:
            continue
        x0, y0, x1, y1 = labs[bi]
        hh = 170 if not c.vert else 150
        card = mcard(c, nmf, int(hh * 1.1), hh) if matte else pcard(c, nmf, h=hh)
        cx_ = (x0 + x1) / 2
        cy_ = y1 + hh / 2 + 34 if not c.vert else y0 - hh / 2 + 20
        if c.vert:
            cx_ = 160 if bi % 2 else c.W - 250
            cy_ = y1 + hh / 2 + 30
        b = show(c, f, card, cx_, cy_, t, ta, "bottom")
        if b:
            ntag(c, f, lab, t, ta + 0.3, (b[0] + b[2]) / 2, b[3] - 34, size=22)
    # 'other paths': Salahaddin Bahaaddin as a separate small card beside the tree, not a branch
    card = pcard(c, P19, h=190 if not c.vert else 170, rot=2)
    px, py = (c.W * 0.27, c.H * 0.68) if not c.vert else (c.cx - 260, 1150)
    b = show(c, f, card, px, py, t, t4, "left")
    if b:
        ntag(c, f, c.lab("صلاح الدين بهاء الدين", "سەلاحەدین بەهائەدین"), t, t4 + 0.3, (b[0] + b[2]) / 2, b[3] - 34, size=22)
        ntag(c, f, c.lab("مسارات أخرى", "ڕێڕەوی تر"), t, t4 + 0.6, (b[0] + b[2]) / 2, b[1] - 36, size=24, fill=(28, 30, 34),
             fg=CREAM)
    return B.grain(f, t, 5)


def s31(c, t):
    if not c.vert:
        return _s31_wide(c, t)
    f = B.paper_bg(c, t, c.D, 31)
    root = (c.cx, 1250)
    rc = pcard(c, "A18_dawn_hawraman.jpg", w=420)
    c.illustration()
    show(c, f, rc, root[0], root[1], t, c.a0, "bottom")
    ntag(c, f, nm(c, "halabja"), t, c.a0 + 0.4, root[0], root[1] + rc.height / 2 - 70, fill=(28, 30, 34), fg=CREAM)
    show_ost(c, f, ost(c), t, c.a0 + 0.2, cy=410, size=42)
    t1 = c.at("الأم", "دایک", default=c.frac(0.4))
    t2 = c.at("الوحدة", "یەکگرتنی", default=c.frac(0.5))
    t3 = c.at("والجماعة", "کۆمەڵی", default=c.frac(0.62))
    t4 = c.at("مسارات", "ڕێڕەوی", default=c.frac(0.8))
    rows = [(c.lab("الحركة الإسلامية الأم", "بزووتنەوەی ئیسلامیی دایک"), t1, P20, c.lab("عرفان علي عبد العزيز", "عیرفان عەلی عەبدولعەزیز"), True),
            (c.lab("حركة الوحدة الإسلامية (1999)", "بزووتنەوەی یەکگرتنی ئیسلامی (1999)"), t2, "P10_mulla_siddiq_abdulaziz.jpg",
             c.lab("الملا صديق عبد العزيز", "مەلا سدیق عەبدولعەزیز"), False),
            (c.lab("الجماعة الإسلامية ← جماعة العدل (2001/2021)", "کۆمەڵی ئیسلامی ← کۆمەڵی دادگەری (2001/2021)"), t3,
             "P18_ali_bapir.jpg", c.lab("علي بابير", "عەلی باپیر"), False)]
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    top = 560
    p = ease((t - c.a0 - 0.3) / 0.9)
    kit.ink_line(d, [(c.cx, root[1] - rc.height / 2 + 20), (c.cx, root[1] - rc.height / 2 + 20 - (root[1] - rc.height / 2 - top) * p)],
                 1.0, INK, 12)
    f.alpha_composite(lay)
    for i, (lab, ta, pf, pname, matte) in enumerate(rows):
        y = 560 + i * 200
        k = ease_out((t - ta) / 0.5)
        if k <= 0:
            continue
        im = c.get(("vrow", lab), lambda lab=lab: B.fit_w(B.strip_img(c.lang, lab, 34, INK, CREAM), 600))
        x = c.cx + 70 - im.width / 2
        paste(f, im, x + (1 - k) * 60, y - im.height / 2, k)
        card = mcard(c, pf, 150, 130) if matte else pcard(c, pf, h=130)
        b = show(c, f, card, 150, y + 30, t, ta + 0.4, "left")
        if b:
            ntag(c, f, pname, t, ta + 0.7, (b[0] + b[2]) / 2 + 40, b[3] - 30, size=22)
    card = pcard(c, P19, h=150, rot=2)
    b = show(c, f, card, 150, 1180, t, t4, "left")
    if b:
        ntag(c, f, c.lab("صلاح الدين بهاء الدين", "سەلاحەدین بەهائەدین"), t, t4 + 0.3, (b[0] + b[2]) / 2 + 40, b[3] - 30, size=22)
        ntag(c, f, c.lab("مسارات أخرى", "ڕێڕەوی تر"), t, t4 + 0.6, (b[0] + b[2]) / 2 + 40, b[1] - 30, size=22,
             fill=(28, 30, 34), fg=CREAM)
    return B.grain(f, t, 5)


def s31b(c, t):
    f, xy, cam, v = map_frame(c, t, "krg", (1.0, 1.04), (0.5, 0.5))
    img, vv = gmap(c, "krg")
    t_p = c.at("تتولّى", "سێ", default=c.frac(0.25)) - 0.2
    t_sm = c.at("وتشارك", "پێکهاتەکانی", default=c.frac(0.5)) - 0.2
    t_cr = c.at("لكن", "بەڵام", default=c.frac(0.78)) - 0.2
    ring = [cam.pt(*p) for p in vv.ring(geo.AREAS["krg"])]
    tint = Image.new("RGBA", f.size, (0, 0, 0, 0))
    ImageDraw.Draw(tint).polygon(ring, fill=GOLD + (70,), outline=INK + (200,))
    f.alpha_composite(tint)
    names = [c.lab("قضائية", "دادوەری"), c.lab("تنفيذية", "جێبەجێکردن"), c.lab("تشريعية", "یاسادانان")]
    base_y = c.H * 0.74 if not c.vert else 1160
    pw, ph = (150, 300) if not c.vert else (140, 280)
    gap = 90 if not c.vert else 50
    lay = Image.new("RGBA", f.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i, n_ in enumerate(names):
        k = ease((t - t_p - 0.4 * i) / 0.8)
        if k <= 0:
            continue
        x = c.cx + (1 - i) * (pw + gap) - pw / 2
        h = ph * k
        d.rectangle([x, base_y - h, x + pw, base_y], fill=(236, 230, 214, 245), outline=INK + (255,), width=4)
        d.rectangle([x - 14, base_y - h - 22, x + pw + 14, base_y - h], fill=(222, 214, 196, 245), outline=INK + (255,), width=4)
        im = c.get(("pil", n_), lambda n_=n_: B.fit_w(T(c.lang, n_, 34, INK, True), pw + 40))
        paste(lay, im, x + pw / 2 - im.width / 2, base_y + 12, k)
    for j in range(6):
        k = ease_out((t - t_sm - 0.25 * j) / 0.5)
        if k <= 0:
            continue
        side = -1 if j % 2 else 1
        x = c.cx + side * (1.5 * (pw + gap) + 30 + (j // 2) * 70)
        d.rectangle([x - 28, base_y - 60 * k, x + 28, base_y], fill=(214, 200, 176, 235), outline=INK + (220,), width=3)
    f.alpha_composite(lay)
    cr = ease((t - t_cr) / 2.0)
    if cr > 0:
        # the map slowly cracks into two halves
        W, H = f.size
        mask = Image.new("L", (W, H), 0)
        pts = [(W * 0.52, 0), (W * 0.48, H * 0.3), (W * 0.54, H * 0.55), (W * 0.47, H * 0.8), (W * 0.52, H)]
        ImageDraw.Draw(mask).polygon([(0, 0)] + pts + [(0, H)], fill=255)
        left = f.copy()
        right = f.copy()
        sh = int(26 * cr)
        out = Image.new("RGBA", (W, H), DARK + (255,))
        out.paste(right, (sh, 0), Image.eval(mask, lambda v: 255 - v))
        out.paste(left, (-sh, 0), mask)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        kit.ink_line(ImageDraw.Draw(lay), kit.resample([(x, y) for x, y in pts], 6), clamp01(cr * 1.5), INK, 4)
        out.alpha_composite(lay)
        f = out
    show_ost(c, f, ost(c), t, t_cr + 0.4, cy=c.top - 20 if not c.vert else 410, size=48 if not c.vert else 42, fg=INK, bg=GOLD)
    return B.grain(f, t, 5)


def s32(c, t):
    return behind(c, t, "P01a_sheikh_portrait.jpg", ost(c), c.frac(0.55), 150 if not c.vert else 110,
                  c.H * 0.40 if not c.vert else 470, bgfn=lambda tt: glow_bg(c, tt, 32, (150, 110, 50)),
                  foc=(0.5, 0.45), z=(1.0, 1.04), side=True)


def s33(c, t):
    a = 0.0                                         # the chapter card covers the first CHAPTER_PRE seconds
    open0, open1 = c.sc.get("clip_open", [1.6, 8.6])
    t_ph = open1 + (c.D - open1) * 0.18
    t_p1g = open1 + (c.D - open1) * 0.32
    t_map = c.at("وأُقيمت", "مەجلیسی", default=c.frac(0.3)) - 0.4
    t_q = c.at("وقال", "یەکێک", default=c.frac(0.7)) - 0.2
    shots = [(0.0, lambda tt: funeral_clip(c, max(0, tt - open0))),
             (t_ph, lambda tt: cover(c, tt, "R01b_funeral_1999_photo.jpg", (1.05, 1.0), (0.5, 0.5), D=t_p1g - t_ph + 0.6,
                                     t0=t_ph, vf=(0.55, 0.5))),
             (t_p1g, lambda tt: cover(c, tt, "P01g_sheikh.jpg", (1.0, 1.05), (0.4, 0.4), D=t_map - t_p1g + 0.6, t0=t_p1g,
                                      dark=0.9, vf=(0.35, 0.4))),
             (t_map, lambda tt: _cities(c, tt, t_map))]
    f = crossfade(c, t, shots, 0.7)
    if t > t_q:
        f = veil(f, 0.45 * ease((t - t_q) / 0.5))
        quote(c, f, ost(c), t, t_q)
    return f


def _cities(c, t, t0):
    f, xy, cam, v = map_frame(c, t, "region", (1.08, 1.0), (0.62, 0.42), D=c.D - t0, t0=t0)
    keys = ["halabja", "erbil", "pawe", "sanandaj", "marivan", "damascus"]
    words = [("حلبجة", "هەڵەبجە"), ("وأربيل", "هەولێر"), ("پاوە", "پاوە"), ("وسنندج", "سنە"), ("ومريوان", "مەریوان"),
             ("دمشق", "دیمەشق")]
    for i, (k, w) in enumerate(zip(keys, words)):
        ta = c.at(w[0], w[1], default=t0 + 0.6 * i)
        if ta < t0:
            ta = t0 + 0.5 * i
        x, y = xy(k)
        # v2: Halabja, Pawe, Marivan and Sanandaj sit within a few pixels of each other at this scale, so each
        # label goes to its own side (Halabja left, Sanandaj right, Marivan above, Pawe below) instead of colliding
        side = {"halabja": "left", "sanandaj": "right"}.get(k)
        city(c, f, x, y, nm(c, k), t, ta, GOLD, below=k in ("pawe", "damascus"), glow=True, side=side)
    ta = c.at("ولندن", "لەندەن", default=t0 + 4)
    # London is far off the map: a gold badge on the reading-end edge, with an arrow toward it
    if t > ta:
        k = ease_out((t - ta) / 0.4)
        im = c.get(("london",), lambda: B.pill(c.lang, "◀ " + nm(c, "london"), 32, GOLD, INK))
        paste(f, im, (c.margin if not c.vert else 70), c.H * 0.22 if not c.vert else 420, k)
    return B.grain(f, t, 5)


def s34(c, t):
    t_q = c.at("فأمسكوا", "دەستێکی", default=c.frac(0.7)) - 0.6
    return behind(c, t, "P01a_sheikh_portrait.jpg", ost(c), t_q, 140 if not c.vert else 100,
                  c.H * 0.40 if not c.vert else 470, bgfn=lambda tt: glow_bg(c, tt, 34, (110, 90, 60)),
                  foc=(0.5, 0.45), z=(1.04, 1.0), gold=False, side=True)


def r10(c, t):
    a, b = c.sc.get("clip", [0.0, 43.1])
    tc = max(0.0, t - 0.4) + a
    cl = B.clip(c, "R10_lecture_prophet.mp4", 1080 if not c.vert else 610)
    fr = cl.at(tc)
    if not c.vert:
        f = kit.cover(fr.convert("RGB"), c.W, c.H).convert("RGBA")
    else:
        bg = kit.cover(fr.convert("RGB"), c.W // 4, c.H // 4).resize((c.W, c.H), Image.BILINEAR)
        f = B.darken(bg.filter(ImageFilter.GaussianBlur(6)).convert("RGBA"), 0.4)
        im = fr.resize((c.W, int(fr.height * c.W / fr.width)), Image.BILINEAR)
        paste(f, im, 0, 700 - im.height / 2)
    k = ease(t / 0.5) * ease((c.D - t) / 0.5)
    if k < 1:
        f = Image.blend(Image.new("RGBA", f.size, (0, 0, 0, 255)), f, k)
    return f


def s35(c, t):
    f = cover(c, t, "A18_dawn_hawraman.jpg", (1.0, 1.06), (0.55, 0.45), (0.58, 0.40), dark=0.85, vf=(0.62, 0.45))
    t_q = c.at("كم", "چەند", default=c.frac(0.3)) - 0.3
    headline(c, f, ost(c), t, t_q, 84 if not c.vert else 68, c.H * 0.36 if not c.vert else 640, CREAM)
    return f


SCENES = {f"S{i:02d}": globals()[f"s{i:02d}"] for i in range(1, 36)}
SCENES.update({"S22b": s22b, "S28b": s28b, "S31b": s31b, "R10": r10, "END": end})
