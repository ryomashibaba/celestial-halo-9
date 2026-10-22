from pathlib import Path
import json,hashlib,datetime
root=Path(__file__).resolve().parents[2]
folder=root/'studies/A2-G4'
old=json.loads((folder/'inherited/latest-A2-G3.json').read_text(encoding='utf8'))
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
assets=[]
for f in sorted(folder.rglob('*')):
 if not f.is_file() or f.name in ['manifest.json','SHA256SUMS.txt']:continue
 b=f.read_bytes();ext=f.suffix.lower()
 assets.append({'path':f.relative_to(root).as_posix(),'kind':{'.py':'CODE','.md':'REPORT','.json':'JSON','.png':'PNG','.glb':'GLB','.blend':'BLEND'}[ext],'sha256':hashlib.sha256(b).hexdigest(),'size_bytes':len(b)})
validation=json.loads((folder/'validation.json').read_text(encoding='utf8'))
entry={'study_id':'A2-G4','title':'七内天・回天褶都／共晶聖都・三院共嶺 — 主質量二構想と再設計の実3D比較','stage':'BLOCKOUT_3D','art_review_status':'HOLD','updated_at':stamp,'dimensions_m':validation['models']['P2R']['dimensions_m'],'proposed_dimensions_m':None,'dimensions_scope':'P2R only, verified GLB world bounds excluding context; includes district markers. P1/P2 dimensions in validation.json.','assets':assets,'validation':{'model_load':'All three GLBs reimported in Blender and independently loaded in trimesh','mesh_qa':'All three primary masses watertight and winding-consistent after reassembling material partitions; individual partitions can be open. See mesh-qa.json.','external_camera_comparison':'Five identical 8500m orthographic cameras, 1000x900, same light and 10km context. Renders produced after actual GLB reimport.','internal_camera_comparison':'Different camera per spatial concept; not a controlled comparison','district_centre_support':{'P1':'11/36 within5m','P2':'19/24 within5m','P2R':'216/216 within5m'},'limits':['Not complete inhabited cities','N3 four-horizon visibility not revalidated on G4','G3 C3 shared public wall not equivalently proven on G4','P1/P2 support defects preserved','No engineering or construction feasibility','Art targets not achieved; no detail progression']},'notes':'Two concepts and one main-mass revision; no art candidate selected. HOLD is this study working judgment, not a user formal REJECT or acceptance. M247-C and Minecraft construction remain HOLD.'}
manifest={'schema_version':old['schema_version'],'branch':'art/a','track':'A',**entry,'provenance':{'baseline_commit':'2557681ad23a14399c6d5071d6b9adb0915ec8ba','prior_study':'A2-G3','prior_manifest_path':'studies/A2-G3/manifest.json','track_identification':'Local A2/G3 artifacts match art/a HEAD submission'},'execution':{'environment':'Existing local research workspace; no Work handoff','blender':'5.2.1 LTS','native_generation':False,'render_source':'Exported and reimported GLB meshes','decision':'Stop detail; retain spatial findings and return to main-mass ideation'}}
(folder/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
f=folder/'manifest.json';b=f.read_bytes();ma={'path':f.relative_to(root).as_posix(),'kind':'JSON','sha256':hashlib.sha256(b).hexdigest(),'size_bytes':len(b)}
history=list(old['history'])
if not any(x['study_id']==old['latest']['study_id'] for x in history):history.append({'study_id':old['latest']['study_id'],'manifest_path':'studies/'+old['latest']['study_id']+'/manifest.json'})
latest={**old,'latest':{**entry,'assets':assets+[ma]},'history':history,'last_submission_at':stamp}
(root/'latest.json').write_text(json.dumps(latest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(folder/'SHA256SUMS.txt').write_text(''.join(x['sha256']+'  '+x['path']+'\n' for x in assets+[ma]),encoding='utf8')
for a in assets+[ma]:
 b=(root/a['path']).read_bytes();assert len(b)==a['size_bytes'] and hashlib.sha256(b).hexdigest()==a['sha256']
print(json.dumps({'assets':len(assets)+1,'total_bytes':sum(a['size_bytes'] for a in assets+[ma]),'history':history,'max_file_bytes':max(a['size_bytes'] for a in assets+[ma]),'hashes':'VERIFIED'}))
