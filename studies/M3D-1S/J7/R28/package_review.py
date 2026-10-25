"""Deterministic sheets, measured summary, byte manifest. No image synthesis."""
import sys,json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
labels=[('01_ESTUARY_CITY','Estuary / city composition'),('02_CENTRAL_CHOIR','Central oblique'),
 ('03_FORUM_HUMAN','Public forum / floor +1.7m'),('04_LIBRARY_LANE','Library lane / floor +1.7m'),
 ('05_SEA_TERRACE','Sea terrace / floor +1.7m'),('06_REAR_NORTH','North rear / aerial'),
 ('07_SKY_COURT','Unassigned sky B / floor +1.7m'),('08_WHOLE_CITY','Whole provisional composition / aerial'),
 ('09_UPPER_CIVIC_PROMENADE','Upper public promenade / floor +1.7m')]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
big=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',26)
sheet=Image.new('RGB',(1920,1450),'#172731');d=ImageDraw.Draw(sheet)
d.text((18,12),'R28 | CELESTIAL ESTUARY | ACTUAL BLENDER RENDERS',font=big,fill='#dfd4bd')
d.text((18,49),'Producer ART HOLD / promising partial architecture. Independent provisional coordinates. NOT completed city master.',font=font,fill='white')
for i,(name,label) in enumerate(labels):
    im=Image.open(R/'renders'/f'{name}.png');assert im.size==(1600,1000)
    im=im.convert('RGB').resize((632,395),Image.Resampling.LANCZOS)
    x=6+(i%3)*640;y=86+(i//3)*450
    sheet.paste(im,(x,y));d.text((x+5,y+403),name[:2]+' '+label,font=font,fill='white')
sheet.save(R/'qa/REVIEW_SHEET.jpg',quality=94)
qa=json.loads((R/'qa/SAVED_GEOMETRY_CHECK.json').read_text(encoding='utf8'));g=qa['saved_blend']['group_bounds']
def union(keys):
    lo=[min(g[k]['min_m'][i] for k in keys) for i in range(3)]
    hi=[max(g[k]['max_m'][i] for k in keys) for i in range(3)]
    return {'min_m':lo,'max_m':hi,'dimensions_m':[hi[i]-lo[i] for i in range(3)]}
out={'date_jst':'2026-10-26','art':'PRODUCER ART HOLD / promising partial architecture, breakthrough not established',
 'central_architecture':union([k for k in g if k.startswith('CENTRAL')]),
 'architecture_and_transport_excluding_terrain_sea_far_ground':union([k for k in g if not k.startswith('CONTEXT')]),
 'background_extent_is_not_city_size':True,'mesh_count':qa['saved_blend']['meshes'],
 'triangles':qa['saved_blend']['triangles'],'render_count':len(labels),'saved_geometry_readback_pass':qa['geometry_readback_pass'],
 'human_floor_camera_count':5,'public_volume_full_verification':False,'formal_city_master_complete':False,
 'canonical_transform_verified':False,'formal_art_adoptions':0,'minecraft':'HOLD',
 'next_value':'Co-design a specific inhabited wing slice, sky arrival station and public room as a connected architectural section; replace generic repeated districts and refine the silhouette after independent review.'}
(R/'qa/DELIVERY_SUMMARY.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
files=[]
for p in sorted(R.rglob('*')):
    if p.is_file() and p.name!='MANIFEST_SHA256.json':
        assert p.suffix not in ['.blend1','.pyc'],p
        raw=p.read_bytes();files.append({'path':p.relative_to(R).as_posix(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
(R/'MANIFEST_SHA256.json').write_text(json.dumps({'scope':'R28 files except this manifest itself','files':files},indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False,indent=2));print('MANIFEST',len(files),'files',sum(f['bytes'] for f in files),'bytes')
