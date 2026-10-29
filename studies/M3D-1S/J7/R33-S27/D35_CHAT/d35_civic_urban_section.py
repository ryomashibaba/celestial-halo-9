#!/usr/bin/env python3
"""D35 exploratory inhabited-canyon spatial section, local research meters only.
The geometry is not the approved M247-C, not a city master and is not for Minecraft.
Goal: test room/terrace-to-macroform coupling BEFORE any detailed work.
"""
import sys, math, hashlib, json
from pathlib import Path
import numpy as np
import trimesh
OUT=Path(__file__).resolve().parent
COLORS={
 'terrain':[36,55,62,255], 'sand':[134,146,139,255], 'shell':[94,132,142,255],
 'shell_light':[116,159,169,255], 'habitat':[174,196,193,255],
 'void':[20,57,67,255], 'civic':[215,181,112,255], 'glass':[38,137,168,205],
 'walk':[205,215,206,255], 'rib':[164,179,178,255]
}
def tint(m,colour):m.visual.face_colors=np.asarray(COLORS[colour],np.uint8);return m
def box(name,c,e,col):
 mesh=trimesh.creation.box(extents=e);mesh.apply_translation(c);return (name,tint(mesh,col))
def rounded_path(t,side,level,variant):
 # Genuine, vertically inhabited pathways are the governing geometry.
 y=t*860-430
 q=level/7.
 phase=0.58*level+0.33*(side>0)
 x=side*(162+39*q + (25+8*q)*np.sin(1.7*np.pi*t+phase) + 28*np.sin(0.69*np.pi*t+0.7))
 z=56+level*64+15*np.sin(np.pi*t+phase) + (14*side)*np.sin(2*np.pi*t)
 if variant=='REVERSE_SKEW':
  # macro-height reallocation and response in occupied gallery envelope, not only skin painting
  x+=side*(35*q)*np.sin(np.pi*t)
  z+= (80*q)*(t-0.45) + 36*q*np.sin(np.pi*1.3*t+phase)
 return np.array([x,y,z])
def ribbon(name, pts, widths, thick, col, closed=False):
 pts=np.asarray(pts,float);widths=np.broadcast_to(np.asarray(widths,float),len(pts));n=len(pts)
 vv=[]
 for i,p in enumerate(pts):
  tang=pts[min(n-1,i+1)]-pts[max(0,i-1)]; tang[2]=0
  if np.linalg.norm(tang[:2])<0.001:raise ValueError('degenerate tangent')
  r=np.array([-tang[1],tang[0],0]); r=r/np.linalg.norm(r)
  for shift in [-1,1]:vv.append(p+shift*0.5*widths[i]*r)
 vv=np.asarray(vv)
 vv=np.vstack([vv,vv-np.array([0,0,thick])]);f=[]
 for i in range(n-1):
  a,b=2*i,2*i+1;c,d=2*(i+1),2*(i+1)+1
  f.extend([[a,b,c],[b,d,c],[a+2*n,c+2*n,b+2*n],[b+2*n,c+2*n,d+2*n],
            [a,c,a+2*n],[c,c+2*n,a+2*n],[b,b+2*n,d],[d,b+2*n,d+2*n]])
 f.extend([[0,2*n,1],[1,2*n,2*n+1],[2*n-2,2*n-1,4*n-2],[2*n-1,4*n-1,4*n-2]])
 m=trimesh.Trimesh(vertices=vv,faces=np.asarray(f),process=False);m.fix_normals()
 return (name,tint(m,col))
def beam(name,a,b,r,col,sides=8):
 a=np.asarray(a,float);b=np.asarray(b,float);d=b-a
 m=trimesh.creation.cylinder(radius=r,height=float(np.linalg.norm(d)),sections=sides)
 tr=trimesh.geometry.align_vectors([0,0,1],d)
 m.apply_transform(tr);m.apply_translation((a+b)/2)
 return (name,tint(m,col))
