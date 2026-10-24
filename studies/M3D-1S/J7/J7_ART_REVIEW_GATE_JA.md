# M3D-1S/J7 — ART-FIRST stop gate and same-camera real-GLB review

**Date:** 2026-10-24 JST  
**Status:** REVIEW INFRASTRUCTURE ONLY / NO NEW ART ADOPTED  
**Depends on:** J6 (Draft PR #31); this research branch does not modify J6 or main.

## 0. Locked project requirements (checked against main)
- **CITY MASTER 3D FIRST:** build a detailed, editable, integrated ~10 km city master before Minecraft. Only ordinary buildings' private interiors may be simplified; all exteriors, public interiors, all SB01–SB16, H1–H6, W0 terrain, infrastructure, roads, light/materials remain detailed.
- **ART-FIRST / Macro Impact First:** central protagonist must have huge inhabited continuous city masses, readable urban-scale civic voids, strong asymmetric massing, coherent multi-view architectural art. Numerical size, GLB existence and QA pass do not imply beauty.
- Preserve W0, H1–H6, SB01–SB16, HERO4, M247-C as a formal *research direction* (not approved art); artistic exploration is not restricted to a clone of M247-C.
- **Minecraft construction HOLD, canonical originals protected, main unchanged, no auto merge.**

## 1. Why J7 changes focus
J6 reduced the remaining three sampled full-width BOX headroom events from 100 to zero and preserves 429 existing pieces. This is a **limited collision screen**, not a walking test. The J3–J6 object collection still relies on plain block/deck construction; it does **not** prove the user's urgent artistic requirement ("規模感が足りない") is satisfied.

**STOP treating J6 as a plausible finished central building.** Retain J3–J6 for route/asset technique only. Another cycle of fixing its mesh cannot be counted as central art progress.

## 2. J7-R0 objective
Use a real, single GLB in Blender to test whether the geometry visually reads as inhabitable civic space instead of boxes and floating platforms. The included audit runner changes neither the GLB nor any original. It sets **fixed-scale** exterior cameras and a separate local-detail camera, creates render images and numerical readback. The runner is **not yet executed** in Blender; render output and Blender import success must not be claimed.

### Fixed exterior views
Front / three-quarter / right side / rear / aerial / ground approach / reverse diagonal. An additional local-detail camera tests readability of real spatial elements. Exterior orthographic scale is always 10,500 m and the target datum (0,0,1700 m) stays consistent, so changing cameras cannot fake an increase in urban size. Local-detail is explicitly excluded from scale comparison.

### Pass/fail questions
1. At fixed city camera, does a central mass read as a **single civilization**, not separate giant geometric primitives?
2. Are the central civic voids actually carved into the bodies and legible, rather than an empty sky gap or a dark colored surface?
3. Are the west/east and bottom/top inhabited districts large and visibly **inside** integrated structural masses?
4. Can a visitor enter a real public room and move via real floors and transport? Do not infer this from route graphs.
5. Are side, rear, aerial and ground views **equally architectural**, instead of a single promotional front silhouette?
6. Is it visually distinguished from the known REJECT vocabulary (boxes, thick planks, giant simple gates, smooth opaque shells, trays, symbolic windows)?
7. At the same 10 km context scale is the protagonist unmistakably monumental **without crowding out** W0, H1–H6 and SB01–SB16?

For J6, the expected decision is **ART HOLD**, because real artistic improvements were not authored. A numerical scale or mesh count is not a pass. Do not fabricate an art grade before opening the actual renders.

## 3. Architectural direction to test after baseline review
**Research direction, not formally adopted: "Civic Rift as Inhabited Geography."** Instead of enlarging C's two smooth shells:
- Build **inhabited and occupiable cliff cross-sections** on each shore of an asymmetric sky fracture. Habitat, transit levels, civic rooms and roof geometry are the *mass itself*, not wallpaper on a flat exterior.
- Use at least two different multi-hundred-metre public volumes: one mostly enclosed inside an inhabited shore, one with a deliberately open high-altitude threshold. Their sections must meaningfully modify the outer skyline.
- Make a distinct high-altitude urban continent (with thickness, neighbourhood streets, and transport) and a defensible relationship to W0 ground; don't stack skinny view decks and tiny houses on a pole.
- Require shared spatial evidence: section cuts, entrance-to-destination continuity, 7+ camera views **from the same GLB**, and readable width/height/depth inside the same 10km research context.
- **Do not implement by automatically enlarging the old A/B/C loft proxies**. First prove a small shared liveable section in real geometry, then scale up while keeping the same artistic vocabulary.

The J6 geometry cannot fill this role; a new artwork and genuine Blender viewport feedback are required. An experimental mesh should be rejected early if it again becomes a flat sheet, box canyon or futuristic train station.

## 4. Deliverable and exact evidence status
- `blender_multiview_audit.py`: stand-alone *unexecuted* Blender 5.x background review utility with fixed camera settings. Imports the selected GLB; never exports geometry over the original.
- `J7_REVIEW_MANIFEST.json`: machine-readable art requirements and no-run status.
- No GLB edited, no new central design accepted. Actual fixed-camera images and GUI/Blender import are **PENDING**, not represented as successful.

## 5. Suggested isolated invocation (when a Blender-capable environment is available)
Run from a disposable copy of the research assets; use separate audit output folder and avoid overwrite of originals.

```bash
blender --background --factory-startup --python blender_multiview_audit.py -- /path/to/M3D1S_J6_UPPER_EAST.glb /path/to/output-j7-review
```

The report written by Blender must distinguish load/render PASS from art PASS; rendering never means visual approval. Next genuine J7 work is the 3D-authoring and multiview assessment loop, not another prose-only spec. The user need not perform manual expert modeling.
