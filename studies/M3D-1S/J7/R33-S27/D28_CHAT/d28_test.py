import json, tempfile, hashlib, subprocess, sys
from pathlib import Path
from fastapi.testclient import TestClient
from PIL import Image
from d28_visual_workbench import Workspace,create_app,load_scene,apply_recipe,sha,VIEWS
R=Path(__file__).resolve().parent

def check():
 with tempfile.TemporaryDirectory(prefix='d28_') as tmp:
  w=Workspace(Path(tmp));client=TestClient(create_app(w))
  s=client.get('/api/state').json()
  assert s['art']=='NOT SUBMITTED' and s['operations']==0
  base=Path(tmp,'BASE.glb').read_bytes()
  for v in VIEWS:
   r=client.get('/api/view/'+v);assert r.status_code==200
   assert Image.open(__import__('io').BytesIO(r.content)).size==(560,350)
   (R/f'D28_TEST_{v}.png').write_bytes(r.content)
  # hit several points of visible 3D with picker; set from first valid front/oblique
  selection=None
  for view in ['front','oblique','east']:
   for u in [.30,.38,.45,.55,.62,.72]:
    r=client.post('/api/select',json={'view':view,'u':u,'v':.53});assert r.status_code==200
    if r.json():selection=r.json();break
   if selection:break
  assert selection, 'VTK mouse picking must hit real geometry'
  print('PICKED',selection)
  # Reject stale/no state prior to any mutation
  assert client.post('/api/edit',json={'revision':'stale','radius_m':150,'delta_xyz_m':[32,0,0]}).status_code==422
  assert client.post('/api/edit',json={'revision':s['revision'],'radius_m':0,'delta_xyz_m':[32,0,0]}).status_code==422
  assert Path(tmp,'BASE.glb').read_bytes()==base
  new=client.post('/api/edit',json={'revision':s['revision'],'radius_m':150,'delta_xyz_m':[32,0,0]})
  print('EDIT',new.status_code,new.text[:300]);assert new.status_code==200
  edited=new.json();assert edited['operations']==1 and edited['revision']!=s['revision']
  (R/'D28_TEST_EDIT_front.png').write_bytes(client.get('/api/view/front').content)
  (R/'D28_TEST_EDIT_oblique.png').write_bytes(client.get('/api/view/oblique').content)
  assert Path(tmp,'BASE.glb').read_bytes()==base
  assert client.get('/artifact/EDIT.glb').content==Path(tmp,'EDIT.glb').read_bytes()
  assert client.post('/api/undo',json={'revision':'stale'}).status_code==422
  # restart with same recipe and source bytes; immutable recipe replay
  wd2=Workspace(Path(tmp));assert wd2.edited==w.edited
  independent=apply_recipe(base,json.loads(Path(tmp,'EDIT_PLAN.json').read_text())['operations'])
  assert independent==w.edited
  after=client.post('/api/undo',json={'revision':edited['revision']});assert after.status_code==200
  assert after.json()['operations']==0 and Path(tmp,'EDIT.glb').read_bytes()==base
  # corrupt source hash in recipe must refuse, no overwrite existing protected source
  wrong={'study':'D28','base_sha256':'0'*64,'operations':[]}
  Path(tmp,'EDIT_PLAN.json').write_text(json.dumps(wrong))
  try:Workspace(Path(tmp))
  except ValueError:pass
  else:assert False,'tampered SHA accepted'
  print('PASS: six real render views, VTK pick, brush edit, SHA replay, protected baseline, stale/invalid rejection, undo, tamper rejection')
if __name__=='__main__':check()
# Note: the integration test above deliberately uses a temporary, non-project fixture.
