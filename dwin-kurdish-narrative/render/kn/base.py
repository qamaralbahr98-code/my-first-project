"""Drawing base for the Kurdish-youth explainer (ar / ckb / kmr, 16:9 and 9:16).

Size-aware context, shaped text with glyph fallback, paper strips, photos with camera moves, video clips,
Ken Burns with grain and vignette. Reuses the Vox kit of the Sheikh Said project (paper, cut-outs, libraqm).
"""
import math
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PROJ = Path(__file__).resolve().parents[2]            # dwin-kurd-youth/
REPO = PROJ.parent
sys.path.insert(0, str(REPO / "sheikh-said-vox" / "render"))
from vox import kit  # noqa: E402
from vox.kit import clamp01, ease, ease_out, back_out, paste  # noqa: E402,F401

IMG = PROJ / "assets"
REAL = PROJ / "assets" / "real"
CACHE = PROJ / "build" / "cache"

PAPER = (239, 232, 220)        # cream
INK = (17, 20, 24)             # near-black
SAFFRON = (232, 163, 61)
RED = (178, 52, 40)
GREEN = (74, 128, 84)
CREAM = (248, 244, 236)
GREY = (110, 106, 100)
DARK = (17, 20, 24)
RTL = {"ar": True, "ckb": True, "kmr": False}

SRC_WORD = {"ar": "المصدر", "ckb": "سەرچاوە", "kmr": "Çavkanî"}
ILLUS = {"ar": "صورة توضيحية", "ckb": "وێنەی ڕوونکردنەوە", "kmr": "Wêneya nîşanî"}

_MISSING = set()


class Ctx:
    def __init__(self, sc, lang, size, cache, txt):
        self.sc, self.lang = sc, lang
        self.W, self.H = size
        self.vert = self.H > self.W
        self.rtl = RTL[lang]
        self.L = kit.Lang(lang, "rtl" if self.rtl else "ltr")
        self.id = sc["id"]
        self.D = sc["dur"]
        self.ost = sc["ost"]
        self.words = sc["words"]
        self.cache = cache
        self.labels = []
        self.credit = None
        self.txt = txt
        a = sc["audio"]
        self.a0 = a[0]["start"] if a else 0.3
        self.a1 = (a[0]["start"] + a[0]["dur"]) if a else self.D

    def get(self, key, fn):
        k = (self.id, self.W, key)
        if k not in self.cache:
            self.cache[k] = fn()
        return self.cache[k]

    def mx(self, x):
        """Mirror an x measured from the left for RTL layouts."""
        return self.W - x if self.rtl else x

    def w(self, i):
        if not self.words:
            return self.a0
        return self.words[max(-len(self.words), min(i, len(self.words) - 1))]["s"]

    def frac(self, u):
        """Time at fraction u of the narration."""
        return self.a0 + (self.a1 - self.a0) * u

    def find(self, part, nth=0, default=None):
        k = 0
        for w in self.words:
            if part in w["text"]:
                if k == nth:
                    return w["s"]
                k += 1
        if (self.lang, self.id, part) not in _MISSING:
            _MISSING.add((self.lang, self.id, part))
            print(f"warning: {self.lang} {self.id}: no word with {part!r}", file=sys.stderr)
        return self.a0 if default is None else default

    def at(self, ar, ckb, kmr, nth=0, default=None):
        """Narration time of a key word, one spelling per language; a float means a fraction of the narration."""
        v = {"ar": ar, "ckb": ckb, "kmr": kmr}[self.lang]
        if isinstance(v, (int, float)):
            return self.frac(v)
        return self.find(v, nth, default)

    def illustration(self):
        self.labels.append("illustration")

    @property
    def margin(self):
        return 70 if self.vert else 120

    @property
    def top(self):
        return 400 if self.vert else 150

    @property
    def cap_top(self):
        """Top of the caption band (keep text out of it)."""
        return 1420 if self.vert else self.H - 210


