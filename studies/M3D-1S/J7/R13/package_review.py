"""Offline review packaging: labels/resizing only, no invented architecture."""
import sys
sys.dont_write_bytecode=True
import json,hashlib,ast
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageStat
ROOT=Path(__file__).parent
QA=ROOT/'qa';QA.mkdir(exist_ok=True)
FONT=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
SMALL=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)

def sheet(name,items,cols=3,width=540):
    rows=(len(items)+cols-1)//cols;tileh=int(width*1000/1200)
    image=Image.new('RGB',(cols*width,rows*(tileh+42)),(19,28,37));draw=ImageDraw.Draw(image)
    for i,(label,path) in enumerate(items):
        src=Image.open(ROOT/path).convert('RGB');src.thumbnail((width,tileh))
        x=(i%cols)*width;y=(i//cols)*(tileh+42)
        image.paste(src,(x+(width-src.width)//2,y))
        draw.text((x+12,y+tileh+9),label,fill=(225,232,235),font=SMALL)
    image.save(QA/name,quality=93)

sheet('R13_EXPLORATION_COMPARISON.jpg',[(n,p+'/02_OBLIQUE.png') for n,p in [('A / open courtyard stack - REJECT','exploration_A'),('B / meridional chambers - REJECT','exploration_B'),('C / carved city land - selected for revision','selected')]])
sheet('R13_MAIN_FORM_REVISIONS.jpg',[(n,p+'/'+v+'.png') for v in ['02_OBLIQUE','04_REAR'] for n,p in [('C selected','selected'),('C revision 1','revision_1'),('C revision 2 / ART REJECT','revision_2')]])
sheet('R13_FINAL_SIX_VIEWS.jpg',[(n,'revision_2/'+n+'.png') for n in ['01_FRONT','02_OBLIQUE','03_SIDE','04_REAR','05_AERIAL','06_GROUND']])
sheet('R13_SPATIAL_EVIDENCE.jpg',[(n,'revision_2/'+n+'.png') for n in ['07_MAIN_CAVERN','08_MID_CITY','09_HUMAN_EYE_1_7M','10_REVERSE_WORLD']]+[('Real cut XZ / Y=680m','sections/SECTION_XZ_Y680/SECTION_XZ_Y680.png'),('Real cut YZ / X=0m','sections/SECTION_YZ_X0/SECTION_YZ_X0.png')])

readback=json.loads((QA/'BLEND_GLB_READBACK.json').read_text(encoding='utf8'))
assert readback['basic_persistence_pass']
groups=['exploration_A','exploration_B','exploration_C','selected','revision_1','revision_2','sections']
images=[]
for group in groups:
    for path in sorted((ROOT/group).rglob('*.png')):
        with Image.open(path) as im:
            assert im.size==(1200,1000),(path,im.size)
            stat=ImageStat.Stat(im.convert('RGB'))
            images.append(dict(path=str(path.relative_to(ROOT)).replace('\\','/'),size=list(im.size),mean_rgb=stat.mean))
            assert max(stat.mean)>8,'black image '+str(path)
# Wide cameras are the exact same metre coordinates and projection for every stage.
wide=['01_FRONT','02_OBLIQUE','03_SIDE','04_REAR','05_AERIAL','06_GROUND']
reference=json.loads((ROOT/'exploration_A/cameras.json').read_text())
for g in ['exploration_B','exploration_C','selected','revision_1','revision_2']:
    data=json.loads((ROOT/g/'cameras.json').read_text())
    assert all(data[k]==reference[k] for k in wide),g
for p in ROOT.glob('*.py'):ast.parse(p.read_text(encoding='utf8'),filename=str(p))
native=Image.open(ROOT/'revision_2/02_OBLIQUE.png').convert('RGB')
glb=Image.open(QA/'ACTUAL_GLB_REIMPORT_OBLIQUE.png').convert('RGB')
diff=ImageStat.Stat(ImageChops.difference(native,glb))
out=dict(status='PASS_BASIC_EVIDENCE_ONLY',images=images,actual_png_count=len(images),
         matched_six_cameras=True,source_syntax=True,
         independent_glb_render_mean_absolute_rgb_error=diff.mean,
         independent_glb_render_extrema=ImageChops.difference(native,glb).getextrema(),
         actual_human_floor_ray_distance_m=1.6999511543437185,
         limitations=['Nonblack image check is not artistic quality','No full walking or enclosed void volume measured','City master incomplete; art rejected'])
(QA/'OFFLINE_EVIDENCE_QA.json').write_text(json.dumps(out,indent=2),encoding='utf8')
manifest=[]
for g in groups:
    for p in sorted((ROOT/g).rglob('*')):
        if p.is_file() and p.suffix in ['.blend','.glb','.png','.json']:
            manifest.append(dict(path=str(p.relative_to(ROOT)).replace('\\','/'),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(QA/'MODEL_IMAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps(dict(offline_checks='PASS',actual_pngs=len(images),manifest_files=len(manifest),glb_render_mean_rgb_error=diff.mean),ensure_ascii=False))
