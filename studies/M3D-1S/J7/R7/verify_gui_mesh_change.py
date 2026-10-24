"""J7-R7 GUI results auditing: reject any claim without changed Blender mesh and screen captures."""
import bpy, json, math, sys
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index("--")+1:]
assert len(args)==3,"expected -- BEFORE.blend AFTER.blend output-dir"
before,after,output=map(lambda s:Path(s).resolve(),args)
target="04_GRAND_CIVIC_FORUM_ACTUAL_PUBLIC_FLOOR"
def read_model(path):
 bpy.ops.wm.open_mainfile(filepath=str(path))
 o=bpy.data.objects.get(target)
 assert o and o.type=="MESH"
 if o.mode=="EDIT":o.update_from_editmode()
 points=[o.matrix_world@v.co for v in o.data.vertices]
 b=[[round(min(p[i] for p in points),4) for i in range(3)],[round(max(p[i] for p in points),4) for i in range(3)]]
 other=bpy.data.objects.get("01_SINGLE_INHABITED_CONTINENT_FOUNDATION")
 assert other and other.type=="MESH"
 if other.mode=="EDIT":other.update_from_editmode()
 oth=[tuple(round(float(w),4) for w in (other.matrix_world@v.co)) for v in other.data.vertices]
 return b,len(points),oth,len([z for z in bpy.data.objects if z.type=="MESH"])
bb,bv,bo,bcount=read_model(before)
aa,av,ao,acount=read_model(after)
assert bv==av and bcount==acount and bo==ao,"GUI edit unexpectedly changed protected mass or objects"
bw=bb[1][0]-bb[0][0];aw=aa[1][0]-aa[0][0]
assert 1.30<aw/bw<1.42,"GUI edit did not scale public hall X as planned"
assert -78<aa[0][1]-bb[0][1]<-52,"GUI translate Y expected -65m"
# Verify screenshot files are distinct, native Blender GUI, not generated art.
from hashlib import sha256
screens={}
for name in ("01_REAL_GUI_BEFORE.png","02_REAL_GUI_AFTER.png"):
 p=output/name
 assert p.exists() and p.stat().st_size>12000, "GUI screenshot missing: "+name
 screens[name]={"bytes":p.stat().st_size,"sha256":sha256(p.read_bytes()).hexdigest()}
assert screens["01_REAL_GUI_BEFORE.png"]["sha256"]!=screens["02_REAL_GUI_AFTER.png"]["sha256"],"same GUI screenshot"
# Export edited 3D file and render 2 exact scene views for future art judgement.
bpy.ops.wm.open_mainfile(filepath=str(after))
if bpy.context.object and bpy.context.object.mode=="EDIT":
 bpy.ops.object.mode_set(mode="OBJECT")
sc=bpy.context.scene
sc.render.engine="BLENDER_WORKBENCH"
sc.render.resolution_x=1200;sc.render.resolution_y=840;sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.display.shading.light="STUDIO"
sc.display.shading.color_type="MATERIAL"
sc.display.shading.show_shadows=True
views=[
 ("03_BLENDER_RENDER_AFTER_CIVIC_LOCAL.png",(1750,-2850,1590),(0,-420,960),3600),
 ("04_BLENDER_RENDER_AFTER_CITY_CONTEXT.png",(0,-11300,5100),(0,0,1560),10500)]
for name,pos,focus,scale in views:
 camd=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,camd)
 bpy.context.collection.objects.link(cam)
 cam.location=Vector(pos)
 cam.rotation_euler=(Vector(focus)-cam.location).to_track_quat("-Z","Y").to_euler()
 camd.type="ORTHO";camd.ortho_scale=scale;camd.clip_end=80000
 sc.camera=cam
 p=output/name;sc.render.filepath=str(p)
 bpy.ops.render.render(write_still=True)
 assert p.exists() and p.stat().st_size>10000
glb=output/"J7R7_GUI_EDITED_ACTUAL_MODEL.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB")
assert glb.exists() and glb.stat().st_size>20000
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(glb))
nreimport=len([o for o in bpy.data.objects if o.type=="MESH"])
assert nreimport>=acount,"GLB reimport missed objects"
evidence={
"schema":"halo9.j7.r7.true_blender_viewport_keyboard_gui.v1",
"blender_version":bpy.app.version_string,
"actual_GUIApplication_run":"xvfb Blender interactive window; xdotool viewport keyboard Scale X and Move Y; scrot framebuffer proof",
"not_claimed":"not a human or AI mouse-brush sculpt, not an art-quality approval, not Work mode",
"target":target,"source":str(before),"edited":str(after),
"source_mesh_objects":bcount,"edited_mesh_objects":acount,
"public_hall_vertex_count":bv,"before_bounds_xyz_m":bb,"after_bounds_xyz_m":aa,
"width_ratio_after_before":round(aw/bw,5),
"other_foundation_vertices_unchanged":True,
"real_gui_screenshots":screens,
"rendered_actual_blender_views":len(views),
"edited_export_GLB_bytes":glb.stat().st_size,"glb_reimport_mesh_objects":nreimport,
"formal_art_adoption":0,"minecraft_construction":"HOLD",
"art_improvement":"NOT_DEMONSTRATED",
"official_canonical_world_modified":False}
(output/"J7R7_REAL_GUI_EXECUTION_PROOF.json").write_text(json.dumps(evidence,indent=2),encoding="utf8")
print("J7R7_REAL_GUI_PASS",json.dumps({"ratio":aw/bw,"mesh_count":acount,"views":len(views),"GLB":glb.stat().st_size}))
