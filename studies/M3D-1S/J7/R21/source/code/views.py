import numpy as np
import c55a_city as C, c55a_render as R

def get_views(S, W, H):
    sec = S.sec
    V = []
    def nave_pt(t, dz=0.0, lat=0.0):
        i = int(round(t * (C.NS - 1)))
        return np.array([sec['xs'][i] + sec['nx'][i] * lat, sec['ys'][i] + sec['ny'][i] * lat, sec['fl'][i] + dz])
    V.append(('01_front_sea_gate', R.Cam((8800, -120, 560), (-1500, 150, 1250), 56, W, H), 1.0, False))
    V.append(('02_oblique_SE', R.Cam((6600, -5600, 2300), (-300, 200, 1250), 52, W, H), 1.0, False))
    V.append(('03_side_south', R.Cam((300, -9800, 1100), (0, 200, 1500), 50, W, H), 1.0, False))
    V.append(('04_rear_apse', R.Cam((-13800, 1800, 2600), (-1500, 150, 1750), 58, W, H), 1.0, False))
    V.append(('05_aerial', R.Cam((4200, -7800, 8600), (-250, 250, 900), 46, W, H), 1.0, False))
    g = nave_pt(0.88, 1.8, lat=150.0)
    V.append(('06_ground_plaza', R.Cam(g, g + np.array([-2800, -40, 760]), 72, W, H), 1.0, False))
    h = sec['hall']
    def hl(p):
        return h['O'] + h['Rm'] @ np.array(p, float)
    V.append(('07_interior_great_hall', R.Cam(hl((-520, 10, 44)), hl((520, 0, 205)), 74, W, H), 1.0, True))
    L = sec['islands']['lens']
    lc = L['center']
    dc = sec['disc']['center']
    V.append(('08_high_altitude_lens_district', R.Cam(lc + np.array([-430, 540, 330]), lc + np.array([60, -40, 70]), 68, W, H), 1.0, False))
    n9 = nave_pt(0.50, 9.0)
    V.append(('09_nave_floor_looking_apse', R.Cam(n9, n9 + np.array([-2200, 40, 780]), 72, W, H), 1.0, False))
    i = int(round(0.30 * (C.NS - 1)))
    k = C.PLAZA_TIERS[1]
    lam0 = sec['LAM'][1][i][2 * k + 1]; lam1 = sec['LAM'][1][i][2 * k + 2]
    zz = sec['Z'][1][i][2 * k + 1]
    lam = lam0 + 0.42 * (lam1 - lam0)
    p = np.array([sec['xs'][i] + sec['nx'][i] * lam, sec['ys'][i] + sec['ny'][i] * lam, zz + 1.8])
    tgt = p + np.array([-sec['tx'][i] * 1400 - sec['nx'][i] * 200, -sec['ty'][i] * 1400 - sec['ny'][i] * 200, 420.0])
    V.append(('10_wall_plaza_district', R.Cam(p + np.array([0, 0, 0]), tgt, 80, W, H), 1.0, False))
    V.append(('11_skyline_NE_dusk', R.Cam((9500, 5200, 900), (-800, 150, 1500), 44, W, H), 1.0, False))
    return V
