"""The six scenes as illustrated, animated shots.

Each shot builds its static layers once and then draws a frame for any local time t.
Scholar is only ever a silhouette or seen from behind; no text appears inside the imagery.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .gfx import (W, H, CW, CH, SAND, AMBER, GREEN, BRONZE, PARCH, lerp, lerpc, ease, vgradient, radial,
                  glow_sprite, add_glow, layer, soften, haze, fog_band, dome, minaret_square, minaret_mamluk,
                  city, hills, horseshoe_arch, figure, horse_rider, banner, Cam, cam_move, rot_ellipse)


def blank():
    return Image.new("RGBA", (W, H), (0, 0, 0, 255))


def rim_figure(img_or_draw_target, draw_fn, rim_col, body_col, offset=(4, 0)):
    """Draw a silhouette twice: a warm rim slightly offset, then the dark body."""
    draw_fn(rim_col, offset)
    draw_fn(body_col, (0, 0))


def birds(d, t, items, col=(40, 28, 30)):
    for (x0, y0, sp, sz, ph) in items:
        x = x0 + sp * t
        y = y0 + math.sin(t * 1.3 + ph) * 8
        flap = math.sin(t * 9 + ph) * sz * 0.5
        d.line([(x - sz, y - flap), (x, y), (x + sz, y - flap)], fill=col, width=2)


# ====================================================================== SCENE 1
class DamascusDawn:
    dur = 10.0

    def __init__(self):
        rng = np.random.default_rng(11)
        self.sky = vgradient((CW, CH), [(0, (34, 38, 76)), (0.33, (96, 70, 100)), (0.52, (206, 124, 96)),
                                        (0.64, (246, 178, 102)), (1, (250, 196, 128))]).convert("RGB")
        # Mount Qasioun, far and hazy
        far, d = layer()
        hills(d, 0, CW, 880, 170, (150, 98, 98), rng, freq=0.7)
        self.far = soften(far, 2)
        # main city with the Umayyad Mosque
        mid, d = layer()
        col = (92, 58, 62)
        city(d, 0, CW, 950, col, rng, 40, 120, domes=0.12, minarets=0.025, windows=0.25)
        cx = 1200
        d.rectangle([cx - 330, 850, cx + 330, 960], fill=col)                         # prayer hall
        d.polygon([(cx - 330, 850), (cx + 330, 850), (cx + 300, 822), (cx - 300, 822)], fill=col)
        d.rectangle([cx - 70, 790, cx + 70, 850], fill=col)                           # transept
        dome(d, cx, 790, 62, col, pointed=True, drum=22)                              # Dome of the Eagle
        minaret_square(d, cx - 330, 852, 230, 36, col)
        minaret_square(d, cx + 330, 852, 270, 40, col)
        minaret_square(d, cx + 40, 862, 190, 30, col)
        self.mid = soften(mid, 1.0)
        self.fog = fog_band((CW, CH), 900, 1040, (246, 196, 150), 0.55)
        near, d = layer()
        ncol = (44, 28, 32)
        city(d, 0, CW, 1170, ncol, rng, 60, 190, domes=0.18, minarets=0.02, windows=0.3, wincol=(255, 176, 90))
        for x in rng.uniform(0, CW, 9):  # cypresses
            h = rng.uniform(140, 230)
            d.ellipse([x - 18, 1170 - h, x + 18, 1180], fill=ncol)
        self.near = soften(near, 0.8)
        self.sun = glow_sprite(520, (255, 196, 120), 1.6, 0.95)
        self.sun_core = glow_sprite(70, (255, 238, 196), 0.6, 1.0)
        self.birds = [(-80 - i * 70, 380 + (i % 3) * 40, 70 + i * 6, 9 + i % 3, i * 1.7) for i in range(6)]

    def frame(self, t):
        cam = cam_move(t, self.dur, (1200, 650, 2250), (1200, 790, 1650))
        f = blank()
        cam.place(f, self.sky, 0.15)
        sx, sy, sc = cam.to_screen(1560, 900 - 70 * t / self.dur, 0.15)
        add_glow(f, self.sun, sx, sy, sc)
        add_glow(f, self.sun_core, sx, sy, sc)
        cam.place(f, self.far, 0.35)
        cam.place(f, self.mid, 0.65)
        cam.place(f, self.fog, 0.75)
        cam.place(f, self.near, 1.0)
        birds(ImageDraw.Draw(f), t, self.birds)
        return f


# ====================================================================== SCENE 2
class Manuscript:
    dur = 5.0

    def __init__(self):
        rng = np.random.default_rng(21)
        desk = vgradient((CW, CH), [(0, (46, 28, 18)), (1, (24, 14, 10))])
        d = ImageDraw.Draw(desk)
        for y in range(0, CH, 9):  # wood grain
            c = int(rng.uniform(-8, 8))
            d.line([(0, y), (CW, y + rng.uniform(-20, 20))], fill=(52 + c, 32 + c, 20 + c, 255), width=2)
        self.desk = soften(desk, 1.5).convert("RGB")
        book, d = layer()
        self.spine = (1200, 700)
        # cover + page block
        d.rounded_rectangle([590, 330, 1810, 1100], 18, fill=(70, 30, 22))
        self._page(d, -1, PARCH)
        self._page(d, 1, PARCH)
        self.book = soften(book, 0.7)
        self.lines_left = self._script_lines(rng, -1)
        self.lines_right = self._script_lines(rng, 1)
        self.candle_glow = glow_sprite(700, (255, 170, 80), 1.8, 0.9)
        self.flame_glow = glow_sprite(60, (255, 224, 160), 0.8, 1.0)

    def _page_poly(self, side, open_u=1.0):
        sx, sy = self.spine
        pw = 560 * open_u
        pts = []
        for i in range(21):
            u = i / 20
            x = sx + side * pw * u
            sag = math.sin(u * math.pi) * 18
            pts.append((x, 360 + sag * 0.6 - (1 - u) * 6))
        for i in range(20, -1, -1):
            u = i / 20
            x = sx + side * pw * u
            pts.append((x, 1060 - math.sin(u * math.pi) * 6))
        return pts

    def _page(self, d, side, col):
        d.polygon(self._page_poly(side), fill=col)
        sx = self.spine[0]
        d.line([(sx, 360), (sx, 1060)], fill=(150, 112, 70), width=5)

    def _script_lines(self, rng, side):
        """Illegible abstract ink strokes standing in for handwriting (no real text)."""
        img, d = layer()
        sx = self.spine[0]
        for row in range(15):
            y = 430 + row * 40
            x = sx + side * 60
            end = sx + side * 500
            while (x - end) * side < 0:
                seg = rng.uniform(25, 80)
                pts = []
                for k in range(8):
                    xx = x + side * seg * k / 7
                    pts.append((xx, y + math.sin(k * 2.1 + row) * 3 + rng.uniform(-1.5, 1.5)))
                d.line(pts, fill=(80, 50, 30, 150), width=3)
                x += side * (seg + rng.uniform(10, 22))
        return soften(img, 0.9)

    def hand(self, d, cam, wx, wy):
        """Scholar's hand (silhouette) holding a page corner, sleeve trailing off to the lower right."""
        x, y, s = cam.to_screen(wx, wy)
        col = (50, 30, 22, 255)
        sleeve = (34, 24, 22, 255)
        d.polygon([(x + 30 * s, y - 30 * s), (x + 75 * s, y + 25 * s), (x + 700 * s, y + 420 * s),
                   (x + 520 * s, y + 520 * s)], fill=sleeve)
        d.polygon([(x + 10 * s, y - 25 * s), (x + 60 * s, y + 20 * s), (x + 140 * s, y + 110 * s),
                   (x + 90 * s, y + 150 * s)], fill=col)                               # wrist
        d.polygon(rot_ellipse(x, y, 58 * s, 38 * s, -0.6), fill=col)                   # palm
        for k in range(4):                                                             # fingers, curled over the edge
            fx, fy = x - 30 * s - k * 12 * s, y - 30 * s + k * 16 * s
            d.polygon(rot_ellipse(fx, fy, 38 * s, 11 * s, -2.3 + k * 0.08), fill=col)
        d.polygon(rot_ellipse(x - 5 * s, y + 38 * s, 34 * s, 12 * s, -1.0), fill=col)  # thumb

    def frame(self, t):
        cam = cam_move(t, self.dur, (1200, 700, 1950), (1240, 690, 1660))
        f = blank()
        cam.place(f, self.desk, 0.9)
        cam.place(f, self.book, 1.0)
        cam.place(f, self.lines_left, 1.0)
        cam.place(f, self.lines_right, 1.0)
        d = ImageDraw.Draw(f)
        # page turn (right -> left) between 1.2s and 2.8s
        u = ease((t - 1.2) / 1.6)
        sx, sy = self.spine
        if 0 < u < 1:
            ang = math.pi * u
            pw = 560
            ex = sx + pw * math.cos(ang)
            lift = math.sin(ang) * 120
            top = [(sx, 360), ((sx + ex) / 2, 360 - lift * 0.8), (ex, 360 - lift)]
            bot = [(ex, 1060 - lift * 0.6), ((sx + ex) / 2, 1060 - lift * 0.3), (sx, 1060)]
            shade = 0.72 + 0.28 * abs(math.cos(ang))
            col = tuple(int(c * shade) for c in PARCH)
            pts = [cam.to_screen(x, y)[:2] for x, y in top + bot]
            d.polygon(pts, fill=col + (255,))
            self.hand(d, cam, ex + 10, 1060 - lift * 0.6 - 30)
        elif u <= 0:
            self.hand(d, cam, 1200 + 560 - 30 + 80 * (1 - ease(t / 1.2)), 1030)
        else:
            self.hand(d, cam, 640 + 900 * ease(t - 2.8), 1030 + 260 * ease(t - 2.8))
        # candle
        cx, cy = 470, 300
        flick = 1 + 0.06 * math.sin(t * 23) + 0.04 * math.sin(t * 37 + 1)
        bx, by, bs = cam.to_screen(cx, cy)
        d.rectangle([bx - 28 * bs, by, bx + 28 * bs, by + 260 * bs], fill=(232, 214, 176, 255))
        d.ellipse([bx - 70 * bs, by + 240 * bs, bx + 70 * bs, by + 290 * bs], fill=BRONZE + (255,))
        fh = 70 * bs * flick
        d.ellipse([bx - 13 * bs, by - fh, bx + 13 * bs, by + 4 * bs], fill=(255, 214, 140, 255))
        d.ellipse([bx - 6 * bs, by - fh * 0.6, bx + 6 * bs, by], fill=(255, 250, 225, 255))
        add_glow(f, self.candle_glow, bx, by - 30 * bs, bs * flick, 0.55)
        add_glow(f, self.flame_glow, bx, by - fh * 0.5, bs, 0.9)
        return f


