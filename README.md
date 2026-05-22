# Dyson Sphere Program — Recipe Tree

A bidirectional recipe explorer for [Dyson Sphere Program](https://store.steampowered.com/app/1366540/Dyson_Sphere_Program/). The in-game info panel only walks recipes *backward* (what an item is made from). This tool also walks them *forward* — so you can finally answer questions like *"I have a stack of Unipolar Magnets, what can I actually use them for?"*

**▶ Live: https://pquarterman17.github.io/DysonSphereProgramTree/**

It's a single self-contained HTML file — no install, no server, works offline once loaded.

## Features

- **Both directions.** Pick any item to see what it's *made from* (downward) and what it's *used in* (upward), each expandable tier by tier.
- **Two views.** Toggle between a collapsible tree and a force-directed network graph with adjustable up/down depth.
- **Whole game covered.** 173 items and 186 recipes, including Dark Fog content, buildings, and alternate recipes.
- **Smart sidebar.** Items grouped by production stage (Raw, Smelted, Components, Sciences, Endgame, Dark Fog, plus building categories) with filters for items that have alternate recipes, mineable resources, and a Dark Fog toggle.
- **Producer buildings** shown per recipe, with multi-tier buildings (e.g. the three Assembler tiers) collapsed into one icon to cut clutter.
- **Proliferator preview.** Switch between Mk.I/II/III (extra-products or speedup) to see how recipe times and output quantities change.
- **Honest about edge cases.** Items with no crafting recipe — Dark Fog combat drops, foraged Logs/Plant Fuel, and the Ray Receiver's Graviton-Lens mode — are labeled with their real source instead of a blank tree.

## Usage

Just visit the live link, or open `index.html` in any browser.

## Data

Recipe and item data is normalized from the [FactorioLab](https://github.com/factoriolab/factoriolab) DSP dataset. Item icons are from the same source.

## License

See [LICENSE](LICENSE).
