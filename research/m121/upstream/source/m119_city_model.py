#!/usr/bin/env python3
"""M119 deliberate sculpture-scale urban concept models, NO game IO.
Coordinates x/z/absolute Y are real Minecraft coordinate-frame proposals,
NOT an approved as-built replacement, protected mask or verified construction.
Existing material 8x8 cells are separate observational evidence layer.
"""
from __future__ import annotations
import json, math
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
ATLAS=json.loads((ROOT/'data/M117_USER_READONLY_ATLAS.json').read_text())
HERO={'SB05','SB08','SB09','SB12'}
CIVIC={'SB06','SB07','SB10','SB11'}
WARM='sandstone'; WHITE='pearl'; GLASS='glass'; DARK='structure'; CYAN='cyan'; GOLD='gold'; COURT='court'; GREEN='garden'
PROGRAM={
 'SB01':('West Lantern Trade Quarter','stacked lantern arcades','FRAME'),
 'SB02':('Artisan Spine','tiered workshop halls','FRAME'),
 'SB03':('Echo Market','multi-deck retail atrium','FRAME'),
 'SB04':('Rain Conservatory','giant rain-lit interior garden','FRAME'),
 'SB05':('RADIANT SAIL CITADEL','sky nave with three rising sails','HERO'),
 'SB06':('Civic Auditorium','terraced assembly forum','CIVIC'),
 'SB07':('Public Forum','open interlevel circular public core','CIVIC'),
 'SB08':('AURORA TWIN VAULT','two immense arch vaults and central atrium','HERO'),
 'SB09':('GRAND HALO GATEWAY','protected gateway framed by great threshold','HERO'),
 'SB10':('Transit Hall','multiple concourse decks','CIVIC'),
 'SB11':('Harmonic Assembly','spiral theater and terraces','CIVIC'),
 'SB12':('MOUNTAIN HALO SANCTUARY','five ridge terraces and open sky temple','HERO'),
 'SB13':('South Threshold District','preserved minimum 3x4 entry corridor','FRAME'),
 'SB14':('Orbital Machine Hall','industrial exhibition atria','FRAME'),
 'SB15':('Prism Studios','terraced glass creative district','FRAME'),
 'SB16':('Dusk Observation Ward','luminous sky gallery','FRAME'),
}
MATERIALS={WHITE:'#e7ece9',WARM:'#c5ac8e',GLASS:'#7caebc',DARK:'#1a2a30',CYAN:'#73c7d5',GOLD:'#dfaa5a',COURT:'#a3b5b7',GREEN:'#698d7d'}

def mesh(mid,v,faces,mat,site=None,role='envelope',note=''):
 return {'id':mid,'v':[[round(i,2) for i in p] for p in v], 'f':faces,'material':mat,'site':site,'role':role,'note':note,
 'approved_for_world_write':False,'collision_certified':False,'replaces_frozen_geometry':False}

def box(name,x0,z0,y0,x1,z1,y1,mat,site=None,role='envelope'):
 if not (x0<x1 and z0<z1 and y0<y1):raise ValueError((name,x0,z0,y0,x1,z1,y1))
 v=[[x0,z0,y0],[x1,z0,y0],[x1,z1,y0],[x0,z1,y0],[x0,z0,y1],[x1,z0,y1],[x1,z1,y1],[x0,z1,y1]]
 f=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
 return mesh(name,v,f,mat,site,role)

def section(name,x,z,y,wx,wz,height,mat,site=None,top_ratio=0.72):
 v=[[x-wx/2,z-wz/2,y],[x+wx/2,z-wz/2,y],[x+wx/2,z+wz/2,y],[x-wx/2,z+wz/2,y]]
 for dx,dz in [(-1,-1),(1,-1),(1,1),(-1,1)]:v.append([x+dx*wx*top_ratio/2,z+dz*wz*top_ratio/2,y+height])
 f=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
 return mesh(name,v,f,mat,site)

