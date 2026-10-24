"""J7-R6 - TENKAKU CIVIC STRATA: Blender research model with an OPEN inhabited city section.
Noncanonical metres, nonfinal art. Distinct from J7-R5 two towers/bridge:
one interlinked asymmetrical terraced urban geology with nested civic chambers.
Blender-native editable bodies, deliberate sculpted silhouettes, 9 rendered observations.
"""
import bpy, math, json, sys, collections
from mathutils import Vector
from pathlib import Path
from math import sin,cos,pi
OUT=Path(sys.argv[sys.argv.index("--")+1]).resolve()
if OUT.exists() and list(OUT.iterdir()):raise RuntimeError("Output path must be new/empty")
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
SC=bpy.context.scene
SC.unit_settings.system="METRIC"
PALETTE={
  "ivory":(.85,.88,.82,.98),"warm_white":(.98,.93,.81,1),
  "cliff":(.41,.56,.62,1),"deep":(.09,.21,.27,1),
  "roof":(.67,.77,.75,1),"copper":(.87,.56,.29,1),
  "aqua":(.17,.59,.67,1),"gardens":(.21,.43,.34,1),
  "shaded_city":(.45,.51,.49,1),"void_floor":(.79,.77,.69,1),
  "basis":(.15,.20,.24,1),"sea":(.05,.29,.39,1)}
M={}
for name,rgb in PALETTE.items():
 m=bpy.data.materials.new(name);m.diffuse_color=rgb;m.use_nodes=True
 p=m.node_tree.nodes.get("Principled BSDF")
 if p:
  p.inputs["Base Color"].default_value=rgb
  p.inputs["Metallic"].default_value=.15 if name not in ("copper","aqua") else .55
 M[name]=m
ROLES=collections.Counter()
def geo(name,vertices,faces,role,material):
 if len(vertices)<3 or not faces:raise RuntimeError(name+" empty geometry")
 me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],faces);me.update()
 o=bpy.data.objects.new(name,me);SC.collection.objects.link(o)
 me.materials.append(M[material]);o["role"]=role;o["R6_research_only"]=True
 ROLES[role]+=1
 return o
def mass(name,xyrings,levels,role,material):
 """True 3D irregular cliff block from keyed cutaway/canyon terraces, not cylinder."""
 if len(xyrings)!=len(levels):raise RuntimeError("rings mismatch")
 n=len(xyrings[0])
 if any(len(s)!=n for s in xyrings):raise RuntimeError("ring n mismatch")
 verts=[]
 for z,ring in zip(levels,xyrings):
  verts.extend([(x,y,z) for x,y in ring])
 fs=[tuple(range(n-1,-1,-1)),tuple((len(levels)-1)*n+i for i in range(n))]
 for i in range(len(levels)-1):
  for k in range(n):
   a=i*n+k;b=i*n+(k+1)%n;c=(i+1)*n+(k+1)%n;d=(i+1)*n+k
   fs.append((a,b,c,d))
 return geo(name,verts,fs,role,material)
def shape(points,cx,cy,sx,sy,skew=0):
 return [(cx+x*sx+skew*y*sy,cy+y*sy) for x,y in points]
def prism(name,p,z0,z1,role,mat,skew=(0,0),taper=1):
 N=len(p);cx=sum(q[0] for q in p)/N;cy=sum(q[1] for q in p)/N
 a=[(x,y,z0) for x,y in p]
 b=[(cx+(x-cx)*taper+skew[0],cy+(y-cy)*taper+skew[1],z1) for x,y in p]
 f=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]
 for i in range(N):j=(i+1)%N;f.append((i,j,N+j,N+i))
 return geo(name,a+b,f,role,mat)
def beam(name,a,b,w,d,role,mat):
 p=Vector(a);q=Vector(b);v=q-p
 n=Vector((-v.y,v.x,0))
 if n.length<.00001:n=Vector((1,0,0))
 n.normalize();wx=n*w*.5;dz=Vector((0,0,d*.5))
 verts=[]
 for c in (p,q):
  verts.extend([tuple(c-wx-dz),tuple(c+wx-dz),tuple(c+wx+dz),tuple(c-wx+dz)])
 f=[(3,2,1,0),(4,5,6,7)]
 for i in range(4):j=(i+1)%4;f.append((i,j,j+4,i+4))
 return geo(name,verts,f,role,mat)
