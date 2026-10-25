"""Narration recording plan: two batches per language, scenes joined by [long pause] (split later at those pauses).

    python3 render/vo_plan.py ckb|kmr   -> build/<lang>/vo_plan.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAUSE = " [long pause] "
BATCHES = [["S01", "S02", "S03", "S04", "S05", "S06", "S07"], ["S08", "S09", "S10", "S11", "S12", "S13", "S14"]]


def plan(lang):
    sc = {s["id"]: s for s in json.loads((ROOT / "script" / "scenes.json").read_text(encoding="utf-8"))["scenes"]}
    segs = [dict(id=s, scene=s, voice="narrator", text=sc[s]["vo"][lang].strip()) for b in BATCHES for s in b]
    batches = [dict(name=f"n{i + 1:02d}", voice="narrator", segs=ids, prompt=PAUSE.join(sc[s]["vo"][lang].strip() for s in ids))
               for i, ids in enumerate(BATCHES)]
    return dict(lang=lang, segments=segs, batches=batches)


if __name__ == "__main__":
    lang = sys.argv[1]
    p = plan(lang)
    out = ROOT / "build" / lang
    out.mkdir(parents=True, exist_ok=True)
    (out / "vo_plan.json").write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
    for b in p["batches"]:
        print(f"=== {b['name']} ({len(b['segs'])} parts, {len(b['prompt'])} chars)")
        print(b["prompt"])