class Pulpit:
    dur = 5.0

    def __init__(self):
        rng = np.random.default_rng(22)
        bg = vgradient((CW, CH), [(0, (40, 26, 22)), (0.7, (66, 42, 30)), (1, (36, 22, 18))])
        d = ImageDraw.Draw(bg)
        # arcade of horseshoe arches opening onto a lit courtyard
        for i, cx in enumerate(range(150, CW, 300)):
            horseshoe_arch(d, cx, 1000, 190, 520, (120, 80, 48, 255))
            horseshoe_arch(d, cx, 1000, 150, 470, (168, 116, 66, 255))
            d.rectangle([cx - 75, 760, cx + 75, 1000], fill=(110, 74, 46, 255))      # courtyard wall beyond
        # floor carpet
        d.polygon([(0, 1000), (CW, 1000), (CW, CH), (0, CH)], fill=(96, 40, 30, 255))
        for k in range(0, CW, 120):
            d.line([(k, 1000), (k + (k - CW / 2) * 0.6, CH)], fill=(80, 32, 24, 255), width=3)
        self.bg = soften(bg, 1.2).convert("RGB")
        # light shafts from high windows
        shafts, d = layer()
        for x in (500, 900, 1300):
            d.polygon([(x, 0), (x + 90, 0), (x + 520, CH), (x + 330, CH)], fill=(255, 210, 140, 40))
        self.shafts = shafts.filter(ImageFilter.GaussianBlur(25))
        # minbar
        mb, d = layer()
        mcol = (34, 22, 18)
        d.polygon([(1180, 1010), (1600, 1010), (1600, 700), (1500, 700)], fill=mcol)  # stair block
        d.line([(1170, 890), (1520, 590)], fill=mcol, width=14)                          # handrail
        for k in range(9):
            bx = 1190 + k * 38
            d.line([(bx, 1010 - k * 34), (bx, 890 - k * 33)], fill=mcol, width=6)       # balusters
        d.rectangle([1250, 1010 - 230, 1330, 1010], fill=(92, 60, 36, 255))             # door panel
        d.rectangle([1590, 520, 1760, 1010], fill=mcol)                                  # landing + canopy
        d.rectangle([1610, 560, 1740, 720], fill=(150, 100, 58, 255))                    # open kiosk
        d.rectangle([1580, 505, 1770, 525], fill=mcol)
        dome(d, 1675, 505, 70, mcol, pointed=True, drum=12)
        self.minbar = soften(mb, 0.8)
        self.lamp_glow = glow_sprite(220, (255, 180, 90), 1.6, 0.9)
        self.lamps = [(300 + i * 360, 260 + (i % 2) * 70) for i in range(6)]
        self.halo = glow_sprite(330, (255, 196, 120), 1.4, 0.8)

    def frame(self, t):
        cam = cam_move(t, self.dur, (1200, 700, 2150), (1500, 650, 1450))
        f = blank()
        cam.place(f, self.bg, 0.8)
        cam.place(f, self.shafts, 0.85)
        d = ImageDraw.Draw(f)
        for i, (lx, ly) in enumerate(self.lamps):
            x, y, s = cam.to_screen(lx, ly, 0.85)
            x2, y2, _ = cam.to_screen(lx, 0, 0.85)
            d.line([(x2, y2), (x, y)], fill=(30, 20, 14, 255), width=2)
            d.pieslice([x - 28 * s, y - 16 * s, x + 28 * s, y + 30 * s], 0, 180, fill=(120, 80, 40, 255))
            flick = 1 + 0.07 * math.sin(t * 19 + i * 2)
            add_glow(f, self.lamp_glow, x, y, s * flick, 0.75)
        cam.place(f, self.minbar, 1.0)
        # scholar on the minbar, from behind, rim-lit
        x, y, s = cam.to_screen(1675, 718, 1.0)
        add_glow(f, self.halo, x, y - 120 * s, s, 0.5)
        d = ImageDraw.Draw(f)
        figure(d, x + 4 * s, y, 196 * s, (240, 170, 90, 255), "scholar")
        figure(d, x, y, 194 * s, (16, 11, 10, 255), "scholar")
        return f


