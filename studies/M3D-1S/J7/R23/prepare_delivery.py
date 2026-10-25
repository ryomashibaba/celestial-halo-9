import sys,json,hashlib,re,subprocess
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
handoff=dict(schema='halo9.j7r23.v1',date_jst='2026-10-25',stage='J7-R23',art='REJECT',initial_art_gate='FAIL',second_stage_started=False,
    base_r21_head='628abb8d80e3e39a9bad6dd5fe7dec7556a0bcd9',verified_main_head='a2f88995eee8d10ee4830dbdf33ccb9c0790de8f',
    branch='research/m3d1s-j7-r23-crossing-horizons-20261025',title='交叉天陸 / CROSSING HORIZONS',macro_revisions=2,
    models=['initial/R23_INITIAL.blend','revision/R23_REVISED.blend','final/R23_CROSSING_HORIZONS.blend','final/R23_CROSSING_HORIZONS.glb'],
    principal_renders=dict(initial=8,revision=8,final=11,sections=2,retained_failed=1),
    actual_sections=['sections/LONG_Xminus800.blend','sections/CROSS_Y500.blend'],
    geometry_dimensions_m=[7550,7241.93408203125,5150],highest_point_m=4930,
    save_reload='BLEND exact vertex fingerprint and triangle count match; GLB AABB error 0m and same 3481 triangles',
    quality='FAIL: transverse continent has 3 boundary/nonmanifold edges and 1 degenerate face; overlapping surfaces produce visible artifacts',
    art_reason='Blank folded giant parts still dominate. Distinct inhabited urban worlds, destinations, rear/underside architecture and human-scale depth not achieved.',
    next='Do not decorate or adopt this massing. Re-design concrete connected floor-level destinations and their joins in parallel with the entire silhouette; change the mass-first loft/carve method.',
    not_verified=['global intersections/unions','closed connected air volume','continuous walkability','ground-to-sky transport','structural safety','inhabited room capacity','official city coordinates','Minecraft suitability'],
    art_review='R23_ART_REVIEW_JA.md',qa='qa/FINAL_VERIFICATION.json',official_art_adoptions=0,minecraft_construction='HOLD',detailed_10km_city_master_complete=False,
    main_existing_pr_originals_freeze_protected_changed=False,actual_minecraft_saves_accessed=False,foreground_computer_use=False,auto_merge=False,
    github_delivery='PENDING',draft_pr=None,artifact_commit=None)
(R/'R23_HANDOFF.json').write_text(json.dumps(handoff,ensure_ascii=False,indent=2),encoding='utf8')
# Frozen production manifest: excludes itself and later delivery metadata.
files=[]
for p in sorted(R.rglob('*')):
    if not p.is_file() or p.name in ['MANIFEST_SHA256.json','R23_HANDOFF.json'] or p.name.startswith(('GITHUB_','DELIVERY')) or re.search(r'\.blend\d+$',p.name) or '__pycache__' in p.parts:continue
    # Git may normalize text newlines. Manifest the staged bytes actually sent
    # to GitHub, rather than claiming raw Windows log bytes are identical.
    rel='studies/M3D-1S/J7/R23/'+p.relative_to(R).as_posix()
    b=subprocess.check_output(['git','show',':'+rel]);files.append(dict(path=p.relative_to(R).as_posix(),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
out=dict(scope='Frozen production Git-index bytes (text newline normalization included); excludes manifest self, mutable handoff, later delivery receipts and Blender backups',files=len(files),bytes=sum(v['bytes'] for v in files),entries=files)
(R/'MANIFEST_SHA256.json').write_text(json.dumps(out,indent=2),encoding='utf8')
assert all((R/f).is_file() for f in handoff['models']+handoff['actual_sections'])
for folder,n in [('initial',8),('revision',8),('final',11)]:assert len(list((R/folder/'renders').glob('*.png')))==n
assert len(list((R/'sections').glob('*.png')))==2
for p in R.rglob('*.md'):
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',p.read_text(encoding='utf8')):
        if '://' in target or target.startswith('#'):continue
        assert (p.parent/target.split('#')[0]).exists(),(p,target)
print(json.dumps({k:v for k,v in out.items() if k!='entries'}))
