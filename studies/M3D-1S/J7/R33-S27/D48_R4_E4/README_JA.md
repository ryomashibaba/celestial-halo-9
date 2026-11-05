# CELESTIAL HALO-9 / D48 R4-E4 — H1 & NAVE native Blender study

**2026-11-05 / R0: source authored, native Blender execution and visual jury NOT YET VERIFIED.**  
**Formal ART adoption: 0. CITY MASTER 3D: incomplete. Minecraft writing: HOLD.**

## Exact provenance and boundary

- Formal policy: `main/docs/policy/START_HERE.md` and the six linked policy/agent documents; never modify main or policy.
- Parent E3 research HEAD: `e3af9abb63f38399811a3c2c7c2e1e5279b036d9`.
- E2 previous artist evidence: ART REJECT; `R0/R1/R2/E2_WORKING.blend` are frozen historical evidence, *not* a source to modify or reuse.
- Research-only scene coordinates (metres) are **not Minecraft coordinate registration**.
- **Source is not proof**: `author.py.zlib.b64` is a zlib+base64 transport of the actual authoring script with expected decoded SHA256 `b32873c16dedc29ac49f6d4c65c1596c6fc0877fb1709de044f5f434f81f6750`. CI decodes it into an editable `author.py`. A human-readable local source is also provided as a separate chat file. Compression is a connector transport workaround, not a design method.
- The new script does not read E2 rejected geometry. No exterior monolithic shell is created in R0.

## R0 intended geometry (PARTIAL STUDY, not completed city)

1. `H1_LIVING_URBAN_STREET`: two unequal public squares; central public street; real occupied section; six varied residential masses with roof and facade detailing; school studios and library, public clinic, market hall, civic orchard; distinct higher terraces and stairs; sky eye at 1.65m over street.
2. `NAVE_INHABITED_PUBLIC_ROOM`: inhabited civic forum, market, open gallery piers and double-height library, staggered public mezzanines, actual stairs and daylight; 1.65m public interior eye.
3. `PUBLIC_VERTICAL_CONNECTION`: continuous structural lift frame and multiple landings. This is **visual/geometry study only**, not certified elevator operation or continuous accessible route.
4. Registry: 30 named research markers, no marker passed off as a building. All are unregistered coordinates. The other special facilities and districts are unmade.

## Mandatory ART gating

- First inspect **real rendered PNG** `human_sky_district` and `human_public_interior` with naked-eye judgement.
- REJECT if sky street is simple boxes/shelves or if public interior is empty monumental volume with token bridges.
- REJECT if circulation, dwelling/public identity, multiple urban elevations, and 3D depth are not visually legible.
- R0 is not ART PASS merely because the file loads, renders or passes counts.
- Only after initial real render inspection, *edit the same saved BLEND directly*, keeping same two camera viewpoints and lighting, and rerender. Do not preapprove R1/R2 unseen.
- Do not build giant alpha shells to rescue a weak H1/NAVE; do not backfill the remaining 24 structures as empty markers.
- Later macro/7-view gate: `human_street`, `urban_aerial`, `central_front`, `central_rear`, `east_seafront`, with independent jury.
- Do not claim the full-city 3D master or any Minecraft build approval.

## Reproducible isolated native run

The research-only workflow `.github/workflows/halo9-r4-e4-native-study.yml` may run in an **ephemeral GitHub-hosted Linux runner** (not user's PC or Work). It verifies source SHA256, installs Blender only in that ephemeral runner, saves a native `.blend`, renders the first two fixed human views, independently reopens the actual BLEND, then attempts to commit evidence **back to this research branch only**. Even if the branch write fails, an Actions artifact is uploaded where possible.

**Completion statuses to treat separately**:

- `SOURCE_PY_SYNTAX_PASS`: only syntax, confirmed off-machine before GitHub save.
- `BLENDER_EXECUTION_PENDING`: real Blender process not yet demonstrated here.
- `NATIVE_REOPEN_PENDING`: no independent re-open report yet.
- `ART_NOT_REVIEWED`: neither images nor shape improvement have been visually approved.
- `FORMAL_ADOPTION_0`, `MINECRAFT_HOLD`.

If a runner cannot start, the same source can be executed with existing local Blender under the user's specifically bounded permission. Do not broaden local permissions or use foreground Computer Use. No Cloud Work session was launched for this E4 chat operation.
