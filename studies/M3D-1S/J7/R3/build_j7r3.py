"""CELESTIAL HALO-9 / J7-R3 study of OPEN inhabitable civic cross-sections.
Independent NONCANONICAL research art. No Minecraft construction or art adoption.
All structures are real editable meshes. No SDF enclosed opaque shell.
"""
import os, json, math, hashlib
from pathlib import Path
from collections import Counter
import numpy as np
import trimesh
OUT=Path(__file__).resolve().parent
scene=trimesh.Scene(); records=[]
PALETTE={
 'NACRE':[214,228,226,255], 'ALABASTER':[230,225,209,255], 'FRAME':[91,122,142,255],
 'GRAPHITE':[38,60,78,255], 'CERAMIC':[162,190,198,255], 'AZURE':[78,167,196,255],
 'BRONZE':[185,139,101,255], 'GREEN':[97,143,133,255], 'WATER':[40,104,131,255],
 'VOID':[19,38,53,255], 'GOLD':[235,200,145,255]}
def add(name, mesh, mat, role):
 if mesh is None or not len(mesh.faces):return
 assert isinstance(mesh,trimesh.Trimesh),name
 mesh.visual.vertex_colors=np.tile(np.array(PALETTE[mat],dtype=np.uint8),(len(mesh.vertices),1))
 mesh.metadata={'role':role,'material':mat,'authored_as':'noncanonical_independent_geometry'}
 scene.add_geometry(mesh,geom_name=name,node_name=name)
 records.append({'id':name,'role':role,'material':mat,'v':len(mesh.vertices),'f':len(mesh.faces),
   'bounds':np.round(mesh.bounds,2).tolist()})
def box(name,center,ext,mat,role):
 m=trimesh.creation.box(extents=ext);m.apply_translation(center);add(name,m,mat,role)
def capsule(name,a,b,r,mat,role,sections=12):
 a=np.array(a,float);b=np.array(b,float)
 if np.linalg.norm(a-b)<1:return
 m=trimesh.creation.cylinder(radius=r,segment=np.array([a,b]),sections=sections)
 add(name,m,mat,role)
def prism(name,poly,z0,z1,mat,role,topshift=(0,0)):
 p=np.asarray(poly,float);n=len(p)
 q=p+np.asarray(topshift)
 v=np.vstack([np.c_[p,np.full(n,z0)],np.c_[q,np.full(n,z1)]])
 f=[]
 for k in range(1,n-1):f.extend([[0,k+1,k],[n,n+k,n+k+1]])
 for k in range(n):
  kk=(k+1)%n
  f.extend([[k,kk,n+kk],[k,n+kk,n+k]])
 add(name,trimesh.Trimesh(vertices=v,faces=f,process=False),mat,role)
def planegrid(name,points,mat,role,thickness):
 """A distinct folded thickened surface, all boundary edges walled. points (rows, cols, 3)."""
 g=np.asarray(points,float);rows,cols,_=g.shape;V=g.reshape(-1,3);Vlo=V.copy();Vlo[:,2]-=thickness
 v=np.vstack([V,Vlo]);N=len(V);faces=[]
 def idx(r,c):return r*cols+c
 for r in range(rows-1):
  for c in range(cols-1):
   a=idx(r,c);b=idx(r,c+1);d=idx(r+1,c);e=idx(r+1,c+1)
   faces.extend([[a,b,e],[a,e,d],[N+a,N+e,N+b],[N+a,N+d,N+e]])
 order=[]
 for c in range(cols):order.append(idx(0,c))
 for r in range(1,rows):order.append(idx(r,cols-1))
 for c in range(cols-2,-1,-1):order.append(idx(rows-1,c))
 for r in range(rows-2,0,-1):order.append(idx(r,0))
 for a,b in zip(order,order[1:]+[order[0]]):faces.extend([[a,N+b,b],[a,N+a,N+b]])
 m=trimesh.Trimesh(vertices=v,faces=faces,process=False)
 add(name,m,mat,role)