def ring(name,cx,cy,rx,ry,inner,z0,z1,role,mat,N=16,phase=.2):
 # A true vertical OPEN SKY VOID. No opaque material covering central aperture.
 verts=[]
 for z in (z0,z1):
  for rad in (1.0,inner):
   for i in range(N):
    theta=2*pi*i/N+phase
    r=rad*(1+.06*sin(5*theta))
    verts.append((cx+rx*r*cos(theta),cy+ry*r*sin(theta),z))
 faces=[]
 for i in range(N):
  j=(i+1)%N
  faces.extend([(i,j,2*N+j,2*N+i),(N+i,3*N+i,3*N+j,N+j),
                (2*N+i,2*N+j,3*N+j,3*N+i),(i,N+i,N+j,j)])
 return geo(name,verts,faces,role,mat)
def arched_arcade(name,span_x,zbase,height,y,segments,w,d,mat):
 for k in range(segments):
  xa=span_x[0]+(span_x[1]-span_x[0])*k/segments
  xb=span_x[0]+(span_x[1]-span_x[0])*(k+1)/segments
  xx=(xa+xb)*.5
  beam(name+"_PIER_"+str(k),(xa,y,zbase),(xa,y,zbase+height*.72),w,w*1.3,"public_arcade_pier",mat)
  pts=[]
  for j in range(9):
   t=j/8;xx2=xa+(xb-xa)*t
   zz=zbase+height*.72+height*.28*(1-(2*t-1)**2)
   pts.append((xx2,y,zz))
  for j in range(8):
   beam(name+"_ARCH_"+str(k)+"_"+str(j),pts[j],pts[j+1],w*.75,d,"public_arcade_intrados_visible",mat)
# BASE shared continuous thick inhabited continental plate. Neither shore is an isolated turret.
BASE=[(-1.0,-.60),(-.90,-.94),(-.48,-1.02),(-.20,-.88),(.17,-.99),(.63,-.81),
      (1.0,-.52),(.96,.26),(.80,.65),(.50,.94),(.05,.75),(-.39,.87),(-.88,.55),(-1.0,-.16)]
B0=shape(BASE,0,0,3430,1900,.12)
B1=shape(BASE,60,80,3350,1810,.1)
B2=shape(BASE,150,90,3170,1720,.075)
mass("01_SINGLE_INHABITED_CONTINENT_FOUNDATION",[B0,B1,B2],[-95,310,670],
 "single_citywide_connected_foundation_mass","deep")
# Major true sectional cavity: foundation has a south-facing opening at the upper-level
# civic layer, because raised banks are separate polygon cores, not one opaque bridge.
WEST=[(-1,-.77),(-.90,-.99),(-.53,-.92),(-.27,-.65),(-.10,-.26),
      (-.12,.16),(-.55,.55),(-.88,.94),(-1.02,.47)]
EAST=[(.08,-.38),(.19,-.76),(.44,-.98),(.92,-.80),(1.00,-.17),
      (.83,.55),(.58,.95),(.26,.76),(.13,.27)]
# West city is longer but lower, multiple inhabitable terraces; east city is steeper
# with long roof-level living streets instead of a freestanding tall cylinder.
WEST_RINGS=[
 shape(WEST,-850,90,2690,1770,.015),
 shape(WEST,-870,130,2580,1770,.04),
 shape(WEST,-1050,155,2330,1550,.08),
 shape(WEST,-1320,175,2040,1280,.09),
 shape(WEST,-1660,230,1480,1040,.14)]
EAST_RINGS=[
 shape(EAST,420,35,3020,1810,.01),
 shape(EAST,480,40,2900,1700,-.04),
 shape(EAST,580,30,2680,1540,-.08),
 shape(EAST,690,120,2230,1250,-.13),
 shape(EAST,880,190,1770,1050,-.15),
 shape(EAST,1070,330,1180,760,-.16)]
