"""Reusable shot builders on top of the kit: camera, photo cut-outs, maps, case board, quotes, labels."""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import kit
from .kit import CREAM, GOLD, GREEN, H, INK, PAPER, RED, W, clamp01, ease, ease_out, paste
from .geo import View, base_map, area_tint

IMG_DIR = kit.PROJ / "assets" / "images"


class Ctx:
    """Everything a scene needs: language, timing (content time t starts after the chapter card), text, cache."""

    def __init__(self, sc, L, lang, img_types, extra, cache):
        self.sc, self.L, self.lang = sc, L, lang
        self.id = sc["id"]
        self.card = sc["card"]
        self.D = sc["dur"] - sc["card"]
        self.A = [dict(a, start=a["start"] - sc["card"]) for a in sc["audio"]]
        self.ost = sc["ost"]
        self.types = img_types
        self.x = extra
        self.cache = cache
        self.labels = []             # image labels requested for this frame

    @property
    def a0(self):
        return self.A[0]["start"] if self.A else 0.3

    @property
    def a1(self):
        return (self.A[-1]["start"] + self.A[-1]["dur"]) if self.A else self.D

    def quote(self):
        q = [a for a in self.A if a["voice"] == "quote"]
        return q[0] if q else None

    def get(self, key, fn):
        k = (self.id, key)
        if k not in self.cache:
            self.cache[k] = fn()
        return self.cache[k]

    def mx(self, x):
        """Layouts are designed for right-to-left reading; mirror them for left-to-right."""
        return x if self.L.rtl else W - x

    def label_for(self, fname):
        t = self.types.get("assets/images/" + fname)
        if t in ("ai", "painting"):
            self.labels.append("illustration")
        elif t == "colourised":
            self.labels.append("colourised")


def img(name):
    return kit.load(str(IMG_DIR / name))


# ------------------------------------------------------------------ camera with point mapping
class Cam:
    def __init__(self, iw, ih, u, z0=1.0, z1=1.06, c0=(0.5, 0.5), c1=(0.5, 0.5), out=(W, H)):
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

    def pts(self, ps):
        return [self.pt(x, y) for x, y in ps]


def prog(t, D):
    u = clamp01(t / max(D, 0.01))
    return ease(u) * 0.6 + u * 0.4


# ------------------------------------------------------------------ photo shots
def full_photo(c, key, name, t, D, z=(1.0, 1.08), c0=(0.5, 0.5), c1=(0.5, 0.5), prep=None, label=True):
    """Full-bleed photo with a slow camera move (2.5D push)."""
    def build():
        im = img(name)
        if prep:
            im = prep(im)
        s = max(2304 / im.width, 1296 / im.height)
        if s > 1:
            im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
        return im
    im = c.get(("full", key, name), build)
    cam = Cam(im.width, im.height, prog(t, D), z[0], z[1], c0, c1)
    if label:
        c.label_for(name)
    return cam.view(im).convert("RGBA"), cam


def paper_bg(c, t, D, seed=1, drift=18):
    """Parchment that drifts slightly (background layer of the parallax)."""
    p = c.get(("paper", seed), lambda: kit.paper(W + 80, H + 50, seed=seed))
    u = prog(t, D)
    x = 40 + (drift * (u - 0.5) if c.L.rtl else -drift * (u - 0.5))
    return p.crop((int(x), 25, int(x) + W, 25 + H)).copy()


