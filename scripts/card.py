"""Draws the animated status cards (GIF) with a blinking status light.

Usage: python scripts/card.py OUT_DIR [SYNC_NUMBER]
Reads state.json and writes OUT_DIR/<mod key>.gif for every mod.
"""
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "fonts" / "Furore.otf"

W, H = 640, 184          # layout units; every coordinate below uses these
ZOOM = 1.5               # output is 1.5x the layout size (960x276)
SS = 3                   # supersampling for smooth edges
U = SS * ZOOM            # pixels per layout unit while drawing
OUT_W, OUT_H = round(W * ZOOM), round(H * ZOOM)
FRAMES, FRAME_MS = 16, 90

BG = (41, 41, 46)        # Nexus Mods page background (#29292E)
ORANGE = (255, 119, 0)   # Nexus Mods orange (#FF7700)
DIM = (150, 150, 158)
WHITE = (236, 236, 240)
STATUS = {
    "working":    ("WORKING",                  (57, 255, 136), "VERIFIED"),
    "unverified": ("GAME UPDATED - UNTESTED",  (255, 201, 51), "PATCH DETECTED"),
    "wip":        ("IN DEVELOPMENT",           (255, 201, 51), "LAST UPDATE"),
    "broken":     ("BROKEN - FIX IN PROGRESS", (255, 59, 78),  "BROKEN SINCE"),
}


def font(px):
    return ImageFont.truetype(str(FONT), round(px * U))


def fit_font(text, px, max_w):
    while px > 8 and font(px).getlength(text) > max_w * U:
        px -= 0.5
    return font(px)


def fmt_date(iso):
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d %b %Y").upper()


def glow_text(layer, xy, text, f, color, anchor="lm", glow=6):
    """Text with a soft neon glow, drawn at supersampled scale."""
    g = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).text(xy, text, font=f, fill=color + (200,), anchor=anchor)
    g = g.filter(ImageFilter.GaussianBlur(glow))
    layer.alpha_composite(g)
    ImageDraw.Draw(layer).text(xy, text, font=f, fill=color + (255,), anchor=anchor)


def s(v):
    return round(v * U)


