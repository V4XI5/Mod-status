"""Updates the Nexus status badge for Enhanced Internal Graphics Mod.

Usage: python scripts/update.py check|working|broken
  check   - run on a schedule; flags the badge if Crimson Desert updated since the last test
  working - you tested the mod on the current game build and it works
  broken  - the mod is known to be broken on the current game build
"""
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

APP_ID = "3321460"  # Crimson Desert on Steam
LABEL = "Enhanced Internal Graphics"
ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state.json"
BADGE = ROOT / "status.json"


def current_build():
    req = urllib.request.Request(
        f"https://api.steamcmd.net/v1/info/{APP_ID}",
        headers={"User-Agent": "mod-status-badge"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    return data["data"][APP_ID]["depots"]["branches"]["public"]["buildid"]


def pretty(iso_date):
    d = datetime.strptime(iso_date, "%Y-%m-%d")
    return f"{d:%b} {d.day}, {d.year}"


def write_badge(state):
    status = state["status"]
    if status == "working":
        message, color = f"Working as of {pretty(state['date'])}", "brightgreen"
    elif status == "unverified":
        message, color = f"Game updated {pretty(state['date'])} - untested", "orange"
    else:
        message, color = f"Broken since {pretty(state['date'])} - fix in progress", "red"
    BADGE.write_text(json.dumps(
        {"schemaVersion": 1, "label": LABEL, "message": message, "color": color},
        indent=2) + "\n")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    state = json.loads(STATE.read_text())
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    build = current_build()

    if mode == "working":
        state.update(status="working", date=today, tested_build=build)
    elif mode == "broken":
        state.update(status="broken", date=today, tested_build=build)
    elif mode == "check":
        if build != state["tested_build"] and state["status"] == "working":
            state.update(status="unverified", date=today)
    else:
        sys.exit(f"unknown mode: {mode}")

    state["latest_build"] = build
    STATE.write_text(json.dumps(state, indent=2) + "\n")
    write_badge(state)
    print(f"{mode}: game build {build} -> {state['status']}")


if __name__ == "__main__":
    main()
