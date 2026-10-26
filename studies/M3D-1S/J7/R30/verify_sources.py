"""Offline original integrity. No world paths and no generators from old evidence."""
import sys,subprocess,hashlib,json
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;REPO=R.parents[3]
BASE='d9f30a36946138359667676a904eba1a9c34da72';MAIN='a2f88995eee8d10ee4830dbdf33ccb9c0790de8f'
def git(*a):return subprocess.check_output(['git',*a],cwd=REPO)
policies=['AGENTS.md']+['docs/policy/'+n+'.md' for n in ['START_HERE','PROJECT_CONSTITUTION','CITY_MASTER_3D_STANDARD','CURRENT_STATUS','DECISION_LOG']]
rows=[]
for family in ['R28','R29']:
    paths=git('ls-tree','-r','--name-only',BASE,'--',f'studies/M3D-1S/J7/{family}/').decode().splitlines()
    for p in paths:
        raw=git('show',BASE+':'+p);actual=(REPO/p).read_bytes()
        rows.append(dict(path=p,bytes=len(actual),sha256=hashlib.sha256(actual).hexdigest(),unchanged=raw==actual))
out=dict(date_jst='2026-10-26',main_verified_live=MAIN,r29_verified_live=BASE,method='git ls-remote with network access; explicit main-ref connector reads; offline original byte comparison',
         branch=git('branch','--show-current').decode().strip(),r29_pr=62,r28_pr=61,c55a_comparison_pr=53,
         policy_blobs=[dict(path=p,ref=MAIN,blob=git('rev-parse',MAIN+':'+p).decode().strip(),sha256=hashlib.sha256(git('show',MAIN+':'+p)).hexdigest()) for p in policies],
         current_status_staleness='main CURRENT_STATUS is dated 2026-10-23. Its old HEAD table is not used as live state.',
         originals=rows,all_unchanged=all(r['unchanged'] for r in rows),
         source_restore='Local R29 checkout HEAD matches live PR62 and git remote; existing BLEND/GLB are verified byte-for-byte against git objects. No duplicate download needed.',
         authorization='Current user explicitly authorizes R30 A/B background Blender production, independent branch, new Draft PR and readback. Prior no-push default is superseded only for this research delivery.',
         local_setup='LOCAL_WORK_RULES and SETUP_STATUS read; old setup report read via integration/local-work-m121-setup-20261014 git object because absent from current checkout.',
         live_mcp='get_addon_status could not connect; no live scene modified',foreground_computer_use=False,paid_services=False,actual_minecraft_save_access=False,canonical_anchor_count=0,formal_art_adoptions=0)
(R/'qa/SOURCE_INTEGRITY.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
assert out['all_unchanged'];print('ORIGINAL_BYTES_PASS',len(rows))
