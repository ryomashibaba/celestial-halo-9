"""C55-A geometry helpers (pure numpy, no bpy). Units: metres. X east, Y north, Z up."""
import numpy as np


def smoothstep(a, b, x):
    t = np.clip((np.asarray(x, dtype=float) - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def normalize(v, axis=-1):
    n = np.linalg.norm(v, axis=axis, keepdims=True)
    return v / np.maximum(n, 1e-9)


def rot_axis(axis, ang):
    a = np.asarray(axis, float)
    a = a / np.linalg.norm(a)
    x, y, z = a
    c, s = np.cos(ang), np.sin(ang)
    C = 1 - c
    return np.array([[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
                     [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                     [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])


def grid_faces(nu, nv):
    i = np.arange(nu - 1)[:, None]
    j = np.arange(nv - 1)[None, :]
    a = i * nv + j
    b = (i + 1) * nv + j
    c = (i + 1) * nv + j + 1
    d = i * nv + j + 1
    t1 = np.stack([a, b, c], -1)
    t2 = np.stack([a, c, d], -1)
    return np.stack([t1, t2], axis=2).reshape(-1, 3).astype(np.int32)


def grid_mesh(P):
    P = np.asarray(P, float)
    nu, nv = P.shape[:2]
    return P.reshape(-1, 3), grid_faces(nu, nv)


def face_seg(nu, nv):
    """for grid_faces ordering -> (i index, j index) per face"""
    q = np.arange((nu - 1) * (nv - 1) * 2) // 2
    return q // (nv - 1), q % (nv - 1)


def sub_mesh(V, F, mask):
    Fm = F[mask]
    if len(Fm) == 0:
        return V[:0], Fm
    used, inv = np.unique(Fm, return_inverse=True)
    return V[used], inv.reshape(-1, 3).astype(np.int32)


def merge(meshes):
    Vs, Fs, off = [], [], 0
    for V, F in meshes:
        if len(F) == 0:
            continue
        Vs.append(V)
        Fs.append(F + off)
        off += len(V)
    if not Vs:
        return np.zeros((0, 3)), np.zeros((0, 3), np.int32)
    return np.vstack(Vs), np.vstack(Fs).astype(np.int32)


_BV = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]], float) * 0.5
_BF = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4],
                [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]], np.int32)


def boxes(centers, sizes, R=None):
    """vectorised boxes. centers (n,3); sizes (n,3) or (3,); R optional (3,3) or (n,3,3)"""
    centers = np.atleast_2d(np.asarray(centers, float))
    n = len(centers)
    sizes = np.broadcast_to(np.asarray(sizes, float), (n, 3))
    V = _BV[None] * sizes[:, None, :]
    if R is not None:
        R = np.asarray(R, float)
        if R.ndim == 2:
            V = V @ R.T
        else:
            V = np.einsum('nij,nkj->nki', R, V)
    V = V + centers[:, None, :]
    F = (_BF[None] + (np.arange(n) * 8)[:, None, None]).reshape(-1, 3)
    return V.reshape(-1, 3), F.astype(np.int32)


def revolve_grid(profile, n=64, a0=0.0, a1=2 * np.pi):
    prof = np.asarray(profile, float)
    th = np.linspace(a0, a1, n + 1)
    P = np.zeros((n + 1, len(prof), 3))
    P[..., 0] = np.cos(th)[:, None] * prof[None, :, 0]
    P[..., 1] = np.sin(th)[:, None] * prof[None, :, 0]
    P[..., 2] = prof[None, :, 1]
    return P


def sweep_grid(path, section, N=None, B=None, closed=True, up=(0, 0, 1)):
    path = np.asarray(path, float)
    T = normalize(np.gradient(path, axis=0))
    if N is None:
        N = normalize(np.cross(np.asarray(up, float), T))
        B = np.cross(T, N)
    sec = np.asarray(section, float)
    if closed:
        sec = np.vstack([sec, sec[:1]])
    return path[:, None, :] + sec[None, :, 0:1] * N[:, None, :] + sec[None, :, 1:2] * B[:, None, :]


def bilerp(c00, c10, c11, c01, u, v):
    """corner arrays (...,3); u,v (...) -> point"""
    u = u[..., None]
    v = v[..., None]
    return (c00 * (1 - u) * (1 - v) + c10 * u * (1 - v) + c11 * u * v + c01 * (1 - u) * v)


