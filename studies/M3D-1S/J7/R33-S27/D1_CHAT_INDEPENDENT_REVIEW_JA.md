# R33-S27-D1 — 独立実3D制作・審査（Chat）
Date: 2026-10-28 JST
State: **ART REJECT / keep only verified research technique**. No formal art adoption; Minecraft construction HOLD; CITY MASTER 3D FIRST unchanged.

## Actual research
Original semantics-based independent GLB, not an edit or copy of rejected T1/S26:
- Four distinct altitudes/district nodes (W_LOW, E_MID, W_HIGH, N_SKY), 12 illustrative building components, civic floor, plazas, access placeholders, 4 sculpted giant mass components, 5 geometric connection intents, 10km **uncertified research-only** context.
- 38 individually closed meshes, 496 triangles, scene GLB sha256 `659b6755453dc01ad1c1e11dad663f4a9f572086c5b895c3e6e2bdd352b04eb4`.
- Six actual 3D camera renders plus a with/without-main-masses counterfactual.
- Reproducible local Python source, VTK rendering, independent line-of-sight occlusion testing; source archive `R33_S27_D1_CHAT_RESEARCH.zip` delivered in Chat only, not pushed to GitHub.

## Honest art review
**REJECT**: four enclosing masses appear as unrelated giant angular rocks; the cities largely disappear visually; exposed urban floor plates and small buildings remain unrelated background props; galleries read as thin sticks. Removing masses reveals unsupported sky shelves, not an appealing city. Continuing to embellish these shapes would repeat S23/S24/S26 failures. D1 is not ART CANDIDATE.

## Quantified visibility QA
17 sample plaza/rooftop targets tested per view against four hull masses (line-of-sight to target centers; NOT pixel-area coverage): oblique **15/17 blocked**, reverse **14/17**, front **14/17**, aerial **17/17**.

## Geometric links are not walkable paths
Connection-intent vertical/horizontal straight-line angles: **5.3°, 71.0°, 31.8°, 57.3°, 65.2°**. Public circulation, landings, supports, real lifts and full urban navigation NOT certified. Connectivity of a semantic graph is not physical access.

## Lessons for S27-D2
Do NOT repeat "program first + wrap in arbitrary large solid"; nor "beautiful shell first + append city". Co-design specific high-value public room/approach and outside skyline as one visual+spatial composition. Require one physically credible public route; keep multiscale 10km context as explicitly uncertified. No new bulk detailing unless independently reviewed actual 3D improves. Avoid C55-C copying and preserve M247-C formal research direction and city-C constitution.

## Evidence / limitations
Local evidence file `evidence/D1_OCCLUSION_AUDIT.json`, generator `s27_d1_build.py`, GLB and rendered views are all in the Chat-only ZIP. GitHub stores the trace and declaration here, NOT the binary GLB or image content. Blender native BLEND, live MCP, C55-C target reproduction, exact world coordinates and full detailed city are unverified.