# ------------------------------------------------------------------ text
FONT = {"ar": "Aljazeera.ttf", "ckb": "Speda.ttf", "kmr": "Montserrat-Bold.ttf"}
FALLBACK = ["Montserrat-Bold.ttf", "DejaVuSans-Bold.ttf"]


def font_name(lang, bold=True):
    if lang == "kmr":
        return "Montserrat-Bold.ttf" if bold else "Montserrat-Regular.ttf"
    return FONT[lang]


@lru_cache(maxsize=8)
def _cmap(name):
    from fontTools.ttLib import TTFont
    return set(TTFont(str(REPO / "fonts" / name)).getBestCmap())


def _font_for(ch, primary):
    if ch == " " or ord(ch) in _cmap(primary):
        return primary
    for f in FALLBACK:
        if ord(ch) in _cmap(f):
            return f
    return primary


@lru_cache(maxsize=6000)
def T(lang, text, size, colour, bold=True, stroke=0):
    """One shaped line. Characters the language font lacks (✓ ✗ ◐ ← ≈ …) come from Montserrat / DejaVu."""
    fname = font_name(lang, bold)
    ldir = "rtl" if RTL[lang] else "ltr"
    if lang != "kmr":
        text = text.replace("٬", "،")
    runs = []
    for ch in text:
        f = _font_for(ch, fname)
        if ch == " " and runs:
            f = runs[-1][1]
        if runs and runs[-1][1] == f:
            runs[-1][0].append(ch)
        else:
            runs.append(([ch], f))
    if len(runs) == 1 and runs[0][1] == fname:
        return kit.line_img(lang, ldir, text, size, tuple(colour), stroke, fname)[0]
    sp = size * 0.26
    imgs = []
    for chars, f in runs:
        s = "".join(chars)
        lead, trail = len(s) - len(s.lstrip(" ")), len(s) - len(s.rstrip(" "))
        if not s.strip():
            imgs.append((None, lead, 0))
            continue
        if f == fname:
            im = kit.line_img(lang, ldir, s.strip(), size, tuple(colour), stroke, f)[0]
        else:
            sz = size * (0.86 if lang == "kmr" else 0.92)
            im = kit.line_img("kmr", "ltr", s.strip(), int(sz / 0.86), tuple(colour), stroke, f)[0]
        imgs.append((im, lead, trail))
    order = imgs[::-1] if ldir == "rtl" else imgs
    h = max(i.height for i, _, _ in order if i is not None)
    pieces, x = [], 0.0
    for im, lead, trail in order:
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


def fit_w(im, maxw):
    if im.width <= maxw:
        return im
    s = maxw / im.width
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)


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
    """Paper-strip labels stacked downwards; 16:9: on the reading-start edge of `col`; 9:16: centred."""
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
            s = c.get(("strip_fit", text, size, colr, bg, x1 - x0), lambda: fit_w(s, (x1 - x0) + 24))
        t_i = times[i] if times else t0 + i * stagger
        k = ease_out((t - t_i) / 0.45)
        if k > 0 and fade_out > 0:
            if align == "center":
                sx = (x0 + x1) / 2 - s.width / 2
                sy = y + (1 - k) * 30
            else:
                off = (1 - k) * 160
                sx = (x1 + 12 - s.width + off) if c.rtl else (x0 - 12 - off)
                sy = y
            paste(f, s, sx, sy, clamp01(k * 1.6) * fade_out)
            boxes.append((sx, sy, sx + s.width, sy + s.height))
        y += s.height + gap
    return boxes, y


def _pill(w, h, fill):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w - 1, h - 1], h // 3, fill=fill)
    return im


def pill(lang, text, size, fill=SAFFRON, fg=INK):
    img = T(lang, text, size, fg, True)
    w, h = img.width + 30, int(size * 1.65)
    out = _pill(w, h, tuple(fill) + (255,))
    out.alpha_composite(img, (15, int(h / 2 - img.height / 2)))
    return out


