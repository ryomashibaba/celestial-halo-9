"""CELESTIAL HALO-9 J7-R2: independent sculpted civic stratum research.

NOT canonical coordinates, not adopted central artwork, not Minecraft construction.
Model the vast INNER public void by actual volumetric subtraction from an integrated
inhabited structural mass; cut interior upper galleries through the volume.
"""
import numpy as np, trimesh, json, hashlib
from skimage.measure import marching_cubes
from pathlib import Path
from collections import Counter
import math

OUT=Path(__file__).parent
OUT.mkdir(parents=True,exist_ok=True)
scene=trimesh.Scene()
roles=[]
COLORS={
 'SHELL': [129,157,171,255], 'FAULT': [35,54,70,255], 'CUT': [242,228,202,255],
 'GOLD': [221,171,107,255], 'WALK': [98,154,154,255], 'CITY': [217,232,230,255],
 'DARK': [34,55,73,255], 'LIGHT': [105,190,204,255], 'NATURE': [59,80,84,255], 'WATER': [48,99,120,255]
}
def add(n,m,mat,role):
 if len(m.faces)==0:return
 m.visual.vertex_colors=np.tile(np.array(COLORS[mat],dtype=np.uint8),(len(m.vertices),1))
 m.metadata={'role':role,'material':mat,'stage':'RESEARCH_NOT_CANON'}
 scene.add_geometry(m,geom_name=n,node_name=n)
 roles.append({'name':n,'role':role,'material':mat,'vertices':len(m.vertices),'faces':len(m.faces),'watertight':bool(m.is_watertight)})
def box(n,c,d,mat,role):
 m=trimesh.creation.box(extents=d);m.apply_translation(c);add(n,m,mat,role)
def beam(n,a,b,r,mat,role):
 a=np.array(a,float);b=np.array(b,float)
 m=trimesh.creation.cylinder(radius=r,segment=np.array([a,b]),sections=12);add(n,m,mat,role)
def panel(n,path,halfwidth,thick,mat,role):
 p=np.array(path,float);vv=[];ff=[]
 for i,q in enumerate(p):
  tan=p[min(i+1,len(p)-1)]-p[max(i-1,0)]
  left=np.array([-tan[1],tan[0],0.]);left/=max(np.linalg.norm(left),1e-8)
  # width variable, prevent constant flat shelf silhouette
  w=halfwidth*(1+.13*math.sin(i*.8))
  vv.extend([q-left*w+[0,0,-thick],q+left*w+[0,0,-thick],q+left*w,q-left*w])
 for i in range(len(p)-1):
  a=i*4;b=(i+1)*4
  for k in range(4):ff.extend([[a+k,a+(k+1)%4,b+(k+1)%4],[a+k,b+(k+1)%4,b+k]])
 ff.extend([[0,1,2],[0,2,3]]);b=(len(p)-1)*4;ff.extend([[b,b+2,b+1],[b,b+3,b+2]])
 add(n,trimesh.Trimesh(vertices=np.array(vv),faces=np.array(ff),process=False),mat,role)

def sdf_super(x,y,z,c,rad,p=3):
 # Direct normalized implicit field in m using superellipsoid 3-norm; capable
 # of thick horizontal inhabitable city-strata, rather than a cone tower.
 ax=np.abs((x-c[0])/rad[0]);ay=np.abs((y-c[1])/rad[1]);az=np.abs((z-c[2])/rad[2])
 return ((ax**p+ay**p+az**p)**(1/p)-1)*min(rad)
def carve_ell(x,y,z,c,rad,p=2.3):
 return sdf_super(x,y,z,c,rad,p)
def smooth_union(a,b,k):
 h=np.clip(.5+.5*(b-a)/k,0,1)
 return (b*(1-h)+a*h)-k*h*(1-h)

