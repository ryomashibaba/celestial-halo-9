"""Software rasteriser for C55-A (NOT Blender). Painter's algorithm + heightfield sun shadow/AO + bloom.
Used only to look at the real mesh data; Blender (Cycles/EEVEE) renders are produced by blender_build.py."""
import numpy as np, time, json, sys
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage
from c55a_geom import normalize, smoothstep
import c55a_city as C

SUN = normalize(np.array([-0.80, -0.34, 0.40]))
SUN_COL = np.array([1.0, 0.80, 0.58]) * 2.7
SKY_AMB = np.array([0.30, 0.34, 0.60])
GND_AMB = np.array([0.40, 0.31, 0.26])
INT_AMB = np.array([0.24, 0.19, 0.16])
FOG_COOL = np.array([0.42, 0.36, 0.58])
FOG_WARM = np.array([1.00, 0.58, 0.36])

MAT_NAMES = list(C.MATERIALS.keys())
MAT_IDX = {k: i for i, k in enumerate(MAT_NAMES)}
MB = np.array([C.MATERIALS[k].get('base', (0, 0, 0)) for k in MAT_NAMES], float)
ME = np.array([C.MATERIALS[k].get('emit', (0, 0, 0)) for k in MAT_NAMES], float)
MA = np.array([C.MATERIALS[k].get('alpha', 1.0) for k in MAT_NAMES], float)
MS = np.array([C.MATERIALS[k].get('spec', 0.0) for k in MAT_NAMES], float)


def assemble(S, interior):
    tri, key, mid, bias, pid, dec = [], [], [], [], [], []
    for pi, p in enumerate(S.parts):
        if p['interior'] != interior:
            continue
        V = p['V'].astype(np.float64)
        F = p['F']
        T = V[F]
        tri.append(T)
        cen_ = T.mean(1)
        if p['key'] is not None:
            kk = p['key'].astype(np.float64)
        else:
            kk = cen_.copy()
            m_ = len(cen_) // 2 * 2
            kk[0:m_:2] = kk[1:m_:2] = (cen_[0:m_:2] + cen_[1:m_:2]) / 2
        key.append(kk)
        dec.append(np.full(len(F), p['key'] is not None))
        mid.append(np.full(len(F), MAT_IDX[p['mat']]))
        bias.append(np.full(len(F), p['bias']))
        pid.append(np.full(len(F), pi))
    A = dict(tri=np.concatenate(tri), key=np.concatenate(key), mid=np.concatenate(mid),
             bias=np.concatenate(bias), pid=np.concatenate(pid), decal=np.concatenate(dec))
    T = A['tri']
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    ar = np.linalg.norm(n, axis=1)
    A['nrm'] = n / np.maximum(ar, 1e-9)[:, None]
    A['cen'] = T.mean(1)
    A['area'] = ar / 2
    rng = np.random.default_rng(3)
    A['jit'] = 1 + 0.07 * (rng.random(len(T)) - 0.5) * 2
    return A


# ---------------- heightfield for shadows / AO
HF_CELL = 40.0
HF_N = 300
HF_X0 = -6000.0


def make_heightfield(S):
    hf = np.zeros((HF_N, HF_N))
    xs = HF_X0 + (np.arange(HF_N) + 0.5) * HF_CELL
    X, Y = np.meshgrid(xs, xs, indexing='ij')
    hf[:] = np.maximum(C.ground_h(X, Y), 0)
    for p in S.parts:
        if not p['massif']:
            continue
        V = p['V']
        ix = np.clip(((V[:, 0] - HF_X0) / HF_CELL).astype(int), 0, HF_N - 1)
        iy = np.clip(((V[:, 1] - HF_X0) / HF_CELL).astype(int), 0, HF_N - 1)
        np.maximum.at(hf, (ix, iy), V[:, 2])
    hf = ndimage.maximum_filter(hf, size=3)
    return hf


def hf_at(hf, x, y):
    ix = ((x - HF_X0) / HF_CELL).astype(int)
    iy = ((y - HF_X0) / HF_CELL).astype(int)
    ok = (ix >= 0) & (ix < HF_N) & (iy >= 0) & (iy < HF_N)
    out = np.zeros(len(x))
    out[ok] = hf[ix[ok], iy[ok]]
    return out


