"""Drawing kit for the Vox paper look: paper, cut-outs, ink, highlighter, pins, cork, text, labels, logo.

Everything works on 1920x1080 RGBA PIL images. Arabic-script text is shaped with libraqm.
"""
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
PROJ = HERE.parent.parent              # sheikh-said-vox/
REPO = PROJ.parent                     # my-first-project/
CACHE = PROJ / "build" / "cache"
W, H = 1920, 1080

PAPER = (239, 230, 212)       # #EFE6D4
INK = (30, 26, 22)            # #1E1A16
GOLD = (201, 164, 92)         # #C9A45C
GREEN = (15, 42, 31)          # #0F2A1F
CREAM = (245, 238, 220)       # #F5EEDC
RED = (158, 43, 37)           # #9E2B25
RIVER = (110, 143, 166)
SEA = (205, 214, 206)

FONT_FILES = {"ar": "Aljazeera.ttf", "ckb": "Speda.ttf", "kmr": "Montserrat-Regular.ttf"}
RAQM = {"ar": "ar", "ckb": "ckb", "kmr": "ku"}
QURAN_FONT = "Amiri-Regular.ttf"           # Naskh with full harakat (OFL)


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def back_out(x, s=1.4):
    """Overshoot ease (for things that slide in and settle)."""
    x = min(1.0, max(0.0, x))
    x -= 1
    return x * x * ((s + 1) * x + s) + 1


def clamp01(x):
    return min(1.0, max(0.0, x))


# ------------------------------------------------------------------ fonts and text
@lru_cache(maxsize=128)
def font(name, size):
    p = REPO / "fonts" / name
    if not p.exists():
        p = Path("/usr/share/fonts/truetype/noto") / name
    return ImageFont.truetype(str(p), size, layout_engine=ImageFont.Layout.RAQM)


class Lang:
    def __init__(self, key, direction):
        self.key = key
        self.rtl = direction == "rtl"
        self.dir = "rtl" if self.rtl else "ltr"
        self.raqm = RAQM[key]
        self.fontname = FONT_FILES[key]
        # Aljazeera draws small for its size; Montserrat draws large
        self.k = {"ar": 1.12, "ckb": 1.0, "kmr": 0.86}[key]

    def f(self, size):
        return font(self.fontname, int(size * self.k))


_probe = ImageDraw.Draw(Image.new("L", (8, 8)))


def text_width(L, text, size, stroke=0, fnt=None, direction=None):
    fnt = fnt or L.f(size)
    return _probe.textlength(text, font=fnt, direction=direction or L.dir, language=L.raqm) + 2 * stroke


def is_latin(s):
    return not any(is_rtl_char(c) for c in s)


def is_rtl_char(c):
    o = ord(c)
    return 0x0590 <= o <= 0x08FF or 0xFB1D <= o <= 0xFDFF or 0xFE70 <= o <= 0xFEFF


def text_dir(text, default):
    """Arabic-script letters -> rtl; Latin letters -> ltr; digits and punctuation only -> the language's direction."""
    if any(is_rtl_char(c) for c in text):
        return "rtl"
    if any(c.isalpha() for c in text):
        return "ltr"
    return default


