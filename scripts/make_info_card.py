#!/usr/bin/env python3
"""Hand-author a neofetch-style info card SVG that prints in line by line.

Edit CONTENT below with your real details -- these are fictional placeholders.
"""
import os
from pathlib import Path

CONTENT = {
    "user": "yassineerraji",
    "now": "Software Engineer @ Fictional Co.",
    "prev": "CS Student, Freelance Dev",
    "stack": "Python · TypeScript · React · Docker",
    "highlights": [
        "Open-source contributor",
        "Built 10+ side projects",
    ],
}

WIDTH = 490
LINE_H = 26
PAD_X = 20
TITLE_H = 40
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

BG = "#0d1117"
BORDER = "#30363d"
TITLEBAR = "#161b22"
LABEL_COLOR = "#39d353"
VALUE_COLOR = "#c9d1d9"
DIM_COLOR = "#8b949e"
DOT_COLORS = ["#ff5f56", "#ffbd2e", "#27c93f"]

STAGGER = 0.12
FADE_DUR = 0.4


def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_rows():
    rows = [("now", "Now", CONTENT["now"]), ("prev", "Prev", CONTENT["prev"]), ("stack", "Stack", CONTENT["stack"])]
    for i, h in enumerate(CONTENT["highlights"]):
        label = "Highlights" if i == 0 else ""
        rows.append((f"hl{i}", label, h))
    return rows


def build_svg(static: bool) -> str:
    rows = build_rows()
    height = TITLE_H + len(rows) * LINE_H + 24

    dots = "".join(
        f'<circle cx="{20 + i * 18}" cy="{TITLE_H / 2}" r="6" fill="{c}"/>'
        for i, c in enumerate(DOT_COLORS)
    )

    lines_svg = []
    for i, (key, label, value) in enumerate(rows):
        y = TITLE_H + 30 + i * LINE_H
        start = i * STAGGER
        label_span = f'<tspan fill="{LABEL_COLOR}">{escape(label + ":"):<11}</tspan> ' if label else " " * 12
        text = (
            f'<text x="{PAD_X}" y="{y}" font-family="{FONT}" font-size="13.5" fill="{VALUE_COLOR}" xml:space="preserve">'
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

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}">
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="8" fill="{BG}" stroke="{BORDER}"/>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{TITLE_H}" rx="8" fill="{TITLEBAR}"/>
  <rect x="0.5" y="{TITLE_H / 2}" width="{WIDTH - 1}" height="{TITLE_H / 2}" fill="{TITLEBAR}"/>
  {dots}
  <text x="{WIDTH / 2}" y="{TITLE_H / 2 + 5}" font-family="{FONT}" font-size="13" fill="{DIM_COLOR}" text-anchor="middle">{escape(CONTENT["user"])}@github: ~</text>
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