def make_terrain_mass():
 # World is noncanonical 10km study only, and does not claim final W0.
 xx=np.arange(-4100,4100,42,dtype=np.float32)
 yy=np.arange(-3050,3050,42,dtype=np.float32)
 zz=np.arange(-600,4800,42,dtype=np.float32)
 X=xx[:,None,None];Y=yy[None,:,None];Z=zz[None,None,:]
 # two long continental forms and an overhanging lenticular crown are united
 # and cut away *after* union, allowing genuine non-opaque openings.
 params=[
  ('west_understory',(-1540,-280,590),(2080,1550,780),5.0),
  ('west_inhabited_fold',(-1810,40,1500),(1860,1550,840),5.0),
  ('west_wing_crest',(-1690,370,2400),(1770,1280,680),4.5),
  ('west_free_edge',(-1180,600,2980),(1340,1050,390),3.6),
  ('east_understory',(1420,220,590),(1890,1500,780),5.3),
  ('east_civic_rise',(1790,50,1590),(1640,1400,1090),5.0),
  ('east_resident_cliff',(2110,380,2830),(1350,1180,950),4.8),
  ('east_crest',(2210,710,3760),(1060,960,570),4.0),
  ('high_civic_ceiling',(70,320,2860),(2130,710,470),3.6),
 ]
 field=None
 for n,c,rad,p in params:
  g=sdf_super(X,Y,Z,c,rad,p)
  field=g if field is None else smooth_union(field,g,95 if 'ceiling' not in n else 140)
  print('UNION',n,flush=True)
 # asymmetrical tear in the city-sized vaulted civic hall: open both sides
 # and two public rooms in LEFT and RIGHT, non-empty open volumes.
 cavities=[
  ('CIVIC_LONG_VAULT',(0,-620,1730),(1390,1870,940),3.3),
  ('CIVIC_HIGH_OCULUS',(160,180,2690),(490,620,540),2.5),
  ('WEST_PUBLIC_LIBRARY',(-1710,-1350,1360),(1020,790,490),3.5),
  ('EAST_PUBLIC_NAVE',(1650,-1310,1780),(1050,960,610),3.5),
  ('EAST_HIGH_GALLERY',(2190,-1060,2970),(750,840,310),2.5),
  ('WEST_LOWER_PUBLIC_ROOM',(-1550,-1150,740),(840,900,270),2.8),
 ]
 # caverns are actual mesh holes, not darker overlays
 for n,c,r,p in cavities:
  g=carve_ell(X,Y,Z,c,r,p)
  field=np.maximum(field,-g)
  print('CARVE',n,flush=True)
 # broad horizontal tectonic faults in walls with shallow relief; deliberate,
 # not a repeated whole-level ring of tiny building boxes.
 front_warp=(34*np.sin(X/370+Z/920)+22*np.sin(Y/250+Z/650))
 field+=front_warp
 # spatial grid provides actual carved cutaways, not image reference only
 verts,faces,normals,values=marching_cubes(field,level=0,spacing=(42,42,42),allow_degenerate=False)
 verts+=np.array([xx[0],yy[0],zz[0]])
 mass=trimesh.Trimesh(vertices=verts,faces=faces,process=False)
 # normal orientation corrected by trimesh if necessary for exterior
 if mass.volume<0:mass.invert()
 # Classify cut surfaces from actual 3D cavities; the cavity is truly excavated.
 fc=mass.triangles_center
 cut_near=np.zeros(len(fc),dtype=bool)
 for _,c,r,p in cavities:
  signed=carve_ell(fc[:,0],fc[:,1],fc[:,2],c,r,p)
  cut_near|=(np.abs(signed)<90)
 roof=(mass.face_normals[:,2]>.47)&~cut_near
 groups={'SHELL':(~cut_near)&(~roof),'CUT':cut_near,'CITY':roof}
 face_counts={}
 for mat,mask in groups.items():
  sub=mass.submesh([np.flatnonzero(mask)],append=True,repair=False)
  add('CARVED_CITY_MASS_'+mat,sub,mat,'volumetric_carved_civic_mass_surface_'+mat.lower())
  face_counts[mat]=int(mask.sum())
 assert sum(face_counts.values())==len(faces)
 print('MODEL',len(verts),len(faces),'bounds',mass.bounds,'watertight',mass.is_watertight,'zone_faces',face_counts,flush=True)
 return { 'sample_pitch_m':42,'implicit_components':params,'carved_cavities':cavities,
          'mesh_vertices':len(verts),'mesh_faces':len(faces),'surface_zones_triangles':face_counts,
          'bounds_m':mass.bounds.tolist(),'watertight_before_material_split':bool(mass.is_watertight)}

