# R33-S27-D36 — Blender-native edit bridge readiness and independent saved-GLB reference

**TECH LIMITED PASS (offline geometry/reference) / BLENDER NOT RUN / ART NOT SUBMITTED / formal adoptions 0 / CITY MASTER 3D incomplete / Minecraft HOLD.**

## Verified foundation

Checked `ryomashibaba/celestial-halo-9` main at `a2f88995eee8d10ee4830dbdf33ccb9c0790de8f` and D35 prior study at `8a6368d825e5a29ad037ece4981e5b1f4f291a10`. Follow main policy (ART FIRST; CITY MASTER 3D FIRST; formal M247-C protection; all ordinary buildings' exteriors + all special/public interiors; urban W0, H1–H6, SB01–SB16). No Work, no Minecraft world mutation, no main/protected asset changes.

## Environment findings

`blender` executable not on PATH or installed, `bpy` Python module absent. Python pip index could not connect due to network name-resolution failure. Blender 5.2 official documentation supports background Python scripts, but **no Blender-native execution or blend creation happened in this chat**. We wrote an explicit offline + Blender-ready bridge instead of claiming an unperformed Blender result.

The 3-mesh D33 ART REJECT GLB also had is_watertight=True but is_winding_consistent=False on all three meshes. It was not carried forward as a design or as the final test fixture. Replaced with a separate neutral and valid fixture.

## Actual offline technical results

New **neutral sculpt TEST ONLY** source GLB (ellipsoid + protected floor + protected access marker). This is not a building and is not submitted to art review.

- Source: 3 mesh GLB, 5,144 triangles (target: 2,562 vertices/5,120 triangles; two protected boxes: 24 triangles), all watertight with consistent winding.
- Input source SHA256: `1643479d50747d152dc4792410f397c7b59e2a62e1bd0b12922441edacfc14f0`.
- Applied two normalized-AABB centered smoothstep radial brushes directly to saved GLB mesh vertices, retaining the two protected meshes.
- Target moved vertices **1,519**; maximum observed displacement **154.993m**.
- Edited GLB SHA256: `546410f1b6969c0edb7b383f8845c9514ea5288d68ce197c4708bf34cfcf85f1`.
- Separate temporary-directory Python interpreter with only source, plan and editor regenerated exactly the same GLB SHA256.
- Seven fail-closed negative cases: invalid source hash, unprotected mesh, unknown target, zero radius, excessive displacement, bad falloff and source overwrite. All refused.
- Trimesh reread preserved mesh names, face counts, protected mesh positions; all meshes watertight and consistent winding.
- Offscreen VTK rendered 6 standard cameras for each of BASE/EDIT and 3-view side-by-side before/after comparison. **These are real GLB images, not Blender native renders or an architectural proposal.**

## Blender bridge constructed but not executed

`d36_blender_bridge.py`: native Blender 5.2 Python plan importer, strict hash/geometry whitelist, protected-mesh hashing, shape-key deform on target, six review cameras, new `.blend` save, GLB export, PNG render attempts, `D36_BLENDER_AUDIT.json` output.

`d36_blender_verify.py`: second fresh Blender process reopens saved `.blend`, verifies shape keys, protected mesh digests, source hash and GLB output; emits `D36_BLENDER_REOPEN_AUDIT.json` only after passing.

`D36_RUN_ON_WINDOWS.bat`: one-click two-process run in a fresh output folder; no original GLB overwrite. Both Blender scripts pass Python syntax compilation, but **native Blender API/runtime/render checks are NOT RUN** and may reveal compatibility issues. A `.blend` file is NOT in this delivered ZIP.

## ART / continuation

The test geometry is intentionally a sphere-like object with visual deformation; it cannot satisfy any megacity, occupied city-space or protected M247-C art criteria. **ART NOT SUBMITTED**, not ART PASS. Do not reinterpret this fixture as a new candidate, and do not resume repeated procedural box/loft mass production merely because a few technical tests pass.

D37: prioritize a real Blender 5.2 run of the bridge on the user's available machine or a legitimately connected machine, with actual `.blend` outputs inspected before moving to the first lived-in architectural form. Work requires new explicit user approval. CITY MASTER 3D FIRST, all-city detail obligations, central adoption 0 and Minecraft construction HOLD remain unchanged.
