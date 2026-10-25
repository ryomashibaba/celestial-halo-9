"""R15: independent metre-space city; render, inspect, revise in separate stages.
Never reads canonical assets or saves. Output confined to this new study.
Run Blender --background --factory-startup --python this.py -- 0|1|2 [views].
"""
import bpy, bmesh, math, sys, json, random
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['0']
REV=int(args[0]); FOLDER=ROOT/['concept','revision_1','revision_2'][REV]
FOLDER.mkdir(parents=True,exist_ok=True)
random.seed(15)
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene; S.unit_settings.system='METRIC'; S.unit_settings.scale_length=1
ARCH=bpy.data.collections.new('R15_SYMMETRIC_LIVED_WORLD');S.collection.children.link(ARCH)
ENV=bpy.data.collections.new('STUDIO_NOT_ARCHITECTURE');S.collection.children.link(ENV)
def mat(n,c,metal=0,rough=.55,em=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if em:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=em
 return m
PEARL=mat('Pearl ceramic titanium',(.62,.73,.76),.38,.32)
IVORY=mat('Warm silver civic stone',(.74,.70,.58),.16,.48)
DARK=mat('Deep blue inhabited strata',(.045,.105,.14),.35,.4)
FLOOR=mat('Pale limestone pedestrian grounds',(.42,.49,.47),.1,.7)
BRONZE=mat('Champagne structural edges',(.38,.27,.12),.6,.3)
GLASS=mat('Opaque shaded azure glazing',(.035,.18,.22),.5,.2)
WATER=mat('Still turquoise water',(.025,.27,.30),.58,.16)
GREEN=mat('Terrace vegetation',(.10,.22,.12),0,.85)
LIGHT=mat('Warm inhabited light',(.95,.57,.22),.1,.3,2)
CYAN=mat('Navigation light',(.2,.65,.76),.2,.3,1.8)
HUMAN=mat('Ochre people',(.8,.28,.065),0,.7)
def mesh(n,v,f,m,bevel=0,coll=ARCH):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(n,me);coll.objects.link(o)
 me.materials.append(m)
 if bevel:
  mod=o.modifiers.new('Designed edge rounding','BEVEL');mod.width=bevel;mod.segments=3
 return o
def box(n,c,d,m,bevel=0,coll=ARCH):
 x,y,z=c;a,b,h=[v/2 for v in d]
 return mesh(n,[(x+u*a,y+v*b,z+w*h) for w in (-1,1) for v in (-1,1) for u in (-1,1)],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],m,bevel,coll)
def prism(n,poly,z0,z1,m,bevel=0):
 N=len(poly);return mesh(n,[(x,y,z) for z in (z0,z1) for x,y in poly],[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],m,bevel)
