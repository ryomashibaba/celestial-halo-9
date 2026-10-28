"""Independent R33-S27-D4 geometry smoke test. Research-only; not building approval.
Usage:
  pip install numpy trimesh
  python d4_verify_ground.py <extracted>/R33_S27_D4_CHAT/models/S27_D4_CIVIC_SEAM.glb
"""
import argparse
import json
import numpy as np
import trimesh

def verify(model):
    scene = trimesh.load(model, force="scene")
    meshes = scene.geometry
    floors = {
        name: mesh.bounds
        for name, mesh in meshes.items()
        if name.endswith("_floor") or "threshold" in name
        or name in {"street_walk_surface", "arrival_plaza", "north_civic_square"}
    }
    obstacles = {
        name: mesh.bounds
        for name, mesh in meshes.items()
        if name not in floors and not name.startswith("context_")
    }
    routes = {
        "street": [(0, y) for y in np.arange(-195, 195.01, 2)],
        "west_hall": [(x, -42) for x in np.arange(0, -59, -1)],
        "east_library": [(x, 45) for x in np.arange(0, 49)],
        "west_studio": [(x, -126) for x in np.arange(0, -52, -1)],
        "east_community": [(x, 135) for x in np.arange(0, 54)]
    }
    path_report = {}
    for route_name, pts in routes.items():
        missed = 0
        collisions = 0
        for x, y in pts:
            ground = any(
                lo[0] <= x <= hi[0] and lo[1] <= y <= hi[1] and abs(hi[2] - 8) <= .3
                for lo, hi in floors.values()
            )
            blocked = any(
                lo[0] - 1 <= x <= hi[0] + 1 and lo[1] - 1 <= y <= hi[1] + 1
                and lo[2] <= 10.5 <= hi[2]
                for lo, hi in obstacles.values()
            )
            missed += not ground
            collisions += blocked
        path_report[route_name] = {"samples": len(pts), "missing_floor": missed, "obstructed": collisions}
    r = {
        "meshes": len(meshes),
        "triangles": sum(len(m.faces) for m in meshes.values()),
        "watertight": sum(m.is_watertight for m in meshes.values()),
        "positive_volume": sum(m.volume > 0 for m in meshes.values()),
        "paths": path_report,
        "LIMITATIONS": "Only ground-level centerline sampling and conservative mesh AABBs; NOT exact mesh collision, whole-width walking certification, upper circulation, real building safety or city master."
    }
    print(json.dumps(r, ensure_ascii=False, indent=2))
    if r["watertight"] != r["meshes"] or any(v["missing_floor"] or v["obstructed"] for v in path_report.values()):
        raise SystemExit(1)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("glb")
    args = p.parse_args()
    verify(args.glb)