@lru_cache(maxsize=2048)
def line_img(lkey, ldir, text, size, colour, stroke=1, fontname=None):
    """One shaped line -> (RGBA image cropped to text height band, word x-ranges in reading order)."""
    L = Lang(lkey, ldir)
    fnt = font(fontname, int(size * L.k)) if fontname else L.f(size)
    # Arabic-script text always runs right to left (also the Qur'an verse in the Kurmanji version)
    direction = text_dir(text, L.dir)
    lang = L.raqm if direction == L.dir else ("ar" if direction == "rtl" else "en")
    tw = int(math.ceil(_probe.textlength(text, font=fnt, direction=direction, language=lang))) + 2 * stroke + 12
    hh = int(round(size * (2.5 if fontname == QURAN_FONT else 1.75)))
    img = Image.new("RGBA", (tw, hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((6 + stroke, hh * 0.52), text, font=fnt, fill=tuple(colour) + (255,), anchor="lm", direction=direction,
           language=lang, stroke_width=stroke, stroke_fill=tuple(colour) + (255,))
    words = text.split(" ")
    space = _probe.textlength(" ", font=fnt, direction=direction, language=lang)
    ranges, acc = [], 0.0
    for i, w in enumerate(words):
        ww = _probe.textlength(w, font=fnt, direction=direction, language=lang)
        a0, a1 = acc - (space / 2 if i else 6), acc + ww + (space / 2 if i < len(words) - 1 else 6)
        if direction == "rtl":
            ranges.append((tw - 6 - stroke - a1, tw - 6 - stroke - a0))
        else:
            ranges.append((6 + stroke + a0, 6 + stroke + a1))
        acc += ww + space
    return img, tuple(ranges)


HARAKAT = set(chr(c) for c in list(range(0x064B, 0x0660)) + [0x0670])


def needs_alt_font(word, ldir):
    """Words the language font cannot draw: Arabic script inside a Latin line, or fully vowelled Arabic (Qur'an)
    inside a Sorani line (Speda has no harakat)."""
    if ldir == "ltr":
        return any(is_rtl_char(c) for c in word)
    return any(c in HARAKAT for c in word)


def mixed_line_img(lkey, ldir, text, size, colour, stroke=0, alt_font="Aljazeera.ttf"):
    """One line whose words need two fonts. Consecutive words of one kind are shaped together; the runs are laid out
    in the line's reading direction."""
    words = []
    for w in text.split(" "):
        if ldir == "ltr" and needs_alt_font(w, ldir):
            # keep Latin punctuation (« » , .) with the Latin text, so quote marks are not mirrored
            i, j = 0, len(w)
            while i < j and not is_rtl_char(w[i]):
                i += 1
            while j > i and not is_rtl_char(w[j - 1]):
                j -= 1
            if i:
                words.append(w[:i] + "\u2060")
            words.append(w[i:j])
            if j < len(w):
                words.append("\u2060" + w[j:])
        else:
            words.append(w)
    runs = []
    for w in words:
        k = needs_alt_font(w, ldir)
        if runs and runs[-1][1] == k:
            runs[-1][0].append(w)
        else:
            runs.append(([w], k))
    imgs = []
    for ws, k in runs:
        chunk = " ".join(ws).replace("\u2060 ", "").replace(" \u2060", "").replace("\u2060", "")
        if k:
            im = line_img("ar", "rtl", chunk, int(size * 0.95), colour, stroke, alt_font)[0]
        else:
            im = line_img(lkey, ldir, chunk, size, colour, stroke)[0]
        imgs.append(im)
    space = int(size * 0.28)
    w = sum(i.width for i in imgs) + space * (len(imgs) - 1)
    h = max(i.height for i in imgs)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    order = imgs if ldir == "ltr" else imgs[::-1]
    x = 0
    for im in order:
        out.alpha_composite(im, (x, (h - im.height) // 2))
        x += im.width + space
    return out


def reveal_words(img, ranges, n_visible_float):
    """Show the first n words (fractional = fading word) of a line image."""
    n = len(ranges)
    if n_visible_float >= n:
        return img
    if n_visible_float <= 0:
        return None
    col = np.zeros(img.width, np.float32)
    xs = np.arange(img.width)
    for j, (x0, x1) in enumerate(ranges):
        a = clamp01(n_visible_float - j)
        if a > 0:
            m = (xs >= x0) & (xs < x1)
            col[m] = np.maximum(col[m], a)
    arr = np.asarray(img).copy()
    arr[..., 3] = (arr[..., 3].astype(np.float32) * col[None, :]).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def wipe(img, frac, rtl):
    """Soft reveal of an image in reading direction."""
    if frac >= 1:
        return img
    if frac <= 0:
        return None
    w = img.width
    xs = np.arange(w, dtype=np.float32)
    edge = frac * (w + 40)
    a = np.clip((edge - (w - xs if rtl else xs)) / 40.0, 0, 1)
    arr = np.asarray(img).copy()
    arr[..., 3] = (arr[..., 3].astype(np.float32) * a[None, :]).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def fade(img, a):
    if a >= 1:
        return img
    if a <= 0:
        return None
    arr = np.asarray(img).copy()
    arr[..., 3] = (arr[..., 3].astype(np.float32) * a).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def paste(frame, img, x, y, a=1.0):
    """Alpha-composite img at integer position (clips to frame)."""
    if img is None or a <= 0:
        return
    if a < 1:
        img = fade(img, a)
        if img is None:
            return
    x, y = int(round(x)), int(round(y))
    if x >= frame.width or y >= frame.height or x + img.width <= 0 or y + img.height <= 0:
        return
    if x < 0 or y < 0 or x + img.width > frame.width or y + img.height > frame.height:
        cx0, cy0 = max(0, -x), max(0, -y)
        cx1, cy1 = min(img.width, frame.width - x), min(img.height, frame.height - y)
        img = img.crop((cx0, cy0, cx1, cy1))
        x, y = x + cx0, y + cy0
    frame.alpha_composite(img, (x, y))


# ------------------------------------------------------------------ paper, cork, dark paper
@lru_cache(maxsize=8)
def paper(w=W, h=H, seed=1, tone=PAPER, vign=0.18):
    rng = np.random.default_rng(seed)
    base = np.array(tone, np.float32)[None, None, :] * np.ones((h, w, 1), np.float32)
    noise = np.zeros((h, w), np.float32)
    for scale, amp in ((4, 5.0), (16, 4.0), (64, 3.0), (256, 2.5)):
        sh, sw = max(2, h // scale), max(2, w // scale)
        n = rng.normal(0, 1, (sh, sw)).astype(np.float32)
        n = np.asarray(Image.fromarray(n).resize((w, h), Image.BICUBIC))
        noise += n * amp
    arr = base + noise[..., None]
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(int(w * h / 3500)):                       # paper fibres
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        ang = rng.uniform(0, math.pi)
        ln = rng.uniform(4, 22)
        c = int(rng.uniform(-30, 25))
        d.line([(x, y), (x + math.cos(ang) * ln, y + math.sin(ang) * ln)],
               fill=(tone[0] + c, tone[1] + c, tone[2] + c, 40), width=1)
    if vign:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        dd = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
        v = 1 - vign * np.clip(dd - 0.45, 0, 1) ** 1.5
        img = Image.fromarray((np.asarray(img).astype(np.float32) * v[..., None]).astype(np.uint8))
    return img.convert("RGBA")


@lru_cache(maxsize=2)
def cork(w=W, h=H):
    rng = np.random.default_rng(5)
    base = np.array((92, 64, 40), np.float32)
    n = rng.normal(0, 1, (h // 2, w // 2)).astype(np.float32)
    n = np.asarray(Image.fromarray(n).resize((w, h), Image.BILINEAR))
    arr = base[None, None, :] + n[..., None] * 16
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(26000):                                  # cork granules
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.uniform(0.8, 3.2)
        c = int(rng.uniform(-35, 40))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(118 + c, 84 + c, 52 + c, 150))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dd = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    v = 1 - 0.45 * np.clip(dd - 0.3, 0, 1) ** 1.3
    img = Image.fromarray((np.asarray(img).astype(np.float32) * v[..., None]).astype(np.uint8))
    return img.convert("RGBA")


@lru_cache(maxsize=2)
def dark_paper(w=W, h=H):
    return paper(w, h, seed=9, tone=(38, 34, 30), vign=0.35)


# ------------------------------------------------------------------ cut-outs
def _edge_noise(n, rng, amp):
    x = np.zeros(n, np.float32)
    for k, a in ((n // 4 or 1, 0.5), (n // 16 or 1, 0.3), (n // 60 or 1, 0.2)):
        pts = rng.normal(0, 1, k + 2)
        x += np.interp(np.linspace(0, k + 1, n), np.arange(k + 2), pts) * a
    return x * amp


@lru_cache(maxsize=64)
def load(path):
    return Image.open(path).convert("RGB")


def cutout(img, torn=True, border=0, seed=0, shadow=True, rim=(246, 240, 226)):
    """Image -> RGBA paper cut-out (torn or straight edge, optional paper border and drop shadow)."""
    img = img.convert("RGB")
    pad = 30
    w, h = img.width + 2 * border, img.height + 2 * border
    canvas = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    rng = np.random.default_rng(seed)
    if torn:
        amp = max(4.0, min(w, h) * 0.012)
        top = _edge_noise(w, rng, amp)
        bot = _edge_noise(w, rng, amp)
        lef = _edge_noise(h, rng, amp)
        rig = _edge_noise(h, rng, amp)
        poly = [(pad + x, pad + 8 + top[x]) for x in range(0, w, 3)]
        poly += [(pad + w - 8 + rig[y], pad + y) for y in range(0, h, 3)]
        poly += [(pad + x, pad + h - 8 + bot[x]) for x in range(w - 1, -1, -3)]
        poly += [(pad + 8 + lef[y], pad + y) for y in range(h - 1, -1, -3)]
        rim_mask = Image.new("L", canvas.size, 0)
        ImageDraw.Draw(rim_mask).polygon(poly, fill=255)
        inner = rim_mask.filter(ImageFilter.MinFilter(7))
        mask = rim_mask
    else:
        mask = Image.new("L", canvas.size, 0)
        ImageDraw.Draw(mask).rectangle([pad, pad, pad + w - 1, pad + h - 1], fill=255)
        inner = mask
    layer = Image.new("RGBA", canvas.size, rim + (255,))
    layer.putalpha(mask)
    photo = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    photo.paste(img, (pad + border, pad + border))
    pm = Image.new("L", canvas.size, 0)
    pm.paste(255, (pad + border, pad + border, pad + border + img.width, pad + border + img.height))
    pm = ImageChops.multiply(pm, inner if torn and border == 0 else mask)
    photo.putalpha(pm)
    layer.alpha_composite(photo)
    if shadow:
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        sa = mask.filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * 0.42))
        sh.putalpha(sa)
        out = Image.new("RGBA", (canvas.width + 12, canvas.height + 12), (0, 0, 0, 0))
        out.alpha_composite(sh, (8, 10))
        out.alpha_composite(layer, (0, 0))
        return out
    return layer


def fit(img, w=None, h=None):
    if w and h:
        s = min(w / img.width, h / img.height)
    elif w:
        s = w / img.width
    else:
        s = h / img.height
    return img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.LANCZOS)


def cover(img, w, h, fx=0.5, fy=0.5):
    """Scale-and-crop img to exactly w x h, keeping the point (fx, fy) in view."""
    s = max(w / img.width, h / img.height)
    im = img.resize((int(math.ceil(img.width * s)), int(math.ceil(img.height * s))), Image.LANCZOS)
    x0 = int(min(max(0, im.width * fx - w / 2), im.width - w))
    y0 = int(min(max(0, im.height * fy - h / 2), im.height - h))
    return im.crop((x0, y0, x0 + w, y0 + h))


def sepia(img, amount=1.0):
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    g = (a * [0.299, 0.587, 0.114]).sum(2, keepdims=True)
    tone = np.concatenate([g * 1.07 + 6, g * 0.98 + 2, g * 0.82 - 4], axis=2)
    a = a * (1 - amount) + tone * amount
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def grade(img, sat=1.0, bright=1.0, tint=(1, 1, 1), contrast=1.0):
    a = np.asarray(img.convert("RGB")).astype(np.float32) / 255
    g = (a * [0.299, 0.587, 0.114]).sum(2, keepdims=True)
    a = g + (a - g) * sat
    a = (a - 0.5) * contrast + 0.5
    a = a * bright * np.array(tint, np.float32)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def mono(img, amount):
    if amount <= 0:
        return img
    return grade(img, sat=1 - amount)


# ------------------------------------------------------------------ camera
def camera(img, t, zoom0=1.0, zoom1=1.06, cx0=0.5, cy0=0.5, cx1=0.5, cy1=0.5, out=(W, H)):
    """Ken-Burns view of img (any size >= out aspect) at progress t in [0,1]."""
    u = ease(t) * 0.7 + t * 0.3
    z = zoom0 + (zoom1 - zoom0) * u
    cx = cx0 + (cx1 - cx0) * u
    cy = cy0 + (cy1 - cy0) * u
    s = max(out[0] / img.width, out[1] / img.height)
    vw, vh = out[0] / (s * z), out[1] / (s * z)
    x0 = min(max(0, cx * img.width - vw / 2), img.width - vw)
    y0 = min(max(0, cy * img.height - vh / 2), img.height - vh)
    return img.resize(out, Image.BILINEAR, box=(x0, y0, x0 + vw, y0 + vh))


# ------------------------------------------------------------------ ink
def wobble_line(pts, rng_seed=0, amp=1.4):
    rng = np.random.default_rng(rng_seed)
    out = []
    for i, (x, y) in enumerate(pts):
        out.append((x + rng.normal(0, amp) * 0.5, y + rng.normal(0, amp) * 0.5))
    return out


def resample(pts, step=4.0):
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        d = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(d / step))
        for k in range(1, n + 1):
            out.append((x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n))
    return out


def partial(pts, p):
    """First fraction p (by length) of a polyline."""
    if p >= 1:
        return pts
    if p <= 0 or len(pts) < 2:
        return pts[:1]
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    total = sum(seg)
    target = total * p
    out, acc = [pts[0]], 0.0
    for (a, b), s in zip(zip(pts, pts[1:]), seg):
        if acc + s >= target:
            r = (target - acc) / s if s else 0
            out.append((a[0] + (b[0] - a[0]) * r, a[1] + (b[1] - a[1]) * r))
            return out
        out.append(b)
        acc += s
    return out


def ink_line(d, pts, p, colour=INK, width=5, alpha=235):
    pp = partial(pts, p)
    if len(pp) >= 2:
        d.line(pp, fill=tuple(colour) + (alpha,), width=width, joint="curve")
        r = width / 2
        for (x, y) in (pp[0], pp[-1]):
            d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(colour) + (alpha,))


def ellipse_pts(box, turns=1.12, seed=0, start=-0.6):
    x0, y0, x1, y1 = box
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
    rng = np.random.default_rng(seed)
    n = 90
    pts = []
    wob = rng.normal(0, 1, 6)
    for k in range(n + 1):
        a = start + 2 * math.pi * turns * k / n
        f = 1 + 0.035 * math.sin(a * 2 + wob[0]) + 0.02 * math.sin(a * 3 + wob[1]) + 0.04 * k / n
        pts.append((cx + rx * f * math.cos(a), cy + ry * f * math.sin(a)))
    return pts


def arrow_head(d, p_from, p_to, colour, size=22, width=5, alpha=235):
    ang = math.atan2(p_to[1] - p_from[1], p_to[0] - p_from[0])
    for s in (-1, 1):
        a = ang + math.pi + s * 0.45
        d.line([p_to, (p_to[0] + size * math.cos(a), p_to[1] + size * math.sin(a))],
               fill=tuple(colour) + (alpha,), width=width)


def curve(p0, p1, bend=0.18, n=40):
    """Gentle quadratic curve between two points."""
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    cx, cy = mx - dy * bend, my + dx * bend
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * cx + t * t * p1[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * cy + t * t * p1[1]) for t in np.linspace(0, 1, n)]


def dotted(d, pts, p, colour=GOLD, r=4.2, gap=15):
    pp = resample(partial(pts, p), step=gap)
    for (x, y) in pp:
        d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(colour) + (255,))


def red_x(d, cx, cy, size, p, width=9):
    a = [(cx - size, cy - size), (cx + size, cy + size)]
    b = [(cx + size, cy - size), (cx - size, cy + size)]
    ink_line(d, a, clamp01(p * 2), RED, width)
    if p > 0.5:
        ink_line(d, b, clamp01(p * 2 - 1), RED, width)


def highlighter(frame, box, p, rtl, colour=GOLD, alpha=110):
    """Gold highlighter stroke behind a text box, drawn in reading direction."""
    if p <= 0:
        return
    x0, y0, x1, y1 = box
    w = (x1 - x0) * clamp01(p)
    lay = Image.new("RGBA", (int(x1 - x0) + 20, int(y1 - y0) + 10), (0, 0, 0, 0))
    dd = ImageDraw.Draw(lay)
    if rtl:
        xa, xb = lay.width - 10 - w, lay.width - 10
    else:
        xa, xb = 10, 10 + w
    dd.polygon([(xa, 8), (xb, 4), (xb + 4, lay.height - 6), (xa - 3, lay.height - 3)], fill=tuple(colour) + (alpha,))
    paste(frame, lay, x0 - 10, y0 - 5)


def pin(d, x, y, colour=RED, r=11):
    d.ellipse([x - r + 3, y - r + 5, x + r + 3, y + r + 5], fill=(0, 0, 0, 90))
    d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(colour) + (255,))
    d.ellipse([x - r * 0.45 - 3, y - r * 0.45 - 3, x - 1, y - 1], fill=(255, 255, 255, 140))


