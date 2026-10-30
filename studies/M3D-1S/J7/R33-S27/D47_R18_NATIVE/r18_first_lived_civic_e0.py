"""D47-R18 E0 / Tidal Light Civic Crossing.
A NEW, small, noncanonical architectural study. NOT an R17 mesh edit.
Native Blender, meters, Z up; real single continuous circulation body.
Art, building safety, structural loads and full accessibility are NOT certified.
"""
import bpy, math, json, sys, hashlib
from pathlib import Path
from mathutils import Vector

OUT=Path(sys.argv[-1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
COLORS={
 "pearl":(.78,.77,.70,1), "plaster":(.88,.81,.65,1),
 "stone":(.30,.36,.39,1), "shadow":(.13,.18,.24,1),
 "copper":(.67,.40,.27,1), "daylight":(.39,.74,.76,1),
 "book":(.40,.53,.49,1), "green":(.36,.56,.42,1)
}
for n,v in COLORS.items():
 m=bpy.data.materials.new("R18_"+n);m.diffuse_color=v
def collection(n):
 c=bpy.data.collections.get(n)
 if not c:
  c=bpy.data.collections.new(n);sc.collection.children.link(c)
 return c
def mesh(name,verts,faces,material,coll,role):
 data=bpy.data.meshes.new(name+"_mesh")
 data.from_pydata(verts,[],faces);data.update()
 ob=bpy.data.objects.new(name,data);collection(coll).objects.link(ob)
 data.materials.append(bpy.data.materials["R18_"+material])
 ob["R18_role"]=role;ob["ART_STATUS"]="NOT_REVIEWED"
 ob.shape_key_add(name="Basis")
 ob.shape_key_add(name="ART_DIRECTED_EDIT")
 return ob
def slab(name,poly,z0,z1,mat,coll,role):
 assert len(poly)>=3 and z1>z0
 N=len(poly)
 v=[(x,y,z0) for x,y in poly]+[(x,y,z1) for x,y in poly]
 f=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]
 f += [(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
 return mesh(name,v,f,mat,coll,role)
def rectangle(name,x0,x1,y0,y1,z,material,group,role,depth=.65):
 return slab(name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z-depth,z,material,group,role)
def continuous_walk(name,pts,widths,depth=1.1):
 """A single welded top, bottom, two sidewalls, both endcaps (not 12 loose treads)."""
 assert len(pts)==len(widths) and len(pts)>=3
 verts=[]; grades=[]
 for i,(x,y,z) in enumerate(pts):
  before=Vector(pts[max(0,i-1)])
  after=Vector(pts[min(len(pts)-1,i+1)])
  tang=after-before;dn=math.hypot(tang.x,tang.y)
  assert dn>0
  dx=-tang.y/dn;dy=tang.x/dn
  h=widths[i]/2
  verts += [(x-dx*h,y-dy*h,z),(x+dx*h,y+dy*h,z),
            (x-dx*h,y-dy*h,z-depth),(x+dx*h,y+dy*h,z-depth)]
  if i:
   a=pts[i-1];b=pts[i]
   grades.append(abs(b[2]-a[2])/math.dist(a[:2],b[:2]))
 faces=[(0,2,3,1)]
 for i in range(len(pts)-1):
  a=i*4;b=a+4
  faces += [(a,a+1,b+1,b),(a,b,b+2,a+2),
            (a+1,a+3,b+3,b+1),(a+2,b+2,b+3,a+3)]
 k=4*(len(pts)-1)
 faces.append((k,k+1,k+3,k+2))
 ob=mesh(name,verts,faces,"pearl","02 REAL CONNECTED PUBLIC MOVEMENT",
        "one actual welded walking volume traversing three different public functions")
 ob["DESIGN_WAYPOINTS_JSON"]=json.dumps(pts)
 ob["MAX_SEGMENT_GRADE"]=max(grades)
 return ob,grades
def wall_ribbon(name,centers,width,material,role):
 """Non-rectangular, finite low wall or archive screen with true thickness."""
 assert len(centers)>=2
 v=[]
 for x,y,bottom,top in centers:
  assert top>bottom
  v += [(x-width/2,y,bottom),(x+width/2,y,bottom),
        (x-width/2,y,top),(x+width/2,y,top)]
 f=[(0,1,3,2)]
 for i in range(len(centers)-1):
  a=4*i;b=a+4
  f += [(a,b,b+1,a+1),(a+2,a+3,b+3,b+2),
        (a,a+2,b+2,b),(a+1,b+1,b+3,a+3)]
 k=4*(len(centers)-1);f.append((k,k+2,k+3,k+1))
 return mesh(name,v,f,material,"03 OCCUPIED CULTURAL BUILDING SECTION",role)
def beam(name,points,width,height,mat,coll,role):
 """A solid, continuously connected architectural line, no loose repeated plates."""
 v=[]
 for i,p in enumerate(points):
  t=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])
  t.normalize()
  side=t.cross(Vector((0,0,1)))
  if side.length<.001: side=t.cross(Vector((0,1,0)))
  side.normalize();up=t.cross(side).normalized()
  center=Vector(p)
  for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]:
   v.append(tuple(center+side*a*width/2+up*b*height/2))
 f=[(0,3,2,1)]
 for i in range(len(points)-1):
  q=4*i
  for j in range(4):
   f.append((q+j,q+(j+1)%4,q+4+(j+1)%4,q+4+j))
 k=4*(len(points)-1);f.append((k,k+1,k+2,k+3))
 return mesh(name,v,f,mat,coll,role)

