"""D47-R9: visual-evidence-led, SUBTRACTIVE macro sculpt on a COPY of R8 native .blend.

R8 stays ART-REJECTED AND FROZEN. The R9 file is a controlled, non-canonical
destructive *method test* on a rejected specimen, NOT a rescue of R8, not a new
candidate for M247-C and not aesthetic acceptance.
The R8 actual 9-view renders identified stacked repetitive shelves and blocked
03/04/05 internal views. This experiment tests whether vertex-level subtraction
and spatial relocation can materially change those same images.
Human review of resulting real before/after is mandatory before any further work.
"""
from pathlib import Path
import hashlib,json,sys,zipfile,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import bpy
R8=Path("studies/M3D-1S/J7/R33-S27/D47_R8_EVIDENCE/R8_TRUE_BLENDER_SEQUENCED_CITY_G0_ART_UNREVIEWED.zip")
R8_BLEND_HASH="3d33a319fed9ddf7565a80271260e1e90dee521097dcd035bafa31a197d2e824"
out=Path(sys.argv[-1]).resolve();out.mkdir(parents=True,exist_ok=True)
assert R8.is_file()
with zipfile.ZipFile(R8) as f:
    original_bytes=f.read("R8_SEQUENCE_3D_NATIVE_EDITABLE.blend")
sha=hashlib.sha256(original_bytes).hexdigest()
assert sha==R8_BLEND_HASH,(sha,R8_BLEND_HASH)
base=out/"R8_INTACT_BASELINE_READ_ONLY.blend"
base.write_bytes(original_bytes)
bpy.ops.wm.open_mainfile(filepath=str(base))
scene=bpy.context.scene
assert scene.get('formal_art_adopted') is False
assert scene.get('minecraft_construction') is False
names=[
"01_APPROACH_GATE","02_RIFT_THRESHOLD","03_OVERHEAD_REVELATION",
"04_UPPER_CITY_INHABITED","05_ARCHIVE_PUBLIC_INTERIOR",
"06_MACRO_FRONT","07_MACRO_SIDE","08_MACRO_REAR","09_MACRO_AERIAL"]
cameras={n:bpy.data.objects[n] for n in names}
assert all(c.type=="CAMERA" for c in cameras.values())
def pose(c):
    return (tuple(round(a,6) for a in c.location),
      tuple(round(a,6) for a in c.rotation_euler),
      c.data.type,round(c.data.lens,5) if c.data.type=="PERSP"
      else round(c.data.ortho_scale,5))
original_camera={n:pose(o) for n,o in cameras.items()}
objects={o.name:o for o in bpy.data.objects if o.type=="MESH"}
assert len(objects)==178,len(objects)
def hash_mesh(obj):
    h=hashlib.sha256()
    for v in obj.data.vertices:
        h.update(("%0.6f,%0.6f,%0.6f;"%tuple(v.co)).encode())
    return h.hexdigest()
original_hashes={n:hash_mesh(o) for n,o in objects.items()}
def setrender(folder):
    folder.mkdir(exist_ok=True)
    for name in names:
        scene.camera=bpy.data.objects[name]
        scene.render.filepath=str(folder/(name+".png"))
        bpy.ops.render.render(write_still=True)
setrender(out/"E0_R8_NATIVE_MATCHED")

targets={
"01_APPROACH_GATE":(0,570,520),
"02_RIFT_THRESHOLD":(-25,590,790),
"03_OVERHEAD_REVELATION":(-25,515,1250),
"04_UPPER_CITY_INHABITED":(-310,460,700),
"05_ARCHIVE_PUBLIC_INTERIOR":(-500,435,405)}
def occlusions():
    dep=bpy.context.evaluated_depsgraph_get()
    world=[(o,BVHTree.FromObject(o,dep)) for o in bpy.data.objects
           if o.type=="MESH"]
    result={}
    for n,target in targets.items():
        eye=bpy.data.objects[n].location.copy()
        vec=Vector(target)-eye;ln=vec.length;vec.normalize()
        hits=[]
        for o,tree in world:
            loc,norm,index,d=tree.ray_cast(eye,vec,ln)
            if loc is not None:hits.append((round(float(d),3),o.name))
        hits.sort()
        result[n]={"target":list(target),"first_intersections":hits[:8],
                   "clear":len(hits)==0}
    return result
before_hits=occlusions()

# The following hand-selected changes arise from inspecting *actual R8 images*:
# 01/02/06-09: every level had stacked horizontal floors and floating box-lids
# 03: air-route crosses the nominated civic revelation line of sight
# 04/05: high city/interior frames are mostly blocked by massive foregrounds
# This is a destructive proof of ability to sculpt the already-saved mesh,
# not preservation of R8's unapproved city architecture.
removed=[]
for name,obj in list(objects.items()):
    if ("_ROOM" in name and ("FACETED_PIER" in name or "BACK_WALL" in name)):
        # Delete repetitive narrow false-urban fins, not useful true room interiors.
        bpy.data.objects.remove(obj,do_unlink=True)
        removed.append(name)
    elif ("_ROOM" in name and "_ROOM2_" in name):
        # Subtract every third floor-of-room proxy; breaks repetitive shelf towers.
        bpy.data.objects.remove(obj,do_unlink=True)
        removed.append(name)
