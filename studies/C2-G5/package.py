"""Package and verify concept deliverables; no network or world IO."""
from pathlib import Path
from PIL import Image
import json,csv,hashlib,datetime,re
R=Path(__file__).resolve().parent;W=R.parent.parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def info(p):
 b=p.read_bytes();return {'path':p.relative_to(W).as_posix(),'kind':{'.png':'PNG','.py':'CODE','.md':'REPORT','.csv':'CSV'}.get(p.suffix,'JSON'),'sha256':hashlib.sha256(b).hexdigest(),'size_bytes':len(b)}
report=(R/'REPORT.md').read_text(encoding='utf-8')
names=['West Lantern Trade Quarter','Artisan Spine','Echo Market','Rain Conservatory','RADIANT SAIL CITADEL','Civic Auditorium','Public Forum','AURORA TWIN VAULT','GRAND HALO GATEWAY','Transit Hall','Harmonic Assembly','MOUNTAIN HALO SANCTUARY','South Threshold District','Orbital Machine Hall','Prism Studios','Dusk Observation Ward']
a=['日常商業の入口','制作・修理の近接目的地','行事外の日常市場','裂隙の緑・滞在','集会前室が低い肩を生む','集会の手前の小討議室','地上・中高度の受入れ','二室が採光裂隙を生む','前庭の空白で質量が後退','側方の乗換と昇降','夜間利用と生活の接点','静かな高所が片肩を生む','到着時の方向認識','SPINE接続を学ぶ目的地','生活街路と創作活動','中央を外から見る終点']
b=['庭へ物資・市を分散','制作と展示の交換','庭間の商業','静かな庭・学習','集いと討議の下部大室','討議活動の仲介','公共室間の共通討議','中高度の文化体験','谷の入口で通過を分流','中央迂回の拠点間交通','上演・交流の庭','静かな高所の室','分散経路への案内','技術と制作の往来','成果を持ち寄る活動','分散中心への対向視点']
with (R/'RELATIONS.csv').open('w',encoding='utf-8-sig',newline='') as out:
 wr=csv.writer(out);wr.writerow(['id','group','historical_M119_name','current_name','current_position_and_height','A_proposed_relation','B_proposed_relation','relocation_authorized','source'])
 for i,name in enumerate(names,1):
  sid=f'SB{i:02}';wr.writerow([sid,'HERO4' if i in [5,8,9,12] else 'CIVIC4' if i in [6,7,10,11] else 'FRAME8',name,'UNCONFIRMED','UNCONFIRMED',a[i-1],b[i-1],False,'M119 source at 29a6973; historical proposal only'])
 for i in range(1,7):wr.writerow([f'H{i}','AIR_DISTRICT','UNCONFIRMED','UNCONFIRMED','UNCONFIRMED','既存交通から受入れ広場へ、別帰路','公共庭から独立受入れ室へ、中央迂回',False,'User brief; identity/coordinates unavailable'])
 for sid in ['W0','HALO-9','CELESTIAL SPINE','三大都市軸','V1','V2','V3']:
  wr.writerow([sid,'CITY_FRAME','UNCONFIRMED','USER_GIVEN_ID','UNCONFIRMED','既存形状照合を先行','既存形状照合を先行',False,'User brief'])
rows=list(csv.DictReader((R/'RELATIONS.csv').open(encoding='utf-8-sig')))
assert {f'SB{i:02}' for i in range(1,17)} <= {r['id'] for r in rows}
assert {f'H{i}' for i in range(1,7)} <= {r['id'] for r in rows}
assert all(r['current_position_and_height']=='UNCONFIRMED' for r in rows)
images={}
for name in ['A_CONCEPT.png','B_CONCEPT.png','CAUSALITY.png']:
 with Image.open(R/name) as im:im.load();assert im.size==(2400,2140);images[name]={'pixels':list(im.size),'readable':True}
assert not list(R.glob('*.glb')) and not list(R.glob('*.blend'))
assert all(f'SB{i:02}' in report for i in range(1,17))
verification={'study_id':'C2-G5','stage':'CONCEPT','checks':{'png_decode':images,'all_16_facilities_and_6_districts_in_relations':True,'all_positions_explicitly_unconfirmed':True,'heavy_3d_assets_absent':True,'source_links_present':True},'visual_review':'All three sheets visually inspected; layout repaired. A still risks tower reading, B rock-cluster reading. Art HOLD.','limits':['2D diagram envelopes only','no shared 3D camera comparison','no W0 or formal coordinates overlay','no measured dimensions','no visibility, structure, transport or livability certification','C2 INAH full text unavailable; official indexed excerpts only'],'formal_M247_C':'UNCHANGED','minecraft':'HOLD','work_migration':False,'art_review_status':'HOLD','supervisor_review':'PENDING'}
write(R/'verification.json',verification)
old=read(W/'latest.json')
prior=[x for x in old.get('history',[]) if x.get('study_id')!='C2-G5']
entry={'study_id':'C2-G5','manifest':'studies/C2-G5/manifest.json','stage':'CONCEPT','art_review_status':'HOLD','date':'2026-10-23','provisional_candidate':'A','formal_adoption':False}
write(R/'history.json',{'previous_study':'C2-G4','previous_status':'ART_SELF_REVIEW_FAIL','legacy_evidence':'studies/C2-G4/','events':[{'date':'2026-10-23','event':'USER_AUTHORIZED_NEW_CONCEPT_RESEARCH','note':'G4 art failure retained; no 3D detailing'},{'date':'2026-10-23','event':'TWO_CONCEPTS_SUBMITTED','candidate':'A','status':'HOLD_SUPERVISOR_REVIEW'}]})
files=[p for p in R.iterdir() if p.name in ['REPORT.md','SOURCES.md','RELATIONS.csv','verification.json','history.json','draw_concepts.py','package.py','publish.py','A_CONCEPT.png','B_CONCEPT.png','CAUSALITY.png']]
assets=[info(p) for p in sorted(files)]
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
latest={'study_id':'C2-G5','track':'C','branch':'art/c','title':'文明象徴都市 × 巨大公共建築：天衢会都／六庭共議都','stage':'CONCEPT','art_review_status':'HOLD','updated_at':'2026-10-22T21:00:00Z','date':'2026-10-23','dimensions_m':None,'proposed_dimensions_m':None,'concept_proposed_dimensions_m':{'A':{'width':2800,'depth':2100,'height':2200},'B':{'width':3200,'depth':2500,'height':1900}},'assets':assets,'validation':verification,'notes':'A provisionally promising; no adoption. Historical M119 program only; current positions unconfirmed. INAH full-text retrieval incomplete.','formal_M247_C':'UNCHANGED','minecraft':'HOLD','work':'PRIOR_APPROVAL_REQUIRED','report':'studies/C2-G5/REPORT.md','preview':'studies/C2-G5/A_CONCEPT.png'}
latest['updated_at']=stamp
write(R/'manifest.json',{'schema_version':'1.0',**latest})
old['latest']=latest;old['history']=prior+[entry];old['last_submission_at']='2026-10-23'
write(W/'latest.json',old)
print(json.dumps({'assets':len(assets),'bytes':sum(a['size_bytes'] for a in assets),'relations':len(rows),'status':'CONCEPT_HOLD'},ensure_ascii=False))
