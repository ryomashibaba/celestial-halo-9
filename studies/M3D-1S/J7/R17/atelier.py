"""R17 native architecture atelier. Metres, isolated research coordinates.
Hand-authored city bodies, not a world importer. No Minecraft filesystem access.
"""
import bpy, bmesh, math, json, sys, hashlib
from pathlib import Path
from mathutils import Vector, Matrix, Euler
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
def setup():
 bpy.ops.wm.read_factory_settings(use_empty=True)
 global S,ARCH,ENV,P,D,G,B,F,W,L,V
 S=bpy.context.scene;S.unit_settings.system='METRIC';S.unit_settings.scale_length=1
 ARCH=bpy.data.collections.new('R17_URBAN_CONTINENTS');S.collection.children.link(ARCH)
 ENV=bpy.data.collections.new('STUDIO_NONCANONICAL');S.collection.children.link(ENV)
 P=material('Porcelain titanium',(.64,.73,.75),.35,.35)
 D=material('Midnight occupied substructure',(.035,.075,.10),.35,.5)
 G=material('Deep blue glazed inhabited faces',(.035,.18,.21),.45,.23)
 B=material('Pale champagne edges',(.38,.27,.13),.5,.4)
 F=material('Warm civic mineral',(.58,.56,.46),.15,.6)
 W=material('Quiet jade water',(.035,.28,.29),.5,.18)
 L=material('Warm interior light',(.9,.63,.31),.1,.4,1.4)
 V=material('Garden canopy',(.09,.20,.14),0,.85)
 S.render.engine='CYCLES';S.cycles.samples=16;S.cycles.use_denoising=True
 S.render.resolution_x=1100;S.render.resolution_y=1000;S.render.resolution_percentage=100
 S.render.image_settings.file_format='PNG';S.render.threads_mode='FIXED';S.render.threads=6
 S.world=bpy.data.worlds.new('Pale blue ambient');S.world.use_nodes=True
 bg=next(n for n in S.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.27,.36,.44,1);bg.inputs[1].default_value=.65
 S.view_settings.view_transform='AgX'
 mesh('Review ground',[(-100000,-100000,-70),(100000,-100000,-70),(100000,100000,-70),(-100000,100000,-70)],[(0,1,2,3)],material('Backdrop',(.115,.16,.19)),ENV)
 sun=bpy.data.lights.new('Sun','SUN');sun.energy=2.8;sun.angle=.16
 ob=bpy.data.objects.new('Sun',sun);ENV.objects.link(ob);ob.rotation_euler=(.4,-.5,-.5)
 for name,loc,power,size in [('Front soft sky',(-2000,-4000,6000),3e9,5000),('Rear reflected sky',(2500,3000,4000),1.8e9,3500)]:
  data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
  ob=bpy.data.objects.new(name,data);ENV.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,1700))-ob.location).to_track_quat('-Z','Y').to_euler()
def material(name,c,metal=0,rough=.5,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
 p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 if emit:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emit
 return m
def mesh(n,vs,fs,mat,coll=None):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update()
 ob=bpy.data.objects.new(n,me);(coll or ARCH).objects.link(ob);me.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 return ob
def box(n,c,d,mat,coll=None):
 return mesh(n,[(c[0]+i*d[0]/2,c[1]+j*d[1]/2,c[2]+k*d[2]/2) for k in (-1,1) for j in (-1,1) for i in (-1,1)],[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],mat,coll)
def prism(n,poly,z0,z1,mat):
 N=len(poly);return mesh(n,[(x,y,z) for z in (z0,z1) for x,y in poly],[tuple(reversed(range(N))),tuple(range(N,N*2))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)],mat)