assert 25 <= len(removed) <= 95,len(removed)
# Sculpt original city terrace polygons rather than generating any new monolith.
actual_edited=[]
for name,obj in objects.items():
    if bpy.data.objects.get(name) is None:continue
    if ("_CIVIC_CITY_FLOOR" in name and name.startswith(("WEST_","EAST_"))):
        for vertex in obj.data.vertices:
            x,y,z=vertex.co
            # Asymmetric reorientation and taper of EXISTING terrain edges:
            # building footprints retain presence; this is no new 3D generator.
            dx=(-1 if name.startswith("WEST") else 1)
            vertex.co.x=x+dx*(75+0.08*y+0.02*z)
            vertex.co.y=y+math.sin((x+z)/240.0)*65
        obj.data.update()
        actual_edited.append(name)
    elif name.startswith("UPPER_REVERSED_COMMONS"):
        # Original upper cluster moved away from an all-central slab framing;
        # this inevitably breaks architectural links, which remain UNVERIFIED.
        for vertex in obj.data.vertices:
            vertex.co.x-=95
            vertex.co.y+=190
            vertex.co.z+=40
        obj.data.update()
        actual_edited.append(name)
    elif name=="SKY_CIVIC_CONNECTOR_WEST_EAST":
        # Direct mesh re-shape, not added decoration: pull link under/south
        # of the formerly BLOCKED third eye-to-city line.
        for vertex in obj.data.vertices:
            vertex.co.y+=230
            vertex.co.z-=210
        obj.data.update()
        actual_edited.append(name)
assert "SKY_CIVIC_CONNECTOR_WEST_EAST" in actual_edited
assert len(actual_edited)>=14,len(actual_edited)
remaining={o.name:o for o in bpy.data.objects if o.type=="MESH"}
assert len(remaining)==len(objects)-len(removed)
assert all(hash_mesh(remaining[n])!=original_hashes[n] for n in actual_edited)
for n in names:assert pose(bpy.data.objects[n])==original_camera[n]
scene["R9_study"]="R9_E1 image-informed destructive macro editing of R8 copy, NONCANONICAL"
scene["R9_rejected_R8_original_hash"]=sha
scene["R9_art_status"]="UNREVIEWED"
scene["R9_morphological_changes_are_diagnostic_only"]=True
scene["R9_abandoned_old_urban_fabric"]=True
scene["R9_valid_city_occupancy"]=False
scene["R9_valid_accessibility"]=False
scene["R9_modification_method"]="opened original saved .blend and edited native vertex coords"
scene["formal_art_adopted"]=False
scene["minecraft_construction"]=False
after_hits=occlusions()
bpy.ops.wm.save_as_mainfile(filepath=str(out/"R9_E1_TRUE_DIRECT_SCULPT_DIAGNOSTIC.blend"))
bpy.ops.export_scene.gltf(filepath=str(out/"R9_E1_TRUE_DIRECT_SCULPT_DIAGNOSTIC.glb"),
     export_format="GLB",export_cameras=False,export_lights=False)
setrender(out/"E1_MACRO_DIRECT_SCULPT")
record={
  "title":"D47 R9 E1 empirical before-vs-after of rejected original, NOT adopted art",
  "original_R8_editable_blend_sha256":sha,
  "original_R8_state":"REJECTED; remains completely immutable in source archive",
  "all_original_camera_poses_same":True,
  "original_mesh_count":len(objects),
  "deleted_repetitive_nonroom_parts_count":len(removed),
  "deleted_list":removed,
  "existing_meshes_with_changed_vertex_coordinates":actual_edited,
  "each_changed_mesh_hash_verifiably_different":True,
  "remaining_mesh_count":len(remaining),
  "before_hits":before_hits,
  "after_hits":after_hits,
  "no_new_geometry_created":True,
  "art_approved":False,
  "city_10km_master_complete":False,
  "full_occupancy_or_transport_validated":False,
  "formal_M247C_adopted":False,
  "minecraft_construction":False,
  "GUI_or_MCP_editing_tested":False
}
(out/"R9_E1_EDIT_PROVENANCE_AND_AUDIT_INPUT.json").write_text(
     json.dumps(record,ensure_ascii=False,indent=2),encoding="utf8")
print("R9_DIRECT_SAVED_NATIVE_MACRO_SCULPT_ART_UNREVIEWED",
      json.dumps({k:record[k] for k in ('original_mesh_count',
          'remaining_mesh_count','deleted_repetitive_nonroom_parts_count',
          'before_hits','after_hits')},ensure_ascii=False))
