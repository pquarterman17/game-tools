# Rise of Nations: EE — Modding Reference

Everything in this document was verified directly against the Steam Extended Edition install (app `287450`). Paths assume the default layout described in the README.

## The three configuration layers

RoN:EE behavior comes from three independent layers. Knowing which layer owns a setting saves hours:

| Layer | Location | Owns | Moddable via `mods\`? |
|---|---|---|---|
| Game data XML | `<game>\Data\*.xml` | All gameplay rules: units, techs, buildings, nations, economy | **Yes** — this is what mods override |
| User/display config | `%APPDATA%\Microsoft Games\Rise of Nations\rise2.ini`, `rise.ini` | Resolution, fullscreen/windowed, vsync, UI toggles | No — per-machine ini files |
| Render constants | `<game>\graphics.txt`, `BHGVidCardConfig.txt` | Terrain/water rendering internals | No — game-root text files |

The binary player profile (`%APPDATA%\...\PlayerProfile\<name>.dat`) stores in-game Options (including Auto Citizen mode and delay). It is not editable as text.

## How the mod system works

A mod is a folder: `<game>\mods\<Mod Name>\` containing:

```
<Mod Name>\
  info.xml         # manifest: display name, description, version, FILES list
  data\            # whole-file overrides of <game>\Data\
  art\ sounds\ ... # other game folders can be mirrored the same way
```

Key facts (verified):

- **Whole-file override, no merging.** If your mod ships `data\rules.xml`, the game loads it *instead of* `Data\rules.xml` — every byte of it. Ship only files you actually changed, and keep each shipped file complete.
- **`info.xml` manifest is lenient.** The `<FILES>` size/checksum attributes are not strictly validated — Workshop mod `769767555` loads fine with sizes off by 2 bytes. Keep them roughly right for tidiness.
- **Enable/priority is in-game**: Main Menu → Mods. State is persisted to `<game>\mods\mod-status.txt` (UTF-16). Higher priority wins when two enabled mods override the same file — disable other rules-touching mods while testing yours.
- **Workshop mods** live separately in `steamapps\workshop\content\287450\<id>\` with the same internal layout.
- **A malformed XML override fails silently or crashes to desktop** — there is no load-time schema validation or error dialog. Always check well-formedness before deploying (our deploy flow does `[xml](Get-Content ...)` in PowerShell).

## Key Data files

| File | Size | Contains |
|---|---|---|
| `rules.xml` | 89 KB | Global constants (`<CONSTANTS>`): pop caps, commerce caps, heal rates, respond ranges, damage modifiers, plus every nation power and wonder bonus |
| `unitrules.xml` | 630 KB | Every unit: stats, costs, prerequisites, upgrade chains. The 90-line comment block at the top documents every field — read it before editing |
| `techrules.xml` | 44 KB | Library techs, including the 7 Ages (each a `<TECH>` with `COST` and `JOB_TIME`) |
| `buildingrules.xml` | 209 KB | Building stats, costs, build times |
| `balance.xml` | 1.6 MB | Per-tech/per-age cost ramp tables |
| `resourcerules.xml` | 46 KB | Resource definitions and rare-resource bonuses |
| `craftrules.xml` | 40 KB | "Craft" (special ability/ammo) rules |
| `interface.xml`, `help.xml`, `string_lookup.xml` | — | UI layout, in-game help, display strings |

### Units of measure (recur everywhere)

- **Time**: frames at 15 per second. `JOB_TIME 1100` ≈ 73 s.
- **Distance**: tiles ("TCoords"). 4 TCoords = 1 WCoord = the width of a farm.
- **Unit `COST`**: multiplied by 10 in-game (`COST 2f` → 20 food). Tech `COST` is literal (`50k/50f` = 50 knowledge + 50 food).
- **Resource letters**: `f` food, `t` timber, `m` metal, `g` wealth, `k` knowledge, `o` oil.
- **Heal rates**: frames per hit point — *lower is faster*.

### Constants this mod touches (`rules.xml`)

| Constant | Vanilla | Meaning |
|---|---|---|
| `POP_CAP entry0..7` | 25–200 | The population choices offered in game setup |
| `MAX_POP_LIMIT` | 300 | Engine hard ceiling — raising the menu without this silently clamps |
| `COMMERCE_CAP entry0..7` | 70–500 | Per-age ceiling on income per resource; *the* economy throttle |
| `CITY_GATHER` | 10 food/10 timber | Base income every city produces by existing |
| `UNIT_BUILD_RESPOND_RANGE` | 12 tiles | How far citizens notice construction/repair jobs |
| `CIVILIAN_HEAL_RATE` | 45 frames | Civilian out-of-combat self-heal (soldiers: 20) |

### Age techs (`techrules.xml`)

The 7 Ages are ordinary `<TECH>` entries named `Classical Age` … `Information Age`, chained by `PREQ0`. Vanilla cost/time table:

| Age | COST | JOB_TIME |
|---|---|---|
| Classical | 25f | 400 |
| Medieval | 25k/25f | 550 |
| Gunpowder | 50k/50f | 700 |
| Enlightenment | 100k/50f | 850 |
| Industrial | 150k/75f | 1000 |
| Modern | 250k/100o | 1150 |
| Information | 375k/150o | 1300 |

(Rise of PQ ships all of these at 2×.)

## Display: borderless windowed

`rise2.ini` keys (game must not be running when you edit):

```ini
Fullscreen=0              ; 0 = windowed; at desktop resolution this renders borderless
Windowed Width=2560
Windowed Height=1440
IgnoreMinimizeOnTabOut=1  ; keep rendering when you alt-tab
```

`tools\borderless.ps1` automates this (detects desktop resolution, backs up the ini, `-Restore` flag to undo).

## Update survival

Steam updates replace `Data\` files. Because mods are whole-file overrides, an updated base file does **not** flow into your mod's copy. After a game update:

1. `tools\snapshot-vanilla.ps1` — refresh the baseline
2. `git diff` the new vanilla against your previous vanilla (git history has it) to see what the patch changed
3. Re-apply your intended deltas onto fresh copies if the base file changed materially
