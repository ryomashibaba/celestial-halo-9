#!/usr/bin/env python3
"""Generate deterministic TECH-ONLY 3-mesh GLB/JSON fixture for real Blender CI.
No protected or canonical city assets; no art claims.
"""
import json, hashlib, argparse
from pathlib import Path
import trimesh
import numpy as np

def sha(b):return hashlib.sha256(b).hexdigest()

def create(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    mass=trimesh.creation.icosphere(subdivisions=4,radius=1.0)
    mass.apply_scale([430,305,580]);mass.apply_translation([0,0,690])
    floor=trimesh.creation.box(extents=[620,480,12]); floor.apply_translation([0,0,-6])
    marker=trimesh.creation.box(extents=[55,55,90]);marker.apply_translation([-280,-160,45])
    s=trimesh.Scene();
    for name,m in [('D37_SCULPT_TARGET',mass),('D37_PROTECTED_FLOOR',floor),('D37_PROTECTED_MARKER',marker)]:
        s.add_geometry(m,geom_name=name,node_name=name)
    source=out/'D37_NEUTRAL_FIXTURE.glb';source.write_bytes(trimesh.exchange.gltf.export_glb(s))
    plan={'schema':'halo9.d37.blender.v1','art_status':'TECHNICAL_FIXTURE_ONLY',
       'source_filename':source.name,'source_sha256':sha(source.read_bytes()),
       'target_geometry':'D37_SCULPT_TARGET','protected_geometries':['D37_PROTECTED_FLOOR','D37_PROTECTED_MARKER'],
       'strokes':[{'center_fraction':[0.62,0.42,0.70],'radius_m':470.0,'delta_xyz_m':[-165.0,90.0,115.0], 'falloff':'smoothstep'},
                  {'center_fraction':[0.27,0.70,0.42],'radius_m':390.0,'delta_xyz_m':[88.0,-85.0,100.0], 'falloff':'smoothstep'}],
       'protect_original':True,'art_gate':'NOT_SUBMITTED', 'minecraft':'HOLD'}
    (out/'D37_EDIT_PLAN.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return {'sha256':plan['source_sha256'],'meshes':len(s.geometry), 'faces':sum(len(g.faces) for g in s.geometry.values())}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('output_directory');args=p.parse_args()
    print(json.dumps(create(args.output_directory),indent=2))
