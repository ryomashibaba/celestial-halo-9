"""Lossless PNG optimization, fixed-scale contact sheets, and evidence validation."""
from pathlib import Path
import json,hashlib,struct,html
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent
names={'N1':'抱候聖陸','N2':'懸海聖台','N3':'気候峡都','OLD':'旧・交湾大陸','OLD1':'旧・断海宮'}
views=['01_FRONT','02_OBLIQUE','03_SIDE','04_TOP','05_REAR','06_INTERIOR']
labels=['正面','斜視','側面','俯瞰','背面','内部・38mm']
font=ImageFont.truetype('C:/Windows/Fonts/YuGothM.ttc',24)
small=ImageFont.truetype('C:/Windows/Fonts/YuGothM.ttc',20)
checks={'study_id':'B2-G4','art_gate':'REJECT_INTERNAL_RESEARCH_REVIEW','user_art_adoption':False,'next_stage':'HOLD_REDESIGN_REQUIRED','checks':{},'limits':['Mesh checks do not establish architectural art, structural feasibility, environment control or inhabited city quality.','Interior cameras are diagnostics, not successful urban experiences.','N3 high camera is on an inclined sampled terrace, not proof of a flat habitable district.','No numerical occupancy, CFD, population or structural analysis was performed.']}
manifests={n:json.loads((R/n/'manifest.json').read_text(encoding='utf-8')) for n in names}
ref=manifests['N1']
for n,m in manifests.items():
 assert all(m['cameras'][v]==ref['cameras'][v] for v in views[:5]),n
 assert m['render']==ref['render'],n
 assert all(v['geometry_sha256']==m['geometry_sha256'] for v in m['renders']),n
 for item in m['renders']:
  p=R/n/item['file'];im=Image.open(p);assert im.size==(1120,980)
  rgb=im.convert('RGB');before=hashlib.sha256(rgb.tobytes()).hexdigest()
  # Fully opaque source PNGs; removing their constant alpha is lossless for displayed RGB.
  if 'A' in im.getbands():assert im.getchannel('A').getextrema()==(255,255)
  rgb.save(p,optimize=True)
  assert hashlib.sha256(Image.open(p).convert('RGB').tobytes()).hexdigest()==before
 checks['checks'][n]={'fixed_external_cameras':True,'fixed_render_conditions':True,'renders':len(m['renders']),'same_geometry_in_all_renders':True,'bounds_m':m['bounds_m'],'status':'REJECT' if not n.startswith('OLD') else 'INHERITED_REJECT'}
 if not n.startswith('OLD'):
  assert m['primary_mesh']['non_manifold_edges']==0
  p=R/n/'study.glb';buf=p.read_bytes();magic,version,length=struct.unpack_from('<III',buf)
  assert magic==0x46546c67 and version==2 and length==len(buf)
  jlen,jtype=struct.unpack_from('<II',buf,12);assert jtype==0x4e4f534a
  gltf=json.loads(buf[20:20+jlen]);assert gltf['asset']['version']=='2.0' and gltf.get('meshes')
  checks['checks'][n]['glb_header_and_meshes']='PASS'
  checks['checks'][n]['primary_mesh_non_manifold_edges']=0
checks['glb_reload']=json.loads((R/'glb_reload_audit.json').read_text())
checks['pedestrian_floor_checks']=manifests['N3']['pedestrian_floor_checks']
for d in checks['pedestrian_floor_checks'].values():assert d['hit'] and abs(d['eye_height_m']-1.7)<.05
protection=[]
for src,dest in [('research/dankaikyu_20261022/dankaikyu_A.glb','dankaikyu_A.glb'),('research/dankaikyu_20261022_study02/dankaikyu_II_A.glb','dankaikyu_II_A.glb'),('research/dankaikyu_20261022/REPORT_ja.md','Study01_REPORT_ja.md'),('research/dankaikyu_20261022_study02/REPORT_ja.md','Study02_REPORT_ja.md')]:
 p=R/'references'/dest;source=R.parent.parent/src
 digest=hashlib.sha256(p.read_bytes()).hexdigest()
 if source.exists():assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
 protection.append({'original_workspace_path':src,'archive_path':'references/'+dest,'sha256':digest,'bytes':p.stat().st_size,'archive_equals_current_original':True})
checks['reference_archive_checks']=protection
(R/'verification.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
def tile(draw,canvas,path,x,y,w,h,label):
 im=Image.open(path).convert('RGB');im.thumbnail((w,h-45));canvas.paste(im,(x+(w-im.width)//2,y+45));draw.text((x+10,y+8),label,font=small,fill='#ece8d8')
W,H=600,580
sheet=Image.new('RGB',(W*3,H),'#14202a');d=ImageDraw.Draw(sheet)
for i,n in enumerate(['N1','N2','N3']):tile(d,sheet,R/n/'02_OBLIQUE.png',i*W,0,W,H,n+' '+names[n]+' / 基本形 STOP')
sheet.save(R/'concept_comparison.jpg',quality=93,subsampling=0)
sheet=Image.new('RGB',(360*5,365*3),'#14202a');d=ImageDraw.Draw(sheet)
for row,n in enumerate(['N1','N2','N3']):
 for col,v in enumerate(views[:5]):tile(d,sheet,R/n/(v+'.png'),col*360,row*365,360,365,n+' '+labels[col])
sheet.save(R/'external_comparison.jpg',quality=93,subsampling=0)
sheet=Image.new('RGB',(440*5,440),'#14202a');d=ImageDraw.Draw(sheet)
for i,n in enumerate(['OLD1','OLD','N1','N2','N3']):tile(d,sheet,R/n/'02_OBLIQUE.png',i*440,0,440,440,n+' '+names[n])
sheet.save(R/'rejected_lineage.jpg',quality=93,subsampling=0)
blocks=[]
for n in ['N1','N2','N3','OLD1','OLD']:
 cards=''.join('<figure><a href="'+n+'/'+v['file']+'"><img loading="lazy" src="'+n+'/'+v['file']+'"></a><figcaption>'+html.escape(v['camera'])+'</figcaption></figure>' for v in manifests[n]['renders'])
 blocks.append('<section><h2>'+n+' '+names[n]+' — '+('継承REJECT' if n.startswith('OLD') else '基本形STOP・正式採択なし')+'</h2><p><a href="'+n+'/manifest.json">カメラ・寸法・幾何記録</a>'+(' / <a href="'+n+'/study.glb">実GLB</a> / <a href="'+n+'/study.blend">BLEND</a>' if not n.startswith('OLD') else '')+'</p><div class="grid">'+cards+'</div></section>')
(R/'review.html').write_text('<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>B2-G4 美術審査</title><style>body{background:#14202a;color:#eee9dc;font:17px/1.7 system-ui;margin:28px}a{color:#cdb680}h1{font-size:28px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}figure{margin:0}img{width:100%}section{margin:50px 0}strong{color:#ffb68c}</style><h1>CELESTIAL HALO-9 / B2-G4</h1><p><strong>3案とも研究内の基本形審査でSTOP。採択案なし。細密化・G5・施工はHOLD。</strong></p><p>画像は実メッシュのCycles描画。生成画像・完成予想図ではありません。外部5視点は同一カメラ・同一尺度・同一照明。内部は診断用で、都市生活の成立を示すものではありません。</p><p><a href="REPORT_ja.md">研究報告</a> / <a href="verification.json">検証JSON</a> / <a href="rejected_lineage.jpg">旧作との同条件比較</a></p>'+''.join(blocks)+'</html>',encoding='utf-8')
print('PASS: fixed camera comparisons, actual GLB reloads, image integrity, source copies; ART GATE STOP')
