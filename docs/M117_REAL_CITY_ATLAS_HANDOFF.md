# M117: survey REAL old city before macro-scale redesign

## World ambiguity resolved for the review copy
Minecraft's first *imagine* entry displays the folder **CH9_D6D_REVIEW_COPY** and its thumbnail shows the old city. User independently verified Windows Explorer folder. The plain folder `SKYTREE_3500/saves/imagine` is a separate save with the same in-game LevelName but only stone in prior sampled sections. **Neither save is approved for construction**, nor registered as the canonical live building target.

## Real implementation in M117 portable ZIP
Portable source & tests: `CELESTIAL_HALO9_M117_REVIEW_COPY_CITY_ATLAS_READONLY_HANDOFF.zip` SHA256 `bea3cac3adcb68b3c36dd28bfdcfb58585222a41111bb970bc512d4dc7f907d1`.
The script is ASCII CRLF launcher plus pure-stdlib Anvil reader, fixed folder tail `SKYTREE_3500/saves/CH9_D6D_REVIEW_COPY`. It reads a maximum of 1456 exact-model parcel chunks; aggregates non-natural building materials into 8×8 occupancy tiles and records exact detected saved Y bounds/material counts. It outputs only summary JSON/CSV in a local folder **outside Minecraft saves**, no auto-upload. Synthetic Anvil tests 3/3 PASS and source files unchanged.

**Full ZIP source is in conversation attachments, not in this GitHub branch.** This PR includes an independent report validator, status ledger and regression tests; do not claim full scanner source migration.

## Truth limits
- M115 only identified 4,476 black-concrete/quartz candidate blocks in a small 13-chunk sample; it did NOT map all 16 real buildings.
- The M117 scanner has NOT been executed on the user's real review copy yet. No actual 16-site atlas currently exists.
- Black concrete/quartz are heuristic built materials; natural-material building elements may be omitted. Blocks cannot be attributed to Frozen408/protected mesh IDs from material alone.
- Model-relative H to actual Minecraft Y still UNKNOWN until verified landmark matching.
- M101 includes **3389 conceptual proposed meshes**, NOT 3389 confirmed Minecraft constructions. Retain M101 comparison baseline, old protected Freeze408/959 meshes, SB09 portal, SB13 minimum 3x4 entrance, 88 voids, roads, parks and full constitutional constraints.

## Macro-first next move
Once M117 real-city atlas arrives, visualize actual occupancy and elevation, then propose a **true citywide overhaul**, not repetitive cosmetic additions to floating rings. Distinguish actual constructed footprint, preserve protected freeze and permitted redesign. Design HERO4 exteriors/interiors, civic core/sky void, FRAME8 districts and orbital transfers as one spatially explorable plan. Keep actual world construction on HOLD pending separate explicit approval and an independently identified canonical live world.
