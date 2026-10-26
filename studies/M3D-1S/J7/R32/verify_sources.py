"""Read-only original bytes vs fixed R31 Git base. python -B -X utf8."""
import sys,subprocess,hashlib,json,ast
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;REPO=R.parents[3]
BASE='69db4bd27f6dc051c5dfdd7b889b819f4e8cc7a3';MAIN='a2f88995eee8d10ee4830dbdf33ccb9c0790de8f'
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
rows=[]
for family in ('R29','R30','R31'):
    for p in git('ls-tree','-r','--name-only',BASE,'--',f'studies/M3D-1S/J7/{family}/').decode().splitlines():
        expected=git('show',BASE+':'+p);actual=(REPO/p).read_bytes()
        rows.append({'path':p,'bytes':len(actual),'sha256':hashlib.sha256(actual).hexdigest(),'unchanged':actual==expected})
policies=['AGENTS.md']+['docs/policy/'+p+'.md' for p in ('START_HERE','PROJECT_CONSTITUTION','CITY_MASTER_3D_STANDARD','CURRENT_STATUS','DECISION_LOG')]
for p in R.glob('*.py'):ast.parse(p.read_text(encoding='utf-8-sig'))
out={'date_jst':'2026-10-26','main_verified_live_HEAD':MAIN,'R30_verified_live_HEAD':'792dd34c96f6e9deefb8f8806fea478e5718b793','R31_verified_live_HEAD':BASE,
     'remote_verification':'Explicit git fetch origin main; git ls-remote origin for main/R30/R31; GitHub connector PR63/64 both open/draft/unmerged with specified HEADs.',
     'policy_read':'All six files explicitly read from freshly fetched main Git object. CURRENT_STATUS and SETUP_STATUS are historical, not current research state. Local setup report read via integration branch Git object.',
     'policy_blobs':[{'path':p,'ref':MAIN,'blob':git('rev-parse',MAIN+':'+p).decode().strip(),'sha256':hashlib.sha256(git('show',MAIN+':'+p)).hexdigest()} for p in policies],
     'branch':git('branch','--show-current').decode().strip(),'source_files':rows,'all_unchanged':all(r['unchanged'] for r in rows),
     'scope':'Only R32 additions; existing untracked research/ preserved. User explicitly authorizes background Blender, new R32 branch, push, new Draft PR; no existing PR mutation, main write or merge.',
     'Minecraft_save_access':False,'foreground_computer_use':False,'new_accounts_or_paid_services':False,'formal_anchor_count':0,'formal_art_adoptions':0,'construction':'HOLD','CITY_MASTER':'LOCKED, incomplete'}
(R/'qa/SOURCE_INTEGRITY.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
assert out['all_unchanged'];print('SOURCE_BYTES_UNCHANGED',len(rows))
