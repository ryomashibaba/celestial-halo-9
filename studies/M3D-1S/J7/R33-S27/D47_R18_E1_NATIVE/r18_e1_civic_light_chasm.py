"""D47 R18 E1 — CIVIC LIGHT CHASM / 光潮の交界院.
Independent new research model, NOT E0 detail and NOT canonical central city.
Art-first authored 1:1 civic void and cultural interior / transit experience.
Three decisive genuine Blender cameras BEFORE further detailed production.
Z-up, metres. NO safety, structural, accessibility or art certification.
"""
from pathlib import Path
import bpy, sys, json, math
from mathutils import Vector

out=Path(sys.argv[-1]).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
palette={
 "limestone":(.69,.71,.68,1),
 "porcelain":(.84,.83,.75,1),
 "basalt":(.18,.25,.30,1),
 "bronze":(.67,.48,.32,1),
 "cyan_glass":(.22,.69,.73,1),
 "forest":(.30,.46,.39,1),
 "floor_warm":(.63,.57,.47,1),
 "void":(.09,.16,.22,1)}
for k,v in palette.items():
 m=bpy.data.materials.new("E1_"+k);m.diffuse_color=v
def col(name):
 c=bpy.data.collections.get(name)
 if not c:
  c=bpy.data.collections.new(name);scene.collection.children.link(c)
 return c
def mesh(name,V,F,mat,group,role):
 me=bpy.data.meshes.new(name+"_mesh")
 me.from_pydata(V,[],F);me.update()
 ob=bpy.data.objects.new(name,me);col(group).objects.link(ob)
 me.materials.append(bpy.data.materials["E1_"+mat])
 ob["E1_function"]=role
 ob["E1_is_formally_adopted"]=False
 ob.shape_key_add(name="Basis")
 ob.shape_key_add(name="Editable_Artist_Variant")
 return ob
def prism(name,xy,z0,z1,material,group,role):
 assert z1>z0 and len(xy)>=3
 n=len(xy)
 V=[(x,y,z0) for x,y in xy]+[(x,y,z1) for x,y in xy]
 F=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
 F +=[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)]
 return mesh(name,V,F,material,group,role)