def compute_lighting(A, hf, chunk=60000):
    nF = len(A['mid'])
    jit = A['jit'].copy()
    flat_mats = [MAT_IDX['ground'], MAT_IDX['water']]
    jit[np.isin(A['mid'], flat_mats)] = 1.0
    base = MB[A['mid']] * jit[:, None]
    lit = np.zeros((2, nF, 3))
    need = np.where(base.sum(1) > 0)[0]
    dirs = np.array([[np.cos(a), np.sin(a)] for a in np.linspace(0, 2 * np.pi, 16, endpoint=False)])
    dists = np.array([160, 380, 800, 1500, 2600.0])
    el = SUN[2] / np.hypot(SUN[0], SUN[1])
    sdir = SUN[:2] / np.hypot(SUN[0], SUN[1])
    steps = 150.0 * 1.2 ** np.arange(22)
    for c0 in range(0, len(need), chunk):
        idx = need[c0:c0 + chunk]
        cen = A['cen'][idx]
        n0 = A['nrm'][idx]
        p0 = cen + SUN[None] * 6.0
        occ = np.zeros(len(idx))
        for d in steps:
            x = p0[:, 0] + sdir[0] * d
            y = p0[:, 1] + sdir[1] * d
            h = hf_at(hf, x, y)
            zr = p0[:, 2] + d * el
            occ = np.maximum(occ, np.clip((h - zr - 25.0 - 0.10 * d) / 90.0, 0, 1))
        vis = 1 - occ
        qs = []
        for di, dv in enumerate(dirs):
            for ki, dd in enumerate(dists):
                h = hf_at(hf, cen[:, 0] + dv[0] * dd, cen[:, 1] + dv[1] * dd)
                qs.append(np.stack([np.full(len(idx), dv[0] * dd), np.full(len(idx), dv[1] * dd), h - cen[:, 2] - 20.0], 1))
        Q = np.stack(qs, 1).reshape(len(idx), len(dirs), len(dists), 3)
        Qn = Q / np.maximum(np.linalg.norm(Q, axis=3, keepdims=True), 1e-6)
        above = (Q[..., 2] > 0)
        for o, sgn in enumerate((1.0, -1.0)):
            n = n0 * sgn
            c = np.maximum(0, np.einsum('nj,ndkj->ndk', n, Qn)) * above
            occd = c.max(2).mean(1)
            ao = 1 - 0.85 * np.clip(occd * 1.15, 0, 1)
            hemi = (0.5 + 0.5 * n[:, 2:3])
            amb = GND_AMB[None] * (1 - hemi) + SKY_AMB[None] * hemi
            ndl = np.maximum(0, n @ SUN)
            col = amb * (0.62 * ao)[:, None] + SUN_COL[None] * (ndl * vis)[:, None]
            lit[o, idx] = col * base[idx]
    return lit


def compute_lighting_interior(A):
    nF = len(A['mid'])
    base = MB[A['mid']] * A['jit'][:, None]
    lit = np.zeros((2, nF, 3))
    z = A['cen'][:, 2]
    for o, sgn in enumerate((1.0, -1.0)):
        n = A['nrm'] * sgn
        up = 0.5 + 0.5 * n[:, 2]
        amb = INT_AMB[None] * (0.55 + 0.55 * np.clip(z / 420.0, 0, 1))[:, None] * (0.7 + 0.5 * up)[:, None]
        lit[o] = amb * base
    return lit


