#!/usr/bin/env python3
import io,sys,json,hashlib,tempfile,traceback
from pathlib import Path
import numpy as np
import trimesh
from fastapi.testclient import TestClient
from d29_orthogonal_csg import fixture_glb,sha,carve_glb,TARGET,PUBLIC
from d29_visual_workbench import D29Workspace,create_app
from d29_audit import audit

ROOT=Path(__file__).resolve().parent
CUTS=[{'min':[-95,-270,40],'max':[95,-130,185]},
      {'min':[-210,-155,40],'max':[230,165,265]},
      {'min':[-60,-45,250],'max':[70,90,380]}]

def reject(fn,label):
    try:fn()
    except (ValueError, KeyError):return label
    raise AssertionError('expected rejection: '+label)

def verify():
    src=ROOT/'D29_SOURCE_NEUTRAL.glb';base=fixture_glb();src.write_bytes(base)
    work=ROOT/'D29_WORK';
    if work.exists():
        import shutil;shutil.rmtree(work)
    w=D29Workspace(work,src)
    assert w.raw==base
    models=[base];history=[]
    for label,box in zip(('ENTRY','ROOM','SKYLIGHT'),CUTS):
        state=w.commit_cut({'revision':w.revision,'box':box})
        result=w.edited
        p=ROOT/f'D29_{label}.glb';p.write_bytes(result)
        (ROOT/f'D29_PLAN_{label}.json').write_text(json.dumps({'baseline_sha256':sha(base),'target_geometry':TARGET,'voids':CUTS[:len(models)]},indent=2)+'\n')
        assert result==carve_glb(base,{'baseline_sha256':sha(base),'target_geometry':TARGET,'voids':CUTS[:len(models)]})
        models.append(result);history.append(state['revision'])
    (ROOT/'D29_BASE.glb').write_bytes(base)
    checks={}
    checks['source_unmodified']=sha(src.read_bytes())==sha(base)
    checks['undo_one']=w.undo(w.revision)['revision']==history[1]
    checks['undo_twice']=w.undo(w.revision)['revision']==history[0]
    checks['undo_all']=w.undo(w.revision)['revision']==sha(base)
    assert all(checks.values())
    w.commit_cut({'revision':w.revision,'box':CUTS[0]})
    w.commit_cut({'revision':w.revision,'box':CUTS[1]})
    w.commit_cut({'revision':w.revision,'box':CUTS[2]})
    work_reload=D29Workspace(work)
    checks['reload_byte_exact']=work_reload.edited==w.edited
    assert checks['reload_byte_exact']
    app=create_app(work_reload);client=TestClient(app)
    response=client.get('/');checks['http_html_loaded']=(response.status_code==200 and 'cut_custom' in response.text)
    checks['http_state_cut_count']=client.get('/api/state').json()['cut_count']==3
    checks['http_six_views']=all(client.get('/api/view/'+view).status_code==200 for view in ('front','rear','east','west','aerial','oblique'))
    checks['api_stale_revision_reject']=client.post('/api/cut',json={'revision':'stale','box':CUTS[0]}).status_code==422
    checks['api_fourth_cut_reject']=client.post('/api/cut',json={'revision':work_reload.revision,'box':CUTS[0]}).status_code==422
    checks['source_sha_reject']=reject(lambda:carve_glb(base,{'baseline_sha256':'0'*64,'target_geometry':TARGET,'voids':CUTS[:2]}),'wrong sha')
    checks['protected_route_target_reject']=reject(lambda:carve_glb(base,{'baseline_sha256':sha(base),'target_geometry':PUBLIC,'voids':CUTS[:2]}),'protected geometry')
    checks['bad_bounds_reject']=reject(lambda:carve_glb(base,{'baseline_sha256':sha(base),'target_geometry':TARGET,'voids':[{'min':[100,0,20],'max':[90,10,100]}]}),'inverted bounds')
    checks['closed_room_reject']=reject(lambda:carve_glb(base,{'baseline_sha256':sha(base),'target_geometry':TARGET,'voids':[CUTS[1]]}),'no exterior access')
    checks['out_of_mass_reject']=reject(lambda:carve_glb(base,{'baseline_sha256':sha(base),'target_geometry':TARGET,'voids':[{'min':[900,900,900],'max':[950,950,950]}]}),'void misses mass')
    checks['isolated_void_reject']=reject(lambda:carve_glb(base,{'baseline_sha256':sha(base),'target_geometry':TARGET,'voids':[CUTS[0],{'min':[260,40,80],'max':[300,90,130]}]}),'disconnected void')
    checks['original_never_rewritten']=sha(src.read_bytes())==sha(base)
    audit_data=audit(*models)
    assert all(v is True or isinstance(v,str) for v in checks.values()),checks
    return {'checks':checks,'model_validation':audit_data,'baselines':{'base':sha(base),'entry':sha(models[1]),'room':sha(models[2]),'skylight':sha(models[3])}}

if __name__=='__main__':
    a=verify()
    (ROOT/'D29_VERIFY.json').write_text(json.dumps(a,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'checks':a['checks'],'hashes':a['baselines']},indent=2))
