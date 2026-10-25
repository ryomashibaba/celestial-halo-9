"""Find unoccluded interior viewpoints from actual native mesh rays, not exterior.
No geometry changes. Candidate visibility is not walking/volume certification.
"""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;bpy.ops.wm.open_mainfile(filepath=str(R/'revision_2/R17_REVISION_2.blend'));S=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
obs=[o for o in bpy.data.collections['R17_URBAN_CONTINENTS'].objects if o.type=='MESH']
def inside(eye):
 d=Vector((1,.173,.057)).normalized()
 for ob in obs:
  inv=ob.matrix_world.inverted();loc=inv@eye;direction=inv.to_3x3()@d
  h,p,n,i=ob.ray_cast(loc,direction,distance=20000)
  if h and n.dot(direction)>1e-5:return True
 return False
out={};selected={}
for name,z in [('08_INTERIOR_LOW',650),('09_INTERIOR_MID',1550),('10_INTERIOR_HIGH',2650)]:
 candidates=[]
 for x in [-950,-650,-350,-50,250,550]:
  for y in [-650,-150,350,850,1250]:
   eye=Vector((x,y,z))
   if inside(eye):continue
   for angle in range(0,360,30):
    for pitch in [-.15,.15,.40]:
     yaw=math.radians(angle);f=Vector((math.sin(yaw),math.cos(yaw),pitch)).normalized();r=f.cross(Vector((0,0,1))).normalized();u=r.cross(f).normalized()
     hits=[];distances=[]
     for sx,sy in [(0,0),(-.5,0),(.5,0),(0,-.4),(0,.4),(-.4,-.3),(.4,-.3),(-.4,.3),(.4,.3)]:
      direction=(f+r*sx+u*sy).normalized();h,p,n,i,o,m=S.ray_cast(dg,eye,direction,distance=10000)
      distances.append((p-eye).length if h else 10000);hits.append(o.name if h else None)
     if not 700<distances[0]<5000 or min(distances)<200:continue
     distinct=len(set(h for h in hits if h));nh=sum(h is not None for h in hits)
     if nh<6:continue
     score=distinct*800+sum(min(d,3000) for d in distances)/9
     candidates.append(dict(score=score,eye=list(eye),target=list(eye+f*1600),surface_distances_m=distances,visible_objects=hits))
 candidates.sort(key=lambda c:c['score'],reverse=True);out[name]=candidates[:10]
 assert candidates,name+' no actual camera candidate'
 c=candidates[0];selected[name]={'location':c['eye'],'target':c['target'],'lens_mm':23}
 print(name,selected[name],c['score'],flush=True)
(R/'qa/INTERIOR_VISIBILITY_CANDIDATES.json').write_text(json.dumps(out,indent=2),encoding='utf8')
(R/'qa/SELECTED_INTERIOR_CAMERAS.json').write_text(json.dumps(selected,indent=2),encoding='utf8')
