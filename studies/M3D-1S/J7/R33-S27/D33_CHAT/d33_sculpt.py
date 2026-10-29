#!/usr/bin/env python3
"""D33: explicitly art-directed 3D control cages -> thick, editable sculptural patch GLBs.
Not a construction system, not a canonical city design. No procedural boxes or lofting to generate art.
Output GLBs and per-cage metadata; modifications use saved cage points, not raster editing.
"""
import json,hashlib,copy
from pathlib import Path
import numpy as np
import trimesh
from scipy.interpolate import RectBivariateSpline
OUT=Path(__file__).resolve().parent
CTRL=7
TILE=52
COLORS={"MAIN_SHEAR":[166,165,154,255],"HANGING_CROWN":[118,131,145,255],"LOWER_BUTTRESS":[83,100,111,255]}

# Every point represents a user-addressable 3D design handle. Surface has both
# horizontal and vertical freeform curvature, and non-axis aligned patch seams.
def initial_guides():
    objects={}
    # physical architecture is research only, in arbitrary meters, NOT formal master coordinates.
    # Each 7x7 point is sculptable as a 3D triplet; not loft sections at constant height.
    configs={
      "MAIN_SHEAR":dict(center=(0,-100,700),X=1150,Z=1580,lean=350,curl=370,tilt=0.8,thickness=150,seed=1.1),
      "HANGING_CROWN":dict(center=(550,330,1140),X=780,Z=1030,lean=-350,curl=-280,tilt=-.63,thickness=115,seed=2.8),
      "LOWER_BUTTRESS":dict(center=(-460,380,430),X=750,Z=700,lean=70,curl=230,tilt=.35,thickness=120,seed=4.2),
    }
    for name,p in configs.items():
        cage=[]
        for i in range(CTRL):
            row=[]
            u=(i/(CTRL-1))-.5
            for j in range(CTRL):
                v=(j/(CTRL-1))-.5
                # Visible hand-addressable cage, irregular outline; tesselation interpolates these, not primitive solids.
                xs=p['center'][0]+p['X']*u + p['lean']*v + 90*np.sin((v+.3)*3+p['seed'])*((.5-abs(u))*2)
                ys=p['center'][1]+p['curl']*np.sin(u*4+p['seed'])*np.cos(v*2.2) + p['tilt']*p['X']*u*v + 200*(v**2) + 42*np.sin(2*i+3*j+p['seed'])
                zs=p['center'][2]+p['Z']*v + 170*np.sin(3*u+p['seed'])*np.cos(2*v) + 95*np.sin(4*u-1.5*v+p['seed'])
                # increased lateral taper gives serrated but smooth terminal boundaries
                row.append([round(xs,5),round(ys,5),round(zs,5)])
            cage.append(row)
        objects[name]={'cage':cage,'thickness_m':p['thickness'],'color':COLORS[name]}
    return {'version':1,'units':'m','type':'D33 isolated sculpture study','objects':objects,
            'policy':'NOT APPROVED ART / NOT CITY MASTER / NOT MINECRAFT CONSTRUCTION'}

def sculpt_mesh(spec,tile=TILE):
    p=np.asarray(spec['cage'],dtype=float)
    if p.shape!=(CTRL,CTRL,3) or not np.isfinite(p).all():raise ValueError('Invalid 7x7x3 control cage')
    t=spec['thickness_m']
    if not 10<=t<=400:raise ValueError('Thickness outside constrained research range')
    # interpolates 7x7 artist-editable points with C2 continuous splines;
    # all three XYZ coordinates may change as function of both u and v.
    u=np.linspace(0,1,tile);v=np.linspace(0,1,tile)
    smooth=np.stack([RectBivariateSpline(np.linspace(0,1,CTRL),np.linspace(0,1,CTRL),p[:,:,k],kx=3,ky=3)(u,v) for k in range(3)],axis=-1)
    du=np.gradient(smooth,axis=0);dv=np.gradient(smooth,axis=1)
    normal=np.cross(du,dv);nl=np.linalg.norm(normal,axis=2)
    if np.min(nl)<1e-5:raise ValueError('Degenerate cage surface')
    normal=normal/nl[:,:,None]
    front=smooth + normal*(t/2)
    back=smooth - normal*(t/2)
    vertices=np.vstack([front.reshape(-1,3),back.reshape(-1,3)])
    face=[];half=tile*tile
    for i in range(tile-1):
      for j in range(tile-1):
        a=i*tile+j;b=(i+1)*tile+j;c=(i+1)*tile+j+1;d=i*tile+j+1
        face.extend([[a,b,c],[a,c,d],[a+half,c+half,b+half],[a+half,d+half,c+half]])
    # All boundary perimeter edges, oriented and joined into a manifold shell.
    ring=[]
    ring.extend([(0,j) for j in range(tile-1)])
    ring.extend([(i,tile-1) for i in range(tile-1)])
    ring.extend([(tile-1,j) for j in range(tile-1,0,-1)])
    ring.extend([(i,0) for i in range(tile-1,0,-1)])
    for k,(i,j) in enumerate(ring):
      i2,j2=ring[(k+1)%len(ring)];a=i*tile+j;b=i2*tile+j2
      face.extend([[a,a+half,b+half],[a,b+half,b]])
    mesh=trimesh.Trimesh(vertices=vertices,faces=np.asarray(face),process=False)
    if mesh.volume<0:mesh.invert()
    # Avoid claiming closed shape is solid-valid until independently tested.
    mesh.visual.vertex_colors=np.tile(np.asarray(spec['color'],dtype=np.uint8),(len(mesh.vertices),1))
    return mesh

def build(plan, path):
    sc=trimesh.Scene()
    for name,spec in plan['objects'].items():
        sc.add_geometry(sculpt_mesh(spec),geom_name=name,node_name=name)
    path.write_bytes(trimesh.exchange.gltf.export_glb(sc))
    return {'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'mesh_count':len(sc.geometry),
            'triangles':sum(len(g.faces) for g in sc.geometry.values()),
            'geometry':{n:{'verts':len(g.vertices),'triangles':len(g.faces),'watertight':bool(g.is_watertight),'volume':round(g.volume,4)} for n,g in sc.geometry.items()}}

def variant(plan):
    q=copy.deepcopy(plan)
    # A single, auditable human-directed cage edit with macro impact, not new primitive sampling.
    q['edits']=[{'object':'MAIN_SHEAR','point':[5,5],'delta_xyz_m':[140,-260,260]},
                {'object':'MAIN_SHEAR','point':[5,4],'delta_xyz_m':[80,-180,180]},
                {'object':'HANGING_CROWN','point':[1,3],'delta_xyz_m':[-210,130,-120]},
                {'object':'HANGING_CROWN','point':[2,3],'delta_xyz_m':[-110,85,-60]},
                {'object':'LOWER_BUTTRESS','point':[4,4],'delta_xyz_m':[0,-145,155]}]
    for e in q['edits']:
        x,y=e['point'];arr=q['objects'][e['object']]['cage'][x][y]
        q['objects'][e['object']]['cage'][x][y]=[round(v+d,5) for v,d in zip(arr,e['delta_xyz_m'])]
    return q

if __name__=='__main__':
    base=initial_guides();edit=variant(base)
    for name,plan in [('BASE',base),('EDIT',edit)]:
        (OUT/f'D33_{name}_CAGE.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
        result=build(plan,OUT/f'D33_{name}_ART_STUDY.glb')
        (OUT/f'D33_{name}_BUILD.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(name,result)
