"""Package actual model views, clearly schematic alternatives, hashes and branch index.
Python + Pillow. PNG render masters stay local; published individual views are JPEG.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,datetime,html
R=Path(__file__).resolve().parent;BASE=R.parents[1]
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def blob(p):
    b=p.read_bytes();return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
font=lambda s:ImageFont.truetype('C:/Windows/Fonts/YuGothM.ttc',s)
BG='#13232d';FG='#e7ebe6';MUT='#a9c1c7';GOLD='#dfb26d';TEAL='#81c7bb'
qa=json.loads((R/'qa.json').read_text(encoding='utf-8'));geom=json.loads((R/'geometry.json').read_text(encoding='utf-8'))
assert qa['selected_glb_sha256']==sha(R/'selected.glb')

# Formation diagrams: intentionally planar, explicitly not images of 3D results.
im=Image.new('RGB',(2200,1530),BG);d=ImageDraw.Draw(im)
d.text((60,35),'A2-G7  |  2つの形成仮説',font=font(47),fill=FG)
d.text((60,105),'形成の模式図：完成景観・実3Dの比較画像ではない。IIは3D未制作。',font=font(26),fill=MUT)
for x in [50,1130]:d.rounded_rectangle((x,170,x+1020,1465),radius=18,fill='#1c313c')
d.text((80,195),'I  合流天窟',font=font(39),fill=GOLD)
d.text((1160,195),'II  斜交縫都',font=font(39),fill=TEAL)
# I: protect one civic void; expose a shared roof at the high street incision.
d.line([(170,760),(225,560),(355,380),(520,300),(710,350),(870,540),(945,760)],fill='#8ea39d',width=100,joint='curve')
d.polygon([(400,265),(580,265),(580,410),(400,410)],fill='#1c313c')
d.line([(165,780),(420,780)],fill=GOLD,width=15)
d.line([(350,462),(660,462)],fill=TEAL,width=13)
d.line([(350,510),(660,510)],fill=GOLD,width=10)
d.text((220,610),'通り抜け・採光域を共有',font=font(29),fill=FG)
d.text((380,535),'公共空洞',font=font(32),fill=FG)
d.text((360,325),'街路が冠を割る',font=font(25),fill=TEAL)
d.text((90,835),'公共機能を空洞の両岸へ集約',font=font(31),fill=FG)
# II: graph-induced junctions rather than a single shared void.
d.line([(1240,760),(1400,570),(1670,470),(1920,320)],fill='#8ea39d',width=96,joint='curve')
d.line([(2020,760),(1800,560),(1615,470),(1430,330)],fill='#647e83',width=96,joint='curve')
for x,y in [(1400,570),(1670,470),(1800,560)]:
    d.rectangle((x-67,y-33,x+67,y+35),fill='#243e49',outline=TEAL,width=4)
    d.line([(x-70,y-35),(x+70,y-35)],fill=TEAL,width=12)
    d.line([(x-50,y+25),(x+50,y+25)],fill=GOLD,width=6)
d.text((1230,800),'共有相手が変わる接合部の連鎖',font=font(31),fill=FG)
for x,lines in [(90,['出発：地上の市場と高所の公共街路','規則：空洞を保護し、公共施設を両岸へ','主形：一つの大きな陰画＋割れた冠','実3D：Iのみ制作 → 美術HOLD']),
                (1170,['出発：上下地区の公共施設を相互利用','規則：接合先の交代で主質量を分岐','主形：斜交する厚い都市岸と接合室','構想保留：橋・斜材の集合に見える懸念'])]:
    for k,line in enumerate(lines):d.text((x,910+k*53),line,font=font(27),fill=FG if k<3 else GOLD)
    # Common local section does not imply identical macro formation.
    yy=1240
    d.line([(x+20,yy+100),(x+850,yy+100)],fill=GOLD,width=9)
    d.rectangle((x+150,yy+24,x+220,yy+92),fill='#658084')
    d.rectangle((x+670,yy+24,x+740,yy+92),fill='#658084')
    d.line([(x+130,yy+12),(x+760,yy+12)],fill=TEAL,width=13)
    for xx in [x+280,x+540]:d.rectangle((xx,yy-33,xx+55,yy+4),outline=FG,width=5)
    d.text((x+20,yy-80),'共通の局所断面：公共施設の屋根＝上の街の地盤',font=font(24),fill=MUT)
    d.text((x+310,yy+40),'下の公共空間',font=font(24),fill=FG)
im.save(R/'concepts.png',optimize=True)

views=['01_oblique','02_side','03_back','04_city','05_shared_high','06_shared_ground','07_front','08_section']
for n in views:
    p=R/'renders'/(n+'.png');j=p.with_suffix('.jpg')
    if p.exists():Image.open(p).convert('RGB').save(j,quality=90,optimize=True,subsampling=0)
    with Image.open(j) as check:assert check.size==(1200,1000);check.verify()

sheet=Image.new('RGB',(2400,1820),BG);d=ImageDraw.Draw(sheet)
d.text((35,22),'CELESTIAL HALO-9   /   A2-G7   /   合流天窟',font=font(43),fill=FG)
d.text((35,86),'初回美術選抜：採択なし / HOLD    同一の低詳細GLBから撮影',font=font(29),fill=GOLD)
for i,(n,label) in enumerate(zip(views[:3],['斜視','側面：壁状の読み','背面：アーチの読み'])):
    x=i*800
    pic=Image.open(R/'renders'/(n+'.jpg'));pic.thumbnail((800,667));sheet.paste(pic,(x,155))
    d.text((x+20,837),label,font=font(31),fill=FG)
for i,(n,label) in enumerate([('04_city','10km概念景（未登録の尺度街区）'),('08_section','高所の共有断面（前半切除・包絡非表示）')]):
    x=i*1200;pic=Image.open(R/'renders'/(n+'.jpg'));pic.thumbnail((1200,785));sheet.paste(pic,(x+(1200-pic.width)//2,930))
    d.text((x+20,892),label,font=font(29),fill=TEAL)
d.text((35,1730),'棚の反復は外したが、生活から主輪郭を導く規則は未達。精密化せず中央審査へ。',font=font(30),fill=GOLD)
quality=86
while True:
    sheet.save(R/'preview.jpg',quality=quality,optimize=True,subsampling=0)
    if (R/'preview.jpg').stat().st_size<600000:break
    quality-=4;assert quality>=50

write(R/'inheritance.json',{'base_head':'156ccccdf0965df64109d43bc62282ab7b818d5e','branch':'art/a',
 'g6_report_git_blob_sha':'e18dff23fea144755fd316a7f50a0bd7746721e7','source_path':'studies/A2-G6/REPORT.md',
 'retained':['same civic roof / upper ground principle','contact tests','GLB roundtrip and independent loader method','G6 complete records at unchanged paths'],
 'not_reused':['G6 outer geometry','G6 meshes','tier counts or housing count as a shape generator'],
 'formal_M247C_modified':False,'minecraft_construction':'HOLD','work_prior_approval':True,'work_transfer':False})
write(R/'concepts.json',{'I':{'title':'合流天窟','principle':'one shared public void, thick civic catchments and an open-sky street incision',
 'stage':'BLOCKOUT_3D','art_status':'HOLD','dimensions_m':qa['dimensions_m'],'mass_generation_limit':'arch curvature is imposed, not derived from urban use; no successful new formation law claimed'},
 'II':{'title':'斜交縫都','principle':'changing district-sharing partners creates oblique civic junctions',
 'stage':'CONCEPT_ONLY','art_status':'DEFERRED','dimensions_m':None,'actual_3d':False,
 'limit':'risk of diagonal rack / bridge assemblage; no rendered-art or geometry validation claimed'},
 'selected_for_detail':None,'central_review':'NOT_REVIEWED'})

page='''<!doctype html><html lang="ja"><meta charset="utf-8"><title>A2-G7 初回美術選抜</title><style>body{max-width:1350px;margin:40px auto;padding:20px;background:#13232d;color:#e7ebe6;font:18px/1.8 sans-serif}a{color:#81c7bb}img{max-width:100%;height:auto}h1,h2{color:#dfb26d}</style><h1>A2-G7 — 初回美術選抜：採択なし / HOLD</h1><p>I《合流天窟》のみ実3D。II《斜交縫都》は形成模式図まで。生活から主質量を発生させる規則としては未達。精密化を停止。</p><p><a href="formation-comparison.md">形成原理の比較</a> · <a href="decision.md">判定</a> · <a href="selected.glb">低詳細GLB</a> · <a href="selected.blend">BLEND</a> · <a href="qa.json">限定的な幾何QA</a></p>'''
for title,p in [('軽量プレビュー：同一モデルの比較','preview.jpg'),('2つの形成仮説：模式図、IIは3D未制作','concepts.png')]+[(n,'renders/'+n+'.jpg') for n in views]:
    page+=f'<h2>{html.escape(title)}</h2><a href="{p}"><img src="{p}" alt="{html.escape(title)}"></a>'
page+='<p>10km背景は未登録の概念配置。断面図はHIGH要素のみをy=-500mで切断し包絡を非表示。構造・全域歩行・居住性・施工の証明ではありません。</p></html>'
(R/'review.html').write_text(page,encoding='utf-8',newline='\n')

# Stable text bytes on Windows and Linux, before computing the delivery hashes.
for p in R.rglob('*'):
    if p.is_file() and (p.suffix in {'.py','.md','.json','.html'} or p.name=='.gitignore'):
        s=p.read_text(encoding='utf-8');p.write_text(s,encoding='utf-8',newline='\n')

stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
files=sorted(p for p in R.rglob('*') if p.is_file() and p.name!='manifest.json' and
   (p.suffix in {'.py','.md','.json','.jpg','.glb','.blend','.html'} or p.name in {'.gitignore','concepts.png'}))
assets=[{'path':p.relative_to(BASE).as_posix(),'size_bytes':p.stat().st_size,'sha256':sha(p),'git_blob_sha':blob(p)} for p in files]
manifest={'study_id':'A2-G7','branch':'art/a','track':'A','base_head':geom['base_head'],'updated_at':stamp,
 'stage':'INITIAL_MASSING_ART_SELECTION','art_review_status':'HOLD','art_adopted_candidate':None,'formal_supervisor_review':'NOT_REVIEWED',
 'dimensions_m':qa['dimensions_m'],'dimensions_scope':'I architecture-only GLB, excluding 10km context; II unmeasured',
 'preview_bytes':(R/'preview.jpg').stat().st_size,'preview_target_under_600000_bytes':True,
 'assets':assets,'qa_summary':{'support_passed':128,'support_samples':128,'envelope_wing_samples':80,'hall_probes':8,'cleft_probes':5,
 'all_vertices_finite':True,'bounds_delta_vs_blender_m':qa['bounds_delta_vs_blender_m'],'triangles':qa['triangles'],
 'caution':'geometry checks do not establish art, engineering, inhabitability or canonical-city alignment'},
 'formal_M247C_modified':False,'minecraft_construction':'HOLD','work_transfer':False}
write(R/'manifest.json',manifest)
index=json.loads((BASE/'latest.json').read_text(encoding='utf-8'))
history=index.get('history',[])
if index['latest']['study_id']!='A2-G7':
    old=index['latest']['study_id']
    if not any(h['study_id']==old for h in history):history.append({'study_id':old,'manifest_path':f'studies/{old}/manifest.json','art_review_status':index['latest']['art_review_status']})
index.update({'branch':'art/a','track':'A','last_submission_at':stamp,'history':history,
 'latest':{'study_id':'A2-G7','title':'共有生活都市の形成規則：合流天窟／斜交縫都 — 初回美術選抜',
 'stage':'INITIAL_MASSING_ART_SELECTION','art_review_status':'HOLD','formal_art_adoption':False,
 'updated_at':stamp,'dimensions_m':qa['dimensions_m'],'proposed_dimensions_m':None,'dimensions_scope':manifest['dimensions_scope'],
 'manifest_path':'studies/A2-G7/manifest.json','preview_path':'studies/A2-G7/preview.jpg',
 'assets':assets+[{'path':'studies/A2-G7/manifest.json','size_bytes':(R/'manifest.json').stat().st_size,'sha256':sha(R/'manifest.json')}],
 'validation':manifest['qa_summary'],'notes':'No adopted art candidate. I real low-detail GLB: giant arch / wall reading persists; formation law not achieved. II conceptual only. Stop detail pending central review.'}})
write(BASE/'latest.json',index)
print(json.dumps({'preview_bytes':manifest['preview_bytes'],'jpeg_quality':quality,'files':len(assets)+1,'art_status':'HOLD','model_triangles':qa['triangles'],'largest_asset_bytes':max(p.stat().st_size for p in files)},ensure_ascii=False))
