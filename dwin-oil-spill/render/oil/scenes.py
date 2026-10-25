"""The 14 scenes + end card, for 16:9 (1920x1080) and 9:16 (1080x1920).

Every scene is f(c, t) -> RGBA frame, t = seconds from the scene start. Sync points come from the recorded narration
(c.at(<Sorani word>, <Kurmanji word>)). In 9:16 all text stays inside the central 1080x1350 area (y 285-1635):
text on top (from y 420), graphics in the middle, source line at y 1385, burned subtitles below.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import base as B
from .base import (CREAM, GOLD, INK, OIL, PAPER, RED, SEA, back_out, clamp01, ease, ease_out, paste)

kit = B.kit


# ------------------------------------------------------------------ shared views
def coast(c):
    """UAE coast from Sharjah to Ras Al Khaimah."""
    return B.map_args(c, 55.66, 25.55, 0.9, Y=1180) if c.vert else B.map_args(c, 55.62, 25.6, 1.3)


def card_crop(im):
    """Crop the quote-card graphic (I03) to the card itself."""
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    bg = a[8, 8]
    m = np.abs(a - bg).sum(axis=2) > 18
    ys, xs = np.where(m)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    pad = 6
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def shadowed(im, blur=10, off=(8, 12), alpha=90):
    out = Image.new("RGBA", (im.width + 60, im.height + 60), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([30 + off[0], 30 + off[1], 30 + im.width + off[0], 30 + im.height + off[1]],
                                 fill=(0, 0, 0, alpha))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    out.alpha_composite(im.convert("RGBA"), (30, 30))
    return out


def pin_label(c, f, text, x, y, t, t0, size=None, anchor="above", colour=INK):
    B.map_label(c, f, text, x, y, t, t0, size=size or (36 if c.vert else 34), colour=colour, anchor=anchor)


def counter_text(final, value, fmt="{:.0f}", token=None):
    """`final` with its number replaced by the running value (the final frame shows `final` exactly)."""
    token = token or next(w for w in final.replace("%", " ").replace("ی", " ").replace("ê", " ").split()
                          if any(ch.isdigit() for ch in w))
    return final.replace(token, fmt.format(value), 1)


def split_frame(c, t, D, oil_p=0.0, slide_in=True):
    """S01/S14: price screen | oil on sand. 16:9 left/right, 9:16 top/bottom. oil_p: oil covers the price half."""
    W, H = c.W, c.H
    f = Image.new("RGBA", (W, H), INK + (255,))
    k = ease_out(t / 0.75) if slide_in else 1.0
    if not c.vert:
        hw = W // 2
        a = B.photo_box(c, "s_a", "I01_oil_price_screen.jpg", hw, H, t, D, (1.0, 1.06), (0.62, 0.45), (0.58, 0.45))
        b = B.photo_box(c, "s_b", "I02_oil_on_sand_closeup.jpg", hw, H, t, D, (1.0, 1.06), (0.5, 0.6), (0.52, 0.62))
        if oil_p > 0:
            a = oil_over(c, a, oil_p, horizontal=True)
        paste(f, a, -(1 - k) * hw, 0)
        paste(f, b, hw + (1 - k) * hw, 0)
        if k >= 1:
            ImageDraw.Draw(f).rectangle([hw - 3, 0, hw + 2, H], fill=CREAM + (255,))
    else:
        hh = H // 2
        a = B.photo_box(c, "s_a", "I01_oil_price_screen.jpg", W, hh, t, D, (1.0, 1.06), (0.7, 0.4), (0.66, 0.42))
        b = B.photo_box(c, "s_b", "I02_oil_on_sand_closeup.jpg", W, hh, t, D, (1.0, 1.06), (0.5, 0.62), (0.52, 0.6))
        if oil_p > 0:
            a = oil_over(c, a, oil_p, horizontal=False)
        paste(f, a, 0, -(1 - k) * hh)
        paste(f, b, 0, hh + (1 - k) * hh)
        if k >= 1:
            ImageDraw.Draw(f).rectangle([0, hh - 3, W, hh + 2], fill=CREAM + (255,))
    return f


def oil_over(c, img, p, horizontal):
    """Oil sheen creeping over the price half from the divider (S14)."""
    w, h = img.size
    tex = c.get(("oiltex", w, h), lambda: B.oil_texture(w, h))
    rng_key = ("oilnoise", w, h)
    n = c.get(rng_key, lambda: np.random.default_rng(4).normal(0, 1, 64).astype(np.float32))
    if horizontal:
        ys = np.arange(h, dtype=np.float32) / h
        edge = sum(n[i] * np.sin(ys * (i + 1) * 2.1 + n[i + 20]) for i in range(6)) * 18
        front = w - p * (w + 120) + edge                                  # x of the front for each row
        xs = np.arange(w, dtype=np.float32)
        a = np.clip((xs[None, :] - front[:, None]) / 10.0, 0, 1)
    else:
        xs = np.arange(w, dtype=np.float32) / w
        edge = sum(n[i] * np.sin(xs * (i + 1) * 2.1 + n[i + 20]) for i in range(6)) * 18
        front = h - p * (h + 120) + edge
        ys = np.arange(h, dtype=np.float32)
        a = np.clip((ys[:, None] - front[None, :]) / 10.0, 0, 1)
    m = Image.fromarray((a * 238).astype(np.uint8), "L")
    out = img.copy()
    out.paste(tex, (0, 0), m)
    return out


# ------------------------------------------------------------------ S01 hook
def s01(c, t):
    D = c.D
    f = split_frame(c, t, D)
    c.illustration()
    o1, o2 = c.ost
    t1, t2 = c.at("نرخی", "bihayê"), c.at("ئێستا", "Niha")
    tt = c.a1 + 0.1                                     # title after the narration
    dim = clamp01((t - tt) / 0.5)
    if c.vert:
        B.strips(c, f, [o1], t, t1, col=(80, c.W - 80), y=c.H // 2 - 300, size=62, out=tt + 0.2)
        B.strips(c, f, [o2], t, t2, col=(80, c.W - 80), y=c.H // 2 + 330, size=62, out=tt + 0.2)
    else:
        hw = c.W // 2
        B.strips(c, f, [o1], t, t1, col=(80, hw - 80), y=c.H - 290, size=62, align="center", out=tt + 0.2)
        B.strips(c, f, [o2], t, t2, col=(hw + 80, c.W - 80), y=c.H - 290, size=62, align="center", out=tt + 0.2)
    if dim > 0:
        f = B.darken(f, 1 - 0.45 * dim)
        title_card(c, f, t, tt)
    return f


def title_card(c, f, t, t0):
    title = c.txt["title"]
    k = ease_out((t - t0) / 0.5)
    if k <= 0:
        return

    def build():
        im = B.T(c.lang, title, 90, INK, True)
        maxw = c.W - 140
        if im.width > maxw:                             # 9:16: break the title at the middle space
            words = title.split(" ")
            best = min(range(1, len(words)), key=lambda i: abs(len(" ".join(words[:i])) - len(" ".join(words[i:]))))
            lines = [" ".join(words[:best]), " ".join(words[best:])]
            ims = [B.fit_w(B.T(c.lang, s, 90, INK, True), maxw) for s in lines]
        else:
            ims = [im]
        lh = int(ims[0].height * 0.78)
        w = max(i.width for i in ims) + 90
        h = lh * len(ims) + 70
        card = Image.new("RGBA", (w, h), PAPER + (255,))
        d = ImageDraw.Draw(card)
        for j, li in enumerate(ims):
            card.alpha_composite(li, ((w - li.width) // 2, int(35 + j * lh - li.height * 0.11)))
        d.rectangle([0, h - 12, w, h], fill=GOLD + (255,))
        return shadowed(card, 14, (10, 14), 110)
    card = c.get(("title",), build)
    paste(f, card, c.W / 2 - card.width / 2, c.H / 2 - card.height / 2 + (1 - k) * 40, clamp01(k * 1.5))


# ------------------------------------------------------------------ S02 ministry card, then the pin on Umm Al Quwain
def s02(c, t):
    D = c.D
    tB = c.at("ڕژانی", "rijandina") - 0.2
    if t < tB:
        f = s02_card(c, t)
    else:
        f = s02_map(c, t)
        if t < tB + 0.45:
            f = B.slide(s02_card(c, tB), f, (t - tB) / 0.45, c.L.rtl)
    o1, o2 = c.ost
    B.strips(c, f, [o1], t, c.at("هەینی", "În,"), size=54)
    B.source_line(c, f, ["ministry"], t, 1.0, right=(c.L.rtl if t < tB else True))
    return f


def s02_card(c, t):
    f = B.paper_bg(c, t, c.D, seed=2)
    w = 1000 if c.vert else 1420

    def build():
        im = card_crop(B.load(f"I03_ministry_quote_card_{c.lang}.jpg"))
        return shadowed(kit.fit(im, w=w), 16, (10, 16), 80)
    card = c.get(("i03", w), build)
    u = B.prog(t, c.D)
    s = 1.0 + 0.04 * u
    im = card.resize((int(card.width * s), int(card.height * s)), Image.BILINEAR)
    cy = 1010 if c.vert else c.H / 2 + 40
    B.place(f, im, c.W / 2, cy, t, 0.25, frm="bottom")
    return f


def s02_map(c, t):
    args = coast(c)
    v, m = B.map_image(c, args)
    ux, uy = v.place("uaq")
    m_, cam, v = B.map_shot(c, args, t, c.D, z=(1.0, 1.22), c0=(0.5, 0.5), c1=(ux / v.w, uy / v.h))
    f = m_
    x, y = B.scr(cam, v, "uaq")
    kit.map_pin(f, x, y, t - c.at("گەیشتۆتە", "gihîştiye"), INK, 1.4)
    pin_label(c, f, c.ost[1], x, y - 58, t, c.at("ئوم", "Ummulqeywîn"), size=44 if c.vert else 42)
    return f


# ------------------------------------------------------------------ S03 towers in haze + three pins with smell lines
def s03(c, t):
    D = c.D
    f, cam = B.photo(c, "i05", "I05_coastal_towers_haze.jpg", t, D, z=(1.0, 1.05), c0=(0.35, 0.5), c1=(0.42, 0.5))
    # warm haze breathing over the photo
    hz = c.get(("haze",), lambda: Image.new("RGBA", (c.W, c.H), (205, 170, 130, 255)))
    paste(f, hz, 0, 0, 0.10 + 0.05 * math.sin(t * 1.3))
    o1, o2 = c.ost
    names = o1.split(" · ")                         # شارقە · عەجمان · ئوم ئەلقەیوەین
    keys = ["sharjah", "ajman", "uaq"]
    times = [c.at("شارقە", "Şarîqe"), c.at("عەجمان", "Ecman"), c.at("ئوم", "Ummulqeywîn")]
    # the map card
    cw, ch = (900, 640) if c.vert else (700, 540)

    def build():
        v = B.MapView(55.50, 25.47, 0.55 if not c.vert else 0.62, cw, ch)
        m = B.base_map(v, seed=5)
        return v, m
    v, m = c.get(("s03map", cw), build)
    card = Image.new("RGBA", (cw + 28, ch + 28), CREAM + (255,))
    card.alpha_composite(m, (14, 14))
    d = ImageDraw.Draw(card, "RGBA")
    # smell lines drifting from the sea (north-west) towards the pins
    ang = math.atan2(0.74, 0.67)
    for i in range(9):
        life = ((t * 0.32 + i / 9) % 1.0)
        if t < times[0] - 0.4:
            break
        sx = 40 + (i * 97) % (cw - 260)
        sy = 20 + (i * 53) % (ch // 2)
        B.whiff(d, sx + life * 170, sy + life * 190, ang, life, 1.1 if c.vert else 1.0)
    for name, key, ti in zip(names, keys, times):
        x, y = v.place(key)
        kit.map_pin(card, x + 14, y + 14, t - ti, INK, 1.2)
    for name, key, ti in zip(names, keys, times):
        x, y = v.place(key)
        anchor = "right" if key != "uaq" else "right"
        pin_label(c, card, name, x + 14 + 4, y + 14 - 22, t, ti + 0.15, size=34 if c.vert else 30, anchor=anchor)
    card = shadowed(card.rotate(1.2 if c.L.rtl else -1.2, resample=Image.BICUBIC, expand=True), 12, (8, 12), 100)
    t_card = times[0] - 0.55
    if c.vert:
        B.place(f, card, c.W / 2, 1060, t, t_card, frm="bottom")
    else:
        cx = 1440 if not c.L.rtl else 1440        # the sea side of the photo (right) in both languages
        B.place(f, card, cx, c.H / 2 + 80, t, t_card, frm="right")
    if c.vert:
        B.strips(c, f, [o1, o2], t, 0, times=[c.at("دانیشتووانی", "niştecihên"), c.at("بۆنێکی", "bêhneke")],
                 size=50)
    else:
        col = (110, 1060) if not c.L.rtl else (110, 1060)
        B.strips(c, f, [o1, o2], t, 0, col=col, y=150,
                 times=[c.at("دانیشتووانی", "niştecihên"), c.at("بۆنێکی", "bêhneke")])
    return f


# ------------------------------------------------------------------ S04 the three closures
def s04(c, t):
    D = c.D
    args = coast(c)
    f, cam, v = B.map_shot(c, args, t, D, z=(1.0, 1.04))
    d = ImageDraw.Draw(f, "RGBA")
    keys = ["uaq", "hamriyah", "rak"]
    times = [c.at("ئوم", "Ummulqeywîn"), c.at("حەمرییە", "Hemriye"), c.at("ڕەئس", "Rasulxeyme")]
    badge = c.get(("badge",), lambda: B.closed_badge(58 if c.vert else 54))
    glow = c.get(("glow",), lambda: B.radial(220, RED, 1.6))
    for key, ti in zip(keys, times):
        x, y = B.scr(cam, v, key)
        k = clamp01((t - ti) / 0.4)
        if k > 0:
            paste(f, glow, x - 110, y - 110, 0.55 * k)
            # pulse ring
            ph = ((t - ti) % 1.6) / 1.6
            r = 18 + ph * 60
            d.ellipse([x - r, y - r, x + r, y + r], outline=RED + (int(200 * (1 - ph)),), width=4)
        kit.map_pin(f, x, y, t - ti, RED, 1.2)
        kb = back_out((t - ti - 0.3) / 0.4, 2.0)
        if kb > 0:
            bb = badge.resize((max(1, int(badge.width * kb)), max(1, int(badge.height * kb))), Image.BILINEAR)
            paste(f, bb, x - 50 - bb.width / 2, y - 58 - bb.height / 2)
    # inserts: barrier tape, empty beach (illustrations)
    ins = [("I06_closed_beach_barrier.jpg", times[0] + 1.0, times[1] - 0.15),
           ("I07_ras_al_khaimah_empty_beach.jpg", times[2] + 1.1, D + 1)]
    iw = 470 if c.vert else 520
    for name, a0, a1 in ins:
        if a0 <= t < a1:
            im = B.cut(c, name, name, w=iw, border=12, rot=-2.0 if name.startswith("I06") else 2.0)
            out = clamp01((a1 - t) / 0.3)
            if c.vert:
                B.place(f, im, 790, 1225, t, a0, frm="right", a=out)
            else:
                B.place(f, im, 1520, 720, t, a0, frm="right", a=out)
            c.illustration()
    if c.vert:
        B.strips(c, f, c.ost, t, 0, times=times, size=46)
    else:
        B.strips(c, f, c.ost, t, 0, times=times, col=(110, 980), y=150)
    B.source_line(c, f, ["ministry"], t, times[0], right=True)
    return f


# ------------------------------------------------------------------ S05 clean-up crews; the health statement
def s05(c, t):
    f, cam = B.photo(c, "i08", "I08_cleanup_crew_beach.jpg", t, c.D, z=(1.06, 1.06), c0=(0.42, 0.5), c1=(0.58, 0.5))
    o1, o2 = c.ost
    times = [c.at("بۆنەکە", "bêhn"), c.at("داوای", "xwest")]
    if c.vert:
        B.strips(c, f, [o1, o2], t, 0, times=times, size=52, bgs=[GOLD, CREAM])
    else:
        B.strips(c, f, [o1, o2], t, 0, times=times, size=58, bgs=[GOLD, CREAM], y=130)
    B.source_line(c, f, ["ministry"], t, times[0], dark=True)
    return f


# ------------------------------------------------------------------ S06 the slick to scale
def s06_args(c):
    if c.vert:
        return B.map_args(c, 55.44, 25.66, 0.55, Y=1060)
    return B.map_args(c, 55.42, 25.665, 0.75, X=c.mx(720))


def s06(c, t):
    D = c.D
    args = s06_args(c)
    f, cam, v = B.map_shot(c, args, t, D, z=(1.0, 1.03))
    o1, o2, o3 = c.ost
    t160 = c.at("160", "160")
    g0, g1 = 0.5, t160 + 1.4
    g = ease(clamp01((t - g0) / (g1 - g0)))
    tp0, tp1 = c.at("واتە", "ango"), c.at("پێ،", "futbolê") + 0.6
    t25 = c.at("25", "25")
    # slick
    lay = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
    if g > 0.01:
        cen = (B.TANKER[0] + (B.SLICK_C[0] - B.TANKER[0]) * g, B.TANKER[1] + (B.SLICK_C[1] - B.TANKER[1]) * g)
        pts = B.slick_poly(v, cam, g, center=cen)
        m = Image.new("L", (c.W, c.H), 0)
        ImageDraw.Draw(m).polygon(pts, fill=255)
        m = m.filter(ImageFilter.GaussianBlur(1.5))
        tex = c.get(("oiltexf",), lambda: B.oil_texture(c.W, c.H, seed=3))
        lay.paste(tex, (0, 0), m.point(lambda q: int(q * 0.94)))
        # pitches filling the slick
        pk = clamp01((t - tp0) / (tp1 - tp0 - 0.6))
        pa = clamp01((t - tp0) / 0.3) * (1 - clamp01((t - t25 + 0.2) / 0.8))
        if pk > 0 and pa > 0:
            grid = c.get(("pitchgrid",), lambda: pitch_grid(c.W, c.H, 36 if not c.vert else 30))
            # reveal along the slick's long axis (south-west -> north-east)
            xs = np.arange(c.W, dtype=np.float32)[None, :]
            ys = np.arange(c.H, dtype=np.float32)[:, None]
            p0, p1 = pts[36], pts[0]                  # ends of the long axis
            ax, ay = p1[0] - p0[0], p1[1] - p0[1]
            proj = ((xs - p0[0]) * ax + (ys - p0[1]) * ay) / (ax * ax + ay * ay)
            rev = np.clip((pk * 1.15 - proj) / 0.08, 0, 1)
            gm = (np.asarray(m, np.float32) / 255.0) * rev * pa
            gl = grid.copy()
            ga = np.asarray(gl).copy()
            ga[..., 3] = (ga[..., 3].astype(np.float32) * gm).astype(np.uint8)
            lay.alpha_composite(Image.fromarray(ga, "RGBA"))
    f.alpha_composite(lay)
    if g > 0.01:
        c.illustration()                             # the slick is a diagram, like I12
    d = ImageDraw.Draw(f, "RGBA")
    tx, ty = B.scr(cam, v, B.TANKER)
    ux, uy = B.scr(cam, v, "uaq")
    # 25 km dashed line from the tanker to the coast
    pl = ease(clamp01((t - t25) / 0.9))
    if pl > 0:
        B.dashed_line(d, (tx, ty), (ux, uy), pl, CREAM, 6, 18, 11)
        B.dashed_line(d, (tx, ty), (ux, uy), pl, INK, 2, 18, 11)
    ship = c.get(("ship",), lambda: B.tanker_icon(54, CREAM))
    paste(f, ship, tx - ship.width / 2, ty - ship.height / 2)
    kit.map_pin(f, ux, uy, t - 0.2, INK, 1.2)
    pin_label(c, f, c.txt["uaq"], ux, uy - 50, t, 0.4, anchor="below" if c.vert else "right")
    # I09 aerial slick (illustration), late
    ti9 = t25 + 1.2
    if t >= ti9:
        im = B.cut(c, "i09", "I09_aerial_oil_slick_sea.jpg", w=420 if c.vert else 440, border=12, rot=2.5)
        if c.vert:
            B.place(f, im, 800, 1270, t, ti9, frm="right")
        else:
            B.place(f, im, 1600 if c.L.rtl else 330, 770, t, ti9, frm="bottom")
        c.illustration()
    # numbers: counter (OST 1), pitches (OST 2), distance (OST 3)
    n = 160 * g * g
    txt1 = o1 if t >= g1 else counter_text(o1, n)
    colw = 640
    bg = GOLD if t >= g1 else CREAM
    if c.vert:
        col = (60, c.W - 60)
        big = c.get(("cnt", txt1, bg), lambda: B.strip_img(c.lang, txt1, 92, INK, bg, pad=(34, 12)))
        bx, by = c.W / 2 - big.width / 2, 400
    else:
        col = c.col_start(colw)
        big = c.get(("cnt", txt1, bg), lambda: B.strip_img(c.lang, txt1, 100, INK, bg, pad=(34, 12)))
        bx = (col[1] + 12 - big.width) if c.L.rtl else col[0] - 12
        by = 140
    if t >= g0:
        paste(f, big, bx, by, clamp01((t - g0) / 0.3))
    ys = by + big.height - 4
    B.strips(c, f, [o2, o3], t, 0, times=[c.at("22", "22"), t25], col=col, y=ys, size=50 if c.vert else 54)
    B.source_line(c, f, ["reuters", "Al Jazeera"], t, t160, right=(True if c.vert else c.L.rtl))
    return f


def pitch_grid(W, H, cell):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    p = B.pitch_icon(cell - 4)
    for y in range(0, H, int(p.height + 4)):
        off = 0 if (y // (p.height + 4)) % 2 == 0 else cell // 2
        for x in range(-cell, W, cell):
            im.alpha_composite(p, (x + off, y)) if 0 <= x + off <= W - p.width else None
    return im


# ------------------------------------------------------------------ S07 the tanker and its ship card
def s07(c, t):
    D = c.D
    f, cam = B.photo(c, "i10", "I10_tanker_smoke_at_sea.jpg", t, D, z=(1.0, 1.06), c0=(0.45, 0.6), c1=(0.47, 0.62))
    times = [c.at("«جێم", "«Gem"), c.at("9ی", "9ê"), c.at("22", "22")]
    t_card = times[0] - 0.35
    if t >= t_card:
        card = ship_card(c, t, times)
        if c.vert:
            B.place(f, card, c.W / 2, 400 + card.height / 2, t, t_card, frm="top")
        else:
            col = c.col_start(card.width - 40)
            cx = (col[0] + col[1]) / 2
            B.place(f, card, cx, 120 + card.height / 2, t, t_card, frm="right" if c.L.rtl else "left")
    B.source_line(c, f, ["reuters", "The National"], t, times[0], dark=True)
    return f


def ship_card(c, t, times):
    w = 940 if c.vert else 760
    o = c.ost
    sz = 46 if c.vert else 44
    rows = [c.get(("sc_row", i, w), lambda i=i: B.fit_w(B.T(c.lang, o[i], sz, INK, True), w - 80)) for i in range(3)]
    flag = c.get(("flag", w), lambda: kit.fit(B.load("I11_panama_flag.png"), h=104 if c.vert else 92))
    ship = c.get(("cship", w), lambda: B.tanker_icon(260 if c.vert else 220, INK))
    length = c.get(("len",), lambda: B.T(c.lang, c.txt["length"], 36 if c.vert else 32, INK, True))
    top_h = flag.height + 36
    rh = int(rows[0].height * 0.86)
    h = 30 + top_h + 3 * rh + 40
    card = Image.new("RGBA", (w, h), CREAM + (255,))
    d = ImageDraw.Draw(card)
    d.rectangle([0, 0, w - 1, 10], fill=GOLD + (255,))
    rtl = c.L.rtl
    # top row: flag on the reading-start side, tanker silhouette with its 330 m length on the other
    fx = w - 40 - flag.width if rtl else 40
    fk = clamp01((t - c.at("پاناما", "Panamayê")) / 0.35)
    if fk > 0:
        fl = kit.fade(flag.convert("RGBA"), fk)
        card.alpha_composite(fl, (int(fx), 34))
        d.rectangle([fx - 1, 33, fx + flag.width, 34 + flag.height], outline=(200, 195, 185, 255), width=1)
    sx = 40 if rtl else w - 40 - ship.width
    sk = clamp01((t - times[0] - 0.2) / 0.5)
    if sk > 0:
        card.alpha_composite(kit.fade(ship, sk), (int(sx), 34 + 6))
        yy = 34 + ship.height + 18
        d.line([(sx, yy), (sx + ship.width * sk, yy)], fill=INK + (255,), width=3)
        d.line([(sx, yy - 8), (sx, yy + 8)], fill=INK + (255,), width=3)
        if sk >= 1:
            d.line([(sx + ship.width, yy - 8), (sx + ship.width, yy + 8)], fill=INK + (255,), width=3)
            card.alpha_composite(length, (int(sx + ship.width / 2 - length.width / 2), int(yy + 2)))
    y = 30 + top_h
    for i, (row, ti) in enumerate(zip(rows, times)):
        k = clamp01((t - ti) / 0.4)
        if k > 0:
            vis = kit.wipe(row, k, rtl)
            x = (w - 40 - row.width) if rtl else 40
            if vis is not None:
                card.alpha_composite(vis, (int(x), int(y - row.height * 0.07)))
        if i < 2:
            d.line([(40, y + rh + 2), (w - 40, y + rh + 2)], fill=(215, 208, 196, 255), width=2)
        y += rh
    return shadowed(card, 14, (10, 14), 120)


# ------------------------------------------------------------------ S08 slick diagram (Copernicus dates)
def s08(c, t):
    D = c.D
    if c.vert:
        f, cam = B.photo(c, "i12", "I12_slick_diagram_map.jpg", t, D, z=(1.0, 1.08), c0=(0.33, 0.38), c1=(0.33, 0.36))
    else:
        f, cam = B.photo(c, "i12", "I12_slick_diagram_map.jpg", t, D, z=(1.0, 1.12), c0=(0.5, 0.5), c1=(0.36, 0.38))
    ts = c.at("کۆپەرنیکۆس", "Copernicus")
    # satellite scan sweep
    p = clamp01((t - ts + 0.6) / 2.2)
    if 0 < p < 1:
        lay = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
        dd = ImageDraw.Draw(lay)
        if c.vert:
            y = p * (c.H + 200) - 100
            for k in range(60):
                dd.line([(0, y - k), (c.W, y - k)], fill=(235, 245, 250, int(70 * (1 - k / 60))))
            dd.line([(0, y), (c.W, y)], fill=(255, 255, 255, 170), width=3)
        else:
            x = p * (c.W + 200) - 100
            x = c.W - x if c.L.rtl else x
            for k in range(80):
                xx = x + k if c.L.rtl else x - k
                dd.line([(xx, 0), (xx, c.H)], fill=(235, 245, 250, int(70 * (1 - k / 80))))
            dd.line([(x, 0), (x, c.H)], fill=(255, 255, 255, 170), width=3)
        f.alpha_composite(lay)
    c.illustration()
    if c.vert:
        B.strips(c, f, c.ost, t, ts, size=50)
    else:
        B.strips(c, f, c.ost, t, ts, col=c.col_start(900), y=150)
    B.source_line(c, f, ["copernicus", "ESA"], t, ts, right=True)
    return f


# ------------------------------------------------------------------ S09 mangroves and corals, a shadow creeps in
def s09(c, t):
    D = c.D
    tB = c.at("بەردە", "zinarên") - 0.25
    if t < tB:
        f = s09_a(c, t)
    else:
        f = s09_b(c, t, tB)
        if t < tB + 0.45:
            f = B.slide(s09_a(c, tB), f, (t - tB) / 0.45, c.L.rtl)
    c.illustration()
    o1, o2 = c.ost
    times = [c.at("دارستانی", "daristanên"), c.at("هەستیارەکانی", "hesas")]
    if c.vert:
        B.strips(c, f, [o1, o2], t, 0, times=times, size=52)
    else:
        B.strips(c, f, [o1, o2], t, 0, times=times, y=140)
    return f


def s09_a(c, t):
    f, _ = B.photo(c, "i13", "I13_mangroves_umm_al_quwain.jpg", t, c.D, z=(1.0, 1.06), c0=(0.5, 0.55), c1=(0.47, 0.5),
                   label=False)
    return f


def s09_b(c, t, tB):
    f, _ = B.photo(c, "i14", "I14_coral_reef_fish.jpg", t - tB, c.D - tB + 1.5, z=(1.02, 1.06), c0=(0.5, 0.5),
                   c1=(0.5, 0.55), label=False)
    # graphic shadow creeping in from the bottom edge (not real oil)
    p = ease(clamp01((t - tB - 0.4) / max(1.0, c.D - tB - 0.6)))
    if p > 0:
        sh = c.get(("creep",), lambda: creep_mask(c.W, c.H))
        a = np.asarray(sh, np.float32) / 255.0
        lim = 0.32 + 0.30 * p                          # the front rises from the bottom edge
        m = np.clip((a - (1 - lim)) / 0.08, 0, 1) * 0.78
        lay = Image.new("RGBA", (c.W, c.H), OIL + (0,))
        lay.putalpha(Image.fromarray((m * 255).astype(np.uint8), "L"))
        f.alpha_composite(lay)
    return f


def creep_mask(W, H):
    """0..255 field rising towards the bottom edge, with an organic front."""
    rng = np.random.default_rng(12)
    ys = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    xs = np.linspace(0, 1, W, dtype=np.float32)[None, :]
    n = np.zeros((H, W), np.float32)
    for sc, amp in ((3, 0.10), (7, 0.05), (16, 0.025)):
        a = rng.normal(0, 1, (sc, sc * 2)).astype(np.float32)
        n += np.asarray(Image.fromarray(a).resize((W, H), Image.BICUBIC)) * amp
    field = ys * 0.85 + n + 0.1 * np.abs(xs - 0.3)
    field = (field - field.min()) / (field.max() - field.min())
    return Image.fromarray((field * 255).astype(np.uint8), "L")


# ------------------------------------------------------------------ S10 out to the Strait of Hormuz
def hormuz(c):
    return B.map_args(c, 56.1, 26.0, 3.2, Y=1000) if c.vert else B.map_args(c, 56.2, 26.0, 5.5)


def s10(c, t):
    D = c.D
    args = hormuz(c)
    v, m = B.map_image(c, args, scale=3.0)
    ux, uy = v.place("uaq")
    tz0, tz1 = 0.2, 3.6
    u = ease(clamp01((t - tz0) / (tz1 - tz0)))
    z = 3.1 + (1.0 - 3.1) * u
    cx = ux / v.w + (0.5 - ux / v.w) * u
    cy = uy / v.h + (0.5 - uy / v.h) * u
    cam = B.Cam(m.width, m.height, 0.0, z, z, (cx, cy), (cx, cy), (c.W, c.H))
    f = cam.view(m).convert("RGBA")
    d = ImageDraw.Draw(f, "RGBA")
    # country labels after the zoom (geography only)
    tl = tz1 - 0.3
    lab = ([((27.05, 55.0), c.txt["iran"], "below"), ((25.2, 55.75), c.txt["uae"], "above")] if c.vert else
           [((27.05, 55.0), c.txt["iran"], "below"), ((24.85, 55.9), c.txt["uae"], "above")])
    for ll, text, anc in lab:
        x, y = B.scr(cam, v, ll)
        pin_label(c, f, text, x, y, t, tl, size=46 if c.vert else 44, colour=(90, 84, 76), anchor=anc)
    # shipping lanes: marching dots
    lk = clamp01((t - tz1) / 0.6)
    if lk > 0:
        for lane in (B.LANE_MAIN, B.LANE_UAE):
            pts = [B.scr(cam, v, p) for p in lane]
            march(d, pts, t, CREAM, int(235 * lk), 5 if not c.vert else 6, 22)
    # attack markers (illustrative positions)
    tp = c.at("کەشتییەکان", "keştî")
    if t >= tp:
        c.illustration()
        for i, p in enumerate(B.PULSES):
            ti = tp + i * 0.22
            if t < ti:
                continue
            x, y = B.scr(cam, v, p)
            ph = ((t - ti) % 1.5) / 1.5
            r = 10 + ph * 46
            d.ellipse([x - r, y - r, x + r, y + r], outline=RED + (int(220 * (1 - ph)),), width=4)
            k = back_out((t - ti) / 0.3, 2)
            rr = 9 * k
            d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=RED + (255,), outline=CREAM + (255,), width=2)
    hx, hy = B.scr(cam, v, "hormuz")
    pin_label(c, f, c.ost[1], hx, hy - 30, t, c.at("گەرووی", "Tengava"), size=50 if c.vert else 46, anchor="above")
    if c.vert:
        B.strips(c, f, [c.ost[0]], t, c.at("28ی", "28ê"), size=54)
    else:
        B.strips(c, f, [c.ost[0]], t, c.at("28ی", "28ê"), col=c.col_start(700), y=c.H - 245)
    B.source_line(c, f, ["reuters", "Al Jazeera"], t, c.at("28ی", "28ê"), right=True)
    return f


def march(d, pts, t, colour, alpha, r, gap):
    """Dotted line whose dots move along the path."""
    segs = []
    tot = 0.0
    for a, b in zip(pts, pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        segs.append((a, b, tot, L))
        tot += L
    off = (t * 40) % gap
    s = off
    while s < tot:
        for a, b, s0, L in segs:
            if s0 <= s <= s0 + L and L > 0:
                q = (s - s0) / L
                x, y = a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q
                d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(colour) + (alpha,))
                break
        s += gap


# ------------------------------------------------------------------ S11 28 attacks in October
def s11(c, t):
    D = c.D
    f = B.paper_bg(c, t, D, seed=11)
    t28 = c.at("28", "28")
    n = int(min(28, max(0, (t - t28) / 1.7 * 28 + 0.999))) if t >= t28 else 0
    o1, o2 = c.ost
    txt = o1 if n >= 28 else counter_text(o1, n)
    big = B.big_number(c, txt, 150 if not c.vert else 140, INK, 0)
    icon = c.get(("ic28",), lambda: B.tanker_icon(104 if not c.vert else 108, INK))
    icon_r = c.get(("ic28r",), lambda: B.tanker_icon(104 if not c.vert else 108, RED))
    cols, rows = (7, 4)
    gx, gy = (icon.width + 34, icon.height + 46)
    if c.vert:
        ox = c.W / 2 - (cols * gx - 34) / 2
        oy = 860
        bx, by = c.W / 2 - big.width / 2, 420
    else:
        gw = cols * gx - 34
        ox = (c.margin + 40) if c.L.rtl else (c.W - c.margin - 40 - gw)
        oy = c.H / 2 - (rows * gy) / 2 + 30
        colw = 700
        col = c.col_start(colw)
        bx = (col[1] - big.width) if c.L.rtl else col[0]
        by = 300
    # grid of 28 ships in reading order, each turns red as the counter passes it
    for i in range(28):
        r, k = divmod(i, cols)
        kk = (cols - 1 - k) if c.L.rtl else k
        x, y = ox + kk * gx, oy + r * gy
        if i < n:
            pk = back_out(clamp01((t - (t28 + i / 28 * 1.7)) / 0.25), 2)
            paste(f, icon_r, x, y - 6 * (1 - pk))
        else:
            paste(f, icon, x, y, 0.16 if t >= t28 - 0.6 else 0.16 * clamp01(t / 0.6))
    if t >= t28 - 0.2:
        paste(f, big, bx, by, clamp01((t - t28 + 0.2) / 0.3))
    if c.vert:
        B.strips(c, f, [o2], t, c.at("زۆرترین", "hejmara"), y=by + big.height * 0.95, size=50, bgs=[GOLD])
    else:
        B.strips(c, f, [o2], t, c.at("زۆرترین", "hejmara"), col=col, y=by + big.height * 0.95, bgs=[GOLD])
    B.source_line(c, f, ["Washington Institute", "reuters"], t, t28)
    return f


# ------------------------------------------------------------------ S12 eleven supertankers
def s12(c, t):
    D = c.D
    f, cam = B.photo(c, "i16", "I16_vlcc_supertanker_at_sea.jpg", t, D, z=(1.0, 1.05), c0=(0.6, 0.55), c1=(0.62, 0.55))
    f = B.darken(f, 0.72)
    t11 = c.at("11", "11")
    icon = c.get(("ic11",), lambda: B.tanker_icon(136 if not c.vert else 140, CREAM))
    icon_m = c.get(("ic11m",), lambda: B.tanker_icon(136 if not c.vert else 140, CREAM, mark=RED))
    per_row = 6 if c.vert else 11
    gap = 162 if not c.vert else 168
    rows = [list(range(0, per_row)), list(range(per_row, 11))] if c.vert else [list(range(11))]
    y0 = 1010 if c.vert else c.H / 2 + 120
    d = ImageDraw.Draw(f, "RGBA")
    for r, idx in enumerate(rows):
        n = len(idx)
        x0 = c.W / 2 - (n * gap - (gap - icon.width)) / 2
        for j, i in enumerate(idx):
            jj = (n - 1 - j) if c.L.rtl else j
            ti = t11 + i * 0.14
            k = back_out(clamp01((t - ti) / 0.3), 2.0)
            if k <= 0:
                continue
            x, y = x0 + jj * gap, y0 + r * 150
            ic = icon_m if t >= ti + 0.18 else icon
            if c.L.rtl:
                ic = c.get(("ic11flip", ic is icon_m), lambda ic=ic: ic.transpose(Image.FLIP_LEFT_RIGHT))
            paste(f, ic, x, y + (1 - k) * 30, clamp01(k * 1.4))
    c.illustration()
    if c.vert:
        B.strips(c, f, c.ost, t, t11, size=58)
    else:
        B.strips(c, f, c.ost, t, t11, col=c.col_start(900), y=180, size=60)
    B.source_line(c, f, ["reuters", "IMO", "MarineTraffic"], t, t11, dark=True)
    return f


# ------------------------------------------------------------------ S13 >30 of 900+: a unit chart
def s13(c, t):
    D = c.D
    f = B.paper_bg(c, t, D, seed=13)
    cols, rows = (30, 30) if c.vert else (45, 20)
    cw, ch = (32, 20) if c.vert else (30, 21)
    gx0 = c.W / 2 - cols * cw / 2
    gy0 = 740 if c.vert else 470
    icon = c.get(("u_ink",), lambda: B.ship_grid_icon(cw - 7, (120, 115, 108)))
    icon_r = c.get(("u_red",), lambda: B.ship_grid_icon(cw - 5, RED))

    def build_grid():
        g = Image.new("RGBA", (cols * cw, rows * ch), (0, 0, 0, 0))
        for i in range(cols * rows):
            r, k = divmod(i, cols)
            g.alpha_composite(icon, (k * cw + 3, r * ch + (ch - icon.height) // 2))
        return g
    grid = c.get(("ugrid",), build_grid)
    gp = clamp01((t - 0.2) / 1.2)
    vis = kit.wipe(grid, gp, c.L.rtl)
    paste(f, vis, gx0, gy0)
    t30 = c.at("30", "30")
    reds = c.get(("ured",), lambda: list(np.random.default_rng(31).choice(cols * rows, 31, replace=False)))
    for j, i in enumerate(reds):
        ti = t30 + j * 0.065
        if t < ti:
            continue
        r, k = divmod(int(i), cols)
        kk = (cols - 1 - k) if c.L.rtl else k
        pk = back_out(clamp01((t - ti) / 0.22), 2.2)
        im = icon_r if pk >= 0.99 else icon_r.resize((max(1, int(icon_r.width * pk)), max(1, int(icon_r.height * pk))))
        paste(f, im, gx0 + kk * cw + 2 + (icon_r.width - im.width) / 2, gy0 + r * ch + (ch - im.height) / 2)
    o1, o2 = c.ost
    t35 = c.at("3.5", "3.5")
    pv = 3.5 * ease(clamp01((t - t35) / 1.3))
    txt2 = o2 if t >= t35 + 1.3 else counter_text(o2, pv, "{:.1f}", "3.5")
    times = [c.at("زیاتر", "zêdetirî"), t35]
    if c.vert:
        B.strips(c, f, [o1], t, times[0], y=430, size=56)
        B.strips(c, f, [txt2], t, times[1], y=530, size=50, bgs=[GOLD if t >= t35 + 1.3 else CREAM])
    else:
        col = c.col_start(1500)
        B.strips(c, f, [o1], t, times[0], col=col, y=150, size=60)
        B.strips(c, f, [txt2], t, times[1], col=col, y=250, size=56, bgs=[GOLD if t >= t35 + 1.3 else CREAM])
    B.source_line(c, f, ["reuters", "IMO", "MarineTraffic"], t, times[0])
    return f


# ------------------------------------------------------------------ S14 bookend
def s14(c, t):
    D = c.D
    t_oil = c.at("نەوتەکە", "neft")
    p = ease(clamp01((t - t_oil) / 3.4))
    f = split_frame(c, t, D, oil_p=p, slide_in=False)
    c.illustration()
    tb = c.at("باجی", "bedela")
    k = clamp01((t - tb) / 0.5)
    if k > 0:
        f = B.darken(f, 1 - 0.35 * k)
    if c.vert:
        B.strips(c, f, c.ost, t, tb, y=c.H / 2 - 60, size=64)
    else:
        B.strips(c, f, c.ost, t, tb, col=(200, c.W - 200), y=c.H / 2 - 60, size=72, align="center")
    return f


# ------------------------------------------------------------------ end card
def end(c, t):
    f = B.paper_bg(c, t, c.D, seed=21, drift=6)

    def build():
        lg = kit.logo(c.lang, False, 300 if c.vert else 260, 1.0)
        name = B.T(c.lang, c.txt["channel"], 60 if c.vert else 56, INK, True)
        return lg, name
    lg, name = c.get(("endcard",), build)
    k = ease_out((t - 0.2) / 0.6)
    cy = c.H / 2 - 60
    paste(f, lg, c.W / 2 - lg.width / 2, cy - lg.height / 2 - 40 + (1 - k) * 20, clamp01(k * 1.3))
    k2 = ease_out((t - 0.6) / 0.6)
    paste(f, name, c.W / 2 - name.width / 2, cy + lg.height / 2 + (1 - k2) * 20, clamp01(k2 * 1.3))
    ImageDraw.Draw(f).rectangle([c.W / 2 - 90 * k2, cy + lg.height / 2 + name.height + 6,
                                 c.W / 2 + 90 * k2, cy + lg.height / 2 + name.height + 12], fill=GOLD + (255,))
    return f


SCENES = {"S01": s01, "S02": s02, "S03": s03, "S04": s04, "S05": s05, "S06": s06, "S07": s07, "S08": s08, "S09": s09,
          "S10": s10, "S11": s11, "S12": s12, "S13": s13, "S14": s14, "END": end}
