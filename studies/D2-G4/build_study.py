"""Build low-detail implicit massing studies for HALO-9 D2-G4.

All coordinates are kilometres internally; GLB exports are metres. This is a
concept massing generator, not a structural or construction model.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
NX, NY, NZ = 83, 73, 81
BOUNDS = ((-3.8, 3.8), (-3.2, 3.2), (-0.75, 6.0))
SMOOTH = 0.66


def grid():
    axes = [np.linspace(a, b, n, dtype=np.float32) for (a, b), n in zip(BOUNDS, (NX, NY, NZ))]
    return np.meshgrid(*axes, indexing="ij"), axes


def ellipsoid_sdf(x, y, z, center, radii, roll=0.0, exponent=2.65):
    cx, cy, cz = center
    rx, ry, rz = radii
    ca, sa = math.cos(roll), math.sin(roll)
    dx, dy = x - cx, y - cy
    u, v = ca * dx + sa * dy, -sa * dx + ca * dy
    q = (np.abs(u / rx) ** exponent + np.abs(v / ry) ** exponent
         + np.abs((z - cz) / rz) ** exponent) ** (1.0 / exponent)
    return (q - 1.0) * min(rx, ry, rz) * 0.82


def smooth_min(a, b, k=SMOOTH):
    h = np.maximum(k - np.abs(a - b), 0.0) / k
    return np.minimum(a, b) - h * h * k * 0.25


def smooth_max(a, b, k=SMOOTH):
    return -smooth_min(-a, -b, k)


def cluster_field(x, y, z, cells):
    field = np.full(x.shape, 8.0, dtype=np.float32)
    for c, r, angle in cells:
        sdf = ellipsoid_sdf(x, y, z, c, r, angle)
        field = smooth_min(field, sdf, SMOOTH)
    # Deliberate low-amplitude striation: a continuous fused geological skin,
    # not repeated balls or a regular cell grid.
    ripple = (0.045 * np.sin(1.15 * x + 0.5 * z) * np.cos(0.92 * y - 0.35 * z)
              + 0.025 * np.sin(1.7 * y + 0.9 * x + 0.3 * z))
    return field + ripple


def field_n1(x, y, z):
    cells = [
        ((-0.62, -0.02, 2.36), (2.70, 2.12, 2.78), -0.12),
        ((1.02, 0.22, 2.18), (2.26, 2.06, 2.05), 0.23),
        ((-1.08, 0.34, 4.22), (1.92, 1.78, 1.50), -0.34),
        ((0.75, 0.22, 4.47), (1.92, 1.58, 1.35), 0.22),
        ((-0.02, 0.12, 0.58), (2.78, 2.22, 1.00), 0.09),
    ]
    mass = cluster_field(x, y, z, cells)
    # A deep, oblique urban gorge, narrower at one inhabited saddle and broad
    # at two public chambers. It opens toward the foreground and curls in plan.
    xc = -0.20 + 0.40 * np.sin(0.82 * z + 0.20) + 0.19 * np.sin(1.65 * y)
    yc = -1.28 + 0.10 * np.sin(0.70 * z)
    wx = 0.74 + 0.23 * np.exp(-((z - 1.32) / 0.62) ** 2) + 0.37 * np.exp(-((z - 3.48) / 0.82) ** 2)
    wy = 1.76 + 0.29 * np.sin(0.60 * z + 0.32)
    main_cut = (np.sqrt(((x - xc) / wx) ** 2 + ((y - yc) / wy) ** 2) - 1.0) * 0.80
    # Short unequal tributary chamber; it makes the canyon turn into the city.
    tributary = ellipsoid_sdf(x, y, z, (0.88, -0.08, 2.72), (1.28, 1.04, 0.76), -0.46)
    cut = smooth_min(main_cut, tributary, 0.24)
    result = smooth_max(mass, -cut, 0.16)
    # One broad, inhabited civic saddle retains city continuity across the cut.
    for center, radii, angle in [
        ((-0.28, -0.18, 2.92), (1.58, 0.72, 0.30), 0.24),
    ]:
        saddle = ellipsoid_sdf(x, y, z, center, radii, angle)
        result = smooth_min(result, saddle, 0.12)
    return result


def field_n2(x, y, z):
    cells = [
        ((-0.72, 0.10, 2.24), (2.68, 2.00, 2.50), 0.21),
        ((1.10, 0.08, 2.70), (2.38, 1.94, 2.42), -0.26),
        ((-1.25, 0.38, 4.27), (1.80, 1.66, 1.38), 0.34),
        ((0.62, 0.42, 4.58), (1.90, 1.52, 1.28), -0.22),
        ((0.08, 0.15, 0.62), (2.70, 2.15, 0.95), -0.10),
    ]
    mass = cluster_field(x, y, z, cells)
    # The first inhabited cleft rises from the forecourt and bends toward the
    # upper rear; the second enters obliquely at a separate altitude.
    x1 = -0.42 + 0.46 * np.sin(0.76 * z + 0.28) + 0.14 * np.sin(1.35 * y)
    y1 = -1.22 + 0.10 * np.sin(0.65 * z)
    w1 = 0.72 + 0.34 * np.exp(-((z - 2.82) / 0.72) ** 2) + 0.18 * np.exp(-((z - 4.2) / 0.58) ** 2)
    d1 = (np.sqrt(((x - x1) / w1) ** 2 + ((y - y1) / 1.82) ** 2) - 1.0) * 0.80
    # Cross-fold is a diagonal civic void, not an orthogonal tunnel: it rises
    # eastward and shifts toward the rear as it crosses the core.
    zc = 2.52 + 0.38 * x + 0.22 * np.sin(0.96 * y + 0.2)
    yc = 0.05 + 0.26 * x
    d2 = (np.sqrt(((z - zc) / 0.58) ** 2 + ((y - yc) / 1.18) ** 2) - 1.0) * 0.68
    cut = smooth_min(d1, d2, 0.20)
    result = smooth_max(mass, -cut, 0.16)
    # A single inhabited concourse deep inside the cross-fold. Its shift in
    # plan and height avoids a symmetrical gateway reading.
    saddle = ellipsoid_sdf(x, y, z, (0.62, 0.05, 3.18), (1.42, 0.62, 0.30), 0.27)
    result = smooth_min(result, saddle, 0.12)
    return result


TETS = ((0, 5, 1, 6), (0, 1, 2, 6), (0, 2, 3, 6),
        (0, 3, 7, 6), (0, 7, 4, 6), (0, 4, 5, 6))
TET_EDGES = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
CUBE_OFFSETS = ((0,0,0),(1,0,0),(1,1,0),(0,1,0),(0,0,1),(1,0,1),(1,1,1),(0,1,1))


def polygonize(values, axes):
    (xs, ys, zs) = axes
    dx, dy, dz = xs[1] - xs[0], ys[1] - ys[0], zs[1] - zs[0]
    verts, faces, edge_cache = [], [], {}
    nx, ny, nz = values.shape
    # Iterate only cells crossed by the isosurface; the 3-D field itself is
    # vectorized. Marching tetrahedra gives a portable, dependency-light mesh.
    corners = [values[ox:nx-1+ox, oy:ny-1+oy, oz:nz-1+oz]
               for ox, oy, oz in CUBE_OFFSETS]
    cmin = np.minimum.reduce(corners)
    cmax = np.maximum.reduce(corners)
    crossing = (cmin <= 0) & (cmax >= 0)
    cells = np.argwhere(crossing)
    for i, j, k in cells:
        positions = [(xs[i+ox], ys[j+oy], zs[k+oz]) for ox,oy,oz in CUBE_OFFSETS]
        vals = [float(values[i+ox, j+oy, k+oz]) for ox,oy,oz in CUBE_OFFSETS]
        if min(vals) > 0 or max(vals) < 0:
            continue
        for tet in TETS:
            tv = [vals[q] for q in tet]
            inside = [q for q in range(4) if tv[q] < 0]
            if not inside or len(inside) == 4:
                continue
            outside = [q for q in range(4) if tv[q] >= 0]
            hits = []
            for ea, eb in TET_EDGES:
                if (tv[ea] < 0) == (tv[eb] < 0):
                    continue
                ca, cb = tet[ea], tet[eb]
                key = tuple(sorted((tuple((i+CUBE_OFFSETS[ca][0], j+CUBE_OFFSETS[ca][1], k+CUBE_OFFSETS[ca][2])),
                                    tuple((i+CUBE_OFFSETS[cb][0], j+CUBE_OFFSETS[cb][1], k+CUBE_OFFSETS[cb][2])))))
                vi = edge_cache.get(key)
                if vi is None:
                    t = tv[ea] / (tv[ea] - tv[eb])
                    pa, pb = positions[ca], positions[cb]
                    vi = len(verts)
                    verts.append((pa[0] + t * (pb[0]-pa[0]), pa[1] + t * (pb[1]-pa[1]), pa[2] + t * (pb[2]-pa[2])))
                    edge_cache[key] = vi
                hits.append(vi)
            if len(hits) == 3:
                faces.append(tuple(hits))
            elif len(hits) == 4:
                # Sort intersections around their polygon plane before splitting
                # the quad. The raw edge iteration order is not cyclic and would
                # otherwise make bow-tie triangles in 2-in/2-out tetrahedra.
                p = np.asarray([verts[q] for q in hits], dtype=np.float64)
                c = p.mean(axis=0)
                normal = np.cross(p[1]-p[0], p[2]-p[0])
                nl = np.linalg.norm(normal)
                if nl < 1e-10: continue
                normal /= nl
                u = p[0]-c; u /= max(np.linalg.norm(u), 1e-12)
                vaxis = np.cross(normal, u)
                angles = np.arctan2((p-c) @ vaxis, (p-c) @ u)
                qids = [hits[q] for q in np.argsort(angles)]
                faces.append((qids[0], qids[1], qids[2]))
                faces.append((qids[0], qids[2], qids[3]))
    v = np.asarray(verts, dtype=np.float32)
    f = np.asarray(faces, dtype=np.int32)
    # Convert km to m; orient faces away from the negative (interior) field.
    v *= 1000.0
    cent = v[f].mean(axis=1) / 1000.0
    # Approximate normal direction from the centroid, sufficient to orient the
    # shell toward the local exterior for this single connected mass.
    normals = np.cross(v[f[:,1]] - v[f[:,0]], v[f[:,2]] - v[f[:,0]])
    radial = cent - np.array([0.0, 0.0, 2.6], dtype=np.float32)
    flip = (normals * radial).sum(axis=1) < 0
    f[flip] = f[flip][:, [0, 2, 1]]
    return trimesh.Trimesh(vertices=v, faces=f, process=True)


def make_mesh(fn):
    (x, y, z), axes = grid()
    field = fn(x, y, z)
    mesh = polygonize(field, axes)
    mesh.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(mesh)
    mesh.export(OUT / ("N1-Marrow-Gorge.glb" if fn is field_n1 else "N2-Offset-Crossfold.glb"))
    return mesh


def render_view(mesh, direction, image, box, color=(190, 203, 212), target=(0.0, 0.0, 2.7)):
    """Small orthographic, flat-lit diagnostic render from the exported mesh."""
    w, h = image.size
    eye = np.asarray(direction, dtype=float)
    eye /= np.linalg.norm(eye)
    up = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(eye, up)) > 0.94:
        up = np.array([0.0, 1.0, 0.0])
    right = np.cross(up, eye); right /= np.linalg.norm(right)
    up2 = np.cross(eye, right); up2 /= np.linalg.norm(up2)
    center = np.asarray(target, dtype=float) * 1000.0
    rel = mesh.vertices - center
    sx, sy, depth = rel @ right, rel @ up2, rel @ eye
    span = max(box) * 1.13
    px = (sx / span + 0.5) * w
    py = (0.5 - sy / span) * h
    tri = mesh.faces
    norms = mesh.face_normals
    # Painter's order is a compact portable preview. Face culling is disabled
    # because the isosurface may contain open boundary edges at its ground cut.
    tids = np.argsort(depth[tri].mean(axis=1))
    light = np.array([-0.42, -0.62, 0.67]); light /= np.linalg.norm(light)
    draw = ImageDraw.Draw(image)
    for t in tids:
        ids = tri[t]
        pts = [(float(px[q]), float(py[q])) for q in ids]
        if max(p[0] for p in pts) < 0 or min(p[0] for p in pts) >= w or max(p[1] for p in pts) < 0 or min(p[1] for p in pts) >= h:
            continue
        lum = 0.40 + 0.60 * abs(float(np.dot(norms[t], light)))
        c = tuple(int(v * lum) for v in color)
        draw.polygon(pts, fill=c)
    return image


def comparison_image(meshes):
    # Six common camera directions; same orthographic span and model center.
    views = [("FRONT", (0,-1,0.11), (0,0,2.7)), ("OBLIQUE", (1,-1,0.55), (0,0,2.7)),
             ("SIDE", (1,0,0.12), (0,0,2.7)), ("TOP", (0.15,-0.24,1), (0,0,2.7)),
             ("REAR", (0,1,0.10), (0,0,2.7)), ("INTERIOR", (0,1,0.12), (0,-0.64,2.75))]
    W, H = 360, 330
    # Three columns by four rows: six equal-scale views for each concept.
    board = Image.new("RGB", (W*3, (H-25)*4), (17,22,31))
    d = ImageDraw.Draw(board)
    for row, (name, mesh) in enumerate(meshes):
        for col, (label, vec, target) in enumerate(views):
            r, c = row*2 + col//3, col%3
            top = r*(H-25)
            img = Image.new("RGB", (W,H-25), (25,33,45))
            render_view(mesh, vec, img, (7600,6400,5700), (190,203,212) if row == 0 else (183,197,205), target=target)
            board.paste(img,(c*W,top))
            ImageDraw.Draw(board).text((c*W+8,top+7), f"{name.split(' — ')[0]} / {label}", fill=(230,235,242))
    board.save(OUT / "D2-G4-six-view-diagnostic.png", optimize=True)


def main():
    meshes = [("N1 — 密核貫峡", make_mesh(field_n1)), ("N2 — 偏心交差峡谷", make_mesh(field_n2))]
    comparison_image(meshes)
    stats = {}
    for name, mesh in meshes:
        dims = mesh.extents.tolist()
        stats[name.split(" — ")[0]] = {
            "vertices": int(len(mesh.vertices)), "faces": int(len(mesh.faces)),
            "watertight": bool(mesh.is_watertight), "bounds_m": mesh.bounds.tolist(),
            "dimensions_m": dims,
            "volume_m3": float(mesh.volume) if mesh.is_watertight else None,
            "surface_area_m2": float(mesh.area),
            "winding_consistent": bool(mesh.is_winding_consistent),
            "connected_components": int(len(mesh.split(only_watertight=False))),
            "geometry_method": "single implicit smooth-union isosurface with carved civic voids; marching tetrahedra"
        }
    (OUT / "geometry-validation.json").write_text(json.dumps({
        "study_id":"D2-G4", "units":"metres in GLB; internal design coordinates in kilometres",
        "grid_resolution":[NX,NY,NZ], "method":"procedural implicit massing, no Blender session",
        "limitations":["concept massing only; no structure, circulation simulation, inhabited district geometry, or constructability claim",
                       "six images are diagnostic software renders from the same mesh with common orthographic scale",
                       "the interior-axis view is orthographic and does not establish walk-through sightlines",
                       "smooth fused mass still reads as a gate and a generic blob in several views; both concepts fail the internal art screen"],
        "models":stats
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
