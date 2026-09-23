# Crimson Desert mod status badges

Badges for the Nexus Mods pages:

    Enhanced Internal Graphics:
    [img]https://raw.githubusercontent.com/V4XI5/Mod-status/main/status.png[/img]

    Lod-Fix:
    [img]https://raw.githubusercontent.com/V4XI5/Mod-status/main/lodfix.png[/img]

## How it works
- Every 3 hours, GitHub Actions checks Crimson Desert's Steam build.
  If the game updated since a mod was last tested, its badge turns orange: "Game updated <date> - untested".
- To set a status: **Actions -> Mod status -> Run workflow**, pick the mod, then:
  - `working`: green, "Working as of <today>"
  - `broken`: red, "Broken since <today> - fix in progress"
  - `wip`: blue, "Being worked on"

Badges are drawn by scripts/render.py with the Furore font (fonts/Furore.otf, free for commercial use).
