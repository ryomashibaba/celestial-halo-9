#!/usr/bin/env python3
"""Must use a SECOND independent genuine bpy Python process to open saved native .blend."""
import sys,json,hashlib
from pathlib import Path
import numpy as np
from d37_kernel import sha

def main(planpath,outdir):
    try:import bpy
    except ImportError as e:raise RuntimeError('BLENDER_NOT_AVAILABLE: bpy is required') from e
    planpath=Path(planpath).resolve();outdir=Path(outdir).resolve()
    p=json.loads(planpath.read_text());r=json.loads((outdir/'D37_BLENDER_RUN.json').read_text())
    src=planpath.parent/p['source_filename'];assert sha(src.read_bytes())==p['source_sha256']
    blend=outdir/r['native_blend_filename'];assert sha(blend.read_bytes())==r['native_blend_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    ob=bpy.data.objects.get(p['target_geometry']);assert ob and ob.type=='MESH'
    keys=ob.data.shape_keys.key_blocks
    assert 'Basis' in keys and 'D37_SCULPT_EDIT' in keys
    assert abs(keys['D37_SCULPT_EDIT'].value-1)<1e-5
    assert len(bpy.data.objects)>=3
    for name in p['protected_geometries']:
        protect=bpy.data.objects.get(name)
        assert protect and protect.type=='MESH' and protect.data.shape_keys is None
    # Additional invariants for native target: sculpt key really deforms vertices.
    basis=np.array([tuple(x.co) for x in keys['Basis'].data])
    sculpt=np.array([tuple(x.co) for x in keys['D37_SCULPT_EDIT'].data])
    moved=np.linalg.norm(sculpt-basis,axis=1)
    assert int(np.count_nonzero(moved>1e-4))>=30
    audit={'native_reopened_in_independent_process':True,'bpy_version':bpy.app.version_string,
           'shape_key_verified':True,'protected_names_verified':True,'source_hash_unchanged':True,
           'changed_control_vertices':int(np.sum(moved>1e-4)),
           'art':'NOT_SUBMITTED','minecraft':'HOLD'}
    (outdir/'D37_NATIVE_REOPEN.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit,indent=2))
if __name__=='__main__':main(*sys.argv[1:])
