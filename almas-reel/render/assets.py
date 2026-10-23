"""Footage crops, drawn illustrative shots and logo variants for the Almas reel (1080x1920)."""
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
REEL = HERE.parent
REPO = REEL.parent
FOOT = REEL / "footage"
CACHE = REEL / "build" / "shots"
W, H = 1080, 1920

GOLD = (201, 164, 92)
GREEN = (15, 42, 31)
CREAM = (245, 238, 220)
INK = (15, 42, 31)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------------ logos
def logo_dark(key):
    """Logo variant for dark backgrounds: olive text/leaves -> cream, gold -> brand gold."""
    out = REEL / "build" / f"logo_dark_{key}.png"
    if out.exists():
        return Image.open(out)
    im = Image.open(REPO / "brand" / f"logo_{key}.png").convert("RGBA")
    a = np.asarray(im).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    olive = (r - b) < 32
    a[olive, 0], a[olive, 1], a[olive, 2] = CREAM
    gold = ~olive
    a[gold, 0], a[gold, 1], a[gold, 2] = GOLD
    out.parent.mkdir(parents=True, exist_ok=True)
    img = Image.fromarray(a.astype(np.uint8), "RGBA")
    img.save(out)
    return img


# ------------------------------------------------------------------ footage
def _load(name):
    return Image.open(FOOT / name).convert("RGB")


CROPS = {
    # name: (file, box) in the 568x1054 screenshots; app UI and HOKAR's caption bubble are left out
    "hokar_presenter": ("01-commentary-hokar-01.jpg", (0, 112, 568, 456)),
    "hokar_presenter2": ("01-commentary-hokar-04.jpg", (0, 112, 568, 456)),
    "hokar_jar": ("01-commentary-hokar-06.jpg", (20, 462, 568, 684)),
    "hokar_adv_a": ("01-commentary-hokar-02.jpg", (20, 462, 568, 684)),
    "hokar_adv_b": ("01-commentary-hokar-05.jpg", (20, 462, 568, 684)),
    "hokar_jar_label": ("01-commentary-hokar-06.jpg", (300, 462, 568, 640)),
    "hokar_street": ("01-commentary-hokar-03.jpg", (0, 200, 300, 400)),
    "k24_market": ("02-kurdistan24-report-01.jpg", (0, 0, 568, 900)),
    "k24_speaker": ("02-kurdistan24-report-02.jpg", (0, 0, 568, 900)),
    "k24_speaker2": ("02-kurdistan24-report-04.jpg", (0, 0, 568, 900)),
    "k24_stall": ("02-kurdistan24-report-05.jpg", (0, 0, 568, 900)),
    "k24_bottle": ("02-kurdistan24-report-01.jpg", (60, 520, 568, 905)),
    "hariri_1": ("03-fakhir-hariri-clarification-01.jpg", (0, 0, 568, 900)),
    "hariri_2": ("03-fakhir-hariri-clarification-03.jpg", (0, 0, 568, 900)),
    "hariri_3": ("03-fakhir-hariri-clarification-04.jpg", (0, 0, 568, 900)),
    "hariri_4": ("03-fakhir-hariri-clarification-06.jpg", (0, 0, 568, 900)),
}


