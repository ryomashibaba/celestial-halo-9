"""B2-G4 real mesh study. Run in a NEW Blender background process only.
Units: metres. No external assets, generated images or fluid simulation.
Comparison uses exact fixed world cameras, not automatic per-object framing.
"""
import bpy, bmesh, math, json, sys, hashlib, argparse
from pathlib import Path
from mathutils import Vector

P=argparse.ArgumentParser()
P.add_argument('--concept',choices=['N1','N2','N3','OLD','OLD1'],default='N1')
P.add_argument('--refine',action='store_true')
P.add_argument('--views',default='02_OBLIQUE')
P.add_argument('--preview',action='store_true')
opt=P.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
if opt.refine:
 raise RuntimeError('B2-G4 macro art gate STOP: refinement is not authorized by a passing basic form. No selected concept exists.')
ROOT=Path(__file__).resolve().parent
OUT=ROOT/(opt.concept+'_selected' if opt.refine else opt.concept)
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene; S.unit_settings.system='METRIC'; S.unit_settings.scale_length=1
def coll(n):
 c=bpy.data.collections.new(n); S.collection.children.link(c); return c
ARCH=coll('01_INHABITED_MASS'); ENV=coll('02_ENVIRONMENT'); CITY=coll('03_URBAN_GROUNDS'); CTX=coll('90_CONTEXT'); CAM=coll('91_CAMERAS')
def mat(n,c):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); m.use_nodes=True
 p=next(x for x in m.node_tree.nodes if x.type=='BSDF_PRINCIPLED'); p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=.8
 return m
ivory=mat('Inhabited mineral',(.69,.67,.58)); pale=mat('Public institution',(.86,.81,.65)); green=mat('Climate ground - schematic',(.18,.33,.27)); dark=mat('Urban court shade',(.30,.38,.36)); bronze=mat('Civic routes',(.55,.35,.15)); water=mat('Horizontal sea - opaque diagnostic',(.055,.31,.38)); grey=mat('Context',(.16,.20,.24))
def mesh(n,v,f,m,c=ARCH):
 me=bpy.data.meshes.new(n); me.from_pydata(v,[],f); me.update()
 bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
 o=bpy.data.objects.new(n,me); c.objects.link(o); me.materials.append(m); return o
def prism(n,poly,z,h,m,c=CITY):
 N=len(poly); v=[(x,y,z) for x,y in poly]+[(x,y,z+h) for x,y in poly]
 f=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]
 f += [(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 return mesh(n,v,f,m,c)
def box(n,x,y,z,w,d,h,m=pale,c=CITY,ang=0):
 ca,sa=math.cos(ang),math.sin(ang)
 return prism(n,[(x+a*ca-b*sa,y+a*sa+b*ca) for a,b in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]],z,h,m,c)
def xy(r,a,variant='N1'):
 if variant=='N1':
  warp=1+.085*math.cos(2*a)+.045*math.sin(3*a)
  return (r*math.sin(a)*warp, r*math.cos(a)*.88*warp)
 # A broad horizontal, fully enclosing maritime plate, very different silhouette.
 return (r*math.sin(a)*(1+.12*math.cos(a)),r*math.cos(a)*.78)
def cap(a): return 1850+2500*max(0,math.cos(a/2.55*math.pi/2))**.66
def ringmesh(n,profile,a0,a1,variant,material=ivory,c=ARCH,steps=120):
 v=[]; K=len(profile)
 for i in range(steps+1):
  a=a0+(a1-a0)*i/steps
  for r,z in profile:
   x,y=xy(r,a,variant)
   zz=min(z,cap(a)) if variant=='N1' else z
   v.append((x,y,zz))
 f=[]
 for i in range(steps):
  for j in range(K): f.append((i*K+j,i*K+(j+1)%K,(i+1)*K+(j+1)%K,(i+1)*K+j))
 # Full circles reuse the coincident seam below during welding.
 if abs(a1-a0-2*math.pi)>1e-5:
  f.extend([tuple(range(K-1,-1,-1)),tuple(steps*K+j for j in range(K))])
 ob=mesh(n,v,f,material,c)
 bm=bmesh.new(); bm.from_mesh(ob.data); bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001); bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.001); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(ob.data); bm.free(); ob.data.update()
 return ob