def source_line(c, f, text, t, t0, dark=True):
    """Small source credit in the corner opposite the logo (16:9) / above the captions (9:16)."""
    if not text:
        return
    full = f"{SRC_WORD[c.lang]}: {text}"
    size = 24 if c.vert else 21
    col = (232, 228, 220) if dark else (70, 66, 60)
    im = c.get(("src", full, dark), lambda: fit_w(T(c.lang, full, size, col, False), c.W - 2 * c.margin))
    a = clamp01((t - t0) / 0.5)
    if a <= 0:
        return
    if c.vert:
        xx, yy = c.W / 2 - im.width / 2, c.cap_top - 70
    else:
        xx = c.margin if c.rtl else c.W - c.margin - im.width
        yy = 40
    pad = c.get(("srcpad", im.width, im.height, dark), lambda: _pill(im.width + 18, int(im.height * 0.8),
                                                                     (0, 0, 0, 135) if dark else PAPER + (215,)))
    paste(f, pad, xx - 9, yy + im.height * 0.1, a)
    paste(f, im, xx, yy, a)


# ------------------------------------------------------------------ images
@lru_cache(maxsize=40)
def load(name):
    p = IMG / name if (IMG / name).exists() else REAL / name
    return Image.open(p).convert("RGB")


@lru_cache(maxsize=8)
def mask(name):
    """Person matte (rembg u2net_human_seg), cached on disk."""
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / (Path(name).stem + "_mask.png")
    if not p.exists():
        src = Path("/home/claude/in3") / (Path(name).stem + "_mask.png")
        if src.exists():
            Image.open(src).convert("L").save(p)
        else:
            from rembg import new_session, remove
            m = remove(load(name), session=new_session("u2net_human_seg"), only_mask=True)
            m.save(p)
    return Image.open(p).convert("L")


class Cam:
    def __init__(self, iw, ih, u, z0, z1, c0, c1, out, rot=0.0):
        z = z0 + (z1 - z0) * u
        cx = c0[0] + (c1[0] - c0[0]) * u
        cy = c0[1] + (c1[1] - c0[1]) * u
        s = max(out[0] / iw, out[1] / ih) * z
        self.vw, self.vh = out[0] / s, out[1] / s
        self.x0 = min(max(0, cx * iw - self.vw / 2), iw - self.vw)
        self.y0 = min(max(0, cy * ih - self.vh / 2), ih - self.vh)
        self.s, self.out = s, out

    def view(self, im, resample=Image.BILINEAR):
        return im.resize(self.out, resample, box=(self.x0, self.y0, self.x0 + self.vw, self.y0 + self.vh))

    def pt(self, x, y):
        return ((x - self.x0) * self.s, (y - self.y0) * self.s)


def prog(t, D):
    u = clamp01(t / max(D, 0.01))
    return ease(u) * 0.5 + u * 0.5


def _big(c, name, prep=None, k=1.2):
    def build():
        im = load(name)
        if prep:
            im = prep(im)
        s = max(c.W * k / im.width, c.H * k / im.height)
        if s > 1:
            im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        return im
    return c.get(("big", name, prep.__name__ if prep else None), build)


def photo(c, name, t, D, z=(1.0, 1.05), c0=(0.5, 0.5), c1=(0.5, 0.5), prep=None, label=True):
    im = _big(c, name, prep)
    cam = Cam(im.width, im.height, prog(t, D), z[0], z[1], c0, c1, (c.W, c.H))
    if label:
        c.illustration()
    return cam.view(im).convert("RGBA"), cam


def photo_box(c, name, w, h, t, D, z=(1.0, 1.05), c0=(0.5, 0.5), c1=(0.5, 0.5), prep=None):
    def build():
        im = load(name)
        if prep:
            im = prep(im)
        s = max(w * 1.15 / im.width, h * 1.15 / im.height)
        if s > 1:
            im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        return im
    im = c.get(("pbox", name, int(w), int(h), prep.__name__ if prep else None), build)
    cam = Cam(im.width, im.height, prog(t, D), z[0], z[1], c0, c1, (int(w), int(h)))
    return cam.view(im).convert("RGBA")


