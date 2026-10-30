"""E-A 《地返し・開格子 / TERRA-TURN OPEN LATTICE》 — fundamental redesign of D1.
Kept from D1: the city ground is ONE continuous surface: back ground -> ramp -> crest (high-altitude city) -> lip, cavity side = ceiling-world.
Changed: (1) section = clothoid (railway easement) not a log-spiral; (2) the skin is an OPEN DIAGRID: ribs + recessed panels, cells dissolve toward the
crest so the interior city is visible through the structure (no smooth 'mountain mass', no contour ledges, no towers on the ridge);
(3) cavity-side streets are HELICAL terraced bands (street rifling) instead of boxes; (4) hanging districts grow from lattice NODES;
(5) two curls of different size/handedness-offset, staggered along the axis (not a single bump).
Convention: shell mid-surface S(p,s); N_L = left-of-path normal = EXTERIOR face; the opposite (R) face is the cavity / ceiling world."""
import sys, time, numpy as np
from lib_e import *
from ea_profile import profile

PR = None


def prof(sc, ds):
    s, u, z, ph = profile(ds=3.0)
    stride = max(int(ds / 3.0), 1)
    return s[::stride] * sc, u[::stride] * sc, z[::stride] * sc, ph[::stride]


CURLS = [
    dict(name='A', front=268., root=(-2150., 3300.), Lp=6800., sc=0.74, bend=500., seed=21, D=470.),
    dict(name='B', front=272., root=(3600., 2500.), Lp=4300., sc=0.56, bend=-300., seed=22, D=400.),
]


