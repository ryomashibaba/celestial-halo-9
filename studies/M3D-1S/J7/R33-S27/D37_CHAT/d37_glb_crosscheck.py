#!/usr/bin/env python3
"""Third-process Trimesh QA. Validates real Blender-produced GLB against offline world-space reference.

Vertex order may differ in Blender GLB exports; compare nearest-neighbor coordinates,
NOT GLB hashes, name alignment, or exact serialized bytes.
"""
import sys,json,hashlib
from pathlib import Path
import numpy as np,trimesh
from scipy.spatial import cKDTree
from d37_kernel import sha

def scene_world(path):
    s=trimesh.load(str(path),force='scene',process=False)
    meshes={}
    for node in s.graph.nodes_geometry:
        t,name=s.graph.get(node)
        m=s.geometry[name]
        w=trimesh.transform_points(np.asarray(m.vertices),t)
        meshes[name]=w
    return meshes

def main(planpath,outdir,reference_glb):
    planpath=Path(planpath);outdir=Path(outdir)
    p=json.loads(planpath.read_text());meta=json.loads((outdir/'D37_BLENDER_RUN.json').read_text())
    assert (outdir/'D37_NATIVE_REOPEN.json').exists(),'Need real independent native reopen'
    ref=scene_world(reference_glb);output=scene_world(outdir/meta['baked_glb_filename'])
    base=scene_world(planpath.parent/p['source_filename'])
    if set(output)!=set(ref):raise ValueError('Mesh identities changed: '+repr((set(output),set(ref))))
    def nearest_errors(a,b):
        return float(max(cKDTree(a).query(b)[0].max(),cKDTree(b).query(a)[0].max()))
    diffs={}
    for name in ref:
        diff=nearest_errors(ref[name],output[name]);diffs[name]=diff
        if diff>0.05:raise ValueError(f'GLB differs from Blender-independent reference {name}: {diff:.3f}m')
    for name in p['protected_geometries']:
        diff=nearest_errors(output[name],base[name])
        if diff>0.05:raise ValueError(f'Protected mesh drift {name}: {diff:.3f}m')
    target=p['target_geometry']
    original_to_output=nearest_errors(base[target],output[target])
    if original_to_output<2:raise ValueError('Target edit not present in exported GLB')
    report={'real_blender_native_reopened':True,'real_blender_export_glb_compared':True,
        'compare_threshold_m':0.05,'max_vertex_set_distance_m':diffs,'changed_target_shape':True,
        'min_detectable_change_m':original_to_output,'protected_unchanged':True,
        'art':'NOT_SUBMITTED','minecraft':'HOLD'}
    (outdir/'D37_CROSSCHECK.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main(*sys.argv[1:])
