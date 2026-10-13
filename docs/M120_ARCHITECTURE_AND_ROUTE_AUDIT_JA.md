# M120 architectural spine and conservative urban walkability review

## Actual research work
M120 uses the unchanged M119 B FRACTURED SKY TERRACES base (603 meshes) and appends **130 new 3D geometric research envelopes** for a total 733. HERO4 become more differentiated in appearance (SB05 five pitched roof canvases, SB08 two tall arches, SB09 gate flanking splays, SB12 mountain ridge fans), civic public court gets six large dark angled structural spines, three deep stepped decks, and macro perimeter includes eight major new diagonal anchors. This is **not a finished game city**: visible improvement over the sparse old model is modest; many old white-box forms remain.

A new proposed SB13->SB09->SB10->civic core->SB07->SB08->inner halo path has 10 mathematical stations, 9 endpoint-contiguous segments and **2 completely unbuilt vertical lifts**. The true SB13 3x4 preserved entrance coordinates are UNKNOWN. Do not label it walkable, fully cleared, or connected to actual existing doors.

## Safety analysis grounded to USER review save
Actual user M117 old-building atlas: 1456/1456 chunks, 1,095,343 material-heuristic blocks, 2,096 occupied 8x8 tiles. M120 **tile-level XZ and material-min/max-Y AABB broadphase** of NEW 130 meshes detects 38 meshes in 600 distinct observed old-material tiles with 1,204 possible mesh-tile intersections; other 92 meshes have no hits in this limited test. Tile ranges are NOT exact voxel collision, and the 88 protected voids/Freeze408/public959/approved roads/parks/outer terrain remain unregistered at exact voxel resolution. 0 tile hits MUST NOT be called safe-to-build. Original old city stays untouched.

The first two route segments have 13 and 8 saved-material tile risk hits. Remaining 7 have no tile hits but still do not have void, roadway, structural, collision or traversability approval. M101 relative H -> Minecraft Y still unknown. New concept Y are visualization proposals in the user's measured absolute-Y coordinate frame only.

## GitHub vs portable source truth
GitHub Draft PR contains this summary, deterministic route node generator, and CI checks. Full M119+M120 source code, original M117 user atlas, M120 full 3D JSON and four rendered architectural research diagrams are in the **portable M120/M121 handoff ZIP**, with manifest and independent reproduction. Do NOT assert GitHub contains the full visual generator or actual saved voxel geometry.

## Next practical M121 major step
1. One large truly convincing interior/public plaza experience from pedestrian-eye and inward cathedral views, based on the actual 16-site map, rather than polishing the floating-ring outline.
2. Exact location/mapping of old Frozen408/protected and 88 voids before any destructive geometry proposal or real-world write; if missing, retain UNKNOWN.
3. Resolve real-world SB13 door anchor and the first lift's 13+8 risk tiles, then complete full 3D traversable design (stairs, lift operation, actual walkable surface) as an **offline** pilot.
4. Distinguish user-verified review copy CH9_D6D_REVIEW_COPY from still NULL official施工 save. No world modifications, no M101 baseline promotion and no freeze/canonical/staging changes.
