import json, hashlib, sys, os, time, numpy as np
from PIL import Image
import c55a_city as C, camera_specs, glb_export

OUT = sys.argv[1]
t0 = time.time()
S = C.build_scene()
S2 = C.build_scene()
def digest(S):
    h = hashlib.sha256()
    for p in S.parts:
        h.update(p['name'].encode()); h.update(np.ascontiguousarray(p['V']).tobytes()); h.update(np.ascontiguousarray(p['F']).tobytes())
    return h.hexdigest()
d1, d2 = digest(S), digest(S2)
glb_path = os.path.join(OUT, 'C55A_SevenfoldHaloRift.glb')
size = glb_export.write_glb(S, glb_path)
gv = glb_export.verify_glb(glb_path)
st = S.stats()
tri_scene = sum(v['tris'] for v in st.values())
sec = S.sec

def bbox(pred):
    mn = np.full(3, np.inf); mx = np.full(3, -np.inf)
    for p in S.parts:
        if pred(p):
            mn = np.minimum(mn, p['V'].min(0)); mx = np.maximum(mx, p['V'].max(0))
    return mn, mx
mn, mx = bbox(lambda p: (not p['context']) and (not p['interior']) and p['coll'] != 'BRIDGES_VEILS_BEAMS')
dim = mx - mn
win = sum(len(p['F']) // 2 for p in S.parts if '_win' in p['name'] or 'win_' in p['mat'])
blades = [p for p in S.parts if p['coll'] == 'OBSIDIAN_BLADES' and not p['name'].endswith('_edge')]
blade_h = [float(p['V'][:, 2].max() - p['V'][:, 2].min()) for p in blades]
crest_abs = float(max(p['V'][:, 2].max() for p in S.parts if p['coll'] in ('NAVE_MASSIF_NORTH', 'APSE_SACRED_FACE') and p['mat'] in ('shell', 'shell_band', 'obsidian')))
hall = [p for p in S.parts if p['interior']]
hmn = np.min([p['V'].min(0) for p in hall], 0); hmx = np.max([p['V'].max(0) for p in hall], 0)
hall_len = float(np.linalg.norm((sec['hall']['Rm'][:, 0]) * 1100))
rings = [dict(index=i + 1, radius_m=r['R'], diameter_m=2 * r['R'], t_along_nave=r['t']) for i, r in enumerate(sec['rings'])]
lens = sec['islands']['lens']
# degenerate/NaN scan on scene meshes
nan_parts = [p['name'] for p in S.parts if not np.isfinite(p['V']).all()]
bad_idx = [p['name'] for p in S.parts if p['F'].max() >= len(p['V']) or p['F'].min() < 0]
# renders
rs = json.load(open(os.path.join(OUT, '_render_stats.json')))
specs = camera_specs.get_specs(S)
cam_match = all(np.allclose(s['pos'], r['camera_pos'], atol=0.2) for s, r in zip(specs, rs))
imgs = []
for r in rs:
    f = os.path.join(OUT, r['label'] + '.png')
    im = Image.open(f)
    a = np.asarray(im.convert('L'), float)
    imgs.append(dict(file=r['label'] + '.png', size=list(im.size), mean_luma=round(float(a.mean() / 255), 3), p1=int(np.percentile(a, 1)), p99=int(np.percentile(a, 99)),
                     geometry_coverage=r['geometry_coverage'], faces_drawn=r['faces_drawn'], render_seconds=r['seconds'],
                     renderer='C55A software rasteriser (numpy+PIL) -- NOT Blender'))
val = dict(
    project='CELESTIAL HALO-9 independent research C55-A', model='Claude Sonnet 5.5', concept_ja='七環天裂都', concept_en='Sevenfold Halo Rift',
    date='2026-10-25', generator_seed=7, deterministic_rebuild_identical=(d1 == d2), geometry_sha256=d1,
    geometry=dict(parts=len(S.parts), collections=st, triangles=tri_scene, vertices=int(sum(len(p['V']) for p in S.parts)),
                  materials=len(C.MATERIALS), nan_parts=nan_parts, parts_with_bad_indices=bad_idx),
    glb=dict(path='C55A_SevenfoldHaloRift.glb', **gv, triangles_match_scene=(gv['triangles'] == tri_scene)),
    scale_m=dict(central_complex_bbox_min=[round(float(x), 1) for x in mn], central_complex_bbox_max=[round(float(x), 1) for x in mx],
                 extent_x=round(float(dim[0]), 1), extent_y=round(float(dim[1]), 1), extent_z=round(float(dim[2]), 1),
                 nave_length=float(C.X1 - C.X0), nave_width_range=[float(C.nave_w(np.array([0.5])).min()), float(C.nave_w(np.array([1.0]))[0])],
                 crest_peak_absolute_height=round(crest_abs, 1), obsidian_blade_heights=[round(h) for h in blade_h],
                 halos=rings, sanctum_lens_radius=float(lens['R']), great_hall_length=1100.0, great_hall_width=460.0, great_hall_vault_apex_height=430.0,
                 window_count=int(win)),
    cameras=dict(count=len(specs), match_render_log=bool(cam_match), specs=specs),
    renders=imgs,
    not_verified=[
        'Blender: no bpy in sandbox -> .blend NOT produced; blender_build.py never executed.',
        'GitHub: no network/credentials in sandbox -> nothing pushed; push_to_github.sh never executed.',
        'GLB opened in an external viewer (Blender/three.js): NOT done; only self-written re-parser used.',
        'CITY_MASTER_3D_STANDARD.md and other policy sub-docs not read (fetch not permitted for that URL in this session).',
        'Walkable connectivity (stairs/lifts between tiers, hall portal cut through the massif) is NOT modelled.',
        'Structural/physical plausibility, collision and water-tightness: NOT checked.',
        '10 km city-wide detail: NOT done (terrain/roads/light carpets are non-design context placeholders).',
        'Minecraft conversion: out of scope (HOLD).'],
    build_validation_seconds=round(time.time() - t0, 1))
json.dump(val, open(os.path.join(OUT, 'C55A_validation.json'), 'w'), indent=1, ensure_ascii=False)
print(json.dumps({k: val[k] for k in ('deterministic_rebuild_identical',)}), 'tris', tri_scene, 'glb', gv['file_bytes'], 'match', val['glb']['triangles_match_scene'], 'cam_match', cam_match)
print('extent', dim, 'crest', crest_abs, 'win', win, 'bad', gv['meshes_with_bad_indices'], gv['meshes_with_nonfinite'], gv['degenerate_triangles'])