# 1) Authored public destinations, NOT a circular gallery nor hundreds of same floors.
rectangle("SOUTH_ARRIVAL_TERRACE",-56,-20,-64,-34,0,"stone",
 "01 DISTINCT INHABITED DESTINATIONS","real public arrival threshold")
slab("EXHIBITION_FLOOR_WITH_OBLIQUE_VIEW_EDGE",
 [(-25,-39),(8,-39),(12,-22),(-4,-11),(-25,-17)],1.25,2,
 "plaster","01 DISTINCT INHABITED DESTINATIONS",
 "public environmental art exhibition, not only a room label")
slab("HIGH_RESEARCH_READING_ROOM",
 [(8,6),(34,5),(39,23),(24,31),(7,24)],5.2,6,
 "book","01 DISTINCT INHABITED DESTINATIONS",
 "inward facing reading room reached by actual continuous walking volume")
slab("TRANSIT_OBSERVATION_TRANSFER",
 [(-24,33),(-4,31),(6,39),(0,56),(-25,54)],7.4,8.2,
 "stone","01 DISTINCT INHABITED DESTINATIONS",
 "raised public transit transfer, visibly linked to cultural research hall")
# Journey turns through cultural exhibition, reading room, transfer rather than repeating a stair module.
WAYPOINTS=[
 (-37,-47,0),(-29,-41,.65),(-19,-34,1.35),(-10,-28,2),
 (3,-20,2.8),(16,-13,3.65),(24,-3,4.5),(22,8,5.25),
 (18,17,6),(12,26,6.7),(2,33,7.4),(-11,40,8.2)
]
ROUTE,gradients=continuous_walk(
 "CONNECTED_SINGLE_BODY_PUBLIC_WALK_CULTURE_RESEARCH_TRANSIT",
 WAYPOINTS,[7,7,8,9,8,7,7,7,8,8,8,9])
assert max(gradients)<1/12,gradients

# 2) Three materially different cultural spaces; distinct internal sightlines.
# The public exhibition is an oblique landscape: angled evidence walls, a split
# acoustic light roof, and a visually open path. NOT a generic box named gallery.
wall_ribbon("CULTURE_ARTIFACT_STRATA_WEST",
 [(-23,-35,2,8),(-24,-25,2,11),(-18,-14,2,15),(-11,-9,2,12)],
 1.25,"copper","visible geological archives, floor level 2")