# ====================================================================== SCENE 3
class Fortress:
    dur = 3.5

    def __init__(self):
        rng = np.random.default_rng(31)
        sky = vgradient((CW, CH), [(0, (22, 20, 46)), (0.42, (84, 46, 78)), (0.66, (196, 92, 64)),
                                   (0.76, (232, 142, 82)), (1, (240, 160, 96))])
        d = ImageDraw.Draw(sky)
        for _ in range(120):
            x, y = rng.uniform(0, CW), rng.uniform(0, 420)
            b = int(rng.uniform(120, 230))
            d.point((x, y), fill=(b, b, b, 255))
        self.sky = sky.convert("RGB")
        far, d = layer()
        hills(d, 0, CW, 1000, 120, (110, 60, 70), rng, freq=1.2)
        self.far = soften(far, 2)
        hill, d = layer()
        col = (32, 22, 30)
        pts = [(0, 1100), (500, 1000), (900, 760), (1200, 690), (1520, 720), (1900, 960), (CW, 1050), (CW, CH), (0, CH)]
        d.polygon(pts, fill=col)
        # fortress
        for x0, x1, top in [(1000, 1500, 560)]:
            d.rectangle([x0, top, x1, 740], fill=col)
            for cx in range(x0, x1, 28):
                d.rectangle([cx, top - 22, cx + 15, top], fill=col)
        for tx, tw, th in [(980, 110, 470), (1220, 130, 420), (1460, 110, 480)]:
            d.rectangle([tx, th, tx + tw, 740], fill=col)
            for cx in range(tx, tx + tw, 26):
                d.rectangle([cx, th - 24, cx + 14, th], fill=col)
            d.rectangle([tx + tw / 2 - 6, th + 60, tx + tw / 2 + 6, th + 90], fill=(255, 170, 90, 255))
        self.hill = soften(hill, 0.8)

    def frame(self, t):
        cam = cam_move(t, self.dur, (1100, 700, 2000), (1330, 680, 1820))
        f = blank()
        cam.place(f, self.sky, 0.2)
        cam.place(f, self.far, 0.5)
        cam.place(f, self.hill, 1.0)
        return f


