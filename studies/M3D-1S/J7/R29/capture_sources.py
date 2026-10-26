"""Fixed source provenance and local original integrity, no upstream execution."""
import sys,subprocess,hashlib,json
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;REPO=R.parents[3]
BASE='da2a2e630b95c939881db7428ac21ac85342346e';MAIN='a2f88995eee8d10ee4830dbdf33ccb9c0790de8f'
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def entry(ref,path):
    raw=git('show',ref+':'+path)
    return {'ref':ref,'path':path,'git_blob':git('rev-parse',ref+':'+path).decode().strip(),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
policy=['AGENTS.md']+['docs/policy/'+n+'.md' for n in ['START_HERE','PROJECT_CONSTITUTION','CITY_MASTER_3D_STANDARD','CURRENT_STATUS','DECISION_LOG','SOURCE_REGISTER']]
history=['R28/README_JA.md','R28/ART_REVIEW_JA.md','R28/build_estuary.py','R28/model/R28_CELESTIAL_ESTUARY.blend','R28/model/R28_CELESTIAL_ESTUARY.glb','R27B/ART_REVIEW_JA.md','R27B/qa/REVIEW_SHEET.jpg','R26/R26_WHOLE_CITY_ART_DIRECTION_JA.md','R27/R27_CITYWIDE_INTEGRATION_REALITY_GATE_JA.md','R27/R27_VERIFIED_ASSET_ANCHOR_REGISTER.json','R21/R21_ART_REVIEW_JA.md']
history += ['R21/source/code/'+n for n in ['c55a_city.py','c55a_geom.py','c55a_hall.py','blender_build.py']]
paths=git('ls-tree','-r','--name-only',BASE,'--','studies/M3D-1S/J7/R28/').decode().splitlines()
integrity=[]
for p in paths:
    raw=git('show',BASE+':'+p);actual=(REPO/p).read_bytes()
    integrity.append({'path':p,'unchanged_bytes':raw==actual,'sha256':hashlib.sha256(actual).hexdigest()})
out={'date_jst':'2026-10-26','main_head_verified_live':MAIN,'R28_head_verified_live':BASE,'PR61':'Draft/open/unmerged, base R27B; inspected via gh pr view before edits','branch':git('branch','--show-current').decode().strip(),'authorization':'User attached J7-R29 request: background Blender actual production, new branch and new Draft PR based on R28, push and download verification. No main/old PR/world edits.','policy_staleness':'CURRENT_STATUS dated 2026-10-23 is historical; current HEADs verified by live fetch and ls-remote, not taken from old setup table.','setup_report':'LOCAL_WORK_RULES and SETUP_STATUS read. Report absent in R28 tree, read via git show integration/local-work-m121-setup-20261014:docs/LOCAL_WORK_SETUP_20261014_JA.md.','sources':[entry(MAIN,p) for p in policy]+[entry(BASE,'studies/M3D-1S/J7/'+p) for p in history],'R28_original_files':integrity,'all_R28_original_files_unchanged':all(r['unchanged_bytes'] for r in integrity),'coordinates':'1 unit=1m, +X east/+Y north/+Z up. Relative R28 research frame only. No certified canonical anchors.','formal_art_adoptions':0,'minecraft':'HOLD','city_master_3d_first':'LOCKED','foreground_computer_use':False,'paid_services':False,'live_blender_mcp':False,'actual_save_access':False}
(R/'qa/STARTUP_AND_SOURCE_INTEGRITY.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
assert out['all_R28_original_files_unchanged'];print('SOURCE_INTEGRITY_PASS',len(integrity),'R28 files')