wall_ribbon("CULTURE_ARTIFACT_STRATA_EAST",
 [(9,-39,2,8),(12,-30,2,13),(8,-22,2,15)],
 1.05,"stone","differently angled public exhibit wall and daylight aperture")
beam("LIGHT_CUT_ABOVE_CULTURE",
 [(-22,-33,13),(-8,-26,17),(7,-20,19),(11,-10,16)],
 2.4,2.0,"pearl","04 SECTION FORMED BY USE AND LIGHT",
 "non-repeating high daylight edge above actual cultural forum")

# Upper reading room consists of a thick distinct body around the actual
# floor, with continuous vertical archive screens & three separated openings.
wall_ribbon("RESEARCH_WALL_OPEN_TO_PUBLIC_VOID",
 [(33,5,6,14),(37,13,6,19),(38,23,6,25)],
 1.9,"stone","reading room vertical archive boundary, offset to preserve view")
wall_ribbon("RESEARCH_WALL_OVERLOOK",
 [(8,6,6,17),(5,14,6,22),(8,23,6,19)],
 1.2,"copper","view-facing high reading-room wall with oblique silhouette")
beam("RESEARCH_INHABITED_CROWN",
 [(3,9,19),(13,11,24),(28,16,29),(38,24,24)],
 3.4,2.3,"plaster","04 SECTION FORMED BY USE AND LIGHT",
 "partial daylight roof over actual elevated room, not a complete station vault")
# Distinct transit interface at high elevation, intentionally exterior.
wall_ribbon("TRANSIT_WIND_AND_SIGNAL_SPINE",
 [(-24,33,8.2,12),(-27,43,8.2,21),(-22,54,8.2,25)],
 2.0,"shadow","high open transport horizon and wayfinding edge")
beam("ASYMMETRIC_CITY_CONNECTION_PROFILE",
 [(-23,55,22),(-11,51,25),(-2,45,21),(5,36,16)],
 2.8,1.8,"pearl","04 SECTION FORMED BY USE AND LIGHT",
 "angled cantilever forms from lived transfer and viewing direction")
# 3) Occupation is meaningful: 3 genuinely different scales, not mass repeats.
slab("CULTURE_PUBLIC_TACTILE_ATLAS",
 [(-10,-34),(-4,-33),(-3,-28),(-9,-26)],2,4.6,"copper",
 "03 OCCUPIED CULTURAL BUILDING SECTION",
 "walk-around civic topographic atlas presented in actual gallery")
slab("RESEARCH_COLLABORATIVE_TABLE",
 [(13,13),(23,12),(29,17),(20,20),(12,19)],6,6.95,
 "plaster","03 OCCUPIED CULTURAL BUILDING SECTION",
 "shared environmental research working surface")
wall_ribbon("VERTICAL_LIVED_RECORD_LIBRARY",
 [(29,7,6,11),(30,12,6,13),(28,21,6,15)],
 .55,"book","public legible archive wall within actual elevated reading room")
slab("TRANSIT_VIEWING_PLINTH",
 [(-20,46),(-11,45),(-8,50),(-16,53)],8.2,8.9,"copper",
 "03 OCCUPIED CULTURAL BUILDING SECTION",
 "raised civic horizon marker attached to high transport concourse")
# One planted outdoor room provides natural contrast, deliberately not repeated.
slab("ENTRY_ONE_INHABITED_GREEN_COURT",
 [(-53,-42),(-44,-40),(-43,-35),(-55,-34)],0,1.1,
 "green","03 OCCUPIED CULTURAL BUILDING SECTION","actual entry court planting bed")