class Prison:
    dur = 3.3

    def __init__(self):
        rng = np.random.default_rng(32)
        img = Image.new("RGBA", (CW, CH), (18, 14, 14, 255))
        d = ImageDraw.Draw(img)
        vx, vy = 1200, 640
        for k in range(12, -1, -1):  # receding stone arches, far ones darker
            s = 0.8 ** k
            w, h = 1700 * s, 1250 * s
            shade = 0.42 + 0.58 * (1 - k / 12)
            stone = tuple(int(c * shade) for c in (118, 92, 74))
            inner = tuple(int(c * shade * 0.75) for c in (64, 50, 42))
            d.rectangle([vx - w / 2, vy - h / 2 + w * 0.15, vx + w / 2, vy + h / 2], fill=stone + (255,))
            d.ellipse([vx - w / 2, vy - h / 2, vx + w / 2, vy - h / 2 + w * 0.6], fill=stone + (255,))
            iw = w * 0.78
            d.rectangle([vx - iw / 2, vy - h / 2 + w * 0.2, vx + iw / 2, vy + h / 2], fill=inner + (255,))
            d.ellipse([vx - iw / 2, vy - h / 2 + w * 0.06, vx + iw / 2, vy - h / 2 + w * 0.06 + iw * 0.6], fill=inner + (255,))
            # stone joints
            for j in range(6):
                yy = vy - h / 2 + w * 0.2 + j * h / 7
                d.line([(vx - w / 2, yy), (vx - iw / 2, yy)], fill=tuple(int(c * 0.7) for c in stone) + (255,), width=max(1, int(4 * s)))
                d.line([(vx + iw / 2, yy), (vx + w / 2, yy)], fill=tuple(int(c * 0.7) for c in stone) + (255,), width=max(1, int(4 * s)))
        # floor
        d.polygon([(0, CH), (CW, CH), (vx + 190, vy + 150), (vx - 190, vy + 150)], fill=(62, 48, 40, 255))
        for k in range(1, 9):
            yy = vy + 150 + (CH - vy - 150) * (k / 9) ** 1.8
            hw_ = 190 + (CW / 2 - 190) * (yy - vy - 150) / (CH - vy - 150)
            d.line([(vx - hw_, yy), (vx + hw_, yy)], fill=(48, 36, 30, 255), width=3)
        self.corr = soften(img, 1.5).convert("RGB")
        # barred window light on left wall
        beam, d = layer()
        d.polygon([(420, 380), (560, 360), (1250, 1350), (850, 1350)], fill=(255, 214, 160, 46))
        self.beam = beam.filter(ImageFilter.GaussianBlur(30))
        win, d = layer()
        d.rectangle([380, 300, 600, 470], fill=(220, 180, 130, 255))
        for bx in range(400, 600, 40):
            d.rectangle([bx, 300, bx + 12, 470], fill=(20, 14, 14, 255))
        self.win = soften(win, 1.0)
        bars, d = layer()
        for bx in range(80, CW, 210):
            d.rectangle([bx, 0, bx + 26, CH], fill=(14, 10, 10, 255))
        d.rectangle([0, 140, CW, 175], fill=(14, 10, 10, 255))
        self.bars = soften(bars, 3)
        self.torch = glow_sprite(380, (255, 150, 60), 1.6, 0.9)

    def frame(self, t):
        cam = cam_move(t, self.dur, (1080, 675, 1950), (1320, 675, 1850))
        f = blank()
        cam.place(f, self.corr, 0.8)
        cam.place(f, self.win, 0.8)
        cam.place(f, self.beam, 0.85)
        x, y, s = cam.to_screen(1820, 560, 0.8)
        d = ImageDraw.Draw(f)
        d.polygon([(x - 10 * s, y), (x + 10 * s, y), (x + 5 * s, y + 60 * s), (x - 5 * s, y + 60 * s)], fill=(40, 26, 18, 255))
        flick = 1 + 0.12 * math.sin(t * 17) + 0.06 * math.sin(t * 31)
        d.ellipse([x - 16 * s, y - 50 * s * flick, x + 16 * s, y + 4 * s], fill=(255, 190, 90, 255))
        add_glow(f, self.torch, x, y - 20 * s, s * flick, 0.7)
        if t < 1.6:  # the camera drifts past the cell bars at the start
            a = 1 - ease(t / 1.6)
            tmp = blank()
            tmp.paste((0, 0, 0, 0), (0, 0, W, H))
            cam.place(tmp, self.bars, 1.6)
            arr = np.asarray(tmp).copy()
            arr[..., 3] = (arr[..., 3] * a).astype(np.uint8)
            f.alpha_composite(Image.fromarray(arr, "RGBA"))
        return f


