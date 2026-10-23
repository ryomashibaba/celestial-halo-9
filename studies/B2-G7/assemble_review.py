"""Pillow: assemble actual Blender views; no painted or generated architecture."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,datetime
p=Path(__file__).resolve().parent
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',22)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
im=Image.new('RGB',(1440,930),'#e5e8e8');d=ImageDraw.Draw(im)
d.text((22,14),'CELESTIAL HALO-9 / B2-G7 / INITIAL ART GATE',fill='#25383f',font=font)
d.text((22,48),'A: Street-cell accretion    B: Confluence grounds    /    Both rejected before occupied-city modeling',fill='#25383f',font=small)
ctx=Image.new('RGB',(1440,640),'#e5e8e8');cd=ImageDraw.Draw(ctx);cd.text((22,12),'10 km schematic context / unregistered study coordinates',font=font,fill='#25383f')
for i,c in enumerate('AB'):
 folder=p/(c+'_massing');m=json.loads((folder/'manifest.json').read_text())
 for n in ['oblique','side','rear','context']:
  src=Image.open(folder/(n+'.png')).convert('RGB');src.save(folder/(n+'.jpg'),quality=83,optimize=True)
 for j,n in enumerate(['oblique','side','rear']):
  x=j*480;y=108+i*408;im.paste(Image.open(folder/(n+'.jpg')).resize((480,380)),(x,y))
  d.text((x+12,y-26),c+' / '+n.upper(),font=small,fill='#25383f')
 ctx.paste(Image.open(folder/'context.jpg').resize((720,570)),(i*720,60));cd.text((i*720+15,40),c,font=small,fill='#25383f')
 for r in m['renders']:r['path']=r['path'].replace('.png','.jpg')
 m['render_distribution']='JPEG derivatives of lossless Blender renders; rerun generation to obtain PNG sources'
 (folder/'manifest.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
d.text((22,906),'Actual same-model views / no formal adoption / no detailed model / Minecraft HOLD / Work prior approval',font=small,fill='#25383f')
im.save(p/'preview.jpg',quality=85,optimize=True);ctx.save(p/'context_comparison.jpg',quality=83,optimize=True)
# Publish only review evidence, sources, comparison BLENDs and minimal QA, never temp logs/backups.
files=[p/n for n in ['principles.md','decision.md','preview.jpg','context_comparison.jpg','build_scene.py','assemble_review.py','audit_saved.py','reproduce.ps1','verification.json']]
for c in 'AB':files.extend(p/(c+'_massing')/n for n in ['study.blend','manifest.json','oblique.jpg','side.jpg','rear.jpg','context.jpg'])
assets=[]
for f in files:
 if not f.exists():continue
 data=f.read_bytes();assets.append(dict(path=f.relative_to(p.parent.parent).as_posix(),size_bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),git_blob_sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()))
manifest=dict(study_id='B2-G7',branch='art/b',base_head='6da74b479bae8250739fe9fc413e513b94e243fd',stage='INITIAL_ART_GATE_STOPPED',art_review_status='BOTH_REJECT_INTERNAL',selected_concept=None,formal_adoption=False,assets=assets,construction='HOLD',work='PRIOR_APPROVAL_REQUIRED')
(p/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
root=p.parent.parent;latest=json.loads((root/'latest.json').read_text(encoding='utf-8'));previous=latest['latest']
if previous['study_id']=='B2-G7':previous=previous['previous_study']
latest['latest']=dict(study_id='B2-G7',title='街胞断層・合流地盤：二つの形成原理と初期美術REJECT',stage=manifest['stage'],art_review_status=manifest['art_review_status'],review_authority='Internal research self-review; central supervisor retains formal authority',updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),selected_concept=None,formal_adoption=False,assets=assets+[dict(path='studies/B2-G7/manifest.json',kind='MANIFEST')],decision='studies/B2-G7/decision.md',previous_study=dict(study_id=previous['study_id'],art_review_status=previous['art_review_status']),minecraft='HOLD',work='PRIOR_APPROVAL_REQUIRED')
if not any(h.get('study_id')=='B2-G7' for h in latest.get('history',[])):
 latest.setdefault('history',[]).append(dict(study_id='B2-G7',manifest='studies/B2-G7/manifest.json',event='initial_art_gate_submission',art_review_status='BOTH_REJECT_INTERNAL',updated_at=latest['latest']['updated_at']))
latest['last_submission_at']=latest['latest']['updated_at']
(root/'latest.json').write_text(json.dumps(latest,ensure_ascii=False,indent=2),encoding='utf-8')
print('ASSEMBLED',len(assets),'assets; total',sum(x['size_bytes'] for x in assets),'bytes')
