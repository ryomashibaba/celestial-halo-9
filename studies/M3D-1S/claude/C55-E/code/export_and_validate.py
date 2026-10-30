import sys,json,os,hashlib,numpy as np
sys.path.insert(0,'/home/claude/c55e/code')
from core import *
from lib_e import mesh_report
from scipy.spatial import cKDTree
MD_EB={0:('EB_shell_underside_facade_neutral',[0.58,0.58,0.58,1],0.0,0.9,[0,0,0]),1:('EB_habitation_face_neutral',[0.58,0.58,0.58,1],0.0,0.9,[0,0,0]),2:('ground_context_low_neutral',[0.46,0.46,0.46,1],0.0,0.9,[0,0,0])}
MD_EA={0:('EA_lattice_shell_ribs_neutral',[0.58,0.58,0.58,1],0.0,0.9,[0,0,0]),1:('EA_cavity_ceiling_world_neutral',[0.58,0.58,0.58,1],0.0,0.9,[0,0,0]),2:('ground_context_low_neutral',[0.46,0.46,0.46,1],0.0,0.9,[0,0,0]),7:('EA_hanging_district_drums_neutral',[0.58,0.58,0.58,1],0.0,0.9,[0,0,0])}
res={}
for tag,npz,glb,MD in (('E-B','_eb.npz','C55E_EB_yori_well_v3.glb',MD_EB),('E-A','_ea.npz','C55E_EA_terra_turn_open_lattice_v2.glb',MD_EA)):
    z=np.load('/home/claude/c55e/model/'+npz); mesh={k:z[k] for k in z.files}
    path='/home/claude/c55e/model/'+glb; n=write_glb(path,mesh,MD)
    parts=read_glb(path); tt=sum(len(p[2]) for p in parts); allv=np.concatenate([p[1] for p in parts])
    chk=dict(glb_bytes=int(n),prims=[(p[0],int(len(p[2]))) for p in parts],tris_reread=int(tt),tris_source=int(len(mesh['F'])),
        bbox_min=[round(float(x),1) for x in allv.min(0)],bbox_max=[round(float(x),1) for x in allv.max(0)],
        index_in_range=bool(all(p[2].max()<len(p[1]) for p in parts)),nan_free=bool(np.isfinite(allv).all()))
    chk['mesh_report']=mesh_report(mesh)
    V=mesh['V']; chk['below_ground_vertices']=int((V[:,2]<-1).sum()); chk['min_z']=round(float(V[:,2].min()),1)
    res[tag]=chk; print(tag,'glb',n,'tris',tt)
# ---------- E-B specifics
fr=np.load('/home/claude/c55e/model/_eb_frames.npz'); sol=np.load('/home/claude/c55e/model/_eb_solidsamples.npz')
eb={}
for a,b in (('A','C'),('C','B'),('A','B')):
    d,_=cKDTree(sol[b]).query(sol[a]); eb[f'min_clearance_{a}_{b}_m']=round(float(d.min()),1)
Bp=sol['B']; r=np.hypot(Bp[:,0],Bp[:,1]); m=(Bp[:,2]>800)&(Bp[:,2]<3000); eb['void_radius_m_at_z800_3000_(min distance of ribbon B surface to axis)']=round(float(r[m].min()),0)
eb['structure_height_m(ribbons+rim slabs)']=res['E-B']['bbox_max'][2]
eb['ribbon_path_lengths_km']={k:round(float(fr[f'{k}_s'][-1])/1000,1) for k in 'ACB'}
eb['ribbon_top_altitudes_m']={k:round(float(fr[f'{k}_zc'][-1]),0) for k in 'ACB'}
# mean climb gradient along ribbons
eb['mean_climb_gradient_1_in']={k:round(float(fr[f'{k}_s'][-1]/fr[f'{k}_zc'][-1]),1) for k in 'ACB'}
res['E-B']['specific']=eb
# ---------- E-A specifics
sf=np.load('/home/claude/c55e/model/_ea_surf.npz'); ea={}
for k in 'AB':
    S=sf[f'{k}_S']; NL=sf[f'{k}_NL']; tk=sf[f'{k}_tk']; cav=S[...,:]-0   # S already = cavity-side face (path)
    ea[f'curl_{k}']=dict(cavity_face_max_height_m=round(float(S[...,2].max()),0),lip_tip_min_height_m=round(float(S[:,-1,2].mean()),0),
        axis_length_m=round(float(np.linalg.norm(S[-1,0]-S[0,0])),0),shell_thickness_max_m=round(float(tk.max()),0),open_cell_fraction=round(float(sf[f'{k}_drop'].mean()),3))
d,_=cKDTree(sf['B_S'][::2,::2].reshape(-1,3)).query(sf['A_S'][::2,::2].reshape(-1,3)); ea['min_distance_curlA_to_curlB_surface_samples_m']=round(float(d.min()),0)
res['E-A']['specific']=ea
json.dump(res,open('/home/claude/c55e/validation/glb_selfcheck_and_geometry.json','w'),indent=1,ensure_ascii=False)
print(json.dumps({k:v['specific'] for k,v in res.items()},ensure_ascii=False,indent=1))
