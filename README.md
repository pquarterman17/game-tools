# game-tools

Personal collection of game mods, tools, and peripheral fixes. Each subfolder
is an independent project with its own README; the two that started life as
standalone repos were merged in with full git history preserved.

## Projects

| Folder | What it is |
|---|---|
| [`RiseOfPQ/`](RiseOfPQ/) | Epic-pacing overhaul mod for *Rise of Nations: Extended Edition* |
| [`DysonSphereProgramTree/`](DysonSphereProgramTree/) | Recipe-tree tool for *Dyson Sphere Program* (open `index.html`) |
| [`x56_GhostBuster/`](x56_GhostBuster/) | Scripts fixing Logitech X56 HOTAS ghost inputs — diagnostic, debounce filter, and a Joystick Gremlin plugin |

## Notes

- `RiseOfPQ/vanilla/` holds pristine game files for diffing. They are
  copyrighted and gitignored — regenerate from your own game install with
  `RiseOfPQ/tools/snapshot-vanilla.ps1`.
- Formerly separate repos: `pquarterman17/RiseOfPQ` and
  `pquarterman17/DysonSphereProgramTree` (both archived; history lives here).

## License

MIT — see [LICENSE](LICENSE). Applies to all projects in this repo.
