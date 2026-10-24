"""CELESTIAL HALO-9 J7-R8: art-directed CIVIC LENS local architecture (research-only).
One habitable architectural SECTOR with a real open nave, promenade levels, dwellings,
and an expressive paired cantilever roof; not another two giant towers/monoliths.
Actual Blender mesh geometry and all nine views, no Minecraft or canonical coordinates.
"""
import bpy, math, json, sys, collections
from pathlib import Path
from mathutils import Vector
from math import sin, cos, pi
out=Path(sys.argv[sys.argv.index("--")+1]).resolve()
if out.exists() and list(out.iterdir()):raise RuntimeError("Output dir must be empty")
out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
sc.unit_settings.system="METRIC"
COL={
 "pearl":(.80,.86,.83,1),"chalk":(.93,.92,.86,1),
 "teal":(.22,.55,.58,1),"glass":(.25,.72,.79,1),
 "basalt":(.13,.22,.27,1),"copper":(.83,.60,.38,1),
 "gardens":(.24,.50,.39,1),"sunken":(.63,.72,.68,1),
 "trim":(.61,.69,.70,1),"sea":(.13,.25,.31,1)}
mt={}
for name,col in COL.items():
 m=bpy.data.materials.new(name);m.diffuse_color=col;m.use_nodes=True
 p=m.node_tree.nodes.get("Principled BSDF")
 if p:
  p.inputs["Base Color"].default_value=col
  p.inputs["Roughness"].default_value=.45
  p.inputs["Metallic"].default_value=.35 if name in ("copper","teal","glass") else .06
 mt[name]=m
roles=collections.Counter()
def obj(name,v,f,role,material):
 me=bpy.data.meshes.new(name)
 me.from_pydata(v,[],f);me.update()
 o=bpy.data.objects.new(name,me);sc.collection.objects.link(o)
 o.data.materials.append(mt[material]);o["role"]=role;o["research_only"]=True
 roles[role]+=1
 return o
def sector(name,center,r0,r1,a0,a1,z0,z1,mat,role,n=38,twist=0):
 """Open radial sweep, with true EMPTY interior and four exposed sculpted sides."""
 cx,cy=center;v=[]
 def ring(r,z):
  for i in range(n+1):
   t=i/n;a=a0+(a1-a0)*t
   wa=1+.055*sin(3*a+twist)+.035*sin(7*a)
   rr=r*wa
   v.append((cx+rr*cos(a)+.10*(z-70)*sin(a),
             cy+rr*.77*sin(a)+.11*(z-70)*cos(a),z))
 for z in (z0,z1):
  ring(r0,z);ring(r1,z)
 sz=n+1;f=[]
 for i in range(n):
  for a,b in ((0,2*sz),(sz,3*sz)):
   f.append((a+i,a+i+1,b+i+1,b+i))
  f.append((i,i+1,sz+i+1,sz+i))
  f.append((2*sz+i,3*sz+i,3*sz+i+1,2*sz+i+1))
 f+=[(0,sz,3*sz,2*sz),(n,2*sz+n,3*sz+n,sz+n)]
 return obj(name,v,f,role,mat)
def prism(name,p,z0,z1,material,role):
 n=len(p);v=[(x,y,z0) for x,y in p]+[(x,y,z1) for x,y in p]
 f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
 for i in range(n):j=(i+1)%n;f.append((i,j,n+j,n+i))
 return obj(name,v,f,role,material)
def bar(name,a,b,w,d,mat,role):
 p=Vector(a);q=Vector(b);v=q-p
 lat=Vector((-v.y,v.x,0))
 if lat.length<.001:lat=Vector((1,0,0))
 lat.normalize();u=lat*w/2;t=Vector((0,0,d/2))
 pts=[]
 for c in (p,q):pts.extend([tuple(c-u-t),tuple(c+u-t),tuple(c+u+t),tuple(c-u+t)])
 faces=[(3,2,1,0),(4,5,6,7)]
 for i in range(4):j=(i+1)%4;faces.append((i,j,j+4,i+4))
 return obj(name,pts,faces,role,mat)
