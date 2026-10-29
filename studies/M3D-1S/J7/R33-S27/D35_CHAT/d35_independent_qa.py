#!/usr/bin/env python3
"""Independent readback QA for D35; local geometry only. Fail closed for aesthetic claims."""
import json, math, sys, hashlib
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial import cKDTree
O=Path(__file__).parent

def curve_from_ribbon(mesh):
    v=np.asarray(mesh.vertices)
    # Export GLB groups may reorder vertices/faces; reconstruct top surface path by sorted Y
    # Multiple vertices per longitudinal station (left/right, top/bottom); aggregate by nearest Y.
    ys=np.round(v[:,1],5);vals=[]
    for y in sorted(set(ys)):
        at=v[ys==y]
        # only upper surface vertices at each Y; averaging paired XY yields path centre
        ztop=at[:,2].max();top=at[np.abs(at[:,2]-ztop)<0.02]
        vals.append([top[:,0].mean(),top[:,1].mean(),top[:,2].mean()])
    return np.asarray(vals)

def run(label):
    p=O/f'D35_{label}_URBAN_CANYON.glb';s=trimesh.load(p,force='scene',process=False)
    n=len(s.geometry); tri=sum(len(g.faces) for g in s.geometry.values());wt=sum(int(g.is_watertight) for g in s.geometry.values())
    results=[]
    for name,geom in s.geometry.items():
        if 'LEVEL0_TO1_PUBLIC_RAMP' not in name:continue
        v=np.asarray(geom.vertices,dtype=float)
        xy=v[:,:2]
        # Ramp was created by a linear centreline, width extends perpendicular.
        # PCA centreline gives the longitudinal slope from actual *saved* vertices.
        u,ss,vt=np.linalg.svd(xy-xy.mean(axis=0),full_matrices=False)
        t=(xy-xy.mean(axis=0))@vt[0]
        long=(np.percentile(t,99)-np.percentile(t,1))
        slope=float(abs(np.dot(t,v[:,2]-v[:,2].mean()) / np.dot(t,t)))
        rise=float(slope*long)
        # Check regression fit to rule out claiming a warped/non-planar ramp is a straight grade.
        predicted=v[:,2].mean()+ np.sign(np.dot(t,v[:,2]-v[:,2].mean()))*slope*t
        residual=float(np.sqrt(np.mean((v[:,2]-predicted)**2)))
        results.append({'name':name,'estimated_longitudinal_length_m':float(long),'estimated_rise_m':rise,'linear_fit_grade_percent':100*slope,'linear_fit_residual_m':residual,'under_5pct':bool(slope<=.05+1e-5)})
    con=[]
    for name,m in s.geometry.items():
        if not name.startswith('CROSS_CANYON_DECK_LEVEL'):continue
        center=curve_from_ribbon(m)
        lev=int(name.split('_')[-1]);w=[v for k,v in s.geometry.items() if f'WEST_LEVEL_{lev}_PUBLIC_DECK' in k];e=[v for k,v in s.geometry.items() if f'EAST_LEVEL_{lev}_PUBLIC_DECK' in k]
        # Nearest vertex gap lower-bound/approximation, NOT exact edge/walk attachment
        if len(w)!=1 or len(e)!=1:raise AssertionError('missing intended cross deck')
        con.append({'name':name,'end_approx_nearest_west_deck_vertex_m':float(cKDTree(w[0].vertices).query(center[0])[0]),'end_approx_nearest_east_deck_vertex_m':float(cKDTree(e[0].vertices).query(center[-1])[0]),'connector_approved':False})
    # Full fidelity: X/Y floor opening is solid on ground passage. Camera originally at z=2 inside floor volume (top=3).
    floor=s.geometry['CIVIC_CANYON_FLOOR']; fmin,fmax=floor.bounds
    eye=np.array([0,-390,2.0]);ground_camera_embedded=bool(np.all(eye>=fmin)&np.all(eye<=fmax))
    if not ground_camera_embedded:raise AssertionError('D35 camera regression premise changed')
    result={'candidate':label,'glb_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'readback_geometry_count':n,'readback_triangle_count':tri,'readback_individually_watertight':wt,'sampled_ramps':results,'sampled_crossings':con,'original_human_camera_inside_floor_bbox':ground_camera_embedded,'original_human_camera_eye_z_m':2.0,'civic_floor_top_z_m':float(fmax[2]),'all_ramps_pass_5pct':all(x['under_5pct'] for x in results),'certified_housing_rooms':0,'whole_city_master_complete':False,'art_gate':'REJECT','tech_gate':'FAIL_VERTICAL_CIRCULATION','full_walkability_certified':False}
    (O/f'D35_{label}_QA.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
    return result
if __name__=='__main__':
    for label in ['BASE','REVERSE_SKEW']:
        q=run(label);print(label, 'slopes',[(round(x['linear_fit_grade_percent'],2),round(x['estimated_rise_m'],2)) for x in q['sampled_ramps']], 'crossings', [(round(x['end_approx_nearest_west_deck_vertex_m'],2),round(x['end_approx_nearest_east_deck_vertex_m'],2)) for x in q['sampled_crossings']], 'camera_inside_floor',q['original_human_camera_inside_floor_bbox'])
