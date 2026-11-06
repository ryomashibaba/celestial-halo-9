"""INT21 — one image-selected *actual native mesh composition* study (RESEARCH).

Authored against the real INT20 offscreen full-city E11 aerial screenshot:
the huge forward right egg entirely conceals the intended central public city;
the left egg and northern severed head read as undifferentiated round solids.
Rather than another egg mesh / procedural boxes / windows / holes / micro-brush,
move and cant the THREE EXISTING principal masses to open an off-axis canyon.

This is native Blender OBJECT MATRIX editing through a live MCP GUI session.
It is NOT GUI hand sculpt, NOT detailed urban architecture, NOT ART adoption.
It can fail artistically (expected to be judged from actual fixed E11 renders).
Preserve W0, all 3 E11 matrices, the original BLEND and the old study branches.
No linked groups or bridges are silently declared functionally connected.
"""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Matrix,Vector,Euler

src=Path(bpy.data.filepath)
EXPECTED="e996fab613904dc557638612d4380ba67ef5c6bbd4aa9fb219d9aeaa8f511fb9"
assert src.name=="INT21_SOURCE.blend",src
assert src.is_file() and hashlib.sha256(src.read_bytes()).hexdigest()==EXPECTED
scene=bpy.context.scene
assert scene["CONSTRUCTION"]=="HOLD"
assert scene["FORMAL_ART_ACCEPTED"]==scene["COMPLETED_TARGETS"]==0
assert not bpy.app.background

out=Path("/tmp/halo9-int21")
out.mkdir(parents=True,exist_ok=True)
fixed=("E11_NAVE_HUMAN","E11_H1_HUMAN","E11_URBAN_AERIAL")
w0=("W0_NORTH_FRACTURED_RANGE","W0_WEST_BASALT_ESCARPMENT",
    "W0_GROUND_BASIN","W0_EASTERN_ARTIFICIAL_SEA")
cameras={n:bpy.data.objects[n].matrix_world.copy() for n in fixed}
def sha_mesh(ob):
    h=hashlib.sha256()
    for v in ob.data.vertices:
        h.update((",".join(f"{float(p):.10g}" for p in v.co)+";").encode())
    return h.hexdigest()
w0_before={
    n:{"world_matrix":[[float(v) for v in row] for row in bpy.data.objects[n].matrix_world],
       "vertex_sha":sha_mesh(bpy.data.objects[n])} for n in w0
}

# The following are three *specific* artistic tectonic movements chosen from
# INT20's real picture, not an algorithm generating new architecture:
# left library mass opens outward, huge eastern slab stands back & toward sea,
# the severed upper fragment breaks the oval silhouette at a different height.
# Deltas are research metres in this study's own Blender scene only.
authored=[
    ("INT11_M247C_ALPHA_WEST_ACCRETED_ARCHIVE",
     (-520.0,-140.0,95.0),(-5.0,-25.0,14.0),
     "Western archive opens away from public axis; steep reverse-inclined civic face"),
    ("INT11_M247C_ALPHA_EAST_CIVIC_HIGH_CITY",
     (840.0,260.0,-90.0),(4.0,21.0,-17.0),
     "High-city shell withdraws east, uncovers central diagonal public canyon"),
    ("INT11_M247C_ALPHA_FLOATING_SEVERED_NORTH",
     (170.0,330.0,310.0),(19.0,-11.0,20.0),
     "Severed northern urban crown stands visibly detached at high altitude")
]
changed=[]
for name,shift,angles,design_intent in authored:
    ob=bpy.data.objects.get(name)
    assert ob and ob.type=="MESH" and len(ob.data.vertices)>100,(name,"NOT_TRUE_MEGA_MESH")
    pre=ob.matrix_world.copy()
    vs=ob.data.vertices
    centroid=sum((pre@v.co for v in vs),Vector((0,0,0)))/len(vs)
    R=Euler(tuple(math.radians(a) for a in angles),"XYZ").to_matrix().to_4x4()
    mat=(Matrix.Translation(Vector(shift))@
         Matrix.Translation(centroid)@R@
         Matrix.Translation(-centroid))
    ob.matrix_world=mat@ob.matrix_world
    bpy.context.view_layer.update()
    max_delta=max((ob.matrix_world@v.co-pre@v.co).length for v in vs)
    assert max_delta>150,"NO_MACRO_MOVEMENT"
    # No generated geometry and no preexisting mesh removed.
    changed.append({"name":name,"intent":design_intent,
        "source_mesh_vertices":len(vs),
        "world_centroid_before":[float(c) for c in centroid],
        "delta_m":shift,"tilt_deg_xyz":angles,
        "maximum_world_vertex_movement_m":round(max_delta,3),
        "before_matrix":[[float(c) for c in row] for row in pre],
        "after_matrix":[[float(c) for c in row] for row in ob.matrix_world]})
    print("INT21_EXISTING_M247C_MASS_RECOMPOSED",name,"max_move",round(max_delta,3),flush=True)

