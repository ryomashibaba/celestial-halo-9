#!/usr/bin/env python3
"""D36 test-only GLB deformation: normalized-AABB sculpt strokes on one named mesh.

This reference implementation is independently executable without Blender. The
matching Blender script is supplied separately and MUST be tested in Blender.
Does NOT claim a new art design; input fixture was ART REJECT at D33.
"""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import trimesh


def sha(b): return hashlib.sha256(b).hexdigest()


def check_plan(plan, src_bytes, geom_names):
    if plan['source_sha256']!=sha(src_bytes):raise ValueError('Input SHA256 mismatch')
    if plan.get('art_status')!='TECHNICAL_FIXTURE_ONLY':raise ValueError('Study art gate must be explicit')
    target=plan.get('target_geometry')
    protected=plan.get('protected_geometries')
    if not target or target not in geom_names:raise ValueError('Unknown target geometry')
    if not isinstance(protected,list) or not protected or len(protected)!=len(set(protected)):
        raise ValueError('Protected list missing or duplicate')
    if target in protected or not set(protected).issubset(geom_names):raise ValueError('Invalid protected set')
    if set(protected)!=(set(geom_names)-{target}):raise ValueError('All nontarget meshes must be protected')
    strokes=plan.get('strokes',[])
    if not isinstance(strokes,list) or not strokes or len(strokes)>12:raise ValueError('Bad strokes')
    for i,s in enumerate(strokes):
        n=np.asarray(s.get('center_fraction'), dtype=float); d=np.asarray(s.get('delta_xyz_m'),dtype=float)
        r=float(s.get('radius_m',0))
        if n.shape!=(3,) or d.shape!=(3,) or not np.isfinite(n).all() or not np.isfinite(d).all():
            raise ValueError(f'Invalid stroke vectors {i}')
        if (n<0).any() or (n>1).any():raise ValueError('center_fraction outside [0,1]')
        if not 1<=r<=750 or np.linalg.norm(d)>300:raise ValueError('Unsafe stroke size')
        if s.get('falloff')!='smoothstep':raise ValueError('Only smoothstep falloff supported')


def deform(vertices, strokes):
    base=np.asarray(vertices,dtype=np.float64).copy()
    mins=base.min(axis=0); extent=base.max(axis=0)-mins
    changed=base.copy()
    for s in strokes:
        # The stroke center is computed on the frozen base model, never from the edit.
        center=mins+np.asarray(s['center_fraction'],float)*extent
        radius=float(s['radius_m'])
        dist=np.linalg.norm(base-center,axis=1)
        weight=np.maximum(0,1-dist/radius)
        weight=weight*weight*(3-2*weight)
        changed+=weight[:,None]*np.asarray(s['delta_xyz_m'],float)
    return changed


def apply(source, plan_path, output):
    source,plan_path,output=map(Path,(source,plan_path,output))
    if source.resolve()==output.resolve():raise ValueError('Source overwrite refused')
    if output.exists():raise ValueError('Output already exists')
    raw=source.read_bytes(); plan=json.loads(plan_path.read_text(encoding='utf-8'))
    scene=trimesh.load(str(source),force='scene',process=False)
    check_plan(plan,raw,set(scene.geometry))
    tgt=scene.geometry[plan['target_geometry']]
    orig=np.asarray(tgt.vertices).copy()
    edited=deform(orig,plan['strokes'])
    changed=int(np.count_nonzero(np.linalg.norm(edited-orig,axis=1)>1e-5))
    if changed<30:raise ValueError('Brush did not touch enough vertices')
    tgt.vertices=edited
    if not tgt.is_watertight or not tgt.is_winding_consistent or tgt.volume<=0:
        raise ValueError('Basic topological consistency test failed')
    result=trimesh.exchange.gltf.export_glb(scene)
    restored=trimesh.load(trimesh.util.wrap_as_stream(result),file_type='glb',force='scene',process=False)
    if set(restored.geometry)!=set(scene.geometry):raise ValueError('GLB names lost')
    # Canonical GLB roundtrip may store float32; avoid pretending vertex bit equality.
    for key in scene.geometry:
        a,b=scene.geometry[key],restored.geometry[key]
        if len(a.faces)!=len(b.faces):raise ValueError('Triangle count changed')
        if key in plan['protected_geometries'] and not np.allclose(np.asarray(a.vertices),np.asarray(b.vertices),atol=0.0002):
            raise ValueError('Protected object drift')
    output.write_bytes(result)
    return {'input_sha256':sha(raw),'output_sha256':sha(result),
            'target':plan['target_geometry'],'strokes':len(plan['strokes']),
            'modified_vertices':changed,'max_displacement_m':float(np.linalg.norm(edited-orig,axis=1).max()),
            'mesh_count':len(restored.geometry),'triangles':sum(len(g.faces) for g in restored.geometry.values()),
            'protected_count':len(plan['protected_geometries']),
            'actual_blender_execution':False,'art_status':'NOT_SUBMITTED'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('plan');ap.add_argument('output');a=ap.parse_args()
    print(json.dumps(apply(a.source,a.plan,a.output),indent=2))
