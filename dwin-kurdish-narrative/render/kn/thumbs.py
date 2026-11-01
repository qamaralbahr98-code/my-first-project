"""Thumbnails per THUMBNAILS.md: A03 + giant title behind the person, saffron tag, faint 1923, logo top-left.
    python3 -m kn.thumbs
"""
import json

import numpy as np
from PIL import Image

from . import base as B
from .base import CREAM, INK, SAFFRON, T, kit, paste, PROJ
from .lib import big_text, person_layer

TITLE = {"ar": "من يملك الحكاية؟", "ckb": "چیرۆکەکە هی کێیە؟", "kmr": "ÇÎROK YA KÊ YE?"}
TAG = {"ar": "السردية الكردية", "ckb": "گێڕانەوەی کوردی", "kmr": "Vegotina Kurdî"}
NAME = "A03_person_on_ridge_sunrise.png"


def warm(im):
    a = np.asarray(im.convert("RGB")).astype(np.float32) * [1.06, 1.0, 0.92]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def shadowed_text(im):
    return B.shadowed(im, 14, (0, 6), 150)


def make(lang, fmt):
    W, H = (1920, 1080) if fmt == "16x9" else (1080, 1920)
    tl = json.loads((PROJ / "build" / lang / "timeline.json").read_text(encoding="utf-8"))
    sc = next(s for s in tl["scenes"] if s["id"] == "S04")
    c = B.Ctx(sc, lang, (W, H), {}, {})
    im = B._big(c, NAME)
    cam = B.Cam(im.width, im.height, 0.0, 1.0, 1.0, (0.5, 0.5), (0.5, 0.5), (W, H))
    f = warm(cam.view(im))
    lay = cam.view(person_layer(c, NAME, "p"))
    vert = H > W
    rtl = lang != "kmr"
    # faint 1923 in the sky
    y = T("kmr", "1923", 260 if not vert else 300, CREAM, True)
    paste(f, y, (W * 0.08 if rtl else W - y.width - W * 0.08) if not vert else W / 2 - y.width / 2,
          H * 0.06 if not vert else H * 0.04, 0.12)
    # title (behind person)
    tw = int(W * 0.94) if not vert else W - 60
    ti = shadowed_text(big_text(c, TITLE[lang], 190 if not vert else 165, CREAM, tw))
    tx = W / 2 - ti.width / 2
    ty = H * 0.57 - ti.height if not vert else H * 0.555 - ti.height
    paste(f, ti, tx, ty)
    f.alpha_composite(lay)
    tg = B.strip_img(lang, TAG[lang], 56 if not vert else 60, INK, SAFFRON)
    paste(f, tg, W / 2 - tg.width / 2, ty - tg.height + 20)
    lg = kit.logo(lang, True, 120 if not vert else 150, 1.0)
    paste(f, lg, 40, 40 if not vert else 120)
    out = PROJ / "thumbnails"
    out.mkdir(exist_ok=True)
    f = f.convert("RGB")
    if not vert:
        f = f.resize((1280, 720), Image.LANCZOS)
    p = out / f"thumb_{lang}_{fmt}.png"
    f.save(p, optimize=True)
    f.resize((160, int(160 * f.height / f.width)), Image.LANCZOS).save(out / f"preview_{lang}_{fmt}.png")
    print(p, p.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    for lang in ("ar", "ckb", "kmr"):
        for fmt in ("16x9", "9x16"):
            make(lang, fmt)
