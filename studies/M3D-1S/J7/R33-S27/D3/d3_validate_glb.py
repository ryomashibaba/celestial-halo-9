"""Independent mesh audit for research-only S27-D3 GLB.
Usage: python d3_validate_glb.py path/to/S27_D3_INHABITED_CONFLUENCE.glb
Requires: pip install trimesh numpy
Does not certify architectural occupancy, path collision, or city integration.
"""
import argparse
import hashlib
import json
from pathlib import Path
import trimesh


def validate(path):
    scene = trimesh.load(path, force="scene")
    meshes = list(scene.geometry.values())
    result = {
        "file": path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "mesh_count": int(len(meshes)),
        "triangle_count": int(sum(len(mesh.faces) for mesh in meshes)),
        "watertight": int(sum(mesh.is_watertight for mesh in meshes)),
        "winding_consistent": int(sum(mesh.is_winding_consistent for mesh in meshes)),
        "positive_volume": int(sum(mesh.volume > 0 for mesh in meshes)),
        "bounds_m": scene.bounds.tolist(),
        "limitation": "Mesh integrity only. Not proof of usable rooms or walkable routes.",
    }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("glb", type=Path)
    args = parser.parse_args()
    report = validate(args.glb)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["watertight"] != report["mesh_count"] or report["winding_consistent"] != report["mesh_count"] or report["positive_volume"] != report["mesh_count"]:
        raise SystemExit(1)
