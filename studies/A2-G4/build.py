"""A2-G4 original mesh blockouts. Blender 5.2. Metres. No external assets.
Run blender -b --factory-startup --python build.py
Exports GLB, reimports it, measures that mesh and renders that same geometry.
"""
import bpy, math, os, json, random, sys
from mathutils import Vector
R=os.path.dirname(os.path.abspath(__file__))
os.makedirs(R+'/renders',exist_ok=True)
def mat(n,c):
 m=bpy.data.materials.new(n); m.diffuse_color=(*c,1);m.use_nodes=True
 p=next(x for x in m.node_tree.nodes if x.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.78
 return m
def mesh(n,v,f,m):
 d=bpy.data.meshes.new(n);d.from_pydata(v,[],f);d.update();o=bpy.data.objects.new(n,d);bpy.context.collection.objects.link(o);o.data.materials.append(m);return o
def box(n,p,s,m):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);return o
def sweep(n,func,profile,start,end,m,N=140):
 v=[];L=len(profile)
 for i in range(N+1):
  t=start+(end-start)*i/N;a,r,z=func(t)
  for dr,dz in profile:v.append(((r+dr)*math.cos(a),(r+dr)*math.sin(a),z+dz))
 f=[tuple(reversed(range(L)))]
 for i in range(N):
  for j in range(L):f.append((i*L+j,i*L+(j+1)%L,(i+1)*L+(j+1)%L,(i+1)*L+j))
 f.append(tuple(N*L+j for j in range(L)))
 return mesh(n,v,f,m)
def cut(ob,tool):
 bpy.context.view_layer.objects.active=ob;md=ob.modifiers.new('public_space_subtraction','BOOLEAN');md.operation='DIFFERENCE';md.solver='EXACT';md.object=tool;bpy.ops.object.modifier_apply(modifier=md.name);bpy.data.objects.remove(tool,do_unlink=True)
def reset():
 bpy.ops.wm.read_factory_settings(use_empty=True)
def pointcam(name,eye,target,ortho=None):
 bpy.ops.object.camera_add(location=eye);c=bpy.context.object;c.name=name;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.clip_end=100000;c.data.clip_start=.5
 if ortho:c.data.type='ORTHO';c.data.ortho_scale=ortho
 else:c.data.type='PERSP';c.data.lens=22;c.data.sensor_width=36
 return c
cams={
 '01_front':([0,-14000,3100],[0,0,2800],8500),
 '02_oblique':([11000,-14000,9400],[0,0,2800],8500),
 '03_side':([14000,0,3100],[0,0,2800],8500),
 '04_aerial':([9000,-11000,17000],[0,0,2800],8500),
 '05_back':([0,14000,3100],[0,0,2800],8500)}
audit={'units':'metres','external_cameras':cams,'external_resolution':[1000,900],'generative_images':False,'formal_art_acceptance':False,'models':{}}
if os.path.exists(R+'/validation.json'):
 with open(R+'/validation.json',encoding='utf8') as f:audit=json.load(f)
