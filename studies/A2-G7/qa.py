"""Independent GLB geometry checks. Python + numpy + trimesh, no Blender.
Vertical triangle intersections need no rtree. No engineering certification.
"""
import json,hashlib
from pathlib import Path
import numpy as np
import trimesh
R=Path(__file__).resolve().parent
record=json.loads((R/'geometry.json').read_text(encoding='utf-8'))
sc=trimesh.load(R/'selected.glb',force='scene')
C=np.array([[1,0,0,0],[0,0,-1,0],[0,1,0,0],[0,0,0,1]],float)
objs={}
for node in sc.graph.nodes_geometry:
    T,key=sc.graph[node];g=sc.geometry[key].copy();g.apply_transform(C@T);objs[node]=g
v=np.vstack([g.vertices for g in objs.values()]);assert np.isfinite(v).all()
bb=np.array([v.min(axis=0),v.max(axis=0)])
delta=float(np.max(np.abs(bb-np.array(record['bounds_m']))));assert delta<.01
def named(n):
    a=[g for k,g in objs.items() if k==n or k.startswith(n+'_')];assert a,(n,len(a));return trimesh.util.concatenate(a)
def hits(g,x,y):
    t=g.triangles;a=t[:,0,:];u=t[:,1,:]-a;w=t[:,2,:]-a
    den=u[:,0]*w[:,1]-u[:,1]*w[:,0];valid=np.abs(den)>1e-9
    den=np.where(valid,den,1);px=x-a[:,0];py=y-a[:,1]
    b=(px*w[:,1]-py*w[:,0])/den;c=(u[:,0]*py-u[:,1]*px)/den
    keep=valid&(b>=-1e-7)&(c>=-1e-7)&(b+c<=1+1e-7)
    return sorted(set(round(float(q),5) for q in (a[:,2]+b*u[:,2]+c*w[:,2])[keep]))
def overlaps(a,b):
    return bool(np.all(np.minimum(a[1],b[1])-np.maximum(a[0],b[0])>.01))
envelope=named('CIVIC_CATCHMENT_ENVELOPE')
support=[];collisions=[];clearance=[]
for pair in record['pairs']:
    roof=named(pair['roof']);ground=named(pair['id']+'_LOWER_GROUND')
    assert abs(roof.bounds[1,2]-pair['upper_z_m'])<.01
    for court in pair['courts']:
        x,y,z=court['x'],court['y'],court['floor_z_m']
        g=roof if abs(z-pair['upper_z_m'])<.01 else ground
        for dx,dy in [(-35,-44),(-35,44),(35,-44),(35,44),(-30,0),(30,0),(0,38),(0,-38)]:
            zs=hits(g,x+dx,y+dy);error=min(abs(q-z) for q in zs)
            support.append({'court':court['id'],'xy_m':[x+dx,y+dy],'error_m':error,'pass':error<.01})
        # Envelope occupancy through the actual height of each sampled housing wing.
        for dx,dy in [(-30,0),(30,0),(0,38),(-21,-38),(21,-38)]:
            h=hits(envelope,x+dx,y+dy)
            intervals=list(zip(h[::2],h[1::2]))
            if any(min(z+27.9,b)-max(z+.1,a)>.01 for a,b in intervals):
                collisions.append({'court':court['id'],'kind':'envelope','xy':[x+dx,y+dy],'intervals':intervals})
        wings=[g for k,g in objs.items() if k.startswith(court['id']+'_') and not k.endswith('_COURT')]
        rooms=[(k,g) for k,g in objs.items() if k.startswith(pair['id']+'_LIBRARY_CLINIC')]
        for wing in wings:
            for k,g in rooms:
                if overlaps(wing.bounds,g.bounds):collisions.append({'court':court['id'],'kind':'room','object':k})
    x,y=pair['common_hall_axis_xy'];z=pair['lower_z_m'];top=pair['upper_z_m']-12
    for dx,dy in [(-20,-150),(20,-150),(-20,100),(20,100)]:
        rh=hits(roof,x+dx,y+dy)
        assert abs(min(rh)-top)<.01
        clearance.append({'pair':pair['id'],'xy':[x+dx,y+dy],'hall_clear_m':min(rh)-z,'same_roof':True})
assert all(q['pass'] for q in support)
assert not collisions,collisions
# High open-sky street cut really removes the macro envelope above the shared roof.
cleft=[]
for x in [-850,-600,-300,0,250]:
    h=hits(envelope,x,-600);cleft.append({'xy':[x,-600],'envelope_z_hits':h,'above_3800_removed':not any(z>3800.02 for z in h)})
assert all(p['above_3800_removed'] for p in cleft)
qa={'study':'A2-G7','loader':'trimesh, independent of Blender','gltf_to_study_transform':C.tolist(),
 'selected_glb_sha256':hashlib.sha256((R/'selected.glb').read_bytes()).hexdigest(),
 'bounds_m':bb.tolist(),'dimensions_m':dict(zip(['width','depth','height'],(bb[1]-bb[0]).tolist())),
 'bounds_delta_vs_blender_m':delta,'all_vertices_finite':True,'geometry_objects':len(objs),'triangles':sum(len(g.faces) for g in objs.values()),
 'support':{'passed':sum(q['pass'] for q in support),'samples':len(support),'probes':support},
 'housing_vs_envelope_wing_samples':80,'housing_vs_civic_room_aabb_collisions':collisions,
 'shared_hall_clearance_probes':clearance,'open_sky_cleft':cleft,
 'roof_removal_test':'All 8 upper court footprints use their pair shared roof as sole modeled ground; deleting it removes that ground. Geometry dependency only.',
 'ground_to_high_route':'Static connected ground pavement to 3760m transport reservation and high district ground; local 128m lift meshes. No operational simulation, full accessibility or evacuation verification.',
 'not_tested':['full-model collisions','structural safety','occupiable macro envelope','transit capacity','services','pressure/wind/thermal comfort','canonical-city clearances'],
 'art_status':'HOLD','formal_adoption':False,'formal_M247C_modified':False,'world_writes':0,'work_transfer':False}
(R/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:qa[k] for k in ['dimensions_m','bounds_delta_vs_blender_m','geometry_objects','triangles','housing_vs_civic_room_aabb_collisions']}))
print('support',len(support),'passed; envelope wing samples 80; cleft samples 5; hall probes 8')
