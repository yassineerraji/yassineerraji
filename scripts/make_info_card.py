#!/usr/bin/env python3
"""Hand-author a neofetch-style info card SVG that prints in line by line.

Edit CONTENT below with your real details.
"""
import os
from pathlib import Path

USER = "yassineerraji"

CONTENT = [
    ("About", "Engineer-minded, business-aware, endlessly curious"),
    ("Now", "AI & Data @ CentraleSupélec × ESSEC"),
    ("Exploring", "AI · Markets · Technology · Strategy · Complex Systems"),
    ("Building", "Products, systems and tools with real-world utility"),
    ("Thinking", "From first principles, tested against reality"),
    ("Learning", "Broadly, deeply and continuously"),
    ("Enjoy", "Hard problems · Clear thinking · Strong execution"),
    ("Goal", "Build things that are useful, rigorous and hard to ignore"),
]

LINE_H = 26
PAD_X = 20
TITLE_H = 40
FONT_SIZE = 13.5
CHAR_W = FONT_SIZE * 0.6   # approx advance width for ui-monospace at this size
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

BG = "#0d1117"
BORDER = "#30363d"
TITLEBAR = "#161b22"
LABEL_COLOR = "#39d353"
VALUE_COLOR = "#c9d1d9"
DIM_COLOR = "#8b949e"
DOT_COLORS = ["#ff5f56", "#ffbd2e", "#27c93f"]

STAGGER = 0.1
FADE_DUR = 0.4


def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(static: bool) -> str:
    label_col = max(len(label) for label, _ in CONTENT) + 2  # "Label:" + 1 space
    max_line_chars = max(label_col + len(value) for _, value in CONTENT)
    width = round(PAD_X * 2 + max_line_chars * CHAR_W) + 10

    height = TITLE_H + len(CONTENT) * LINE_H + 24

    dots = "".join(
        f'<circle cx="{20 + i * 18}" cy="{TITLE_H / 2}" r="6" fill="{c}"/>'
        for i, c in enumerate(DOT_COLORS)
    )

    lines_svg = []
    for i, (label, value) in enumerate(CONTENT):
        y = TITLE_H + 30 + i * LINE_H
        start = i * STAGGER
        label_span = f'<tspan fill="{LABEL_COLOR}">{escape(label + ":"):<{label_col}}</tspan>'
        text = (
            f'<text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="{FONT_SIZE}" fill="{VALUE_COLOR}" xml:space="preserve">'
            f'{label_span}<tspan fill="{VALUE_COLOR}">{escape(value)}</tspan></text>'
        )
        if static:
            lines_svg.append(f'<g>{text}</g>')
        else:
            lines_svg.append(
                f'<g opacity="0" transform="translate(-8,0)">'
                f'{text}'
                f'<animate attributeName="opacity" from="0" to="1" begin="{start:.3f}s" '
                f'dur="{FADE_DUR:.3f}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-8 0" to="0 0" begin="{start:.3f}s" dur="{FADE_DUR:.3f}s" '
                f'fill="freeze" calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
                f'</g>'
            )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" fill="{BG}" stroke="{BORDER}"/>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{TITLE_H}" rx="8" fill="{TITLEBAR}"/>
  <rect x="0.5" y="{TITLE_H / 2}" width="{width - 1}" height="{TITLE_H / 2}" fill="{TITLEBAR}"/>
  {dots}
  <text x="{width / 2}" y="{TITLE_H / 2 + 5}" font-family="{FONT}" font-size="13" fill="{DIM_COLOR}" text-anchor="middle">{escape(USER)}@github: ~</text>
{chr(10).join(lines_svg)}
</svg>
'''


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    dst = Path("info-card.svg")
    dst.write_text(build_svg(static))
    print(f"wrote {dst} (static={static})")


if __name__ == "__main__":
    main()
