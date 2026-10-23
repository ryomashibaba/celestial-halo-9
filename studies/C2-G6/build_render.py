"""C2-G6 offline Blender. Synthetic study frame, metres Z-up; no world IO.
Run: blender -b -t 6 --python build_render.py -- A|B preview|full
"""
import bpy, math, json, sys, random, bmesh
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:];scheme=args[0];mode=args[1]
out=R/'renders'/scheme;out.mkdir(parents=True,exist_ok=True)
random.seed(39)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene;sc.unit_settings.system='METRIC'
def material(name,c,metal=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.72;p.inputs['Metallic'].default_value=metal
 return m
M={n:material(n,c) for n,c in {'ivory':(.68,.73,.70),'edge':(.26,.37,.39),'public':(.52,.40,.23),'life':(.58,.53,.42),'garden':(.18,.32,.26),'water':(.10,.24,.30),'terrain':(.17,.22,.24),'context':(.26,.31,.32),'road':(.39,.39,.34),'light':(.81,.69,.40)}.items()}
central=[];context=[];floors=[];events=[]
def mesh(name,v,f,mat='ivory',role='central'):
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 ob=bpy.data.objects.new(name,me);sc.collection.objects.link(ob);ob.data.materials.append(M[mat]);ob['role']=role
 (central if role!='context' else context).append(ob)
 return ob
def box(name,loc,dim,mat='ivory',role='central',angle=0):
 x,y,z=[q/2 for q in dim]
 v=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
 faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 ob=mesh(name,v,faces,mat,role);ob.location=loc;ob.rotation_euler.z=angle;return ob
def join(obs,name):
 central[:]=[x for x in central if x not in obs]
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.join();ob=obs[0];ob.name=name
 central.append(ob)
 return ob
def difference(ob,cutter):
 bpy.context.view_layer.update()
 bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('PROGRAM_VOID','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='MANIFOLD';mod.object=cutter
 bpy.ops.object.modifier_apply(modifier=mod.name)
 print('CARVED',cutter.name,len(ob.data.polygons),flush=True)
 if cutter in central:central.remove(cutter)
 bpy.data.objects.remove(cutter,do_unlink=True)
def wing(name,ang,length,width,peak,shift=(0,0),form='roof'):
 # A full, thick inhabited volume follows a changing civic section, not a thin bridge.
 v=[];n=38
 for i in range(n+1):
  t=i/n;u=-420+length*t
  if form=='roof':
   lo=-80+1420*(math.cos(t*math.pi/2)**1.5);hi=lo+620+430*math.sin(math.pi*t)**.7
   hi*=peak/2450;lo*=peak/2450
   w=width*(.70+.40*math.sin(math.pi*t))*(1-.35*t)
  else:
   lo=0;hi=peak*(.68+.26*math.sin(math.pi*t))
   w=width*(.70+.25*math.cos(2*math.pi*t));lean=400*math.sin(math.pi*t)+220
  # folded trapezoidal cross section; non-parallel skyline, no tower extrusion.
  if form=='wall':cross=[(-w*.42,0),(w*.42,0),(w*.32+lean,hi*.54),(w*.48+lean,hi-90),(-w*.20+lean,hi+60),(-w*.55,hi*.40)]
  else:cross=[(-w*.52,lo),(w*.48,lo+35),(w*.60,lo+150),(w*.34,hi-80),(-w*.10,hi+65),(-w*.55,hi-130)]
  for q,z in cross:
   v.append((shift[0]+u*math.cos(ang)-q*math.sin(ang),shift[1]+u*math.sin(ang)+q*math.cos(ang),z))
 f=[];k=6
 for i in range(n):
  for j in range(k):f.append((i*k+j,i*k+(j+1)%k,(i+1)*k+(j+1)%k,(i+1)*k+j))
 f.extend([tuple(reversed(range(k))),tuple(n*k+j for j in range(k))])
 return mesh(name,v,f)
if scheme=='A':
 angles=[math.radians(a) for a in [225,345,100]]
 bodies=[wing('activity_generated_fold_'+str(i),a,L,w,p) for i,(a,L,w,p) in enumerate(zip(angles,[2700,2450,2250],[1120,1450,1250],[2470,2260,2600]))]
else:
 angles=[math.radians(a) for a in [25,160]]
 bodies=[wing('foldback_city_'+str(i),a,L,w,p,shift=s,form='wall') for i,(a,L,w,p,s) in enumerate(zip(angles,[3650,3300],[1100,1250],[2250,2580],[(-1350,-600),(1100,300)]))]
body=join(bodies,'CIVIC_CONTINUOUS_MASS_'+scheme)
# Union overlapping folds through a bounded study-resolution remesh.
bpy.context.view_layer.objects.active=body
mod=body.modifiers.new('unify_folds','REMESH');mod.mode='VOXEL';mod.voxel_size=48;mod.use_smooth_shade=False;bpy.ops.object.modifier_apply(modifier=mod.name)
print('UNIFIED',scheme,len(body.data.polygons),flush=True)
mod=body.modifiers.new('surface_relax','SMOOTH');mod.factor=.65;mod.iterations=3;bpy.ops.object.modifier_apply(modifier=mod.name)
# Public daylight oculus at the place where activities meet: open up, not a solid summit.
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=300,depth=3500,location=(0,0,1750));cut=bpy.context.object;cut.name='shared_sky_room'
difference(body,cut)
if scheme=='A':
 c=box('diagonal_civic_daylight_ravine',(500,300,2150),(2100,440,1300),'edge',angle=math.radians(32));difference(body,c)
# Activity-specific lateral loggias are carved INTO the same body.
for wi,a in enumerate(angles):
 for level in [950,1420,1870]:
  for sign in [-1,1]:
   u=750;v=sign*490;x=u*math.cos(a)-v*math.sin(a);y=u*math.sin(a)+v*math.cos(a)
   c=box('street_void',(x,y,level+65),(1780,360,130),'edge',angle=a)
   difference(body,c)
events.append({'operation':'continuous mass minus shared sky room, A diagonal ravine, and lateral loggias','voxel_union_resolution_m':48,'scheme':scheme})
for p in body.data.polygons:p.use_smooth=True
print('MASS_CARVING_COMPLETE',flush=True)
# Public chamber at the convergence, with a real floor and human-scale frontage.
floor=box('great_public_chamber_floor',(0,-180,15),(1350,1250,30),'public');floors.append(floor)
box('arrival_court',(0,-1450,5),(850,1550,10),'public')
box('crossing_public_street',(0,-650,34),(1250,24,8),'road')
# Inhabited loggias: floors, courtyard blocks, shop-fronts and daylight streets derived from the mass.
dg=bpy.context.evaluated_depsgraph_get();tree=BVHTree.FromObject(body,dg)
districts=[]
for wi,a in enumerate(angles):
 for level in [950,1420,1870]:
  count=0
  for side in [-1,1]:
   for u in range(40,1500,155):
    v=side*445;x=u*math.cos(a)-v*math.sin(a);y=u*math.sin(a)+v*math.cos(a)
    hit=tree.ray_cast(Vector((x,y,level+4)),Vector((0,0,-1)),100)
    if hit[0] is None:continue
    # Floor sits in the carved channel; it extends 12m below its clear street.
    deck=box(f'L{level}_W{wi}_deck_{side}_{u}',(x,y,level-5.8),(150,190,12),'public',angle=a);floors.append(deck)
    # paired narrow blocks leave a 24m street open; 3.5m shop bays below.
    for s in [-1,1]:
     vv=v+s*34;xx=u*math.cos(a)-vv*math.sin(a);yy=u*math.sin(a)+vv*math.cos(a)
     box(f'inhabited_block_{wi}_{level}_{side}_{u}_{s}',(xx,yy,level+30),(104,44,60),'life',angle=a)
     for q in range(4):
      uu=u-37+q*25;vv2=vv-s*23;px=uu*math.cos(a)-vv2*math.sin(a);py=uu*math.sin(a)+vv2*math.cos(a)
      box('shop_front',(px,py,level+5),(8,1.5,7),'light',angle=a)
    count+=1
  districts.append({'wing':wi,'floor_z':level,'street_modules':count,'purpose':'housing and everyday services envelopes, not fitted dwellings'})
print('LOGGIAS_COMPLETE',sum(x['street_modules'] for x in districts),flush=True)
# Add roof neighbourhoods where an actual downward hit supplies the support height.
for wi,a in enumerate(angles):
 for u in [500,850,1200,1550]:
  x=u*math.cos(a);y=u*math.sin(a)
  loc,normal,_,dist=tree.ray_cast(Vector((x,y,3200)),Vector((0,0,-1)),4000)
  if loc is None:continue
  z=loc.z+5
  deck=box('high_neighbourhood_court',(x,y,z),(225,210,10),'public',angle=a);floors.append(deck)
  for du,dv in [(-80,0),(80,0),(0,80)]:
   xx=x+du*math.cos(a)-dv*math.sin(a);yy=y+du*math.sin(a)+dv*math.cos(a)
   box('high_living_culture_block',(xx,yy,z+36),(55,155 if du else 45,62),'life',angle=a)
  box('high_shared_garden',(x,y,z+7),(62,100,4),'garden',angle=a)
# Existing facilities remain outside: synthetic reception relations, not ID placements.
for wi,a in enumerate(angles):
 for u in [1650,2150]:
  x=u*math.cos(a);y=u*math.sin(a)
  deck=box('approach_route',(x,y,18),(550,110,18),'road',angle=a);floors.append(deck)
 # Vertical circulation envelopes explicitly reach the carved street floors.
 u=650;v=0;x=u*math.cos(a);y=u*math.sin(a)
 box('vertical_exchange_core',(x,y,900),(70,90,1800),'edge',angle=a)
# eye-level public chamber frontage; it physically shares the great hall floor.
for side in [-1,1]:
 for i in range(12):
  x=side*560;y=-640+i*86
  box('ground_frontage',(x,y,57),(65,67,54),'life')
  box('ground_shop',(x-side*34,y,35),(2,35,7),'light')
  box('arcade_colonnade',(x-side*55,y,57),(5,5,54),'edge')
for x,y in [(-430,-530),(-425,-510),(440,-380),(420,-365),(-400,40),(300,-200)]:
 box('human_1p7m',(x,y,30.85),(.5,.4,1.7),'edge')
for y in [-550,-480,-300]:box('arcade_human_1p7m',(-490,y,30.85),(.5,.4,1.7),'edge')
# Record central bounds before adding a synthetic 10km context.
central=[o for o in central if o.name in bpy.data.objects]
bpy.context.view_layer.update()
print('CENTRAL_OBJECTS',len(central),flush=True)
pts=[o.matrix_world@Vector(p) for o in central for p in o.bound_box]
mn=[min(p[i] for p in pts) for i in range(3)];mx=[max(p[i] for p in pts) for i in range(3)]
central_names=[o.name for o in central]
box('abstract_10km_urban_ground',(0,0,-75),(10000,10000,100),'terrain','context')
# Eastern inland sea / southwest void / north mountain / west cliff, synthetic only.
box('east_artificial_inland_sea',(3600,200,-18),(2700,6500,8),'water','context')
box('southwest_negative_space',(-3000,-3000,-20),(2500,3000,25),'water','context')
for i in range(7):
 bpy.ops.mesh.primitive_cone_add(vertices=7,radius1=700+80*(i%3),radius2=80,depth=1100+150*(i%4),location=(-2800+i*850,4400,450+75*(i%4)))
 ob=bpy.context.object;ob.name='abstract_north_mountain';ob.data.materials.append(M['terrain']);context.append(ob);ob['role']='context'
box('abstract_west_cliff',(-4670,0,190),(550,9000,600),'terrain','context')
for j in range(-10,11):
 for i in range(-10,11):
  x=i*420;y=j*420
  if abs(x)>4200 or abs(y)>4100 or math.hypot(x,y)<2550 or x>2500 or (x<-1600 and y<-1700):continue
  h=random.uniform(45,145)
  box('life_city_context',(x,y,h/2-20),(random.uniform(90,170),random.uniform(100,190),h),'context','context')
# 16 facilties expressed as 16 generic parcels; four sculptural landmarks, no SB mapping.
for i in range(16):
 a=2*math.pi*i/16;r=3250+(i%3)*160;x=r*math.cos(a);y=r*math.sin(a)
 if i%4==0:
  ob=wing('synthetic_major_facility_'+str(i),a,720,320,650,shift=(x,y));ob['role']='context';central.remove(ob);context.append(ob)
 else:box('synthetic_facility_parcel_'+str(i),(x,y,100),(230,190,220),'context','context',a)
# Six unlabeled aerial-district stations; not H1...H6 positions.
for i in range(6):
 a=2*math.pi*i/6+.3;r=3200;x=r*math.cos(a);y=r*math.sin(a);z=900+i%3*350
 box('synthetic_aerial_district_'+str(i),(x,y,z),(580,450,35),'edge','context',a)
 for q in range(5):box('aerial_life_context',(x+(q-2)*75,y,z+70),(55,160,100),'context','context')
for a in [math.radians(-90),math.radians(20),math.radians(155)]:
 u=3400;box('synthetic_major_axis',(u*math.cos(a),u*math.sin(a),-8),(3000,120,18),'road','context',a)
# Render and measured cameras share one scene, no generated imagery.
print('CONTEXT_OBJECTS',len(context),flush=True)
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=10 if mode=='preview' else 20;sc.cycles.use_denoising=True
sc.render.resolution_x=1000 if mode=='preview' else 1440;sc.render.resolution_y=750 if mode=='preview' else 1080;sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG'
sc.world.use_nodes=True;bg=sc.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.44,.55,.65,1);bg.inputs['Strength'].default_value=.65
ld=bpy.data.lights.new('same_sun','SUN');ld.energy=3;ld.angle=.15;sun=bpy.data.objects.new('same_sun',ld);sc.collection.objects.link(sun);sun.rotation_euler=(.45,-.5,-.4)
# Designed interior area illumination, shared by the two comparison scenes.
ld=bpy.data.lights.new('public_chamber_lighting','AREA');ld.energy=8_000_000;ld.shape='DISK';ld.size=900
light=bpy.data.objects.new('public_chamber_lighting',ld);sc.collection.objects.link(light);light.location=(0,-250,450)
for deck in [o for o in floors if o.name.startswith('L1420')][::8]:
 ld=bpy.data.lights.new('street_lighting','AREA');ld.energy=120000;ld.size=80
 light=bpy.data.objects.new('street_lighting',ld);sc.collection.objects.link(light);light.location=(deck.location.x,deck.location.y,1510)
