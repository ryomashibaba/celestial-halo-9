"""E-B 《縒界井 / YORI-WELL》 v2 — independent macro study (does NOT use the D1 'ground rolls up' principle).
Gravity is not 'down' but 'toward the public void'. Three habitat ribbons (thick, inhabited on BOTH faces) wind around a
~2.3 km wide, 4.4 km tall central void with different radius / handedness / pitch. Each ribbon is banked toward the void
(its floor faces the void); its underside is an egg-crate ceiling world; its inner edge is a tiered wall-city facing the void; its outer edge
is a fluted exterior facade topped by a colonnade of fins. Radial blade-slabs (not boxes) stand on the terraces and set the rhythm.
v1 failure (see rejected/): revolved hanging pods read as fangs/stalactites -> removed."""
import sys, time, numpy as np
from lib_e import *
from blocks import block_mesh

SPECS = [
    dict(name='A', R=3380., W=960., T=560., turns=1.35, th0=np.radians(200), dirn=+1, z1=4400., bank=0.50, seed=11),
    dict(name='C', R=2210., W=780., T=480., turns=1.55, th0=np.radians(20), dirn=-1, z1=3900., bank=0.60, seed=12),
    dict(name='B', R=1330., W=540., T=420., turns=2.05, th0=np.radians(110), dirn=+1, z1=3300., bank=0.72, seed=13),
]


def ribbon_frames(sp, ds):
    R0 = sp['R']; L = sp['turns'] * 2 * np.pi * R0 * 1.15
    nT = int(L / ds)
    tau = np.linspace(0, 1, nT)
    th = sp['th0'] + sp['dirn'] * 2 * np.pi * sp['turns'] * tau
    zc = sp['z1'] * tau ** 1.18
    Rr = R0 * (1 + 0.40 * np.exp(-tau * 7.5))
    rnd = np.where(tau > 0.952, np.sqrt(np.clip(1 - ((tau - 0.952) / 0.048) ** 2, 0, 1)), 1.0)      # semicircular terminal
    Wd = sp['W'] * (1 + 0.22 * np.exp(-tau * 6.0)) * (1 + 0.15 * smooth(0.84, 0.95, tau)) * np.maximum(rnd, 0.02)
    Tt = sp['T'] * smooth(0.0, 0.08, tau) * (1 - 0.30 * smooth(0.88, 1.0, tau))
    beta = sp['bank'] * smooth(0.04, 0.38, tau) * (1 - smooth(0.84, 1.0, tau))
    r_hat = np.stack([np.cos(th), np.sin(th), np.zeros(nT)], 1)
    C = np.stack([Rr * np.cos(th), Rr * np.sin(th), zc + np.sin(beta) * Wd / 2 + np.cos(beta) * Tt / 2 + 0.5], 1)
    w_hat = np.cos(beta)[:, None] * r_hat + np.sin(beta)[:, None] * np.array([[0, 0, 1.0]])
    Tg = unit(np.gradient(C, axis=0))
    n_hat = unit(np.cross(w_hat, Tg))
    n_hat = np.where((n_hat[:, 2] < 0)[:, None], -n_hat, n_hat)
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))]
    return dict(tau=tau, C=C, w=w_hat, n=n_hat, W=Wd, T=Tt, s=s, th=th, r_hat=r_hat, beta=beta, zc=zc, tang=Tg), nT


