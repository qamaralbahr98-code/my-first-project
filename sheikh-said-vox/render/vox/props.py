"""Hand-drawn props in the paper style. No readable invented text appears on any of them."""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import kit
from .kit import CREAM, GOLD, INK, PAPER, RED


def _scribble(d, x0, y0, x1, y1, rng, colour, width=3, rows=1):
    """Abstract handwriting-like squiggle (unreadable on purpose)."""
    for r in range(rows):
        y = y0 + (y1 - y0) * (r + 0.5) / rows
        pts, x = [], x0
        while x < x1:
            pts.append((x, y + rng.uniform(-1, 1) * (y1 - y0) / rows * 0.32))
            x += rng.uniform(6, 14)
        d.line(pts, fill=colour, width=width, joint="curve")


def newspaper(w=900, h=1180, seed=0, tone=(232, 224, 204)):
    rng = np.random.default_rng(seed)
    pg = kit.paper(w, h, seed=60 + seed, tone=tone, vign=0.12).copy()
    d = ImageDraw.Draw(pg, "RGBA")
    m = 46
    d.rectangle([m, m, w - m, m + 6], fill=INK + (220,))
    _scribble(d, m + 60, m + 26, w - m - 60, m + 120, rng, INK + (230,), 7, 1)          # masthead
    d.rectangle([m, m + 140, w - m, m + 144], fill=INK + (220,))
    d.rectangle([m, m + 152, w - m, m + 154], fill=INK + (160,))
    hb = (m + 20, m + 185, w - m - 20, m + 300)                                          # headline block
    for r in range(2):
        y = hb[1] + 18 + r * 52
        d.rounded_rectangle([hb[0] + rng.uniform(0, 60), y, hb[2] - rng.uniform(0, 120), y + 30], 6, fill=INK + (215,))
    ph = (m + 20, m + 330, w // 2 + 40, m + 640)                                         # photo box
    d.rectangle(ph, fill=(150, 135, 110, 255))
    d.rectangle(ph, outline=INK + (180,), width=2)
    cols = 4
    cw = (w - 2 * m) / cols
    for c in range(cols):
        x0 = m + c * cw + 12
        x1 = m + (c + 1) * cw - 12
        y = m + 330 if x0 > ph[2] else m + 670
        while y < h - m - 20:
            if rng.random() < 0.07:
                y += 18
                continue
            d.line([(x0, y), (x1 - rng.uniform(0, 40 if rng.random() < 0.2 else 4), y)], fill=INK + (120,), width=4)
            y += 15
    return pg


def magazine(w=520, h=700, seed=0, tone=(214, 196, 160), accent=(120, 60, 40)):
    rng = np.random.default_rng(seed)
    pg = kit.paper(w, h, seed=80 + seed, tone=tone, vign=0.15).copy()
    d = ImageDraw.Draw(pg, "RGBA")
    d.rectangle([22, 22, w - 22, h - 22], outline=tuple(accent) + (230,), width=6)
    d.rectangle([34, 34, w - 34, h - 34], outline=tuple(accent) + (160,), width=2)
    for k in range(16):                                         # ornament band
        x = 50 + k * (w - 100) / 15
        d.ellipse([x - 7, 70 - 7, x + 7, 70 + 7], outline=tuple(accent) + (200,), width=2)
    _scribble(d, 80, 110, w - 80, 210, rng, INK + (230,), 8, 1)  # unreadable title
    d.ellipse([w / 2 - 120, 260, w / 2 + 120, 500], outline=tuple(accent) + (220,), width=4)
    d.ellipse([w / 2 - 60, 320, w / 2 + 60, 440], fill=tuple(accent) + (140,))
    _scribble(d, 90, 540, w - 90, 640, rng, INK + (150,), 3, 4)
    return pg


def ledger(w=1100, h=360, seed=0):
    rng = np.random.default_rng(seed)
    pg = kit.paper(w, h, seed=90 + seed, tone=(228, 218, 192), vign=0.1).copy()
    d = ImageDraw.Draw(pg, "RGBA")
    for y in range(60, h - 20, 34):
        d.line([(30, y), (w - 30, y)], fill=(120, 140, 170, 140), width=2)
    d.line([(w * 0.72, 30), (w * 0.72, h - 20)], fill=RED + (150,), width=3)
    for y in range(66, h - 30, 34):
        _scribble(d, 50, y - 22, w * 0.62, y - 6, rng, INK + (150,), 3, 1)
        d.rectangle([w * 0.76, y - 22, w * 0.76 + rng.uniform(80, 200), y - 8], fill=INK + (140,))
    return pg


def stamp(w=420, h=200, colour=RED, seed=0, mark=True):
    """Rubber-stamp outline with an abstract mark inside (no readable text)."""
    rng = np.random.default_rng(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([8, 8, w - 8, h - 8], 18, outline=tuple(colour) + (235,), width=10)
    d.rounded_rectangle([26, 26, w - 26, h - 26], 12, outline=tuple(colour) + (200,), width=4)
    if mark:
        _scribble(d, 60, 60, w - 60, h - 60, rng, tuple(colour) + (230,), 9, 1)
    a = np.asarray(im).copy()                                   # worn ink
    n = rng.random(a.shape[:2])
    a[..., 3] = (a[..., 3] * np.where(n < 0.18, 0.35, 1.0)).astype(np.uint8)
    return Image.fromarray(a, "RGBA")


def padlock(size=120, colour=INK):
    im = Image.new("RGBA", (size, int(size * 1.25)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    s = size
    d.arc([s * 0.22, s * 0.02, s * 0.78, s * 0.62], 180, 360, fill=tuple(colour) + (255,), width=int(s * 0.1))
    d.line([(s * 0.27, s * 0.32), (s * 0.27, s * 0.55)], fill=tuple(colour) + (255,), width=int(s * 0.1))
    d.line([(s * 0.73, s * 0.32), (s * 0.73, s * 0.55)], fill=tuple(colour) + (255,), width=int(s * 0.1))
    d.rounded_rectangle([s * 0.08, s * 0.5, s * 0.92, s * 1.2], int(s * 0.1), fill=tuple(colour) + (255,))
    d.ellipse([s * 0.43, s * 0.72, s * 0.57, s * 0.86], fill=CREAM + (255,))
    d.rectangle([s * 0.475, s * 0.8, s * 0.525, s * 1.0], fill=CREAM + (255,))
    return im


def envelope(w=200, h=130):
    im = Image.new("RGBA", (w + 16, h + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([10, 12, w + 10, h + 12], fill=(0, 0, 0, 80))
    d.rectangle([4, 4, w + 4, h + 4], fill=CREAM + (255,), outline=INK + (200,), width=3)
    d.line([(4, 4), (w / 2 + 4, h * 0.6), (w + 4, 4)], fill=INK + (200,), width=3)
    d.ellipse([w / 2 - 16, h * 0.6 - 14, w / 2 + 22, h * 0.6 + 22], fill=RED + (255,))
    return im.filter(ImageFilter.GaussianBlur(0.4))


def flame(t, size=90):
    """Small flickering flame graphic (Newroz / ignition)."""
    im = Image.new("RGBA", (size, int(size * 1.5)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, base = size / 2, size * 1.45
    for k, (col, sc) in enumerate((((214, 120, 40), 1.0), ((240, 180, 70), 0.68), ((255, 236, 170), 0.38))):
        f = 1 + 0.08 * math.sin(t * 17 + k) + 0.05 * math.sin(t * 29 + 2 * k)
        hgt = size * 1.3 * sc * f
        wid = size * 0.42 * sc
        pts = []
        for i in range(25):
            a = i / 24
            y = base - hgt * a
            x = wid * math.sin(math.pi * (1 - a) ** 0.8) * (1 - a ** 3) * (1.0 + 0.1 * math.sin(t * 11 + a * 6))
            pts.append((cx + x + 3 * math.sin(t * 9 + a * 4) * a, y))
        pts += [(2 * cx - x, y) for (x, y) in reversed(pts)]
        d.polygon(pts, fill=col + (235,))
    return im.filter(ImageFilter.GaussianBlur(1.0))


def tent(size=60, colour=(235, 228, 212)):
    im = Image.new("RGBA", (size, int(size * 0.75)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(2, size * 0.73), (size / 2, 3), (size - 2, size * 0.73)], fill=tuple(colour) + (255,),
              outline=INK + (220,))
    d.polygon([(size * 0.42, size * 0.73), (size / 2, size * 0.36), (size * 0.58, size * 0.73)], fill=INK + (200,))
    return im


def skyline(w=2200, h=700, seed=4):
    """Paper cut-out skyline of domes and minarets (generic, drawn)."""
    rng = np.random.default_rng(seed)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layers = [((202, 186, 156), 0.55, 0), ((176, 156, 122), 0.75, 1), ((120, 98, 72), 1.0, 2)]
    for col, hs, k in layers:
        d = ImageDraw.Draw(im)
        base = h - 10 - k * 6
        x = -rng.uniform(0, 120)
        while x < w:
            bw = rng.uniform(140, 300)
            bh = h * hs * rng.uniform(0.18, 0.32)
            d.rectangle([x, base - bh, x + bw, base], fill=col + (255,))
            r = rng.random()
            if r < 0.5:                                         # dome on a drum
                dr = bw * rng.uniform(0.28, 0.42)
                cx = x + bw / 2
                d.rectangle([cx - dr * 0.9, base - bh - dr * 0.25, cx + dr * 0.9, base - bh], fill=col + (255,))
                d.pieslice([cx - dr, base - bh - dr * 1.25, cx + dr, base - bh + dr * 0.75], 180, 360, fill=col + (255,))
                d.line([(cx, base - bh - dr * 1.2), (cx, base - bh - dr * 1.55)], fill=col + (255,), width=5)
                d.ellipse([cx - 7, base - bh - dr * 1.62, cx + 7, base - bh - dr * 1.48], fill=col + (255,))
            elif r < 0.78:                                      # minaret
                mx = x + bw * rng.uniform(0.2, 0.8)
                mh = h * hs * rng.uniform(0.55, 0.85)
                mw = rng.uniform(26, 40)
                d.rectangle([mx - mw / 2, base - mh, mx + mw / 2, base], fill=col + (255,))
                d.rectangle([mx - mw * 0.85, base - mh * 0.72, mx + mw * 0.85, base - mh * 0.68], fill=col + (255,))
                d.polygon([(mx - mw / 2, base - mh), (mx + mw / 2, base - mh), (mx, base - mh - mw * 1.6)], fill=col + (255,))
            for a in range(int(bw // 60)):                      # arches
                ax = x + 20 + a * 60
                if ax + 34 < x + bw:
                    d.rectangle([ax, base - bh * 0.55, ax + 30, base], fill=tuple(int(v * 0.8) for v in col) + (255,))
                    d.pieslice([ax, base - bh * 0.55 - 15, ax + 30, base - bh * 0.55 + 15], 180, 360,
                               fill=tuple(int(v * 0.8) for v in col) + (255,))
            x += bw * rng.uniform(0.7, 1.05)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(im.getchannel("A").point(lambda v: int(v * 0.35)).filter(ImageFilter.GaussianBlur(6)))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 0))
    out.alpha_composite(im)
    return out


def wheat_field(w=2300, h=1300, seed=2):
    rng = np.random.default_rng(seed)
    im = kit.paper(w, h, seed=70, tone=(236, 222, 186), vign=0.1).copy()
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, 0, w, h * 0.36], fill=(214, 226, 230, 180))           # pale sky
    for row in range(26):
        y = h * 0.38 + row * (h * 0.62 / 26)
        sc = 0.45 + row / 26
        x = rng.uniform(0, 30)
        while x < w:
            hgt = rng.uniform(50, 80) * sc
            col = (196 + int(rng.uniform(-20, 20)), 154 + int(rng.uniform(-20, 20)), 70, 235)
            d.line([(x, y), (x + rng.uniform(-6, 6), y - hgt)], fill=col, width=max(1, int(2 * sc)))
            d.ellipse([x - 3 * sc, y - hgt - 10 * sc, x + 3 * sc, y - hgt + 6 * sc], fill=col)
            x += rng.uniform(12, 22) * sc
    return im


def city_plan(w=1500, h=1100):
    """Schematic walled city (Amed): ring of walls with towers; the south gate (Mardin Gate) is returned."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy, rx, ry = w / 2, h / 2, w * 0.36, h * 0.38
    pts = []
    rng = np.random.default_rng(1)
    for k in range(64):
        a = 2 * math.pi * k / 64
        f = 1 + 0.06 * math.sin(3 * a + 0.5) + 0.03 * math.sin(7 * a)
        pts.append((cx + rx * f * math.cos(a), cy + ry * f * math.sin(a)))
    d.polygon(pts, fill=(226, 214, 190, 255))
    for i in range(140):                                         # streets / blocks
        x, y = rng.uniform(cx - rx * 0.8, cx + rx * 0.8), rng.uniform(cy - ry * 0.8, cy + ry * 0.8)
        if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 0.7:
            s = rng.uniform(14, 34)
            d.rectangle([x, y, x + s, y + s * rng.uniform(0.6, 1.2)], fill=(196, 182, 156, 255))
    d.line(pts + pts[:1], fill=(40, 36, 34, 255), width=16)
    for k in range(0, 64, 4):
        x, y = pts[k]
        d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(40, 36, 34, 255))
    gate = pts[16]                                               # angle pi/2 -> south
    return im, gate, (cx, cy)