def sail(name,pts,thick,mat,site=None):
 # triangular pitched sail, physical-ish facade sheet thickness
 a,b,c=pts;v=[list(a),list(b),list(c),[a[0]+thick,a[1],a[2]],[b[0]+thick,b[1],b[2]],[c[0]+thick,c[1],c[2]]]
 return mesh(name,v,[[0,1,2],[5,4,3],[0,3,4,1],[1,4,5,2],[2,5,3,0]],mat,site)

def beam(name,p0,p1,w,h,mat,site=None,role='proposed_link'):
 (x0,z0,y0),(x1,z1,y1)=p0,p1;length=math.hypot(x1-x0,z1-z0)
 if length<1e-4:raise ValueError(name)
 dx=(z1-z0)/length*w/2;dz=-(x1-x0)/length*w/2
 v=[[x0-dx,z0-dz,y0-h/2],[x0+dx,z0+dz,y0-h/2],
    [x1+dx,z1+dz,y1-h/2],[x1-dx,z1-dz,y1-h/2],
    [x0-dx,z0-dz,y0+h/2],[x0+dx,z0+dz,y0+h/2],
    [x1+dx,z1+dz,y1+h/2],[x1-dx,z1-dz,y1+h/2]]
 f=[[0,3,2,1],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]
 return mesh(name,v,f,mat,site,role)

def plan_summary(site):
 ts=site['tiles'];x0=min(t['x'] for t in ts);x1=max(t['x']+8 for t in ts);z0=min(t['z'] for t in ts);z1=max(t['z']+8 for t in ts)
 return {'site':site['site'],'center':[(x0+x1)/2,(z0+z1)/2], 'tile_box':[x0,z0,x1,z1],
  'observed_y_min':site['real_world_min_artificial_y'],'observed_y_max':site['real_world_max_artificial_y'],
  'actual_building_like_blocks':site['artificial_blocks_exact'],'tiles':site['occupied_8x8_tiles']}

SITES={s['site']:plan_summary(s) for s in ATLAS['sites']}

