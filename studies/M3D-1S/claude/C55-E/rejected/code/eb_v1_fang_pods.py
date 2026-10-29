"""E-B 《縒界井 / YORI-WELL》 — independent macro study (does NOT use the D1 'ground rolls up' principle).
Idea: gravity is not 'down' but 'toward the public void'. Three habitat ribbons (thick, inhabited on BOTH faces) wind around a
2.2 km wide, 4.4 km tall central void with different radius / handedness / pitch. Each ribbon is banked toward the void
(floor faces the void), its underside is an overhead city (pods grow along the underside normal = local gravity of that world),
its inner edge is a wall-city facing the void, its outer edge is the exterior facade.
Ribbons never share a radial band, so they pass over/under each other with no collisions."""
import sys, time, numpy as np
from lib_e import *

SPECS = [
    dict(name='A', R=3000., W=820., T=430., turns=1.35, th0=np.radians(200), dirn=+1, z1=4400., bank=0.50, seed=11),
    dict(name='C', R=2110., W=650., T=380., turns=1.55, th0=np.radians(20), dirn=-1, z1=3900., bank=0.62, seed=12),
    dict(name='B', R=1400., W=490., T=330., turns=2.05, th0=np.radians(110), dirn=+1, z1=3300., bank=0.74, seed=13),
]


def ribbon_frames(sp, ds=15.0):
    R0 = sp['R']; L = sp['turns'] * 2 * np.pi * R0 * 1.15
    nT = int(L / ds)
    tau = np.linspace(0, 1, nT)
    # arclength-ish reparametrisation is not needed: relief uses true arclength computed below
    th = sp['th0'] + sp['dirn'] * 2 * np.pi * sp['turns'] * tau
    zc = sp['z1'] * tau ** 1.18
    flare = 1 + 0.45 * np.exp(-tau * 7.5)
    Rr = R0 * flare
    Wd = sp['W'] * (1 + 0.55 * np.exp(-tau * 6.0)) * (1 + 0.45 * smooth(0.86, 1.0, tau))        # roots splay, tops open into a sky-deck
    Tt = sp['T'] * smooth(0.0, 0.08, tau) * (1 - 0.35 * smooth(0.88, 1.0, tau))
    beta = sp['bank'] * smooth(0.04, 0.38, tau) * (1 - smooth(0.84, 1.0, tau))
    r_hat = np.stack([np.cos(th), np.sin(th), np.zeros(nT)], 1)
    C = np.stack([Rr * np.cos(th), Rr * np.sin(th), zc + np.sin(beta) * Wd / 2 + np.cos(beta) * Tt / 2 + 0.5], 1)
    w_hat = np.cos(beta)[:, None] * r_hat + np.sin(beta)[:, None] * np.array([[0, 0, 1.0]])
    Tg = unit(np.gradient(C, axis=0))
    n_hat = unit(np.cross(w_hat, Tg))
    n_hat = np.where((n_hat[:, 2] < 0)[:, None], -n_hat, n_hat)
    s = np.r_[0, np.cumsum(np.linalg.norm(np.diff(C, axis=0), axis=1))]
    return dict(tau=tau, C=C, w=w_hat, n=n_hat, W=Wd, T=Tt, s=s, th=th, r_hat=r_hat, nT=nT, beta=beta, zc=zc)


def top_relief(fr, nW, seed):
    """habitation face: banked terrace amphitheatre facing the void + cross streets + pockets + radial fin-ridges."""
    nT = fr['nT']; s = fr['s'][:, None]; Wd = fr['W'][:, None]
    j = np.linspace(0, 1, nW)[None, :]; u = j * np.ones((nT, 1))            # u=0 void-side edge ... 1 outer edge
    Nt = np.maximum(Wd / 86.0, 3)                                           # terrace count across
    ter = stair(u * Nt, 0.68) / Nt * 0.0 + stair(u * Nt, 0.68) * 17.0          # terraces rise outward (amphitheatre)
    ter = ter - ter[:, :1]                                                  # zero at inner edge
    ter *= 1 - 0.0
    ps = 98.0
    cross = -11.0 * pulse((s / ps) % 1.0, 0.26) * np.ones_like(u)
    ridge = 26.0 * pulse((s / (ps * 2)) % 1.0, 0.06) * smooth(0.15, 0.4, u) * (1 - smooth(0.8, 0.95, u))   # radial fin walls every ~200 m
    cx = np.floor(s / 49.0); cy = np.floor(u * Nt * 2.0)
    fx = (s / 49.0) % 1.0; fy = (u * Nt * 2.0) % 1.0
    pad = smooth(0.0, 0.22, 0.5 - np.abs(fx - 0.5)) * smooth(0.0, 0.22, 0.5 - np.abs(fy - 0.5))
    pocket = -13.0 * pad * (hash2(cx, cy, seed) < 0.38)
    edge = smooth(0.0, 0.035, u) * smooth(0.0, 0.035, 1 - u)
    h = (ter + cross + ridge + pocket) * edge
    h = h * smooth(0.0, 0.07, fr['tau'])[:, None]                           # calm at the ground root
    return h


