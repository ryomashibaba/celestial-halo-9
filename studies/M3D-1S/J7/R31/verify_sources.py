"""Read-only original checks against R30 base Git bytes. No world paths.
Offline: python -B -X utf8 verify_sources.py
"""
import sys,subprocess,hashlib,json
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;REPO=R.parents[3]
BASE='792dd34c96f6e9deefb8f8806fea478e5718b793'
MAIN='a2f88995eee8d10ee4830dbdf33ccb9c0790de8f'
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
paths=[]
for family in ('R29','R30'):
    paths+=git('ls-tree','-r','--name-only',BASE,'--',f'studies/M3D-1S/J7/{family}/').decode().splitlines()
paths+=['studies/M3D-1S/J7/R21/sheets/MATERIALS.jpg']
rows=[]
for p in paths:
    expected=git('show',BASE+':'+p);actual=(REPO/p).read_bytes()
    rows.append({'path':p,'bytes':len(actual),'sha256':hashlib.sha256(actual).hexdigest(),'unchanged':actual==expected})
policies=['AGENTS.md']+['docs/policy/'+p+'.md' for p in ('START_HERE','PROJECT_CONSTITUTION','CITY_MASTER_3D_STANDARD','CURRENT_STATUS','DECISION_LOG')]
out={'date_jst':'2026-10-26','main_confirmed_live_HEAD':MAIN,'R30_confirmed_live_HEAD':BASE,'R30_PR':63,'R30_state_at_start':'open/draft/unmerged','live_verification':'GitHub connector explicit main-ref reads, get_pr_info(63), network-enabled git ls-remote. This offline script does not itself refresh remote state.',
     'branch':git('branch','--show-current').decode().strip(),'authorization':'Current user explicitly authorizes R31 background Blender creation, isolated new branch, push and new Draft PR. Existing PR updates, main writes and merge are excluded.',
     'policy_blobs':[{'path':p,'ref':MAIN,'blob':git('rev-parse',MAIN+':'+p).decode().strip(),'sha256':hashlib.sha256(git('show',MAIN+':'+p)).hexdigest()} for p in policies],
     'source_files':rows,'all_unchanged':all(r['unchanged'] for r in rows),'R29_R30_count':len(rows)-1,'C55A_reference_sheet_count':1,
     'setup_rules':'LOCAL_WORK_RULES and SETUP_STATUS read. Missing current-branch local setup report read from integration/local-work-m121-setup-20261014 Git object.',
     'current_status_warning':'main CURRENT_STATUS dated 2026-10-23 and SETUP_STATUS are historical, not live research progress.',
     'actual_Minecraft_save_access':False,'foreground_computer_use':False,'new_paid_services':False,'canonical_anchor_count':0,'formal_art_adoptions':0,'construction':'HOLD','CITY_MASTER_3D_FIRST':'LOCKED; all city except ordinary private interiors must ultimately be detailed'}
(R/'qa/SOURCE_INTEGRITY.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
assert out['all_unchanged'];print('SOURCE_BYTES_UNCHANGED',len(rows))
