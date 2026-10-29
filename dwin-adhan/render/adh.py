"""Dwin 9:16 short: the numbers in the adhan (ar / ckb / kmr). Photo-free design: paper, drawn minaret, counters.

  python3 adh.py timeline ar          build/ar/timeline.json + captions
  python3 adh.py sheet ar             contact sheet
  python3 adh.py render ar            build/ar/picture.mp4 (silent)
  python3 adh.py sound ar             build/ar/mix.wav (voice + soft ambience + SFX, no music)
  python3 adh.py finish ar            output/dwin_adhan_ar_9x16.mp4 + .srt
"""
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PROJ = Path(__file__).resolve().parents[1]
REPO = PROJ.parent
sys.path.insert(0, str(REPO / "dwin-kurd-youth" / "render"))
sys.path.insert(0, str(REPO / "sheikh-said-vox" / "render"))
from ky import base as B  # noqa: E402
from ky.base import T, clamp01, ease, ease_out, back_out, kit, paste  # noqa: E402

W, H, FPS = 1080, 1920, 24
PAPER = (238, 228, 208)
INK = (34, 30, 24)
GOLD = (196, 158, 92)
OLIVE = (96, 104, 58)
CREAM = (250, 245, 234)
NIGHT = (20, 28, 52)
RTL = {"ar": True, "ckb": True, "kmr": False}
EAST = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
CHANNEL = {"ar": "دوين - العربية", "ckb": "Dween - دوین", "kmr": "Dwîn - Kurmancî"}

ADHAN = (["الله", "أكبر"] * 4 + ["أشهد", "أن", "لا", "إله", "إلا", "الله"] * 2 +
         ["أشهد", "أن", "محمدًا", "رسول", "الله"] * 2 + ["حي", "على", "الصلاة"] * 2 + ["حي", "على", "الفلاح"] * 2 +
         ["الله", "أكبر"] * 2 + ["لا", "إله", "إلا", "الله"])
LETTERS = ["ا", "ل", "ه", "ك", "ب", "ر", "ش", "د", "ن", "م", "ح", "س", "و", "ي", "ع", "ص", "ف"]
PRAYERS = [("الفجر", 2), ("الظهر", 4), ("العصر", 4), ("المغرب", 3), ("العشاء", 4)]
assert len(ADHAN) == 50 and len(LETTERS) == 17


def dg(lang, n):
    return str(n).translate(EAST) if lang in ("ar", "ckb") else str(n)


def AR(text, size, colour):
    """Arabic liturgical text (the adhan, letters, prayer names) always in Aljazeera, RTL."""
    return T("ar", text, size, colour, True)


# ------------------------------------------------------------------ timeline
PRE, POST = 0.35, 0.6


def timeline(lang):
    loc = json.loads((PROJ / "locales" / f"{lang}.json").read_text(encoding="utf-8"))["scenes"]
    vo = PROJ / "build" / lang / "vo"
    parts = json.loads((vo / "parts.json").read_text())
    sw = json.loads((vo / "words.json").read_text(encoding="utf-8"))
    scenes, t = [], 0.0
    for sid in sorted(loc):
        d = parts[sid]["dur"]
        post = 1.2 if sid == "scene09" else POST
        script = loc[sid]["narration"].split()
        rec = sw[sid]
        toks = script if len(script) == len(rec) else [w["text"] for w in rec]
        words = [dict(text=x, s=round(PRE + w["start"], 3), e=round(PRE + w["end"], 3)) for x, w in zip(toks, rec)]
        scenes.append(dict(id=sid, start=round(t, 3), dur=round(PRE + d + post, 3), headline=loc[sid]["headline"],
                           audio=dict(start=PRE, dur=d), words=words))
        t += PRE + d + post
    scenes.append(dict(id="END", start=round(t, 3), dur=3.5, headline="", audio=None, words=[]))
    t += 3.5
    tl = dict(lang=lang, total=round(t, 3), scenes=scenes)
    sys.path.insert(0, str(REPO / "dwin-kurd-youth" / "render"))
    from ky.timeline import captions, write_srt
    out = PROJ / "build" / lang
    (out / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "cues.json").write_text(json.dumps(captions(tl, 26), ensure_ascii=False), encoding="utf-8")
    write_srt(tl, out / f"adhan_{lang}.srt")
    print(lang, f"{t:.1f}s")