def loft(name,profiles,mat,group,role):
 # Consecutive authored polyline rings; polyhedron with real depth.
 n=len(profiles[0]);assert len(profiles)>1 and n>=3
 assert all(len(p)==n for p in profiles)
 V=[pt for ring in profiles for pt in ring]
 F=[tuple(range(n-1,-1,-1))]
 for j in range(len(profiles)-1):
  for i in range(n):
   a=j*n+i
   F.append((a,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
 F.append(tuple(range((len(profiles)-1)*n,len(profiles)*n)))
 return mesh(name,V,F,mat,group,role)
def ribbon(name,positions,width,depth,mat,group,role):
 # Swept closed architectural element, not a stack of disconnected objects.
 V=[]
 for i,p in enumerate(positions):
  a=Vector(positions[max(0,i-1)])
  b=Vector(positions[min(len(positions)-1,i+1)])
  tang=b-a
  if tang.length<1e-5:raise ValueError(name)
  tang.normalize()
  side=tang.cross(Vector((0,0,1)))
  if side.length<.1:side=tang.cross(Vector((0,1,0)))
  side.normalize();up=tang.cross(side).normalized()
  C=Vector(p)
  for s,t in [(-1,-1),(1,-1),(1,1),(-1,1)]:
   V.append(tuple(C+side*s*width/2+up*t*depth/2))
 F=[(0,3,2,1)]
 for j in range(len(positions)-1):
  for i in range(4):
   a=4*j+i;b=4*j+(i+1)%4
   F.append((a,b,b+4,a+4))
 k=4*(len(positions)-1);F.append((k,k+1,k+2,k+3))
 return mesh(name,V,F,mat,group,role)
def thin_screen(name,pts,z0,z1,mat,role):
 # Actual vertical face from original slanted curved drawing, not a generic rect.
 v=[(x,y,z0) for x,y in pts]+[(x,y,z1) for x,y in pts]
 n=len(pts)
 f=[(i,i+1,n+i+1,n+i) for i in range(n-1)]
 return mesh(name,v,f,mat,"03 DISTINCT_PUBLIC_INTERIORS",role)
def walk(name,centerline,widths,material):
 assert len(centerline)==len(widths)
 V=[]
 for i,(x,y,z) in enumerate(centerline):
  a=Vector(centerline[max(0,i-1)])
  b=Vector(centerline[min(i+1,len(centerline)-1)])
  t=b-a; t.z=0;t.normalize();normal=Vector((-t.y,t.x,0))
  for side,dep in [(-1,0),(1,0),(-1,-1.3),(1,-1.3)]:
   p=Vector((x,y,z))+normal*(side*widths[i]/2)+Vector((0,0,dep))
   V.append(tuple(p))
 F=[(0,2,3,1)]
 for i in range(len(centerline)-1):
  a=4*i;b=a+4
  F +=[(a,a+1,b+1,b),(a,b,b+2,a+2),
       (a+1,a+3,b+3,b+1),(a+2,b+2,b+3,a+3)]
 k=4*(len(centerline)-1);F.append((k,k+1,k+3,k+2))
 ob=mesh(name,V,F,material,"02 PHYSICAL_CIRCULATION_UNCERTIFIED",
         "single route with public sightline and grade; dimensions not safety certified")
 grades=[abs(b[2]-a[2])/math.hypot(b[0]-a[0],b[1]-a[1])
         for a,b in zip(centerline,centerline[1:])]
 ob["E1_waypoints_m"]=json.dumps(centerline)
 ob["E1_max_slope"]=max(grades)
 return ob,max(grades)
# CITY SPACE FIRST: void is open north-south and open to side daylight;
# no ring, complete overhead arch or repeated rectangular floors.
prism("CIVIC_ARRIVAL_GROUND_A",
 [(-65,-99),(16,-101),(37,-79),(20,-64),(-53,-67),(-73,-82)],-2.4,0,
 "floor_warm","01 CIVILIZATION_CROSS_SECTION",
 "ground entry framed by actual lower reading rooms")
prism("CIVIC_OPEN_FORUM_SUNKEN",
 [(-22,-50),(20,-50),(35,-16),(28,34),(8,55),(-31,36),(-36,-10)],-7,-5.8,
 "limestone","01 CIVILIZATION_CROSS_SECTION",
 "low public performance and research exchange court, naturally sky-lit")
# WEST: a *thick inhabitable arc of urban ground* with a usable exhibition
# overlook, but visibly distinct convex / concave massing.
west0=[(-104,-77),(-62,-80),(-48,-53),(-49,-19),(-30,21),
       (-43,67),(-99,80),(-116,40),(-115,-32)]
west1=[(-106,-80),(-66,-80),(-50,-55),(-51,-19),(-33,22),
       (-47,70),(-95,81),(-117,40),(-115,-33)]
prism("WEST_INHABITED_MINERAL_ROOT",west0,-12,2.8,
 "basalt","01 CIVILIZATION_CROSS_SECTION",
 "thick nonrepetitive inhabited western bank that shapes civic negative space")
west_top=[(-100,-69),(-57,-78),(-47,-49),(-36,-16),(-16,29),
          (-27,68),(-91,80),(-107,46),(-111,-19)]
prism("WEST_CULTURAL_GALLERY_UPPER_FLOOR",west_top,7.5,9.2,
 "floor_warm","01 CIVILIZATION_CROSS_SECTION",
 "inhabitable culture archive gallery around urban open forum")
# EAST: elevated public research body *asymmetric to west*, never mirrored.
east0=[(36,-91),(87,-81),(119,-39),(118,19),(91,74),(52,83),
       (36,47),(47,6),(29,-30)]
east1=[(32,-88),(88,-78),(120,-38),(121,18),(87,81),(47,80),
       (30,43),(38,3),(23,-31)]
prism("EAST_RESEARCH_CITY_GROUND",east0,-6,4.5,
 "basalt","01 CIVILIZATION_CROSS_SECTION",
 "deep occupied research bank, partly facing public square")
prism("EAST_LIVING_RESEARCH_TERRACE",
 [(42,-52),(91,-54),(105,-18),(97,29),(76,57),(36,53),(26,9)],
 19.5,21.5,"porcelain","01 CIVILIZATION_CROSS_SECTION",
 "high public laboratory with deliberate view of lower forum")
# NORTH high transit reaches the rest of the city at a distinct height.
prism("NORTHERN_TRANSIT_METROPOLITAN_GATEWAY",
 [(-53,65),(3,59),(57,65),(82,106),(-46,113),(-67,94)],
 29,32,"floor_warm","01 CIVILIZATION_CROSS_SECTION",
 "real 30m public transport threshold leading towards future linked city")
# One meandering low-level promenade. High-level connections remain NOT CERTIFIED.
# Does not claim that rooms at z9, z21, z32 are reached by this single ramp.
pts=[(-10,-89,0),(-7,-75,.8),(-2,-58,1.8),(10,-40,3),(16,-17,4.2),
     (13,6,5.4),(7,28,6.6),(-2,49,7.8),(-13,68,9.0)]
route,grade=walk("CONTINUOUS_VISIBLE_CULTURAL_RAVINE_PROMENADE",
 pts,[11,11,12,12,12,13,13,12,12],"limestone")
# Actual varied high-section city access structural prototypes (not certified).
ribbon("HIGH_RESEARCH_TRANSIT_OVERPASS",
 [(68,40,21.5),(54,63,23.9),(32,82,27),(7,94,31)],
 9,2,"porcelain","02 PHYSICAL_CIRCULATION_UNCERTIFIED",
 "continuous-looking but slope, landing, deck clearance and joints not certified")
# TWO REAL PUBLIC ROOM INTERIORS, distinct spatial use and orientation.
# Workshop is an open multi-height culture hall; exhibit walls have differing angle.
thin_screen("WEST_CULTURE_CARVED_ARCHIVE_FACE",
 [(-48,-62),(-46,-40),(-40,-21),(-34,-5),(-26,17),(-21,37)],
 9.2,20.5,"bronze",
 "real visible research artifacts mounted in a multi-height western public gallery")
thin_screen("CULTURAL_HISTORY_TERRACED_STORY",
 [(-93,-52),(-76,-33),(-63,-9),(-49,21),(-44,55)],
 9.2,24.2,"limestone",
 "distinct historical archive wall, angled against public circulation")
thin_screen("EAST_PUBLIC_RESEARCH_FACADE",
 [(42,-57),(34,-24),(30,1),(31,29),(36,55)],
 21.5,39,"cyan_glass",
 "transparent multi-height public laboratory facing full inhabited atrium")
thin_screen("RESEARCH_INSTRUMENT_NORTH_WALL",
 [(65,55),(81,33),(95,13),(96,-15)],
 21.5,34,"bronze",
 "tall public research instrument wall, visible from pedestrian arrivals")
# Architecture grows FROM distinct rooms. Two asymmetrical carved daylight crests,
# leaving the heart fully open to sky and from rear. Not a full giant arched station roof.
loft("WEST_LIGHT_CREST_FROM_CULTURAL_ARCHIVE",[
 [(-114,-65,24),(-95,-75,28),(-65,-60,37),(-51,-13,34),(-30,35,32),(-49,80,29)],
 [(-101,-70,37),(-85,-76,43),(-60,-47,55),(-37,-8,58),(-22,38,44),(-49,79,40)],
 [(-95,-68,41),(-75,-64,48),(-53,-38,60),(-36,-3,64),(-18,39,51),(-44,69,44)]
],"porcelain","04 PARTIAL_DAYLIGHT_ARCHITECTURE",
 "western partial inhabited crest rooted in culture; central open light ravine remains")
loft("EAST_LIGHT_SPIRE_FROM_RESEARCH",[
 [(98,-63,35),(122,-46,39),(125,-10,46),(112,29,49),(82,78,46),(65,66,38)],
 [(90,-60,48),(118,-43,53),(132,-10,60),(115,31,69),(91,78,62),(69,63,49)],
 [(86,-58,51),(113,-37,59),(130,-6,70),(111,35,79),(92,72,67),(67,61,53)]
],"basalt","04 PARTIAL_DAYLIGHT_ARCHITECTURE",
 "right-sided tall nonmirror research urban crown, no center roof")
# A civic cross-sectional overhead canopy, not a repetitive screen on empty lots.
ribbon("CULTURE_RESEARCH_GAP_LIGHT_MARKER",
 [(-51,-14,33),(-24,-10,44),(12,-2,48),(44,4,43),(85,18,49)],
 3.2,4,"bronze","04 PARTIAL_DAYLIGHT_ARCHITECTURE",
 "single daylight line explaining relationship of the adjacent civic rooms")
# The spaces use deliberately different kinds of intellectual activity.
prism("CULTURAL_PUBLIC_PALEOGRAPHIC_TABLE",
 [(-83,15),(-68,10),(-58,19),(-69,30),(-83,26)],
 9.2,10.7,"bronze","03 DISTINCT_PUBLIC_INTERIORS",
 "walk-around archival exhibition table, within western room")
loft("RESEARCH_SHARED_PLANETARY_INSTRUMENT",[
 [(66,-32,21.5),(79,-28,21.5),(82,-16,21.5),(68,-15,21.5)],
 [(67,-29,26),(82,-27,24),(84,-15,24),(69,-15,26)],
 [(70,-27,31),(78,-25,31),(81,-17,31),(70,-16,31)]
],"cyan_glass","03 DISTINCT_PUBLIC_INTERIORS",
 "volumetric civic research instrument that can be examined from several sides")
ribbon("EXHIBITION_AIRLIGHT_SUSPENDED_MAP",
 [(-22,-28,12),(-16,-18,14),(2,-8,20),(22,-7,21)],
 1.2,1.4,"bronze","03 DISTINCT_PUBLIC_INTERIORS",
 "suspended three-dimensional public cultural map giving a central visual destination")
prism("FORUM_CONVEX_INFORMATION_ISLAND",
 [(-12,-24),(5,-29),(16,-13),(1,-5),(-13,-9)],
 -5.8,-4.7,"bronze","03 DISTINCT_PUBLIC_INTERIORS",
 "actual public interpretation desk in lower gathering space")
ribbon("NORTH_RAIL_HORIZON_EDGE",
 [(-42,110,33),(-4,112,35),(39,104,37),(76,103,34)],
 2.1,1.7,"cyan_glass","04 PARTIAL_DAYLIGHT_ARCHITECTURE",
 "asymmetric city transport edge that remains open behind")
# Actual people-proportion reference geometries are grouped, for scale only.
for n,(x,y,z) in enumerate([(-8,-72,0),(-17,-21,-5.8),(71,8,21.5)]):
 prism("SCALE_REFERENCE_NOT_POPULATION_"+str(n),
 [(x-.32,y-.32),(x+.32,y-.32),(x+.32,y+.32),(x-.32,y+.32)],
 z,z+1.75,"forest","05 SCALE_AND_CAMERA",
 "scale reference only; not an occupied city population claim")

CAMS={
 "01_HUMAN_ENTRANCE":((-9,-97,1.7),(1,2,21),None),
 "02_TRUE_OBLIQUE_SILHOUETTE":((-191,-137,143),(3,11,27),245),
 "03_UNMASKED_REAR":((55,196,107),(1,-1,28),240)
}
for name,(eye,target,ortho) in CAMS.items():
 data=bpy.data.cameras.new(name)
 ob=bpy.data.objects.new(name,data)
 col("05 SCALE_AND_CAMERA").objects.link(ob)
 ob.location=eye
 ob.rotation_euler=(Vector(target)-ob.location).to_track_quat("-Z","Y").to_euler()
 data.clip_start=.05;data.clip_end=5000
 if ortho:
  data.type="ORTHO";data.ortho_scale=ortho
 else:
  data.type="PERSP";data.lens=24
scene.camera=bpy.data.objects["02_TRUE_OBLIQUE_SILHOUETTE"]
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type="BOTH"
scene.render.film_transparent=False
scene.render.resolution_x=1260
scene.render.resolution_y=840
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene["D47_R18_E1_ART_PASS"]=False
scene["D47_R18_E1_ART_REVIEW"]="AWAITING_3_TRUE_VIEWS"
scene["D47_R18_E1_FUNCTION_CERTIFIED"]=False
scene["D47_R18_E1_CITY_MASTER_COMPLETE"]=False
scene["D47_R18_E1_M247C_ADOPTED"]=False
scene["D47_R18_E1_MINECRAFT_WRITE"]=False
scene["D47_R18_E1_STATUS"]="ART_FIRST_NONCANONICAL_R18_E1"
native=out/"R18_E1_REAL_EDITABLE_CIVIC_LIGHT_CHASM.blend"
glb=out/"R18_E1_REAL_CIVIC_LIGHT_CHASM.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
  export_cameras=False,export_lights=False)
for name in CAMS:
 scene.camera=bpy.data.objects[name]
 scene.render.filepath=str(out/(name+".png"))
 bpy.ops.render.render(write_still=True)
objects=[o for o in bpy.data.objects if o.type=="MESH"]
manifest={
 "stage":"D47 R18 E1 first art gate, noncanonical",
 "model":"new civic light chasm, architecture from three distinct public experiences",
 "generation":"new authored real Blender geometry; NOT E0 source nor mesh reused",
 "files":{"blend":native.name,"glb":glb.name,"cameras":[n+".png" for n in CAMS]},
 "mesh_count":len(objects),
 "vertices":sum(len(o.data.vertices) for o in objects),
 "triangles":sum(len(p.vertices)-2 for o in objects for p in o.data.polygons),
 "entry_to_low_culture_route":{"max_grade":grade,"continuous_single_mesh":True},
 "UNCONNECTED_HI_LEVELS_STILL_UNCERTIFIED":True,
 "STRUCTURAL_ACCESSIBILITY_EGRESS_UNCERTIFIED":True,
 "ART_APPROVAL":False,"FORMAL_M247C_ADOPTION":False,
 "CITY_MASTER_COMPLETE":False,"MINECRAFT_WRITE":False,
 "Blender":bpy.app.version_string}
(out/"R18_E1_G0_MANIFEST.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf8")
print("R18_E1_G0_TRUE3D_3VIEW_ART_PENDING",json.dumps(manifest,ensure_ascii=False),flush=True)