def paper_bg(c, t, D, seed=1, drift=16, tone=PAPER):
    p = c.get(("paper", seed, tone), lambda: kit.paper(c.W + 60, c.H + 40, seed=seed, tone=tone, vign=0.14))
    u = prog(t, D)
    x = 30 + drift * (u - 0.5) * (1 if c.rtl else -1)
    return p.crop((int(x), 20, int(x) + c.W, 20 + c.H)).copy()


def dark_bg(c, seed=2):
    return c.get(("dark", seed), lambda: kit.paper(c.W, c.H, seed=seed, tone=(24, 26, 30), vign=0.35)).copy()


def darken(img, k):
    if k >= 0.999:
        return img
    arr = np.asarray(img).astype(np.float32)
    arr[..., :3] *= k
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")


def grade(img, k=(1.0, 1.0, 1.0), sat=1.0):
    arr = np.asarray(img).astype(np.float32)
    rgb = arr[..., :3]
    if sat != 1.0:
        g = rgb.mean(axis=2, keepdims=True)
        rgb = g + (rgb - g) * sat
    rgb = rgb * np.array(k, np.float32)
    arr[..., :3] = rgb
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")


@lru_cache(maxsize=4)
def _vignette(W, H, strength):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
    v = 1 - strength * np.clip(r - 0.55, 0, None) ** 1.6
    return v.clip(0, 1)[..., None]


def vignette(img, strength=0.55):
    arr = np.asarray(img).astype(np.float32)
    arr[..., :3] *= _vignette(img.width, img.height, strength)
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")


@lru_cache(maxsize=4)
def _grain(W, H, seed):
    rng = np.random.default_rng(seed)
    return rng.normal(0, 1, (H, W)).astype(np.float32)


def grain(img, t, amount=10.0):
    """Paper/film grain: one of 6 noise fields chosen by time."""
    g = _grain(img.width, img.height, int(t * 12) % 6)
    arr = np.asarray(img).astype(np.float32)
    arr[..., :3] += g[..., None] * amount
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")


def kenburns(c, name, t, D, z=None, label=True, prep=None, c0=(0.5, 0.5), c1=(0.5, 0.5), dark=1.0, grain_amt=8.0):
    """Ken Burns 1.00 -> 1.05 alternating by scene, grain, vignette."""
    n = int(c.id[1:]) if c.id[1:].isdigit() else 0
    z = z or ((1.0, 1.05) if n % 2 else (1.05, 1.0))
    f, cam = photo(c, name, t, D, z, c0, c1, prep, label)
    f = vignette(f, 0.5)
    if dark < 1:
        f = darken(f, dark)
    return grain(f, t, grain_amt), cam


def cut(c, name, w=None, h=None, torn=False, border=14, rot=0.0, seed=0, prep=None):
    def build():
        im = load(name)
        if prep:
            im = prep(im)
        co = kit.cutout(kit.fit(im, w, h), torn=torn, border=border, seed=seed)
        return co.rotate(rot, resample=Image.BICUBIC, expand=True) if rot else co
    return c.get(("cut", name, w, h, rot, border), build)


def place(f, im, cx, cy, t, t0, frm=None, a=1.0, dist=900):
    if t < t0:
        return None
    k = back_out((t - t0) / 0.55, 1.2)
    dx = dy = 0
    if frm == "left":
        dx = -(1 - k) * dist
    elif frm == "right":
        dx = (1 - k) * dist
    elif frm == "bottom":
        dy = (1 - k) * dist
    elif frm == "top":
        dy = -(1 - k) * dist
    x, y = cx - im.width / 2 + dx, cy - im.height / 2 + dy
    paste(f, im, x, y, a * (clamp01(k * 2) if frm is None else 1))
    return (x, y, x + im.width, y + im.height)


