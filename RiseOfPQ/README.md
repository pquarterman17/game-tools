# Rise of PQ

An **epic pacing** overhaul mod for [Rise of Nations: Extended Edition](https://store.steampowered.com/app/287450/) — longer ages, bigger economies, higher population caps, and automation for the tedious parts. Built for single-player vs AI.

## What it changes

### Mod (`mod/Rise of PQ/`)

| Area | Vanilla | Rise of PQ |
|---|---|---|
| Age research cost | 25f … 375k/150o | **2×** (50f … 750k/300o) |
| Age research time | 27 s … 87 s | **2×** (53 s … 173 s) |
| Population cap choices | 25–200 | **50–400** |
| Hard population ceiling | 300 | **999** |
| Commerce caps per age | 70–500 | **2×** (140–1000) |
| Base city income | 10 food / 10 timber | **20 / 20** |
| Citizen build/repair respond range | 12 tiles | **20 tiles** |
| Civilian self-heal rate | 45 frames/HP | **20 frames/HP** |

### Auto_Train script (`scripts/Auto_Train/`)

A standalone game script (selectable in the game-setup screen, like the built-in *Auto Pause*) that removes production busywork:

- **Auto-trains citizens** while you have no idle ones (pays normal costs through the normal queue)
- **Auto-trains scholars** until your universities are full
- **Optional military auto-training** (heavy/light infantry, archers) — toggles in the script's config block; unit lines auto-resolve to your current age and nation-unique variants
- **Forces the engine's built-in Auto Citizen automation** ("Build and Gather") so idle citizens automatically repair, build, and gather

## Installation

Requires Rise of Nations: Extended Edition (Steam) on Windows.

```powershell
git clone https://github.com/pquarterman17/RiseOfPQ.git
cd RiseOfPQ

# 1. Snapshot your game's vanilla files (diff baseline; game files are not shipped in this repo)
powershell -File tools\snapshot-vanilla.ps1            # add -GameDir if not in the default Steam library

# 2. Deploy the mod + scripts into the game
powershell -File tools\deploy.ps1

# 3. (Optional) borderless windowed mode at desktop resolution
powershell -File tools\borderless.ps1                  # -Restore to undo
```

Then in-game:

1. **Main Menu → Mods** → enable **Rise of PQ** (set it to top priority)
2. In game setup, set **Script** to **Auto_Train**
3. Once, in **Options**: drag *Auto Citizen Delay* to minimum

If your game is installed somewhere else, edit `$GameDir` at the top of `tools/deploy.ps1` or pass `-GameDir` to the snapshot script.

## How it works

RoN:EE mods are **whole-file overrides**: anything in `mods\<Name>\data\` is loaded *instead of* the same file in the game's `Data\` folder. This repo keeps your pristine copies in `vanilla/` (generated locally, git-ignored) so `git diff --no-index vanilla/<file> "mod/Rise of PQ/data/<file>"` always shows exactly what the mod changes.

The auto-train feature uses RoN:EE's standalone script system (BHS language) — see `scripts/Auto_Train/auto_train.bhs`, which is heavily commented, including the engine behavior that makes `train_unit("Hoplites")` keep working in every age.

## Repo layout

```
mod/Rise of PQ/        # the mod payload (deployed to <game>\mods\)
scripts/               # standalone .bhs scripts (deployed to <game>\scenario\Scripts\)
tools/                 # deploy / snapshot / borderless PowerShell scripts
docs/                  # modding reference, scripting guide, design notes
plans/                 # development plan
vanilla/               # local-only baseline of game files (git-ignored)
```

## Documentation

- **[Modding reference](docs/modding-reference.md)** — how RoN:EE's mod system actually works (verified against the install): the three config layers, whole-file overrides, key Data XML files, units of measure, surviving game updates
- **[BHS scripting guide](docs/bhs-scripting.md)** — the standalone script system: language shape, the repeating-trigger idiom, the 626-function catalog, why `train_unit("Hoplites")` works in every age, Auto Citizen levels
- **[Design notes](docs/design-notes.md)** — why every value is what it is, which knob to turn when a playtest disagrees, and the playtest checklist

## License

MIT — see [LICENSE](LICENSE). Rise of Nations and its data files are © Microsoft / Big Huge Games; this repo contains only modified rule values and original tooling, no redistributed game assets.
