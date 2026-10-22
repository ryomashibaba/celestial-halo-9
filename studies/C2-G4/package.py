"""Assemble model-derived evidence, retain earlier C research, validate GLBs.
No aesthetic pass is inferred from these checks.
"""
from pathlib import Path
import json,hashlib,shutil
import trimesh
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;W=R.parent.parent
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ref=R/'reference'/'asterion_rejected';ref.mkdir(parents=True,exist_ok=True)
old=W/'research_asterion_massing_reinvention'
if not old.exists():old=ref
for name in ['geometry.py','geometry.json','geometry_r1.py','geometry_r1.json','render.py','assemble.py','REVIEW.md','CONCEPTS.md','MEASUREMENTS.md','model_metrics.json','verification.json','glb_validation.json','protected_legacy_hashes.json','ASTERION_REINVENTION.glb','SIX_VIEWS.png']:
    if (old/name).resolve()!=(ref/name).resolve():shutil.copy2(old/name,ref/name)
archived={str(p.relative_to(ref)).replace('\\','/'):{'sha256':digest(p),'source_sha256':digest(old/p.name),'byte_identical':digest(p)==digest(old/p.name)} for p in ref.iterdir() if p.is_file()}
fontpath=Path('C:/Windows/Fonts/meiryo.ttc')
font=lambda s:ImageFont.truetype(str(fontpath),s)
def sheet(filename,title,tiles,cols=3,w=720):
    h=w*3//4;rows=(len(tiles)+cols-1)//cols;out=Image.new('RGB',(cols*w,74+rows*(h+60)),(16,24,34));d=ImageDraw.Draw(out);d.text((20,18),title,font=font(25),fill='white')
    for i,(p,label) in enumerate(tiles):
        im=Image.open(p).convert('RGB');im.thumbnail((w,h));x=i%cols*w;y=74+i//cols*(h+60);out.paste(im,(x+(w-im.width)//2,y));d.text((x+14,y+h+10),label,font=font(20),fill=(226,233,240))
    out.save(R/filename,optimize=True)
sheet('CONCEPT_COMPARISON.png','C2-G4｜二構想＋主質量改訂｜同一尺度・カメラ',[(R/'renders'/n/(view+'.png'),label+' / '+vlabel) for view,vlabel in [('02_oblique','斜視'),('04_top','俯瞰')] for n,label in [('N1','N1 聖湾公都・初形'),('N2','N2 天層公都'),('N1R1','N1-R1 聖湾公都・主質量改訂')]])
views=[('01_front','正面'),('02_oblique','斜視'),('03_side','側面'),('04_top','俯瞰'),('05_back','背面'),('06_middle_pedestrian','内部・中高度街路')]
sheet('SIX_VIEWS.png','C2-G4 N1-R1｜同じ実3Dの六視点｜美術自己審査：未達',[(R/'renders/N1R1'/(n+'.png'),l) for n,l in views])
sheet('BEFORE_AFTER.png','旧アステリオン → N1-R1｜5方向・同じ7800m画角',[(R/'renders'/n/(v+'.png'),label+' / '+l) for v,l in views[:5] for n,label in [('legacy','旧REJECT'),('N1R1','G4・未達')]],cols=2,w=720)
sheet('INTERIORS.png','N1-R1｜床上1.7m・24mm｜住宅計画・動線成立を保証しない',[(R/'renders/N1R1'/(n+'.png'),l) for n,l in [('06_middle_pedestrian','中高度街路：標高1458m'),('07_high_pedestrian','高高度街路：標高2708m'),('08_ground_pedestrian','地上公共広場：標高0m'),('09_hall_pedestrian','400×300×210m公共施設')]],cols=2,w=900)
validation={}
for name in ['N1','N2','N1R1']:
    s=trimesh.load(R/(name+'.glb'),force='scene')
    welded=[]
    for g in s.geometry.values():
        c=g.copy();c.merge_vertices();welded.append(c)
    validation[name]=dict(loaded=True,geometry_count=len(s.geometry),bounds=s.bounds.tolist(),dimensions_m=s.extents.tolist(),empty_geometries=[k for k,g in s.geometry.items() if len(g.vertices)==0],watertight_components=sum(g.is_watertight for g in s.geometry.values()),watertight_after_position_weld=sum(g.is_watertight for g in welded),component_count=len(s.geometry),method='Independent trimesh reload of exported GLB. Raw vertex splits are retained. Position-weld analysis changes copies only. Component watertightness is not union topology, structural, habitation or collision validation.')
metrics={n:json.loads((R/(n+'_metrics.json')).read_text()) for n in ['N1','N2','N1R1','legacy']}
common=['01_front','02_oblique','03_side','04_top','05_back']
protected=json.loads((old/'protected_legacy_hashes.json').read_text())
primary=W/'research_asterion_primary_gate'
changed=[p for p,v in protected.items() if not (primary/p).exists() or digest(primary/p)!=v['sha256']] if primary.exists() else None
verification=dict(track='C',branch='art/c',identity_evidence=['Local AGENTS.md: HALO9_Research_C','Previous REVIEW.md: Chat C / 天綾宮アステリオン','GitHub art/c latest.json: track C'],external_cameras_identical={n:all(metrics[n]['cameras'][k]==metrics['legacy']['cameras'][k] for k in common) for n in ['N1','N2','N1R1']},image_dimensions_comparison={n:Image.open(R/'renders'/n/'02_oblique.png').size for n in metrics},human_eye_floor_1_7m={n:abs(v['floor_below_eye'][0]-1.7)<.002 for n,v in metrics['N1R1']['rays'].items()},protected_prior_primary_files=len(protected),changed_prior_primary_files=changed,archived_legacy_files=archived,actual_3d=validation,claims_not_validated=['structural stability','continuous lift/terrace access','evacuation','dwelling interiors / population','city-wide occupancy or volume union','sacred/danger 80/20 perception','six-view aesthetic pass'],status='ART_SELF_REVIEW_FAIL / USER_ADOPTION_PENDING / DETAIL_HOLD / M247-C_AND_MINECRAFT_HOLD')
(R/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf-8')
assert not changed
assert all(verification['external_cameras_identical'].values())
assert all(verification['human_eye_floor_1_7m'].values())
assert all(v['loaded'] and not v['empty_geometries'] for v in validation.values())
print(json.dumps({n:dict(dimensions_m=v['dimensions_m'],geometries=v['component_count'],watertight=v['watertight_components']) for n,v in validation.items()},indent=2))
print('Verified model reload, cameras, eye heights and protected legacy hashes. NOT an art pass.')
