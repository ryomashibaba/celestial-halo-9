#!/usr/bin/env python3
"""D34 isolated functional three-level civic section; NOT the canonical M247-C or a city master.
Self-contained source. Creates actual hollow galleries + continuous ramped path in metres.
Uses no rejected D23-D33 macroform geometry. Outputs actual editable named GLB meshes.
"""
from pathlib import Path
import json, math, hashlib
import numpy as np
import trimesh

OUT=Path(__file__).parent
PATH=[
 ('GROUND_ENTRY',(-300.,-90.,0.),(-240.,-90.,0.)),
 ('RAMP_WEST',(-240.,-90.,0.),(-80.,-90.,8.)),
 ('MID_CROSSING',(-80.,-90.,8.),(-80.,90.,8.)),
 ('RAMP_EAST',(-80.,90.,8.),(80.,90.,16.)),
 ('TOP_PROMENADE',(80.,90.,16.),(255.,90.,16.)),
]
BRANCH=[
 ('ROOM_G0_ACCESS',(-260.,-90.,0.),(-260.,-113.,0.)),
 ('ROOM_G1_ACCESS',(-80.,-90.,8.),(-80.,-113.,8.)),
 ('ROOM_G2_ACCESS',(190.,90.,16.),(190.,113.,16.)),
 ('ROOM_G0_INTERIOR',(-260.,-113.,0.),(-260.,-147.,0.)),
 ('ROOM_G1_INTERIOR',(-80.,-113.,8.),(-80.,-147.,8.)),
 ('ROOM_G2_INTERIOR',(190.,113.,16.),(190.,147.,16.)),
]
ROOMS=[('G0',-260.,-145.,0.,'N'),('G1',-80.,-145.,8.,'N'),('G2',190.,145.,16.,'S')]
materials={
 'routes':[54,196,206,255],'rooms':[216,225,231,255],
 'walls':[81,102,116,255],'roof':[210,174,112,255],
 'structure':[118,135,145,255], 'glass':[70,172,188,175],
 'ground':[68,82,92,255], 'highlight':[251,212,133,255],
}

def box(name,center,extents,color):
 m=trimesh.creation.box(extents=np.asarray(extents,float));m.apply_translation(np.asarray(center,float));
 m.visual.face_colors=np.array(materials[color],dtype=np.uint8)
 return name,m

def route_segment(name,a,b,width=12.,thickness=.8):
 a=np.asarray(a,float);b=np.asarray(b,float)
 d=b[:2]-a[:2];length=float(np.linalg.norm(d)); unit=d/length;ortho=np.array([-unit[1],unit[0]])*width/2
 top=np.array([np.array([a[0]+ortho[0],a[1]+ortho[1],a[2]]),np.array([a[0]-ortho[0],a[1]-ortho[1],a[2]]),np.array([b[0]-ortho[0],b[1]-ortho[1],b[2]]),np.array([b[0]+ortho[0],b[1]+ortho[1],b[2]])])
 vertices=np.vstack([top,top-np.array([0,0,thickness])]);faces=np.array([[0,1,2],[0,2,3],[4,6,5],[4,7,6],[0,4,5],[0,5,1],[1,5,6],[1,6,2],[2,6,7],[2,7,3],[3,7,4],[3,4,0]],int)
 # faces winding top orientation corrected by explicit bottom if necessary
 m=trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
 if m.volume<0:m.invert()
 m.visual.face_colors=np.array(materials['routes'],dtype=np.uint8)
 return name,m

def annulus_ribbon(name,xcenter,ycenter,z,major=70,minor=47,width=4,depth=1,n=96):
 ts=np.linspace(0,2*np.pi,n,endpoint=False)
 vertices=[]
 for rr in [(major,minor),(major+width,minor+width)]:
  for h in [z,z-depth]:
   for t in ts:vertices.append([xcenter+rr[0]*np.cos(t),ycenter+rr[1]*np.sin(t),h])
 vv=np.array(vertices)
 faces=[]
 def wrap(a,b):
  for i in range(n):
   j=(i+1)%n;faces.extend([[a+i,a+j,b+j],[a+i,b+j,b+i]])
 wrap(0,n);wrap(2*n,3*n);wrap(2*n,0);wrap(n,3*n)
 m=trimesh.Trimesh(vertices=vv,faces=np.array(faces),process=False);m.fix_normals();m.visual.face_colors=np.array(materials['highlight'],dtype=np.uint8)
 return name,m

