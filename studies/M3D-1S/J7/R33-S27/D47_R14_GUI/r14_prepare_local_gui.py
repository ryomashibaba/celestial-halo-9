"""R14 E0: prepare a localized selection inside SAVED genuine R11 native BLEND.
DO NOT rebuild massing; do not modify canonical central city or R13 reject.
This is an editing-control study, not a future city proposal.
"""
import bpy,bmesh,json,hashlib,zipfile,sys
from pathlib import Path
from mathutils import Vector
zippath=Path(sys.argv[-2]).resolve()
out=Path(sys.argv[-1]).resolve();out.mkdir(exist_ok=True,parents=True)
assert zippath.is_file()
with zipfile.ZipFile(zippath) as z:
    raw=z.read("R11_OPEN_IN_BLENDER_VISUAL_SCULPT_STUDIO.blend")
expected="c3c23d5ceedf9b922d0c62ca8ed7550079c243847dc5376a2444aee8b243ec66"
assert hashlib.sha256(raw).hexdigest()==expected
source=out/"R11_ORIGINAL_READONLY.blend";source.write_bytes(raw)
bpy.ops.wm.open_mainfile(filepath=str(source))
sc=bpy.context.scene
o=bpy.data.objects["R11_EDIT_ONLY_UNAPPROVED_STUDY_SURFACE"]
assert o.data.shape_keys is not None
key=o.data.shape_keys.key_blocks["R11_ARTIST_REVERSIBLE_LAYER"]
key.value=1.0
o.active_shape_key_index=1
# Define first observed visual intervention (NOT automatically a beautiful city).
# A local patch in upper-left and deep in the Y axis, producing a real 3D fold.
zone=[v.index for v in o.data.vertices if v.co.x < -45 and 275 < v.co.z < 560]
assert 100<len(zone)<len(o.data.vertices)*.55,len(zone)
if bpy.context.object and bpy.context.object.mode!="OBJECT":
    bpy.ops.object.mode_set(mode="OBJECT")
bpy.ops.object.select_all(action="DESELECT")
o.select_set(True);bpy.context.view_layer.objects.active=o
for vert in o.data.vertices:vert.select=False
bpy.ops.object.mode_set(mode="EDIT")
# Selection in the OBJECT-mode mesh vertex flags is not reliable after
# Blender enters Edit Mode. Set and verify it in the actual edit BMesh.
bpy.ops.mesh.select_mode(type="VERT")
bpy.ops.mesh.select_all(action="DESELECT")
bm=bmesh.from_edit_mesh(o.data)
bm.verts.ensure_lookup_table()
selected_zone=set(zone)
for v in bm.verts:
    v.select_set(v.index in selected_zone)
bm.select_flush_mode()
bmesh.update_edit_mesh(o.data,loop_triangles=False,destructive=False)
selected_live=[v.index for v in bm.verts if v.select]
assert set(selected_live)==selected_zone,(len(selected_live),len(zone))
assert 100<len(selected_live)<len(o.data.vertices)*.55
# Do not use selection-all in screenshot-driven GUI; BMesh selective proof.
for scn in bpy.data.screens:
    for area in scn.areas:
        if area.type=="VIEW_3D":
            space=area.spaces.active
            space.shading.type="SOLID"
            space.shading.color_type="MATERIAL"
            space.region_3d.view_location=Vector((0,0,320))
            space.region_3d.view_distance=1110
            space.clip_end=30000
sc["R14_EXPERIMENT"]="multi-view native GUI local shape key intervention"
sc["R14_NOT_ART_PROPOSAL"]=True
sc["R14_ART_ADOPTED"]=False
sc["R14_OFFICIAL_MASTER_COMPLETE"]=False
sc["R14_MINECRAFT_WRITE"]=False
sc["R14_SELECT_ZONE"]="LEFT_UPPER_ONLY"
sc["R14_GUI_SCULPT_REVISIONS"]=0
path=out/"R14_E0_NATIVE_PRESELECTED.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(path))
manifest={
    "source_R11_blend_SHA256":expected,
    "prepared_blend_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
    "model":"real saved R11 neutral surface; not new city",
    "mesh_count":len([x for x in bpy.data.objects if x.type=="MESH"]),
    "selected_indices":zone,
    "selected_vertex_count":len(zone),
    "total_vertices":len(o.data.vertices),
    "selected_part":"x<-45 and 275<z<560 local patch",
    "intervention_reason":"prove localized mesh edit instead of full-object translation",
    "source_art":"fixture only, no art evaluation or adoption",
    "sculpt_shape_key":"R11_ARTIST_REVERSIBLE_LAYER",
    "cameras":[s for s in bpy.data.objects.keys() if s[:2] in ("01","02","03","04","05","06")],
    "original_R11_bytes_unchanged":True,
    "official_master":False,"minecraft":False
}
(out/"R14_E0_PROVENANCE.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf8")
print("R14_PREPARE_LOCAL_GUI_ZONE",len(zone),manifest["prepared_blend_sha256"])