# ------------------------------------------------------------------ drawing helpers
_cache = {}


def cached(key, fn):
    if key not in _cache:
        _cache[key] = fn()
    return _cache[key]


def paper(seed=1):
    return cached(("paper", seed), lambda: kit.paper(W, H, seed=seed, tone=PAPER, vign=0.16)).copy()


def gradient(top, bot, key):
    def build():
        y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        a = np.array(top, np.float32)[None, None, :] * (1 - y) + np.array(bot, np.float32)[None, None, :] * y
        arr = np.repeat(a, W, axis=1)
        im = Image.fromarray(arr.clip(0, 255).astype(np.uint8)).convert("RGBA")
        return B.grain(im, 0.0, 5)
    return cached(("grad", key), build).copy()


def minaret(h, colour):
    """Simple mosque silhouette: dome, minaret with balcony and crescent."""
    w = int(h * 0.9)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = tuple(colour) + (255,)
    mx = int(w * 0.72)
    mw = int(h * 0.06)
    d.rectangle([mx - mw, int(h * 0.22), mx + mw, h], fill=c)                       # shaft
    d.rectangle([mx - mw * 1.8, int(h * 0.36), mx + mw * 1.8, int(h * 0.39)], fill=c)  # balcony
    d.rectangle([mx - mw * 1.4, int(h * 0.60), mx + mw * 1.4, int(h * 0.62)], fill=c)
    d.polygon([(mx - mw, int(h * 0.22)), (mx + mw, int(h * 0.22)), (mx, int(h * 0.10))], fill=c)  # cone
    r = int(h * 0.028)
    cy = int(h * 0.07)
    d.ellipse([mx - r, cy - r, mx + r, cy + r], fill=c)
    d.ellipse([mx - r + int(r * 0.45), cy - r - 2, mx + r + int(r * 0.45), cy + r - 2], fill=(0, 0, 0, 0))
    # prayer hall + dome
    hx0, hx1 = int(w * 0.05), int(w * 0.62)
    d.rectangle([hx0, int(h * 0.68), hx1, h], fill=c)
    dc = (hx0 + hx1) // 2
    dr = int((hx1 - hx0) * 0.34)
    d.ellipse([dc - dr, int(h * 0.68) - dr * 1.4, dc + dr, int(h * 0.68) + dr * 0.6], fill=c)
    d.polygon([(dc - 6, int(h * 0.68) - dr * 1.4), (dc + 6, int(h * 0.68) - dr * 1.4), (dc, int(h * 0.68) - dr * 1.75)],
              fill=c)
    # window arches cut out
    for k in range(3):
        ax = hx0 + int((hx1 - hx0) * (0.25 + 0.25 * k))
        d.rounded_rectangle([ax - 18, int(h * 0.80), ax + 18, int(h * 0.92)], 18, fill=(0, 0, 0, 0))
    return im


def stars(seed, n=140):
    def build():
        rng = np.random.default_rng(seed)
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        for _ in range(n):
            x, y = rng.uniform(0, W), rng.uniform(0, H * 0.65)
            r = rng.choice([1, 1, 1.5, 2, 2.5])
            a = int(rng.uniform(90, 230))
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 250, 230, a))
        return im
    return cached(("stars", seed), build)