class Desert:
    dur = 3.2

    def __init__(self):
        rng = np.random.default_rng(33)
        self.sky = vgradient((CW, CH), [(0, (28, 34, 70)), (0.45, (104, 76, 100)), (0.6, (220, 140, 90)),
                                        (0.66, (244, 176, 112)), (1, (244, 176, 112))]).convert("RGB")
        far, d = layer()
        hills(d, 0, CW, 900, 60, (178, 112, 86), rng, freq=1.5)
        self.far = soften(far, 2)
        mid, d = layer()
        hills(d, 0, CW, 980, 90, (138, 84, 58), rng, freq=0.9)
        self.mid = soften(mid, 1.2)
        near, d = layer()
        hills(d, 0, CW, 1080, 70, (86, 52, 38), rng, freq=0.6)
        # road toward the horizon
        pts_l, pts_r = [], []
        for i in range(40):
            u = i / 39
            y = lerp(CH, 905, u ** 0.8)
            cx = 1200 + math.sin(u * 3.2) * 160 * (1 - u)
            hw = lerp(260, 6, u ** 0.7)
            pts_l.append((cx - hw, y))
            pts_r.append((cx + hw, y))
        d.polygon(pts_l + pts_r[::-1], fill=(158, 112, 76, 255))
        self.near = soften(near, 1.0)
        self.road = (pts_l, pts_r)
        self.sunset = glow_sprite(600, (255, 170, 100), 1.8, 0.7)

    def frame(self, t):
        cam = cam_move(t, self.dur, (1200, 720, 1900), (1200, 730, 1780))
        f = blank()
        cam.place(f, self.sky, 0.2)
        x, y, s = cam.to_screen(1700, 880, 0.2)
        add_glow(f, self.sunset, x, y, s)
        cam.place(f, self.far, 0.4)
        cam.place(f, self.mid, 0.7)
        cam.place(f, self.near, 1.0)
        # lone traveller walking away down the road (south)
        u = 0.34 + 0.06 * t / self.dur
        yy = lerp(CH, 905, u ** 0.8)
        cx = 1200 + math.sin(u * 3.2) * 160 * (1 - u)
        x, y, s = cam.to_screen(cx, yy, 1.0)
        h = 300 * (1 - u) * s
        d = ImageDraw.Draw(f)
        d.polygon([(x - h * 0.12, y), (x + h * 0.12, y), (x - h * 0.6, y + h * 0.18), (x - h * 0.9, y + h * 0.16)],
                  fill=(60, 36, 28, 140))  # long shadow
        figure(d, x, y, h, (26, 18, 18, 255), "traveler", phase=t * 6.0)
        return f


# ====================================================================== SCENE 4
def draw_palm(d, px, base_y, ph, lean, col):
    trunk = [(px + lean * ph * (k / 12) ** 2, base_y - ph * k / 12) for k in range(13)]
    for (x1, y1), (x2, y2) in zip(trunk, trunk[1:]):
        w = int(lerp(20, 11, (base_y - y1) / ph))
        d.line([(x1, y1), (x2, y2)], fill=col, width=w)
    tx, ty = trunk[-1]
    for ang in (-170, -140, -110, -70, -40, -10, 15, 200, 165):
        a = math.radians(ang)
        ln = ph * 0.42
        pts_top, pts_bot = [], []
        for k in range(12):
            u = k / 11
            fx = tx + math.cos(a) * ln * u
            fy = ty + math.sin(a) * ln * u * 0.5 + (ln * 0.5) * u * u        # fronds droop
            wdt = math.sin(math.pi * u) * ph * 0.035 + 1
            pts_top.append((fx, fy - wdt))
            pts_bot.append((fx, fy + wdt))
        d.polygon(pts_top + pts_bot[::-1], fill=col)
    d.ellipse([tx - ph * 0.04, ty - ph * 0.02, tx + ph * 0.05, ty + ph * 0.06], fill=col)


class Nile:
    dur = 3.5

    def __init__(self):
        rng = np.random.default_rng(41)
        self.sky = vgradient((CW, CH), [(0, (116, 96, 112)), (0.38, (222, 150, 92)), (0.6, (252, 200, 126)),
                                        (1, (252, 200, 126))]).convert("RGB")
        far, d = layer()
        hills(d, 1300, CW, 800, 110, (170, 112, 84), rng, freq=0.6)
        ccol = (150, 98, 76)
        d.rectangle([1650, 600, 2150, 720], fill=ccol)  # citadel walls
        for cx in range(1650, 2150, 26):
            d.rectangle([cx, 585, cx + 14, 600], fill=ccol)
        dome(d, 1900, 600, 60, ccol, pointed=True, drum=14)
        minaret_mamluk(d, 1780, 600, 150, 30, ccol)
        self.far = soften(far, 1.8)
        mid, d = layer()
        col = (88, 56, 46)
        city(d, 0, CW, 830, col, rng, 40, 110, domes=0.16, minarets=0.07, style="cairo")
        self.mid = soften(mid, 1.0)
        water = vgradient((CW, CH - 830), [(0, (246, 196, 128)), (0.25, (200, 136, 92)), (0.7, (110, 72, 62)), (1, (60, 40, 42))])
        self.water = water.convert("RGB")
        bank, d = layer()
        bcol = (34, 26, 22)
        d.polygon([(0, 1130), (420, 1110), (820, 1165), (1000, CH), (0, CH)], fill=bcol)   # near bank
        for px, ph, lean in [(150, 380, 0.25), (330, 310, -0.18), (560, 430, 0.1)]:
            draw_palm(d, px, 1140, ph, lean, bcol)
        for rx in range(640, 960, 22):                                                    # reeds
            d.line([(rx, 1180), (rx + 8, 1180 - 60 - (rx % 50))], fill=bcol, width=4)
        self.bank = soften(bank, 0.8)
        self.sun = glow_sprite(560, (255, 210, 140), 1.5, 0.95)

    def frame(self, t):
        cam = cam_move(t, self.dur, (1150, 700, 2000), (1260, 690, 1840))
        f = blank()
        cam.place(f, self.sky, 0.2)
        x, y, s = cam.to_screen(820, 760, 0.2)
        add_glow(f, self.sun, x, y, s)
        cam.place(f, self.far, 0.4)
        # water band placed in world coords (y 830..CH)
        wl = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        wl.paste(self.water, (0, 830))
        cam.place(f, wl, 0.7)
        d = ImageDraw.Draw(f)
        rng = np.random.default_rng(int(t * 8))
        for k in range(110):  # shimmering sun path on the water
            wy = 835 + (k / 110) ** 1.5 * 480
            wx = 820 + rng.normal(0, 25 + (wy - 830) * 0.18)
            ln = rng.uniform(25, 110) * (1 + (wy - 830) / 260)
            sx1, sy1, _ = cam.to_screen(wx - ln / 2, wy, 0.7)
            sx2, _, _ = cam.to_screen(wx + ln / 2, wy, 0.7)
            d.line([(sx1, sy1), (sx2, sy1)], fill=(255, 226, 170, 255), width=2)
        cam.place(f, self.mid, 0.7)
        # felucca gliding
        bx = 1300 + 60 * t
        x, y, s = cam.to_screen(bx, 1000, 0.85)
        hc = (30, 22, 20, 255)
        d.polygon([(x - 90 * s, y), (x + 100 * s, y), (x + 70 * s, y + 28 * s), (x - 70 * s, y + 28 * s)], fill=hc)
        d.line([(x, y), (x + 10 * s, y - 230 * s)], fill=hc, width=max(2, int(5 * s)))
        d.polygon([(x - 120 * s, y - 20 * s), (x + 60 * s, y - 280 * s), (x + 10 * s, y - 10 * s)], fill=(50, 34, 28, 255))
        cam.place(f, self.bank, 1.0)
        return f


