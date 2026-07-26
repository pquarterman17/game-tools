# CLAUDE.md

Rise of PQ — a gameplay/balance overhaul mod for **Rise of Nations: Extended Edition** (Steam), focused on slower "epic pacing" for single-player vs AI.

## Paths

| What | Path |
|---|---|
| Game install | `G:\SteamLibrary\steamapps\common\Rise of Nations` |
| Base game data XML | `<game>\Data\` |
| Local mods folder | `<game>\mods\<ModName>\` |
| Workshop mods | `G:\SteamLibrary\steamapps\workshop\content\287450\<id>\` |
| User display/window settings | `%APPDATA%\Microsoft Games\Rise of Nations\rise2.ini` |
| Terrain render constants | `<game>\graphics.txt` |

## Repo layout

```
mod/Rise of PQ/        # the mod payload — deployed verbatim to <game>\mods\Rise of PQ
  info.xml             # mod manifest (name, description, FILES list)
  data/                # whole-file overrides of <game>\Data\*.xml
scripts/               # standalone .bhs scripts — deployed to <game>\scenario\Scripts\
vanilla/               # pristine copies of every base file we override — NEVER edit.
                       #   git-ignored (copyrighted); regenerate with tools/snapshot-vanilla.ps1
tools/deploy.ps1       # copy mod/ + scripts/ into the game install (run after every change)
tools/snapshot-vanilla.ps1  # rebuild vanilla/ from the local game install
tools/borderless.ps1   # toggle borderless-windowed mode in rise2.ini
docs/                  # modding-reference.md, bhs-scripting.md, design-notes.md
plans/                 # tiered plan documents
```

Deep documentation lives in `docs/` — consult `modding-reference.md` for file formats and units of measure, `bhs-scripting.md` for the standalone script system, and `design-notes.md` for tuning rationale before changing any shipped value.

## How RoN:EE modding works

- A mod is a folder under `<game>\mods\` containing `info.xml` + a `data\` subfolder mirroring `<game>\Data\`.
- **Files are whole-file overrides** — the game loads the mod's copy *instead of* the base file. There is no merge/patch mechanism. Only ship files that actually differ from vanilla.
- `info.xml` manifest sizes/checksums are NOT strictly validated (verified: Workshop mod 769767555 loads with mismatched sizes).
- Mods are enabled and prioritized in-game: Main Menu → Mods. The game writes state to `<game>\mods\mod-status.txt` (UTF-16).
- Higher-priority enabled mods override lower ones; ours should be highest priority when testing.

## Key data files (all in `Data\`)

| File | Contains | Epic-pacing knobs |
|---|---|---|
| `rules.xml` | Global constants, nation powers | `POP_CAP entry0..7` (line ~170), `MAX_POP_LIMIT` (300 hard cap), damage modifiers |
| `techrules.xml` | Library techs incl. the 7 Ages | Age `<COST>` and `<JOB_TIME>` (15ths of a second) |
| `unitrules.xml` | Every unit's stats | `COST` (×10), `SUPPORT` (ramp), `JOB_TIME`, `HITS`, `ATTACK` |
| `balance.xml` | Per-tech/per-age cost ramps | research cost scaling |
| `buildingrules.xml` | Building stats/costs | build times, city costs |
| `resourcerules.xml` | Resource gather rates | commerce caps, gather speeds |

Unit `OBJ_MASK`/`FLAGS` letter codes are documented in the comment block at the top of `unitrules.xml` (vanilla copy, lines 16–80).

## Workflow

1. Edit files in `mod/Rise of PQ/data/` (copy from `vanilla/` first if the file isn't in the mod yet).
2. `git diff --no-index vanilla/<file> "mod/Rise of PQ/data/<file>"` to review what the mod changes.
3. Deploy: `powershell -File tools\deploy.ps1`
4. Launch RoN:EE, enable "Rise of PQ" in Main Menu → Mods, start a quick battle to verify.
5. Commit on a feature branch per global rules.

## Standalone scripts (BHS)

RoN:EE loads scripts from `<game>\scenario\Scripts\<Name>\<name>.bhs`, selectable in the game-setup screen (alongside the shipped "Auto Pause" and "No Nukes"). Format: C-like, one `scenario { }` block with `static` vars, `run_once { }`, and `trigger Name(condition) { }` blocks.

- Triggers fire ONCE; re-arm with `enable_trigger("Name")` inside the body (repeating-timer idiom: `set_timer` + `enable_trigger`, see `scenario\Custom\italy_mp\italy_mp.bhs`).
- `train_unit(who, num, "Type")` resolves the type through `current_upgrade()` + `get_graft()` — Ancient-age line names ("Hoplites") stay valid in every age and for nation-unique variants. Source: `<game>\obsoletescriptfuncs.txt` lines 547–589.
- Function catalog: `Data\scriptfunctions.xml` (626 funcs, one line — parse with regex). Unit names = `<NAME>` values in `unitrules.xml` (case-insensitive).
- `get_console_player()` = the human player number.

## Constraints

- XML files use the game's exact schema — no DTD validation at load, but a malformed file silently falls back or crashes to desktop. Always keep edits minimal and diffable.
- `JOB_TIME` units are frames (15 per second). `COST` in unitrules is multiplied by 10 in-game.
- Single-player focus: the AI reads the same XML, so cost/pacing changes apply to it symmetrically — but extreme values can confuse AI build orders (it budgets from these tables).
- Vanilla snapshots in `vanilla/` are the diff baseline. If Steam updates the game, re-snapshot and rebase the mod's files.
