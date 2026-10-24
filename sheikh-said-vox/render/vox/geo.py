"""Paper-style maps: Natural Earth country outlines (public domain), hand-entered rivers and places.

A View maps lon/lat to pixels of a map image (equirectangular, scaled by cos(latitude)).
"""
import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .kit import INK, PAPER, RIVER, SEA, paper

DATA = Path(__file__).resolve().parents[1] / "data" / "countries.json"

# (lat, lon)
PLACES = {
    "amed": (37.91, 40.23), "palu": (38.69, 39.93), "khinis": (39.36, 41.70), "piran": (38.37, 40.07),
    "lice": (38.46, 40.65), "genc": (38.75, 40.56), "maden": (38.39, 39.67), "elazig": (38.67, 39.22),
    "bitlis": (38.40, 42.11), "mardin": (37.31, 40.74), "aleppo": (36.20, 37.16), "geneva": (46.20, 6.14),
    "tikrit": (34.61, 43.68), "jerusalem": (31.78, 35.23), "istanbul": (41.01, 28.98), "ankara": (39.93, 32.85),
    "damascus": (33.51, 36.29), "baghdad": (33.34, 44.40), "cairo": (30.04, 31.24), "mosul": (36.34, 43.13),
    "erbil": (36.19, 44.01), "sulaymaniyah": (35.56, 45.43), "urmia": (37.55, 45.07), "van": (38.50, 43.38),
    "mus": (38.75, 41.49), "erzurum": (39.90, 41.27), "siverek": (37.75, 39.32), "silvan": (38.14, 41.00),
    "ergani": (38.27, 39.76), "bingol": (38.88, 40.50), "izmir": (38.42, 27.14), "konya": (37.87, 32.48),
    "burdur": (37.72, 30.29), "kirkuk": (35.47, 44.39), "duhok": (36.87, 42.99), "zakho": (37.14, 42.68),
    "qamishli": (37.05, 41.22), "mecca": (21.42, 39.83), "tehran": (35.69, 51.39), "malatya": (38.35, 38.31),
    "kharput": (38.71, 39.25), "varto": (39.17, 41.45), "solhan": (38.97, 41.05),
}

# rivers as (lat, lon) polylines, simplified by hand
RIVERS = {
    "murat": [(39.30, 43.60), (39.15, 42.55), (39.00, 42.00), (38.80, 41.60), (38.78, 41.05), (38.76, 40.55),
              (38.69, 39.93), (38.75, 39.45), (38.80, 39.05), (38.80, 38.78)],
    "karasu": [(39.90, 41.20), (39.75, 40.30), (39.70, 39.50), (39.25, 38.85), (38.80, 38.78)],
    "euphrates": [(38.80, 38.78), (38.55, 38.60), (38.20, 38.50), (37.80, 38.30), (37.40, 38.00), (37.03, 37.98),
                  (36.65, 38.10), (36.00, 38.40), (35.95, 39.00), (35.33, 40.14), (34.45, 40.92), (34.13, 42.38),
                  (33.42, 43.30), (32.60, 44.00), (32.00, 44.60), (31.05, 46.30), (31.00, 47.40)],
    "tigris": [(38.45, 39.55), (38.20, 39.90), (37.92, 40.24), (37.88, 40.60), (37.71, 41.41), (37.55, 41.90),
               (37.33, 42.19), (37.05, 42.40), (36.75, 42.70), (36.34, 43.13), (35.80, 43.30), (35.45, 43.25),
               (34.61, 43.68), (34.19, 43.87), (33.34, 44.40), (32.50, 45.82), (31.84, 47.15), (31.00, 47.40)],
}

# schematic areas as (lon, lat) rings
AREAS = {
    "sevres": [(38.5, 38.9), (40.0, 39.4), (41.6, 39.1), (42.8, 38.7), (43.9, 38.3), (44.4, 37.6), (44.6, 37.1),
               (43.0, 37.3), (42.2, 37.2), (41.0, 37.1), (40.0, 36.9), (38.9, 36.8), (38.2, 37.2), (38.0, 38.0)],
    "kurdistan": [(37.0, 37.0), (38.5, 38.6), (40.0, 39.6), (42.0, 40.0), (43.8, 39.8), (44.6, 38.9), (45.5, 37.4),
                  (46.2, 35.8), (46.8, 34.5), (45.6, 33.8), (44.6, 34.6), (43.4, 35.7), (42.0, 36.5), (40.0, 36.6),
                  (38.0, 36.6)],
    "revolt": [(39.0, 38.9), (40.0, 39.15), (41.0, 39.4), (41.8, 39.1), (41.6, 38.3), (40.8, 37.8), (40.2, 37.5),
               (39.4, 37.6), (38.9, 38.2)],
    "krg": [(42.7, 37.2), (43.6, 37.3), (44.4, 37.1), (45.0, 36.6), (45.6, 35.9), (45.9, 35.2), (45.6, 34.9),
            (45.0, 35.3), (44.4, 35.6), (43.6, 36.0), (43.0, 36.5), (42.7, 36.9)],
}


