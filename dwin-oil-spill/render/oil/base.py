"""Drawing base for the oil-spill explainer: palette, size-aware context (16:9 and 9:16), text with glyph fallback,
paper strips, photos with camera moves, cut-outs, Natural Earth maps, source lines.

Reuses the Vox kit of the Sheikh Said project (paper, cut-outs, ink, shaping with libraqm).
"""
import json
import math
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PROJ = Path(__file__).resolve().parents[2]            # dwin-oil-spill/
REPO = PROJ.parent
sys.path.insert(0, str(REPO / "sheikh-said-vox" / "render"))
from vox import kit  # noqa: E402
from vox.kit import clamp01, ease, ease_out, back_out, paste  # noqa: E402,F401

IMG = PROJ / "assets" / "images"
DATA = PROJ / "render" / "data" / "gulf_10m.json"

PAPER = (242, 238, 230)        # #F2EEE6
INK = (27, 27, 27)             # #1B1B1B
OIL = (11, 11, 11)             # #0B0B0B
SEA = (46, 111, 142)           # #2E6F8E
GOLD = (201, 164, 92)          # #C9A45C
RED = (179, 38, 30)            # #B3261E
CREAM = (250, 247, 240)
LAND = (236, 230, 217)
GREY = (110, 106, 100)

SOURCES = {
    "ministry": ("وەزارەتی ژینگەی ئیمارات", "Wezareta Jîngehê ya MEY"),
    "reuters": ("ڕۆیتەرز", "Reuters"),
    "copernicus": ("کۆپەرنیکۆس", "Copernicus"),
}
SRC_WORD = {"ckb": "سەرچاوە", "kmr": "Çavkanî"}


# ------------------------------------------------------------------ context
_MISSING = set()


class Ctx:
    def __init__(self, sc, lang, size, cache, txt):
        self.sc, self.lang = sc, lang
        self.W, self.H = size
        self.vert = self.H > self.W
        self.L = kit.Lang(lang, "rtl" if lang == "ckb" else "ltr")
        self.id = sc["id"]
        self.D = sc["dur"]
        self.ost = sc["ost"]
        self.words = sc["words"]
        self.cache = cache
        self.labels = []
        self.txt = txt                   # title, illustration label, end-card name
        a = sc["audio"]
        self.a0 = a[0]["start"] if a else 0.3
        self.a1 = (a[0]["start"] + a[0]["dur"]) if a else self.D

    def get(self, key, fn):
        k = (self.id, self.W, key)
        if k not in self.cache:
            self.cache[k] = fn()
        return self.cache[k]

    def mx(self, x):
        return x if self.L.rtl else self.W - x

    def w(self, i):
        """Start time of word i of the narration (negative i counts from the end)."""
        if not self.words:
            return self.a0
        return self.words[max(-len(self.words), min(i, len(self.words) - 1))]["s"]

    def find(self, part, nth=0, default=None):
        """Start time of the nth narration word containing `part`."""
        k = 0
        for w in self.words:
            if part in w["text"]:
                if k == nth:
                    return w["s"]
                k += 1
        if (self.id, part) not in _MISSING:
            _MISSING.add((self.id, part))
            print(f"warning: {self.lang} {self.id}: no word with {part!r}", file=sys.stderr)
        return self.a0 if default is None else default

    def at(self, ckb, kmr, nth=0):
        return self.find(ckb if self.lang == "ckb" else kmr, nth)

    def col_start(self, width):
        """Column of `width` on the reading-start side (16:9)."""
        return (self.W - self.margin - width, self.W - self.margin) if self.L.rtl else (self.margin, self.margin + width)

    def col_end(self, width):
        return (self.margin, self.margin + width) if self.L.rtl else (self.W - self.margin - width, self.W - self.margin)

    def illustration(self):
        self.labels.append("illustration")

    # layout helpers: the text column of the frame
    @property
    def margin(self):
        return 70 if self.vert else 110

    @property
    def top(self):
        return 420 if self.vert else 140

    @property
    def safe_bottom(self):
        return 1630 if self.vert else self.H - 60


