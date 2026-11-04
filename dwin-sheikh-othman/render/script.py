"""Parse prompts/*.md (the final source) into build/script.json: one entry per scene with both languages."""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
FILES = {"ckb": "prompts/01_sorani.md", "ar": "prompts/02_arabic.md"}


def parse(path):
    t = (ROOT / path).read_text(encoding="utf-8")
    out = []
    for b in re.split(r"(?m)^(?=### S)", t)[1:]:
        m = re.match(r"### (S\w+) · (\d) ([^·]+)· (\d+):(\d\d) · ([\d.]+)s", b)
        codes = re.findall(r"```\n(.*?)\n```", b, re.S)
        f = lambda k: (re.search(rf"\*\*{k}:\*\*\s*(.*)", b) or [None, ""])[1].strip()
        out.append(dict(id=m.group(1), part=int(m.group(2)), est=float(m.group(6)), style=f("Style"), visual=f("Visual"),
                        files=f("Files"), source=f("Source line"), labels=f(r"Name labels[^*]*"), n=codes[0], t=codes[1]))
    return out


sc = {l: parse(p) for l, p in FILES.items()}
res = []
for a, k in zip(sc["ar"], sc["ckb"]):
    assert a["id"] == k["id"]
    d = {x: a[x] for x in ("id", "part", "style", "visual", "files", "source")}
    d["ar"] = dict(n=a["n"], t=a["t"], est=a["est"], labels=a["labels"])
    d["ckb"] = dict(n=k["n"], t=k["t"], est=k["est"], labels=k["labels"])
    res.append(d)
(ROOT / "build").mkdir(exist_ok=True)
(ROOT / "build" / "script.json").write_text(json.dumps(dict(scenes=res), ensure_ascii=False, indent=1), encoding="utf-8")
for l in ("ar", "ckb"):
    parts = {}
    for s in res:
        parts.setdefault(s["part"], 0)
        parts[s["part"]] += len(s[l]["n"])
    print(l, parts, sum(parts.values()), "chars; est", round(sum(s[l]["est"] for s in res) / 60, 2), "min")