def path(n,pts,r=8,m=bronze,c=CITY):
 cu=bpy.data.curves.new(n,'CURVE'); cu.dimensions='3D'; cu.bevel_depth=r; cu.bevel_resolution=1
 sp=cu.splines.new('POLY'); sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(n,cu); c.objects.link(o); cu.materials.append(m); return o

if opt.concept=='N1':
 # One closed inhabited cross-section swept around an OPEN climate valley.
 # Horizontal shelves are part of the primary mesh, not decorative floating disks.
 profile=[(1100,0),(2630,0),(2630,650),(2430,650),(2430,1350),(2340,1350),(2340,2200),(2220,2200),(2220,3000),(2130,3000),(2130,3900),(2040,4350),(1960,4350),(1960,3500),(1810,3500),(1810,2800),(1590,2800),(1590,2100),(1360,2100),(1360,1300),(1100,1300)]
 mass=ringmesh('N1 / single thick climate escarpment',profile,-2.55,2.55,'N1')
 # An inhabitable horizontal garden joins both sides. Its front edge opens to the city.
 poly=[xy(1095,-2.55+5.10*i/90) for i in range(91)]
 garden=prism('N1 / open-sky climate ground',poly,1230,70,green,ENV)
 # Inner radial terraces are wide enough for actual districts; place broad civic volumes first.
 institutions=[('Climate forum',1250,-.66,1300,320,170,130),('Public archive',1480,.72,2100,370,160,160),('High university',1690,-.36,2800,390,160,175),('Sky conservatory',1870,.16,3500,360,110,150)]
 for name,r,a,z,w,d,h in institutions:
  x,y=xy(r,a); box(name,x,y,z,w,d,h,pale,ang=-a)
 for r,z,extent in [(1210,1300,2.50),(1470,2100,2.40),(1690,2800,1.93),(1880,3500,1.30)]:
  pts=[(*xy(r,-extent+2*extent*i/90),z+8) for i in range(91)]
  path('Continuous civic contour '+str(z),pts,7)
 if opt.refine:
  # Only low detail district massing: 65-110m blocks with real open courts and streets.
  # There are no windows, facade textures, trees, or ornamental detail.
  sites=[]
  for tier,(r,z,extent) in enumerate([(1220,1300,2.42),(1470,2100,2.20),(1690,2800,1.80),(1880,3500,1.05)]):
   count=int(2*extent*r/190)
   for i in range(count+1):
    a=-extent+2*extent*i/count
    if any(abs(a-q[2])<.24 and z==q[3] for q in institutions):continue
    x,y=xy(r,a); tang=-a; h=65+25*((i+2*tier)%4)
    # Three occupied wings surround a genuinely open 38m court.
    ca,sa=math.cos(tang),math.sin(tang)
    for k,(dx,dy,w,d) in enumerate([(-43,0,27,96),(43,0,27,96),(0,36,60,24)]):
     box('District %d-%02d wing %d'%(tier,i,k),x+dx*ca-dy*sa,y+dx*sa+dy*ca,z,w,d,h,ivory,ang=tang)
    sites.append({'tier':tier,'centre_m':[x,y,z],'court_width_m':59,'court_depth_m':60,'height_m':h})
  # At the rear, occupied terraces are also articulated; not a blank support face.
  for r,z,extent in [(2380,1350,1.6),(2270,2200,1.2),(2175,3000,.8)]:
   for i in range(17):
    a=-extent+2*extent*i/16
    if cap(a)<z+160:continue
    x,y=xy(r,a); box('Outer inhabited district '+str(z)+'-'+str(i),x,y,z,100,45,100,ivory,ang=-a)
  # Broad diagonal public ramps connect every shelf; rise/run recorded, not certified accessible.
  for idx,(r0,r1,z0,z1,a0,a1) in enumerate([(1240,1470,1300,2100,-2.25,-.95),(1470,1690,2100,2800,1.9,.7),(1690,1880,2800,3500,-1.45,-.3)]):
   vs=[]; N=80
   for i in range(N+1):
    t=i/N; a=a0+(a1-a0)*t; r=r0+(r1-r0)*t; x,y=xy(r,a); z=z0+(z1-z0)*t
    # Flat cross-section, actual 55m wide ground; thickness 25m.
    nx,ny=math.sin(a),math.cos(a)
    vs.extend([(x-27.5*nx,y-27.5*ny,z),(x+27.5*nx,y+27.5*ny,z),(x+27.5*nx,y+27.5*ny,z-25),(x-27.5*nx,y-27.5*ny,z-25)])
   fs=[(3,2,1,0),(4*N,4*N+1,4*N+2,4*N+3)]
   for i in range(N):
    for j in range(4):fs.append((i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j))
   mesh('Public ascent %d'%idx,vs,fs,bronze,CITY)
  (OUT/'districts.json').write_text(json.dumps(sites,indent=2),encoding='utf-8')
  # Human reference and mid-ground civic shelter at climate-garden level.
  box('12m public shelter',-340,-650,1300,12,8,8,pale)
  box('1.8m person reference',-334,-645,1300,.6,.4,1.8,bronze)
