import json, copy, hashlib, importlib.util, sys
from pathlib import Path
import tempfile
from fastapi.testclient import TestClient
from d33_visual_editor import create_app
from d33_sculpt import build
import trimesh,numpy as np

ROOT=Path(__file__).resolve().parent
checks={}
with tempfile.TemporaryDirectory() as tt:
 d=Path(tt)
 for f in ['D33_BASE_CAGE.json','D33_BASE_ART_STUDY.glb','D33_EDITOR.html','plotly.min.js']:
  (d/f).write_bytes((ROOT/f).read_bytes())
 app=create_app(d);c=TestClient(app);s=c.get('/api/state').json()
 checks['server_state_200']=len(s['meshes'])==3 and s['revision']==0
 originalsha=hashlib.sha256((d/'D33_BASE_ART_STUDY.glb').read_bytes()).hexdigest()
 obj='MAIN_SHEAR';start=s['controls'][obj][3][3]
 payload={'revision':0,'object':obj,'i':3,'j':3,'x':start[0]+50,'y':start[1]+35,'z':start[2]-40}
 e=c.post('/api/edit',json=payload)
 checks['edit_200']=e.status_code==200
 if not checks['edit_200']:print(e.text[:1000]);raise SystemExit(1)
 data=e.json();edited_sha=data['model']['sha256']
 checks['changed_export']=edited_sha!=originalsha
 checks['source_immutable']=hashlib.sha256((d/'D33_BASE_ART_STUDY.glb').read_bytes()).hexdigest()==originalsha
 checks['base_export_watertight']=bool(all(x['watertight'] for x in data['model']['geometry'].values()))
 checks['all_triangle_counts']=data['model']['triangles']==32436
 exported=c.get('/api/export').content
 checks['glb_real_readback']=len(trimesh.load(trimesh.util.wrap_as_stream(exported),file_type='glb',force='scene').geometry)==3
 checks['export_hash_match']=hashlib.sha256(exported).hexdigest()==edited_sha
 checks['cage_match']=json.loads(c.get('/api/cage').content)['objects'][obj]['cage'][3][3]==[round(payload['x'],5),round(payload['y'],5),round(payload['z'],5)]
 # independent reconstruction in a different temporary folder from saved cage JSON
 with tempfile.TemporaryDirectory() as rr:
  p=Path(rr)/'isolated_replay.glb'
  build(json.loads(c.get('/api/cage').content),p)
  checks['replay_independent_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()==edited_sha
 for label,bad in [
  ('reject_stale_revision',{**payload,'revision':0}),
  ('reject_unknown_mesh',{**payload,'revision':1,'object':'forbidden'}),
  ('reject_large_move',{**payload,'revision':1,'z':start[2]+2000}),
  ('reject_negative_handle',{**payload,'revision':1,'i':-1})]:
  checks[label]=c.post('/api/edit',json=bad).status_code==400
 un=c.post('/api/undo',json={'revision':1})
 checks['undo_200']=un.status_code==200
 checks['undo_exact_controls']=un.json()['state']['controls'][obj][3][3]==start
 checks['undo_source_immutable']=hashlib.sha256((d/'D33_BASE_ART_STUDY.glb').read_bytes()).hexdigest()==originalsha
 checks['undo_glb_equal_base']=un.json()['model']['sha256']==originalsha
 checks['export_revision_2']=bool((d/'runtime_exports/D33_EDIT_r0002.glb').exists())
checks['all_pass']=all(checks.values())
(ROOT/'D33_TEST_RESULTS.json').write_text(json.dumps(checks,indent=2,ensure_ascii=False),encoding='utf-8')
for name,value in checks.items():print(('PASS' if value else 'FAIL'),name)
assert checks['all_pass']