def top_relief(fr, nT, nW, seed):
    s = fr['s'][:, None]; Wd = fr['W'][:, None]
    u = np.linspace(0, 1, nW)[None, :] * np.ones((nT, 1))          # u=0 void-side edge, 1 outer edge
    Nt = np.maximum(Wd / 90.0, 3)
    ter = stair(u * Nt, 0.68) * 17.0
    ter = ter - ter[:, :1]
    cross = -11.0 * pulse((s / 98.0) % 1.0, 0.26)
    ridge = 22.0 * pulse((s / 196.0) % 1.0, 0.08) * smooth(0.15, 0.4, u) * (1 - smooth(0.8, 0.95, u))
    cx = np.floor(s / 49.0); cy = np.floor(u * Nt * 2.0)
    fx = (s / 49.0) % 1.0; fy = (u * Nt * 2.0) % 1.0
    pad = smooth(0.0, 0.22, 0.5 - np.abs(fx - 0.5)) * smooth(0.0, 0.22, 0.5 - np.abs(fy - 0.5))
    pocket = -13.0 * pad * (hash2(cx, cy, seed) < 0.38)
    edge = smooth(0.0, 0.035, u) * smooth(0.0, 0.035, 1 - u)
    return (ter + cross + ridge + pocket) * edge * smooth(0.0, 0.07, fr['tau'])[:, None]


def bottom_relief(fr, nT, nW, seed):
    """underside = ceiling world: egg-crate coffers (inverted terraced bowls) + deep long ribs. Max protrusion ~45 m, no spikes."""
    s = fr['s'][:, None]; Wd = fr['W'][:, None]
    u = np.linspace(0, 1, nW)[None, :] * np.ones((nT, 1)); w_m = u * Wd
    rib = 30.0 * pulse((w_m / 150.0) % 1.0, 0.22)
    xr = 24.0 * pulse((s / 150.0) % 1.0, 0.16)
    fx = (s / 150.0) % 1.0; fy = (w_m / 150.0) % 1.0
    bowl = smooth(0.0, 0.35, 0.5 - np.abs(fx - 0.5)) * smooth(0.0, 0.35, 0.5 - np.abs(fy - 0.5))
    coffer = -22.0 * bowl * (hash2(np.floor(s / 150.0), np.floor(w_m / 150.0), seed) < 0.55)
    edge = smooth(0.0, 0.04, u) * smooth(0.0, 0.04, 1 - u)
    return (rib + xr + coffer) * edge * smooth(0.0, 0.07, fr['tau'])[:, None]


