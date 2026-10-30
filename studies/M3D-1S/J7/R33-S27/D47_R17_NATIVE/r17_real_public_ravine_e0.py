"""R17 / CIVIC RAVINE ONE — genuine 330 m public-section architectural trial.

NOT a whole city, NOT canonical M247-C. ART G0 only.
Build public-space topology FIRST; an authored asymmetric broken vault grows
around EXISTING real public paths, not the other way around.
All measurements in meters, Z-up. Structural/load/egress certification: absent.
"""
import bpy,math,sys,json,hashlib
from pathlib import Path
from mathutils import Vector

OUT=Path(sys.argv[-1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
materials={}
for name,rgba in [
 ("CIVIC_PALE_STONE",(0.72,.72,.65,1)),
 ("PUBLIC_HONEY_STONE",(.74,.60,.39,1)),
 ("SHADOW_MINERAL",(.26,.32,.37,1)),
 ("INNER_WARM_WOOD",(.58,.37,.24,1)),
 ("AIR_SKY_MINT",(.32,.55,.54,1)),
 ("LIVING_GREEN",(.31,.50,.37,1)),
 ("DEEP_CITY_CUT",(.15,.20,.23,1))]:
 m=bpy.data.materials.new(name);m.diffuse_color=rgba;materials[name]=m
def collection(name):
 c=bpy.data.collections.get(name)
 if c is None:c=bpy.data.collections.new(name);scene.collection.children.link(c)
 return c
def geom(name,vert,face,mat,grp,role,editable=True):
 me=bpy.data.meshes.new(name+"_MESH")
 me.from_pydata(vert,[],face);me.update()
 ob=bpy.data.objects.new(name,me)
 collection(grp).objects.link(ob)
 me.materials.append(materials[mat])
 ob["R17_role"]=role
 ob["R17_design_status"]="G0_ART_UNREVIEWED"
 if editable:
  ob.shape_key_add(name="Basis")
  ob.shape_key_add(name="R17_GUI_AUTHOR_EDIT")
 return ob
def prism(n,polygon,zmin,zmax,mat,grp,role):
 assert zmax>zmin and len(polygon)>=3
 N=len(polygon)
 v=[(x,y,zmin) for x,y in polygon]+[(x,y,zmax) for x,y in polygon]
 f=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]
 f.extend((i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N))
 return geom(n,v,f,mat,grp,role)
def rect(n,x0,x1,y0,y1,z0,z1,mat,grp,role):
 return prism(n,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1,mat,grp,role)
def walk(n,pts,widths,thick,mat,role,kind):
 """Actual topological walking strip and 3D side depth, with endpoint metadata."""
 assert len(pts)>=2 and len(widths)==len(pts)
 v=[]
 for i,(x,y,z) in enumerate(pts):
  b=Vector(pts[min(i+1,len(pts)-1)])
  a=Vector(pts[max(i-1,0)])
  d=b-a
  norm=math.hypot(d.x,d.y)
  assert norm>0
  nx=-d.y/norm;ny=d.x/norm
  w=widths[i]/2
  v.extend([(x-nx*w,y-ny*w,z),(x+nx*w,y+ny*w,z),
            (x-nx*w,y-ny*w,z-thick),(x+nx*w,y+ny*w,z-thick)])
 f=[]
 for i in range(len(pts)-1):
  b=4*i
  f.extend([(b,b+4,b+5,b+1),(b+2,b+3,b+7,b+6),
            (b,b+2,b+6,b+4),(b+1,b+5,b+7,b+3)])
 f.extend([(0,1,3,2)])
 k=4*(len(pts)-1)
 f.append((k+2,k+3,k+1,k))
 ob=geom(n,v,f,mat,kind,role)
 ob["R17_route_endpoints"]=json.dumps([pts[0],pts[-1]])
 rise=pts[-1][2]-pts[0][2]
 dist=sum(math.dist(a[:2],b[:2]) for a,b in zip(pts,pts[1:]))
 ob["R17_horizontal_route_length_m"]=round(dist,3)
 ob["R17_route_gradient"]=round(abs(rise)/dist,5)
 return ob,abs(rise)/dist

# STEP 1. A true ground-to-court-to-library PUBLIC CIRCULATION SECTION,
# built before ANY heroic shell, with real floors at physically chosen heights.
ground=collection("01 PUBLIC WALKABLE TOPOLOGY BEFORE SHELL")
rect("ENTRANCE_PUBLIC_STREET",-118,118,-172,-20,-1.5,0,
 "PUBLIC_HONEY_STONE",ground.name,"contiguous outer-city arrival street")
rect("WEST_ATRIUM_RIM",-123,-56,-20,145,-1.5,0,
 "PUBLIC_HONEY_STONE",ground.name,"public rim facing actual sunken square")
rect("EAST_ATRIUM_RIM",56,123,-20,145,-1.5,0,
 "PUBLIC_HONEY_STONE",ground.name,"street of rooted public life")
rect("NORTH_CULTURAL_SQUARE",-123,123,125,175,-1.5,0,
 "PUBLIC_HONEY_STONE",ground.name,"ground access to cultural rooms")
prism("SUNKEN_STONE_CIVIC_FLOOR",
 [(-54,-12),(48,-19),(62,35),(45,116),(-50,116),(-65,66)],-7.5,-6,
 "CIVIC_PALE_STONE",ground.name,"real public room open to sky and upper street")
# Connection ground west branch -> level one on same west side.
ramps={}
ramps["WEST_ELEVATED_PUBLIC_PROMENADE"],g1=walk(
 "WEST_WALKABLE_ASCENT_FROM_GROUND_TO_14M",
 [(-96,-144,0),(-99,-85,3.0),(-107,-25,6.0),(-113,39,9.5),(-109,91,12.2),(-107,125,14)],
 [11,12,11,13,14,15],2.0,"AIR_SKY_MINT",
 "physical public ramp on west city inside edge","02 UPPER CONNECTED PUBLIC STREETS")
# Civic well descent is actual floor and has gradient 6/145 <=1/12.
ramps["COURT_DESCENT"],g2=walk(
 "CIVIC_WELL_GENTLE_DESCENT_FROM_ENTRY",
 [(3,-151,0),(8,-115,-1.5),(14,-80,-3.1),(15,-45,-4.4),(12,-5,-6.0)],
 [17,17,15,16,20],1.2,"PUBLIC_HONEY_STONE",
 "civic well ramp, real geometry, not an implied staircase",
 "02 UPPER CONNECTED PUBLIC STREETS")
rect("WEST_14M_LIVING_LIBRARY_CITY_FLOOR",-134,-67,108,157,12.5,14,
 "INNER_WARM_WOOD","02 UPPER CONNECTED PUBLIC STREETS","upper public library connected to ground ramp")
rect("EAST_14M_MUSEUM_GALLERY_FLOOR",64,136,103,157,12.5,14,
 "INNER_WARM_WOOD","02 UPPER CONNECTED PUBLIC STREETS","upper exhibition room connected by crossing")
# A real connected transverse bridge connects 14m levels.
ramps["14M_CROSSING"],g3=walk(
 "PUBLIC_FOURTEEN_METER_CROSSING",
 [(-104,130,14),(-43,128,14),(32,126,14),(100,128,14)],
 [21,18,19,21],2.1,"CIVIC_PALE_STONE",
 "same-height civic crossing visibly connects two destination floors",
 "02 UPPER CONNECTED PUBLIC STREETS")
# A second ramp starts on left level 14 and goes to upper research hall z 30.
ramps["WEST_30M_ASCENT"],g4=walk(
 "WEST_LEVEL_14_TO_RESEARCH_LEVEL_30",
 [(-112,127,14),(-118,82,17),(-126,24,20.8),(-133,-31,24.5),(-136,-86,28),(-133,-133,30)],
 [13,13,12,12,12,14],2.0,"AIR_SKY_MINT",
 "upper 16m ascent, not a disconnected floor",
 "02 UPPER CONNECTED PUBLIC STREETS")
rect("WEST_30M_RESEARCH_ROOM", -153,-96,-155,-98,28.7,30,
 "INNER_WARM_WOOD","02 UPPER CONNECTED PUBLIC STREETS","research and culture destination on the connected ascent")
assert all(v<=1/12 for v in (g1,g2,g4)),(g1,g2,g4)
assert g3==0
# STEP 2. Living CIVIC SPACE: enough ACTUAL furniture-level objects to be
# visible from the gallery, without introducing new isolated buildings.
def bench(n,x,y,z,orientation):
 if orientation=="E":coords=[(x-6,y-1.0),(x+6,y-1.0),(x+6,y+1),(x-6,y+1)]
 else:coords=[(x-1,y-6),(x+1,y-6),(x+1,y+6),(x-1,y+6)]
 return prism(n,coords,z,z+.75,"INNER_WARM_WOOD",
       "03 REAL CULTURAL DESTINATIONS","reading/meeting bench inside public destination")
for i,(x,y,z,axis) in enumerate([
 (-104,140,14,"E"),(-122,146,14,"E"),(-101,119,14,"E"),
 (94,145,14,"E"),(119,116,14,"E"),
 (-128,-121,30,"E"),(-106,-145,30,"E"),
 (-33,57,-6,"E"),(21,83,-6,"E")]):
 bench(f"AUTHORED_PUBLIC_SEAT_{i+1}",x,y,z,axis)
# Reading/library objects are within the SAME spatial interior, not pavillions.
for i,(x0,x1,y0,y1,z) in enumerate([
 (-130,-125,115,140,14),(-77,-72,116,144,14),
 (-145,-140,-144,-113,30),(-101,-97,-143,-113,30)]):
 rect(f"RESEARCH_PUBLIC_BOOK_WALL_{i}",x0,x1,y0,y1,z,z+7,
 "SHADOW_MINERAL","03 REAL CULTURAL DESTINATIONS",
 "real archive/cultural wall; internal clearance not certified")
# Life that reads as civic interior, not generic greens on exterior.
for i,(x,y,z) in enumerate([(-35,5,-6),(36,102,-6),(-114,35,0),(110,25,0)]):
 poly=[(x-4.5,y-3),(x+3,y-4.5),(x+5,y+2),(x-2,y+4)]
 prism("GROUND_CIVIC_PLANTED_TERRACE_"+str(i),poly,z,z+2.2,
  "LIVING_GREEN","03 REAL CULTURAL DESTINATIONS","raised planting in actual public hall")

# STEP 3. THE ARCHITECTURE IS A RESULT OF PUBLIC SECTION.
# Huge asymmetric outer folds bracket, but do not enclose the public
# journeys, and are NOT an all-covering tower shell. Broken ceiling remains
# above central courtyard. 3 deliberately nonmatching vault sections.
ARCH_Y=[-145,-80,10,75,144]
ARCH_Z=[76,99,122,111,69]
def vault_z(y,t):
 # Keel offset, deliberate asymmetry. 0/1 are grounded flanks.
 def lerp_controls(values):
  for k in range(len(ARCH_Y)-1):
   if ARCH_Y[k]<=y<=ARCH_Y[k+1]:
    a=(y-ARCH_Y[k])/(ARCH_Y[k+1]-ARCH_Y[k])
    u=a*a*(3-2*a)
    return values[k]*(1-u)+values[k+1]*u
  return values[0] if y<ARCH_Y[0] else values[-1]
 peak=lerp_controls(ARCH_Z)
 ridge=peak*(1-(abs((t-.43)/.58))**2)
 return max(7,ridge)+15+13*math.sin(2.6*t+1.25*math.sin(y/70))
def vault_x(y,t):
 spread=141+10*math.sin(y/74)
 return (2*t-1)*spread+17*math.sin(t*math.pi)*math.sin(y/63)
# discontinuous roof ribbons: deliberately architected giant skylight
# in the center of the cathedral, do NOT fabricate a filled ceiling.
def vault_band(n,t0,t1,material):
 yv=[-150,-132,-105,-77,-43,-10,22,58,91,122,150]
 nv=24
 v=[]
 for y in yv:
  for j in range(nv+1):
   t=t0+(t1-t0)*j/nv
   v.append((vault_x(y,t),y,vault_z(y,t)))
 f=[]
 for k in range(len(yv)-1):
  for j in range(nv):
   a=k*(nv+1)+j;f.append((a,a+1,a+nv+2,a+nv+1))
 return geom(n,v,f,material,"04 SECTION-DERIVED FRACTURED VAULT",
             "partial overhead vault anchored in floor circulation, open skylight")
vault_band("WEST_HIGH_CIVIC_SKYLIGHT_EAVE",.03,.285,"CIVIC_PALE_STONE")
vault_band("EAST_DIAGONAL_SKY_FRACTURE",.75,.98,"CIVIC_PALE_STONE")
# One central partial cross-ridge interrupts otherwise fully open upper sky.
vault_band("SINGLE_OFFSET_CULTURAL_CROWN_SPLICE",.43,.54,"SHADOW_MINERAL")
# Large finite structural members, not hundreds of repeated vertical pillars.
def tube(name,centerline,width,depth,material):
 from mathutils import Vector
 v=[]
 for i,(x,y,z) in enumerate(centerline):
  a=Vector(centerline[max(0,i-1)])
  b=Vector(centerline[min(len(centerline)-1,i+1)])
  T=(b-a).normalized()
  side=T.cross(Vector((0,0,1)))
  if side.length<.1:side=T.cross(Vector((0,1,0)))
  side.normalize()
  vert=T.cross(side).normalized()
  for X,Z in [(-1,-1),(1,-1),(1,1),(-1,1)]:
    v.append(tuple(Vector((x,y,z))+X*width*.5*side+Z*depth*.5*vert))
 f=[(0,3,2,1)]
 for i in range(len(centerline)-1):
  for q in range(4):
   a=i*4+q;b=i*4+(q+1)%4
   f.append((a,b,b+4,a+4))
 f.append(tuple(range(4*(len(centerline)-1),4*len(centerline))))
 return geom(name,v,f,material,"04 SECTION-DERIVED FRACTURED VAULT","distinct load-path expressed as form, structural capacity NOT calculated")
for name,y,w in [
 ("THRESHOLD_OBLIQUE_VAULT_RIB",-130,9),
 ("CULTURE_MIDSPAN_SKEWED_RIB",-6,12),
 ("REAR_IRREGULAR_DAYLIGHT_APSE",135,8)]:
 p=[]
 for i in range(25):
  t=i/24
  p.append((vault_x(y,t),y,vault_z(y,t)-2))
 tube(name,p,w,11,"SHADOW_MINERAL")
# Two striking wall folds on extreme edges, positioned outside pedestrian strips.
# They are *partial* and always visibly follow the hall levels: low street / high rim.
def folded_side(name,left):
 v=[]
 Ys=[-164,-121,-75,-15,48,110,165]
 for zlayer in (0,1,2,3):
  for i,y in enumerate(Ys):
   a=145+15*math.sin(y/55+(.3 if left else 1.3))
   xx=(-a if left else a)
   k=[0,13,51,86][zlayer]
   x=xx+(-1 if left else 1)*(.35*k+12*math.sin(i*.8+zlayer))
   z=[-2,15,51,88][zlayer]+7*math.cos(y/67+zlayer)
   v.append((x,y,z))
 faces=[]
 for row in range(3):
  for i in range(len(Ys)-1):
   a=row*len(Ys)+i
   faces.append((a,a+1,a+len(Ys)+1,a+len(Ys)))
 return geom(name,v,faces,"CIVIC_PALE_STONE","04 SECTION-DERIVED FRACTURED VAULT",
  "outer sculpted broken civic ground edge, not monolithic façade")
folded_side("WEST_ROOTED_GALLERY_CLIFF",True)
folded_side("EAST_RISING_CULTURAL_FISSURE",False)

# STEP 4. Cameras deliberately inspect true human spaces + complete 3D shape.
CAMS={
 "01_LONG_PUBLIC_APPROACH":((0,-365,120),(0,25,43),None),
 "02_FRONTAL_SECTION":((0,-370,93),(0,0,54),365),
 "03_OBLIQUE_STRUCTURE":((340,-290,230),(0,10,55),415),
 "04_SIDE_SECTION":((420,0,130),(0,0,55),376),
 "05_REAR":((0,390,138),(0,0,55),366),
 "06_AERIAL_CITY_SECTION":((285,-180,460),(0,10,24),432),
 "07_ENTERING_PUBLIC_HALL":((1,-153,2),(0,65,27),None),
 "08_INSIDE_LOW_COURT":((0,45,-4),(-110,101,23),None),
 "09_UPPER_READING_ROOM":((-112,116,17),(-13,32,33),None),
 "10_PUBLIC_HIGH_CITY":((-132,-109,34),(40,-8,68),None)
}
for name,(eye,look,ortho) in CAMS.items():
 cam=bpy.data.cameras.new(name)
 ob=bpy.data.objects.new(name,cam)
 collection("05 TEN NATIVE ART CRITIQUE CAMERAS").objects.link(ob)
 ob.location=eye
 ob.rotation_euler=(Vector(look)-ob.location).to_track_quat("-Z","Y").to_euler()
 cam.clip_start=.03;cam.clip_end=9000
 if ortho:
  cam.type="ORTHO";cam.ortho_scale=ortho
 else:
  cam.type="PERSP";cam.lens=21
scene.camera=bpy.data.objects["03_OBLIQUE_STRUCTURE"]
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_cavity=True
scene.render.resolution_x=1100
scene.render.resolution_y=740
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene["R17_ART_APPROVED"]=False
scene["R17_CITY_MASTER_COMPLETED"]=False
scene["R17_M247C_FORMAL_ADOPTION"]=False
scene["R17_MINECRAFT_CONSTRUCTION"]=False
scene["R17_ARCHITECTURE_PROGRAM"]="small noncanonical ~330m public-ravine section, circulation before shell"
scene["R17_ROUTE_GRADIENTS"]=json.dumps({"west_level_one":g1,"sunken_civic":g2,"level_one_crossing":g3,"level_two":g4})
scene["R17_PROGRAM_UNCERTIFIED"]="structures, roof drainage, crowd egress, accessibility/clearances, lighting, all full interior"
native=OUT/"R17_E0_EDITABLE_PUBLIC_RAVINE_330M.blend"
glb=OUT/"R17_E0_PUBLIC_RAVINE_330M.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",export_cameras=False,export_lights=False)
for name in CAMS:
 scene.camera=bpy.data.objects[name]
 scene.render.filepath=str(OUT/(name+".png"))
 bpy.ops.render.render(write_still=True)
