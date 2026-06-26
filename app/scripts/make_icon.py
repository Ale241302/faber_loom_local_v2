"""Generate faberloom.ico from the brand SVG.

Reads the source SVG at ../../Diseños/faberloom_appicon512.svg and writes a
multi-resolution Windows .ico to app/static/faberloom.ico.
"""
from __future__ import annotations

import io
import struct
from pathlib import Path

from PIL import Image, ImageDraw

APP_DIR = Path(__file__).resolve().parents[1]
SVG_PATH = APP_DIR.parent / "Diseños" / "faberloom_appicon512.svg"
OUT_PATH = APP_DIR / "static" / "faberloom.ico"

SOURCE_SIZE = 512
CORAL = "#C96442"
CREAM = "#F4F1ED"
RX = 112.64

# Strokes extracted from the SVG (viewBox 48×48 inside the 512 icon).
VERTICAL = [
    ((14, 7), (14, 19)),
    ((14, 29), (14, 41)),
    ((24, 7), (24, 9)),
    ((24, 19), (24, 29)),
    ((24, 39), (24, 41)),
    ((34, 7), (34, 19)),
    ((34, 29), (34, 41)),
]
HORIZONTAL = [
    ((7, 14), (9, 14)),
    ((19, 14), (29, 14)),
    ((39, 14), (41, 14)),
    ((7, 24), (19, 24)),
    ((29, 24), (41, 24)),
    ((7, 34), (9, 34)),
    ((19, 34), (29, 34)),
    ((39, 34), (41, 34)),
]


def render(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Rounded coral background.
    draw.rounded_rectangle(
        [(0, 0), (size - 1, size - 1)],
        radius=int(RX * size / SOURCE_SIZE),
        fill=CORAL,
    )

    # The weave glyph is scaled 6.25× and translated (106,106) in the 512 icon.
    scale = 6.25 * size / SOURCE_SIZE
    tx = 106 * size / SOURCE_SIZE
    ty = 106 * size / SOURCE_SIZE
    stroke = max(1, int(3.5 * scale))

    def pt(p):
        return (p[0] * scale + tx, p[1] * scale + ty)

    for a, b in VERTICAL + HORIZONTAL:
        draw.line([pt(a), pt(b)], fill=CREAM, width=stroke, joint="curve")

    return img


def save_ico(path: Path, images: list[Image.Image]) -> None:
    """Write a multi-resolution ICO file using embedded PNG data."""
    pngs: list[bytes] = []
    for im in images:
        buf = io.BytesIO()
        im.save(buf, format="PNG")
        pngs.append(buf.getvalue())

    n = len(images)
    header = struct.pack("<HHH", 0, 1, n)
    directory = b""
    data_offset = 6 + 16 * n
    for im, png in zip(images, pngs):
        w = im.width if im.width < 256 else 0
        h = im.height if im.height < 256 else 0
        directory += struct.pack("<BBBBHHII", w, h, 0, 0, 1, 32, len(png), data_offset)
        data_offset += len(png)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        f.write(header)
        f.write(directory)
        for png in pngs:
            f.write(png)


def main() -> None:
    if not SVG_PATH.exists():
        raise FileNotFoundError(SVG_PATH)

    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = [render(s) for s in sizes]
    save_ico(OUT_PATH, images)
    print(f"[make_icon] wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
