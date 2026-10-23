"""Camera-only correction: geometry/lighting unchanged; avoid near-plane terrain clipping."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;k=sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.open_mainfile(filepath=str(R/(k+'.blend')))
p=R/(k+'_metrics.json');data=json.loads(p.read_text());s={'eye':[0,9000,4500],'target':[0,0,1100],'ortho':6800};data['cameras']['08_back']=s
data['camera_correction']='Back camera moved outside synthetic mountain volume; geometry unchanged.'
sc=bpy.context.scene;cam=sc.camera;cam.location=s['eye'];cam.rotation_euler=(Vector(s['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=s['ortho']
sc.render.filepath=str(R/'renders'/k/'08_back.png');bpy.ops.render.render(write_still=True)
p.write_text(json.dumps(data,indent=2),encoding='utf-8');bpy.ops.wm.save_as_mainfile(filepath=str(R/(k+'.blend')),compress=True)
