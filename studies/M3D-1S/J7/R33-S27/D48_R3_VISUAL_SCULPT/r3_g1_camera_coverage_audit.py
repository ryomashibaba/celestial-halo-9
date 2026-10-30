"""D48 R3 camera-ray first-hit visual occlusion audit on actual saved native BLEND.
Counts nearest visible MESH hit per camera image grid. Does NOT claim human safety.
Run: python r3_g1_camera_coverage_audit.py R3_G1_DIRECTORY
"""
from pathlib import Path
import json,sys,hashlib,collections,math
import bpy
from mathutils import Vector

ROOT=Path(sys.argv[-1]).resolve()
record=json.loads((ROOT/"R3_G1_NATIVE_SCULPT_AUDIT.json").read_text())
p=ROOT/record["file_names"]["blend"]
assert hashlib.sha256(p.read_bytes()).hexdigest()==record["sha256"][p.name]
bpy.ops.wm.open_mainfile(filepath=str(p))
scene=bpy.context.scene
deps=bpy.context.evaluated_depsgraph_get()
qa={}
nx,ny=35,23
for name in record["camera_names"]:
 camera=bpy.data.objects[name]
 frame=camera.data.view_frame(scene=scene)
 xmin=min(v.x for v in frame);xmax=max(v.x for v in frame)
 ymin=min(v.y for v in frame);ymax=max(v.y for v in frame)
 z=sum(v.z for v in frame)/len(frame)
 loc=camera.matrix_world.translation
 rot=camera.matrix_world.to_quaternion()
 counts=collections.Counter()
 hits={}
 for yi in range(ny):
  yy=ymax-(yi+.5)*(ymax-ymin)/ny
  for xi in range(nx):
   xx=xmin+(xi+.5)*(xmax-xmin)/nx
   direction=rot@Vector((xx,yy,z))
   hit,where,normal,face,ob,_=scene.ray_cast(deps,loc,direction.normalized(),distance=60000)
   which=ob.name if hit else "SKY_NO_GEOMETRY"
   counts[which]+=1
   if hit:
    if which not in hits:hits[which]={"x":round(where.x,2),"y":round(where.y,2),"z":round(where.z,2)}
 total=nx*ny
 top=[{"name":n,"ratio":round(c/total,4),"ray_count":c,"example_hit":hits.get(n)}
       for n,c in counts.most_common(18)]
 qa[name]={"total_rays":total,"top_first_hit_objects":top,
            "mesh_fraction":round(1-counts["SKY_NO_GEOMETRY"]/total,4),
            "camera_world_xyz":[round(float(x),3) for x in loc]}
assert len(qa)==7
data={"schema":"D48_R3_G1_NATIVE_7_VIEW_3D_OCCLUSION","source_blend_sha256":record["sha256"][p.name],
      "ray_count_total":nx*ny*7,"grid":[nx,ny],"art":"UNREVIEWED_VISUAL_SUBJECTIVITY",
      "line_of_sight_only_no_walkability_certified":True,
      "no_changes_to_source_blend":True,"original_sha_still_matches":hashlib.sha256(p.read_bytes()).hexdigest()==record["sha256"][p.name],
      "formal_adoption":False,"minecraft_write":False,"per_camera":qa}
(ROOT/"R3_G1_REAL_CAMERA_COVERAGE.json").write_text(json.dumps(data,ensure_ascii=False,indent=2))
for n in qa:
 print("R3_NATIVE_CAMERA_HIT_SUMMARY",n,[(t["name"],t["ratio"]) for t in qa[n]["top_first_hit_objects"][:6]],flush=True)