def footage_frame(crop, fill="width", y_center=None):
    """Compose a 1080x1920 frame: the crop fitted to the width over a blurred, darkened copy of itself."""
    bg = crop.copy()
    s = max(W / bg.width, H / bg.height)
    bg = bg.resize((int(bg.width * s) + 2, int(bg.height * s) + 2), Image.BILINEAR)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = bg.filter(ImageFilter.GaussianBlur(38))
    bg = Image.fromarray((np.asarray(bg).astype(np.float32) * 0.45).astype(np.uint8))
    s = W / crop.width
    fg = crop.resize((W, int(crop.height * s)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
    y = (H - fg.height) // 2 if y_center is None else int(y_center - fg.height / 2)
    y = max(0, min(H - fg.height, y))
    # soft top/bottom edges so the footage melts into the blurred fill
    m = Image.new("L", fg.size, 255)
    if fg.height < H:
        md = np.ones((fg.height, 1), np.float32)
        e = min(40, fg.height // 8)
        md[:e, 0] = np.linspace(0, 1, e)
        md[-e:, 0] = np.linspace(1, 0, e)
        m = Image.fromarray((np.repeat(md, fg.width, 1) * 255).astype(np.uint8))
    bg.paste(fg, (0, y), m)
    return bg


def footage(name):
    f, box = CROPS[name]
    crop = _load(f).crop(box)
    if crop.width / crop.height > 1.0:      # landscape panel: place it in the upper-middle of the frame
        return footage_frame(crop, y_center=760)
    return footage_frame(crop)


# ------------------------------------------------------------------ drawn (illustrative) shots
def _grad(top, bottom):
    y = np.linspace(0, 1, H)[:, None, None]
    arr = np.array(top, np.float32) * (1 - y) + np.array(bottom, np.float32) * y
    return Image.fromarray(np.repeat(arr, W, 1).astype(np.uint8), "RGB")


def _glow(img, cx, cy, r, col, strength=0.6):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.clip(1 - np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / r, 0, 1) ** 2 * strength
    a = np.asarray(img).astype(np.float32)
    a = a + (np.array(col, np.float32) - a) * d[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def _jar(d, cx, cy, w, body=(236, 232, 224), lid=(210, 206, 198), label=None, outline=None):
    h = w * 0.62
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], int(w * 0.08), fill=body, outline=outline,
                        width=3 if outline else 0)
    d.rounded_rectangle([cx - w * 0.52, cy - h / 2 - w * 0.2, cx + w * 0.52, cy - h / 2 + w * 0.02], int(w * 0.05),
                        fill=lid)
    if label:
        d.rectangle([cx - w * 0.38, cy - h * 0.18, cx + w * 0.38, cy + h * 0.26], fill=label)


def _phone(d, cx, cy, w, screen=(26, 30, 34), frame=(12, 14, 16)):
    h = w * 2.05
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], int(w * 0.13), fill=frame)
    d.rounded_rectangle([cx - w / 2 + 16, cy - h / 2 + 16, cx + w / 2 - 16, cy + h / 2 - 16], int(w * 0.1), fill=screen)
    return (cx - w / 2 + 16, cy - h / 2 + 16, cx + w / 2 - 16, cy + h / 2 - 16)


def _hand(d, x, y, s, col=(196, 150, 118), sleeve=(40, 52, 60), angle=0.0):
    """Simple stylised hand coming in from below/right (no face, no identity)."""
    pts = [(x, y), (x + 70 * s, y - 20 * s), (x + 170 * s, y + 10 * s), (x + 190 * s, y + 70 * s),
           (x + 120 * s, y + 110 * s), (x + 20 * s, y + 90 * s)]
    d.polygon(pts, fill=col)
    for i in range(4):
        fx = x + 40 * s + i * 34 * s
        d.rounded_rectangle([fx, y - 55 * s + i * 6 * s, fx + 26 * s, y + 15 * s], int(12 * s), fill=col)
    d.polygon([(x + 120 * s, y + 110 * s), (x + 190 * s, y + 70 * s), (x + 420 * s, y + 360 * s),
               (x + 300 * s, y + 470 * s)], fill=sleeve)


