"""Updates the Nexus status badges.

Usage: python scripts/update.py check
       python scripts/update.py MOD working|broken|wip
  check   - run on a schedule; flags working mods if Crimson Desert updated since their last test
  working - you tested the mod on the current game build and it works
  broken  - the mod is known to be broken on the current game build
  wip     - the mod is being worked on
MOD is a key under "mods" in state.json, e.g. internal-graphics or lod-fix.
"""
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

APP_ID = "3321460"  # Crimson Desert on Steam
ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state.json"


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


def write_badge(mod):
    status = mod["status"]
    if status == "working":
        message, color = f"Working as of {pretty(mod['date'])}", "brightgreen"
    elif status == "unverified":
        message, color = f"Game updated {pretty(mod['date'])} - untested", "orange"
    elif status == "wip":
        message, color = "Being worked on", "blue"
    else:
        message, color = f"Broken since {pretty(mod['date'])} - fix in progress", "red"
    (ROOT / mod["badge"]).write_text(json.dumps(
        {"schemaVersion": 1, "label": mod["label"], "message": message, "color": color},
        indent=2) + "\n")


def main():
    args = sys.argv[1:] or ["check"]
    state = json.loads(STATE.read_text())
    mods = state["mods"]
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    build = current_build()

    if args[0] == "check":
        for mod in mods.values():
            if mod["status"] == "working" and build != mod["tested_build"]:
                mod.update(status="unverified", date=today)
    else:
        if len(args) != 2 or args[0] not in mods or args[1] not in ("working", "broken", "wip"):
            sys.exit(__doc__)
        mods[args[0]].update(status=args[1], date=today, tested_build=build)

    state["latest_build"] = build
    STATE.write_text(json.dumps(state, indent=2) + "\n")
    for key, mod in mods.items():
        write_badge(mod)
        print(f"{key}: game build {build} -> {mod['status']}")


if __name__ == "__main__":
    main()
