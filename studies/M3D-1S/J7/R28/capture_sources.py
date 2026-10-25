"""Record fixed policy/history blobs without running upstream source code."""
import sys, subprocess, hashlib, json
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;repo=R.parents[3]
BASE='60bff854b8cec7265a50de34190d740a626d4c13'
MAIN='a2f88995eee8d10ee4830dbdf33ccb9c0790de8f'
def git(*a):return subprocess.check_output(['git',*a],cwd=repo)
def entry(ref,p):
    raw=git('show',ref+':'+p)
    return {'ref':ref,'path':p,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
            'git_blob':git('rev-parse',ref+':'+p).decode().strip()}
policy=['AGENTS.md']+['docs/policy/'+n+'.md' for n in ['START_HERE','PROJECT_CONSTITUTION','CITY_MASTER_3D_STANDARD','CURRENT_STATUS','DECISION_LOG']]
history=['R21/source/code/'+n for n in ['c55a_city.py','c55a_geom.py','c55a_hall.py','blender_build.py']]
history += ['R21/R21_ART_REVIEW_JA.md','R26/R26_WHOLE_CITY_ART_DIRECTION_JA.md',
    'R27/R27_CITYWIDE_INTEGRATION_REALITY_GATE_JA.md','R27/R27_VERIFIED_ASSET_ANCHOR_REGISTER.json',
    'R27B/build_city.py','R27B/ART_REVIEW_JA.md','R27B/README_JA.md','R27B/model/R27B_LIVING_HORIZONS.blend','R27B/qa/REVIEW_SHEET.jpg']
out={'date_jst':'2026-10-26','verified_main_head':MAIN,'verified_R27B_head':BASE,
 'verification':'Live Git ls-remote after successful fetch + GitHub connector main files and PR60 metadata; PR60 draft/open/unmerged',
 'policy_current_status_date':'2026-10-23; historical rolling contents are stale; do not treat listed old HEADs as current',
 'branch':git('branch','--show-current').decode().strip(),'sources':[entry(MAIN,p) for p in policy]+[entry(BASE,'studies/M3D-1S/J7/'+p) for p in history],
 'local_setup_status':'SETUP_STATUS.txt read; dated 2026-10-14. Referenced setup report absent in current checkout (also recorded by R21). Current R27B HEAD verified directly.',
 'authorization':'2026-10-26 attached R28 request: background local Blender production, new R28 branch, push and new Draft PR. No merge or existing PR writes authorized.',
 'canonical_common_coordinate_anchors':'Not certified; retain R27A unresolved asset/transform status',
 'geometry':'Entire R28 newly authored; no legacy model import, no old city scaling. C55-A code read as principles only; no source code copied or executed.',
 'canonical_changes':False,'world_save_access':False,'foreground_UI_control':False,'paid_external_AI':False,
 'policy_amendment':None,'formal_central_art_adoptions':0,'minecraft':'HOLD','CITY_MASTER_3D_FIRST':'LOCKED'}
(R/'qa/STARTUP_PROVENANCE.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print('R28 source records',len(out['sources']),MAIN,BASE)
