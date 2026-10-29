"""Narration batches (one ElevenLabs recording per part of the film), text exactly from script/scenes.json.
    python3 render/vo_plan.py <lang>   -> build/<lang>/vo_plan.json
"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
PAUSE = " [long pause] "
lang = sys.argv[1]
d = json.loads((ROOT / "script" / "scenes.json").read_text(encoding="utf-8"))
segs = [dict(id=s["id"], scene=s["id"], voice="narrator", text=s[lang]["n"].strip()) for s in d["scenes"]]
parts = {}
for s in d["scenes"]:
    parts.setdefault(s["part"], []).append(s["id"])
batches = [dict(name=f"n{i + 1:02d}", voice="narrator", segs=ids,
                prompt=PAUSE.join(g["text"] for g in segs if g["id"] in ids)) for i, ids in enumerate(parts.values())]
out = ROOT / "build" / lang
(out / "vo").mkdir(parents=True, exist_ok=True)
(out / "vo_plan.json").write_text(json.dumps(dict(lang=lang, segments=segs, batches=batches), ensure_ascii=False, indent=1), encoding="utf-8")
for b in batches: print(b["name"], len(b["segs"]), len(b["prompt"]))
