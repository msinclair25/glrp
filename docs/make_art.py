#!/usr/bin/env python3
"""Generate GLRP marketing images (social 1280x640, banner 2400x800)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs"
OUT.mkdir(exist_ok=True)

BG = (7, 8, 12)
INK = (236, 232, 220)
MUTED = (150, 146, 136)
AMBER = (245, 193, 92)
TEAL = (62, 224, 197)
LINE = (32, 34, 42)
CARD = (16, 17, 23)


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


F_DISPLAY = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
F_SANS = "/System/Library/Fonts/SFNS.ttf"
F_SERIF = "/System/Library/Fonts/NewYork.ttf"


def base(w: int, h: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (w, h), BG)
    px = img.load()
    # faint vertical grain + vignette
    for y in range(h):
        for x in range(0, w, 3):
            n = (x * 17 + y * 31) % 11
            if n == 0:
                c = px[x, y]
                px[x, y] = (c[0] + 6, c[1] + 6, c[2] + 7)
    glow = Image.new("RGB", (w, h), BG)
    g = ImageDraw.Draw(glow)
    g.ellipse((w * 0.55, -h * 0.3, w * 1.15, h * 0.7), fill=(40, 28, 8))
    g.ellipse((-w * 0.15, h * 0.45, w * 0.45, h * 1.25), fill=(8, 36, 32))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    img = Image.blend(img, glow, 0.45)
    draw = ImageDraw.Draw(img)
    # grid
    for x in range(0, w, 48):
        draw.line((x, 0, x, h), fill=LINE)
    for y in range(0, h, 48):
        draw.line((0, y, w, y), fill=LINE)
    # top accent bar
    draw.rectangle((0, 0, w, 4), fill=AMBER)
    return img, draw


def chip(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: tuple[int, int, int]) -> None:
    x, y = xy
    pad_x, pad_y = 18, 10
    f = font(F_SANS, 22)
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.rounded_rectangle(
        (x, y, x + tw + pad_x * 2, y + th + pad_y * 2),
        radius=8,
        outline=fill,
        width=2,
    )
    draw.text((x + pad_x, y + pad_y - 2), text, font=f, fill=fill)


def social() -> Path:
    w, h = 1280, 640
    img, draw = base(w, h)
    kicker = font(F_SANS, 22)
    title = font(F_DISPLAY, 132)
    sub = font(F_SERIF, 36)
    draw.text((72, 78), "GROK  ·  HERMES  ·  AGENTIC CODING", font=kicker, fill=AMBER)
    draw.text((68, 128), "GLRP", font=title, fill=INK)
    draw.text(
        (74, 300),
        "Pick up where you left off.",
        font=sub,
        fill=TEAL,
    )
    draw.text(
        (74, 356),
        "Writes the full plan down. Does one sitting.\nRuns a real check. The next session continues.",
        font=font(F_SANS, 26),
        fill=MUTED,
    )
    chip(draw, (74, 500), "GOAL", AMBER)
    chip(draw, (210, 500), "UNIT", TEAL)
    chip(draw, (350, 500), "CHECK", INK)
    path = OUT / "social.png"
    img.save(path, "PNG", optimize=True)
    return path


def banner() -> Path:
    w, h = 2400, 800
    img, draw = base(w, h)
    draw.text((96, 90), "FOR GROK BUILD AND HERMES", font=font(F_SANS, 28), fill=AMBER)
    draw.text((88, 150), "GLRP", font=font(F_DISPLAY, 180), fill=INK)
    draw.text((100, 380), "Pick up where you left off.", font=font(F_SERIF, 52), fill=TEAL)
    draw.text(
        (100, 460),
        "Number the work. Do one sitting. Run a check that can fail.\nClose it. The next session already knows what’s next.",
        font=font(F_SANS, 32),
        fill=MUTED,
    )
    chip(draw, (100, 640), "GOAL.md", AMBER)
    chip(draw, (300, 640), "UNIT.md", TEAL)
    chip(draw, (500, 640), "check.py", INK)
    path = OUT / "banner.png"
    img.save(path, "PNG", optimize=True)
    return path


if __name__ == "__main__":
    print(social())
    print(banner())
