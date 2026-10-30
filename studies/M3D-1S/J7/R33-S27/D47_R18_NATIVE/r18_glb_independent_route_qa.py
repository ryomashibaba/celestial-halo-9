"""Independent D47-R18 E0 GLB topology audit; not a safety/art certificate.

Requires: numpy, scipy, trimesh.
Run: python r18_glb_independent_route_qa.py R18_E0_LIVED_CIVIC.glb
"""
import argparse
import json
import numpy as np
import trimesh
from pathlib import Path
from scipy.spatial import ConvexHull

FLOORS = {
    "SOUTH_ARRIVAL_TERRACE": 0.0,
    "EXHIBITION_FLOOR_WITH_OBLIQUE_VIEW_EDGE": 2.0,
    "HIGH_RESEARCH_READING_ROOM": 6.0,
    "TRANSIT_OBSERVATION_TRANSFER": 8.2,
}
ROUTE_PREFIX = "CONNECTED_SINGLE_BODY_PUBLIC_WALK"

def components(mesh):
    return len(mesh.split(only_watertight=False))

def actual_mesh(scene, prefix):
    matches=[]
    for node in scene.graph.nodes_geometry:
        transform,name=scene.graph[node]
        if node.startswith(prefix):
            m=scene.geometry[name].copy()
            m.apply_transform(transform)
            matches.append(m)
    assert len(matches)==1,(prefix,len(matches))
    return matches[0]

def welded(mesh):
    m=mesh.copy()
    # GLB may split coincident positions to preserve UV/normal seams.
    # Count spatially connected geometry, then test an intentionally broken mesh.
    m.merge_vertices(merge_tex=True,merge_norm=True,digits_vertex=5)
    return m

def z_up(points):
    # glTF Y-up imported from Blender Z-up
    p=np.asarray(points)
    return np.column_stack((p[:,0],-p[:,2],p[:,1]))

def inside_convex(q,poly,tol=1e-4):
    signs=[]
    for p,n in zip(poly,np.roll(poly,-1,axis=0)):
        c=(n[0]-p[0])*(q[1]-p[1])-(n[1]-p[1])*(q[0]-p[0])
        if abs(c)>tol:signs.append(c>0)
    return not signs or all(v==signs[0] for v in signs)

def inspect(glb):
    scene=trimesh.load(glb,file_type="glb",force="scene")
    raw=actual_mesh(scene,ROUTE_PREFIX)
    before=components(raw)
    route=welded(raw)
    after=components(route)
    assert after==1 and route.is_watertight, ("real route discontinuity",after,route.is_watertight)
    R=z_up(route.vertices)
    floors={}
    for prefix,expected in FLOORS.items():
        f=z_up(welded(actual_mesh(scene,prefix)).vertices)
        top=float(f[:,2].max())
        assert abs(top-expected)<.02,("wrong elevation",prefix,top)
        points=np.unique(np.round(f[np.isclose(f[:,2],top,atol=.02)][:,:2],5),axis=0)
        hull=points[ConvexHull(points).vertices]
        count=sum(inside_convex(p[:2],hull) for p in R if abs(p[2]-top)<.04)
        assert count>0,("public destination disconnected",prefix)
        floors[prefix]={"floor_top_z_m":top,"real_welded_route_contact_vertices":count}
    # Negative control: cut the actual mid-route model; must detect disconnection.
    y=R[:,1]
    remove=np.any((y[route.faces]>-13.1)&(y[route.faces]<-2.9),axis=1)
    assert int(np.sum(remove))>0
    severed=trimesh.Trimesh(vertices=route.vertices,faces=route.faces[~remove],process=False)
    negative=components(severed)
    assert negative>1,("negative control wrongly passed",negative)
    return {
        "source":"independently reopened original GLB","route_original_vertices":len(raw.vertices),
        "route_raw_glb_components":before,"route_welded_vertices":len(route.vertices),
        "route_real_connected_components":after,"route_watertight_after_weld":True,
        "floor_contacts":floors,"negative_cut_faces_removed":int(np.sum(remove)),
        "negative_cut_components":negative,"GEOMETRY_LIMITED":"PASS",
        "FUNCTION_CERTIFIED":False,"ART_APPROVED":False,
        "STRUCTURAL_AND_EGRESS_CERTIFIED":False,"ACCESSIBILITY_CERTIFIED":False,
        "MINECRAFT_WRITE":False,
        "warning":"Single polygon component and point contacts do not establish safe access, building functionality or acceptable architecture"
    }

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("glb",type=Path)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    result=inspect(a.glb)
    output=json.dumps(result,indent=2,ensure_ascii=False)
    if a.out:a.out.write_text(output,encoding="utf-8")
    print(output)
