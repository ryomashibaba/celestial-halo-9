"""R19 authored urban sections. Independent research coordinates, metres.
No source model import, world lookup, or image synthesis. Run with background Blender.
The path/section tools are drafting aids; district arrangements are authored below.
"""
import bpy, bmesh, math, sys, json, hashlib
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent

def mat(n,c,metal=0,rough=.5,emission=0):
 m=bpy.data.materials.new(n);m.use_nodes=True;m.diffuse_color=(*c,1)
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emission:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emission
 return m

def bind():
 global S,A,E,P,D,G,C,T,W,L,V
 S=bpy.context.scene;A=bpy.data.collections['R19_LIVING_HORIZON'];E=bpy.data.collections['REVIEW_STUDIO']
 P,D,G,C,T,W,L,V=[bpy.data.materials[n] for n in ['Pearl ceramic','Graphite urban structure','Petrol inhabited glass','Warm public stone','Brushed bronze','Estuary water','Civic warm light','Urban gardens']]

def setup():
 bpy.ops.wm.read_factory_settings(use_empty=True)
 s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
 for n in ['R19_LIVING_HORIZON','REVIEW_STUDIO']:s.collection.children.link(bpy.data.collections.new(n))
 mat('Pearl ceramic',(.62,.70,.69),.35,.36);mat('Graphite urban structure',(.038,.065,.073),.48,.44)
 mat('Petrol inhabited glass',(.035,.15,.17),.55,.24);mat('Warm public stone',(.44,.39,.28),.1,.68)
 mat('Brushed bronze',(.44,.29,.12),.65,.35);mat('Estuary water',(.026,.22,.24),.55,.17)
 mat('Civic warm light',(.9,.53,.21),.1,.42,1.7);mat('Urban gardens',(.085,.18,.12),0,.9)
 bind();s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
 s.render.threads_mode='FIXED';s.render.threads=5;s.render.resolution_x=1280;s.render.resolution_y=1080;s.render.resolution_percentage=100
 s.render.image_settings.file_format='PNG';s.render.film_transparent=False;s.view_settings.view_transform='AgX'
 s.world=bpy.data.worlds.new('High pale atmosphere');s.world.use_nodes=True
 bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.36,.44,.5,1);bg.inputs[1].default_value=.65
 for n,loc,power,size in [('Sun',(-4000,-6000,9000),2.7,None),('Sky fill',(4000,-4000,6000),2.5e9,6500),('Rear sky',(-2000,5000,6500),2e9,5000)]:
  data=bpy.data.lights.new(n,'SUN' if size is None else 'AREA');data.energy=power
  if size:data.shape='DISK';data.size=size
  else:data.angle=.15
  o=bpy.data.objects.new(n,data);E.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,0,1600))-o.location).to_track_quat('-Z','Y').to_euler()
 mesh('STUDIO ground',[(-100000,-100000,-160),(100000,-100000,-160),(100000,100000,-160),(-100000,100000,-160)],[(0,1,2,3)],mat('Studio slate',(.11,.15,.17)),E)

def mesh(n,vs,fs,m,coll=None):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(n,me);(coll or A).objects.link(o);me.materials.append(m)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 return o

def prism(n,poly,z,h,m):
 N=len(poly)
 return mesh(n,[(x,y,zz) for zz in (z,z+h) for x,y in poly],[tuple(reversed(range(N))),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],m)

def box(n,c,d,m,coll=None):
 return mesh(n,[(c[0]+i*d[0]/2,c[1]+j*d[1]/2,c[2]+k*d[2]/2) for k in (-1,1) for j in (-1,1) for i in (-1,1)],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],m,coll)

def edges(path,width):
 # Mitred polygonal street boundaries, each point may carry its own elevation.
 left=[];right=[]
 for i,p in enumerate(path):
  tangent=Vector(path[min(i+1,len(path)-1)])-Vector(path[max(0,i-1)])
  u=Vector((-tangent.y,tangent.x,0)).normalized()*width/2
  left.append(Vector(p)+u);right.append(Vector(p)-u)
 return left,right