def carve(o,n,c,d,rounding=0):
 cut=box(n,c,d,DARK,rounding)
 bpy.context.view_layer.objects.active=cut
 for mod in list(cut.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 # Explicitly orient all cutter surfaces before exact solid difference.
 bm=bmesh.new();bm.from_mesh(cut.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cut.data);bm.free()
 bpy.context.view_layer.objects.active=o
 mod=o.modifiers.new('Actual public volume subtraction','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
def escarpment(n,side):
 # Authored broad, occupied landform sections; deliberately no conical tower.
 stations=[(1040,40,330,655,90),(1030,440,330,625,120),(950,900,280,490,210),(790,1420,190,350,340),(640,1840,105,235,450)]
 v=[];N=12
 for x,z,rx,ry,cy in stations:
  for i in range(N):
   a=2*math.pi*i/N;ca,sa=math.cos(a),math.sin(a)
   v.append((side*x+rx*math.copysign(abs(ca)**.45,ca),cy+ry*math.copysign(abs(sa)**.45,sa),z))
 f=[tuple(reversed(range(N))),tuple(range(len(v)-N,len(v)))]+[(j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i) for j in range(len(stations)-1) for i in range(N)]
 o=mesh(n,v,f,PEARL)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 # Irregularly proportioned city-scale true apertures, not six repeated holes.
 carve(o,n+'_lower_civic_cleft',(side*1050,-270 if REV>=2 else -70,680),(1100,1100 if REV>=2 else 520,360),65)
 carve(o,n+'_upper_civic_cleft',(side*820,200 if REV>=2 else 385,1250),(1000,920 if REV>=2 else 355,240),45)
 if REV>=2:
  carve(o,n+'_upper_inhabited_loggia',(side*700,300,1650),(900,710,145),22)
  # 250m tall daylight ravine breaks the massive outer flank into occupied wings.
  carve(o,n+'_outer_vertical_daylight',(side*1200,140,970),(160,1200,290),30)
 # Crown is an occupied roof plateau with a slit garden, not a needle.
 carve(o,n+'_crown_garden',(side*650,450,1840),(110,275,140),18)
 return o
def rib(n,stations,m,segments=20):
 # variable elliptical section, authored position/radii at each station
 v=[]
 for x,y,z,rx,ry in stations:
  v.extend([(x+rx*math.cos(2*math.pi*i/segments),y+ry*math.sin(2*math.pi*i/segments),z) for i in range(segments)])
 f=[tuple(reversed(range(segments))),tuple(range(len(v)-segments,len(v)))]
 f += [(j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i) for j in range(len(stations)-1) for i in range(segments)]
 o=mesh(n,v,f,m)
 for p in o.data.polygons:p.use_smooth=len(p.vertices)==4
 return o
def path(n,points,width,thick,m):
 v=[]
 for i,p in enumerate(points):
  d=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)])
  side=Vector((-d.y,d.x,0)).normalized()*width/2
  for z in (-thick,0):
   for s in (-1,1):v.append(tuple(Vector(p)+s*side+Vector((0,0,z))))
 f=[(0,1,3,2),(len(v)-4,len(v)-2,len(v)-1,len(v)-3)]
 for i in range(len(points)-1):
  a=i*4;b=a+4;f.extend([(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
 return mesh(n,v,f,m)
def ellipsoid(n,c,d,m):
 # low poly organic canopy, actual geometry
 x,y,z=c;rx,ry,rz=d;N=10;K=5
 v=[(x,y,z-rz)]
 for j in range(1,K):
  t=-math.pi/2+j*math.pi/K
  v += [(x+rx*math.cos(t)*math.cos(i*2*math.pi/N),y+ry*math.cos(t)*math.sin(i*2*math.pi/N),z+rz*math.sin(t)) for i in range(N)]
 v.append((x,y,z+rz));top=len(v)-1
 f=[(0,1+(i+1)%N,1+i) for i in range(N)]+[(top,top-1-i,top-1-(i+1)%N) for i in range(N)]
 f += [(1+j*N+i,1+j*N+(i+1)%N,1+(j+1)*N+(i+1)%N,1+(j+1)*N+i) for j in range(K-2) for i in range(N)]
 return mesh(n,v,f,m)
def tree(x,y,z,k):
 box(k+'_trunk',(x,y,z+3),(1.1,1.1,6),BRONZE)
 ellipsoid(k+'_crown',(x,y,z+7),(5,5,4.5),GREEN)
def person(x,y,z,k):
 rib(k,[(x,y,z+.03,.18,.12),(x,y,z+1.35,.24,.15),(x,y,z+1.52,.12,.12)],HUMAN,8)
 ellipsoid(k+'_head',(x,y,z+1.65),(.12,.12,.15),HUMAN)
def court(n,x,y,z,w=66,d=86,h=28,kind='west'):
 # true open courtyard; entrance split into jambs and lintel, 7m clear height.
 mm=IVORY if kind=='west' else PEARL
 box(n+'_west',(x-w/2+6,y,z+h/2),(12,d,h),mm)
 box(n+'_east',(x+w/2-6,y,z+h/2),(12,d,h+4),mm)
 box(n+'_north',(x,y+d/2-6,z+h/2),(w-24,12,h),mm)
 opening=14
 for a in (-1,1):box(n+'_entry_jamb',(x+a*((w-24+opening)/4),y-d/2+5,z+h/2),((w-24-opening)/2,10,h),DARK)
 box(n+'_entry_lintel',(x,y-d/2+5,z+7+(h-7)/2),(opening,10,h-7),mm)
 box(n+'_court_paving',(x,y,z+.12),(w-24,d-22,.24),FLOOR)
 # floor depth/recess shadows, horizontal balconies oriented towards real court
 for q in range(1,int(h/5)):
  zz=z+q*5
  for s in (-1,1):
   box(n+'_courtyard_balcony',(x+s*(w/2-13),y,zz),(3,d-22,.65),BRONZE)
   box(n+'_outer_shade',(x+s*(w/2+.5),y,zz),(2,d,.7),PEARL)
  box(n+'_north_glazing',(x,y+d/2+.05,zz+1.8),(w-27,.3,2.5),GLASS)
 if kind=='west':tree(x,y,z,n+'_garden')
 else:box(n+'_watercourt',(x,y,z+.3),(w-30,d-38,.35),WATER)
 # a lifted top room makes each mass more than a repeated block
 box(n+'_roof_room',(x-w*.2,y+d*.13,z+h+5),(w*.32,d*.43,10),mm)
 box(n+'_roof_room_glass',(x-w*.2,y-d*.09,z+h+5),(w*.26,.3,5),GLASS)

# CITY GROUNDS define the mother structure before spires or a crown.
# Opposed stepped inhabited valleys, clear 800m central canyon.
districts=[]
for side in (-1,1):
 label='WEST_GARDEN' if side==-1 else 'EAST_WATER'
 for tier in range(3):
  inner=420+tier*250;outer=inner+250;z=240+tier*115
  poly=[(side*inner,-650),(side*(outer-35),-705),(side*(outer+30),-570),(side*(outer+15),400),(side*(outer-45),650),(side*inner,590)]
  # revisions later replace flat foundations with more articulated city-depth landforms
  base=z-(100 if REV==0 else 165)
  ground=prism(label+f'_T{tier}_inhabited_landform',poly,base,z,DARK,4)
  if REV>=1:
   # Orientation is independent of which shore generated the footprint.
   bm=bmesh.new();bm.from_mesh(ground.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ground.data);bm.free()
   for yy in (-395,155):carve(ground,label+'_real_public_undercroft',(side*(inner+125),yy,base+80),(400,330,105),15)
  # actual streets on top of a massive city ground
  prism(label+f'_T{tier}_walkable_ground',poly,z+.02,z+.06,FLOOR,0)
  for row in range(7):
   yy=-540+row*155
   for col in range(2):
    xx=side*(inner+65+col*112)
    if (row==3 and col==0) or (row==1 and tier==0):continue
    h=22+((row*7+col*11+tier*13+(side+1)*3)%5)*7
    if side==1 and row in (2,5):
     # eastern vertical garden lamellae create tall slots instead of west courtyard rhythm
     for a in (-1,1):
      box(label+f'_vertical_garden_{tier}_{row}_{col}',(xx+a*20,yy,z+h),(18,105,h*2),PEARL)
      for k in range(1,5):box(label+'_garden_sky_slot',(xx+a*20,yy,z+k*h*.37),(24,112,2),BRONZE)
     box(label+'_vertical_water',(xx,yy,z+.2),(18,110,.3),WATER)
    else:court(label+f'_{tier}_{row}_{col}',xx,yy,z,66,96,h,'west' if side==-1 else 'east')
  # 900m longitudinal planted promenade / water-channel defines a district, not windows
  px=side*(inner+125)
  if side==-1:
   for row in range(10):tree(px,-600+row*120,z,label+f'_allee_{tier}_{row}')
  else:box(label+f'_canal_{tier}',(px,-20,z+.1),(11,1090,.2),WATER)
  # true public undercroft: 30m deep landing, paired piers, large occupied void
  for yy in (-480,-60,360):
   for sx in (inner+30,outer-30):box(label+'_undercroft_pier',(side*sx,yy,base+48),(20,22,96),PEARL)
   box(label+'_undercroft_arcade',(side*(inner+125),yy,base+102),(225,75,12),IVORY)
  districts.append(dict(name=label+f'_T{tier}',plan_span_m=[250,1355],living_core_m=[230,930],floor_z_m=z,role='garden courts' if side==-1 else 'canal and vertical gardens'))
 # broad indoor transit canyon at rear, real landing levels and open shafts
 for j,yy in enumerate((-580,500)):
  x=side*840
  height=1050 if REV==0 else 485
  for sx in (-36,36):box(label+'_LIFT_reveal',(x+sx,yy,height/2+50),(18,70,height),PEARL,3)
  box(label+'_LIFT_dark_shaft',(x,yy+28,height/2+50),(48,12,height),GLASS)
  for zz in ((75,240,355,470,820,1050) if REV==0 else (75,240,355,470)):
   box(label+'_LIFT_landing',(x,yy-15,zz-3),(100,110,6),IVORY)
   box(label+'_LIFT_cabin',(x,yy,zz+7),(34,34,14),BRONZE)
 # two authored civic spines form the canyon boundaries; ground grows into them
 for yy in ((130,570) if REV==0 else ()):
  if REV==0:profile=[(980,50,170,125),(1000,500,145,110),(820,1050,100,85),(650,1570,70,60),(540,1870,8,15)]
  else:profile=[(1050,50,170,125),(1040,360,160,112),(950,740,130,95),(790,1130,105,82),(670,1510,80,65),(610,1810,55,46),(570,2100,3,5)]
  rib(label+'_inhabited_spine',[(side*x,yy,z,rx,ry) for x,z,rx,ry in profile],PEARL,28)
  # actual returning civic galleries between spines at separately meaningful heights
 if REV>=1:escarpment(label+'_CONTINUOUS_INHABITED_ESCARPMENT',side)
 for i,zz in enumerate((820,1050,1300,1530) if REV==0 else (510,1130,1590)):
  xx=side*(910-i*85)
  front=(-330,45,210)[i] if REV>=2 else -330
  poly=[(xx-140,front),(xx+140,front),(xx+150,front+80),(xx+140,630),(xx-140,630),(xx-150,front+80)] if REV>=1 else [(xx-90,70),(xx+90,70),(xx+110,160),(xx+85,630),(xx-85,630),(xx-110,160)]
  prism(label+'_civic_sky_court',poly,zz-30,zz,DARK,3)
  for y in (([-210,-50,240,440] if i==0 else [180,400,550] if i==1 else [340,520]) if REV>=2 else (-210,-50,240,440) if REV>=1 else (240,440)):court(label+f'_sky_housing_{i}_{y}',xx,y,zz,92,100,28+i*5,'west' if side==-1 else 'east')
  if REV>=2:
   # Wider urban grounds turn a 300-600m civic cleft into a district with courts,
   # not a lonely building on a balcony. Layout differs across the two shores.
   for row,yy in enumerate(([-170,10,200,400] if i==0 else [170,350,530] if i==1 else [320,510])):
    for col in (-1,1):
     if i==2 and row==0:continue
     court(label+f'_cleft_city_{i}_{row}_{col}',xx+col*83,yy,zz,62,112,24+(row%3)*9,'west' if side==-1 else 'east')
   # Internal tall transfer bay, with legible floor and landings.
   x=side*610
   if i==0:
    for s in (-1,1):box(label+'_CLEFT_LIFT_reveal',(x+s*25,570,930),(10,40,1740),BRONZE)
   floor=zz
   path(label+'_CLEFT_transfer',[(x,570,floor),(xx,570,floor),(xx,450,floor)],48,8,IVORY)
   box(label+'_CLEFT_lift_cabin',(x,570,floor+6),(32,27,12),GLASS)
 # massive public prow where urban terrain meets shared space
 poly=[(side*420,-650),(side*670,-650),(side*630,-850),(side*480,-955),(side*375,-810)]
 prow=prism(label+'_PUBLIC_PROW',poly,90,240,IVORY,8)
 if REV>=1:
  bm=bmesh.new();bm.from_mesh(prow.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(prow.data);bm.free()
  carve(prow,label+'_PROW_OPEN_PORTICO',(side*520,-800,165),(420,135,100),18)
 # canyon facing public balcony with inhabitable deep portico (3m colonnade to 70m atrium)
 for yy in (-430,-210,10):
  x=side*455
  box(label+'_portico_roof',(x,yy,258),(68,105,6),PEARL,1)
  for a in (-1,1):box(label+'_portico_pier',(x-side*22,yy+a*43,249),(3.5,3.5,18),BRONZE)

# Central public ground, a lowered reflecting basin, promenades along both sides.
prism('LOWER_CIVIC_GROUND',[(-440,-850),(440,-850),(500,-500),(420,690),(-420,690),(-500,-500)],-40,60,DARK,8)
box('Central_basin',(0,0,60),(440,970,1),WATER)
for side in (-1,1):box('Lower_public_promenade',(side*335,-40,61),(135,1320,2),IVORY,1)
box('Southern_civic_forecourt',(0,-750,62),(820,210,4),FLOOR,2)

# Two public crossings, thick inhabited vessel sections, not connecting sticks.
def crossing(n,y,z,w,depth,rise):
 points=[(-w/2+i*w/32,y+55*math.sin(math.pi*i/32),z+rise*math.sin(math.pi*i/32)) for i in range(33)]
 if REV>=2:
  # Variable vessel section: broad, deep civic middle and slender district arrivals.
  v=[]
  for j,(x,yy,zz) in enumerate(points):
   t=j/32;wid=depth*(1+.85*math.sin(math.pi*t)**2);thick=32+58*math.sin(math.pi*t)**2
   v.extend([(x,yy-wid/2,zz-thick),(x,yy+wid/2,zz-thick),(x,yy-wid/2,zz),(x,yy+wid/2,zz)])
  f=[(0,2,3,1),(128,129,131,130)]
  for j in range(32):
   a=j*4;b=a+4;f.extend([(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
  mesh(n+'_sculpted_civic_vessel',v,f,DARK)
 else:path(n+'_inhabited_hull',points,depth,32,DARK)
 path(n+'_public_street',[(x,y,z+1) for x,y,z in points],depth-12,2,IVORY)
 for s in (-1,1):path(n+'_parapet',[(x,y+s*(depth/2-5),z+4) for x,y,z in points],5,5,BRONZE)
 for x in (-w*.36,w*.36):
  t=(x+w/2)/w;zy=z+rise*math.sin(math.pi*t);yy=y+55*math.sin(math.pi*t)
  if REV>=2:
   box(n+'_arrival_ground',(x,yy,zy),(120,depth-16,6),IVORY)
   for a in (-1,1):
    for b in (-1,1):box(n+'_hall_pier',(x+a*48,yy+b*(depth/2-18),zy+16),(8,8,32),PEARL)
   box(n+'_open_hall_roof',(x,yy,zy+34),(126,depth-6,6),PEARL,2)
  else:
   box(n+'_arrival_hall',(x,y,z+18),(110,depth-20,30),PEARL,3)
   box(n+'_hall_portal',(x,y-depth/2+8,z+12),(55,2,22),GLASS)
crossing('LOWER_BOULEVARD',-400,240,1080,110,0 if REV==0 else 8)
crossing('UPPER_CIVIC_VESSEL',400 if REV<2 else 570,1250 if REV==0 else 1700,1440 if REV==0 else 1350,160 if REV==0 else 115,90 if REV==0 else 140)

# R2 form edit: scooped receiving amphitheatres and deep station fan at each shore.
if REV>=2:
 for side in (-1,1):
  # fan-shaped terrain mediates the 1km canyon and the 10m street
  for q in range(8):
   x=side*(420+q*19);yy=-110
   poly=[(x,-300-q*10),(x+side*26,-310-q*10),(x+side*26,170+q*10),(x,160+q*10)]
   prism(('WEST' if side==-1 else 'EAST')+'_public_receiving_steps',poly,207+q*4,211+q*4,IVORY)
  for yy in (-580,500):
   # diagonal return gallery creates a space-depth arrival rather than a vertical stick
   path('R2_returning_transit_gallery',[(side*840,yy,355),(side*690,yy-45,355),(side*580,yy-140,355)],65,20,DARK)
  # open public vaulted canopy: ribs + thin roof strips, not a closed labelled box
  for j in range(5):
   yy=-220+j*22
   pts=[(side*(430+q*14),yy,270+28*math.sin(math.pi*q/12)) for q in range(13)]
   path('R2_market_canopy_fan',pts,8,4,PEARL)
  box('R2_market_lane',(side*540,-170,240.15),(150,180,.3),FLOOR)
  for yy in (-230,-200,-170,-140,-110):
   box('R2_market_occupied_bay',(side*600,yy,244),(18,18,8),DARK)
   box('R2_market_bay_lantern',(side*590,yy,245),(1,10,3),LIGHT)

# Local human scale belongs to the actual district street, not a separate sample scene.
for i in range(24):person(-545+(i%3)*4,-510+(i//3)*18,240.06,'WEST_resident_'+str(i))
for i in range(12):person(465+(i%2)*5,-270+(i//2)*16,240,'EAST_resident_'+str(i))
for i in range(18):person(-240+i*28,-750,64,'Civic_resident_'+str(i))

# Apply authored edge rounds so GLB and blend have identical triangulated geometry.
bpy.context.view_layer.update()
for o in list(ARCH.objects):
 if o.type=='MESH' and o.modifiers:
  bpy.context.view_layer.objects.active=o
  for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 if o.type=='MESH':
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()

S.render.engine='CYCLES';S.cycles.samples=24;S.cycles.use_denoising=True
S.render.resolution_x=1200;S.render.resolution_y=1100;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.film_transparent=False
S.world=bpy.data.worlds.new('Pale blue atmosphere');S.world.use_nodes=True
bg=next(n for n in S.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.20,.29,.38,1);bg.inputs[1].default_value=.5
S.view_settings.view_transform='AgX'
box('Infinite_studio_ground',(0,0,-65),(200000,200000,25),mat('Studio ground',(.085,.12,.15)),coll=ENV)
def area(n,loc,power,size,target):
 d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(n,d);ENV.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Softbox',(0,-2000,4800),1.5e9,2800,(0,0,650))
sun=bpy.data.lights.new('Late morning sun','SUN');sun.energy=3;sun.angle=.15
o=bpy.data.objects.new('Late morning sun',sun);ENV.objects.link(o);o.rotation_euler=(.45,-.5,-.3)
def cam(n,loc,target,ortho=None,lens=30):
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d);ENV.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.clip_start=.15;d.clip_end=100000
 if ortho:d.type='ORTHO';d.ortho_scale=ortho
 else:d.type='PERSP';d.lens=lens
 return o
CAMERAS={
 '01_FRONT':cam('01_FRONT',(0,-5500,1260),(0,0,1010),3400),
 '02_OBLIQUE':cam('02_OBLIQUE',(3600,-4700,2900),(0,0,850),3900),
 '03_SIDE':cam('03_SIDE',(5400,0,1360),(0,0,1000),3200),
 '04_REAR':cam('04_REAR',(0,5500,1500),(0,0,1000),3400),
 '05_AERIAL':cam('05_AERIAL',(2200,-2600,4700),(0,0,750),3700),
 '06_SHARED_CANYON':cam('06_SHARED_CANYON',(60,-950,440),(0,430,1300),lens=18),
 '07_WEST_DISTRICT':cam('07_WEST_DISTRICT',(-1470,-1230,990),(-800,-100,360),lens=36),
 '08_HUMAN_WEST':cam('08_HUMAN_WEST',(-545,-450,241.76),(-545,-150,247),lens=24),
 '09_EAST_DISTRICT':cam('09_EAST_DISTRICT',(1300,-1130,850),(780,-10,400),lens=35),
 '10_HUMAN_CANYON':cam('10_HUMAN_CANYON',(-390,-620,63.7 if REV>=1 else 62.7),(100,280,450),lens=22),
}
S.camera=CAMERAS['02_OBLIQUE']
bpy.context.view_layer.update()
qa={'revision':REV,'blender_version':bpy.app.version_string,'units':'metres; independent study coordinates, not official world anchors','districts':districts,'human_floor_rays':{}}
for name in ('08_HUMAN_WEST','10_HUMAN_CANYON'):
 c=CAMERAS[name];hit,loc,normal,index,ob,matrix=S.ray_cast(bpy.context.evaluated_depsgraph_get(),c.location,Vector((0,0,-1)),distance=20)
 distance=(c.location-loc).length if hit else None
 qa['human_floor_rays'][name]={'camera_xyz_m':list(c.location),'hit':hit,'object':ob.name if hit else None,'floor_xyz_m':list(loc) if hit else None,'distance_m':distance,'pass_1_7m_2mm':bool(hit and abs(distance-1.7)<.002)}
print('HUMAN',qa['human_floor_rays'],flush=True)
stem='R15_'+['CONCEPT','REVISION_1','FINAL'][REV]
bpy.ops.wm.save_as_mainfile(filepath=str(FOLDER/(stem+'.blend')),compress=True)
bpy.ops.object.select_all(action='DESELECT')
for o in ARCH.objects:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(FOLDER/(stem+'.glb')),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
(FOLDER/'BUILD_EVIDENCE.json').write_text(json.dumps(qa,indent=2),encoding='utf8')
views=args[1:] or ['01_FRONT','02_OBLIQUE']
for name in views:
 S.camera=CAMERAS[name];S.render.filepath=str(FOLDER/(name+'.png'));bpy.ops.render.render(write_still=True)
 print('RENDERED',name,flush=True)
print('R15 STAGE COMPLETE',REV,flush=True)