# ------------------------------------------------------------------ text
def font_name(lang, bold=True):
    if lang == "ckb":
        return "Speda.ttf"
    return "Montserrat-Bold.ttf" if bold else "Montserrat-Regular.ttf"


@lru_cache(maxsize=8)
def _cmap(name):
    from fontTools.ttLib import TTFont
    return set(TTFont(str(REPO / "fonts" / name)).getBestCmap())


@lru_cache(maxsize=4096)
def T(lang, text, size, colour, bold=True, stroke=0):
    """One shaped line. Characters the language font lacks (↑ ≈ ² in Speda) are set in Montserrat Bold."""
    fname = font_name(lang, bold)
    ldir = "rtl" if lang == "ckb" else "ltr"
    cm = _cmap(fname)
    runs = []
    for ch in text:
        ok = ord(ch) in cm or ch == " "
        if runs and runs[-1][1] == ok:
            runs[-1][0].append(ch)
        else:
            runs.append(([ch], ok))
    if all(ok for _, ok in runs):
        return kit.line_img(lang, ldir, text, size, tuple(colour), stroke, fname)[0]
    sp = size * 0.26
    imgs = []                     # (image, space before in logical order, space after)
    for chars, ok in runs:
        s = "".join(chars)
        lead, trail = len(s) - len(s.lstrip(" ")), len(s) - len(s.rstrip(" "))
        if not s.strip():
            imgs.append((None, lead, 0))
            continue
        f = fname if ok else "Montserrat-Bold.ttf"
        # symbols render at the size of the Kurdish face (Montserrat draws large: kit scales kmr by 0.86)
        im = kit.line_img(lang if ok else "kmr", ldir if ok else "ltr", s.strip(), size, tuple(colour), stroke, f)[0]
        imgs.append((im, lead, trail))
    order = imgs[::-1] if ldir == "rtl" else imgs
    h = max(i.height for i, _, _ in order if i is not None)
    pieces, x = [], 0.0
    for k, (im, lead, trail) in enumerate(order):
        before, after = (trail, lead) if ldir == "rtl" else (lead, trail)
        x += before * sp
        if im is not None:
            pieces.append((im, x))
            x += im.width - 12
        x += after * sp
    out = Image.new("RGBA", (max(1, int(x + 12)), h), (0, 0, 0, 0))
    for im, px in pieces:
        out.alpha_composite(im, (int(px), (h - im.height) // 2))
    return out


def text_w(c, text, size, bold=True):
    return T(c.lang, text, size, INK, bold).width


def strip_img(lang, text, size, colour=INK, bg=CREAM, pad=(26, 10), rot=0.0, bold=True):
    img = T(lang, text, size, tuple(colour), bold)
    w, h = img.width + 2 * pad[0], int(img.height * 0.82) + 2 * pad[1]
    out = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([16, 18, 12 + w + 4, 12 + h + 6], fill=(0, 0, 0, 80))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
    ImageDraw.Draw(out).rectangle([12, 12, 12 + w, 12 + h], fill=tuple(bg) + (255,))
    out.alpha_composite(img, (12 + pad[0], int(12 + pad[1] - img.height * 0.09)))
    if rot:
        out = out.rotate(rot, resample=Image.BICUBIC, expand=True)
    return out


def strips(c, f, lines, t, t0, col=None, y=None, size=54, gap=-2, stagger=0.35, colours=None, bgs=None, times=None,
           align=None, out=None):
    """Paper-strip labels stacked downwards. In 16:9 they sit on the reading-start edge of the column `col` = (x0, x1)
    (default: the frame minus margins) and slide in from that side; in 9:16 they are centred.
    `times` overrides the start times; `out` = time the stack fades away."""
    if c.vert and align is None:
        align = "center"
    x0, x1 = col or (c.margin, c.W - c.margin)
    y = c.top if y is None else y
    boxes = []
    fade_out = 1.0 if out is None else clamp01((out - t) / 0.35)
    for i, text in enumerate(lines):
        colr = colours[i] if colours else INK
        bg = bgs[i] if bgs else CREAM
        s = c.get(("strip", text, size, colr, bg), lambda: strip_img(c.lang, text, size, colr, bg))
        if s.width > (x1 - x0) + 24:
            sc = ((x1 - x0) + 24) / s.width
            s = c.get(("strip_fit", text, size, colr, bg, x1 - x0),
                      lambda: s.resize((int(s.width * sc), int(s.height * sc)), Image.LANCZOS))
        t_i = times[i] if times else t0 + i * stagger
        k = ease_out((t - t_i) / 0.45)
        if k > 0 and fade_out > 0:
            if align == "center":
                sx = (x0 + x1) / 2 - s.width / 2
                sy = y + (1 - k) * 30
            else:
                off = (1 - k) * 160
                sx = (x1 + 12 - s.width + off) if c.L.rtl else (x0 - 12 - off)
                sy = y
            paste(f, s, sx, sy, clamp01(k * 1.6) * fade_out)
            boxes.append((sx, sy, sx + s.width, sy + s.height))
        y += s.height + gap
    return boxes, y


def source_line(c, f, keys, t, t0, x=None, y=None, extra=None, dark=False, right=None):
    """Small source credit, e.g. «سەرچاوە: ڕۆیتەرز · Al Jazeera». 16:9: bottom, on the reading-start side unless
    `right` says which edge (True = right margin, False = left margin); 9:16: centred above the subtitles."""
    li = 0 if c.lang == "ckb" else 1
    names = [SOURCES[k][li] if k in SOURCES else k for k in keys]
    text = f"{SRC_WORD[c.lang]}: " + " · ".join(names)
    size = 26 if c.vert else 22
    col = (235, 230, 220) if dark else (70, 66, 60)
    im = c.get(("src", text, dark), lambda: T(c.lang, text, size, col, False))
    a = clamp01((t - t0) / 0.5)
    if a <= 0:
        return
    if c.vert:
        xx = c.W / 2 - im.width / 2
        yy = 1385 if y is None else y
    else:
        r = c.L.rtl if right is None else right
        if x is None:
            xx = (c.W - c.margin - im.width) if r else c.margin
        else:
            xx = x - im.width if r else x
        yy = c.H - 128 if y is None else y
    pad = c.get(("srcpad", im.width, im.height, dark), lambda: _pill(im.width + 16, int(im.height * 0.78),
                                                                     (0, 0, 0, 120) if dark else PAPER + (205,)))
    paste(f, pad, xx - 8, yy + im.height * 0.11, a)
    paste(f, im, xx, yy, a)


def _pill(w, h, fill):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w - 1, h - 1], h // 3, fill=fill)
    return im


def big_number(c, text, size, colour=INK, stroke=3):
    return c.get(("num", text, size, colour), lambda: T(c.lang, text, size, colour, True, stroke))


# ------------------------------------------------------------------ images
@lru_cache(maxsize=32)
def load(name):
    return Image.open(IMG / name).convert("RGB")


class Cam:
    def __init__(self, iw, ih, u, z0, z1, c0, c1, out):
        z = z0 + (z1 - z0) * u
        cx = c0[0] + (c1[0] - c0[0]) * u
        cy = c0[1] + (c1[1] - c0[1]) * u
        s = max(out[0] / iw, out[1] / ih) * z
        self.vw, self.vh = out[0] / s, out[1] / s
        self.x0 = min(max(0, cx * iw - self.vw / 2), iw - self.vw)
        self.y0 = min(max(0, cy * ih - self.vh / 2), ih - self.vh)
        self.s, self.out = s, out

    def view(self, im):
        return im.resize(self.out, Image.BILINEAR, box=(self.x0, self.y0, self.x0 + self.vw, self.y0 + self.vh))

    def pt(self, x, y):
        return ((x - self.x0) * self.s, (y - self.y0) * self.s)


def prog(t, D):
    u = clamp01(t / max(D, 0.01))
    return ease(u) * 0.6 + u * 0.4


def photo(c, key, name, t, D, z=(1.0, 1.05), c0=(0.5, 0.5), c1=(0.5, 0.5), prep=None, label=True):
    """Full-bleed photo with a slow push (2.5D)."""
    def build():
        im = load(name)
        if prep:
            im = prep(im)
        s = max(c.W * 1.2 / im.width, c.H * 1.2 / im.height)
        if s > 1:
            im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        return im
    im = c.get(("photo", key, name), build)
    cam = Cam(im.width, im.height, prog(t, D), z[0], z[1], c0, c1, (c.W, c.H))
    if label:
        c.illustration()
    return cam.view(im).convert("RGBA"), cam


def paper_bg(c, t, D, seed=1, drift=16):
    p = c.get(("paper", seed), lambda: kit.paper(c.W + 60, c.H + 40, seed=seed, tone=PAPER, vign=0.12))
    u = prog(t, D)
    x = 30 + drift * (u - 0.5) * (1 if c.L.rtl else -1)
    return p.crop((int(x), 20, int(x) + c.W, 20 + c.H)).copy()


def cut(c, key, name, w=None, h=None, torn=False, border=14, rot=0.0, seed=0, prep=None, crop=None):
    def build():
        im = load(name)
        if crop:
            im = im.crop(tuple(int(v * (im.width if i % 2 == 0 else im.height)) for i, v in enumerate(crop)))
        if prep:
            im = prep(im)
        co = kit.cutout(kit.fit(im, w, h), torn=torn, border=border, seed=seed)
        return co.rotate(rot, resample=Image.BICUBIC, expand=True) if rot else co
    return c.get(("cut", key, name, w, h, rot), build)


def place(f, im, cx, cy, t, t0, frm=None, scale=(1.0, 1.0), D=None, a=1.0):
    """Paste an image centred at (cx, cy) with an entrance (slide in from a side, slight overshoot)."""
    if t < t0:
        return None
    k = back_out((t - t0) / 0.55, 1.2)
    if D:
        u = prog(t, D)
        s = scale[0] + (scale[1] - scale[0]) * u
        if abs(s - 1) > 0.003:
            im = im.resize((int(im.width * s), int(im.height * s)), Image.BILINEAR)
    dx = dy = 0
    if frm == "left":
        dx = -(1 - k) * 900
    elif frm == "right":
        dx = (1 - k) * 900
    elif frm == "bottom":
        dy = (1 - k) * 800
    elif frm == "top":
        dy = -(1 - k) * 800
    x, y = cx - im.width / 2 + dx, cy - im.height / 2 + dy
    paste(f, im, x, y, a * (clamp01(k * 2) if frm is None else 1))
    return (x, y, x + im.width, y + im.height)


# ------------------------------------------------------------------ maps (Natural Earth 10m)
PLACES = {  # (lat, lon)
    "uaq": (25.565, 55.555), "ajman": (25.405, 55.513), "sharjah": (25.346, 55.421), "hamriyah": (25.468, 55.517),
    "rak": (25.790, 55.943), "dubai": (25.205, 55.271), "hormuz": (26.57, 56.33), "iran": (27.45, 55.2),
    "uae": (24.35, 54.85),
}
# tanker ~25 km off Umm Al Quwain, to the north-west (offshore normal of a coast running SW-NE)
TANKER = (25.732, 55.388)
SLICK_C = (25.684, 55.329)       # slick centre, ~8 km south-west of the tanker along the coast
# shipping lanes (lat, lon): through the strait, and the branch to the UAE ports
LANE_MAIN = [(26.2, 54.8), (26.45, 55.6), (26.5, 56.28), (26.45, 56.55), (26.2, 56.7), (25.6, 56.9), (24.9, 57.5)]
LANE_UAE = [(26.45, 55.6), (26.0, 55.5), (25.4, 55.1), (25.05, 54.95)]
# illustrative attack markers (not exact incident positions; the scene carries the illustration label)
PULSES = [(26.35, 55.25), (26.52, 56.05), (26.38, 56.62), (25.95, 56.82), (25.3, 57.05), (26.1, 55.0), (25.7, 55.25),
          (26.55, 55.7)]


class MapView:
    def __init__(self, lon_c, lat_c, lon_span, w, h):
        self.lon_c, self.lat_c, self.w, self.h = lon_c, lat_c, w, h
        self.kx = w / lon_span
        self.ky = self.kx / math.cos(math.radians(lat_c))

    def xy(self, lat, lon):
        return (self.w / 2 + (lon - self.lon_c) * self.kx, self.h / 2 - (lat - self.lat_c) * self.ky)

    def place(self, name):
        return self.xy(*PLACES[name])

    def km(self):
        """Pixels per kilometre (east-west)."""
        return self.kx / (111.32 * math.cos(math.radians(self.lat_c)))


@lru_cache(maxsize=1)
def gulf():
    return json.loads(DATA.read_text())


def base_map(v, seed=3):
    w, h = v.w, v.h
    img = Image.new("RGBA", (w, h), SEA + (255,))
    # light sea texture
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (h // 8 + 1, w // 8 + 1)).astype(np.float32)
    n = np.asarray(Image.fromarray((n * 30 + 128).clip(0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC),
                   np.float32) - 128
    arr = np.asarray(img).astype(np.float32)
    arr[..., :3] += n[..., None] * 0.08
    img = Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")
    mask = Image.new("L", (w, h), 0)
    dm = ImageDraw.Draw(mask)
    for ring in gulf()["land"]:
        pts = [v.xy(lat, lon) for lon, lat in ring]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        if max(xs) < -50 or min(xs) > w + 50 or max(ys) < -50 or min(ys) > h + 50:
            continue
        dm.polygon(pts, fill=255)
    if w * h > 5e6:
        land = kit.paper(w // 2, h // 2, seed=seed + 5, tone=LAND, vign=0.0).resize((w, h), Image.BICUBIC)
    else:
        land = kit.paper(w, h, seed=seed + 5, tone=LAND, vign=0.0)
    img.paste(land, (0, 0), mask)
    edge = mask.filter(ImageFilter.FIND_EDGES).point(lambda q: 200 if q > 40 else 0).filter(ImageFilter.GaussianBlur(0.8))
    coast = Image.new("RGBA", (w, h), (20, 50, 66, 0))
    coast.putalpha(edge)
    img.alpha_composite(coast)
    d = ImageDraw.Draw(img, "RGBA")
    for line in gulf()["borders"]:
        pts = [v.xy(lat, lon) for lon, lat in line]
        _dashed(d, pts, 10, 8, (90, 84, 76, 150), 2)
    return img


def _dashed(d, pts, dash, gap, fill, width):
    acc, on = 0.0, True
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        pos = 0.0
        while pos < seg:
            step = min((dash if on else gap) - acc, seg - pos)
            if on:
                a, b = pos / seg, (pos + step) / seg
                d.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)],
                       fill=fill, width=width)
            pos += step
            acc += step
            if acc >= (dash if on else gap) - 1e-6:
                acc, on = 0.0, not on


def dashed_line(d, a, b, p, colour=CREAM, width=4, dash=16, gap=10):
    if p <= 0:
        return
    e = (a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p)
    _dashed(d, [a, e], dash, gap, tuple(colour) + (255,), width)


def map_args(c, lon0, lat0, span, X=None, Y=None):
    """View (lon_c, lat_c, span) that puts (lon0, lat0) at screen point (X, Y) at zoom 1 (default: frame centre)."""
    X = c.W / 2 if X is None else X
    Y = c.H / 2 if Y is None else Y
    kx = c.W / span
    ky = kx / math.cos(math.radians(lat0))
    return (lon0 - (X - c.W / 2) / kx, lat0 + (Y - c.H / 2) / ky, span)


_MAPS = {}


def map_image(c, args, scale=1.25):
    """Base map (shared by all scenes and kept for the whole render)."""
    k = (c.W, c.H, tuple(round(a, 5) for a in args), scale)
    if k not in _MAPS:
        w, h = int(c.W * scale), int(c.H * scale)
        v = MapView(*args, w, h)
        _MAPS[k] = (v, base_map(v))
    return _MAPS[k]


def map_shot(c, args, t, D, z=(1.0, 1.0), c0=(0.5, 0.5), c1=(0.5, 0.5), u=None, scale=1.25):
    """args = (lon_c, lat_c, lon_span) for this orientation; the map image is `scale` x the frame."""
    v, m = map_image(c, args, scale)
    cam = Cam(m.width, m.height, prog(t, D) if u is None else u, z[0], z[1], c0, c1, (c.W, c.H))
    return cam.view(m).convert("RGBA"), cam, v


def scr(cam, v, name_or_latlon):
    """Screen position of a place (name in PLACES or (lat, lon))."""
    ll = PLACES[name_or_latlon] if isinstance(name_or_latlon, str) else name_or_latlon
    return cam.pt(*v.xy(*ll))


def map_label(c, f, text, x, y, t, t0, size=34, colour=INK, anchor="above", halo=PAPER):
    if not text:
        return
    def build():
        fg = T(c.lang, text, size, tuple(colour), True)
        hl = T(c.lang, text, size, tuple(halo), True, 6)
        out = Image.new("RGBA", hl.size, (0, 0, 0, 0))
        out.alpha_composite(hl.filter(ImageFilter.GaussianBlur(1.5)))
        out.alpha_composite(fg, ((hl.width - fg.width) // 2, (hl.height - fg.height) // 2))
        return out
    im = c.get(("ml", text, size, colour, halo), build)
    vis = kit.wipe(im, clamp01((t - t0) / 0.5), c.L.rtl)
    if vis is None:
        return
    if anchor == "above":
        paste(f, vis, x - im.width / 2, y - im.height - 14)
    elif anchor == "below":
        paste(f, vis, x - im.width / 2, y + 8)
    elif anchor == "left":
        paste(f, vis, x - im.width - 18, y - im.height / 2)
    else:
        paste(f, vis, x + 18, y - im.height / 2)


def dot(d, x, y, r=7, colour=INK, a=1.0):
    d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(colour) + (int(255 * a),))


def slick_poly(v, cam, growth, seed=6, center=None):
    """Slick of ~160 km^2 (x growth^2): an irregular, slightly bent band ~30 km long along the coast (bearing 48 deg),
    in screen points. Point 0 and point 36 are the two ends of the long axis."""
    rng = np.random.default_rng(seed)
    lat0, lon0 = center or SLICK_C
    a_km, b_km = 15.0 * growth, 3.4 * growth
    th = math.radians(48)                       # long axis direction (from north, clockwise)
    harm = rng.normal(0, 1, 6)
    km = []
    for k in range(72):
        ang = 2 * math.pi * k / 72
        s = math.cos(ang)                                   # position along the long axis, -1..1
        width = 1 + 0.2 * math.sin(3.1 * s + harm[0]) + 0.1 * math.sin(7.3 * s + harm[1]) \
            + 0.05 * math.sin(13 * s + harm[3]) * math.sin(ang)
        bend = 0.45 * b_km * math.sin(2.2 * s + harm[2])    # the slick bends a little (wind, current)
        ex = a_km * s * (1 + 0.03 * math.sin(5 * ang + harm[4]))
        ey = b_km * math.sin(ang) * width
        km.append((ex, ey, bend))
    # keep the area exact: pi * a * b (= 160 km^2 at full size)
    xs = [e[0] for e in km]
    ys = [e[1] for e in km]
    area = abs(sum(xs[i] * ys[i - 1] - xs[i - 1] * ys[i] for i in range(len(xs)))) / 2
    kk = (math.pi * a_km * b_km / area) if area > 1e-9 else 1.0
    pts = []
    for ex, ey, bend in km:
        ey = ey * kk + bend
        north = ex * math.cos(th) - ey * math.sin(th)
        east = ex * math.sin(th) + ey * math.cos(th)
        lat = lat0 + north / 111.0
        lon = lon0 + east / (111.32 * math.cos(math.radians(lat0)))
        pts.append(cam.pt(*v.xy(lat, lon)))
    return pts


# ------------------------------------------------------------------ small graphics
def tanker_icon(w=60, colour=INK, mark=None):
    """Side view of a crude tanker (bow to the right), drawn at 4x and reduced. `mark`: colour of a damage dot
    on the hull."""
    S = 4
    W_, H_ = w * S, int(w * 0.36) * S
    im = Image.new("RGBA", (W_, H_), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = tuple(colour) + (255,)
    deck, keel = H_ * 0.46, H_ * 0.97
    d.polygon([(W_ * 0.01, deck), (W_ * 0.90, deck), (W_ * 0.995, H_ * 0.40), (W_ * 0.93, keel), (W_ * 0.045, keel)],
              fill=col)
    d.rectangle([W_ * 0.05, H_ * 0.12, W_ * 0.19, deck], fill=col)                    # bridge
    d.rectangle([W_ * 0.075, H_ * 0.0, W_ * 0.115, H_ * 0.14], fill=col)              # funnel
    d.rectangle([W_ * 0.22, deck - H_ * 0.07, W_ * 0.86, deck], fill=col)             # deck pipes
    for k in range(5):                                                                 # manifold posts
        x = W_ * (0.32 + k * 0.11)
        d.rectangle([x, deck - H_ * 0.16, x + W_ * 0.012, deck], fill=col)
    if mark:
        r = H_ * 0.2
        cx, cy = W_ * 0.55, (deck + keel) / 2
        d.ellipse([cx - r - S * 2, cy - r - S * 2, cx + r + S * 2, cy + r + S * 2], fill=CREAM + (255,))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tuple(mark) + (255,))
    return im.resize((w, int(w * 0.36)), Image.LANCZOS)


def pitch_icon(w=40):
    h = int(w * 0.65)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], fill=(64, 130, 72, 255), outline=(240, 240, 240, 255), width=2)
    d.line([(w / 2, 0), (w / 2, h)], fill=(240, 240, 240, 255), width=2)
    d.ellipse([w / 2 - h * 0.18, h / 2 - h * 0.18, w / 2 + h * 0.18, h / 2 + h * 0.18], outline=(240, 240, 240, 255), width=2)
    return im


