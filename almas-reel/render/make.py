"""Build the finished reels: python3 render/make.py [ckb kmr ar]"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reel                      # noqa: E402
import sound                     # noqa: E402

REEL = HERE.parent
OUT = REEL / "output"
BUILD = REEL / "build"


def audio(key):
    reel._init(key)
    TL = reel.Timeline(reel.LANGS[key])
    wav = sound.build(TL.cards, TL.events, TL.n / reel.FPS, BUILD / f"sound_{key}.wav")
    return sound.master(wav, BUILD / f"sound_{key}.m4a")


def make(key):
    OUT.mkdir(exist_ok=True)
    a = audio(key)
    pic = BUILD / f"picture_{key}.mp4"
    reel.render_video(key, pic)
    out = OUT / f"dwin_almas_{key}_v01.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(pic), "-i", str(a), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "copy", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    print("wrote", out)
    return out


if __name__ == "__main__":
    for k in (sys.argv[1:] or ["ckb", "kmr", "ar"]):
        make(k)