def art_stratum(name,origin_y,segments,mat):
 """Segments are explicit x, y, centre_z, lateral_width, longitudinal_width, underdeep;
 not a lofted closed monolith. Each city's open urban levels are separately built."""
 grid=[]
 for i,(x,y,z,w,span,dep) in enumerate(segments):
  # a jagged faceted folded geography, separate south/north streets and public voids visible
  section=[]
  for j,t in enumerate([-1,-.67,-.30,.13,.62,1]):
   pz=z+145*math.sin((i+1)*.62 +j*1.2)+130*(.5-abs(t))
   section.append([x+w*t+62*math.sin(i*2.1+j*.6),origin_y+y+90*math.sin(i*.9+j*.5),pz])
  grid.append(section)
 planegrid(name,grid,mat,'inhabited_folded_ground_exposed_structure',thickness=240)
 for n,seg in enumerate(segments):
  x,y,z,w,span,dep=seg
  if n%2==0:
   # a distinct city-sized escarpment edge rather than tiny balconies
   a=[x-w*.81,origin_y+y-260,z-155];b=[x+w*.71,origin_y+y-240,z-155]
   capsule(name+'_TEETH_'+str(n),a,b,34,'GRAPHITE','urban_cliff_load_path_incomplete')
 return
# explicit two asymmetric *open* urban continents, with no box wall occluding their city sections
art_stratum('WEST_COAST_FOLDED_INHABITED_GROUND',-350,
 [(-2420,-1450,490,970,350,270),(-2460,-820,760,1240,350,270),(-2520,10,1040,1560,350,290),(-2340,750,1460,1480,350,310),(-1950,1510,2150,970,350,290)],'CERAMIC')
art_stratum('EAST_HIGH_TECTONIC_CITY',370,
 [(2190,-1580,540,1220,350,290),(2320,-790,870,1350,350,280),(2250,0,1480,1450,350,270),(2140,750,2480,1330,350,300),(1800,1560,3690,680,320,240)],'NACRE')
# second axial bands are wide, separate and sliced by *open air*, not painted onto opaque wall
art_stratum('WEST_UPPER_SKY_CAMPUS',550,
 [(-2320,-1600,1310,760,250,220),(-2140,-900,1740,1080,290,240),(-1980,-100,2170,1110,300,250),(-1690,740,2720,690,280,220)],'NACRE')
art_stratum('EAST_LONGHORIZON_PUBLIC_CITY',-580,
 [(2130,-1720,1150,910,250,200),(2010,-1010,1560,1020,300,230),(1880,-230,2250,1080,300,230),(1670,700,3180,570,280,210)],'ALABASTER')
# a steep geometric 'UPTURNED HORIZON' has a silhouette different from rings, boxes and stone domes
# three folded thin but kilometer-scale wing faces tether into inhabited grounds
wing_specs=[
 ('SKY_HORIZON_BROKEN_CROWN',[(1600,-740,3010), (880,-200,3510), (160,400,4040),(-900,1020,4370)],
  [450,590,700,130],[120,120,100,64],'NACRE'),
 ('WEST_FREE_EDGE_WINDWARD', [(-3050,-620,1820),(-2840,220,2580),(-2220,1040,3470),(-1450,1660,3850)],
  [480,500,460,50],[115,115,90,48],'ALABASTER'),
 ('EAST_SPIRE_FOLD',[ (3030,-1300,1050),(2990,-490,1800),(2660,420,3180),(2000,1230,4520)],
  [260,490,540,38],[150,135,100,36],'CERAMIC')]
