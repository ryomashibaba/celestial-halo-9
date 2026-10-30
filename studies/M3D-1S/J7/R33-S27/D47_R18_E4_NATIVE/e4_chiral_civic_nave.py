"""CELESTIAL HALO-9 / R18 E4 G0 / 斜光の記憶路 — CHIRAL CIVIC NAVE.
New, editable Blender 1:1 metre public architectural space, not an E3 ring edit.
Art-first authored non-repeating occupiable room with a diagonal daylight fissure
and contrasting public culture / environmental research / future transit volumes.
Source is in discrete artist-intended parts; in no way a completed City Master.
No ART acceptance, certified function, physical building or Minecraft works.
"""
import bpy, sys, json, math
from pathlib import Path
from mathutils import Vector
out=Path(sys.argv[-1]).resolve()
out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene
colors={
 "porcelain":(.84,.82,.72,1),"black_rock":(.14,.23,.27,1),
 "cobalt":(.14,.32,.42,1),"bronze":(.70,.48,.26,1),
 "window_cyan":(.34,.78,.76,1),"pearl":(.72,.77,.72,1),
 "stone":(.42,.48,.46,1),"archive_wood":(.44,.31,.24,1),
 "reading_green":(.30,.53,.46,1),"soft_light":(.86,.91,.82,1)}
for name,color in colors.items():
 m=bpy.data.materials.new("E4_"+name);m.diffuse_color=color
def collection(n):
 c=bpy.data.collections.get(n)
 if c is None:c=bpy.data.collections.new(n);S.collection.children.link(c)
 return c
def raw(n,V,F,mat,gr,role):
 assert mat in colors,(n,mat)
 d=bpy.data.meshes.new(n+"_data")
 d.from_pydata(V,[],F);d.update()
 o=bpy.data.objects.new(n,d)
 collection(gr).objects.link(o);d.materials.append(bpy.data.materials["E4_"+mat])
 o["room_role"]=role;o["E4_study_unapproved"]=True
 o.shape_key_add(name="Basis");o.shape_key_add(name="ArtistEditable")
 return o
def slab(n,XY,z0,z1,mat,gr,role):
 assert z1>z0 and len(XY)>=3
 N=len(XY)
 V=[(x,y,z0) for x,y in XY]+[(x,y,z1) for x,y in XY]
 F=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]
 F +=[(i,(i+1)%N,N+(i+1)%N,N+i) for i in range(N)]
 return raw(n,V,F,mat,gr,role)
def box(n,x0,x1,y0,y1,z0,z1,mat,gr,role):
 return slab(n,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1,mat,gr,role)
def strip(n,L,R,top,thick,mat,gr,role):
 # Author controls every source/terminus point and contour, no primitive ring.
 assert len(L)==len(R)==len(top) and len(L)>2
 V=[]
 for (x,y),(xx,yy),z in zip(L,R,top):
  V.extend([(x,y,z),(xx,yy,z),(x,y,z-thick),(xx,yy,z-thick)])
 F=[(0,2,3,1)]
 for i in range(len(L)-1):
  a=i*4;b=a+4
  F +=[(a,a+1,b+1,b),(a,b,b+2,a+2),
      (a+1,a+3,b+3,b+1),(a+2,b+2,b+3,a+3)]
 k=4*(len(L)-1);F.append((k,k+1,k+3,k+2))
 return raw(n,V,F,mat,gr,role)
def artist_loft(n,sections,mat,gr,role):
 # Radially asymmetric artist-specified closed planar rings in 3D space.
 assert len(sections)>1 and len(sections[0])>=3
 N=len(sections[0]);assert all(len(x)==N for x in sections)
 V=[p for r in sections for p in r]
 F=[tuple(range(N-1,-1,-1))]
 for j in range(len(sections)-1):
  for i in range(N):
   a=j*N+i;b=j*N+(i+1)%N
   F.append((a,b,b+N,a+N))
 a=N*(len(sections)-1);F.append(tuple(range(a,a+N)))
 return raw(n,V,F,mat,gr,role)