# ---------------- camera
class Cam:
    def __init__(self, pos, target, hfov, W, H, up=(0, 0, 1.0)):
        self.pos = np.array(pos, float)
        f = normalize(np.array(target, float) - self.pos)
        r = normalize(np.cross(f, up))
        u = np.cross(r, f)
        self.f, self.r, self.u = f, r, u
        self.W, self.H = W, H
        self.fpx = (W / 2) / np.tan(np.radians(hfov) / 2)

    def to_cam(self, P):
        d = P - self.pos
        return np.stack([d @ self.r, d @ self.u, d @ self.f], -1)

    def project(self, Pc):
        z = np.maximum(Pc[..., 2], 1e-6)
        return np.stack([self.W / 2 + Pc[..., 0] / z * self.fpx, self.H / 2 - Pc[..., 1] / z * self.fpx], -1)

    def ray_dirs(self):
        xs = (np.arange(self.W) + 0.5 - self.W / 2) / self.fpx
        ys = -(np.arange(self.H) + 0.5 - self.H / 2) / self.fpx
        X, Y = np.meshgrid(xs, ys)
        d = self.f[None, None] + X[..., None] * self.r[None, None] + Y[..., None] * self.u[None, None]
        return d / np.linalg.norm(d, axis=-1, keepdims=True)


def sky_image(cam, interior=False, seed=5):
    d = cam.ray_dirs()
    e = d[..., 2]
    sd = d @ SUN
    if interior:
        return np.full((cam.H, cam.W, 3), 0.02)
    hor = np.array([1.00, 0.52, 0.30]) * 1.0
    mid = np.array([0.50, 0.28, 0.48])
    top = np.array([0.035, 0.05, 0.20])
    t1 = np.clip(e / 0.35, 0, 1)[..., None]
    t2 = np.clip((e - 0.2) / 0.8, 0, 1)[..., None] ** 0.7
    col = hor * (1 - t1) + mid * t1
    col = col * (1 - t2) + top * t2
    below = np.clip(-e * 6, 0, 1)[..., None]
    col = col * (1 - below) + np.array([0.35, 0.28, 0.30]) * below
    az = np.arctan2(d[..., 1], d[..., 0])
    glow = np.clip(sd, 0, 1)
    col = col + np.array([1.0, 0.62, 0.30])[None, None] * (glow ** 6)[..., None] * 0.9
    col = col + np.array([1.0, 0.85, 0.6])[None, None] * (glow ** 90)[..., None] * 3.5
    disc = (sd > 0.99965)[..., None]
    col = np.where(disc, np.array([9.0, 7.0, 4.5]), col)
    # cloud bands
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 6.28, 8)
    cl = (np.sin(az * 6 + ph[0] + 3 * e) * np.sin(az * 11 + ph[1] - 5 * e) + 0.6 * np.sin(az * 19 + ph[2] + 9 * e) * np.sin(az * 3.3 + ph[3]))
    band = np.exp(-((e - 0.16) / 0.07) ** 2) + 0.7 * np.exp(-((e - 0.36) / 0.09) ** 2)
    cm = np.clip(cl * 0.5 + 0.35, 0, 1) * band
    ccol = np.array([0.95, 0.60, 0.52]) * (0.5 + 0.9 * np.clip(sd, 0, 1) ** 2)[..., None] + np.array([0.25, 0.22, 0.42])
    col = col * (1 - 0.55 * cm[..., None]) + ccol * (0.55 * cm[..., None])
    # stars
    st = rng.random((cam.H, cam.W)) > 0.9993
    col = col + (st * np.clip((e - 0.3) * 2, 0, 1))[..., None] * 0.8
    return col


def sky_grad(d):
    e = d[..., 2]
    sd = np.clip(d @ SUN, 0, 1)
    hor = np.array([1.00, 0.52, 0.30]) * 1.0
    mid = np.array([0.50, 0.28, 0.48])
    top = np.array([0.035, 0.05, 0.20])
    t1 = np.clip(e / 0.35, 0, 1)[..., None]
    t2 = np.clip((e - 0.2) / 0.8, 0, 1)[..., None] ** 0.7
    col = hor * (1 - t1) + mid * t1
    col = col * (1 - t2) + top * t2
    col = col + np.array([1.0, 0.62, 0.30]) * (sd ** 6)[..., None] * 0.9
    return col


def aces(x):
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    return np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)


def to_srgb(c, exposure):
    return np.clip(aces(np.maximum(c, 0) * exposure) ** (1 / 2.2), 0, 1)


def clip_near(Pc, near):
    out = []
    n = len(Pc)
    for i in range(n):
        a, b = Pc[i], Pc[(i + 1) % n]
        ina, inb = a[2] >= near, b[2] >= near
        if ina:
            out.append(a)
        if ina != inb:
            t = (near - a[2]) / (b[2] - a[2])
            out.append(a + (b - a) * t)
    return out