class Court:
    dur = 3.3

    def __init__(self):
        rng = np.random.default_rng(42)
        bg = vgradient((CW, CH), [(0, (36, 24, 20)), (1, (58, 38, 28))])
        d = ImageDraw.Draw(bg)
        horseshoe_arch(d, 1200, 820, 420, 700, (252, 196, 120, 255))   # bright window behind the judge
        for cx in (500, 1900):
            horseshoe_arch(d, cx, 900, 260, 560, (120, 78, 46, 255))
        for cx in (850, 1550):
            d.rectangle([cx - 40, 150, cx + 40, 1010], fill=(26, 18, 16, 255))  # columns
        d.rectangle([700, 820, 1700, 900], fill=(44, 30, 24, 255))            # dais
        d.polygon([(0, 1000), (CW, 1000), (CW, CH), (0, CH)], fill=(40, 26, 22, 255))
        self.bg = soften(bg, 1.2).convert("RGB")
        self.window_glow = glow_sprite(650, (255, 196, 120), 1.5, 0.6)

    def frame(self, t):
        cam = cam_move(t, self.dur, (1200, 680, 2050), (1210, 640, 1700))
        f = blank()
        cam.place(f, self.bg, 0.8)
        x, y, s = cam.to_screen(1200, 600, 0.8)
        add_glow(f, self.window_glow, x, y, s, 0.7)
        d = ImageDraw.Draw(f)
        # seated judge (backlit)
        jx, jy, js = cam.to_screen(1200, 820, 0.8)
        col = (16, 11, 10, 255)
        figure(d, jx, jy, 300 * js, col, "judge")
        d.rectangle([jx - 190 * js, jy - 70 * js, jx + 190 * js, jy + 10 * js], fill=(30, 20, 16, 255))  # low desk
        # people standing before the court, seen from behind
        for px, h in [(620, 620), (1780, 660), (960, 560)]:
            x, y, s = cam.to_screen(px, 1300, 1.15)
            figure(d, x + 5 * s, y, h * s, (230, 160, 90, 255), "scholar" if px == 960 else "plain")
            figure(d, x, y, h * s, (12, 9, 8, 255), "scholar" if px == 960 else "plain")
        return f


class Emirs:
    dur = 3.2

    def __init__(self):
        bg = vgradient((CW, CH), [(0, (44, 28, 22)), (1, (60, 38, 28))])
        d = ImageDraw.Draw(bg)
        horseshoe_arch(d, 1200, 1020, 900, 960, (250, 204, 134, 255))     # sunlit courtyard through a great arch
        for cx in range(820, 1600, 130):                                 # arcade across the courtyard
            horseshoe_arch(d, cx, 840, 90, 220, (214, 162, 100, 255))
        d.rectangle([750, 840, 1650, 1020], fill=(232, 182, 118, 255))
        self.bg = soften(bg, 1.5).convert("RGB")
        self.glow = glow_sprite(800, (255, 210, 140), 1.4, 0.5)

    def frame(self, t):
        cam = cam_move(t, self.dur, (1200, 720, 2100), (1200, 690, 1820))
        f = blank()
        cam.place(f, self.bg, 0.8)
        x, y, s = cam.to_screen(1200, 760, 0.8)
        add_glow(f, self.glow, x, y, s, 0.6)
        d = ImageDraw.Draw(f)
        for px, h in [(760, 980), (1230, 1060), (1690, 1000)]:
            x, y, s = cam.to_screen(px, 1500, 1.25)
            figure(d, x + 7 * s, y, h * s, (255, 190, 110, 255), "emir")
            figure(d, x, y, h * s, (14, 10, 9, 255), "emir")
        return f


