import json,hashlib,shutil,zipfile,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'outputs'/'D10_Blender'
ROOT=OUT.parent.parent
(OUT/'sources').mkdir(exist_ok=True)
for p in Path(__file__).parent.glob('*.py'):
    target=OUT/'sources'/p.name
    if p.resolve()!=target.resolve():shutil.copy2(p,target)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
views=['OBLIQUE','REAR','FRONT','TOP','CIVIC','HALL']
def sheet(selected,path,width):
    pane=width//2;image_height=int(pane*825/1100);head=95;row=image_height+42
    board=Image.new('RGB',(width,head+row*len(selected)),(245,245,241));d=ImageDraw.Draw(board)
    d.text((20,10),'D10 / SAME SAVED 3D / ART REJECT',font=font,fill=(20,30,35))
    d.text((20,45),'BASE',font=font,fill=(20,30,35));d.text((pane+20,45),'DIRECT VERTEX EDIT',font=font,fill=(20,30,35))
    for r,view in enumerate(selected):
        top=head+r*row
        for c,stage in enumerate(['BASE','EDIT']):
            im=Image.open(OUT/(stage+'_'+view+'.png')).convert('RGB').resize((pane,image_height),Image.Resampling.LANCZOS)
            board.paste(im,(c*pane,top))
            d.text((c*pane+12,top+image_height+8),stage+' / '+view+' / identical camera',font=small,fill=(20,30,35))
    board.save(OUT/path,quality=90,subsampling=0)
sheet(views,'D10_SAME_SCENE_COMPARISON.jpg',1400)
sheet(['OBLIQUE'],'D10_OBLIQUE_COMPARISON.jpg',1600)
inventory=[]
for p in sorted(OUT.rglob('*')):
    if p.is_file() and p.name!='D10_BLENDER_EVIDENCE_MANIFEST.json':
        raw=p.read_bytes();inventory.append({'path':p.relative_to(OUT).as_posix(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'github_included':p.suffix!='.png'})
manifest={'study':'R33-S27-D10-BLENDER','date_jst':'2026-10-28','approval':'User replied 承認します to isolated local Blender trial immediately before execution',
 'execution':'Blender 5.2.1 LTS background; MCP live connection failed; no GUI direct manipulation proven',
 'source_research_head':'230254e26b407a05f0fc2ee46c85a3dcf34d2cf3','technical':'TECH LIMITED PASS','art':'ART REJECT',
 'formal_art_adoption':0,'city_master':'INCOMPLETE','minecraft':'HOLD','raw_png_count':12,
 'local_zip_only':['BASE_*.png','EDIT_*.png'],'manifest_self_hash':'omitted; use repository blob identity / ZIP external hash',
 'files':inventory}
(OUT/'D10_BLENDER_EVIDENCE_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
archive=ROOT/'outputs'/'R33_S27_D10_BLENDER_RESEARCH.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(OUT.rglob('*')):
        if p.is_file():z.write(p,'D10_Blender/'+p.relative_to(OUT).as_posix())
print(json.dumps({'files':len(inventory)+1,'zip':str(archive),'zip_bytes':archive.stat().st_size,'zip_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'github_files':sum(x['github_included'] for x in inventory)+1},ensure_ascii=False))