def detailed_cutaways():
 # floor systems of a very large real CARVED room, directly rooted in cavity geometry
 # (representative only: no collision/walking certification)
 for side,cx,cy,rad,zs in [
    ('WEST',-1650,-1160,570,[770,1130,1420]),
    ('EAST',1640,-1060,655,[1150,1620,1980]),
    ('EAST_HIGH',2280,-940,420,[2820,3000])]:
  for i,z in enumerate(zs):
   path=[]
   for j in range(19):
    t=.12+2.9*j/18
    x=cx+rad*math.cos(t)
    y=cy-240+400*math.sin(t)
    path.append([x,y,z+80*math.sin(t)*math.sin(i+.3)])
   panel(f'{side}_CARVED_ROOM_SHARED_CITY_GALLERY_{i}',path,74,45,'CUT','public_floor_in_carved_civic_room_unverified')
   # window into real room -- pier walls and ceiling must remain visible behind floor
   for j in (1,5,10,16):
    a=path[j];b=path[j+1]
    beam(f'{side}_ROOM_EDGE_FIN_{i}_{j}',[a[0],a[1],a[2]-40],[a[0]+35,a[1]+25,a[2]+140],17,'FAULT','civic_room_support_exploratory')
 # central ceremonial sky-court is intentionally not filled with a cylinder
 # four enormous asymmetrical radial suspended civic struts outside its opening
 for i,(a,b) in enumerate([
  ((-1040,-1200,1210),(-500,190,1850)),
  ((820,-1200,1500),(440,340,2070)),
  ((-800,580,2450),(-140,50,2710)),
  ((1050,660,2460),(520,50,2660)),
 ]):
  panel(f'CIVIC_VAULT_BUTTRESS_{i}',[a,[(a[0]+b[0])*.5,(a[1]+b[1])*.5,(a[2]+b[2])*.5+120],b],85,90,'FAULT','civic_vault_structural_fin_unverified')
 # layer district indices on inner curve of mass, residents and connecting station
 # no hundreds of floating buildings; city facade recesses are integrated sections
 # near the mountainsides outside main architectural negative space
 for side,sign in [('WEST',-1),('EAST',1)]:
  for level,z in enumerate([550,1000,1520,2200,2820] if sign<0 else [550,1040,1640,2260,3080,3710]):
   for i in range(7):
    y=-650+i*230
    x=sign*(2600-140*math.sin((i+level)*.9))
    # a few stepped protruding civic roof fins aligned with original cliff face
    p=[[x,y-80,z-140],[x-sign*110,y,z+40],[x-sign*270,y+150,z+140]]
    panel(f'{side}_TECTONIC_CITY_SEAM_{level}_{i}',p,40,18,'FAULT','integrated_terrace_joint_study')
  for level,z in enumerate([680,1420,2200] if sign<0 else [830,1750,2700,3400]):
   # actual large civic observation plazas keyed into exterior landmass
   p=[]
   for i in range(9):
    t=i/8;y=-760+t*1530
    x=sign*(2500-140*math.sin(t*4+level*.6))
    p.append([x,y,z+50*math.sin(t*math.pi)])
   panel(f'{side}_PUBLIC_URBAN_EDGE_{level}',p,115,40,'CUT','visible_habitable_city_edge_unverified')
 # broad stadium-like transport spine with a deliberate free arch crossing the void
 # Still not continuous public access PASS.
 paths={
 'LOW_CROSS_CITY':[[-2030,-200,940],[-1250,-100,1030],[-530,60,1200],[100,190,1250],[780,140,1320],[1890,50,1520]],
 'HIGH_TRANSIT':[[-1900,720,2370],[-1000,640,2460],[-240,360,2640],[460,450,2780],[1400,530,3000],[2040,640,3240]],
 }
 for key,pts in paths.items():panel(key+'_MEGACITY_FLOOR',pts,115,65,'CUT','interbank_public_transport_deck_unverified')
 # occasional structural carrying ribs with changing tangent, NOT many repetitive lines
 for k,(a,b) in enumerate([
    ((-870,-1300,460),(-1100,-740,2460)),
    ((1100,-1450,430),(1420,-580,2980)),
    ((-1360,1040,980),(-820,620,2880)),
    ((1640,1120,1020),(2110,780,3440)),
 ]):
  panel(f'LONG_CIVIC_SPINE_{k}',[a,[(a[0]+b[0])/2,(a[1]+b[1])/2,(a[2]+b[2])/2],b],78,62,'FAULT','structural_carrying_spline_unverified')