def make(variant='BASE',save=True):
 if variant not in ('BASE','REVERSE_SKEW'):raise ValueError('variant')
 parts=[]
 def add(x):parts.append(x)
 add(box('URBAN_GROUND_PLATE',(0,0,-10),(1100,1180,20),'terrain'))
 # Central civic public space is actually open, never substituted with a solid dummy volume.
 add(box('CIVIC_CANYON_FLOOR',(0,0,1.5),(275,830,3),'walk'))
 # Civic boulevard and endpoints
 add(box('CIVIC_ENTRY_SOUTH',(0,-520,1.5),(90,220,3),'walk'))
 add(box('CIVIC_ENTRY_NORTH',(0,520,1.5),(90,220,3),'walk'))
 # Asymmetric inhabited bands: every visible principal deck has a real floor and adjacent inhabited bays.
 for side in (-1,1):
  label='WEST' if side<0 else 'EAST'
  levels=[0,1,2,3,4,5] if side<0 else [0,1,2,3,4,6]
  for k in levels:
   tt=np.linspace(0.09+0.013*k,0.91-0.021*k,52)
   pts=np.array([rounded_path(t,side,k,variant) for t in tt])
   ww=30+10*np.cos(1.3*np.pi*tt)**2+4*k
   add(ribbon(f'{label}_LEVEL_{k}_PUBLIC_DECK',pts,ww,3.8,'habitat'))
   # Actual roof and asymmetrical backs follow the same curved deck, so room space drives envelope.
   roof=np.array([p+[0,0,22+6*np.sin(2*np.pi*t+k)] for p,t in zip(pts,tt)])
   add(ribbon(f'{label}_LEVEL_{k}_ROOF',roof,ww*0.8,2.4,'shell_light'))
   for q in range(2,len(tt)-3,7):
    p=pts[q]; w=float(ww[q]); h=float(roof[q,2]-p[2]);gap=12.0
    # Public front open towards canyon; back service wall and sidewalls, not solid cubes.
    add(beam(f'{label}_L{k}_BAY{q}_OUTER_PIER',p+np.array([side*w*0.42,0,0]),p+np.array([side*w*0.42,0,h-2]),1.7,'rib'))
    add(beam(f'{label}_L{k}_BAY{q}_INNER_PIER',p+np.array([-side*w*0.35,0,0]),p+np.array([-side*w*0.35,0,h-2]),1.4,'rib'))
    # Dark occupied perimeter window; avoid asserting actual apartments certified.
    add(box(f'{label}_L{k}_BAY{q}_SERVICE_BACK',p+np.array([side*w*0.32,0,10]),(2.5,gap,16),'void'))
    add(box(f'{label}_L{k}_BAY{q}_GLAZING',p+np.array([-side*w*0.22,0,10]),(1,gap,14),'glass'))
   # Thick exoskeleton braces follow trajectories of the inhabitated decks rather than disconnected sculpture.
   if k in (0,2,4):
    for v in [0.13,0.40,0.70,0.87]:
     src=rounded_path(v,side,k,variant);dst=rounded_path(min(0.98,v+0.08),side,min(6,k+2),variant)
     add(beam(f'{label}_DIAGONAL_FLYING_BUTTRESS_{k}_{int(100*v)}',src+[side*5,0,-3],dst+[side*7,0,-3],3.8,'shell'))
   # vertical access axes are geometric placeholders, NOT access certified.
   if k==0:
    for loc in [0.25,0.75]:
     p=rounded_path(loc,side,0,variant)
     add(beam(f'{label}_LIFT_SHAFT_{int(loc*100)}', [p[0]+side*12,p[1],0],[p[0]+side*12,p[1],400],4,'civic'))
  # Open-air long ramps, no claim of full 400m accessibility without sweep test.
  for v in [0.30,0.67]:
   lower=rounded_path(v,side,0,variant); upper=rounded_path(v+0.13,side,1,variant)
   coords=np.linspace(lower,upper,65);widths=np.full(len(coords),14)
   add(ribbon(f'{label}_LEVEL0_TO1_PUBLIC_RAMP_{int(100*v)}',coords,widths,1.8,'walk'))
 # Meeting structure across canyon, only a civic crossing from opposing occupied level 1; endpoint geometry not certified.
 for h,t in [(1,0.22),(3,0.69)]:
  a=rounded_path(t,-1,h,variant);b=rounded_path(t+0.06,1,h,variant)
  z=(a[2]+b[2])/2
  a[2]=b[2]=z
  add(ribbon(f'CROSS_CANYON_DECK_LEVEL_{h}',np.linspace(a,b,54),[18]*54,2.4,'civic'))
 scene=trimesh.Scene()
 for name,m in parts:
  if not m.is_watertight:raise AssertionError('not watertight: '+name)
  scene.add_geometry(m,geom_name=name,node_name=name)
 data=trimesh.exchange.gltf.export_glb(scene)
 if save:
  p=OUT/f'D35_{variant}_URBAN_CANYON.glb';p.write_bytes(data)
  d={'mode':variant,'meshes':len(scene.geometry),'triangles':sum(len(m.faces) for m in scene.geometry.values()),'watertight_meshes':sum(int(m.is_watertight) for m in scene.geometry.values()),'sha256':hashlib.sha256(data).hexdigest(),'asset':p.name,'local_research_only':True,'inhabitability_certified':False,'transport_certified':False}
  (OUT/f'D35_{variant}_GEOMETRY.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
  return d
 return data
if __name__=='__main__':
 for v in ['BASE','REVERSE_SKEW']:print(json.dumps(make(v),indent=2))
