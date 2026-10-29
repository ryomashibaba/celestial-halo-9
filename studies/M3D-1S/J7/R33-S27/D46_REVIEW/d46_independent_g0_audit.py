"""D46 independent native GLB structural review. Not an ART approval.
Usage: python d46_independent_g0_audit.py path/to/D46_BASE.glb path/to/D46_BASE_MANIFEST.json
Dependencies: trimesh 4.x, numpy, scipy.
Read-only; never import authoring code. Correct glTF Y-up coordinate convention.
"""
import numpy as np, trimesh, json, sys, hashlib
from pathlib import Path
glb=Path(sys.argv[1]); manifest=Path(sys.argv[2])
scene=trimesh.load(glb,force="scene")
by_name={}
for name in scene.graph.nodes_geometry:
    transform, geometry_id=scene.graph.get(name)
    assert name not in by_name,("duplicate",name)
    mesh=scene.geometry[geometry_id].copy()
    mesh.apply_transform(transform)
    by_name[name]=mesh
assert len(by_name)>100
classify=lambda pattern: [m.copy() for n,m in by_name.items() if pattern in n]
mesh_health={}
for kind in ("CITY_GROUND","INNER_CIVIC_SPACE","INHABITED_MASS","UPPER_HOUSE"):
    subset=classify(kind)
    for mesh in subset: mesh.merge_vertices(digits_vertex=4)
    mesh_health[kind]={"meshes":len(subset),"watertight_after_weld":sum(m.is_watertight for m in subset),
        "winding_consistent_after_weld":sum(m.is_winding_consistent for m in subset)}
data=json.loads(manifest.read_text(encoding="utf-8"))
air=[]
for v in data["void_contract"]:
    # Stored design reserve is Blender (X,Y,Z), GLB triangles are glTF (X,Z,-Y).
    x,y,z=v["center"];rx,ry,rz=v["radii"]
    center=np.array([x,z,-y],float);radii=np.array([rx,rz,ry],float)
    offending=[]
    for name,mesh in by_name.items():
        if name.startswith(("W0_","H1::","H2::","H3::","H4::","H5::","H6::","SB")):continue
        pts=np.concatenate((mesh.vertices,
            trimesh.sample.sample_surface(mesh,min(50,max(10,2*len(mesh.faces))),seed=460)[0]))
        hits=int(np.count_nonzero(np.sum(((pts-center)/radii)**2,axis=1)<1))
        if hits:offending.append({"object":name,"intruding_surface_samples":hits,
                                 "tested_surface_samples":len(pts)})
    air.append({"name":v["name"],"intruding_meshes":len(offending),
                "examples":sorted(offending,key=lambda m:-m["intruding_surface_samples"])[:12]})
result={"sha256_glb":hashlib.sha256(glb.read_bytes()).hexdigest(),
        "actual_mesh_nodes":len(by_name),
        "total_triangles":sum(len(m.faces) for m in by_name.values()),
        "studied_city_ground_floors":len(classify("CITY_GROUND")),
        "actual_public_floors":len(classify("ACTUAL_PUBLIC_FLOOR")),
        "vertical_lift_solid_nodes":len(classify("VERTICAL_LIFT")),
        "horizontal_access_solid_nodes":len(classify("HORIZONTAL_ACCESS")),
        "health_after_explicit_gltf_vertex_weld":mesh_health,
        "reserved_air_surface_sample_intrusion":air,
        "notes":["An air Empty is not a real Boolean cavity.","Surface intersection with reserved air includes possibly intentional public floors; it is not automatically a failure, but no clearance contract is implemented.","Civic routes and structural support are NOT VERIFIED.","Coordinates are design-only, not official."],
        "art":"REJECT AFTER VISUAL EXAMINATION"}
print(json.dumps(result,indent=2,ensure_ascii=False))