def headline_box(lang, text, t, t0=0.15, y=330, colour=INK, box=GOLD):
    key = ("hl", lang, text)

    def build():
        lines = B.text_lines(lang, text, 92 if lang != "kmr" else 80, W - 200, colour, True)
        st = B.stack(lines, 0.1, "center")
        bw, bh = st.width + 80, int(st.height * 0.95) + 50
        im = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([24, 28, bw + 14, bh + 18], 22, fill=(0, 0, 0, 70))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
        ImageDraw.Draw(im).rounded_rectangle([10, 10, bw + 10, bh + 10], 22, fill=tuple(box) + (255,))
        im.alpha_composite(st, (10 + (bw - st.width) // 2, 10 + (bh - st.height) // 2 - 4))
        return im
    im = cached(key, build)
    k = back_out((t - t0) / 0.5, 1.3)
    if k <= 0:
        return None
    s = 0.85 + 0.15 * k
    im2 = im.resize((int(im.width * s), int(im.height * s)), Image.BILINEAR) if s < 0.999 else im
    return im2, clamp01(k * 1.6), y


def put_headline(f, lang, text, t, **kw):
    r = headline_box(lang, text, t, **kw)
    if r:
        im, a, y = r
        paste(f, im, W / 2 - im.width / 2, y, a)


def big_num(lang, n, size, colour):
    return cached(("num", lang, n, size, colour), lambda: T(lang if lang != "kmr" else "kmr", dg(lang, n), size, colour, True))


def word_t(sc, i):
    ws = sc["words"]
    if not ws:
        return 0.5
    return ws[max(-len(ws), min(i, len(ws) - 1))]["s"]


def frac(sc, u):
    a = sc["audio"]
    return a["start"] + a["dur"] * u


# ------------------------------------------------------------------ scenes
def scene01(sc, lang, t):
    f = gradient((40, 34, 52), (214, 140, 72), "dusk")
    m = cached(("min", 900, "ink"), lambda: minaret(900, (28, 22, 30)))
    u = t / sc["dur"]
    s = 1.0 + 0.04 * u
    m2 = m.resize((int(m.width * s), int(m.height * s)), Image.BILINEAR)
    paste(f, m2, W / 2 - m2.width / 2, H - m2.height - 120)
    sun = cached(("sun",), lambda: B.radial_img(700, 700, (255, 200, 120)))
    paste(f, sun, W * 0.5 - 350, H * 0.52 - 350, 0.55)
    put_headline(f, lang, sc["headline"], t)
    return f


def phone_icon(w):
    h = int(w * 1.9)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 48, fill=INK + (255,))
    d.rounded_rectangle([18, 40, w - 19, h - 40], 26, fill=(60, 56, 50, 255))
    cx, cy = w / 2, h / 2
    d.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], fill=CREAM + (230,))
    d.polygon([(cx - 22, cy - 36), (cx - 22, cy + 36), (cx + 38, cy)], fill=INK + (255,))
    return im