def closed_badge(size=64):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([2, 2, size - 2, size - 2], fill=RED + (255,), outline=CREAM + (255,), width=4)
    d.rectangle([size * 0.22, size * 0.42, size * 0.78, size * 0.58], fill=CREAM + (255,))
    return im


def radial(size, colour, power=2.0):
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    dd = np.sqrt((xx - size / 2) ** 2 + (yy - size / 2) ** 2) / (size / 2)
    a = np.clip(1 - dd, 0, 1) ** power * 255
    arr = np.zeros((size, size, 4), np.uint8)
    arr[..., :3] = colour
    arr[..., 3] = a.astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def slide(old, new, p, rtl):
    """Paper slide: the new sheet slides in over the old one from the reading-end side."""
    p = ease(p)
    if p >= 1:
        return new
    W, H = new.size
    out = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    shift = int(p * W * 0.18)
    out.paste(old, (shift if rtl else -shift, 0))
    off = int((1 - p) * W)
    x = -off if rtl else off
    sh = Image.new("RGBA", (60, H), (0, 0, 0, 0))
    g = np.linspace(110, 0, 60).astype(np.uint8)
    sh.putalpha(Image.fromarray(np.repeat(g[None, :], H, 0)))
    out.paste(new, (x, 0))
    if rtl:
        paste(out, sh, x + W, 0)
    else:
        paste(out, sh.transpose(Image.FLIP_LEFT_RIGHT), x - 60, 0)
    return out


