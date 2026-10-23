"""Blender 5.2 batch: --python build_scene.py -- --concept A|B [--occupied]. Metres."""
import bpy, bmesh, math, json, argparse, sys, hashlib
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--concept',choices=['A','B'],required=True);p.add_argument('--occupied',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
OUT=Path(__file__).resolve().parent/(a.concept+('_occupied' if a.occupied else '_massing'));OUT.mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC'
def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8;return m
stone=mat('Civic mineral structure',(.43,.53,.55));roof=mat('Horizontal public ground',(.73,.78,.68));route=mat('Street seams / transport',(.18,.49,.51));home=mat('Occupied district envelopes',(.78,.66,.48));park=mat('Public courtyards',(.35,.48,.34));ctx=mat('Unregistered ten km context',(.24,.3,.34))
arch=[];grounds=[];districts=[];routes=[]
def mesh(n,v,f,m,architecture=True):
 me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();ob=bpy.data.objects.new(n,me);s.collection.objects.link(ob);ob.data.materials.append(m)
 if architecture:arch.append(ob)
 return ob
def prism(n,poly,z0,z1,m,architecture=True):
 N=len(poly);v=[(x,y,z) for z in (z0,z1) for x,y in poly];f=[tuple(reversed(range(N))),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 return mesh(n,v,f,m,architecture)
def box(n,x,y,z,w,d,h,m,architecture=True):return prism(n,[(x-w/2,y-d/2),(x+w/2,y-d/2),(x+w/2,y+d/2),(x-w/2,y+d/2)],z,z+h,m,architecture)
def beam(n,p,q,w,h,m):
 x,y,z=p;X,Y,Z=q;dx=X-x;dy=Y-y;L=math.hypot(dx,dy);u=-dy/L*w/2;v=dx/L*w/2
 return mesh(n,[(x+u,y+v,z),(x-u,y-v,z),(X-u,Y-v,Z),(X+u,Y+v,Z),(x+u,y+v,z+h),(x-u,y-v,z+h),(X-u,Y-v,Z+h),(X+u,Y+v,Z+h)],[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)
def ground(n,x,y,z,w,d):
 box(n,x,y,z-32,w,d,32,roof);grounds.append(dict(id=n,center=[x,y,z],size=[w,d],area_m2=w*d))
 if a.occupied:
  # Four occupied perimeter bands enclose a real open-air court. Main streets stay between bands.
  for i in range(3):
   for j in range(2):
    cx=x+(i-1)*w/3;cy=y+(j-.5)*d/2;bw=w/3-38;bd=d/2-38;t=24
    for k,(xx,yy,ww,dd) in enumerate([(cx,cy-bd/2+t/2,bw,t),(cx,cy+bd/2-t/2,bw,t),(cx-bw/2+t/2,cy,t,bd-2*t),(cx+bw/2-t/2,cy,t,bd-2*t)]):
     box(n+f'_court_{i}_{j}_{k}',xx,yy,z,ww,dd,32+8*((i+j)%3),home)
    box(n+'_court_ground',cx,cy,z+.1,bw-2*t,bd-2*t,.2,park)
    districts.append(dict(ground=n,center=[cx,cy,z],court=[bw-2*t,bd-2*t],envelope_only=True))
  box(n+'_school_market',x,y,z+1,76,48,22,route)
if a.concept=='A':
 # Lateral cellular accretion: offset city lobes with through-streets. No bored mountain or gate shell.
 cells=[(-1130,-550,620,900,1080),(-400,-780,1180,650,1020),(400,-450,1660,760,1000),(1140,-50,1020,660,1120),(-850,650,1460,850,1000),(100,730,1940,820,980),(1030,1020,1540,720,900)]
 for i,(x,y,z,w,d) in enumerate(cells):
  # Two volumetric urban flanks, separated by an open-ended internal street slot.
  gap=110
  for sg in (-1,1):
   xx=x+sg*(gap/2+(w-gap)/4)
   box(f'A{i}_inhabitable_flank_{sg}',xx,y-160,0,(w-gap)/2,d-320,z-262,stone)
   ground(f'A{i}_shoulder_{sg}',xx,y-160,z-230,(w-gap)/2,d-320)
  # Rear cross connection occurs at a single local level, leaving open sky along most of the slot.
  ground(f'A{i}_confluence',x,y+d/2-160,z,w,320)
  box(f'A{i}_deep_civic_core',x,y+d/2-160,0,w,320,z-32,stone)
  beam(f'A{i}_internal_street',(x,y-d/2,8),(x,y+d/2-330,8),76,6,route)
  for sg in (-1,1):box(f'A{i}_vertical_interchange_{sg}',x+sg*65,y+d/2-340,0,34,50,z,route)
  routes.append(dict(type='open_ended_street_and_twin_vertical_transport',cell=i,top_z=z,vertical_access='envelope_only'))
 for k,(i,j) in enumerate([(0,1),(1,2),(2,3),(0,4),(4,5),(5,6),(2,5)]):
  x,y,z,w,d=cells[i];X,Y,Z,W,D=cells[j]
  # Sloped bands are transport, never represented as walkable streets.
  beam(f'A_transfer_{k}',(x,y+d/2-120,z),(X,Y+D/2-120,Z),100,35,route)
  routes.append(dict(type='inclined_transit_not_walkway',start=[x,y+d/2-120,z],end=[X,Y+D/2-120,Z],gradient=abs(Z-z)/math.hypot(X-x,Y+D/2-y-d/2)))
else:
 # Network first: three deep inhabited ribbons split and reunite at different heights.
 paths=[[(-1900,-1300,240),(-900,-600,850),(200,-300,1650),(1600,900,1900)], [(-1700,1100,350),(-800,400,1300),(200,-300,1650),(1700,-1000,850)], [(-300,-1800,180),(400,-500,1100),(800,500,1500),(300,1800,1100)]]
 seen_nodes=set()
 for i,path in enumerate(paths):
  for j,(P,Q) in enumerate(zip(path,path[1:])):
   beam(f'B{i}_deep_city_ribbon_{j}',P,Q,480,228,stone)
   beam(f'B{i}_transit_{j}',(P[0],P[1],P[2]+265),(Q[0],Q[1],Q[2]+265),60,15,route)
  for j,(x,y,z) in enumerate(path[1:]):
   if (x,y,z) in seen_nodes:continue
   seen_nodes.add((x,y,z))
   box(f'B{i}_inhabited_support_{j}',x,y,0,330,400,z,stone);ground(f'B{i}_horizontal_district_{j}',x,y,z+260,650,590)
   routes.append(dict(type='inclined_transit_and_horizontal_station_city',node=[x,y,z+260]))
# Context is a diagram, not a registered W0 model. 10 km square and low proxy districts only.
box('10km comparison frame',0,0,-90,10000,10000,65,ctx,False)
for x in range(-4200,4201,1400):
 for y in range(-4200,4201,1400):
  if abs(x)<2400 and abs(y)<2400:continue
  box('Context urban tile',x,y,-20,700,600,50,stone,False)
world=bpy.data.worlds.new('Daylight');s.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs['Color'].default_value=(.52,.65,.74,1);world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
ld=bpy.data.lights.new('Sun','SUN');ob=bpy.data.objects.new('Sun',ld);s.collection.objects.link(ob);ld.energy=3;ld.angle=.12;ob.rotation_euler=(.45,-.65,-.4)
cams={}
for n,pos,target,scale in [('oblique',(6200,-8500,5700),(0,100,900),5900),('side',(10000,0,2400),(0,100,950),5900),('rear',(-5500,8500,4900),(0,100,950),5900),('context',(10000,-14000,13000),(0,0,200),14500)]:
 ca=bpy.data.cameras.new(n);ob=bpy.data.objects.new(n,ca);s.collection.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();ca.type='ORTHO';ca.ortho_scale=scale;ca.clip_end=50000;cams[n]=ob
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=10;s.render.resolution_x=960;s.render.resolution_y=760;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
bpy.context.view_layer.update()
def signature():
 h=hashlib.sha256()
 for ob in arch:
  h.update(ob.name.encode());h.update(str([tuple(v.co) for v in ob.data.vertices]).encode())
 return h.hexdigest()
sig=signature();pts=[ob.matrix_world@Vector(v) for ob in arch for v in ob.bound_box];lo=[min(v[k] for v in pts) for k in range(3)];hi=[max(v[k] for v in pts) for k in range(3)]
nonmanifold=0
for ob in arch:
 bm=bmesh.new();bm.from_mesh(ob.data);nonmanifold+=sum(not e.is_manifold for e in bm.edges);bm.free()
manifest=dict(study_id='B2-G7',concept=a.concept,stage='LOW_DETAIL_OCCUPIED_ENVELOPES' if a.occupied else 'SIMPLE_VOLUMETRIC_COMPARISON',units='metres',bounds_m=dict(min=lo,max=hi,size=[hi[k]-lo[k] for k in range(3)]),geometry_sha256=sig,mesh_objects=len(arch),vertices=sum(len(o.data.vertices) for o in arch),nonmanifold_edges_per_object=nonmanifold,grounds=grounds,districts=districts,routes=routes,cameras={n:dict(position=list(o.location),target=([0,0,200] if n=='context' else [0,100,900 if n=='oblique' else 950]),ortho_scale=o.data.ortho_scale) for n,o in cams.items()},qa_limits=['closed individual solids only; intersecting assemblies are not a watertight unified building','no structural, wind, daylight, circulation collision or egress certification','district program is an envelope hypothesis; interiors not designed'],formal_adoption=False,coordinate_registration='NONE',minecraft='HOLD',work='PRIOR_APPROVAL_REQUIRED',renders=[])
s.camera=cams['oblique'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'study.blend'),compress=True)
# Comparison stages remain BLEND massing, only the selected occupied test gets a portable GLB.
if a.occupied:
 bpy.ops.object.select_all(action='DESELECT')
 for ob in arch:ob.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(OUT/'study.glb'),use_selection=True,export_format='GLB')
for n,cam in cams.items():
 s.camera=cam;s.render.filepath=str(OUT/(n+'.png'));bpy.ops.render.render(write_still=True);assert sig==signature();manifest['renders'].append(dict(path=n+'.png',geometry_sha256=sig))
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('COMPLETE',a.concept,a.occupied,len(arch),nonmanifold)
