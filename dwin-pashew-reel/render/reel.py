"""Instagram/TikTok reel (1080x1920, 25 fps) of Abdulla Pashew reciting «کوردستانتان بۆ دەکەمە شاری دوبەی».

    python3 render/reel.py ckb|ar|kmr [--still SECONDS]

Layout: the 4:3 clip full-width in the middle over a blurred, darkened copy of itself; the title and the poet's name
at the top (right of the channel logo), one subtitle phrase at a time under the picture, all clear of the Instagram
buttons (right) and caption area (bottom 320 px). The last seconds of applause end on the Dween logo card.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PROJ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJ.parent / "dwin-sheikh-othman" / "render"))
sys.path.insert(0, str(Path(__file__).parent))
from so import base as B  # noqa: E402
from so.base import CREAM, GOLD, kit  # noqa: E402
from cues import CUES, POET, TAGLINE, TITLE  # noqa: E402

W, H, FPS = 1080, 1920, 25
SRC = PROJ / "source" / "pashew_dubai.mp4"
VID_Y = 470                     # top of the 1080x810 picture
SUB_CY = 1395                   # subtitle centre (well above the bottom 320 px)
SUB_CX = 500                    # a little left of centre: the like/comment buttons sit on the right
END_CARD = 3.2                  # seconds of logo card at the very end
LANGS = {"ckb": 1, "ar": 2, "kmr": 3}


def duration():
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(SRC)],
                         capture_output=True, text=True, check=True).stdout
    return float(out)


def timed_cues():
    """Each Sorani phrase gets the time of its aligned words; translations share that time."""
    ws = json.loads((PROJ / "build" / "words_ckb.json").read_text(encoding="utf-8"))
    out, k = [], 0
    for c in CUES:
        n = len(c[0].split())
        span = ws[k:k + n]
        assert [w["text"] for w in span] == c[0].split(), (c[0], [w["text"] for w in span])
        out.append(dict(start=span[0]["start"] - 0.12, end=span[-1]["end"], texts=c))
        k += n
    for i, c in enumerate(out):
        nxt = out[i + 1]["start"] if i + 1 < len(out) else c["end"] + 3.0
        c["end"] = min(nxt - 0.04, c["end"] + 1.6)
    return out


def srt(cues, lang, path):
    def ts(x):
        ms = int(round(max(0, x) * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    path.write_text("\n".join(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['texts'][LANGS[lang] - 1]}\n"
                              for i, c in enumerate(cues, 1)), encoding="utf-8")


def card(img, pad=(34, 18), radius=22, alpha=170):
    w, h = img.width + 2 * pad[0], img.height + 2 * pad[1]
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(out).rounded_rectangle([0, 0, w - 1, h - 1], radius, fill=(12, 16, 20, alpha))
    out.alpha_composite(img, (pad[0], pad[1]))
    return out


def lines(lang, text, size, maxw, colour, gap=0.0):
    """One line if it fits, else the most balanced two-line split (no orphan word), else greedy wrapping."""
    one = B.T(lang, text, size, colour)
    if one.width <= maxw:
        return one
    words = text.split()
    best = None
    for k in range(1, len(words)):
        a, b = " ".join(words[:k]), " ".join(words[k:])
        ia, ib = B.T(lang, a, size, colour), B.T(lang, b, size, colour)
        m = max(ia.width, ib.width)
        if m <= maxw and (best is None or m < best[0]):
            best = (m, [ia, ib])
    if best:
        return B.stack(best[1], gap, "center")
    return B.stack(B.text_lines(lang, text, size, maxw, colour), gap, "center")


def shade():
    """Dark gradients behind the title zone and the subtitle zone (legibility over the blurred background)."""
    a = np.zeros((H, 1), np.float32)
    y = np.arange(H, dtype=np.float32)[:, None]
    a = np.maximum(a, np.clip(1 - (y - 380) / 140, 0, 1) * 0.62)            # top: full until 380, fades by 520
    a = np.maximum(a, np.clip((y - VID_Y - 790) / 90, 0, 1) * 0.55)          # under the picture
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = 10, 13, 16
    arr[..., 3] = (np.repeat(a, W, 1) * 255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


class Overlay:
    def __init__(self, lang):
        self.lang = lang
        self.cues = timed_cues()
        self.total = duration()
        self.logo = kit.logo(lang, True, 108, 0.92)
        t = lines(lang, TITLE[lang], 60 if lang != "kmr" else 46, 720, GOLD, -0.06)
        p = B.T(lang, POET[lang], 36 if lang != "kmr" else 30, CREAM, False)
        top = Image.new("RGBA", (max(t.width, p.width), t.height + p.height + 4), (0, 0, 0, 0))
        top.alpha_composite(t, ((top.width - t.width) // 2, 0))
        top.alpha_composite(p, ((top.width - p.width) // 2, t.height + 4))
        self.top = B.shadowed(top, 10, (0, 4), 170)
        self.subs = [B.shadowed(card(lines(lang, c["texts"][LANGS[lang] - 1], 54 if lang != "kmr" else 48, 780, CREAM,
                                           0.02)), 10, (0, 5), 120) for c in self.cues]
        self.end_logo = kit.logo(lang, True, 330, 1.0)
        self.tagline = B.shadowed(lines(lang, TAGLINE[lang], 52 if lang != "kmr" else 42, 860, CREAM, 0.0), 10,
                                  (0, 4), 150)
        self.shade = shade()

    def frame(self, f, t):
        """f: RGBA base frame (PIL). Draws everything for time t."""
        f.alpha_composite(self.shade)
        a_top = B.clamp01((t - 0.2) / 0.6) * (1 - B.clamp01((t - (self.total - END_CARD)) / 0.5))
        B.paste(f, self.top, W / 2 + 40 - self.top.width / 2, 300 - self.top.height / 2, a_top)
        for c, im in zip(self.cues, self.subs):
            if c["start"] - 0.15 <= t <= c["end"] + 0.15:
                a = B.clamp01((t - c["start"] + 0.15) / 0.15) * B.clamp01((c["end"] + 0.15 - t) / 0.15)
                B.paste(f, im, SUB_CX - im.width / 2, SUB_CY - im.height / 2, a)
        te = t - (self.total - END_CARD)
        if te > 0:
            k = B.clamp01(te / 0.6)
            dark = Image.new("RGBA", (W, H), (12, 16, 20, int(225 * k)))
            f.alpha_composite(dark)
            B.paste(f, self.end_logo, W / 2 - self.end_logo.width / 2, 860 - self.end_logo.height / 2,
                    B.ease_out(B.clamp01((te - 0.2) / 0.7)))
            ty = 860 + self.end_logo.height / 2 + 70
            B.paste(f, self.tagline, W / 2 - self.tagline.width / 2, ty + (1 - B.ease_out(B.clamp01((te - 0.7) / 0.6))) * 20,
                    B.clamp01((te - 0.7) / 0.6))
        else:
            B.paste(f, self.logo, 40, 160, 1.0)
        return f


def base_cmd():
    """Decoded base picture: blurred cover background + the clip at full width, as raw RGB frames."""
    vf = (f"[0:v]split[a][b];[a]scale=-2:{H}:flags=bicubic,crop={W}:{H},gblur=sigma=28,"
          f"colorchannelmixer=rr=0.42:gg=0.42:bb=0.42[bg];"
          f"[b]scale={W}:{W * 3 // 4}:flags=lanczos,unsharp=5:5:0.55[fg];[bg][fg]overlay=0:{VID_Y},fps={FPS}")
    return ["ffmpeg", "-v", "error", "-i", str(SRC), "-filter_complex", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]


def render(lang):
    ov = Overlay(lang)
    out = PROJ / "output" / f"pashew_dubai_reel_{lang}.mp4"
    out.parent.mkdir(exist_ok=True)
    srt(ov.cues, lang, PROJ / "output" / f"pashew_dubai_reel_{lang}.srt")
    dec = subprocess.Popen(base_cmd(), stdout=subprocess.PIPE)
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={ov.total - 1.6:.2f}:d=1.6")
    enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-i", str(SRC), "-map", "0:v", "-map", "1:a", "-af", af,
                            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-profile:v", "high",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
                            "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
    n, size = 0, W * H * 3
    while True:
        raw = dec.stdout.read(size)
        if len(raw) < size:
            break
        f = Image.frombuffer("RGB", (W, H), raw).convert("RGBA")
        f = ov.frame(f, n / FPS)
        enc.stdin.write(f.convert("RGB").tobytes())
        n += 1
    enc.stdin.close()
    enc.wait()
    dec.wait()
    print(out, n, "frames")


def still(lang, t):
    ov = Overlay(lang)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(SRC), "-filter_complex",
                          base_cmd()[6].replace(f",fps={FPS}", ""), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt",
                          "rgb24", "-"], capture_output=True, check=True).stdout
    f = Image.frombuffer("RGB", (W, H), raw[:W * H * 3]).convert("RGBA")
    p = PROJ / "build" / f"still_{lang}_{t:.1f}.jpg"
    ov.frame(f, t).convert("RGB").save(p, quality=90)
    print(p)


def sheet(lang):
    ov = Overlay(lang)
    ts = [(c["start"] + c["end"]) / 2 for c in ov.cues] + [ov.total - 1.0]
    tiles = []
    for t in ts:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(SRC), "-filter_complex",
                              base_cmd()[6].replace(f",fps={FPS}", ""), "-frames:v", "1", "-f", "rawvideo",
                              "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
        f = Image.frombuffer("RGB", (W, H), raw[:W * H * 3]).convert("RGBA")
        tiles.append(ov.frame(f, t).convert("RGB").resize((270, 480)))
    cols = 9
    out = Image.new("RGB", (cols * 270, ((len(tiles) + cols - 1) // cols) * 480), (20, 20, 20))
    for i, im in enumerate(tiles):
        out.paste(im, ((i % cols) * 270, (i // cols) * 480))
    p = PROJ / "build" / f"sheet_{lang}.jpg"
    out.save(p, quality=90)
    print(p)


if __name__ == "__main__":
    lang = sys.argv[1]
    if "--sheet" in sys.argv:
        sheet(lang)
    elif "--still" in sys.argv:
        for x in sys.argv[sys.argv.index("--still") + 1:]:
            still(lang, float(x))
    else:
        render(lang)