# G0 cameras: first five exterior & upper, last five at human standing height.
cams={
 "01_FAR_CITY_APPROACH":((-122,-132,76),(-4,0,11),105),
 "02_ENTRY_FRONTAL":((-7,-115,39),(-7,-1,12),None),
 "03_OBLIQUE_OCCUPIED_SECTION":((100,-94,70),(0,0,12),110),
 "04_SIDE_UNMASKED":((125,8,46),(0,0,12),100),
 "05_REAR_TRANSIT":((-30,135,42),(-10,7,13),None),
 "06_AERIAL_ROOM_RELATION":((94,87,154),(0,0,7),135),
 "07_HUMAN_GROUND_ENTRY":((-38,-60,1.7),(-13,-28,6),None),
 "08_HUMAN_IN_GALLERY":((-8,-34,3.7),(19,-10,15),None),
 "09_HUMAN_RESEARCH_ROOM":((18,13,7.7),(-12,-28,5),None),
 "10_HUMAN_TRANSIT_VIEW":((-10,44,9.9),(19,-7,19),None)
}
for n,(eye,look,ortho) in cams.items():
 cam=bpy.data.cameras.new(n)
 ob=bpy.data.objects.new(n,cam)
 collection("05 MULTI_SCALE_REAL_3D_ART_CAMERAS").objects.link(ob)
 ob.location=eye;ob.rotation_euler=(Vector(look)-ob.location).to_track_quat("-Z","Y").to_euler()
 cam.clip_start=.05;cam.clip_end=2000
 if ortho:cam.type="ORTHO";cam.ortho_scale=ortho
 else:cam.type="PERSP";cam.lens=24
sc.camera=bpy.data.objects["03_OBLIQUE_OCCUPIED_SECTION"]
sc.render.engine="BLENDER_WORKBENCH"
sc.display.shading.light="STUDIO"
sc.display.shading.color_type="MATERIAL"
sc.display.shading.show_cavity=True
sc.render.resolution_x=1100;sc.render.resolution_y=740
sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc["R18_ART_APPROVED"]=False
sc["R18_FUNCTION_CERTIFIED"]=False
sc["R18_M247C_ADOPTED"]=False
sc["R18_CITY_MASTER_COMPLETE"]=False
sc["R18_MINECRAFT_WRITE"]=False
sc["R18_STATUS"]="G0_SCIENTIFICALLY_UNCERTIFIED_NEW_ARCHITECTURAL_TRIAL"
sc["R18_ABSTRACT"]="inhabited civic exhibition -> exposed research room -> urban transit"
native=OUT/"R18_E0_EDITABLE_LIVED_CIVIC.blend"
glb=OUT/"R18_E0_LIVED_CIVIC.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",export_cameras=False,export_lights=False)
for n in cams:
 sc.camera=bpy.data.objects[n]
 sc.render.filepath=str(OUT/(n+".png"))
 bpy.ops.render.render(write_still=True)
objs=[o for o in bpy.data.objects if o.type=="MESH"]
manifest={
 "source":"New R18 E0 lived-civic room study, 1:1 meters, noncanonical",
 "NOT_R17_recycled_mesh":True,
 "blender_version":bpy.app.version_string,
 "route_waypoints":WAYPOINTS,
 "max_route_segment_grade":max(gradients),
 "routes_are_natively_welded_in_one_object":True,
 "object_count":len(objs),
 "total_vertices":sum(len(o.data.vertices) for o in objs),
 "triangles":sum(sum(max(1,len(f.vertices)-2) for f in o.data.polygons) for o in objs),
 "files":{"blend":native.name,"glb":glb.name,"cameras":[n+".png" for n in cams]},
 "formal_ART":"NOT_REVIEWED","function":"INDEPENDENT_GEO_QA_REQUIRED",
 "human_accessibility_certified":False,"egress_and_load_certified":False,
 "city_master_complete":False,"minecraft_write":False,
 "protected_M247C_modified":False}
(OUT/"R18_E0_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print("R18_E0_NATIVE_OUTPUT",json.dumps(manifest,ensure_ascii=False),flush=True)
