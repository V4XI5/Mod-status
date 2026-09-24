# Crimson Desert mod status badges

Live status cards (animated, 960x276, updated every 5 minutes):

    Enhanced Internal Graphics:
    [img]https://raw.githubusercontent.com/V4XI5/Mod-status/badges/internal-graphics.gif[/img]

    Lod-Fix:
    [img]https://raw.githubusercontent.com/V4XI5/Mod-status/badges/lod-fix.gif[/img]

Older small badges (still updated when a status changes):

Badges for the Nexus Mods pages:

    Enhanced Internal Graphics:
    [img]https://raw.githubusercontent.com/V4XI5/Mod-status/main/status.png[/img]

    Lod-Fix:
    [img]https://raw.githubusercontent.com/V4XI5/Mod-status/main/lodfix.png[/img]

## How it works
- Every 5 minutes, GitHub Actions checks Crimson Desert's Steam build.
  If the game updated since a mod was last tested, it switches to its `on_patch` status in state.json:
  Enhanced Internal Graphics -> yellow "Game updated - untested"; LOD-Fix -> red "Broken - fix in progress"
  (LOD-Fix always breaks on a patch because it depends on the game .exe memory layout).
- To set a status: **Actions -> Mod status -> Run workflow**, pick the mod, then:
  - `working`: green, "Working as of <today>"
  - `broken`: red, "Broken since <today> - fix in progress"
  - `wip`: blue, "Being worked on"

Badges are drawn by scripts/render.py with the Furore font (fonts/Furore.otf, free for commercial use).
