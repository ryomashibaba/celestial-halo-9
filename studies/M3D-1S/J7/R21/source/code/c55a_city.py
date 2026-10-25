"""CELESTIAL HALO-9 independent research C55-A  (Claude Sonnet 5.5)
《七環天裂都》 SEVENFOLD HALO RIFT  -- procedural real-mesh generator (pure numpy).
Units metres. X east, Y north, Z up.  Same code is used by blender_build.py (bpy) and the GLB exporter.
"""
import numpy as np
from c55a_geom import *

MATERIALS = {
    'shell':       dict(base=(0.93, 0.89, 0.80), spec=0.06),
    'riser':       dict(base=(0.88, 0.83, 0.74), spec=0.04),
    'shell_band':  dict(base=(0.74, 0.62, 0.50), spec=0.05),
    'crest_light': dict(base=(0.0, 0.0, 0.0), emit=(2.4, 1.7, 0.9)),
    'terrace':     dict(base=(0.60, 0.55, 0.49)),
    'plaza':       dict(base=(0.74, 0.70, 0.64)),
    'garden':      dict(base=(0.15, 0.30, 0.15)),
    'tree':        dict(base=(0.10, 0.25, 0.12)),
    'underside':   dict(base=(0.40, 0.36, 0.36)),
    'obsidian':    dict(base=(0.022, 0.022, 0.038), spec=0.9),
    'champagne':   dict(base=(0.90, 0.72, 0.42), spec=0.55),
    'halo_glow':   dict(base=(0.0, 0.0, 0.0), emit=(2.6, 1.9, 1.0)),
    'edge_light':  dict(base=(0.0, 0.0, 0.0), emit=(2.0, 1.45, 0.8)),
    'seam':        dict(base=(0.0, 0.0, 0.0), emit=(1.3, 0.95, 0.55)),
    'under_glow':  dict(base=(0.0, 0.0, 0.0), emit=(0.7, 1.7, 2.3)),
    'win_warm':    dict(base=(0.0, 0.0, 0.0), emit=(2.6, 1.55, 0.65)),
    'win_cool':    dict(base=(0.0, 0.0, 0.0), emit=(1.7, 2.1, 2.6)),
    'win_cyan':    dict(base=(0.0, 0.0, 0.0), emit=(0.5, 2.2, 2.6)),
    'canal':       dict(base=(0.0, 0.0, 0.0), emit=(0.40, 1.25, 1.55)),
    'water':       dict(base=(0.012, 0.05, 0.085), spec=0.8),
    'ground':      dict(base=(0.075, 0.08, 0.095)),
    'road_glow':   dict(base=(0.0, 0.0, 0.0), emit=(1.9, 1.15, 0.5)),
    'carpet_warm': dict(base=(0.0, 0.0, 0.0), emit=(0.42, 0.25, 0.11)),
    'carpet_cool': dict(base=(0.0, 0.0, 0.0), emit=(0.18, 0.33, 0.46)),
    'veil':        dict(base=(1.0, 0.86, 0.62), emit=(0.35, 0.25, 0.12), alpha=0.17),
    'beam':        dict(base=(0.0, 0.0, 0.0), emit=(1.4, 1.05, 0.62), alpha=0.035),
    'blade_edge':  dict(base=(0.0, 0.0, 0.0), emit=(1.6, 0.9, 1.5)),
    'sun_disc':    dict(base=(0.0, 0.0, 0.0), emit=(7.0, 5.2, 3.2)),
    'hall_stone':  dict(base=(0.50, 0.45, 0.41)),
    'hall_ledge':  dict(base=(0.42, 0.37, 0.33)),
    'bronze':      dict(base=(0.30, 0.21, 0.12), spec=0.6),
    'hall_floor':  dict(base=(0.66, 0.60, 0.54), spec=0.3),
    'vault_a':     dict(base=(0.0, 0.0, 0.0), emit=(1.7, 1.35, 0.95)),
    'vault_b':     dict(base=(0.0, 0.0, 0.0), emit=(0.55, 0.42, 0.32)),
    'vault_sky':   dict(base=(0.0, 0.0, 0.0), emit=(1.6, 1.9, 2.6)),
    'rose':        dict(base=(0.0, 0.0, 0.0), emit=(2.2, 1.4, 0.9)),
    'lantern':     dict(base=(0.0, 0.0, 0.0), emit=(3.0, 2.2, 1.2)),
    'people':      dict(base=(0.0, 0.0, 0.0), emit=(0.75, 0.55, 0.35)),
}

# ------------------------------------------------------------------ nave definition
X0, X1 = -2300.0, 2300.0
K = 30                      # tiers per wall
NS = 230                    # sections along nave
FIN_L = 190.0

_k = np.arange(K)
_wh = (1.35 - 0.7 * _k / K) * (1 + 0.30 * np.sin(1.7 * _k))
WH = _wh / _wh.sum()
_wb = 0.6 + 0.4 * (0.5 + 0.5 * np.sin(0.9 * _k + 1.1))
_wb[6::7] *= 3.2
WB = _wb / _wb.sum()
PLAZA_TIERS = list(range(6, K, 7))
M_OUT = 26


def nave_xy(t):
    return X0 + (X1 - X0) * t, 300.0 * np.sin(2 * np.pi * 0.7 * t)


def nave_tan(t):
    dx = (X1 - X0)
    dy = 300.0 * 2 * np.pi * 0.7 * np.cos(2 * np.pi * 0.7 * t)
    n = np.hypot(dx, dy)
    return dx / n, dy / n


def floor_h(t):
    f = 250.0 * (1 - np.asarray(t, float)) ** 1.4
    q = f / 22.0
    fl = np.floor(q)
    return 22.0 * (fl + smoothstep(0.78, 1.0, q - fl))


def nave_w(t):
    return 420.0 + 560.0 * smoothstep(0.72, 1.0, t) + 300.0 * (1 - smoothstep(0.0, 0.22, t))


def H_N(t):
    return 2000.0 + 700.0 * (1 - t) + 950.0 * np.exp(-((t - 0.30) / 0.16) ** 2)


def H_S(t):
    gap = smoothstep(0.29, 0.33, t) * (1 - smoothstep(0.80, 0.84, t))
    return 0.74 * H_N(t) * (1 - 0.80 * gap)


def fin_fn(t, s, phase):
    return 62.0 * np.maximum(0.0, np.cos(2 * np.pi * (s + phase) / FIN_L)) ** 1.5 * smoothstep(0.05, 0.12, t)


def wall_prof(H, whalf, f, s, lscale, finamp):
    H = np.asarray(H, float)
    n = len(H)
    hk = H[:, None] * WH[None, :]
    zc = np.cumsum(hk, 1)
    lat_total = (0.30 * H + 120.0) * lscale
    bk = lat_total[:, None] * WB[None, :]
    lc = np.cumsum(bk, 1)
    l0 = lc - bk
    J_in = 2 * K + 1
    lam = np.zeros((n, J_in))
    zz = np.zeros((n, J_in))
    lam[:, 1::2] = l0
    zz[:, 1::2] = zc
    lam[:, 2::2] = lc
    zz[:, 2::2] = zc
    zz[:, 0] = -30.0
    g = np.clip(1 - zz / (0.55 * H[:, None]), 0, 1) ** 1.2
    lam_in = whalf[:, None] + lam - finamp[:, None] * g
    u = np.linspace(1.0 / M_OUT, 1.0, M_OUT)
    lamc = whalf + lc[:, -1]
    Wout = 0.24 * H + 220.0
    flute = (62.0 * (H / 3000.0))[:, None] * (np.sin(2 * np.pi * s[:, None] / 150.0 + 0.9 * u[None, :]) * 0.8 + 0.45 * np.sin(2 * np.pi * s[:, None] / 410.0 + 3.0 * u[None, :])) * (np.sin(np.pi * u) ** 0.7)[None, :]
    lam_out = lamc[:, None] + Wout[:, None] * u[None, :] + flute
    z_out = (H + f)[:, None] * (1 - u) ** 1.55 - f[:, None]
    return np.hstack([lam_in, lam_out]), np.hstack([zz, z_out]) + f[:, None]