models=[o for o in bpy.data.objects if o.type=="MESH"]
summary={
 "source":"R17 E0 330m independent single civic section, not canonical M247-C",
 "design_order":"civic walking network > public living spaces > partial sculpted roof and edges",
 "files":{"blend":native.name,"glb":glb.name,"cameras":[c+".png" for c in CAMS]},
 "mesh_count":len(models),
 "vertices":sum(len(o.data.vertices) for o in models),
 "triangles":sum(sum(max(1,len(f.vertices)-2) for f in o.data.polygons) for o in models),
 "floor_roles":sum(o.get("R17_role","").find("public")>=0 for o in models),
 "true_path_gradients":{k:v for k,v in [("west_first",g1),("sunken_court",g2),("level_one_bridge",g3),("west_second",g4)]},
 "max_intended_walking_gradient":1/12,
 "no_egress_or_engineering_certification":True,
 "formal_ART":"G0_NOT_YET_REVIEWED",
 "M247C_unchanged":True,
 "ten_km_city_master_complete":False,
 "Minecraft_write":False,
 "blender_version":bpy.app.version_string
}
(OUT/"R17_E0_NATIVE_MANIFEST.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf8")
print("R17_REAL_330M_PUBLIC_SECTION_10_NATIVE_VIEWS",json.dumps(summary,ensure_ascii=False),flush=True)