elif opt.concept=='N2':
 # A horizontal marine podium: a 2km sea is a real level surface, never an inclined ribbon.
 profile=[(1080,0),(2680,0),(2680,550),(2460,550),(2460,1050),(2260,1050),(2260,1600),(1980,1600),(1980,1850),(1730,1850),(1730,1550),(1350,1550),(1350,1450),(1080,1450)]
 mass=ringmesh('N2 / inhabited maritime plate',profile,-math.pi,math.pi,'N2')
 sea=prism('N2 / level inland sea',[xy(1075,2*math.pi*i/100,'N2') for i in range(100)],1390,60,water,ENV)
 # A SINGLE continuous rising headland, rather than repeated towers or support pylons.
 sections=[]
 for cy,w,dep,z0,z1 in [(1000,2100,600,1450,1800),(1450,1700,500,1000,2550),(1900,1100,400,550,3800),(2250,430,170,0,4300)]:
  sections.append([(-w/2,cy-dep,z0),(w/2,cy-dep,z0),(w/2,cy+dep,z0),(-w/2,cy+dep,z0),(-w/2,cy-dep,z1),(w/2,cy-dep,z1),(w/2,cy+dep,z1),(-w/2,cy+dep,z1)])
 # Each station defines one solid segment; all segments overlap the podium physically.
 for k in range(3):
  v=sections[k]+sections[k+1]; f=[]
  # Convex hull is a low detail continuous slope; no reuse of old GLB or shape.
  bm=bmesh.new()
  for co in v:bm.verts.new(co)
  bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
  me=bpy.data.meshes.new('Marine headland'); bm.to_mesh(me); bm.free()
  o=bpy.data.objects.new('N2 / rising headland '+str(k),me); ARCH.objects.link(o); me.materials.append(ivory)
 for i in range(11):
  a=-2.7+i*.49;x,y=xy(1530,a,'N2');box('Coastal public institution '+str(i),x,y,1550,350,130,170,pale,ang=-a)
 for r,z in [(1510,1550),(1850,1850),(2330,1050)]:path('Coastal civic route '+str(z),[(*xy(r,2*math.pi*i/100,'N2'),z+8) for i in range(101)],8)
