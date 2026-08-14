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


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


F_DISPLAY = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
F_SANS = "/System/Library/Fonts/SFNS.ttf"
F_SERIF = "/System/Library/Fonts/NewYork.ttf"

PROBLEM = "Long coding sessions with Grok keeps dying."
SOLUTION = (
    "A tiny skill. It writes the plan as a numbered list, does one step,\n"
    "runs a real test, writes down the next step.\n"
    "Next chat reads that file and keeps going."
)


def base(w: int, h: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (w, h), BG)
    px = img.load()
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
    for x in range(0, w, 48):
        draw.line((x, 0, x, h), fill=LINE)
    for y in range(0, h, 48):
        draw.line((0, y, w, y), fill=LINE)
    draw.rectangle((0, 0, w, 4), fill=AMBER)
    return img, draw


def social() -> Path:
    w, h = 1280, 640
    img, draw = base(w, h)
    draw.text((72, 56), "GROK  ·  HERMES", font=font(F_SANS, 20), fill=AMBER)
    draw.text((68, 92), "GLRP", font=font(F_DISPLAY, 96), fill=INK)

    draw.text((74, 230), "PROBLEM", font=font(F_SANS, 18), fill=AMBER)
    draw.text((74, 258), PROBLEM, font=font(F_SERIF, 30), fill=INK)

    draw.text((74, 330), "SOLUTION", font=font(F_SANS, 18), fill=TEAL)
    draw.text((74, 358), SOLUTION, font=font(F_SANS, 24), fill=MUTED, spacing=8)

    path = OUT / "social.png"
    img.save(path, "PNG", optimize=True)
    return path


def banner() -> Path:
    w, h = 2400, 800
    img, draw = base(w, h)
    draw.text((96, 64), "FOR GROK BUILD AND HERMES", font=font(F_SANS, 26), fill=AMBER)
    draw.text((88, 110), "GLRP", font=font(F_DISPLAY, 140), fill=INK)

    draw.text((100, 300), "PROBLEM", font=font(F_SANS, 22), fill=AMBER)
    draw.text((100, 338), PROBLEM, font=font(F_SERIF, 40), fill=INK)

    draw.text((100, 430), "SOLUTION", font=font(F_SANS, 22), fill=TEAL)
    draw.text((100, 472), SOLUTION, font=font(F_SANS, 30), fill=MUTED, spacing=10)

    path = OUT / "banner.png"
    img.save(path, "PNG", optimize=True)
    return path


if __name__ == "__main__":
    print(social())
    print(banner())
