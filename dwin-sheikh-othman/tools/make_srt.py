#!/usr/bin/env python3
"""The prompts in prompts/ are the final source. This script rebuilds subtitles/<lang>.srt,
script/scenes.json and the YouTube chapter list from them.  Run: python3 tools/make_srt.py"""
import re, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
FILES = {"ckb": "prompts/01_sorani.md", "ar": "prompts/02_arabic.md"}
CHAP = {"ar": ["المقدمة", "من الحُجرة إلى التأسيس", "السؤال الكبير", "الوقائع والشهادات", "الانتقادات: ماذا يصمد؟", "ماذا يعني لنا اليوم؟", "الخاتمة"],
        "ckb": ["پێشەکی", "لە حوجرەوە بۆ دامەزراندن", "پرسیارە گەورەکە", "ڕووداو و شایەتییەکان", "ڕەخنەکان: کامیان ڕاستە؟", "ئەمڕۆ بۆ ئێمە چی دەگەیەنێت؟", "کۆتایی"]}
def ts(sec):
    ms = int(round(sec * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
def scenes(path):
    t = (ROOT / path).read_text(encoding="utf-8")
    out = []
    for b in re.split(r"(?m)^(?=### S)", t)[1:]:
        m = re.match(r"### (S\w+) · (\d) [^·]+· (\d+):(\d\d) · ([\d.]+)s", b)
        codes = re.findall(r"```\n(.*?)\n```", b, re.S)
        out.append(dict(id=m.group(1), part=int(m.group(2)), start=int(m.group(3)) * 60 + int(m.group(4)), dur=float(m.group(5)), n=codes[0], t=codes[1]))
    return out
allsc = {}
for lang, f in FILES.items():
    sc = scenes(f); allsc[lang] = sc; srt = []
    for i, s in enumerate(sc, 1):
        srt += [str(i), f"{ts(s['start'])} --> {ts(s['start'] + s['dur'] - 0.2)}", s["n"], ""]
    (ROOT / f"subtitles/{lang}.srt").write_text("\n".join(srt), encoding="utf-8")
    seen, ch = set(), []
    for s in sc:
        if s["part"] not in seen: seen.add(s["part"]); ch.append(f"{s['start']//60}:{s['start']%60:02d} {CHAP[lang][s['part']-1]}")
    yt = ROOT / f"social/youtube_{lang}.md"; y = yt.read_text(encoding="utf-8")
    y = re.sub(r"(?m)^\d+:\d\d .*(\n\d+:\d\d .*)*", "\n".join(ch), y, count=1)
    yt.write_text(y, encoding="utf-8")
    print(lang, len(sc), "scenes,", round((sc[-1]["start"] + sc[-1]["dur"]) / 60, 1), "min")
ids = [s["id"] for s in allsc["ar"]]
assert ids == [s["id"] for s in allsc["ckb"]]
json.dump(dict(note="Generated from prompts/ (the prompts are the final source).", scenes=[
    dict(id=i, ar=dict(n=a["n"], t=a["t"]), ckb=dict(n=k["n"], t=k["t"])) for i, a, k in zip(ids, allsc["ar"], allsc["ckb"])]),
    open(ROOT / "script/scenes.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
