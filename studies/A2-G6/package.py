"""Package original research geometry, full-size views, candid art judgment and index."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,datetime,html
R=Path(__file__).resolve().parent;BASE=R.parents[1];WORK=BASE.parents[1]
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def blob(p):
    b=p.read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
font=lambda sz:ImageFont.truetype('C:/Windows/Fonts/YuGothM.ttc',sz)
bg=(18,28,38);fg=(230,232,226);gold=(232,190,120)

geometry=json.loads((R/'geometry-record.json').read_text(encoding='utf-8'))
qa=json.loads((R/'mesh-qa.json').read_text(encoding='utf-8'))
assert qa['sha256']==sha(R/'selected.glb')
inherit=json.loads((R/'inheritance.json').read_text(encoding='utf-8'))
for a in inherit['source_assets']:
    p=WORK/'research/G5-A-submission'/a['path'];assert blob(p)==a['git_blob_sha']

expected=['01_city','02_oblique','03_front','04_side','05_back','06_high','07_human','08_public_hall','09_pair_aerial','10_pair_section','11_living_street']
image_info=[]
for n in expected:
    p=R/'renders'/(n+'.png')
    with Image.open(p) as im:
        size=im.size;im.verify()
    assert size==((1600,1350) if int(n[:2])<=6 else (1900,1400)),(n,size)
    image_info.append({'path':p.relative_to(R).as_posix(),'pixels':size})
# Only palette reduction, no geometric retouching, resizing or invented details.
for p in list((R/'renders').glob('*.png'))+list((R/'comparison').glob('*.png')):
    with Image.open(p) as im:
        if im.mode!='P':im.convert('RGB').quantize(colors=128).save(p,optimize=True)

six=Image.new('RGB',(2400,1500),bg);d=ImageDraw.Draw(six)
labels=['全都市：概念背景10km','中央斜視','正面','側面','背面','高高度俯瞰']
for i,n in enumerate(expected[:6]):
    im=Image.open(R/'renders'/(n+'.png')).convert('RGB');im.thumbnail((800,675))
    x=(i%3)*800;y=(i//3)*750;six.paste(im,(x,y+55));d.text((x+15,y+12),labels[i],font=font(29),fill=gold)
six.save(R/'six_views.png',optimize=True)

comp=Image.new('RGB',(2400,1880),bg);d=ImageDraw.Draw(comp)
rows=[('A / 連湾交庭','A_02_oblique.png','A_03_front.png','A_05_back.png',['停止：曲面壁＋棚が先に見える','生活都市が主質量に現れない']),
      ('B / 折面交庭','B_02_oblique.png','B_03_front.png','B_05_back.png',['停止：板・壁・斜材の印象','棚の反復を解決できない']),
      ('C / 主質量を再生成','C_02_oblique.png',None,'C_05_back.png',['共有断面の実3D検証用として保持','全景の棚状反復は未解決／美術HOLD'])]
for row,(title,ob,front,back,notes) in enumerate(rows):
    y=row*620;d.text((25,y+8),title,font=font(32),fill=gold)
    for x,p,size in [(15,R/'comparison'/ob,(680,565)),(715,(R/'comparison'/front if front else R/'renders'/'03_front.png'),(520,435)),(1260,R/'comparison'/back,(520,435))]:
        im=Image.open(p).convert('RGB');im.thumbnail(size);comp.paste(im,(x,y+55))
    for k,line in enumerate(notes):d.text((1805,y+170+k*70),line,font=font(25),fill=fg)
    if row==2:d.text((720,y+535),'C初期の斜視・背面＋最終C正面（形状同一比較ではない）',font=font(23),fill=fg)
comp.save(R/'comparison.png',optimize=True)

human=Image.new('RGB',(2400,1000),bg);d=ImageDraw.Draw(human)
for i,(p,label) in enumerate([(R/'comparison'/'C_initial_human_blocked.png','初回：室群が共有広場への見通しを遮る'),(R/'renders'/'07_human.png','修正後：同じカメラ／干渉する室群を除去')]):
    im=Image.open(p).convert('RGB');im.thumbnail((1200,900));human.paste(im,(i*1200,65));d.text((i*1200+15,15),label,font=font(29),fill=gold)
d.text((20,960),'同じカメラ位置。最終診断は補助光・露出が異なる。生活都市としての密度は未達。',font=font(25),fill=fg)
human.save(R/'human_comparison.png',optimize=True)

sections=[('全都市と中央主質量','six_views.png'),('異なる構成と再設計','comparison.png'),('初回の失敗と干渉修正','human_comparison.png'),('人間視点：市場側','renders/07_human.png'),('人間視点：公共広間','renders/08_public_hall.png'),('人間視点：住宅街路側','renders/11_living_street.png'),('重点生活地区の俯瞰','renders/09_pair_aerial.png'),('上下都市と共有施設の断面','renders/10_pair_section.png')]
page='''<!doctype html><html lang="ja"><meta charset="utf-8"><title>HALO-9 A2-G6</title><style>body{max-width:1400px;margin:35px auto;background:#101c29;color:#e8ece9;font:18px/1.7 sans-serif;padding:20px}h1,h2{color:#edc67d}a{color:#87cbc9}img{width:100%;height:auto;border:1px solid #4a616c}p{max-width:1100px}</style><h1>A2-G6 交庭聖都：実メッシュ研究</h1><p>BLOCKOUT_3D / 美術HOLD。共有公共断面は制作したが、全景の棚状反復と中央主役性は未解決。正式採択・施工承認ではありません。</p><p><a href="REPORT.md">研究報告</a> · <a href="selected.glb">中央建築GLB</a> · <a href="selected.blend">BLEND</a> · <a href="mesh-qa.json">検証記録</a></p><p>背景は未登録の10km概念配置。W0・H地区の正式復元ではありません。単画像はクリックして元解像度で確認できます。</p>'''
for title,path in sections:page+=f'<h2>{html.escape(title)}</h2><a href="{path}"><img src="{path}" alt="{html.escape(title)}"></a>'
page+='<p>図像は同じ実GLBから撮影。断面はコピーを切断。住宅・窓等は幾何学ですが、居住・構造・避難の認証ではありません。</p></html>'
(R/'review.html').write_text(page,encoding='utf-8')

validation={'stage':'BLOCKOUT_3D','art_review_status':'HOLD','formal_art_adoption':False,'formal_supervisor_art_review':'NOT_REVIEWED',
 'measured_dimensions_m':qa['dimensions_m'],'model_source':'new original meshes','selected_glb_sha256':sha(R/'selected.glb'),
 'blender_glb_roundtrip':'SUCCESS','independent_loader':'trimesh SUCCESS','bounds_max_delta_m':qa['vs_blender_bounds_max_delta_m'],
 'mesh_objects':qa['geometry_objects'],'triangles':qa['triangles'],'all_finite':qa['all_vertices_finite'],
 'shared_roof':qa['shared_roof'],'housing_support':qa['focus_housing_support_summary'],
 'images':image_info,'render_source':'reimported selected.glb; final model used for every final view',
 'palette_reduction':128,'section':'same GLB mesh copies bisected; cut faces uncapped',
 'human_view_verdict':'HOLD: civic hall remains oversized and daily street/market density too weak; not a validated inhabited civilization city',
 'human_diagnostic_exposure':-2,'human_before_after_lighting_comparable':False,
 'art_verdict':'STOP DETAIL: tiered shelf/rack reading persists. Preserve spatial evidence, not an adopted art candidate.',
 'initial_human_failure':{'image':'comparison/C_initial_human_blocked.png','nearest_central_obstruction_m':98.92,'object':'INHABITED_BACK_ROOMS_AND_CIVIC_PIERS','response':'removed conflicting macro room piers and rerendered all final views'},
 'geometry_checks_are_not':['global walkability','structural safety','complete services','protection clearance','inhabitability','art acceptance'],
 'world_writes':0,'formal_M247C_modified':False,'work_transfer':False,'minecraft_construction':'HOLD',
 'context':'10km square + six unregistered scale quarters in separate BLEND collection; architecture-only GLB',
 'M204_M207_fusion':False,'coordinate_endpoints':'UNCONFIRMED / UNDETERMINED'}
write(R/'validation.json',validation)

stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
allowed={'.py','.md','.json','.png','.glb','.blend','.html'}
files=sorted(p for p in R.rglob('*') if p.is_file() and p.suffix in allowed and p.name!='manifest.json')
assets=[]
for p in files:
    kind={'.py':'CODE','.md':'REPORT','.json':'JSON','.png':'PNG','.glb':'GLB','.blend':'BLEND','.html':'HTML'}[p.suffix]
    assets.append({'path':p.relative_to(BASE).as_posix(),'kind':kind,'sha256':sha(p),'size_bytes':p.stat().st_size})
old=json.loads((BASE/'previous-index.json').read_text(encoding='utf-8'))
entry={'study_id':'A2-G6','title':'交庭聖都：上下生活地区の共有公共建築 — 二構成と主質量再設計の実3D研究',
 'stage':'BLOCKOUT_3D','art_review_status':'HOLD','updated_at':stamp,'dimensions_m':qa['dimensions_m'],'proposed_dimensions_m':None,
 'dimensions_scope':'selected.glb architecture-only bounds; includes transit and scale people; excludes context. No canonical-city registration.',
 'assets':assets,'validation':validation,'notes':'Actual GLB/BLEND and eleven final full-size views. Shared civic roof/upper ground verified at focused district. Central hero art target NOT achieved; stop detail. HOLD is study judgment, no formal adoption.'}
manifest={'schema_version':'1.0','branch':'art/a','track':'A',**entry,
 'provenance':{'baseline_commit':'b74e452f664adc8ae505846509d978e324fc6e1b','prior_study':'A2-G5','inheritance':'inheritance.json'},
 'execution':{'environment':'existing project workspace; background Blender; no Work handoff','blender':'5.2.1 LTS','world_writes':0}}
write(R/'manifest.json',manifest)
ma={'path':'studies/A2-G6/manifest.json','kind':'JSON','sha256':sha(R/'manifest.json'),'size_bytes':(R/'manifest.json').stat().st_size}
history=list(old['history'])
if not any(x['study_id']==old['latest']['study_id'] for x in history):history.append({'study_id':old['latest']['study_id'],'manifest_path':'studies/'+old['latest']['study_id']+'/manifest.json'})
assert history[:len(old['history'])]==old['history']
write(BASE/'latest.json',{**old,'latest':{**entry,'assets':assets+[ma]},'history':history,'last_submission_at':stamp})
(R/'SHA256SUMS.txt').write_text(''.join(a['sha256']+'  '+a['path']+'\n' for a in assets+[ma]),encoding='utf-8')
for a in assets+[ma]:assert sha(BASE/a['path'])==a['sha256']
deliver=[BASE/a['path'] for a in assets+[ma]]+[R/'SHA256SUMS.txt',BASE/'latest.json']
write(BASE/'upload-index.json',[{'path':p.relative_to(BASE).as_posix(),'size_bytes':p.stat().st_size,'git_blob_sha':blob(p)} for p in deliver])
print(json.dumps({'files':len(deliver),'total_bytes':sum(p.stat().st_size for p in deliver),'max_file_bytes':max(p.stat().st_size for p in deliver),'history':history,'dimensions_m':qa['dimensions_m'],'stage':entry['stage'],'art_status':entry['art_review_status']}))