# ====================================================================== SCENE 5
class Coins:
    dur = 4.0

    def __init__(self):
        rng = np.random.default_rng(51)
        bg = vgradient((CW, CH), [(0, (34, 22, 18)), (1, (54, 34, 26))])
        d = ImageDraw.Draw(bg)
        for cx in range(200, CW, 400):
            horseshoe_arch(d, cx, 820, 260, 560, (110, 72, 44, 255))
        self.bg = soften(bg, 1.5).convert("RGB")
        tb, d = layer()
        d.polygon([(560, 820), (1840, 820), (2200, 1350), (200, 1350)], fill=(70, 40, 26, 255))   # table top
        d.polygon([(560, 820), (1840, 820), (1840, 840), (560, 840)], fill=(46, 26, 18, 255))
        self.table = soften(tb, 0.8)
        self.chests = [(820, 1000, 1.0), (1560, 980, 0.95)]
        self.gold = glow_sprite(160, (255, 200, 90), 1.4, 0.8)
        self.sparkles = [(rng.uniform(-90, 90), rng.uniform(-40, 10), rng.uniform(0, 6)) for _ in range(14)]
        self.lamp = glow_sprite(260, (255, 176, 90), 1.6, 0.8)

    def chest(self, d, f, cam, cx, cy, sc, t, open_=True):
        x, y, s = cam.to_screen(cx, cy, 1.0)
        s *= sc
        wood, band = (92, 52, 28, 255), (176, 124, 60, 255)
        d.rectangle([x - 150 * s, y - 100 * s, x + 150 * s, y + 40 * s], fill=wood)
        d.rectangle([x - 150 * s, y - 60 * s, x + 150 * s, y - 45 * s], fill=band)
        d.rectangle([x - 110 * s, y - 100 * s, x - 95 * s, y + 40 * s], fill=band)
        d.rectangle([x + 95 * s, y - 100 * s, x + 110 * s, y + 40 * s], fill=band)
        if not open_:
            d.polygon([(x - 158 * s, y - 100 * s), (x + 158 * s, y - 100 * s), (x + 140 * s, y - 150 * s),
                       (x - 140 * s, y - 150 * s)], fill=(122, 72, 38, 255))                       # closed lid
            d.rectangle([x - 20 * s, y - 70 * s, x + 20 * s, y - 30 * s], fill=(214, 168, 80, 255))  # clasp
            add_glow(f, self.gold, x, y - 60 * s, s * 0.6, 0.25)
        if open_:
            d.polygon([(x - 150 * s, y - 100 * s), (x + 150 * s, y - 100 * s), (x + 140 * s, y - 230 * s),
                       (x - 140 * s, y - 230 * s)], fill=(70, 38, 20, 255))                       # lid
            d.ellipse([x - 140 * s, y - 135 * s, x + 140 * s, y - 70 * s], fill=(222, 170, 64, 255))  # coin heap
            for k in range(18):
                ang = k * 2.3
                rx, ry = math.cos(ang) * 100 * s * (k % 5) / 5, math.sin(ang) * 18 * s
                d.ellipse([x + rx - 12 * s, y - 108 * s + ry - 6 * s, x + rx + 12 * s, y - 108 * s + ry + 6 * s],
                          fill=(250, 210, 110, 255))
            add_glow(f, self.gold, x, y - 100 * s, s, 0.5)
            for (sx, sy, ph) in self.sparkles:
                a = max(0.0, math.sin(t * 3 + ph * 5)) ** 6
                if a > 0.05:
                    px, py = x + sx * s, y - 105 * s + sy * s
                    r = 16 * s * a
                    d.line([(px - r, py), (px + r, py)], fill=(255, 250, 220, 255), width=2)
                    d.line([(px, py - r), (px, py + r)], fill=(255, 250, 220, 255), width=2)

    def frame(self, t):
        cam = cam_move(t, self.dur, (1200, 760, 2000), (1200, 790, 1700))
        f = blank()
        cam.place(f, self.bg, 0.8)
        for lx in (600, 1200, 1800):
            x, y, s = cam.to_screen(lx, 360, 0.8)
            add_glow(f, self.lamp, x, y, s * (1 + 0.05 * math.sin(t * 13 + lx)), 0.7)
        # an emir behind the table sets down a third chest
        d = ImageDraw.Draw(f)
        u = ease(t / 1.8)
        cy = lerp(830, 900, u)
        x, y, s = cam.to_screen(1200, 860, 1.0)
        body = (22, 15, 13, 255)
        figure(d, x + 5 * s, y + 40 * s, 560 * s, (230, 160, 90, 255), "emir")
        figure(d, x, y + 40 * s, 560 * s, body, "emir")
        cam.place(f, self.table, 1.0)
        d = ImageDraw.Draw(f)
        for cx, cy0, sc in self.chests:
            self.chest(d, f, cam, cx, cy0, sc, t)
        cx_, cy_, cs = cam.to_screen(1200, cy, 1.0)
        for side in (-1, 1):  # arms reaching down to the chest's handles
            d.polygon([(x + side * 80 * s, y - 400 * s), (x + side * 125 * s, y - 330 * s),
                       (cx_ + side * 185 * cs, cy_ - 40 * cs), (cx_ + side * 125 * cs, cy_ - 85 * cs)], fill=body)
        self.chest(d, f, cam, 1200, cy, 1.05, t, open_=False)
        for side in (-1, 1):
            d.polygon(rot_ellipse(cx_ + side * 158 * cs, cy_ - 60 * cs, 26 * cs, 18 * cs, 0), fill=body)
        # emirs standing at the table edges
        for px, h in [(330, 900), (2080, 940)]:
            x, y, s = cam.to_screen(px, 1500, 1.2)
            figure(d, x + 6 * s, y, h * s, (240, 170, 90, 255), "emir")
            figure(d, x, y, h * s, (14, 10, 9, 255), "emir")
        return f


