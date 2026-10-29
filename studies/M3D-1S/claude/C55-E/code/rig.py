"""C55-E render rig. Same renderer as C55-D (numpy software rasterizer + sun/sky shadow maps). NOT Blender / Cycles.
Neutral clay: every material albedo 0.58 (ground 0.46), no emission, no windows. Same sun, FOV, resolution, exterior camera POSITIONS as C55-C/D renders.
Targets / interior cameras are structure-specific (documented in ART_REVIEW)."""
import sys, time, os, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core import *
from raster_c55c import Camera

SUN = {'clay': (-0.70, 0.35, 0.62), 'dusk': (-0.30, -0.93, 0.16)}
Z = (0, 0, 1)
OUT = '/home/claude/c55e/renders'


def mats(mode):
    if mode == 'clay':
        return {i: dict(alb=0.58) for i in range(12)} | {2: dict(alb=0.46)}
    return {0: dict(alb=0.10), 1: dict(alb=0.30, emis=(1.5, 1.2, 0.8)), 2: dict(alb=0.10, emis=(0.10, 0.06, 0.03)), 4: dict(alb=0.16, emis=(1.5, 0.80, 0.36)),
            5: dict(alb=0.07), 6: dict(alb=0.12, emis=(1.2, 0.66, 0.30)), 7: dict(alb=0.2, emis=(1.6, 0.85, 0.40)), 8: dict(alb=0.06)}


def ext_cams(tgt, tgt_side=None, tgt_aerial=None):
    """exterior camera POSITIONS identical to CAMS_D1 (C55-D). Only the look-at target differs per structure."""
    ts = tgt_side or tgt; ta = tgt_aerial or tgt
    return {
        '01_far': ((-10200, -7600, 420), tgt, 40, Z),
        '02_front': ((0, -9800, 1300), tgt, 46, Z),
        '03_side': ((-12500, 900, 1100), ts, 40, Z),
        '04_back': ((300, 9800, 1100), tgt, 46, Z),
        '05_aerial': ((0, -2600, 8800), ta, 52, Z),
    }


def run(npz, prefix, mode, cams, sel=None, W=1600, H=900, ss=1.5, light=None, radius=13000, center=(0, 0, 1500), res=1536, log=print):
    z = np.load(npz); mesh = {k: z[k] for k in z.files}
    if light is None:
        t = time.time(); light = Light(mesh, unit(SUN[mode]), center, radius, res=res, sky=(6, 6, 3), log=lambda *a: None); log(f'light {time.time()-t:.0f}s')
    MI = mats(mode)
    for k, (p, tg, fov, up) in cams.items():
        if sel and k not in sel: continue
        cam = Camera(p, tg, fov, int(W * ss), int(H * ss), up=up); t = time.time()
        img = render(cam, mesh, light, mode, mat_info=MI, log=lambda *a: None)
        if ss != 1: img = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)
        cv2.imwrite(f'{OUT}/{prefix}_{k}_{mode}.png', img); log(f'{k} {time.time()-t:.0f}s')
    return light