def build_curl(m, c, ds=26.0, log=print):
    rng = np.random.default_rng(c['seed'])
    s_, u_, z_, ph_ = prof(c['sc'], ds)
    ns = len(s_); npn = int(c['Lp'] / ds) + 1
    p = np.linspace(0, c['Lp'], npn); q = p / c['Lp']
    env = np.clip(np.sin(np.pi * q), 0, 1) ** 0.55
    f = np.array([np.cos(np.radians(c['front'])), np.sin(np.radians(c['front'])), 0.0])
    a = np.array([-f[1], f[0], 0.0]); ez = np.array([0, 0, 1.0])
    root = np.array([c['root'][0], c['root'][1], 0.0])
    U = u_[None, :] * env[:, None] + (c['bend'] * (q - 0.5) ** 2 * 4 - c['bend'] * 0.25 * 0)[:, None]
    Z = z_[None, :] * env[:, None]
    S = root[None, None, :] + a[None, None, :] * (p - c['Lp'] / 2)[:, None, None] + f[None, None, :] * U[..., None] + ez[None, None, :] * Z[..., None]
    # normal (left of path = exterior)
    dp = np.gradient(S, axis=0); dsd = np.gradient(S, axis=1)
    NL = unit(np.cross(dsd, dp))
    # orient: at the root portion (small s) the exterior must point up
    if NL[npn // 2, 4, 2] < 0: NL = -NL
    tk = (380.0 * c['sc'] / 0.74) * (0.45 + 0.55 * env)[:, None] * smooth(0, 700, s_)[None, :] * np.ones((1, ns))
    S = S + NL * (tk / 2)[..., None]        # cavity-side (R) face = the clothoid ground path itself; exterior face = path + thickness
    pm = p[:, None] * np.ones((1, ns)); sm = s_[None, :] * np.ones((npn, 1))
    D = c['D']
    fa = ((pm - sm) / D) % 1.0; fb = ((pm + sm) / D) % 1.0
    db = np.minimum(np.minimum(fa, 1 - fa), np.minimum(fb, 1 - fb))
    # ---- exterior relief: recessed panels framed by ribs, fine louvres
    recess = -42.0 * smooth(0.06, 0.26, db)
    louv = -7.0 * pulse((pm / 54.0) % 1.0, 0.42)
    hL = (recess + louv) * smooth(0, 500, sm) * smooth(0.0, 0.05, q)[:, None] * smooth(0.0, 0.05, 1 - q)[:, None]
    # ---- cavity-side relief: helical terraced streets + pockets
    xi = (pm - 0.62 * sm)
    fr = (xi / 170.0) % 1.0
    band = 12.0 * np.minimum(stair(fr * 3.0, 0.55), 3.0)
    pk = smooth(0.0, 0.2, 0.5 - np.abs(((xi / 56.0) % 1.0) - 0.5)) * smooth(0.0, 0.2, 0.5 - np.abs((((pm + 0.62 * sm) / 70.0) % 1.0) - 0.5))
    pocket = -12.0 * pk * (hash2(np.floor(xi / 56.0), np.floor((pm + 0.62 * sm) / 70.0), c['seed']) < 0.33)
    hR = (band + pocket) * smooth(0, 500, sm) * smooth(0.0, 0.05, q)[:, None] * smooth(0.0, 0.05, 1 - q)[:, None]
    PL = S + NL * (tk / 2 + hL)[..., None]          # exterior face
    PR_ = S - NL * (tk / 2 + hR)[..., None]         # cavity face
    # ---- open cells: dissolve toward the crest / lip
    ca = np.floor((pm - sm) / D); cb = np.floor((pm + sm) / D)
    cpm = 0.25 * (pm[:-1, :-1] + pm[1:, :-1] + pm[:-1, 1:] + pm[1:, 1:]); csm = 0.25 * (sm[:-1, :-1] + sm[1:, :-1] + sm[:-1, 1:] + sm[1:, 1:])
    cia = np.floor((cpm - csm) / D); cib = np.floor((cpm + csm) / D)
    sf = csm / s_[-1]
    openp = 0.82 * smooth(0.36, 0.78, sf) * smooth(0.06, 0.18, cpm / c['Lp']) * smooth(0.06, 0.18, 1 - cpm / c['Lp'])
    drop = hash2(cia, cib, c['seed'] + 3) < openp
    # keep the root/ground portion fully closed
    drop &= (csm > 1500)
    nt = add_grid(m, PL, mat=0, drop=drop); nt += add_grid(m, PR_, mat=1, drop=drop)
    # lip edge strip + end seams
    add_strip(m, PL[:, -1], PR_[:, -1], mat=0)
    # ---- ribs (diagrid)
    nrib = 0; nodes = []
    for sgn in (+1, -1):
        kmin = int(np.floor(((0 - sgn * s_[-1]) / D))) - 1; kmax = int(np.ceil((c['Lp'] - sgn * 0) / D)) + 1
        for k in range(kmin, kmax + 1):
            c0 = k * D
            pp = c0 + sgn * s_
            ok = (pp > 0.03 * c['Lp']) & (pp < 0.97 * c['Lp']) & (s_ > 120)
            if ok.sum() < 6: continue
            ii = np.nonzero(ok)[0]
            ip = np.interp(pp[ii], p, np.arange(npn))
            from scipy.ndimage import map_coordinates
            coords = np.stack([ip, ii.astype(float)])
            path = np.stack([map_coordinates(S[..., d], coords, order=1) for d in range(3)], 1)
            nrm = np.stack([map_coordinates(NL[..., d], coords, order=1) for d in range(3)], 1)
            tkk = map_coordinates(tk, coords, order=1)
            sweep_rect(path, unit(nrm), 70.0 * c['sc'] / 0.74 + 10, tkk + 100.0, m, mat=0, closed_ends=True); nrib += 1
    # nodes of the lattice (intersections) on the cavity side: hanging districts grow along the cavity normal (their local 'up' = ceiling-world gravity)
    nn = 0
    ia = np.arange(int(0.6 * (ns)), ns - 4)    # profile samples in the crest/lip zone only
    PP = []; DD = []; LL = []; RR = []
    for ca_ in range(int(-s_[-1] / D) - 1, int((c['Lp'] + s_[-1]) / D) + 2):
        for cb_ in range(int(-s_[-1] / D) - 1, int((c['Lp'] + s_[-1]) / D) + 2):
            pn = (ca_ + cb_) * D / 2 * 1.0 + 0.0; sn = (cb_ - ca_) * D / 2 * 1.0
            # node where (p - s)/D = ca and (p + s)/D = cb  => p=(ca+cb)D/2, s=(cb-ca)D/2
            if not (0.12 * c['Lp'] < pn < 0.88 * c['Lp']) or not (0.56 * s_[-1] < sn < 0.93 * s_[-1]): continue
            if hash2(ca_, cb_, c['seed'] + 7) > 0.55: continue
            ip = np.interp(pn, p, np.arange(npn)); iss = np.interp(sn, s_, np.arange(ns))
            co = np.array([[ip], [iss]])
            from scipy.ndimage import map_coordinates
            P0 = np.array([map_coordinates(S[..., d], co, order=1)[0] for d in range(3)])
            n0 = np.array([map_coordinates(NL[..., d], co, order=1)[0] for d in range(3)])
            t0 = float(map_coordinates(tk, co, order=1)[0])
            PP.append(P0 - unit(n0) * (t0 / 2 + 20)); DD.append(-unit(n0)); LL.append(rng.uniform(180, 520) * c['sc'] / 0.74); RR.append(rng.uniform(70, 170) * c['sc'] / 0.74)
    if PP:
        PP = np.array(PP); DD = np.array(DD); LL = np.array(LL); RR = np.array(RR)
        endz = PP[:, 2] + DD[:, 2] * LL
        okp = endz > 220
        Vp, Fp = revolve_pods(PP[okp], DD[okp], LL[okp], RR[okp], seg=18, rings=10)
        m.add(Vp, Fp, None, mat=7, flat=True); nn = int(okp.sum())
    log(f"  curl {c['name']}: grid {npn}x{ns} open-cells={int(drop.sum())}/{drop.size} ribs={nrib} nodes={nn} tris={nt}")
    return dict(S=S, NL=NL, tk=tk, p=p, s=s_, front=f, a=a, root=root, drop=drop), nt


def build(ds=26.0, seed=7, log=print, ground=True):
    t0 = time.time(); m = Mesh(); info = {}; curls = {}; tri = 0
    for c in CURLS:
        d, nt = build_curl(m, c, ds, log); curls[c['name']] = d; tri += nt
    ng = 0
    if ground:
        from scipy.spatial import cKDTree
        pts = np.concatenate([np.concatenate([d['S'][::3, ::2][d['S'][::3, ::2][..., 2] < 260].reshape(-1, 3)[:, :2]]) for d in curls.values()])
        tree = cKDTree(pts)
        def excl(x, y):
            dd, _ = tree.query(np.stack([x, y], 1))
            return (dd < 520)
        Vg, Fg, ng = ground_polar(excl, seed=seed, R=11000.)
        m.add(Vg, Fg, None, mat=2, flat=True)
    mesh = m.done(); info = dict(shell_tris=int(tri), ground_blocks=int(ng), build_s=round(time.time() - t0, 1))
    return mesh, info, curls


if __name__ == "__main__":
    mesh, info, curls = build()
    print(info, len(mesh['F']), 'tris')
    np.savez('/home/claude/c55e/model/_ea.npz', **mesh)
    np.savez('/home/claude/c55e/model/_ea_surf.npz', **{f'{k}_{kk}': v for k, d in curls.items() for kk, v in d.items() if isinstance(v, np.ndarray)})
    print(mesh_report(mesh))
