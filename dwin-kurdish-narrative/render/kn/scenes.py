"""The 39 scenes of «The Kurdish narrative». Each scene(c, t) returns an RGBA frame of c.W x c.H.

All on-screen text is the scene's `t` text from script/scenes.json, split at its own separators.
Missing real items (R18, R22-R25, R28) are covered with graphics; R26/R27 reuse earlier real clips.
"""
import math
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import base as B
from .base import CREAM, DARK, GREEN, INK, PAPER, RED, SAFFRON, T, clamp01, ease, ease_out, back_out, kit, paste, strips
from .lib import (big_text, headline, tag, timeline_bar, ink_layer, lower_strip, framed_clip, vert_bg_from_clip,
                  person_layer, split, counter_text, _stamp)
from vox import geo

ARCH = "Public archive"
CREDITS = {
    "R01_sharafnama_manuscript.jpg": ARCH, "R02_saladin_statue.jpg": ARCH, "R03_jerusalem_old_city.jpg": ARCH,
    "R04_chaldiran_mural.jpg": "Chehel Sotoun, Isfahan", "R05_mem_u_zin_manuscript.jpg": ARCH,
    "R06_bedirxan_beg_portrait.jpg": ARCH, "R07_treaty_of_sevres_page.jpg": ARCH,
    "R08_lausanne_conference_1923.jpg": ARCH, "R09_diyarbakir_walls.jpg": ARCH, "R10_sanandaj_city.jpg": ARCH,
    "R11_erbil_citadel.jpg": ARCH, "R12_qamishli_street.jpg": ARCH, "R13_nowruz_fire_akre.jpg": ARCH,
    "R14_amna_suraka_museum.jpg": ARCH, "R15_halabja_monument.jpg": ARCH, "R16_dersim_landscape.jpg": ARCH,
    "R17_mahabad_republic_1946.jpg": ARCH, "R19_said_nursi_portrait.jpg": ARCH, "R20_sheikh_said_1925.jpg": ARCH,
    "R21_tekke_courtyard.jpg": ARCH,
    "R26_damascus_dec2024.mp4": "BBC News", "R27_syria_jan2026_agreement.mp4": "Syrian Presidency",
}
ERA = (1187, 1514, 1597, 1692, 1847, 1920, 1923, 2005)
A = {k: f"{k}.png" for k in ("A01_zagros_mountains_mist", "A02_old_book_pages_wind", "A03_person_on_ridge_sunrise",
                             "A04_cracked_mirror", "A05_islamic_manuscript_library", "A06_calligraphy_desk",
                             "A07_two_doors_corridor", "A08_group_walking_dusk")}


def ost(c, i=0):
    return c.ost[i] if i < len(c.ost) else ""


def credit(c, name):
    c.credit = CREDITS.get(name)


def sepia(im):
    return kit.sepia(im, 0.85)


def cold(im):
    return Image.fromarray(np.clip(np.asarray(im.convert("RGB")).astype(np.float32) * [0.85, 0.95, 1.12], 0, 255)
                           .astype(np.uint8))


def golden(im):
    return Image.fromarray(np.clip(np.asarray(im.convert("RGB")).astype(np.float32) * [1.12, 1.0, 0.82], 0, 255)
                           .astype(np.uint8))


# ------------------------------------------------------------------ building blocks
def photo_scene(c, t, name, z=None, dark=0.85, label=None, prep=None, grain_amt=8.0, c0=(0.5, 0.5), c1=(0.5, 0.5)):
    real = not name.startswith("A")
    f, cam = B.kenburns(c, name, t, c.D, z=z, label=not real if label is None else label, prep=prep, dark=dark,
                        grain_amt=grain_amt, c0=c0, c1=c1)
    if real:
        credit(c, name)
    return f


def top_strips(c, f, lines, t, t0=0.5, stagger=0.45, size=None, colours=None, bgs=None):
    return lower_strip(c, f, [l for l in lines if l], t, t0, stagger=stagger, size=size or (52 if not c.vert else 48),
                       y=c.top - (10 if not c.vert else 0), colours=colours, bgs=bgs)


def cut_photo(c, f, t, name, t0, cx, cy, w=None, h=None, rot=0.0, prep=None, frm=None, torn=False):
    im = B.cut(c, name, w=w, h=h, torn=torn, border=12, rot=rot, seed=hash(name) % 7, prep=prep)
    box = B.place(f, im, cx, cy, t, t0, frm)
    credit(c, name) if not name.startswith("A") else c.illustration()
    return box


def side_layout(c):
    """(photo centre x, text column) for 16:9: photo on the reading-end side, text on the reading-start side."""
    if c.vert:
        return c.W / 2, (c.margin, c.W - c.margin)
    px = c.W * 0.30 if c.rtl else c.W * 0.70
    col = (c.W * 0.50, c.W - c.margin) if c.rtl else (c.margin, c.W * 0.50)
    return px, col