for name,spans,widths,thicks,mat in wing_specs:
 pts=[]
 for ix,p in enumerate(spans):
  x,y,z=p;W=widths[ix]
  # paired folded structural creases, not an isolated board: face has 2D geometric ridges
  pts.append([[x-W,y-110,z-50],[x-W*.42,y-35,z+110],
              [x+W*.18,y+80,z+220],[x+W,y+160,z-95]])
 planegrid(name,pts,mat,'structural_sky_crown_mass_not_habitable_yet',thickness=170)
 for j in range(len(spans)-1):
  a=np.array(spans[j]);b=np.array(spans[j+1]);
  capsule(name+'_STRUCTURAL_SPINE_'+str(j),a+[0,0,-140],b+[0,0,-140],40,'GRAPHITE','exposed_diagonal_cantilever_support')
# Civic NAVE: genuine open public hall with *separate floor, back wall and roof*, no overlaid black rectangles
# South opens toward viewer and north opens toward habitable west/east city
hall=[(-1180,-950,1300),(-650,-900,1350),(0,-870,1420),(740,-760,1580),(1170,-550,1730)]
# broad 240m public spine, material mass thickness 65
L=[]
for i,(x,y,z) in enumerate(hall):
 L.append([[x,y-170,z],[x,y-60,z+15],[x,y+95,z+20],[x,y+185,z+10]])
planegrid('NAVE_MAIN_PROCESSIONAL_FLOOR',L,'ALABASTER','genuine_public_hall_floor_open',thickness=85)
# The overhead shell intentionally opens below, and roof has open slit at middle; two waves folded as unique wings
Lroof1=[];Lroof2=[]
for i,(x,y,z) in enumerate(hall):
 Lroof1.append([[x,y-130,z+570],[x,y-15,z+705],[x,y+85,z+580]])
 Lroof2.append([[x,y+110,z+520],[x,y+200,z+640],[x,y+305,z+450]])
planegrid('NAVE_VAULT_SUSPENDED_NORTH_FOLD',Lroof1,'NACRE','actual_civic_room_roof_structure',thickness=110)
planegrid('NAVE_VAULT_SUSPENDED_SOUTH_FOLD',Lroof2,'ALABASTER','actual_civic_room_roof_structure',thickness=95)
for k,(x,y,z) in enumerate(hall):
 if k in [0,1,3,4]:
  # publicly accessible columns separate enough for actual large room
  capsule('NAVE_TENSION_PIER_'+str(k),[x,y+140,z+20],[x+65,y+70,z+560],30,'GRAPHITE','structural_room_column')
  capsule('NAVE_LIGHT_REVEAL_'+str(k),[x-30,y-150,z+90],[x+20,y-120,z+500],13,'AZURE','nave_wayfinding_luminance')
# A crossing public gallery and sky trains: in open space, visibly occupy the same urban mass, not wall-mounted props
paths={
 'LOWER_EAST_WEST_PUBLIC_SPINE':[(-2550,-350,820),(-1880,-280,1130),(-1100,-240,1330),(-460,-180,1550),(300,50,1850),(900,300,2110),(1680,530,2360),(2290,690,2610)],
 'UPPER_CIVIC_TRANSIT':[(-2320,950,2340),(-1780,600,2700),(-1050,300,2980),(-250,70,3280),(520,-50,3510),(1320,250,3720),(1930,800,4020)],
 'CANYON_VALLEY_ROUTE':[(-2800,-1350,520),(-1750,-1300,750),(-850,-1200,960),(0,-1120,1230),(960,-970,1530),(2000,-1020,1660),(2600,-1180,1540)]}
for name,path in paths.items():
 mesh=[]
 for k,(x,y,z) in enumerate(path):mesh.append([[x,y-85,z],[x,y-55,z+7],[x,y+55,z+7],[x,y+85,z]])
 planegrid(name,mesh,'CERAMIC' if 'LOWER' in name else 'BRONZE','actual_3d_transport_spine_unverified_grade',thickness=70)
 for i,p in enumerate(path[1:-1]):
  if i%2==0:capsule(name+'_LIGHT_MAST_'+str(i),p,np.array(p)+[0,0,115],15,'AZURE','city_public_signage')