def cutout_on(c, frame, key, name, t, D, cx, cy, w=None, h=None, torn=True, border=0, rot=0.0, seed=0,
              prep=None, enter=0.0, enter_from=None, scale=(1.0, 1.04), alpha=1.0, label=True):
    """A paper cut-out photo placed at (cx, cy) (designed for RTL; mirrored for LTR), with parallax drift."""
    def build():
        im = img(name)
        if prep:
            im = prep(im)
        im = kit.fit(im, w, h)
        co = kit.cutout(im, torn=torn, border=border, seed=seed)
        if rot:
            co = co.rotate(rot, resample=Image.BICUBIC, expand=True)
        return co
    co = c.get(("cut", key, name, w, h, rot), build)
    u = prog(t, D)
    s = scale[0] + (scale[1] - scale[0]) * u
    if abs(s - 1) > 0.002:
        co = co.resize((int(co.width * s), int(co.height * s)), Image.BILINEAR)
    x = c.mx(cx) - co.width / 2
    y = cy - co.height / 2
    if enter_from is not None:
        k = kit.back_out((t - enter) / 0.55, 1.2) if t >= enter else 0
        if k <= 0:
            return None
        dx = {"left": -1, "right": 1}.get(enter_from, 0) * (1 - k) * 900
        dy = {"top": -1, "bottom": 1}.get(enter_from, 0) * (1 - k) * 700
        if not c.L.rtl:
            dx = -dx
        x, y = x + dx, y + dy
    paste(frame, co, x, y, alpha)
    if label and alpha > 0.05:
        c.label_for(name)
    return (x, y, x + co.width, y + co.height)


# ------------------------------------------------------------------ on-screen text
def ost_strips(c, frame, lines, t, t0, x=None, y=150, size=54, gap=22, stagger=0.35, colours=None, bgs=None):
    """Lines as paper-strip labels sliding in from the reading-start edge, stacked downwards."""
    x = c.mx(W - 110) if x is None else c.mx(x)
    yy = y
    boxes = []
    for i, text in enumerate(lines):
        col = colours[i] if colours else INK
        bg = bgs[i] if bgs else CREAM
        strip = c.get(("strip", text, size, col, bg), lambda: kit.label_strip(c.L, text, size, col, bg))
        k = ease_out((t - t0 - i * stagger) / 0.45)
        if k > 0:
            off = (1 - k) * 160
            sx = (x - strip.width + off) if c.L.rtl else (x - off)
            paste(frame, strip, sx, yy, clamp01(k * 1.6))
            boxes.append((sx, yy, sx + strip.width, yy + strip.height))
        yy += strip.height + gap - 24
    return boxes


def ink_text(c, frame, lines, t, t0, x=None, y=150, size=64, colour=INK, rate=5.0, mode="words", align=None,
             line_gap=1.45, stroke=1, fontname=None):
    x = c.mx(W - 120) if x is None else (x if align == "center" else c.mx(x))
    return kit.text_block(frame, c.L, lines, x, y, size, colour, t, rate, t0, align, stroke, line_gap, mode, fontname)


def tag_pill(c, frame, key, t, t0, y=96, x=None):
    """Attributed / per-article tags (small pill)."""
    text = c.x["labels"][key]
    p = c.get(("pill", text), lambda: kit.pill(c.L, text, 26, fill=None, fg=INK, outline=INK))
    a = clamp01((t - t0) / 0.4)
    if a > 0:
        xx = c.mx(W - 110 if x is None else x)
        paste(frame, p, (xx - p.width) if c.L.rtl else xx, y, a)


# ------------------------------------------------------------------ maps
def map_shot(c, key, view_args, t, D, z=(1.0, 1.0), c0=(0.5, 0.5), c1=(0.5, 0.5), rivers=None, tints=(),
             size=(2400, 1350)):
    """Paper map (cached) with a camera move. Returns frame, cam, view (map-pixel coordinates)."""
    def build():
        v = View(*view_args, size[0], size[1])
        kw = {} if rivers is None else {"rivers": rivers}
        m = base_map(v, **kw)
        return v, m
    v, m = c.get(("map", key), build)
    cam = Cam(m.width, m.height, prog(t, D), z[0], z[1], c0, c1)
    frame = cam.view(m).convert("RGBA")
    for (area, colour, alpha) in tints:
        if alpha > 0:
            tint = c.get(("tint", key, area, colour), lambda: area_tint(v, area, colour, 255))
            tv = cam.view(tint)
            paste(frame, tv, 0, 0, alpha / 255)
    return frame, cam, v


