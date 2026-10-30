"""R18-E6 G1: VISUALLY DIRECTED direct edit of the original G0 Blender fold.

This file does not make a fresh building or choose a design by itself.
It REQUIRES a separate review JSON grounded in genuine G0 camera renders.
Must be run only after someone has inspected and committed that review.
The existing editable mesh is modified in-place; all other mesh coordinates and
all real Blender camera transforms are invariant. ART remains unapproved.
"""
from pathlib import Path
import sys,json,hashlib,bpy
from mathutils import Vector
if len(sys.argv)<4:
 raise SystemExit("Usage: editor.py DIR_OF_ACTUAL_G0_DIR NEW_OUT_DIR REVIEW_JSON")
base,out,decision=(Path(s).resolve() for s in sys.argv[-3:])
out.mkdir(parents=True,exist_ok=True)
d=json.loads(decision.read_text(encoding="utf8"))
assert d["actual_source_stage"]=="E6_G0_REAL_NATIVE_5_VIEW"
assert d["status"]=="INSPECTED_ACTUAL_5_RENDERINGS"
assert d["art_G0"]=="REJECT"
assert d["target"]=="WEST_INHABITED_FOLD_EDITABLE"
assert d["operation"]=="reshape_original_fold_by_ring_vertex_offsets"
assert isinstance(d["ring_offsets_xz_m"],list) and len(d["ring_offsets_xz_m"])==7
assert isinstance(d["profile_vertex_weight"],list) and len(d["profile_vertex_weight"])==6
assert all(len(r)==2 for r in d["ring_offsets_xz_m"])
assert all(-16<=v<=16 for r in d["ring_offsets_xz_m"] for v in r)
assert all(0<=w<=1 for w in d["profile_vertex_weight"])
assert len(d["observations"])>=3
native=base/"E6_G0_REAL_INHABITED_FISSURE_BEFORE.blend"
m=json.loads((base/"E6_G0_REAL_NATIVE_MANIFEST.json").read_text())
assert native.is_file() and native.stat().st_size>40000
assert d["source_blend_sha256"]==hashlib.sha256(native.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(native))
sc=bpy.context.scene
assert sc["E6_ART_ADOPTED"] is False and sc["E6_MINECRAFT_WRITTEN"] is False
obj=bpy.data.objects[d["target"]]
assert obj.type=="MESH" and len(obj.data.vertices)==42
assert len(obj.data.polygons)==38
assert obj.get("E6_ring_vertices")==6 and obj.get("E6_ring_count")==7
def geometry_hash(o):
 return hashlib.sha256(json.dumps({
  "v":[[round(float(c),6) for c in v.co] for v in o.data.vertices],
  "f":[list(f.vertices) for f in o.data.polygons]
 },sort_keys=True).encode()).hexdigest()
original={o.name:geometry_hash(o) for o in bpy.data.objects if o.type=="MESH"}
def cam_meta(o):
 return (
  tuple(round(float(c),8) for row in o.matrix_world for c in row),
  o.data.type,round(float(o.data.lens),8),
  round(float(o.data.ortho_scale),8),
  round(float(o.data.clip_start),8))
cams={o.name:cam_meta(o) for o in bpy.data.objects if o.type=="CAMERA"}
assert len(cams)==5
before_positions=[tuple(v.co) for v in obj.data.vertices]
changed=[]
for ring in range(7):
 offx,offz=d["ring_offsets_xz_m"][ring]
 for profile in range(6):
  idx=6*ring+profile
  w=d["profile_vertex_weight"][profile]
  dx=float(offx)*float(w);dz=float(offz)*float(w)
  if abs(dx)+abs(dz)<1e-4:continue
  orig=before_positions[idx]
  new=(orig[0]+dx,orig[1],orig[2]+dz)
  obj.data.vertices[idx].co=new
  for kb in obj.data.shape_keys.key_blocks:
   kb.data[idx].co=new
  changed.append({
   "vertex_id":idx,
   "before":[round(float(q),6) for q in orig],
   "after":[round(float(q),6) for q in new]})
assert len(changed)>=12
obj.data.update()
updated={o.name:geometry_hash(o) for o in bpy.data.objects if o.type=="MESH"}
assert set(updated)==set(original)
assert updated[obj.name]!=original[obj.name]
assert all(updated[k]==original[k] for k in updated if k!=obj.name)
assert all(cam_meta(o)==cams[o.name] for o in bpy.data.objects if o.type=="CAMERA")
assert len(obj.data.vertices)==42 and len(obj.data.polygons)==38
assert sc.render.resolution_x==1160 and sc.render.resolution_y==760
sc["E6_G1_EDIT_METHOD"]="actual source BLEND opened; existing fold vertex positions changed"
sc["E6_G1_ART_JUDGEMENT"]="NOT_REVIEWED"
sc.camera=bpy.data.objects["01_HUMAN_ARRIVAL"]
edit=out/"E6_G1_ACTUAL_SAME_BLENDER_REMODELED_FOLD.blend"
glb=out/"E6_G1_ACTUAL_SAME_BLENDER_REMODELED_FOLD.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(edit))
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
                           export_cameras=False,export_lights=False)
for name in cams:
 sc.camera=bpy.data.objects[name]
 sc.render.filepath=str(out/("AFTER_"+name+".png"))
 bpy.ops.render.render(write_still=True)
audit={
 "SOURCE_TECH":"DIRECT_VERTEX_EDIT_CREATED_NOT_YET_INDEPENDENTLY_AUDITED",
 "G0_original_sha256":hashlib.sha256(native.read_bytes()).hexdigest(),
 "G1_edited_sha256":hashlib.sha256(edit.read_bytes()).hexdigest(),
 "GLB_edited_sha256":hashlib.sha256(glb.read_bytes()).hexdigest(),
 "G0_review_decision":d,"change_count":len(changed),
 "exact_same_camera_matrices":True,
 "other_meshes_geometrically_identical":True,
 "target_original_hash":original[obj.name],
 "target_edited_hash":updated[obj.name],
 "all_edited_vertex_deltas":changed,
 "ART":"UNREVIEWED_TRUE_AFTER_VIEWS",
 "FUNCTION":"UNCERTIFIED","FORMAL_ADOPTION":False,"MINECRAFT":False}
(out/"E6_G1_ACTUAL_SAME_SOURCE_EDIT_AUDIT.json").write_text(
 json.dumps(audit,indent=2,ensure_ascii=False),encoding="utf8")
print("E6_G1_REAL_SAME_BLENDER_MAIN_FORM_EDIT_CREATED",len(changed),flush=True)
