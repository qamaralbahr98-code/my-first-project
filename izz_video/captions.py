"""Parse the script files and draw the lower-third caption cards."""
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .gfx import W, H

FONT_DIRS = [Path("/usr/share/fonts/truetype/noto"), Path(__file__).resolve().parent.parent / "fonts"]

LANGS = {
    # key: (script file, font file, direction, raqm language, label)
    "arabic": ("01_Arabic_Fusha.txt", "NotoNaskhArabic-Regular.ttf", "rtl", "ar", "Arabic"),
    "sorani": ("02_Kurdish_Sorani.txt", "NotoSansArabic-Regular.ttf", "rtl", "ckb", "Sorani"),
    "kurmanji": ("03_Kurdish_Kurmanji_Latin.txt", "NotoSans-Regular.ttf", "ltr", "ku", "Kurmanji"),
}


def font_path(name):
    for d in FONT_DIRS:
        if (d / name).exists():
            return str(d / name)
    raise FileNotFoundError(f"Font {name} not found. Install fonts-noto-core or put it in ./fonts/")


def parse_script(path):
    """Return a list of scenes: {start, end, cards: [text, ...]} from a script file."""
    text = Path(path).read_text(encoding="utf-8")
    scenes = []
    for m in re.finditer(r"SCENE\s+\d+\s+[—-]\s+(\d+):(\d+)[–-](\d+):(\d+)(.*?)(?=SCENE\s+\d+\s+[—-]|\Z)", text, re.S):
        start = int(m.group(1)) * 60 + int(m.group(2))
        end = int(m.group(3)) * 60 + int(m.group(4))
        cards = re.findall(r"Card\s*\d+:\s*(.+)", m.group(5))
        scenes.append({"start": start, "end": end, "cards": [c.strip() for c in cards]})
    return scenes


def parse_titles(path):
    titles = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*(Arabic|Sorani|Kurmanji):\s*(.+)", line)
        if m:
            titles[m.group(1).lower()] = m.group(2).strip()
    return titles


def card_times(scene, total=60.0):
    """Split a scene's time between its cards in proportion to their length."""
    s, e = scene["start"] + 0.35, min(scene["end"], total - 1.4) - 0.3
    lens = [max(len(c), 12) for c in scene["cards"]]
    gap = 0.2
    avail = e - s - gap * (len(lens) - 1)
    out, t = [], s
    for n in lens:
        d = avail * n / sum(lens)
        out.append((t, t + d))
        t += d + gap
    return out


def wrap(draw, text, font, maxw, direction, lang):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font, direction=direction, language=lang) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def render_card(text, lang_key, out_path):
    """A full-frame transparent PNG: text on a semi-transparent dark band in the lower third."""
    _, fname, direction, lang, _ = LANGS[lang_key]
    path = font_path(fname)
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    maxw = W * 0.78
    size = 50 if lang_key != "arabic" else 56
    while True:
        font = ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)
        lines = wrap(probe, text, font, maxw, direction, lang)
        if len(lines) <= 2 or size <= 30:
            break
        size -= 2
    line_h = int(size * (1.62 if direction == "rtl" else 1.32))
    widths = [probe.textlength(l, font=font, direction=direction, language=lang) for l in lines]
    pad_x, pad_y = 46, 20
    band_w = max(widths) + 2 * pad_x
    first_base = pad_y + size * (1.12 if direction == "rtl" else 1.0)
    band_h = first_base + line_h * (len(lines) - 1) + size * (0.5 if direction == "rtl" else 0.32) + pad_y
    cx = W / 2
    band_bottom = H * 0.915
    y0 = band_bottom - band_h

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(band).rounded_rectangle([cx - band_w / 2, y0, cx + band_w / 2, band_bottom], 14,
                                           fill=(10, 8, 8, 150))
    img.alpha_composite(band.filter(ImageFilter.GaussianBlur(1.2)))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds, dt = ImageDraw.Draw(shadow), ImageDraw.Draw(txt)
    for i, line in enumerate(lines):
        y = y0 + first_base + i * line_h          # baseline, text centred on cx
        ds.text((cx + 2, y + 3), line, font=font, fill=(0, 0, 0, 200), anchor="ms", direction=direction, language=lang)
        dt.text((cx, y), line, font=font, fill=(255, 255, 255, 255), anchor="ms", direction=direction, language=lang)
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(3)))
    img.alpha_composite(txt)
    img.save(out_path)
    return len(lines), size


def render_title(text, lang_key, base_frame, out_path):
    """Thumbnail: a frame from the film with the title centred over it."""
    _, fname, direction, lang, _ = LANGS[lang_key]
    font = ImageFont.truetype(font_path(fname.replace("Regular", "Bold")), 92, layout_engine=ImageFont.Layout.RAQM)
    img = base_frame.convert("RGBA")
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shade).rectangle([0, H * 0.36, W, H * 0.64], fill=(10, 8, 8, 120))
    img.alpha_composite(shade.filter(ImageFilter.GaussianBlur(40)))
    d = ImageDraw.Draw(img)
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    lines = wrap(probe, text, font, W * 0.85, direction, lang)
    asc, desc = font.getmetrics()
    total = len(lines) * (asc + desc)
    for i, line in enumerate(lines):
        lw = probe.textlength(line, font=font, direction=direction, language=lang)
        y = H / 2 - total / 2 + i * (asc + desc) - 10
        d.text((W / 2 - lw / 2 + 3, y + 4), line, font=font, fill=(0, 0, 0, 180), direction=direction, language=lang)
        d.text((W / 2 - lw / 2, y), line, font=font, fill=(255, 236, 200, 255), direction=direction, language=lang)
    img.convert("RGB").save(out_path, quality=92)
