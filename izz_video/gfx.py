"""Drawing helpers: gradients, glows, architecture and figure silhouettes, camera, film look."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1920, 1080          # output frame
CW, CH = 2400, 1350        # world canvas each shot is drawn on (gives room for camera moves)

# palette: sandstone, amber, deep green, bronze
SAND = (214, 180, 130)
AMBER = (236, 160, 72)
GREEN = (30, 66, 54)
BRONZE = (150, 98, 48)
PARCH = (226, 200, 150)


def lerp(a, b, t):
    return a + (b - a) * t


def lerpc(c1, c2, t):
    return tuple(int(round(lerp(a, b, t))) for a, b in zip(c1, c2))


def ease(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ gradients
def vgradient(size, stops):
    """stops: list of (pos 0..1, (r,g,b)). Returns RGBA image."""
    w, h = size
    ys = np.linspace(0, 1, h)
    pos = [p for p, _ in stops]
    cols = np.array([c for _, c in stops], dtype=np.float32)
    rgb = np.stack([np.interp(ys, pos, cols[:, k]) for k in range(3)], axis=1)
    arr = np.repeat(rgb[:, None, :], w, axis=1)
    a = np.full((h, w, 1), 255, np.float32)
    return Image.fromarray(np.concatenate([arr, a], axis=2).astype(np.uint8), "RGBA")


def radial(size, center, radius, color, strength=1.0, falloff=2.0):
    """Soft additive-looking glow as an RGBA layer (alpha carries the falloff)."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((xx - center[0]) ** 2 + (yy - center[1]) ** 2) / radius
    a = np.clip(1 - d, 0, 1) ** falloff * 255 * strength
    arr = np.zeros((h, w, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = color
    arr[..., 3] = np.clip(a, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def glow_sprite(radius, color, falloff=2.0, strength=1.0):
    r = int(radius)
    return radial((2 * r, 2 * r), (r, r), r, color, strength, falloff)


def add_glow(img, sprite, cx, cy, scale=1.0, alpha=1.0):
    """Additive blend of a glow sprite onto an RGB(A) image, in place, returns img."""
    if scale != 1.0:
        sw = max(2, int(sprite.width * scale))
        sprite = sprite.resize((sw, sw), Image.BILINEAR)
    x0, y0 = int(cx - sprite.width / 2), int(cy - sprite.height / 2)
    x1, y1 = x0 + sprite.width, y0 + sprite.height
    bx0, by0, bx1, by1 = max(0, x0), max(0, y0), min(img.width, x1), min(img.height, y1)
    if bx0 >= bx1 or by0 >= by1:
        return img
    base = np.asarray(img.crop((bx0, by0, bx1, by1))).astype(np.float32)
    sp = np.asarray(sprite.crop((bx0 - x0, by0 - y0, bx1 - x0, by1 - y0))).astype(np.float32)
    a = sp[..., 3:4] / 255.0 * alpha
    base[..., :3] = np.clip(base[..., :3] + sp[..., :3] * a, 0, 255)
    img.paste(Image.fromarray(base.astype(np.uint8), img.mode), (bx0, by0))
    return img


def layer(size=(CW, CH)):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def soften(img, r=0.8):
    return img.filter(ImageFilter.GaussianBlur(r))


def haze(img, color, amount):
    """Mix a layer's colours toward a haze colour, keeping alpha."""
    arr = np.asarray(img).astype(np.float32)
    arr[..., :3] = arr[..., :3] * (1 - amount) + np.array(color, np.float32) * amount
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def fog_band(size, y0, y1, color, alpha):
    w, h = size
    arr = np.zeros((h, w, 4), np.uint8)
    arr[..., :3] = color
    ys = np.arange(h)
    a = np.clip(1 - np.abs(ys - (y0 + y1) / 2) / ((y1 - y0) / 2), 0, 1) ** 1.5 * alpha * 255
    arr[..., 3] = a[:, None].astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


# ------------------------------------------------------------------ architecture
def dome(d, cx, base_y, r, col, pointed=True, drum=0):
    if drum:
        d.rectangle([cx - r * 0.9, base_y - drum, cx + r * 0.9, base_y], fill=col)
        base_y -= drum
    pts = []
    for i in range(41):
        a = math.pi * i / 40
        x = cx - r * math.cos(a)
        y = base_y - r * math.sin(a) * (1.05 if pointed else 1.0)
        if pointed:
            y -= r * 0.35 * (math.sin(a) ** 6)
        pts.append((x, y))
    d.polygon(pts, fill=col)
    if pointed:
        top = base_y - r * 1.4
        d.line([cx, top, cx, top - r * 0.35], fill=col, width=max(2, int(r * 0.06)))
        d.ellipse([cx - r * 0.07, top - r * 0.3, cx + r * 0.07, top - r * 0.16], fill=col)


def minaret_square(d, cx, base_y, h, w, col):
    """Damascus-style square tower with balcony and pyramid cap."""
    d.rectangle([cx - w / 2, base_y - h, cx + w / 2, base_y], fill=col)
    d.rectangle([cx - w * 0.75, base_y - h * 0.82, cx + w * 0.75, base_y - h * 0.78], fill=col)
    d.rectangle([cx - w * 0.38, base_y - h * 1.08, cx + w * 0.38, base_y - h], fill=col)
    d.polygon([(cx - w * 0.45, base_y - h * 1.08), (cx + w * 0.45, base_y - h * 1.08),
               (cx, base_y - h * 1.3)], fill=col)
    d.line([cx, base_y - h * 1.3, cx, base_y - h * 1.38], fill=col, width=3)


def minaret_mamluk(d, cx, base_y, h, w, col):
    """Cairo Mamluk minaret: square base, octagonal shaft, balconies, bulb top."""
    d.rectangle([cx - w / 2, base_y - h * 0.45, cx + w / 2, base_y], fill=col)
    d.rectangle([cx - w * 0.7, base_y - h * 0.48, cx + w * 0.7, base_y - h * 0.45], fill=col)
    d.rectangle([cx - w * 0.38, base_y - h * 0.78, cx + w * 0.38, base_y - h * 0.48], fill=col)
    d.rectangle([cx - w * 0.6, base_y - h * 0.8, cx + w * 0.6, base_y - h * 0.78], fill=col)
    d.rectangle([cx - w * 0.22, base_y - h * 0.93, cx + w * 0.22, base_y - h * 0.8], fill=col)
    bw = w * 0.32
    d.ellipse([cx - bw, base_y - h * 1.02, cx + bw, base_y - h * 0.9], fill=col)
    d.polygon([(cx - bw * 0.6, base_y - h * 0.99), (cx + bw * 0.6, base_y - h * 0.99), (cx, base_y - h * 1.08)], fill=col)
    d.line([cx, base_y - h * 1.08, cx, base_y - h * 1.14], fill=col, width=3)


def city(d, x0, x1, base_y, col, rng, hmin, hmax, domes=0.15, minarets=0.03, style="damascus",
         windows=None, wincol=(255, 190, 100)):
    """A row of flat-roofed buildings with the odd dome / minaret."""
    x = x0
    while x < x1:
        bw = rng.uniform(40, 120)
        bh = rng.uniform(hmin, hmax)
        d.rectangle([x, base_y - bh, x + bw, base_y + 400], fill=col)
        if rng.random() < 0.35:  # parapet / rooftop room
            d.rectangle([x + bw * 0.2, base_y - bh - bh * 0.15, x + bw * 0.55, base_y - bh], fill=col)
        r = rng.random()
        if r < domes:
            dome(d, x + bw / 2, base_y - bh, bw * 0.35, col, pointed=style == "cairo", drum=bw * 0.12)
        elif r < domes + minarets:
            mh = rng.uniform(hmax * 1.6, hmax * 2.4)
            (minaret_mamluk if style == "cairo" else minaret_square)(d, x + bw / 2, base_y - bh + 5, mh, bw * 0.22, col)
        if windows is not None and rng.random() < windows:
            wx = x + rng.uniform(0.2, 0.7) * bw
            wy = base_y - bh * rng.uniform(0.3, 0.8)
            d.rectangle([wx, wy, wx + 6, wy + 9], fill=wincol + (255,))
        x += bw * rng.uniform(0.55, 0.95)


def hills(d, x0, x1, base_y, amp, col, rng, freq=1.0, bottom=None):
    xs = np.linspace(x0, x1, 120)
    ph = rng.uniform(0, 10, 3)
    ys = base_y - amp * (0.5 + 0.3 * np.sin(xs / 300 * freq + ph[0]) + 0.15 * np.sin(xs / 110 * freq + ph[1])
                         + 0.05 * np.sin(xs / 40 + ph[2]))
    pts = list(zip(xs, ys)) + [(x1, bottom or CH), (x0, bottom or CH)]
    d.polygon(pts, fill=col)


def arch_window(d, x, y, w, h, col):
    d.rectangle([x, y + w / 2, x + w, y + h], fill=col)
    d.pieslice([x, y, x + w, y + w], 180, 360, fill=col)


def horseshoe_arch(d, cx, base_y, w, h, col_fill):
    """Fill an arch-shaped opening."""
    d.rectangle([cx - w / 2, base_y - h + w / 2, cx + w / 2, base_y], fill=col_fill)
    d.ellipse([cx - w / 2 - w * 0.05, base_y - h, cx + w / 2 + w * 0.05, base_y - h + w], fill=col_fill)


# ------------------------------------------------------------------ figures
def rot_ellipse(cx, cy, rx, ry, ang, n=24):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + rx * math.cos(a) * ca - ry * math.sin(a) * sa, cy + rx * math.cos(a) * sa + ry * math.sin(a) * ca)
            for a in (2 * math.pi * k / n for k in range(n))]


def figure(d, x, feet_y, h, col, kind="scholar", phase=None, facing=1):
    """Human silhouette seen from behind. phase animates walking (radians)."""
    armored = kind in ("emir", "soldier", "rider")
    head_r = h * 0.064
    top = feet_y - h
    hy = top + head_r * (1.9 if kind in ("scholar", "judge") else 1.6 if armored else 1.1)
    sh = hy + head_r * 1.75                      # shoulder line
    hw = h * (0.155 if not armored else 0.19)    # half shoulder width
    hem = hw * (1.45 if kind in ("scholar", "judge", "traveler") else 1.15)
    if phase is not None:
        sw = math.sin(phase) * h * 0.07
        lw = max(2, int(h * 0.055))
        for side, k in ((-1, 1), (1, -1)):
            d.line([x + side * h * 0.035, feet_y - h * 0.3, x + side * h * 0.035 + k * sw, feet_y], fill=col, width=lw)
        bottom = feet_y - h * 0.2
    else:
        bottom = feet_y
    neck = h * 0.042
    right = [(x + neck, hy + head_r * 0.6), (x + neck * 1.3, sh - h * 0.018), (x + hw * 0.72, sh - h * 0.004)]
    for k in range(6):                           # rounded shoulder cap
        a = math.pi / 2 * (k + 1) / 6
        right.append((x + hw * 0.72 + hw * 0.3 * math.sin(a), sh - h * 0.004 + hw * 0.32 * (1 - math.cos(a))))
    right += [(x + hw * 1.03, sh + h * 0.2), (x + hw * 0.97, sh + h * 0.36),
              (x + hem * 0.8, (sh + bottom) / 2 + h * 0.12), (x + hem, bottom)]
    left = [(2 * x - px, py) for px, py in right]
    d.polygon(right + left[::-1], fill=col)
    if kind in ("scholar", "judge"):
        d.polygon(rot_ellipse(x, hy + head_r * 0.25, head_r * 0.82, head_r * 1.05, 0), fill=col)
        d.polygon(rot_ellipse(x, hy - head_r * 0.55, head_r * 1.28, head_r * 0.85, 0), fill=col)   # turban
        d.polygon(rot_ellipse(x - head_r * 0.2, hy - head_r * 1.15, head_r * 0.9, head_r * 0.55, -0.2), fill=col)
    elif kind == "traveler":
        d.polygon(rot_ellipse(x, hy, head_r * 0.95, head_r * 1.1, 0), fill=col)
        d.polygon([(x - head_r * 1.15, hy + head_r * 0.4), (x + head_r * 1.15, hy + head_r * 0.4),
                   (x + hw * 0.9, sh + h * 0.03), (x - hw * 0.9, sh + h * 0.03)], fill=col)   # hood drape
    elif armored:
        d.polygon(rot_ellipse(x, hy + head_r * 0.2, head_r * 0.9, head_r, 0), fill=col)
        helm = []
        for k in range(13):                      # ogival helmet with spike
            u = k / 12
            helm.append((x - head_r * 1.08 + 2.16 * head_r * u,
                         hy - head_r * 0.15 - head_r * 0.95 * math.sin(math.pi * u) ** 0.7))
        d.polygon(helm, fill=col)
        d.line([x, hy - head_r * 1.0, x, hy - head_r * 1.55], fill=col, width=max(2, int(head_r * 0.18)))
        d.polygon([(x - head_r * 1.0, hy - head_r * 0.2), (x + head_r * 1.0, hy - head_r * 0.2),
                   (x + head_r * 1.25, sh - h * 0.005), (x - head_r * 1.25, sh - h * 0.005)], fill=col)  # mail aventail
        for side in (-1, 1):                     # pauldrons
            d.polygon(rot_ellipse(x + side * hw * 0.88, sh + h * 0.02, hw * 0.3, h * 0.04, side * 0.3), fill=col)
    else:
        d.polygon(rot_ellipse(x, hy + head_r * 0.1, head_r * 0.85, head_r * 1.05, 0), fill=col)
        d.polygon(rot_ellipse(x, hy - head_r * 0.55, head_r * 0.95, head_r * 0.55, 0), fill=col)    # cap
    if kind == "traveler":
        sx = x + hw * 1.25 * facing
        d.line([sx, feet_y, sx + h * 0.04 * facing, sh - h * 0.12], fill=col, width=max(2, int(h * 0.022)))
    if kind == "soldier":
        sx = x + hw * 1.15
        d.line([sx, feet_y - h * 0.05, sx, top - h * 0.25], fill=col, width=max(2, int(h * 0.022)))
        d.polygon([(sx - h * 0.02, top - h * 0.25), (sx + h * 0.02, top - h * 0.25), (sx, top - h * 0.36)], fill=col)
        d.polygon(rot_ellipse(x - hw * 0.95, sh + h * 0.25, hw * 0.45, h * 0.12, 0), fill=col)    # round shield
    if kind == "emir":
        d.polygon([(x - hw * 0.95, sh + h * 0.06), (x + hw * 0.95, sh + h * 0.06),
                   (x + hem * 1.05, feet_y), (x - hem * 1.05, feet_y)], fill=col)            # cape
        d.line([x + hw * 0.7, sh + h * 0.42, x + hw * 1.25, sh + h * 0.78], fill=col, width=max(2, int(h * 0.028)))


def horse_rider(d, x, ground_y, h, col, phase):
    """Mounted soldier with spear, walking right."""
    bl = h * 0.75
    by = ground_y - h * 0.55
    d.ellipse([x - bl / 2, by - h * 0.17, x + bl / 2, by + h * 0.13], fill=col)        # body
    d.polygon([(x + bl * 0.35, by - h * 0.05), (x + bl * 0.5, by - h * 0.35),
               (x + bl * 0.62, by - h * 0.32), (x + bl * 0.48, by + h * 0.02)], fill=col)  # neck
    d.ellipse([x + bl * 0.5, by - h * 0.4, x + bl * 0.75, by - h * 0.27], fill=col)    # head
    for i, lx in enumerate((-0.35, -0.22, 0.25, 0.38)):
        sw = math.sin(phase + i * 1.6) * h * 0.06
        d.line([x + bl * lx, by + h * 0.05, x + bl * lx + sw, ground_y], fill=col, width=max(2, int(h * 0.035)))
    d.line([x - bl * 0.48, by - h * 0.1, x - bl * 0.62, by + h * 0.2], fill=col, width=max(2, int(h * 0.03)))  # tail
    figure(d, x - bl * 0.05, by - h * 0.05, h * 0.62, col, "rider")
    sx = x + h * 0.08
    d.line([sx, by - h * 0.1, sx + h * 0.05, by - h * 0.95], fill=col, width=max(2, int(h * 0.02)))


def banner(d, x, top_y, pole_h, col, flagcol, t, size):
    d.line([x, top_y + pole_h, x, top_y], fill=col, width=max(2, int(size * 0.08)))
    pts_top, pts_bot = [], []
    for i in range(11):
        u = i / 10
        wave = math.sin(t * 5 + u * 4) * size * 0.12 * u
        pts_top.append((x + u * size * 1.4, top_y + wave))
        pts_bot.append((x + u * size * 1.4, top_y + size * (0.8 - 0.25 * u) + wave))
    d.polygon(pts_top + pts_bot[::-1], fill=flagcol)


# ------------------------------------------------------------------ camera
class Cam:
    """Camera window over a CWxCH world. depth p=0 is fixed background, p=1 follows camera."""

    def __init__(self, cx, cy, w):
        self.cx, self.cy, self.w = cx, cy, w

    def window(self, p=1.0, ref=(CW / 2, CH / 2, W * 1.0)):
        rcx, rcy, rw = ref
        cx = rcx + (self.cx - rcx) * p
        cy = rcy + (self.cy - rcy) * p
        w = rw * (self.w / rw) ** p
        s = w / W
        return cx - w / 2, cy - (H * s) / 2, s

    def place(self, frame, img, p=1.0):
        x0, y0, s = self.window(p)
        out = img.transform((W, H), Image.AFFINE, (s, 0, x0, 0, s, y0), resample=Image.BILINEAR)
        if img.mode == "RGBA":
            frame.alpha_composite(out)
        else:
            frame.paste(out)

    def to_screen(self, x, y, p=1.0):
        x0, y0, s = self.window(p)
        return (x - x0) / s, (y - y0) / s, 1 / s


def cam_move(t, dur, a, b):
    """Interpolate camera (cx, cy, w) from a to b with gentle easing."""
    u = ease(t / dur) * 0.6 + (t / dur) * 0.4
    return Cam(*(lerp(x, y, u) for x, y in zip(a, b)))


# ------------------------------------------------------------------ film look
_grain = None
_vign = None


def film_look(img, seed):
    global _grain, _vign
    if _vign is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        v = 1 - 0.38 * np.clip(d - 0.35, 0, 1) ** 1.6
        grade = np.array([1.04, 1.0, 0.9], np.float32)  # warm grade
        _vign = (v[..., None] * grade).astype(np.float32)
        g = np.random.default_rng(1)
        small = g.normal(0, 4.5, (8, H // 2, W // 2)).astype(np.float32)
        _grain = [np.kron(s, np.ones((2, 2), np.float32)) for s in small]
    arr = np.asarray(img.convert("RGB")).astype(np.float32)
    arr = arr * _vign
    # lift blacks slightly for a filmic toe
    arr = arr * 0.94 + 10
    arr += _grain[seed % len(_grain)][..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
