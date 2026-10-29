#!/usr/bin/env python3
"""Local fail-closed audit: static contracts + independent GLB replay; NEVER report Blender runtime PASS here."""
import json, sys, subprocess, tempfile, hashlib, shutil, ast
from pathlib import Path
import numpy as np,trimesh
from d37_kernel import validate,apply,sha
ROOT=Path(__file__).resolve().parent
source=ROOT/'D37_NEUTRAL_FIXTURE.glb'; plan=ROOT/'D37_EDIT_PLAN.json';reference=ROOT/'D37_REFERENCE_EDIT.glb'
p=json.loads(plan.read_text(encoding='utf-8'))
s=trimesh.load(str(source),force='scene',process=False)
validate(p,source,s.geometry)
assert sha(source.read_bytes())==p['source_sha256']
orig=np.asarray(s.geometry[p['target_geometry']].vertices); expected=apply(orig,p['strokes'])
assert int(np.sum(np.linalg.norm(orig-expected,axis=1)>1e-4))>=100
protected=p['protected_geometries']
for name in protected:
    assert len(s.geometry[name].vertices)>0
for f in ROOT.glob('d37_*.py'):
    ast.parse(f.read_text(encoding='utf-8'))
with tempfile.TemporaryDirectory(prefix='halo9-d37-replay-') as tmp:
    tmp=Path(tmp)
    for name in ['d37_kernel.py','d37_offline_reference.py']:
        shutil.copy2(ROOT/name,tmp/name)
    subprocess.run([sys.executable,str(tmp/'d37_offline_reference.py'),str(plan),str(tmp/'replay.glb')],capture_output=True,text=True,check=True)
    assert (tmp/'replay.glb').read_bytes()==reference.read_bytes(),'Independent reference GLB SHA mismatch'
    problems={}
    def check(label,fn):
        q=json.loads(json.dumps(p));fn(q)
        try:validate(q,source,s.geometry)
        except (ValueError,KeyError,TypeError) as exc:problems[label]=str(exc)
        else:raise AssertionError(f'Invalid plan accepted: {label}')
    check('bad_sha',lambda q:q.update(source_sha256='0'*64))
    check('unprotected',lambda q:q.update(protected_geometries=[]))
    check('same_target_protected',lambda q:q.update(target_geometry=protected[0]))
    check('bad_falloff',lambda q:q['strokes'][0].update(falloff='flat'))
    check('bad_radius',lambda q:q['strokes'][0].update(radius_m=0))
    check('oversize_delta',lambda q:q['strokes'][0].update(delta_xyz_m=[1000,0,0]))
    check('not_tech_only',lambda q:q.update(art_status='APPROVED'))
    check('nan_value',lambda q:q['strokes'][0].update(center_fraction=[float('nan'),0,0]))
    check('source_unprotected',lambda q:q.update(protect_original=False))
    check('invalid_minecraft',lambda q:q.update(minecraft='APPROVED'))
    assert not (ROOT/'D37_NATIVE_EDITABLE.blend').exists()
    report={'model': 'D37-neutral-fixture','offline_source_sha256':sha(source.read_bytes()),
       'offline_reference_sha256':sha(reference.read_bytes()),'independent_reference_replay_sha256_equal':True,
       'moved_vertices':int(np.sum(np.linalg.norm(orig-expected,axis=1)>1e-4)),
       'negative_tests':problems,'negative_tests_pass':len(problems),
       'real_blender_available_here':False,'actual_native_blend_created':False,
       'github_actions_run_confirmed':False,'technical':'LIMITED_PASS_OFFLINE_ONLY',
       'art':'NOT_SUBMITTED','formal_adoptions':0,'minecraft':'HOLD'}
    (ROOT/'D37_LOCAL_AUDIT.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))
