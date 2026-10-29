"""Independent isolated replay of original/edited control cages and actual GLB audits.
Never reads/imports code from protected city branches or any Minecraft world.
"""
from pathlib import Path
import subprocess,sys,shutil,tempfile,json,hashlib,io
import numpy as np,trimesh
from PIL import Image
ROOT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
record={'study':'R33-S27-D33','type':'art-directed freeform control cages / NOT FORMAL DESIGN','working_file_source':'D33_sculpt.py', 'art':'REJECT, uninhabited abstract sculpture', 'base_art_adopted':False}
with tempfile.TemporaryDirectory() as t:
    temp=Path(t)
    shutil.copy2(ROOT/'d33_sculpt.py',temp/'d33_sculpt.py')
    task=subprocess.run([sys.executable,str(temp/'d33_sculpt.py')],cwd=temp,capture_output=True,text=True,timeout=80)
    record['independent_process_exit']=task.returncode
    record['independent_stdout']=task.stdout[:2500]
    record['independent_stderr']=task.stderr[:1800]
    if task.returncode:raise RuntimeError('Independent subprocess failed')
    record['glb_replay_sha']={}
    for key in ('BASE','EDIT'):
        original=ROOT/f'D33_{key}_ART_STUDY.glb'; replay=temp/f'D33_{key}_ART_STUDY.glb'
        record['glb_replay_sha'][key]={'original':sha(original),'independent':sha(replay),'match':sha(original)==sha(replay)}
        assert sha(original)==sha(replay)
record['real_glb']={}
for tag in ('BASE','EDIT'):
    sc=trimesh.load(ROOT/f'D33_{tag}_ART_STUDY.glb',force='scene',process=False)
    record['real_glb'][tag]={'geometry_count':len(sc.geometry),'triangle_count':sum(len(x.faces) for x in sc.geometry.values()),
        'watertight_per_mesh':{name:bool(g.is_watertight) for name,g in sc.geometry.items()},
        'bounds':np.round(sc.bounds,3).tolist(),
        'volume_by_mesh_m3':{name:round(g.volume,2) for name,g in sc.geometry.items()},
        'no_certification_of_selfintersections':True,'interior_accessible':False,'walkable_civic_route':False,'multi-district_city':False}
    assert len(sc.geometry)==3 and all(g.is_watertight for g in sc.geometry.values())
views=('01_south','02_east','03_north','04_west','05_aerial','06_human')
record['views']={}
for name in views:
    a=np.asarray(Image.open(ROOT/f'D33_BASE_VIEWS/{name}.png').convert('RGB'),dtype=np.int16)
    b=np.asarray(Image.open(ROOT/f'D33_EDIT_VIEWS/{name}.png').convert('RGB'),dtype=np.int16)
    change=np.any(np.abs(a-b)>20,axis=2)
    record['views'][name]={'changed_pixels_percent':round(100*change.mean(),3),'base_nonempty':bool(a.std()>4),'edit_nonempty':bool(b.std()>4)}
    assert record['views'][name]['base_nonempty'] and record['views'][name]['edit_nonempty']
record['automated_editor_tests']=json.loads((ROOT/'D33_TEST_RESULTS.json').read_text())
record['chromium_ui_test']=json.loads((ROOT/'D33_BROWSER_TEST.json').read_text())
record['work_used']=False;record['blender_native_tested']=False;record['minecraft_world_modified']=False
record['main_modified']=False;record['central_art_adoptions']=0
record['limitations']=['Only 3 visual surface-shell geometries, no rooms and public routes','Watertight meshes do not imply non-selfintersecting geometry or safety','WebGL interactive 3D orbit and point click were not certified by headless Chromium due to WebGL unavailable','Browser API tested by FastAPI shim because localhost connection denied','Closed code-tested control-cage operation, not Blender native sculpt or master city']
(ROOT/'D33_INDEPENDENT_AUDIT.json').write_text(json.dumps(record,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:record[k] for k in ['glb_replay_sha','views']},indent=2))