def _rand_mats(rng, nwin, p=(0.78, 0.16, 0.06)):
    return rng.choice(3, size=nwin, p=p)


def add_windows(S, name, coll, V, F, Kk, rng, p=(0.78, 0.16, 0.06), bias=0.0, context=False):
    if len(F) == 0:
        return
    nw = len(F) // 2
    cat = _rand_mats(rng, nw, p)
    fc = np.repeat(cat, 2)
    for ci, m in enumerate(('win_warm', 'win_cool', 'win_cyan')):
        msk = fc == ci
        if msk.any():
            v, f = sub_mesh(V, F, msk)
            S.add(f'{name}_{m}', coll, m, v, f, bias=bias, key=Kk[msk])


def ref_toward_axis(px, py):
    def f(cen):
        d = np.stack([px - cen[:, 0], py - cen[:, 1], np.zeros(len(cen))], 1)
        return d
    return f


def build_nave(S, rng):
    ts = np.linspace(0, 1, NS)
    xs, ys = nave_xy(ts)
    tx, ty = nave_tan(ts)
    nx, ny = -ty, tx
    fl = floor_h(ts)
    flw = 250.0 * (1 - ts) ** 1.4
    w = nave_w(ts)
    HN = H_N(ts)
    HS = H_S(ts)
    s = ts * (X1 - X0)
    sec = dict(ts=ts, xs=xs, ys=ys, nx=nx, ny=ny, tx=tx, ty=ty, fl=fl, flw=flw, w=w, HN=HN, HS=HS, s=s, LAM={}, Z={})
    J = 2 * K + 1 + M_OUT
    sec['J'] = J
    # nearest-centreline lookup arrays for decal refs
    for side, H, nm, phase in ((+1, HN, 'N', 0.0), (-1, HS, 'S', 0.5 * FIN_L)):
        fin = fin_fn(ts, s, phase)
        LAM, Z = wall_prof(H, w / 2, flw, s + (0 if side > 0 else 777.0), np.ones(NS), fin)
        sec['LAM'][side] = LAM
        sec['Z'][side] = Z
        P = np.stack([xs[:, None] + side * nx[:, None] * LAM, ys[:, None] + side * ny[:, None] * LAM, Z], -1)
        V, F = grid_mesh(P)
        fi, fj = face_seg(NS, J)
        riser = (fj < 2 * K) & (fj % 2 == 0)
        ledge = (fj < 2 * K) & (fj % 2 == 1)
        outer = fj >= 2 * K
        coll = 'NAVE_MASSIF_NORTH' if side > 0 else 'NAVE_MASSIF_SOUTH'
        band = outer & (((fj - 2 * K) // 3) % 2 == 1)
        for msk, mat, tag in ((riser, 'riser', 'risers'), (ledge, 'terrace', 'ledges'), (outer & ~band, 'shell', 'outer_shell'), (band, 'shell_band', 'outer_band')):
            v, f = sub_mesh(V, F, msk)
            S.add(f'{nm}_wall_{tag}', coll, mat, v, f, massif=True)
        # --- decals
        rj = [2 * k for k in range(K)]
        lj = [2 * k + 1 for k in range(K)]
        ref_c = None
        # reference toward the centreline per section: use per-cell section index via nearest x on centreline
        def ref(cen, xs=xs, ys=ys):
            idx = np.clip(np.searchsorted(xs, cen[:, 0]), 0, NS - 1)
            return np.stack([xs[idx] - cen[:, 0], ys[idx] - cen[:, 1], np.zeros(len(cen))], 1)
        Vw, Fw, Kw = quad_decals(P, rj, [(0.12, 0.46), (0.56, 0.9)], [(0.10, 0.27), (0.38, 0.55), (0.66, 0.83)],
                                 0.7, ref, keep=0.62, rng=rng)
        add_windows(S, f'{nm}_win', 'LIGHT_DECALS', Vw, Fw, Kw, rng)
        # promenade light lines on every ledge lip
        Vl, Fl, Kl = quad_decals(P, lj, [(0.0, 1.0)], [(0.0, 0.05)], 0.9, lambda c: np.tile([0, 0, 1.0], (len(c), 1)))
        S.add(f'{nm}_ledge_lights', 'LIGHT_DECALS', 'edge_light', Vl, Fl, key=Kl)
        # gardens
        pl = [2 * k + 1 for k in PLAZA_TIERS]
        ot = [j for j in lj if j not in pl]
        up_ = lambda c: np.tile([0, 0, 1.0], (len(c), 1))
        Vg, Fg, Kg = quad_decals(P, pl, [(0.04, 0.17), (0.22, 0.35), (0.40, 0.53), (0.58, 0.71), (0.76, 0.89)], [(0.12, 0.34), (0.66, 0.9)], 0.5,
                                 up_, keep=0.55, rng=rng)
        S.add(f'{nm}_gardens_plaza', 'LIGHT_DECALS', 'garden', Vg, Fg, key=Kg)
        Vg, Fg, Kg = quad_decals(P, pl, [(0.05, 0.16), (0.30, 0.41), (0.55, 0.66), (0.80, 0.91)], [(0.47, 0.53)], 0.7, up_)
        S.add(f'{nm}_plaza_path_lights', 'LIGHT_DECALS', 'edge_light', Vg, Fg, key=Kg)
        Vg, Fg, Kg = quad_decals(P, ot, [(0.1, 0.45), (0.55, 0.9)], [(0.25, 0.8)], 0.5,
                                 lambda c: np.tile([0, 0, 1.0], (len(c), 1)), keep=0.10, rng=rng)
        S.add(f'{nm}_gardens_ledge', 'LIGHT_DECALS', 'garden', Vg, Fg, key=Kg)
        # outer shell gold seams (contour lines of light)
        sj = [2 * K + 1 + m for m in range(0, M_OUT - 1, 3)]
        def ref_out(cen, xs=xs, ys=ys, side=side):
            idx = np.clip(np.searchsorted(xs, cen[:, 0]), 0, NS - 1)
            return np.stack([cen[:, 0] - xs[idx], cen[:, 1] - ys[idx], np.full(len(cen), 0.35)], 1)
        Vs_, Fs_, Ks_ = quad_decals(P, sj, [(0.0, 1.0)], [(0.0, 0.07)], 1.2, ref_out)
        S.add(f'{nm}_shell_seams', 'LIGHT_DECALS', 'seam', Vs_, Fs_, key=Ks_)
        # outer-face window belts (foot city seen from outside) : lower 60% of the outer shell
        oj = [2 * K + m for m in range(0, 14)]
        Vo, Fo, Ko = quad_decals(P, oj, [(0.15, 0.85)], [(0.25, 0.7)], 1.0, ref_out, keep=0.30, rng=rng)
        add_windows(S, f'{nm}_outwin', 'LIGHT_DECALS', Vo, Fo, Ko, rng, p=(0.85, 0.10, 0.05))
        # crest light line (knife-edge ridge)
        Vcr, Fcr = grid_mesh(np.stack([P[:, 2 * K, :] + [0, 0, 2.0], P[:, 2 * K + 1, :] + [0, 0, 1.5]], 1))
        S.add(f'{nm}_crest_light', 'LIGHT_DECALS', 'crest_light', Vcr, Fcr, bias=3.0)
    # ---- floor + canal
    lat = np.array([-1, -0.0, 1.0])
    Pf_rows = []
    lats = [-1.0, -34.0, 34.0, 1.0]  # fractions of w/2 handled below
    PL = np.stack([xs - nx * (w / 2 + 6), ys - ny * (w / 2 + 6), fl], -1)
    PM1 = np.stack([xs - nx * 34, ys - ny * 34, fl], -1)
    PM2 = np.stack([xs + nx * 34, ys + ny * 34, fl], -1)
    PR = np.stack([xs + nx * (w / 2 + 6), ys + ny * (w / 2 + 6), fl], -1)
    for nm, A, B in (('floor_S', PL, PM1), ('floor_N', PM2, PR)):
        V, F = grid_mesh(np.stack([A, B], 1))
        S.add(nm, 'NAVE_FLOOR_CANAL', 'plaza', V, F, massif=True)
    Vc, Fc = grid_mesh(np.stack([PM1 + [0, 0, 0.8], PM2 + [0, 0, 0.8]], 1))
    S.add('canal_cascade', 'NAVE_FLOOR_CANAL', 'canal', Vc, Fc, bias=2.0)
    return sec


def build_apse(S, sec, rng):
    nA = 37
    psi = np.linspace(0, np.pi, nA)
    u = psi / np.pi
    H0n, H0s = sec['HN'][0], sec['HS'][0]
    HA = H0n * (1 - u) + H0s * u + 700.0 * np.sin(np.pi * u)
    lscale = 1 - 0.90 * np.exp(-((u - 0.5) / 0.13) ** 2)
    w0, f0 = sec['w'][0], sec['flw'][0]
    LAM, Z = wall_prof(HA, np.full(nA, w0 / 2), np.full(nA, f0), psi * 560.0 + 91.0, lscale, np.zeros(nA))
    n0 = np.array([sec['nx'][0], sec['ny'][0]])
    T0 = np.array([sec['tx'][0], sec['ty'][0]])
    xc, yc = sec['xs'][0], sec['ys'][0]
    e = n0[None, :] * np.cos(psi)[:, None] - T0[None, :] * np.sin(psi)[:, None]
    P = np.stack([xc + e[:, 0:1] * LAM, yc + e[:, 1:2] * LAM, Z], -1)
    V, F = grid_mesh(P)
    J = LAM.shape[1]
    fi, fj = face_seg(nA, J)
    riser = (fj < 2 * K) & (fj % 2 == 0)
    ledge = (fj < 2 * K) & (fj % 2 == 1)
    outer = fj >= 2 * K
    band = outer & (((fj - 2 * K) // 3) % 2 == 1)
    for msk, mat, tag in ((riser, 'riser', 'risers'), (ledge, 'terrace', 'ledges'), (outer & ~band, 'shell', 'outer_shell'), (band, 'shell_band', 'outer_band')):
        v, f = sub_mesh(V, F, msk)
        S.add(f'apse_{tag}', 'APSE_SACRED_FACE', mat, v, f, massif=True)
    rj = [2 * k for k in range(K)]
    lj = [2 * k + 1 for k in range(K)]
    ref = ref_toward_axis(xc, yc)
    def keepfun(cen):
        ang = np.arctan2(cen[:, 1] - yc, cen[:, 0] - xc)
        # sacred face (west direction) has no windows
        wdir = np.arctan2(-T0[1], -T0[0])
        dd = np.abs(np.angle(np.exp(1j * (ang - wdir))))
        return np.where(dd < 0.33, 0.0, 0.62)
    Vw, Fw, Kw = quad_decals(P, rj, [(0.12, 0.46), (0.56, 0.9)], [(0.10, 0.27), (0.38, 0.55), (0.66, 0.83)], 0.7, ref,
                             keep=keepfun, rng=rng)
    add_windows(S, 'apse_win', 'LIGHT_DECALS', Vw, Fw, Kw, rng)
    Vl, Fl, Kl = quad_decals(P, lj, [(0.0, 1.0)], [(0.0, 0.05)], 0.9, lambda c: np.tile([0, 0, 1.0], (len(c), 1)))
    S.add('apse_ledge_lights', 'LIGHT_DECALS', 'edge_light', Vl, Fl, key=Kl)
    sj = [2 * K + 1 + m for m in range(0, M_OUT - 1, 3)]
    def ref_out(cen):
        return np.stack([cen[:, 0] - xc, cen[:, 1] - yc, np.full(len(cen), 0.35)], 1)
    Vs_, Fs_, Ks_ = quad_decals(P, sj, [(0.0, 1.0)], [(0.0, 0.07)], 1.2, ref_out)
    S.add('apse_shell_seams', 'LIGHT_DECALS', 'seam', Vs_, Fs_, key=Ks_)
    Vcr, Fcr = grid_mesh(np.stack([P[:, 2 * K, :] + [0, 0, 2.0], P[:, 2 * K + 1, :] + [0, 0, 1.5]], 1))
    S.add('apse_crest_light', 'LIGHT_DECALS', 'crest_light', Vcr, Fcr, bias=3.0)
    # outer windows on apse shell
    oj = [2 * K + m for m in range(0, 14)]
    Vo, Fo, Ko = quad_decals(P, oj, [(0.15, 0.85)], [(0.25, 0.7)], 1.0, ref_out, keep=0.30, rng=rng)
    add_windows(S, 'apse_outwin', 'LIGHT_DECALS', Vo, Fo, Ko, rng, p=(0.85, 0.10, 0.05))
    # rear buttress fins: obsidian ribs climbing the apse shell and rising as sharp thorns above the crest
    fins = []
    for q, ia in enumerate(range(1, nA - 1, 2)):
        radial = np.array([e[ia, 0], e[ia, 1], 0.0])
        tdir = np.array([-radial[1], radial[0], 0.0])
        shell = P[ia, 2 * K:, :] + radial[None] * 26.0 + np.array([0, 0, 4.0])
        shell = shell[::-1]  # ground -> crest
        crest = shell[-1]
        Lh = 260.0 + 520.0 * (0.5 + 0.5 * np.sin(q * 2.3 + 0.7))
        s_ = np.linspace(0, 1, 14)[1:]
        ext = crest[None] + np.stack([radial[0] * 0.30 * Lh * s_ ** 1.5, radial[1] * 0.30 * Lh * s_ ** 1.5, Lh * s_], 1)
        path = np.vstack([shell, ext])
        n_s = len(shell)
        u_ = np.linspace(0, 1, len(path))
        w_ = np.where(np.arange(len(path)) < n_s, 78.0 * (1 - 0.35 * np.arange(len(path)) / n_s), 0)
        tail = np.arange(len(path)) >= n_s
        w_[tail] = 78.0 * 0.65 * (1 - (np.arange(len(path))[tail] - n_s + 1) / (len(path) - n_s + 0.0)) ** 0.8
        th_ = 30.0 * (1 - 0.7 * u_)
        Tg = normalize(np.gradient(path, axis=0))
        Bn = normalize(np.cross(Tg, tdir[None]))
        Pf = np.zeros((len(path), 5, 3))
        for jj, (a_, b_) in enumerate([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5), (-0.5, -0.5)]):
            Pf[:, jj] = path + (a_ * w_)[:, None] * tdir[None] + (b_ * th_)[:, None] * Bn
        fins.append(grid_mesh(Pf))
    Vf_, Ff_ = merge(fins)
    S.add('apse_rear_fins', 'APSE_SACRED_FACE', 'obsidian', Vf_, Ff_)
    # floor fan
    th = np.linspace(0, np.pi, 40)
    rim = np.stack([xc + (w0 / 2 + 6) * (n0[0] * np.cos(th) - T0[0] * np.sin(th)),
                    yc + (w0 / 2 + 6) * (n0[1] * np.cos(th) - T0[1] * np.sin(th)),
                    np.full(40, f0)], -1)
    ctr = np.array([[xc, yc, f0]])
    Vf = np.vstack([ctr, rim])
    Ff = np.array([[0, i + 1, i + 2] for i in range(39)], np.int32)
    S.add('apse_floor', 'NAVE_FLOOR_CANAL', 'plaza', Vf, Ff, massif=True)
    # sacred face disc (sun disc) + frame
    uc = 0.5
    i_mid = nA // 2
    z_disc = f0 + 1380.0
    lam_at = float(np.interp(z_disc, Z[i_mid][:2 * K + 1], LAM[i_mid][:2 * K + 1]))
    wdirv = -T0
    ctr = np.array([xc + wdirv[0] * lam_at, yc + wdirv[1] * lam_at, z_disc])
    ctr = ctr - np.array([wdirv[0], wdirv[1], 0]) * 0  # on face
    face_n = np.array([T0[0], T0[1], 0.0])  # facing east into nave
    Rd = 400.0
    cc = ctr + face_n * 45.0
    lat_v = np.array([-T0[1], T0[0], 0.0])
    ph = np.linspace(0, 2 * np.pi, 97)
    ring = cc[None] + Rd * (np.cos(ph)[:, None] * lat_v[None] + np.sin(ph)[:, None] * np.array([0, 0, 1.0])[None])
    Vd = np.vstack([cc[None], ring])
    Fd = np.array([[0, i + 1, i + 2] for i in range(96)], np.int32)
    S.add('sacred_sun_disc', 'APSE_SACRED_FACE', 'sun_disc', Vd, Fd, bias=6.0)
    # frame torus (champagne) around disc
    ringp = cc[None] + (Rd + 18) * (np.cos(ph)[:, None] * lat_v[None] + np.sin(ph)[:, None] * np.array([0, 0, 1.0])[None])
    Nn = normalize(ringp - cc[None])
    Bn = np.tile(face_n, (len(ph), 1))
    sec_ = [(-26, -30), (26, -30), (26, 30), (-26, 30)]
    Pf = sweep_grid(ringp, sec_, N=Nn, B=Bn)
    Vf_, Ff_ = grid_mesh(Pf)
    S.add('sacred_disc_frame', 'APSE_SACRED_FACE', 'champagne', Vf_, Ff_, bias=4.0)
    # concentric rays in disc (spokes)
    spokes = []
    for a in np.linspace(0, np.pi, 13)[:-1]:
        d = np.cos(a) * lat_v + np.sin(a) * np.array([0, 0, 1.0])
        Rm = np.eye(3)
        c = cc + face_n * 3.0
        sp = boxes([c], [[2 * Rd * 0.98, 7.0, 7.0]], R=np.stack([d, np.cross(face_n, d), face_n], 1))
        spokes.append(sp)
    Vs2, Fs2 = merge(spokes)
    S.add('sacred_disc_spokes', 'APSE_SACRED_FACE', 'champagne', Vs2, Fs2, bias=8.0)
    sec['disc'] = dict(center=cc, radius=Rd, normal=face_n)
    sec['apse'] = dict(xc=xc, yc=yc, f0=f0)
    # light cone from disc
    tgt = cc + face_n * 1600.0 - np.array([0, 0, 1.0]) * (cc[2] - f0 - 40) * 0.92
    ph2 = np.linspace(0, 2 * np.pi, 49)
    base = cc[None] + Rd * 0.93 * (np.cos(ph2)[:, None] * lat_v[None] + np.sin(ph2)[:, None] * np.array([0, 0, 1.0])[None])
    far = tgt[None] + 650.0 * (np.cos(ph2)[:, None] * lat_v[None] + 0.35 * np.sin(ph2)[:, None] * np.array([0, 0, 1.0])[None])
    Vb, Fb = grid_mesh(np.stack([base, far], 1))
    S.add('sacred_light_cone', 'BRIDGES_VEILS_BEAMS', 'beam', Vb, Fb, bias=0.0)
    return P, LAM, Z


def inner_wall_lat(sec, side, i, zabs):
    LAM = sec['LAM'][side][i][:2 * K + 1]
    Z = sec['Z'][side][i][:2 * K + 1]
    return float(np.interp(zabs, Z, LAM))


def wall_point(sec, side, t, zrel):
    i = int(round(t * (NS - 1)))
    zabs = sec['flw'][i] + zrel
    lam = inner_wall_lat(sec, side, i, zabs)
    return np.array([sec['xs'][i] + side * sec['nx'][i] * lam, sec['ys'][i] + side * sec['ny'][i] * lam, zabs])


# ------------------------------------------------------------------ rings
RING_SPECS = [  # t, R, yaw, pitch, lateral offset
    (0.115, 640, 12, 8, 30),
    (0.235, 760, -16, -6, -40),
    (0.355, 880, 20, 10, 60),
    (0.475, 1010, -9, -12, -30),
    (0.595, 1150, 24, 5, 50),
    (0.715, 1300, -18, 9, -60),
    (0.860, 1480, 6, -4, 20),
]


def ring_basis(sec, t, yaw, pitch, lat):
    i = int(round(t * (NS - 1)))
    T = np.array([sec['tx'][i], sec['ty'][i], 0.0])
    n = np.array([sec['nx'][i], sec['ny'][i], 0.0])
    Nr = rot_axis([0, 0, 1], np.radians(yaw)) @ T
    lat_ax = np.cross([0, 0, 1.0], Nr)
    Nr = rot_axis(lat_ax, np.radians(pitch)) @ Nr
    Nr = normalize(Nr)
    ctr_xy = np.array([sec['xs'][i], sec['ys'][i]]) + n[:2] * lat
    return i, Nr, ctr_xy


def inside_solid(sec, p):
    d = (sec['xs'] - p[0]) ** 2 + (sec['ys'] - p[1]) ** 2
    i = int(np.argmin(d))
    lam = (p[0] - sec['xs'][i]) * sec['nx'][i] + (p[1] - sec['ys'][i]) * sec['ny'][i]
    side = 1 if lam >= 0 else -1
    a = abs(lam)
    if a <= sec['w'][i] / 2:
        return p[2] < sec['fl'][i] - 25
    LAM = np.maximum.accumulate(sec['LAM'][side][i])
    Z = sec['Z'][side][i]
    if a > LAM[-1]:
        return p[2] < -25
    zs = np.interp(a, LAM + np.arange(len(LAM)) * 1e-6, Z)
    return p[2] < zs - 30


def build_rings(S, sec, rng):
    rings = []
    for ri, (t, R, yaw, pitch, lat) in enumerate(RING_SPECS):
        i, Nr, cxy = ring_basis(sec, t, yaw, pitch, lat)
        zc = sec['fl'][i] + 0.80 * R
        C = np.array([cxy[0], cxy[1], zc])
        uax = normalize(np.cross(Nr, [0, 0, 1.0]))
        vax = np.cross(Nr, uax)
        nth = int(R / 4.0) + 60
        th = np.linspace(0, 2 * np.pi, nth, endpoint=False)
        rad = np.cos(th)[:, None] * uax[None] + np.sin(th)[:, None] * vax[None]
        pts = C[None] + R * rad
        keep = np.array([not inside_solid(sec, p) for p in pts])
        # contiguous runs (circular)
        if keep.all():
            runs = [np.arange(nth)]
        else:
            start = np.where(~keep)[0][0]
            order = (np.arange(nth) + start) % nth
            runs, cur = [], []
            for idx in order:
                if keep[idx]:
                    cur.append(idx)
                else:
                    if len(cur) > 2:
                        runs.append(np.array(cur))
                    cur = []
            if len(cur) > 2:
                runs.append(np.array(cur))
        a, b = 0.17 * R, 0.12 * R
        secpoly = np.array([(-a / 2, -0.2 * b), (-a * 0.275, -b / 2), (a * 0.275, -b / 2), (a / 2, -0.2 * b),
                            (a / 2, 0.2 * b), (a * 0.275, b / 2), (-a * 0.275, b / 2), (-a / 2, 0.2 * b)])
        for rr, run in enumerate(runs):
            if len(run) < 3:
                continue
            path = pts[run]
            N = rad[run]
            B = np.tile(Nr, (len(run), 1))
            P = sweep_grid(path, secpoly, N=N, B=B)
            V, F = grid_mesh(P)
            fi, fj = face_seg(len(run), P.shape[1])
            glow = fj == 7
            v, f = sub_mesh(V, F, ~glow)
            S.add(f'halo{ri + 1}_body_{rr}', 'SEVEN_HALOS', 'champagne', v, f)
            v, f = sub_mesh(V, F, glow)
            S.add(f'halo{ri + 1}_inner_glow_{rr}', 'SEVEN_HALOS', 'halo_glow', v, f)
            # windows on flat faces
            Cc = C.copy()
            def ref(cen, Cc=Cc, Nr=Nr):
                s_ = np.sign((cen - Cc) @ Nr)
                s_[s_ == 0] = 1
                return s_[:, None] * Nr[None]
            Vw, Fw, Kw = quad_decals(P, [1, 5], [(0.1, 0.5), (0.58, 0.95)], [(0.2, 0.8)], 0.8, ref, keep=0.55, rng=rng)
            add_windows(S, f'halo{ri + 1}_win{rr}', 'LIGHT_DECALS', Vw, Fw, Kw, rng, p=(0.6, 0.25, 0.15))
            # outer teeth
            m = max(8, int(len(run) / 2))
            sel = run[::2]
            cen = pts[sel] + rad[sel] * (a / 2 + 0.05 * R)
            Rm = np.stack([rad[sel], np.cross(Nr[None], rad[sel]), np.tile(Nr, (len(sel), 1))], 2)
            Vt, Ft = boxes(cen, [0.10 * R, 0.035 * R, 0.8 * b], R=Rm)
            S.add(f'halo{ri + 1}_teeth{rr}', 'SEVEN_HALOS', 'champagne', Vt, Ft)
        rings.append(dict(C=C, R=R, u=uax, v=vax, N=Nr, t=t, i=i))
    sec['rings'] = rings
    return rings


# ------------------------------------------------------------------ obsidian blades
def make_blade(base, height, w0, th0, yaw, lean_dir, lean, seg=16):
    u = np.linspace(0, 1, seg)
    width = w0 * (1 - u ** 0.85) * (1 - 0.18 * np.sin(np.pi * u))
    thick = th0 * (1 - u) ** 0.9
    c = base[None] + np.stack([lean_dir[0] * lean * u ** 1.6, lean_dir[1] * lean * u ** 1.6, height * u], 1)
    ax = np.array([np.cos(yaw), np.sin(yaw), 0.0])
    bx = np.array([-np.sin(yaw), np.cos(yaw), 0.0])
    sec4 = np.array([(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)])
    P = np.zeros((seg, 5, 3))
    for k in range(5):
        a_, b_ = sec4[k % 4]
        P[:, k] = c + (a_ * width)[:, None] * ax[None] + (b_ * thick)[:, None] * bx[None]
    V, F = grid_mesh(P)
    # glowing leading edge: thin strip down the +ax edge
    e0 = c + (0.5 * width)[:, None] * ax[None]
    Pe = np.stack([e0 + (0.5 * thick + 0.15)[:, None] * bx[None], e0 - (0.5 * thick + 0.15)[:, None] * bx[None]], 1)
    Ve, Fe = grid_mesh(Pe)
    return V, F, Ve, Fe


def build_blades(S, sec, rng):
    spec = []
    for t, hh, w0, lean in [(0.045, 880, 190, 150), (0.13, 1180, 240, 260), (0.215, 1480, 200, 330),
                            (0.30, 2050, 150, 420), (0.385, 1250, 260, 280), (0.505, 820, 210, 160), (0.65, 640, 180, 130)]:
        spec.append((+1, t, hh, w0, lean))
    for t, hh, w0, lean in [(0.04, 700, 200, -120), (0.17, 980, 170, -200), (0.905, 520, 150, -100)]:
        spec.append((-1, t, hh, w0, lean))
    for si, (side, t, hh, w0, lean) in enumerate(spec):
        i = int(round(t * (NS - 1)))
        crest = np.array([sec['xs'][i] + side * sec['nx'][i] * (sec['LAM'][side][i][2 * K] + 40),
                          sec['ys'][i] + side * sec['ny'][i] * (sec['LAM'][side][i][2 * K] + 40),
                          sec['Z'][side][i][2 * K] - 50.0])
        outdir = np.array([side * sec['nx'][i], side * sec['ny'][i]])
        if side > 0 and t > 0.25 and t < 0.35:
            outdir = np.array([-sec['tx'][i] * 0.8 + outdir[0] * 0.3, -sec['ty'][i] * 0.8 + outdir[1] * 0.3])
        yaw = np.arctan2(sec['ty'][i], sec['tx'][i]) + np.radians(rng.uniform(-35, 35))
        V, F, Ve, Fe = make_blade(crest, hh, w0, 0.16 * w0 + 12, yaw, outdir, abs(lean))
        S.add(f'blade_{si:02d}', 'OBSIDIAN_BLADES', 'obsidian', V, F)
        S.add(f'blade_{si:02d}_edge', 'OBSIDIAN_BLADES', 'blade_edge', Ve, Fe, bias=2.0)


# ------------------------------------------------------------------ floating islands / sanctum lens
def place(V, Rm, c):
    return V @ Rm.T + np.asarray(c)


def build_island(S, name, coll, center, R, th_top, th_bot, tilt_axis, tilt_deg, nterr, nbot, rng,
                 n_spires=6, n_domes=8, nth=72, hanging=True):
    Rm = rot_axis(tilt_axis, np.radians(tilt_deg))
    rs = R * np.linspace(1, 0, nterr + 1) ** 0.85
    zs = th_top * np.linspace(0, 1, nterr + 1) ** 0.7
    pt = [(rs[0], zs[0])]
    for j in range(1, nterr + 1):
        pt.append((rs[j - 1], zs[j]))
        pt.append((rs[j], zs[j]))
    pt = np.array(pt)
    P = revolve_grid(pt, nth)
    V, F = grid_mesh(P)
    fi, fj = face_seg(nth + 1, len(pt))
    ris = fj % 2 == 0
    led = ~ris
    def T(Vx):
        return place(Vx, Rm, center)
    v, f = sub_mesh(V, F, ris)
    S.add(f'{name}_top_risers', coll, 'riser', T(v), f)
    v, f = sub_mesh(V, F, led)
    S.add(f'{name}_top_ledges', coll, 'terrace', T(v), f)
    radial = lambda c: np.stack([c[:, 0], c[:, 1], np.zeros(len(c))], 1)
    rj = [j for j in range(len(pt) - 1) if j % 2 == 0]
    Vw, Fw, Kw = quad_decals(P, rj, [(0.1, 0.45), (0.55, 0.9)], [(0.12, 0.3), (0.4, 0.6), (0.7, 0.88)], 0.6, radial,
                             keep=0.62, rng=rng)
    add_windows(S, f'{name}_win', 'LIGHT_DECALS', T(Vw), Fw, T(Kw), rng)
    lj = [j for j in range(len(pt) - 1) if j % 2 == 1]
    Vl, Fl, Kl = quad_decals(P, lj, [(0.0, 1.0)], [(0.0, 0.06)], 0.8, lambda c: np.tile([0, 0, 1.0], (len(c), 1)))
    S.add(f'{name}_ledge_lights', 'LIGHT_DECALS', 'edge_light', T(Vl), Fl, key=T(Kl))
    Vg, Fg, Kg = quad_decals(P, lj, [(0.03, 0.2), (0.25, 0.45), (0.5, 0.7), (0.75, 0.95)], [(0.25, 0.85)], 0.5,
                             lambda c: np.tile([0, 0, 1.0], (len(c), 1)), keep=0.55, rng=rng)
    S.add(f'{name}_gardens', 'LIGHT_DECALS', 'garden', T(Vg), Fg, key=T(Kg))
    # domes (pavilion shells) on upper ledges
    Vd_all = []
    for d in range(n_domes):
        j = rng.integers(1, nterr + 1)
        rr = rng.uniform(0.15, 0.85) * rs[j - 1]
        a = rng.uniform(0, 2 * np.pi)
        rad_d = rng.uniform(0.02, 0.05) * R + 8
        prof = np.array([(rad_d, 0), (rad_d * 0.95, rad_d * 0.5), (rad_d * 0.7, rad_d * 0.95), (rad_d * 0.3, rad_d * 1.25), (0, rad_d * 1.35)])
        Pd = revolve_grid(prof, 14)
        Vd, Fd = grid_mesh(Pd)
        Vd = Vd + np.array([rr * np.cos(a), rr * np.sin(a), zs[j]])
        Vd_all.append((Vd, Fd))
    Vd, Fd = merge(Vd_all)
    S.add(f'{name}_domes', coll, 'champagne', T(Vd), Fd)
    # underside
    rb = R * np.linspace(1, 0, nbot + 1) ** 1.3
    zb = -th_bot * np.linspace(0, 1, nbot + 1) ** 1.6
    pb = [(rb[0], 0.0)]
    for j in range(1, nbot + 1):
        pb.append((rb[j - 1] * 0.96, zb[j]))
        pb.append((rb[j], zb[j]))
    pb = np.array(pb)
    Pb = revolve_grid(pb, nth)
    Vb, Fb = grid_mesh(Pb)
    S.add(f'{name}_underside', coll, 'underside', T(Vb), Fb)
    lb = [j for j in range(len(pb) - 1) if j % 2 == 1]
    Vu, Fu, Ku = quad_decals(Pb, lb, [(0.0, 1.0)], [(0.82, 0.96)], -0.8, lambda c: np.tile([0, 0, -1.0], (len(c), 1)))
    S.add(f'{name}_under_glow', 'LIGHT_DECALS', 'under_glow', T(Vu), Fu, key=T(Ku))
    # spires
    if hanging:
        sp = []
        for q in range(n_spires):
            a = 2 * np.pi * q / n_spires + rng.uniform(-0.2, 0.2)
            rr = R * rng.uniform(0.42, 0.78)
            zu = float(np.interp(rr, rb[::-1], zb[::-1]))
            L = th_bot * rng.uniform(0.30, 0.55)
            rs_ = 0.085 * R + 8
            prof = np.array([(0, -L), (0.10 * rs_, -0.70 * L), (0.45 * rs_, -0.30 * L), (rs_, 0.0)])
            Pp = revolve_grid(prof, 12)
            Vp, Fp = grid_mesh(Pp)
            Vp = Vp + np.array([rr * np.cos(a), rr * np.sin(a), zu + 6])
            sp.append((Vp, Fp))
        prof = np.array([(0, -th_bot * 1.65), (0.02 * R, -th_bot * 1.2), (0.06 * R, -th_bot * 0.6), (0.11 * R, -th_bot * 0.1)])
        Pp = revolve_grid(prof, 16)
        Vp, Fp = grid_mesh(Pp)
        sp.append((Vp + np.array([0, 0, zb[-1] * 0.5]), Fp))
        Vs_, Fs_ = merge(sp)
        S.add(f'{name}_spires', coll, 'obsidian', T(Vs_), Fs_)
    return dict(center=np.array(center, float), R=R, th_top=th_top, Rm=Rm)


def build_islands(S, sec, rng):
    isl = {}
    i = int(round(0.075 * (NS - 1)))
    cx, cy = sec['xs'][i], sec['ys'][i]
    zc = sec['fl'][i] + 880
    isl['lens'] = build_island(S, 'sanctum_lens', 'SANCTUM_LENS', (cx, cy, zc), 520, 150, 420, [0, 1, 0], 7, 9, 7, rng,
                               n_spires=9, n_domes=16, nth=96)
    for k, (t, lat, hh, R, ang, ax) in enumerate([(0.40, -1650, 880, 470, 13, [1, 0.3, 0]), (0.58, -1500, 1180, 380, -17, [0.2, 1, 0]),
                                                  (0.745, -1750, 720, 320, 21, [1, -0.4, 0]), (0.25, -1450, 1560, 200, -9, [0, 1, 0])]):
        i = int(round(t * (NS - 1)))
        c = (sec['xs'][i] + sec['nx'][i] * lat, sec['ys'][i] + sec['ny'][i] * lat, hh)
        isl[f'isle{k}'] = build_island(S, f'sky_isle_{k + 1}', 'FLOATING_DISTRICTS', c, R, 0.30 * R, 1.05 * R, ax, ang,
                                       6, 6, rng, n_spires=3, n_domes=6, nth=72)
    sec['islands'] = isl
    return isl


# ------------------------------------------------------------------ bridges / veils / beams
def bridge(S, name, A, B, rise, width=26.0, coll='BRIDGES_VEILS_BEAMS', interior=False):
    A = np.asarray(A, float)
    B = np.asarray(B, float)
    n = 60
    tt = np.linspace(0, 1, n)
    path = A[None] + (B - A)[None] * tt[:, None] + np.array([0, 0, 1.0])[None] * (rise * 4 * tt * (1 - tt))[:, None]
    deck = [(-width / 2, 0), (width / 2, 0), (width / 2, 5), (-width / 2, 5)]
    d = B - A
    Nn = normalize(np.cross([0, 0, 1.0], d))[None].repeat(n, 0)
    Bn = np.tile([0, 0, 1.0], (n, 1))
    P = sweep_grid(path, deck, N=Nn, B=Bn)
    V, F = grid_mesh(P)
    S.add(name + '_deck', coll, 'riser', V, F, interior=interior)
    glow = [(-1.2, 5.4), (1.2, 5.4), (1.2, 6.2), (-1.2, 6.2)]
    P = sweep_grid(path, glow, N=Nn, B=Bn)
    V, F = grid_mesh(P)
    S.add(name + '_deckline', coll, 'edge_light', V, F, interior=interior)
    sag = rise * 0.8 + 30
    path2 = A[None] + (B - A)[None] * tt[:, None] - np.array([0, 0, 1.0])[None] * (sag * 4 * tt * (1 - tt) ** 1)[:, None] + np.array([0, 0, 1.0])[None] * (rise * 4 * tt * (1 - tt))[:, None] * 0.0
    arch = [(-4, -4), (4, -4), (4, 4), (-4, 4)]
    P = sweep_grid(path2, arch, N=Nn, B=Bn)
    V, F = grid_mesh(P)
    S.add(name + '_arch', coll, 'champagne', V, F, interior=interior)
    # hangers
    idx = np.arange(4, n - 3, 4)
    top = path[idx]
    bot = path2[idx]
    cen = (top + bot) / 2
    hh = np.linalg.norm(top - bot, axis=1)
    Vh, Fh = boxes(cen, np.stack([np.full(len(idx), 2.0), np.full(len(idx), 2.0), np.maximum(hh, 1.0)], 1))
    S.add(name + '_hangers', coll, 'champagne', Vh, Fh, interior=interior)


def build_bridges(S, sec):
    for k, (t, zr) in enumerate([(0.045, 330), (0.135, 580), (0.215, 820), (0.905, 260), (0.955, 520)]):
        A = wall_point(sec, +1, t, zr)
        B = wall_point(sec, -1, t, zr)
        bridge(S, f'bridge{k + 1}', A, B, 40 + 18 * k)


def build_veils(S, sec):
    for k in (1, 3, 5):
        r = sec['rings'][k]
        th = np.radians(np.linspace(22, 158, 46))
        L = 330.0
        vv = np.linspace(0, 1, 9)
        P = np.zeros((len(th), len(vv), 3))
        for a, t_ in enumerate(th):
            top = r['C'] + r['R'] * (np.cos(t_) * r['u'] + np.sin(t_) * r['v'])
            if top[2] < r['C'][2]:
                top = r['C'] + r['R'] * (np.cos(-t_) * r['u'] + np.sin(-t_) * r['v'])
            for b, v_ in enumerate(vv):
                P[a, b] = top + np.array([0, 0, -L * v_ * (0.6 + 0.4 * np.sin(5 * t_))]) + r['N'] * 26 * np.sin(4 * t_ + 3 * v_) * v_
        V, F = grid_mesh(P)
        S.add(f'veil_{k + 1}', 'BRIDGES_VEILS_BEAMS', 'veil', V, F)


def build_beams(S, sec):
    # slanted sun shafts through the nave from the crest gap
    for k, t in enumerate([0.22, 0.37, 0.52, 0.64, 0.78]):
        i = int(round(t * (NS - 1)))
        top = np.array([sec['xs'][i] + 500 + 120 * k, sec['ys'][i] - 500 - 80 * k, 3000.0 - 120 * k])
        bot = np.array([sec['xs'][i] - 260, sec['ys'][i] + 120, sec['fl'][i] + 10])
        d = bot - top
        side = normalize(np.cross(d, [0, 0, 1.0])) * (80 + 15 * k)
        up = normalize(np.cross(d, side)) * 40
        Q = np.array([top - side, top + side, bot + side * 2.2, bot - side * 2.2])
        S.add(f'sunshaft_{k + 1}', 'BRIDGES_VEILS_BEAMS', 'beam',
              Q, np.array([[0, 1, 2], [0, 2, 3]], np.int32))


# ------------------------------------------------------------------ terrain / sea / roads (context)
def ground_h(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    r = np.hypot(x, y)
    n = (60 * np.sin(x / 1900 + 1.3) * np.cos(y / 2300 + 0.7) + 35 * np.sin(x / 700 + y / 900) + 25 * np.cos(y / 520 - x / 1300))
    mt = np.clip((r - 7500) / 5500, 0, 1) ** 1.6
    mount = 1500 * mt * (0.55 + 0.45 * np.sin(x / 1500 + 2.0) * np.cos(y / 1700 - 1.0)) * (0.5 + 0.5 * np.cos(np.arctan2(y, x) - 2.4))
    flat = smoothstep(2800, 6500, r)
    h = n * flat + mount
    sea = smoothstep(2500, 3300, x) * (1 - smoothstep(6500, 9500, np.abs(y) + 0.0 * x))
    return h * (1 - sea) - 55.0 * sea


def build_terrain(S, sec, rng):
    xs = np.concatenate([np.arange(-16000, -7000, 700.0), np.arange(-7000, 7000, 200.0), np.arange(7000, 16001, 700.0)])
    ys = np.concatenate([np.arange(-16000, -7000, 700.0), np.arange(-7000, 7000, 200.0), np.arange(7000, 16001, 700.0)])
    X, Y = np.meshgrid(xs, ys, indexing='ij')
    Z = ground_h(X, Y)
    P = np.stack([X, Y, Z], -1)
    V, F = grid_mesh(P)
    fi, fj = face_seg(len(xs), len(ys))
    cx = (xs[fi] + xs[np.minimum(fi + 1, len(xs) - 1)]) / 2
    cy = (ys[fj] + ys[np.minimum(fj + 1, len(ys) - 1)]) / 2
    sea = (cx > 2800) & (np.abs(cy) < 8000)
    v, f = sub_mesh(V, F, ~sea)
    S.add('terrain_land', 'TERRAIN_CONTEXT', 'ground', v, f, bias=-300.0, context=True)
    # sea: flat tiles at z=0
    xs2 = np.arange(2200, 16001, 400.0)
    ys2 = np.arange(-9500, 9501, 400.0)
    X2, Y2 = np.meshgrid(xs2, ys2, indexing='ij')
    P2 = np.stack([X2, Y2, np.full_like(X2, 0.0)], -1)
    V2, F2 = grid_mesh(P2)
    S.add('inland_sea', 'TERRAIN_CONTEXT', 'water', V2, F2, bias=-250.0, context=True)
    # causeway into the sea + arterial roads (emissive ribbons)
    def ribbon(name, pts, width, mat, dz=2.5, bias=2.0):
        pts = np.asarray(pts, float)
        T = normalize(np.gradient(pts, axis=0))
        Nn = np.stack([-T[:, 1], T[:, 0], np.zeros(len(T))], 1)
        P_ = np.stack([pts - Nn * width / 2, pts + Nn * width / 2], 1)
        P_[..., 2] += dz
        V_, F_ = grid_mesh(P_)
        S.add(name, 'TERRAIN_CONTEXT', mat, V_, F_, bias=bias, context=True)
    xx = np.linspace(2300, 15500, 120)
    ribbon('causeway', np.stack([xx, 60 * np.sin(xx / 1800), np.zeros_like(xx)], 1), 90, 'road_glow', dz=6.0)
    for k, (a0, curl) in enumerate([(0.6, 0.3), (1.15, -0.25), (1.85, 0.2), (2.6, -0.3), (3.4, 0.25), (4.2, -0.2), (5.0, 0.28)]):
        rr = np.linspace(3300, 15500, 140)
        ang = a0 + curl * np.sin(rr / 2500 + k)
        px, py = rr * np.cos(ang), rr * np.sin(ang)
        pts = np.stack([px, py, ground_h(px, py)], 1)
        ok = ~((px > 2800) & (np.abs(py) < 8000))
        if ok.sum() > 3:
            ribbon(f'artery_{k}', pts[ok], 40, 'road_glow', dz=3.0)
    # light carpets (context placeholder: flat lit districts, NOT detailed design)
    n_c = 9000
    r = rng.gamma(2.2, 2200, n_c) + 2500
    a = rng.uniform(0, 2 * np.pi, n_c)
    px, py = r * np.cos(a), r * np.sin(a)
    # exclude massif footprint and sea
    d2 = (sec['xs'][None] - px[:, None]) ** 2 + (sec['ys'][None] - py[:, None]) ** 2
    ii = np.argmin(d2, 1)
    lam = np.abs((px - sec['xs'][ii]) * sec['nx'][ii] + (py - sec['ys'][ii]) * sec['ny'][ii])
    inside = (px > X0 - 2600) & (px < X1 + 400) & (lam < 3300)
    sea_m = (px > 2800) & (np.abs(py) < 8000)
    ok = (~inside) & (~sea_m) & (r < 14500)
    px, py = px[ok], py[ok]
    gz = ground_h(px, py) + 1.5
    sz = np.stack([rng.uniform(30, 90, len(px)), rng.uniform(18, 50, len(px)), np.full(len(px), 0.4)], 1)
    ang = rng.uniform(0, np.pi, len(px))
    Rm = np.zeros((len(px), 3, 3))
    Rm[:, 0, 0] = np.cos(ang); Rm[:, 0, 1] = -np.sin(ang); Rm[:, 1, 0] = np.sin(ang); Rm[:, 1, 1] = np.cos(ang); Rm[:, 2, 2] = 1
    Vc, Fc = boxes(np.stack([px, py, gz], 1), sz, R=Rm)
    cool = rng.random(len(px)) < 0.28
    fc = np.repeat(cool, 12)
    v, f = sub_mesh(Vc, Fc, ~fc)
    S.add('district_carpets_warm', 'TERRAIN_CONTEXT', 'carpet_warm', v, f, bias=1.0, context=True)
    v, f = sub_mesh(Vc, Fc, fc)
    S.add('district_carpets_cool', 'TERRAIN_CONTEXT', 'carpet_cool', v, f, bias=1.0, context=True)


def build_people(S, sec, rng, n=7000):
    ii = rng.integers(0, NS, n)
    lat = rng.uniform(-1, 1, n) * (sec['w'][ii] / 2 - 25)
    lat = np.where(np.abs(lat) < 40, np.sign(lat + 1e-9) * 40 + lat, lat)
    px = sec['xs'][ii] + sec['nx'][ii] * lat
    py = sec['ys'][ii] + sec['ny'][ii] * lat
    pz = sec['fl'][ii] + 0.3
    qa = []
    for ang in (0.0, np.pi / 2):
        d = np.array([np.cos(ang), np.sin(ang), 0.0])
        v = np.zeros((n, 4, 3))
        base = np.stack([px, py, pz], 1)
        v[:, 0] = base - d * 0.45
        v[:, 1] = base + d * 0.45
        v[:, 2] = base + d * 0.45 + [0, 0, 1.85]
        v[:, 3] = base - d * 0.45 + [0, 0, 1.85]
        qa.append(v)
    v = np.concatenate(qa)
    m = len(v)
    b = np.arange(m) * 4
    F = np.stack([np.stack([b, b + 1, b + 2], 1), np.stack([b, b + 2, b + 3], 1)], 1).reshape(-1, 3)
    S.add('nave_people', 'NAVE_FLOOR_CANAL', 'people', v.reshape(-1, 3), F, bias=0.5)


def build_plazas(S, sec, rng):
    xs, ys, nx, ny, tx, ty = sec['xs'], sec['ys'], sec['nx'], sec['ny'], sec['tx'], sec['ty']
    trees, domes, pp, cols = [], [], [], []
    for side in (1, -1):
        LAM, Z = sec['LAM'][side], sec['Z'][side]
        for k in PLAZA_TIERS:
            l0, l1, zc = LAM[:, 2 * k + 1], LAM[:, 2 * k + 2], Z[:, 2 * k + 1]
            idx0 = np.where((l1 - l0) > 30)[0]
            idx = idx0[::2]
            if len(idx) == 0:
                continue
            for rep in range(8):
                fr = rng.uniform(0.15, 0.85, len(idx))
                lam = l0[idx] + fr * (l1[idx] - l0[idx])
                jit = rng.uniform(-14, 14, len(idx))
                x = xs[idx] + side * nx[idx] * lam + tx[idx] * jit
                y = ys[idx] + side * ny[idx] * lam + ty[idx] * jit
                rad = rng.uniform(3.2, 5.6, len(idx))
                trees.append((np.stack([x, y, zc[idx] + rad * 1.6], 1), rad))
            # pavilions
            sel = idx[rng.random(len(idx)) < 0.55]
            for i in sel:
                wd = l1[i] - l0[i]
                lam = l0[i] + rng.uniform(0.3, 0.7) * wd
                rr = min(22.0, 0.30 * wd)
                domes.append((xs[i] + side * nx[i] * lam, ys[i] + side * ny[i] * lam, zc[i], rr))
            # people
            for rep in range(14):
                fr = rng.uniform(0.1, 0.9, len(idx))
                lam = l0[idx] + fr * (l1[idx] - l0[idx])
                jit = rng.uniform(-15, 15, len(idx))
                pp.append(np.stack([xs[idx] + side * nx[idx] * lam + tx[idx] * jit,
                                    ys[idx] + side * ny[idx] * lam + ty[idx] * jit, zc[idx] + 0.4], 1))
            # lip colonnade
            lip = np.stack([xs[idx] + side * nx[idx] * (l0[idx] + 5.0), ys[idx] + side * ny[idx] * (l0[idx] + 5.0), zc[idx] + 14.0], 1)
            cols.append(lip)
    tl = []
    for c_, r_ in trees:
        v_, f_ = octa(c_, r_)
        v3 = v_.reshape(len(c_), 6, 3)
        v3[..., 2] = c_[:, None, 2] + (v3[..., 2] - c_[:, None, 2]) * 1.9
        tl.append((v3.reshape(-1, 3), f_))
    Vt, Ft = merge(tl)
    S.add('plaza_trees', 'PLAZA_DISTRICTS', 'tree', Vt, Ft)
    dm = []
    for (x, y, z, rr) in domes:
        prof = np.array([(rr, 0), (rr * 0.95, rr * 0.5), (rr * 0.7, rr * 0.95), (rr * 0.3, rr * 1.25), (0, rr * 1.35)])
        Pd = revolve_grid(prof, 12)
        Vd, Fd = grid_mesh(Pd)
        dm.append((Vd + [x, y, z], Fd))
    Vd, Fd = merge(dm)
    S.add('plaza_pavilions', 'PLAZA_DISTRICTS', 'champagne', Vd, Fd)
    pp = np.vstack(pp)
    Vp, Fp = people_quads(pp[:, 0], pp[:, 1], pp[:, 2])
    S.add('plaza_people', 'PLAZA_DISTRICTS', 'people', Vp, Fp, bias=0.5)
    cols = np.vstack(cols)
    Vc, Fc = boxes(cols, [3.0, 3.0, 28.0])
    S.add('plaza_lip_columns', 'PLAZA_DISTRICTS', 'champagne', Vc, Fc)


def build_scene(seed=7, with_hall=True):
    rng = np.random.default_rng(seed)
    S = Scene()
    sec = build_nave(S, rng)
    build_apse(S, sec, rng)
    build_rings(S, sec, rng)
    build_blades(S, sec, rng)
    build_islands(S, sec, rng)
    build_bridges(S, sec)
    build_veils(S, sec)
    build_beams(S, sec)
    build_people(S, sec, rng)
    build_plazas(S, sec, rng)
    build_terrain(S, sec, rng)
    if with_hall:
        import c55a_hall
        c55a_hall.build_hall(S, sec, rng)
    S.sec = sec
    return S


if __name__ == '__main__':
    import time
    t0 = time.time()
    S = build_scene(with_hall=False)
    print('build s', round(time.time() - t0, 1))
    tot = 0
    for k, v in S.stats().items():
        print(k, v)
        tot += v['tris']
    print('TOTAL tris', tot)
