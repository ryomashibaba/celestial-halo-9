"""Audit GUI-rendered physical mesh edit, and render 9 frames from actual edited BLEND."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index("--")+1:]
assert len(args)==3,"-- before.blend after.blend output_dir"
before,after,out=map(lambda x:Path(x).resolve(),args)
name="SIX_CIVIC_VAULT_SPINES_2"
def load(p):
 bpy.ops.wm.open_mainfile(filepath=str(p))
 t=bpy.data.objects.get(name)
 assert t and t.type=="MESH"
 if t.mode=="EDIT":t.update_from_editmode()
 points=[tuple(round(c,4) for c in v.co) for v in t.data.vertices]
 others={ob.name:tuple(tuple(round(c,4) for c in v.co) for v in ob.data.vertices)
         for ob in bpy.data.objects if ob.type=="MESH" and ob.name!=name}
 return points,others,len(others)+1
b,orig,n=load(before);a,other,n2=load(after)
assert n==n2 and orig==other,"GUI modified unrelated city objects"
assert len(b)==len(a)>8
moved=[(i,p,q) for i,(p,q) in enumerate(zip(b,a)) if any(abs(p[d]-q[d])>.001 for d in range(3))]
assert 2<=len(moved)<len(a),("crest selection failed",len(moved),len(a))
for i,p,q in moved:
 assert p[2]>499 and abs(q[2]-p[2]-120)<.05 and abs(q[0]-p[0])<.05 and abs(q[1]-p[1])<.05,("unexpected crest distortion",i,p,q)
assert abs(max(p[2] for p in a)-max(p[2] for p in b)-120)<.05
checks={}
for fn in ("01_ACTUAL_GUI_BEFORE.png","02_ACTUAL_GUI_AFTER.png"):
 p=out/fn
 assert p.exists() and p.stat().st_size>12000,fn
 checks[fn]={"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
assert checks["01_ACTUAL_GUI_BEFORE.png"]["sha256"]!=checks["02_ACTUAL_GUI_AFTER.png"]["sha256"]
# Render final edited scene using same 9 camera viewpoints as R8 A+B.
bpy.ops.wm.open_mainfile(filepath=str(after))
if bpy.context.object and bpy.context.object.mode=="EDIT":bpy.ops.object.mode_set(mode="OBJECT")
sc=bpy.context.scene
sc.render.engine="BLENDER_WORKBENCH";sc.render.resolution_x=1200;sc.render.resolution_y=840
sc.render.resolution_percentage=100;sc.render.image_settings.file_format="PNG"
sc.display.shading.light="STUDIO";sc.display.shading.color_type="MATERIAL"
sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=True
sc.display.shading.cavity_type="BOTH"
focus=(0,0,225)
vv=[
 ("01_FRONT",(0,-1900,880),focus,1900),
 ("02_OBLIQUE",(1500,-1430,1020),focus,1900),
 ("03_SIDE",(1950,0,850),focus,1900),
 ("04_REAR",(0,1950,900),focus,1900),
 ("05_AERIAL",(1300,-1100,2100),focus,1900),
 ("06_GROUND",(0,-1950,90),(0,0,250),1900),
 ("07_REVERSE",(-1450,1450,1150),focus,1900),
 ("08_NAVE",(40,-380,170),(0,110,280),800),
 ("09_CITY_STREET",(540,50,195),(0,100,260),860)]
images=[]
for fn,eye,aim,scale in vv:
 camd=bpy.data.cameras.new(fn);cam=bpy.data.objects.new(fn,camd)
 bpy.context.collection.objects.link(cam);cam.location=Vector(eye)
 cam.rotation_euler=(Vector(aim)-cam.location).to_track_quat("-Z","Y").to_euler()
 camd.type="ORTHO";camd.ortho_scale=scale;camd.clip_end=35000
 sc.camera=cam;path=out/("RENDER_"+fn+".png");sc.render.filepath=str(path)
 bpy.ops.render.render(write_still=True)
 assert path.exists() and path.stat().st_size>10000,fn
 images.append({"frame":fn,"bytes":path.stat().st_size})
glb=out/"J7R8_GUI_RESCULPTED_ACTUAL.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(glb))
reimport=len([o for o in bpy.data.objects if o.type=="MESH"])
assert reimport>=n,("lost geo",n,reimport)
e={"schema":"halo9.j7r8.actual_GUI_crest_edit.v1",
   "blender":bpy.app.version_string,"method":"true Blender X11 GUI keyboard Edit Mode",
   "target":name,"changed_vertices":len(moved),"source_vertices":len(b),
   "change":"GUI G Z 120m only to selected high roof crest vertices, anchored bottom unchanged",
   "before_crest_z_m":max(p[2] for p in b),"after_crest_z_m":max(p[2] for p in a),
   "unrelated_meshes_unchanged":True,"mesh_count":n,"GLB_reimport":reimport,
   "screenshots":checks,"nine_blender_renders":images,"glb_bytes":glb.stat().st_size,
   "visual_art_adoption":"NO","minecraft_construction":"HOLD",
   "user_local_machine_access":"NONE"}
(out/"J7R8_REAL_GUI_EDIT_EVIDENCE.json").write_text(json.dumps(e,indent=2),encoding="utf8")
print("J7R8_ACTUAL_GUI_EDIT_PASS",json.dumps({"edited_vertices":len(moved),"scenes":reimport,"rendered_views":len(images)}))