def produce(variant):
 assert variant in ('A_CROWNED_MERIDIAN','B_FRACTURED_SKY_TERRACES')
 B=variant.startswith('B');g=[];voids=[];walk=[];rec=[]
 for sid,s in SITES.items():
  x,z=s['center'];x0,z0,x1,z1=s['tile_box'];y=s['observed_y_min']+6;top=s['observed_y_max'];wx=x1-x0;wz=z1-z0
  name,interior,kind=PROGRAM[sid]
  # Concept is a replacement-style massing survey envelope, not cumulative onto protected existing towers.
  rec.append({'site':sid,'name':name,'kind':kind,'proposed_primary_interior':interior,
    'built_observed_material_bounds':s,'new_geometry_clashes_with_existing_not_clearance_tested':True,
    'actual_indoor_walkable_route_certified':False,'frozen_legacy_mask_unresolved':True})
  if kind=='FRAME':
   tier=3 if sid in ('SB14','SB15','SB16') else 2
   g.append(section(sid+'_DISTRICT_SHOULDER',x,z,y,wx*.64,wz*.63,49+10*tier,WHITE,sid,.85 if B else .70))
   g.append(section(sid+'_SLANTED_LANTERN',x+(18 if sid in ('SB03','SB15') else -12),z,y+25,wx*.36,wz*.52,top-y+42,GLASS,sid,.58))
   for n in range(3):
    yy=y+26+n*21
    g.append(box(sid+f'_PLAZA_DECK_{n}',x0+12,z0+8,yy,x1-12,z1-8,yy+3,COURT,sid,'proposed_public_floor'))
  if kind=='CIVIC':
   # theatre split arcades: two tall sides and large genuinely open void in the middle
   pad=28 if B else 37
   height=top+57 if B else top+68
   g.append(box(sid+'_LEFT_HALL',x0+7,z0+6,y,x-pad,z1-6,height,WHITE,sid))
   g.append(box(sid+'_RIGHT_HALL',x+pad,z0+6,y,x1-7,z1-6,height,WHITE,sid))
   g.append(box(sid+'_SKY_BRIDGE',x-pad,z0+7,height-8,x+pad,z0+19,height,GLASS,sid,'proposed_public_bridge'))
   for n in range(3):
    yy=y+14+n*23
    g.append(box(sid+f'_PUBLIC_GALLERY_{n}',x-pad,z0+12,yy,x+pad,z0+21,yy+4,GOLD if n==2 else COURT,sid,'proposed_gallery'))
   voids.append({'id':sid+'_OPEN_HALL','site':sid,'x0':x-pad+4,'x1':x+pad-4,'z0':z0+26,'z1':z1-13,
                 'y0':y+3,'y1':height-10,'purpose':interior,'real_saved_blocks_not_removed':True})
  if sid=='SB05':
   # Five rising sails: open central nave, triangular folded blade volumes
   for n,(xp,dz) in enumerate([(-72,-30),(-35,27),(7,-18),(42,32),(76,-25)]):
    hh=(92,158,192,144,111)[n] if B else (122,143,166,143,122)[n]
    g.append(sail(f'SB05_CITADEL_SAIL_{n}',[(x+xp,z-38,y+24),(x+xp+35,z+dz,y+35),(x+xp+14,z+dz+6,y+hh)],4,WHITE if n%2==0 else GLASS,sid))
   g.append(box('SB05_GREAT_NAVE_ENTRY',x-43,z-52,y+12,x+43,z-39,y+31,DARK,sid,'portal_sculpture'))
   voids.append({'id':'SB05_SKY_NAVE','site':sid,'x0':x-43,'x1':x+42,'z0':z-32,'z1':z+28,'y0':y+11,'y1':y+155,'purpose':interior,'real_saved_blocks_not_removed':True})
  if sid=='SB08':
   # Two towering arch ribs, vertex Y is absolute Minecraft Y; central upper sky remains open
   base=y+8;archtop=y+(171 if B else 150)
   for sign in (-1,1):
    cx=x+sign*56
    for n in range(9):
     t0=n*math.pi/9;t1=(n+1)*math.pi/9
     p0=(cx-41*math.cos(t0),z-31,base+(archtop-base)*math.sin(t0))
     p1=(cx-41*math.cos(t1),z-31,base+(archtop-base)*math.sin(t1))
     p2=(p0[0],z+33,p0[2]);p3=(p1[0],z+33,p1[2])
     g.append(beam(f'SB08_ARCH_{sign}_{n}_SOUTH',p0,p1,9,9,WHITE,sid,'vault_rib'))
     g.append(beam(f'SB08_ARCH_{sign}_{n}_NORTH',p2,p3,9,9,WHITE,sid,'vault_rib'))
    g.append(box(f'SB08_AURORA_VAULT_GLASS_{sign}',cx-36,z-19,y+38,cx+36,z+19,y+43,GLASS,sid,'light_court'))
   voids.append({'id':'SB08_TWIN_ATRIUM','site':sid,'x0':x-25,'x1':x+25,'z0':z-30,'z1':z+30,'y0':y+10,'y1':archtop-8,'purpose':interior,'real_saved_blocks_not_removed':True})
  if sid=='SB09':
   # Two giant frame pylons around historic gate — construction-overlap NOT checked.
   high=top+(90 if B else 76)
   for sign in (-1,1):
    cx=x+sign*79
    g.append(section('SB09_GATE_TOWER_'+str(sign),cx,z,y+3,36,50,high-y-3,DARK,sid,.60))
    g.append(sail('SB09_CROWN_WING_'+str(sign),[(cx-17,z-29,high-38),(cx+17,z+23,high-21),(cx,z+5,high+49)],5,WHITE,sid))
   g.append(box('SB09_CEREMONIAL_UPPER_BEAM',x-84,z-12,high-9,x+84,z+12,high+7,WHITE,sid,'gateway_overpass'))
   voids.append({'id':'SB09_HISTORIC_UPPER_GATE_RESERVED','site':sid,'x0':x-51,'x1':x+51,'z0':z-31,'z1':z+31,'y0':y+12,'y1':high-14,'purpose':'preserve existing SB09 entrance; geometry NOT certified','real_saved_blocks_not_removed':True})
  if sid=='SB12':
   for n in range(5):
    ty=y+24+n*(24 if B else 20);pad=10+n*11
    g.append(box('SB12_RIDGE_DECK_'+str(n),x0+pad,z0+5+n*9,ty,x1-pad,z1-5-n*7,ty+6,WHITE if n%2==0 else GREEN,sid,'sanctuary_terrace'))
   g.append(section('SB12_MOUNTAIN_LANTERN',x,z,y+139,80,66,86 if B else 65,GLASS,sid,.28))
   voids.append({'id':'SB12_SKY_SANCTUARY','site':sid,'x0':x-47,'x1':x+47,'z0':z-25,'z1':z+25,'y0':y+11,'y1':y+143,'purpose':interior,'real_saved_blocks_not_removed':True})
  # one architectural entrance idea; NOT a working entrance
  walk.append({'from':sid+'_PUBLIC_LOBBY','to':sid+'_PRIMARY_INTERIOR','status':'INTENT_ONLY_NO_REAL_WORLD_PATH_VALIDATION'})
 # Architectural heart: two suspended perimeter galleries enclose an intentionally huge sky void.
 # This is a MAJOR CONCEPTUAL replacement form above currently occupied urban ground,
 # NOT proof that historic roads/structures can be cleared or that decks are walkable.
 core_x,core_z=3703.5,-2184.5
 for level,(rx,rz,h) in enumerate([(160,103,-1687),(205,134,-1638)] if B else [(167,112,-1678)]):
  n=50
  for i in range(n):
   t0=2*math.pi*i/n;t1=2*math.pi*(i+1)/n
   if B and level==1 and (.2*math.pi < (t0+t1)/2 < .47*math.pi):continue
   p0=(core_x+rx*math.cos(t0),core_z+rz*math.sin(t0),h+6*math.sin(2*t0))
   p1=(core_x+rx*math.cos(t1),core_z+rz*math.sin(t1),h+6*math.sin(2*t1))
   g.append(beam(f'M119_CIVIC_ATRIUM_GALLERY_L{level}_{i}',p0,p1,20,5,WHITE,'CIVIC_CORE','unconnected_sky_gallery'))
  for i in range(0,n,10):
   t0=2*math.pi*i/n
   x=core_x+rx*math.cos(t0);z=core_z+rz*math.sin(t0)
   g.append(section(f'M119_CIVIC_MONUMENTAL_GALLERY_GATE_L{level}_{i}',x,z,h-37,29,30,67,DARK,'CIVIC_CORE',.38))
 # Massive wing terraces introduce the distinctive layered skyline away from thin rings.
 if B:
  for index,(dx,dz,ww,zz,yy) in enumerate([(-230,-97,164,58,-1717),(210,89,173,61,-1704),(-161,164,115,56,-1665),(144,-180,132,56,-1656)]):
   x=core_x+dx;z=core_z+dz
   g.append(section(f'M119_CIVIC_SUSPENDED_LATERAL_WING_{index}',x,z,yy,ww,zz,18,WHITE,'CIVIC_CORE',.86))
   g.append(box(f'M119_CIVIC_GARDEN_CROWN_{index}',x-ww*.40,z-zz*.32,yy+18,x+ww*.40,z+zz*.32,yy+24,GREEN,'CIVIC_CORE','unverified_garden_terrace'))
 # Whole-city broken/continuous megastructure: visually high sky frame, disconnected segments noted
 cx,cz=3703.5,-2184.5
 for band,(rx,rz) in enumerate(((575,319),(686,392))):
  n=112
  for i in range(n):
   t0=2*math.pi*i/n;t1=2*math.pi*(i+1)/n;mid=(t0+t1)/2
   # two large void breaches facing north-east and south-west in B; continuous for A
   if B and ((.21*math.pi<mid<.38*math.pi) or (1.21*math.pi<mid<1.41*math.pi) or (band==1 and 1.77*math.pi<mid<1.91*math.pi)):
    continue
   def v(t):
    yy=-1650 + band*45+(21*math.sin(t*2.5+band) if B else 4*math.sin(t))
    return cx+rx*math.cos(t), cz+rz*math.sin(t), yy
   p0,p1=v(t0),v(t1)
   g.append(beam(f'M119_ORBITAL_B{band}_S{i:03}',p0,p1,35 if band==0 else 23,10,DARK,'MACRO','ORBital-UNAPPROVED'))
   g.append(beam(f'M119_SKY_WALK_B{band}_S{i:03}',(p0[0],p0[1],p0[2]+7),(p1[0],p1[1],p1[2]+7),27 if band==0 else 16,4,WHITE,'MACRO','unverified_orbital_public_deck'))
   if i%9==0:
    x,z,y=v(t0)
    g.append(section(f'M119_OUTER_GATE_{band}_{i}',x,z,y-72,40,42,104,WHITE if i%2==0 else DARK,'MACRO',.5))
  
 # Large promenade intent: not validated, not an accessible route
 public=[('SB13','SB09'),('SB09','SB10'),('SB10','SB06'),('SB06','SB07'),('SB07','SB08'),('SB07','SB11'),('SB11','SB12'),('SB05','SB06')]
 for a,b in public:
  walk.append({'from':a,'to':b,'status':'INTENT_ONLY_NOT_SOLVED','protected_void_cleared':False})
 # paired grand public sky voids, intentional ground/public realm gap not necessarily unobstructed in saved world
 for n,(x,z,sx,sz) in enumerate([(3704,-2185,150,77),(3710,-2110,120,41)] if B else [(3704,-2185,130,100)]):
  voids.append({'id':'MEGACITY_SKY_COURT_'+str(n),'site':None,'x0':x-sx,'x1':x+sx,'z0':z-sz,'z1':z+sz,'y0':-1820,'y1':-1610,
    'purpose':'large multilayer public void; old world and protected-collision UNCHECKED','real_saved_blocks_not_removed':True})
 return {'phase':'M119','variant':variant,'research_not_approved':True,'minecraft_save_to_modify':None,
         'reference_review_copy':'CH9_D6D_REVIEW_COPY','world_y_for_rendering':'Minecraft absolute Y proposal, matched XY to observed tile coordinates',
         'model_relative_H_mapping_still':'UNKNOWN','world_writes':0,'protected_mesh_collision_certified':False,
         'all_facility_entrances_walkable':False,'protected_existing_geometry_intentionally_unmodified':True,
         'observed_legacy_blocks_deleted':0,'meshes':g,'facility_programs':rec,'proposed_courts_and_voids':voids,
         'unverified_route_intents':walk,
         'warnings':['PROPOSED geometry overlaps existing occupied land intentionally as REPLACEMENT CONCEPT; not additive施工',
          'No protected Frozen408 mapping to saved voxels; zero collision certifications',
          'Outer rings exceed verified 16 parcels; site and terrain rights unknown',
          'Neither Minecraft save is authorized for world edits or piloting',
          'Relative H to actual Y is still unknown; this proposal is placed in observed saved absolute coordinate frame for visual study only']}

if __name__=='__main__':
 for v in ('A_CROWNED_MERIDIAN','B_FRACTURED_SKY_TERRACES'):
  p=produce(v);out=ROOT/'data'/('M119_'+v+'.json');out.write_text(json.dumps(p,ensure_ascii=False,separators=(',',':')))
  print(v,len(p['meshes']),len(p['facility_programs']),len(p['proposed_courts_and_voids']),out)
