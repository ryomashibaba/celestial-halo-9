"""Package diagnostic images and independently inspect exported GLBs. Python + Pillow + trimesh."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,trimesh
R=Path(__file__).resolve().parent
try:font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23)
except OSError:font=ImageFont.load_default()
# Palette conversion only; no image generation, compositing architecture, or retouching.
for p in (R/'renders').glob('*.png'):
 im=Image.open(p).convert('RGB');im.quantize(colors=128).save(p,optimize=True)
labels=['FRONT','OBLIQUE','SIDE','AERIAL','BACK','INTERIOR (model-specific camera)']
keys=['P1','P2','P2R']
sheet=Image.new('RGB',(1800,3*590),(18,26,32));d=ImageDraw.Draw(sheet)
for row,key in enumerate(keys):
 d.text((20,row*590+10),key+('  /  main-mass revision' if key=='P2R' else '  /  initial blockout'),fill='white',font=font)
 for j,p in enumerate(sorted((R/'renders').glob(key+'_*.png'))):
  im=Image.open(p).convert('RGB');im.thumbnail((300,270));x=j*300;y=row*590+55
  sheet.paste(im,(x,y));d.text((x+6,y+275),labels[j].split(' (')[0],fill='white',font=font)
 # Large matching oblique image shows the principal mass without losing all detail.
 im=Image.open(R/'renders'/f'{key}_02_oblique.png').convert('RGB');im.thumbnail((600,245));sheet.paste(im,(20,row*590+340))
 text={'P1':['STOP DETAIL: spiral ramp dominates','36 district markers; support probes fail','No four-horizon city verification'],
       'P2':['STOP DETAIL: overlapping voids','Cavern / mountain silhouette dominates','City markers do not establish habitation'],
       'P2R':['HOLD ART: tiered monument dominates','216 supported markers; city still schematic','Shared public boundaries remain unproven']}[key]
 for k,t in enumerate(text):d.text((340,row*590+365+k*55),t,fill=(222,225,220),font=font)
sheet.save(R/'comparison.png',optimize=True)
for key in keys:
 s=Image.new('RGB',(1500,1030),(18,26,32));dr=ImageDraw.Draw(s)
 for j,p in enumerate(sorted((R/'renders').glob(key+'_*.png'))):
  im=Image.open(p).convert('RGB');im.thumbnail((500,450));x=(j%3)*500;y=(j//3)*515;s.paste(im,(x,y));dr.text((x+10,y+465),key+' / '+labels[j].split(' (')[0],fill='white',font=font)
 s.save(R/f'{key}_six_views.png',optimize=True)
qa={}
for key in keys:
 scene=trimesh.load(R/f'{key}.glb',force='scene')
 items=[]
 for name,g in scene.geometry.items():
  g.merge_vertices(merge_tex=True,merge_norm=True);g.remove_unreferenced_vertices()
  items.append({'name':name,'watertight_after_vertex_merge':bool(g.is_watertight),'winding_consistent':bool(g.is_winding_consistent),'finite_vertices':bool(__import__('numpy').isfinite(g.vertices).all()),'vertices':len(g.vertices),'triangles':len(g.faces)})
 primary=[g.copy() for n,g in scene.geometry.items() if 'CITY_FOLD' in n or 'CIVIC_MASS' in n]
 joined=trimesh.util.concatenate(primary);joined.merge_vertices(merge_tex=True,merge_norm=True)
 qa[key]={'loader':'trimesh','geometry_count':len(items),'geometry':items,'primary_mass_after_material_partition_reassembly':{'watertight':bool(joined.is_watertight),'winding_consistent':bool(joined.is_winding_consistent),'vertices':len(joined.vertices),'triangles':len(joined.faces)},'scope':'Material partitions individually can be open. Main mass reassembled and welded for topology. No collision, support engineering or art acceptance'}
(R/'mesh-qa.json').write_text(json.dumps(qa,indent=2),encoding='utf8')
models=json.loads((R/'inherited/spatial-models.json').read_text(encoding='utf8'))
checks=json.loads((R/'inherited/geometric-checks.json').read_text(encoding='utf8'))
inherit={'source_branch':'art/a','source_commit':'2557681ad23a14399c6d5071d6b9adb0915ec8ba','N3_definition':next(x for x in models['models'] if x['id']=='N3'),'N3_checks':next(x for x in checks['models'] if x['id']=='N3'),'meaning':'Preserved analytic constraints and diagnostic results; NOT revalidated on P1/P2/P2R. Do not transfer N3 clearance or visibility claims to these new meshes.','preserved_checks':['Four N3 target points in a common frame with clear view and 120m backing','600x240m N3 patches: west21/21 east15/21 north18/21 overhead21/21','900m thickness at one section, not global minimum','Eight clear route centreline segments, not walkable routes'],'C3_shared_boundary_principle':'C3 removal tests remain inherited evidence only. G4 does not establish an equivalent common public wall between three institutions.'}
(R/'inheritance.json').write_text(json.dumps(inherit,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'files':len(list(R.rglob('*.*'))),'mesh_qa':{k:{'geometries':len(v['geometry']),'nonwatertight':sum(not g['watertight_after_vertex_merge'] for g in v['geometry'])} for k,v in qa.items()}},indent=2))
