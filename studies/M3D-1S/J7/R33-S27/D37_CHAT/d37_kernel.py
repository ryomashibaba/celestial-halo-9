"""Shared deterministic stroke math and strict plan validation. Runs without Blender."""
import json, math, hashlib
from pathlib import Path
import numpy as np

def sha(data):return hashlib.sha256(data).hexdigest()

def validate(plan, source, names):
    if plan.get('schema')!='halo9.d37.blender.v1':raise ValueError('Bad schema')
    if plan.get('art_status')!='TECHNICAL_FIXTURE_ONLY' or plan.get('minecraft')!='HOLD':raise ValueError('Protected production boundary')
    if plan.get('source_sha256')!=sha(Path(source).read_bytes()):raise ValueError('GLB source SHA mismatch')
    target=plan.get('target_geometry');protected=plan.get('protected_geometries')
    if not isinstance(protected,list) or len(protected)!=2 or len(set(protected))!=2:raise ValueError('Protected names invalid')
    if set(names)!=set(protected)|{target} or target in protected:raise ValueError('Unexpected geometry or protected target')
    if plan.get('protect_original') is not True:raise ValueError('Source overwrite prevention required')
    ss=plan.get('strokes')
    if not isinstance(ss,list) or not 1<=len(ss)<=12:raise ValueError('Unsafe stroke count')
    for s in ss:
        cf=np.asarray(s.get('center_fraction',[]),dtype=float)
        d=np.asarray(s.get('delta_xyz_m',[]),dtype=float)
        r=float(s.get('radius_m',0))
        if cf.shape!=(3,) or d.shape!=(3,) or not np.isfinite(cf).all() or not np.isfinite(d).all():raise ValueError('Nonfinite or malformed stroke')
        if np.any(cf<0) or np.any(cf>1):raise ValueError('Center fraction out of range')
        if not 1<=r<=750 or np.linalg.norm(d)>300:raise ValueError('Unsafe stroke radius/delta')
        if s.get('falloff')!='smoothstep':raise ValueError('Only smoothstep allowed')

def apply(vertices,strokes):
    a=np.asarray(vertices,dtype=np.float64);low=a.min(axis=0);span=a.max(axis=0)-low
    edited=a.copy()
    for s in strokes:
        center=low+np.asarray(s['center_fraction'],float)*span
        r=float(s['radius_m']); dist=np.linalg.norm(a-center,axis=1)
        w=np.clip(1.0-dist/r,0,1);w=w*w*(3-2*w)
        edited+=w[:,None]*np.asarray(s['delta_xyz_m'],float)
    return edited
