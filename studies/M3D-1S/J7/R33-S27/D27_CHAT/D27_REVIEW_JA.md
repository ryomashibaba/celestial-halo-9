# R33-S27-D27 — multi-mesh direct editing and bridge coupling (2026-10-29 JST)

**TECH LIMITED PASS / ART REJECT / FORMAL ADOPTION 0 / CITY MASTER 3D incomplete / Minecraft construction HOLD.**

## Verified foundations
main `a2f88995eee8d10ee4830dbdf33ccb9c0790de8f`; parent D26 `3dc46767d463f755d5f63c1748569eb83ed88fea`.
Respects official CITY MASTER 3D FIRST, city C, M247-C protection, W0, H1–H6 and SB01–SB16. No main, canonical assets, existing PR, Freeze or Minecraft world mutation. No Work, Blender GUI or Blender MCP.

## Real 3D study
Unlike D26's one neutral mesh, a new, isolated research testbed was built with **19 separately named, watertight geometries**, each GLB 3,768 triangles. It contains a continuous local ground route, plaza, roofed areas with open-air central atrium, two placeholder district masses, terraces and an elevated connector. **The district masses are solid placeholders, not inhabited buildings.** No approved city geometry, formal coordinates or real public-room certification.

BASE GLB SHA256 `c95bf29fd9a313c1c2d1b6f6a33053fb410fbf3b1ce4fb2877d065a2b9441622`.
EDIT GLB SHA256 `f00403b382bb4d3438eef7f50349abaed4295f33ed7a6f21ae5abfeba2207034`.

Read the saved GLB, move the 8 WEST meshes X=-60m and 8 EAST meshes X=+72m, then stretch the saved high-bridge mesh vertex ends to meet the shifted supports. **17 mesh coordinates changed**, while the ground route and plaza meshes stayed exactly unchanged. All face index arrays were preserved.

## QA (bounded)
- Real GLB readback and VTK intersection: ground route 335/335 sampled floor supports both BASE/EDIT, planned grade 1.8%.
- Elevated bridge/support pairs have 3D AABB overlap in both versions; this **does not certify structural joints or actual pedestrian access**.
- Injected obstruction appears at 3 centerline sample locations. Deleting the ground route and retaining only the plaza causes 335/335 failed supports.
- Bad group names, out-of-bounds displacement, nonfinite values and source SHA mismatch were rejected.
- Independent temporary-directory rerun of BASE-generating source gives byte-identical GLB. Independent subprocess replay of EDIT from BASE, JSON and editor gives byte-identical GLB.
- 7 corresponding VTK camera views from each saved GLB; RGB pixel difference threshold (>20) changed south 28.672%, west 20.972%, east 18.439%, reverse 29.185%, aerial 25.174%, ground-human 5.861%, side-human 16.300%. **Pixel differences are not silhouettes or art scores.**

## ART REJECT — stop this form
Multiview images still show generic giant box masses and thin roof/floor planes, with no real inhabited urban strata, genuine internal destination, or central M247-C architectural quality. Reject these meshes and do not rescue via detail or decoration. The useful output is the limited **multiple-named-mesh editor, bridge coupling, protected ground access and reproducible testing**, not the shape. Full access, bridge structure, all-city integration, Blender-native direct sculpt and artistic quality remain unproven.

## Evidence sharing boundary
This GitHub branch stores the guarded multi-mesh editor, JSON edit plan, review and lightweight evidence summary. Full builder, renderer, independent auditor, GLBs, original renders and QA are in chat ZIP `HALO9_D27_CHAT_RESEARCH.zip`; ZIP SHA256 `3e77e4c03adf8241c68abb8943eac6ca33640f74cb53fe528aa8c8a6a301888e`. **GLB and PNG/JPG binary evidence is not on GitHub.**

Next D28: do not resume box-based generative construction. Establish a visually driven workflow for genuinely inhabited mass, cut-through civic rooms and multidirectional macro aesthetics. User's new explicit permission is required for Work. Minecraft remains HOLD.