def loft(n,stations,mat,N=20):
 # horizontal rounded rectangular sections: x,y,z, half-width,half-depth
 vs=[]
 for x,y,z,rx,ry in stations:
  for i in range(N):
   a=i*2*math.pi/N;u=math.cos(a);v=math.sin(a)
   vs.append((x+rx*math.copysign(abs(u)**.60,u),y+ry*math.copysign(abs(v)**.60,v),z))
 return mesh(n,vs,[tuple(reversed(range(N))),tuple(range(len(vs)-N,len(vs)))]+[(k*N+i,k*N+(i+1)%N,(k+1)*N+(i+1)%N,(k+1)*N+i) for k in range(len(stations)-1) for i in range(N)],mat)
def tube(n,pts,r,mat,sides=10):
 vs=[]
 for i,p in enumerate(pts):
  tangent=(Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(0,i-1)])).normalized()
  u=tangent.cross(Vector((0,0,1)))
  if u.length<.01:u=tangent.cross(Vector((0,1,0)))
  u.normalize();v=tangent.cross(u).normalized()
  vs += [tuple(Vector(p)+r*(math.cos(j*2*math.pi/sides)*u+math.sin(j*2*math.pi/sides)*v)) for j in range(sides)]
 return mesh(n,vs,[tuple(reversed(range(sides))),tuple(range(len(vs)-sides,len(vs)))]+[(k*sides+j,k*sides+(j+1)%sides,(k+1)*sides+(j+1)%sides,(k+1)*sides+j) for k in range(len(pts)-1) for j in range(sides)],mat)
def ribbon(n,points,width,thick,mat):
 vs=[]
 for i,p in enumerate(points):
  t=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)]);u=Vector((-t.y,t.x,0)).normalized()*width/2
  vs += [tuple(Vector(p)+side*u+Vector((0,0,z))) for z in (-thick,0) for side in (-1,1)]
 fs=[(0,2,3,1),(len(vs)-4,len(vs)-3,len(vs)-1,len(vs)-2)]
 for k in range(len(points)-1):
  a=k*4;b=a+4;fs += [(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)]
 return mesh(n,vs,fs,mat)
def transform(obs,location,rot=(0,0,0)):
 M=Matrix.Translation(Vector(location))@Euler(rot).to_matrix().to_4x4()
 for o in obs:o.matrix_world=M@o.matrix_world
def polar_poly(rx,ry,N=24):
 return [(rx*math.copysign(abs(math.cos(i*2*math.pi/N))**.6,math.cos(i*2*math.pi/N)),ry*math.copysign(abs(math.sin(i*2*math.pi/N))**.6,math.sin(i*2*math.pi/N))) for i in range(N)]
