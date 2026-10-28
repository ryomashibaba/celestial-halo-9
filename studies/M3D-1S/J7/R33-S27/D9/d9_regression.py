"""D9 independent GLB geometry/edit regression.
Usage: python d9_regression.py <folder-containing-D9-glbs>
Requires: numpy, trimesh. Checks bounded technical evidence only, not art.
"""
from pathlib import Path
import json,sys
import numpy as np
import trimesh

path=Path(sys.argv[1])
a=trimesh.load(path/"D9_BASE.glb",force="scene").geometry
b=trimesh.load(path/"D9_CIVIC_WIDEN.glb",force="scene").geometry
def mesh_health(g):
    m=list(g.values())
    return {"meshes":len(m),"triangles":sum(len(x.faces) for x in m),
        "watertight":sum(x.is_watertight for x in m),
        "consistent_winding":sum(x.is_winding_consistent for x in m),
        "positive_volume":sum(x.volume>0 for x in m)}
def changes(fragment):
    names=[n for n in a if n.startswith("W_CROWN") and fragment in n]
    mx=0;num=0
    for n in names:
        x=np.asarray(a[n].vertices);y=np.asarray(b[n].vertices)
        assert x.shape==y.shape,(n,x.shape,y.shape)
        distance=np.linalg.norm(y-x,axis=1)
        mx=max(mx,float(distance.max()))
        num+=int(float(distance.max())>0.005)
    return {"total":len(names),"changed":num,"largest_m":round(mx,4)}
health={"base":mesh_health(a),"edited":mesh_health(b)}
assert health["base"]==health["edited"]
assert health["base"]["meshes"]==980
assert health["base"]["watertight"]==980
assert health["base"]["consistent_winding"]==980
assert health["base"]["positive_volume"]==980
result={"geometry":health,"public_edit":{
    "west_public_floor":changes("_public_floor_sector"),
    "west_facade":changes("_frame"),
    "west_crown_roof":changes("_crown_roof")}}
unaltered=[]
for n in a:
    if n.startswith(("E_CIVIC","N_ARCHIVE","S_EXCHANGE")):
        x=np.asarray(a[n].vertices);y=np.asarray(b[n].vertices)
        if x.shape!=y.shape or not np.allclose(x,y,atol=1e-5):unaltered.append(n)
result["unexpected_other_city_changes"]=unaltered
assert not unaltered
assert result["public_edit"]["west_public_floor"]["changed"]==132
assert result["public_edit"]["west_facade"]["changed"]==106
print(json.dumps(result,ensure_ascii=False,indent=2))
print("D9 LIMITED TECH PASS — NOT proof of a finished city, human circulation, or artistic acceptance.")
