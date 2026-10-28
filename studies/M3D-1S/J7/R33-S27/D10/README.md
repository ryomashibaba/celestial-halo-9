# R33-S27-D10 — method research, partial execution
2026-10-28 JST

**TECH LIMITED PASS (open-patch editing coupon only) / ART HOLD (architecture unproduced, art unassessed).**
Formal central adoption **0**. CITY MASTER **incomplete**. Minecraft **HOLD**.

- [D9 evidence audit](D9_EVIDENCE_AUDIT_JA.md): source consistency, missing binary evidence, verifier blind spots; no false D9 rerun claim.
- [Method comparison and measured result](D10_METHOD_STUDY_JA.md): four production methods, primary sources, actual positive and negative experiments, limitations.
- [Pure executable research source](d10_method_coupon.mjs): runD10() returns OBJ text, separate-parser verification, mutation results, SHA256. No IO, imports, or Blender calls. It was actually evaluated as ECMAScript in the Chat orchestration isolate (only the export declaration was removed there). Local execution is subject to the project's prior Work-approval rule.
- [Observed output](D10_RESULTS.json).
- [Content inventory/hashes](D10_EVIDENCE_MANIFEST.json).

## Actual editable geometry included
`models/BASE.obj`, `models/SEMANTIC_EDIT.obj`, `models/DIRECT_EDIT.obj` are text vertex/triangle meshes. `models/CAGE_ONLY_DRAG.obj` and `models/GLOBAL_SCALE.obj` are deliberate negative/control cases. All five contain the same connectivity. They are small open-surface method coupons, not buildings, public interiors, closed Mesh Deform cages, approved central models, GLB or native BLEND. Import into Blender has **not** been tested. No images/renders are included.

Measured success: two floor sample widths changed +24m/+12m while preserving eight patch pins; arbitrary selected handle +32m also propagated into the two floor samples. A separate serialization/parser measurement detected an unbound floor gap of 19.2m and global-scaling pin drift of 89.725490m. Those comparisons do not demonstrate beautiful architecture.

The previous D9 binary objects/images are still NOT shared by this folder. This folder adds fully disclosed, reproducible D10 source and small OBJ test data instead of claiming unseen legacy models are present.

## Boundaries and remaining work
Only this D10 folder and an append-only S27 status entry are intended changes. No main/PR/original/Freeze/world edits; no approval to change M247-C, W0/H/SB/view/axis obligations; no automatic adoption. Initial local read operations are disclosed in the audit. No Blender or local prototype was executed.

The next substantive art test requires observing and editing a real authored Blender form with public-space relationships, then reviewing consistent distant/oblique/rear/overhead/interior/human views, and native save/reload. **Work/local-computer approval is still required before that phase.** This is not D10 whole-stage completion and not another proposed Work prompt passed off as implementation.