def cut(o,n,c,d):
 cutter=box(n,c,d,D);bpy.context.view_layer.objects.active=o
 mod=o.modifiers.new('Designed real civic void','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
def bank(n,poly,z,h,mat):
 return prism(n,poly,z,z+h,mat)
def world(n,loc,w,d,h,style=0,rot=(0,0,0),detail=False):
 """The district IS a thick inhabited body: four civic levels around real open air.
 Public grounds, banks, interior streets and roofs jointly form the exterior.
 No later enclosing shell. Each style has a different street section/void.
 """
 old=set(ARCH.objects);levels=(0,.26,.56,.82)
 # Curved city banks with open internal valley, differ by authored section.
 for k,t in enumerate(levels):
  z=t*h;inset=(k%2)*w*.035;spread=w*(.46-.055*k)
  for side in (-1,1):
   inner=w*(.11+.025*k)+(w*.045 if style==1 else 0)
   poly=[(side*inner,-d*.46),(side*(spread-inset),-d*.52),(side*(spread+w*.07),-d*.24),(side*(spread+w*.04),d*.22),(side*spread,d*.48),(side*(inner+w*.03),d*.43)]
   bank(n+f'_city_ground_{k}_{side}',poly,z,32 if k else 65,D)
   # long blocks are 100-250m urban buildings; alternating cuts create real public courts.
   rows=5 if style!=2 else 4
   for j in range(rows):
    yy=-d*.38+j*d*.19;xx=side*(inner+spread)*.5
    rw=max(50,spread-inner-26);rd=d*(.12 if style!=1 else .145)
    bh=h*(.19 if (j+k)%3 else .24)
    if style==2:xx+=side*w*.035*(j%2);bh*=1.12
    poly2=[(xx-rw*.50,yy-rd*.45),(xx+rw*.5,yy-rd*.5),(xx+rw*.47,yy+rd*.5),(xx-rw*.43,yy+rd*.44)]
    ob=bank(n+f'_occupied_borough_{k}_{side}_{j}',poly2,z+32,bh,P if (j+k)%3 else F)
    # Each large borough has an actual 45-100m high inner street, never a dark decal.
    if (j+k)%2==0:cut(ob,n+'_cross_street',(xx,yy,z+32+bh*.45),(rw+10,rd*.33,bh*.44))
    # deep blue inhabited upper facings, framed by structural edges
    box(n+'_recessed_civic_face',(xx,yy-rd*.46,z+36+bh*.50),(rw*.84,4,bh*.71),G)
    box(n+'_roof_street',(xx,yy,z+32+bh+2),(rw*.94,rd*.88,4),F)
    if detail:
     for f in range(1,max(2,int(bh/12))):
      box(n+'_floor_reveal',(xx,yy-rd*.47,z+32+f*12),(rw*.90,7,1.8),P)
     for a in (-1,1):box(n+'_public_entrance_jamb',(xx+a*rw*.34,yy-rd*.49,z+42),(5,14,20),B)
   # far end district links integrate opposing shores, no dominant front gate.
   if (k+style)%2==0:
    ribbon(n+'_rear_ground_return',[(-inner,d*.36,z+32),(0,d*.42,z+32),(inner,d*.36,z+32)],d*.16,24,F)
  # Ground is open through multiple levels, bridges differ in direction.
  if k in ((0,2) if style==0 else (1,3)):
   pts=[(-w*.28,-d*.24,z+42),(0,-d*.13,z+58),(w*.28,d*.04,z+42)]
   ribbon(n+'_local_civic_crossing',pts,65,18,F)
 # Coherent deep end walls are built from vertical inhabited sections and landings.
 for side in (-1,1):
  pts=[(side*w*.44,-d*.42,0,w*.065,d*.07),(side*w*.39,-d*.39,h*.45,w*.055,d*.07),(side*w*.31,-d*.32,h*1.03,w*.045,d*.065)]
  loft(n+'_continuous_living_buttress',pts,P,12)
 # quiet public water and a narrow, continuous diagonal transport channel.
 ribbon(n+'_water_garden',[(0,-d*.43,68),(w*.035,0,68),(0,d*.38,68)],w*.08,3,W)
 tube(n+'_inclined_transit',[(w*.29,-d*.40,20),(w*.27,-d*.08,h*.48),(w*.23,d*.30,h*.95)],12,B)
 obs=set(ARCH.objects)-old;transform(obs,loc,rot)
 return list(obs)
def cameras():
 poses={
 '01_FRONT':((0,-13000,2650),(0,0,2050),8000),
 '02_OBLIQUE':((8800,-11000,7200),(0,0,1800),8700),
 '03_SIDE':((14000,0,2700),(0,0,2050),8000),
 '04_REAR':((0,14000,2900),(0,0,2050),8000),
 '05_AERIAL':((5000,-6500,12500),(0,0,1500),8700),
 '06_UNDERSIDE':((5500,-7000,-1300),(0,300,2100),8500),
 '07_GROUND_UP':((800,-4600,90),(-300,300,2300),None),
 '08_INTERIOR_LOW':((0,-1100,420),(-350,500,1750),None),
 '09_INTERIOR_MID':((300,-300,1550),(-500,1000,2350),None),
 '10_INTERIOR_HIGH':((-500,300,2750),(800,500,3000),None),
 '11_DISTRICT':((-3300,-2400,1800),(-1600,-300,850),None),
 '12_CITY_10KM':((12500,-16500,12500),(0,0,1450),14500),
 }
 for n,(loc,target,ortho) in poses.items():
  data=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,data);ENV.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();data.clip_start=.1;data.clip_end=200000;data.lens=23 if 'INTERIOR' in n else 29
  if ortho:data.type='ORTHO';data.ortho_scale=ortho
 S.camera=bpy.data.objects['02_OBLIQUE']