def year_of(text):
    m = re.search(r"\b(1\d{3}|20\d{2})\b", text.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")))
    return int(m.group(1)) if m else None


def era_bar(c, f, t, year, frm=None):
    timeline_bar(c, f, t, year, 0.4, years=ERA, frm=frm or year)


def archival_scene(c, t, name, prep=sepia, rot=-2.0, year=None, frm=None, bg_seed=None, w=None):
    """Paper desk, an archival cut-out on the reading-end side, OST strips on the reading-start side."""
    f = B.paper_bg(c, t, c.D, bg_seed or (int(c.id[1:]) + 3))
    px, col = side_layout(c)
    if c.vert:
        cut_photo(c, f, t, name, 0.2, c.W / 2, c.H * 0.56, w=w or 820, rot=rot, prep=prep, frm="bottom")
        strips(c, f, [l for l in c.ost if l], t, 0.6, y=c.top, size=48, stagger=0.45)
    else:
        cut_photo(c, f, t, name, 0.2, px, c.H * 0.46, w=w or 720, h=620, rot=rot, prep=prep,
                  frm="left" if c.rtl else "right")
        strips(c, f, [l for l in c.ost if l], t, 0.6, col=col, y=c.H * 0.30, size=54, stagger=0.45)
    if year:
        era_bar(c, f, t, year, frm)
    return B.grain(f, t, 6)


def quote_card(c, f, text, t, t0, colour=CREAM, box=(24, 26, 30), hi=SAFFRON, size=None, y=None):
    size = size or (78 if not c.vert else 66)
    cw = c.W - (300 if not c.vert else 120)
    im = big_text(c, text, size, colour, cw - 120)
    ch = im.height + 160
    card = c.get(("qcard", text), lambda: B.card(cw, ch, box, 18))
    k = ease_out((t - t0) / 0.6)
    if k <= 0:
        return
    y = y if y is not None else (c.H * 0.42 - ch / 2)
    x = c.W / 2 - cw / 2
    paste(f, card, x, y + (1 - k) * 40, 0.93 * k)
    q = T("ar", "«" if c.rtl else "“", 220, hi, True)
    paste(f, q, x + (cw - q.width - 20 if c.rtl else 20), y - 70, k)
    paste(f, kit.wipe(im, ease((t - t0 - 0.3) / 1.0), c.rtl), c.W / 2 - im.width / 2, y + 80)


def mist(c, f, t, alpha=0.25):
    def build():
        rng = np.random.default_rng(3)
        w, h = c.W // 4 * 2, c.H // 4
        n = np.zeros((h, w), np.float32)
        for sc, amp in ((8, 1.0), (24, 0.7), (64, 0.5)):
            a = rng.normal(0, 1, (max(2, h // sc), max(2, w // sc))).astype(np.float32)
            n += np.asarray(Image.fromarray(a).resize((w, h), Image.BICUBIC)) * amp
        n = np.clip((n - n.min()) / (n.max() - n.min()), 0, 1) ** 1.6
        arr = np.zeros((h, w, 4), np.uint8)
        arr[..., :3] = 235
        arr[..., 3] = (n * 255).astype(np.uint8)
        return Image.fromarray(arr, "RGBA").resize((c.W * 2, c.H), Image.BICUBIC)
    m = c.get(("mist",), build)
    x = -((t * c.W * 0.02) % c.W)
    paste(f, m, x, c.H * 0.25, alpha)


def mountains(c, t, grade):
    """M1: 2-layer parallax on A01 (far ridges 1%, near 4%), mist drifting, cold or golden grade."""
    name = A["A01_zagros_mountains_mist"]
    prep = cold if grade == "cold" else golden
    im = B._big(c, name, prep=prep, k=1.3)
    u = B.prog(t, c.D)
    far = B.Cam(im.width, im.height, u, 1.0, 1.01, (0.5, 0.45), (0.5 + (0.005 if c.rtl else -0.005), 0.45), (c.W, c.H))
    f = far.view(im).convert("RGBA")
    near = B.Cam(im.width, im.height, u, 1.0, 1.04, (0.5, 0.6), (0.5 + (0.02 if c.rtl else -0.02), 0.62), (c.W, c.H))
    nv = near.view(im).convert("RGBA")
    m = c.get(("nearmask",), lambda: Image.fromarray((np.clip((np.linspace(0, 1, c.H) - 0.55) / 0.2, 0, 1) * 255)
                                                      .astype(np.uint8)[:, None].repeat(c.W, 1)))
    f.paste(nv, (0, 0), m)
    mist(c, f, t, 0.22)
    c.illustration()
    return B.grain(B.vignette(f, 0.5), t, 8)


def book(c, t):
    """M2: push-in 1.00->1.08 on A02, page flutter top-right, dust."""
    name = A["A02_old_book_pages_wind"]
    f, cam = B.photo(c, name, t, c.D, (1.0, 1.08), (0.55, 0.5), (0.58, 0.48))
    arr = np.asarray(f).copy()
    H, W = arr.shape[:2]
    y0, y1, x0 = int(H * 0.15), int(H * 0.55), int(W * 0.55)
    for y in range(y0, y1, 2):
        sh = int(3 * math.sin(2 * math.pi * t / 1.5 + y * 0.03) * (1 - (y - y0) / (y1 - y0)))
        if sh:
            arr[y:y + 2, x0:] = np.roll(arr[y:y + 2, x0:], sh, axis=1)
    f = Image.fromarray(arr, "RGBA")
    rng = np.random.default_rng(11)
    d = ImageDraw.Draw(f)
    for k in range(60):
        x = (rng.uniform(0, W) + t * rng.uniform(-15, 15)) % W
        y = (rng.uniform(0, H) - t * rng.uniform(5, 20)) % H
        r = rng.uniform(1, 2.5)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 236, 200, int(rng.uniform(60, 150))))
    return B.grain(B.vignette(f, 0.5), t, 8)


def doors(c, t):
    """M3: dolly toward the warm right door, light-leak flicker."""
    name = A["A07_two_doors_corridor"]
    f, cam = B.photo(c, name, t, c.D, (1.0, 1.15), (0.5, 0.5), (0.62, 0.52))
    fl = 1 + 0.05 * math.sin(t * 5.3) * math.sin(t * 1.7 + 0.4)
    glow = c.get(("dglow",), lambda: B.radial_img(int(c.W * 0.7), int(c.H * 0.9), (255, 190, 110)))
    im = B._big(c, name)
    gx, gy = cam.pt(0.62 * im.width, 0.55 * im.height)
    paste(f, glow, gx - glow.width / 2, gy - glow.height / 2, 0.18 * fl)
    return B.grain(B.vignette(f, 0.55), t, 8)


def text_behind(c, t, name, title, t0, size, z_bg=(1.0, 1.03), z_p=(1.0, 1.06), ty=0.28, prep=None):
    """Background -> giant title -> subject matte (rembg)."""
    im = B._big(c, name)
    u = B.prog(t, c.D)
    cam_bg = B.Cam(im.width, im.height, u, z_bg[0], z_bg[1], (0.5, 0.5), (0.5, 0.5), (c.W, c.H))
    f = B.darken(cam_bg.view(im).convert("RGBA"), 0.85)
    k = ease_out((t - t0) / 0.9)
    if k > 0:
        ti = big_text(c, title, size, CREAM, c.W - 120)
        paste(f, ti, c.W / 2 - ti.width / 2, c.H * ty - ti.height / 2 + (1 - k) * 40, k)
    lay = person_layer(c, name, "p")
    cam_p = B.Cam(im.width, im.height, u, z_p[0], z_p[1], (0.5, 0.5), (0.5, 0.5 - 0.015 * u), (c.W, c.H))
    f.alpha_composite(cam_p.view(lay))
    if name.startswith("A"):
        c.illustration()
    return B.grain(B.vignette(f, 0.5), t, 8)


def chapter_card(c, n, t):
    f = B.dark_bg(c, 5)
    num = c.get(("chnum", n), lambda: T(c.lang, f"0{n}" if c.lang == "kmr" else str(n).translate(
        str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")), 190 if not c.vert else 210, SAFFRON, True))
    title = c.sc.get("chapter_title", "")
    k = ease_out(t / 0.5)
    cy = c.H * 0.45
    paste(f, num, c.W / 2 - num.width / 2, cy - num.height + 30 - (1 - k) * 30, k)
    if title:
        ti = big_text(c, title, 84 if not c.vert else 72, CREAM, c.W - 200)
        paste(f, kit.wipe(ti, ease((t - 0.25) / 0.6), c.rtl), c.W / 2 - ti.width / 2, cy + 50)
        w = int(260 * ease((t - 0.4) / 0.6))
        if w > 2:
            yy = cy + 50 + ti.height + 30
            ImageDraw.Draw(f).line([(c.W / 2 - w / 2, yy), (c.W / 2 + w / 2, yy)], fill=SAFFRON + (255,), width=6)
    return f


# ------------------------------------------------------------------ maps
COUNTRIES = ["Turkey", "Iran", "Iraq", "Syria"]


def region_map(c):
    def build():
        span = 22.0 if not c.vert else 13.5
        v = geo.View(42.5, 36.2 if not c.vert else 36.0, span, c.W, c.H)
        im = geo.base_map(v, rivers=("euphrates", "tigris"), highlight=COUNTRIES, seed=4)
        im.alpha_composite(geo.area_tint(v, "kurdistan", SAFFRON, 120))
        return im, v
    return c.get(("rmap",), build)


# ------------------------------------------------------------------ scenes
def s01(c, t):
    f = mountains(c, t, "cold")
    headline(c, f, ost(c), t, 0.8, 84 if not c.vert else 72, c.H * (0.24 if not c.vert else 0.30), mode="wipe", dur=1.6)
    return f


def s02(c, t):
    mp, v = region_map(c)
    u = B.prog(t, c.D)
    cam = B.Cam(c.W, c.H, u, 1.0, 1.05, (0.5, 0.5), (0.5, 0.48), (c.W, c.H))
    f = cam.view(mp).convert("RGBA")
    parts = split(ost(c), "|")
    tn = c.at("نحو", "نزیکەی", "Nêzîkî", default=c.frac(0.05))
    if t > tn - 0.3:
        txt = counter_text(parts[0], clamp01((t - tn) / 1.6))
        im = B.strip_img(c.lang, txt, 96 if not c.vert else 80, CREAM, INK)
        paste(f, im, c.W / 2 - im.width / 2, c.top - 20, ease((t - tn + 0.3) / 0.4))
    if len(parts) > 1:
        tc = c.at("تركيا", "تورکیا", "Tirkiye", default=c.frac(0.3))
        st = B.strip_img(c.lang, parts[1], 60, INK, SAFFRON)
        paste(f, st, c.W / 2 - st.width / 2, c.top + (150 if not c.vert else 140), ease((t - tc) / 0.5))
    return B.grain(f, t, 5)


def s03(c, t):
    f = B.darken(book(c, t), 0.55)
    c.illustration()
    t0 = c.at("الحكاية", "چیرۆکەکە", "Çîrok", default=c.frac(0.35))
    headline(c, f, ost(c), t, t0 - 0.2, 140 if not c.vert else 110, c.H * 0.42, mode="wipe", dur=1.0)
    return f


def s04(c, t):
    f = text_behind(c, t, A["A03_person_on_ridge_sunrise"], ost(c), 0.3, 230 if not c.vert else 160, ty=0.30)
    return f


def s05(c, t):
    f = B.paper_bg(c, t, c.D, 5)
    parts = split(ost(c), "=")
    k = ease((t - 0.3) / 0.8)
    if k > 0:
        im = big_text(c, ost(c), 92 if not c.vert else 76, INK)
        paste(f, kit.wipe(im, k, c.rtl), c.W / 2 - im.width / 2, c.H * 0.24)
    # three narrative boxes: memory (past) -> reading (present) -> direction (future)
    n = 3
    bw = 300 if not c.vert else 260
    gap = 120 if not c.vert else 60
    total = n * bw + (n - 1) * gap
    lay = ink_layer(c)
    d = ImageDraw.Draw(lay)
    for i in range(n):
        ki = ease((t - c.frac(0.25 + 0.2 * i)) / 0.6)
        if ki <= 0:
            continue
        idx = (n - 1 - i) if c.rtl else i
        x = c.W / 2 - total / 2 + idx * (bw + gap)
        y = c.H * (0.52 if not c.vert else 0.50)
        pts = [(x, y), (x + bw, y), (x + bw, y + bw * 0.7), (x, y + bw * 0.7), (x, y)]
        kit.ink_line(d, kit.resample(pts, 6), ki, INK, 6)
        cx, cy = x + bw / 2, y + bw * 0.35
        if ki > 0.9:
            if i == 0:
                d.ellipse([cx - 50, cy - 50, cx + 50, cy + 50], outline=INK + (230,), width=6)
                d.line([(cx, cy), (cx, cy - 34)], fill=INK + (230,), width=6)
                d.line([(cx, cy), (cx + 26, cy)], fill=INK + (230,), width=6)
            elif i == 1:
                d.ellipse([cx - 70, cy - 32, cx + 70, cy + 32], outline=INK + (230,), width=6)
                d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=SAFFRON + (255,))
            else:
                sgn = -1 if c.rtl else 1
                d.line([(cx - 60 * sgn, cy), (cx + 60 * sgn, cy)], fill=INK + (230,), width=8)
                kit.arrow_head(d, (cx - 60 * sgn, cy), (cx + 60 * sgn, cy), INK, 30, 8)
        if i < n - 1 and ki > 0.95:
            ax0 = x + bw + 15 if not c.rtl else x - 15
            ax1 = x + bw + gap - 15 if not c.rtl else x - gap + 15
            ay = y + bw * 0.35
            d.line([(ax0, ay), (ax1, ay)], fill=SAFFRON + (255,), width=6)
            kit.arrow_head(d, (ax0, ay), (ax1, ay), SAFFRON, 22, 6)
    f.alpha_composite(lay)
    return B.grain(f, t, 6)


def s06(c, t):
    return archival_scene(c, t, "R01_sharafnama_manuscript.jpg", prep=None, year=1597, frm=1187, w=520)


def s07(c, t):
    bg = photo_scene(c, t, "R03_jerusalem_old_city.jpg", dark=0.55)
    px, col = side_layout(c)
    if c.vert:
        cut_photo(c, bg, t, "R02_saladin_statue.jpg", 0.3, c.W / 2, c.H * 0.58, w=760, rot=1.5, frm="bottom")
        strips(c, bg, [l for l in c.ost if l], t, 0.8, y=c.top, size=48)
    else:
        cut_photo(c, bg, t, "R02_saladin_statue.jpg", 0.3, px, c.H * 0.47, h=760, rot=1.5,
                  frm="left" if c.rtl else "right")
        strips(c, bg, [l for l in c.ost if l], t, 0.8, col=col, y=c.H * 0.32, size=56)
    era_bar(c, bg, t, 1187)
    return bg


def s08(c, t):
    return archival_scene(c, t, "R04_chaldiran_mural.jpg", prep=None, year=1514, frm=1187, w=560, rot=1.5)


def s09(c, t):
    f = photo_scene(c, t, "R05_mem_u_zin_manuscript.jpg", dark=0.45, prep=sepia)
    parts = split(ost(c), "—")
    quote_card(c, f, parts[0], t, c.at("لو", "ئەگەر", "Ger", default=c.frac(0.5)) - 0.3)
    if len(parts) > 1:
        tag(c, f, parts[1], t, c.frac(0.7), y=c.H * (0.72 if not c.vert else 0.66))
    era_bar(c, f, t, 1692, 1597)
    return f


def s10(c, t):
    return archival_scene(c, t, "R06_bedirxan_beg_portrait.jpg", year=1847, frm=1692, w=440, rot=-1.5)


def s11(c, t):
    f = archival_scene(c, t, "R07_treaty_of_sevres_page.jpg", prep=None, year=1920, frm=1847, w=760, rot=1.0)
    return f


def s12(c, t):
    return archival_scene(c, t, "R08_lausanne_conference_1923.jpg", year=1923, frm=1920, w=700, rot=-1.0)


def panel_grid(c, i, n=4):
    if not c.vert:
        cols, rows = 2, 2
        gw, gh = 24, 24
        w = (c.W - 2 * 140 - gw) / cols
        h = (c.cap_top - 140 - 160 - gh) / rows
        r, k = divmod(i, cols)
        if c.rtl:
            k = cols - 1 - k
        return int(140 + k * (w + gw)), int(160 + r * (h + gh)), int(w), int(h)
    top, bot = 330, c.cap_top - 60
    h = (bot - top - 3 * 16) / 4
    return 60, int(top + i * (h + 16)), c.W - 120, int(h)


def s13(c, t):
    f = B.paper_bg(c, t, c.D, 13)
    names = ["R09_diyarbakir_walls.jpg", "R10_sanandaj_city.jpg", "R11_erbil_citadel.jpg", "R12_qamishli_street.jpg"]
    labels = split(ost(c), "·")
    keys = [("تركيا", "تورکیا", "Tirkiyeyê"), ("إيران", "ئێران", "Îranê"), ("العراق", "عێراق", "Iraqê"),
            ("سوريا", "سووریا", "Sûriyeyê")]
    for i, nm in enumerate(names):
        x, y, w, h = panel_grid(c, i)
        t0 = c.at(*keys[i], default=c.frac(0.15 + 0.2 * i)) - 0.3
        k = ease_out((t - t0) / 0.5)
        if k <= 0:
            continue
        im = B.photo_box(c, nm, w, h, t - t0, c.D, (1.0, 1.06))
        if i < len(labels):
            lb = B.fit_w(B.strip_img(c.lang, labels[i], 42 if not c.vert else 40, INK, SAFFRON), w - 20)
            paste(im, lb, w / 2 - lb.width / 2, h - lb.height - 10)
        fr = Image.new("RGBA", (w + 10, h + 10), CREAM + (255,))
        fr.alpha_composite(im, (5, 5))
        paste(f, B.shadowed(fr, 8, (6, 8), 90), x - 5 - 24, y - 5 - 24 + (1 - k) * 50, k)
    c.credit = ARCH
    era_bar(c, f, t, 2005, 1923)
    return f


def s14(c, t):
    f = photo_scene(c, t, A["A04_cracked_mirror"], z=(1.0, 1.06), dark=0.7)
    headline(c, f, ost(c), t, c.frac(0.1), 86 if not c.vert else 70, c.H * (0.20 if not c.vert else 0.24), mode="wipe",
             dur=1.0)
    return f


def s15(c, t):
    f = photo_scene(c, t, "R13_nowruz_fire_akre.jpg", dark=0.6)
    lines = [l for l in c.ost if l]
    t1 = c.at("يجمعها", "کۆیان", "dicivîne", default=c.frac(0.1))
    t2 = c.at("يفرّقها", "جیایان", "dixe", default=c.frac(0.5))
    strips(c, f, lines[:2], t, t1, y=c.top, size=52 if not c.vert else 46, times=[t1, t2][:len(lines[:2])],
           colours=[INK, CREAM], bgs=[SAFFRON, (40, 40, 44)])
    return f


def s16(c, t):
    f = B.paper_bg(c, t, c.D, 16)
    items = split(ost(c), "·")
    n = len(items)
    lay = ink_layer(c)
    d = ImageDraw.Draw(lay)
    rx, ry = c.W / 2, c.H * (0.30 if not c.vert else 0.30)
    trunk = ease((t - 0.3) / 0.8)
    d.line([(rx, ry - 140), (rx, ry - 140 + 140 * trunk)], fill=INK + (230,), width=10)
    f.alpha_composite(lay)
    for i, it in enumerate(items):
        ki = ease((t - c.frac(0.15 + 0.12 * i)) / 0.6)
        if ki <= 0:
            continue
        if not c.vert:
            u = i / max(1, n - 1)
            x = c.margin + 120 + (c.W - 2 * c.margin - 240) * (1 - u if c.rtl else u)
            y = c.H * 0.62
        else:
            x = c.W / 2 + (-230 if i % 2 == 0 else 230)
            y = c.H * 0.42 + i * 150
        lay2 = ink_layer(c)
        kit.ink_line(ImageDraw.Draw(lay2), kit.curve((rx, ry), (x, y - 50), 0.12), ki, INK, 6)
        f.alpha_composite(lay2)
        lb = c.get(("dlab", i), lambda it=it: B.strip_img(c.lang, it, 46 if not c.vert else 40, INK,
                                                         SAFFRON if i < 2 else CREAM))
        paste(f, lb, x - lb.width / 2, y - 40, clamp01(ki * 2 - 1))
    return B.grain(f, t, 6)


def s17(c, t):
    f = B.paper_bg(c, t, c.D, 17, tone=(214, 196, 168))
    left, res = (split(ost(c), "←", "→") + [""])[:2]
    caps = split(left, "·")
    hub = (c.W / 2, c.H * (0.62 if not c.vert else 0.66))
    pts = ([(c.W * 0.2, c.H * 0.32), (c.W * 0.5, c.H * 0.24), (c.W * 0.8, c.H * 0.32)] if not c.vert else
           [(c.W * 0.25, c.H * 0.30), (c.W * 0.75, c.H * 0.38), (c.W * 0.3, c.H * 0.48)])
    if c.rtl and not c.vert:
        pts = pts[::-1]
    lay = ink_layer(c)
    d = ImageDraw.Draw(lay)
    for i, (x, y) in enumerate(pts[:len(caps)]):
        ki = ease((t - c.frac(0.1 + 0.15 * i)) / 0.6)
        if ki <= 0:
            continue
        kit.string(d, (x, y), hub, RED, 4, ki)
        kit.pin(d, x, y)
    kit.pin(d, *hub)
    f.alpha_composite(lay)
    for i, (x, y) in enumerate(pts[:len(caps)]):
        ki = ease((t - c.frac(0.1 + 0.15 * i)) / 0.5)
        if ki > 0:
            card = c.get(("sb", i), lambda i=i: B.strip_img(c.lang, caps[i], 52, INK, CREAM, rot=(-2, 1.5, -1)[i]))
            paste(f, card, x - card.width / 2, y - card.height - 14, ki)
    if res:
        kr = ease((t - c.frac(0.7)) / 0.5)
        card = c.get(("sbr",), lambda: B.strip_img(c.lang, res, 56, CREAM, RED))
        paste(f, card, hub[0] - card.width / 2, hub[1] + 20, kr)
    return B.grain(f, t, 6)


def s18(c, t):
    f = B.dark_bg(c, 18)
    words = ost(c).split(" ")
    n = len(words)
    k = clamp01((t - 0.3) / max(1.0, c.a1 - 0.8))
    shown = " ".join(words[:max(1, int(math.ceil(k * n)))])
    if k > 0:
        im = big_text(c, shown, 110 if not c.vert else 88, CREAM, c.W - 200)
        paste(f, im, c.W / 2 - im.width / 2, c.H * 0.42 - im.height / 2)
    return f


def range_chart(c, f, t, t0, lo=50, hi=182, maxv=200, y=None):
    y = y or (c.H * 0.70 if not c.vert else c.H * 0.70)
    x0, x1 = c.margin + 40, c.W - c.margin - 40

    def X(v):
        return x1 - (x1 - x0) * v / maxv if c.rtl else x0 + (x1 - x0) * v / maxv
    d = ImageDraw.Draw(f)
    pa = ease((t - t0) / 0.8)
    if pa <= 0:
        return
    d.line([(x0, y + 60), (x1, y + 60)], fill=INK + (255,), width=3)
    for v in range(0, maxv + 1, 50):
        xx = X(v)
        d.line([(xx, y + 50), (xx, y + 70)], fill=INK + (255,), width=3)
        im = T(c.lang, str(v), 26, INK, True)
        paste(f, im, xx - im.width / 2, y + 72)
    p2 = ease((t - t0 - 0.6) / 1.4)
    if p2 > 0:
        a, b = X(lo), X(lo + (hi - lo) * p2)
        lay = ink_layer(c)
        dl = ImageDraw.Draw(lay)
        dl.rectangle([min(a, b), y - 30, max(a, b), y + 40], fill=RED + (190,))
        dl.rectangle([min(a, b), y - 30, max(a, b), y + 40], outline=INK + (255,), width=3)
        f.alpha_composite(lay)


def s19(c, t):
    f = B.paper_bg(c, t, c.D, 19)
    px, col = side_layout(c)
    if not c.vert:
        cut_photo(c, f, t, "R14_amna_suraka_museum.jpg", 0.2, px, c.H * 0.36, w=600, rot=-1.5,
                  frm="left" if c.rtl else "right")
        strips(c, f, split(ost(c), "|"), t, 0.6, col=col, y=c.H * 0.20, size=54)
    else:
        cut_photo(c, f, t, "R14_amna_suraka_museum.jpg", 0.2, c.W / 2, c.H * 0.46, w=700, rot=-1.5, frm="bottom")
        strips(c, f, split(ost(c), "|"), t, 0.6, y=c.top, size=48)
    range_chart(c, f, t, c.at("50", "پەنجا", "pêncî", default=c.frac(0.4)) - 0.4,
                y=c.H * (0.66 if not c.vert else 0.62))
    return f


def s20(c, t):
    f = B.paper_bg(c, t, c.D, 20)
    parts = split(ost(c), "|")
    t2 = c.at("ديرسم", "دێرسیمی", "Dêrsimê", default=c.frac(0.5))
    for i, (nm, t0) in enumerate((("R15_halabja_monument.jpg", 0.2), ("R16_dersim_landscape.jpg", t2 - 0.3))):
        if not c.vert:
            w, h = c.W // 2 - 110, c.cap_top - 330
            x = c.mx(70 + i * (w + 40)) - (w if c.rtl else 0)
            y = 250
        else:
            w, h = c.W - 120, (c.cap_top - 420) // 2 - 20
            x, y = 60, 300 + i * (h + 60)
        k = ease_out((t - t0) / 0.5)
        if k <= 0:
            continue
        im = B.photo_box(c, nm, w, h, t, c.D, (1.0, 1.05))
        if i < len(parts):
            lb = B.fit_w(B.strip_img(c.lang, parts[i], 44, INK, SAFFRON if i == 0 else CREAM), w - 20)
            paste(im, lb, w / 2 - lb.width / 2, h - lb.height - 14)
        fr = Image.new("RGBA", (w + 10, h + 10), CREAM + (255,))
        fr.alpha_composite(im, (5, 5))
        paste(f, B.shadowed(fr, 8, (6, 8), 90), x - 29, y - 29, k)
    c.credit = ARCH
    return f


def s21(c, t):
    f = archival_scene(c, t, "R17_mahabad_republic_1946.jpg", prep=None, w=600, rot=1.0)
    t0 = c.at("11", "یازدە", "yazdeh", default=c.frac(0.55))
    if t > t0 - 0.2:
        val = max(0, 11 - int((t - t0) * 6))
        n = T(c.lang, str(val), 150, RED, True)
        x = c.W / 2 if c.vert else (c.W * 0.75 if c.rtl else c.W * 0.25)
        paste(f, n, x - n.width / 2, c.H * (0.62 if not c.vert else 0.80) - n.height / 2, ease((t - t0 + 0.2) / 0.3))
    return f


def s22(c, t):
    f = B.paper_bg(c, t, c.D, 22)
    strips(c, f, split(ost(c), "|"), t, 0.4, y=c.top, size=54 if not c.vert else 46)
    n = 5
    lay = ink_layer(c)
    d = ImageDraw.Draw(lay)
    cy = c.H * (0.58 if not c.vert else 0.55)
    span = c.W - 2 * c.margin - 100
    lw = span / n
    t_break = c.at("سُحب", "پشتیوانی", "piştgirî", default=c.frac(0.6))
    gap = 60 * ease((t - t_break) / 0.6)
    for i in range(n):
        ki = ease((t - 0.5 - i * 0.25) / 0.4)
        if ki <= 0:
            continue
        idx = n - 1 - i if c.rtl else i
        x = c.margin + 50 + idx * lw
        off = gap if idx >= n // 2 + 1 else (-gap if idx <= n // 2 - 1 else 0)
        if idx == n // 2:
            ang = 0.3 * ease((t - t_break) / 0.6)
            d.arc([x - 10, cy - 50 + 30 * ang, x + lw * 0.45, cy + 50 + 30 * ang], 90, 270, fill=RED + (240,), width=12)
            d.arc([x + lw * 0.55, cy - 50 - 30 * ang, x + lw + 10, cy + 50 - 30 * ang], 270, 90, fill=RED + (240,), width=12)
        else:
            d.rounded_rectangle([x + off, cy - 50, x + lw * 0.95 + off, cy + 50], 46, outline=INK + (240,), width=12)
    f.alpha_composite(lay)
    return B.grain(f, t, 6)


def s23(c, t):
    f = B.paper_bg(c, t, c.D, 23)
    quote_card(c, f, ost(c), t, c.at("«شريكًا", "«هاوبەشێکی", "«hevparekî", default=c.frac(0.2)) - 0.3,
               y=c.H * (0.18 if not c.vert else 0.22))
    years = [1991, 2014, 2019]
    keys = [("1991", "نەوەد", "nod"), ("داعش", "داعشدا", "DAIŞê"), ("2019", "نۆزدە", "nozdehan")]
    y = c.H * (0.70 if not c.vert else 0.68)
    x0, x1 = c.margin + 80, c.W - c.margin - 80
    d = ImageDraw.Draw(f)
    d.line([(x0, y), (x1, y)], fill=INK + (200,), width=4)
    for i, yr in enumerate(years):
        ki = ease((t - c.at(*keys[i], default=c.frac(0.5 + 0.15 * i))) / 0.4)
        if ki <= 0:
            continue
        u = (0.15 + 0.35 * i)
        x = x1 - (x1 - x0) * u if c.rtl else x0 + (x1 - x0) * u
        col = RED if i == 2 else GREEN
        d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=col + (255,))
        im = T(c.lang, str(yr), 44, INK, True)
        paste(f, im, x - im.width / 2, y + 26, ki)
    return f


def s24(c, t):
    f = photo_scene(c, t, A["A05_islamic_manuscript_library"], dark=0.5)
    px, col = side_layout(c)
    if not c.vert:
        cut_photo(c, f, t, "R19_said_nursi_portrait.jpg", 0.3, px, c.H * 0.42, h=560, rot=-2, prep=sepia,
                  frm="left" if c.rtl else "right")
        q = big_text(c, ost(c), 58, CREAM, int(c.W * 0.40))
        k = ease((t - c.frac(0.55)) / 0.8)
        if k > 0:
            xx = (col[0] + col[1]) / 2 - q.width / 2
            paste(f, kit.wipe(q, k, c.rtl), xx, c.H * 0.36)
    else:
        cut_photo(c, f, t, "R19_said_nursi_portrait.jpg", 0.3, c.W / 2, c.H * 0.33, h=560, rot=-2, prep=sepia,
                  frm="bottom")
        quote_card(c, f, ost(c), t, c.frac(0.55), y=c.H * 0.56, size=50)
    return f


def s25(c, t):
    f = photo_scene(c, t, "R21_tekke_courtyard.jpg", dark=0.55)
    px, col = side_layout(c)
    if not c.vert:
        cut_photo(c, f, t, "R20_sheikh_said_1925.jpg", 0.3, px, c.H * 0.44, h=600, rot=1.5, prep=sepia,
                  frm="left" if c.rtl else "right")
        strips(c, f, [ost(c)], t, c.frac(0.55), col=col, y=c.H * 0.40, size=52)
    else:
        cut_photo(c, f, t, "R20_sheikh_said_1925.jpg", 0.3, c.W / 2, c.H * 0.36, h=600, rot=1.5, prep=sepia,
                  frm="bottom")
        strips(c, f, [ost(c)], t, c.frac(0.55), y=c.H * 0.62, size=46)
    c.credit = ARCH
    return f


def s26(c, t):
    f = photo_scene(c, t, "R11_erbil_citadel.jpg", z=(1.0, 1.12), dark=0.62, c0=(0.5, 0.5), c1=(0.52, 0.47))
    items = split(ost(c), "·")
    strips(c, f, items, t, c.frac(0.3), y=c.top, size=52 if not c.vert else 46, stagger=c.D * 0.25,
           bgs=[SAFFRON, CREAM], colours=[INK, INK])
    return f


def verdict(c, t, bg=None, t_v=None, extra=None, text=None):
    text = text or ost(c)
    m = re.match(r"(.*?[؟?])\s*([✗◐✓])\s*(.*)", text)
    claim, mark, verd = (m.group(1), m.group(2), m.group(3)) if m else (text, "", "")
    f = bg if bg is not None else B.paper_bg(c, t, c.D, int(c.id[1:]))
    cy = c.H * (0.34 if not c.vert else 0.32)
    strip = c.get(("vclaim",), lambda: B.fit_w(B.strip_img(c.lang, claim, 84 if not c.vert else 68, INK, CREAM,
                                                            pad=(40, 22), rot=-1.5), c.W - 80))
    k = ease_out((t - 0.3) / 0.6)
    paste(f, strip, c.W / 2 - strip.width / 2 + (1 - k) * (200 if c.rtl else -200), cy - strip.height / 2, k)
    t_v = t_v if t_v is not None else c.frac(0.3)
    kv = clamp01((t - t_v) / 0.3)
    if kv > 0 and mark:
        colr = RED if mark == "✗" else SAFFRON
        st = c.get(("vstamp", mark), lambda: _stamp(c, mark, verd, colr))
        s = 1 + 0.7 * (1 - back_out(kv, 2.0))
        im = st.resize((int(st.width * s), int(st.height * s)), Image.BILINEAR)
        paste(f, im, c.W / 2 - im.width / 2, cy + strip.height / 2 + 40 + st.height / 2 - im.height / 2,
              clamp01(kv * 3))
    if extra:
        extra(f, t, t_v)
    return f


def s27(c, t):
    def ex(f, t, t_v):
        tn = c.at("93", "نەوەد", "nod", default=c.frac(0.45))
        if t > tn - 0.2:
            txt = counter_text("93%", clamp01((t - tn) / 1.0))
            im = T(c.lang, txt, 130, INK, True)
            paste(f, im, c.W / 2 - im.width / 2, c.H * (0.72 if not c.vert else 0.66), ease((t - tn) / 0.3))
            tg = T(c.lang, "2017", 44, (90, 84, 76), True)
            paste(f, tg, c.W / 2 - tg.width / 2, c.H * (0.72 if not c.vert else 0.66) - 50, ease((t - tn) / 0.3))
    return verdict(c, t, t_v=c.at("جزئيًا", "بەشێکی", "beşek", default=c.frac(0.2)), extra=ex)


def s28(c, t):
    return verdict(c, t, t_v=c.at("مزدوجة", "دوولایەنەیە", "dualî", default=c.frac(0.2)))


def s29(c, t):
    f = photo_scene(c, t, A["A06_calligraphy_desk"], dark=0.6)
    lines = c.ost
    verse = next((l for l in lines if "وجعلناكم" in l), lines[0])
    t_v = c.at("«وجعلناكم", "«وجعلناكم", "«Me", default=c.frac(0.5))
    k = ease((t - t_v + 0.2) / 1.2)
    if k > 0:
        im = c.get(("verse",), lambda: kit.line_img("ar", "rtl", verse, 96 if not c.vert else 64, (250, 236, 200), 0,
                                                    "Amiri-Regular.ttf")[0])
        im = B.fit_w(im, c.W - 140)
        paste(f, kit.wipe(im, k, True), c.W / 2 - im.width / 2, c.H * 0.30 - im.height / 2)
    rest = [l for l in lines if l is not verse]
    if rest:
        strips(c, f, rest, t, t_v + 1.2, y=c.H * 0.44, size=46 if not c.vert else 40)
    return f


def s30(c, t):
    return verdict(c, t, t_v=c.at("لكن", "بەڵام", "Lê", default=c.frac(0.5)))


def s31(c, t):
    return verdict(c, t, t_v=c.at("جزئيًا", "بەشێکی", "beşek", default=c.frac(0.3)))


def s32(c, t):
    f = B.paper_bg(c, t, c.D, 32)
    left, right = (split(ost(c), "←", "→") + [""])[:2]
    tn = c.at("40", "چل", "çil", default=c.frac(0.45))
    if t > tn - 0.3:
        txt = counter_text(left, clamp01((t - tn) / 1.4))
        im = B.strip_img(c.lang, txt, 96 if not c.vert else 76, CREAM, INK)
        paste(f, im, c.W / 2 - im.width / 2, c.H * 0.30, ease((t - tn + 0.3) / 0.4))
    if right:
        t2 = c.at("2025", "پێنج", "pêncan", default=c.frac(0.75))
        im = B.strip_img(c.lang, right, 66 if not c.vert else 54, INK, SAFFRON)
        paste(f, im, c.W / 2 - im.width / 2, c.H * 0.30 + 190, ease((t - t2) / 0.5))
    return B.grain(f, t, 6)


def s33(c, t):
    t_sw = c.at("صدر", "فەرمانی", "Biryarnameya", default=c.frac(0.4))
    a, b = "R26_damascus_dec2024.mp4", "R27_syria_jan2026_agreement.mp4"
    name, tc = (a, t + 2.0) if t < t_sw else (b, t - t_sw + 0.5)
    f = vert_bg_from_clip(c, name, tc) if c.vert else B.paper_bg(c, t, c.D, 33, tone=(30, 32, 36))
    box = framed_clip(c, f, name, t, tc)
    dt = t - t_sw
    if -0.18 < dt < 0.18:
        f = f.filter(ImageFilter.BoxBlur(int(2 + 30 * (1 - abs(dt) / 0.18))))
    c.credit = CREDITS[name]
    parts = split(ost(c), "|")
    tag(c, f, parts[0], t, 0.4, y=box[3] + 30)
    if len(parts) > 1 and t > t_sw:
        lower_strip(c, f, [parts[1]], t, t_sw + 0.6, y=c.top - 60 if not c.vert else box[1] - 140)
    return f


def s34(c, t):
    f = doors(c, t)
    c.illustration()
    headline(c, f, ost(c), t, c.at("حكاية", "چیرۆکی", "Çîroka", nth=0, default=c.frac(0.6)) - 0.2,
             86 if not c.vert else 68, c.H * (0.18 if not c.vert else 0.22), mode="wipe", dur=1.0)
    return f


def s35(c, t):
    f = B.paper_bg(c, t, c.D, 35)
    items = split(ost(c), "·")
    n = len(items)
    for i, it in enumerate(items):
        ki = ease_out((t - c.frac(0.1 + 0.18 * i)) / 0.5)
        if ki <= 0:
            continue
        if not c.vert:
            cw, ch = (c.W - 2 * c.margin - 3 * 30) / 4, 420
            idx = n - 1 - i if c.rtl else i
            x, y = c.margin + idx * (cw + 30), c.H * 0.26
        else:
            cw, ch = c.W - 160, 230
            x, y = 80, 330 + i * (ch + 30)
        card = c.get(("scn", i), lambda it=it, i=i, cw=cw, ch=ch: _scenario(c, it, int(cw), int(ch), i))
        paste(f, card, x - 20, y + (1 - ki) * 60, ki)
    return B.grain(f, t, 6)


def _scenario(c, text, w, h, i):
    m = re.match(r"\s*(\d)\s*(.*)", text)
    num, label = (m.group(1), m.group(2)) if m else (str(i + 1), text)
    im = B.card(w, h, (CREAM, CREAM, (238, 214, 206), (226, 232, 214))[i % 4], 16, INK)
    nn = T(c.lang, num, 110 if h > 300 else 90, SAFFRON, True)
    lb = B.stack(B.text_lines(c.lang, label, 46, w - 60, INK), 0.1, "center")
    if h > 300:
        im.alpha_composite(nn, (w // 2 - nn.width // 2, 30))
        im.alpha_composite(lb, (w // 2 - lb.width // 2, 60 + nn.height))
    else:
        if c.rtl:
            im.alpha_composite(nn, (w - nn.width - 30, h // 2 - nn.height // 2))
            im.alpha_composite(lb, (w - nn.width - 60 - lb.width, h // 2 - lb.height // 2))
        else:
            im.alpha_composite(nn, (30, h // 2 - nn.height // 2))
            im.alpha_composite(lb, (60 + nn.width, h // 2 - lb.height // 2))
    return B.shadowed(im, 8, (6, 8), 70)


def s36(c, t):
    f = photo_scene(c, t, "R12_qamishli_street.jpg", dark=0.4)
    f = f.filter(ImageFilter.GaussianBlur(3))
    lines = [l for l in c.ost if l]
    checks = [x.strip() for x in re.split(r"(?=✓)", lines[0]) if x.strip()] if lines else []
    items = checks + lines[1:]
    n = len(items)
    t0s = [c.frac(0.05 + 0.85 * i / n) for i in range(n)]
    strips(c, f, items, t, 0, y=c.top - (0 if c.vert else 20), size=50 if not c.vert else 46, times=t0s,
           bgs=[CREAM] * len(checks) + [SAFFRON] * (n - len(checks)), gap=6 if not c.vert else 14)
    return f


def s37(c, t):
    f = mountains(c, t, "golden")
    headline(c, f, ost(c), t, c.at("الجبال", "چیاکان", "çiya", nth=1, default=c.frac(0.4)) - 0.2,
             100 if not c.vert else 80, c.H * (0.22 if not c.vert else 0.28), mode="wipe", dur=1.0)
    return f


def s38(c, t):
    return text_behind(c, t, A["A08_group_walking_dusk"], ost(c), 0.8, 96 if not c.vert else 72,
                       z_bg=(1.0, 1.02), z_p=(1.0, 1.04), ty=0.30)


def s39(c, t):
    f = B.dark_bg(c, 39)
    lines = [l for l in c.ost if l]
    headline(c, f, lines[0], t, c.frac(0.0), 110 if not c.vert else 84, c.H * 0.36, mode="wipe", dur=1.0)
    if len(lines) > 1:
        tag(c, f, lines[1], t, c.frac(0.45), y=c.H * 0.52, x=None)
    return f


def end(c, t):
    f = B.dark_bg(c, 40)
    lg = c.get(("endlogo",), lambda: kit.logo(c.lang, True, 220 if not c.vert else 260, 1.0))
    k = ease_out(t / 0.8)
    cy = c.H * 0.38
    paste(f, lg, c.W / 2 - lg.width / 2, cy - lg.height / 2 + (1 - k) * 30, k)
    name = {"ar": "دوين - العربية", "ckb": "Dween - دوین", "kmr": "Dwîn - Kurmancî"}[c.lang]
    ch = c.get(("endch",), lambda: T(c.lang, name, 64, CREAM, True))
    paste(f, ch, c.W / 2 - ch.width / 2, cy + lg.height / 2 + 30, ease((t - 0.5) / 0.6))
    return f


SCENES = {f"S{i:02d}": globals()[f"s{i:02d}"] for i in range(1, 40)}
SCENES["END"] = end
