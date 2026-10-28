"""Independent D7 GLB audit. Requires trimesh, vtk, numpy.
No art, walkability, or CITY MASTER certification.
Usage: python d7_audit.py S27_D7_FRACTURED_CIVIC_JUNCTION.glb
"""
import sys, json, hashlib
from pathlib import Path
import numpy as np, trimesh, vtk
from vtk.util.numpy_support import numpy_to_vtk, numpy_to_vtkIdTypeArray

def vtkpoly(g):
    p=vtk.vtkPolyData();pts=vtk.vtkPoints()
    pts.SetData(numpy_to_vtk(np.asarray(g.vertices,dtype=np.float64),deep=1));p.SetPoints(pts)
    f=np.asarray(g.faces,dtype=np.int64);cells=vtk.vtkCellArray()
    cells.SetCells(len(f),numpy_to_vtkIdTypeArray(np.c_[np.full(len(f),3,dtype=np.int64),f].ravel(),deep=1))
    p.SetPolys(cells)
    return p
def verify(path):
    s=trimesh.load(path,force="scene");g=s.geometry
    funcs={}
    for side,name in (("left","01_left_inhabited_hull"),("right","02_right_inhabited_hull")):
        d=vtk.vtkImplicitPolyDataDistance();d.SetInput(vtkpoly(g[name]));funcs[side]=d
    rng=np.random.default_rng(2710);overlap={}
    for key,geom in g.items():
        if key.startswith(("12_","13_","14_","15_","16_","17_")):
            pts=rng.uniform(geom.bounds[0],geom.bounds[1],(250,3))
            left=np.array([funcs["left"].EvaluateFunction(p)<0 for p in pts])
            right=np.array([funcs["right"].EvaluateFunction(p)<0 for p in pts])
            overlap[key]={"samples":250,"inside_any_shell":int((left|right).sum())}
    cameras={}
    for name,target,direction in [
        ("initial_hall",(-95,-145,105),(.9,-.24,.18)),
        ("corrected_hall",(-188,-145,86),(.62,-.10,.03))
    ]:
        dire=np.array(direction,dtype=float);dire/=np.linalg.norm(dire)
        pos=np.array(target)+155*dire
        cameras[name]={"xyz":pos.tolist(),"inside_shell":any(f.EvaluateFunction(pos)<0 for f in funcs.values())}
    report={"file":str(path),"sha256":hashlib.sha256(Path(path).read_bytes()).hexdigest(),
       "meshes":len(g),"triangles":sum(len(m.faces) for m in g.values()),
       "watertight":sum(int(m.is_watertight) for m in g.values()),
       "consistent_winding":sum(int(m.is_winding_consistent) for m in g.values()),
       "positive_volume":sum(int(m.volume>0) for m in g.values()),
       "interpenetration_samples":overlap,"cameras":cameras,
       "LIMITS":"Only per-piece geometry, samples inside shell and view placement. Not usable rooms, continuous public routes or art adoption."}
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":verify(Path(sys.argv[1]))