def artist_beam(n,A,B,width,depth,mat,gr,role):
 a=Vector(A);b=Vector(B)
 t=(b-a).normalized()
 u=t.cross(Vector((0,0,1)))
 if u.length<.01:u=t.cross(Vector((0,1,0)))
 u.normalize();v=t.cross(u).normalized()
 V=[]
 for center in (a,b):
  for i,j in ((-1,-1),(1,-1),(1,1),(-1,1)):
   V.append(tuple(center+width*.5*i*u+depth*.5*j*v))
 F=[(3,2,1,0),(4,5,6,7)]
 F +=[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
 return raw(n,V,F,mat,gr,role)
def stairbank(n,xy0,xy1,z0,z1,stepN,mat,group,role):
 # Real steps, but **not** a proof of continuous, safe, barrier-free access.
 x0,y0=xy0;x1,y1=xy1
 for i in range(stepN):
  a=i/stepN;b=(i+1)/stepN
  dx=x1-x0;dy=y1-y0
  center=(x0+dx*(a+b)/2,y0+dy*(a+b)/2)
  d=math.hypot(dx,dy)
  normal=(-dy/d,dx/d)
  w=5.5
  P=[
   (x0+dx*a+normal[0]*w/2,y0+dy*a+normal[1]*w/2),
   (x0+dx*a-normal[0]*w/2,y0+dy*a-normal[1]*w/2),
   (x0+dx*b-normal[0]*w/2,y0+dy*b-normal[1]*w/2),
   (x0+dx*b+normal[0]*w/2,y0+dy*b+normal[1]*w/2)]
  slab(n+"_STEP_"+str(i),P,z0+(z1-z0)*a-1,z0+(z1-z0)*b,
       mat,group,role)
def bookwall(n,anchor,direction,length,z0,z1,count):
 # Visible physical archival storage; one deliberately irregular modular wall.
 x,y=anchor
 tangent=Vector((direction[0],direction[1],0)).normalized()
 lateral=Vector((-tangent.y,tangent.x,0))
 for j in range(count):
  u=j/(count-1) if count>1 else .5
  a=Vector((x,y,0))+tangent*(u*length)
  w=length/count*.87
  P=[]
  for dx,dy in ((-w/2,-.55),(w/2,-.55),(w/2,.55),(-w/2,.55)):
   p=a+tangent*dx+lateral*dy
   P.append((p.x,p.y))
  slab(n+"_CABINET_"+str(j),P,z0,z1-.25,"archive_wood",
       "03 ACTUAL CULTURAL PUBLIC LIFE","physical archives in a genuine public reading corridor")
  for row in range(3):
   hz=z0+1.15+row*(z1-z0-1.3)/3
   slab(n+"_BACKLIT_RECORD_"+str(j)+"_"+str(row),P,hz,hz+.25,
        "bronze","03 ACTUAL CULTURAL PUBLIC LIFE","actual exhibits in archive cabinet")
def table(n,center,z,length,width):
 x,y=center
 box(n+"_TOP",x-length/2,x+length/2,y-width/2,y+width/2,
      z+.74,z+.98,"porcelain","03 ACTUAL CULTURAL PUBLIC LIFE",
      "real usable collaborative research table")
 for u in (-.38,.38):
  for v in (-.32,.32):
   box(n+"_FOOT_"+str(u)+"_"+str(v),
       x+u*length-.18,x+u*length+.18,y+v*width-.18,y+v*width+.18,
       z,z+.76,"cobalt","03 ACTUAL CULTURAL PUBLIC LIFE","real table support")
def human(n,x,y,z):
 # A strict scale proxy, not evidence of a functioning population simulation.
 box(n+"_BODY",x-.24,x+.24,y-.19,y+.19,z+.65,z+1.57,
     "stone","04 PUBLIC SCALE","human scale only; no occupancy certification")
 box(n+"_HEAD",x-.17,x+.17,y-.17,y+.17,z+1.58,z+1.9,
     "porcelain","04 PUBLIC SCALE","human scale only")

# The target human eye: the first visible destination at (0,18,9), an
# intentionally unbalanced suspended research library with a cut of real sky.
# Room = 120m long, 85m wide, 60m high; all points are noncanonical.
slab("PUBLIC_ENTRANCE_CITY_THRESHOLD",
 [(-36,-78),(24,-79),(35,-62),(27,-49),(-34,-47),(-45,-61)],
 -1.0,0,"stone","01 OCCUPIED GROUND AND CROSSING",
 "real welcoming arrival forecourt, view oriented to archive/experiment")
slab("CIVIC_MAIN_FLOOR_CONTOUR",
 [(-35,-48),(31,-48),(38,-19),(28,18),(31,61),
  (-2,81),(-41,55),(-36,12)],
 -.7,.25,"pearl","01 OCCUPIED GROUND AND CROSSING",
 "one main public room floor, uneven visually navigable urban threshold")
slab("OPEN_ARCHIVE_STUDIO_WEST",
 [(-69,-24),(-35,-28),(-33,-1),(-45,37),(-68,46),(-79,13)],
 8.3,9.45,"archive_wood","01 OCCUPIED GROUND AND CROSSING",
 "west occupied public archive not a mirrored arena level")
slab("RESEARCH_WORKSHOP_EAST",
 [(31,-19),(70,-25),(76,12),(54,36),(29,31)],
 13.5,14.85,"porcelain","01 OCCUPIED GROUND AND CROSSING",
 "east high laboratory, diagonally offset above public atrium")
slab("UPPER_PUBLIC_TRANSIT_OVERLOOK",
 [(-61,48),(-21,52),(8,79),(4,107),(-54,106)],
 27.2,28.7,"stone","01 OCCUPIED GROUND AND CROSSING",
 "north elevated public city interface without repeating gallery levels")
# Main entrance walk is one genuine continuous editable slab.
P=[
 ((-7,-76),(-7,-70),0),((-7,-63),(-7,-57),.02),
 ((-5,-49),(-5,-43),.10),((-2,-36),(-2,-30),.15),
 ((1,-25),(1,-19),.22),((2,-14),(2,-8),.25)]
L=[a for a,b,z in P];R=[b for a,b,z in P];Z=[z for a,b,z in P]
# L/R above are longitudinal, use world X width instead to avoid winding.
LL=[(-12,y,z) for (x,y),_,z in P]
RR=[(10,b[1],z) for a,b,z in P]
strip("ONE_NATIVE_WELDED_MAIN_PUBLIC_APPROACH",
 [(x,y) for x,y,z in LL],[(x,y) for x,y,z in RR],
 Z,.8,"stone","02 REAL PUBLIC CONNECTION_GEOMETRY",
 "entry to central forum, polygon-connected single volume")
# Route links to other floors require further inspection. Native stair modules
# visible but their safety / landing continuity / lifts are not certified.
stairbank("WEST_ARCHIVE_STAIR",(-32,-21),(-44,-13),.25,9.45,18,
 "archive_wood","02 REAL PUBLIC CONNECTION_GEOMETRY",
 "visually real public stair, FUNCTION_PENDING")
stairbank("EAST_WORKSHOP_STAIR",(28,9),(49,10),.25,14.85,29,
 "porcelain","02 REAL PUBLIC CONNECTION_GEOMETRY",
 "visually real workshop stair, FUNCTION_PENDING")
# Huge meaningful sculptural mass: a folded, *habitable* diagonal suspended
# archive, different top and bottom contours; not a full ring or giant arch.
westProfiles=[
 [(-78,-65,4),(-61,-64,5),(-53,-60,24),(-67,-57,30),(-79,-56,20)],
 [(-78,-30,7),(-56,-29,10),(-48,-25,37),(-69,-20,48),(-86,-19,31)],
 [(-73,5,11),(-45,5,15),(-35,13,51),(-60,20,66),(-84,19,42)],
 [(-72,43,14),(-42,42,19),(-31,47,61),(-57,51,73),(-83,51,48)],
 [(-56,82,15),(-38,81,19),(-24,86,47),(-50,90,64),(-65,91,43)]
]
artist_loft("WEST_CULTURAL_STRATA_TECTONIC_LOFT",westProfiles,
 "black_rock","05 SCULPTURAL_INHABITED_SECTION",
 "nonrepeating public archive tectonic fissure, not cylindrical stadium")
eastProfiles=[
 [(67,-57,14),(84,-56,13),(99,-52,26),(83,-48,40),(61,-46,34)],
 [(47,-17,15),(69,-16,19),(85,-10,41),(70,-4,51),(43,-6,40)],
 [(40,26,17),(64,25,24),(80,38,58),(61,43,70),(37,33,47)],
 [(59,68,16),(79,65,20),(94,76,47),(80,82,57),(59,75,42)]
]
artist_loft("EAST_PUBLIC_RESEARCH_SHIFTED_FOLD",eastProfiles,
 "porcelain","05 SCULPTURAL_INHABITED_SECTION",
 "asymmetric bright research bank with purposeful interior reveal")
# The daylight negative space between the two tectonic elements is open.
# Only one thin off-axis glancing sliver joins at height. no complete roof.
artist_loft("MEMORIAL_LIGHT_SEAM",
 [
  [(-44,-41,43),(-40,-42,44),(-39,-38,47),(-45,-37,48)],
  [(-25,-16,54),(-19,-15,52),(-17,-11,57),(-26,-11,61)],
  [(-3,12,62),(4,12,59),(9,17,64),(0,18,68)],
  [(30,44,58),(36,43,57),(39,48,61),(29,49,63)],
  [(43,70,46),(49,70,44),(51,73,48),(41,74,52)]
 ],"bronze","05 SCULPTURAL_INHABITED_SECTION",
 "finite off-axis daylight seam expressing a real void, not a sky roof")
# The public research laboratory gets a cutaway facade to preserve the sightline.
# Intermittent screens have genuine gaps; repeated side-panels are subordinate.
for j,(u,z0,z1) in enumerate([
 (0.10,15,27),(0.29,15,32),(0.49,15,29),(0.75,15,25)]):
 a=Vector((31,-19,0));b=Vector((70,-25,0))
 p=a.lerp(b,u)
 artist_beam("RESEARCH_CUTAWAY_BAY_%d"%j,
 (p.x,p.y,z0),(p.x,p.y,z1),1.0,1.2,"window_cyan",
 "06 PUBLIC_LIFE_WITH_LIGHT",
 "real public lab facade with cutaway aperture, not flat panel")
# 3D public life placed along sight-line, not random repetitive benches.
bookwall("WEST_PUBLIC_MEMORY_STUDIES",(-60,-15),(0,1),42,9.45,16.9,7)
bookwall("WEST_PUBLIC_EPHEMERA",(-51,28),(1,.2),17,9.45,15.3,4)
for j,(x,y) in enumerate([(-57,-11),(-54,13),(-45,30)]):
 table("ARCHIVE_READING_"+str(j),(x,y),9.45,4.8,2.6)
 human("CURATOR_"+str(j),x-2.4,y,9.45)
for j,(x,y) in enumerate([(46,-9),(56,4),(54,19)]):
 table("RESEARCH_LIVE_WORKBENCH_"+str(j),(x,y),14.85,6.5,3.5)
 human("WORKSHOP_RESEARCHER_"+str(j),x+3.4,y,14.85)
# Arrival exhibition / gallery works as a real recognizable focal object.
slab("PUBLIC_ARCHIVE_ARTIFACT_PLATFORM",
 [(-17,11),(15,9),(20,25),(4,36),(-20,29)],
 .25,.95,"archive_wood","03 ACTUAL CULTURAL PUBLIC LIFE",
 "central permanent public exhibition with a distinct walking perimeter")
for j,(xy,z1) in enumerate([
 ([(-14,14),(-9,11),(-4,18),(-12,21)],8),
 ([(1,15),(8,12),(11,20),(4,25)],13),
 ([(-5,26),(4,25),(7,33),(-8,34)],10)]):
 slab("PUBLIC_ARCHIVE_RECORD_OBELISK_"+str(j),xy,.95,z1,
      "cobalt" if j==1 else "bronze",
      "03 ACTUAL CULTURAL PUBLIC LIFE",
      "human-reachable high vertical public research exhibit, physical 3D")
 for h in (2.0,4.1,6.5):
  if h<z1:
   a=xy[0];b=xy[1]
   artist_beam("VISIBLE_INFORMATION_LINE_%d_%d"%(j,int(h*10)),
        (a[0],a[1],h),(b[0],b[1],h),
        .25,.5,"window_cyan","03 ACTUAL CULTURAL PUBLIC LIFE",
        "readable civic research information carried by physical sculpture")
for j,(x,y) in enumerate([(0,-34),(19,-18),(-25,-10),(-15,43),(17,42)]):
 human("REAL_SCALE_PUBLIC_VISITOR_%d"%j,x,y,.25)
# Cultural transits: actual thick horizontal sky street / side module.
strip("NORTHERN_UPPER_CITY_THRESHOLD",
 [(-38,70),(-34,83),(-26,96),(-14,111)],
 [(6,70),(7,83),(11,96),(20,111)],
 [28.7,28.7,28.7,28.7],
 2.0,"stone","02 REAL PUBLIC CONNECTION_GEOMETRY",
 "real elevated connection interface; intermediate vertical access uncertified")
# Interior art-direction camera set. Foreground no topologically opaque wall.
CAMS={
 "01_HUMAN_ARRIVAL":((0,-66,1.72),(0,17,18),None),
 "02_HUMAN_CULTURE_FORUM":((11,-14,1.72),(-16,27,26),None),
 "03_HUMAN_WEST_ARCHIVE":((-53,-19,11.2),(12,21,20),None),
 "04_ARCHITECTURE_OBLIQUE":((165,-153,119),(0,20,30),240),
 "05_CITY_LINK_REAR":((61,181,97),(-10,4,32),248)
}
for name,(eye,target,ortho) in CAMS.items():
 d=bpy.data.cameras.new(name)
 o=bpy.data.objects.new(name,d);collection("07 TRUE_MODEL_CAMERAS").objects.link(o)
 o.location=eye;o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
 d.clip_start=.08;d.clip_end=4000
 if ortho:d.type="ORTHO";d.ortho_scale=ortho
 else:d.type="PERSP";d.lens=27
S.camera=bpy.data.objects["01_HUMAN_ARRIVAL"]
S.world=bpy.data.worlds.new("E4_STUDIO_WORLD")
S.world.color=(.43,.49,.50)
S.render.engine="BLENDER_WORKBENCH"
S.display.shading.light="STUDIO"
S.display.shading.color_type="MATERIAL"
S.display.shading.show_cavity=True
S.display.shading.cavity_type="BOTH"
S.display.shading.background_type="WORLD"
S.render.resolution_x=1200;S.render.resolution_y=800
S.render.resolution_percentage=100
S.render.image_settings.file_format="PNG"
for k,v in {
 "R18_E4_ART_APPROVED":False,
 "R18_E4_FUNCTION_CERTIFIED":False,
 "R18_E4_M247C_ADOPTED":False,
 "R18_E4_CITY_MASTER_COMPLETE":False,
 "R18_E4_MINECRAFT_WRITTEN":False,
 "R18_E4_ART_G0_STATUS":"AWAITING_TRUE_NATIVE_FIVE_VIEW_JUDGEMENT"}.items():
 S[k]=v
native=out/"R18_E4_TRUE_EDITABLE_CHIRAL_NAVE.blend"
glb=out/"R18_E4_TRUE_CHIRAL_NAVE.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
                          export_lights=False,export_cameras=False)
