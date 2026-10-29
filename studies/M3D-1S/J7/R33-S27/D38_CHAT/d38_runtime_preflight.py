#!/usr/bin/env python3
"""Fail if real bpy or Blender glTF operators are absent; never synthesize success."""
import json,platform,sys,os

def main():
    try:import bpy
    except ImportError as e:raise RuntimeError('GENUINE_BPY_NOT_INSTALLED; native D38 gate NOT RUN') from e
    version=bpy.app.version_string
    if not version.startswith('4.5.'):
        raise RuntimeError('D38 requires pinned LTS bpy 4.5.x, got '+version)
    operators={}
    for category,name in [('import_scene','gltf'),('export_scene','gltf'),('wm','open_mainfile')]:
        try:
            op=getattr(getattr(bpy.ops,category),name)
            op.get_rna_type()
            operators[f'{category}.{name}']=True
        except Exception as exc:
            raise RuntimeError(f'Blender missing required operator {category}.{name}; native gate cannot run') from exc
    d={'blender_version':version,'genuine_bpy':True,'python':sys.version.split()[0],
       'architecture':platform.machine(),'operators':operators,'github_run_id':os.getenv('GITHUB_RUN_ID'),
       'art':'NOT_SUBMITTED','minecraft':'HOLD'}
    print(json.dumps(d,ensure_ascii=False,indent=2))
    return d

if __name__=='__main__':main()