def shadowed(im, blur=10, off=(8, 12), alpha=90):
    pad = blur * 3
    out = Image.new("RGBA", (im.width + pad * 2 + abs(off[0]), im.height + pad * 2 + abs(off[1])), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    a = im.split()[3].point(lambda v: v * alpha // 255)
    blk = Image.new("RGBA", im.size, (0, 0, 0, 255))
    blk.putalpha(a)
    sh.alpha_composite(blk, (pad + off[0], pad + off[1]))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))
    out.alpha_composite(im, (pad, pad))
    return out


def card(w, h, fill=CREAM, radius=10, border=None):
    im = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, int(w) - 1, int(h) - 1], radius, fill=tuple(fill) + (255,),
                                         outline=(tuple(border) + (255,)) if border else None, width=3)
    return im


def text_lines(lang, text, size, maxw, colour=INK, bold=True):
    """Greedy wrap into lines no wider than maxw; returns list of images."""
    words = text.split(" ")
    lines, cur = [], []
    for w in words:
        trial = " ".join(cur + [w])
        if cur and T(lang, trial, size, colour, bold).width > maxw:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))
    return [T(lang, s, size, colour, bold) for s in lines]


def stack(imgs, gap=0.0, align="center", rtl=False):
    """Stack line images vertically into one image."""
    w = max(i.width for i in imgs)
    lh = [int(i.height * (0.86 + gap)) for i in imgs]
    out = Image.new("RGBA", (w, sum(lh) + imgs[-1].height - lh[-1]), (0, 0, 0, 0))
    y = 0
    for im, h in zip(imgs, lh):
        if align == "center":
            x = (w - im.width) // 2
        elif (align == "start" and rtl) or align == "right":
            x = w - im.width
        else:
            x = 0
        out.alpha_composite(im, (x, y))
        y += h
    return out


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


# ------------------------------------------------------------------ video clips
class Clip:
    """A real clip read sequentially through an ffmpeg pipe at 24 fps, scaled to height h (frames on demand)."""

    def __init__(self, name, h, start=0.0, crop=None):
        self.path, self.h, self.start, self.crop = REAL / name, h, start, crop
        info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                               "stream=width,height:format=duration", "-of", "json", str(self.path)],
                              capture_output=True, text=True)
        import json
        j = json.loads(info.stdout)
        w0, h0 = j["streams"][0]["width"], j["streams"][0]["height"]
        self.dur = float(j["format"]["duration"]) - start
        if crop:
            w0, h0 = map(int, crop.split(":")[:2])
        self.w = int(round(w0 * h / h0 / 2)) * 2
        self.n = max(1, int(self.dur * 24) - 1)
        self.p, self.pos, self.last = None, -1, None

    def _open(self):
        if self.p:
            self.p.kill()
        vf = f"fps=24,scale={self.w}:{self.h}:flags=lanczos"
        if self.crop:
            vf = f"crop={self.crop}," + vf
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(self.start), "-i", str(self.path), "-vf", vf,
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.pos = -1

    def at(self, t, loop=False):
        i = int(t * 24)
        i = i % self.n if loop else min(max(0, i), self.n - 1)
        if i == self.pos and self.last is not None:
            return self.last
        if self.p is None or i < self.pos:
            self._open()
        size = self.w * self.h * 3
        while self.pos < i:
            raw = self.p.stdout.read(size)
            if len(raw) < size:
                self.n = max(1, self.pos)
                break
            self.pos += 1
            buf = raw
            if self.pos == i:
                self.last = Image.frombytes("RGB", (self.w, self.h), buf).convert("RGBA")
        return self.last


def clip(c, name, h, **kw):
    return c.get(("clip", name, h, tuple(sorted(kw.items()))), lambda: Clip(name, h, **kw))


def radial_img(w, h, colour, power=2.0):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    a = np.clip(1 - r, 0, 1) ** power
    arr = np.zeros((h, w, 4), np.uint8)
    arr[..., :3] = colour
    arr[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")
