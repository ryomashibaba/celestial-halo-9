"""Read exact G6 final .blend, render only three low-resolution review images.
Never save or export the G6 scene. No initial_comparison inputs.
"""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;S=R.parent/'C2-G6'
source=S/'A.blend';bpy.ops.wm.open_mainfile(filepath=str(source))
sc=bpy.context.scene;cam=sc.camera
sc.render.resolution_x=960;sc.render.resolution_y=720;sc.render.resolution_percentage=100
sc.cycles.samples=12;sc.render.image_settings.file_format='JPEG';sc.render.image_settings.quality=84
specs=json.loads((S/'A_metrics.json').read_text())['cameras']
used={}
for label,key in [('oblique','05_oblique'),('side','07_side'),('back','08_back')]:
 s=specs[key];cam.location=s['eye'];cam.rotation_euler=(Vector(s['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=s['ortho']
 sc.render.filepath=str(R/('g6_'+label+'.jpg'));bpy.ops.render.render(write_still=True);used[label]=s
pts=[o.matrix_world@Vector(p) for o in sc.objects if o.type=='MESH' and o.get('role')!='context' for p in o.bound_box]
mn=[min(p[i] for p in pts) for i in range(3)];mx=[max(p[i] for p in pts) for i in range(3)]
(R/'g6_review_source.json').write_text(json.dumps({'source':'studies/C2-G6/A.blend','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'central_glb_sha256':hashlib.sha256((S/'A_CENTRAL.glb').read_bytes()).hexdigest(),'initial_comparison_used':False,'G6_model_or_high_resolution_images_rebuilt':False,'loaded_central_dimensions_m':[mx[i]-mn[i] for i in range(3)],'views':used,'render':{'resolution':[960,720],'samples':12,'format':'JPEG','quality':84}},indent=2),encoding='utf-8')
print('G6 FINAL REVIEW COMPLETE',flush=True)