elif opt.concept=='N3':
 # A solid urban landform: two unequal folded ridgelines are joined by occupied
 # terrain, not towers and bridges. The central valley is part of the same solid.
 # The mesh is a closed sampled height field; no CSG reuse from prior studies.
 def terrain_raw(x,y):
  # Outline is 5.2 x 4.8km, tapered unevenly by plan coordinates.
  q=(x/2650)**2+((y+100)/2400)**2
  if q>=1:return 0
  env=min(1,(1-q)/.23)
  env=env*env*(3-2*env)
  left=-1050+340*math.sin(y/1050)
  right=1050+250*math.sin(y/1200+.8)
  hleft=3100*math.exp(-((y-440)/1750)**4)*math.exp(-((x-left)/640)**4)
  hright=2370*math.exp(-((y+400)/1750)**4)*math.exp(-((x-right)/690)**4)
  # Rear civic watershed makes a physical inhabited connection between ridges.
  saddle=1350*math.exp(-((y-1250)/570)**4)*math.exp(-(x/1400)**6)
  return (1300+max(hleft,hright,saddle))*env
 def terrain(x,y):
  h=terrain_raw(x,y)
  if h<=1300:return h
  t=(h-1300)/350; k=math.floor(t);f=t-k
  # The broad horizontal inhabited terraces are actual geometry.
  blend=max(0,min(1,(f-.70)/.30));blend=blend*blend*(3-2*blend)
  return 1300+350*(k+blend)
 NX,NY=120,112
 vv=[]
 for j in range(NY+1):
  y=-2500+j*5000/NY
  for i in range(NX+1):
   x=-2800+i*5600/NX;vv.append((x,y,terrain(x,y)))
 ff=[]
 for j in range(NY):
  for i in range(NX):
   a=j*(NX+1)+i;face=(a,a+1,a+NX+2,a+NX+1)
   if any(vv[k][2]>0 for k in face):ff.append(face)
 used=sorted({k for face in ff for k in face});mapping={old:new for new,old in enumerate(used)}
 vv=[vv[k] for k in used];ff=[tuple(mapping[k] for k in face) for face in ff]
 edgecounts={}
 for face in ff:
  for a,b in zip(face,face[1:]+face[:1]):
   key=tuple(sorted((a,b)));edgecounts[key]=edgecounts.get(key,0)+1
 N=len(vv);vv.extend([(x,y,-35) for x,y,z in vv[:]])
 topfaces=ff[:];ff.extend([tuple(k+N for k in reversed(face)) for face in topfaces])
 for (a,b),count in edgecounts.items():
  if count==1:ff.append((a,b,b+N,a+N))
 mass=mesh('N3 / one occupied climate watershed',vv,ff,ivory)
 # Continuous valley park at 1300m is an environment and civic ground, not mist.
 parkpoly=[(-350,-1580),(350,-1580),(470,-1150),(450,-500),(320,200),(360,680),(-300,680),(-450,150),(-470,-700)]
 mass.data.materials.append(green)
 for p in mass.data.polygons:
  if abs(p.center.x)<510 and -1600<p.center.y<700 and abs(p.center.z-1300)<.01:p.material_index=1
 for name,x,y,z,w,d,h in [('Valley civic forum',0,-450,1300,340,220,140)]:
  # Pad elevation is documented; terrace collision is checked separately below.
  box(name,x,y,z,w,d,h,pale)
 if opt.refine:
  # Place districts only where the entire footprint is flat on the actual surface.
  sites=[]
  for y in range(-1700,1801,170):
   for x in range(-2000,2101,165):
    z=terrain(x,y)
    if z<1600:continue
    zs=[terrain(x+dx,y+dy) for dx in [-55,0,55] for dy in [-45,0,45]]
    if max(zs)-min(zs)>.01:continue
    if any(abs(x-a)<w/2+80 and abs(y-b)<d/2+70 for _,a,b,zz,w,d,h in [('A',-60,1250,2350,450,240,180),('B',-1100,250,4100,360,180,130)]):continue
    h=65+((x+y)//5%4)*20
    for k,(dx,dy,w,d) in enumerate([(-42,0,24,90),(42,0,24,90),(0,32,60,26)]):box('N3 district %d wing %d'%(len(sites),k),x+dx,y+dy,z,w,d,h,ivory)
    sites.append({'centre_m':[x,y,z],'court_width_m':60,'height_m':h,'flat_footprint_checked_m':[110,90]})
  (OUT/'districts.json').write_text(json.dumps(sites,indent=2),encoding='utf-8')
  box('12m valley shelter',-250,-940,1300,12,8,8,pale)
  box('1.8m person',-241,-935,1300,.6,.4,1.8,bronze)
  path('Valley civic avenue',[(-200,-1450,1306),(-180,-900,1306),(-200,-300,1306),(0,600,1306)],12)
else:
 baseline=ROOT/'references'/('dankaikyu_A.glb' if opt.concept=='OLD1' else 'dankaikyu_II_A.glb')
 bpy.ops.import_scene.gltf(filepath=str(baseline))
 for o in list(bpy.context.selected_objects):
  for c in list(o.users_collection):c.objects.unlink(o)
  ARCH.objects.link(o)

# Identical 10km context and absolute cameras for both candidates and rejected baseline.
box('10km city ground',0,0,-110,20000,20000,100,grey,CTX)
path('10km diameter reference',[ (5000*math.sin(i*math.tau/160),5000*math.cos(i*math.tau/160),1) for i in range(161)],6,bronze,CTX)
for x in [-3100,3100]:box('100m datum '+str(x),x,-2500,0,30,30,100,pale,CTX)
def camera(n,pos,target,ortho=None,lens=38):
 ca=bpy.data.cameras.new(n); ob=bpy.data.objects.new(n,ca); CAM.objects.link(ob); ob.location=pos; ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler(); ca.lens=lens; ca.clip_start=.1; ca.clip_end=60000
 if ortho:ca.type='ORTHO';ca.ortho_scale=ortho
 return ob
camera('01_FRONT',(0,-13000,2600),(0,0,2200),8000)
camera('02_OBLIQUE',(-8500,-10500,7200),(0,0,2100),8000)
camera('03_SIDE',(-13000,0,3000),(0,0,2200),8000)
camera('04_TOP',(0,-.1,15000),(0,0,0),8000)
camera('05_REAR',(7000,11000,6500),(0,0,2100),8000)
camera('06_INTERIOR',(-320,-720,1301.7),(0,1050,2400),lens=38)
if opt.concept=='N2':
 cam=bpy.data.objects['06_INTERIOR'];cam.location=(1650,-180,1551.7);cam.rotation_euler=(Vector((-900,300,2200))-cam.location).to_track_quat('-Z','Y').to_euler()
x,y=xy(1690,-.82)
if opt.concept=='N3':
 bpy.data.objects['06_INTERIOR'].location=(-250,-1050,1301.7)
 bpy.data.objects['06_INTERIOR'].rotation_euler=(Vector((0,600,1900))-bpy.data.objects['06_INTERIOR'].location).to_track_quat('-Z','Y').to_euler()
 # Exact flat terrace selected algorithmically, with no floating camera.
 candidates=[]
 for yy in range(-900,1200,30):
  for xx in range(-1550,-650,30):
   zz=terrain(xx,yy)
   if 2800<zz<4000 and max(terrain(xx+dx,yy+dy) for dx in [-8,8] for dy in [-8,8])-min(terrain(xx+dx,yy+dy) for dx in [-8,8] for dy in [-8,8])<.01:candidates.append((xx,yy,zz))
 x,y,z=min(candidates,key=lambda q:abs(q[1]+500)+abs(q[2]-3400))
 camera('07_HIGH_CITY',(x,y,z+1.7),(x+800,y+450,z+180),lens=38)
else:camera('07_HIGH_CITY',(x,y,2801.7),(*xy(1690,-.3),2920),lens=38)
world=bpy.data.worlds.new('Fixed studio');S.world=world;world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.36,.43,.51,1);bg.inputs['Strength'].default_value=.6
li=bpy.data.lights.new('Fixed sun','SUN');lo=bpy.data.objects.new('Fixed sun',li);S.collection.objects.link(lo);lo.rotation_euler=(.46,-.55,-.45);li.energy=2.7;li.angle=.12
S.render.engine='CYCLES';S.cycles.samples=12;S.cycles.use_denoising=True
S.render.resolution_x=1120;S.render.resolution_y=980;S.render.resolution_percentage=55 if opt.preview else 100;S.render.image_settings.file_format='PNG';S.view_settings.view_transform='AgX'
S.render.threads_mode='FIXED';S.render.threads=10
S.camera=bpy.data.objects['02_OBLIQUE']
def signature(obs):
 rec=[]
 for o in sorted(obs,key=lambda o:o.name):
  d={'name':o.name,'matrix':[list(r) for r in o.matrix_world]}
  if o.type=='MESH':d['v']=[list(v.co) for v in o.data.vertices];d['p']=[list(p.vertices) for p in o.data.polygons]
  elif o.type=='CURVE':d['p']=[[list(p.co) for p in s.points] for s in o.data.splines]
  rec.append(d)
 return hashlib.sha256(json.dumps(rec,sort_keys=True).encode()).hexdigest()