def string(d, a, b, colour=RED, width=4, p=1.0, sag=0.08):
    pts = curve(a, b, bend=-sag, n=30)
    ink_line(d, pts, p, colour, width, alpha=245)


def map_pin(frame, x, y, t, colour=RED, size=1.0):
    """Teardrop map pin dropping in with a small bounce (t = seconds since drop)."""
    if t < 0:
        return
    k = back_out(t / 0.35, 2.2)
    yoff = (1 - k) * -60
    r = 15 * size
    lay = Image.new("RGBA", (int(r * 4), int(r * 5)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy = lay.width / 2, r * 1.4
    d.ellipse([cx - r * 0.6 + 3, lay.height - r * 0.5, cx + r * 0.6 + 3, lay.height - r * 0.1], fill=(0, 0, 0, 70))
    d.polygon([(cx - r * 0.75, cy + r * 0.3), (cx + r * 0.75, cy + r * 0.3), (cx, lay.height - r * 0.35)],
              fill=tuple(colour) + (255,))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tuple(colour) + (255,))
    d.ellipse([cx - r * 0.38, cy - r * 0.38, cx + r * 0.38, cy + r * 0.38], fill=CREAM + (255,))
    paste(frame, lay, x - cx, y - (lay.height - r * 0.35) + yoff)


# ------------------------------------------------------------------ text blocks
def text_block(frame, L, lines, x, y, size, colour=INK, t=1e9, rate=6.0, start=0.0, align=None, stroke=1,
               line_gap=1.45, mode="words", fontname=None, alpha=1.0):
    """Draw lines of text, typed on word by word starting at `start` (seconds), `rate` words/second.

    x is the reading-start edge (right edge for RTL, left for LTR) unless align='center'.
    Returns list of (x0, y0, x1, y1) boxes of the drawn lines and the time the last word appears.
    """
    boxes = []
    k = 0
    tt = (t - start) * rate
    for i, text in enumerate(lines):
        img, ranges = line_img(L.key, L.dir, text, size, tuple(colour), stroke, fontname)
        if align == "center":
            lx = x - img.width / 2
        elif L.rtl and not (is_latin(text) and False):
            lx = x - img.width
        else:
            lx = x
        ly = y + i * size * line_gap
        n = len(ranges)
        if mode == "words":
            vis = reveal_words(img, ranges, tt - k)
        elif mode == "wipe":
            vis = wipe(img, clamp01((tt - k) / max(1, n)), L.rtl)
        else:
            vis = img if tt > 0 else None
        if vis is not None:
            paste(frame, vis, lx, ly, alpha)
        boxes.append((lx, ly + img.height * 0.18, lx + img.width, ly + img.height * 0.86))
        k += n
    return boxes, start + k / rate


def label_strip(L, text, size=54, colour=INK, bg=CREAM, pad=(26, 10), seed=0, rot=0.0):
    """Text on a paper strip with a soft shadow (Vox-style label)."""
    img, _ = line_img(L.key, L.dir, text, size, tuple(colour), 1)
    w, h = img.width + 2 * pad[0], int(img.height * 0.82) + 2 * pad[1]
    strip = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    sh = Image.new("RGBA", strip.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([12 + 4, 12 + 6, 12 + w + 4, 12 + h + 6], fill=(0, 0, 0, 95))
    strip.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
    ImageDraw.Draw(strip).rectangle([12, 12, 12 + w, 12 + h], fill=tuple(bg) + (255,))
    strip.alpha_composite(img, (12 + pad[0], int(12 + pad[1] - img.height * 0.09)))
    if rot:
        strip = strip.rotate(rot, resample=Image.BICUBIC, expand=True)
    return strip


def pill(L, text, size=30, fill=GOLD, fg=GREEN, outline=None):
    img, _ = line_img(L.key, L.dir, text, size, tuple(fg), 0)
    w, h = img.width + 26, int(size * 1.7)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(out).rounded_rectangle([0, 0, w - 1, h - 1], int(h / 2.4), fill=(tuple(fill) + (255,)) if fill else None,
                                          outline=(tuple(outline) + (255,)) if outline else None, width=3)
    out.alpha_composite(img, (13, int(h / 2 - img.height / 2)))
    return out


# ------------------------------------------------------------------ logo
@lru_cache(maxsize=8)
def logo(key, dark, width=90, opacity=0.7):
    name = {"ar": "arabic", "ckb": "sorani", "kmr": "kurmanji"}[key]
    lg = Image.open(REPO / "brand" / f"logo_{name}.png").convert("RGBA")
    if dark:
        a = np.asarray(lg).astype(np.float32)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        olive = (r - b) < 32
        a[olive, 0], a[olive, 1], a[olive, 2] = CREAM
        a[~olive, 0], a[~olive, 1], a[~olive, 2] = GOLD
        lg = Image.fromarray(a.astype(np.uint8), "RGBA")
    lg = lg.resize((width, int(lg.height * width / lg.width)), Image.LANCZOS)
    if opacity < 1:
        arr = np.asarray(lg).copy()
        arr[..., 3] = (arr[..., 3] * opacity).astype(np.uint8)
        lg = Image.fromarray(arr, "RGBA")
    return lg
