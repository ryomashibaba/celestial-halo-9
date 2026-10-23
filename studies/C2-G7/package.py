"""Minimal G7 checks, immutable G6 protection, schema index and history. No network."""
from pathlib import Path
import hashlib,json,datetime
import numpy as np
import trimesh
from PIL import Image
R=Path(__file__).resolve().parent;W=R.parent.parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
protected=read(R/'protected_hashes.json')
assert all(sha(W/p)==h for p,h in protected.items() if p!='latest.json_BASELINE')
expected={'studies/C2-G6/A.blend':'c7506eb8556713e8b21cf0e1dc9e25f9d3c992e1a1d9bfe5c3e6804185302e01','studies/C2-G6/A_CENTRAL.glb':'e5d2fcdb8ffd1a23ac3d4a1d56cc2208706c526d69c5fb90c48599caf03d9d9e'}
assert all(sha(W/p)==h for p,h in expected.items())
src=read(R/'g6_review_source.json');new=read(R/'new_metrics.json')
models={}
for rel in ['studies/C2-G6/A_CENTRAL.glb','studies/C2-G7/N1_CENTRAL.glb']:
 scene=trimesh.load(W/rel,force='scene');meshes=list(scene.geometry.values());assert meshes and all(np.isfinite(m.vertices).all() for m in meshes)
 m=max(meshes,key=lambda m:len(m.faces)).copy();m.merge_vertices()
 dims=[float(scene.extents[i]) for i in [0,2,1]]
 models[rel]={'load':'PASS','finite_vertices':True,'geometry_count':len(meshes),'dimensions_m_xyz_z_up':dims,'main_mass_watertight_after_merge':bool(m.is_watertight),'main_mass_connected_components':len(m.split(only_watertight=False))}
 expected_dims=src['loaded_central_dimensions_m'] if 'C2-G6' in rel else new['dimensions_m']
 assert np.allclose(dims,expected_dims,atol=.1)
assert (R/'preview.jpg').stat().st_size<=600000
images={}
for p in R.glob('*.jpg'):
 with Image.open(p) as im:im.load();images[p.name]={'pixels':list(im.size),'bytes':p.stat().st_size}
assert len([x for x in images if x.startswith('g6_')])==3
assert len([x for x in images if x.startswith('new_') and x!='new_comparison.jpg'])==3
assert not list(R.glob('*.blend'))
verification={'study_id':'C2-G7','date_jst':'2026-10-23','basis_commit':'aaa0696f0239d05eda60c6bfeffe528363d8af3d','g6_source_hashes_match_basis_manifest':True,'protected_g6_files_unchanged':len(protected)-1,'initial_comparison_used_for_final_preview':False,'G6_models_or_high_resolution_images_rebuilt':False,'gltf':models,'images':images,'preview_under_600000_bytes':True,'new_3D_candidate_count':1,'camera_render_count':6,'camera_render_pixels':[960,720],'housing_mass_addition':False,'detailed_interiors':False,'art_decisions':{'G6_final_A_self_rereview':'REJECT_DETAIL_STOP','G7_N1':'REJECT_DETAIL_STOP','G7_N2':'UNRESOLVED_CONCEPT_NOT_MODELED'},'selected_promising_candidate':None,'formal_M247_C':'UNCHANGED','minecraft':'HOLD','work_migration':False,'limits':['No structural analysis, all-route testing, population or habitable-area validation','N1 main body is non-watertight after vertex merge','Synthetic background only; no current SB/H/V coordinates claimed','G6 samples12 vs N1 samples14; shared camera/background/sun/world but not pixel-identical settings','Technical load/dimension success does not constitute art acceptance']}
write(R/'verification.json',verification)
write(R/'history.json',{'study_id':'C2-G7','basis_commit':verification['basis_commit'],'previous_study':'C2-G6','previous_history_preserved':True,'events':[{'event':'REVIEW_EXACT_G6_FINAL_BLEND','preview':'studies/C2-G7/preview.jpg','status':'SELF_REJECT_DETAIL_STOP'},{'event':'COMPARE_TWO_DIFFERENT_FORMATION_PRINCIPLES','concepts':['N1 交室都宮','N2 双地盤会都']},{'event':'MODEL_ONLY_N1_AND_REVIEW_THREE_DIRECTIONS','status':'SELF_REJECT_DETAIL_STOP','selected_candidate':None}]})
old=read(W/'latest.json')
files=[p for p in R.iterdir() if p.is_file() and p.suffix in ['.jpg','.glb','.py','.md','.json'] and p.name!='manifest.json' and '.local.' not in p.name]
assets=[{'path':p.relative_to(W).as_posix(),'kind':{'.jpg':'JPEG','.glb':'GLB','.py':'CODE','.md':'REPORT'}.get(p.suffix,'JSON'),'sha256':sha(p),'size_bytes':p.stat().st_size} for p in sorted(files)]
latest={'study_id':'C2-G7','track':'C','branch':'art/c','title':'会流天蓋最終再審査・新主質量の不合格記録','stage':'BLOCKOUT_3D','art_review_status':'REJECT','review_authority':'C_SELF_REVIEW_NOT_FORMAL_ADOPTION','updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'date':'2026-10-23','dimensions_m':dict(zip(['width','depth','height'],new['dimensions_m'])),'dimensions_subject':'G7_N1_REJECTED_TEST','proposed_dimensions_m':None,'assets':assets,'validation':verification,'report':'studies/C2-G7/decision.md','preview':'studies/C2-G7/preview.jpg','preview_subject':'G6_FINAL_A_NOT_G7_N1','new_preview':'studies/C2-G7/new_comparison.jpg','model':'studies/C2-G7/N1_CENTRAL.glb','model_role':'REJECTED_RESEARCH_TEST','selected_candidate':None,'notes':'G6 final and G7 N1 fail art self-review. N2 is unresolved concept only. Detail stopped; prior evidence retained.','formal_adoption':False,'formal_M247_C':'UNCHANGED','minecraft':'HOLD','work':'PRIOR_APPROVAL_REQUIRED'}
write(R/'manifest.json',{'schema_version':'1.0',**latest})
old['latest']=latest;old['history']=[h for h in old.get('history',[]) if h.get('study_id')!='C2-G7']+[{'study_id':'C2-G7','manifest':'studies/C2-G7/manifest.json','stage':'BLOCKOUT_3D','art_review_status':'REJECT','selected_candidate':None}];old['last_submission_at']='2026-10-23'
write(W/'latest.json',old)
print(json.dumps({'assets':len(assets),'bytes':sum(x['size_bytes'] for x in assets),'preview_bytes':images['preview.jpg']['bytes'],'new_glb_bytes':(R/'N1_CENTRAL.glb').stat().st_size,'protected_g6_files':len(protected)-1,'art':'REJECT_DETAIL_STOP'},ensure_ascii=False))
