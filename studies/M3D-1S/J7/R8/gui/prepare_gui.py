"""Prepare an authentic R8 BLEND geometry-edit viewport. No geometry changes here."""
import bpy,sys,math
from pathlib import Path
from mathutils import Vector,Euler
args=sys.argv[sys.argv.index("--")+1:]
assert len(args)==2, "need -- before.blend prepared.blend"
src,dst=[Path(a).resolve() for a in args]
assert src.exists() and src!=dst
bpy.ops.wm.open_mainfile(filepath=str(src))
target=bpy.data.objects.get("SIX_CIVIC_VAULT_SPINES_2")
assert target and target.type=="MESH","required sculptural vault rib missing"
for o in bpy.context.selected_objects:o.select_set(False)
target.select_set(True);bpy.context.view_layer.objects.active=target
# Edit ONLY crest vertices; retain the grounded base anchored to existing galleries.
n=0
for v in target.data.vertices:
 v.select=v.co.z>499
 n+=bool(v.select)
assert 2<=n<len(target.data.vertices),("unexpected crest vertex subset",n,len(target.data.vertices))
bpy.context.tool_settings.mesh_select_mode=(True,False,False)
for area in [a for screen in bpy.data.screens for a in screen.areas if a.type=="VIEW_3D"]:
 s=area.spaces.active
 s.shading.type="SOLID";s.shading.color_type="MATERIAL"
 s.region_3d.view_location=Vector((0,0,385))
 s.region_3d.view_distance=1350;s.clip_end=35000
 s.region_3d.view_rotation=Euler((math.radians(70),0,math.radians(27)),"XYZ").to_quaternion()
bpy.ops.object.mode_set(mode="EDIT")
dst.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=True)
print("R8_GUI_PREPARED",target.name,"selected_crest",n,"all",len(target.data.vertices))
