"""Render the Dwin Almas reel for one language from script/cards.<lang>.json.

    python3 render/reel.py ckb|kmr|ar [--preview SECONDS ...]

Follows section 4 of prompts/0x_*.md: 1080x1920, 30 fps, caption styles A/B/C/S/E, tags,
highlights, word-by-word animation, white flashes between chapters, source credits,
illustrative labels, Dwin logo top-left, grade and fairness rules.
"""
import json
import math
import subprocess
import sys
from functools import lru_cache
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assets import (CREAM, GOLD, GREEN, H, INK, REEL, REPO, W, logo_dark, shot)   # noqa: E402

FPS = 30
FONTS = {"ckb": "Speda.ttf", "kmr": "Montserrat-Regular.ttf", "ar": "Aljazeera.ttf"}
RAQM_LANG = {"ckb": "ckb", "kmr": "ku", "ar": "ar"}
LOGO_KEY = {"ckb": "sorani", "kmr": "kurmanji", "ar": "arabic"}
LATIN = "Montserrat-Regular.ttf"
WHITE = (255, 255, 255)

# ------------------------------------------------------------------ shot plan (card -> shots)
# (shot, motion, graded). Kurdistan24 and Hariri footage: static and ungraded (fairness rule 4.7).
PLAN = {
    "C01": [("hokar_jar", "push", True), ("phone_feed", "push", True)],
    "C02": [("hokar_presenter", "push", True)],
    "C03": [("hokar_jar", "push", True)],
    "C04": [("hokar_street", "push", True), ("hokar_jar_label", "push", True)],
    "C05": [("hokar_adv_a", "static", True), ("hokar_adv_b", "static", True)],
    "C06": [("lab", "push", True)],
    "C07": [("k24_market", "static", False)],
    "C08": [("k24_speaker", "static", False)],
    "C09": [("k24_stall", "static", False), ("pharmacy", "push", True)],
    "C10": [("k24_bottle", "push", False)],
    "C11": [("hariri_1", "static", False)],
    "C12": [("hariri_3", "static", False), ("hariri_4", "static", False)],
    "C13": [("law_doc", "doc", True)],
    "C14": [("law_doc", "doc", True)],
    "C15": [("law_doc", "doc", True)],
    "C16": [("gavel", "push", True)],
    "C17": [("jar_sticker", "push", False)],
    "C18": [("phone_likes", "push", False)],
    "C19": [(None, "static", False)],
    "C20": [("pharmacy_handover", "push", "warm")],
    "C21": [("phone_mock_ad", "scroll", "warm")],
    "C22": [("receipt_photo", "push", "warm")],
    "C23": [("complaint_form", "push", "warm")],
    "C24": [("hokar_jar", "pullback", True)],
    "C25": [(None, "static", False)],
    "C26": [(None, "static", False)],
}
DRAWN_LAW = {"C13", "C14", "C15"}   # drawn document, not the real PDF: labelled illustrative


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------------ grading (baked into stills)
_vig = None


def vignette():
    global _vig
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        _vig = (1 - 0.20 * np.clip(d - 0.45, 0, 1) ** 1.4)[..., None]
    return _vig


@lru_cache(maxsize=64)
def graded(name, mode):
    img = shot(name)
    if mode is False:
        return img
    a = np.asarray(img).astype(np.float32) / 255
    lum = (a * [0.299, 0.587, 0.114]).sum(2, keepdims=True)
    if mode == "warm":                                    # chapter 7: brighter, warmer, sat -10%, no vignette
        a = lum + (a - lum) * 0.90
        a = a * 1.06 + 0.02
        a = a * [1.04, 1.0, 0.93]
    else:                                                 # sat -25%, contrast +10, shadows -10, vignette 20%
        a = lum + (a - lum) * 0.75
        a = (a - 0.5) * 1.10 + 0.5
        a = a - 0.10 * np.clip(0.35 - lum, 0, 0.35) / 0.35 * 0.35
        a = a * vignette()
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def moved(img, motion, u):
    """u in [0,1] across the shot."""
    if motion in ("static", "doc"):
        z, dy = 1.0, 0
    elif motion == "push":
        z, dy = 1.0 + 0.06 * u, 0
    elif motion == "pullback":
        z, dy = 1.06 - 0.06 * u, 0
    elif motion == "scroll":
        z, dy = 1.04, (0.5 - u) * 120
    else:
        z, dy = 1.0, 0
    if z == 1.0 and dy == 0:
        return img.copy()
    cw, ch = W / z, H / z
    x0 = (W - cw) / 2
    y0 = min(max(0.0, (H - ch) / 2 + dy / z), H - ch - 1e-3)
    return img.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))