class View:
    """lon/lat window -> pixel space of a w x h map image."""

    def __init__(self, lon_c, lat_c, lon_span, w, h):
        self.lon_c, self.lat_c, self.w, self.h = lon_c, lat_c, w, h
        self.kx = w / lon_span
        self.ky = self.kx / math.cos(math.radians(lat_c))

    def xy(self, lat, lon):
        return (self.w / 2 + (lon - self.lon_c) * self.kx, self.h / 2 - (lat - self.lat_c) * self.ky)

    def place(self, name):
        return self.xy(*PLACES[name])

    def line(self, latlons):
        return [self.xy(a, b) for a, b in latlons]

    def ring(self, lonlats):
        return [self.xy(b, a) for a, b in lonlats]


@lru_cache(maxsize=1)
def countries():
    return json.loads(DATA.read_text())


def _smooth(pts, n=6):
    """Catmull-Rom style densify so hand-entered rivers look drawn rather than angular."""
    if len(pts) < 3:
        return pts
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 +
                                    (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out


def dashed(d, pts, dash=10, gap=7, fill=INK + (110,), width=2):
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


def base_map(view, rivers=("murat", "euphrates", "tigris", "karasu"), highlight=None, seed=3, border_w=2,
             river_w=4):
    """Land on paper, sea in muted blue, dashed borders, rivers. Returns RGBA image of view size."""
    w, h = view.w, view.h
    sea = paper(w, h, seed=seed + 1, tone=SEA, vign=0.0).copy()
    land = paper(w, h, seed=seed, tone=PAPER, vign=0.0)
    mask = Image.new("L", (w, h), 0)
    dm = ImageDraw.Draw(mask)
    rings = []
    for c in countries():
        for poly in c["polys"]:
            ring = [view.xy(lat, lon) for lon, lat in poly]
            xs = [p[0] for p in ring]
            ys = [p[1] for p in ring]
            if max(xs) < -50 or min(xs) > w + 50 or max(ys) < -50 or min(ys) > h + 50:
                continue
            dm.polygon(ring, fill=255)
            rings.append((c["name"], ring))
    img = sea
    img.paste(land, (0, 0), mask)
    d = ImageDraw.Draw(img, "RGBA")
    if highlight:
        for name in highlight:
            for n, ring in rings:
                if n == name:
                    d.polygon(ring, fill=(228, 214, 186, 255))
    # coastline: solid thin ink; borders: dashed
    edge = mask.filter(ImageFilter.FIND_EDGES)
    coast = Image.new("RGBA", (w, h), INK + (0,))
    coast.putalpha(edge.point(lambda v: 150 if v > 40 else 0).filter(ImageFilter.GaussianBlur(0.6)))
    for n, ring in rings:
        dashed(d, ring + ring[:1], fill=INK + (95,), width=border_w)
    img.alpha_composite(coast)
    _hills(view, d, mask, seed)
    for r in rivers:
        pts = _smooth(view.line(RIVERS[r]))
        d.line(pts, fill=RIVER + (230,), width=river_w, joint="curve")
    return img


# rough mountain belts (Taurus, Armenian highland, Zagros) as (lon0, lat0, lon1, lat1) boxes
MOUNTAINS = [(36.5, 37.0, 44.5, 40.6), (42.5, 35.0, 47.5, 38.2), (44.0, 32.5, 49.5, 35.2), (30.5, 36.6, 36.5, 38.0)]


def _hills(view, d, mask, seed):
    """Small ink chevrons for relief, a fixed size on screen whatever the map scale."""
    rng = np.random.default_rng(seed + 11)
    m = np.asarray(mask)
    step = 64
    for y in range(20, view.h - 20, step):
        for x in range(20, view.w - 20, step):
            jx, jy = x + rng.uniform(-18, 18), y + rng.uniform(-14, 14)
            lon = view.lon_c + (jx - view.w / 2) / view.kx
            lat = view.lat_c - (jy - view.h / 2) / view.ky
            if not any(a <= lon <= c and b <= lat <= e for a, b, c, e in MOUNTAINS):
                continue
            if m[int(jy), int(jx)] < 128 or rng.random() < 0.55:
                continue
            s = rng.uniform(7, 11)
            d.line([(jx - s, jy + s * 0.55), (jx, jy - s * 0.45), (jx + s, jy + s * 0.55)], fill=INK + (44,), width=2)


def area_tint(view, area, colour, alpha):
    lay = Image.new("RGBA", (view.w, view.h), (0, 0, 0, 0))
    ring = _smooth(view.ring(AREAS[area]) + view.ring(AREAS[area])[:1], 5)
    ImageDraw.Draw(lay).polygon(ring, fill=tuple(colour) + (int(alpha),))
    return lay.filter(ImageFilter.GaussianBlur(3))