def map_label(c, frame, text, x, y, t, t0, size=34, colour=INK, anchor="above"):
    """Place name with a paper halo, written on in reading direction."""
    if not text:
        return
    def build():
        halo, _ = kit.line_img(c.L.key, c.L.dir, text, size, PAPER, 6)
        fg, _ = kit.line_img(c.L.key, c.L.dir, text, size, tuple(colour), 1)
        out = Image.new("RGBA", (halo.width, halo.height), (0, 0, 0, 0))
        out.alpha_composite(halo.filter(ImageFilter.GaussianBlur(1.5)))
        out.alpha_composite(fg, ((halo.width - fg.width) // 2, (halo.height - fg.height) // 2))
        return out
    im = c.get(("maplabel", text, size, colour), build)
    vis = kit.wipe(im, clamp01((t - t0) / 0.5), c.L.rtl)
    if vis is None:
        return
    if anchor == "above":
        paste(frame, vis, x - im.width / 2, y - im.height - 8)
    elif anchor == "below":
        paste(frame, vis, x - im.width / 2, y + 6)
    elif anchor == "side":
        paste(frame, vis, (x - im.width - 14) if c.L.rtl else (x + 14), y - im.height / 2)
    else:
        paste(frame, vis, x - im.width / 2, y - im.height / 2)


def city_dot(d, x, y, r=7, colour=INK, a=1.0):
    if a <= 0:
        return
    d.ellipse([x - r, y - r, x + r, y + r], fill=tuple(colour) + (int(255 * a),))


def route(frame, pts, p, colour=GOLD, r=5, gap=16):
    if p <= 0:
        return
    d = ImageDraw.Draw(frame, "RGBA")
    kit.dotted(d, pts, p, (90, 70, 40), r + 1.5, gap)      # dark rim so gold dots read on pale paper
    kit.dotted(d, pts, p, colour, r, gap)


def arrow(frame, pts, p, colour=INK, width=7, head=26, alpha=235):
    if p <= 0:
        return
    d = ImageDraw.Draw(frame, "RGBA")
    kit.ink_line(d, pts, p, colour, width, alpha)
    if p >= 0.98:
        kit.arrow_head(d, pts[-2], pts[-1], colour, head, width, alpha)


# ------------------------------------------------------------------ case board
def board_card(c, lines, size=44, w=None, colour=INK, bg=CREAM, rot=0.0, seed=0):
    """A typed note card for the cork board."""
    imgs = [kit.line_img(c.L.key, c.L.dir, s, size, tuple(colour), 1)[0] for s in lines]
    tw = max(i.width for i in imgs)
    w = max(w or 0, tw + 70)
    h = int(sum(i.height * 0.86 for i in imgs) + 70)
    card = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0))
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([15 + 5, 15 + 8, 15 + w + 5, 15 + h + 8], fill=(0, 0, 0, 120))
    card.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    note = kit.paper(w, h, seed=seed + 20, tone=tuple(bg), vign=0.05).copy()
    card.alpha_composite(note, (15, 15))
    y = 15 + 35
    for im in imgs:
        card.alpha_composite(im, (15 + (w - im.width) // 2, int(y - im.height * 0.12)))
        y += im.height * 0.86
    if rot:
        card = card.rotate(rot, resample=Image.BICUBIC, expand=True)
    return card


def pinned(frame, item, cx, cy, t, t0, from_side=1, pin_colour=RED):
    """Item flies onto the board and gets a pin; returns pin position or None."""
    if t < t0:
        return None
    k = kit.back_out((t - t0) / 0.5, 1.3)
    x = cx - item.width / 2 + (1 - k) * 700 * from_side
    y = cy - item.height / 2 - (1 - k) * 80
    paste(frame, item, x, y)
    px, py = cx + (1 - k) * 700 * from_side, cy - item.height / 2 + 34
    if t - t0 > 0.45:
        kit.pin(ImageDraw.Draw(frame, "RGBA"), px, py, pin_colour)
    return (px, py)


# ------------------------------------------------------------------ quotes
def quote_card(c, frame, lines, t, t_start, t_end, size=72, y=None, portrait=None, portrait_alpha=0.18,
               underline_line=None, colour=INK, gold_marks=True):
    """Vox pull-quote: big gold quote marks, the text typed on word by word between t_start and t_end."""
    n = sum(len(s.split()) for s in lines)
    rate = n / max(0.8, (t_end - t_start))
    total_h = len(lines) * size * 1.55
    y = (H / 2 - total_h / 2 - 20) if y is None else y
    if gold_marks:
        qm = c.get(("qmark", size), lambda: kit.line_img(c.L.key, c.L.dir, "«", int(size * 3.2), GOLD, 0)[0])
        a = clamp01((t - t_start + 0.6) / 0.5)
        if a > 0:
            paste(frame, qm, c.mx(W - 230) - (qm.width if c.L.rtl else 0) * 0.5 - qm.width / 2, y - size * 1.9, a * 0.85)
    boxes, t_done = kit.text_block(frame, c.L, lines, W / 2, y, size, colour, t, rate, t_start, "center", 2, 1.55)
    if underline_line is not None and t > t_done:
        x0, y0, x1, y1 = boxes[underline_line]
        d = ImageDraw.Draw(frame, "RGBA")
        pts = kit.wobble_line([(x1 - 10, y1 + 10), (x0 + 10, y1 + 14)] if c.L.rtl else [(x0 + 10, y1 + 10), (x1 - 10, y1 + 14)], 3)
        kit.ink_line(d, kit.resample(pts, 6), clamp01((t - t_done) / 0.5), GOLD, 8)
    return boxes, t_done


def portrait_behind(c, frame, name, t, alpha, side="left", h=980, prep=None):
    def build():
        im = img(name)
        if prep:
            im = prep(im)
        im = kit.fit(im, h=h)
        a = np.asarray(im.convert("RGBA")).copy()
        hh, ww = a.shape[:2]
        xs = np.linspace(0, 1, ww)[None, :]
        ys = np.linspace(0, 1, hh)[:, None]
        m = np.clip(np.minimum(np.minimum(xs, 1 - xs), np.minimum(ys, 1 - ys)) / 0.18, 0, 1)
        a[..., 3] = (m * 255).astype(np.uint8)
        return Image.fromarray(a, "RGBA")
    p = c.get(("behind", name, h), build)
    x = 60 if side == "left" else W - 60 - p.width
    if not c.L.rtl:
        x = W - x - p.width
    paste(frame, p, x, (H - p.height) / 2, alpha)
    c.label_for(name)


# ------------------------------------------------------------------ chapter card, transitions
def chapter_card(c, number, title, t):
    frame = kit.paper(W, H, seed=40 + number).copy()
    d = ImageDraw.Draw(frame, "RGBA")
    num = c.get(("cardnum", number), lambda: kit.line_img("kmr", "ltr", str(number), 260, GOLD, 3)[0])
    k = ease_out((t - 0.15) / 0.5)
    paste(frame, num, W / 2 - num.width / 2, 250 - (1 - k) * 40, k)
    ti = c.get(("cardtitle", title), lambda: kit.line_img(c.L.key, c.L.dir, title, 96, INK, 2)[0])
    vis = kit.wipe(ti, clamp01((t - 0.45) / 0.7), c.L.rtl)
    if vis is not None:
        paste(frame, vis, W / 2 - ti.width / 2, 560)
    lw = 360 * ease_out((t - 0.9) / 0.6)
    if lw > 0:
        d.line([(W / 2 - lw / 2, 740), (W / 2 + lw / 2, 740)], fill=GOLD + (255,), width=5)
    return frame


def slide(old, new, p, rtl, from_side=None):
    """New sheet slides in over the old one (paper slide), with a soft shadow on its leading edge."""
    p = ease(p)
    if p >= 1:
        return new
    side = from_side or ("left" if rtl else "right")
    off = int((1 - p) * W)
    out = old.copy()
    if p > 0:
        shift = int(p * W * 0.18)
        out = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        out.paste(old, (shift if side == "left" else -shift, 0))
        sh = Image.new("RGBA", (60, H), (0, 0, 0, 0))
        g = np.linspace(110, 0, 60).astype(np.uint8)
        sh.putalpha(Image.fromarray(np.repeat(g[None, :], H, 0)))
        if side == "left":
            x = -off
            out.paste(new, (x, 0))
            paste(out, sh, x + W, 0)
        else:
            x = off
            out.paste(new, (x, 0))
            paste(out, sh.transpose(Image.FLIP_LEFT_RIGHT), x - 60, 0)
    return out
