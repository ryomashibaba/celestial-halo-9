"""D48 R3 G1 | Actual Blender visual-art revision of saved G2 P2 native source.
NO scene regeneration. Adjust selected existing ROOF MESHES and add reversible
shape-key sculpting; open actual central skylights. Not an adopted art design.
Run python r3_g1_direct_roof_sculpt.py ORIGINAL_P2_ARTIFACT_DIR OUT_DIR.
"""
import bpy,bmesh,hashlib,json,sys,math,shutil
from mathutils import Vector
from pathlib import Path
SRC=Path(sys.argv[-2]).resolve()
OUT=Path(sys.argv[-1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
G="G2_REJECTED_OUTER_MASS_REMOVED"
m=json.loads((SRC/G/"P2_NATIVE_DIRECT_EDIT_MANIFEST.json").read_text())
assert m["kind"]==G and m["removed_object_count"]==20
fn=SRC/G/m["files"]["blend"]
assert hashlib.sha256(fn.read_bytes()).hexdigest()==m["sha256"][fn.name]
bpy.ops.wm.open_mainfile(filepath=str(fn))
scene=bpy.context.scene
assert scene["D48_CITY_MASTER_COMPLETE"] is False
assert scene["D48_FORMAL_ADOPTED"] is False
assert scene["D48_MINECRAFT_WRITTEN"] is False
assert scene["D48_OFFICIAL_COORDINATES"] is False

def fingerprint(o):
 return hashlib.sha256(json.dumps({
  "verts":[[round(float(x),6) for x in v.co] for v in o.data.vertices],
  "faces":[list(poly.vertices) for poly in o.data.polygons],
  "matrix":[round(float(v),6) for row in o.matrix_world for v in row],
  "materials":[mat.name if mat else "" for mat in o.data.materials]
 },sort_keys=True,separators=(",",":")).encode()).hexdigest()

before={o.name:fingerprint(o) for o in bpy.data.objects if o.type=="MESH"}
cams={o.name:(tuple(tuple(float(v) for v in row) for row in o.matrix_world),
                   o.data.lens,o.data.clip_start,o.data.clip_end)
      for o in bpy.data.objects if o.type=="CAMERA"}
ROOFS=[
 ("H1_ROOF",315.,235.,235.,"H1"),
 ("H2_ROOF",340.,280.,295.,"H2"),
 ("RESEARCH_ARCHIVE_WEST_ROOF",175.,118.,140.,"M247-C"),
 ("CULTURAL_ATLAS_EAST_ROOF",185.,125.,170.,"M247-C"),
 ("EXCHANGE_FORUM_WEST_ROOF",145.,140.,135.,"M247-C"),
 ("OPEN_SCIENCE_WALL_EAST_ROOF",146.,111.,165.,"M247-C"),
]
for name,radius_x,radius_y,lift,asset in ROOFS:
 assert name in bpy.data.objects,name
 ob=bpy.data.objects[name]
 assert ob.type=="MESH" and len(ob.data.vertices)==8
 # 1) Apply true skylight carve to existing material roof, NOT a decal.
 cx=sum((ob.matrix_world@v.co).x for v in ob.data.vertices)/8
 cy=sum((ob.matrix_world@v.co).y for v in ob.data.vertices)/8
 cz=sum((ob.matrix_world@v.co).z for v in ob.data.vertices)/8
 bpy.ops.mesh.primitive_cylinder_add(vertices=56,radius=1,depth=1,location=(cx+radius_x*.09,cy-radius_y*.05,cz))
 cutter=bpy.context.object
 cutter.name="R3_TEMP_SKYLIGHT_CUTTER_"+name
 cutter.scale=(radius_x*.65,radius_y*.68,120)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 boolmod=ob.modifiers.new("R3_REAL_SKYLIGHT_OPEN_TO_DAYLIGHT","BOOLEAN")
 boolmod.operation="DIFFERENCE";boolmod.solver="EXACT";boolmod.object=cutter
 bpy.ops.object.select_all(action="DESELECT")
 ob.select_set(True)
 bpy.context.view_layer.objects.active=ob
 bpy.ops.object.modifier_apply(modifier=boolmod.name)
 bpy.data.objects.remove(cutter,do_unlink=True)
 assert len(ob.data.vertices)>8
 # 2) Sculpt genuine existing roof mesh with nonrigid 3D shape key.
 # The perimeter stays physically attached to its original building walls.
 bm=bmesh.new();bm.from_mesh(ob.data)
 bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=5,use_grid_fill=True)
 bm.to_mesh(ob.data);bm.free();ob.data.update()
 basis=ob.shape_key_add(name="Basis",from_mix=False)
 edit=ob.shape_key_add(name="R3_G1_SCULPTED_ART_DIRECTED_ROOF",from_mix=False)
 xs=[v.co.x for v in ob.data.vertices];ys=[v.co.y for v in ob.data.vertices]
 minx,maxx=min(xs),max(xs);miny,maxy=min(ys),max(ys)
 spanx=maxx-minx;spany=maxy-miny
 assert spanx>200 and spany>200
 changes=0
 for i,v in enumerate(ob.data.vertices):
  u=(float(v.co.x)-minx)/spanx
  w=(float(v.co.y)-miny)/spany
  # Roof remains anchored along all four original perimeter walls.
  fade=max(0,math.sin(math.pi*u))*max(0,math.sin(math.pi*w))
  asym=0.67+0.33*math.sin(1.37*math.pi*(u-w)+0.42)**2
  rise=lift*(fade**.74)*asym
  shear=46*fade*math.sin(2*math.pi*w+.55)
  edit.data[i].co=(v.co.x+shear,v.co.y+20*fade*(u-.25),v.co.z+rise)
  if rise>1:changes+=1
 assert changes>=50,(name,changes)
 edit.value=1
 ob["R3_GEOMETRICALLY_CARVED_SKYLIGHT"]=True
 ob["R3_SHAPE_KEY"]="R3_G1_SCULPTED_ART_DIRECTED_ROOF"
 ob["R3_SCULPTED_VERTEX_COUNT"]=changes
 ob["R3_SOURCE_ART_STATUS"]="UNREVIEWED"
# Original 7 saved cameras stay pixel-comparable and unchanged.
for name,data in cams.items():
 o=bpy.data.objects[name]
 assert (tuple(tuple(float(v) for v in row) for row in o.matrix_world),
         o.data.lens,o.data.clip_start,o.data.clip_end)==data
for name,digest in before.items():
 if name in [p[0] for p in ROOFS]:
  assert fingerprint(bpy.data.objects[name])!=digest
 else:
  assert fingerprint(bpy.data.objects[name])==digest,name
assert len([o for o in bpy.data.objects if o.type=="MESH"])==len(before)

scene["D48_ART"]="R3_G1_UNREVIEWED"
scene["D48_FORMAL_ADOPTED"]=False
scene["D48_MINECRAFT_WRITTEN"]=False
scene["D48_CITY_MASTER_COMPLETE"]=False
scene["D48_OFFICIAL_COORDINATES"]=False
# Studio consists of sculpt-ready shape keys with original Basis,
# sculpted edit layer, original camera rig and honest original artifacts.
outblend=OUT/"R3_G1_DIRECTLY_SCULPTED_6_EXISTING_ROOFS.blend"
outglb=OUT/"R3_G1_TRUE_SCULPTED_EDITABLE_SCENE.glb"
scene.camera=bpy.data.objects[m["camera_names"][0]]
bpy.ops.wm.save_as_mainfile(filepath=str(outblend))
bpy.ops.export_scene.gltf(filepath=str(outglb),export_format="GLB",export_cameras=False,export_lights=False)
renders=[]
for name in m["camera_names"]:
 scene.camera=bpy.data.objects[name]
 render=OUT/(name+".png")
 scene.render.filepath=str(render)
 bpy.ops.render.render(write_still=True)
 renders.append(render)
newhash={o.name:fingerprint(o) for o in bpy.data.objects if o.type=="MESH"}
output={
 "schema":"D48_R3_G1_SAVED_G2_NATIVE_DIRECT_NONRIGID_SCULPT",
 "source_blend_sha256":m["sha256"][fn.name],
 "source_P2_source_run":41141480988,
 "art":"UNREVIEWED_PENDING_ACTUAL_IMAGES",
 "formal_adoption":False,"minecraft_write":False,"city_master_complete":False,
 "P1_P2_rejected_urban_form_was_never_adopted":True,
 "sculpted_existing_meshes":[p[0] for p in ROOFS],
 "original_mesh_count":len(before),
 "changed_existing_meshes":sorted(k for k in before if before[k]!=newhash[k]),
 "nontarget_meshes_unchanged":True,
 "original_camera_matrices_unchanged":True,
 "real_boolean_skylights":len(ROOFS),
 "native_editable_shape_keys":len(ROOFS),
 "source_art_basis":"P2 G2 visible interior-city from 7 views, not complete",
 "camera_names":m["camera_names"],
 "file_names":{"blend":outblend.name,"glb":outglb.name,"pngs":[p.name for p in renders]},
 "sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [outblend,outglb,*renders]},
}
assert len(output["changed_existing_meshes"])==len(ROOFS)
(OUT/"R3_G1_NATIVE_SCULPT_AUDIT.json").write_text(json.dumps(output,ensure_ascii=False,indent=2))
print("R3_G1_DIRECT_NONRIGID_EDIT_EXISTING_NATIVE_BLENDER",output["sculpted_existing_meshes"],flush=True)
