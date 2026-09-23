"""Draws a badge PNG in the Shields.io "flat" layout, using the Furore font."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = Path(__file__).resolve().parent.parent / "fonts" / "Furore.otf"
SCALE = 1.05     # 5% bigger than a standard 20px Shields.io badge
SS = 4           # supersampling for smooth edges
COLORS = {
    "brightgreen": "#44bb00",
    "orange": "#fe7d37",
    "red": "#e05d44",
    "blue": "#007ec6",
}
LABEL_BG = "#555555"


def render(label, message, color, out_path):
    s = SCALE * SS
    height = round(20 * s)
    pad = round(6 * s)
    font = ImageFont.truetype(str(FONT), round(10.5 * s))

    def text_width(t):
        return round(font.getlength(t))

    lw = text_width(label) + 2 * pad
    mw = text_width(message) + 2 * pad
    w = lw + mw

    img = Image.new("RGBA", (w, height), (0, 0, 0, 0))
    bg = Image.new("RGBA", (w, height))
    d = ImageDraw.Draw(bg)
    d.rectangle([0, 0, lw, height], fill=LABEL_BG)
    d.rectangle([lw, 0, w, height], fill=COLORS.get(color, color))
    # Shields-style subtle top-to-bottom shading
    shade = Image.new("RGBA", (w, height))
    sd = ImageDraw.Draw(shade)
    for y in range(height):
        a = int(26 * y / height)
        sd.line([(0, y), (w, y)], fill=(0, 0, 0, a))
    bg = Image.alpha_composite(bg, shade)

    mask = Image.new("L", (w, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, height - 1], radius=round(3 * s), fill=255)
    img.paste(bg, (0, 0), mask)

    d = ImageDraw.Draw(img)
    cy = height / 2
    off = round(1 * s)
    for text, cx in ((label, lw / 2), (message, lw + mw / 2)):
        d.text((cx, cy + off), text, font=font, fill=(1, 1, 1, 90), anchor="mm")
        d.text((cx, cy), text, font=font, fill="white", anchor="mm")

    final = img.resize((round(w / SS), round(height / SS)), Image.LANCZOS)
    final.save(out_path, optimize=True)
