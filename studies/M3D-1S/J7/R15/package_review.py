"""Offline evidence/manifest and contact sheets. Run python -B -X utf8.
Does not render or invent architectural imagery. No outside file reads/writes.
"""
import json,hashlib,sys
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageChops,ImageStat
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;Q=R/'qa';Q.mkdir(exist_ok=True)
def sheet(items,dest,cols=2,w=700):
 h=660;im=Image.new('RGB',(w*cols,h*((len(items)+cols-1)//cols)),(18,28,35));dr=ImageDraw.Draw(im)
 for i,(p,label) in enumerate(items):
  image=Image.open(R/p).convert('RGB');image.thumbnail((w,h-40))
  x=(i%cols)*w+(w-image.width)//2;y=(i//cols)*h+35
  im.paste(image,(x,y));dr.text(((i%cols)*w+15,(i//cols)*h+10),label,fill='white')
 im.save(Q/dest,quality=91)
sheet([(f'{stage}/{v}.png',label+' / '+v) for stage,label in [('concept','INITIAL'),('revision_1','REVISION 1'),('revision_2','REVISION 2')] for v in ['01_FRONT','02_OBLIQUE']],'R15_MAIN_FORM_REVISIONS.jpg')
sheet([(f'revision_2/{v}.png',v) for v in ['01_FRONT','02_OBLIQUE','03_SIDE','04_REAR','05_AERIAL','06_SHARED_CANYON']],'R15_MACRO_VIEWS.jpg',3)
sheet([(f'revision_2/{v}.png',v) for v in ['11_WEST_STREET_WORLD','12_EAST_CANAL_WORLD','08_HUMAN_WEST','10_HUMAN_CANYON']]+[(f'sections/{v}/{v}.png',v) for v in ['SECTION_XZ_Y0','SECTION_YZ_X0']],'R15_SPATIAL_EVIDENCE.jpg',2)
qa=json.loads((Q/'BLEND_GLB_READBACK.json').read_text('utf8'))
build=json.loads((R/'revision_2/BUILD_EVIDENCE.json').read_text('utf8'))
assert qa['pass_basic_persistence']
assert all(x['pass_1_7m_2mm'] for x in build['human_floor_rays'].values())
required=[R/'revision_2'/f'{v}.png' for v in ['01_FRONT','02_OBLIQUE','03_SIDE','04_REAR','05_AERIAL','06_SHARED_CANYON','07_WEST_DISTRICT','08_HUMAN_WEST','09_EAST_DISTRICT','10_HUMAN_CANYON','11_WEST_STREET_WORLD','12_EAST_CANAL_WORLD']]
required += [R/'sections'/v/(v+'.png') for v in ['SECTION_XZ_Y0','SECTION_YZ_X0']]
for p in required:
 with Image.open(p) as im:assert im.size==(1200,1100);im.verify()
diff=ImageChops.difference(Image.open(R/'revision_2/02_OBLIQUE.png').convert('RGB'),Image.open(Q/'GLB_REIMPORT_OBLIQUE.png').convert('RGB'))
comparison=dict(mean_absolute_rgb_difference_0_255=ImageStat.Stat(diff).mean,max_absolute_rgb_difference_0_255=[x[1] for x in diff.getextrema()],scope='Independent GLB render with identical studio and camera; stochastic Cycles and normal representation can differ.')
(Q/'GLB_NATIVE_IMAGE_COMPARISON.json').write_text(json.dumps(comparison,indent=2),encoding='utf8')
manifest=[]
for p in sorted(R.rglob('*')):
 if p.is_file() and p.suffix in ('.png','.jpg','.blend','.glb'):
  manifest.append(dict(path=p.relative_to(R).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(Q/'MODEL_IMAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
(Q/'OFFLINE_EVIDENCE_QA.json').write_text(json.dumps(dict(required_final_images=len(required),all_pngs_decode=True,human_both_actual_floor_rays_pass=True,readback_models_pass=len(qa['models']),manifest_files=len(manifest),actual_blender_render_pngs=len(list(R.rglob('*.png'))),image_processing='Resize, label and arrange only. No image generation, architectural enhancement or painted geometry.',walkability='NOT_CERTIFIED',art='SEPARATE_HUMAN_AND_RESEARCH_JUDGMENT_REQUIRED'),indent=2),encoding='utf8')
print('OFFLINE EVIDENCE PASS',len(manifest),'model/image files')
