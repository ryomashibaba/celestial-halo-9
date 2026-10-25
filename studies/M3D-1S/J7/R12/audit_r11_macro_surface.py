#!/usr/bin/env python3
"""J7-R12: inspect R11 ACTUAL GLB surfaces, not art quality.
All surface-area and raster summaries are proxy geometry measures; never
classify space as truly inhabited, traversable, or enclosed using them.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, math
from pathlib import Path
import numpy as np
import trimesh

CASES = {
    "A": "concept_A/R11_A.glb",
    "B": "concept_B/R11_B.glb",
    "B_REFINED": "refined/R11_B_REFINED.glb",
}
BINS = [
    (0, 20, "under_20m"),
    (20, 100, "20_to_100m"),
    (100, 500, "100_to_500m"),
    (500, 1500, "500_to_1500m"),
    (1500, float("inf"), "over_1500m"),
]
AXES = {
    "XZ": (0, 2, (-3600, 3700), (-300, 4750)),
    "YZ": (1, 2, (-3100, 2600), (-300, 4750)),
}
AREA_THRESH_M2 = 100.0 # remove rail/detail triangles from diagnostic maps ONLY


def spatial_metrics(scene):
    counts = collections.Counter()
    surface_buckets = collections.defaultdict(float)
    area_records = []
    macro_centers = []
    macro_weights = []
    all_min = np.array([np.inf, np.inf, np.inf])
    all_max = np.array([-np.inf, -np.inf, -np.inf])
    objects = 0
    bad = 0
    triangle_count = 0
    area_total = 0.0
    for node in scene.graph.nodes_geometry:
        matrix, geom_name = scene.graph[node]
        mesh = scene.geometry[geom_name]
        if not isinstance(mesh, trimesh.Trimesh) or len(mesh.vertices) == 0 or len(mesh.faces) == 0:
            continue
        vertices = trimesh.transform_points(np.asarray(mesh.vertices, dtype=float), matrix)
        faces = np.asarray(mesh.faces, dtype=int)
        if not np.isfinite(vertices).all():
            bad += 1
            continue
        low, high = vertices.min(axis=0), vertices.max(axis=0)
        all_min = np.minimum(low, all_min)
        all_max = np.maximum(high, all_max)
        side = float((high - low).max())
        tri = vertices[faces]
        cross = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        areas = 0.5 * np.linalg.norm(cross, axis=1)
        centroids = tri.mean(axis=1)
        area = float(areas.sum())
        triangle_count += len(faces)
        objects += 1
        area_total += area
        area_records.append((node, round(area, 3), round(side, 3), len(faces)))
        for left, right, key in BINS:
            if left <= side < right:
                counts[key] += 1
                surface_buckets[key] += area
                break
        significant = areas >= AREA_THRESH_M2
        if significant.any():
            macro_centers.append(centroids[significant])
            macro_weights.append(areas[significant])
    if not objects or not macro_centers:
        raise RuntimeError("GLB lacks sufficient actual macro surfaces")
    centers = np.vstack(macro_centers)
    weights = np.concatenate(macro_weights)
    if not np.isfinite(weights).all():
        raise RuntimeError("Nonfinite surface areas")
    total_macro_area = float(weights.sum())
    images = {}
    grid = {}
    for view, (ai, aj, xrange, yrange) in AXES.items():
        ranges = [np.linspace(*xrange, 91), np.linspace(*yrange, 75)]
        hist, xedges, yedges = np.histogram2d(
            centers[:, ai], centers[:, aj], bins=ranges, weights=weights)
        # This is projection of significant surface triangle CENTROIDS only.
        # Dark cells do NOT prove a volume is an empty open usable void.
        grid[view] = hist
        images[view] = {
            "x_axis": ["X", "Y"][view == "YZ"] + "_metres",
            "y_axis": "Z_metres",
            "x_range_m": list(xrange), "z_range_m": list(yrange),
            "grid_bins": list(hist.shape),
            "occupied_cells_surface_centroid_proxy": int(np.count_nonzero(hist)),
            "sum_macro_face_area_m2": round(float(hist.sum()), 2),
        }
    key_order = [name for a,b,name in BINS]
    top = sorted(area_records, key=lambda item:item[1], reverse=True)[:15]
    z_centers = centers[:, 2]
    zedges = np.arange(-300, 4801, 250)
    vertical_area_hist = np.histogram(z_centers, bins=zedges, weights=weights)[0]
    result = {
        "objects_examined": objects,
        "triangles_examined": triangle_count,
        "invalid_vertex_objects": bad,
        "model_bounds_m": [[round(float(x),2) for x in all_min],[round(float(x),2) for x in all_max]],
        "model_span_xyz_m": [round(float(x),2) for x in all_max-all_min],
        "all_face_area_proxy_m2": round(area_total,2),
        "macro_face_area_at_or_above_100m2_m2": round(total_macro_area,2),
        "macro_fraction_of_surface_area": round(total_macro_area / area_total,6),
        "size_bucket_by_object_max_span_m": [
            {"label":n, "object_count":counts[n],
             "surface_area_m2":round(surface_buckets[n],2),
             "fraction_of_total_face_area":round(surface_buckets[n]/area_total,6)}
            for n in key_order
        ],
        "largest_15_individual_mesh_nodes_by_surface_area": [
            {"name": n, "face_area_m2":a, "object_span_max_m":side, "triangles":tri}
            for n,a,side,tri in top
        ],
        "macro_area_by_z_250m": [
            {"z_from_m":int(zedges[i]),"z_to_m":int(zedges[i+1]),
             "macro_face_area_m2":round(float(vertical_area_hist[i]),2)}
            for i in range(len(vertical_area_hist))
        ],
        "face_centroid_projection_maps":images,
        "interpretation_warning":"Projected surface area and face-centroid occupancy are NOT a true solid-volume, hollow-void, clearance, traversal, habitation or artistic-quality test.",
    }
    return result, grid


def save_graphics(grids, dest):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    for view in AXES:
        fig, axes = plt.subplots(1, len(CASES), figsize=(14,5.5), sharex=True, sharey=True)
        _, _, xlim, zlim = AXES[view]
        for ax, (name, _) in zip(axes, CASES.items()):
            Z = np.log1p(grids[name][view]).T
            ax.imshow(Z, origin="lower", interpolation="nearest",
                      extent=[*xlim,*zlim], aspect="auto")
            ax.set_title(name + " | macro surface centroid")
            ax.set_xlabel(("X" if view=="XZ" else "Y")+" (m)")
            ax.set_ylabel("Z (m)")
        fig.suptitle("R11 "+view+" • actual GLB surface distribution, NOT enclosed volume/void")
        fig.tight_layout()
        path=dest/("R12_R11_MACRO_SURFACE_"+view+".png")
        fig.savefig(path,dpi=140)
        plt.close(fig)
        if not path.is_file() or path.stat().st_size<10000:
            raise RuntimeError("diagnostic image missing: "+str(path))


def test_geometry():
    # A 10x20x30m actual box must be one examined mesh, 12 triangles.
    box=trimesh.creation.box(extents=[10,20,30])
    sc=trimesh.Scene()
    sc.add_geometry(box,node_name="synthetic_baseline_box")
    metrics, grid=spatial_metrics(sc)
    assert metrics["objects_examined"]==1,metrics
    assert metrics["triangles_examined"]==12,metrics
    assert [round(x) for x in metrics["model_span_xyz_m"]]==[10,20,30],metrics
    assert metrics["invalid_vertex_objects"]==0,metrics
    assert grid["XZ"].ndim==2
    print("R12_AUDIT_TEST_PASS")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--r11",type=Path,help="J7/R11 folder with three actual GLBs")
    ap.add_argument("--out",type=Path,help="new R12 output folder")
    ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    if args.self_test:
        test_geometry()
        return
    if not args.r11 or not args.out:
        ap.error("--r11 and --out required unless --self-test")
    out=args.out.resolve()
    out.mkdir(parents=True,exist_ok=True)
    # Disallow silently reusing old QA that a failed runner could fake-pass.
    if list(out.iterdir()):
        raise RuntimeError("Output directory MUST be empty: "+str(out))
    grids={}
    evidence={
        "schema":"halo9.j7r12.r11_glb_macro_surface_audit.v1",
        "source":"REAL_EXISTING_J7_R11_GLB",
        "purpose":"Quantify visible distribution of large triangle surfaces, not judge art.",
        "tri_threshold_for_map_m2":AREA_THRESH_M2,
        "cases":{},
        "formal_art_adoption":"NONE",
        "minecraft_construction":"HOLD",
        "actual_new_blender_design":"NOT_MADE_BY_THIS_AUDIT",
        "method_limitation":"Triangle centroid and area summary. No exact void volume/watertightness, no traversability, no aesthetic PASS.",
    }
    for name, rel in CASES.items():
        path=args.r11 / rel
        if not path.is_file():
            raise RuntimeError("actual GLB unavailable "+str(path))
        sc=trimesh.load(str(path),force="scene",process=False)
        if not isinstance(sc,trimesh.Scene):
            raise RuntimeError("Unexpected scene type")
        result, g=spatial_metrics(sc)
        if result["invalid_vertex_objects"]:
            raise RuntimeError("Bad vertices in "+name)
        result["glb_bytes"]=path.stat().st_size
        result["glb_sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
        evidence["cases"][name]=result
        grids[name]=g
    save_graphics(grids,out)
    p=out/"R12_R11_MACRO_SURFACE_AUDIT.json"
    p.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("R12_ACTUAL_R11_GLB_AUDIT_PASS",json.dumps({
        n:{"objects":x["objects_examined"],"triangles":x["triangles_examined"],
           "bounds":x["model_span_xyz_m"]}
        for n,x in evidence["cases"].items()
    }))


if __name__=="__main__":
    main()