class Army:
    dur = 6.0

    def __init__(self):
        rng = np.random.default_rng(52)
        self.sky = vgradient((CW, CH), [(0, (40, 44, 82)), (0.4, (126, 86, 102)), (0.58, (222, 132, 90)),
                                        (0.64, (246, 182, 112)), (1, (246, 182, 112))]).convert("RGB")
        far, d = layer()
        hills(d, 0, CW, 860, 90, (150, 96, 92), rng, freq=0.8)
        self.far = soften(far, 2)
        ground, d = layer()
        d.polygon([(0, 900), (CW, 880), (CW, CH), (0, CH)], fill=(70, 44, 38, 255))
        self.ground = soften(ground, 1)
        self.dust = fog_band((CW, CH), 860, 1000, (240, 176, 120), 0.5)
        self.sun = glow_sprite(600, (255, 200, 130), 1.5, 0.9)
        self.rows = []
        for (y, h, n, speed, p, col, riders) in [(900, 62, 46, 26, 0.55, (96, 62, 60), 0.0),
                                                  (970, 115, 24, 42, 0.75, (52, 34, 34), 0.15),
                                                  (1140, 230, 11, 70, 1.0, (24, 16, 16), 0.3)]:
            xs = np.sort(rng.uniform(-400, CW + 400, n))
            kinds = ["rider" if rng.random() < riders else "soldier" for _ in range(n)]
            ban = [rng.random() < 0.18 for _ in range(n)]
            self.rows.append((y, h, xs, speed, p, col, kinds, ban, rng.uniform(0, 6, n)))

    def frame(self, t):
        cam = cam_move(t, self.dur, (1080, 720, 2000), (1320, 720, 1940))
        f = blank()
        cam.place(f, self.sky, 0.2)
        x, y, s = cam.to_screen(1900, 900 - 20 * t / self.dur, 0.2)
        add_glow(f, self.sun, x, y, s)
        cam.place(f, self.far, 0.4)
        cam.place(f, self.ground, 0.6)
        d = ImageDraw.Draw(f)
        span = CW + 800
        for ri, (gy, h, xs, speed, p, col, kinds, ban, ph) in enumerate(self.rows):
            if ri == 2:
                cam.place(f, self.dust, 0.8)
                d = ImageDraw.Draw(f)
            for i, x0 in enumerate(xs):
                wx = (x0 + speed * t + 400) % span - 400
                x, y, s = cam.to_screen(wx, gy, p)
                if x < -300 or x > W + 300:
                    continue
                c = col + (255,)
                phase = t * (7 + ri) + ph[i]
                if kinds[i] == "rider":
                    horse_rider(d, x, y, h * 1.3 * s, c, phase)
                else:
                    figure(d, x, y, h * s, c, "soldier", phase=phase)
                if ban[i]:
                    banner(d, x - h * 0.25 * s, y - h * 1.7 * s, h * 1.6 * s, c, (110, 40, 30, 255) if ri == 2 else c,
                           t + ph[i], h * 0.4 * s)
        return f


# ====================================================================== SCENE 6
class Sunset:
    dur = 10.0

    def __init__(self):
        rng = np.random.default_rng(61)
        self.sky = vgradient((CW, CH), [(0, (40, 30, 66)), (0.33, (128, 56, 72)), (0.55, (226, 100, 62)),
                                        (0.67, (250, 158, 82)), (1, (250, 158, 82))]).convert("RGB")
        far, d = layer()
        hills(d, 0, CW, 905, 70, (160, 78, 72), rng, freq=0.9)
        self.far = soften(far, 2)
        mid, d = layer()
        col = (70, 34, 40)
        city(d, 0, CW, 930, col, rng, 40, 100, domes=0.15, minarets=0.08, style="cairo")
        for mx, mh in [(860, 330), (1040, 280), (1480, 360), (1620, 300)]:
            minaret_mamluk(d, mx, 935, mh, 46, col)
        dome(d, 1260, 900, 90, col, pointed=True, drum=30)
        self.mid = soften(mid, 1.0)
        water = vgradient((CW, CH - 940), [(0, (240, 140, 80)), (0.5, (120, 56, 56)), (1, (40, 24, 32))])
        self.water = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        self.water.paste(water, (0, 940))
        near, d = layer()
        d.polygon([(0, 1250), (CW, 1230), (CW, CH), (0, CH)], fill=(26, 16, 20, 255))
        self.near = soften(near, 1)
        self.sun = glow_sprite(700, (255, 170, 100), 1.5, 1.0)
        self.core = glow_sprite(90, (255, 228, 180), 0.6, 1.0)
        self.birds = [(300 + i * 90, 420 + (i % 3) * 50, 40 + i * 4, 10, i * 1.3) for i in range(7)]

    def frame(self, t):
        cam = cam_move(t, self.dur, (1200, 830, 1500), (1200, 650, 2250))
        f = blank()
        cam.place(f, self.sky, 0.25)
        x, y, s = cam.to_screen(1260, 860 + 45 * t / self.dur, 0.25)
        add_glow(f, self.sun, x, y, s)
        add_glow(f, self.core, x, y, s)
        cam.place(f, self.far, 0.45)
        cam.place(f, self.water, 0.7)
        d = ImageDraw.Draw(f)
        rng = np.random.default_rng(int(t * 8))
        for k in range(50):
            wy = 945 + (k / 50) ** 1.5 * 300
            wx = 1260 + rng.normal(0, 30 + (wy - 940) * 0.15)
            ln = rng.uniform(20, 70)
            sx1, sy1, _ = cam.to_screen(wx - ln / 2, wy, 0.7)
            sx2, _, _ = cam.to_screen(wx + ln / 2, wy, 0.7)
            d.line([(sx1, sy1), (sx2, sy1)], fill=(255, 210, 150, 255), width=2)
        cam.place(f, self.mid, 0.7)
        cam.place(f, self.near, 1.0)
        birds(ImageDraw.Draw(f), t, self.birds, col=(30, 16, 22, 255))
        return f


# ====================================================================== timeline
TIMELINE = [  # (start, shot class)
    (0.0, DamascusDawn),
    (10.0, Manuscript), (15.0, Pulpit),
    (20.0, Fortress), (23.5, Prison), (26.8, Desert),
    (30.0, Nile), (33.5, Court), (36.8, Emirs),
    (40.0, Coins), (44.0, Army),
    (50.0, Sunset),
]
TOTAL = 60.0
XFADE = 0.6
