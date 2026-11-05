"""Hash only this research delivery and record exact inherited Git sources."""
from pathlib import Path
import subprocess,hashlib,json
R=Path(__file__).parent;repo=R.parents[4]
def git(*args):return subprocess.check_output(['git','-C',str(repo),*args])
base='94073f97cd65e346e5a3a9846f8dd48a73c6e8e4'
main='a2f88995eee8d10ee4830dbdf33ccb9c0790de8f'
sources=[]
for p in ['AGENTS.md']+['docs/policy/'+n+'.md' for n in ['START_HERE','PROJECT_CONSTITUTION','CITY_MASTER_3D_STANDARD','CURRENT_STATUS','DECISION_LOG','SOURCE_REGISTER']]:
    raw=git('show',main+':'+p)
    sources.append({'ref':main,'path':p,'sha256':hashlib.sha256(raw).hexdigest(),'read_scope':'full'})
for p in [
 'studies/M3D-1S/J7/R33-S27/D48_R4_E5/HALO9_COMPLETE_HANDOFF_E5_CRITICAL_REVIEW_20261105_JA.md',
 'studies/M3D-1S/J7/R33-S27/D48_R4_E6/E6_DIRECT_NATIVE_ART_JURY_JA.md',
 'studies/M3D-1S/J7/R33-S27/D48_R4_E8/E8_DIRECT_NATIVE_ART_REVIEW_AND_NEXT_HANDOFF_JA.md',
 'studies/M3D-1S/J7/R33-S27/D48_R4_E9_R1/E9_R1_TRUE_NATIVE_CRITICAL_ART_JURY_AND_HANDOFF_JA.md',
 'studies/M3D-1S/J7/R33-S27/D48_R4_E10/E10_DIRECT_ART_JURY_AND_GUI_SCULPT_HANDOFF_JA.md']:
    raw=git('show',base+':'+p)
    sources.append({'ref':base,'path':p,'sha256':hashlib.sha256(raw).hexdigest(),'read_scope':'full'})
(R/'INHERITED_SOURCE_REFS.json').write_text(json.dumps({'verified_main':main,'verified_e10':base,'sources':sources,'scope_limit':'Not a fresh exhaustive audit of every historical individual asset'},indent=2),encoding='utf-8')
relative=R.relative_to(repo).as_posix()
paths=sorted(set(git('ls-files','--cached','--others','--exclude-standard','--',relative).decode('utf-8').splitlines()))
rows=[]
for p in paths:
    f=repo/p
    if f.name=='SHA256SUMS.txt':continue
    assert f.stat().st_size<50*1024*1024
    rows.append(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.relative_to(R).as_posix())
(R/'SHA256SUMS.txt').write_text('\n'.join(rows)+'\n',encoding='utf-8')
for row in rows:
    digest,p=row.split('  ',1);assert hashlib.sha256((R/p).read_bytes()).hexdigest()==digest
print('DELIVERY_SHA256_PASS',len(rows),'FILES')