bpy.context.view_layer.update()
if opt.concept in ['N2','N3']:
 for n in (['06_INTERIOR','07_HIGH_CITY'] if opt.concept=='N3' else ['06_INTERIOR']):
  cam=bpy.data.objects[n]
  hit,p,no,idx,ob,ma=S.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector((cam.location.x,cam.location.y,6000)),Vector((0,0,-1)),distance=6500)
  assert hit and ob==mass,(n,hit,ob.name if hit else None)
  cam.location.z=p.z+1.7
 bpy.context.view_layer.update()
obs=list(ARCH.objects)+list(ENV.objects)+list(CITY.objects)
points=[o.matrix_world@Vector(v) for o in obs if o.type=='MESH' for v in o.bound_box]
low=[min(p[k] for p in points) for k in range(3)];high=[max(p[k] for p in points) for k in range(3)]
manifest={'concept':opt.concept,'stage':'selected low detail urban massing' if opt.refine else 'macro comparison','units':'metres','geometry_sha256':signature(obs),'bounds_m':{'min':low,'max':high,'size':[high[k]-low[k] for k in range(3)]},'cameras':{o.name:{'position_m':list(o.location),'target_orientation':[list(r) for r in o.matrix_world],'projection':o.data.type,'ortho_scale_m':o.data.ortho_scale,'lens_mm':o.data.lens} for o in CAM.objects},'environment':{'N1':'open sky climate court - NO simulated atmosphere','N2':'opaque horizontal sea - NO fluid simulation','N3':'open sky climate valley - terrain material only, NO atmosphere simulation','OLD':'rejected imported source with original materials','OLD1':'rejected imported source with original materials'}[opt.concept],'render':{'engine':S.render.engine,'samples':S.cycles.samples,'resolution':[int(S.render.resolution_x*S.render.resolution_percentage/100),int(S.render.resolution_y*S.render.resolution_percentage/100)],'sun_energy':li.energy,'exposure':S.view_settings.exposure},'renders':[],'formal_adoption':'USER_REVIEW_REQUIRED','construction':'HOLD'}
if not opt.concept.startswith('OLD'):
 bm=bmesh.new();bm.from_mesh(mass.data)
 manifest['primary_mesh']={'vertices':len(bm.verts),'faces':len(bm.faces),'non_manifold_edges':sum(not e.is_manifold for e in bm.edges),'volume_m3':abs(bm.calc_volume(signed=True))};bm.free()