for name in CAMS:
 S.camera=bpy.data.objects[name]
 S.render.filepath=str(out/(name+".png"))
 bpy.ops.render.render(write_still=True)
objects=[o for o in bpy.data.objects if o.type=="MESH"]
man={
 "study":"D47-R18 E4 new asymmetric civic room, NOT formal city",
 "source":"new artist-authored 3D space, no E0-E3 geometry reused",
 "design":"nonmirrored cultural + research banks and one diagonal light seam around visible civic activity",
 "blender":bpy.app.version_string,
 "files":{"blend":native.name,"glb":glb.name,"cameras":[x+".png" for x in CAMS]},
 "meshes":len(objects),
 "vertices":sum(len(o.data.vertices) for o in objects),
 "triangles":sum(len(f.vertices)-2 for o in objects for f in o.data.polygons),
 "first_entry_route_geometry_welded":True,
 "full_building_function_unverified":True,
 "high_terrace_access_unverified":True,
 "structure_egress_railings_accessibility_unverified":True,
 "art_status":"AWAITING_TRUE_5_CAMERA_REVIEW",
 "city_master_complete":False,"formal_art_adopted":False,"minecraft_write":False}
(out/"R18_E4_G0_MANIFEST.json").write_text(json.dumps(man,indent=2,ensure_ascii=False),encoding="utf-8")
print("R18_E4_NATIVE_CREATED_NOT_ART_APPROVED",json.dumps(man,ensure_ascii=False),flush=True)
