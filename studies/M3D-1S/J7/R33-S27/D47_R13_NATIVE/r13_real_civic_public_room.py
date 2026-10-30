"""HALO-9 R13: inhabited space FIRST. One authored 520m public city-room.

ART is *UNREVIEWED* until actual exported views are inspected. This is an
architectural SPATIAL SCALE experiment, NOT another megacity generator,
not central M247-C, not a full city district or city.
Own vertices, no Claude/R12 geometry borrowed. Inspired by general
'circulation + habitable boundaries' concept, not copies of example designs.
"""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
P=Path(sys.argv[-1]).resolve();P.mkdir(exist_ok=True,parents=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
M={}
for key,color in {
"01_STONE":(.64,.67,.64),"02_DARK":(.25,.34,.37),
"03_HABITAT":(.69,.66,.53),"04_COPPER":(.58,.42,.30),
"05_TRANSIT":(.28,.53,.56),"06_GARDEN":(.39,.54,.40),
"07_FLOOR":(.47,.50,.47),"08_LIGHT":(.81,.78,.63)}.items():
 m=bpy.data.materials.new(key);m.diffuse_color=(*color,1);M[key]=m
def group(n):
 c=bpy.data.collections.get(n)
 if not c:
  c=bpy.data.collections.new(n);scene.collection.children.link(c)
 return c
def mesh(name,verts,faces,ma,grp,role):
 assert len(name)<58,name
 me=bpy.data.meshes.new(name+"_native");me.from_pydata(verts,[],faces);me.update()
 obj=bpy.data.objects.new(name,me);group(grp).objects.link(obj)
 me.materials.append(M[ma]);obj["role"]=role;obj["architectural_master"]=False
 return obj
def slab(n,pts,lower,upper,ma,grp,role):
 assert upper>lower and len(pts)>=3
 k=len(pts);v=[(x,y,lower) for x,y in pts]+[(x,y,upper) for x,y in pts]
 f=[tuple(range(k-1,-1,-1)),tuple(range(k,2*k))]
 f.extend((i,(i+1)%k,(i+1)%k+k,i+k) for i in range(k))
 return mesh(n,v,f,ma,grp,role)
def beam(n,a,b,w,d,ma,grp,role):
 a=Vector(a);b=Vector(b);direction=(b-a).normalized()
 h=Vector((0,0,1))
 if abs(h.dot(direction))>.94:h=Vector((1,0,0))
 side=direction.cross(h).normalized();up=direction.cross(side).normalized()
 cor=[side*w/2+up*d/2,side*w/2-up*d/2,-side*w/2-up*d/2,-side*w/2+up*d/2]
 v=[tuple(a+x) for x in cor]+[tuple(b+x) for x in cor]
 f=[(0,3,2,1),(4,5,6,7)]
 f += [(i,(i+1)%4,4+(i+1)%4,4+i) for i in range(4)]
 return mesh(n,v,f,ma,grp,role)
def strip(n,st,wide,ma,grp,role):
 assert len(st)==len(wide) and len(st)>2
 v=[]
 for i,(x,y,z) in enumerate(st):
  p=st[max(0,i-1)];q=st[min(len(st)-1,i+1)]
  dx,dy=q[0]-p[0],q[1]-p[1];L=math.hypot(dx,dy)
  assert L>1
  vx,vy=-dy/L,dx/L
  v.extend([(x+vx*wide[i]/2,y+vy*wide[i]/2,z),(x-vx*wide[i]/2,y-vy*wide[i]/2,z)])
 f=[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(st)-1)]
 return mesh(n,v,f,ma,grp,role)
# Architectural art brief: ONE public place, not macro city, not a generator of
# a giant shell to fill. An outdoor academy market square framed by
# differentiated courtyard galleries physically accessible in concept.
FOOTPRINT=[
 (-225,-190),(-92,-229),(100,-211),(208,-147),(236,-4),(188,127),
 (104,214),(-69,225),(-191,139),(-248,10)]
slab("G00_PUBLIC_COURT_GROUND",FOOTPRINT,-5,0,"07_FLOOR","01 PUBLIC LIFE",
     "actual public gathering surface")
# Pond/garden are specific outdoor destinations with real walkable surrounds
slab("G01_EVENT_COURT",[(-90,-96),(45,-125),(108,-52),(96,28),(6,70),(-96,9)],0,2,
     "08_LIGHT","01 PUBLIC LIFE","outdoor public meeting stage")
slab("G02_URBAN_GARDEN",[(-190,55),(-124,80),(-83,172),(-189,137)],0,3,
     "06_GARDEN","01 PUBLIC LIFE","actual ecological public garden plot")
# Enter from south and turn around central courtyard, not fill it with a wall.
strip("G03_APPROACH_FROM_SOUTH",
 [(2,-360,-1),(-9,-282,-1),(-14,-185,0),(-13,-94,1),(-15,-17,1)],
 [29,26,31,27,25],"01_STONE","01 PUBLIC LIFE",
 "continuous lower public open-air promenade")
