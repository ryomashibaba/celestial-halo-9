#!/usr/bin/env python3
"""D31 independent verification of STEP solid, GLB reimport, voids, joint overlap and replay.
This audits what is actually true, NOT art acceptance, structural safety, or walkability.
"""
import cadquery as cq, trimesh, numpy as np, json, hashlib, os, sys, subprocess, tempfile
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));import d31_cad_artfirst as design

def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def visit(w):
    sp=ROOT/f'D31_{w}_CAD_EXACT.step'; gp=ROOT/f'D31_{w}_real3d.glb'
    solidlist=cq.importers.importStep(str(sp)).solids().vals()
    assert len(solidlist)==5 and all(s.isValid() for s in solidlist)
    scene=trimesh.load(gp,force='scene',process=False);assert set(scene.geometry)=={'WEST','EAST','SKY','FLOAT','GROUND'}
    mesh={}
    for name,g in scene.geometry.items():
        copy=g.copy();copy.merge_vertices(digits_vertex=4)
        mesh[name]={'triangles':int(len(g.faces)),'watertight_after_normalseam_weld':bool(copy.is_watertight),'winding_consistent':bool(copy.is_winding_consistent),'euler_number':int(copy.euler_number)}
        assert copy.is_watertight and copy.is_winding_consistent,name
    # The two exact CAD boolean cuts remove actual solid material at given points.
    west=design.front(design.WEST,560,0);east=design.front(design.EAST,630,90)
    westcut=west.cut(design.front(design.WEST_VOID,650,0))
    eastcut=east.cut(design.front(design.EAST_VOID,740,90))
    wpt=cq.Vector(-540,0,540);ept=cq.Vector(800,90,620)
    opens={'west_before':bool(west.isInside(wpt,0.0001)),'west_after':bool(westcut.isInside(wpt,0.0001)),'east_before':bool(east.isInside(ept,0.0001)),'east_after':bool(eastcut.isInside(ept,0.0001))}
    assert opens=={'west_before':True,'west_after':False,'east_before':True,'east_after':False},opens
    bridge=design.front(design.BRIDGE if w=='A' else design.BRIDGE_B,490,-10)
    floating=design.front(design.FLOAT if w=='A' else design.FLOAT_B,390,-90)
    contact={'west_bridge_intersect_m3':float(westcut.intersect(bridge).Volume()),'east_bridge_intersect_m3':float(eastcut.intersect(bridge).Volume()),'float_west_intersect_m3':float(floating.intersect(westcut).Volume()),'float_east_intersect_m3':float(floating.intersect(eastcut).Volume())}
    assert contact['west_bridge_intersect_m3']>0 and contact['east_bridge_intersect_m3']>0
    # Note the floating module has no verified access/transport route. No public walkable interior is claimed.
    result={'step_sha256':hashfile(sp),'step_size_bytes':sp.stat().st_size,'step_reimported_valid_solids':5,'step_compound_volume_m3':float(sum(s.Volume() for s in solidlist)),'glb_sha256':hashfile(gp),'glb_geometry_count':len(scene.geometry),'glb_geometry':mesh,'actual_material_removed_at_test_points':opens,'solid_overlap':contact,'verified_public_paths':0,'inhabited_districts_verified':0,'art_decision':'REJECT'}
    return result

def image_diff(a,b):
    x=np.asarray(Image.open(ROOT/f'D31_A_{a}.png').convert('RGB'),dtype=np.int16)
    y=np.asarray(Image.open(ROOT/f'D31_B_{b}.png').convert('RGB'),dtype=np.int16)
    return round(100*float(np.mean(np.max(np.abs(x-y),axis=2)>20)),3)

if __name__=='__main__':
    out={w:visit(w) for w in ('A','B')}
    out['render_changed_pixels_percent_A_vs_B']={name:image_diff(name,name) for name in ['front','west_oblique','east_oblique','rear','aerial','side','human_canyon']}
    with tempfile.TemporaryDirectory(prefix='d31-isolated-') as tmp:
        env=os.environ.copy();env['D31_OUTPUT_DIR']=tmp
        run=subprocess.run([sys.executable,str(ROOT/'d31_cad_artfirst.py')],env=env,capture_output=True,text=True,timeout=90)
        if run.returncode!=0:raise RuntimeError(run.stderr[-4000:])
        out['independent_subprocess']={w:{'glb_sha_match':hashfile(Path(tmp)/f'D31_{w}_real3d.glb')==out[w]['glb_sha256'], 'step_5_valid':len(cq.importers.importStep(str(Path(tmp)/f'D31_{w}_CAD_EXACT.step')).solids().vals())==5} for w in ('A','B')}
        assert all(d['glb_sha_match'] and d['step_5_valid'] for d in out['independent_subprocess'].values())
    (ROOT/'D31_INDEPENDENT_QA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({w:{'solid_overlap':out[w]['solid_overlap'],'glb_sha256':out[w]['glb_sha256']} for w in ('A','B')},ensure_ascii=False,indent=2));print('image differences',out['render_changed_pixels_percent_A_vs_B']);print('isolated',out['independent_subprocess'])
