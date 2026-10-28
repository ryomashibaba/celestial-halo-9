#!/usr/bin/env python3
"""Apply saved, explicit vertex-brush strokes to an existing single-mesh GLB.

Usage: python d26_apply_strokes.py original.glb strokes.json result.glb
No new mass generation, remeshing, or topology changes. Rejects unsupported scenes.
This is a limited technical sculpt tool, *not* a Blender GUI or an architecture generator.
"""
import sys, json, math, hashlib
from pathlib import Path
import numpy as np
import trimesh

def load_single(path):
    s=trimesh.load(str(path),force='scene',process=False)
    if len(s.geometry)!=1:
        raise ValueError(f'Unsupported: requires one geometry, found {len(s.geometry)}')
    gname,mesh=next(iter(s.geometry.items()))
    nodes=list(s.graph.nodes_geometry)
    if len(nodes)!=1:
        raise ValueError('Unsupported: requires one geometry node')
    T,g=s.graph.get(nodes[0]);
    if g!=gname or not np.allclose(T,np.eye(4)):
        raise ValueError('Unsupported: non-identity scene transform')
    return gname,mesh.copy()

def change(mesh,strokes):
    if not isinstance(strokes,list) or not strokes:
        raise ValueError('strokes must be a nonempty array')
    v=np.asarray(mesh.vertices,dtype=float).copy()
    for i,s in enumerate(strokes):
        idx=s.get('anchor_vertex')
        if type(idx) is not int or not 0<=idx<len(v):
            raise ValueError(f'bad anchor_vertex in stroke {i}')
        radius=float(s.get('radius_m',0))
        dv=np.asarray(s.get('delta_xyz_m'),dtype=float)
        if not (math.isfinite(radius) and 0<radius<=10000 and dv.shape==(3,) and np.isfinite(dv).all()):
            raise ValueError(f'bad radius/shift in stroke {i}')
        center=v[idx].copy()
        distance=np.linalg.norm(v-center,axis=1)
        t=np.clip(1-distance/radius,0,1)
        w=t*t*(3-2*t)
        v += w[:,None]*dv
    mesh.vertices=v
    return mesh

def apply(src,plan_path,dst):
    src=Path(src);dst=Path(dst)
    if src.resolve()==dst.resolve():
        raise ValueError('Refusing to overwrite source GLB')
    plan=json.loads(Path(plan_path).read_text(encoding='utf-8'))
    name,base=load_single(src)
    if plan.get('target_geometry')!=name:
        raise ValueError('Selected geometry name does not match')
    result=change(base.copy(),plan.get('strokes'))
    if not (result.is_watertight and result.is_winding_consistent and result.volume>0):
        raise ValueError('Result fails basic mesh integrity; stop. No output written.')
    sc=trimesh.Scene();sc.add_geometry(result,geom_name=name,node_name=name)
    dst.write_bytes(trimesh.exchange.gltf.export_glb(sc))
    _,verify=load_single(dst)
    np.testing.assert_array_equal(result.faces,verify.faces)
    assert np.allclose(result.vertices,verify.vertices,rtol=0,atol=0.0001)
    return {'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),
            'vertices':len(verify.vertices),'triangles':len(verify.faces),
            'watertight':bool(verify.is_watertight)}

if __name__=='__main__':
    if len(sys.argv)!=4:
        raise SystemExit(__doc__)
    print(json.dumps(apply(*sys.argv[1:]),indent=2))