def export(folder,stem):
 folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
 bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(folder/(stem+'.blend')),compress=True)
 bpy.ops.object.select_all(action='DESELECT')
 for o in ARCH.objects:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(folder/(stem+'.glb')),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
 print('SAVED',stem,flush=True)
def render(folder,views):
 for n in views:
  S.camera=bpy.data.objects[n]
  ground=bpy.data.objects.get('Review ground')
  if ground:ground.hide_render=n=='06_UNDERSIDE'
  S.render.filepath=str(Path(folder)/(n+'.png'));bpy.ops.render.render(write_still=True)
  print('RENDERED',n,flush=True)
def build_A():
 # Different broad terrains ascend and move in depth; no bilateral gate.
 world('A_ESTUARY',(-1600,-700,40),1900,2000,680,0,detail=False)
 world('A_ASCENT',(-1650,100,700),1700,1700,820,2,rot=(0,-.18,-.12))
 world('A_MIDDLE_CIVILIZATION',(-900,250,1480),1550,1700,850,1,rot=(.12,-.22,.12))
 world('A_HIGH_CONTINENT',(-250,550,2260),1750,1550,900,2,rot=(.08,-.20,.36))
 world('A_ZENITH',(-50,800,3100),1350,1350,850,0,rot=(0,-.12,.22))
 world('A_EAST_DELTA',(1550,0,180),2100,1900,900,1,rot=(0,.13,-.24))
 world('A_REAR_CONFLUENCE',(900,1400,1050),1700,1800,1000,2,rot=(.08,.22,.30))
 world('A_REAR_SKY',(700,1600,2140),1600,1400,800,0,rot=(.05,.17,.5))
 # broad inhabited diagonal districts link front-left, back-right and zenith.
 ribbon('A_SHARED_CIVIC_FLOOR',[(-2100,-1100,85),(-700,-850,120),(900,-400,180),(2200,400,380)],480,85,D)
 ribbon('A_SHARED_REFLECTION',[(-1700,-1000,92),(-600,-750,127),(700,-350,187),(1900,320,385)],110,4,W)
 tube('A_GROUND_TO_HIGH_TRANSIT',[(-1900,-950,120),(-1100,-400,1000),(-500,100,1800),(120,780,3200),(100,900,3800)],22,B)
 tube('A_EAST_TO_REAR_TRANSIT',[(2300,0,350),(1600,800,950),(1000,1600,1800),(700,1750,2700)],20,B)
def build_B():
 # Worlds are orthogonal / partly inverted, organised round a deep diagonal volume.
 world('B_LOW_ORIGIN',(-500,-900,50),2500,2100,720,1)
 world('B_OBLIQUE_WEST',(-1800,200,1000),2100,1800,1000,2,rot=(.15,-.65,.35))
 world('B_HIGH_INVERTED',(-150,600,3450),2900,2000,1000,0,rot=(math.pi-.18,0,.25))
 world('B_EAST_REVERSED',(1650,450,2700),2200,1900,900,1,rot=(math.pi,.55,-.5))
 world('B_REAR_VERTICAL',(200,1800,1600),1800,1900,1200,2,rot=(.68,0,.6))
 world('B_FORWARD_TRANSFER',(1000,-600,1100),1600,1400,700,0,rot=(0,.17,-.55))
 tube('B_ASYMMETRIC_TRANSFER',[(-2400,-300,500),(-1800,800,1600),(-900,1300,2700),(200,900,3500)],35,B)
