"""Render the shared 60-second picture track (no captions) to MP4."""
import subprocess
from multiprocessing import Pool
from pathlib import Path

from PIL import Image

from .gfx import W, H, film_look, ease
from .scenes import TIMELINE, TOTAL, XFADE

FPS = 24
_cache = {}


def _shot(i):
    if i not in _cache:
        _cache[i] = TIMELINE[i][1]()
    return _cache[i]


def frame_at(T):
    starts = [s for s, _ in TIMELINE]
    i = max(k for k, s in enumerate(starts) if s <= T + 1e-9)
    img = _shot(i).frame(T - starts[i]).convert("RGB")
    # crossfade into the next shot around each boundary
    if i + 1 < len(TIMELINE):
        b = starts[i + 1]
        if T > b - XFADE / 2:
            nxt = _shot(i + 1).frame(T - b).convert("RGB")
            img = Image.blend(img, nxt, ease((T - (b - XFADE / 2)) / XFADE))
    if i > 0:
        b = starts[i]
        if T < b + XFADE / 2:
            prev = _shot(i - 1).frame(T - starts[i - 1]).convert("RGB")
            img = Image.blend(prev, img, ease((T - (b - XFADE / 2)) / XFADE))
    # fade in from black, fade out to black at the end
    k = min(1.0, T / 1.2) * min(1.0, max(0.0, (TOTAL - T) / 1.8))
    if k < 1:
        img = Image.blend(Image.new("RGB", (W, H)), img, ease(k))
    return film_look(img, int(T * FPS))


def _render_chunk(args):
    f0, f1, out = args
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
           "-pix_fmt", "yuv420p", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(f0, f1):
        p.stdin.write(frame_at(n / FPS).tobytes())
    p.stdin.close()
    p.wait()
    return out


def render_picture(out_path, workers=2):
    out_path = Path(out_path)
    tmp = out_path.parent / "chunks"
    tmp.mkdir(parents=True, exist_ok=True)
    total = int(TOTAL * FPS)
    bounds = [round(total * k / workers) for k in range(workers + 1)]
    jobs = [(bounds[k], bounds[k + 1], tmp / f"chunk{k}.mp4") for k in range(workers)]
    with Pool(workers) as pool:
        parts = pool.map(_render_chunk, jobs)
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", str(out_path)], check=True)
    return out_path