def render(A, lit, cam, exposure=1.0, SS=2, interior=False, fog_d=62000.0, bloom=1.0, label=''):
    t0 = time.time()
    W, H = cam.W, cam.H
    # supersampled camera
    scam = Cam(cam.pos, cam.pos + cam.f, 90, W * SS, H * SS)
    scam.r, scam.u, scam.f = cam.r, cam.u, cam.f
    scam.fpx = cam.fpx * SS
    sky = sky_image(scam, interior)
    T = A['tri']
    nF = len(T)
    cen = A['cen']
    key = A['key']
    nrm = A['nrm']
    to_cam = cam.pos[None] - cen
    dist = np.linalg.norm(to_cam, axis=1)
    facing = np.sum(nrm * to_cam, 1) >= 0
    L = np.where(facing[:, None], lit[0], lit[1])
    # specular (cheap): blinn with sun
    vdir = to_cam / np.maximum(dist, 1e-6)[:, None]
    nn = np.where(facing[:, None], nrm, -nrm)
    hh = normalize(vdir + SUN[None])
    sp = np.maximum(0, np.sum(nn * hh, 1)) ** 40 * MS[A['mid']]
    col = L + sp[:, None] * SUN_COL[None] * 0.35 + ME[A['mid']]
    wm = A['mid'] == MAT_IDX['water']
    if wm.any():
        nw = nn[wm]
        vw = vdir[wm]
        ndv = np.abs(np.sum(nw * vw, 1))
        rz = 2 * ndv[:, None] * nw - vw
        rcol = sky_grad(rz)
        fres = 0.04 + 0.96 * (1 - ndv) ** 4
        glit = np.maximum(0, np.sum(normalize(rz) * SUN[None], 1)) ** 60 * 3.0
        col[wm] = MB[A['mid'][wm]] * 0.9 + fres[:, None] * rcol * 0.55 + glit[:, None] * SUN_COL[None] * 0.25
    # fog
    if not interior:
        fd = np.linalg.norm(key - cam.pos[None], axis=1)
        dens = 0.45 + 0.55 * np.exp(-np.maximum(cen[:, 2], 0) / 2600.0)
        ff = 1 - np.exp(-fd / fog_d * dens * 1.1)
        sdv = np.clip(np.sum(-vdir * SUN[None], 1), 0, 1) ** 2
        fc = FOG_COOL[None] * (1 - sdv)[:, None] + FOG_WARM[None] * sdv[:, None]
        em = ME[A['mid']].max(1) > 0
        ffe = np.where(em, ff * 0.55, ff)
        col = col * (1 - ffe)[:, None] + fc * ffe[:, None] * 0.95
    c8 = (to_srgb(col, exposure) * 255).astype(np.uint8)
    emis = ME[A['mid']]
    gl = np.clip(emis / 3.0, 0, 1)
    gl8 = (np.clip(gl * (1 - 0.5 * (0 if interior else 1) * 0), 0, 1) ** (1 / 1.8) * 255).astype(np.uint8)
    glow_on = emis.max(1) > 0.9
    alpha = MA[A['mid']]
    # depth keys / sort
    kd = np.linalg.norm(key - cam.pos[None], axis=1)
    bi = A['bias']
    eff = np.where(bi >= 0, np.minimum(bi, 0.02 * kd), -np.minimum(-bi, 0.06 * kd))
    sortkey = kd - eff - 0.1 * A['decal']
    # project
    Pc = cam.to_cam(T.reshape(-1, 3)).reshape(nF, 3, 3)
    near = 0.4
    zmin = Pc[..., 2].min(1)
    zmax = Pc[..., 2].max(1)
    vis = zmax > near
    full = zmin >= near
    S2 = SS
    scr = np.zeros((nF, 3, 2))
    zz = np.maximum(Pc[..., 2], 1e-6)
    scr[..., 0] = (W / 2 + Pc[..., 0] / zz * cam.fpx) * S2
    scr[..., 1] = (H / 2 - Pc[..., 1] / zz * cam.fpx) * S2
    bx0 = scr[..., 0].min(1); bx1 = scr[..., 0].max(1)
    by0 = scr[..., 1].min(1); by1 = scr[..., 1].max(1)
    onscreen = full & (bx1 > 0) & (bx0 < W * S2) & (by1 > 0) & (by0 < H * S2)
    # tiny sub-pixel triangles still drawn (emissive points)
    straddle = vis & (~full)
    order = np.argsort(-sortkey)
    img = Image.fromarray((np.clip(sky, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8)) if False else None
    skyc = to_srgb(sky, exposure)
    img = Image.fromarray((skyc * 255).astype(np.uint8), 'RGB')
    glw = Image.new('RGB', (W * S2, H * S2), (0, 0, 0))
    gsky = np.clip((sky - 3.0) / 6.0, 0, 1)
    glw = Image.fromarray((gsky * 255).astype(np.uint8), 'RGB')
    d1 = ImageDraw.Draw(img, 'RGBA')
    d2 = ImageDraw.Draw(glw, 'RGB')
    scr_l = scr.reshape(nF, 6).tolist()
    c8l = c8.tolist()
    g8l = gl8.tolist()
    al = alpha.tolist()
    on = onscreen.tolist()
    st = straddle.tolist()
    ge = glow_on.tolist()
    ndraw = 0
    for i in order.tolist():
        if on[i]:
            p = scr_l[i]
            c = c8l[i]
            a = al[i]
            if a < 1.0:
                d1.polygon(p, fill=(c[0], c[1], c[2], int(a * 255)))
            else:
                d1.polygon(p, fill=(c[0], c[1], c[2]))
                if ge[i]:
                    g = g8l[i]
                    d2.polygon(p, fill=(g[0], g[1], g[2]))
                else:
                    d2.polygon(p, fill=(0, 0, 0))
            ndraw += 1
        elif st[i]:
            poly = clip_near(Pc[i], near)
            if len(poly) >= 3:
                poly = np.array(poly)
                q = cam.project(poly)
                q = (q * S2).ravel().tolist()
                c = c8l[i]
                a = al[i]
                if a < 1.0:
                    d1.polygon(q, fill=(c[0], c[1], c[2], int(a * 255)))
                else:
                    d1.polygon(q, fill=(c[0], c[1], c[2]))
                    if ge[i]:
                        g = g8l[i]
                        d2.polygon(q, fill=(g[0], g[1], g[2]))
                    else:
                        d2.polygon(q, fill=(0, 0, 0))
                ndraw += 1
    # downsample
    out = img.resize((W, H), Image.LANCZOS)
    gl_small = glw.resize((W, H), Image.BOX)
    b1 = gl_small.filter(ImageFilter.GaussianBlur(max(2, W / 320)))
    b2 = gl_small.filter(ImageFilter.GaussianBlur(max(6, W / 90)))
    b3 = gl_small.filter(ImageFilter.GaussianBlur(max(14, W / 35)))
    o = np.asarray(out).astype(np.float32) / 255
    g = (np.asarray(b1).astype(np.float32) * 0.5 + np.asarray(b2).astype(np.float32) * 0.8 + np.asarray(b3).astype(np.float32) * 0.9) / 255
    o = 1 - (1 - o) * (1 - np.clip(g * 0.9 * bloom, 0, 1))
    # vignette + subtle grade
    yy, xx = np.mgrid[0:H, 0:W]
    vg = 1 - 0.28 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.2
    o = o * vg[..., None]
    o = np.clip(o, 0, 1)
    res = Image.fromarray((o * 255).astype(np.uint8), 'RGB')
    skyd = np.asarray(Image.fromarray((skyc * 255).astype(np.uint8)).resize((W, H), Image.BOX)).astype(np.int16)
    diff = np.abs(np.asarray(out).astype(np.int16) - skyd).sum(2)
    cover = float((diff > 12).mean())
    lum = float((o * np.array([0.2126, 0.7152, 0.0722])).sum(2).mean())
    return res, dict(label=label, faces_drawn=ndraw, seconds=round(time.time() - t0, 1), geometry_coverage=round(cover, 3),
                     mean_luma=round(lum, 3))