# One deliberately hand-placed REAL civic plan. There are exactly 3 DIFFERENT
# neighborhoods with separated thresholds and asymmetric levels; no loop of
# repeated identical sides / symmetric concentric building.
DISTRICTS=[
 {"id":"WEST_LIBRARY","side":"W",
  "levels":[(26,[(-240,-181),(-175,-220),(-106,-173),(-121,-79),(-199,-30),(-255,-72)]),
            (70,[(-238,-47),(-193,-90),(-103,-44),(-92,75),(-182,124),(-234,76)]),
            (125,[(-211,87),(-125,42),(-47,101),(-72,195),(-174,225)])],
  "material":"03_HABITAT","program":"real elevated public archive + library terraces"},
 {"id":"EAST_TRANSIT","side":"E",
  "levels":[(42,[(104,-210),(208,-148),(231,-63),(173,-34),(93,-99)]),
            (103,[(111,-112),(239,-24),(203,86),(153,119),(72,44)]),
            (166,[(84,32),(186,75),(170,176),(103,217),(34,149)])],
  "material":"05_TRANSIT","program":"real elevated public station edge + civic walk"},
 {"id":"NORTH_CIVIC","side":"N",
  "levels":[(58,[(-96,119),(-19,72),(79,105),(139,173),(79,240),(-65,253)]),
            (140,[(-145,118),(-56,107),(59,161),(101,245),(-80,266),(-172,206)]),
            (217,[(-181,137),(-68,102),(4,192),(-44,277),(-142,279)])],
  "material":"04_COPPER","program":"real public forum and learning terraces"}
]
def edge_center(p,k):
 a,b=p[k],p[(k+1)%len(p)]
 return ((a[0]+b[0])/2,(a[1]+b[1])/2)
rooms=0
for di,d in enumerate(DISTRICTS):
 levels=d["levels"]
 for li,(z,outline) in enumerate(levels):
  fid=d["id"]+"_%d"%li
  slab(fid+"_PUBLIC_WALK",outline,z-8,z,d["material"],"02 PHYSICAL COURTYARD GALLERIES",
       d["program"]+" walkable surface; safety unproven")
  # Public rooms genuinely contain a floor, tall facade columns, and a
  # broken roof. One edge remains OPEN toward the central outdoor plaza.
  cx=sum(p[0] for p in outline)/len(outline)
  cy=sum(p[1] for p in outline)/len(outline)
  inner=(0-cx,0-cy)
  entry=max(range(len(outline)),
            key=lambda k: ((0-edge_center(outline,k)[0])**2+
                 (0-edge_center(outline,k)[1])**2)*-1)
  for k in range(len(outline)):
   a,b=outline[k],outline[(k+1)%len(outline)]
   if k==entry:
    # Real open facade leaves a broad entrance, with no solid infill
    for x in (a,b):
     beam(fid+"_PORTAL_"+str(k)+"_"+str(int(x[0])),
        (x[0],x[1],z+3),(x[0],x[1],z+64),4,5,
        "02_DARK","03 REAL OPEN FACADES","actual entry pier")
   else:
    # Three architectural bays with real open air between; not fake windows
    seg=3
    for r in range(seg):
     t=(r+.13)/seg
     x=a[0]+(b[0]-a[0])*t
     y=a[1]+(b[1]-a[1])*t
     beam(fid+f"_COL_{k}_{r}",(x,y,z+2),(x,y,z+64+9*(k%3)),
          4,4,"02_DARK","03 REAL OPEN FACADES","open facade support")
  # Room ceiling is a folded inhabited roof above the ACTUAL usable floor.
  # Only part of floor covered: remaining outdoor terrace.
  upper=[(cx+(x-cx)*.67,cy+(y-cy)*.67) for x,y in outline]
  slab(fid+"_REAL_CEILING",upper,z+64,z+70,
       "08_LIGHT","03 REAL OPEN FACADES",
       "real roof of distinguishable public room within each floor")
  # Studio reading counter / benches built INSIDE volume, not floating boxes
  for b in range(2):
   ox=(-22 if b==0 else 22)
   slab(fid+f"_ACTIVE_DESK_{b}",
       [(cx+ox-11,cy-19),(cx+ox+10,cy-21),(cx+ox+17,cy+13),(cx+ox-13,cy+16)],
       z+3,z+6,"03_HABITAT","04 URBAN PUBLIC CULTURE",
       "physical interior library or civic market counter")
  # Exterior garden on select real terraces only
  if li==1:
   tt=[(cx+(x-cx)*.45+30,cy+(y-cy)*.4+17) for x,y in outline]
   slab(fid+"_SKY_GARDEN",tt,z+1,z+4,"06_GARDEN",
        "04 URBAN PUBLIC CULTURE","real elevated public planted area")
  rooms+=1
 # Physical district upward connection between neighboring levels.
 # These are high gradients: DO NOT claim as walkable accessible stairways.
 for i in range(2):
  p1=d["levels"][i][1];p2=d["levels"][i+1][1]
  z1=d["levels"][i][0];z2=d["levels"][i+1][0]
  start=Vector((sum(x for x,y in p1)/len(p1),
                sum(y for x,y in p1)/len(p1),z1+3))
  end=Vector((sum(x for x,y in p2)/len(p2),
              sum(y for x,y in p2)/len(p2),z2+3))
  mid=tuple(start.lerp(end,.53))
  strip(d["id"]+f"_VERTICAL_ACCESS_PROXY_{i}",
        [tuple(start),mid,tuple(end)],[14,13,12],
        "05_TRANSIT","05 VERTICAL CITY CONNECTIONS",
        "physical public connector, too steep/accessibility unverified")
