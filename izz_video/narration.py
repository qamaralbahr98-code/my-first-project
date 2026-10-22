"""Fit a narration recording to the six scenes and mix it with the music.

A narration file is one take of the whole script, read with a long pause between
scenes (ElevenLabs `[long pause]` tags, or a person pausing). We find the five
longest pauses, cut there, and start each scene's part at that scene's start
time, so the voice always matches the picture. If a part is longer than its
scene, it is moved later rather than overlapping the next part.
"""
import json
import subprocess
from pathlib import Path

import numpy as np

SR = 48000
SCENE_STARTS = [0, 10, 20, 30, 40, 50]
LEAD_IN = 0.45          # seconds after a scene starts before the voice comes in
TOTAL = 60.0


def load_mono(path, tempo=1.0):
    af = ["-af", f"atempo={tempo:.4f}"] if abs(tempo - 1) > 1e-3 else []
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), *af, "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def speech_regions(x, frame=0.02, gap=0.55):
    """Return [(start_s, end_s), ...] of speech, merging pauses shorter than `gap`."""
    n = int(frame * SR)
    frames = len(x) // n
    rms = np.sqrt(np.mean(x[: frames * n].reshape(frames, n) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    thresh = max(np.percentile(db, 95) - 32, -55)
    voiced = db > thresh
    regions, start = [], None
    for i, v in enumerate(voiced):
        if v and start is None:
            start = i
        elif not v and start is not None:
            regions.append([start * frame, i * frame])
            start = None
    if start is not None:
        regions.append([start * frame, frames * frame])
    merged = []
    for r in regions:
        if merged and r[0] - merged[-1][1] < gap:
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    return [(a, b) for a, b in merged if b - a > 0.12]


def split_scenes(x, n=6):
    """Cut at the n-1 longest pauses. Returns [(start_s, end_s)] per scene."""
    regs = speech_regions(x)
    if len(regs) < n:
        raise ValueError(f"Found only {len(regs)} spoken parts; expected {n}. "
                         "Make sure the narration pauses clearly between scenes.")
    gaps = sorted(range(len(regs) - 1), key=lambda i: regs[i + 1][0] - regs[i][1], reverse=True)[: n - 1]
    cuts = sorted(gaps)
    parts, s = [], 0
    for c in cuts:
        parts.append((regs[s][0], regs[c][1]))
        s = c + 1
    parts.append((regs[s][0], regs[-1][1]))
    return parts


GAP = 0.3               # minimum silence between two scenes' lines
END_MARGIN = 0.8        # keep the last word clear of the fade to black


def fits(parts):
    speech = sum(b - a for a, b in parts)
    return speech + GAP * (len(parts) - 1) + LEAD_IN <= TOTAL - END_MARGIN


def place(parts):
    """Decide where each part starts in the video. Returns [(video_start, src_start, src_end)].

    Each line starts at its scene (plus a short lead-in) or right after the previous line,
    whichever is later; then, if the last line would run past the end, lines are pulled
    earlier from the back, never overlapping.
    """
    starts, prev_end = [], 0.0
    for i, (a, b) in enumerate(parts):
        t = max(SCENE_STARTS[i] + LEAD_IN, prev_end + GAP)
        starts.append(t)
        prev_end = t + (b - a)
    limit = TOTAL - END_MARGIN
    for i in range(len(parts) - 1, -1, -1):
        a, b = parts[i]
        starts[i] = min(starts[i], limit - (b - a))
        limit = starts[i] - GAP
    return [(t, a, b) for t, (a, b) in zip(starts, parts)]


def build_voice_track(narration_path, out_wav):
    """Write a 60 s voice-only track with each scene's part at its scene, and return the timing."""
    x = load_mono(narration_path)
    parts = split_scenes(x)
    if not fits(parts):  # too long for 60 s: speed the read up just enough
        speech = sum(b - a for a, b in parts)
        tempo = speech / (TOTAL - END_MARGIN - LEAD_IN - GAP * (len(parts) - 1)) * 1.01
        print(f"    narration is long; speeding it up x{tempo:.2f}")
        x = load_mono(narration_path, tempo)
        parts = split_scenes(x)
    placed = place(parts)
    track = np.zeros(int(TOTAL * SR), np.float32)
    fade = int(0.03 * SR)
    for t, a, b in placed:
        seg = x[int(max(0, a - 0.06) * SR): int((b + 0.12) * SR)].copy()
        seg[:fade] *= np.linspace(0, 1, fade)
        seg[-fade:] *= np.linspace(1, 0, fade)
        i = int((t - 0.06) * SR)
        j = min(len(track), i + len(seg))
        track[i:j] += seg[: j - i]
    peak = np.max(np.abs(track)) or 1.0
    track = track / peak * 0.89
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    str(out_wav)], input=track.tobytes(), check=True)
    timing = [{"start": round(t, 3), "end": round(t + (b - a), 3)} for t, a, b in placed]
    Path(out_wav).with_suffix(".json").write_text(json.dumps(timing, indent=1))
    return timing


def mix(music_path, voice_wav, out_path):
    """Music ducked under the voice (sidechain), voice on top, loudness-normalised."""
    flt = ("[1:a]aformat=channel_layouts=stereo,volume=1.0,asplit=2[v][key];"
           "[0:a]volume=0.75[m];"
           "[m][key]sidechaincompress=threshold=0.02:ratio=8:attack=60:release=700:makeup=1[duck];"
           "[duck][v]amix=inputs=2:normalize=0:weights='1 1.15',"
           "loudnorm=I=-16:TP=-1.5:LRA=11[out]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(music_path), "-i", str(voice_wav),
                    "-filter_complex", flt, "-map", "[out]", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                    "-t", str(TOTAL), str(out_path)], check=True)
    return out_path
