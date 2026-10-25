"""Download finished ElevenLabs takes listed in saved run-status JSON files.

    python3 render/fetch_vo.py ar status1.json [status2.json ...]
Saves build/<lang>/vo/<batch>_t<take>.mp3 (take order = order of the session ids in sessions.json).
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
for f in sys.argv[2:]:
    txt = Path(f).read_text()
    try:
        d = json.loads(txt)
    except json.JSONDecodeError:
        d = json.loads(json.loads(txt)[0]["text"]) if txt.startswith("[") else None
    gens = d.get("generations", [])
    for g in gens:
        url = g.get("content_url")
        sid = url.split("/content_generation/")[1].split("/")[0] if url else None
        if not url:
            print("not ready:", g["id"], g["status"], g.get("error_message", ""))
            continue
        b, t = where[sid]
        out = vo / f"{b}_t{t}.mp3"
        if out.exists():
            continue
        urllib.request.urlretrieve(url, out)
        print("saved", out.name, g.get("duration_secs"))