if opt.refine or opt.concept in ['N2','N3']:
 manifest['pedestrian_floor_checks']={}
 for n in (['06_INTERIOR','07_HIGH_CITY'] if opt.concept=='N3' else ['06_INTERIOR']):
  o=bpy.data.objects[n];hit,p,no,idx,ob,ma=S.ray_cast(bpy.context.evaluated_depsgraph_get(),o.location,Vector((0,0,-1)),distance=3)
  d={'hit':hit,'floor_object':ob.name if hit else None,'floor_z_m':p.z if hit else None,'eye_height_m':o.location.z-p.z if hit else None};manifest['pedestrian_floor_checks'][n]=d
  assert hit and abs(d['eye_height_m']-1.7)<.05,d
S['status']='ART-FIRST / research only / formal adoption USER REVIEW / M247-C and Minecraft HOLD'
if not opt.concept.startswith('OLD'):
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'study.blend'),compress=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(OUT/'study.glb'),use_selection=True,export_format='GLB',export_cameras=False,export_lights=False)
if (OUT/'manifest.json').exists():
 previous=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
 if previous['geometry_sha256']==manifest['geometry_sha256'] and previous['render']==manifest['render']:
  manifest['renders']=[v for v in previous['renders'] if v['camera'] not in opt.views.split(',')]
for name in opt.views.split(','):
 S.camera=bpy.data.objects[name];S.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
 manifest['renders'].append({'camera':name,'file':name+'.png','geometry_sha256':signature(obs)})
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('B2-G4 DONE',opt.concept,manifest['bounds_m'])
