"""Frame renderer for the oil-spill explainer: scenes + paper-slide transitions + logo + labels (+ subtitles in 9:16).

  python3 -m oil.render ckb 16x9 --sheet           contact sheet (2 stills per scene)
  python3 -m oil.render ckb 9x16 --still S06 5.0   one still
  python3 -m oil.render ckb 16x9 --chunk 0/2       render part 0 of 2 (silent) to build/ckb/video_16x9/part0.mp4
  python3 -m oil.render ckb 16x9 --concat 2        join the parts into picture.mp4
Run from dwin-oil-spill/render.
"""
import json
import subprocess
import sys
import time

import numpy as np
from PIL import Image, ImageDraw

from . import base as B
from .base import CREAM, PROJ, clamp01, ease, kit, paste
from .scenes import SCENES

FPS = 24
TR = 0.45
SIZES = {"16x9": (1920, 1080), "9x16": (1080, 1920)}
TXT = {
    "ckb": {"iran": "ئێران", "uae": "ئیمارات", "length": "330 م", "channel": "Dween - دوین"},
    "kmr": {"iran": "Îran", "uae": "Mîrnişînên Erebî", "length": "330 m", "channel": "Dwîn - Kurmancî"},
}


class Film:
    def __init__(self, lang, fmt):
        self.lang, self.fmt = lang, fmt
        self.W, self.H = SIZES[fmt]
        self.vert = self.H > self.W
        b = PROJ / "build" / lang
        self.tl = json.loads((b / "timeline.json").read_text(encoding="utf-8"))
        self.cues = json.loads((b / "cues.json").read_text(encoding="utf-8"))
        sj = json.loads((PROJ / "script" / "scenes.json").read_text(encoding="utf-8"))
        ost = {s["id"]: s["ost"] for s in self.tl["scenes"]}
        self.txt = dict(TXT[lang], title=sj["title"][lang], illustration=sj["label_illustration"][lang],
                        uaq=ost["S02"][1])
        self.L = kit.Lang(lang, "rtl" if lang == "ckb" else "ltr")
        self.scenes = self.tl["scenes"]
        self.total = self.scenes[-1]["start"] + self.scenes[-1]["dur"]
        self.nframes = int(round(self.total * FPS))
        self.cache = {}
        self.last_frames = {}
        self.cur = None

    def ctx(self, i):
        return B.Ctx(self.scenes[i], self.lang, (self.W, self.H), self.cache, self.txt)

    def content(self, i, t):
        c = self.ctx(i)
        f = SCENES[self.scenes[i]["id"]](c, t)
        return f.convert("RGBA"), c.labels

    def last_frame(self, i):
        if i not in self.last_frames:
            self.last_frames[i] = self.content(i, self.scenes[i]["dur"] - 1 / FPS)[0]
        return self.last_frames[i]

    def scene_at(self, t):
        for i, sc in enumerate(self.scenes):
            if t < sc["start"] + sc["dur"]:
                return i
        return len(self.scenes) - 1

    def free(self, i):
        keep = {self.scenes[j]["id"] for j in range(max(0, i - 1), len(self.scenes))}
        for k in [k for k in self.cache if isinstance(k, tuple) and k and k[0] not in keep and k[0] != "_"]:
            del self.cache[k]
        for j in [j for j in self.last_frames if j < i - 1]:
            del self.last_frames[j]

    # -------------------------------------------------------------- overlays
    def logo(self, f):
        x, y, w = (40, 290, 76) if self.vert else (40, 34, 90)
        h = int(w * 1.54)
        reg = np.asarray(f.crop((x, y, x + w, y + h)).convert("L"), np.float32).mean()
        dk = clamp01((150 - reg) / 50)
        if dk < 1:
            paste(f, kit.logo(self.lang, False, w, 0.7), x, y, 1 - dk)
        if dk > 0:
            paste(f, kit.logo(self.lang, True, w, 0.7), x, y, dk)

    def label(self, f):
        key = ("_", "label")
        p = self.cache.get(key)
        if p is None:
            p = kit.pill(self.L, self.txt["illustration"], 26 if self.vert else 24, fill=(22, 20, 18), fg=CREAM)
            self.cache[key] = p
        if self.vert:
            paste(f, p, self.W - 36 - p.width, 300, 0.6)
        else:
            paste(f, p, self.W - 36 - p.width, self.H - 34 - p.height, 0.6)

    def subtitle(self, f, t):
        cue = next((q for q in self.cues if q["start"] <= t < q["end"]), None)
        if cue is None:
            return
        a = min(clamp01((t - cue["start"]) / 0.12), clamp01((cue["end"] - t) / 0.12))
        key = ("_", "sub", tuple(cue["lines"]))
        im = self.cache.get(key)
        if im is None:
            size = 44
            imgs = [B.T(self.lang, s, size, CREAM, True) for s in cue["lines"]]
            imgs = [B.fit_w(i, self.W - 120) for i in imgs]
            lh = int(size * 1.45 * self.L.k)
            w = max(i.width for i in imgs) + 44
            h = lh * len(imgs) + 24
            im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            ImageDraw.Draw(im).rounded_rectangle([0, 0, w - 1, h - 1], 12, fill=(0, 0, 0, 153))
            for k, li in enumerate(imgs):
                im.alpha_composite(li, ((w - li.width) // 2, int(12 + k * lh + lh / 2 - li.height / 2)))
            self.cache[key] = im
        paste(f, im, self.W / 2 - im.width / 2, 1630 - im.height, a)

    # -------------------------------------------------------------- full frame
    def frame(self, n):
        t = n / FPS
        i = self.scene_at(t)
        if self.cur != i:
            self.free(i)
            self.cur = i
        sc = self.scenes[i]
        tr = t - sc["start"]
        f, labels = self.content(i, tr)
        if i > 0 and tr < TR:
            prev = self.last_frame(i - 1)
            if sc["id"] == "END":
                f = Image.blend(prev, f, ease(tr / TR))
            else:
                f = B.slide(prev, f, tr / TR, self.L.rtl)
                if tr / TR < 0.5:
                    labels = []
        if sc["id"] != "END":
            self.logo(f)
        if labels:
            self.label(f)
        if self.vert:
            self.subtitle(f, t)
        return f.convert("RGB")

    def frame_scene(self, sid, tc):
        i = [s["id"] for s in self.scenes].index(sid)
        return self.frame(int(round((self.scenes[i]["start"] + tc) * FPS)))


def vid_dir(lang, fmt):
    return PROJ / "build" / lang / f"video_{fmt}"


def contact_sheet(film, out, fracs=(0.35, 0.85), ids=None):
    ids = ids or [s["id"] for s in film.scenes]
    tw, th = (480, 270) if not film.vert else (216, 384)
    per = 2 if not film.vert else 4
    cols = len(fracs) * per
    rows = (len(ids) + per - 1) // per
    sheet = Image.new("RGB", (cols * (tw + 6), rows * (th + 26)), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    for k, sid in enumerate(ids):
        sc = [s for s in film.scenes if s["id"] == sid][0]
        for j, fr in enumerate(fracs):
            t0 = time.time()
            im = film.frame_scene(sid, sc["dur"] * fr)
            dt = time.time() - t0
            im.thumbnail((tw, th))
            x = ((k % per) * len(fracs) + j) * (tw + 6)
            y = (k // per) * (th + 26)
            sheet.paste(im, (x, y))
            d.text((x + 4, y + th + 4), f"{sid} {sc['dur'] * fr:.1f}s {dt * 1000:.0f}ms", fill=(255, 255, 255))
    sheet.save(out, quality=88)


def render_chunk(film, k, n, out_dir):
    bounds, acc = [0], 0.0
    for i, sc in enumerate(film.scenes):
        acc += sc["dur"]
        if len(bounds) < n and acc >= film.total * len(bounds) / n:
            bounds.append(i + 1)
    bounds.append(len(film.scenes))
    a, b = bounds[k], bounds[k + 1]
    f0 = int(round(film.scenes[a]["start"] * FPS))
    f1 = film.nframes if b >= len(film.scenes) else int(round(film.scenes[b]["start"] * FPS))
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"part{k}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{film.W}x{film.H}",
           "-r", str(FPS), "-i", "-", "-vf", "format=yuv420p,noise=c0s=5:c0f=t+u", "-c:v", "libx264", "-preset",
           "veryfast", "-crf", "18", "-threads", "1", "-pix_fmt", "yuv420p", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for fn in range(f0, f1):
        p.stdin.write(film.frame(fn).tobytes())
        if (fn - f0) % 240 == 0:
            el = time.time() - t0
            done = fn - f0 + 1
            print(f"part{k}: {done}/{f1 - f0}, {el / done:.3f}s/frame, eta {(f1 - fn) * el / done / 60:.1f} min",
                  flush=True)
    p.stdin.close()
    p.wait()
    print(f"part{k} done: {out} ({f1 - f0} frames, {(time.time() - t0) / 60:.1f} min)", flush=True)


def concat(out_dir, n):
    lst = out_dir / "parts.txt"
    lst.write_text("".join(f"file 'part{k}.mp4'\n" for k in range(n)))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    str(out_dir / "picture.mp4")], check=True)


if __name__ == "__main__":
    lang, fmt = sys.argv[1], sys.argv[2]
    film = Film(lang, fmt)
    vd = vid_dir(lang, fmt)
    vd.mkdir(parents=True, exist_ok=True)
    if "--sheet" in sys.argv:
        ids = sys.argv[sys.argv.index("--sheet") + 1:] or None
        contact_sheet(film, vd / "sheet.jpg", ids=ids)
        print(vd / "sheet.jpg")
    elif "--still" in sys.argv:
        k = sys.argv.index("--still")
        sid, tc = sys.argv[k + 1], float(sys.argv[k + 2])
        out = vd / f"still_{sid}_{tc:.1f}.jpg"
        film.frame_scene(sid, tc).save(out, quality=92)
        print(out)
    elif "--chunk" in sys.argv:
        k, n = map(int, sys.argv[sys.argv.index("--chunk") + 1].split("/"))
        render_chunk(film, k, n, vd)
    elif "--concat" in sys.argv:
        concat(vd, int(sys.argv[sys.argv.index("--concat") + 1]))