keys=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['P1','P2','P2R']
for key in keys:
 reset();ivory=mat('city-bearing ivory',(.72,.76,.73));gold=mat('public institutions ochre',(.53,.34,.14));urban=mat('residential district markers',(.16,.31,.34));pav=mat('public terraces',(.37,.46,.43))
 facilities=[];districts=[]
 if key=='P1':
  # A continuous thick urban fold; cross-section stepped toward the shared sky.
  def path(t):return (-2.35+6.65*t,1750+320*math.sin(math.pi*t),650+4600*t)
  profile=[(-780,-480),(800,-480),(800,650),(440,510),(80,510),(80,330),(-350,330),(-350,150),(-780,150)]
  body=sweep('P1_CONTINUOUS_CITY_FOLD',path,profile,0,1,ivory)
  # Three 400m-wide civic galleries carved into the very same urban ground.
  for j,t in enumerate([.21,.50,.79]):
   a,r,z=path(t);q=box('cutter',(r*math.cos(a),r*math.sin(a),z-80),(2000,460,330),gold);q.rotation_euler.z=a;cut(body,q)
   facilities.append({'id':'gallery_'+str(j),'centre_m':[r*math.cos(a),r*math.sin(a),z-80],'clearance_m':[2000,460,330],'roof_is_city_ground':True,'scope':'single oriented box subtraction; no room fit-out'})
  # Terraced districts are blockout markers, not complete inhabited cities.
  for k,t in enumerate([.12,.28,.43,.60,.76,.90]):
   a,r,z=path(t)
   for j in range(6):
    aa=a+(j-2.5)*.047;rr=r+250;zz=path(t+(aa-a)/6.65)[2]+510
    o=box('P1_District_%02d_block_%02d'%(k,j),(rr*math.cos(aa),rr*math.sin(aa),zz+55),(110,85,110+20*(j%2)),urban);o.rotation_euler.z=aa
   districts.append({'id':k,'surface_altitude_m':z+510,'blocks':6,'nominal_street_gap_m':20,'population':None})
  # Thick foot reaches ground: no float or separately attached monument pedestal.
  a,r,z=path(0);box('P1_ground_transfer',(r*math.cos(a),r*math.sin(a),200),(1200,1300,400),ivory)
  internal=([0,-2200,652],[0,700,3400],None)
 else:
  # A single terraced civic mountain with three non-concentric public courts.
  # Shared floors are the solids between stepped courtyard voids, never three boxes.
  N=120;v=[];rings=[]
  levels=[(0,2950,0,0),(450,3000,0,0),(1250,2780,-90,50),(2300,2440,-210,160),(3350,2090,-400,280),(4250,1760,-540,430),(5050,1400,-680,550),(5600,950,-760,600)]
  if key=='P2R':
   levels=[(0,3000,0,0),(400,3000,0,0),(1500,2800,0,0),(1500,2250,-100,100),(1950,2250,-100,100),(3350,2100,-170,200),(3350,1550,-370,350),(3900,1550,-370,350),(5050,1400,-530,480),(5050,850,-700,600),(5600,850,-700,600)]
  for z,rad,cx,cy in levels:
   ring=[]
   for i in range(N):
    a=2*math.pi*i/N;r=rad*(1+.075*math.cos(3*a+.4));ring.append(len(v));v.append((cx+r*math.cos(a),cy+r*math.sin(a),z))
   rings.append(ring)
  f=[tuple(reversed(rings[0]))]
  for j in range(len(rings)-1):
   for i in range(N):f.append((rings[j][i],rings[j][(i+1)%N],rings[j+1][(i+1)%N],rings[j+1][i]))
  f.append(tuple(rings[-1]));body=mesh('P2_SINGLE_SHARED_CIVIC_MASS',v,f,ivory)
  # Broad open courts: lower assembly / middle library / upper academy.
  courts=[('assembly',650,-1300,500,1350,950),('library',-850,150,2300,1100,820),('academy',-650,650,4250,800,610)]
  if key=='P2R':courts=[('assembly',100,-1950,450,1400,1250),('library',1350,100,2150,1250,1000),('academy',-650,1450,3950,1000,1100)]
  for label,cx,cy,floor,rx,ry in courts:
   # A stepped inward court whose open top and entry cut change the exterior.
   vv=[];NN=64
   ceiling=floor+800 if key=='P2R' else 7000
   for zz,scale in [(floor,1),(floor+350,1),(ceiling,.88 if key=='P2R' else 1.18)]:
    for i in range(NN):a=2*math.pi*i/NN;vv.append((cx+rx*scale*math.cos(a),cy+ry*scale*math.sin(a),zz))
   ff=[tuple(reversed(range(NN)))]+[(k*NN+i,k*NN+(i+1)%NN,(k+1)*NN+(i+1)%NN,(k+1)*NN+i) for k in range(2) for i in range(NN)]+[tuple(2*NN+i for i in range(NN))]
   cut(body,mesh('court_subtractor',vv,ff,ivory))
   # A 300m high public hall opens radially from court to exterior, sharing roof with district above.
   if key!='P2R':
    q=box('public_entry',(cx,cy-1100,floor+160),(600,2300,320),gold);cut(body,q)
   facilities.append({'id':label,'court_floor_z_m':floor,'court_radii_m':[rx,ry],'public_hall_clearance_m':[600,2300,320],'roof_is_city_ground':True,'scope':'court and hall subtractions; sharing is geometric not operational'})
   # Exposed ledge toward rear of each court, attached to main mass, wide enough for a street.
   # Follow court ellipse; marker bases are checked later, not assumed supported.
   for j in range(0 if key=='P2R' else 8):
    a=.12+math.pi*j/7;rrx=rx+100;rry=ry+100;x=cx+rrx*math.cos(a);y=cy+rry*math.sin(a)
    # No floating city markers: locate actual outer surface at this x/y with a vertical ray.
    hit,loc,n,ind=body.ray_cast(Vector((x,y,7000)),Vector((0,0,-1)))
    if hit:
     o=box('P2_'+label+'_district_'+str(j),(x,y,loc.z+50),(100,90,100),urban);o.rotation_euler.z=a
   districts.append({'id':label,'court_floor_z_m':floor,'blocks_requested':8,'population':None})
  if key=='P2R':
   # Three broad horizontal populated terraces; public halls below share these roofs.
   for level,rad,cx,cy in [(1500,2540,0,0),(3350,1810,-170,200),(5050,1110,-530,480)]:
    for j in range(36):
     a=2*math.pi*j/36;r=rad*(1+.075*math.cos(3*a+.4));x=cx+r*math.cos(a);y=cy+r*math.sin(a)
     for lane in [0,1]:
      rr=r+lane*130;x=cx+rr*math.cos(a);y=cy+rr*math.sin(a)
      o=box('P2R_district_%d_%d_%d'%(level,j,lane),(x,y,level+40),(80,95,80),urban);o.rotation_euler.z=a
   districts=[{'id':str(z),'surface_altitude_m':z,'nominal_blocks':72,'note':'Horizontal terrace blockouts; streets and support require verification'} for z in [1500,3350,5050]]
   internal=([100,-2200,452],[100,-1000,1050],None)
  else:internal=([650,-1750,502],[0,-500,2400],None)
 # Mesh bounds exclude context, lights and cameras.
 modelobs=list(bpy.context.scene.objects)
 verts=[o.matrix_world@p.co for o in modelobs if o.type=='MESH' for p in o.data.vertices]
 bounds=[[min(p[k] for p in verts) for k in range(3)],[max(p[k] for p in verts) for k in range(3)]]
 # Export architecture alone and then render only the reimported GLB geometry.
 bpy.ops.object.select_all(action='SELECT')
 bpy.ops.export_scene.gltf(filepath=R+'/'+key+'.glb',export_format='GLB',use_selection=True)
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 bpy.ops.import_scene.gltf(filepath=R+'/'+key+'.glb')
 imported=[o for o in bpy.context.scene.objects if o.type=='MESH']
 vv=[o.matrix_world@p.co for o in imported for p in o.data.vertices]
 bb=[[min(p[k] for p in vv) for k in range(3)],[max(p[k] for p in vv) for k in range(3)]]
 dims=[bb[1][k]-bb[0][k] for k in range(3)]
 # District support probe against primary mass after GLB round trip.
 main=next(o for o in imported if 'CONTINUOUS_CITY' in o.name or 'SINGLE_SHARED' in o.name)
 support=[]
 for o in imported:
  if 'district' in o.name.lower() or 'District' in o.name:
   w=[o.matrix_world@p.co for p in o.data.vertices];x=sum(p.x for p in w)/len(w);y=sum(p.y for p in w)/len(w);z=min(p.z for p in w)
   hit,p,n,idx=main.ray_cast(main.matrix_world.inverted()@Vector((x,y,z+1)),Vector((0,0,-1)))
   gap=(z-(main.matrix_world@p).z) if hit else None
   support.append({'object':o.name,'vertical_gap_m':gap,'within_5m':gap is not None and abs(gap)<5})
 audit['models'][key]={'glb_reimport':'SUCCESS','bounds_m':bb,'dimensions_m':dict(zip(['width','depth','height'],dims)),'mesh_objects':len(imported),'triangles':sum(len(o.data.polygons) for o in imported),'bounds_roundtrip_max_error_m':max(abs(bounds[i][k]-bb[i][k]) for i in range(2) for k in range(3)),'facilities':facilities,'districts':districts,'district_support_probes':support,'internal_camera':internal,'limits':['Blockout markers are not complete cities','No structure, services, accessibility or gravity transition engineering','No claim that N3 four-horizon visibility survives redesign','Public-space subtraction is not occupied floor-area validation']}
 ground=mat('10km context',(.12,.17,.20));box('10km_scale_ground',(0,0,-65),(10000,10000,100),ground)
 # 100m high context silhouettes set apart from architecture; regular scale evidence only.
 for x in [-4200,-3600,3600,4200]:
  for y in [-4200,-3600,3600,4200]:box('context_100m',(x,y,50),(180,180,100),pav)
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
 sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=True;sc.render.threads_mode='FIXED';sc.render.threads=8
 sc.render.resolution_x=1000;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
 sc.world=bpy.data.worlds.new('diffuse study sky');sc.world.use_nodes=True;bg=next(n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.45,.55,.70,1);bg.inputs['Strength'].default_value=.65
 bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=(.35,-.45,-.4);sun.data.energy=3;sun.data.angle=.12
 for view,(eye,target,span) in {**cams,'06_inside':internal}.items():
  c=pointcam(view,eye,target,span);sc.camera=c;sc.render.filepath=R+'/renders/'+key+'_'+view+'.png';bpy.ops.render.render(write_still=True)
 bpy.ops.wm.save_as_mainfile(filepath=R+'/'+key+'.blend',compress=True)
 with open(R+'/validation.json','w',encoding='utf8') as f:json.dump(audit,f,ensure_ascii=False,indent=2)
