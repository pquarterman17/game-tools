# BHS Standalone Scripts — Practical Guide

RoN:EE can attach a script to *any* game (not just scenarios) via the standalone script system. This is how Rise of PQ implements auto-training — behavior the XML data layer cannot express.

## Where scripts live and load

```
<game>\scenario\Scripts\<Script Name>\<script>.bhs
```

Each subfolder is one selectable script; the folder name is what appears in the **Script** selector on the game-setup screen (the shipped examples are `Auto_Pause` and `No_Nukes`). One `.bhs` file per folder.

There is no error dialog for many script faults — if your script doesn't appear or silently does nothing, suspect a syntax error and bisect against a known-good script.

## Language shape

BHS is C-like. A standalone script is a single `scenario { }` block:

```c
scenario {
  // statics persist for the whole game; also where config lives
  static int interval = 15;

  run_once {
    // executes once at game start
    set_timer("MY_TIMER", interval);
    print_game_msg("hello");
  }

  trigger MyTrigger(timer_expired("MY_TIMER")) {
    // body runs when the condition becomes true
    set_timer("MY_TIMER", interval);
    enable_trigger("MyTrigger");      // <-- triggers fire ONCE; re-arm explicitly
  }
}
```

### The repeating-timer idiom

Triggers are one-shot. The canonical repeat pattern (used by the shipped scripts and `scenario\Custom\italy_mp\italy_mp.bhs`):

1. `run_once` arms a named timer: `set_timer("T", seconds)`
2. A trigger fires on `timer_expired("T")`
3. The trigger body does its work, re-arms the timer, and calls `enable_trigger("OwnName")`

Timer ids are strings; seconds are game-time integers. For wall-clock timing instead, use `real_time_millis()` (returns < 0 in multiplayer — the shipped `auto_pause.bhs` uses that as an "is this solo?" check).

## The function catalog

`<game>\Data\scriptfunctions.xml` declares all 626 callable functions with parameter lists (one long line — grep it, don't read it). Parameter *semantics* are mostly undocumented, but `<game>\obsoletescriptfuncs.txt` contains real C++ source of earlier versions of many functions — the best documentation of engine behavior that exists.

### Functions used by Rise of PQ

| Function | Notes |
|---|---|
| `get_console_player()` | The human player's number |
| `train_unit(who, num, "Type")` | Queue `num` of a type at an eligible building; pays normal cost; returns 0/-1 (no exception) when impossible |
| `train_unit_at(who, num, "Type", build_o)` | Same, at a specific building object |
| `find_num_idle_unit(who, "Type")` | Count of that unit type currently idle |
| `set_auto_peasant_level(level)` | Force the engine's Auto Citizen mode (see below) |
| `set_timer(id, secs)` / `timer_expired(id)` | Game-time timers |
| `print_game_msg(string)` | Chat-area message; supports `+` string concatenation |
| `enable_trigger("Name")` / `disable_trigger("Name")` | Trigger re-arm/disarm |

### The upgrade-resolution behavior (why "Hoplites" works forever)

From the engine source preserved in `obsoletescriptfuncs.txt` (lines 547–589): `train_unit` passes the requested type through

```cpp
t = LEADER2.current_upgrade(t);   // e.g. Hoplites -> Pikemen -> ... -> Assault Infantry
t = LEADER2.get_graft(t);         // nation-unique substitution (e.g. Roman Legions)
```

So scripts should always reference the **Ancient-age line name** ("Hoplites", "Bowmen", "Slingers", "Citizen", "Scholar") and let the engine resolve age and nation. Valid names = `<NAME>` values in `unitrules.xml` (case-insensitive).

### Auto Citizen levels (`set_auto_peasant_level`)

Maps to Options → "Auto Citizen". Level ids from `Data\optionswin.xml`:

| Level | Mode | Idle citizens will… |
|---|---|---|
| 0 | Gather | auto-return to gathering |
| 1 | Build and Gather | auto-build, **auto-repair**, and auto-gather |
| 2 | Build | auto-build and auto-repair only |
| 3 | Idle | nothing (automation off) |

Repair is internally the same task as build, so levels 1–2 give automatic repair of damaged buildings. The *delay* before automation kicks in is the "Auto Citizen Delay" Options slider, stored in the binary player profile — not settable from a script or mod.

## Gotchas

- **Fail-soft everywhere**: most functions return 0/-1 instead of erroring. Good for "just try every cycle" designs; bad for debugging — add `print_game_msg` breadcrumbs.
- **Strings**: timer ids and trigger names are quoted strings; trigger names in `enable_trigger` must match the declared name exactly.
- **No arrays / limited iteration**: you cannot enumerate "all damaged buildings". Design around point queries (`find_build`, `find_idle_citizen`, `object_health`) or lean on engine automation.
- **Scripts are global, mods are overlay**: a script is selected per-game in setup and runs regardless of which mods are enabled. The two systems don't interact unless you make them.
- **MP caution**: functions acting on `get_console_player()` are inherently single-player-shaped. Gate with `real_time_millis() < 0` if a script must refuse to run in multiplayer.