def build(ds=17.0, dw=15.0, seed=3, log=print, ground=True):
    t0 = time.time(); rng = np.random.default_rng(seed); m = Mesh()
    foot = []; tri_ribbon = 0; ribbons = {}; n_slab = 0; sol = {}
    for sp in SPECS:
        fr, nT = ribbon_frames(sp, ds); Wmax = fr['W'].max(); nW = int(Wmax / dw) + 1
        jw = np.linspace(-0.5, 0.5, nW)[None, :, None]
        Wd = fr['W'][:, None, None]
        C = fr['C'][:, None, :]; wv = fr['w'][:, None, :]; nv = fr['n'][:, None, :]; T = fr['T'][:, None, None]
        h_top = top_relief(fr, nT, nW, sp['seed']); h_bot = bottom_relief(fr, nT, nW, sp['seed'] + 5)
        Ptop = C + wv * (jw * Wd) + nv * (T / 2 + h_top[..., None])
        Pbot = C + wv * (jw * Wd) - nv * (T / 2 + h_bot[..., None])
        tri_ribbon += add_grid(m, Ptop, mat=1)
        tri_ribbon += add_grid(m, Pbot[::2], mat=0)
        sol[sp['name']] = np.concatenate([Ptop[::3, ::4].reshape(-1, 3), Pbot[::3, ::4].reshape(-1, 3)])
        # side strips: inner = tiered wall city facing the void ; outer = fluted facade
        nZ = 46; kz = np.linspace(0, 1, nZ)[None, :]; s = fr['s'][:, None]
        bal = 30.0 * (1 - smooth(0.55, 1.0, (kz * 8.0) % 1.0))
        bay_p = smooth(0.0, 0.2, 0.5 - np.abs(((s / 62.0) % 1.0) - 0.5))
        edge_z = smooth(0.0, 0.05, kz) * smooth(0.0, 0.05, 1 - kz)
        root = smooth(0.0, 0.07, fr['tau'])[:, None]
        g_in = bal * (0.45 + 0.55 * bay_p) * edge_z * root
        cs = np.floor(s / 118.0); cz = np.floor(kz * 4.0)
        bayo = smooth(0.0, 0.22, 0.5 - np.abs(((s / 118.0) % 1.0) - 0.5)) * smooth(0.0, 0.22, 0.5 - np.abs(((kz * 4.0) % 1.0) - 0.5))
        recess = 52.0 * bayo * (hash2(cs, cz, sp['seed'] + 9) < 0.62)
        slot = 110.0 * pulse((s / (118.0 * 9)) % 1.0, 0.045) * smooth(0.06, 0.15, kz) * (1 - smooth(0.85, 0.94, kz))
        flute = (recess + slot) * edge_z * root
        zz = (T[:, :, 0] / 2) * (1 - 2 * kz)
        Wh = fr['W'][:, None] / 2
        for sgn, g, mat in ((-1.0, g_in, 1), (+1.0, -flute, 0)):
            Ps = fr['C'][:, None, :] + fr['w'][:, None, :] * (sgn * (Wh + g))[..., None] + fr['n'][:, None, :] * zz[..., None]
            tri_ribbon += add_grid(m, Ps, mat=mat)
        for ie in (0, nT - 1):
            add_strip(m, Ptop[ie], Pbot[ie], mat=0)
        # ---- radial blade-slabs on the terraces (thin slabs along the radial street direction; height envelope rises outward)
        step = 5; idx = np.arange(int(0.10 * nT), int(0.95 * nT), step)
        SP = []; SN = []; SF = []; SL = []; SW = []; SH = []
        for i in idx:
            k = rng.integers(1, 4)
            for _ in range(k):
                u_ = rng.uniform(0.18, 0.86); j = int(u_ * (nW - 1))
                if fr['W'][i] < 0.45 * sp['W']: continue
                jj = int(np.clip(u_ * (nW - 1) * (Wmax / max(fr['W'][i], 1.0)) * 0 + u_ * (nW - 1), 0, nW - 1))
                SP.append(Ptop[i, j]); SN.append(fr['n'][i]); SF.append(-fr['w'][i])
                SL.append(rng.uniform(110, 250)); SW.append(rng.uniform(30, 52)); SH.append((40 + 190 * u_ ** 1.3) * rng.uniform(0.55, 1.25))
        SP = np.array(SP); SN = np.array(SN); SF = np.array(SF); SL = np.array(SL); SW = np.array(SW); SH = np.array(SH)
        Vb, Fb = block_mesh(SP, SN, SF, SL, SW, SH, 0.10 * SH, rng.uniform(0.05, 0.3, len(SP)))
        m.add(Vb, Fb, None, mat=1, flat=True); n_slab += len(SP)
        # ---- rim skyline: long slabs along the outer rim (exterior city silhouette) + small colonnade fins
        io = np.arange(int(0.10 * nT), int(0.95 * nT), 4)
        Po = fr['C'][io] + fr['w'][io] * (fr['W'][io] * 0.46)[:, None] + fr['n'][io] * (fr['T'][io] / 2 + 2)[:, None]
        env = 0.5 + 0.5 * np.sin(fr['s'][io] / 1400.0 + sp['seed'])
        Hc = (90 + 330 * env ** 1.6) * rng.uniform(0.55, 1.1, len(io))
        Vc, Fc = block_mesh(Po, fr['n'][io], fr['tang'][io], rng.uniform(90, 220, len(io)), rng.uniform(36, 70, len(io)), Hc, 0.05 * Hc, rng.uniform(0.05, 0.3, len(io)))
        m.add(Vc, Fc, None, mat=1, flat=True); n_slab += len(io)
        io2 = np.arange(int(0.10 * nT), int(0.95 * nT), 2)
        Po2 = fr['C'][io2] + fr['w'][io2] * (fr['W'][io2] / 2)[:, None] + fr['n'][io2] * (fr['T'][io2] / 2 + 2)[:, None]
        Vc, Fc = block_mesh(Po2, fr['n'][io2], -fr['w'][io2], np.full(len(io2), 46.), np.full(len(io2), 15.), 40 + 30 * hash2(io2 // 2, io2 % 5, sp['seed']), np.zeros(len(io2)), np.zeros(len(io2)))
        m.add(Vc, Fc, None, mat=0, flat=True); n_slab += len(io2)
        foot.append(fr['C'][fr['zc'] < 300][:, :2]); ribbons[sp['name']] = fr
        log(f"  ribbon {sp['name']}: nT={nT} nW={nW} len={fr['s'][-1]/1000:.1f}km slabs={len(SP)}+{len(io)}  {time.time()-t0:.1f}s")
    # ---- annular agora platters inside the void (public floors) + radial blade bridges to ribbon B's void edge
    ag = [(2250., 2.1, 470., -0.16), (3300., 4.0, 400., 0.22)]
    for (zh, ph, rad, tilt) in ag:
        nr, na = 24, 120
        r = np.linspace(0.30, 1, nr)[:, None]; a = np.linspace(0, 2 * np.pi, na)[None, :]
        rr = rad * r
        X = rr * np.cos(a); Y = rr * np.sin(a)
        thick = 70 * (1 - ((r - 0.65) / 0.35) ** 2).clip(0.0, 1) + 12
        tz = np.cos(a - ph) * tilt * rr * 0.5
        terr = 10.0 * stair((r - 0.30) * 7.0, 0.6)
        Zt = zh + tz + thick / 2 + terr; Zb = zh + tz - thick / 2 - 12 * pulse((rr / 55.0) % 1.0, 0.25)
        Pt = np.stack([X, Y, Zt * np.ones_like(X)], -1); Pb = np.stack([X, Y, Zb * np.ones_like(X)], -1)
        tri_ribbon += add_grid(m, Pt, mat=1); tri_ribbon += add_grid(m, Pb, mat=0)
        add_strip(m, Pt[-1], Pb[-1], mat=0); add_strip(m, Pt[0], Pb[0], mat=0)
        for k in range(3):
            az = ph + 2.1 * k + 0.4
            rs = np.linspace(rad - 10, 1190.0, 40)
            zb = zh + np.cos(az - ph) * tilt * rs * 0.5
            path = np.stack([rs * np.cos(az), rs * np.sin(az), zb], 1)
            sweep_rect(path, np.tile([0, 0, 1.0], (40, 1)), 34, 46, m, mat=0)
    ng = 0
    if ground:
        from scipy.spatial import cKDTree
        tree = cKDTree(np.concatenate(foot))
        def excl(x, y):
            d, _ = tree.query(np.stack([x, y], 1))
            return (d < 900) | (np.hypot(x, y) < 1500)
        Vg, Fg, ng = ground_polar(excl, seed=7, R=11000.)
        m.add(Vg, Fg, None, mat=2, flat=True)
    mesh = m.done(); info = dict(ribbon_tris=int(tri_ribbon), blade_slabs_and_fins=int(n_slab), ground_blocks=int(ng), build_s=round(time.time() - t0, 1))
    return mesh, info, ribbons, sol


if __name__ == "__main__":
    mesh, info, rib, sol = build()
    print(info, len(mesh['F']), 'tris')
    np.savez('/home/claude/c55e/model/_eb.npz', **mesh)
    np.savez('/home/claude/c55e/model/_eb_frames.npz', **{f'{k}_{kk}': v for k, fr in rib.items() for kk, v in fr.items() if isinstance(v, np.ndarray)})
    np.savez('/home/claude/c55e/model/_eb_solidsamples.npz', **sol)
    print(mesh_report(mesh))
