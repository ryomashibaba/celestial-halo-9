"""Compose labelled sheets from actual renders, inspect files, no new architecture."""
import sys,json,hashlib,ast
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
FONT=Path('C:/Windows/Fonts/segoeui.ttf')
def font(n):return ImageFont.truetype(str(FONT),n)
def tile(im,path,xy,size,label):
    with Image.open(path) as src:
        src.verify()
    with Image.open(path) as src:
        src=src.convert('RGB');src.thumbnail(size)
        im.paste(src,xy)
    ImageDraw.Draw(im).text((xy[0]+8,xy[1]+size[1]+7),label,font=font(18),fill='#e5e5dc')
pairs=['02_CENTRAL_CHOIR','03_FORUM_HUMAN','10_EAST_CITY_SECTION','08_WHOLE_CITY']
im=Image.new('RGB',(1940,2660),'#15262c');d=ImageDraw.Draw(im)
d.text((20,12),'R29 TIDAL COMMONS | MATCHED ACTUAL BLENDER COMPARISON',font=font(29),fill='#f1e0bd')
d.text((20,53),'R28 left / R29 right. Same camera, sun, world, exposure, Cycles 32 samples, 1600 x 1000.',font=font(22),fill='white')
d.text((20,85),'Independent relative-coordinate study. Producer ART HOLD; not adopted art or a completed city master.',font=font(20),fill='#b6c5c9')
for i,name in enumerate(pairs):
    y=125+i*628
    tile(im,R/'comparison'/('R28_'+name+'.png'),(10,y),(950,594),'R28 | '+name)
    tile(im,R/'renders'/(name+'.png'),(980,y),(950,594),'R29 | '+name)
im.save(R/'comparison/MATCHED_BEFORE_AFTER.jpg',quality=94)
names=['02_CENTRAL_CHOIR','03_FORUM_HUMAN','06_REAR_NORTH','08_WHOLE_CITY','10_EAST_CITY_SECTION','11_SKY_READING_HUMAN','12_CENTRAL_ARRIVAL_HUMAN','14_LEARNING_HUMAN','16_B_LOWER_PUBLIC_CITY']
log=(R/'process/delivery_render.log').read_text(encoding='utf8')
assert all('RENDER_DONE '+name in log for name in names)
assert 'RENDER_DONE 10_EAST_CITY_SECTION' in (R/'process/matched_R28_render.log').read_text(encoding='utf8')
assert all((R/'renders'/(name+'.png')).stat().st_mtime >= (R/'model/R29_TIDAL_COMMONS.blend').stat().st_mtime for name in names)
im=Image.new('RGB',(1940,1440),'#15262c');d=ImageDraw.Draw(im)
d.text((18,12),'R29 | TIDAL COMMONS | ACTUAL SAVED BLENDER MODEL',font=font(29),fill='#f1e0bd')
d.text((18,53),'Producer ART HOLD: local architectural progress; lived-city / whole-city quality remains unresolved.',font=font(22),fill='white')
for i,name in enumerate(names):
    x=10+(i%3)*645;y=105+(i//3)*440
    tile(im,R/'renders'/(name+'.png'),(x,y),(630,394),name)
im.save(R/'qa/REVIEW_SHEET.jpg',quality=94)
for p in R.glob('*.py'):ast.parse(p.read_text(encoding='utf8'),filename=str(p))
qa=json.loads((R/'qa/SAVED_GEOMETRY_CHECK.json').read_text(encoding='utf8'))
sp=json.loads((R/'qa/SPACE_AND_CONNECTIONS.json').read_text(encoding='utf8'))
cams=json.loads((R/'qa/CAMERAS.json').read_text(encoding='utf8'))
delta=json.loads((R/'qa/ACTUAL_MESH_DELTA.json').read_text(encoding='utf8'))
receipt={'final_render_count':len(names),'matched_comparison_pairs':len(pairs),'render_dimensions':[1600,1000],'geometry_readback_pass':qa['geometry_readback_pass'],'meshes':qa['saved_blend']['meshes'],'triangles':qa['saved_blend']['triangles'],'R28_camera_lens_and_pose_identical':all(delta['R28_camera_transforms_and_lenses_unchanged'].values()),'R28_lighting_and_quality_identical':delta['R28_lighting_exposure_and_quality_unchanged'],'floor_supported_human_cameras':sum(bool(c.get('floor_height_pass')) for c in cams),'floor_join_segments':len(sp['sampled_floor_joins']),'floor_samples_per_segment':21,'floor_join_pass':all(j['all_floor_samples_pass'] for j in sp['sampled_floor_joins']),'clear_public_rays':sum(r['clear'] for r in sp['rays'][:7]),'public_rays_tested':7,'distant_city_ray_first_hit':sp['rays'][7]['first_hit'],'art':'Producer ART HOLD; formal central adoptions 0','world':'HOLD; no actual save access','not_certified':['complete public interiors','full routes and egress','vehicle turn radius / operations / capacity','body swept clearance and all interpenetrations','structure','canonical city coordinates / official assets','whole 10km art and detailed completion','Minecraft construction']}
(R/'qa/DELIVERY_SUMMARY.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
files=[]
for p in sorted(R.rglob('*')):
    if p.is_file() and p.name!='MANIFEST_SHA256.json':
        raw=p.read_bytes();files.append({'path':p.relative_to(R).as_posix(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
(R/'MANIFEST_SHA256.json').write_text(json.dumps({'files':files,'scope':'R29 directory except this manifest; regenerated before commit'},indent=2),encoding='utf8')
assert receipt['geometry_readback_pass'] and receipt['floor_join_pass'] and receipt['clear_public_rays']==7
print(json.dumps(receipt,ensure_ascii=False,indent=2))
