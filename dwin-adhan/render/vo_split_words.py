"""Cut each batch at its "[long pause]" tokens using the transcript word times.
Writes build/<lang>/vo/parts/<seg>.wav, parts.json (dur) and words.json (per-seg words, times relative to the part)."""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from vo_split import load, save, SR
ROOT = Path(__file__).resolve().parent.parent
lang = sys.argv[1]
vo = ROOT / "build" / lang / "vo"
plan = json.loads((ROOT / "build" / lang / "vo_plan.json").read_text(encoding="utf-8"))
(vo / "parts").mkdir(exist_ok=True)
info, allw = {}, {}
for b in plan["batches"]:
    x = load(vo / f"{b['name']}_t1.mp3")
    ws = json.loads((vo / f"{b['name']}_words.json").read_text(encoding="utf-8"))["words"]
    groups, cur, i = [], [], 0
    while i < len(ws):
        t = ws[i]["text"]
        if t.startswith("[long"):
            groups.append(cur); cur = []
            i += 2 if i + 1 < len(ws) and ws[i + 1]["text"].startswith("pause") else 1
            continue
        cur.append(ws[i]); i += 1
    groups.append(cur)
    groups = [g for g in groups if g]
    if len(groups) != len(b["segs"]):
        raise SystemExit(f"{lang} {b['name']}: {len(groups)} groups vs {len(b['segs'])} segs")
    for seg, g in zip(b["segs"], groups):
        a = max(0, g[0]["start"] - 0.08); e = min(len(x) / SR, g[-1]["end"] + 0.18)
        y = x[int(a * SR): int(e * SR)].copy()
        f = int(0.01 * SR); y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
        save(vo / "parts" / f"{seg}.wav", y)
        info[seg] = dict(batch=b["name"], take=1, dur=round(len(y) / SR, 3), voice=b["voice"])
        allw[seg] = [dict(text=w["text"], start=round(w["start"] - a, 3), end=round(w["end"] - a, 3)) for w in g]
    print(lang, b["name"], [info[s]["dur"] for s in b["segs"]])
(vo / "parts.json").write_text(json.dumps(info, indent=1))
(vo / "words.json").write_text(json.dumps(allw, ensure_ascii=False), encoding="utf-8")
