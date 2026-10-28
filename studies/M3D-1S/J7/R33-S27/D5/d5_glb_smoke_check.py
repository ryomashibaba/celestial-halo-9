"""D5 GLB independent smoke test. pip install trimesh; python d5_glb_smoke_check.py model.glb
NOT proof of artistic quality, walkability, habitation, city or construction.
"""
import json
import sys
import trimesh

scene = trimesh.load(sys.argv[1], force="scene")
meshes = list(scene.geometry.values())
result = {
    "mesh_count": int(len(meshes)),
    "triangles": int(sum(len(m.faces) for m in meshes)),
    "watertight": int(sum(m.is_watertight for m in meshes)),
    "winding_consistent": int(sum(m.is_winding_consistent for m in meshes)),
    "positive_volume": int(sum(m.volume > 0 for m in meshes)),
    "bounds_m": scene.bounds.tolist(),
    "limitation": "Individual GLB mesh integrity only; no usable-space/route/aesthetic certification."
}
print(json.dumps(result, indent=2))
if any(result[k] != result["mesh_count"] for k in ("watertight", "winding_consistent", "positive_volume")):
    raise SystemExit(1)
