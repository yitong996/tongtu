#!/usr/bin/env python3
"""Regenerate Tongtu app/tray icons with transparent corners and logo mark."""

from __future__ import annotations

import os
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "tongtu-icon-1024.png"
OUT_DIR = ROOT / "src-tauri" / "icons"
ICONSET = ROOT / "assets" / "tongtu.iconset"


def make_transparent_corners(img: Image.Image) -> Image.Image:
    """Keep rounded-square content; make near-black outer corners transparent."""
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, _a = px[x, y]
            if r < 25 and g < 25 and b < 25:
                px[x, y] = (0, 0, 0, 0)
    return img


def extract_logo_mark(img: Image.Image) -> Image.Image:
    """Extract teal/navy mark on transparent background for tray."""
    src = img.convert("RGBA")
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    sp, op = src.load(), out.load()
    xs: list[int] = []
    ys: list[int] = []
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, _a = sp[x, y]
            is_teal = (
                5 <= r <= 40
                and 90 <= g <= 130
                and 85 <= b <= 130
                and g >= r + 40
            )
            is_navy = (
                5 <= r <= 50
                and 55 <= g <= 100
                and 95 <= b <= 140
                and b >= g + 20
            )
            if is_teal or is_navy:
                op[x, y] = (r, g, b, 255)
                xs.append(x)
                ys.append(y)
    bbox = (min(xs), min(ys), max(xs) + 1, max(ys) + 1)
    cropped = out.crop(bbox)
    cw, ch = cropped.size
    pad = int(max(cw, ch) * 0.12)
    side = max(cw, ch) + pad * 2
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.paste(cropped, ((side - cw) // 2, (side - ch) // 2), cropped)
    return square


def to_template_mono(mark: Image.Image, size: int) -> Image.Image:
    """Black silhouette on transparent bg for macOS menu bar template."""
    m = mark.resize((size, size), Image.Resampling.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sp, op = m.load(), out.load()
    for y in range(size):
        for x in range(size):
            _r, _g, _b, a = sp[x, y]
            if a > 20:
                op[x, y] = (0, 0, 0, a)
    return out


def save_ico(image: Image.Image, path: Path, sizes=(16, 32, 64, 128, 256)) -> None:
    image.save(path, format="ICO", sizes=[(s, s) for s in sizes])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ICONSET.mkdir(parents=True, exist_ok=True)

    base = make_transparent_corners(Image.open(SRC))
    base.save(OUT_DIR / "icon.png", optimize=True)
    print("icon.png corner", base.getpixel((0, 0)))

    for size, name in [
        (32, "32x32.png"),
        (128, "128x128.png"),
        (256, "128x128@2x.png"),
    ]:
        base.resize((size, size), Image.Resampling.LANCZOS).save(
            OUT_DIR / name, optimize=True
        )

    mapping = {
        16: ["icon_16x16.png"],
        32: ["icon_16x16@2x.png", "icon_32x32.png"],
        64: ["icon_32x32@2x.png"],
        128: ["icon_128x128.png"],
        256: ["icon_128x128@2x.png", "icon_256x256.png"],
        512: ["icon_256x256@2x.png", "icon_512x512.png"],
        1024: ["icon_512x512@2x.png"],
    }
    for size, names in mapping.items():
        im = base.resize((size, size), Image.Resampling.LANCZOS)
        for name in names:
            im.save(ICONSET / name)

    mark = extract_logo_mark(Image.open(SRC))
    color256 = mark.resize((256, 256), Image.Resampling.LANCZOS)
    for name in ("tray-icon.ico", "tray-icon-sys.ico", "tray-icon-tun.ico"):
        save_ico(color256, OUT_DIR / name)

    mono256 = to_template_mono(mark, 256)
    for name in (
        "tray-icon-mono.ico",
        "tray-icon-sys-mono.ico",
        "tray-icon-sys-mono-new.ico",
        "tray-icon-tun-mono.ico",
        "tray-icon-tun-mono-new.ico",
    ):
        save_ico(mono256, OUT_DIR / name)

    save_ico(
        base.resize((256, 256), Image.Resampling.LANCZOS),
        OUT_DIR / "icon.ico",
        sizes=(16, 32, 48, 64, 128, 256),
    )
    print("png/ico generated")


if __name__ == "__main__":
    main()
