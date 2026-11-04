"""Absolute film times of every v2 splice / cut point (for QA frame grabs and the report).

    python3 render/v2_splices.py  -> build/fix/splices.json
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def fmt(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


def main():
    res = {}
    for lang in ("ar", "ckb"):
        tl = json.loads((ROOT / "build" / lang / "timeline.json").read_text(encoding="utf-8"))
        sc = {s["id"]: s for s in tl["scenes"]}
        ops = {}
        for line in (ROOT / "build" / "fix" / f"audio_log_{lang}.txt").read_text(encoding="utf-8").split("\n"):
            m = re.match(r"\w+ (\S+): (replaced|cut) (\S+)\.\.(\S+) \(([\d.]+)-([\d.]+) s(?:, [\d.]+ s)?\)"
                         r"(?: with (\S+) \(([\d.]+) s\))?", line)
            if not m:
                continue
            sid, op, first, last, a, b, f, n = m.groups()
            ops.setdefault(sid, []).append(dict(op=op, first=first, last=last, a=float(a), b=float(b),
                                                n=float(n) if n else 0.0, file=f))
        out = []
        for sid, lst in ops.items():
            s = sc[sid]
            x = next(x for x in s["audio"] if x["seg"] == sid)
            part_end = x["src"] + x["dur"]
            shift = 0.0
            for o in sorted(lst, key=lambda o: o["a"]):
                na = o["a"] + shift
                nb = na + o["n"]
                shift += o["n"] - (o["b"] - o["a"])
                pts = []
                if na > 0.05:
                    pts.append(na)
                if o["op"] == "replaced" and nb < part_end - 0.05:
                    pts.append(nb)
                ab = [round(s["start"] + x["start"] + p - x["src"], 3) for p in pts]
                out.append(dict(scene=sid, op=o["op"], words=f"{o['first']}..{o['last']}", file=o["file"],
                                sentence_start=round(s["start"] + x["start"] + na - x["src"], 3),
                                sentence_end=round(s["start"] + x["start"] + nb - x["src"], 3),
                                splice_points=ab, splice_labels=[fmt(t) for t in ab]))
        res[lang] = out
    (ROOT / "build" / "fix" / "splices.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for lang, lst in res.items():
        for o in lst:
            print(lang, o["scene"], o["op"], fmt(o["sentence_start"]), "->", fmt(o["sentence_end"]), o["splice_labels"])


if __name__ == "__main__":
    main()
