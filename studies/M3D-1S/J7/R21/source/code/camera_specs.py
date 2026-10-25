"""Camera specification for the 11 required review views (pure numpy; usable from Blender and the software renderer)."""
import numpy as np
import c55a_city as C


def get_specs(S):
    sec = S.sec
    out = []

    def nave_pt(t, dz=0.0, lat=0.0):
        i = int(round(t * (C.NS - 1)))
        return np.array([sec['xs'][i] + sec['nx'][i] * lat, sec['ys'][i] + sec['ny'][i] * lat, sec['fl'][i] + dz])

    def add(name, pos, tgt, hfov, interior=False):
        out.append(dict(name=name, pos=[float(x) for x in pos], target=[float(x) for x in tgt], hfov=float(hfov), interior=interior))

    add('01_front_sea_gate', (8800, -120, 560), (-1500, 150, 1250), 56)
    add('02_oblique_SE', (6600, -5600, 2300), (-300, 200, 1250), 52)
    add('03_side_south', (300, -9800, 1100), (0, 200, 1500), 50)
    add('04_rear_apse', (-13800, 1800, 2600), (-1500, 150, 1750), 58)
    add('05_aerial', (4200, -7800, 8600), (-250, 250, 900), 46)
    g = nave_pt(0.88, 1.8, lat=150.0)
    add('06_ground_plaza', g, g + np.array([-2800, -40, 760]), 72)
    h = sec['hall']
    hl = lambda p: h['O'] + h['Rm'] @ np.array(p, float)
    add('07_interior_great_hall', hl((-520, 10, 44)), hl((520, 0, 205)), 74, True)
    lc = sec['islands']['lens']['center']
    add('08_high_altitude_lens_district', lc + np.array([-430, 540, 330]), lc + np.array([60, -40, 70]), 68)
    n9 = nave_pt(0.50, 9.0)
    add('09_nave_floor_looking_apse', n9, n9 + np.array([-2200, 40, 780]), 72)
    i = int(round(0.30 * (C.NS - 1)))
    k = C.PLAZA_TIERS[1]
    lam0 = sec['LAM'][1][i][2 * k + 1]
    lam1 = sec['LAM'][1][i][2 * k + 2]
    zz = sec['Z'][1][i][2 * k + 1]
    lam = lam0 + 0.42 * (lam1 - lam0)
    p = np.array([sec['xs'][i] + sec['nx'][i] * lam, sec['ys'][i] + sec['ny'][i] * lam, zz + 1.8])
    add('10_wall_plaza_district', p, p + np.array([-sec['tx'][i] * 1400 - sec['nx'][i] * 200, -sec['ty'][i] * 1400 - sec['ny'][i] * 200, 420.0]), 80)
    add('11_skyline_NE_dusk', (9500, 5200, 900), (-800, 150, 1500), 44)
    return out
