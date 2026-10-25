"""Read only provenance and legacy data, never imports any upstream renderer."""
import sys, json, hashlib, subprocess
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;repo=R.parents[3]
def git(*args):return subprocess.check_output(['git',*args],cwd=repo)
def record(ref,path):
    raw=git('show',ref+':'+path)
    return {'ref':ref,'path':path,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'blob':git('rev-parse',ref+':'+path).decode().strip()}
main=git('rev-parse','origin/main').decode().strip()
base='61608a286922e296ffc129f844fe0e700dae0518'
policy=['AGENTS.md']+['docs/policy/'+n+'.md' for n in ['START_HERE','PROJECT_CONSTITUTION','CITY_MASTER_3D_STANDARD','CURRENT_STATUS','DECISION_LOG','SOURCE_REGISTER']]
history=['R26/R26_WHOLE_CITY_ART_DIRECTION_JA.md','R26/R26_CITYWIDE_MASTER_GATE.json','R27/R27_CITYWIDE_INTEGRATION_REALITY_GATE_JA.md','R27/R27_VERIFIED_ASSET_ANCHOR_REGISTER.json','R9/REPORT_JA.md','R14/R14_ART_AND_QA_JA.md','R18/R18_CIVILIZATION_LANDSCAPE_ART_DIRECTION_JA.md','R19/R19_ART_REVIEW_JA.md','R21/R21_ART_REVIEW_JA.md','R23/R23_ART_REVIEW_JA.md','R25_EXEC/qa/INDEPENDENT_ART_REVIEW_JA.md']
records=[record(main,p) for p in policy]+[record(base,'studies/M3D-1S/J7/'+p) for p in history]
records.append(record(base,'studies/M3D-1S/proxies/COMMON_W0_NONCANONICAL_CONTEXT.obj'))
legacy=[]
for n in ['M117_USER_READONLY_ATLAS.json','M121_B_PUBLIC_REALM_RESEARCH.json']:
    path=repo/'research/m121/upstream/data'/n;raw=path.read_bytes();data=json.loads(raw)
    counts=({'meshes':len(data['meshes']),'facilities':len(data['facility_programs']),'route_intents':len(data['unverified_route_intents'])}
            if 'meshes' in data else {'top_level_keys':list(data)})
    legacy.append({'path':str(path.relative_to(repo)),'sha256':hashlib.sha256(raw).hexdigest(),'git_blob':git('hash-object',str(path)).decode().strip(),'actual_read_summary':counts,'json_keys':list(data)})
out={'date_jst':'2026-10-25','main_verified_head':main,'base_verified_head':base,'base_pr':59,
     'branch':git('branch','--show-current').decode().strip(),'records':records,'legacy_read_only_files':legacy,
     'canonical_common_anchors_certified':0,'official_terrain_source':'NOT_LOCATED in inspected repository tree, R27A register and local M121 sources',
     'M247_C':'Protected direction confirmed from main. No adopted central original imported; no original modified.',
     'existing_W0_proxy':'Noncanonical marked proxy inspected, not imported as official terrain',
     'sky_and_facility_sources':'No certified current six-district or sixteen-facility integrated master located in inspected sources',
     'new_geometry_provenance':'All model geometry newly authored in build_city.py. No old 912x416 block cluster scaling or old mesh import.',
     'authorization':'User pasted R27B request explicitly permits background local Blender, new branch, push and NEW Draft PR only',
     'policy_amendments':None,'actual_save_access':False,'foreground_UI_control':False,'untracked_research_preserved':True}
(R/'qa/STARTUP_PROVENANCE.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('Source provenance captured:',main,base,len(records))