def quad_decals(P, jcols, u_rng, v_rng, offset, ref, keep=None, rng=None, nrep=1):
    """Create small quads inside selected grid cells of P (nu,nv,3).
    jcols: list of j (cell column) indices; u_rng,v_rng: list of (a,b) sub-ranges per decal;
    offset: metres along normal oriented toward ref(centroids)->(n,3) direction.
    keep: probability a decal exists (array-able). returns V,F,keyPos(per face)."""
    nu, nv = P.shape[:2]
    jcols = np.asarray(jcols, int)
    ii, jj = np.meshgrid(np.arange(nu - 1), jcols, indexing='ij')
    ii = ii.ravel()
    jj = jj.ravel()
    c00 = P[ii, jj]
    c10 = P[ii + 1, jj]
    c11 = P[ii + 1, jj + 1]
    c01 = P[ii, jj + 1]
    cen = (c00 + c10 + c11 + c01) / 4
    nrm = normalize(np.cross(c10 - c00, c01 - c00))
    d = ref(cen)
    sgn = np.sign(np.sum(nrm * d, axis=1))
    sgn[sgn == 0] = 1
    nrm = nrm * sgn[:, None]
    Vs, Fs, Ks = [], [], []
    off = 0
    for (ua, ub) in u_rng:
        for (va, vb) in v_rng:
            if keep is None:
                m = np.ones(len(ii), bool)
            else:
                pk = keep(cen) if callable(keep) else keep
                m = rng.random(len(ii)) < pk
            if not m.any():
                continue
            a = c00[m]; b = c10[m]; c = c11[m]; e = c01[m]; nn = nrm[m]
            k = len(a)
            ones = np.ones(k)
            p0 = bilerp(a, b, c, e, ua * ones, va * ones) + nn * offset
            p1 = bilerp(a, b, c, e, ub * ones, va * ones) + nn * offset
            p2 = bilerp(a, b, c, e, ub * ones, vb * ones) + nn * offset
            p3 = bilerp(a, b, c, e, ua * ones, vb * ones) + nn * offset
            V = np.stack([p0, p1, p2, p3], 1).reshape(-1, 3)
            base = (np.arange(k) * 4)
            F = np.stack([np.stack([base, base + 1, base + 2], 1),
                          np.stack([base, base + 2, base + 3], 1)], 1).reshape(-1, 3)
            Vs.append(V)
            Fs.append(F + off)
            off += len(V)
            Ks.append(np.repeat(((2 * c00 + c10 + 2 * c11 + c01) / 6)[m], 2, axis=0))
    if not Vs:
        return np.zeros((0, 3)), np.zeros((0, 3), np.int32), np.zeros((0, 3))
    return np.vstack(Vs), np.vstack(Fs).astype(np.int32), np.vstack(Ks)


class Scene:
    def __init__(self):
        self.parts = []

    def add(self, name, coll, mat, V, F, bias=0.0, interior=False, massif=False, key=None, context=False):
        V = np.asarray(V, dtype=np.float32).reshape(-1, 3)
        F = np.asarray(F, dtype=np.int32).reshape(-1, 3)
        if len(F) == 0:
            return
        if key is not None:
            key = np.asarray(key, dtype=np.float32).reshape(-1, 3)
            assert len(key) == len(F), (name, len(key), len(F))
        # drop zero-area (degenerate) triangles: sphere/revolve poles, blade tips, collapsed strips
        T = V.astype(np.float64)[F]
        ar = np.linalg.norm(np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]), axis=1)
        okf = ar > 1e-6
        if not okf.all():
            F = F[okf]
            if key is not None:
                key = key[okf]
            if len(F) == 0:
                return
        self.parts.append(dict(name=name, coll=coll, mat=mat, V=V, F=F, bias=bias,
                               interior=interior, massif=massif, key=key, context=context))

    def stats(self):
        out = {}
        for p in self.parts:
            c = out.setdefault(p['coll'], dict(parts=0, verts=0, tris=0))
            c['parts'] += 1
            c['verts'] += len(p['V'])
            c['tris'] += len(p['F'])
        return out


def octa(centers, r):
    centers = np.atleast_2d(np.asarray(centers, float))
    n = len(centers)
    r = np.broadcast_to(np.asarray(r, float), (n,))
    base = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], float)
    Fb = np.array([[0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4], [2, 0, 5], [1, 2, 5], [3, 1, 5], [0, 3, 5]], np.int32)
    V = base[None] * r[:, None, None] + centers[:, None, :]
    F = Fb[None] + (np.arange(n) * 6)[:, None, None]
    return V.reshape(-1, 3), F.reshape(-1, 3).astype(np.int32)


def people_quads(px, py, pz, h=1.85, w=0.9):
    n = len(px)
    qa = []
    for ang in (0.0, np.pi / 2):
        d = np.array([np.cos(ang), np.sin(ang), 0.0])
        v = np.zeros((n, 4, 3))
        base = np.stack([px, py, pz], 1)
        v[:, 0] = base - d * w / 2
        v[:, 1] = base + d * w / 2
        v[:, 2] = base + d * w / 2 + [0, 0, h]
        v[:, 3] = base - d * w / 2 + [0, 0, h]
        qa.append(v)
    v = np.concatenate(qa)
    m = len(v)
    b = np.arange(m) * 4
    F = np.stack([np.stack([b, b + 1, b + 2], 1), np.stack([b, b + 2, b + 3], 1)], 1).reshape(-1, 3)
    return v.reshape(-1, 3), F.astype(np.int32)
