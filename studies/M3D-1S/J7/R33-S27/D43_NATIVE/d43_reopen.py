"""Independent new bpy process: validate saved BLEND and GLB identifiers."""
import bpy, json, sys
from pathlib import Path
out=Path(sys.argv[-1])
blend=out/"D43_BASE_EDITABLE.blend"; glb=out/"D43_BASE.glb"
assert blend.is_file() and blend.stat().st_size > 100_000, str(blend)
assert glb.is_file() and glb.stat().st_size > 100_000, str(glb)
bpy.ops.wm.open_mainfile(filepath=str(blend))
native={o.name for o in bpy.data.objects if o.type=='MESH'}
must={"W0 research ground - not canonical","W0 artificial inner sea - placeholder","CITY_MASS A left ascending cliff",
      "CITY_MASS B right dislocated escarpment","CITY_MASS C inhabited back-fold",
      "public forum void 0 - FLOOR","public forum void 1 - FLOOR"}
assert must.issubset(native), must-native
assert len([o for o in bpy.data.objects if o.type=='CAMERA'])==8
assert len(list(out.glob("0?_*.png")))==8
for p in out.glob("0?_*.png"): assert p.stat().st_size>2000, str(p)
basis={name:(len(bpy.data.objects[name].data.vertices),len(bpy.data.objects[name].data.polygons)) for name in must}
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(glb))
actual={o.name for o in bpy.data.objects if o.type=="MESH"}
assert must.issubset(actual), {"missing":sorted(must-actual),"actual":sorted(actual)[:10]}
for n,(v,f) in basis.items():
    o=bpy.data.objects[n]
    assert (len(o.data.vertices),len(o.data.polygons))==(v,f),(n,v,f,len(o.data.vertices),len(o.data.polygons))
report={"status":"NATIVE_MODEL_TECH_BASE_ONLY",
        "blender":bpy.app.version_string,"objects_mesh_native":len(native),
        "objects_mesh_glb":len(actual),"matched_required_names":sorted(must),
        "face_count_preserved":True,"render_count":8,
        "art":"NOT_REVIEWED","route":"NOT_VERIFIED"}
(out/"D43_REOPEN_QA.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("D43_INDEPENDENT_BLENDER_REOPEN_PASS",json.dumps(report))
