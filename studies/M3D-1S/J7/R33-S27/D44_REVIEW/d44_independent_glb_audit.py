"""Independent read-only D43 vs D44 GLB audit.
Usage: python d44_independent_glb_audit.py D43_BASE.glb D44_EDIT1.glb report.json
Requires trimesh >= 4, numpy, scipy. Real saved GLBs are inputs. NEVER edits.
"""
import json, sys
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial import cKDTree
a_path,b_path,out_path=map(Path,sys.argv[1:4])
def meshes(path):
    scene=trimesh.load(path,force="scene")
    data={}
    for node in scene.graph.nodes_geometry:
        matrix,g=scene.graph.get(node)
        assert node not in data,("DUPLICATE_NODE",node)
        m=scene.geometry[g].copy()
        m.apply_transform(matrix)
        data[node]=m
    return data
a,b=meshes(a_path),meshes(b_path)
assert set(a)==set(b),{"missing":sorted(set(a)-set(b)),"new":sorted(set(b)-set(a))}
protected=[n for n in a if n.startswith(("W0 ","H1 ","H2 ","H3 ","H4 ","H5 ","H6 ","SB"))]
assert len(protected)>=47,len(protected)
for n in protected:
    assert np.array_equal(a[n].vertices,b[n].vertices),("CHANGED_PROTECTED_VERTICES",n)
    assert np.array_equal(a[n].faces,b[n].faces),("CHANGED_PROTECTED_TRIANGLES",n)
changed={}
for n in sorted(a):
    if not n.startswith("CITY_MASS"):continue
    before=a[n];after=b[n]
    prev=before.copy();prev.merge_vertices(digits_vertex=4)
    curr=after.copy();curr.merge_vertices(digits_vertex=4)
    dist=cKDTree(before.vertices).query(after.vertices,k=1)[0]
    changed[n]={"before_triangle_count":len(before.faces),
       "after_triangle_count":len(after.faces),
       "before_connected_components_after_weld":len(prev.split(only_watertight=False)),
       "after_connected_components_after_weld":len(curr.split(only_watertight=False)),
       "before_welded_watertight":bool(prev.is_watertight),
       "after_welded_watertight":bool(curr.is_watertight),
       "world_vertex_displacement_max_m":float(dist.max())}
assert len(changed)==3,len(changed)
assert all(v["world_vertex_displacement_max_m"]>50 for v in changed.values())
result={"status":"INDEPENDENT_GLTF_INSPECTION_ONLY_NOT_ART_PASS",
  "object_name_set_identical":True,"object_count":len(a),
  "protected_w0_h_sb_identical_glb":len(protected),
  "mesh_discussion":"glTF splits vertices at normals/triangles; weld duplicate positions before testing component count",
  "three_mass_meshes":changed,
  "clearance_support_world_geometry":"NOT_VERIFIED",
  "art":"REJECT"}
out_path.parent.mkdir(parents=True,exist_ok=True)
out_path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({k:v for k,v in result.items() if k!="three_mass_meshes"},ensure_ascii=False))
