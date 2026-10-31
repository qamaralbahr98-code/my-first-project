"""Narration batches (one per film part) for ElevenLabs. Kurdish digits are spoken as Kurdish words in the prompt only;
captions keep the script text exactly.

    python3 render/vo_plan.py ar|ckb|kmr
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

KMR1 = "sifir yek du sê çar pênc şeş heft heşt neh".split()
KMR10 = "deh yazdeh dazdeh sêzdeh çardeh pazdeh şanzdeh hevdeh hejdeh nozdeh".split()
KMRT = [None, None, "bîst", "sî", "çil", "pêncî", "şêst", "heftê", "heştê", "nod"]
CKB1 = "سفر یەک دوو سێ چوار پێنج شەش حەوت هەشت نۆ".split()
CKB10 = "دە یازدە دوازدە سیازدە چواردە پازدە شازدە حەڤدە هەژدە نۆزدە".split()
CKBT = [None, None, "بیست", "سی", "چل", "پەنجا", "شەست", "حەفتا", "هەشتا", "نەوەد"]


def words(n, lang):
    one, ten, tens = (KMR1, KMR10, KMRT) if lang == "kmr" else (CKB1, CKB10, CKBT)
    hundred, thousand, joiner = ("sed", "hezar", " û ") if lang == "kmr" else ("سەد", "هەزار", " و ")

    def lt1000(m):
        parts = []
        h, r = divmod(m, 100)
        if h:
            parts.append(hundred if h == 1 else f"{one[h]} {hundred}")
        if r >= 20:
            t, u = divmod(r, 10)
            parts.append(tens[t] if not u else f"{tens[t]}{joiner}{one[u]}")
        elif r >= 10:
            parts.append(ten[r - 10])
        elif r:
            parts.append(one[r])
        return joiner.join(parts)
    if n == 0:
        return one[0]
    th, r = divmod(n, 1000)
    parts = []
    if th:
        parts.append(thousand if th == 1 else f"{lt1000(th)} {thousand}")
    if r:
        parts.append(lt1000(r))
    return joiner.join(parts)


def speak(text, lang):
    if lang == "ar":
        return text
    t = text.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    pct = "sedî " if lang == "kmr" else "لە سەدا "

    def rep(m):
        lead, num, tail = m.group(1), m.group(2), m.group(3)
        w = words(int(num.replace(",", "")), lang)
        if lead == "%" or tail.startswith("%"):
            return pct + w + (tail[1:] if tail.startswith("%") else tail)
        if lang == "kmr" and tail[:1] in "aeêiîouû" and tail and w[-1] in "aeêiîouû":
            tail = "y" + tail
        return w + tail
    t = re.sub(r"(%?)(\d[\d,]*)(%?[^\s\d–\-]*)", rep, t)
    return t


def main(lang):
    sj = json.loads((ROOT / "script" / "scenes.json").read_text(encoding="utf-8"))
    parts = {}
    for s in sj["scenes"]:
        parts.setdefault(s["part"], []).append(s)
    batches = []
    for i, (p, ss) in enumerate(parts.items()):
        batches.append(dict(name=f"n{i + 1:02d}", voice="narrator", segs=[s["id"] for s in ss],
                            prompt=" [long pause] ".join(speak(s[lang]["n"], lang) for s in ss)))
    out = ROOT / "build" / lang
    (out / "vo").mkdir(parents=True, exist_ok=True)
    (out / "vo_plan.json").write_text(json.dumps(dict(batches=batches), ensure_ascii=False, indent=1), encoding="utf-8")
    for b in batches:
        print(b["name"], len(b["prompt"]))


if __name__ == "__main__":
    main(sys.argv[1])
