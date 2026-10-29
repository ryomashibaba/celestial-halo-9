#!/usr/bin/env python3
"""D27 experimental named multi-mesh rig editor. Moves existing GLB mesh vertices only.

No new geometry, topology generation, destructive source writes, Blender GUI or generalized rigging.
Only approved named sets are allowed, with protected public-route geometry fixed.
"""
import json,sys,hashlib,math
from pathlib import Path
import numpy as np
import trimesh
WEST=['WEST_roof_shell','WEST_support_0','WEST_support_1','WEST_urban_outer','WEST_urban_high',*[f'WEST_civic_terrace_{i}' for i in range(3)]]
EAST=['EAST_roof_shell','EAST_support_0','EAST_support_1','EAST_urban_outer','EAST_urban_high',*[f'EAST_civic_terrace_{i}' for i in range(3)]]
GROUPS={'WEST_DISTRICT':WEST,'EAST_DISTRICT':EAST}
PROTECTED=('civic_spine','civic_plaza')
BRIDGE='civic_high_bridge'
def digest(data):return hashlib.sha256(data).hexdigest()
def read_scene(p):
    s=trimesh.load(str(p),force='scene',process=False)
    if set(s.geometry)!=set(WEST+EAST+list(PROTECTED)+[BRIDGE]):raise ValueError('unexpected geometry set')
    nodes=list(s.graph.nodes_geometry)
    if len(nodes)!=len(s.geometry):raise ValueError('instancing / duplicate nodes unsupported')
    for node in nodes:
        transform,name=s.graph.get(node)
        if not np.allclose(transform,np.eye(4)):raise ValueError('nonidentity transform unsupported')
    return s
def apply(src,recipe,dst):
    src,recipe,dst=map(Path,(src,recipe,dst))
    if not src.exists() or not recipe.exists():raise ValueError('missing source or plan')
    if src.resolve()==dst.resolve():raise ValueError('source overwrite refused')
    if dst.exists():raise ValueError('overwrite of existing output refused')
    p=json.loads(recipe.read_text(encoding='utf-8'))
    if p.get('expected_source_sha256')!=digest(src.read_bytes()):raise ValueError('source sha mismatch')
    s=read_scene(src)
    steps=p.get('moves');seen=set()
    if not isinstance(steps,list) or not steps:raise ValueError('empty plan')
    for step in steps:
        group=step.get('group')
        if group not in GROUPS or group in seen:raise ValueError('unknown/duplicate group')
        seen.add(group)
        d=np.asarray(step.get('delta_xyz_m',[]),dtype=float)
        if d.shape!=(3,) or not np.all(np.isfinite(d)) or np.linalg.norm(d)>120:raise ValueError('invalid or too large delta')
        for name in GROUPS[group]:
            obj=s.geometry[name]; v=np.asarray(obj.vertices).copy()+d
            obj.vertices=v
            if not obj.is_watertight or not obj.is_winding_consistent:raise ValueError('watertightness broken')
    # Public sky bridge connects two moved shoulders; stretch its *saved mesh vertices*
    # at the two ends. This is not a mechanical joint certification.
    if set(seen)!=set(GROUPS):raise ValueError('Both districts required for bridge coupling')
    if p.get('bridge_connect_mode')!='endpoints_affine_x':raise ValueError('bridge coupling required')
    steps_by_group={step['group']:np.asarray(step['delta_xyz_m'],dtype=float) for step in steps}
    if any(abs(steps_by_group[g][i])>0.00001 for g in GROUPS for i in (1,2)):
        raise ValueError('bridge coupling only supports X moves')
    bridge=s.geometry[BRIDGE]; v=np.asarray(bridge.vertices).copy()
    xmin,xmax=float(v[:,0].min()),float(v[:,0].max())
    if xmax-xmin<0.1:raise ValueError('bridge has no span')
    t=(v[:,0]-xmin)/(xmax-xmin)
    v[:,0]+=(1-t)*steps_by_group['WEST_DISTRICT'][0]+t*steps_by_group['EAST_DISTRICT'][0]
    bridge.vertices=v
    if not bridge.is_watertight or not bridge.is_winding_consistent:
        raise ValueError('bridge mesh invalid after stretching')
    # Immutable at-grade public pathway and plaza geometry: exact vertex/faces comparison
    source=read_scene(src)
    for name in PROTECTED:
        if not np.array_equal(s.geometry[name].vertices,source.geometry[name].vertices):raise ValueError('public space moved')
        if not np.array_equal(s.geometry[name].faces,source.geometry[name].faces):raise ValueError('public topology changed')
    data=trimesh.exchange.gltf.export_glb(s)
    # Load from bytes to independently establish names, support mesh and unchanged topology
    test=trimesh.load(trimesh.util.wrap_as_stream(data),file_type='glb',force='scene',process=False)
    if set(test.geometry)!=set(source.geometry):raise ValueError('export lost named geometry')
    for name in source.geometry:
        a,b=source.geometry[name],test.geometry[name]
        if not np.array_equal(a.faces,b.faces):raise ValueError('topology changed: '+name)
    dst.write_bytes(data)
    return {'sha256':digest(data),'mesh_count':len(test.geometry),'triangle_count':sum(len(g.faces) for g in test.geometry.values()),'groups_moved':list(seen),'protected_unchanged':list(PROTECTED),'bridge_stretched':True}
if __name__=='__main__':
    if len(sys.argv)!=4:raise SystemExit('usage: python d27_multimesh_editor.py INPUT.glb RECIPE.json OUTPUT.glb')
    print(json.dumps(apply(*sys.argv[1:]),indent=2))
