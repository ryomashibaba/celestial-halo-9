"""Great Hall (大回廊 'Reliquary Nave') -- interior public city inside the north wall of the Rift.
Local frame: x along hall axis (-550..550), y lateral, z up from hall floor. Placed inside the north massif."""
import numpy as np
from c55a_geom import *
import c55a_city as C

COLL = 'GREAT_HALL_INTERIOR'
LX = 550.0
NXS = 56
TIER_H, TIER_B, NT, LAM0 = 38.0, 28.0, 6, 62.0
SPRING_Z, APEX_Z, HALF_W = 228.0, 430.0, 230.0


def octa(centers, r):
    centers = np.atleast_2d(centers)
    n = len(centers)
    r = np.broadcast_to(np.asarray(r, float), (n,))
    base = np.array([[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], float)
    Fb = np.array([[0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4], [2, 0, 5], [1, 2, 5], [3, 1, 5], [0, 3, 5]], np.int32)
    V = base[None] * r[:, None, None] + centers[:, None, :]
    F = Fb[None] + (np.arange(n) * 6)[:, None, None]
    return V.reshape(-1, 3), F.reshape(-1, 3).astype(np.int32)


def arch_curve(n=41):
    u = np.linspace(-1, 1, n)
    return u, np.stack([np.zeros(n), HALF_W * u, SPRING_Z + (APEX_Z - SPRING_Z) * (1 - np.abs(u) ** 1.3)], 1)


def build_hall(S, sec, rng):
    i = int(round(0.40 * (C.NS - 1)))
    ex = np.array([sec['tx'][i], sec['ty'][i], 0.0])
    ey = np.array([sec['nx'][i], sec['ny'][i], 0.0])
    ez = np.array([0, 0, 1.0])
    O = np.array([sec['xs'][i], sec['ys'][i], sec['fl'][i] + 330.0]) + ey * 900.0
    Rm = np.stack([ex, ey, ez], 1)
    sec['hall'] = dict(O=O, Rm=Rm)

    def T(V):
        return np.asarray(V, float) @ Rm.T + O

    def add(name, mat, V, F, key=None, bias=0.0):
        S.add(name, COLL, mat, T(V), F, interior=True, key=None if key is None else T(key), bias=bias)

    xs = np.linspace(-LX, LX, NXS)
    # --- floor
    ys = [-LAM0, -12.0, 12.0, LAM0]
    Pf = np.zeros((NXS, 4, 3))
    for j, y in enumerate(ys):
        Pf[:, j] = np.stack([xs, np.full(NXS, y), np.zeros(NXS)], 1)
    V, F = grid_mesh(Pf)
    fi, fj = face_seg(NXS, 4)
    v, f = sub_mesh(V, F, fj != 1)
    add('hall_floor', 'hall_floor', v, f)
    v, f = sub_mesh(V, F, fj == 1)
    v = v + [0, 0, 0.5]
    add('hall_canal', 'canal', v, f, bias=1.0)
    # --- galleries
    prof = [(LAM0, 0.0)]
    for k in range(NT):
        prof.append((LAM0 + TIER_B * k, TIER_H * (k + 1)))
        prof.append((LAM0 + TIER_B * (k + 1), TIER_H * (k + 1)))
    prof.append((LAM0 + TIER_B * NT, SPRING_Z + 24))
    prof = np.array(prof)
    nseg = len(prof) - 1
    for side, nm in ((1, 'E'), (-1, 'W')):
        P = np.zeros((NXS, len(prof), 3))
        for j, (lam, z) in enumerate(prof):
            P[:, j] = np.stack([xs, np.full(NXS, side * lam), np.full(NXS, z)], 1)
        V, F = grid_mesh(P)
        fi, fj = face_seg(NXS, len(prof))
        ris = (fj < 2 * NT) & (fj % 2 == 0)
        led = (fj < 2 * NT) & (fj % 2 == 1)
        top = fj >= 2 * NT
        add(f'gallery_{nm}_risers', 'hall_stone', *sub_mesh(V, F, ris))
        add(f'gallery_{nm}_ledges', 'hall_ledge', *sub_mesh(V, F, led))
        add(f'gallery_{nm}_wall', 'hall_stone', *sub_mesh(V, F, top))
        toward = lambda cen: np.stack([np.zeros(len(cen)), -np.sign(cen[:, 1]), np.zeros(len(cen))], 1)
        rj = [2 * k for k in range(NT)]
        lj = [2 * k + 1 for k in range(NT)]
        Vw, Fw, Kw = quad_decals(P, rj, [(0.12, 0.45), (0.55, 0.88)], [(0.12, 0.42), (0.55, 0.85)], 0.5, toward, keep=0.82, rng=rng)
        nw = len(Fw) // 2
        cat = rng.choice(3, size=nw, p=[0.82, 0.13, 0.05])
        fc = np.repeat(cat, 2)
        for ci, m in enumerate(('win_warm', 'win_cool', 'win_cyan')):
            msk = fc == ci
            if msk.any():
                v, f = sub_mesh(Vw, Fw, msk)
                add(f'gallery_{nm}_{m}', m, v, f, key=Kw[msk])
        up = lambda c: np.tile([0, 0, 1.0], (len(c), 1))
        Vl, Fl, Kl = quad_decals(P, lj, [(0.0, 1.0)], [(0.0, 0.06)], 0.6, up)
        add(f'gallery_{nm}_lip_lights', 'edge_light', Vl, Fl, key=Kl)
        Vg, Fg, Kg = quad_decals(P, lj, [(0.04, 0.2), (0.25, 0.45), (0.5, 0.7), (0.75, 0.95)], [(0.3, 0.9)], 0.4, up, keep=0.6, rng=rng)
        add(f'gallery_{nm}_gardens', 'garden', Vg, Fg, key=Kg)
        # trees
        tp = []
        for k in range(NT):
            lam = LAM0 + TIER_B * k + 0.55 * TIER_B
            z = TIER_H * (k + 1) + 3.5
            xs_t = np.arange(-LX + 8, LX, 13.0) + rng.uniform(-3, 3, len(np.arange(-LX + 8, LX, 13.0)))
            keep = rng.random(len(xs_t)) < 0.75
            tp.append(np.stack([xs_t[keep], np.full(keep.sum(), side * lam), np.full(keep.sum(), z)], 1))
        tp = np.vstack(tp)
        Vt, Ft = octa(tp, rng.uniform(4.0, 6.5, len(tp)))
        add(f'gallery_{nm}_trees', 'tree', Vt, Ft)
        # columns on riser fronts
        cp = []
        for k in range(1, NT):
            lam = LAM0 + TIER_B * k - 1.2
            cx = np.arange(-LX + 5, LX, 11.0)
            cp.append(np.stack([cx, np.full(len(cx), side * lam), np.full(len(cx), TIER_H * k + TIER_H / 2 + 0.0)], 1))
        cp = np.vstack(cp)
        Vc, Fc = boxes(cp, [2.2, 2.2, TIER_H - 2])
        add(f'gallery_{nm}_columns', 'bronze', Vc, Fc)
    # --- vault ribs
    u, arch = arch_curve(41)
    nrib = 21
    xr = np.linspace(-LX, LX, nrib)
    rect = [(-6, -4.5), (6, -4.5), (6, 4.5), (-6, 4.5)]
    ribs = []
    Tg = normalize(np.gradient(arch, axis=0))
    Nn = np.tile([1.0, 0, 0], (len(arch), 1))
    Bn = normalize(np.cross(Tg, Nn))
    for x in xr:
        path = arch + [x, 0, 0]
        P = sweep_grid(path, rect, N=Nn, B=Bn)
        ribs.append(grid_mesh(P))
    Vr, Fr = merge(ribs)
    add('vault_ribs', 'bronze', Vr, Fr)
    # --- vault panels
    for r in range(nrib - 1):
        P = np.zeros((2, len(arch), 3))
        P[0] = arch + [xr[r] + 7, 0, -2.0]
        P[1] = arch + [xr[r + 1] - 7, 0, -2.0]
        V, F = grid_mesh(P)
        fi, fj = face_seg(2, len(arch))
        um = -1 + 2 * (fj + 0.5) / (len(arch) - 1)
        sky = (np.abs(um) < 0.26) & (7 <= r <= 12)
        mat = 'vault_a' if r % 2 == 0 else 'vault_b'
        add(f'vault_panel_{r:02d}', mat, *sub_mesh(V, F, ~sky))
        if sky.any():
            add(f'vault_sky_{r:02d}', 'vault_sky', *sub_mesh(V, F, sky))
    # --- end walls
    for xe, nm, sgn in ((LX, 'E', -1), (-LX, 'W', 1)):
        bnd = [(-HALF_W, 0.0)] + [(HALF_W, 0.0)] + [(HALF_W, SPRING_Z)] + [(a[1], a[2]) for a in arch[::-1]][1:-1] + [(-HALF_W, SPRING_Z)]
        bnd = np.array([[xe, y, z] for y, z in bnd])
        ctr = np.array([[xe, 0, 190.0]])
        Vw = np.vstack([ctr, bnd])
        Fw = np.array([[0, k + 1, (k + 1) % len(bnd) + 1] for k in range(len(bnd))], np.int32)
        add(f'endwall_{nm}', 'hall_stone', Vw, Fw)
    # rose window (east end) and glowing portal (west end)
    ph = np.linspace(0, 2 * np.pi, 97)
    cc = np.array([LX - 3.0, 0, 262.0])
    ring = cc + 150.0 * np.stack([np.zeros(97), np.cos(ph), np.sin(ph)], 1)
    Vd = np.vstack([cc[None], ring])
    Fd = np.array([[0, k + 1, k + 2] for k in range(96)], np.int32)
    add('rose_window', 'rose', Vd, Fd, bias=2.0)
    ringf = cc + 158.0 * np.stack([np.zeros(97), np.cos(ph), np.sin(ph)], 1)
    Nn2 = normalize(ringf - cc)
    Bn2 = np.tile([1.0, 0, 0], (97, 1))
    Pf2 = sweep_grid(ringf, [(-10, -9), (10, -9), (10, 9), (-10, 9)], N=Nn2, B=Bn2)
    add('rose_frame', 'champagne', *grid_mesh(Pf2), bias=3.0)
    sp = []
    for a in np.linspace(0, np.pi, 13)[:-1]:
        dvec = np.array([0, np.cos(a), np.sin(a)])
        Rb = np.stack([np.cross([1.0, 0, 0], dvec), dvec, [1.0, 0, 0]], 1)
        sp.append(boxes([cc + [-3, 0, 0]], [[4, 300, 5]], R=Rb) if False else boxes([cc + [-4, 0, 0]], [[6.0, 5.0, 300.0]], R=np.stack([[1.0, 0, 0], np.cross([1.0, 0, 0], dvec) * 0 + np.array([0, -np.sin(a), np.cos(a)]), dvec], 1)))
    add('rose_spokes', 'champagne', *merge(sp), bias=4.0)
    cw = np.array([-LX + 3.0, 0, 150.0])
    ellipse = cw + np.stack([np.zeros(97), 120 * np.cos(ph), 150 * np.sin(ph)], 1)
    Vd = np.vstack([cw[None], ellipse])
    add('west_portal_glow', 'vault_sky', Vd, Fd, bias=2.0)
    # --- bridges across the hall
    for k, (x, tier) in enumerate([(-330, 3), (-110, 4), (130, 3), (360, 4)]):
        lam = LAM0 + TIER_B * tier + 1.0
        z = TIER_H * tier
        A = T(np.array([[x, -lam, z]]))[0]
        B = T(np.array([[x, lam, z]]))[0]
        C.bridge(S, f'hall_bridge{k + 1}', A, B, 26, width=18, coll=COLL, interior=True)
    # --- lanterns
    lx = (xr[:-1] + xr[1:]) / 2
    Vl, Fl = octa(np.stack([lx, np.zeros_like(lx), np.full_like(lx, 345.0)], 1), 9.0)
    add('lanterns', 'lantern', Vl, Fl)
    # --- people (scale cues)
    npp = 1100
    px = rng.uniform(-LX + 5, LX - 5, npp)
    onfloor = rng.random(npp) < 0.45
    py = np.where(onfloor, rng.uniform(-LAM0 + 3, LAM0 - 3, npp), 0.0)
    pz = np.zeros(npp)
    pk = rng.integers(0, NT, npp)
    sd = np.where(rng.random(npp) < 0.5, 1, -1)
    lam = LAM0 + TIER_B * pk + rng.uniform(6, TIER_B - 6, npp)
    py = np.where(onfloor, py, sd * lam)
    pz = np.where(onfloor, 0.0, TIER_H * (pk + 1) + 0.2)
    pv = np.zeros((npp, 4, 3))
    pv[:, 0] = np.stack([px, py - 0.45, pz], 1)
    pv[:, 1] = np.stack([px, py + 0.45, pz], 1)
    pv[:, 2] = np.stack([px, py + 0.45, pz + 1.85], 1)
    pv[:, 3] = np.stack([px, py - 0.45, pz + 1.85], 1)
    base = np.arange(npp) * 4
    Fp = np.stack([np.stack([base, base + 1, base + 2], 1), np.stack([base, base + 2, base + 3], 1)], 1).reshape(-1, 3)
    add('people', 'people', pv.reshape(-1, 3), Fp)
    # --- central floor pavilions (low shells)
    pav = []
    for x in np.arange(-480, 500, 140):
        rad = 17.0
        prof = np.array([(rad, 0), (rad * 0.96, rad * 0.45), (rad * 0.7, rad * 0.9), (rad * 0.3, rad * 1.2), (0, rad * 1.3)])
        Pd = revolve_grid(prof, 16)
        Vd, Fd2 = grid_mesh(Pd)
        pav.append((Vd + [x, 0, 0.2], Fd2))
    add('floor_pavilions', 'bronze', *merge(pav))


if __name__ == '__main__':
    S = C.Scene() if hasattr(C, 'Scene') else None