mass("02_WEST_INHABITED_ESCARPMENT",WEST_RINGS,[650,920,1380,1900,2440],
 "west_extensive_inhabited_city_face","ivory")
mass("03_EAST_ASCENDING_INHABITED_ESCARPMENT",EAST_RINGS,[655,980,1510,2220,2870,3490],
 "east_high_inhabited_city_face","cliff")
# Actual terraces carved visually by layered, broad, irregular grounds with open street texture.
TERRACE=[(-1,-.61),(-.67,-.93),(-.1,-1.0),(.44,-.84),(1,-.38),(.90,.63),(.45,.91),(-.30,.85),(-.90,.35)]
for side,stages in [
 ("W",[(-1200,-100,930,1120,780),(-1390,170,1410,980,680),(-1550,300,1900,730,495),(-1680,410,2420,470,270)]),
 ("E",[(1070,-160,1040,1100,750),(1350,50,1580,975,670),(1650,120,2250,840,580),(1820,260,2870,570,340)])]:
 for idx,(cx,cy,z,rx,ry) in enumerate(stages):
  outline=shape(TERRACE,cx,cy,rx,ry,.05 if side=="W" else -.09)
  prism(side+"_OCCUPIABLE_STREET_SHELF_"+str(idx),outline,z,z+60,
   "city_inhabited_thick_neighbourhood_street","warm_white",taper=.98)
  # Real road and plazas clearly separate from foundation mass, but there is one shared base.
  a=(-rx*.44);b=(rx*.45)
  beam(side+"_MEGACITY_AVENUE_"+str(idx),(cx+a,cy-.10*ry,z+71),
    (cx+b,cy+.17*ry,z+78),68,14,"actual_3d_neighbourhood_avenue_preliminary","aqua")
  for j in range(5):
   u=-.66+j*.34
   bx=cx+u*rx*.65
   by=cy+.40*ry*cos((j+1)*1.3)
   p=[(bx-77,by-50),(bx+68,by-45),(bx+79,by+55),(bx-66,by+54)]
   hh=140+40*((j+idx*2)%3)
   prism(side+"_CIVIC_HABITAT_"+str(idx)+"_"+str(j),p,z+60,z+hh,
    "inhabited_research_building_exterior_not_final","roof",skew=(hh*.12*(1 if idx%2 else -1),0),taper=.78)
  ring(side+"_SKY_GARDEN_"+str(idx),cx+rx*.09,cy+ry*.23,rx*.23,ry*.28,.43,
       z+61,z+100,"true_urban_courtyard_and_green_public_room","gardens",N=12)
# Deep front-facing CIVIC SECTION HALL: the continental foundation below it is solid,
# but the tall volume between broad urban rims is open air, not filled by a giant stone box.
# 1.8km wide floor; the central tectonic void is deliberately NOT capped by a slab.
HALL=[(-910,-1040),(-680,-1290),(-210,-1420),(410,-1390),(870,-1000),
      (830,370),(480,490),(-520,450),(-870,120)]
prism("04_GRAND_CIVIC_FORUM_ACTUAL_PUBLIC_FLOOR",HALL,680,733,
 "public_assembly_room_floor_under_open_skylight","void_floor")
# Tall retaining inhabited gallery wings with actual open civic entrances from SOUTH
prism("04_FORUM_WEST_GALLERY_OCCUPIABLE",
 [(-1010,-1250),(-785,-1200),(-780,510),(-1020,600)],710,1250,
 "west_civic_gallery_with_floor_and_volume","warm_white",skew=(-80,0),taper=.90)
prism("04_FORUM_EAST_GALLERY_OCCUPIABLE",
 [(770,-1140),(1085,-1180),(1100,650),(820,570)],710,1460,
 "east_civic_gallery_with_floor_and_volume","ivory",skew=(60,40),taper=.90)
# Opening at the center has a true roof aperture (no faked dark texture)
ring("04_HIGH_CIVIC_OCULUS",0,-290,1080,820,.62,1490,1585,
 "real_open_civic_roof_aperture","warm_white",N=18,phase=.07)
