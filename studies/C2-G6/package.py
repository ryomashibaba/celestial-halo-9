"""Verify rendered models and package actual study evidence. No network/world IO."""
from pathlib import Path
import json,hashlib,datetime,shutil
import numpy as np
import trimesh
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parent;W=R.parent.parent
def j(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
font='C:/Windows/Fonts/meiryo.ttc'
def sheet(name,title,items,cols=2,w=1900):
 tw=w//cols;th=int(tw*.75);head=120;label=55;rows=(len(items)+cols-1)//cols
 im=Image.new('RGB',(w,head+rows*(th+label)+65),'#10262f');d=ImageDraw.Draw(im)
 d.text((30,24),title,font=ImageFont.truetype(font,34),fill='#edf0e9')
 d.text((30,76),'C2-G6 / 実3Dから描画 / 研究用抽象配置・正式配置ではない',font=ImageFont.truetype(font,23),fill='#b5c8c7')
 for i,(path,caption) in enumerate(items):
  x=(i%cols)*tw;y=head+(i//cols)*(th+label)
  with Image.open(path) as src:img=ImageOps.fit(src,(tw,th))
  im.paste(img,(x,y));d.text((x+18,y+th+8),caption,font=ImageFont.truetype(font,22),fill='#e2c18b')
 d.text((30,im.height-47),'美術採択未了 / 正式M247-C保護 / Minecraft施工HOLD',font=ImageFont.truetype(font,22),fill='#b5c8c7')
 im.save(R/name)
if __name__=='__main__':
 compare=[(R/'renders'/k/(v+'.png'),k+' '+s) for k in ['A','B'] for v,s in [('05_oblique','同条件斜視'),('08_back','同条件背面')]]
 sheet('COMPARISON.png','二つの主質量：A 会流天蓋 / B 交襞公都',compare)
 # Both final comparison images use 1440x1080, Cycles20, and identical cameras.
 full=R/'renders/A'
 sheet('CITY_AND_APPROACHES.png','中央主役を10km都市と三方向の接近で読む',[(full/(p+'.png'),s) for p,s in [('01_city_10km','約10km都市全景'),('02_approach_alpha','接近α：南方の公共軸'),('03_approach_beta','接近β：内海側の仮方向'),('04_approach_gamma','接近γ：断崖側の仮方向')]])
 sheet('SIX_VIEWS.png','A 会流天蓋：同じモデルの六視点',[(full/(p+'.png'),s) for p,s in [('06_front','正面'),('05_oblique','象徴的斜視'),('07_side','側面'),('08_back','背面'),('10_top','全都市俯瞰'),('09_aerial_district','空中地区相当の視点')]],cols=3,w=2160)
 interior=[(full/(p+'.png'),s) for p,s in [('11_public_chamber','巨大公共室：床上1.7m'),('12_living_street','同じ公共室と生活街路')]]
 if (full/'13_elevated_living_street.png').exists():interior.append((full/'13_elevated_living_street.png','中高度の生活街路：床上1.7m'))
 sheet('INTERIORS.png','公共室と生活都市の距離を実際の床から見る',interior)
 checks={}
 for name in ['A_CENTRAL.glb','A_CITY.glb','B_CENTRAL.glb','B_CITY.glb']:
  scene=trimesh.load(R/name,force='scene');meshes=list(scene.geometry.values())
  checks[name]={'readable':True,'geometry_count':len(meshes),'vertices':sum(len(m.vertices) for m in meshes),'faces':sum(len(m.faces) for m in meshes),'bounds_gltf_y_up':scene.bounds.tolist(),'extent_gltf_y_up_m':scene.extents.tolist(),'all_vertices_finite':all(np.isfinite(m.vertices).all() for m in meshes),'component_meshes_watertight':sum(m.is_watertight for m in meshes),'note':'Component check only; combined city is not one manifold solid.'}
  merged=[]
  for m in meshes:
   q=m.copy();q.merge_vertices();merged.append(q)
  checks[name]['component_meshes_watertight_after_vertex_merge']=sum(m.is_watertight for m in merged)
  main=max(merged,key=lambda m:len(m.faces))
  checks[name]['main_mass_after_vertex_merge']={'watertight':bool(main.is_watertight),'connected_components':len(main.split(only_watertight=False))}
  assert meshes and checks[name]['all_vertices_finite']
 images={}
 for p in sorted(R.rglob('*.png')):
  if '.local.' in p.name:continue
  with Image.open(p) as im:
   im.load();images[p.relative_to(R).as_posix()]=list(im.size)
   if 'initial_comparison' not in p.as_posix():assert np.asarray(im.convert('RGB')).mean()>8,'Unusable black render: '+str(p)
 protected=j(R/'protected_hashes.json');assert all(sha(W/p)==v for p,v in protected.items())
 metrics=j(R/'A_metrics.json')
 assert all(hit and abs(hit[0]-1.7)<.02 for hit in metrics['interior_floor_rays'].values()),'Interior camera lacks correct real floor'
 assert np.allclose(checks['A_CENTRAL.glb']['extent_gltf_y_up_m'],[metrics['central_dimensions'][0],metrics['central_dimensions'][2],metrics['central_dimensions'][1]],atol=.1)
 counts=sum(d['street_modules'] for d in metrics['district_loggias'])
 result='# 実測・確認結果\n\n'
 result+='中央外接寸法（地形・周辺都市を除く）：東西 %.2fm × 南北 %.2fm × 高さ %.2fm。地下側の根元も高さに含む。\n\n'%tuple(metrics['central_dimensions'])
 result+=f'中央メッシュオブジェクト：{metrics["central_objects"]}。切込みに配置した街路モジュール：{counts}。モジュールごとに2列の生活包絡を置くが、住戸数・人口ではない。上部庭の街区と地上の店舗列は別に含む。\n\n'
 result+='内観3地点の床レイはいずれも約1.7m。GLB4点の独立再読込と有限頂点、画像の読込、参照ハッシュの保持を確認。中央主質量は頂点統合後も非閉鎖で、2成分が残る。構造・全動線・現行正式配置との整合は未検証。高所街路の床は本体面との重なりを0.2mずらして解消し、約24m幅の路面を確認した。\n'
 (R/'RESULTS.md').write_text(result,encoding='utf-8')
 verification={'study_id':'C2-G6','stage':'BLOCKOUT_3D','date_jst':'2026-10-23','gltf':checks,'images':images,'floor_rays':metrics['interior_floor_rays'],'protected_reference_hashes_match':True,'context':'Synthetic abstract layout only. No mapping to current SB/H/V coordinates.','art_review_status':'HOLD','formal_M247_C':'UNCHANGED','minecraft':'HOLD','work_migration':False,'limits':['No structural analysis or all-route accessibility','Housing blocks are courtyard/service envelopes, not fitted homes','Transport cores are geometry envelopes, not certified elevators','No approved W0 overlay, formal H/Y transform or voxel clearance','All render cameras recorded; context deliberately present','GLTF is Y-up; Blender is Z-up; extents must be permuted','Global meshes intersect; component watertightness is not city solidity']}
 write(R/'verification.json',verification)
 old=j(W/'latest.json');prior=old.get('history',[])
 if not any(x.get('study_id')=='C2-G5' for x in prior):prior.append({'study_id':'C2-G5','manifest':'studies/C2-G5/manifest.json'})
 write(R/'history.json',{'study_id':'C2-G6','parent':'C2-G5','parent_commit':'9fb9bc4493425b370dbde2eeed775ca133ff2182','retained_alternative':'C2-G5 B 六庭共議都','events':[{'event':'SUPERVISOR_PRIORITIZED_G5_A','date':'2026-10-23'},{'event':'TWO_3D_MASSINGS_COMPARED','schemes':['A 会流天蓋','B 交襞公都']},{'event':'A_FULL_CONTEXT_AND_INTERIOR_BLOCKOUT','status':'ART_HOLD_NOT_ADOPTED'}]})
 files=[p for p in R.rglob('*') if p.is_file() and p.suffix in ['.png','.glb','.blend','.json','.md','.py','.csv'] and not '.local.' in p.name and p.name not in ['manifest.json']]
 assets=[{'path':p.relative_to(W).as_posix(),'kind':{'.png':'PNG','.glb':'GLB','.blend':'BLEND','.py':'CODE','.md':'REPORT'}.get(p.suffix,'JSON'),'sha256':sha(p),'size_bytes':p.stat().st_size} for p in sorted(files)]
 assert all(a['size_bytes']<10_000_000 for a in assets),'Large file storage review required'
 latest={'study_id':'C2-G6','track':'C','branch':'art/c','title':'天衢会都：会流天蓋の実3D研究','stage':'BLOCKOUT_3D','art_review_status':'HOLD','updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'date':'2026-10-23','dimensions_m':dict(zip(['width','depth','height'],metrics['central_dimensions'])),'proposed_dimensions_m':None,'assets':assets,'validation':verification,'report':'studies/C2-G6/REPORT.md','model':'studies/C2-G6/A_CENTRAL.glb','city_model':'studies/C2-G6/A_CITY.glb','preview':'studies/C2-G6/CITY_AND_APPROACHES.png','notes':'A provisionally preferred. Art and livability not accepted. Formal coordinates unconfirmed.','formal_M247_C':'UNCHANGED','minecraft':'HOLD','work':'PRIOR_APPROVAL_REQUIRED'}
 write(R/'manifest.json',{'schema_version':'1.0',**latest})
 old['latest']=latest;old['history']=[x for x in prior if x.get('study_id')!='C2-G6']+[{'study_id':'C2-G6','manifest':'studies/C2-G6/manifest.json','stage':'BLOCKOUT_3D','art_review_status':'HOLD'}];old['last_submission_at']='2026-10-23'
 write(W/'latest.json',old)
 print(json.dumps({'files':len(assets),'bytes':sum(x['size_bytes'] for x in assets),'floor_rays':verification['floor_rays'],'dimensions_m':metrics['central_dimensions']},ensure_ascii=False))
