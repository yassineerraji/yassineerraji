#!/usr/bin/env python3
"""Render data/contributions.json as an animated 53x7 contribution heatmap SVG."""
import datetime as dt
import json
import os
from pathlib import Path

PALETTE = ["#161b22", "#0e4429", "#006d32",
           "#26a641", "#39d353", "#69f0a0"]
#          none -> brightest (level 5 is a neon top end)

BOX = 11
GAP = 3
CELL = BOX + GAP
LEFT_PAD = 28
TOP_PAD = 20
BOTTOM_PAD = 44
DAY_LABELS = ["", "Mon", "", "Wed", "", "Fri", ""]
MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

STAGGER = 0.012
BOX_DUR = 0.35
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
DIM = "#8b949e"


def build_weeks(days: list[dict]) -> list[list[dict | None]]:
    by_date = {d["date"]: d for d in days}
    if not days:
        return []
    start = dt.date.fromisoformat(days[0]["date"])
    end = dt.date.fromisoformat(days[-1]["date"])

    # Align to the Sunday on/before `start` so weeks are Sun..Sat columns.
    grid_start = start - dt.timedelta(days=(start.weekday() + 1) % 7)

    weeks: list[list[dict | None]] = []
    cur = grid_start
    week: list[dict | None] = []
    while cur <= end:
        key = cur.isoformat()
        week.append(by_date.get(key))
        if len(week) == 7:
            weeks.append(week)
            week = []
        cur += dt.timedelta(days=1)
    if week:
        while len(week) < 7:
            week.append(None)
        weeks.append(week)
    return weeks


def month_ticks(weeks: list[list[dict | None]]) -> list[tuple[int, str]]:
    ticks = []
    last_month = None
    for wi, week in enumerate(weeks):
        first = next((d for d in week if d), None)
        if not first:
            continue
        month = dt.date.fromisoformat(first["date"]).month
        if month != last_month:
            ticks.append((wi, MONTH_LABELS[month - 1]))
            last_month = month
    return ticks


def build_svg(data: dict, static: bool = False) -> str:
    days = data["days"]
    weeks = build_weeks(days)
    best_date = data["best_day"]["date"] if data["best_day"] else None

    n_weeks = len(weeks)
    width = LEFT_PAD + n_weeks * CELL + 30
    height = TOP_PAD + 7 * CELL + BOTTOM_PAD

    boxes = []
    i = 0
    for col, week in enumerate(weeks):
        for row, day in enumerate(week):
            x = LEFT_PAD + col * CELL
            y = TOP_PAD + row * CELL
            if day is None:
                i += 1
                continue
            level = min(day["level"], 4)
            color = PALETTE[level]
            if day["date"] == best_date and level == 4:
                color = PALETTE[5]
            title = f'<title>{day["date"]}: {day["count"]} contributions</title>'
            if static:
                boxes.append(
                    f'<rect x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="2" fill="{color}">{title}</rect>'
                )
            else:
                delay = (col + row) * STAGGER
                boxes.append(
                    f'<rect x="{x}" y="{y - 6}" width="{BOX}" height="{BOX}" rx="2" fill="{color}" opacity="0">'
                    f'{title}'
                    f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.3f}s" dur="{BOX_DUR:.3f}s" fill="freeze"/>'
                    f'<animate attributeName="y" from="{y - 6}" to="{y}" begin="{delay:.3f}s" dur="{BOX_DUR:.3f}s" '
                    f'fill="freeze" calcMode="spline" keySplines="0.25 0.1 0.25 1"/>'
                    f'</rect>'
                )
            i += 1

    day_labels = "".join(
        f'<text x="{LEFT_PAD - 6}" y="{TOP_PAD + r * CELL + BOX - 1}" font-family="{FONT}" '
        f'font-size="9" fill="{DIM}" text-anchor="end">{lbl}</text>'
        for r, lbl in enumerate(DAY_LABELS) if lbl
    )

    month_labels = "".join(
        f'<text x="{LEFT_PAD + wi * CELL}" y="{TOP_PAD - 6}" font-family="{FONT}" '
        f'font-size="9" fill="{DIM}">{lbl}</text>'
        for wi, lbl in month_ticks(weeks)
    )

    legend_y = height - 24
    less_w, gap, more_w = 26, 8, 32
    box_group_w = len(PALETTE) * (BOX + 4) - 4
    legend_w = less_w + gap + box_group_w + gap + more_w
    legend_x = width - 12 - legend_w
    boxes_x0 = legend_x + less_w + gap
    more_x = boxes_x0 + box_group_w + gap

    legend_boxes = "".join(
        f'<rect x="{boxes_x0 + idx * (BOX + 4)}" y="{legend_y}" width="{BOX}" height="{BOX}" rx="2" fill="{c}"/>'
        for idx, c in enumerate(PALETTE)
    )

    footer = f'{data["total"]} contributions in the last year · {data["longest_streak"]}-day best streak'

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="none"/>
  {month_labels}
  {day_labels}
{chr(10).join(boxes)}
  <text x="{LEFT_PAD}" y="{legend_y + BOX - 1}" font-family="{FONT}" font-size="10" fill="{DIM}">{footer}</text>
  <text x="{legend_x}" y="{legend_y + BOX - 1}" font-family="{FONT}" font-size="10" fill="{DIM}">Less</text>
  {legend_boxes}
  <text x="{more_x}" y="{legend_y + BOX - 1}" font-family="{FONT}" font-size="10" fill="{DIM}">More</text>
</svg>
'''


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    data = json.loads(Path("data/contributions.json").read_text())
    svg = build_svg(data, static=static)
    Path("contrib-heatmap.svg").write_text(svg)
    print(f"wrote contrib-heatmap.svg ({len(data['days'])} days, static={static})")


if __name__ == "__main__":
    main()
