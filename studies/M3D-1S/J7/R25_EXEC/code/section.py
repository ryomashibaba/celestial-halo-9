"""Finite actual triangle/plane intersection, no inferred solid or invented caps."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
out={'plane_native_x_m':-430,'window_yz_m':[550,1050,500,850],'solid_volume_certified':False}
for state,path in [('before','C55A_BEFORE.blend'),('after','C55A_R25_LOCAL_EDIT.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/'models'/path));segments=[]
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.hide_render:continue
  o.data.calc_loop_triangles()
  for t in o.data.loop_triangles:
   ps=[o.matrix_world@o.data.vertices[i].co for i in t.vertices]
   if min(p.x for p in ps)>-430 or max(p.x for p in ps)<-430:continue
   pts=[]
   for a,b in zip(ps,ps[1:]+ps[:1]):
    if (a.x+430)*(b.x+430)<0:pts.append(a+(b-a)*((-430-a.x)/(b.x-a.x)))
   if len(pts)!=2:continue
   if any(max(p[i] for p in pts)<lo or min(p[i] for p in pts)>hi for i,lo,hi in [(1,550,1050),(2,500,850)]):continue
   segments.append({'object':o.name,'yz':[[p.y,p.z] for p in pts]})
 out[state]=segments
(R/'qa/ACTUAL_SECTION.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print('SECTION_DONE',flush=True)