# ------------------------------------------------------------------ text helpers
@lru_cache(maxsize=64)
def font(name, size):
    return ImageFont.truetype(str(REPO / "fonts" / name), size, layout_engine=ImageFont.Layout.RAQM)


class Lang:
    def __init__(self, key):
        self.key = key
        self.data = json.load(open(REEL / "script" / f"cards.{key}.json", encoding="utf-8"))
        self.rtl = self.data["direction"] == "rtl"
        self.dir = "rtl" if self.rtl else "ltr"
        self.lang = RAQM_LANG[key]
        self.fontname = FONTS[key]
        self.labels = self.data["labels"]
        self.cards = self.data["cards"]
        self.total = self.data["total_seconds"]

    def f(self, size):
        return font(self.fontname, size)

    def width(self, text, size, stroke=0, latin=False):
        fnt = font(LATIN, size) if latin else self.f(size)
        d = ImageDraw.Draw(Image.new("L", (8, 8)))
        return d.textlength(text, font=fnt, direction=None if latin else self.dir,
                            language=None if latin else self.lang) + 2 * stroke


def is_latin(s):
    return all(ord(c) < 0x0590 for c in s)


@lru_cache(maxsize=512)
def line_image(key, text, size, colour, stroke):
    """Rendered line (RGBA, tight width, height = 1.35*size) + per-word x ranges in that image."""
    L = LANGS[key]
    fnt = L.f(size)
    tw = int(math.ceil(L.width(text, size, stroke))) + 8
    hh = int(round(size * 1.35))
    img = Image.new("RGBA", (tw, hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((4 + stroke, hh / 2 + size * 0.02), text, font=fnt, fill=colour + (255,), anchor="lm", direction=L.dir,
           language=L.lang, stroke_width=stroke, stroke_fill=colour + (255,))
    words = text.split(" ")
    space = L.width(" ", size)
    ranges, acc = [], 0.0
    for i, w in enumerate(words):
        ww = L.width(w, size)
        a0, a1 = acc, acc + ww + (space / 2 if i < len(words) - 1 else 4)
        a0 = a0 - (space / 2 if i else 4)
        if L.rtl:
            ranges.append((tw - 4 - stroke - a1, tw - 4 - stroke - a0))
        else:
            ranges.append((4 + stroke + a0, 4 + stroke + a1))
        acc += ww + space
    return img, ranges


def with_word_alpha(img, ranges, alphas):
    """Multiply the line image's alpha by a per-column mask from per-word alphas (0..1)."""
    if all(a >= 1 for a in alphas):
        return img
    col = np.zeros(img.width, np.float32)
    xs = np.arange(img.width)
    for (x0, x1), a in zip(ranges, alphas):
        col[(xs >= x0) & (xs < x1)] = np.maximum(col[(xs >= x0) & (xs < x1)], a)
    arr = np.asarray(img).copy()
    arr[..., 3] = (arr[..., 3].astype(np.float32) * col[None, :]).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


# ------------------------------------------------------------------ caption layouts
BASE = 56


def a_size(L, lines):
    s = BASE
    while s > 46 and max(L.width(t, s, max(1, s // 40)) for t in lines) > 900:
        s -= 2
    return s


def centred_size(L, lines, base, maxw=960, minsize=40):
    s = base
    while s > minsize and max(L.width(t, s, max(1, s // 40)) for t in lines) > maxw:
        s -= 2
    return s


def pill(text, size, L, fill, outline, fg, latin=False):
    fnt = font(LATIN, size) if latin else L.f(size)
    tw = L.width(text, size, latin=latin)
    ph, px = int(size * 1.7), int(size * 0.7)
    img = Image.new("RGBA", (int(tw + 2 * px), ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([1, 1, img.width - 2, ph - 2], 11, fill=fill, outline=outline, width=3 if outline else 0)
    d.text((img.width / 2, ph / 2), text, font=fnt, fill=fg + (255,), anchor="mm",
           direction=None if latin else L.dir, language=None if latin else L.lang)
    return img


def style_a(layer, L, card, f, nframes, events=None):
    lines = card["lines"]
    size = a_size(L, lines)
    stroke = max(1, size // 40)
    bh = int(round(size * 1.35))
    padx = 18
    top = int(1180 - len(lines) * bh / 2)
    anchor = W - 160 if L.rtl else 80
    d = ImageDraw.Draw(layer)
    # marker: tag pill or gold square, pops in over 3 frames
    k = ease_out(f / 3)
    if card["tag"]:
        p = pill(card["tag"], int(size * 0.6), L, GREEN + (230,), GOLD + (255,), CREAM)
        if k > 0:
            p = p.resize((max(1, int(p.width * k)), max(1, int(p.height * k))), Image.BILINEAR)
            px = anchor - p.width if L.rtl else anchor
            layer.alpha_composite(p, (int(px), int(top - 14 - p.height)))
    elif k > 0:
        s = 14 * k
        x = anchor if L.rtl else anchor - 14
        d.rectangle([x + (14 - s) / 2, top - 14 + (14 - s) / 2, x + (14 + s) / 2, top - 14 + (14 + s) / 2], fill=GOLD)
    start = 2
    for i, text in enumerate(lines):
        img, ranges = line_image(L.key, text, size, INK, stroke)
        n = len(ranges)
        if events is not None:
            events.append(("tick", start))
        bw = img.width - 8 + 2 * padx
        wipe = ease_out((f - start) / 6)
        if wipe > 0:
            y0 = top + i * bh
            box = GOLD if i == 0 else CREAM
            ww = bw * wipe
            x0, x1 = (anchor - ww, anchor) if L.rtl else (anchor, anchor + ww)
            d.rectangle([x0, y0, x1, y0 + bh], fill=box)
            alphas = [min(1.0, max(0.0, (f - (start + 2 + 4 * j)) / 4)) for j in range(n)]
            if max(alphas) > 0:
                li = with_word_alpha(img, ranges, alphas)
                tx = anchor - padx - (img.width - 4) if L.rtl else anchor + padx - 4
                layer.alpha_composite(li, (int(tx), int(y0)))
            line_done = start + 2 + 4 * n
            if card["highlight"] == i and f >= line_done:
                g = ease_out((f - line_done) / 6)
                uw = (img.width - 8) * g
                uy = y0 + bh - 9
                ucol = INK if i == 0 else GOLD
                ux0, ux1 = (anchor - padx - uw, anchor - padx) if L.rtl else (anchor + padx, anchor + padx + uw)
                d.rectangle([ux0, uy, ux1, uy + 5], fill=ucol)
        start = start + 2 + 4 * n
    return start


def style_centred(layer, L, card, f, base, colour, ul_px, shadow=False, events=None):
    lines = card["lines"]
    size = centred_size(L, lines, base)
    stroke = max(1, size // 40)
    lh = int(round(size * 1.35))
    total = len(lines) * lh
    top = 960 - total / 2
    if card["style"] == "C" and card["tag"]:
        p = pill(card["tag"], int(BASE * 0.6), L, GOLD + (255,), None, GREEN)
        k = ease_out(f / 3)
        if k > 0:
            p = p.resize((max(1, int(p.width * k)), max(1, int(p.height * k))), Image.BILINEAR)
            layer.alpha_composite(p, (int(W / 2 - p.width / 2), int(top - 30 - p.height)))
    d = ImageDraw.Draw(layer)
    for i, text in enumerate(lines):
        a = ease_out((f - (2 + 10 * i)) / 10)
        if events is not None:
            events.append(("line", 2 + 10 * i))
        if a <= 0:
            continue
        img, _ = line_image(L.key, text, size, colour, stroke)
        x = int(W / 2 - img.width / 2)
        y = int(top + i * lh)
        if shadow:
            sh, _ = line_image(L.key, text, size, (0, 0, 0), stroke + 2)
            sh = sh.filter(ImageFilter.GaussianBlur(6))
            arr = np.asarray(sh).copy()
            arr[..., 3] = (arr[..., 3] * 0.7 * a).astype(np.uint8)
            layer.alpha_composite(Image.fromarray(arr, "RGBA"), (x - 2, y + 2))
        if a < 1:
            arr = np.asarray(img).copy()
            arr[..., 3] = (arr[..., 3] * a).astype(np.uint8)
            img = Image.fromarray(arr, "RGBA")
        layer.alpha_composite(img, (x, y))
        if card["highlight"] == i and f >= 12 + 10 * i:
            g = ease_out((f - 12 - 10 * i) / 6)
            uw = (img.width - 8) * g
            d.rectangle([W / 2 - uw / 2, y + lh - 6, W / 2 + uw / 2, y + lh - 6 + ul_px], fill=GOLD)
    return 2 + 10 * len(lines)


# ------------------------------------------------------------------ timeline
class Timeline:
    def __init__(self, L):
        self.L = L
        self.cards = L.cards
        self.n = int(round(L.total * FPS))
        self.logo_small = {}
        self.events = []        # (time_s, kind, info) for the sound design
        for c in self.cards:
            ev = []
            layer = Image.new("RGBA", (8, 8))
            nfr = int(round((c["end"] - c["start"]) * FPS))
            if c["style"] == "A":
                style_a(Image.new("RGBA", (W, H)), L, c, 0, nfr, ev)
            elif c["style"] in "BCS":
                style_centred(Image.new("RGBA", (W, H)), L, c, 0, BASE, WHITE, 6, events=ev)
            for kind, fr in ev:
                self.events.append((c["start"] + fr / FPS, kind, c["id"]))
            if c["flash_before"]:
                self.events.append((c["start"] - 0.5, "flash", c["id"]))

    def card_at(self, t):
        for i, c in enumerate(self.cards):
            if c["start"] <= t < c["end"]:
                return i, c
        return None, None

    def logo(self, key, dark):
        k = (key, dark)
        if k not in self.logo_small:
            lg = logo_dark(key) if dark else Image.open(REPO / "brand" / f"logo_{key}.png").convert("RGBA")
            w = 110
            lg = lg.resize((w, int(lg.height * w / lg.width)), Image.LANCZOS)
            arr = np.asarray(lg).copy()
            arr[..., 3] = (arr[..., 3] * 0.85).astype(np.uint8)
            self.logo_small[k] = Image.fromarray(arr, "RGBA")
        return self.logo_small[k]


def shot_frame(card, t):
    """Background picture for card at absolute time t (RGB)."""
    plan = PLAN[card["id"]]
    dur = card["end"] - card["start"]
    k = min(len(plan) - 1, int((t - card["start"]) / (dur / len(plan))))
    name, motion, grade = plan[k]
    seg0 = card["start"] + k * dur / len(plan)
    u = min(1.0, max(0.0, (t - seg0) / (dur / len(plan))))
    if name is None:
        return Image.new("RGB", (W, H), GREEN), False
    return moved(graded(name, grade), motion, u), (grade is not False)


def compose(TL, t):
    L = TL.L
    i, card = TL.card_at(t)
    flash = 0.0
    if card is None:                         # inside a white-flash gap before a chapter
        nxt = next(c for c in TL.cards if c["start"] > t)
        g = t - (nxt["start"] - 0.5)
        prev = TL.cards[TL.cards.index(nxt) - 1]
        if g < 0.25:
            flash = g / 0.25
            card, tt = prev, prev["end"] - 1 / FPS
        elif g < 0.25 + 2 / FPS:
            flash, card, tt = 1.0, nxt, nxt["start"]
        else:
            flash = 1 - (g - 0.25 - 2 / FPS) / 0.2
            card, tt = nxt, nxt["start"]
        frame_img = render_card(TL, card, tt, captions=(card is prev))
    else:
        frame_img = render_card(TL, card, t, captions=True)
    if flash > 0:
        frame_img = Image.blend(frame_img, Image.new("RGB", (W, H), WHITE), min(1.0, max(0.0, flash)))
    return frame_img


def render_card(TL, card, t, captions=True):
    L = TL.L
    f = int(round((t - card["start"]) * FPS))
    nfr = int(round((card["end"] - card["start"]) * FPS))
    bg, _ = shot_frame(card, t)
    style = card["style"]
    if style == "B":
        bg = Image.fromarray((np.asarray(bg).astype(np.float32) * 0.6).astype(np.uint8))
    if style in "CSE":
        green = Image.new("RGB", (W, H), GREEN)
        bg = Image.blend(green, bg, 0.15) if PLAN[card["id"]][0][0] else green
    frame = bg.convert("RGBA")
    if card["id"] in DRAWN_LAW:
        doc_highlight(frame, card, f, nfr)
    if card["id"] == "C19":
        lg = logo_dark(LOGO_KEY[L.key])
        w = 700
        lg = lg.resize((w, int(lg.height * w / lg.width)), Image.LANCZOS)
        arr = np.asarray(lg).copy()
        arr[..., 3] = (arr[..., 3] * 0.08).astype(np.uint8)
        frame.alpha_composite(Image.fromarray(arr, "RGBA"), (int(W / 2 - w / 2), int(H / 2 - lg.height / 2)))
    if style == "E":
        end_card(frame, L, card, f)
        return frame.convert("RGB")

    # captions
    if captions:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if style == "A":
            style_a(layer, L, card, f, nfr)
        elif style == "B":
            style_centred(layer, L, card, f, int(BASE * 1.2), WHITE, 6, shadow=True)
        elif style == "C":
            style_centred(layer, L, card, f, int(BASE * 1.15), CREAM, 6)
        elif style == "S":
            style_centred(layer, L, card, f, int(BASE * 0.7), CREAM, 0)
        out = nfr - f
        if out <= 8:                                     # fade out with a 6 px blur over the last 8 frames
            k = max(0.0, (out - 1) / 7)
            layer = layer.filter(ImageFilter.GaussianBlur(6 * (1 - k)))
            arr = np.asarray(layer).copy()
            arr[..., 3] = (arr[..., 3] * k).astype(np.uint8)
            layer = Image.fromarray(arr, "RGBA")
        frame.alpha_composite(layer)

    # credit along the reading-side edge
    credit = card.get("credit")
    if credit:
        lat = is_latin(credit)
        fnt = font(LATIN if lat else L.fontname, 22)
        tw = int(L.width(credit, 22, latin=lat)) + 8
        ci = Image.new("RGBA", (tw, 34), (0, 0, 0, 0))
        ImageDraw.Draw(ci).text((4, 17), credit, font=fnt, fill=(255, 255, 255, 140), anchor="lm",
                                direction=None if lat else L.dir, language=None if lat else L.lang)
        ci = ci.rotate(90, expand=True)
        cx = W - 40 - ci.width if L.rtl else 40
        frame.alpha_composite(ci, (int(cx), int(H / 2 - ci.height / 2)))
    # illustrative label
    if card["illustrative"] or card["id"] in DRAWN_LAW:
        text = L.labels["illustrative"]
        lat = is_latin(text)
        fnt = font(LATIN if lat else L.fontname, 26)
        d = ImageDraw.Draw(frame)
        region = (W - 460, H - 470, W - 140, H - 420) if L.rtl else (48, H - 470, 368, H - 420)
        light = np.asarray(bg.crop(region)).mean() > 150
        col = (INK + (170,)) if light else (CREAM + (153,))
        if L.rtl:
            d.text((W - 140, H - 420), text, font=fnt, fill=col, anchor="rd", direction="rtl", language=L.lang)
        else:
            d.text((48, H - 420), text, font=fnt, fill=col, anchor="ld")
    # logo top-left (dark-background variant unless the corner is light)
    corner = np.asarray(bg.crop((48, 60, 158, 220))).mean()
    frame.alpha_composite(TL.logo(LOGO_KEY[L.key], dark=corner < 150), (48, 60))
    return frame.convert("RGB")


def doc_highlight(frame, card, f, nfr):
    """Gold marker sweeping down the (abstract) document lines, in sync with the card."""
    u = min(1.0, f / max(1, nfr - 10))
    y = 380 + u * 900
    hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(hl).rectangle([170, y - 6, 910, y + 26], fill=GOLD + (90,))
    frame.alpha_composite(hl)


def end_card(frame, L, card, f):
    k = ease_out(f / 12)
    lg = logo_dark(LOGO_KEY[L.key])
    w = int(W * 0.40 * (0.96 + 0.04 * k))
    lg = lg.resize((w, int(lg.height * w / lg.width)), Image.LANCZOS)
    arr = np.asarray(lg).copy()
    arr[..., 3] = (arr[..., 3] * k).astype(np.uint8)
    frame.alpha_composite(Image.fromarray(arr, "RGBA"), (int(W / 2 - w / 2), int(700 - lg.height / 2)))
    sizes = [52, 36]
    y = 700 + 0.40 * W * 1.6 / 2 + 70
    for i, text in enumerate(card["lines"]):
        a = ease_out((f - 8 - 8 * i) / 10)
        if a <= 0:
            continue
        s = sizes[min(i, 1)]
        img, _ = line_image(L.key, text, s, CREAM if i == 0 else GOLD, 1)
        arr = np.asarray(img).copy()
        arr[..., 3] = (arr[..., 3] * a).astype(np.uint8)
        frame.alpha_composite(Image.fromarray(arr, "RGBA"), (int(W / 2 - img.width / 2), int(y)))
        y += s * 1.6


# ------------------------------------------------------------------ rendering
LANGS = {}


def _init(key):
    LANGS[key] = Lang(key)


def _chunk(args):
    key, f0, f1, out = args
    if key not in LANGS:
        _init(key)
    TL = Timeline(LANGS[key])
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-profile:v", "high", "-pix_fmt", "yuv420p",
           str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(f0, f1):
        p.stdin.write(compose(TL, n / FPS).tobytes())
    p.stdin.close()
    p.wait()
    return out


def render_video(key, out, workers=2):
    _init(key)
    TL = Timeline(LANGS[key])
    tmp = REEL / "build" / f"chunks_{key}"
    tmp.mkdir(parents=True, exist_ok=True)
    b = [round(TL.n * i / workers) for i in range(workers + 1)]
    jobs = [(key, b[i], b[i + 1], tmp / f"c{i}.mp4") for i in range(workers)]
    with Pool(workers) as pool:
        parts = pool.map(_chunk, jobs)
    (tmp / "list.txt").write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(tmp / "list.txt"),
                    "-c", "copy", str(out)], check=True)
    return TL


def preview(key, times, out):
    _init(key)
    TL = Timeline(LANGS[key])
    ims = [compose(TL, t).resize((360, 640)) for t in times]
    cols = min(6, len(ims))
    rows = math.ceil(len(ims) / cols)
    sheet = Image.new("RGB", (360 * cols, 640 * rows))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * 360, (i // cols) * 640))
    sheet.save(out, quality=88)


if __name__ == "__main__":
    key = sys.argv[1]
    if "--preview" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--preview") + 1:]]
        preview(key, ts, REEL / "build" / f"preview_{key}.jpg")
    else:
        render_video(key, REEL / "build" / f"picture_{key}.mp4")
