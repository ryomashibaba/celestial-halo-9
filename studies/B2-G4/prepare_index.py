"""Prepare B-only artifact inventory. Run after review assembly, before GitHub upload.
Does not upload, promote, or modify any Git branch. Self-manifest excluded from its
own checksum list; root latest lists the completed manifest checksum separately.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
R=Path(__file__).resolve().parent
stamp=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
history={'study_id':'B2-G4','branch':'art/b','events':[{'event':'inherit_rejection','source':'references/Study01_REPORT_ja.md','status':'REJECT','note':'Inherited user rejection; the historical report may contain earlier selection wording.'},{'event':'inherit_rejection','source':'references/Study02_REPORT_ja.md','status':'REJECT','note':'Local study identifier preserved; not inventing an earlier GitHub submission.'}]+[{'event':'macro_art_review','concept':n,'status':'REJECT','reason':reason,'model':n+'/study.glb','detail_work':'STOP'} for n,reason in [('N1','Concentric walls dominate, insufficient new architectural identity.'),('N2','Podium and headland split; horizontal sea does not unify the building.'),('N3','Two mountain-like masses dominate; oppressive interiors, no inhabited city demonstrated.')]],'decision':'No selected concept. G4 redesign continues; G5 and construction HOLD.','formal_adoption':'USER_REVIEW_REQUIRED'}
write(R/'history.json',history)
kind={'.glb':'GLB','.blend':'BLEND','.png':'PNG','.jpg':'JPEG','.json':'JSON','.md':'REPORT','.py':'CODE','.ps1':'CODE','.html':'REVIEW','.log':'LOG'}
def asset(p):
 data=p.read_bytes()
 return {'path':p.relative_to(R.parent.parent).as_posix(),'kind':kind[p.suffix],'sha256':hashlib.sha256(data).hexdigest(),'size_bytes':len(data),'git_blob_sha':hashlib.sha1(('blob '+str(len(data))+'\0').encode()+data).hexdigest()}
files=sorted(p for p in R.rglob('*') if p.is_file() and p.suffix in kind and p.name!='manifest.json')
# Include per-concept manifests; exclude only the study's self-referential manifest.
files+=sorted(R.glob('*/manifest.json'))
assets=[asset(p) for p in files]
variant={n:json.loads((R/n/'manifest.json').read_text(encoding='utf-8'))['bounds_m'] for n in ['N1','N2','N3']}
study={'schema_version':'1.0','study_id':'B2-G4','track':'B','branch':'art/b','title':'巨大環境と都市の一体化 — 基本形3案・美術ゲートSTOP','stage':'BLOCKOUT_3D','art_review_status':'REJECT','review_authority':'Internal research self-review; formal art adoption belongs to user','updated_at':stamp,'dimensions_m':None,'proposed_dimensions_m':None,'measured_variants_m':variant,'selected_concept':None,'assets':assets,'validation':{'report':'studies/B2-G4/verification.json','actual_glb_reload':'PASS','shared_external_cameras':'PASS','art_gate':'FAIL','structural_feasibility':'NOT_TESTED','environment_simulation':'NOT_PERFORMED','inhabited_city_design':'NOT_COMPLETED'},'notes':'Three real GLBs and BLEND files. N1/N2/N3 all STOP before detail. 19 new PNGs + 4 baseline PNGs. No generated images. M247-C and Minecraft remain HOLD.'}
write(R/'manifest.json',study)
latest={k:v for k,v in study.items() if k not in ['schema_version','track','branch']}
latest['assets']=assets+[asset(R/'manifest.json')]
index={'schema_version':'1.0','branch':'art/b','track':'B','latest':latest,'history':[{'study_id':'B2-G4','manifest':'studies/B2-G4/manifest.json','event':'initial_submission','art_review_status':'REJECT','updated_at':stamp}],'last_submission_at':stamp,'policy':'ART-FIRST. Internal REJECT is research history, not formal adoption. M247-C and Minecraft construction remain HOLD.'}
write(R.parent.parent/'latest.json',index)
payload=latest['assets']+[asset(R.parent.parent/'latest.json')]
# Local upload receipt plan is kept outside the published study, with no secrets.
write(R.parent.parent/'B2-G4_upload_plan.json',payload)
print(json.dumps({'files':len(payload),'total_bytes':sum(a['size_bytes'] for a in payload),'max_file_bytes':max(a['size_bytes'] for a in payload),'updated_at':stamp}))
