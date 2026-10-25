"""Build a labeled comparison sheet from actual renders; no image synthesis."""
import sys,json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
labels=[('01_SW_VOID','SW negative space / aerial'),('02_EAST_SEA','East inland sea / aerial'),
        ('03_NORTH_HIGHLAND','North highland / aerial'),('04_CENTRAL_OBLIQUE','Central oblique / aerial'),
        ('05_ENTRY_HUMAN','Entry / actual study floor +1.7m'),('06_PUBLIC_PLAZA','Public plaza / actual floor +1.7m'),
        ('07_SKY_HARBOR','Sky harbor / actual floor +1.7m'),('08_REAR_UNDERSIDE','Rear / upper underside / floating'),
        ('09_WHOLE_AERIAL','Whole terrain / aerial')]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
big=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',25)
sheet=Image.new('RGB',(1920,1512),'#15242d');d=ImageDraw.Draw(sheet)
d.text((18,14),'R27B | ACTUAL BLENDER RENDERS | ART REJECT',font=big,fill='#f0d5b2')
d.text((18,51),'All provisional relative placement. Not canonical W0 / H / SB or Minecraft coordinates.',font=font,fill='white')
for i,(name,label) in enumerate(labels):
    im=Image.open(R/'renders'/f'{name}.png');assert im.size==(1440,960)
    im=im.convert('RGB').resize((632,421),Image.Resampling.LANCZOS)
    x=6+(i%3)*640;y=90+(i//3)*472
    sheet.paste(im,(x,y));d.text((x+5,y+428),name[:2]+' '+label,font=font,fill='white')
sheet.save(R/'qa/REVIEW_SHEET.jpg',quality=93)
qa=json.loads((R/'qa/SAVED_GEOMETRY_CHECK.json').read_text(encoding='utf8'))
g=qa['saved_blend']['group_bounds']
def union(keys):
    lo=[min(g[k]['min_m'][i] for k in keys) for i in range(3)]
    hi=[max(g[k]['max_m'][i] for k in keys) for i in range(3)]
    return {'min_m':lo,'max_m':hi,'dimensions_m':[hi[i]-lo[i] for i in range(3)]}
out={'all_geometry_m':qa['saved_blend']['dimensions_m'],
     'architecture_excluding_terrain_and_water':union([k for k in g if k!='TERRAIN_STUDY']),
     'central_architecture':union([k for k in g if k.startswith('CENTRAL_')]),
     'render_count':len(labels),'floor_camera_count':len(qa['saved_floor_recheck']),
     'geometry_readback':qa['geometry_readback_pass'],'art':'REJECT','Stage_D':False,
     'official_master_complete':False,'coordinate_transform_verified':False,'formal_art_adoptions':0,'minecraft':'HOLD'}
(R/'qa/DELIVERY_SUMMARY.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps(out,indent=2))
files=[]
for p in sorted(R.rglob('*')):
    if p.is_file() and p.name!='MANIFEST_SHA256.json':
        raw=p.read_bytes();files.append({'path':p.relative_to(R).as_posix(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
(R/'MANIFEST_SHA256.json').write_text(json.dumps({'scope':'R27B files except this manifest itself','files':files},indent=2),encoding='utf8')
