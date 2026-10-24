"""Save ElevenLabs transcription word timings and make the transcribed take the one the edit uses.

    python3 render/save_words.py <lang> status1.json [status2.json ...]
Transcribing a TTS node uses one of its takes; that take becomes <batch>_t1.mp3 (the other is kept as _alt.mp3),
and its word timings go to <batch>_words.json.
"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
lang = sys.argv[1]
vo = ROOT / "build" / lang / "vo"
sess = json.loads((vo / "sessions.json").read_text())
where = {s: (b, i + 1) for b, ids in sess.items() if b != "flow" for i, s in enumerate(ids)}
plan = {b["name"]: b for b in json.loads((ROOT / "build" / lang / "vo_plan.json").read_text(encoding="utf-8"))["batches"]}
for f in sys.argv[2:]:
    d = json.loads(Path(f).read_text())
    print(f, "completed:", d["all_completed"], "failures:", d["has_failures"])
    for tr in d.get("transcripts", []):
        url = tr["source"]["url"]
        sid = url.split("/content_generation/")[1].split("/")[0]
        b, take = where[sid]
        mp3 = vo / f"{b}_t{take}.mp3"
        if not mp3.exists():
            urllib.request.urlretrieve(url, mp3)
        if take != 1:
            t1 = vo / f"{b}_t1.mp3"
            if t1.exists():
                t1.rename(vo / f"{b}_alt.mp3")
            mp3.rename(t1)
        words = [w for w in tr["words"] if w.get("type", "word") == "word"]
        (vo / f"{b}_words.json").write_text(json.dumps(dict(text=tr["text"], words=words, dur=tr.get("spoken_duration_secs"),
                                                           take=take), ensure_ascii=False), encoding="utf-8")
        n_prompt = len(plan[b]["prompt"].split())
        flag = "" if len(words) == n_prompt else f"  <-- {len(words)} words vs {n_prompt} in the prompt"
        print(f"  {b}: take {take}, {len(words)} words, {tr.get('spoken_duration_secs')}s{flag}")