def edge_fade(layer):
    """Multiplies a layer's alpha by a soft mask that reaches zero at the card edges."""
    mask = Image.new("L", layer.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([s(24), s(20), s(W - 24), s(H - 20)], radius=s(20), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(s(12)))
    r, g, b, a = layer.split()
    a = Image.composite(a, Image.new("L", layer.size, 0), mask)
    return Image.merge("RGBA", (r, g, b, a))


def static_layer(mod, state, sync_no, now):
    label, color, date_label = STATUS[mod["status"]]
    img = Image.new("RGBA", (s(W), s(H)), BG + (255,))
    d = ImageDraw.Draw(img)

    # soft status-coloured glow behind the light, faded out before the edges
    # so the card blends into the Nexus page background
    haze = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(haze).ellipse([s(-10), s(10), s(160), s(130)], fill=color + (34,))
    img.alpha_composite(edge_fade(haze.filter(ImageFilter.GaussianBlur(s(30)))))
    d = ImageDraw.Draw(img)

    # header
    small = font(9)
    d.text((s(26), s(20)), "LIVE STATUS  //  AUTO-CHECKED", font=small, fill=ORANGE + (255,), anchor="lm")
    d.text((s(W - 22), s(20)), f"SYNC #{sync_no:05d}", font=small, fill=DIM + (255,), anchor="rm")
    d.line([(s(20), s(32)), (s(W - 20), s(32))], fill=ORANGE + (70,), width=s(0.8))
    for k in range(6):  # tick marks
        x = W - 22 - k * 6
        d.line([(s(x), s(30)), (s(x), s(34))], fill=ORANGE + (170,), width=s(0.8))

    # title + status
    title = mod["label"].upper()
    d.text((s(80), s(60)), title, font=fit_font(title, 26, W - 80 - 24), fill=WHITE + (255,), anchor="lm")
    d.polygon([(s(80), s(83)), (s(80), s(95)), (s(88), s(89))], fill=color + (255,))
    glow_text(img, (s(96), s(89)), label, font(15), color, glow=s(2))
    d = ImageDraw.Draw(img)

    # data row
    d.line([(s(20), s(112)), (s(W - 20), s(112))], fill=ORANGE + (70,), width=s(0.8))
    patch = state.get("latest_version") or "?"
    cols = [
        ("GAME PATCH", f"V{patch}", f"BUILD {state['latest_build']}"),
        (date_label, fmt_date(mod["date"]), ""),
        ("LAST SYNC", now.strftime("%d %b %Y").upper(), now.strftime("%H:%M UTC")),
    ]
    for n, (lab, val, sub) in enumerate(cols):
        x = 26 + n * 205
        if n:
            d.line([(s(x - 12), s(122)), (s(x - 12), s(166))], fill=ORANGE + (50,), width=s(0.8))
        d.text((s(x), s(128)), lab, font=font(8.5), fill=DIM + (255,), anchor="lm")
        d.text((s(x), s(146)), val, font=font(13), fill=WHITE + (255,), anchor="lm")
        if sub:
            d.text((s(x), s(163)), sub, font=font(8.5), fill=ORANGE + (230,), anchor="lm")

    return img.resize((OUT_W, OUT_H), Image.LANCZOS)


def light(color, level):
    """The blinking status light, returned at output resolution; level 0..1."""
    size = 80  # layout units
    L = Image.new("RGBA", (s(size), s(size)), (0, 0, 0, 0))
    cx = cy = s(size) // 2
    dim = tuple(int(v * 0.35) for v in color)
    lit = tuple(int(dim[k] + (color[k] - dim[k]) * level) for k in range(3))
    halo = Image.new("RGBA", L.size, (0, 0, 0, 0))
    r = s(20)
    ImageDraw.Draw(halo).ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (int(140 * level),))
    L.alpha_composite(halo.filter(ImageFilter.GaussianBlur(s(8))))
    d = ImageDraw.Draw(L)
    r = s(13)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ORANGE + (200,), width=s(1.5))
    r = s(10)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=lit + (255,))
    r = s(3.5)  # specular highlight
    d.ellipse([cx - r - s(3), cy - r - s(3), cx + r - s(3), cy + r - s(3)],
              fill=(255, 255, 255, int(40 + 150 * level)))
    out = round(size * ZOOM)
    return L.resize((out, out), Image.LANCZOS)


def render(mod, state, sync_no, now, out_path):
    color = STATUS[mod["status"]][1]
    base = static_layer(mod, state, sync_no, now)
    frames = []
    for f in range(FRAMES):
        t = f / FRAMES
        level = 0.5 + 0.5 * math.cos(2 * math.pi * t)          # smooth pulse
        fr = base.copy()
        fr.alpha_composite(light(color, level), (round((44 - 40) * ZOOM), round((66 - 40) * ZOOM)))
        # "LIVE" dot blinks in step with the light
        dot = [round(v * ZOOM) for v in (13, 17, 19, 23)]
        ImageDraw.Draw(fr).ellipse(dot, fill=(ORANGE if level > 0.5 else DIM) + (255,))
        frames.append(fr.convert("RGB"))

    # one shared palette built from the light-on and light-off frames
    sheet = Image.new("RGB", (OUT_W, OUT_H * 2))
    sheet.paste(frames[0], (0, 0))
    sheet.paste(frames[FRAMES // 2], (0, OUT_H))
    pal = sheet.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    # reserve the last palette slot for the exact page colour so the edges are seamless
    entries = (pal.getpalette() + [0] * 768)[:768]
    entries[765:768] = BG
    pal.putpalette(entries)
    q = []
    for fr in frames:
        qf = fr.quantize(palette=pal, dither=Image.Dither.NONE)
        # Pillow's palette lookup is approximate, so snap near-page-colour pixels to the exact colour
        exact = Image.eval(ImageChops.difference(fr, Image.new("RGB", fr.size, BG)).convert("L"),
                           lambda v: 255 if v <= 3 else 0)
        qf.paste(255, mask=exact)
        q.append(qf)
    q[0].save(out_path, save_all=True, append_images=q[1:], duration=FRAME_MS, loop=0, optimize=True)


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    sync_no = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    state = json.loads((ROOT / "state.json").read_text())
    now = datetime.now(timezone.utc)
    for key, mod in state["mods"].items():
        render(mod, state, sync_no, now, out / f"{key}.gif")
        print(f"wrote {key}.gif")


if __name__ == "__main__":
    main()
