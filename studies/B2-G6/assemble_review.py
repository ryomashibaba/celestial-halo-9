"""Assemble actual-render contact sheets and validate delivered evidence.
No repainting, invented architectural pixels, or image generation.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,struct,re,datetime
R=Path(__file__).resolve().parent;B=R.parent.parent
font='C:/Windows/Fonts/YuGothM.ttc'
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def write(p,d): (R/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sheet(name,title,items,cols=2,tilew=650,tileh=590):
    rows=(len(items)+cols-1)//cols;im=Image.new('RGB',(cols*tilew,85+rows*tileh),(15,25,34));d=ImageDraw.Draw(im)
    d.text((24,24),title,font=ImageFont.truetype(font,26),fill='#ead2a3')
    for i,(path,label) in enumerate(items):
        x=(i%cols)*tilew;y=85+(i//cols)*tileh
        with Image.open(R/path) as pic:
            pic=pic.convert('RGB');pic.thumbnail((tilew-24,tileh-60));im.paste(pic,(x+(tilew-pic.width)//2,y+43))
        d.text((x+14,y+8),label,font=ImageFont.truetype(font,18),fill='#dce9eb')
    im.save(R/name,quality=91,subsampling=0)

macro={n:read(f'macro_{n}/manifest.json') for n in 'ABC'};sel=read('selected/manifest.json');audit=read('glb_reload_audit.json')
sheet('macro_comparison.jpg','B2-G6 / 住宅追加前の実3D比較 — A/B REJECT、Cを空間検証へ',[(f'macro_{n}/{view}.png',f'{n} / '+label) for n in 'ABC' for view,label in [('01_FRONT','正面'),('02_OBLIQUE','斜視')]],2)
views=[('00_CITY','10km概念背景'),('01_FRONT','正面'),('02_OBLIQUE','斜視'),('03_SIDE','側面'),('04_REAR','背面'),('05_TOP','俯瞰'),('06_GROUND_A','場面A 地上眼高'),('07_HIGH_B','場面B 高所眼高'),('08_HALL','公共ホール内部'),('09_SECTION','X=0断面'),('10_ALLEY','高所住居中庭')]
sheet('selected_views.jpg','B2-G6 / 同一Cモデルの11画像 — 最終研究内美術REJECT',[(f'selected/{n}.png',label) for n,label in views],3,500,440)
sheet('scenes_AB.jpg','B2-G6 / 場面A・Bと内部・中庭 — 未達部分を含む実レンダー',[(f'selected/{n}.png',label) for n,label in views if n in ['06_GROUND_A','07_HIGH_B','08_HALL','10_ALLEY']],2)
sheet('macro_to_occupied.jpg','B2-G6 / Cの主質量は同一 — 公共生活を加えても美術問題は残った',[('macro_C/02_OBLIQUE.png','住宅追加前'),('selected/02_OBLIQUE.png','生活街区・公共床追加後')],2)

images=[]
for sub in ['macro_A','macro_B','macro_C','selected']:
    m=read(sub+'/manifest.json')
    for item in m['renders']:
        p=R/sub/item['path']
        with Image.open(p) as im:
            assert im.size==tuple(m['render']['resolution'])
            extrema=im.convert('RGB').getextrema();assert any(a!=b for a,b in extrema)
            images.append({'path':p.relative_to(B).as_posix(),'sha256':sha(p),'size':list(im.size),'source_geometry_sha256':item['source_geometry_sha256'],'derived_section':item.get('section_derived',False)})
assert len(images)==17
for n in ['01_FRONT','02_OBLIQUE']:
    assert all(macro[k]['cameras'][n]==macro['A']['cameras'][n] for k in 'BC')
assert len(sel['renders'])==11
assert len(set(v['source_geometry_sha256'] for v in sel['renders']))==1
assert sel['geometry']['primary_non_manifold_edges']==0
assert audit['primary_mass_unchanged_from_macro_C']['result']=='PASS'
for n,c in audit['selected_eye_floor_checks'].items():
    assert c['hit'] and abs(c['eye_height_m']-1.7)<.01,(n,c)
for name in ['macro_A','macro_B','macro_C','selected']:
    b=(R/name/'study.glb').read_bytes();magic,version,length=struct.unpack('<4sII',b[:12]);assert magic==b'glTF' and version==2 and length==len(b)

art={'study_id':'B2-G6','authority':'Internal research self-review. Central supervisor retains formal authority.','A':'REJECT','B':'REJECT','C':'REJECT','selected_for_spatial_investigation':'C','formal_adoption':None,'findings':['A/B repeat detached vault units','C has actual roof/public-room/living-ground relationships but remains a thick terraced gate','Scene A is dominated by monumental arch, not readable urban life','Scene B has a real roof-to-next-interior threshold but insufficient lived urban richness','More housing/windows would not fix primary form'],'detail_after_final_review':'STOP','G7':'HOLD'}
write('art_review.json',art)
write('history.json',{'study_id':'B2-G6','branch':'art/b','g5_head':'05c224a46e030db4ac8dc28c49103bffced31aa3','events':[{'event':'CENTRAL_SUPERVISOR_REQUEST','scope':'G5-01 priority real 3D investigation; not formal art adoption'},{'event':'TWO_INDEPENDENT_MASSING_RULES_MODELLED','candidates':['A','B'],'housing_added':False},{'event':'MACRO_REJECT','candidates':['A','B'],'next':'Redesign formation rule'},{'event':'C_REDESIGN_SELECTED_FOR_SPATIAL_VERIFICATION','record':'selection.json','formal_adoption':False},{'event':'C01_TECHNICAL_DIAGNOSTICS','archive':'iterations/C01','issues':'duplicate coplanar arrival floor and hanging lift representation; technical fixes do not claim art improvement'},{'event':'FINAL_11_VIEW_AND_INTERIOR_REVIEW','candidate':'C','status':'REJECT','record':'art_review.json','further_detail':'STOP'}],'preserved_lineage':['studies/B2-G4/history.json','studies/B2-G5/history.json'],'construction':'HOLD','Work':'PRIOR_APPROVAL_REQUIRED'})
write('verification.json',{'study_id':'B2-G6','stage':'BLOCKOUT_3D','technical_checks':{'actual_glb_reloads':4,'images_from_mesh_rendering':17,'selected_images_same_geometry':11,'shared_macro_cameras':'PASS','primary_C_mesh_unchanged':'PASS','finite_imported_vertices':'PASS','selected_primary_non_manifold_edges':0,'actual_eye_floor_checks':'PASS','roof_surface_samples':len(audit['selected_roof_surface_samples'])},'selected_measured_bounds_m':sel['bounds_m'],'selected_mesh_statistics':sel['geometry'],'modelled_court_blocks':len(sel['districts']),'images':images,'art_status':'REJECT_INTERNAL_RESEARCH_REVIEW','formal_adoption':None,'limitations':['No structural or climate engineering','No full network clash/egress/capacity certification','No dwelling interior plans','W0 concept backdrop only; no canonical coordinate alignment','Section is temporary uncapped bisection of same source mesh','Population and functional capacity not calculated'],'source_baseline':{'G5_head':'05c224a46e030db4ac8dc28c49103bffced31aa3','REPORT_sha256':sha(B/'studies/B2-G5/REPORT_ja.md'),'sections_png_sha256':sha(B/'studies/B2-G5/sections.png'),'comparison_png_sha256':sha(B/'studies/B2-G5/comparison.png')}})

figures=''.join(f'<figure><img loading="lazy" src="selected/{n}.png" alt="{label}"><figcaption>{label} — 実メッシュからのCyclesレンダー</figcaption></figure>' for n,label in views)
page='''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>B2-G6 実3D研究審査</title><style>body{background:#101b25;color:#dce8eb;font:17px/1.8 'Yu Gothic',sans-serif;margin:0}main{max-width:1440px;padding:30px;margin:auto}h1,h2{color:#ead2a3}a{color:#81cfc4}img{display:block;width:100%;height:auto}figure{margin:24px 0}figcaption{padding:8px}aside{border-left:5px solid #d49485;padding:16px 24px;background:#172834}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}@media(max-width:800px){.grid{display:block}}nav a{margin-right:20px}</style><main><h1>B2-G6｜昇街褶都：実3D検証</h1><p>2026-10-23 / art/b / 実形状・実レンダー / 正式採用なし</p><aside><b>結論：研究内美術REJECT。</b> A/Bの異なる形成規則を比較して停止し、Cを再設計して実生活街区と公共室を検証。Cも厚い段状の門と低い生活密度の問題が残り、中央文明都市の美術目標は未達。住宅追加・細密化・G7への移行は停止。技術PASSは美術合格ではありません。</aside><nav><a href="REPORT_ja.md">研究報告全文</a><a href="selected/study.glb">実GLB</a><a href="selected/study.blend">実BLEND</a><a href="verification.json">検証</a><a href="glb_reload_audit.json">GLB再読み込み</a></nav><h2>異なる二構成と、失敗後の第三案</h2><img src="macro_comparison.jpg" alt="A/B/Cの住宅追加前の実3D比較"><h2>同じ主質量の制作前後</h2><img src="macro_to_occupied.jpg" alt="Cの住宅追加前と後。主質量は不変"><h2>地上・高所・公共内部・中庭</h2><img src="scenes_AB.jpg" alt="場面A/Bと内部・中庭"><h2>同一Cモデルからの全景・外部・眼高・断面</h2><p>W0は概念背景のみ。M207/M204/M117座標の統合は行っていません。断面はX=0で一時的に東側を切除した派生表示です。</p><div class="grid">'''+figures+'''</div><h2>原本と履歴</h2><p><a href="macro_A/study.glb">不採用A GLB</a> / <a href="macro_B/study.glb">不採用B GLB</a> / <a href="macro_C/study.glb">マクロC GLB</a> / <a href="selection.json">Cの空間検証選抜記録</a> / <a href="art_review.json">最終美術REJECT</a> / <a href="history.json">履歴</a> / <a href="manifest.json">資産索引</a></p><p>正式M247-C・原本を保護。Minecraft施工HOLD。Work利用は事前承認制。構造・環境・住居内部・都市機能の成立は未検証です。</p></main></html>'''
(R/'review.html').write_text(page,encoding='utf-8')
for href in re.findall(r'(?:src|href)="([^"]+)"',page):
    if href!='manifest.json':assert (R/href).is_file(),href

# Publish only deliverables and explicit iteration records; never blend backup files.
files=[p for p in sorted(R.rglob('*')) if p.is_file() and p.suffix in ['.py','.ps1','.md','.json','.png','.jpg','.glb','.blend','.html','.log'] and p.name not in ['manifest.json','delivery_receipt.json']]
# Subfolder manifests are essential source records; exclude only the root self-manifest.
files += [R/sub/'manifest.json' for sub in ['macro_A','macro_B','macro_C','selected','iterations/C01']]
files=sorted(set(files))
def kind(p):return {'.glb':'GLB','.blend':'BLEND','.png':'PNG','.jpg':'JPEG','.json':'JSON','.md':'REPORT','.py':'CODE','.ps1':'CODE','.log':'LOG','.html':'HTML'}[p.suffix]
assets=[{'path':p.relative_to(B).as_posix(),'kind':kind(p),'sha256':sha(p),'size_bytes':p.stat().st_size} for p in files]
write('manifest.json',{'study_id':'B2-G6','branch':'art/b','stage':'BLOCKOUT_3D','art_review_status':'REJECT','selected_for_spatial_investigation':'C','formally_selected':None,'assets':assets,'dimensions_m':sel['bounds_m'],'g5_counterproposal_preserved':'studies/B2-G5/REPORT_ja.md#4','holds':['G7','FURTHER_DETAIL','MINECRAFT_CONSTRUCTION','UNAPPROVED_WORK_USE']})
idx=json.loads((B/'latest.json').read_text(encoding='utf-8-sig'))
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
idx['latest']={'study_id':'B2-G6','title':'昇街褶都：形成規則3案と実生活断面・美術未達','stage':'BLOCKOUT_3D','art_review_status':'REJECT','review_authority':'Internal research self-review; central supervisor retains formal authority','updated_at':now,'dimensions_m':dict(zip(['width','depth','height'],sel['bounds_m']['size'])),'proposed_dimensions_m':None,'selected_concept':None,'selected_for_spatial_investigation':'C','assets':assets+[{'path':'studies/B2-G6/manifest.json','kind':'JSON','sha256':sha(R/'manifest.json'),'size_bytes':(R/'manifest.json').stat().st_size}],'validation':{'report':'studies/B2-G6/verification.json','actual_glb_reload':'PASS','shared_macro_cameras':'PASS','selected_same_model_views':'PASS','art_gate':'FAIL','structural_feasibility':'NOT_TESTED','functional_city':'NOT_VERIFIED'},'notes':'A/B rejected before housing. C redesigned and modelled with actual public rooms and roof districts, but final internal art REJECT. Four current GLBs/BLENDs; initial detailed BLEND retained. W0 unregistered. No further detail/G7/construction.'}
if not any(v.get('study_id')=='B2-G6' for v in idx['history']):idx['history'].append({'study_id':'B2-G6','manifest':'studies/B2-G6/manifest.json','event':'real_3D_investigation_submission','art_review_status':'REJECT','updated_at':now})
idx['last_submission_at']=now
(B/'latest.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'assets':len(assets)+1,'bytes':sum(a['size_bytes'] for a in assets),'largest_file_bytes':max(a['size_bytes'] for a in assets),'selected_bounds':sel['bounds_m'],'images':len(images),'art':'REJECT'}))