# Geologically asymmetrical 3D lift bays: open ribs, terminal stations, enterable public floor
for side,c in [('WEST',(-2000,450)),('EAST',(2100,440))]:
 levels=([550,1300,2150,2880] if side=='WEST' else [680,1650,2670,3720])
 for k in range(4):
  ang=k*math.pi/2;dx=115*math.cos(ang);dy=115*math.sin(ang)
  capsule(side+'_LIFT_GUIDE_'+str(k),[c[0]+dx,c[1]+dy,levels[0]],[c[0]+dx,c[1]+dy,levels[-1]],24,'GRAPHITE','actual_vertical_rail')
 for j,z in enumerate(levels):
  poly=np.array([[c[0]-215,c[1]-125],[c[0]+185,c[1]-125],[c[0]+230,c[1]+95],[c[0]-155,c[1]+155]])
  prism(side+'_PUBLIC_VERTICAL_INTERCHANGE_'+str(j),poly,z-38,z+16,'ALABASTER','open_transport_interchange_floor')
# An inhabited *cliff section* with identifiable urban architecture rather than symbols on a shell
# Four long high-altitude avenues, housing blocks with irregular footprints and explicit civic gaps
terraces=[('W_LOW',-2440,-250,1110,7),('W_HIGH',-1900,820,2190,5),
          ('E_LOW',2020,-300,1550,8),('E_HIGH',1740,850,3190,6)]
for id,cx,cy,z,n in terraces:
 # urban floor platforms in cross section; cracks kept between individual terraces
 for j in range(n):
  shift=(j-(n-1)/2)*200; a=cx+shift; b=cy+95*math.sin(j*1.2)
  poly=np.array([[a-90,b-80],[a+90,b-80],[a+120,b+80],[a-105,b+105]])
  prism(id+'_STREET_BLOCK_'+str(j),poly,z-18,z+35,'ALABASTER','true_local_neighbourhood_floor_preliminary')
  if j%3!=1:
   # coherent inhabited masses with multiple setbacks; architectural section interior NOT completed
   footprint=np.array([[a-67,b-50],[a+60,b-48],[a+84,b+36],[a+24,b+69],[a-80,b+42]])
   prism(id+'_INHABITED_BUILDING_'+str(j),footprint,z+35,z+145+50*((j+1)%3),'NACRE','inhabited_building_study_public_interior_incomplete',topshift=(15*(-1)**j,12))
  else:
   poly2=np.array([[a-68,b-45],[a+73,b-42],[a+85,b+45],[a-75,b+55]])
   prism(id+'_PUBLIC_PLAZA_'+str(j),poly2,z+25,z+43,'GREEN','public_open_plaza_urban_section')
# civic districts are not completed buildings. Open-center 'hearth' is city-scale real negative space
# W0 is ONLY a noncanonical scale frame (no fake H or SB canonical placements)
box('W0_NONCANONICAL_10KM_REFERENCE',[0,0,-275],[10000,10000,80],'GRAPHITE','noncanonical_10km_ground_reference_only')
# tentative east water stripe (not canonical coast)
box('W0_EAST_WATER_ABSTRACT',[4720,300,-210],[560,7400,34],'WATER','noncanonical_east_sea_reference_only')
# R3-B visual revision: explicitly inhabited three-dimensional canyon sections,
# added after comparing R3-A eight real-GLB views. Not SDF and not an opaque giant shell.
from shapely.geometry import Polygon
from shapely.ops import triangulate

