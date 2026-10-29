"""Frame renderer: scenes + transitions + chapter cards + logo + source line + tags + burned captions.

  python3 -m ky.render ar 16x9 --sheet            contact sheet (2 stills per scene)
  python3 -m ky.render ar 9x16 --still S06 5.0    one still
  python3 -m ky.render ar 16x9 --chunk 0/2        render part 0 of 2 (silent) to build/ar/video_16x9/part0.mp4
  python3 -m ky.render ar 16x9 --concat 2         join the parts into picture.mp4
Run from dwin-kurd-youth/render.
"""
import json
import subprocess
import sys
import time

import numpy as np

from PIL import Image, ImageDraw

from . import base as B
from .base import CREAM, INK, PROJ, SAFFRON, clamp01, ease, kit, paste
from .scenes import SCENES, chapter_card
from .timeline import CHAPTER_PRE

FPS = 24
TR = 0.45
SIZES = {"16x9": (1920, 1080), "9x16": (1080, 1920)}
HARD_CUT = {"S03", "S11", "S16", "S23", "S27", "S33", "END"}


class Film:
    def __init__(self, lang, fmt):
        self.lang, self.fmt = lang, fmt
        self.W, self.H = SIZES[fmt]
        self.vert = self.H > self.W
        b = PROJ / "build" / lang
        self.tl = json.loads((b / "timeline.json").read_text(encoding="utf-8"))
        self.cues = json.loads((b / f"cues_{fmt}.json").read_text(encoding="utf-8"))
        self.scenes = self.tl["scenes"]
        self.total = self.tl["total"]
        self.nframes = int(round(self.total * FPS))
        self.rtl = B.RTL[lang]
        self.cache, self.last_frames, self.cur = {}, {}, None
        self.ci = 0

    def ctx(self, i):
        return B.Ctx(self.scenes[i], self.lang, (self.W, self.H), self.cache, {})

    def content(self, i, t):
        c = self.ctx(i)
        sc = self.scenes[i]
        f = SCENES[sc["id"]](c, t).convert("RGBA")
        return f, c

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
            v = self.cache.pop(k)
            if isinstance(v, B.Clip) and v.p:
                v.p.kill()
        for j in [j for j in self.last_frames if j < i - 1]:
            del self.last_frames[j]

    # -------------------------------------------------------------- overlays
    def logo(self, f):
        w = 60
        x, y = (40, 160) if self.vert else (40, 40)
        h = int(w * 1.54)
        reg = float(np.asarray(f.crop((x, y, x + w, y + h)).convert("L")).mean())
        dk = clamp01((150 - reg) / 50)
        if dk < 1:
            paste(f, kit.logo(self.lang, False, w, 0.85), x, y, 1 - dk)
        if dk > 0:
            paste(f, kit.logo(self.lang, True, w, 0.85), x, y, dk)

    def corner_tags(self, f, c, sc, tr):
        """Source line (60% opacity) and the illustration tag, in the top corner opposite the logo."""
        y = 170 if self.vert else 42
        if sc["source"] and sc["id"] != "END":
            key = ("_", "src", sc["source"])
            im = self.cache.get(key)
            if im is None:
                full = f"{B.SRC_WORD[self.lang]}: {sc['source']}"
                txt = B.fit_w(B.T(self.lang, full, 22 if self.vert else 20, CREAM, False), self.W - 260)
                im = B._pill(txt.width + 20, int(txt.height * 0.82), (0, 0, 0, 150))
                im.alpha_composite(txt, (10, int(im.height / 2 - txt.height / 2)))
                self.cache[key] = im
            paste(f, im, self.W - 36 - im.width, y, 0.6 * clamp01((tr - 0.5) / 0.5))
            y += im.height + 8
        if "illustration" in c.labels:
            key = ("_", "illus")
            p = self.cache.get(key)
            if p is None:
                p = B.pill(self.lang, B.ILLUS[self.lang], 22 if self.vert else 20, (22, 20, 18), CREAM)
                self.cache[key] = p
            paste(f, p, self.W - 36 - p.width, y, 0.7)

    def credit(self, f, c, tr):
        if not c.credit:
            return
        key = ("_", "credit", c.credit)
        im = self.cache.get(key)
        if im is None:
            txt = B.T("kmr", "▶ " + c.credit if not self.rtl else c.credit + " ◀", 24, CREAM, True)
            im = B._pill(txt.width + 24, int(txt.height * 0.9), (17, 20, 24, 215))
            ImageDraw.Draw(im).rectangle([0, 0, 6, im.height], fill=SAFFRON + (255,))
            im.alpha_composite(txt, (14, int(im.height / 2 - txt.height / 2)))
            self.cache[key] = im
        k = ease((tr - 0.3) / 0.4)
        y = (c.cap_top - 70) if not self.vert else 1330
        x = (self.W - 40 - im.width) if self.rtl else 40
        paste(f, im, x + (1 - k) * (80 if self.rtl else -80), y, k)

    def caption(self, f, t):
        while self.ci < len(self.cues) - 1 and self.cues[self.ci]["end"] < t:
            self.ci += 1
        while self.ci > 0 and self.cues[self.ci]["start"] > t:
            self.ci -= 1
        cue = self.cues[self.ci]
        if not (cue["start"] <= t < cue["end"]):
            return
        hi = -1
        for j, w in enumerate(cue["words"]):
            if w["s"] <= t + 0.02:
                hi = j
        key = ("_", "cap", self.ci, hi)
        im = self.cache.get(key)
        if im is None:
            im = self.caption_img(cue, hi)
            for k in [k for k in self.cache if k[:2] == ("_", "cap") and k[2] < self.ci]:
                del self.cache[k]
            self.cache[key] = im
        a = min(clamp01((t - cue["start"]) / 0.1), clamp01((cue["end"] - t) / 0.1))
        y = (self.H - 70 - im.height) if not self.vert else (1640 - im.height)
        paste(f, im, self.W / 2 - im.width / 2, y, a)

    def caption_img(self, cue, hi):
        size = 46 if not self.vert else 50
        words = [w["text"] for w in cue["words"]]
        ims = [B.T(self.lang, w, size, SAFFRON if j == hi else CREAM, True) for j, w in enumerate(words)]
        sp = size * 0.3
        maxw = self.W - (200 if not self.vert else 80)
        lines, cur, cw = [], [], 0
        for im in ims:
            if cur and cw + im.width - 12 + sp > maxw:
                lines.append(cur)
                cur, cw = [], 0
            cur.append(im)
            cw += im.width - 12 + sp
        if cur:
            lines.append(cur)
        line_imgs = []
        for ln in lines:
            order = ln[::-1] if self.rtl else ln
            w = int(sum(i.width - 12 for i in order) + sp * (len(order) - 1) + 12)
            h = max(i.height for i in order)
            li = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            x = 0
            for i in order:
                li.alpha_composite(i, (int(x), (h - i.height) // 2))
                x += i.width - 12 + sp
            line_imgs.append(li)
        lh = int(size * 1.5)
        w = max(i.width for i in line_imgs) + 48
        h = lh * len(line_imgs) + 22
        out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(out).rounded_rectangle([0, 0, w - 1, h - 1], 14, fill=(0, 0, 0, 178))
        for k, li in enumerate(line_imgs):
            out.alpha_composite(li, ((w - li.width) // 2, int(11 + k * lh + lh / 2 - li.height / 2)))
        return out

    # -------------------------------------------------------------- full frame
    def frame(self, n):
        t = n / FPS
        i = self.scene_at(t)
        if self.cur != i:
            self.free(i)
            self.cur = i
        sc = self.scenes[i]
        tr = t - sc["start"]
        f, c = self.content(i, tr)
        if sc.get("chapter") and tr < CHAPTER_PRE:
            card = chapter_card(c, sc["chapter"], tr)
            if tr > CHAPTER_PRE - 0.35:
                f = Image.blend(card, f, ease((tr - (CHAPTER_PRE - 0.35)) / 0.35))
            else:
                f = card
            c.labels, c.credit = [], None
        elif i > 0 and tr < TR and sc["id"] not in HARD_CUT:
            prev = self.last_frame(i - 1)
            f = B.slide(prev, f, tr / TR, self.rtl)
        if sc["id"] != "END":
            self.logo(f)
            self.corner_tags(f, c, sc, tr if not sc.get("chapter") else tr - CHAPTER_PRE)
            self.credit(f, c, tr)
        self.caption(f, t)
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
           "-r", str(FPS), "-i", "-", "-vf", "format=yuv420p", "-c:v", "libx264", "-preset",
           "veryfast", "-crf", "18", "-threads", "1", "-pix_fmt", "yuv420p", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for fn in range(f0, f1):
        p.stdin.write(film.frame(fn).tobytes())
        if (fn - f0) % 480 == 0:
            el = time.time() - t0
            done = fn - f0 + 1
            print(f"{film.lang} {film.fmt} part{k}: {done}/{f1 - f0}, {el / done:.3f}s/frame, "
                  f"eta {(f1 - fn) * el / done / 60:.1f} min", flush=True)
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
