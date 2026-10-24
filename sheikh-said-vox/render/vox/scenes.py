"""The 54 scenes. Each function draws the content of one scene at content time t (seconds after its chapter card).

Layouts are designed right-to-left (Arabic, Sorani) and mirrored for Kurmanji through c.mx().
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from matplotlib.path import Path as MPath

from . import kit, props
from .geo import AREAS, area_tint
from .sound import S27_SHOTS
from .kit import CREAM, GOLD, GREEN, H, INK, PAPER, RED, W, clamp01, ease, ease_out, paste
from .shots import (Cam, arrow, board_card, chapter_card, city_dot, cutout_on, full_photo, img, ink_text, map_label,
                    map_shot, ost_strips, paper_bg, pinned, portrait_behind, prog, quote_card, route, slide, tag_pill)

# ------------------------------------------------------------------ language extras (not narration or on-screen text)
EXTRA = {
    "ar": dict(
        places=dict(amed="آمد", palu="بالو", khinis="خنس", piran="بيران", lice="ليجة", genc="كنج", maden="معدن",
                    bitlis="بدليس", aleppo="حلب", geneva="جنيف", tikrit="تكريت", jerusalem="القدس",
                    istanbul="إسطنبول", ankara="أنقرة", damascus="دمشق", baghdad="بغداد", cairo="القاهرة",
                    van="وان", burdur="بوردور", mosul="الموصل", erbil="أربيل", urmia="أورمية"),
        peoples=["كرد", "عرب", "شركس", "لاز"],
        compass=["الغرب", "الجنوب", "الشرق"],
        commanders=["صالح بك خان", "الشيخ شمس الدين", "الشيخ أيوب"],
        cal_focus=(0.711, 0.688),
    ),
}

ARCHIVAL_SEPIA = "Sheikh_Said_Archival_Sepia_Portrait.jpg"
SEATED = "Sheikh_Said_Seated_Between_Two_Men_1925.jpg"
WALLS = "S01_Diyarbakir_Basalt_Walls_Dawn.jpg"


def blue_grey(im):
    return kit.grade(im, sat=0.45, bright=0.86, tint=(0.9, 0.96, 1.08), contrast=1.05)


def night(im):
    return kit.grade(im, sat=0.7, bright=0.62, tint=(0.92, 0.95, 1.1), contrast=1.1)


def cold(im):
    return kit.grade(im, sat=0.6, bright=0.9, tint=(0.92, 0.98, 1.08), contrast=1.05)


def seq(c, t, shots, xf=0.35):
    """shots: [(start, end, fn(t_local, dur) -> frame)]; cross-fades xf seconds into each new shot."""
    for i, (a, b, fn) in enumerate(shots):
        if t < b or i == len(shots) - 1:
            if i > 0 and t - a < xf:
                pa, pb, pfn = shots[i - 1]
                g = pfn(t - pa, pb - pa)
                f = fn(t - a, b - a)          # drawn last, so its image label wins
                return Image.blend(g.convert("RGBA"), f.convert("RGBA"), ease((t - a) / xf))
            return fn(t - a, b - a)


def ost_parts(line):
    return [p.strip() for p in line.split("·")]


def dark_strip_text(c, frame, text, t, t0, x, y, size=60, rate=4.0):
    """Typewriter date on a dark strip (cold open / bookend)."""
    strip = c.get(("dstrip", text, size), lambda: kit.label_strip(c.L, text, size, CREAM, (22, 20, 18)))
    n = len(text.split())
    vis = kit.wipe(strip, clamp01((t - t0) * rate / max(1, n)), c.L.rtl)
    if vis is not None:
        paste(frame, vis, c.mx(x) - (strip.width if c.L.rtl else 0), y)


# ================================================================== chapter 1
def S01(c, t):
    f, _ = full_photo(c, "a", WALLS, t, c.D, (1.0, 1.10), (0.5, 0.55), (0.52, 0.5), prep=blue_grey)
    k = ease(t / 2.2)
    if k < 1:
        f = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), f, k)
    dark_strip_text(c, f, c.ost[0], t, c.a0 + 1.0, W - 120, 720)
    return f


def S02(c, t):
    f = paper_bg(c, t, c.D)
    portrait_behind(c, f, ARCHIVAL_SEPIA, t, 0.2 * clamp01(t / 3.0), side="left")
    tag_pill(c, f, "attributed", t, 0.3)
    q = c.quote()
    quote_card(c, f, c.ost, t, q["start"] + q["dur"] * 0.2, q["start"] + q["dur"] * 0.5, size=78, underline_line=1)
    return f


def S03(c, t):
    f = paper_bg(c, t, c.D, seed=2)
    cutout_on(c, f, "p", ARCHIVAL_SEPIA, t, c.D, 600, 560, h=860, torn=True, seed=3, enter=0.1, enter_from="left",
              scale=(1.0, 1.035))
    x = W - 160
    lines = c.ost
    big = c.get("name", lambda: kit.line_img(c.L.key, c.L.dir, lines[0], 120, INK, 3)[0])
    k = kit.back_out((t - 0.35) / 0.6, 1.2)
    if k > 0:
        paste(f, big, c.mx(x) - (big.width if c.L.rtl else 0) + (1 - k) * 120 * (1 if c.L.rtl else -1), 300)
    ink_text(c, f, [lines[1]], t, 0.9, x=x, y=500, size=76, colour=INK, rate=8, mode="wipe")
    ink_text(c, f, [lines[2]], t, 1.4, x=x, y=640, size=60, colour=GOLD, rate=6, mode="words", stroke=2)
    lk = clamp01((t - 0.3) / 2.0)                                 # light leak sweep
    if 0 < lk < 1:
        xx = (-400 + lk * (W + 800)) / 4
        xs = np.arange(W // 4, dtype=np.float32)[None, :].repeat(H // 4, 0)
        g = np.clip(1 - np.abs(xs - xx) / 95, 0, 1) ** 2 * 70 * math.sin(math.pi * lk)
        lay = np.zeros((H // 4, W // 4, 4), np.uint8)
        lay[..., 0], lay[..., 1], lay[..., 2] = 255, 200, 120
        lay[..., 3] = g.astype(np.uint8)
        paste(f, Image.fromarray(lay, "RGBA").resize((W, H), Image.BILINEAR), 0, 0)
    return f


# ================================================================== chapter 2
def S04(c, t):
    def wide(tl, d):
        f, cam, v = map_shot(c, "wide", (38.0, 37.6, 20), tl, d, (1.0, 1.45), (0.5, 0.5), (0.58, 0.42))
        return f

    def close(tl, d):
        f, cam, v = map_shot(c, "close", (40.4, 38.7, 4.8), tl, d, (1.0, 1.12), (0.45, 0.5), (0.4, 0.5))
        ax, ay = cam.pt(*v.place("amed"))
        city_dot(ImageDraw.Draw(f, "RGBA"), ax, ay, 8)
        map_label(c, f, EXTRA[c.lang]["places"]["amed"], ax, ay, tl, 0.2, size=38)
        x, y = cam.pt(*v.place("palu"))
        kit.map_pin(f, x, y, tl - 0.4)
        map_label(c, f, c.ost[1], x, y - 52, tl, 0.7, size=48)
        return f

    def valley(tl, d):
        f, _ = full_photo(c, "v", "S04_Palu_Valley_Murat_River.jpg", tl, d, (1.05, 1.12), (0.35, 0.5), (0.62, 0.5))
        return f

    a, b = c.D * 0.22, c.D * 0.6
    f = seq(c, t, [(0, a, wide), (a, b, close), (b, c.D, valley)], xf=0.5)
    ost_strips(c, f, [c.ost[0]], t, c.a0 + 0.2, size=60)
    return f


def _tree(c, t, show_mother_at=None):
    f = paper_bg(c, t, c.D, seed=4)
    d = ImageDraw.Draw(f, "RGBA")
    cards = [c.get(("tree", i), lambda i=i: board_card(c, [c.ost[i]], 46, bg=(246, 240, 226), seed=i)) for i in range(3)]
    pos = [(c.mx(W / 2 + 230), 270), (c.mx(W / 2 + 230), 640), (c.mx(W / 2 - 430), 640)]
    times = [c.a0 + 0.1, c.D * 0.18, show_mother_at]
    for i in range(3):
        if times[i] is None or t < times[i]:
            continue
        k = ease_out((t - times[i]) / 0.45)
        cx, cy = pos[i]
        paste(f, cards[i], cx - cards[i].width / 2, cy - cards[i].height / 2 + (1 - k) * 40, k)
    if t > times[1] + 0.2:
        p0 = (pos[0][0], pos[0][1] + cards[0].height / 2 - 10)
        p1 = (pos[1][0], pos[1][1] - cards[1].height / 2 + 14)
        kit.ink_line(d, kit.resample(kit.wobble_line([p0, p1], 1), 6), clamp01((t - times[1] - 0.2) / 0.5), INK, 5)
    if times[2] is not None and t > times[2] + 0.2:
        p0 = (pos[1][0] + (-1 if c.L.rtl else 1) * cards[1].width / 2, pos[1][1])
        p1 = (pos[2][0] + (1 if c.L.rtl else -1) * cards[2].width / 2, pos[2][1])
        kit.ink_line(d, kit.resample(kit.wobble_line([p0, p1], 2), 6), clamp01((t - times[2] - 0.2) / 0.5), INK, 5)
    return f


def S05(c, t):
    P = EXTRA[c.lang]["places"]

    def tree(tl, d):
        return _tree(c, tl)

    def mapf(tl, d):
        f, cam, v = map_shot(c, "m", (40.8, 38.95, 4.4), tl, d, (1.0, 1.05))
        a, b = cam.pt(*v.place("palu")), cam.pt(*v.place("khinis"))
        for n, (x, y) in (("palu", a), ("khinis", b)):
            city_dot(ImageDraw.Draw(f, "RGBA"), x, y, 9)
        map_label(c, f, P["palu"], a[0], a[1], tl, 0.1, 42, anchor="above")
        route(f, kit.curve(a, b, 0.12, 60), clamp01((tl - 0.4) / (d * 0.55)))
        map_label(c, f, P["khinis"], b[0], b[1], tl, 0.4 + d * 0.55, 42, anchor="above")
        return f

    def tree2(tl, d):
        return _tree(c, tl + 99, show_mother_at=99 + 0.3)

    a, b = c.D * 0.36, c.D * 0.7
    return seq(c, t, [(0, a, tree), (a, b, mapf), (b, c.D, tree2)], xf=0.4)


def S06(c, t):
    def khinis(tl, d):
        f, _ = full_photo(c, "k", "S06_Sheikh_Said_in_Khinis.jpg", tl, d, (1.0, 1.08), (0.5, 0.45), (0.5, 0.4))
        return f

    def portrait(tl, d):
        f = paper_bg(c, tl, d, seed=5)
        cutout_on(c, f, "bg", "S06_Khinis_Plateau_Winter.jpg", tl, d, 520, 520, w=760, torn=True, seed=6, rot=3,
                  scale=(1.0, 1.02), alpha=0.9)
        cutout_on(c, f, "p", ARCHIVAL_SEPIA, tl, d, 700, 580, h=760, torn=True, seed=7, scale=(1.0, 1.05))
        words = ost_parts(c.ost[0])
        for i, wd in enumerate(words):
            t0 = 0.3 + i * d * 0.22
            if tl <= t0:
                continue
            boxes, _ = ink_text(c, f, [wd], -99, 0, x=W - 230, y=230 + i * 190, size=92, stroke=2)   # measure only
            bx = boxes[0]
            kit.highlighter(f, (bx[0] + 6, bx[1] + 14, bx[2] - 6, bx[3] - 4), clamp01((tl - t0 - 0.25) / 0.4), c.L.rtl)
            ink_text(c, f, [wd], tl, t0, x=W - 230, y=230 + i * 190, size=92, rate=10, mode="wipe", stroke=2)
        return f

    a = c.D * 0.42
    return seq(c, t, [(0, a, khinis), (a, c.D, portrait)], xf=0.45)


# ================================================================== chapter 3
def S07(c, t):
    def rewind(tl, d):
        f = paper_bg(c, tl, d, seed=8)
        u = ease(clamp01(tl / (d * 0.9)))
        year = int(round(1925 - (1925 - 1187) * u))
        num = kit.line_img("kmr", "ltr", str(year), 300, INK, 4)[0]
        jitter = 0 if u >= 1 else math.sin(tl * 60) * 3
        paste(f, num, W / 2 - num.width / 2, H / 2 - num.height / 2 - 40 + jitter)
        dd = ImageDraw.Draw(f, "RGBA")
        for k in range(12):                                         # clock ticks around
            a = -math.pi / 2 - 2 * math.pi * k / 12 - u * 6 * math.pi
            r0, r1 = 400, 430 if k % 3 else 450
            dd.line([(W / 2 + r0 * math.cos(a), H / 2 - 40 + r0 * math.sin(a)),
                     (W / 2 + r1 * math.cos(a), H / 2 - 40 + r1 * math.sin(a))], fill=GOLD + (220,), width=6)
        return f

    def domes(tl, d):
        f = paper_bg(c, tl, d, seed=9)
        sk = c.get("sky", lambda: props.skyline())
        u = prog(tl, d)
        x = -100 - u * 160 if c.L.rtl else -260 + u * 160
        paste(f, sk, x, H - sk.height + 40)
        sun = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
        ImageDraw.Draw(sun).ellipse([10, 10, 410, 410], fill=GOLD + (120,))
        paste(f, sun.filter(ImageFilter.GaussianBlur(6)), c.mx(1350) - 210, 120)
        ost_strips(c, f, c.ost, tl, 0.4, y=140, size=60)
        return f

    a = c.D * 0.42
    return seq(c, t, [(0, a, rewind), (a, c.D, domes)], xf=0.3)


def S08(c, t):
    P = EXTRA[c.lang]["places"]
    f = paper_bg(c, t, c.D, seed=10)
    cutout_on(c, f, "s", "S08_Salahuddin_al-Ayyubi.jpg", t, c.D, 560, 560, h=880, torn=True, seed=11, enter=0.0,
              enter_from="left")
    boxes, _ = ink_text(c, f, [c.ost[0]], t, c.a0, x=W - 150, y=170, size=74, rate=8, mode="wipe", stroke=2)
    t_circle = c.D * 0.3
    if t > t_circle:
        x0, y0, x1, y1 = boxes[0]
        kit.ink_line(ImageDraw.Draw(f, "RGBA"), kit.ellipse_pts((x0 - 30, y0 - 30, x1 + 30, y1 + 30), seed=2),
                     clamp01((t - t_circle) / 0.7), GOLD, 7)
    ink_text(c, f, [c.ost[1]], t, c.D * 0.45, x=W - 150, y=340, size=62, rate=6)
    # inset map: Tikrit -> Jerusalem
    def build():
        from .geo import View, base_map
        v = View(39.4, 33.6, 12.5, 760, 470)
        m = base_map(v, rivers=("tigris", "euphrates"), border_w=1, river_w=3)
        co = kit.cutout(m.convert("RGB"), torn=False, border=10, seed=1)
        return v, co
    v, co = c.get("inset", build)
    k = ease_out((t - c.D * 0.4) / 0.5)
    if k > 0:
        ix, iy = c.mx(W - 560) - co.width / 2, 440 + (1 - k) * 60
        paste(f, co, ix, iy, k)
        a = v.place("tikrit")
        b = v.place("jerusalem")
        o = (ix + 30 + 10, iy + 30 + 10)
        pa, pb = (o[0] + a[0], o[1] + a[1]), (o[0] + b[0], o[1] + b[1])
        dd = ImageDraw.Draw(f, "RGBA")
        city_dot(dd, *pa, 7)
        route(f, kit.curve(pa, pb, -0.15, 50), clamp01((t - c.D * 0.5) / (c.D * 0.35)), r=4, gap=13)
        if t > c.D * 0.85:
            kit.map_pin(f, pb[0], pb[1], t - c.D * 0.85, size=0.8)
        map_label(c, f, P["tikrit"], pa[0], pa[1], t, c.D * 0.5, 30, anchor="below")
        map_label(c, f, P["jerusalem"], pb[0], pb[1], t, c.D * 0.85, 30, anchor="below")
    return f


def S09(c, t):
    f, _ = full_photo(c, "g", "Ottoman_Soldiers_at_Gallipoli_1915.jpg", t, c.D, (1.0, 1.1), (0.4, 0.5), (0.58, 0.5),
                      prep=lambda im: kit.sepia(im, 0.35))
    ost_strips(c, f, [c.ost[0]], t, c.a0 + 0.2, size=56)
    ost_strips(c, f, [c.ost[1]], t, c.D * 0.5, y=255, size=56)
    d = ImageDraw.Draw(f, "RGBA")
    y = 780
    x0, x1 = (W - 260, 260) if c.L.rtl else (260, W - 260)
    p = clamp01((t - 0.6) / (c.D * 0.75))
    d.rectangle([min(x0, x1) - 30, y - 70, max(x0, x1) + 30, y + 40], fill=(20, 18, 16, 120))
    kit.ink_line(d, [(x0, y), (x0 + (x1 - x0) * p, y)], 1, CREAM, 5)
    for i, (yr, at) in enumerate((("1915", 0.0), ("1919", 0.57), ("1922", 1.0))):
        if p >= at:
            xx = x0 + (x1 - x0) * at
            d.line([(xx, y - 18), (xx, y + 18)], fill=GOLD + (255,), width=7)
            lab = c.get(("yr", yr), lambda yr=yr: kit.line_img("kmr", "ltr", yr, 40, CREAM, 1)[0])
            paste(f, lab, xx - lab.width / 2, y - 78)
    return f


def _sevres_map(c, t, d, tint_alpha, key="sev"):
    f, cam, v = map_shot(c, key, (39.5, 37.8, 15.5), t, d, (1.0, 1.06), (0.5, 0.5), (0.55, 0.5),
                         tints=(("sevres", GOLD, tint_alpha),))
    return f, cam, v


def S10(c, t):
    f, cam, v = _sevres_map(c, t, c.D, 150 * ease(clamp01((t - c.D * 0.12) / (c.D * 0.3))))
    ost_strips(c, f, [c.ost[0]], t, c.a0 + 0.2, size=60)
    k = ease_out((t - c.D * 0.5) / 0.5)
    if k > 0:
        doc = c.get("doc", lambda: kit.cutout(props.newspaper(560, 720, seed=3, tone=(236, 228, 210)).convert("RGB"),
                                               torn=False, border=0, seed=2).rotate(-3, expand=True))
        dx = c.mx(560) - doc.width / 2 + (1 - k) * (-500 if c.L.rtl else 500)
        paste(f, doc, dx, 230)
        hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for i in range(3):
            kit.highlighter(hl, (dx + 90, 640 + i * 48, dx + doc.width - 120, 668 + i * 48),
                            clamp01((t - c.D * 0.62 - i * 0.3) / 0.4), c.L.rtl, alpha=120)
        f.alpha_composite(hl)
        ost_strips(c, f, [c.ost[1]], t, c.D * 0.58, y=270, size=56)
    return f


# ================================================================== chapter 4
def S11(c, t):
    drain = 1 - ease(clamp01((t - 0.6) / (c.D * 0.3)))
    f, cam, v = _sevres_map(c, t, c.D, 150 * drain)
    tt = clamp01((t - c.D * 0.45) / (c.D * 0.35))
    if tt > 0:
        # paper tear: the map splits along a jagged vertical line and the halves move apart
        rng = np.random.default_rng(3)
        xs = W / 2 + np.cumsum(rng.normal(0, 14, 40))
        ys = np.linspace(-20, H + 20, 40)
        left_poly = [(0, -20)] + list(zip(xs, ys)) + [(0, H + 20)]
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).polygon(left_poly, fill=255)
        under = kit.dark_paper().copy()
        lh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        lh.paste(f, (0, 0), m)
        rh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        rh.paste(f, (0, 0), Image.eval(m, lambda v: 255 - v))
        k = ease(tt)
        out = under
        paste(out, lh.rotate(-4 * k, center=(0, H)), -k * 260, k * 30)
        paste(out, rh.rotate(4 * k, center=(W, H)), k * 260, k * 30)
        f = out
    ost_strips(c, f, [c.ost[0]], t, c.a0 + 0.2, size=60)
    return f


def S12(c, t):
    P = EXTRA[c.lang]["places"]

    def paper_(tl, d):
        f = paper_bg(c, tl, d, seed=12)
        np_ = c.get("np", lambda: kit.cutout(props.newspaper(820, 1080, seed=7).convert("RGB"), torn=False, seed=4))
        u = prog(tl, d)
        s = 0.86 + 0.08 * u
        im = np_.resize((int(np_.width * s), int(np_.height * s)), Image.BILINEAR)
        x = c.mx(640) - im.width / 2
        paste(f, im, x, 40 - u * 60)
        if tl > d * 0.35:
            box = (x + 70 * s, 40 - u * 60 + 210 * s, x + im.width - 90 * s, 40 - u * 60 + 360 * s)
            kit.ink_line(ImageDraw.Draw(f, "RGBA"), kit.ellipse_pts(box, seed=5), clamp01((tl - d * 0.35) / 0.6), RED, 8)
        ost_strips(c, f, [c.ost[0]], tl, c.a0 + 0.2, size=60)
        ost_strips(c, f, [c.ost[1]], tl, d * 0.45, y=270, size=62, colours=[RED])
        return f

    def threads(tl, d):
        f, cam, v = map_shot(c, "th", (35.0, 36.0, 28), tl, d, (1.0, 1.04))
        hub = cam.pt(*v.place("istanbul"))
        others = ["damascus", "baghdad", "cairo", "jerusalem", "amed"]
        dd = ImageDraw.Draw(f, "RGBA")
        snap = d * 0.55
        for i, n in enumerate(others):
            p = cam.pt(*v.place(n))
            city_dot(dd, *p, 8)
            if tl < snap:
                kit.ink_line(dd, kit.curve(hub, p, 0.1, 30), clamp01((tl - 0.1 - i * 0.12) / 0.5), GOLD, 4)
            else:
                k = ease((tl - snap) / 0.6)
                pts = kit.curve(hub, p, 0.1, 30)
                mid = len(pts) // 2
                a = [(x, y + k * 120 * (j / mid) ** 2) for j, (x, y) in enumerate(pts[:mid])]
                b = [(x, y + k * 120 * ((len(pts) - 1 - j) / mid) ** 2) for j, (x, y) in enumerate(pts[mid:], mid)]
                kit.ink_line(dd, a, 1, GOLD, 4, int(240 * (1 - k * 0.6)))
                kit.ink_line(dd, b, 1, GOLD, 4, int(240 * (1 - k * 0.6)))
        city_dot(dd, *hub, 12, RED)
        map_label(c, f, P["istanbul"], hub[0], hub[1], tl, 0.2, 36)
        return f

    a = c.D * 0.56
    return seq(c, t, [(0, a, paper_), (a, c.D, threads)], xf=0.35)


def S13(c, t):
    f = paper_bg(c, t, c.D, seed=13)
    peoples = EXTRA[c.lang]["peoples"]
    stamp_t = c.D * 0.38
    spots = [(c.mx(1480), 260), (c.mx(560), 330), (c.mx(1250), 700), (c.mx(700), 760)]
    for i, (wd, (x, y)) in enumerate(zip(peoples, spots)):
        t0 = c.a0 + 0.2 + i * 0.4
        if t < t0:
            continue
        strip = c.get(("pp", wd), lambda wd=wd: kit.label_strip(c.L, wd, 58, INK, CREAM, rot=[-4, 3, 5, -3][i]))
        if t < stamp_t:
            k = ease_out((t - t0) / 0.35)
            paste(f, strip, x - strip.width / 2, y - strip.height / 2 + (1 - k) * 30, k)
        else:
            k = ease((t - stamp_t) / 0.35)
            xx = x + (W / 2 - x) * k
            yy = y + (430 - y) * k
            paste(f, strip, xx - strip.width / 2, yy - strip.height / 2, 1 - k)
    if t > stamp_t:
        k = kit.back_out((t - stamp_t) / 0.3, 1.0)
        st = c.get("stmp", lambda: props.stamp(760, 260, INK, seed=3, mark=False))
        s = 1.6 - 0.6 * k
        im = st.resize((int(st.width * s), int(st.height * s)), Image.BILINEAR)
        paste(f, im, W / 2 - im.width / 2, 430 - im.height / 2, clamp01(k * 1.5) * 0.35)
        ink_text(c, f, [c.ost[0]], t, stamp_t + 0.1, x=W / 2, y=380, size=96, rate=20, mode="plain", align="center",
                 stroke=3)
    t2 = c.D * 0.6
    if t > t2:
        boxes, _ = ink_text(c, f, [c.ost[1]], t, t2, x=W / 2, y=620, size=74, rate=8, mode="wipe", align="center")
        t3 = c.D * 0.82
        if t > t3:
            x0, y0, x1, y1 = boxes[0]
            ym = (y0 + y1) / 2 + 4
            pts = kit.wobble_line([(x0 - 20, ym + 6), (x1 + 20, ym - 6)], 5)
            if c.L.rtl:
                pts = pts[::-1]
            kit.ink_line(ImageDraw.Draw(f, "RGBA"), kit.resample(pts, 6), clamp01((t - t3) / 0.4), RED, 10)
    return f


def S14(c, t):
    f = paper_bg(c, t, c.D, seed=14)
    words = ost_parts(c.ost[1])
    xs = [c.mx(1440), c.mx(960), c.mx(480)]
    ost_strips(c, f, [c.ost[0]], t, c.a0 + 0.2, y=90, size=60, colours=[RED])
    for i in range(3):
        t0 = 0.5 + i * 0.5
        if t < t0:
            continue
        mag = c.get(("mag", i), lambda i=i: kit.cutout(props.magazine(400, 540, seed=i, accent=[(120, 60, 40), (40, 80, 90),
                                                                                             (90, 70, 30)][i]).convert("RGB"),
                                                     torn=False, seed=i).rotate([-3, 2, -2][i], expand=True))
        k = ease_out((t - t0) / 0.45)
        paste(f, mag, xs[i] - mag.width / 2, 250 + (1 - k) * 80, k)
        tl = c.D * (0.45 + i * 0.15)
        if t > tl:
            lk = c.get("lock", lambda: props.padlock(120))
            kk = kit.back_out((t - tl) / 0.3, 2.0)
            s = 0.6 + 0.4 * kk
            im = lk.resize((int(lk.width * s), int(lk.height * s)), Image.BILINEAR)
            paste(f, im, xs[i] - im.width / 2, 470 - im.height / 2, clamp01(kk * 2))
            lab = c.get(("w", i), lambda i=i: kit.label_strip(c.L, words[i], 50, INK, CREAM))
            paste(f, lab, xs[i] - lab.width / 2, 790)
    return f


def S15(c, t):
    f, cam, v = map_shot(c, "mig", (35.5, 38.6, 19), t, c.D, (1.0, 1.04),
                         tints=(("kurdistan", GOLD, 70),))
    dd = ImageDraw.Draw(f, "RGBA")
    rng = np.random.default_rng(15)
    east = [(rng.uniform(38.6, 43.5), rng.uniform(37.2, 39.4)) for _ in range(46)]
    dim = clamp01((t - c.D * 0.25) / (c.D * 0.3))
    for lon, lat in east:
        x, y = cam.pt(*v.xy(lat, lon))
        city_dot(dd, x, y, 6, tuple(int(INK[i] + (170 - INK[i]) * dim) for i in range(3)), 0.9)
    for i in range(9):
        lat0 = 37.5 + (i % 3) * 0.6 + rng.uniform(-0.2, 0.2)
        a = cam.pt(*v.xy(lat0, 41.5 - (i % 2)))
        b = cam.pt(*v.xy(lat0 + rng.uniform(-0.6, 0.6), 29.5 + rng.uniform(0, 2)))
        arrow(f, kit.curve(a, b, 0.06 * (1 if i % 2 else -1), 30), clamp01((t - 0.3 - i * 0.18) / 1.2), RED, 6, 22, 210)
    for i in range(5):
        a = cam.pt(*v.xy(38.3 + i * 0.3, 32.0))
        b = cam.pt(*v.xy(38.0 + i * 0.35, 39.6))
        arrow(f, kit.curve(a, b, 0.05, 30), clamp01((t - 0.9 - i * 0.2) / 1.2), (90, 84, 76), 5, 18, 190)
    words = ost_parts(c.ost[0])
    for i, wd in enumerate(words):
        t0 = c.D * 0.55 + i * c.D * 0.1
        if t > t0:
            st = c.get(("rw", wd), lambda wd=wd: kit.label_strip(c.L, wd, 64, RED, CREAM, rot=[2, -2, 3, -1][i]))
            k = kit.back_out((t - t0) / 0.25, 2.0)
            s = 1.5 - 0.5 * k
            im = st.resize((int(st.width * s), int(st.height * s)), Image.BILINEAR)
            x = c.mx(W - 260 - i * 380)
            paste(f, im, x - im.width / 2, 760 - im.height / 2, clamp01(k * 2))
    return f


def S16(c, t):
    fld = c.get("fld", lambda: props.wheat_field())
    cam = Cam(fld.width, fld.height, prog(t, c.D), 1.0, 1.06, (0.5, 0.55), (0.52, 0.55))
    f = cam.view(fld).convert("RGBA")
    top, bot = (c.mx(1120), 392), (c.mx(960), H + 20)
    drain = clamp01((t - c.D * 0.5) / (c.D * 0.3))
    if drain > 0:
        grey = c.get("grey", lambda: kit.grade(fld, sat=0.12, bright=0.78, tint=(1.0, 0.97, 0.92)))
        gv = cam.view(grey).convert("RGBA")
        edge = 0 if c.L.rtl else W
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).polygon([(edge, top[1]), top, bot, (edge, H)], fill=int(255 * drain))
        f.paste(gv, (0, 0), m.filter(ImageFilter.GaussianBlur(3)))
    p = clamp01((t - c.D * 0.15) / (c.D * 0.3))
    if p > 0:
        d = ImageDraw.Draw(f, "RGBA")
        pts = kit.resample(kit.partial([top, bot], p), 30)
        for i in range(0, len(pts) - 1, 2):
            d.line([pts[i], pts[i + 1]], fill=RED + (245,), width=10)
    ost_strips(c, f, [c.ost[0]], t, c.a0 + 0.2, size=60)
    ost_strips(c, f, [c.ost[1]], t, c.D * 0.62, y=270, size=66, colours=[RED])
    return f


def S17(c, t):
    P = EXTRA[c.lang]["places"]
    f, cam, v = map_shot(c, "trade", (41.6, 36.9, 11.5), t, c.D, (1.0, 1.05), tints=(("kurdistan", GOLD, 85),))
    dd = ImageDraw.Draw(f, "RGBA")
    nodes = ["amed", "mosul", "urmia", "erbil", "aleppo", "van", "bitlis"]
    pairs = [("amed", "mosul"), ("amed", "aleppo"), ("mosul", "erbil"), ("erbil", "urmia"), ("van", "urmia"),
             ("bitlis", "amed"), ("van", "bitlis")]
    for n in nodes:
        city_dot(dd, *cam.pt(*v.place(n)), 8)
    for i, (a, b) in enumerate(pairs):
        pa, pb = cam.pt(*v.place(a)), cam.pt(*v.place(b))
        pts = kit.curve(pa, pb, 0.1, 40)
        route(f, pts, clamp01((t - 0.2 - i * 0.15) / 1.0), r=4.5, gap=15)
        tc = c.D * 0.3 + i * 0.35
        if t > tc:
            mx_, my_ = pts[len(pts) // 2]
            k = kit.back_out((t - tc) / 0.25, 2)
            ang = math.atan2(pb[1] - pa[1], pb[0] - pa[0]) + math.pi / 2
            L_ = 26 * k
            dd = ImageDraw.Draw(f, "RGBA")
            dd.line([(mx_ - L_ * math.cos(ang), my_ - L_ * math.sin(ang)), (mx_ + L_ * math.cos(ang), my_ + L_ * math.sin(ang))],
                    fill=RED + (255,), width=10)
    for n in ("amed", "mosul", "erbil", "aleppo"):
        x, y = cam.pt(*v.place(n))
        map_label(c, f, P[n], x, y, t, 0.5, 32)
    ost_strips(c, f, [c.ost[0]], t, c.a0 + 0.2, size=60)
    tl = c.D * 0.62
    if t > tl:
        lg = c.get("ledger", lambda: kit.cutout(props.ledger().convert("RGB"), torn=False, seed=3))
        k = kit.back_out((t - tl) / 0.4, 1.2)
        paste(f, lg, W / 2 - lg.width / 2, H - 120 - lg.height + (1 - k) * 400)
        if t > tl + 0.6:
            stp = c.get("stp", lambda: props.stamp(300, 150, RED, seed=8).rotate(8, expand=True))
            kk = kit.back_out((t - tl - 0.6) / 0.25, 2)
            s = 1.5 - 0.5 * kk
            im = stp.resize((int(stp.width * s), int(stp.height * s)), Image.BILINEAR)
            paste(f, im, c.mx(W / 2 + 320) - im.width / 2, H - 330 - im.height / 2, clamp01(kk * 2))
        ost_strips(c, f, [c.ost[1]], t, tl + 0.2, y=270, size=60, colours=[RED])
    return f


# ================================================================== chapter 5 (case board)
def _board(c, t, items):
    """items: list of (key, kind, payload, cx, cy, t0); returns frame and pin positions dict."""
    f = kit.cork().copy()
    pins = {}
    for key, kind, payload, cx, cy, t0 in items:
        if kind == "photo":
            name, h, rot, prep = payload

            def build(name=name, h=h, rot=rot, prep=prep):
                im = prep(img(name)) if prep else img(name)
                co = kit.cutout(kit.fit(im, h=h), torn=False, border=16, seed=len(name))
                return co.rotate(rot, resample=Image.BICUBIC, expand=True)
            co = c.get(("bp", name, h, rot), build)
            p = pinned(f, co, c.mx(cx), cy, t, t0, from_side=-1 if c.L.rtl else 1)
            if p:
                c.label_for(name)
        else:
            lines, size, rot = payload
            card = c.get(("bc", tuple(lines), size, rot), lambda: board_card(c, lines, size, rot=rot, seed=len(lines[0])))
            p = pinned(f, card, c.mx(cx), cy, t, t0, from_side=1 if c.L.rtl else -1)
        if p:
            pins[key] = p
    return f, pins


def _strings(f, pins, specs, t):
    d = ImageDraw.Draw(f, "RGBA")
    for a, b, t0, col in specs:
        if a in pins and b in pins and t > t0:
            kit.string(d, pins[a], pins[b], col, 4, clamp01((t - t0) / 0.6))


def _yusuf(im):
    return im.crop((0, 0, im.width, int(im.height * 0.885)))      # drop the printed caption


BOARD_SHEIKH = ("sheikh", "photo", (ARCHIVAL_SEPIA, 470, -2, None), 560, 560)
BOARD_AZADI = ("azadi", "card", None, 1330, 330)


def S18(c, t):
    items = [BOARD_SHEIKH + (c.D * 0.3,), ("azadi", "card", ([c.ost[0]], 54, 2), 1330, 330, c.a0 + 0.1)]
    f, pins = _board(c, t, items)
    _strings(f, pins, [("azadi", "sheikh", c.D * 0.55, RED)], t)
    return f


def _board_ch5(c, t, extra_items, strings, t_base=-99):
    items = [BOARD_SHEIKH + (t_base,), ("azadi", "card", ([c.x["azadi"]], 54, 2), 1330, 330, t_base)] + extra_items
    f, pins = _board(c, t, items)
    _strings(f, pins, [("azadi", "sheikh", -99, RED)] + strings, t)
    return f


def S19(c, t):
    P = EXTRA[c.lang]["places"]

    def mapf(tl, d):
        f, cam, v = map_shot(c, "bk", (41.0, 38.9, 5.6), tl, d, (1.0, 1.05))
        a, b = cam.pt(*v.place("bitlis")), cam.pt(*v.place("khinis"))
        dd = ImageDraw.Draw(f, "RGBA")
        city_dot(dd, *a, 9)
        map_label(c, f, P["bitlis"], a[0], a[1], tl, 0.2, 40, anchor="below")
        route(f, kit.curve(a, b, -0.15, 60), clamp01((tl - 0.6) / (d * 0.6)))
        if tl > 0.6 + d * 0.6:
            kit.map_pin(f, b[0], b[1], tl - 0.6 - d * 0.6)
            map_label(c, f, P["khinis"], b[0], b[1] - 50, tl, 0.8 + d * 0.6, 40)
        ost_strips(c, f, c.ost, tl, c.a0 + 0.2, size=56)
        return f

    def board(tl, d):
        T = tl + 0.0
        return _board_ch5(c, T, [("yusuf", "photo", ("Yusuf_Ziya_Bey_Portrait.jpg", 430, 3, _yusuf), 1000, 640, 0.2)],
                          [("yusuf", "sheikh", d * 0.45, GOLD)])

    a = c.D * 0.5
    return seq(c, t, [(0, a, mapf), (a, c.D, board)], xf=0.4)


def S20(c, t):
    f = kit.dark_paper().copy()
    flick = 1 + 0.06 * math.sin(t * 9.0) + 0.04 * math.sin(t * 23.0)
    co_box = cutout_on(c, f, "g", "Sheikh_Said_Group_Photo.jpg", t, c.D, 640, 540, h=900, torn=True, seed=20,
                       prep=lambda im: kit.grade(kit.sepia(im, 0.6), bright=0.95), scale=(1.0, 1.06))
    glow = c.get("glow", lambda: _radial(900, (255, 190, 110)))
    paste(f, glow, c.mx(640) - 450, 540 - 450, 0.25 * flick)
    rng = np.random.default_rng(int(1))
    d = ImageDraw.Draw(f, "RGBA")
    for i in range(140):                                          # snow
        x0 = rng.uniform(0, W)
        sp = rng.uniform(25, 70)
        y = (rng.uniform(0, H) + t * sp) % (H + 20)
        x = x0 + math.sin(t * 0.8 + i) * 18
        r = rng.uniform(1.5, 4)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(240, 240, 245, int(rng.uniform(120, 220))))
    ost_strips(c, f, c.ost, t, c.a0 + 0.2, size=58)
    return f


def _radial(size, colour):
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    dd = np.sqrt((xx - size / 2) ** 2 + (yy - size / 2) ** 2) / (size / 2)
    a = np.clip(1 - dd, 0, 1) ** 2 * 255
    arr = np.zeros((size, size, 4), np.uint8)
    arr[..., :3] = colour
    arr[..., 3] = a.astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def _board_allies(t_hafid=-99, t_simko=-99):
    return [("yusuf", "photo", ("Yusuf_Ziya_Bey_Portrait.jpg", 430, 3, _yusuf), 1000, 640, -99),
            ("hafid", "photo", ("Sheikh_Mahmud_Hafid_Portrait.jpg", 360, -3, None), 1400, 620, t_hafid),
            ("simko", "photo", ("Simko_Shikak_Portrait.jpg", 360, 4, None), 1735, 560, t_simko)]


def S21(c, t):
    P = EXTRA[c.lang]["places"]
    names = ost_parts(c.ost[0])

    def board(tl, d):
        f = _board_ch5(c, tl, _board_allies(0.2, 0.9), [("yusuf", "sheikh", -99, GOLD), ("hafid", "sheikh", 0.8, GOLD),
                                                         ("simko", "sheikh", 1.5, GOLD)])
        for i, (nm, (x, y)) in enumerate(zip(names, [(1400, 790), (1735, 730)])):
            if tl > 0.6 + i * 0.7:
                lab = c.get(("nm", nm), lambda nm=nm: kit.label_strip(c.L, nm, 40, INK, CREAM))
                paste(f, lab, c.mx(x) - lab.width / 2, y - lab.height / 2)
        return f

    def env(tl, d):
        f, cam, v = map_shot(c, "eu", (24.0, 41.5, 44), tl, d, (1.0, 1.03))
        a, b = cam.pt(*v.place("khinis")), cam.pt(*v.place("geneva"))
        dd = ImageDraw.Draw(f, "RGBA")
        city_dot(dd, *a, 9)
        pts = kit.curve(a, b, 0.22, 80)
        p = clamp01((tl - 0.3) / (d * 0.65))
        route(f, pts, p, r=4, gap=14)
        e = c.get("env", props.envelope)
        ex, ey = kit.partial(pts, p)[-1]
        paste(f, e, ex - e.width / 2, ey - e.height / 2 - 20)
        if p >= 1:
            kit.map_pin(f, b[0], b[1], tl - 0.3 - d * 0.65)
            map_label(c, f, P["geneva"], b[0], b[1] - 50, tl, 0.5 + d * 0.65, 40)
        ost_strips(c, f, [c.ost[1]], tl, 0.2, size=58)
        return f

    a = c.D * 0.5
    return seq(c, t, [(0, a, board), (a, c.D, env)], xf=0.4)


def S22(c, t):
    P = EXTRA[c.lang]["places"]
    names = ost_parts(c.x["allies"])

    def board(tl, d):
        f = _board_ch5(c, 99, _board_allies(), [("yusuf", "sheikh", -99, GOLD), ("hafid", "sheikh", -99, GOLD),
                                                 ("simko", "sheikh", -99, GOLD)])
        for nm, (x, y) in zip(names, [(1400, 790), (1735, 730)]):
            lab = c.get(("nm", nm), lambda nm=nm: kit.label_strip(c.L, nm, 40, INK, CREAM))
            paste(f, lab, c.mx(x) - lab.width / 2, y - lab.height / 2)
        # the society chooses its head: a gold frame drawn around the Sheikh's photo
        x0, x1 = sorted((c.mx(560 - 215), c.mx(560 + 215)))
        kit.ink_line(ImageDraw.Draw(f, "RGBA"), kit.ellipse_pts((x0 - 30, 560 - 300, x1 + 30, 560 + 300), seed=22),
                     clamp01((tl - 1.0) / 1.0), GOLD, 9)
        return f

    def mapf(tl, d):
        f, cam, v = map_shot(c, "ar", (39.4, 37.6, 9.5), tl, d, (1.0, 1.04))
        dd = ImageDraw.Draw(f, "RGBA")
        k_, am, al = cam.pt(*v.place("khinis")), cam.pt(*v.place("amed")), cam.pt(*v.place("aleppo"))
        for p in (k_, am, al):
            city_dot(dd, *p, 9)
        map_label(c, f, P["khinis"], k_[0], k_[1], tl, 0.1, 38)
        cutout_on(c, f, "ali", "S22_Ali_Riza.jpg", tl, d, 370, 370, h=480, torn=True, seed=22, enter=0.2,
                  enter_from="left")
        r1 = d * 0.2
        route(f, kit.curve(k_, am, 0.12, 60), clamp01((tl - r1) / (d * 0.2)))
        if tl > r1 + d * 0.2:
            map_label(c, f, P["amed"], am[0], am[1], tl, r1 + d * 0.2, 38)
        r2 = r1 + d * 0.22
        route(f, kit.curve(am, al, 0.12, 60), clamp01((tl - r2) / (d * 0.2)))
        if tl > r2 + d * 0.2:
            kit.map_pin(f, al[0], al[1], tl - r2 - d * 0.2)
            map_label(c, f, P["aleppo"], al[0], al[1] - 50, tl, r2 + d * 0.22, 38)
        comp = EXTRA[c.lang]["compass"]
        spots = [(c.mx(170), 720), (W / 2, H - 260), (c.mx(W - 170), 560)]
        for i, (wd, (x, y)) in enumerate(zip(comp, spots)):
            t0 = d * (0.72 + i * 0.07)
            if tl > t0:
                lab = c.get(("cp", wd), lambda wd=wd: kit.label_strip(c.L, wd, 46, CREAM, GREEN))
                paste(f, lab, x - lab.width / 2, y - lab.height / 2, clamp01((tl - t0) / 0.3))
        ost_strips(c, f, [c.ost[0]], tl, 0.5, size=56)
        ost_strips(c, f, [c.ost[1]], tl, r1, y=255, size=56)
        return f

    a = c.D * 0.4
    return seq(c, t, [(0, a, board), (a, c.D, mapf)], xf=0.4)


def S23(c, t):
    fx, fy = EXTRA[c.lang]["cal_focus"]
    name = f"S23_March_1925_Calendar_21_Circled_{c.lang}.jpg"
    f, cam = full_photo(c, "cal", name, t, c.D, (1.0, 1.7), (0.5, 0.5), (fx, fy), label=False)
    im = c.get(("full", "cal", name), lambda: None)
    x, y = cam.pt(fx * im.width, fy * im.height)
    if t > c.D * 0.45:
        r = 135 * cam.s * im.width / 3840          # a little outside the printed red circle
        kit.ink_line(ImageDraw.Draw(f, "RGBA"), kit.ellipse_pts((x - r, y - r, x + r, y + r), seed=8),
                     clamp01((t - c.D * 0.45) / 0.7), GOLD, 9)
        fl = props.flame(t, 80)
        paste(f, fl, x + r + 10 if c.L.rtl else x - r - 10 - fl.width, y - fl.height + 20, clamp01((t - c.D * 0.5) / 0.4))
    ost_strips(c, f, c.ost, t, c.D * 0.55, size=60)
    return f


def S24(c, t):
    def tour(tl, d):
        fr, _ = full_photo(c, "tr", "S24_Sheikh_Said_on_Tour.jpg", tl, d, (1.0, 1.08), (0.5, 0.5), (0.5, 0.45))
        return fr

    a = c.D * 0.68
    f = seq(c, t, [(0, a, lambda tl, d: _tour_map(c, tl, d)), (a, c.D, tour)], xf=0.45)
    ost_strips(c, f, c.ost, t, c.a0 + 0.2, size=56)
    return f


def _tour_map(c, t, D):
    P = EXTRA[c.lang]["places"]
    f, cam, v = map_shot(c, "tour", (40.6, 38.55, 5.8), t, D, (1.0, 1.05))
    stops = ["khinis", "varto", "solhan", "genc", "palu", "maden", "amed", "silvan", "lice", "piran"]
    pts = []
    for n in stops:
        pts.append(cam.pt(*v.place(n)))
    path = []
    for a, b in zip(pts, pts[1:]):
        path += kit.curve(a, b, 0.1, 20)
    p = clamp01((t - 0.3) / (c.D * 0.75))
    route(f, path, p, r=4.5, gap=15)
    dd = ImageDraw.Draw(f, "RGBA")
    rng = np.random.default_rng(24)
    for i, (x, y) in enumerate(pts):
        at = i / (len(pts) - 1)
        if p >= at:
            n_dots = int(min(14, (p - at) * 60))
            for j in range(n_dots):
                ang = rng.uniform(0, 2 * math.pi)
                rr = rng.uniform(14, 40)
                city_dot(dd, x + rr * math.cos(ang), y + rr * math.sin(ang), 4, GOLD)
            city_dot(dd, x, y, 8)
    for n in ("khinis", "amed"):
        x, y = cam.pt(*v.place(n))
        map_label(c, f, P[n], x, y, t, 0.4, 36)
    if t > c.D * 0.5:
        cutout_on(c, f, "ride", "Sheikh_Said_Painting_on_Horseback.jpg", t - c.D * 0.5, c.D * 0.5, 430, 690, w=560,
                  torn=True, seed=24, enter=0.0, enter_from="bottom")
    ost_strips(c, f, c.ost, t, c.a0 + 0.2, size=56)
    return f


def S25(c, t):
    P = EXTRA[c.lang]["places"]

    def mapf(tl, d):
        f, cam, v = map_shot(c, "kp", (40.9, 38.85, 3.9), tl, d, (1.0, 1.05))
        a, b = cam.pt(*v.place("khinis")), cam.pt(*v.place("piran"))
        dd = ImageDraw.Draw(f, "RGBA")
        city_dot(dd, *a, 9)
        map_label(c, f, P["khinis"], a[0], a[1], tl, 0.1, 40)
        route(f, kit.curve(a, b, 0.12, 70), clamp01((tl - 0.4) / (d * 0.65)))
        if tl > 0.4 + d * 0.65:
            kit.map_pin(f, b[0], b[1], tl - 0.4 - d * 0.65)
            map_label(c, f, P["piran"], b[0], b[1] - 50, tl, 0.6 + d * 0.65, 40)
        n = int(round(100 * ease(clamp01((tl - 0.3) / (d * 0.7)))))
        badge = Image.new("RGBA", (230, 230), (0, 0, 0, 0))
        bd = ImageDraw.Draw(badge)
        bd.ellipse([8, 8, 222, 222], fill=GREEN + (235,), outline=GOLD + (255,), width=6)
        num = kit.line_img("kmr", "ltr", str(n), 92, GOLD, 2)[0]
        badge.alpha_composite(num, (115 - num.width // 2, 115 - num.height // 2))
        paste(f, badge, c.mx(W - 300) - 115, H - 420)
        return f

    def ride(tl, d):
        fr, _ = full_photo(c, "r", "S25_Leaving_Khinis_with_100_Riders.jpg", tl, d, (1.0, 1.08), (0.5, 0.6), (0.5, 0.55))
        return fr

    def village(tl, d):
        fr, _ = full_photo(c, "vl", "S25_Snowy_Plateau_Village.jpg", tl, d, (1.0, 1.07), (0.5, 0.55), (0.5, 0.5))
        return fr

    a, b = c.D * 0.3, c.D * 0.74
    f = seq(c, t, [(0, a, ride), (a, b, mapf), (b, c.D, village)], xf=0.4)
    ost_strips(c, f, c.ost, t, c.a0 + 0.2, size=56)
    return f


# ================================================================== chapter 6
def S26(c, t):
    def house(tl, d):
        fr, _ = full_photo(c, "h", "S25-S26_Sheikh_Abdulrahims_House.jpg", tl, d, (1.0, 1.08), (0.5, 0.55),
                           (0.5, 0.5), prep=night)
        return fr

    def det(tl, d):
        fr, _ = full_photo(c, "d", "S26_Husni_Efendi_Mustafa_Alim_Detachment.jpg", tl, d, (1.0, 1.06), (0.5, 0.6),
                           (0.5, 0.55), prep=night)
        return fr

    a = c.D * 0.42
    f = seq(c, t, [(0, a, house), (a, c.D, det)], xf=0.5)
    glow = c.get("lg", lambda: _radial(700, (255, 170, 80)))
    paste(f, glow, c.mx(1250) - 350, 300, 0.18 * (1 + 0.15 * math.sin(t * 7)))
    names = ost_parts(c.ost[0])
    for i, nm in enumerate(names):
        t0 = c.a0 + 1.0 + i * 0.7
        if t > t0:
            card = c.get(("nc", nm), lambda nm=nm: board_card(c, [nm], 46, rot=[-3, 2][i], seed=i + 30))
            k = ease_out((t - t0) / 0.45)
            x = c.mx(W - 260 - i * 470)
            paste(f, card, x - card.width / 2 + (1 - k) * (300 if c.L.rtl else -300), 640, k)
    return f


def S27(c, t):
    f = kit.dark_paper().copy()
    bg, _ = full_photo(c, "n", "S27_The_Piran_Night.jpg", t, c.D, (1.0, 1.06), (0.5, 0.5), (0.5, 0.45),
                       prep=lambda im: kit.grade(im, sat=0.6, bright=0.55))
    f = Image.blend(f, bg, 0.85)
    for k, at in enumerate(S27_SHOTS):                           # brief light flickers synced to the distant shots
        dt = t - c.D * at
        if 0 <= dt < 0.14:
            r = np.random.default_rng(270 + k)
            fl = c.get("flash", lambda: _radial(420, (255, 220, 160)))
            paste(f, fl, r.uniform(300, W - 300) - 210, r.uniform(300, 650) - 210, 0.5 * (1 - dt / 0.14))
    sp = clamp01((t - c.D * 0.62) / 0.8)
    if sp > 0:
        d = ImageDraw.Draw(f, "RGBA")
        r2 = np.random.default_rng(27)
        for i in range(28):
            cx, cy = r2.uniform(200, W - 200), r2.uniform(150, H - 300)
            r = r2.uniform(10, 70) * ease(sp)
            d.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], fill=(14, 12, 12, 200))
    ost_strips(c, f, c.ost, t, c.a0 + 0.3, size=60)
    return f


def S28(c, t):
    P = EXTRA[c.lang]["places"]

    def mapf(tl, d):
        f, cam, v = map_shot(c, "pl", (40.35, 38.42, 2.6), tl, d, (1.0, 1.05))
        pi, li = cam.pt(*v.place("piran")), cam.pt(*v.place("lice"))
        dd = ImageDraw.Draw(f, "RGBA")
        city_dot(dd, *pi, 9)
        map_label(c, f, P["piran"], pi[0], pi[1] + 70, tl, 0.1, 40, anchor="below")
        fl = props.flame(tl, 110)
        paste(f, fl, pi[0] - fl.width / 2, pi[1] - fl.height + 10, clamp01((tl - 0.3) / 0.4))
        if tl > d * 0.45:
            fl2 = props.flame(tl + 1.3, 110)
            paste(f, fl2, li[0] - fl2.width / 2, li[1] - fl2.height + 10, clamp01((tl - d * 0.45) / 0.4))
            city_dot(dd, *li, 9)
            map_label(c, f, P["lice"], li[0], li[1] + 70, tl, d * 0.5, 40, anchor="below")
        return f

    def tayar(tl, d):
        fr, _ = full_photo(c, "t", "S28_Sheikh_Tayar_Takes_Lice.jpg", tl, d, (1.0, 1.08), (0.5, 0.55), (0.5, 0.5))
        return fr

    def desk(tl, d):
        fr, _ = full_photo(c, "dk", "S28_1920s_Desk_Telegrams_Letters_Coins.jpg", tl, d, (1.0, 1.12), (0.5, 0.5),
                           (0.45, 0.45))
        if tl > 0.6:
            stp = c.get("st", lambda: props.stamp(380, 180, RED, seed=11).rotate(-12, expand=True))
            k = kit.back_out((tl - 0.6) / 0.25, 2)
            s = 1.5 - 0.5 * k
            im = stp.resize((int(stp.width * s), int(stp.height * s)), Image.BILINEAR)
            paste(fr, im, c.mx(700) - im.width / 2, 520 - im.height / 2, clamp01(k * 2) * 0.9)
        ost_strips(c, fr, [c.ost[1]], tl, 0.3, y=270, size=54)
        return fr

    a, b = c.D * 0.36, c.D * 0.66
    f = seq(c, t, [(0, a, mapf), (a, b, tayar), (b, c.D, desk)], xf=0.4)
    ost_strips(c, f, [c.ost[0]], t, c.a0 + 0.2, size=56)
    return f


def S29(c, t):
    name = f"S29_March_1925_Calendar_crossed_out_{c.lang}.jpg"
    fx, fy = EXTRA[c.lang]["cal_focus"]
    f, cam = full_photo(c, "cal2", name, t, c.D, (1.25, 1.1), (fx * 0.7 + 0.15, fy * 0.7 + 0.15), (0.5, 0.5),
                        label=False)
    tt = clamp01((t - c.D * 0.5) / (c.D * 0.3))
    if tt > 0:
        rng = np.random.default_rng(29)
        ys = H * 0.45 + np.cumsum(rng.normal(0, 10, 40))
        xs = np.linspace(-20, W + 20, 40)
        top = Image.new("L", (W, H), 0)
        ImageDraw.Draw(top).polygon([(-20, -20), (W + 20, -20)] + list(zip(xs[::-1], ys[::-1])), fill=255)
        under = paper_bg(c, t, c.D, seed=29)
        th = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        th.paste(f, (0, 0), top)
        bh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bh.paste(f, (0, 0), Image.eval(top, lambda v: 255 - v))
        k = ease(tt)
        paste(under, th.rotate(5 * k, center=(W / 2, 0)), 0, -k * 700)
        paste(under, bh, 0, k * 40)
        f = under
    ost_strips(c, f, c.ost, t, c.a0 + 0.3, size=66)
    return f


def S30(c, t):
    f = paper_bg(c, t, c.D, seed=30)
    for i in range(3):
        t0 = 0.2 + i * 0.35
        if t < t0:
            continue
        npg = c.get(("np30", i), lambda i=i: kit.cutout(props.newspaper(560, 740, seed=20 + i).convert("RGB"),
                                                        torn=False, seed=i))
        k = ease_out((t - t0) / 0.5)
        ang = (-14 + i * 12) * k
        im = npg.rotate(ang, resample=Image.BICUBIC, expand=True)
        cx = c.mx(560 + i * 170)
        paste(f, im, cx - im.width / 2, 200 - (1 - k) * 200 + i * 20, k)
    ost_strips(c, f, [c.ost[0]], t, c.a0 + 0.2, size=60, colours=[RED])
    tp = c.D * 0.45
    if t > tp:
        co = c.get("ism", lambda: kit.cutout(kit.fit(img("Ismet_Pasha_Inonu_1920s_Portrait.jpg"), h=560), torn=False,
                                             border=16, seed=3).rotate(3, resample=Image.BICUBIC, expand=True))
        p = pinned(f, co, c.mx(W - 520), 600, t, tp, from_side=1 if c.L.rtl else -1)
        ost_strips(c, f, [c.ost[1]], t, tp + 0.4, y=270, size=54)
    return f


# ================================================================== chapter 7
def S31(c, t):
    f = paper_bg(c, t, c.D, seed=31)
    ink_text(c, f, [c.ost[0]], t, c.a0, x=W - 160, y=90, size=58, rate=6)
    ink_text(c, f, [c.ost[1]], t, c.a0 + 1.2, x=W - 160, y=180, size=52, colour=(90, 80, 70), rate=6)
    d = ImageDraw.Draw(f, "RGBA")
    full = 1300
    x0 = c.mx(W - 200)
    bars = [(600000, GOLD, c.D * 0.18, 330), (100000, INK, c.D * 0.32, 460)]
    for val, col, t0, y in bars:
        p = ease_out((t - t0) / 1.0)
        if p <= 0:
            continue
        L_ = full * val / 600000 * p
        xa, xb = (x0 - L_, x0) if c.L.rtl else (x0, x0 + L_)
        d.rectangle([xa, y, xb, y + 90], fill=tuple(col) + (255,))
        num = c.get(("bn", val), lambda val=val: kit.line_img("kmr", "ltr", f"{val:,}", 50, INK, 1)[0])
        paste(f, num, (xa - num.width - 20) if c.L.rtl else (xb + 20), y + 45 - num.height / 2, clamp01(p * 2))
    t3 = c.D * 0.62
    if t > t3:
        p = ease_out((t - t3) / 0.8)
        L_ = max(3, full * 10000 / 600000 * p)
        y = 600
        xa, xb = (x0 - L_, x0) if c.L.rtl else (x0, x0 + L_)
        d.rectangle([xa, y, xb, y + 90], fill=RED + (255,))
        kit.ink_line(d, kit.ellipse_pts((xa - 30, y - 25, xb + 30, y + 115), seed=31), clamp01((t - t3 - 0.6) / 0.5), RED, 6)
        num = c.get("bn10", lambda: kit.line_img("kmr", "ltr", "10,000", 50, RED, 1)[0])
        paste(f, num, (xa - num.width - 60) if c.L.rtl else (xb + 60), y + 45 - num.height / 2)
        ink_text(c, f, [c.ost[2]], t, t3 + 0.3, x=W - 160, y=730, size=56, colour=RED, rate=6)
    return f


def S32(c, t):
    f, cam, v = map_shot(c, "prov", (40.4, 38.3, 5.6), t, c.D, (1.0, 1.04), tints=(("revolt", GOLD, 95),))
    d = ImageDraw.Draw(f, "RGBA")
    cols = [(70, 110, 150), (170, 110, 50), (120, 70, 110)]
    rng = np.random.default_rng(32)
    pth = MPath(v.ring(AREAS["revolt"]))
    for k, col in enumerate(cols):
        t0 = c.D * (0.12 + k * 0.12)
        if t < t0:
            continue
        n = int(min(22, (t - t0) * 30))
        r2 = np.random.default_rng(100 + k)
        placed = 0
        while placed < n:
            x, y = r2.uniform(0, v.w), r2.uniform(0, v.h)
            if pth.contains_point((x, y)):
                sx, sy = cam.pt(x, y)
                d.ellipse([sx - 9, sy - 9, sx + 9, sy + 9], fill=col + (210,))
                placed += 1
    words = ost_parts(c.ost[0])
    legend = c.get("legend", lambda: _legend(c, words, cols))
    paste(f, legend, c.mx(W - 110) - (legend.width if c.L.rtl else 0), 170, clamp01((t - c.D * 0.12) / 0.4))
    tag_pill(c, f, "per_article", t, 0.2)
    return f


def _legend(c, words, cols):
    imgs = [kit.line_img(c.L.key, c.L.dir, w_, 48, INK, 1)[0] for w_ in words]
    w = max(i.width for i in imgs) + 120
    h = len(imgs) * 80 + 40
    card = kit.cutout(kit.paper(w, h, seed=33, tone=CREAM, vign=0.0).convert("RGB"), torn=False, seed=2)
    d = ImageDraw.Draw(card)
    for i, (im, col) in enumerate(zip(imgs, cols)):
        y = 30 + 20 + i * 80
        if c.L.rtl:
            d.ellipse([30 + w - 60, y + 22, 30 + w - 30, y + 52], fill=col + (255,))
            card.alpha_composite(im, (30 + w - 80 - im.width, int(y + 37 - im.height / 2)))
        else:
            d.ellipse([60, y + 22, 90, y + 52], fill=col + (255,))
            card.alpha_composite(im, (110, int(y + 37 - im.height / 2)))
    return card


def S33(c, t):
    def ride(tl, d):
        f = paper_bg(c, tl, d, seed=33)
        cutout_on(c, f, "h", "Sheikh_Said_Painting_on_Horseback.jpg", tl, d, 700, 560, h=900, torn=True, seed=33,
                  scale=(1.0, 1.06))
        rng = np.random.default_rng(3)
        dd = ImageDraw.Draw(f, "RGBA")
        for i in range(90):
            x = (rng.uniform(0, W) + tl * rng.uniform(20, 60)) % W
            y = rng.uniform(500, H) - tl * rng.uniform(5, 20)
            r = rng.uniform(1, 3)
            dd.ellipse([x - r, y - r, x + r, y + r], fill=(160, 130, 90, 110))
        return f

    def cmd(tl, d):
        fr, _ = full_photo(c, "cm", "S33-S34_The_Commanders.jpg", tl, d, (1.0, 1.08), (0.5, 0.5), (0.55, 0.5))
        return fr

    a = c.D * 0.55
    f = seq(c, t, [(0, a, ride), (a, c.D, cmd)], xf=0.4)
    ost_strips(c, f, c.ost, t, c.a0 + 0.2, size=54)
    return f


def S34(c, t):
    P = EXTRA[c.lang]["places"]
    f, cam, v = map_shot(c, "conv", (40.0, 38.15, 3.4), t, c.D, (1.0, 1.05))
    am, md = cam.pt(*v.place("amed")), cam.pt(*v.place("maden"))
    dd = ImageDraw.Draw(f, "RGBA")
    city_dot(dd, *am, 12, RED)
    city_dot(dd, *md, 10)
    map_label(c, f, P["amed"], am[0], am[1], t, 0.1, 44, anchor="below")
    map_label(c, f, c.ost[0], md[0], md[1], t, 0.3, 44, anchor="above")
    cmds = EXTRA[c.lang]["commanders"]
    legs = [(cam.pt(*v.place("palu")), md, c.D * 0.08), (cam.pt(*v.place("elazig")), md, c.D * 0.2),
            (cam.pt(*v.place("lice")), cam.pt(*v.xy(38.12, 40.3)), c.D * 0.38)]
    for i, (a, b, t0) in enumerate(legs):
        pts = kit.curve(a, b, 0.1 * (1 if i % 2 else -1), 40)
        arrow(f, pts, clamp01((t - t0) / 1.1), GOLD, 9, 30, 255)
        if t > t0 + 0.3:
            card = c.get(("cmd", i), lambda i=i: kit.label_strip(c.L, cmds[i], 38, INK, CREAM, rot=[-2, 2, -1][i]))
            mx_, my_ = pts[len(pts) // 3]
            paste(f, card, mx_ - card.width / 2, my_ - card.height - 14, clamp01((t - t0 - 0.3) / 0.3))
    tb = c.D * 0.6
    arrow(f, kit.curve(md, (am[0] - 20, am[1] - 26), -0.08, 40), clamp01((t - tb) / 1.3), RED, 16, 44, 250)
    ost_strips(c, f, [c.ost[1]], t, tb + 0.3, size=64)
    return f


def S35(c, t):
    def before(tl, d):
        fr, _ = full_photo(c, "b", "S35_Sheikh_Said_before_Amed.jpg", tl, d, (1.0, 1.08), (0.5, 0.5), (0.5, 0.45))
        return fr

    def walls(tl, d):
        fr, _ = full_photo(c, "w", WALLS, tl, d, (1.1, 1.1), (0.35, 0.55), (0.65, 0.55),
                           prep=lambda im: kit.grade(im, sat=0.75, bright=0.92))
        dd = ImageDraw.Draw(fr, "RGBA")
        p = clamp01((tl - 0.5) / (d * 0.5))
        x_end = W * 0.55
        pts = [(c.mx(W - 60), 700), (c.mx(x_end), 700)]
        kit.dotted(dd, pts, p, GOLD, 6, 20)
        if p >= 1:
            kit.red_x(dd, c.mx(x_end - 40), 700, 46, clamp01((tl - 0.5 - d * 0.5) / 0.4))
        return fr

    a = c.D * 0.38
    f = seq(c, t, [(0, a, before), (a, c.D, walls)], xf=0.45)
    ost_strips(c, f, c.ost, t, c.a0 + 0.3, size=60)
    return f


def _plan_scaled():
    plan, gate, centre = props.city_plan()
    k = 0.7
    plan = plan.resize((int(plan.width * k), int(plan.height * k)), Image.LANCZOS)
    return plan, (gate[0] * k, gate[1] * k)


def _cityplan(c, t, D, arrows_p, retract=0.0, pulse=False):
    f = paper_bg(c, t, D, seed=36)
    plan, gate = c.get("plan", _plan_scaled)
    px, py = W / 2 - plan.width / 2, 40
    paste(f, plan, px, py)
    g = (px + gate[0], py + gate[1])
    dd = ImageDraw.Draw(f, "RGBA")
    dd.ellipse([g[0] - 30, g[1] - 30, g[0] + 30, g[1] + 30], fill=GOLD + (255,), outline=INK + (255,), width=4)
    p = arrows_p * (1 - retract)
    if p > 0:
        alpha = int(250 * (0.55 + 0.45 * abs(math.sin(t * 5)))) if pulse else 250
        for i, (sx, sy) in enumerate(((g[0] - 620, H - 40), (g[0] - 330, H + 30), (g[0] + 330, H + 30), (g[0] + 620, H - 40))):
            end = (g[0] + (i - 1.5) * 26, g[1] + 34)
            arrow(f, kit.curve((sx, sy), end, 0.12 * (1 if i < 2 else -1), 30), p, RED if retract > 0 else GOLD, 10, 32,
                  alpha)
    return f, g


def S36(c, t):
    def gate(tl, d):
        fr, _ = full_photo(c, "g", "S36_The_Mardin_Gate.jpg", tl, d, (1.0, 1.08), (0.5, 0.45), (0.5, 0.4))
        return fr

    def plan(tl, d):
        f, g = _cityplan(c, tl, d, ease(clamp01((tl - 0.3) / 1.4)) * (0.92 + 0.08 * math.sin(tl * 6)))
        return f

    a = c.D * 0.45
    f = seq(c, t, [(0, a, gate), (a, c.D, plan)], xf=0.45)
    ost_strips(c, f, c.ost, t, c.a0 + 0.2, size=58)
    return f


def S37(c, t):
    def plan(tl, d):
        f, g = _cityplan(c, tl, d, 1.0, retract=ease(clamp01((tl - d * 0.35) / (d * 0.5))), pulse=tl < d * 0.35)
        return f

    def walls(tl, d):
        fr, _ = full_photo(c, "w", WALLS, tl, d, (1.1, 1.16), (0.6, 0.55), (0.5, 0.55))
        k = ease(clamp01(tl / (d * 0.7)))
        g = kit.grade(fr, sat=1 - k * 0.95, bright=1 - 0.15 * k).convert("RGBA")
        return g

    a = c.D * 0.45
    f = seq(c, t, [(0, a, plan), (a, c.D, walls)], xf=0.5)
    ost_strips(c, f, c.ost, t, c.D * 0.6, size=64, colours=[RED])
    return f


# ================================================================== chapter 8
def S38(c, t):
    f, cam, v = map_shot(c, "enc", (40.4, 38.3, 8.5), t, c.D, (1.0, 1.04))
    shrink = 1 - 0.45 * ease(clamp01((t - c.D * 0.35) / (c.D * 0.45)))
    tint = c.get("rt", lambda: area_tint(v, "revolt", GOLD, 190))
    tv = cam.view(tint)
    cx, cy = cam.pt(*v.xy(38.3, 40.3))
    s = shrink
    tv2 = tv.resize((int(W * s), int(H * s)), Image.BILINEAR)
    paste(f, tv2, cx - cx * s, cy - cy * s)
    for i, (lat0, lat1) in enumerate(((40.6, 38.95), (36.4, 37.7))):
        for j, dlon in enumerate((-1.2, 0.0, 1.2)):
            a = cam.pt(*v.xy(lat0, 40.3 + dlon * 1.6))
            b = cam.pt(*v.xy(lat1, 40.3 + dlon * 0.7))
            arrow(f, kit.curve(a, b, 0.1 * (j - 1), 30), clamp01((t - 0.3 - j * 0.25 - i * 0.4) / 1.4), (40, 34, 30),
                  16, 40, 240)
    tp = c.D * 0.55
    if t > tp:
        pl = c.get("plane", lambda: kit.cutout(kit.fit(img("S38_1920s_Propeller_Warplane.jpg"), h=520), torn=True, seed=38))
        u = clamp01((t - tp) / (c.D * 0.42))
        x = (-pl.width + u * (W + pl.width)) if c.L.rtl else (W - u * (W + pl.width))
        paste(f, pl, x, 120 + math.sin(u * 3) * 20)
        c.label_for("S38_1920s_Propeller_Warplane.jpg")
    ost_strips(c, f, [c.ost[0]], t, c.a0 + 0.2, size=56)
    ost_strips(c, f, [c.ost[1]], t, tp + 0.3, y=270, size=56, colours=[RED])
    return f


def S39(c, t):
    def bridge(tl, d):
        fr, _ = full_photo(c, "b", "S39_Qasim_Beg_Jibrans_Betrayal.jpg", tl, d, (1.0, 1.1), (0.5, 0.5), (0.5, 0.45),
                           prep=cold)
        t0 = d * 0.35
        if tl > t0:
            st = c.get("betray", lambda: kit.label_strip(c.L, c.ost[1], 76, RED, CREAM, pad=(40, 16)))
            k = kit.back_out((tl - t0) / 0.35, 1.6)
            sc = 1.25 - 0.25 * k
            im = st.resize((int(st.width * sc), int(st.height * sc)), Image.BILINEAR)
            paste(fr, im, W / 2 - im.width / 2, 600 - im.height / 2, clamp01(k * 2))
            if tl > t0 + 1.0:
                dd = ImageDraw.Draw(fr, "RGBA")
                rng = np.random.default_rng(39)
                for k in range(5):
                    x, y = rng.uniform(W / 2 - st.width * 0.4, W / 2 + st.width * 0.4), rng.uniform(560, 640)
                    pts = [(x, y)]
                    for s in range(8):
                        x += rng.uniform(-40, 40)
                        y += rng.uniform(-30, 30)
                        pts.append((x, y))
                    kit.ink_line(dd, pts, clamp01((tl - t0 - 1.0 - k * 0.1) / 0.4), (20, 16, 14), 3, 200)
        return fr

    def walk(tl, d):
        fr, _ = full_photo(c, "w", "Sheikh_Said_Walking_Beside_a_Wall.jpg", tl, d, (1.0, 1.1), (0.45, 0.5), (0.4, 0.45))
        return fr

    a = c.D * 0.6
    f = seq(c, t, [(0, a, bridge), (a, c.D, walk)], xf=0.5)
    ost_strips(c, f, [c.ost[0]], t, c.a0 + 0.2, size=54)
    return f


# ================================================================== chapter 9
def _vignette(f, strength=0.55):
    v = _vig_cache(strength)
    f.alpha_composite(v)
    return f


_VIG = {}


def _vig_cache(s):
    if s not in _VIG:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dd = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        a = np.clip(dd - 0.35, 0, 1) ** 1.2 * 255 * s
        arr = np.zeros((H, W, 4), np.uint8)
        arr[..., 3] = np.clip(a, 0, 255).astype(np.uint8)
        _VIG[s] = Image.fromarray(arr, "RGBA")
    return _VIG[s]


def S40(c, t):
    f = kit.dark_paper().copy()
    cutout_on(c, f, "s", SEATED, t, c.D, 820, 560, h=960, torn=False, border=0, seed=40,
              prep=lambda im: kit.sepia(im, 0.5), scale=(1.0, 1.08))
    shaft = c.get("shaft", _shaft)
    paste(f, shaft, 0, 0, 0.55 + 0.05 * math.sin(t))
    _vignette(f, 0.7)
    ost_strips(c, f, c.ost, t, c.D * 0.55, size=68)
    return f


def _shaft():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(lay).polygon([(1250, -40), (1450, -40), (900, H + 40), (520, H + 40)], fill=(255, 240, 210, 70))
    return lay.filter(ImageFilter.GaussianBlur(40))


def S41(c, t):
    f = paper_bg(c, t, c.D, seed=41)
    portrait_behind(c, f, "S41-S43_Sheikh_Said_in_Prison.jpg", t, 0.2, side="left")
    tag_pill(c, f, "per_article", t, 0.3)
    q = c.quote()
    quote_card(c, f, c.ost, t, q["start"] + 0.2, q["start"] + q["dur"] * 0.22, size=84, underline_line=1)
    return f


def S42(c, t):
    f = paper_bg(c, t, c.D, seed=42)
    d = ImageDraw.Draw(f, "RGBA")
    fold = c.get("fold", _fold)
    f.alpha_composite(fold)
    k1 = kit.back_out((t - 0.2) / 0.6, 1.1)
    k2 = kit.back_out((t - c.D * 0.3) / 0.6, 1.1)
    sh = c.get("sh", lambda: kit.cutout(kit.fit(kit.sepia(img(SEATED).crop((int(2490 * 0.3), int(3004 * 0.18),
                                                                              int(2490 * 0.7), int(3004 * 0.78))),
                                                          0.5), h=760), torn=True, seed=42))
    ism = c.get("is", lambda: kit.cutout(kit.fit(img("Ismet_Pasha_Inonu_1920s_Portrait.jpg"), h=760), torn=True, seed=43))
    if k1 > 0:
        paste(f, sh, c.mx(W * 0.73) - sh.width / 2 + (1 - k1) * (700 if c.L.rtl else -700), H / 2 - sh.height / 2 - 30)
    if k2 > 0:
        paste(f, ism, c.mx(W * 0.27) - ism.width / 2 - (1 - k2) * (700 if c.L.rtl else -700), H / 2 - ism.height / 2 - 30)
        lab = c.get("isl", lambda: kit.label_strip(c.L, c.ost[0], 56, INK, CREAM))
        paste(f, lab, c.mx(W * 0.27) - lab.width / 2, H - 250, clamp01((t - c.D * 0.3 - 0.5) / 0.3))
    return f


def _fold():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    xs = np.arange(W, dtype=np.float32)
    a = np.clip(1 - np.abs(xs - W / 2) / 60, 0, 1) ** 2 * 90
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 3] = a[None, :].astype(np.uint8)
    lay = Image.fromarray(arr, "RGBA")
    ImageDraw.Draw(lay).line([(W / 2, 0), (W / 2, H)], fill=(255, 250, 235, 120), width=2)
    return lay


def S43(c, t):
    f = paper_bg(c, t, c.D, seed=43)
    q = c.quote()
    bright = 0.15 + 0.15 * ease(clamp01((t - q["start"]) / 1.5))
    portrait_behind(c, f, ARCHIVAL_SEPIA, t, bright, side="left")
    tag_pill(c, f, "per_article", t, 0.3)
    quote_card(c, f, c.ost, t, q["start"] + 0.2, q["start"] + q["dur"] * 0.36, size=92, underline_line=None)
    return f


# ================================================================== chapter 10
def _marks(f, t, t0, t1, colour_k=0.0, x_centre=None, y0=330):
    d = ImageDraw.Draw(f, "RGBA")
    n = 48
    for i in range(n):
        at = t0 + (t1 - t0) * (i / n) ** 0.7
        if t < at:
            break
        r, col = divmod(i, 8)
        x = x_centre - 3.5 * 62 + col * 62
        y = y0 + r * 74
        g = tuple(int(GOLD[j] + (150 - GOLD[j]) * colour_k) for j in range(3))
        d.rounded_rectangle([x - 18, y - 26, x + 18, y + 26], 6, fill=g + (255,))


def S44(c, t):
    f = paper_bg(c, t, c.D, seed=44)
    cutout_on(c, f, "s", SEATED, t, c.D, 520, 560, h=880, torn=False, border=14, seed=44,
              prep=lambda im: kit.grade(im, sat=0.0), scale=(1.0, 1.04))
    _marks(f, t, c.D * 0.42, c.D * 0.8, 0.0, x_centre=c.mx(1340), y0=420)
    ost_strips(c, f, [c.ost[0]], t, c.a0 + 0.2, size=56)
    ost_strips(c, f, [c.ost[1]], t, c.D * 0.42, y=270, size=56)
    return f


def S45(c, t):
    f, _ = full_photo(c, "w", WALLS, t, c.D, (1.08, 1.0), (0.52, 0.5), (0.5, 0.55), prep=blue_grey)
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    _marks(over, 99, 0, 1, colour_k=ease(clamp01(t / (c.D * 0.6))), x_centre=c.mx(1460), y0=200)
    paste(f, over, 0, 0, 0.75 * (1 - clamp01((t - c.D * 0.7) / (c.D * 0.3))))
    dark_strip_text(c, f, c.ost[0], t, c.a0 + 0.4, W - 120, 720)
    return f


def S46(c, t):
    P = EXTRA[c.lang]["places"]

    def after(tl, d):
        fr, _ = full_photo(c, "a", "S46_The_Aftermath.jpg", tl, d, (1.0, 1.08), (0.5, 0.55), (0.5, 0.5))
        ost_strips(c, fr, [c.ost[0]], tl, 0.3, size=58, colours=[RED])
        return fr

    def ash(tl, d):
        f, cam, v = map_shot(c, "ash", (40.4, 38.3, 5.6), tl, d, (1.0, 1.04), tints=(("revolt", GOLD, 70),))
        dd = ImageDraw.Draw(f, "RGBA")
        rng = np.random.default_rng(46)
        pth = MPath(v.ring(AREAS["revolt"]))
        k = 0
        while k < 70:
            x, y = rng.uniform(0, v.w), rng.uniform(0, v.h)
            if not pth.contains_point((x, y)):
                continue
            at = rng.uniform(0.1, 0.8) * d
            sx, sy = cam.pt(x, y)
            g = ease(clamp01((tl - at) / 0.4))
            col = tuple(int(GOLD[j] + (110 - GOLD[j]) * g) for j in range(3))
            dd.ellipse([sx - 8, sy - 8, sx + 8, sy + 8], fill=col + (255,))
            if g > 0.5:
                dd.line([(sx - 6, sy - 6), (sx + 6, sy + 6)], fill=(60, 56, 52, 220), width=2)
            k += 1
        ost_strips(c, f, [c.ost[0]], 99, 0, size=58, colours=[RED])
        return f

    def nursi(tl, d):
        f, cam, v = map_shot(c, "ex", (35.8, 38.6, 16), tl, d, (1.0, 1.03))
        a, b = cam.pt(*v.place("van")), cam.pt(*v.place("burdur"))
        dd = ImageDraw.Draw(f, "RGBA")
        city_dot(dd, *a, 9)
        route(f, kit.curve(a, b, -0.1, 80), clamp01((tl - 0.6) / (d * 0.7)), r=5, gap=17)
        if tl > 0.6 + d * 0.7:
            kit.map_pin(f, b[0], b[1], tl - 0.6 - d * 0.7)
        map_label(c, f, P["van"], a[0], a[1], tl, 0.3, 38)
        cutout_on(c, f, "n", "Said_Nursi_Portrait.jpg", tl, d, W - 380, 560, h=640, torn=True, seed=46, enter=0.0,
                  enter_from="right")
        ost_strips(c, f, [c.ost[1]], tl, 0.4, y=150, x=W - 760, size=54)
        return f

    a, b = c.D * 0.28, c.D * 0.55
    return seq(c, t, [(0, a, after), (a, b, ash), (b, c.D, nursi)], xf=0.4)


# ================================================================== chapter 11
def S47(c, t):
    f = paper_bg(c, t, c.D, seed=47)
    portrait_behind(c, f, "Sheikh_Said_Painted_Cover_Portrait.jpg", t, 0.24, side="left")
    tag_pill(c, f, "attributed", t, 0.3)
    q = c.quote()
    quote_card(c, f, c.ost, t, q["start"] + q["dur"] * 0.3, q["start"] + q["dur"] * 0.45, size=124, underline_line=0)
    return f


def S48(c, t):
    f = paper_bg(c, t, c.D, seed=48)
    portrait_behind(c, f, "Sheikh_Said_Colourised_Portrait.jpg", t, 0.22, side="left")
    tag_pill(c, f, "attributed", t, 0.3)
    q = c.quote()
    quote_card(c, f, c.ost, t, q["start"] + q["dur"] * 0.5, q["start"] + q["dur"] * 0.92, size=82, underline_line=1)
    return f


# ================================================================== chapter 12
def S49(c, t):
    def pair(tl, d):
        f = paper_bg(c, tl, d, seed=49)
        cutout_on(c, f, "s", "S08_Salahuddin_al-Ayyubi.jpg", tl, d, W - 520, 560, h=760, torn=True, seed=49, enter=0.1,
                  enter_from="right")
        cutout_on(c, f, "k", ARCHIVAL_SEPIA, tl, d, 520, 560, h=760, torn=True, seed=50, enter=0.6, enter_from="left")
        if tl > 1.2:
            dd = ImageDraw.Draw(f, "RGBA")
            pts = kit.curve((c.mx(W - 520 - 260), 600), (c.mx(520 + 260), 600), -0.12, 50)
            kit.ink_line(dd, pts, clamp01((tl - 1.2) / 0.8), GOLD, 9)
        ink_text(c, f, [c.ost[0]], tl, d * 0.45, x=W / 2, y=90, size=76, rate=6, mode="words", align="center", stroke=2)
        return f

    def domes(tl, d):
        f = paper_bg(c, tl, d, seed=51)
        sk = c.get("sky", lambda: props.skyline(seed=7))
        u = prog(tl, d)
        paste(f, sk, -120 - u * 140 if c.L.rtl else -260 + u * 140, H - sk.height + 40)
        ink_text(c, f, [c.ost[0]], 99, 0, x=W / 2, y=90, size=76, rate=6, mode="words", align="center", stroke=2)
        return f

    a = c.D * 0.62
    return seq(c, t, [(0, a, pair), (a, c.D, domes)], xf=0.45)


def S50(c, t):
    f, cam, v = map_shot(c, "krg", (42.6, 35.7, 9.0), t, c.D, (1.0, 1.04), tints=(("krg", GOLD, 140),))
    dd = ImageDraw.Draw(f, "RGBA")
    for i in range(6):
        if i < 3:
            a = cam.pt(*v.xy(36.4 + i * 0.4, 38.8))
        else:
            a = cam.pt(*v.xy(33.6, 42.0 + (i - 3) * 1.0))
        b = cam.pt(*v.xy(36.2 + (i % 3) * 0.2, 43.8 + (i % 3) * 0.3))
        arrow(f, kit.curve(a, b, 0.08, 30), clamp01((t - 0.4 - i * 0.25) / 1.4), (90, 80, 70), 7, 24, 220)
    rng = np.random.default_rng(50)
    tn = c.get("tent", props.tent)
    n = int(min(40, max(0, t - 1.0) * 6))
    for i in range(n):
        lat, lon = rng.uniform(35.6, 36.9), rng.uniform(43.2, 45.0)
        x, y = cam.pt(*v.xy(lat, lon))
        paste(f, tn, x - tn.width / 2, y - tn.height / 2)
    ost_strips(c, f, [c.ost[0]], t, c.a0 + 0.2, size=60)
    t1 = c.D * 0.5
    if t > t1:
        u = ease(clamp01((t - t1) / (c.D * 0.3)))
        num = kit.line_img("kmr", "ltr", f"{1.8 * u:.1f}", 190, GOLD, 4)[0]
        panel = Image.new("RGBA", (500, 270), (0, 0, 0, 0))
        ImageDraw.Draw(panel).rounded_rectangle([0, 0, 499, 269], 24, fill=GREEN + (235,))
        px = c.mx(W - 140) - (500 if c.L.rtl else 0)
        paste(f, panel, px, 380)
        paste(f, num, px + 250 - num.width / 2, 380 + 135 - num.height / 2)
        ost_strips(c, f, [c.ost[1]], t, t1 + 0.6, y=680, size=54)
    return f


def S51(c, t):
    f = paper_bg(c, t, c.D, seed=52)
    verse = c.ost[0]
    vimg = c.get("verse", lambda: kit.line_img("ar", "rtl", verse, 84, (150, 112, 44), 1, kit.QURAN_FONT)[0])
    a = ease(clamp01((t - 0.2) / 1.5))
    paste(f, vimg, W / 2 - vimg.width / 2, 330 - vimg.height / 2, a)
    ref = c.get("ref", lambda: kit.line_img(c.L.key, c.L.dir, c.ost[1], 46, INK, 1)[0])
    paste(f, ref, W / 2 - ref.width / 2, 470, clamp01((t - 1.4) / 0.8))
    t3 = c.D * 0.66
    ink_text(c, f, [c.ost[2]], t, t3, x=W / 2, y=650, size=72, rate=4, mode="words", align="center", stroke=2)
    return f


# ================================================================== chapter 13
def S52(c, t):
    f = Image.new("RGBA", (W, H), GREEN + (255,))
    p = c.get("pos", lambda: kit.pill(c.L, c.x["labels"]["position_tag"], 34, fill=GOLD, fg=GREEN))
    paste(f, p, W / 2 - p.width / 2, 230, clamp01((t - 0.2) / 0.4))
    n = len(c.ost)
    for i, line in enumerate(c.ost):
        t0 = c.a0 + 0.2 + i * (c.D * 0.75 / n)
        im = c.get(("pl", i), lambda line=line: kit.line_img(c.L.key, c.L.dir, line, 72, CREAM, 2)[0])
        k = ease(clamp01((t - t0) / 0.6))
        paste(f, im, W / 2 - im.width / 2, 380 + i * 130 + (1 - k) * 20, k)
    return f


def S53(c, t):
    f = paper_bg(c, t, c.D, seed=53)
    co = c.get("p", lambda: kit.cutout(kit.fit(img(ARCHIVAL_SEPIA), h=880), torn=True, seed=3))
    k = kit.back_out(t / 0.7, 1.1)
    z = 1.0 + 0.22 * ease(clamp01(t / c.D))
    im = co.resize((int(co.width * z), int(co.height * z)), Image.BILINEAR)
    ex = c.mx(600)
    paste(f, im, ex - im.width / 2, 560 - im.height * 0.42 + (1 - k) * 300)
    warm = clamp01(t / c.D)
    glow = c.get("wg", lambda: _radial(1400, (255, 200, 130)))
    paste(f, glow, ex - 700, 560 - 700, 0.25 * warm)
    big = c.get("nm", lambda: kit.line_img(c.L.key, c.L.dir, c.ost[0], 112, INK, 3)[0])
    paste(f, big, c.mx(W - 160) - (big.width if c.L.rtl else 0), 340, clamp01((t - 0.5) / 0.6))
    yrs = c.get("yr", lambda: kit.line_img(c.L.key, c.L.dir, c.ost[1], 76, GOLD, 2)[0])
    paste(f, yrs, c.mx(W - 160) - (yrs.width if c.L.rtl else 0), 540, clamp01((t - 0.9) / 0.6))
    return f


def S54(c, t):
    f = Image.new("RGBA", (W, H), GREEN + (255,))
    k = ease(clamp01(t / 0.4))
    lg = kit.logo(c.L.key, True, 420, 1.0)
    s = 0.96 + 0.04 * k
    im = lg.resize((int(lg.width * s), int(lg.height * s)), Image.LANCZOS)
    paste(f, im, W / 2 - im.width / 2, 380 - im.height / 2, k)
    for i, line in enumerate(c.ost):
        im2 = c.get(("end", i), lambda line=line, i=i: kit.line_img(c.L.key, c.L.dir, line, [60, 44][i], [CREAM, GOLD][i], 1)[0])
        paste(f, im2, W / 2 - im2.width / 2, 700 + i * 100, clamp01((t - 0.5 - i * 0.3) / 0.5))
    fade = clamp01((t - (c.D - 1.0)) / 1.0)
    if fade > 0:
        f = Image.blend(f, Image.new("RGBA", (W, H), (0, 0, 0, 255)), fade)
    return f


SCENES = {k: v for k, v in globals().items() if k.startswith("S") and k[1:].isdigit()}
