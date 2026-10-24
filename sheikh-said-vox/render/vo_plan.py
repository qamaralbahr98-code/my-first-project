"""Split the narration into recording batches for ElevenLabs.

Scenes marked with the quote voice start with a short narrator lead-in ("قال الشيخ:")
followed by the Sheikh's words in « ». The narrator reads the lead-in; the older quote
voice reads the words. Text is taken from script/master.json exactly as written.

    python3 sheikh-said-vox/render/vo_plan.py ar     # writes build/<lang>/vo_plan.json and prints the prompts
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAUSE = " [long pause] "

# narrator batches (scene ids); each batch is one recording, split later at its longest pauses
BATCHES = [
    ["S01", "S02", "S03"],
    ["S04", "S05", "S06"],
    ["S07", "S08", "S09", "S10"],
    ["S11", "S12", "S13", "S14", "S15", "S16", "S17"],
    ["S18", "S19", "S20", "S21"],
    ["S22", "S23", "S24", "S25"],
    ["S26", "S27", "S28", "S29", "S30"],
    ["S31", "S32", "S33", "S34"],
    ["S35", "S36", "S37"],
    ["S38", "S39", "S40", "S41", "S42", "S43"],
    ["S44", "S45", "S46", "S47", "S48"],
    ["S49", "S50", "S51", "S52", "S53"],
]


def segments(lang):
    m = json.loads((ROOT / "script" / "master.json").read_text(encoding="utf-8"))
    segs = []
    for s in m["scenes"]:
        text = s["vo"][lang].strip()
        if not text:
            continue
        if s.get("voice") == "quote" and "«" in text:
            i = text.index("«")
            lead, quote = text[:i].strip(), text[i:].strip()
            if lead:
                segs.append(dict(id=s["id"] + "a", scene=s["id"], voice="narrator", text=lead))
            segs.append(dict(id=s["id"] + "q", scene=s["id"], voice="quote", text=quote))
        else:
            segs.append(dict(id=s["id"], scene=s["id"], voice="narrator", text=text))
    return segs


def plan(lang):
    segs = segments(lang)
    batches = []
    for i, ids in enumerate(BATCHES):
        part = [g for g in segs if g["scene"] in ids and g["voice"] == "narrator"]
        batches.append(dict(name=f"n{i + 1:02d}", voice="narrator", segs=[g["id"] for g in part],
                            prompt=PAUSE.join(g["text"] for g in part)))
    # quotes: S43 is recorded on its own (a combined take was blocked by the TTS filter)
    q = [g for g in segs if g["voice"] == "quote"]
    for name, part in (("q01", [g for g in q if g["scene"] != "S43"]), ("q02", [g for g in q if g["scene"] == "S43"])):
        batches.append(dict(name=name, voice="quote", segs=[g["id"] for g in part],
                            prompt="[slowly] [deep voice] " + PAUSE.join(g["text"] for g in part)))
    covered = [s for b in batches for s in b["segs"]]
    assert sorted(covered) == sorted(g["id"] for g in segs), "every segment must be in exactly one batch"
    return dict(lang=lang, segments=segs, batches=batches)


if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) > 1 else "ar"
    p = plan(lang)
    out = ROOT / "build" / lang
    out.mkdir(parents=True, exist_ok=True)
    (out / "vo_plan.json").write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
    for b in p["batches"]:
        print(f"=== {b['name']} ({b['voice']}, {len(b['segs'])} parts, {len(b['prompt'])} chars)")
        print(b["prompt"])
