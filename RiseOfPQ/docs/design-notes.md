# Rise of PQ — Design Notes & Tuning Guide

Why each change is what it is, and which knob to turn if a playtest says it's wrong. Single-player vs AI is the design target throughout — every change applies symmetrically to the AI, which budgets from the same XML tables.

## Design pillars

1. **Epic pacing** — each age should feel like an era you inhabit, not a checkpoint you sprint past.
2. **Bigger economies, bigger armies** — the pop/commerce ceilings, not micro speed, should bound your empire.
3. **Automate the busywork, keep the decisions** — production spam and repair-clicking are removed; *what* to build and *where* to fight stay yours.

## Change-by-change rationale

### Age costs and research times: 2× (`techrules.xml`)

Doubling **both** cost and `JOB_TIME` matters: cost alone barely slows a stockpiled economy, time alone makes the cost trivial by the time the timer ends. Together they set a floor on real minutes per age.

*Tuning:* the multiplier is uniform, so the original table (in `docs/modding-reference.md`) × 2 is current state. If late ages drag while early ages feel right, scale Industrial+ back to ~1.5× and leave Classical–Enlightenment at 2×. The AI handles this well — it reads the same costs — but verify it still reaches Information Age in long games (plan item 7).

### Pop caps: setup menu 50–400, hard cap 999 (`rules.xml`)

The menu (`POP_CAP`) and ceiling (`MAX_POP_LIMIT`) are separate; raising the menu past the ceiling silently clamps, hence 999. Existing "no limit" Workshop mods use similar ceilings, so 999 is known-safe for the engine.

*Tuning:* pure preference. Pathfinding gets visibly slower beyond ~500 total units on huge maps — old engine.

### Commerce caps: 2× (140–1000) (`rules.xml`)

RoN's economy is bounded by the commerce cap, not by gather speed — extra citizens past the cap add nothing. With 2× age costs the vanilla caps would stall progression: you'd hit the ceiling and wait. Doubling restores the vanilla *feel* (income roughly tracks ambition) at the new scale, and it synergizes with the raised pop cap — those extra citizens now have a reason to exist.

*Tuning:* this is the most sensitive lever in the mod. If games feel too rich (armies replace instantly, costs never bite), pull back to ~1.5× before touching anything else. Wonder/nation commerce bonuses (`TAJ_WEALTH_COMMERCE` etc.) were deliberately left vanilla so they're proportionally *weaker* — intended.

### City base income: 10/10 → 20/20 (`CITY_GATHER`)

Smooths the early game at 2× age costs so the opening isn't pure waiting. Every city produces this passively, so it also slightly rewards wide play — consistent with epic pacing.

### Citizen respond range: 12 → 20 tiles (`UNIT_BUILD_RESPOND_RANGE`)

The "noticing" radius for auto-join on construction/repair. 12 tiles ≈ next door; 20 covers a typical city footprint. Not raised further: citizens abandoning gathering to cross half the map is worse than the disease.

### Civilian heal rate: 45 → 20 frames/HP (`CIVILIAN_HEAL_RATE`)

Brings civilians to base-soldier heal speed. Pure QoL after raids — wounded citizens limping at half-health for ten minutes added nothing strategically.

### Auto_Train script (citizens, scholars, optional military)

Design constraints that shaped it:

- **Idle-gating for citizens** (`find_num_idle_unit < 1`): mimics what a good player does — keep training while everyone's employed, stop when bodies pile up. The batch of 2 per 15 s cycle intentionally trails a hard-booming pace; raise `citizen_batch` to 3–4 to boom harder.
- **Scholars are uncapped** because the university slot limit (and your wealth) caps them naturally; `train_unit` fail-soft does the bookkeeping.
- **Military defaults off**: auto-trained armies spend resources without strategy. The toggles exist for "I just want a garrison stream" moods.
- **Costs are honest**: everything goes through the normal queue at normal prices. The script clicks for you; it doesn't cheat for you.

### Forced Auto Citizen level 1 (script, `set_auto_peasant_level`)

The engine's own automation (gather + build + repair) is the correct repair solution — script-driven repair would need building enumeration BHS doesn't have. Forcing level 1 each game beats relying on the buried, per-profile Options setting. Set `auto_citizen_level = -1` in the script to stop overriding your profile.

## Interaction map

```
2x age cost/time  <--needs-->  2x commerce caps   (else: progression stalls at cap)
        |                            |
        v                            v
   longer ages              bigger income ceiling
        |                            |
        +-----> 50-400 pop caps <----+        (armies/economies that use the time & income)
                     |
                     v
        Auto_Train + Auto Citizen          (scale without proportional clicking)
```

Change one side of an arrow, revisit the other.

## Playtest checklist (carries plan items 1–3, 8, 11–13)

- [ ] Mod loads: "Rise of PQ" appears and enables in Main Menu → Mods
- [ ] Setup screen offers pop 50–400; Classical Age costs 50 food
- [ ] Script selector shows Auto_Train; start prints the "Rise of PQ Auto-Train enabled" block
- [ ] Citizens auto-queue at the city while none are idle; stop when several idle
- [ ] Idle citizens walk to and repair a damaged building unprompted
- [ ] Borderless: fills screen, no title bar, mouse to second monitor without minimize
- [ ] AI opponents age up and field armies at Moderate+ difficulty
- [ ] One full game: note minutes per age (target: roughly 2× vanilla feel)