cd=bpy.data.cameras.new('C2G6_Camera');cam=bpy.data.objects.new('C2G6_Camera',cd);sc.collection.objects.link(cam);sc.camera=cam;cd.clip_start=.05;cd.clip_end=60000
cameras={
 '01_city_10km':{'eye':(8000,-11000,6500),'target':(0,0,600),'lens':35},
 '02_approach_alpha':{'eye':(0,-5200,160),'target':(0,0,1000),'lens':24},
 '03_approach_beta':{'eye':(4900,1800,300),'target':(0,0,1000),'lens':28},
 '04_approach_gamma':{'eye':(-4200,2100,220),'target':(0,0,1000),'lens':28},
 '05_oblique':{'eye':(6100,-7500,4800),'target':(0,0,1000),'ortho':7800},
 '06_front':{'eye':(0,-9000,1700),'target':(0,0,1100),'ortho':6800},
 '07_side':{'eye':(9000,0,1700),'target':(0,0,1100),'ortho':6800},
 '08_back':{'eye':(0,9000,4500),'target':(0,0,1100),'ortho':6800},
 '09_aerial_district':{'eye':(3500,-3300,3000),'target':(0,0,800),'lens':25},
 '10_top':{'eye':(0,0,10500),'target':(0,0,0),'ortho':10500},
 '11_public_chamber':{'eye':(-420,-530,31.7),'target':(60,100,700),'lens':20},
 '12_living_street':{'eye':(-490,-600,31.7),'target':(-525,-250,40),'lens':24},
}
# Select one real elevated street floor and place the camera 1.7m above it.
decks=[o for o in floors if o.name.startswith('L1420')]
if decks:
 deck=decks[len(decks)//2];v=deck.rotation_euler.z;pos=deck.location;dx,dy=math.cos(v),math.sin(v)
 cameras['13_elevated_living_street']={'eye':(pos.x-55*dx,pos.y-55*dy,1421.9),'target':(pos.x+95*dx,pos.y+95*dy,1440),'lens':24}
def configure(s):
 cam.location=s['eye'];cam.rotation_euler=(Vector(s['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO' if 'ortho' in s else 'PERSP'
 if 'ortho' in s:cd.ortho_scale=s['ortho']
 else:cd.lens=s['lens']
def render(k):
 configure(cameras[k]);sc.render.filepath=str(out/(k+'.png'));bpy.ops.render.render(write_still=True);print('DONE',scheme,k,flush=True)
metrics={'study_id':'C2-G6','scheme':scheme,'units':'m','up':'Z','central_bbox_min':mn,'central_bbox_max':mx,'central_dimensions':[mx[i]-mn[i] for i in range(3)],'context_extent_m':10000,'context_is_synthetic':True,'SB_and_H_position_mapping':None,'central_objects':len(central_names),'district_loggias':districts,'program_operations':events,'cameras':cameras,'render':{'engine':'Cycles','samples':sc.cycles.samples,'resolution':[sc.render.resolution_x,sc.render.resolution_y]},'interior_floor_rays':{}}
dg=bpy.context.evaluated_depsgraph_get();floor_trees=[(o.name,BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])) for o in floors]
for k,s in cameras.items():
 if 'street' not in k and 'chamber' not in k:continue
 hits=[]
 for name,t in floor_trees:
  loc,_,_,dist=t.ray_cast(Vector(s['eye']),Vector((0,0,-1)),50)
  if loc is not None:hits.append((dist,name))
 metrics['interior_floor_rays'][k]=min(hits) if hits else None
(R/(scheme+'_metrics.json')).write_text(json.dumps(metrics,indent=2),encoding='utf-8')
if mode=='preview':
 for k in ['05_oblique','08_back']:render(k)
else:
 # export full study scene and a central-only model; context is explicitly marked.
 bpy.ops.object.select_all(action='DESELECT')
 for o in sc.objects:
  if o.type=='MESH':o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(R/(scheme+'_CITY.glb')),export_format='GLB',use_selection=True,export_extras=True)
 bpy.ops.object.select_all(action='DESELECT')
 for name in central_names:bpy.data.objects[name].select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(R/(scheme+'_CENTRAL.glb')),export_format='GLB',use_selection=True,export_extras=True)
 configure(cameras['05_oblique']);bpy.ops.wm.save_as_mainfile(filepath=str(R/(scheme+'.blend')),compress=True)
 for k in (['05_oblique','08_back'] if mode=='comparison' else cameras):render(k)
print('COMPLETE',scheme,mode,flush=True)