def bottom_relief(fr, nW, seed):
    """underside = ceiling world: long coffer ribs + cross vault ribs."""
    nT = fr['nT']; s = fr['s'][:, None]; Wd = fr['W'][:, None]
    u = np.linspace(0, 1, nW)[None, :] * np.ones((nT, 1)); w_m = u * Wd
    rib = 24.0 * pulse((w_m / 118.0) % 1.0, 0.2)
    xr = 16.0 * pulse((s / 164.0) % 1.0, 0.12)
    edge = smooth(0.0, 0.04, u) * smooth(0.0, 0.04, 1 - u)
    return (rib + xr) * edge * smooth(0.0, 0.07, fr['tau'])[:, None]


def build(ds=17.0, dw=15.0, seed=3, log=print, ground=True):
    t0 = time.time(); rng = np.random.default_rng(seed); m = Mesh(); info = {}
    foot = []     # xy samples of ribbon feet for ground exclusion
    n_pods = 0; tri_ribbon = 0
    ribbons = {}
    for sp in SPECS:
        fr = ribbon_frames(sp, ds); nT = fr['nT']; Wmax = fr['W'].max(); nW = int(Wmax / dw) + 1
        jw = np.linspace(-0.5, 0.5, nW)[None, :, None]            # fractional width coord
        Wd = fr['W'][:, None, None]
        C = fr['C'][:, None, :]; wv = fr['w'][:, None, :]; nv = fr['n'][:, None, :]; T = fr['T'][:, None, None]
        # NOTE: u=0 is the VOID side (inner edge) -> w = -W/2 ; u=1 outer
        h_top = top_relief(fr, nW, sp['seed']); h_bot = bottom_relief(fr, nW, sp['seed'] + 5)
        Ptop = C + wv * (jw * Wd) + nv * (T / 2 + h_top[..., None])
        Pbot = C + wv * (jw * Wd) - nv * (T / 2 + h_bot[..., None])
        tri_ribbon += add_grid(m, Ptop, mat=1)
        tri_ribbon += add_grid(m, Pbot[::2], mat=0)
        # side strips (inner edge = void-facing wall city, outer edge = exterior facade)
        nZ = 46; kz = np.linspace(0, 1, nZ)[None, :]
        s = fr['s'][:, None]
        tier = stair(kz * 8.0, 0.55) / 8.0
        bal = 38.0 * (stair(kz * 8.0, 0.55) - kz * 8.0 * 0 ) % 1.0 if False else 30.0 * (1 - smooth(0.55, 1.0, (kz * 8.0) % 1.0))
        bay = 1 - 0.0 * s
        fx = (s / 62.0) % 1.0
        bay_p = smooth(0.0, 0.2, 0.5 - np.abs(fx - 0.5))
        edge_z = smooth(0.0, 0.05, kz) * smooth(0.0, 0.05, 1 - kz)
        g_in = (bal * (0.45 + 0.55 * bay_p)) * edge_z * smooth(0.0, 0.07, fr['tau'])[:, None]
        flute = 9.0 * pulse((s / 41.0) % 1.0, 0.4) * edge_z * smooth(0.0, 0.07, fr['tau'])[:, None]
        zz = (T[:, :, 0] / 2) * (1 - 2 * kz)                       # (nT,nZ): +T/2 (top) ... -T/2
        for side, g, sgn, mat in (('in', g_in, -1.0, 1), ('out', -flute, +1.0, 0)):
            Wh = fr['W'][:, None] / 2
            Ps = fr['C'][:, None, :] + fr['w'][:, None, :] * (sgn * (Wh + (g if side == 'in' else g))[..., None]) + fr['n'][:, None, :] * zz[..., None]
            tri_ribbon += add_grid(m, Ps, mat=mat)
        # end caps
        for ie in (0, nT - 1):
            A = Ptop[ie]; B = Pbot[ie]
            add_strip(m, A, B, mat=0)
        # hanging districts along the underside (grow along local underside normal = their 'up')
        sp_pod = 170.0
        idx = np.arange(int(0.12 * nT), nT - 3, max(int(sp_pod / ds), 1))
        PP = []; DD = []; LL = []; RR = []
        for i in idx:
            tauv = fr['tau'][i]
            for _ in range(2):
                jj = rng.uniform(-0.4, 0.4)
                p = fr['C'][i] + fr['w'][i] * jj * fr['W'][i] - fr['n'][i] * (fr['T'][i] / 2 + 2)
                PP.append(p); DD.append(-fr['n'][i] + 0.15 * rng.normal(size=3)); 
                big = 0.55 + 0.45 * np.sin(tauv * 9 + sp['seed'])
                LL.append(rng.uniform(110, 360) * (0.5 + big)); RR.append(rng.uniform(42, 118) * (0.6 + 0.4 * big))
        PP = np.array(PP); DD = np.array(DD); LL = np.array(LL); RR = np.array(RR)
        endz = PP[:, 2] + unit(DD)[:, 2] * LL
        okp = endz > 90.0
        PP, DD, LL, RR = PP[okp], DD[okp], LL[okp], RR[okp]
        # gravity: pods never hang into the ground
        Vp, Fp = revolve_pods(PP, DD, LL, RR)
        m.add(Vp, Fp, None, mat=7, flat=True); n_pods += len(PP)
        low = fr['zc'] < 300
        foot.append(fr['C'][low][:, :2]); ribbons[sp['name']] = fr
        log(f"  ribbon {sp['name']}: nT={nT} nW={nW} len={fr['s'][-1]/1000:.1f}km pods={len(PP)}  {time.time()-t0:.1f}s")
    # ---- agora platters inside the void (public floors) hung on radial blade-bridges to ribbon B's void edge
    ag = [(1150., 0.0, 560., 0.10), (2250., 2.1, 440., -0.16), (3250., 4.0, 380., 0.22)]
    for (zh, ph, rad, tilt) in ag:
        nr, na = 22, 96
        r = np.linspace(0, 1, nr)[:, None]; a = np.linspace(0, 2 * np.pi, na)[None, :]
        rr = rad * (r ** 0.9)
        X = rr * np.cos(a); Y = rr * np.sin(a)
        thick = 80 * (1 - r ** 3) + 8
        tz = np.cos(a - ph) * tilt * rr * 0.5
        terr = 9.0 * stair(r * 7.0, 0.6)
        Zt = zh + tz + thick / 2 + terr; Zb = zh + tz - thick / 2 - 12 * pulse((rr / 55.0) % 1.0, 0.25)
        Pt = np.stack([X, Y, Zt * np.ones_like(X)], -1); Pb = np.stack([X, Y, Zb * np.ones_like(X)], -1)
        tri_ribbon += add_grid(m, Pt, mat=1); tri_ribbon += add_grid(m, Pb, mat=0)
        add_strip(m, Pt[-1], Pb[-1], mat=0)
        # blade bridge from platter rim to the void edge of ribbon B (radial slab)
        for k in range(3):
            az = ph + 2.1 * k + 0.4
            R0, R1 = rad - 10, 1150.0
            rs = np.linspace(R0, R1, 40)
            zb = zh + np.cos(az - ph) * tilt * rs * 0.5 + 0.0 * rs
            path = np.stack([rs * np.cos(az), rs * np.sin(az), zb], 1)
            sweep_rect(path, np.tile([0, 0, 1.0], (40, 1)), 34, 46, m, mat=0)
    # ---- ground context
    ng = 0
    if ground:
        from scipy.spatial import cKDTree
        pts = np.concatenate(foot)
        tree = cKDTree(pts)
        def excl(x, y):
            d, _ = tree.query(np.stack([x, y], 1))
            return (d < 780) | (np.hypot(x, y) < 1500)
        Vg, Fg, ng = ground_polar(excl, seed=7, R=11000.)
        m.add(Vg, Fg, None, mat=2, flat=True)
    mesh = m.done(); info = dict(ribbon_tris=int(tri_ribbon), pods=int(n_pods), ground_blocks=int(ng), build_s=round(time.time() - t0, 1))
    return mesh, info, ribbons


if __name__ == "__main__":
    ds = float(sys.argv[1]) if len(sys.argv) > 1 else 17.0
    mesh, info, rib = build(ds=ds)
    print(info, len(mesh['F']), 'tris')
    np.savez('/home/claude/c55e/model/_eb.npz', **mesh)
    np.savez('/home/claude/c55e/model/_eb_frames.npz', **{f'{k}_{kk}': v for k, fr in rib.items() for kk, v in fr.items() if isinstance(v, np.ndarray)})
    print(mesh_report(mesh))
