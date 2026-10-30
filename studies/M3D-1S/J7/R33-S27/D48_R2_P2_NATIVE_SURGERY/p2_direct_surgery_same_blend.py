"""D48-R2/P2: direct edits on the ACTUAL rejected P1 BLEND, not scene regeneration.
Variant A opens blocked H1 -> H2 public wall with an applied mesh boolean.
Variant B A + removes ONLY the 20 rejected exterior cubes for root-cause view.
All original P1 cameras untouched. Other authored meshes preserved byte-geometry.
Strictly research: rejected design, no adoption, no world write. 
Run: python p2_direct_surgery_same_blend.py SOURCE_P1_ARTIFACT_DIR OUTPUT_DIR
"""
from pathlib import Path
import bpy
from mathutils import Vector
import json, hashlib, sys, shutil

SRC=Path(sys.argv[-2]).resolve()
OUT=Path(sys.argv[-1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
p1=json.loads((SRC/"D48_R2_P1_MANIFEST.json").read_text())
assert p1["stage"]=="D48_R2_P1_INTERIOR_FIRST_REAL_3D"
assert p1["art"]=="AWAIT_ACTUAL_7_VIEW_REVIEW" # legacy, subsequent verdict ART REJECT
assert not p1["formal_adoption"] and not p1["minecraft_construction"]
orig=SRC/p1["files"]["blend"]
assert hashlib.sha256(orig.read_bytes()).hexdigest()==p1["sha256"][orig.name]
for n in p1["files"]["pngs"]:
 assert hashlib.sha256((SRC/n).read_bytes()).hexdigest()==p1["sha256"][n]

VIEWS=p1["camera_names"]
assert len(VIEWS)==7 and "04_REAL_EYE_H1_PUBLIC" in VIEWS
baseline=OUT/"G0_UNMODIFIED_P1_TRUE_SOURCE_IMAGES"
baseline.mkdir(exist_ok=True)
for name in VIEWS:
 shutil.copy2(SRC/(name+".png"),baseline/(name+".png"))

def digest(data):
 return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def mesh_signatures():
 d={}
 for ob in bpy.data.objects:
  if ob.type!="MESH":continue
  d[ob.name]=digest({
   "v":[[round(float(z),6) for z in p.co] for p in ob.data.vertices],
   "f":[list(p.vertices) for p in ob.data.polygons],
   "world":[round(float(z),6) for row in ob.matrix_world for z in row],
   "material":[x.name if x else "" for x in ob.data.materials],
   "id":ob.get("D48_ASSET")})
 return d
def cam_signatures():
 return {ob.name:digest({"world":[round(float(z),8) for row in ob.matrix_world for z in row],
   "lens":round(float(ob.data.lens),8),"near":ob.data.clip_start,"far":ob.data.clip_end})
  for ob in bpy.data.objects if ob.type=="CAMERA"}
def ray_report():
 deps=bpy.context.evaluated_depsgraph_get()
 target={"04_REAL_EYE_H1_PUBLIC":(600,1810,900),
         "01_REAL_EYE_ARRIVAL":(0,-510,110),
         "02_REAL_EYE_FORUM":(0,450,135),
         "03_REAL_EYE_RESEARCH":(0,850,260)}
 out={}
 for c,t in target.items():
  cam=bpy.data.objects[c]
  origin=cam.matrix_world.translation
  d=Vector(t)-origin
  hit,p,n,face,obj,mtx=bpy.context.scene.ray_cast(deps,origin,d.normalized(),distance=d.length)
  out[c]={"target":list(t),"hit":bool(hit),"first_hit":obj.name if hit else None,
    "hit_location":[round(float(z),3) for z in p] if hit else None,
    "camera_eye_z":round(float(origin.z),3)}
 return out
def save_and_render(kind,base_mesh_hash,cameras):
 folder=OUT/kind;folder.mkdir(exist_ok=True)
 scene=bpy.context.scene
 scene["D48_ART"]="ART_REJECT_UNTIL_TRUE_VISUAL_REVIEW"
 scene["D48_CITY_MASTER_COMPLETE"]=False
 scene["D48_FORMAL_ADOPTED"]=False
 scene["D48_MINECRAFT_WRITTEN"]=False
 scene["D48_OFFICIAL_COORDINATES"]=False
 assert cam_signatures()==cameras
 shape=mesh_signatures()
 changed=sorted(k for k in base_mesh_hash if k in shape and base_mesh_hash[k]!=shape[k])
 removed=sorted(set(base_mesh_hash)-set(shape))
 added=sorted(set(shape)-set(base_mesh_hash))
 assert changed==["H1_EAST_EDGE"],changed
 assert added==[],added
 if kind=="G1_H1_OPEN_PORTAL":assert removed==[],removed
 else:
  assert kind=="G2_REJECTED_OUTER_MASS_REMOVED"
  assert len(removed)==20,removed
  assert all(k.startswith(("WEST_FOLDED_","EAST_FOLDED_","PARTIAL_HIGH_CITY_CANOPY_")) for k in removed)
 assert all(base_mesh_hash[k]==shape[k] for k in shape if k!="H1_EAST_EDGE")
 assert bpy.data.objects["H1_EAST_EDGE"].get("P2_PUBLIC_PORTAL_CARVED") is True
 blade=bpy.data.objects["H1_EAST_EDGE"]
 assert len(blade.data.vertices)>8
 assert len([o for o in bpy.data.objects if o.type=="CAMERA"])==7
 files=[]
 native=folder/(kind+"_DIRECTLY_EDITED_NATIVE.blend")
 glb=folder/(kind+"_REAL_EDITED_GEOMETRY.glb")
 bpy.ops.wm.save_as_mainfile(filepath=str(native))
 bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
                            export_cameras=False,export_lights=False)
 for name in VIEWS:
  scene.camera=bpy.data.objects[name]
  path=folder/(name+".png")
  scene.render.filepath=str(path)
  bpy.ops.render.render(write_still=True)
  files.append(path)
 record={
  "kind":kind,
  "upstream_P1_art":"REJECT",
  "source_blend_sha256":p1["sha256"][orig.name],
  "edit_method":"OPEN_REAL_SAVED_BLEND_APPLY_BOOLEAN_AND_DELETE_ORIGINAL_OBJECTS",
  "h1_portal_real_boolean":True,"removed_object_count":len(removed),
  "removed_original_names":removed,"original_changed_geometry":changed,
  "untargeted_original_meshes_unchanged":True,"camera_matrices_unchanged":True,
  "real_eye_height_1_65m_unchanged":True,
  "art":"UNREVIEWED","function":"UNCERTIFIED",
  "formal_adoption":False,"city_master_complete":False,"minecraft_write":False,
  "world_coordinates":"RESEARCH_ONLY_UNVERIFIED",
  "camera_names":VIEWS,"ray_cast_after":ray_report(),
  "files":{"blend":native.name,"glb":glb.name,"images":[p.name for p in files]},
  "sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [native,glb,*files]},
  "mesh_count":len(shape)}
 (folder/"P2_NATIVE_DIRECT_EDIT_MANIFEST.json").write_text(json.dumps(record,indent=2,ensure_ascii=False))
 print("P2_TRUE_ORIGINAL_DIRECT_EDIT",kind,record["mesh_count"],len(removed),flush=True)
 return record
def p1_load():
 bpy.ops.wm.open_mainfile(filepath=str(orig))
 sc=bpy.context.scene
 assert sc["D48_FORMAL_ADOPTED"] is False
 assert sc["D48_MINECRAFT_WRITTEN"] is False
 assert sc["D48_OFFICIAL_COORDINATES"] is False
 assert sc["D48_CITY_MASTER_COMPLETE"] is False
 assert len([ob for ob in bpy.data.objects if ob.type=="MESH"])==p1["mesh_count"]
 return mesh_signatures(),cam_signatures()
def h1_portal():
 # Real existing H1 west-to-east connection, around x=300, y=1645.
 # The P1 H1 east-edge wall had no portal, blocking the public bridge to H2.
 wall=bpy.data.objects["H1_EAST_EDGE"]
 assert wall.type=="MESH" and len(wall.data.vertices)==8
 bpy.ops.mesh.primitive_cube_add(size=1,location=(300,1647,850))
 cutter=bpy.context.object
 cutter.name="TEMP_H1_EAST_ENTRY_CUTTER_NOT_A_REAL_BUILDING"
 cutter.dimensions=(160,370,280)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 mod=wall.modifiers.new("P2_DIRECT_EXISTING_WALL_PUBLIC_DOOR","BOOLEAN")
 mod.operation="DIFFERENCE"
 mod.solver="EXACT"
 mod.object=cutter
 bpy.ops.object.select_all(action="DESELECT")
 wall.select_set(True)
 bpy.context.view_layer.objects.active=wall
 bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.data.objects.remove(cutter,do_unlink=True)
 assert len(wall.data.vertices)>8
 wall["P2_PUBLIC_PORTAL_CARVED"]=True
 wall["P2_NEW_PORTAL_IS_FUNCTION_VERIFIED"]=False
 assert all(ob.name!="TEMP_H1_EAST_ENTRY_CUTTER_NOT_A_REAL_BUILDING" for ob in bpy.data.objects)
def remove_rejected_shells():
 col=bpy.data.collections.get("04_ARCHITECTURAL_ENVELOPE_ONLY_AFTER_INTERIORS")
 assert col
 names=sorted(o.name for o in col.objects if o.type=="MESH")
 assert len(names)==20,names
 assert sum(k.startswith("WEST_FOLDED_") for k in names)==8
 assert sum(k.startswith("EAST_FOLDED_") for k in names)==8
 assert sum(k.startswith("PARTIAL_HIGH_CITY_CANOPY_") for k in names)==4
 for name in names:
  bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 return names
basehash,cams=p1_load()
before_ray=ray_report()
h1_portal()
A=save_and_render("G1_H1_OPEN_PORTAL",basehash,cams)
basehash,cams=p1_load()
assert ray_report()==before_ray, "Original P1 was not faithfully reloaded."
h1_portal()
removed=remove_rejected_shells()
B=save_and_render("G2_REJECTED_OUTER_MASS_REMOVED",basehash,cams)
root={
 "schema":"D48_R2_P2_TRUE_BLENDER_SAME_SOURCE_CAUSAL_VISUAL_REVIEW",
 "source_run_id":41140650010,
 "source_sha":"c298e4028c4696207ca12f93e44079d54cfe264f",
 "source_art":"REJECT",
 "source_blend_sha256":p1["sha256"][orig.name],
 "source_original_images_reused_untouched":7,
 "source_original_eye_cameras_unchanged":True,
 "ray_cast_before":before_ray,
 "variants":[A,B],
 "provenance_gate":"TWO_INDEPENDENT_LOADS_OF_ONE_REJECTED_NATIVE_BLEND",
 "final_art":"UNREVIEWED_PENDING_REAL_IMAGES",
 "formal_adoption":False,"minecraft_construction":False,
 "city_master_complete":False}
(OUT/"P2_SAME_SOURCE_3WAY_AUDIT.json").write_text(json.dumps(root,indent=2,ensure_ascii=False))
print("P2_FINISHED_TWO_REAL_DIRECT_EDIT_COMPARATORS",flush=True)