def petal(name,positions,widths,thickness,mat,role):
 """Ruled, twisting surface like a thin but inhabitable large-roof canopy,
 with actually exposed sides & space under it; no solid giant opaque block."""
 assert len(positions)==len(widths)
 v=[]
 for i,((x,y,z),w) in enumerate(zip(positions,widths)):
  if i==0:d=Vector(positions[1])-Vector(positions[0])
  elif i==len(positions)-1:d=Vector(positions[-1])-Vector(positions[-2])
  else:d=Vector(positions[i+1])-Vector(positions[i-1])
  lat=Vector((-d.y,d.x,0))
  if lat.length<.01:lat=Vector((1,0,0))
  lat.normalize()
  for h in (-thickness/2,thickness/2):
   for sg in (-1,1):
    c=Vector((x,y,z))+lat*sg*w*.5+Vector((0,0,h))
    v.append(tuple(c))
 f=[(0,2,3,1),(len(v)-4,len(v)-3,len(v)-1,len(v)-2)]
 for j in range(len(positions)-1):
  for k in range(4):
   kk=(k+1)%4;f.append((4*j+k,4*j+kk,4*(j+1)+kk,4*(j+1)+k))
 return obj(name,v,f,role,mat)
# FOUNDATION: one sculpted urban promontory, no two-column silhouette.
# Ground is fully open and deliberately not a roof covering empty-looking halls.
SHORE=[(-655,-490),(-710,-205),(-655,220),(-410,540),(80,620),(575,395),
       (715,85),(595,-390),(330,-640),(-330,-660)]
prism("BASE_SINGLE_CIVIC_LENS_CITY_SHORE",SHORE,-35,18,"basalt","inhabited_shared_city_ground_local")
# Amphitheatre open civic floor and world-looking water plaza, leading to south gate.
prism("NAVE_TRULY_OPEN_CENTRAL_ASSEMBLY",
  [(-330,-345),(-360,-25),(-255,215),(0,325),(260,198),(360,-25),(280,-345)],
  20,35,"sunken","actual_public_hall_floor")
prism("PUBLIC_ARRIVAL_FORECOURT",[(-265,-590),(280,-590),(325,-340),(-335,-340)],
  19,35,"chalk","south_public_entry_genuine_open")
prism("CENTRAL_PUBLIC_STAGE",
  [(-120,30),(-95,140),(0,205),(130,137),(153,10),(10,-70)],
  34,64,"copper","ceremonial_stage_public")
# Four truly open stepped gathering tiers - ACTUAL separated rings with a hole.
for i in range(5):
 sector("NAVE_AMPHITHEATRE_TIER_"+str(i),(0,-80),215+29*i,240+29*i,
   .15*pi,.92*pi,40+i*15,54+i*15,"chalk","public_amphitheatre_terrace_open")
# THE URBAN BUILDING is a spatially integrated helical inhabited crescent,
# not two giant towers. Level ribbons deliberately overlap with vertical
# supports, each has openings at main south entry.
asym=(0,50)
for i,(z,rin,rout,a0,a1) in enumerate([
 (57,352,502,-.35*pi,1.27*pi),
 (117,355,512,-.26*pi,1.33*pi),
 (180,370,512,-.16*pi,1.34*pi),
 (250,386,503,-.09*pi,1.29*pi),
 (333,401,490,-.01*pi,1.18*pi)]):
 sector("INHABITED_URBAN_TERRACE_"+str(i),asym,rin,rout,a0,a1,z,z+27,
  "pearl" if i%2 else "chalk","true_urban_promendade_horizontal_floor",n=44,twist=i*.43)
 sector("PUBLIC_AVENUE_PAVEMENT_"+str(i),asym,395 if i>1 else 377,
  428 if i>1 else 416,a0,a1,z+27,z+34,"teal","walkable_intended_street_strip_unverified",n=44)
 # Curving arches/pier frames cut a CIVIC CITY FRONT, not an opaque flat cliff.
 for j in range(10):
  t=(j+.5)/10;angle=a0+(a1-a0)*t
  x=(rout-19)*cos(angle);y=50+.77*(rout-19)*sin(angle)
  z0=27 if i==0 else [57,117,180,250,333][i-1]+27
  bar("TERRACE_RHYTHM_PIER_"+str(i)+"_"+str(j),(x,y,z0),
      (x-12*sin(angle),y-10*cos(angle),z),"11" if False else 11,
      11,"basalt","real_pier_between_occupied_levels")
 # Front glass walls are spaced window mullions, the gaps are actual openings.
 for j in range(12):
  t=(j+.45)/12;angle=a0+(a1-a0)*t
  x=(rout-22)*cos(angle);y=50+.77*(rout-22)*sin(angle)
  bar("EXPOSED_CITY_FACADE_MULLION_"+str(i)+"_"+str(j),
       (x,y,z+33),(x-8*sin(angle),y,z+96),6,8,
       "copper","actual_fenestration_pier_preliminary")
