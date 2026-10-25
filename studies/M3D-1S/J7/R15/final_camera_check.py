"""Correct the canyon camera to the actual promenade top and independently raycast.
Geometry stays unchanged; this is a documented camera correction, not a form revision.
"""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;F=R/'revision_2'
bpy.ops.wm.open_mainfile(filepath=str(F/'R15_FINAL.blend'));s=bpy.context.scene
c=bpy.data.objects['10_HUMAN_CANYON'];needs_render=(c.location-Vector((-390,-620,63.7))).length>.001;c.location=(-390,-620,63.7)
c.rotation_euler=(Vector((100,280,450))-c.location).to_track_quat('-Z','Y').to_euler()
bpy.context.view_layer.update()
q=json.loads((F/'BUILD_EVIDENCE.json').read_text('utf8'))
for name in ('08_HUMAN_WEST','10_HUMAN_CANYON'):
 c=bpy.data.objects[name];dg=bpy.context.evaluated_depsgraph_get()
 hit,p,n,idx,o,m=s.ray_cast(dg,c.location,Vector((0,0,-1)),distance=20)
 # Descend from above as well: do not accept a camera hidden below a thin floor.
 high_hit,hp,hn,hi,ho,hm=s.ray_cast(dg,c.location+Vector((0,0,10)),Vector((0,0,-1)),distance=30)
 d=(c.location-p).length if hit else None
 valid=bool(hit and abs(d-1.7)<.002 and n.z>.9 and high_hit and (hp-p).length<.002)
 q['human_floor_rays'][name]=dict(camera_xyz_m=list(c.location),hit=hit,object=o.name if hit else None,floor_xyz_m=list(p) if hit else None,distance_m=d,floor_normal=list(n),higher_origin_hit=ho.name if high_hit else None,higher_origin_floor_xyz_m=list(hp) if high_hit else None,higher_origin_matches_floor=bool(high_hit and (hp-p).length<.002),pass_1_7m_2mm=valid)
 assert valid,(name,q['human_floor_rays'][name])
print('INDEPENDENT HUMAN CHECK',q['human_floor_rays'],flush=True)
q['camera_correction']='Canyon camera moved from Y=-650 to -620m, clear of the overlapping Z=64m southern forecourt. Promenade actual top is Z=62m, eye Z=63.7m. Two-origin downward rays exclude the earlier below-slab camera. West paving raised 6cm to avoid coincident faces.'
(F/'BUILD_EVIDENCE.json').write_text(json.dumps(q,indent=2),encoding='utf8')
s.camera=bpy.data.objects['02_OBLIQUE']
bpy.ops.wm.save_as_mainfile(filepath=str(F/'R15_FINAL.blend'),compress=True)
if needs_render:
 s.camera=bpy.data.objects['10_HUMAN_CANYON'];s.render.filepath=str(F/'10_HUMAN_CANYON.png');bpy.ops.render.render(write_still=True)
