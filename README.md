# Enhanced Internal Graphics Mod - live status badge

Badge for the Nexus Mods page. Paste this into the mod description:

    [img]https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/V4XI5/Mod-status/main/status.json[/img]

## How it works
- Every 3 hours, GitHub Actions checks Crimson Desert's Steam build.
  If the game updated since you last tested, the badge turns orange: "Game updated <date> - untested".
- After testing, go to **Actions -> Mod status -> Run workflow**, then pick:
  - `working`: green, "Working as of <today>"
  - `broken`: red, "Broken since <today> - fix in progress"
