"""C55-E shared library (numpy only). Z-up, metres.
Sheet = thick habitable plate (two inhabited faces) built from a parametric mid-surface grid.
Renderer = C55-D numpy software renderer (core.py). NOT Blender / Cycles."""
import numpy as np
from core import Mesh, grid_faces, vertex_normals, boxes


def smooth(a, b, x):
    t = np.clip((np.asarray(x, float) - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def pulse(f, w, soft=0.15):
    """periodic groove/rib profile: f in [0,1) phase, w = full width as fraction of period. 1 inside, 0 outside."""
    d = np.abs(f - 0.5) * 2.0          # 0 centre -> 1 edge
    return 1.0 - smooth(w * (1 - soft), w, d)


def stair(x, tread=0.7):
    """sloped-riser staircase: flat tread (fraction) then smooth riser. returns continuous 'count' of steps."""
    i = np.floor(x)
    f = x - i
    return i + smooth(tread, 1.0, f)


def hash2(a, b, seed=0):
    a = np.asarray(a, np.int64); b = np.asarray(b, np.int64)
    h = (a * 73856093) ^ (b * 19349663) ^ (seed * 83492791)
    h = (h ^ (h >> 13)) * 1274126177
    h = h ^ (h >> 16)
    return (h & 0xFFFFFF) / float(0x1000000)


def unit(v, axis=-1):
    v = np.asarray(v, float)
    return v / np.maximum(np.linalg.norm(v, axis=axis, keepdims=True), 1e-12)


def rot_normal_from_grid(P):
    """finite-difference normal of a (nu,nv,3) grid, direction = dP/du x dP/dv"""
    du = np.gradient(P, axis=0); dv = np.gradient(P, axis=1)
    return unit(np.cross(du, dv))


def add_grid(m, P, mat=0, drop=None, flip=False):
    """add a (nu,nv,3) grid as a smooth-shaded surface. drop = (nu-1,nv-1) bool of quads to omit."""
    nu, nv = P.shape[:2]
    V = P.reshape(-1, 3).astype(np.float32)
    F = grid_faces(nu, nv)
    if flip:
        F = F[:, ::-1]
    if drop is not None:
        i, j = np.meshgrid(np.arange(nu - 1), np.arange(nv - 1), indexing='ij')
        q = (i * (nv - 1) + j).ravel()
        keep_q = ~drop.ravel()
        nq = (nu - 1) * (nv - 1)
        # grid_faces orders: first all (a,b,c) tris of every quad then all (a,c,d)
        keep = np.concatenate([keep_q, keep_q])
        F = F[keep]
    N = vertex_normals(V, F)
    m.add(V, F, N, mat=mat)
    return len(F)


def add_strip(m, A, B, mat=0):
    """connect two polylines A,B (k,3) with a ribbon of quads"""
    k = len(A)
    V = np.concatenate([A, B]).astype(np.float32)
    i = np.arange(k - 1)
    F = np.concatenate([np.stack([i, i + 1, k + i + 1], 1), np.stack([i, k + i + 1, k + i], 1)])
    m.add(V, F, None, mat=mat, flat=True)


def sweep_rect(path, up, w, d, mat_mesh, mat=0, closed_ends=True):
    """rectangular-section beam along path (K,3). up = (K,3) unit vector (beam 'depth' direction), w,d scalars or (K,) arrays.
    cross-section: width w along (tangent x up), depth d along up."""
    K = len(path)
    T = unit(np.gradient(path, axis=0))
    side = unit(np.cross(T, up))
    up2 = unit(np.cross(side, T))
    w = np.broadcast_to(np.asarray(w, float), (K,))[:, None]
    d = np.broadcast_to(np.asarray(d, float), (K,))[:, None]
    c = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    ring = np.stack([path + side * (sx * w / 2) + up2 * (sy * d / 2) for sx, sy in c], 1)  # (K,4,3)
    V = ring.reshape(-1, 3).astype(np.float32)
    F = []
    for q in range(4):
        q2 = (q + 1) % 4
        a = np.arange(K - 1) * 4 + q; b = np.arange(K - 1) * 4 + q2
        F.append(np.stack([a, b, b + 4], 1)); F.append(np.stack([a, b + 4, a + 4], 1))
    if closed_ends:
        for k0, rev in ((0, False), (K - 1, True)):
            o = k0 * 4
            t1 = np.array([[o, o + 1, o + 2], [o, o + 2, o + 3]])
            F.append(t1[:, ::-1] if rev else t1)
    F = np.concatenate(F)
    mat_mesh.add(V, F, None, mat=mat, flat=True)


def revolve_pods(P, axis_dir, L, R, profile='drop', seg=14, rings=9):
    """many small revolved bodies. P (M,3) attach points; axis_dir (M,3) unit direction the pod extends along;
    L, R (M,) length & radius. profile 'drop' = rounded top (at P) narrowing to a point at the far end, with stepped rings.
    returns V,F (flat shading by caller)."""
    M = len(P)
    n = unit(axis_dir)
    ref = np.where(np.abs(n[:, 2:3]) < 0.9, np.array([[0, 0, 1.0]]), np.array([[1.0, 0, 0]]))
    u = unit(np.cross(n, ref)); v = np.cross(n, u)
    ang = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    ca, sa = np.cos(ang), np.sin(ang)
    t = np.linspace(0, 1, rings + 1)
    # radius profile with stepped shoulders (terraced pod): wide shoulder, then stepping in
    r_prof = (1 - t ** 1.35) ** 0.62
    steps = np.floor(t * 4) / 4.0
    r_prof = 0.55 * r_prof + 0.45 * (1 - steps) ** 0.8 * (1 - t) ** 0.3
    r_prof = np.clip(r_prof, 0.0, 1.0)
    r_prof[-1] = 0.0
    out = []
    ring_pts = []
    for i in range(rings + 1):
        c = P + n * (L * t[i])[:, None]
        rr = R * r_prof[i]
        ring_pts.append(c[:, None, :] + (u[:, None, :] * ca[None, :, None] + v[:, None, :] * sa[None, :, None]) * rr[:, None, None])
    ring_pts = np.stack(ring_pts, 1)   # (M, rings+1, seg, 3)
    V = ring_pts.reshape(-1, 3)
    per = (rings + 1) * seg
    idx = np.arange(seg); i2 = (idx + 1) % seg
    F = []
    for r in range(rings):
        a = r * seg + idx; b = r * seg + i2
        F.append(np.stack([a, b, b + seg], 1)); F.append(np.stack([a, b + seg, a + seg], 1))
    F = np.concatenate(F)
    off = (np.arange(M) * per)[:, None, None]
    Fall = (off + F[None]).reshape(-1, 3)
    return V.astype(np.float32), Fall


def ground_polar(excl, seed=7, R=11000., cx=0., cy=0., hscale=1.0, row_pitch=(205, 245), blk_pitch=170., hmul_fn=None):
    """convergent polar low-rise ground city (context only). excl(x,y)->bool mask of positions to leave EMPTY (under/inside the structure)."""
    from blocks import block_mesh
    rng = np.random.default_rng(seed)
    rows = []
    rg = 900.0
    while rg < R:
        dth = blk_pitch / rg
        th = np.arange(0, 2 * np.pi, dth) + rng.uniform(0, dth)
        rows.append((rg, th)); rg += rng.uniform(*row_pitch)
    GX = cx + np.concatenate([r * np.cos(t) for r, t in rows]); GY = cy + np.concatenate([r * np.sin(t) for r, t in rows])
    TH = np.concatenate([t for r, t in rows]); RR = np.concatenate([np.full(len(t), r) for r, t in rows])
    k = (~excl(GX, GY)) & (rng.random(len(GX)) > 0.08)
    GX, GY, TH, RR = GX[k], GY[k], TH[k], RR[k]
    Hg = 14 * np.exp(rng.normal(0, 0.45, len(GX))) * (1 + 2.6 * np.exp(-RR / 3500.)) * hscale
    radial = np.stack([-np.cos(TH), -np.sin(TH), np.zeros(len(GX))], 1)
    Vg, Fg = block_mesh(np.stack([GX, GY, np.zeros(len(GX))], 1), np.tile([0, 0, 1.0], (len(GX), 1)), radial,
                        rng.uniform(95, 150, len(GX)), rng.uniform(55, 90, len(GX)), Hg, 0.16 * Hg, rng.uniform(0.05, 0.25, len(GX)))
    return Vg, Fg, len(GX)


def mesh_report(mesh):
    V, F, N, M = mesh['V'], mesh['F'], mesh['N'], mesh['M']
    A = V[F[:, 0]].astype(np.float64); B = V[F[:, 1]].astype(np.float64); C = V[F[:, 2]].astype(np.float64)
    area = 0.5 * np.linalg.norm(np.cross(B - A, C - A), axis=1)
    rep = dict(tris=int(len(F)), verts=int(len(V)), nan_free=bool(np.isfinite(V).all()),
               degenerate_tris=int((area < 1e-6).sum()), index_in_range=bool(F.max() < len(V)),
               bbox_min=[round(float(x), 1) for x in V.min(0)], bbox_max=[round(float(x), 1) for x in V.max(0)],
               tris_by_material={int(k): int((M == k).sum()) for k in np.unique(M)})
    return rep


def revolve_drums(P, axis_dir, L, R, seg=20):
    """flat-bottomed, stepped drums (hanging district): 3 stepped cylinders, wide at the attachment, narrowing in steps. No taper to a point."""
    M = len(P); n = unit(axis_dir)
    ref = np.where(np.abs(n[:, 2:3]) < 0.9, np.array([[0, 0, 1.0]]), np.array([[1.0, 0, 0]]))
    u = unit(np.cross(n, ref)); v = np.cross(n, u)
    ang = np.linspace(0, 2 * np.pi, seg, endpoint=False); ca, sa = np.cos(ang), np.sin(ang)
    # (t, radius fraction) station list producing steps with small chamfers
    st = [(0.00, 1.00), (0.34, 1.00), (0.38, 0.80), (0.64, 0.80), (0.68, 0.58), (0.94, 0.58), (1.00, 0.46), (1.00, 0.0)]
    rings = []
    for t, rf in st:
        c = P + n * (L * t)[:, None]
        rings.append(c[:, None, :] + (u[:, None, :] * ca[None, :, None] + v[:, None, :] * sa[None, :, None]) * (R * rf)[:, None, None])
    rp = np.stack(rings, 1); V = rp.reshape(-1, 3); K = len(st); per = K * seg
    idx = np.arange(seg); i2 = (idx + 1) % seg; F = []
    for r in range(K - 1):
        a = r * seg + idx; b = r * seg + i2
        F.append(np.stack([a, b, b + seg], 1)); F.append(np.stack([a, b + seg, a + seg], 1))
    F = np.concatenate(F); off = (np.arange(M) * per)[:, None, None]
    return V.astype(np.float32), (off + F[None]).reshape(-1, 3)