for name,mtx in cameras.items():
    q=bpy.data.objects[name].matrix_world
    assert max(abs(q[i][j]-mtx[i][j]) for i in range(4) for j in range(4))<1e-6,"E11_CHANGED"
for name,data in w0_before.items():
    q=bpy.data.objects[name]
    assert sha_mesh(q)==data["vertex_sha"],"W0_MESH_MUTATION"
    assert max(abs(float(q.matrix_world[i][j])-data["world_matrix"][i][j])
        for i in range(4) for j in range(4))<1e-6,"W0_TRANSFORM_MUTATION"
assert scene["CONSTRUCTION"]=="HOLD"
assert scene["FORMAL_ART_ACCEPTED"]==scene["COMPLETED_TARGETS"]==0

scene["INT21_STUDY"]="VISUALLY_AUTHORED_OPEN_CIVIC_CANYON_COMPOSITION"
scene["INT21_INPUT_IMAGE"]="INT20_REAL_MCP_OFFSCREEN_CITY_VIEWPORT.png"
scene["INT21_ART"]="UNREVIEWED_NOT_ADOPTED"
scene["INT21_FUNCTION"]="UNKNOWN__LINKS_NOT_CERTIFIED"
scene["INT21_METHOD"]="MCP_NATIVE_MATRIX_EDIT_THREE_EXISTING_MESHES_NOT_GUI_SCULPT"
scene["INT21_MINECRAFT"]="HOLD"
scene["INT21_WORLD_COORDS"]="RESEARCH_UNREGISTERED"
scene.camera=bpy.data.objects["E11_URBAN_AERIAL"]
bpy.context.view_layer.update()

result=Path("/tmp/halo9-int21/HALO9_INT21_M247C_OPEN_CIVIC_CANYON_RESEARCH.blend")
bpy.ops.wm.save_as_mainfile(filepath=str(result),compress=True)
assert result.is_file() and result.stat().st_size>25000
proof={"status":"NATIVE_COMPOSITION_TECH_PROVISIONAL_ART_UNREVIEWED",
       "source_sha256":EXPECTED,
       "saved_blend_sha256":hashlib.sha256(result.read_bytes()).hexdigest(),
       "new_blend_name":result.name,
       "source_modified":False,"objects_created":0,"objects_deleted":0,
       "actual_world_geometry_composition_transformed":len(changed),
       "authored_macro_movements":changed,
       "W0_before":w0_before,
       "E11_fixed_original":{
           n:[[float(x) for x in row] for row in matrix] for n,matrix in cameras.items()},
       "formal_adopted":0,"complete":0,"minecraft":"HOLD",
       "art":"UNREVIEWED_NOT_ADOPTED","function":"UNVERIFIED",
       "world_alignment":"UNREGISTERED_RESEARCH"}
(out/"INT21_LIVE_MCP_GEOMETRY_EVIDENCE.json").write_text(json.dumps(proof,indent=2))
print("INT21_TRUE_LIVE_MCP_EXISTING_CITY_MACRO_RECOMPOSED_ART_UNREVIEWED",
      proof["saved_blend_sha256"],flush=True)
