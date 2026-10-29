#!/usr/bin/env python3
"""Real GLB reference using same WORLD-space kernel, independent of Blender."""
import sys,json
from pathlib import Path
import numpy as np,trimesh
from d37_kernel import validate,apply,sha

def run(planpath,out):
    planpath=Path(planpath).resolve();p=json.loads(planpath.read_text());src=planpath.parent/p['source_filename'];out=Path(out).resolve()
    if out==src or out.exists():raise ValueError('Refusing output overwrite')
    s=trimesh.load(str(src),force='scene',process=False)
    validate(p,src,s.geometry.keys());target=s.geometry[p['target_geometry']]
    a=np.asarray(target.vertices).copy();b=apply(a,p['strokes']);target.vertices=b
    if not target.is_watertight or not target.is_winding_consistent or target.volume<=0:raise ValueError('Post edit geometry invalid')
    data=trimesh.exchange.gltf.export_glb(s);out.write_bytes(data)
    return {'source_sha256':p['source_sha256'],'reference_sha256':sha(data), 'target_moved_vertices':int(np.sum(np.linalg.norm(b-a,axis=1)>0.0001)), 'target_max_move_m':float(np.linalg.norm(b-a,axis=1).max()), 'blender_run':False}
if __name__=='__main__':print(json.dumps(run(sys.argv[1],sys.argv[2]),indent=2))
