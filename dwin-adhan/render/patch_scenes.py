"""Replace scenes 02, 03, 06 with a re-recorded batch; word times spread by characters over the spoken regions."""
import json, sys, urllib.request
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent))
from vo_split import load, save, split, regions, SR
ROOT = Path(__file__).resolve().parent.parent
lang, url = sys.argv[1], sys.argv[2]
vo = ROOT / "build" / lang / "vo"
mp3 = vo / "fix_02_03_06.mp3"
urllib.request.urlretrieve(url, mp3)
x = load(mp3)
segs = ["scene02", "scene03", "scene06"]
parts, cmin, kmax = split(x, 3)
print(lang, "cut gaps", cmin, "kept", round(kmax, 2))
loc = json.loads((ROOT / "locales" / f"{lang}.json").read_text(encoding="utf-8"))["scenes"]
info = json.loads((vo / "parts.json").read_text())
words = json.loads((vo / "words.json").read_text(encoding="utf-8"))
for seg, (a, e, g) in zip(segs, parts):
    a0 = max(0, a - 0.06)
    y = x[int(a0 * SR): int((e + 0.15) * SR)].copy()
    f = int(0.01 * SR); y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
    save(vo / "parts" / f"{seg}.wav", y)
    info[seg]["dur"] = round(len(y) / SR, 3)
    regs = [(max(0, r0 - a0), r1 - a0) for r0, r1 in regions(y)]
    total = sum(r1 - r0 for r0, r1 in regs)
    toks = loc[seg]["narration"].split()
    wts = [len(t) + 1 for t in toks]
    acc, out = 0.0, []
    def at(d):
        for r0, r1 in regs:
            if d <= r1 - r0:
                return r0 + d
            d -= r1 - r0
        return regs[-1][1]
    for t, wt in zip(toks, wts):
        s = acc / sum(wts) * total
        acc += wt
        out.append(dict(text=t, start=round(at(s), 3), end=round(at(acc / sum(wts) * total) - 0.02, 3)))
    words[seg] = out
    print(" ", seg, info[seg]["dur"], "s")
(vo / "parts.json").write_text(json.dumps(info, indent=1))
(vo / "words.json").write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
