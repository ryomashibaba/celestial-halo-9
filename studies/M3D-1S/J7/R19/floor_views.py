"""Replace floating interior cameras with actual floor-ray-verified city viewpoints.
Geometry unchanged. Prior camera failures are preserved as evidence.
"""
import bpy,sys,json,shutil,hashlib
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));import atelier as a
source=R/'final/R19_LIVING_HORIZON.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));a.bind();scene=bpy.context.scene
before=hashlib.sha256(source.read_bytes()).hexdigest()
repeat=(R/'qa/FLOOR_VERIFIED_CAMERAS.json').exists()
old=R/('qa/OCCLUDED_FLOOR_CAMERAS' if repeat else 'qa/INITIAL_FLOATING_CAMERAS');old.mkdir(exist_ok=True)
if repeat:shutil.copy2(R/'qa/FLOOR_VERIFIED_CAMERAS.json',old/'PRIOR_FLOOR_CAMERAS.json')
record={'source_before_camera_repair_sha256':before,'geometry_changed':False,'views':{}}
for name,xy,top,target in [
 ('08_LOW',(600,-600),850,(1500,450,2100)),
 ('09_MID',(-600,-65),1300,(-1700,600,2200)),
 ('10_HIGH',(1570,480),2600,(-650,1540,3500)),
]:
 cam=bpy.data.objects[name];prior=list(cam.location);hit,point,normal,idx,obj,matrix=scene.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector((*xy,top)),Vector((0,0,-1)),distance=1500)
 assert hit and normal.z>.95,(name,hit,normal,obj.name if obj else None)
 cam.location=point+Vector((0,0,1.7));cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 record['views'][name]={'prior_camera_m':prior,'floor_object':obj.name,'floor_m':list(point),'eye_m':list(cam.location),'eye_above_floor_m':cam.location.z-point.z,'target_m':list(target)}
 previous=R/'final'/(name+'.png')
 if previous.exists():shutil.copy2(previous,old/previous.name)
a.save(R/'final','R19_LIVING_HORIZON')
a.S.render.threads=3
a.render(R/'final',['09_MID'] if '--mid-only' in sys.argv else (['08_LOW','09_MID'] if repeat else ['08_LOW','09_MID','10_HIGH']))
(R/'qa/FLOOR_VERIFIED_CAMERAS.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print('VERIFIED_FLOOR_VIEWS',json.dumps(record,indent=2),flush=True)
