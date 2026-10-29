#!/usr/bin/env python3
"""Separate Blender background process validates saved .blend (unrun in this Chat)."""
import json,hashlib,sys
from pathlib import Path

def hash_geometry(obj):
    return hashlib.sha256(json.dumps([tuple(round(c,6) for c in v.co) for v in obj.data.vertices],separators=(',',':')).encode()).hexdigest()

def verify(plan_path,out_dir):
    import bpy
    plan_path=Path(plan_path).resolve();folder=Path(out_dir).resolve()
    plan=json.loads(plan_path.read_text(encoding='utf-8'))
    prior=json.loads((folder/'D36_BLENDER_AUDIT.json').read_text(encoding='utf-8'))
    source=plan_path.parent/plan['source_filename']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==plan['source_sha256'],'source modified'
    target=bpy.data.objects.get(plan['target_geometry'])
    assert target is not None and target.type=='MESH','sculpt object missing'
    assert target.data.shape_keys is not None,'no saved shape key data'
    keys=target.data.shape_keys.key_blocks
    assert 'Basis' in keys and 'D36_SCULPT_EDIT' in keys,'shape keys not stored'
    assert abs(keys['D36_SCULPT_EDIT'].value-1.0)<1e-5,'saved sculpt key not active'
    for name in plan['protected_geometries']:
        obj=bpy.data.objects.get(name)
        assert obj and obj.type=='MESH','protected object not preserved: '+name
        assert hash_geometry(obj)==prior['protected_local_mesh_digests'][name],'protected object altered: '+name
        assert obj.data.shape_keys is None,'protected object unexpectedly deformed: '+name
    assert (folder/'D36_BLENDER_OUTPUT.glb').is_file(),'missing Blender GLB output'
    assert (folder/'D36_EDITABLE_SCULPT_STUDY.blend').is_file(),'missing native BLEND'
    result={'saved_native_blend_reopened':True,'target_shape_key_verified':True,
            'protected_mesh_digests_match':True,'source_hash_match':True,
            'blender_version':bpy.app.version_string,'art_adoption':False,'minecraft':'HOLD'}
    (folder/'D36_BLENDER_REOPEN_AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('D36 native Blender reopen check passed:',json.dumps(result))

if __name__=='__main__':
    assert '--' in sys.argv
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=2:raise SystemExit('Expected edit plan and output directory')
    verify(*args)
