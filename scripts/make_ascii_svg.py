#!/usr/bin/env python3
"""Convert the prepped grayscale photo into a self-typing monochrome ASCII SVG."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense)
#        ^ leading space clears the background to nothing

COLS = 100
ROWS = 53
CHAR_W = 6.6
CHAR_H = 12
FILL = "#c9d1d9"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

ROW_DURATION = 0.55       # seconds for one row to wipe in
ROW_STAGGER = 0.045       # delay between successive row starts


def image_to_grid(img: Image.Image, cols: int, rows: int) -> list[str]:
    small = img.convert("L").resize((cols, rows), Image.LANCZOS)
    arr = np.array(small).astype(np.float32)
    idx = (arr / 255.0 * (len(RAMP) - 1)).round().astype(int)
    idx = (len(RAMP) - 1) - idx  # dark pixel -> dense glyph
    lines = ["".join(RAMP[i] for i in row) for row in idx]
    return lines


def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(lines: list[str]) -> str:
    width = COLS * CHAR_W
    height = ROWS * CHAR_H

    defs = []
    rows_svg = []
    for r, line in enumerate(lines):
        text = escape(line) if line.strip() else escape(line.replace(" ", " "))
        clip_id = f"wipe{r}"
        start = r * ROW_STAGGER
        end = start + ROW_DURATION

        defs.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="0" y="{r * CHAR_H}" width="0" height="{CHAR_H}">'
            f'<animate attributeName="width" from="0" to="{width}" '
            f'begin="{start:.3f}s" dur="{ROW_DURATION:.3f}s" '
            f'fill="freeze" calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
            f'</rect></clipPath>'
        )

        y = (r + 1) * CHAR_H - 3
        rows_svg.append(
            f'<g clip-path="url(#{clip_id})">'
            f'<text x="0" y="{y}" font-family="{FONT}" font-size="{CHAR_H - 2}" '
            f'fill="{FILL}" xml:space="preserve">{text}</text>'
            f'<rect x="0" y="{r * CHAR_H + 1}" width="{CHAR_W}" height="{CHAR_H - 2}" fill="{FILL}">'
            f'<animate attributeName="x" from="0" to="{width}" '
            f'begin="{start:.3f}s" dur="{ROW_DURATION:.3f}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
            f'<animate attributeName="opacity" values="1;1;0" keyTimes="0;0.92;1" '
            f'begin="{start:.3f}s" dur="{ROW_DURATION:.3f}s" fill="freeze"/>'
            f'</rect>'
            f'</g>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" width="{width:.0f}" height="{height:.0f}">
  <defs>
{chr(10).join(defs)}
  </defs>
  <rect width="100%" height="100%" fill="none"/>
{chr(10).join(rows_svg)}
</svg>
'''


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("source-prepped.png")
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("yassine-ascii.svg")

    img = Image.open(src)
    lines = image_to_grid(img, COLS, ROWS)
    svg = build_svg(lines)
    dst.write_text(svg)
    print(f"wrote {dst} ({COLS}x{ROWS} grid)")


if __name__ == "__main__":
    main()
