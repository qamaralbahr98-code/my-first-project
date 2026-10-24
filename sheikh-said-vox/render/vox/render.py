"""Frame renderer: scenes + chapter cards + paper-slide transitions + logo + image labels + subtitles.

  python3 -m vox.render ar --sheet                 contact sheet of every scene (2 stills each)
  python3 -m vox.render ar --still S04 3.5         one still at content time 3.5 s of S04
  python3 -m vox.render ar --chunk 0/2             render part 0 of 2 to build/ar/video/part0.mp4 (silent)
  python3 -m vox.render ar --concat 2              join the parts into build/ar/video/picture.mp4
Run from sheikh-said-vox/render.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from . import kit
from .kit import CREAM, H, W, clamp01, ease, paste
from .scenes import SCENES
from .shots import Ctx, chapter_card, slide

FPS = 24
TR = 0.45            # paper-slide transition at the start of each scene
PROJ = kit.PROJ


class Film:
    def __init__(self, lang):
        self.lang = lang
        b = PROJ / "build" / lang
        self.tl = json.loads((b / "timeline.json").read_text(encoding="utf-8"))
        self.cues = json.loads((b / "cues.json").read_text(encoding="utf-8"))
        sj = json.loads((PROJ / "script" / f"scenes.{lang}.json").read_text(encoding="utf-8"))
        m = json.loads((PROJ / "script" / "master.json").read_text(encoding="utf-8"))
        self.L = kit.Lang(lang, sj["direction"])
        self.types = {i["file"]: i["type"] for i in m["images"]}
        labels = {k: v[lang] for k, v in m["labels"].items()}
        ost = {s["id"]: s["ost"] for s in self.tl["scenes"]}
        self.extra = {"labels": labels, "azadi": ost["S18"][0], "allies": ost["S21"][0]}
        self.scenes = self.tl["scenes"]
        self.total = self.scenes[-1]["start"] + self.scenes[-1]["dur"]
        self.nframes = int(round(self.total * FPS))
        self.cache = {}
        self.last_frames = {}
        self.cur_scene = None

    # -------------------------------------------------------------- scene content
    def ctx(self, i):
        return Ctx(self.scenes[i], self.L, self.lang, self.types, self.extra, self.cache)

    def content(self, i, t_rel):
        """Scene i at time t_rel (from its start, card included) -> (RGBA frame, labels, in_card)."""
        sc = self.scenes[i]
        c = self.ctx(i)
        if t_rel < sc["card"]:
            title = sc["chapter_title"][self.lang]
            return chapter_card(c, sc["chapter"] - 1, title, t_rel), [], True
        f = SCENES[sc["id"]](c, t_rel - sc["card"])
        return f.convert("RGBA"), c.labels, False

    def last_frame(self, i):
        if i not in self.last_frames:
            sc = self.scenes[i]
            self.last_frames[i] = self.content(i, sc["dur"] - 1 / FPS)[0]
        return self.last_frames[i]

    def scene_at(self, t):
        for i, sc in enumerate(self.scenes):
            if t < sc["start"] + sc["dur"]:
                return i
        return len(self.scenes) - 1

    def free(self, i):
        """Drop cached items of scenes before i (memory)."""
        keep = {self.scenes[j]["id"] for j in range(max(0, i - 1), len(self.scenes))}
        for k in [k for k in self.cache if isinstance(k, tuple) and k[0] not in keep]:
            del self.cache[k]
        for j in [j for j in self.last_frames if j < i - 1]:
            del self.last_frames[j]

    # -------------------------------------------------------------- overlays
    def logo(self, frame):
        reg = np.asarray(frame.crop((30, 24, 150, 144)).convert("L"), np.float32).mean()
        dk = clamp01((150 - reg) / 50)
        x, y = 40, 34
        if dk < 1:
            paste(frame, kit.logo(self.lang, False), x, y, 1 - dk)
        if dk > 0:
            paste(frame, kit.logo(self.lang, True), x, y, dk)

    def image_label(self, frame, key):
        text = self.extra["labels"][key]
        p = self.cache.get(("_lab", text))
        if p is None:
            p = kit.pill(self.L, text, 24, fill=(22, 20, 18), fg=CREAM)
            self.cache[("_lab", text)] = p
        paste(frame, p, W - 36 - p.width, H - 34 - p.height, 0.6)

    def subtitle(self, frame, t):
        cue = None
        for q in self.cues:
            if q["start"] <= t < q["end"]:
                cue = q
                break
        if cue is None:
            return
        a = min(clamp01((t - cue["start"]) / 0.12), clamp01((cue["end"] - t) / 0.12))
        key = ("_sub", tuple(cue["lines"]))
        im = self.cache.get(key)
        if im is None:
            imgs = [kit.mixed_line_img(self.L.key, self.L.dir, s, 40, CREAM, 0)
                    if (self.L.key != "ar" and any(kit.needs_alt_font(w, self.L.dir) for w in s.split()))
                    else kit.line_img(self.L.key, self.L.dir, s, 40, CREAM, 0)[0]
                    for s in cue["lines"]]
            lh = int(40 * 1.5 * self.L.k)
            w = max(i.width for i in imgs) + 44
            h = lh * len(imgs) + 22
            im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            ImageDraw.Draw(im).rounded_rectangle([0, 0, w - 1, h - 1], 10, fill=(0, 0, 0, 153))
            for k, li in enumerate(imgs):
                im.alpha_composite(li, ((w - li.width) // 2, int(11 + k * lh + lh / 2 - li.height / 2)))
            self.cache[key] = im
        paste(frame, im, W / 2 - im.width / 2, H - 58 - im.height, a)

    # -------------------------------------------------------------- full frame
    def frame(self, n, subs=True):
        t = n / FPS
        i = self.scene_at(t)
        if self.cur_scene != i:
            self.free(i)
            self.cur_scene = i
        sc = self.scenes[i]
        t_rel = t - sc["start"]
        f, labels, in_card = self.content(i, t_rel)
        if i > 0 and t_rel < TR:
            prev = self.last_frame(i - 1)
            if sc["id"] == "S54":
                f = Image.blend(prev, f, ease(t_rel / TR))
            else:
                f = slide(prev, f, t_rel / TR, self.L.rtl)
                if t_rel / TR < 0.5:
                    labels = []
        if not in_card and sc["id"] != "S54":
            self.logo(f)
        if labels:
            self.image_label(f, labels[-1])
        if subs:
            self.subtitle(f, t)
        return f.convert("RGB")

    def frame_scene(self, sid, t_content, subs=True):
        i = [s["id"] for s in self.scenes].index(sid)
        sc = self.scenes[i]
        n = int(round((sc["start"] + sc["card"] + t_content) * FPS))
        return self.frame(n, subs)


# ------------------------------------------------------------------ outputs
def contact_sheet(film, out, fracs=(0.3, 0.8), ids=None):
    ids = ids or [s["id"] for s in film.scenes]
    tw, th = 480, 270
    cols = len(fracs) * 2
    rows = (len(ids) + 1) // 2
    sheet = Image.new("RGB", (cols * (tw + 6), rows * (th + 26)), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    for k, sid in enumerate(ids):
        sc = [s for s in film.scenes if s["id"] == sid][0]
        D = sc["dur"] - sc["card"]
        for j, fr in enumerate(fracs):
            t0 = time.time()
            im = film.frame_scene(sid, D * fr)
            dt = time.time() - t0
            im.thumbnail((tw, th))
            x = ((k % 2) * len(fracs) + j) * (tw + 6)
            y = (k // 2) * (th + 26)
            sheet.paste(im, (x, y))
            d.text((x + 4, y + th + 4), f"{sid} t={D * fr:.1f}  {dt * 1000:.0f}ms", fill=(255, 255, 255))
    sheet.save(out, quality=88)


def render_chunk(film, k, n, out_dir):
    # split by scenes, balanced by duration
    total = film.total
    bounds = [0]
    acc = 0
    for i, sc in enumerate(film.scenes):
        acc += sc["dur"]
        if len(bounds) < n and acc >= total * len(bounds) / n:
            bounds.append(i + 1)
    bounds.append(len(film.scenes))
    a, b = bounds[k], bounds[k + 1]
    f0 = int(round(film.scenes[a]["start"] * FPS))
    f1 = film.nframes if b >= len(film.scenes) else int(round(film.scenes[b]["start"] * FPS))
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"part{k}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
           str(FPS), "-i", "-", "-vf", "format=yuv420p,noise=c0s=7:c0f=t+u", "-c:v", "libx264", "-preset",
           "veryfast", "-crf", "18", "-threads", "1", "-pix_fmt", "yuv420p", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for fn in range(f0, f1):
        p.stdin.write(film.frame(fn).tobytes())
        if (fn - f0) % 240 == 0:
            el = time.time() - t0
            done = fn - f0 + 1
            print(f"part{k}: {done}/{f1 - f0} frames, {el / done:.3f}s/frame, eta {(f1 - fn) * el / done / 60:.1f} min",
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
    lang = sys.argv[1]
    film = Film(lang)
    vid = PROJ / "build" / lang / "video"
    if "--sheet" in sys.argv:
        ids = sys.argv[sys.argv.index("--sheet") + 1:] or None
        vid.mkdir(parents=True, exist_ok=True)
        contact_sheet(film, vid / "sheet.jpg", ids=ids)
        print(vid / "sheet.jpg")
    elif "--still" in sys.argv:
        k = sys.argv.index("--still")
        sid, tc = sys.argv[k + 1], float(sys.argv[k + 2])
        vid.mkdir(parents=True, exist_ok=True)
        out = vid / f"still_{sid}_{tc:.1f}.jpg"
        film.frame_scene(sid, tc).save(out, quality=92)
        print(out)
    elif "--chunk" in sys.argv:
        k, n = map(int, sys.argv[sys.argv.index("--chunk") + 1].split("/"))
        render_chunk(film, k, n, vid)
    elif "--concat" in sys.argv:
        concat(vid, int(sys.argv[sys.argv.index("--concat") + 1]))