def photo_box(c, key, name, w, h, t, D, z=(1.0, 1.05), c0=(0.5, 0.5), c1=(0.5, 0.5), prep=None):
    """Photo cropped to a w x h box with a slow push (used for split screens)."""
    def build():
        im = load(name)
        if prep:
            im = prep(im)
        s = max(w * 1.15 / im.width, h * 1.15 / im.height)
        if s > 1:
            im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        return im
    im = c.get(("pbox", key, name, w, h), build)
    cam = Cam(im.width, im.height, prog(t, D), z[0], z[1], c0, c1, (int(w), int(h)))
    return cam.view(im).convert("RGBA")


def darken(img, k):
    """Multiply an RGBA frame by k (0..1)."""
    if k >= 0.999:
        return img
    arr = np.asarray(img).astype(np.float32)
    arr[..., :3] *= k
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")


def whiff(d, x, y, ang, t_life, size=1.0, colour=(112, 100, 88)):
    """'Smell' lines: three short wavy strokes drifting along angle `ang` (radians, screen); t_life in 0..1."""
    if not 0 < t_life < 1:
        return
    a = math.sin(math.pi * t_life) ** 0.8
    ux, uy = math.cos(ang), math.sin(ang)
    px, py = -uy, ux
    L = 70 * size
    for k in (-1, 0, 1):
        pts = []
        for i in range(13):
            s = i / 12
            wav = math.sin(s * math.pi * 2.2 + t_life * 9 + k) * 6 * size
            bx = x + ux * (s * L) + px * (k * 15 * size + wav)
            by = y + uy * (s * L) + py * (k * 15 * size + wav)
            pts.append((bx, by))
        d.line(pts, fill=tuple(colour) + (int(150 * a),), width=max(2, int(3 * size)), joint="curve")


def ship_grid_icon(w, colour):
    """Tiny top-down tanker for unit charts."""
    h = max(3, int(w * 0.42))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.polygon([(0, 0), (w * 0.8, 0), (w - 1, h / 2), (w * 0.8, h - 1), (0, h - 1)], fill=tuple(colour) + (255,))
    return im


def oil_texture(w, h, seed=9):
    """Glossy black oil sheen (cached by the caller)."""
    rng = np.random.default_rng(seed)
    n = np.zeros((h, w), np.float32)
    for sc, amp in ((6, 1.0), (24, 0.8), (90, 0.6)):
        a = rng.normal(0, 1, (max(2, h // sc), max(2, w // sc))).astype(np.float32)
        n += np.asarray(Image.fromarray(a).resize((w, h), Image.BICUBIC)) * amp
    sheen = np.clip(n - 1.2, 0, None) * 22
    arr = np.zeros((h, w, 4), np.float32)
    arr[..., 0] = OIL[0] + sheen * 0.9
    arr[..., 1] = OIL[1] + sheen * 0.95
    arr[..., 2] = OIL[2] + sheen * 1.1
    arr[..., 3] = 255
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")


def fit_w(im, maxw):
    if im.width <= maxw:
        return im
    s = maxw / im.width
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
