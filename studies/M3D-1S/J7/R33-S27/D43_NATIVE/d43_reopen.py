"""Independent native bpy verification of saved scene and glTF re-import.
Blender glTF triangulates quads and splits vertices at flat normals. Vertex
and face COUNTS therefore must not be compared blindly. Explicit object names,
transformed point-cloud positions, and bounding boxes remain mandatory.
"""
import bpy, json, sys
from pathlib import Path
from mathutils import Vector
out=Path(sys.argv[-1]); blend=out/"D43_BASE_EDITABLE.blend"; glb=out/"D43_BASE.glb"
assert blend.is_file() and blend.stat().st_size>100_000
assert glb.is_file() and glb.stat().st_size>100_000
bpy.ops.wm.open_mainfile(filepath=str(blend))
native={o.name for o in bpy.data.objects if o.type=="MESH"}
required={"W0 research ground - not canonical","W0 artificial inner sea - placeholder",
          "CITY_MASS A left ascending cliff","CITY_MASS B right dislocated escarpment",
          "CITY_MASS C inhabited back-fold","public forum void 0 - FLOOR",
          "public forum void 1 - FLOOR"}
assert required.issubset(native), sorted(required-native)
assert len([o for o in bpy.data.objects if o.type=="CAMERA"])==8
assert len(list(out.glob("0?_*.png")))==8
for p in out.glob("0?_*.png"): assert p.stat().st_size>2000,str(p)
def cloud(obj):
    return [obj.matrix_world @ v.co for v in obj.data.vertices]
native_points={o.name:cloud(o) for o in bpy.data.objects if o.type=="MESH"}
native_faces={o.name:len(o.data.polygons) for o in bpy.data.objects if o.type=="MESH"}
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(glb))
actual={o.name for o in bpy.data.objects if o.type=="MESH"}
# Failing closed: no invented fallback, no silently ignored names.
assert actual==native, {"missing":sorted(native-actual),"extra":sorted(actual-native)}
def max_nn(source,target):
    return max(min((p-q).length for q in target) for p in source)
statistics={}
for name in sorted(native):
    a=native_points[name];b=cloud(bpy.data.objects[name])
    assert len(a)>0 and len(b)>0
    fwd=max_nn(a,b);rev=max_nn(b,a)
    maxerr=max(fwd,rev)
    # float32 precision at city scales: 2cm bound, observed errors recorded
    assert maxerr<=0.02,(name,maxerr,len(a),len(b))
    statistics[name]={"blend_vertices":len(a),"glb_vertices":len(b),
        "blend_polygons":native_faces[name],
        "glb_polygons":len(bpy.data.objects[name].data.polygons),
        "position_error_m":maxerr}
report={"status":"NATIVE_TECH_GEOMETRY_POSITION_ONLY_PASS",
       "blender":bpy.app.version_string,"source_mesh_names":len(native),
       "glb_mesh_names":len(actual),"same_exact_name_set":True,
       "maximum_surface_vertex_error_m":max(v["position_error_m"] for v in statistics.values()),
       "protected_ground_error_m":statistics["W0 research ground - not canonical"]["position_error_m"],
       "protected_sea_error_m":statistics["W0 artificial inner sea - placeholder"]["position_error_m"],
       "triangulation_vertex_split_expected":any(v["blend_vertices"]!=v["glb_vertices"] for v in statistics.values()),
       "mesh_stats":statistics,"render_count":8,
       "face_connectivity_exact":"NOT_CHECKED_GLTF_TRIANGULATES",
       "world_real_route_clearance":"NOT_VERIFIED",
       "art":"REJECT_AFTER_AI_IMAGE_REVIEW"}
(out/"D43_REOPEN_QA.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("D43_INDEPENDENT_BLENDER_REOPEN_PASS",json.dumps({k:v for k,v in report.items() if k!="mesh_stats"}))