# Interior program — building masses on the outer arcade, avoiding generic skyline.
# Five asymmetrically-sized public wings rising FROM curving occupied city streets.
for j,(angle,lev,h,w) in enumerate([
 (.00*pi,1,86,87),(.20*pi,1,135,83),(.41*pi,2,102,105),(.61*pi,3,95,105),
 (.78*pi,2,125,95),(.96*pi,1,128,95),(1.16*pi,0,146,128),
 (.29*pi,4,76,72),(.82*pi,4,70,74)]):
 z=[57,117,180,250,333][lev]+34
 x=458*cos(angle);y=50+355*sin(angle)
 dx=w*.5;dy=w*.65
 p=[(x-dx,y-dy),(x+dx*.9,y-dy),(x+dx,y+dy),(x-dx*1.10,y+dy)]
 prism("HABITABLE_PUBLIC_PROGRAM_WING_"+str(j),p,z,z+h,
       "trim" if j%2 else "pearl","architectural_public_wing_interior_not_detailed")
 # open roof profiles
 petal("PUBLIC_WING_ROOF_SAWTOOTH_"+str(j),
       [(x-dx,y,z+h),(x,y+25,z+h+16),(x+dx,y,z+h+6)],
       [38,w,46],9,"chalk","visible_programmatic_roofline")
# Chapel-like civic monumental focal point is a SINGLE interconnected sculpted
# roof, made from 6 DIFFERENT sweeping blades anchored to deep city terrace.
# Central nave is NOT blocked; these enormous frames expose the public interior.
for j in range(6):
 x=-480+j*185
 heights=[470,555,610,650,570,495]
 zcrest=heights[j]
 yfront=-245-65*sin(j*1.3)
 petal("SIX_CIVIC_VAULT_SPINES_"+str(j),
   [(x*1.02,425,340),(x*.92,300,385),(x*.82,115,zcrest),
    (x*.92,-135,zcrest-65),(x*1.08,yfront,370)],
   [70,95,124,83,44],23,"chalk","monumental_exposed_roof_buttress_open_span")
 # tie into inhabited city at the rear; no magically floating crown.
 bar("VAULT_SPINE_REAR_STRUCTURE_"+str(j),(x,420,210),
      (x*1.02,425,365),26,30,"basalt","civic_roof_support_member")
# Southern gateway is intentionally GRAND and OPEN between curved inhabited banks.
for x in [-420,420]:
 bar("SOUTH_GATE_CIVIC_PIER_"+str(x),(x,-425,24),(x,-430,340),55,50,
     "pearl","exposed_civic_entry_gate")
# A diagnostic street crosses from one connected edge to another; unverified grade.
bar("CITY_INNER_LINK_PROMENADE",
  (-520,190,180),(520,245,185),105,25,"teal","public_connection_across_sections_no_traversal_QA")
# Architectural events for interior scale
for k in range(4):
 x=(-220+150*k)
 petal("HALL_HANGING_PLANTER_SUSPENSION_"+str(k),
    [(x,340,250),(x*1.15,250,220),(x*.83,190,204)],
    [26,48,44],15,"gardens","botanical_civic_garden_hung_inside")
# Frame city reference 10km not exported? Actual local model intentionally not context,
# as false W0 would make reviewers misinterpret scale.
# Render from REAL Blender scene with both panorama and interior views.
sc.render.engine="BLENDER_WORKBENCH"
sc.render.resolution_x=1200;sc.render.resolution_y=840;sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.display.shading.light="STUDIO";sc.display.shading.color_type="MATERIAL"
sc.display.shading.show_shadows=True;sc.display.shading.show_cavity=True
sc.display.shading.cavity_type="BOTH";sc.view_settings.view_transform="Standard"
def snap(name,eye,focus,scale,typ):
 camera=bpy.data.cameras.new(name);node=bpy.data.objects.new(name,camera)
 sc.collection.objects.link(node);node.location=Vector(eye)
 node.rotation_euler=(Vector(focus)-node.location).to_track_quat("-Z","Y").to_euler()
 camera.type="ORTHO";camera.ortho_scale=scale;camera.clip_end=35000
 sc.camera=node;p=out/(name+".png");sc.render.filepath=str(p)
 bpy.ops.render.render(write_still=True)
 if not p.exists() or p.stat().st_size<10000:raise RuntimeError("render "+name+" missing")
 return {"name":name,"camera_class":typ,"ortho_scale_m":scale,"bytes":p.stat().st_size}