# Across atrium, two great elevated streets cross off-axis rather than
# enclose a roof. Their geometry can be seen from below as inhabited places.
strip("X01_PUBLIC_CROSSING_LOW",
 [(-169,-85,80),(-108,-26,89),(-29,16,99),(50,45,103),(171,65,107)],
 [16,17,18,17,15],"05_TRANSIT","05 VERTICAL CITY CONNECTIONS",
 "true public crossing deck, ends and gradient not fully engineered")
strip("X02_PUBLIC_CROSSING_HIGH",
 [(-173,89,138),(-88,103,150),(0,93,156),(77,129,160),(114,155,170)],
 [15,16,18,16,14],"08_LIGHT","05 VERTICAL CITY CONNECTIONS",
 "higher real public crossing with incomplete lift approach")
# Open air over everything: the skyline comes from room level articulation,
# no central giant shell, no copy of previous R12 giant wall membranes.
VIEWS=[
 ("01_LONG_APPROACH",(0,-800,255),(0,0,150),800),
 ("02_FRONT",(0,-680,180),(0,0,150),660),
 ("03_SIDE",(730,-90,280),(0,0,150),680),
 ("04_REAR",(-10,720,265),(0,0,150),690),
 ("05_AERIAL",(510,-560,850),(0,0,130),820),
 ("06_GROUND_PUBLIC",(0,-110,7),(0,40,145),None),
 ("07_INSIDE_LIBRARY",(-188,-68,83),(-147,8,113),None),
 ("08_SKY_OVERLOOK",(83,143,172),(-95,83,148),None)]
def camera(name,pos,target,scale):
 cam=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,cam)
 group("06 FIXED CITY ROOM G0 CAMERAS").objects.link(ob);ob.location=pos
 ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
 cam.clip_end=20000
 if scale:
  cam.type='ORTHO';cam.ortho_scale=scale
 else:
  cam.type='PERSP';cam.lens=19
for n,p,t,s in VIEWS:camera(n,p,t,s)
scene["R13_ARCHITECTURE"] = "one real public 520m test courtyard, art unreviewed"
scene["R13_ART_ADOPTED"]=False
scene["R13_W0_CITY_MASTER"]=False
scene["R13_M247_C_REPLACEMENT"]=False
scene["R13_MINECRAFT_CONSTRUCTION"]=False
scene["R13_NOT_FINAL_PUBLIC_WALK_CERTIFICATION"]=True
scene["R13_REVIEW_CATEGORY"]="public district 520m one space, not 10km whole"
scene["R13_SOURCE_INDEPENDENT_FROM_R12_GEOMETRY"]=True
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_cavity=True
scene.render.resolution_x=1200;scene.render.resolution_y=760
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
blend=P/"R13_E0_ACTUAL_SINGLE_CIVIC_ROOM.blend"
glb=P/"R13_E0_ACTUAL_SINGLE_CIVIC_ROOM.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",export_cameras=False,
                          export_lights=False)
for name,*_ in VIEWS:
 scene.camera=bpy.data.objects[name]
 scene.render.filepath=str(P/(name+".png"))
 bpy.ops.render.render(write_still=True)
state={
 "scope":"one self-contained 520m shared public city-room, no megacity proposal",
 "actual_public_gallery_rooms":rooms,
 "actual_court_public_floor":True,
 "actual_3D_mesh_count":len([o for o in bpy.data.objects if o.type=='MESH']),
 "actual_camera_count":len(VIEWS),
 "real_images":[v[0]+".png" for v in VIEWS],
 "native_blend":blend.name,"source_glb":glb.name,
 "art":"UNREVIEWED",
 "all_accesses_qualified":False,"canonical_art_adopted":False,
 "10km_city_master_complete":False,"minecraft_write":False}
(P/"R13_E0_MANIFEST.json").write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf8")
print("R13_E0_GENUINE_ONE_CIVIC_ROOM_8_CAMERAS_ART_UNREVIEWED",state)
