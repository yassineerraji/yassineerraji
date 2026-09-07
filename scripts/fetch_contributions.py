#!/usr/bin/env python3
"""Fetch a public GitHub contribution calendar (no token needed) and derive stats."""
import datetime as dt
import json
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = sys.argv[1] if len(sys.argv) > 1 else "yassineerraji"
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_days() -> list[dict]:
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cells = soup.select("td[data-date]") or soup.select("[data-date]")
    days = []
    for cell in cells:
        date = cell.get("data-date")
        if not date:
            continue
        level_attr = cell.get("data-level")
        count_attr = cell.get("data-count")
        if level_attr is not None:
            level = int(level_attr)
        else:
            level = 0
        if count_attr is not None:
            count = int(count_attr)
        else:
            tt_id = cell.get("id")
            tooltip = soup.find(attrs={"for": tt_id}) if tt_id else None
            text = tooltip.get_text(strip=True) if tooltip else ""
            count = 0
            for tok in text.split():
                if tok.isdigit():
                    count = int(tok)
                    break
                if tok == "No":
                    count = 0
                    break
        days.append({"date": date, "count": count, "level": level})

    days.sort(key=lambda d: d["date"])
    return days


def derive_stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)

    longest = current = 0
    running = 0
    today = dt.date.today()
    for d in days:
        if d["count"] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    # current streak: walk backwards from the most recent day
    running = 0
    for d in reversed(days):
        if d["count"] > 0:
            running += 1
        else:
            break
    current = running

    best_day = max(days, key=lambda d: d["count"], default=None)

    monthly: dict[str, int] = {}
    for d in days:
        month = d["date"][:7]
        monthly[month] = monthly.get(month, 0) + d["count"]

    return {
        "username": USERNAME,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best_day,
        "monthly_totals": monthly,
        "days": days,
    }


def main() -> None:
    days = fetch_days()
    if not days:
        raise SystemExit("no contribution cells found -- GitHub markup may have changed")
    data = derive_stats(days)
    out = Path("data/contributions.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, indent=2))
    print(f"wrote {out}: {data['total']} contributions, streak {data['current_streak']}/{data['longest_streak']}")


if __name__ == "__main__":
    main()