def drawn(name):
    if name == "phone_feed":
        img = _grad((24, 30, 34), (10, 14, 16))
        img = _glow(img, 540, 900, 700, (60, 80, 90), 0.4)
        d = ImageDraw.Draw(img)
        x0, y0, x1, y1 = _phone(d, 540, 900, 560)
        for i in range(5):
            yy = y0 + 40 + i * 230
            d.rounded_rectangle([x0 + 24, yy, x1 - 24, yy + 200], 18, fill=(52, 58, 64))
            d.ellipse([x0 + 40, yy + 20, x0 + 100, yy + 80], fill=(95, 100, 106))   # blurred avatar
            d.rounded_rectangle([x0 + 120, yy + 30, x0 + 330, yy + 50], 10, fill=(90, 96, 102))
            d.rounded_rectangle([x0 + 40, yy + 100, x1 - 60, yy + 170], 12, fill=(78, 84, 90))
        img = img.filter(ImageFilter.GaussianBlur(5))      # everything on the screen stays unreadable
        return img
    if name == "lab":
        img = _grad((18, 46, 36), (8, 22, 18))
        img = _glow(img, 540, 760, 650, (60, 110, 90), 0.5)
        d = ImageDraw.Draw(img)
        glass = (150, 200, 185)
        for cx, h, w in [(330, 420, 170), (560, 560, 210), (790, 380, 150)]:
            base = 1150
            d.polygon([(cx - w * 0.18, base - h), (cx + w * 0.18, base - h), (cx + w * 0.18, base - h * 0.55),
                       (cx + w / 2, base), (cx - w / 2, base), (cx - w * 0.18, base - h * 0.55)], outline=glass, width=6)
            d.polygon([(cx - w * 0.36, base - h * 0.2), (cx + w * 0.36, base - h * 0.2), (cx + w / 2 - 6, base - 6),
                       (cx - w / 2 + 6, base - 6)], fill=(70, 150, 125))
            d.line([(cx - w * 0.24, base - h), (cx + w * 0.24, base - h)], fill=glass, width=8)
        d.rectangle([140, 1150, 940, 1170], fill=(40, 70, 60))
        return img.filter(ImageFilter.GaussianBlur(1.2))
    if name == "pharmacy":
        img = _grad((236, 240, 236), (196, 210, 204))
        d = ImageDraw.Draw(img)
        for row in range(5):                       # shelves with plain boxes
            y = 330 + row * 150
            d.rectangle([60, y + 110, 1020, y + 122], fill=(170, 180, 176))
            for i in range(9):
                bx = 80 + i * 104
                c = [(220, 226, 230), (206, 222, 214), (230, 222, 206)][(i + row) % 3]
                d.rectangle([bx, y + 20, bx + 84, y + 110], fill=c, outline=(180, 186, 184))
        cx, cy = 540, 200                           # green cross sign
        d.rounded_rectangle([cx - 90, cy - 90, cx + 90, cy + 90], 20, fill=(255, 255, 255))
        d.rectangle([cx - 22, cy - 66, cx + 22, cy + 66], fill=(0, 150, 80))
        d.rectangle([cx - 66, cy - 22, cx + 66, cy + 22], fill=(0, 150, 80))
        d.rectangle([0, 1120, W, H], fill=(214, 200, 176))                   # counter
        d.rectangle([0, 1120, W, 1150], fill=(190, 174, 148))
        return img.filter(ImageFilter.GaussianBlur(1.0))
    if name == "pharmacy_handover":
        img = drawn("pharmacy")
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([430, 980, 700, 1150], 10, fill=(250, 250, 248), outline=(150, 160, 160), width=4)
        d.rectangle([450, 1040, 680, 1060], fill=(0, 150, 80))
        _hand(d, 640, 1060, 1.1, col=(205, 160, 126), sleeve=(240, 244, 244))      # pharmacist (white coat)
        img = _glow(img, 540, 900, 900, (255, 230, 190), 0.25)
        return img
    if name == "law_doc":
        img = _grad((236, 232, 220), (214, 208, 194))
        d = ImageDraw.Draw(img)
        d.rectangle([120, 160, 960, 1760], fill=(252, 250, 244), outline=(200, 194, 180), width=3)
        rng = np.random.default_rng(4)
        y = 260
        while y < 1680:                             # abstract text lines (no readable text)
            if rng.random() < 0.12:
                y += 40
                continue
            x1 = 900 - rng.uniform(0, 180) if rng.random() < 0.2 else 900
            d.rounded_rectangle([180, y, x1, y + 16], 8, fill=(170, 166, 156))
            y += 46
        return img.filter(ImageFilter.GaussianBlur(1.4))
    if name == "gavel":
        img = _grad((20, 20, 22), (6, 6, 8))
        img = _glow(img, 540, 900, 700, (90, 70, 40), 0.45)
        d = ImageDraw.Draw(img)
        wood, dark = (120, 78, 40), (70, 44, 22)
        d.ellipse([300, 1180, 780, 1300], fill=dark)                           # sound block
        d.rectangle([300, 1150, 780, 1240], fill=wood)
        d.ellipse([300, 1100, 780, 1200], fill=(140, 92, 50))
        cx, cy, ang = 560, 820, -0.5
        def rot(px, py):
            return (cx + (px * math.cos(ang) - py * math.sin(ang)), cy + (px * math.sin(ang) + py * math.cos(ang)))
        d.polygon([rot(-40, -20), rot(380, -20), rot(380, 20), rot(-40, 20)], fill=wood)        # handle
        d.polygon([rot(-170, -90), rot(40, -90), rot(40, 90), rot(-170, 90)], fill=(150, 98, 52))  # head
        d.polygon([rot(-150, -100), rot(-120, -100), rot(-120, 100), rot(-150, 100)], fill=GOLD)
        d.polygon([rot(0, -100), rot(30, -100), rot(30, 100), rot(0, 100)], fill=GOLD)
        return img.filter(ImageFilter.GaussianBlur(1.0))
    if name == "jar_sticker":
        img = _grad((60, 60, 60), (24, 24, 24))
        d = ImageDraw.Draw(img)
        _jar(d, 540, 960, 620, body=(200, 200, 200), lid=(170, 170, 170), label=(240, 240, 240))
        d.polygon([(560, 860), (790, 830), (800, 1010), (600, 1050)], fill=(250, 250, 250))       # sticker peeling
        d.polygon([(790, 830), (860, 780), (880, 950), (800, 1010)], fill=(215, 215, 215))
        return img.filter(ImageFilter.GaussianBlur(2))
    if name == "phone_likes":
        img = _grad((20, 24, 28), (8, 10, 12))
        d = ImageDraw.Draw(img)
        x0, y0, x1, y1 = _phone(d, 540, 960, 560)
        for i in range(6):
            d.ellipse([x1 - 150, y0 + 300 + i * 120, x1 - 70, y0 + 380 + i * 120], fill=(220, 60, 80))
            d.rounded_rectangle([x0 + 50, y0 + 320 + i * 120, x1 - 200, y0 + 352 + i * 120], 12, fill=(80, 86, 92))
        return img.filter(ImageFilter.GaussianBlur(14))
    if name == "phone_mock_ad":
        img = _grad((236, 232, 226), (200, 196, 190))
        d = ImageDraw.Draw(img)
        x0, y0, x1, y1 = _phone(d, 540, 940, 600, screen=(246, 244, 240))
        d.rounded_rectangle([x0 + 30, y0 + 120, x1 - 30, y0 + 820], 24, fill=(232, 220, 236))   # invented product ad
        _jar(d, (x0 + x1) / 2, y0 + 480, 300, body=(250, 246, 252), lid=(200, 170, 210), label=(220, 196, 228))
        for i in range(3):
            d.rounded_rectangle([x0 + 60, y0 + 870 + i * 60, x1 - 60 - i * 80, y0 + 900 + i * 60], 12, fill=(200, 196, 204))
        _hand(d, 640, 1500, 1.2, col=(205, 160, 126), sleeve=(60, 80, 100))
        return img
    if name == "receipt_photo":
        img = _grad((230, 226, 218), (196, 190, 180))
        d = ImageDraw.Draw(img)
        d.polygon([(200, 560), (520, 520), (580, 1300), (260, 1340)], fill=(252, 252, 250))          # receipt
        for i in range(12):
            y = 600 + i * 55
            d.line([(240, y + i * 0), (520, y - 30)], fill=(190, 190, 190), width=8)
        d.rectangle([600, 760, 900, 1200], fill=(240, 236, 228), outline=(170, 160, 150), width=4)  # product box
        d.rectangle([630, 900, 870, 960], fill=(200, 210, 220))
        x0, y0, x1, y1 = _phone(d, 560, 1520, 380, screen=(60, 70, 80))
        d.ellipse([(x0 + x1) / 2 - 50, y1 - 120, (x0 + x1) / 2 + 50, y1 - 20], outline=(240, 240, 240), width=6)
        return img
    if name == "complaint_form":
        img = _grad((226, 230, 228), (190, 198, 196))
        d = ImageDraw.Draw(img)
        d.rectangle([170, 260, 910, 1600], fill=(255, 255, 255), outline=(170, 176, 176), width=3)
        d.rectangle([170, 260, 910, 360], fill=(30, 90, 70))
        for i in range(8):
            y = 440 + i * 130
            d.rounded_rectangle([230, y, 420, y + 24], 10, fill=(150, 156, 156))
            d.rectangle([450, y - 10, 850, y + 44], outline=(150, 156, 156), width=3)
        d.line([(620, 1380), (900, 1100)], fill=(30, 40, 60), width=18)                  # pen
        d.polygon([(610, 1390), (630, 1370), (600, 1410)], fill=(30, 40, 60))
        return img
    raise KeyError(name)


def shot(name):
    """Return a cached 1080x1920 RGB still for a shot name (footage crop or drawn)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f"{name}.png"
    if p.exists():
        return Image.open(p).convert("RGB")
    img = footage(name) if name in CROPS else drawn(name)
    img.save(p)
    return img