def ground():
 # noncanonical W0 context; deliberately desaturated and gentle to keep source-scale
 # comparison with R1 (unvalidated dimensions/locations)
 box('W0_NONCANONICAL_STUDY_CONTEXT',[0,0,-150],[10000,10000,150],'NATURE','noncanonical_w0_study_frame')
 box('W0_STUDY_EAST_SEA',[4320,400,-70],[1340,6200,10],'WATER','noncanonical_sea_placeholder')
 # landscape relief north is background reference not completed W0 terrain
 x=np.linspace(-4800,4800,44);y=np.linspace(2900,5000,13)
 xx,yy=np.meshgrid(x,y,indexing='ij')
 zz=90+160*np.sin(xx/850+yy/1250)**2+100*np.sin(xx/350+yy/410)**2
 V=np.stack([xx,yy,zz],-1).reshape(-1,3)
 F=[]
 for i in range(len(x)-1):
  for j in range(len(y)-1):
   a=i*len(y)+j;b=a+len(y)
   F.extend([[a,b,a+1],[a+1,b,b+1]])
 add('W0_NORTH_TERRAIN_ONLY_STUDY',trimesh.Trimesh(vertices=V,faces=np.array(F),process=False),'NATURE','noncanonical_mountain_placeholder')

if __name__=='__main__':
 mass=make_terrain_mass();detailed_cutaways();ground()
 path=OUT/'J7R2_SCULPTED_CIVIC_CUTAWAY_NONCANONICAL.glb'
 data=scene.export(file_type='glb')
 path.write_bytes(data)
 scene2=trimesh.load(path,force='scene',process=False)
 assert len(scene2.geometry)==len(scene.geometry),(len(scene2.geometry),len(scene.geometry))
 # Explicit source metadata, readback metrics, no finished-art claims
 meta={'schema':'halo9.j7r2.source_and_mesh_qa.v1','date':'2026-10-24 JST','source':'J7-R1 rejected; new volumetric Boolean carve + multi-height public galleries; standalone study',
       'method':'signed superellipsoid union/subtract + 42m grid marching_cubes; NOT Blender and NOT canonical','mass':mass,
       'geometry_count':len(scene.geometry),'readback_geometry_count':len(scene2.geometry),'glb_size_bytes':len(data),
       'glb_sha256':hashlib.sha256(data).hexdigest(),
       'vertices':sum(len(g.vertices) for g in scene.geometry.values()),'triangles':sum(len(g.faces) for g in scene.geometry.values()),
       'roles':dict(Counter(o['role'] for o in roles)), 'objects':roles,
       'actual_bounds_m':scene2.bounds.tolist(),'blender_import':'NOT_TESTED','room_walkability':'NOT_TESTED','full_urban_interior':'NOT_COMPLETE',
       'multiview_aesthetic_verdict':'PENDING','formal_art_adoptions':0,'construction':'HOLD',
       'warnings':['Public room void is boolean cut but not certified accessible','Small seam surfaces can intersect body; full mesh clash not checked',
                   'W0/H/SB canonical placement absent','Voxel pitch 42m does not show detailed facades','General building exterior and full public interiors not completed']}
 (OUT/'J7R2_MESH_AND_LIMITATIONS.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf-8')
 print(json.dumps({'glb':str(path),'bytes':len(data),'objects':len(scene.geometry),'vertices':meta['vertices'],'faces':meta['triangles'],'bounds':meta['actual_bounds_m']},indent=2))