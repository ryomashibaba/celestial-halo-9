# CELESTIAL HALO-9

**Monumental Minecraft city architecture research** — a ring megastructure with 16 distinct architectural sites, bright civic monuments, dark structural infrastructure, large public voids, and layered elevated circulation.

> **Research-only / NON-CONSTRUCTION.** This repository contains procedural studies, read-only observations from a user-controlled Minecraft review copy, concept meshes, architectural illustrations, and offline verification tools. It is **not** a production-ready Minecraft builder and does not authorize changes to any world.

## Current status

- **Official design comparison baseline:** `M101_TERRACED_DISTRICT_RIM` (comparison baseline only).
- **M119–M121 research:** offline alternative volumes, architecturally articulated vaults, 16-site conceptual interiors, measured material-tile overlays, and human-eye-level studies. The 3D concepts are not a finalized approved city.
- **Source branch:** `integration/local-work-m121-setup-20261014`; immutable upstream copies are in `research/m121/upstream/`.
- **M117 atlas:** a user-provided *read-only* survey of old saved-world building materials, not a world save and not an authorized construction target.
- **Construction:** HOLD. The authoritative world has not been registered; world-coordinate conversion, exact protected meshes, reserved voids, public paths, and pilot construction clearance remain unverified.
- **Pull requests:** an intentionally unmerged sequence of Draft PRs. Do not assume a proposal is part of `main` or accepted for construction.

## Getting oriented

Read `docs/START_HERE_JA.md`, `governance/PROJECT_CONSTITUTION.md`, and `docs/M121_HUMAN_SCALE_INTERIOR_AND_WORK_SETUP.md`. The complete historical research bundle and read-only checks are on the integration branch, with provenance in `research/m121/README.md`.

### Offline checks (on an integrated branch)

```sh
python ci/check_policy.py
python -m unittest discover -s tests -v
```

For source bundle verification, see `research/m121/README.md`. Some older image generators write outputs into their source directory; **do not run them against the preserved `upstream/` originals**. For experiments, copy source and artifacts to an isolated work directory first.

## Boundaries

- No Minecraft save/world write, no WorldEdit deployment, no freezing/merging of design alternatives, no protected-building replacement unless separately approved.
- Do not treat material-bounding-box checks as clearance of exact protected architecture, roads, public corridors, voids, or the final build world.
- Avoid adding local machine paths, credentials, authentication files or complete Minecraft saves to future submissions.
- CI is for research and policy tests, not for construction. Review all proposed CI/workflow changes before executing untrusted pull requests.

## Licensing and public use

This research project does not currently declare an open-source license. Publishing on GitHub and allowing GitHub forks does **not** automatically grant general reuse, modification, redistribution, or commercial licensing rights. License selection is a separate owner decision.

**Publication status:** this README has been prepared on a Draft branch. The repository's visibility remains private until the owner separately approves switching it to Public.