# Architectural counterpoint to cliff masses: five slanted vertical monumental civic piers
for i,x in enumerate([-930,-475,0,485,940]):
 beam("04_PORTICO_RIB_"+str(i),(x,290,740),(x*.72,345,1490),78,88,
  "exposed_structural_civic_rib","deep")
arched_arcade("04_FORUM_PUBLIC_ARCHES",(-920,950),745,450,380,6,37,57,"warm_white")
# Audience terrace seating actual 3D geometries (not texture)
for row in range(6):
 y=-1070+row*125
 beam("04_CIVIC_ASSEMBLY_STEP_"+str(row),(-590,y,735+row*20),(550,y,740+row*20),
      95,22,"actual_amphitheater_public_floor","roof")
prism("04_CIVIC_CEREMONY_STAGE",[(-320,-1160),(350,-1160),(420,-950),(-370,-940)],765,816,
 "actual_ceremonial_platform","warm_white")
# 2 huge public pedestrian embankments CONNECT to the inhabited banks
for name,a,b,w in [
 ("WEST_FORUM_GATE",(-1230,-730,850),(-800,-620,840),220),
 ("EAST_FORUM_GATE",(1450,-620,890),(820,-580,890),230),
 ("WEST_FORUM_UPPER_ACCESS",(-1700,300,1400),(-780,390,1320),150),
 ("EAST_FORUM_UPPER_ACCESS",(1750,330,1630),(900,400,1550),170)]:
 beam(name,a,b,w,64,"spatial_urban_access_plate_grade_unverified","warm_white")
# Open public transit exchange halls on section levels, each with usable floor planes
for side,cx,cy,zs in [
 ("W",-1420,-520,[850,1410,1900]),
 ("E",1410,-610,[960,1610,2300,2840])]:
 for j,z in enumerate(zs):
  prism(side+"_SKY_STATION_PUBLIC_FLOOR_"+str(j),
   [(cx-250,cy-110),(cx+250,cy-100),(cx+270,cy+190),(cx-220,cy+200)],
   z,z+34,"actual_city_station_floor_no_traversal_pass","warm_white")
 for offset in [-130,130]:
  beam(side+"_LIFT_SHAFT_"+str(offset),(cx+offset,cy,zs[0]),(cx+offset,cy,zs[-1]),
       26,32,"actual_transit_guide_not_walk_certified","deep")
# Huge elevated urban rim promenade, intentionally integrated with bank mass, not thin bridge
for z,yrange in [(1130,200),(1590,360)]:
 beam("THE_CITY_INNER_PUBLIC_RIM_"+str(z),(-1180,yrange,z),(1330,yrange+170,z+85),
    165,88,"central_urban_exchange_transit_not_access_pass","roof")
# Diagonal pier clusters create a deep facade rather than simple smooth opaque shells
for side,rx,ys,z in [("W",-2160,-1150,980),("E",2100,-1150,1260)]:
 for n in range(4):
  x=rx+n*(240 if side=="W" else -240)
  yy=ys+130*(n%2)
  beam(side+"_CIVIC_FACE_MEGA_RIB_"+str(n),(x,yy,z),(x+(140 if side=="E" else -90),yy+260,z+740),
     60,110,"human_city_scale_facade_support_not_certified","deep")
# Graphic W0 ten km research context, not original terrain or canonical coordinates
prism("NONCANONICAL_GROUND_FRAME",
 [(-5000,-5000),(5000,-5000),(5000,5000),(-5000,5000)],-260,-246,
 "noncanonical_10km_sizing_context_only","basis")