def cliff_solid(name,profile,ymin,ymax,mat,role,shift_x=0,shift_z=0):
 """Extrudes a hand-drawn concave city geological cross-section, not a convex box.
 The polygon has distinct roof street terraces and actual open vertical notches.
 Inner public streets are separate geometry and not claimed accessible without QA.
 """
 poly=Polygon(profile)
 assert poly.is_valid and poly.area>1000,name
 pv=[]; pf=[]
 # make both capped faces from shapely tessellation using explicit coordinate vertex index
 coords=[(float(x),float(z)) for x,z in poly.exterior.coords[:-1]]; n=len(coords)
 verts=np.array([[x,ymin,z] for x,z in coords]+[[x+shift_x,ymax,z+shift_z] for x,z in coords],float)
 lookup={tuple(np.round(v,5)):i for i,v in enumerate(coords)}
 tris=triangulate(poly); ff=[]
 for t in tris:
  if not poly.covers(t.representative_point()):continue
  vs=[lookup.get(tuple(np.round(x,5))) for x in t.exterior.coords[:-1]]
  if len(vs)!=3 or any(v is None for v in vs):raise ValueError('Unmatched triangulation vertex')
  ff.append(vs)
 for f in ff:
  pf.append(list(reversed(f)));pf.append([x+n for x in f])
 for i in range(n):
  j=(i+1)%n
  pf.extend([[i,j,j+n],[i,j+n,i+n]])
 mesh=trimesh.Trimesh(vertices=verts,faces=np.array(pf,int),process=False)
 if mesh.volume<0:mesh.invert()
 add(name,mesh,mat,role)

# Instead of a flat plate each deep inhabited bedrock contains 1+ km public travel depths.
# The three masses on each shore deliberately contain actual open-air cuts between floors.
# West is lower and longer; east is sharper, higher and more fractured.
cliff_solid('WEST_RESIDENTIAL_CLIFF_LOWER',[
 (-3610,260),(-510,260),(-430,420),(-990,780),(-1650,1120),(-2350,1090),(-3010,860),(-3500,600)],
 -1250,500,'FRAME','thick_inhabited_canyon_substructure_not_room_detailed',shift_x=160)
cliff_solid('WEST_CIVIC_CLIFF_UPPER',[
 (-3100,1340),(-810,1450),(-690,1590),(-1050,1870),(-1500,2200),(-2060,2390),(-2570,2140),(-2980,1640)],
 -550,1020,'CERAMIC','civic_canyon_roof_terrain_with_open_back',shift_x=-130)
cliff_solid('EAST_RESIDENTIAL_CLIFF_LOWER',[
 (460,200),(3750,280),(3780,610),(3300,860),(2550,1200),(1500,1090),(650,690)],
 -1310,420,'FRAME','thick_urban_city_foundation_open_upper_edge',shift_x=-120)
cliff_solid('EAST_CIVIC_ESCARPMENT_MIDDLE',[
 (850,1400),(3470,1300),(3320,1710),(2950,2140),(2280,2510),(1550,2360),(1250,1790)],
 -550,1050,'NACRE','civic_multilayer_urban_shore_inhabited_mass',shift_x=135)
cliff_solid('EAST_SERRATED_CREST_CITY',[
 (1510,2820),(2950,2700),(2810,3190),(2450,3590),(2090,4060),(1760,3770),(1580,3370)],
 100,1240,'ALABASTER','thick_high_city_crest_geography',shift_x=-100)
# actual open usable floors connecting public voids *within* cliff cross-section
for side,coord,levels,band in [
 ('WEST',(-2120,-600),[740,1260,1690,2080],640),
 ('EAST',(1990,-520),[800,1270,1740,2220,2770,3300],720)]:
 x0,y0=coord
 for k,z in enumerate(levels):
  # front stepped floors projecting INTO OPEN cavity, physically part of urban fabric
  yy=y0+60*k; xx=x0+90*math.sin(k*1.7)
  pts=[[[xx-650,yy-360,z-60],[xx-260,yy-380,z+10],
        [xx+210,yy-340,z+30],[xx+band,yy-280,z-50]],
       [[xx-710,yy+380,z-70],[xx-270,yy+430,z+10],
        [xx+260,yy+410,z+5],[xx+band+60,yy+320,z-60]]]
  planegrid(side+'_EXPOSED_RESIDENTIAL_CANYON_FLOOR_'+str(k),pts,
            'ALABASTER' if k%2 else 'CERAMIC',
            'habitable_city_avenue_open_in_city_cross_section_not_full_interiors',thickness=70)
  for j in [0,3]:
   p=pts[0][j]
   capsule(side+'_EXPOSED_AVENUE_COLUMN_'+str(k)+'_'+str(j),
      [p[0],p[1],z-80],[p[0]+15,p[1]+45,z+260],30,
      'GRAPHITE','open_avenue_support_detail')
