"""Evidence sheets, actual GLB measurements, legacy protection and portable review."""
from pathlib import Path
import json,struct,math,hashlib,ast,zipfile
from PIL import Image,ImageDraw,ImageFont
import trimesh
from shapely import Polygon,box

ROOT=Path(__file__).resolve().parent;R=ROOT/'renders';L=ROOT/'legacy_matched'
def font(n):return ImageFont.truetype('C:/Windows/Fonts/meiryo.ttc',n)
def sheet(items,name,cols=3,title='',w=800,h=600):
    im=Image.new('RGB',(w*cols,100+math.ceil(len(items)/cols)*(h+65)),(16,23,32));d=ImageDraw.Draw(im)
    d.text((25,24),title,font=font(27),fill=(231,238,245))
    for i,(p,label) in enumerate(items):
        x=(i%cols)*w;y=100+(i//cols)*(h+65)
        pic=Image.open(p).convert('RGB');pic.thumbnail((w,h),Image.Resampling.LANCZOS)
        im.paste(pic,(x+(w-pic.width)//2,y+(h-pic.height)//2))
        d.text((x+18,y+h+14),label,font=font(20),fill=(222,232,241))
    im.save(ROOT/name)

views=[('01_front','正面｜南'),('02_oblique','斜視｜南東45°'),('03_side','側面｜東'),('04_top','俯瞰｜鉛直'),('05_back','背面｜北'),('06_interior','内部｜天空盆地・床上1.7m・24mm')]
sheet([(R/(n+'.png'),s) for n,s in views],'SIX_VIEWS.png',title='ASTERION — MASSING REINVENTION / 同一モデル・6視点')
sheet([(L/'02_oblique.png','旧案｜同じカメラ・縮尺・照明'),(R/'02_oblique.png','新案｜同じカメラ・縮尺・照明')],
      'BEFORE_AFTER_OBLIQUE.png',cols=2,title='ASTERION — 主建築再構成 / 旧案・新案')
comp=[]
for n,s in views[:5]:comp.extend([(L/(n+'.png'),'旧案｜'+s),(R/(n+'.png'),'新案｜'+s)])
sheet(comp,'BEFORE_AFTER_FIVE.png',cols=2,title='ASTERION — 旧案・新案 / 外観5方向・同条件')
sheet([(R/'06_interior.png','天空盆地｜標高1501.7m・24mm'),(R/'10_ground_pedestrian.png','地上公共広場｜標高1.7m・28mm'),
       (R/'11_crown_pedestrian.png','天稜の高所都市室｜標高3001.7m・24mm'),(R/'12_cavern_pedestrian.png','斜都の公共結節｜標高1551.7m・28mm')],
      'HUMAN_EYE_INTERIORS.png',cols=2,title='ASTERION — 各公共地盤から1.7m / 実寸の透視投影')
sheet([(R/'07_basic_mass.png','単色主質量｜斜視'),(R/'07b_basic_back.png','単色主質量｜背面')],
      'BASIC_MASS.png',cols=2,title='ASTERION — 装飾なし / 主質量と空洞')
sheet([(R/'08_structure.png','都市体｜青：天稜・金：長庭・緑：斜都・赤：結節'),(R/'13_cutaway_city_grounds.png','解析用の部分非表示｜青緑：都市地盤・桃：交通'),
       (R/'09_structure_top.png','同一モデル｜構造の俯瞰'),(R/'14_cutaway_top.png','解析用の部分非表示｜都市地盤の俯瞰')],
      'STRUCTURE_AND_GROUNDS.png',cols=2,title='ASTERION — 主質量・空洞・都市地盤 / 実モデルから描画')

# Schematic sections use the exact model-generating profiles, not a drawn substitute model.
tree=ast.parse((ROOT/'geometry.py').read_text(encoding='utf-8'));coords={}
for node in tree.body:
    if isinstance(node,ast.Assign):
      for t in node.targets:
        if isinstance(t,ast.Name) and t.id in ['Aouter','Ainner','Couter','Cinner']:coords[t.id]=ast.literal_eval(node.value)
im=Image.new('RGB',(2100,1100),(16,23,32));d=ImageDraw.Draw(im)
d.text((25,25),'ASTERION — 都市体の原形断面と主要地盤',font=font(30),fill=(233,240,246))
for i,(out,inner,levels,label) in enumerate([('Aouter','Ainner',[600,1550,3000],'天稜｜居住門の断面'),('Couter','Cinner',[450,1550,2370],'斜都｜斜めの都市峡谷')]):
    left=30+i*1030;pp=Polygon(coords[out]).difference(Polygon(coords[inner]));mnx,mnz,mxx,mxz=pp.bounds
    scale=min(930/(mxx-mnx),820/(mxz-mnz))
    def xy(x,z):return(left+30+(x-mnx)*scale,950-(z-mnz)*scale)
    geoms=[pp] if pp.geom_type=='Polygon' else list(pp.geoms)
    for p in geoms:
        d.polygon([xy(*v) for v in p.exterior.coords],fill=(102,132,156))
        for hole in p.interiors:d.polygon([xy(*v) for v in hole.coords],fill=(16,23,32))
    for z in levels:
        cut=pp.intersection(box(-10000,z-.1,10000,z+.1))
        parts=[cut] if cut.geom_type=='Polygon' else list(getattr(cut,'geoms',[]))
        for part in parts:
            if part.geom_type=='Polygon':
                a,_,b,_=part.bounds;d.line([xy(a,z),xy(b,z)],fill=(87,224,186),width=7)
        d.text((left+15,xy(mnx,z)[1]-27),str(z)+'m',font=font(18),fill=(173,245,222))
    d.text((left+15,990),label,font=font(25),fill=(232,239,246))
d.text((25,1050),'青灰：居住殻の断面　暗部：除去した空洞　青緑：主要都市地盤　他の都市体による横断・施設の占有は別図参照',font=font(21),fill=(212,225,235))
im.save(ROOT/'SECTION_PRINCIPLE.png')

m=json.loads((ROOT/'model_metrics.json').read_text(encoding='utf-8'))
old=json.loads((ROOT/'reference/legacy_model_metrics.json').read_text(encoding='utf-8'))
camera_match={n:m['cameras'][n]==old['cameras'][n] for n,s in views[:5]}
assert all(camera_match.values())
for n,s in views:
    assert Image.open(R/(n+'.png')).size==(1600,1200)
for n,r in m['camera_reference_rays'].items():assert abs(r['floor_below_eye'][0]-1.7)<.01
raw=(ROOT/'ASTERION_REINVENTION.glb').read_bytes();magic,ver,nbytes=struct.unpack_from('<4sII',raw)
assert magic==b'glTF' and ver==2 and nbytes==len(raw)
scene=trimesh.load(ROOT/'ASTERION_REINVENTION.glb',force='scene')
assert all(math.isfinite(float(x)) for x in scene.bounds.flatten())
glb={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'meshes':len(scene.geometry),'triangles':sum(len(g.faces) for g in scene.geometry.values()),'bounds_gltf_y_up_m':scene.bounds.tolist(),'dimensions_gltf_y_up_m':scene.extents.tolist(),
 'scope':'Header, readback, finite bounds; no watertightness, construction, global collision or Minecraft QA.'}
(ROOT/'glb_validation.json').write_text(json.dumps(glb,indent=2),encoding='utf-8')
protected=json.loads((ROOT/'protected_legacy_hashes.json').read_text(encoding='utf-8'))
legacy=ROOT.parent/'research_asterion_primary_gate';changed=[]
if legacy.exists():
    for n,info in protected.items():
        p=legacy/n
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=info['sha256']:changed.append(n)
    assert not changed,'Legacy files changed: '+str(changed)
protection={'legacy_directory_present':legacy.exists(),'protected_files':len(protected),'changed_files':changed,'exterior_cameras_exact_match':camera_match,
 'matched_exterior_render':'1600x1200, ortho width7800m, Cycles12 samples, same sun/world/material colors, area fills disabled. Interior room fills enabled only for new human-eye views.'}
(ROOT/'verification.json').write_text(json.dumps(protection,indent=2),encoding='utf-8')

lines=['# 実寸と空洞の計測','',f"建築全体の外接寸法（地下地盤を含む）：{m['bbox_dimensions_m'][0]:.2f} × {m['bbox_dimensions_m'][1]:.2f} × {m['bbox_dimensions_m'][2]:.2f}m。",'',
f"地上最大標高：{m['bbox_max_m'][2]:.2f}m。地下端：{m['bbox_min_m'][2]:.2f}m。",'',
'原形の開口は実際に削除した断面・平面多角形から計測。他の都市体が横断するため、組立後に同寸法の空の直方体があるという意味ではない。','',
'| 開口 | 実モデル生成に用いた除去形状の外接寸法 |','|---|---|']
for label,key in [('天稜の縦開口','TENRYO_profile_removed_uz_bounds_m'),('斜都の開口','SHATO_profile_removed_uz_bounds_m'),('長庭の公共盆地','CHOTEI_court_xy_bounds_m')]:
    b=m['aperture_geometry'][key];lines.append(f'| {label} | {b[2]-b[0]:.2f} × {b[3]-b[1]:.2f}m |')
lines+=['','## 組立後の空間：参照点から最初の境界まで','',
'各行は同じ点から6方向へ測った軸方向距離。直方体の有効寸法、全空洞の最大寸法、歩行可能領域の保証値ではない。開放は10km以内に建築面がない方向。','',
'| 場所 | 西 | 東 | 南 | 北 | 下 | 上 |','|---|---:|---:|---:|---:|---:|---:|']
for name,space in m['space_axis_measurements'].items():
    cells=[]
    for direction in ['west','east','south','north','down','up']:
        v=space['axis_rays'][direction]['distance_m'];cells.append('開放' if v is None else f'{v:.2f}m')
    lines.append('| '+name+' | '+' | '.join(cells)+' |')
lines+=['','内部4カメラは下方レイで床上約1.7mを確認した。詳細はmodel_metrics.jsonに床のメッシュ名と距離を記録。']
(ROOT/'MEASUREMENTS.md').write_text('\n'.join(lines),encoding='utf-8')

page='''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ASTERION — MASSING REINVENTION</title><style>
body{background:#101820;color:#e5edf4;margin:0;font:16px/1.8 Meiryo,sans-serif}main{max-width:1300px;margin:auto;padding:40px 25px}h1{font-size:38px;line-height:1.3}h2{margin-top:48px}a{color:#9bd1f7}img{display:block;width:100%;height:auto}.panel{background:#20303e;padding:20px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0}figcaption{padding:8px}@media(max-width:700px){.grid{grid-template-columns:1fr}h1{font-size:28px}}</style><main>
<p>CELESTIAL HALO-9 / CHAT C / INDEPENDENT RESEARCH</p><h1>天綾宮 アステリオン<br>MASSING REINVENTION</h1>
<p class="panel"><strong>主質量の再構成は実施。旧案からの改善は確認できるが、主役建築としての美術合格には未達。正式採択・施工HOLD。</strong><br>帯状の積層構成を、居住門・天空盆地・斜めの都市峡谷へ変更した。日常都市としての豊かさ、内部の抜け、上面の統合に課題を残す。細密化は行わない。</p>
<p><a href="ASTERION_REINVENTION.glb">新GLB</a> ／ <a href="CONCEPTS.md">二つの再設計思想</a> ／ <a href="REVIEW.md">美術評価・再現手順</a> ／ <a href="MEASUREMENTS.md">実寸計測</a></p>'''
for title,file in [('同一カメラ・同一縮尺の旧案比較','BEFORE_AFTER_OBLIQUE.png'),('同一の新モデルから描画した6視点','SIX_VIEWS.png'),('無装飾・単色の主質量','BASIC_MASS.png'),('主質量・空洞・都市地盤','STRUCTURE_AND_GROUNDS.png'),('原形断面と主要地盤','SECTION_PRINCIPLE.png'),('床上1.7mの内部・公共空間','HUMAN_EYE_INTERIORS.png'),('外観5方向の旧案比較','BEFORE_AFTER_FIVE.png')]:
    page+=f'<h2>{title}</h2><a href="{file}"><img src="{file}"></a>'
page+='<h2>原寸画像</h2><div class="grid">'
for n,s in views:page+=f'<figure><a href="renders/{n}.png"><img src="renders/{n}.png"></a><figcaption>{s}／1600×1200</figcaption></figure>'
page+='</div><p>旧ファイルの保護確認はverification.json、GLBの読込確認はglb_validation.jsonに収録。Workへの新規切り替え、Minecraft変換、正式資産・GitHubへの変更は実施していない。</p></main></html>'
(ROOT/'review.html').write_text(page,encoding='utf-8')
print(json.dumps({'glb':glb,'protection':protection,'dimensions_m':m['bbox_dimensions_m']},indent=2))
