"""Read known Git objects only; record exact source versions. Offline, no save access."""
import subprocess,json,hashlib,sys
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
MAIN='a2f88995eee8d10ee4830dbdf33ccb9c0790de8f'
BASE='81cdbc878300f7a5a7e3b2309f90b395213bf604'
refs=[(MAIN,p) for p in ['AGENTS.md','docs/policy/START_HERE.md','docs/policy/PROJECT_CONSTITUTION.md','docs/policy/CITY_MASTER_3D_STANDARD.md','docs/policy/CURRENT_STATUS.md','docs/policy/DECISION_LOG.md']]
refs += [(BASE,p) for p in ['studies/M3D-1S/latest.json','studies/M3D-1S/J7/R13/R13_ART_REVIEW_JA.md','studies/M3D-1S/J7/R13/R13_HANDOFF.json','studies/M3D-1S/J7/R14/R14_ART_AND_QA_JA.md','studies/M3D-1S/J7/R14/R14_HANDOFF.json','studies/M3D-1S/J7/R14/outputs/R14_ACTUAL_BLENDER_PILOT_QA.json']]
out=[]
for ref,path in refs:
 b=subprocess.check_output(['git','show',ref+':'+path],cwd=R)
 out.append(dict(ref=ref,path=path,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
record=dict(date_jst='2026-10-25',repository='ryomashibaba/celestial-halo-9',main_verified=MAIN,R14_verified_latest_head=BASE,user_supplied_historical_R14_head='22b6a0092b91fdcfaf7b7eb78bbf4b6c8f04ed07',branch='research/m3d1s-j7-r15-symmetric-lived-world-20261025',sources=out,operation='Explicit user instruction authorizes background Blender, new research branch, push and new Draft PR only.',method='Separate background Blender 5.2.1; no Computer Use, no live Blender scene changes, 8 render threads.',boundary='R15 independent noncanonical coordinates. No actual Minecraft saves read or written; main, Freeze, M247-C and all earlier research unchanged.',retained_obligations=['W0','H1-H6','SB01-SB16','HERO4','three metropolitan axes','V1-V3'],formal_central_art_accepted=0,minecraft_construction='HOLD',master_10km_complete=False,R14_actual_QA_note='Latest R14 pilot QA contains a successful 1.7m ray; R14 report/handoff pending wording is stale. Art remains REJECT.',existing_pr_readonly_snapshot={'44':{'draft':True,'state':'open','head':'f8af02a57c3370ed3d5c38b1496757d6a913b0b4','base':'research/m3d1s-j7-r11-local-blender-art-20261025'},'45':{'draft':True,'state':'open','head':'2bb831bfa19a989ffadc3bbcb675eb8797faf6e9','base':'research/m3d1s-j7-r12-evidence-led-megastructure-gate-20261025'},'46':{'draft':True,'state':'open','head':BASE,'base':'research/m3d1s-j7-r13-habitable-world-mass-20261025'}})
(R/'qa/STARTUP_PROVENANCE.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print('Source versions recorded:',len(out))
