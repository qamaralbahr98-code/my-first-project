"""QA for the v2 videos: container checks (durations, CFR, frame count), A/V sync, and frame grabs.

    python3 render/qa_v2.py <lang> <fmt>      -> build/qa/<lang>_<fmt>/  (frames, sheets, report.json)
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def fmt(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                         capture_output=True, check=True, text=True).stdout
    return json.loads(out)


def frame_times(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time",
                          "-of", "csv=p=0", str(path)], capture_output=True, check=True, text=True).stdout
    return np.sort(np.array([float(x) for x in out.split() if x.strip()]))


def audio(path, t0, dur, sr=16000):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", str(path), "-map", "0:a:0",
                          "-f", "f32le", "-ac", "1", "-ar", str(sr), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def offset(a, b, sr=16000, maxlag=0.2):
    """Lag (s) of b relative to a by cross-correlation."""
    n = min(len(a), len(b))
    a, b = a[:n] - a[:n].mean(), b[:n] - b[:n].mean()
    m = int(maxlag * sr)
    best, lag = -1e18, 0
    for k in range(-m, m + 1, 4):
        x = a[max(0, k):n + min(0, k)]
        y = b[max(0, -k):n - max(0, k)]
        v = float(np.dot(x, y))
        if v > best:
            best, lag = v, k
    for k in range(lag - 4, lag + 5):
        x = a[max(0, k):n + min(0, k)]
        y = b[max(0, -k):n - max(0, k)]
        v = float(np.dot(x, y))
        if v > best:
            best, lag = v, k
    return -lag / sr


def word_time(sc, toks):
    for w in sc["words"]:
        if any(w["text"].startswith(t) or t in w["text"] for t in toks):
            return w["s"]
    return None


def grabs(lang, vert):
    """(label, time) list for every frame the brief asks for."""
    tl = json.loads((ROOT / "build" / lang / "timeline.json").read_text(encoding="utf-8"))
    sc = {s["id"]: s for s in tl["scenes"]}
    g = [("0:54 (as asked)", 54.0), ("0:57 (as asked)", 57.0), ("7:04 (as asked)", 424.0), ("12:31 (as asked)", 751.0)]
    s = sc["S05"]
    g.append(("S05 year tag + Pris-i Saru", s["start"] + word_time(s, ["سەرو"]) + 0.3))
    s = sc["S22b"]
    g.append(("S22b salawat sign in subtitle", s["start"] + word_time(s, ["ﷺ"]) + 0.15))
    s = sc["S33"]
    g.append(("S33 Pawe in subtitle", s["start"] + word_time(s, ["پاوە"]) + 0.15))
    g.append(("S33 Sanandaj in subtitle", s["start"] + word_time(s, ["سنندج", "وسنندج", "سنە"]) + 0.15))
    s = sc["S14"]
    g.append(("S14 Sanandaj subtitle", s["start"] + word_time(s, ["سنندج", "سنە"]) + 0.15))
    s = sc["S28b"]
    g.append(("S28b Qushtapa subtitle", s["start"] + word_time(s, ["قوشت"]) + 0.15))
    # map labels: late in every map scene (all labels are in by then)
    for sid, frac in (("S05", 0.92), ("S10", 0.9), ("S11", 0.75), ("S14", 0.95), ("S19", 0.55), ("S22b", 0.3),
                      ("S28", 0.95), ("S28b", 0.5), ("S28b", 0.62), ("S31b", 0.5), ("S33", 0.97)):
        s = sc[sid]
        g.append((f"map {sid} @{int(frac * 100)}%", s["start"] + s["dur"] * frac))
    # logo
    g.append(("logo", 30.0))
    # inserted photos
    s = sc["S21"]
    t_pe = word_time(s, ["فسعى", "هەوڵی"]) - 0.2
    t_ram = word_time(s, ["رمضان،", "ڕەمەزاندا"]) - 0.6
    g.append(("photo Barzani+Talabani (S21)", s["start"] + t_pe + 1.4))
    g.append(("photo Barzani+Talabani end (S21)", s["start"] + t_ram - 0.2))
    s = sc["S22b"]
    t_89 = word_time(s, ["1989"]) - 0.4
    g.append(("photo Ahmad Jibril (S22b)", s["start"] + t_89 + 3.0))
    g.append(("photo Ahmad Jibril end (S22b)", s["start"] + s["dur"] - 0.6))
    # every splice / cut point
    sp = json.loads((ROOT / "build" / "fix" / "splices.json").read_text(encoding="utf-8"))[lang]
    for o in sp:
        for t in o["splice_points"]:
            g.append((f"splice {o['scene']} {o['op']}", t))
    return g


def main(lang, fmt_):
    ver = os.environ.get("DWIN_VER", "v02")
    vid = ROOT / "output" / f"dwin_sheikh_othman_{lang}_{fmt_}_{ver}.mp4"
    out = ROOT / "build" / "qa" / (f"{lang}_{fmt_}" + ("" if ver == "v02" else f"_{ver}"))
    out.mkdir(parents=True, exist_ok=True)
    rep = {}
    p = probe(vid)
    v = next(s for s in p["streams"] if s["codec_type"] == "video")
    a = next(s for s in p["streams"] if s["codec_type"] == "audio")
    ft = frame_times(vid)
    d = np.diff(ft)
    rep["container"] = dict(size_mb=round(int(p["format"]["size"]) / 1e6, 1), format_dur=float(p["format"]["duration"]),
                            video_dur=float(v["duration"]), audio_dur=float(a["duration"]),
                            r_frame_rate=v["r_frame_rate"], avg_frame_rate=v["avg_frame_rate"], frames=len(ft),
                            frame_step_min=round(float(d.min()), 5), frame_step_max=round(float(d.max()), 5),
                            width=v["width"], height=v["height"])
    tl = json.loads((ROOT / "build" / lang / "timeline.json").read_text(encoding="utf-8"))
    rep["container"]["timeline_dur"] = tl["total"]
    # A/V sync: the muxed audio against the mix it was made from, at start / middle / end
    mix = ROOT / "build" / lang / "audio" / "mix.wav"
    sync = {}
    for name, t in (("start", 8.0), ("middle", tl["total"] / 2), ("end", tl["total"] - 40)):
        x = audio(mix, t, 6.0)
        y = audio(vid, t, 6.0)
        sync[name] = dict(at=fmt(t), offset_ms=round(offset(x, y) * 1000, 1))
    rep["av_sync"] = sync
    # frames
    vert = fmt_ == "9x16"
    g = grabs(lang, vert)
    files = []
    for i, (lab, t) in enumerate(g):
        f = out / f"{i:02d}_{t:07.2f}.jpg"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(vid), "-frames:v", "1", "-q:v", "3",
                        str(f)], check=True)
        files.append((lab, t, f))
    rep["frames"] = [dict(label=lab, time=fmt(t), file=str(f.relative_to(ROOT))) for lab, t, f in files]
    # sheets: 8 per sheet
    font = ImageFont.truetype(FONT, 22)
    tw, th = (640, 360) if not vert else (270, 480)
    per = 8
    for k in range(0, len(files), per):
        chunk = files[k:k + per]
        cols = 4
        rows = (len(chunk) + cols - 1) // cols
        sh = Image.new("RGB", (cols * tw, rows * (th + 34)), (24, 24, 24))
        dr = ImageDraw.Draw(sh)
        for j, (lab, t, f) in enumerate(chunk):
            im = Image.open(f).convert("RGB").resize((tw, th), Image.LANCZOS)
            x, y = (j % cols) * tw, (j // cols) * (th + 34)
            sh.paste(im, (x, y))
            dr.text((x + 6, y + th + 4), f"{fmt(t)}  {lab}"[:44 if not vert else 22], font=font if not vert else
                    ImageFont.truetype(FONT, 14), fill=(240, 220, 160))
        sh.save(out / f"sheet_{k // per}.jpg", quality=88)
    (out / "report.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: rep[k] for k in ("container", "av_sync")}, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
