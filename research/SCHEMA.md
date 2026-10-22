# HALO-9 research artifact schema v1.0

Root `latest.json` is the single index per branch. The track has exclusive write ownership of its branch.
`latest: null` means no study result was submitted to this branch yet; do not treat this as missing data or acceptance.

Once a study is submitted, replace latest with an object containing:
- `study_id`: unique stable ID, e.g. `A2-G1`
- `title`: design name
- `stage`: `CONCEPT`, `BLOCKOUT_3D`, or `DETAILED_3D`
- `art_review_status`: `NOT_REVIEWED`, `HOLD`, `REJECT`, or `ACCEPTED_BY_USER`
- `updated_at`: ISO 8601 UTC timestamp
- `dimensions_m`: null or `{width, depth, height}` for VERIFIED model measurements only
- `proposed_dimensions_m`: null or corresponding conceptual dimensions; never substitute for measured dimensions
- `assets`: list of `{path, kind, sha256, size_bytes}`; kinds include `GLB`, `BLEND`, `PNG`, `CODE`, `JSON`, `REPORT`
- `validation`: object recording load results, shared-camera comparisons, what was actually checked, and limits
- `notes`: compact summary and unresolved concerns

`history` is an append-only array of earlier study IDs and study-manifest relative paths; do not overwrite REJECT evidence.
All study artifacts reside in `studies/<study_id>/` with an optional `studies/<study_id>/manifest.json`.
Keep stable paths and exact SHA-256 checksums. Do not declare a file uploaded until it exists in this branch.

Permissions / policy:
- Never modify main, official Minecraft worlds, formal M247-C source of truth, or other tracks' branches.
- No Minecraft construction, unapproved merges, or promotion from study to formally accepted design.
- Art quality review is independent of mesh/geometry QA. No 3D detail work after art REJECT without fresh concept approval.
- For large files investigate Git LFS or externally hosted research artifacts. Do not assume binary download via ChatGPT GitHub connector works.
- Prefer 6-camera PNG previews captured from exactly the same GLB for visual review; log focal length and scale.

Smoke tests (if present) are tiny synthetic capability checks, NOT HALO-9 research proposals.
