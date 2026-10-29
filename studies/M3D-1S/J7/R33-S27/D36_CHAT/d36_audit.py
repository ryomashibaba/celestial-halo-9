#!/usr/bin/env python3
"""Isolated source replay and fail-closed negative tests."""
import json, sys, subprocess, tempfile, shutil, hashlib
from pathlib import Path
import trimesh, numpy as np
ROOT=Path(__file__).parent
src=ROOT/'D36_NEUTRAL_TECH_FIXTURE.glb';plan=ROOT/'D36_EDIT_PLAN.json';ref=ROOT/'D36_REFERENCE_EDIT.glb'
res=json.loads((ROOT/'D36_OFFLINE_RESULT.json').read_text())
with tempfile.TemporaryDirectory(prefix='halo9-d36-audit-') as tmp:
    tmp=Path(tmp)
    for f in (ROOT/'d36_offline_sculpt.py',src,plan):shutil.copy2(f,tmp/f.name)
    cmd=[sys.executable,str(tmp/'d36_offline_sculpt.py'),str(tmp/src.name),str(tmp/plan.name),str(tmp/'repeat.glb')]
    p=subprocess.run(cmd,capture_output=True,text=True,check=True)
    replay=json.loads(p.stdout)
    assert (tmp/'repeat.glb').read_bytes()==ref.read_bytes()
    sys.path.insert(0,str(ROOT));from d36_offline_sculpt import apply
    base_plan=json.loads(plan.read_text())
    def negative(label,mutation):
        altered=json.loads(json.dumps(base_plan));mutation(altered)
        path=tmp/('bad_'+label+'.json');path.write_text(json.dumps(altered))
        try:apply(src,path,tmp/('test_'+label+'.glb'))
        except (ValueError,KeyError) as e:return str(e)
        raise AssertionError('Negative control not rejected: '+label)
    neg={
      'bad_source_hash':negative('hash',lambda p:p.update(source_sha256='0'*64)),
      'unprotected_other_mesh':negative('unprotected',lambda p:p.update(protected_geometries=[])),
      'bad_target':negative('target',lambda p:p.update(target_geometry='MAIN_SHEAR')),
      'zero_radius':negative('radius',lambda p:p['strokes'][0].update(radius_m=0)),
      'oversize_shift':negative('shift',lambda p:p['strokes'][0].update(delta_xyz_m=[9999,0,0])),
      'bad_falloff':negative('falloff',lambda p:p['strokes'][0].update(falloff='flat')),
    }
    try:apply(src,plan,src)
    except ValueError as e:neg['source_overwrite']=str(e)
    else:raise AssertionError('Source overwrite accepted')
    scenes=[trimesh.load(str(p),force='scene',process=False) for p in (src,ref)]
    assert set(scenes[0].geometry)==set(scenes[1].geometry)
    for key in base_plan['protected_geometries']:
        assert np.array_equal(scenes[0].geometry[key].faces,scenes[1].geometry[key].faces)
        assert np.allclose(scenes[0].geometry[key].vertices,scenes[1].geometry[key].vertices,atol=1e-4)
    target=base_plan['target_geometry']
    original=scenes[0].geometry[target];edited=scenes[1].geometry[target]
    assert len(original.faces)==len(edited.faces)
    assert original.is_watertight and edited.is_watertight
    assert original.is_winding_consistent and edited.is_winding_consistent
    assert all(p.is_watertight for s in scenes for p in s.geometry.values())
    assert hashlib.sha256(src.read_bytes()).hexdigest()==base_plan['source_sha256']
    report={'study':'D36','replay_sha256_exact':True,'source_unchanged':True,
            'saved_glb_mesh_count':len(scenes[1].geometry),'target_faces':len(edited.faces),
            'protected_geometries_bitwise_stable_after_glb_roundtrip':True,
            'negative_controls':neg,'replayed_output_sha256':replay['output_sha256'],
            'bpy_available_here':False,'actual_blender_run':False,'blend_created':False,
            'art_adoption':False,'minecraft_construction':False}
    (ROOT/'D36_AUDIT.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