# Two different genuine PUBLIC volumes, staged into cliff without hidden black windows:
# large public hall #2 within east internal city, with real floor, roof, and four exposed ribs
public_hall_west=[[-2280,-1500,1510],[-1770,-1530,1580],[-1290,-1460,1700],[-910,-1300,1780]]
public_hall_east=[[1030,-1480,2170],[1540,-1480,2290],[2150,-1440,2410],[2800,-1170,2670]]
for name,path in [('WEST_OPEN_ACADEMY',public_hall_west),('EAST_GREAT_EXCHANGE',public_hall_east)]:
 floors=[];roofs=[]
 for x,y,z in path:
  floors.append([[x,y-190,z],[x,y-85,z+18],[x,y+90,z+20],[x,y+235,z]])
  roofs.append([[x,y+40,z+450],[x,y+100,z+530],[x,y+240,z+650],[x,y+390,z+480]])
 planegrid(name+'_ACCESS_FLOOR',floors,'GOLD','actual_public_room_floor_not_access_verified',thickness=80)
 planegrid(name+'_OPEN_ROOF',roofs,'ALABASTER','separate_exposed_civic_room_roof_no_fake_void',thickness=80)
 for j,p in enumerate(path):
  if j in [0,2,3]:
   capsule(name+'_VAULT_PIER_'+str(j),[p[0],p[1]+200,p[2]-40],
    [p[0]+100,p[1]+235,p[2]+520],33,'GRAPHITE','load_path_illustrative')

GLB=OUT/'J7R3_FRACTURED_INHABITED_CIVIC_SKY_NONCANONICAL.glb';GLB.write_bytes(scene.export(file_type='glb'))
loaded=trimesh.load(GLB,force='scene',process=False)
metrics={
 'schema':'halo9.m3d1s.j7r3.measured_mesh_and_limitations.v1',
 'formal_art_decision':'UNASSESSED', 'construction':'HOLD','coordinate':'NONCANONICAL_Z_UP_METRES',
 'geometry_files':{'glb':GLB.name},
 'glb_bytes':GLB.stat().st_size,
 'mesh_nodes':len(loaded.geometry), 'vertices':sum(len(g.vertices) for g in loaded.geometry.values()),
 'triangles':sum(len(g.faces) for g in loaded.geometry.values()),
 'scene_bounds_m':np.round(loaded.bounds,2).tolist(),
 'roles':dict(Counter(r['role'] for r in records)),
 'editable_mesh_records':records,
 'mandatory_limits':['No real Blender GUI or live manual sculpt session','All coordinates study-only; nothing placed at official H/SB/V positions',
 'Public transit grade/physical walking/collisions, inhabited interiors and structural support NOT certified',
 'Mesh gallery use does not establish fully usable urban space','This is NOT 10km all-detail City Master 3D',
 'Do not confuse material color, mesh count or camera images with art PASS'],
 'reimport':'PASS_REAL_GLB_RELOADED_IN_TRIMESH'}
(OUT/'J7R3_MESH_MANIFEST.json').write_text(json.dumps(metrics,indent=2,ensure_ascii=False))
print('DONE',json.dumps({k:v for k,v in metrics.items() if k not in ['editable_mesh_records','roles']},indent=2),flush=True)