SC.render.engine="BLENDER_WORKBENCH"
SC.render.resolution_x=1350;SC.render.resolution_y=900;SC.render.resolution_percentage=100
SC.render.image_settings.file_format="PNG"
SC.display.shading.light="STUDIO";SC.display.shading.color_type="MATERIAL"
SC.display.shading.show_shadows=True;SC.display.shading.show_cavity=True
SC.display.shading.cavity_type="BOTH";SC.view_settings.view_transform="Standard"
def render(id,eye,target,orth,scale_kind):
 camd=bpy.data.cameras.new(id);cam=bpy.data.objects.new(id,camd)
 SC.collection.objects.link(cam);cam.location=Vector(eye)
 cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
 camd.type="ORTHO";camd.ortho_scale=orth;camd.clip_end=85000
 SC.camera=cam;out=OUT/(id+".png");SC.render.filepath=str(out)
 bpy.ops.render.render(write_still=True)
 if not out.exists() or out.stat().st_size<9000:raise RuntimeError(id+" render missing")
 return {"view":id,"classification":scale_kind,"ortho_scale_m":orth,"bytes":out.stat().st_size}
look=(0,0,1460)
VIEWS=[
 ("01_FRONT",(0,-11000,4600),look,10500,"FIXED_CITY_10KM"),
 ("02_OBLIQUE",(7800,-8500,6200),look,10500,"FIXED_CITY_10KM"),
 ("03_SIDE",(11200,0,5200),look,10500,"FIXED_CITY_10KM"),
 ("04_REAR",(0,11000,4500),look,10500,"FIXED_CITY_10KM"),
 ("05_AERIAL",(6900,-7300,13900),look,10500,"FIXED_CITY_10KM"),
 ("06_GROUND",(0,-10200,300),(0,0,1200),10500,"FIXED_CITY_10KM"),
 ("07_REVERSE_DIAGONAL",(-8100,8100,6800),look,10500,"FIXED_CITY_10KM"),
 ("08_CIVIC_ROOM",(1250,-2600,1470),(0,-280,1250),3250,"LOCAL_UNCOMPARABLE"),
 ("09_URBAN_SECTION",(4800,-5000,3900),(90,170,1670),6900,"LOCAL_UNCOMPARABLE")]
images=[render(*args) for args in VIEWS]
# Every file originates in the same Blender scene: editable native master and export.
BLEND=OUT/"J7R6_TENKAKU_SECTION_NONCANONICAL.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(BLEND),compress=True)
GLB=OUT/"J7R6_TENKAKU_SECTION_NONCANONICAL.glb"
bpy.ops.export_scene.gltf(filepath=str(GLB),export_format="GLB")
objects=[o for o in bpy.data.objects if o.type=="MESH"]
vertices=sum(len(o.data.vertices) for o in objects)
triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects)
# measure excluding only the explicit 10km context mesh
co=[o for o in objects if o.name!="NONCANONICAL_GROUND_FRAME"]
loc=[o.matrix_world@v.co for o in co for v in o.data.vertices]
bounds=[[round(min(p[i] for p in loc),2) for i in range(3)],
        [round(max(p[i] for p in loc),2) for i in range(3)]]
metrics={"schema":"halo9.j7r6.real_blender_geometry.v1","blender":bpy.app.version_string,
 "research_status":"NEEDS_HUMAN_ART_REVIEW","coordinate":"NONCANONICAL_Z_UP_M",
 "actual_mesh_objects":len(objects),"vertices":vertices,"triangles":triangles,
 "actual_section_bounds_m":bounds,"span_m":[round(bounds[1][i]-bounds[0][i],2) for i in range(3)],
 "role_distribution":dict(ROLES),"renders":images,
 "GLB_bytes":GLB.stat().st_size,"BLEND_bytes":BLEND.stat().st_size,
 "transport_walkability":"NOT_TESTED","public_interior_completeness":"NOT_CERTIFIED",
 "construction":"HOLD","canonical_art_adoption":"NONE","all_city_master_detail":"NOT_COMPLETED"}
# verify reimport
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(GLB))
metrics["imported_glb_mesh_objects"]=len([o for o in bpy.data.objects if o.type=="MESH"])
if metrics["imported_glb_mesh_objects"]!=len(objects):raise RuntimeError("GLB reimport missing geometry")
(OUT/"J7R6_MODEL_EVIDENCE.json").write_text(json.dumps(metrics,indent=2),encoding="utf8")
print("J7_R6_BLENDER_REAL_MODEL_PASS",json.dumps({k:metrics[k] for k in ("actual_mesh_objects","vertices","triangles","span_m","imported_glb_mesh_objects")}))
