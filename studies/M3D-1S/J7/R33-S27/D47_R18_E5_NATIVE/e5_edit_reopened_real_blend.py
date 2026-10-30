"""E5 G1: OPEN saved G0 BLEND; remove actual occluding faces of one existing mesh.
This is a true edit of the previous scene, not a second generator.
G0 visual review: see E5_G0_REAL_FOUR_CAMERA_VISUAL_DECISION_JA.md.
"""
from pathlib import Path
import bpy,bmesh,sys,json,hashlib
OUT=Path(sys.argv[-1]).resolve()
BEFORE=Path(sys.argv[-2]).resolve()
OUT.mkdir(exist_ok=True,parents=True)
source=BEFORE/"E5_G0_NEW_PUBLIC_ROOM_BEFORE_EDIT.blend"
assert source.stat().st_size>40000
bpy.ops.wm.open_mainfile(filepath=str(source))
S=bpy.context.scene
assert S["E5_MINECRAFT_WRITTEN"] is False
target=bpy.data.objects["E5_SOURCE_EDITABLE_MAIN_VEIL"]
assert target.type=="MESH"
assert len(target.data.vertices)==63 and len(target.data.polygons)==48

def snapshot(o):
 return hashlib.sha256(json.dumps({
  "vertices":[[round(float(c),7) for c in v.co] for v in o.data.vertices],
  "faces":[list(f.vertices) for f in o.data.polygons]
 },sort_keys=True).encode()).hexdigest()
mesh_before={o.name:snapshot(o) for o in bpy.data.objects if o.type=="MESH"}
cam_before={o.name:(
 tuple(round(float(q),9) for row in o.matrix_world for q in row),
 o.data.type,round(o.data.lens,9),round(o.data.ortho_scale,9)
 ) for o in bpy.data.objects if o.type=="CAMERA"}
assert len(cam_before)==4
original_positions=[tuple(v.co) for v in target.data.vertices]
original_name=target.name
original_datablock=target.data
bm=bmesh.new()
bm.from_mesh(original_datablock)
bm.verts.ensure_lookup_table()
bm.verts.index_update()
bm.faces.ensure_lookup_table()
removed=[]
for face in list(bm.faces):
 rows=[v.index//9 for v in face.verts]
 cols=[v.index%9 for v in face.verts]
 if min(cols)>=1 and max(cols)<=7 and max(rows)<=4:
  removed.append(face)
assert len(removed)==24,len(removed)
removed_indices=sorted(f.index for f in removed)
bmesh.ops.delete(bm,geom=removed,context="FACES_ONLY")
bm.to_mesh(original_datablock)
bm.free()
original_datablock.update()
assert target.data==original_datablock
assert target.name==original_name
assert len(target.data.vertices)==63
assert len(target.data.polygons)==24
assert len(target.data.shape_keys.key_blocks)==2
assert [tuple(v.co) for v in target.data.vertices]==original_positions
mesh_after={o.name:snapshot(o) for o in bpy.data.objects if o.type=="MESH"}
assert set(mesh_before)==set(mesh_after)
assert mesh_after[target.name]!=mesh_before[target.name]
assert all(mesh_before[k]==mesh_after[k] for k in mesh_before if k!=target.name)
cam_after={o.name:(
 tuple(round(float(q),9) for row in o.matrix_world for q in row),
 o.data.type,round(o.data.lens,9),round(o.data.ortho_scale,9)
 ) for o in bpy.data.objects if o.type=="CAMERA"}
assert cam_after==cam_before
assert S.render.resolution_x==1160 and S.render.resolution_y==760
S["E5_G1_EXACT_METHOD"]="original BLEND opened; 24 original faces deleted on existing mesh"
S["E5_G1_ART_APPROVED"]=False
S["E5_G1_FUNCTION_CERTIFIED"]=False
S.camera=bpy.data.objects["01_HUMAN_ROOM_ARRIVAL"]
new_blend=OUT/"E5_G1_ACTUAL_EDITED_SAME_SOURCE.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(new_blend))
new_glb=OUT/"E5_G1_ACTUAL_EDITED_SAME_SOURCE.glb"
bpy.ops.export_scene.gltf(filepath=str(new_glb),export_format="GLB",
                         export_cameras=False,export_lights=False)
for name in cam_before:
 S.camera=bpy.data.objects[name]
 S.render.filepath=str(OUT/("AFTER_"+name+".png"))
 bpy.ops.render.render(write_still=True)
audit={
 "g0_blend_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
 "g1_blend_sha256":hashlib.sha256(new_blend.read_bytes()).hexdigest(),
 "target":original_name,"faces_before":48,"faces_after":24,
 "deleted_faces":removed_indices,"same_mesh_datablock":True,
 "unchanged_target_vertices":63,
 "other_39_meshes_unchanged":True,
 "camera_matrices_lenses_and_ortho_unchanged":True,
 "source_mesh_hash_before":mesh_before[target.name],
 "source_mesh_hash_after":mesh_after[target.name],
 "total_source_meshes":len(mesh_before),
 "art":"AWAITING_TRUE_AFTER_IMAGE_REVIEW",
 "function":"UNCERTIFIED",
 "canonical_modified":False,"minecraft_write":False}
(OUT/"E5_G1_DIRECT_MESH_EDIT_AUDIT.json").write_text(
 json.dumps(audit,ensure_ascii=False,indent=2),encoding="utf8")
print("E5_G1_REOPENED_REAL_BLEND_EDITED_EXISTING_MESH",json.dumps(audit),flush=True)