def band(n,path,w,h,m):
 l,r=edges(path,w);N=len(path);vs=[]
 for i in range(N):vs.extend([tuple(l[i]),tuple(r[i]),tuple(l[i]+Vector((0,0,h))),tuple(r[i]+Vector((0,0,h)))])
 fs=[(0,1,3,2),(4*N-4,4*N-2,4*N-1,4*N-3)]
 for i in range(N-1):
  a=4*i;b=a+4;fs.extend([(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
 return mesh(n,vs,fs,m)

def shift(path,dz):return [(x,y,z+dz) for x,y,z in path]

def route(n,pts,width=42,thick=16):
 band(n+'_public_deck',pts,width,thick,C)
 for side in (-1,1):
  l,r=edges(shift(pts,thick+3),width*.88);band(n+'_lit_edge',l if side<0 else r,2.5,2,L)

def citybank(n,path,width,height,style=0):
 """A deep inhabited urban section, open public floors and layered roof streets.
 No enclosing macro shell. Recessed bodies sit between traversable civic levels.
 Domestic room fitout is deliberately not claimed.
 """
 levels=[0,height*.36,height*.72]
 for k,z in enumerate(levels):
  floor=shift(path,z);band(n+f'_civic_ground_{k}',floor,width,15,D)
  # Housing body has real 18m public air below, not a painted black stripe.
  inner=shift(path,z+33);body_h=height*.29
  band(n+f'_inhabited_depth_{k}',inner,width*.78,body_h,G if (k+style)%3 else C)
  band(n+f'_roof_avenue_{k}',shift(inner,body_h),width*.90,9,P)
  # Floor seams, deep vertical ribs, and the two public building fronts.
  for zz in range(16,int(body_h),22 if style!=2 else 28):
   band(n+f'_occupied_floor_{k}_{zz}',shift(inner,zz),width*.80,2.5,P)
  for j in range(len(path)-1):
   a=Vector(path[j]);b=Vector(path[j+1]);ln=(b-a).length;count=max(2,int(ln/(66 if style!=1 else 92)))
   for q in range(count):
    p=a.lerp(b,(q+.5)/count);u=Vector((-(b-a).y,(b-a).x,0)).normalized()
    for side in (-1,1):
     pp=p+u*width*.39;pp.z+=z+33+body_h/2
     ob=box(n+f'_city_rib_{k}_{j}_{q}_{side}',pp,(9,18,body_h+8),P if style!=2 else T)
     ob.rotation_euler.z=math.atan2((b-a).y,(b-a).x)
  # Clear public loggia lighting is sparse, warm, not a glowing full silhouette.
  for j in (0,len(path)-1):
   p=path[j];box(n+f'_arrival_light_{k}_{j}',(p[0],p[1],p[2]+z+23),(width*.7,8,3),L)
 band(n+'_roof_garden',shift(path,height+8),width*.52,4,V)
 # Roof skyline varies through designed elevated public monuments, no miniature house carpet.
 return [o for o in A.objects if o.name.startswith(n)]

def lake(n,poly,z):prism(n,poly,z,3,W)

def terrain(n,poly,z,h):
 prism(n+'_deep_public_land',poly,z,h,D);prism(n+'_public_surface',poly,z+h,6,C)

DISTRICTS=[]
def register(n,z,idea):DISTRICTS.append(dict(id=n,altitude_m=z,spatial_role=idea))

def build():
 # A: estuary is an inhabited delta, with water entering between land fingers.
 register('A_ESTUARY',120,'Three public land fingers around water, buried urban streets open to estuary.')
 terrain('A_WEST',[(-3100,-2050),(-1900,-2250),(-850,-1550),(-1050,-850),(-2300,-850),(-3100,-1300)],-90,210)
 terrain('A_EAST',[(200,-1800),(1900,-2100),(3000,-1250),(2400,-450),(1200,-500),(650,-1000)],-90,300)
 terrain('A_INNER',[(-1300,-750),(-400,-1050),(600,-850),(1000,300),(-550,850),(-1500,150)],-50,350)
 lake('A_INLAND_SEA',[(-2000,-2500),(2000,-2500),(1200,-1600),(250,-1200),(-600,-1200),(-1300,-1600)],-70)
 for n,p,w,h,s in [
  ('A_TIDE_WEST',[(-2920,-1650,126),(-2350,-1850,126),(-1750,-1680,126),(-1350,-1350,126)],235,345,0),
  ('A_TIDE_INNER',[(-2640,-1130,126),(-2120,-1040,126),(-1560,-1020,126),(-1020,-1250,126)],210,275,1),
  ('A_EAST_QUAYS',[(1150,-1420,216),(1790,-1660,216),(2400,-1350,216),(2610,-1000,216)],250,410,2),
  ('A_SOUTH_ARCHIVE',[(760,-1100,216),(1050,-760,216),(1810,-680,216),(2270,-760,216)],225,290,0),
  ('A_CONFLUENCE',[(-1150,-350,306),(-600,-650,306),(50,-570,306),(550,-180,306)],240,460,1)]:citybank(n,p,w,h,s)
 lake('A_PUBLIC_RESERVOIR',[(-950,-200),(-400,-420),(200,-300),(420,80),(-200,240),(-800,180)],312)
 route('A_PUBLIC_CAUSEWAY',[(-2500,-2040,128),(-1600,-1740,128),(-920,-960,320),(0,-800,320),(800,-1250,218),(1800,-1900,218)],92,24)

 # B: inclined metropolitan canyon. Five individually laid-out thick street grounds
 # change their depth and orientation, rather than one giant diagonal member.
 register('B_ASCENT',800,'Stepped urban ridge, split living banks around diagonal canyon, distinct cross-city streets.')
 grounds=[('B1',[(-2700,-900),(-1550,-1000),(-1050,-320),(-1700,90),(-2550,-80)],430,200),
 ('B2',[(-2590,-180),(-1550,-400),(-1050,140),(-1200,620),(-2250,820)],1030,235),
 ('B3',[(-2500,600),(-1400,200),(-950,600),(-1100,1250),(-2100,1500)],1770,260),
 ('B4',[(-2350,1300),(-1250,880),(-650,1450),(-850,2150),(-1900,2180)],2500,280)]
 for n,poly,z,th in grounds:terrain(n,poly,z,th)
 citybank('B1_HARBOR_WALL',[(-2520,-650,636),(-2190,-640,636),(-1740,-770,636),(-1370,-460,636)],210,530,1)
 citybank('B1_INNER_SLOPE',[(-2450,-160,636),(-1890,-50,636),(-1460,-190,636)],195,330,0)
 citybank('B2_PUBLIC_CANYON',[(-2400,190,1271),(-2090,90,1271),(-1720,-100,1271),(-1270,150,1271)],245,580,2)
 citybank('B2_BACK_STREETS',[(-2220,610,1271),(-1790,480,1271),(-1290,410,1271)],205,460,0)
 citybank('B3_ESCARPMENT',[(-2270,980,2036),(-2160,650,2036),(-1820,450,2036),(-1410,470,2036),(-1150,700,2036)],245,620,1)
 citybank('B3_GARDEN_RIDGE',[(-2040,1260,2036),(-1640,1100,2036),(-1210,1140,2036)],200,430,0)
 citybank('B4_SKY_BOROUGH',[(-2030,1830,2786),(-2040,1530,2786),(-1630,1270,2786),(-1170,1270,2786),(-850,1630,2786)],270,670,2)

 # C: reverse amphitheatre. Its inhabited concave side points north, not at hero camera.
 register('C_REVERSE',950,'North-facing amphitheatre city, elevated ground shared with inner high city; underside loggias.')
 terrain('C_REAR_DELTA',[(-1100,1700),(0,1050),(1700,1350),(2200,2200),(1500,2900),(-200,2780),(-1200,2350)],650,300)
 citybank('C_REAR_CIVILIZATION',[(-850,2180,956),(-740,1770,956),(-200,1460,956),(600,1500,956),(1280,1780,956),(1570,2290,956)],310,650,0)
 citybank('C_REVERSE_SHORE',[(-550,2510,956),(0,2620,956),(650,2570,956),(1230,2430,956)],270,350,2)
 lake('C_REAR_LAGOON',[(-500,2120),(0,1810),(600,1880),(1120,2210),(500,2440),(-200,2420)],960)
 route('C_UPPER_PUBLIC_PROMENADE',[(-800,2290,1605),(-650,1870,1605),(0,1600,1605),(680,1680,1605),(1420,2120,1605)],78,18)

 # D: high thick inhabited plateau; two unlike civic banks bound a sky basin.
 register('D_SKY_BASIN',2380,'High inhabited basin, housing depth is its ground; 1100m public sky between non-identical city shores.')
 terrain('D_HIGH_WEST',[(-980,800),(-650,120),(200,-100),(850,230),(540,1050),(-300,1350)],2060,320)
 terrain('D_HIGH_EAST',[(800,-700),(1830,-950),(2540,-280),(2380,650),(1570,1150),(870,740)],2210,300)
 citybank('D_WEST_CRESCENT',[(-700,960,2386),(-680,460,2386),(-200,180,2386),(300,270,2386),(600,620,2386)],300,650,1)
 citybank('D_EAST_SKY_CITY',[(1110,450,2516),(1270,-120,2516),(1820,-470,2516),(2200,-180,2516),(2110,420,2516),(1680,810,2516)],350,740,0)
 lake('D_SKY_WATER',[(1420,-50),(1750,-230),(1960,0),(1870,330),(1540,500),(1320,300)],2520)
 route('D_SKY_CONFLUENCE',[(-240,1060,2390),(550,1180,2490),(1120,900,2520),(1710,900,2520)],160,65)
 # Public underworld has its own streets, light wells, inhabited reverse walls.
 citybank('D_UNDERSIDE_CIVIC_CITY',[(900,-240,1560),(1300,-520,1560),(1810,-510,1560),(2130,-180,1560)],235,470,2)
 route('D_UNDERWORLD_COURT',[(900,-40,1560),(1250,160,1560),(1770,70,1560),(2190,-260,1560)],155,60)

 # E: highest city extends rearward and tapers into an inhabited urban acropolis.
 register('E_ZENITH',3350,'Uppermost tilted horizon: long urban trench, roof gardens and higher civic precinct at asymmetric western end.')
 terrain('E_HIGH_LAND',[(-1980,1470),(-1080,1220),(-120,1640),(220,2300),(-400,2670),(-1500,2480),(-2130,2050)],3060,290)
 citybank('E_HIGH_NORTH',[(-1800,2080,3356),(-1370,2270,3356),(-750,2390,3356),(-210,2170,3356)],275,590,1)
 citybank('E_HIGH_SOUTH',[(-1770,1630,3356),(-1330,1510,3356),(-850,1650,3356),(-500,1940,3356)],265,760,0)
 route('E_PUBLIC_TRENCH',[(-1800,1840,3358),(-1320,1840,3358),(-850,1950,3358),(-340,2100,3358)],112,20)
 # F: middle confluence is a traversable district inside the central spatial sequence.
 register('F_INNER_CONFLUENCE',1170,'Internal civic island, divides low public sky from upper diagonal sky, not a frontal gate.')
 terrain('F_INNER_CITY',[(-1000,-270),(-400,-600),(490,-380),(980,240),(550,910),(-170,1040),(-850,580)],950,220)
 citybank('F_CIVIC_WEST',[(-760,260,1176),(-650,-80,1176),(-170,-310,1176),(300,-200,1176)],210,420,2)
 citybank('F_EAST_PUBLIC',[(-430,790,1176),(70,750,1176),(530,460,1176),(640,80,1176)],220,355,0)
 lake('F_COMMON_WATER',[(-380,220),(-20,-20),(350,130),(280,510),(-120,620),(-440,470)],1180)
 # Real spatial transport ribbons with stops; mechanical operation not certified.
 route('T_WEST_ASCENT',[(-2650,-1700,150),(-2770,-650,660),(-2620,50,1290),(-2420,800,2050),(-2310,1580,2800),(-1920,1960,3370)],65,26)
 route('T_INNER_ASCENT',[(-800,-700,330),(-1160,-200,670),(-1000,350,1180),(-800,1100,1650),(-500,900,2400),(-300,1600,2900),(-440,2350,3370)],54,24)
 route('T_EAST_RISE',[(2400,-1500,230),(2700,-650,850),(2400,100,1580),(2130,100,2530),(1930,500,2940)],60,26)
 route('T_REAR_LINK',[(-1900,2100,1290),(-1200,2300,1290),(-900,2500,980),(200,2750,980),(1600,2500,980),(2280,1200,1580),(2070,400,2530)],64,28)
 # Lateral bridges make shared public airs, but do not close the huge diagonal canyon.
 route('T_LOW_CROSS',[(-1500,-750,660),(-800,-880,660),(0,-820,660),(980,-950,660),(1500,-1100,660)],105,45)
 route('T_MIDDLE_TO_REAR',[(-900,620,1190),(-400,1300,1190),(450,1700,1190)],115,38)
 (R/'qa').mkdir(exist_ok=True);(R/'qa/DISTRICT_DESIGN.json').write_text(json.dumps(DISTRICTS,indent=2),encoding='utf8')

VIEWS={
 '01_FRONT':((0,-14000,3300),(0,100,1900),8500),
 '02_OBLIQUE':((9200,-12500,7700),(0,200,1900),8700),
 '03_SIDE':((14500,300,3500),(0,300,1900),8500),
 '04_REAR':((1000,15000,4100),(0,300,1900),8500),
 '05_AERIAL':((5500,-6500,14000),(0,200,1500),9200),
 '06_UNDERSIDE':((6000,-8000,-2600),(0,500,1900),8500),
 '07_GROUND':((600,-3800,160),(-800,700,2300),None),
 '08_LOW':((-600,-1100,670),(-200,800,1850),None),
 '09_MID':((-100,-650,1380),(500,700,2540),None),
 '10_HIGH':((1120,550,2660),(-650,1500,3500),None),
 '11_REVERSE_CITY':((300,4300,1800),(200,1600,1450),None),
 '12_CITY_10KM':((13500,-17000,13000),(0,300,1600),14500),
}
def cameras():
 for n,(loc,target,scale) in VIEWS.items():
  data=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,data);E.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
  data.clip_start=.15;data.clip_end=200000;data.lens=22 if n in ['08_LOW','09_MID','10_HIGH'] else 30
  if scale:data.type='ORTHO';data.ortho_scale=scale
 S.camera=bpy.data.objects['02_OBLIQUE']

def save(folder,stem,camera='02_OBLIQUE'):
 folder=Path(folder);folder.mkdir(parents=True,exist_ok=True);S.camera=bpy.data.objects[camera]
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(folder/(stem+'.blend')),compress=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in A.objects:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(folder/(stem+'.glb')),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
 print('SAVED',stem,len(A.objects),flush=True)

def render(folder,views):
 for n in views:
  S.camera=bpy.data.objects[n];bpy.data.objects['STUDIO ground'].hide_render=n=='06_UNDERSIDE'
  S.render.filepath=str(Path(folder)/(n+'.png'));bpy.ops.render.render(write_still=True);print('RENDERED',n,flush=True)

if __name__=='__main__':
 setup();build();cameras();save(R/'initial','R19_INITIAL');render(R/'initial',list(VIEWS)[:6])