def gallery(label,cx,cy,z,front):
 """A true hollow 90x64m gallery with usable front 24m portal and two window apertures.
 Explicit geometry sections; no 'solid fake room'."""
 out=[]
 def add(name,center,extents,mat):out.append(box(f'{label}_{name}',center,extents,mat))
 w,d,h=90,64,16; t=1.4
 add('interior_floor',(cx,cy,z-.5),(w,d,1),'rooms')
 add('ceiling_slab',(cx,cy,z+h+.5),(w,d,1),'roof')
 # side walls each: two windows at middle z~8; openings are genuine holes by segments
 for side,sx in [('west',cx-w/2+t/2),('east',cx+w/2-t/2)]:
  for iy,(y1,y2) in enumerate([(cy-d/2,cy-23),(cy-23,cy-11),(cy-11,cy+11),(cy+11,cy+23),(cy+23,cy+d/2)]):
   yc=(y1+y2)/2;dy=y2-y1
   if iy in [1,3]:
    add(f'{side}_window_sill_{iy}',(sx,yc,z+2),(t,dy,4),'walls')
    add(f'{side}_window_header_{iy}',(sx,yc,z+12),(t,dy,8),'walls')
   else:add(f'{side}_wall_{iy}',(sx,yc,z+h/2),(t,dy,h),'walls')
 # Front and back walls split around doorway at x center; a true 24m opening on front
 for at,yy in [('front',cy+d/2-t/2 if front=='N' else cy-d/2+t/2),('rear',cy-d/2+t/2 if front=='N' else cy+d/2-t/2)]:
  if at=='front':
   add('front_left',(cx-(w+24)/4,yy,z+h/2),((w-24)/2,t,h),'walls')
   add('front_right',(cx+(w+24)/4,yy,z+h/2),((w-24)/2,t,h),'walls')
   add('front_header',(cx,yy,z+13.5),(24,t,5),'walls') # 11m clear height
  else:
   add('rear_left',(cx-31,yy,z+h/2),(28,t,h),'walls')
   add('rear_right',(cx+31,yy,z+h/2),(28,t,h),'walls')
   add('rear_window_sill',(cx,yy,z+2),(34,t,4),'walls')
   add('rear_window_lintel',(cx,yy,z+12),(34,t,8),'walls')
 # inhabited cues are real geometry (not occupancy certification)
 for i in [-1,1]:
  add(f'gallery_partition_{i}',(cx+i*25,cy+9,z+3),(1.0,25,6),'structure')
 # Frames/lower service bays
 for xoff in [-31,31]:
  add(f'portal_column_{xoff}',(cx+xoff,cy+(-25 if front=='S' else 25),z+7),(2,2,14),'structure')
 return out

def make():
 things=[]
 def add(x):things.append(x)
 add(box('SITE_STUDY_GROUND',(0,0,-2.1),(720,510,2.0),'ground'))
 for name,a,b in PATH+BRANCH:add(route_segment(name,a,b))
 for label,cx,cy,z,front in ROOMS:things.extend(gallery(label,cx,cy,z,front))
 # colonnades supporting elevated public galleries, only schematic; no structural proof
 for x,y,top in [(-80,-90,8),(-80,0,8),(-80,90,8),(-20,90,12),(40,90,14),(80,90,16),(190,90,16),(-80,-145,8),(190,145,16)]:
  if top>5:add(box(f'column_{x}_{y}',(x,y,(top-1.0)/2),(3.2,3.2,top-1.0),'structure'))
 # central sky aperture landmark is a ring, intentionally open to the sky
 add(annulus_ribbon('CIVIC_VOID_OPEN_SKY_PERIMETER',-80,0,31))
 for i,t in enumerate(np.linspace(0,2*np.pi,16,endpoint=False)+np.pi/16):
  x=-80+78*np.cos(t);y=54*np.sin(t)
  add(box(f'civic_void_pylon_{i}',(x,y,14),(2.5,2.5,28),'structure'))
 scene=trimesh.Scene()
 for name,mesh in things:
  assert mesh.is_watertight,(name,'not watertight');scene.add_geometry(mesh,geom_name=name,node_name=name)
 data=trimesh.exchange.gltf.export_glb(scene);(OUT/'D34_CIVIC_THREE_LEVEL_REAL.glb').write_bytes(data)
 read=trimesh.load(OUT/'D34_CIVIC_THREE_LEVEL_REAL.glb',force='scene',process=False)
 counts={'glb_sha256':hashlib.sha256(data).hexdigest(),'meshes':len(read.geometry),'triangles':sum(len(m.faces) for m in read.geometry.values()),'watertight_meshes':sum(int(m.is_watertight) for m in read.geometry.values()),'site_study_only':True}
 (OUT/'D34_GEOMETRY_COUNTS.json').write_text(json.dumps(counts,indent=2))
 return counts
if __name__=='__main__':print(json.dumps(make(),indent=2))