def _adhan_card():
    w, h = 820, 780
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 40, fill=CREAM + (255,), outline=GOLD + (255,), width=8)
    d.rounded_rectangle([26, 26, w - 27, h - 27], 28, outline=OLIVE + (160,), width=3)
    for k, line in enumerate(("الله أكبر", "حي على الصلاة", "حي على الفلاح")):
        tx = AR(line, 96 if k == 0 else 76, INK if k == 0 else OLIVE)
        im.alpha_composite(tx, ((w - tx.width) // 2, 150 + k * 190))
    return im


def scene02(sc, lang, t):
    f = paper(2)
    ph = cached(("adcard",), lambda: _adhan_card())
    k = ease_out((t - 0.2) / 0.6)
    paste(f, B.shadowed(ph, 14), W / 2 - ph.width / 2 - 42, 640 + (1 - k) * 80, k)
    # numbers floating out of the phone
    t_c = frac(sc, 0.65)
    for i in range(6):
        ki = ease_out((t - t_c - i * 0.18) / 0.5)
        if ki > 0:
            n = big_num(lang, i + 1, 110, GOLD if i % 2 else OLIVE)
            ang = -0.9 + i * 0.36
            r = 330 + 40 * ki
            x = W / 2 + math.cos(ang - math.pi / 2) * r * (1 if not RTL[lang] else -1) * 0 + (i - 2.5) * 150
            y = 640 + 400 - math.sin(ang + 1.6) * 0 - 520 * ki + (i % 2) * 60
            paste(f, n, x - n.width / 2, y, clamp01(ki * 1.5))
    put_headline(f, lang, sc["headline"], t)
    return f


def chip(word, n, lang, on):
    def build(on=on):
        w, h = 186, 92
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([2, 2, w - 3, h - 3], 16, fill=(CREAM if not on else GOLD) + (255,), outline=INK + (180,),
                            width=2)
        tx = B.fit_w(AR(word, 40, INK), w - 50)
        im.alpha_composite(tx, ((w - tx.width) // 2 + 10, (h - tx.height) // 2 + 2))
        nn = T(lang if lang != "kmr" else "kmr", dg(lang, n), 20, (110, 100, 86), True)
        im.alpha_composite(nn, (8, 4))
        return im
    return cached(("chip", word, n, lang, on), build)


def scene03(sc, lang, t):
    f = paper(3)
    t0, t1 = 0.3, sc["dur"] - 1.4
    cols, rows = 5, 10
    x0, y0, gx, gy = 62, 530, 192, 84
    n_on = int(clamp01((t - t0) / (t1 - t0)) * 50 + 0.0001)
    for i, wd in enumerate(ADHAN):
        r, cidx = divmod(i, cols)
        cidx = cols - 1 - cidx          # Arabic reading order: right to left
        if i < n_on:
            last = i == n_on - 1
            paste(f, chip(wd, i + 1, lang, last), x0 + cidx * gx, y0 + r * gy)
    if n_on > 0:
        n = big_num(lang, n_on, 120, OLIVE)
        tag = cached(("w50lab", n_on), lambda: None)
        paste(f, n, W / 2 - n.width / 2, 1370)
    put_headline(f, lang, sc["headline"], t)
    return f


def scene04(sc, lang, t):
    f = gradient((10, 14, 34), (40, 52, 92), "night")
    f.alpha_composite(stars(4))
    tw = 0.5 + 0.5 * math.sin(t * 2.0)
    moon = cached(("moon",), lambda: _crescent(220))
    paste(f, moon, W * 0.68, 520, 0.9)
    glow = cached(("mglow",), lambda: B.radial_img(600, 600, (255, 240, 200)))
    paste(f, glow, W * 0.68 + 110 - 300, 630 - 300, 0.12 + 0.04 * tw)
    t_d = word_t(sc, -3)
    u = clamp01((t - t_d) / 1.4)
    val = 50 if u <= 0 else int(round(50 - 45 * ease(u)))
    n = T(lang if lang != "kmr" else "kmr", dg(lang, val), 320, CREAM, True)
    paste(f, n, W / 2 - n.width / 2, 980, ease((t - 0.6) / 0.6))
    if u >= 1:
        sub = T(lang if lang != "kmr" else "kmr", f"{dg(lang, 50)}  →  {dg(lang, 5)}" if not RTL[lang]
                else f"{dg(lang, 5)}  ←  {dg(lang, 50)}", 64, GOLD, True)
        paste(f, sub, W / 2 - sub.width / 2, 1330, ease((t - t_d - 1.4) / 0.5))
    put_headline(f, lang, sc["headline"], t, box=CREAM)
    return f


def _crescent(r):
    im = Image.new("RGBA", (r * 2, r * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=(250, 238, 200, 255))
    d.ellipse([int(r * 0.45), -int(r * 0.1), int(r * 0.45) + 2 * r, 2 * r - int(r * 0.1)], fill=(0, 0, 0, 0))
    return im


def scene05(sc, lang, t):
    f = paper(5)
    # times of the five numbers: the 5 words after the colon
    ws = sc["words"]
    idx = [i for i, w in enumerate(ws) if w["text"].endswith((":",))]
    start = idx[0] + 1 if idx else int(len(ws) * 0.35)
    tn = [ws[min(start + k, len(ws) - 1)]["s"] for k in range(5)]
    y = 560
    total = 0
    for k, (name, n) in enumerate(PRAYERS):
        a = ease_out((t - tn[k] + 0.15) / 0.4)
        if a <= 0:
            y += 150
            continue
        row = Image.new("RGBA", (W - 140, 120), (0, 0, 0, 0))
        d = ImageDraw.Draw(row)
        d.rounded_rectangle([0, 0, row.width - 1, 119], 20, fill=CREAM + (255,), outline=INK + (90,), width=2)
        nm = AR(name, 54, INK)
        row.alpha_composite(nm, (row.width - nm.width - 30, 60 - nm.height // 2))
        for j in range(n):
            cx = 70 + j * 92
            d.ellipse([cx - 30, 30, cx + 30, 90], fill=(OLIVE if j < n else CREAM) + (255,))
        nn = T(lang if lang != "kmr" else "kmr", dg(lang, n), 64, GOLD, True)
        row.alpha_composite(nn, (70 + 4 * 92 + 10, 60 - nn.height // 2))
        paste(f, row, 70 + (1 - a) * 60, y, a)
        total += n
        y += 150
    t_sum = word_t(sc, -3)
    k = back_out((t - t_sum) / 0.5, 1.6)
    if k > 0:
        n = big_num(lang, 17, 190, OLIVE)
        eq = T("kmr", "=", 140, INK, True)
        paste(f, eq, W / 2 - n.width / 2 - eq.width - 10, 1250, clamp01(k))
        paste(f, n, W / 2 - n.width / 2 + 40, 1230, clamp01(k))
    put_headline(f, lang, sc["headline"], t)
    return f


def scene06(sc, lang, t):
    f = paper(6)
    cols = 6
    gx, gy, x0, y0 = 160, 170, 60, 590
    t0, t1 = 0.4, frac(sc, 0.95)
    n_on = int(clamp01((t - t0) / (t1 - t0)) * 17 + 0.0001)
    for i, L in enumerate(LETTERS[:n_on]):
        r, cidx = divmod(i, cols)
        cidx = cols - 1 - cidx
        tile = cached(("tile", L), lambda L=L: _tile(L))
        paste(f, tile, x0 + cidx * gx, y0 + r * gy)
    if n_on:
        n = big_num(lang, n_on, 160, GOLD)
        paste(f, n, W / 2 - n.width / 2, 1290)
    put_headline(f, lang, sc["headline"], t)
    return f


def _tile(L):
    im = Image.new("RGBA", (146, 146), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([2, 2, 143, 143], 22, fill=CREAM + (255,), outline=OLIVE + (255,), width=4)
    g = AR(L, 90, INK)
    im.alpha_composite(g, ((146 - g.width) // 2, (146 - g.height) // 2 - 6))
    return im


VARIANTS = [(50, None), (58, "الصلاة خير من النوم ×٢"), (72, "الترجيع")]


def scene07(sc, lang, t):
    f = paper(7)
    ts = [frac(sc, 0.05), frac(sc, 0.35), frac(sc, 0.55)]
    y = 680
    for k, (n, label) in enumerate(VARIANTS):
        a = ease_out((t - ts[k]) / 0.5)
        if a <= 0:
            continue
        def build(n=n, label=label, k=k):
            cw, ch = W - 220, 220
            im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.rounded_rectangle([0, 0, cw - 1, ch - 1], 26, fill=(CREAM if k else GOLD) + (255,), outline=INK + (110,),
                                width=3)
            nn = T(lang if lang != "kmr" else "kmr", dg(lang, n), 130, INK, True)
            if RTL[lang]:
                im.alpha_composite(nn, (cw - nn.width - 40, ch // 2 - nn.height // 2))
            else:
                im.alpha_composite(nn, (40, ch // 2 - nn.height // 2))
            if label:
                lb = B.fit_w(AR(label, 46, (90, 82, 70)), cw - nn.width - 120)
                x = 40 if RTL[lang] else cw - lb.width - 40
                im.alpha_composite(lb, (x, ch // 2 - lb.height // 2))
            return B.shadowed(im, 10, (6, 9), 70)
        card = cached(("var", lang, k), build)
        paste(f, card, W / 2 - card.width / 2 + (1 - a) * (80 if k % 2 else -80), y, a)
        y += 250
    # the "?" stamp
    put_headline(f, lang, sc["headline"], t)
    return f


def scene08(sc, lang, t):
    f = gradient((236, 226, 204), (210, 196, 166), "warm")
    m = cached(("min", 760, "olive"), lambda: minaret(760, OLIVE))
    cx, cy = W * 0.5 + m.width * 0.22, H - 760 - 90 + 760 * 0.12
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k in range(5):                                # the call spreading out
        r = ((t * 120) + k * 170) % 850
        a = int(150 * (1 - r / 850))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD + (a,), width=5)
    f.alpha_composite(lay)
    paste(f, m, W / 2 - m.width / 2, H - m.height - 90)
    put_headline(f, lang, sc["headline"], t)
    return f


def scene09(sc, lang, t):
    u = clamp01(t / sc["dur"])
    f = gradient((70, 84, 120), (238, 186, 120), "dawn")
    sun = cached(("sun2",), lambda: B.radial_img(900, 900, (255, 214, 150)))
    paste(f, sun, W / 2 - 450, H * 0.66 - 450 - 160 * ease(u), 0.7)
    m = cached(("min", 980, "ink2"), lambda: minaret(980, (40, 36, 44)))
    paste(f, m, W / 2 - m.width / 2, H - m.height - 60)
    put_headline(f, lang, sc["headline"], t, box=CREAM)
    return f


def end(sc, lang, t):
    f = paper(10)
    lg = cached(("endlogo", lang), lambda: kit.logo(lang, False, 300, 1.0))
    k = ease_out(t / 0.7)
    paste(f, lg, W / 2 - lg.width / 2, 620 + (1 - k) * 30, k)
    ch = cached(("endch", lang), lambda: T(lang, CHANNEL[lang], 64, INK, True))
    paste(f, ch, W / 2 - ch.width / 2, 620 + lg.height + 40, ease((t - 0.4) / 0.6))
    return f


SCENES = {f"scene0{i}": globals()[f"scene0{i}"] for i in range(1, 10)}
SCENES["END"] = end


# ------------------------------------------------------------------ film
class Film:
    def __init__(self, lang):
        self.lang = lang
        b = PROJ / "build" / lang
        self.tl = json.loads((b / "timeline.json").read_text(encoding="utf-8"))
        self.cues = json.loads((b / "cues.json").read_text(encoding="utf-8"))
        self.scenes = self.tl["scenes"]
        self.n = int(round(self.tl["total"] * FPS))
        self.ci = 0
        self.last = {}

    def scene_at(self, t):
        for i, s in enumerate(self.scenes):
            if t < s["start"] + s["dur"]:
                return i
        return len(self.scenes) - 1

    def content(self, i, tr):
        sc = self.scenes[i]
        return SCENES[sc["id"]](sc, self.lang, tr).convert("RGBA")

    def frame(self, fn):
        t = fn / FPS
        i = self.scene_at(t)
        sc = self.scenes[i]
        tr = t - sc["start"]
        f = self.content(i, tr)
        if i > 0 and tr < 0.5:
            if i - 1 not in self.last:
                self.last = {i - 1: self.content(i - 1, self.scenes[i - 1]["dur"] - 1 / FPS)}
            f = Image.blend(self.last[i - 1], f, ease(tr / 0.5))
        if i == 0 and tr < 0.5:
            f = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), f, ease(tr / 0.5))
        f = B.grain(f, t, 5)
        if sc["id"] != "END":
            self.logo(f)
        self.caption(f, t)
        return f.convert("RGB")

    def logo(self, f):
        x, y, w = 40, 150, 70
        h = int(w * 1.54)
        reg = float(np.asarray(f.crop((x, y, x + w, y + h)).convert("L")).mean())
        dark = reg < 120
        paste(f, kit.logo(self.lang, dark, w, 0.85), x, y)

    def caption(self, f, t):
        cues = self.cues
        while self.ci < len(cues) - 1 and cues[self.ci]["end"] < t:
            self.ci += 1
        while self.ci > 0 and cues[self.ci]["start"] > t:
            self.ci -= 1
        cue = cues[self.ci]
        if not (cue["start"] <= t < cue["end"]):
            return
        hi = max([j for j, w in enumerate(cue["words"]) if w["s"] <= t + 0.02] or [-1])
        im = cached(("cap", self.lang, self.ci, hi), lambda: self.cap_img(cue, hi))
        a = min(clamp01((t - cue["start"]) / 0.1), clamp01((cue["end"] - t) / 0.1))
        paste(f, im, W / 2 - im.width / 2, 1640 - im.height, a)

    def cap_img(self, cue, hi):
        size = 50
        ims = [T(self.lang, w["text"], size, GOLD if j == hi else CREAM, True) for j, w in enumerate(cue["words"])]
        sp = size * 0.3
        lines, cur, cw = [], [], 0
        for im in ims:
            if cur and cw + im.width - 12 + sp > W - 100:
                lines.append(cur)
                cur, cw = [], 0
            cur.append(im)
            cw += im.width - 12 + sp
        if cur:
            lines.append(cur)
        lis = []
        for ln in lines:
            order = ln[::-1] if RTL[self.lang] else ln
            w = int(sum(i.width - 12 for i in order) + sp * (len(order) - 1) + 12)
            h = max(i.height for i in order)
            li = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            x = 0
            for i in order:
                li.alpha_composite(i, (int(x), (h - i.height) // 2))
                x += i.width - 12 + sp
            lis.append(li)
        lh = int(size * 1.5)
        w = max(i.width for i in lis) + 48
        h = lh * len(lis) + 22
        out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(out).rounded_rectangle([0, 0, w - 1, h - 1], 14, fill=(0, 0, 0, 178))
        for k, li in enumerate(lis):
            out.alpha_composite(li, ((w - li.width) // 2, int(11 + k * lh + lh / 2 - li.height / 2)))
        return out


def sheet(lang):
    film = Film(lang)
    ids = [s["id"] for s in film.scenes]
    tw, th = 270, 480
    sh = Image.new("RGB", (len(ids) * (tw + 6), th * 2 + 12), (40, 40, 40))
    for k, s in enumerate(film.scenes):
        for j, fr in enumerate((0.4, 0.9)):
            im = film.frame(int((s["start"] + s["dur"] * fr) * FPS))
            im.thumbnail((tw, th))
            sh.paste(im, (k * (tw + 6), j * (th + 6)))
    out = PROJ / "build" / lang / "sheet.jpg"
    sh.save(out, quality=88)
    print(out)


def render(lang):
    film = Film(lang)
    out = PROJ / "build" / lang / "picture.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                          "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
    t0 = time.time()
    for fn in range(film.n):
        p.stdin.write(film.frame(fn).tobytes())
    p.stdin.close()
    p.wait()
    print(lang, "picture", f"{(time.time() - t0) / 60:.1f} min")


# ------------------------------------------------------------------ sound: voice + room tone + soft SFX, no music
def sound(lang):
    from scipy.io import wavfile
    from vox import sound as V
    from vox.sound import SR, Bus, lp
    tl = json.loads((PROJ / "build" / lang / "timeline.json").read_text(encoding="utf-8"))
    total = tl["total"]
    voice, fx = Bus(total), Bus(total)
    parts = PROJ / "build" / lang / "vo" / "parts"
    for s in tl["scenes"]:
        if s["audio"]:
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(parts / f"{s['id']}.wav"), "-f", "f32le", "-ac", "1",
                                  "-ar", str(SR), "-"], capture_output=True, check=True).stdout
            voice.put(np.frombuffer(raw, np.float32).astype(np.float64), s["start"] + s["audio"]["start"])
    rng = np.random.default_rng(5)
    n = int(total * SR)
    room = lp(rng.standard_normal(n), 380, 2) * 0.012
    room = np.stack([room, np.roll(room, 2400)])
    fx.put(room, 0.0)
    S = {s["id"]: s for s in tl["scenes"]}
    for s in tl["scenes"][1:]:
        fx.put(V.rustle(0.45, 35) * 0.25, s["start"], 1.0, 0.15)
    for sid, count, key in (("scene03", 50, "w"), ("scene06", 17, "l")):
        s = S[sid]
        t0, t1 = (0.3, s["dur"] - 1.4) if key == "w" else (0.4, s["audio"]["start"] + s["audio"]["dur"] * 0.95)
        for k in range(count):
            fx.put(V.tick_click(0.18 if key == "w" else 0.3), s["start"] + t0 + (t1 - t0) * (k + 1) / count, 1.0,
                   (k % 5 - 2) / 6)
    for k in range(5):
        fx.put(V.pop() * 0.25, S["scene05"]["start"] + S["scene05"]["words"][min(len(S["scene05"]["words"]) - 1, 5 + k)]["s"])
    fx.put(V.swell(1.4) * 0.3, S["scene04"]["start"] + 0.2)
    fx.put(V.swell(1.8) * 0.3, S["scene09"]["start"] + 0.2)
    m = voice.x[:, :n] + fx.x[:, :n] * 0.55
    fo = int(1.2 * SR)
    m[:, -fo:] *= np.linspace(1, 0, fo)
    m = m * (0.8 / float(np.abs(m).max()))
    out = PROJ / "build" / lang / "mix.wav"
    wavfile.write(out, SR, m.T.astype(np.float32))
    print(out)


def finish(lang):
    from vox.finish import loudnorm
    b = PROJ / "build" / lang
    (PROJ / "output").mkdir(exist_ok=True)
    aac = b / "mix.m4a"
    loudnorm(b / "mix.wav", aac)
    final = PROJ / "output" / f"dwin_adhan_{lang}_9x16.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(b / "picture.mp4"), "-i", str(aac), "-map", "0:v", "-map",
                    "1:a", "-c:v", "copy", "-c:a", "copy", "-movflags", "+faststart", str(final)], check=True)
    import shutil
    shutil.copy(b / f"adhan_{lang}.srt", PROJ / "output" / f"dwin_adhan_{lang}.srt")
    print(final)


if __name__ == "__main__":
    {"timeline": timeline, "sheet": sheet, "render": render, "sound": sound, "finish": finish}[sys.argv[1]](sys.argv[2])
