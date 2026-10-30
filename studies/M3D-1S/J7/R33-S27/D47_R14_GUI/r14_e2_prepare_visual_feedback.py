"""R14 E2: image-motivated adjacent-transition selection in *genuine E1* BLEND.
The six R14 E1 saved views show a sudden square step in front, side, oblique,
rear and low public eye. Refine only the surroundings of that exact protrusion
through REAL Blender GUI. This is a sculpting-method study, no city admission.
"""
import bpy,bmesh,zipfile,hashlib,json,sys
from pathlib import Path
zpath=Path(sys.argv[-2]).resolve();p=Path(sys.argv[-1]).resolve();p.mkdir(exist_ok=True,parents=True)
assert zpath.is_file()
with zipfile.ZipFile(zpath) as z:
    b=z.read("R14_E1_ACTUAL_LOCAL_SCULPT.blend")
expected="639c5834fe5b149196a02c5f6333203a0421b10503725691fc4b57f0e4524195"
assert hashlib.sha256(b).hexdigest()==expected
orig=p/"R14_E1_READONLY_ORIGINAL.blend";orig.write_bytes(b)
bpy.ops.wm.open_mainfile(filepath=str(orig))
o=bpy.data.objects["R11_EDIT_ONLY_UNAPPROVED_STUDY_SURFACE"]
assert o.data.shape_keys is not None
o.active_shape_key_index=1
o.data.shape_keys.key_blocks["R11_ARTIST_REVERSIBLE_LAYER"].value=1
basis=[(v.index,v.co.x,v.co.z) for v in o.data.vertices]
# Existing 234-vertex protrusion = x<-45 & 275<z<560, Y+120.
# New E2 transition should NOT touch any of those original vertices.
def core(x,z):return x<-45 and 275<z<560
def transition(x,z):
    if core(x,z):return False
    x_near=(-125<x<25 and 210<z<620)
    z_near=(x<-45 and (210<z<=275 or 560<=z<620))
    return x_near or z_near
zone=[i for i,x,z in basis if transition(x,z)]
core_ids=[i for i,x,z in basis if core(x,z)]
assert len(core_ids)==234,(len(core_ids),len(zone))
assert 65<len(zone)<600,len(zone)
assert not set(zone).intersection(core_ids)
if bpy.context.object and bpy.context.object.mode!="OBJECT":
    bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.object.select_all(action="DESELECT")
o.select_set(True);bpy.context.view_layer.objects.active=o
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_mode(type="VERT")
bpy.ops.mesh.select_all(action="DESELECT")
bm=bmesh.from_edit_mesh(o.data);bm.verts.ensure_lookup_table()
ids=set(zone)
for v in bm.verts:v.select_set(v.index in ids)
bm.select_flush_mode()
bmesh.update_edit_mesh(o.data,loop_triangles=False,destructive=False)
actual={v.index for v in bm.verts if v.select}
assert actual==ids,(len(actual),len(ids))
sc=bpy.context.scene
sc["R14_E2_REASON"]="actual six-view image showed abrupt rectangular extrusion edges"
sc["R14_E2_CORE_FROZEN"]=True
sc["R14_E2_GUI_ART_SCULPT_ALLOWED"]=True
sc["R14_ART_ADOPTED"]=False
sc["R14_MINECRAFT_WRITE"]=False
out=p/"R14_E2_PREPARED_BOUNDARY_TRANSITION.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(out))
record={
  "E1_real_native_source_sha256":expected,
  "E2_prepared_native_blend_sha256":hashlib.sha256(out.read_bytes()).hexdigest(),
  "initial_core_vertices_frozen":core_ids,
  "boundary_transition_vertices":zone,
  "core_selected":False,
  "why_from_actual_images":"front/rear show square extrusion; side and oblique stepped profile; softening neighboring mesh rather than global re-position",
  "edit_expected":"local transition vertices Y+60, core remains Y+120",
  "not_city_design":True,"art_adopted":False,"minecraft_write":False}
(p/"R14_E2_FEEDBACK_DIRECTED_EDIT_PLAN.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf8")
print("R14_E2_PREPARED_BOUNDARY_GUI",len(zone),"CORE_FIXED",len(core_ids))
