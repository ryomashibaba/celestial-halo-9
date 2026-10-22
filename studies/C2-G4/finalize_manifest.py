from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;W=R.parent.parent
record=dict(study_id='C2-G4',track='C',branch='art/c',date='2026-10-22',status='ART_SELF_REVIEW_FAIL',formal_adoption='USER_DECISION_PENDING',next_step='G4_MASSING_REDESIGN',detail='HOLD',formal_M247_C='UNCHANGED',minecraft='HOLD',report='studies/C2-G4/REPORT.md',model='studies/C2-G4/N1R1.glb',preview='studies/C2-G4/CONCEPT_COMPARISON.png')
history=dict(study_id='C2-G4',events=[dict(stage='inheritance',result='Prior Asterion art rejection and technical assets retained; do not relabel as approved'),dict(stage='concept_comparison',models=['N1','N2'],result='Both aesthetics fail. N1 selected for further massing test only'),dict(stage='primary_mass_revision',model='N1R1',result='Still fails: vessel reading, sparse city, disconnected circulation'),dict(stage='review',result='STOP DETAIL; continue G4 primary mass research; user adoption pending')],latest=record)
(R/'history.json').write_text(json.dumps(history,ensure_ascii=False,indent=2),encoding='utf-8')
latest=dict(schema_version='1.0',branch='art/c',track='C',latest=record,history=[record],last_submission_at='2026-10-22',policy='ART-FIRST. Formal M247-C and Minecraft construction remain HOLD. Technical checks and study storage do not constitute art acceptance.')
(W/'latest.json').write_text(json.dumps(latest,ensure_ascii=False,indent=2),encoding='utf-8')
excluded={'manifest.json','blob_receipt.json','upload_tree_receipt.json','delivery_receipt.json'}
files={}
for p in sorted(R.rglob('*')):
    if p.is_file() and p.suffix in ['.py','.md','.json','.png','.glb','.blend'] and p.name not in excluded:
        files[str(p.relative_to(W)).replace('\\','/')]=dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
manifest=dict(schema_version='1.0',study_id='C2-G4',branch='art/c',parent_commit='36599732dc82d1496851a30d70d38bcd0cf7f44b',art_status='SELF_REVIEW_FAIL',actual_3d=True,ai_generated_images=False,files=files,total_bytes=sum(v['bytes'] for v in files.values()))
(R/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print('Files',len(files),'Bytes',manifest['total_bytes'],'Largest',max(v['bytes'] for v in files.values()))
