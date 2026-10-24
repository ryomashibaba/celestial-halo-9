"""J7-R7 GUI preparation only: preserve R6, select a PUBLIC ROOM target in Edit Mode.
No art adoption; source model remains unchanged; all operations on isolated copy.
"""
import bpy, sys, math
from pathlib import Path
from mathutils import Vector, Euler
args=sys.argv[sys.argv.index("--")+1:]
assert len(args)==2, "source.blend output-prepared.blend"
source,out=map(lambda s:Path(s).resolve(),args)
assert source.exists() and source!=out
bpy.ops.wm.open_mainfile(filepath=str(source))
target=bpy.data.objects.get("04_GRAND_CIVIC_FORUM_ACTUAL_PUBLIC_FLOOR")
assert target and target.type=="MESH", "required R6 target missing"
for ob in bpy.context.selected_objects:ob.select_set(False)
target.select_set(True)
bpy.context.view_layer.objects.active=target
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=="VIEW_3D":
   sp=area.spaces.active
   sp.shading.type="SOLID"
   sp.shading.color_type="MATERIAL"
   sp.shading.light="STUDIO"
   sp.region_3d.view_location=Vector((0,-430,850))
   sp.region_3d.view_distance=3400
   sp.region_3d.view_rotation=Euler((math.radians(70),0,math.radians(24)),"XYZ").to_quaternion()
   sp.clip_end=50000
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
print("GUI_PREPARED_TARGET",target.name,"mode",bpy.context.mode,"model",str(out))