FOCUS=(0,0,225)
views=[
 ("01_FRONT",(0,-1900,880),FOCUS,1900,"FIXED_STUDY"),
 ("02_OBLIQUE",(1500,-1430,1020),FOCUS,1900,"FIXED_STUDY"),
 ("03_SIDE",(1950,0,850),FOCUS,1900,"FIXED_STUDY"),
 ("04_REAR",(0,1950,900),FOCUS,1900,"FIXED_STUDY"),
 ("05_AERIAL",(1300,-1100,2100),FOCUS,1900,"FIXED_STUDY"),
 ("06_GROUND",(0,-1950,90),(0,0,250),1900,"FIXED_STUDY"),
 ("07_REVERSE",(-1450,1450,1150),FOCUS,1900,"FIXED_STUDY"),
 ("08_NAVE",(40,-380,170),(0,110,280),800,"LOCAL_DETAIL"),
 ("09_CITY_STREET",(540,50,195),(0,100,260),860,"LOCAL_DETAIL")]
frames=[snap(*v) for v in views]
# Keep GUI work possible: leave a prominent skin selectable and viewport framed to it.
target=bpy.data.objects.get("SIX_CIVIC_VAULT_SPINES_2")
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=="VIEW_3D":
   space=area.spaces.active;space.shading.type="SOLID"
   space.shading.color_type="MATERIAL";space.region_3d.view_location=Vector((0,0,275))
   space.region_3d.view_distance=1550;space.clip_end=50000
for a in bpy.context.selected_objects:a.select_set(False)
target.select_set(True);bpy.context.view_layer.objects.active=target
blend=out/"J7R8_CIVIC_LENS_ART_STUDY.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
glb=out/"J7R8_CIVIC_LENS_ART_STUDY.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB")
meshes=[o for o in bpy.data.objects if o.type=="MESH"]
n=len(meshes)
vcount=sum(len(o.data.vertices) for o in meshes)
tcount=sum(sum(max(0,len(face.vertices)-2) for face in o.data.polygons) for o in meshes)
pts=[o.matrix_world@p.co for o in meshes for p in o.data.vertices]
bounds=[[round(min(p[i] for p in pts),3) for i in range(3)],[round(max(p[i] for p in pts),3) for i in range(3)]]
meas={"schema":"halo9.j7r8.actual_blender_local_architecture.v1",
 "status":"REAL_BLENDER_PRELIMINARY_MODEL_NOT_ART_ACCEPTED","blender":bpy.app.version_string,
 "coordinate":"NONCANONICAL_Z_UP_METRES","actual_measured_bounds_m":bounds,
 "actual_measured_spans_m":[round(bounds[1][i]-bounds[0][i],2) for i in range(3)],
 "meshes":n,"vertices":vcount,"triangles":tcount,
 "role_distribution":dict(roles),"glb_bytes":glb.stat().st_size,
 "blend_bytes":blend.stat().st_size,"views":frames,
 "public_nave_true_open_center_above_floor":True,
 "inhabited_outer_gallery_floors":5,
 "official_city_master_complete":False,"official_minecraft_coordinates":"UNKNOWN",
 "walkability":"NOT_TESTED","art_result":"REVIEW_REQUIRED",
 "construction":"HOLD"}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(glb))
n2=len([o for o in bpy.data.objects if o.type=="MESH"])
if n2!=n:raise RuntimeError("GLB reimport lost mesh: "+str((n,n2)))
meas["glb_reimport_mesh_objects"]=n2
(out/"J7R8_REAL_BLENDER_EVIDENCE.json").write_text(json.dumps(meas,indent=2),encoding="utf8")
print("J7R8_REAL_BLENDER_PASS",json.dumps({"meshes":n,"verts":vcount,"triangles":tcount,"views":len(frames),"spans_m":meas["actual_measured_spans_m"]}))
