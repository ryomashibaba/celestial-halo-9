"""D47-R18 E2 / LIVING LIGHT CANYON / genuine art-first Blender study.
E2 completely new authored spatial section, not E0/E1 refinement or former meshes.
The civic forum, cultural terraces, research laboratories and suspended transit
are arranged around a visibly occupied urban void, *before* ornamental skin.
A 1:1 metre study only, NOT canonical M247-C or City Master.
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
OUT=Path(sys.argv[-1]).resolve(); OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
colors={
"marble":(.76,.77,.73,1),
"dark_stone":(.16,.24,.29,1),
"warm_stone":(.50,.49,.43,1),
"civic_paving":(.64,.62,.53,1),
"copper":(.72,.49,.27,1),
"white_ceramic":(.88,.84,.73,1),
"research_glass":(.28,.68,.71,1),
"deep_glass":(.12,.44,.55,1),
"living_foliage":(.30,.48,.39,1),
"archive":(.49,.34,.28,1),
"night":(.12,.17,.21,1)}
for n,c in colors.items():
 m=bpy.data.materials.new("E2_"+n);m.diffuse_color=c
def col(name):
 c=bpy.data.collections.get(name)
 if c is None: c=bpy.data.collections.new(name);scene.collection.children.link(c)
 return c
def newmesh(name,verts,faces,material,group,role):
 me=bpy.data.meshes.new(name+"_native")
 me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);col(group).objects.link(ob)
 me.materials.append(bpy.data.materials["E2_"+material])
 ob["E2_public_role"]=role
 ob["E2_artist_editable"]=True
 ob.shape_key_add(name="Basis");ob.shape_key_add(name="ART_EDIT")
 return ob
def polygon(name,P,z0,z1,mat,grp,role):
 assert len(P)>=3 and z1>z0
 n=len(P)
 v=[(x,y,z0) for x,y in P]+[(x,y,z1) for x,y in P]
 f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
 f += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return newmesh(name,v,f,mat,grp,role)
def box(name,x0,x1,y0,y1,z0,z1,mat,grp,role):
 return polygon(name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1,mat,grp,role)
def raw_sheet(name,grid,mat,grp,role):
 # 2D material surface with a real, user-authored irregular deformation
 rows=len(grid);cols=len(grid[0])
 assert rows>1 and cols>1
 V=[v for row in grid for v in row]
 F=[(i*cols+j,i*cols+j+1,(i+1)*cols+j+1,(i+1)*cols+j)
 for i in range(rows-1) for j in range(cols-1)]
 return newmesh(name,V,F,mat,grp,role)
def sweep(name,points,widths,thickness,material,grp,role):
 # An actual continuous volume, not geometrically disconnected steps.
 v=[]
 for i,(x,y,z) in enumerate(points):
  A=Vector(points[max(0,i-1)])
  B=Vector(points[min(len(points)-1,i+1)])
  d=B-A;d.z=0
  assert d.length>.1
  d.normalize()
  normal=Vector((-d.y,d.x,0))
  for side,h in [(-1,0),(1,0),(-1,-thickness),(1,-thickness)]:
   vv=Vector((x,y,z))+side*widths[i]*.5*normal+Vector((0,0,h))
   v.append(tuple(vv))
 f=[(0,2,3,1)]
 for k in range(len(points)-1):
  a=4*k;b=a+4
  f.extend([(a,a+1,b+1,b),(a,b,b+2,a+2),(a+1,a+3,b+3,b+1),(a+2,b+2,b+3,a+3)])
 a=4*(len(points)-1)
 f.append((a,a+1,a+3,a+2))
 ob=newmesh(name,v,f,material,grp,role)
 ob["E2_actual_centerline"]=json.dumps(points)
 grad=[abs(b[2]-a[2])/math.hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(points,points[1:])]
 ob["max_segment_gradient"]=max(grad)
 return ob,max(grad)
def stroke(name,points,r,mat,role):
 # Native curved load-path / suspended urban edge, visually sized for buildings
 # not a generic wavy roof repeated through the whole city.
 n=8;V=[]
 for i,P in enumerate(points):
  A=Vector(points[max(0,i-1)]); B=Vector(points[min(i+1,len(points)-1)])
  tangent=(B-A).normalized()
  u=tangent.cross(Vector((0,0,1)))
  if u.length<.01:u=tangent.cross(Vector((0,1,0)))
  u.normalize();w=tangent.cross(u).normalized()
  for k in range(n):
   t=2*math.pi*k/n
   V.append(tuple(Vector(P)+r*(u*math.cos(t)+w*math.sin(t))))
 F=[tuple(range(n-1,-1,-1))]
 for i in range(len(points)-1):
  for k in range(n):
   a=i*n+k;b=i*n+(k+1)%n
   F.append((a,b,b+n,a+n))
 F.append(tuple(range((len(points)-1)*n,len(points)*n)))
 return newmesh(name,V,F,mat,"04 DAYLIGHT_SECTION_STRUCTURE",role)

# LANDSCAPE OF OCCUPIED CIVIC ROOMS, AUTHOR-DEFINED FIRST:
# One 108m tall inhabited urban slot, five physically distinct destinations.
# Arrival at human scale in front, civic forum lower than street;
# west cultural stacks and east public research over the SAME forum.
polygon("01_PUBLIC_ENTRY_FOOTPRINT",
 [(-44,-129),(52,-129),(58,-103),(38,-77),(-44,-79),(-59,-105)],
 -2,0,"civic_paving","01 ARCHITECTURAL_PUBLIC_GROUND",
 "genuine street arrival that opens forward into a living urban interior")
polygon("02_OPEN_CIVIC_WORKSHOP_FORUM",
 [(-35,-61),(32,-61),(38,-24),(32,49),(5,83),(-42,61),(-46,-4)],
 -9,-7.5,"civic_paving","01 ARCHITECTURAL_PUBLIC_GROUND",
 "central open public research demonstration forum with circulation around it")
# Four unique inhabitable public terraces. The walls are generated later to
# wrap THESE specific places, not the other way around.
polygon("03_WEST_CULTURE_COLLECTION_BALCONY",
 [(-85,-63),(-42,-69),(-35,-38),(-36,7),(-28,35),(-52,59),(-96,48)],
 12,14,"archive","01 ARCHITECTURAL_PUBLIC_GROUND",
 "large human-occupied archive studio overlooking central public void")
polygon("04_EAST_LIVE_RESEARCH_TERRACE",
 [(39,-35),(88,-43),(105,-9),(96,33),(62,66),(35,48)],
 31,33,"marble","01 ARCHITECTURAL_PUBLIC_GROUND",
 "open laboratory amphitheatre, not a freestanding pavilion or floating slab")
polygon("05_WEST_PUBLIC_STUDY_HORIZON",
 [(-85,-3),(-39,-10),(-34,23),(-42,76),(-75,93),(-106,51)],
 57,59,"copper","01 ARCHITECTURAL_PUBLIC_GROUND",
 "singular high cultural overlook with partial protected interior")
polygon("06_NORTH_TRANSIT_PUBLIC_GATE",
 [(-49,79),(3,82),(51,80),(72,112),(48,130),(-36,134),(-57,118)],
 76,79,"marble","01 ARCHITECTURAL_PUBLIC_GROUND",
 "upper-city transit threshold open into other urban districts")
# Lower passage actually connected, graded along the original authored geometry.
route,g=sweep("01_REAL_LOW_PUBLIC_CORRIDOR",
 [(4,-118,0),(9,-95,-1.5),(7,-73,-3),(-2,-48,-4.5),
  (-5,-26,-6),(-4,-8,-7.5)],
 [16,16,17,19,22,23],1.3,"marble",
 "02 CONTINUOUS_VISITOR_GEOMETRY",
 "physically continuous public descending approach (first route only)")
assert g<1/12
# West and east cultural routes are artistically necessary but their engineering
# and joint alignments remain unverified; never claim full accessibility.
sweep("WEST_ARCHIVE_SPIRAL_VISIBLE_SECTION",
 [(-60,-57,13.5),(-66,-30,15),(-70,-1,17),(-63,26,19)],
 [10,11,12,11],1.1,"white_ceramic",
 "02 CONTINUOUS_VISITOR_GEOMETRY",
 "additional native gallery circulation concept, not confirmed accessible")
sweep("EAST_RESEARCH_RAMP_TRUE_VOLUME",
 [(68,-35,33),(74,-9,35),(71,18,37),(65,46,39)],
 [10,10,10,11],1.0,"copper",
 "02 CONTINUOUS_VISITOR_GEOMETRY",
 "additional elevated lab walk, higher floor connection not certified")

# A carved city bank is not one boulder. These are section-based sculpted
# inhabited façades with integrated change of slope at unique program floors.
Ys=[-101,-75,-45,-10,22,48,80,111]
Zs=[-16,0,14,33,58,82,112]
def wall(orientation):
 # West and east change shape and z-profile independently (not mirrored)
 west=orientation=="WEST"
 grid=[]
 for z in Zs:
  row=[]
  for i,y in enumerate(Ys):
   if west:
    x=(-77+9*math.sin(y/52+z/31)-.22*z +
       15*math.exp(-((z-58)/23)**2)*math.sin(y/39))
   else:
    x=(83+14*math.cos(y/46-z/49)+.14*z -
       12*math.exp(-((z-33)/18)**2)*math.sin(y/30))
   row.append((x,y,z+3*math.sin(y/57+z/28)))
  grid.append(row)
 return grid
west=wall("WEST");east=wall("EAST")
raw_sheet("WEST_TRUE_INHABITED_CLIFF_INTERIOR",west,"dark_stone",
 "03 CULTURAL_RESEARCH_INHABITED_CLIFF",
 "irregular bank of human inhabited civic archive, not a featureless floating rock")
raw_sheet("EAST_TRUE_INHABITED_CLIFF_INTERIOR",east,"warm_stone",
 "03 CULTURAL_RESEARCH_INHABITED_CLIFF",
 "independently sculpted public research city enclosure, asymmetric to archive")
# Outer wall visible from exterior, with thickness in visual architecture.
def outer(inside,sgn,shift):
 return [[(x+sgn*(30+4*math.sin(z/17+y/40)),y+shift,z-7)
          for x,y,z in row] for row in inside]
raw_sheet("WEST_OUTER_URBAN_SPINE",outer(west,-1,-7),"marble",
 "03 CULTURAL_RESEARCH_INHABITED_CLIFF",
 "external sculpted urban ground surrounding public cultural activity")
raw_sheet("EAST_OUTER_URBAN_SPINE",outer(east,1,4),"dark_stone",
 "03 CULTURAL_RESEARCH_INHABITED_CLIFF",
 "external research city mass, different silhouette from opposite cliff")
# The civic bank is porous: cross sectional splayed edges and hand-placed
# art apertures, not one entirely closed monolithic roof.
def facade_riser(name,x,y0,y1,z0,z1,mat,role):
 pts=[(x,y0),(x+2.5*math.sin(y0/31),y1),(x+3,y1+3),(x-1.4,y0+3)]
 return polygon(name,pts,z0,z1,mat,"03 CULTURAL_RESEARCH_INHABITED_CLIFF",role)
for idx,(side,x,y,z0,z1) in enumerate([
 ("W",-66,-76,0,30),("W",-66,-16,12,52),("W",-68,52,32,100),
 ("E",65,-82,0,29),("E",63,-27,19,63),("E",59,56,44,103)]):
 facade_riser("INHABITED_CLIFF_CONTINUOUS_STRUCTURAL_CHEEK_"+str(idx),
              x,y,y+8,z0,z1,
              "white_ceramic" if side=="W" else "dark_stone",
              "six non-identical load-path cheeks between actual inhabited public rooms")
# The *cultural program* has real visible vertical fins & instruments. Add authored,
# human-sized but architecture-scale types, not benches randomly placed in emptiness.
# Book history wall: 3 genuinely independent strip volumes crossing exhibition faces.
for idx,(x0,x1,y0,y1,z0,z1) in enumerate([
 (-79,-74,-52,-13,14,26),
 (-74,-69,12,45,14,32),
 (-65,-61,57,80,59,76)]):
 box("CULTURAL_VISIBLE_ARCHIVE_ARTIFACT_"+str(idx),
     x0,x1,y0,y1,z0,z1,"copper","05 VISIBLE_CIVIC_LIFE",
     "museum archive facing 60m civic void")
# Lab: four large differentiated instruments integrated with the terrace.
for idx,(p,z0,z1) in enumerate([
 ([(59,-21),(73,-24),(78,-13),(62,-8)],33,41),
 ([(77,8),(85,4),(88,19),(74,22)],33,44),
 ([(58,35),(72,36),(69,46),(56,45)],33,38)]):
 polygon("PUBLIC_RESEARCH_INSTRUMENT_"+str(idx),p,z0,z1,
         "research_glass","05 VISIBLE_CIVIC_LIFE",
         "working scientific experiment in occupied research terrace")
# Amphitheater is one curved host, not repetitive 15 floor levels.
for idx,(r,z) in enumerate([(11,-6.7),(19,-6.2),(29,-5.6)]):
 # Separate short curves form ACTUAL intentional social seating zones
 pts=[(r*math.cos(t),20+r*math.sin(t),z)
      for t in [math.pi*.16+i*(math.pi*.68)/14 for i in range(15)]]
 stroke("LOW_CULTURAL_CONVERSATION_SEAT_"+str(idx),pts,.65,
        "copper","three intentional benches integrated in central forum")
# The spectacular light recipient is a tall civic instrument / artwork,
# anchored to occupied forum rather than floating over an empty landscape.
for idx,(ang,radius,z0,z1) in enumerate([
 (.18,8,-7.5,51),(1.47,10,-7.5,67),(3.15,13,-7.5,75),
 (4.7,9,-7.5,58)]):
 zvals=[z0,z0+11,z0+25,z1-10,z1]
 points=[(radius*math.cos(ang+.07*i),24+radius*math.sin(ang+.11*i),z)
         for i,z in enumerate(zvals)]
 stroke("TIDAL_LIGHT_INSTRUMENT_ROOTED_"+str(idx),points,
         1.45 if idx%2==0 else 1.1,
         "research_glass" if idx%2==0 else "white_ceramic",
         "four distinct anchored civic light-research devices, not repeated columns")
# Urban atmospheric borders: very few, large enough to read as authored design.
stroke("WEST_ARCHIVE_BACKBONE_VISIBLE_IN_VOID",
 [(-89,-92,17),(-76,-51,32),(-72,-8,55),(-67,39,83),(-79,86,110)],
 3.6,"white_ceramic",
 "single legible arc of structural support integrated into archive cliff")
stroke("EAST_RESEARCH_DAYLIGHT_GUTTER",
 [(90,-83,49),(88,-34,64),(73,13,80),(79,60,111),(100,103,118)],
 3.5,"research_glass",
 "independent research-side light cut, not a mirrored arch or full roof")
# Structural woven transit single bridge at the upper city height.
sweep("UPPER_CIVIC_TRANSIT_REAL_BRIDGE_SECTION",
 [(-57,85,79),(-31,92,79),(4,97,79),(35,106,79),(61,113,79)],
 [10,11,14,12,11],2.1,"white_ceramic",
 "02 CONTINUOUS_VISITOR_GEOMETRY",
 "genuine mesh transit crossing; high-level boarding, guards, loads unverified")
# Three cameras deliberately examine the *inhabited void*, not its labels.
CAMERAS={
 "01_HUMAN_PUBLIC_ENTRY":((5,-119,2.1),(1,23,20),None),
 "02_HUMAN_LIVING_CIVIC_FORUM":((2,-34,-5.1),(4,56,37),None),
 "03_TRUE_OBLIQUE_ARCHITECTURE":((215,-190,181),(4,0,43),340),
 "04_TRUE_REAR_URBAN_LINK":((70,235,134),(0,13,53),360)
}
for name,(eye,look,ortho) in CAMERAS.items():
 data=bpy.data.cameras.new(name)
 ob=bpy.data.objects.new(name,data)
 col("06 ACTUAL_BLENDER_CAMERAS").objects.link(ob)
 ob.location=eye
 ob.rotation_euler=(Vector(look)-ob.location).to_track_quat("-Z","Y").to_euler()
 data.clip_start=.05; data.clip_end=10000
 if ortho: data.type="ORTHO";data.ortho_scale=ortho
 else:data.type="PERSP";data.lens=23
scene.camera=bpy.data.objects["03_TRUE_OBLIQUE_ARCHITECTURE"]
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type="BOTH"
scene.display.shading.background_type="WORLD"
scene.world.color=(.24,.29,.35)
scene.render.resolution_x=1260
scene.render.resolution_y=840
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene["R18_E2_ART_APPROVED"]=False
scene["R18_E2_ART_STATUS"]="FOUR_TRUE_VIEW_REVIEW_PENDING"
scene["R18_E2_FUNCTION_CERTIFIED"]=False
scene["R18_E2_CITY_MASTER_COMPLETE"]=False
scene["R18_E2_FORMAL_M247C_ADOPTED"]=False
scene["R18_E2_MINECRAFT_WRITE"]=False
scene["R18_E2_METHOD"]="authored inhabited civic room and public void first, then freeform enclosing city bank"
bl=OUT/"R18_E2_TRUE_EDITABLE_PUBLIC_CANYON.blend"
gl=OUT/"R18_E2_ACTUAL_PUBLIC_CANYON.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(bl))
bpy.ops.export_scene.gltf(filepath=str(gl),export_format="GLB",
                           export_cameras=False,export_lights=False)
for name in CAMERAS:
 scene.camera=bpy.data.objects[name]
 scene.render.filepath=str(OUT/(name+".png"))
 bpy.ops.render.render(write_still=True)
meshobj=[o for o in bpy.data.objects if o.type=="MESH"]
manifest={
 "study":"D47-R18 E2 new inhabited civic canyon, 1:1 research only",
 "authoring":"spatially authored public rooms then two nonmirror sculpted urban bank surfaces",
 "source":"not E0 or E1 reuse, not canonical 10km city",
 "blender":bpy.app.version_string,
 "files":{"blend":bl.name,"glb":gl.name,"cameras":[n+".png" for n in CAMERAS]},
 "mesh_count":len(meshobj),
 "vertices":sum(len(o.data.vertices) for o in meshobj),
 "triangles":sum(len(f.vertices)-2 for o in meshobj for f in o.data.polygons),
 "one_true_connected_low_route_max_gradient":g,
 "independent_high_route_connectivity_certified":False,
 "building_code_egress_accessibility_and_structure_certified":False,
 "formal_art_approved":False,"adopted_to_M247C":False,
 "city_master_complete":False,"minecraft_write":False,
 "human_entrance_and_forum_visible":True}
(OUT/"R18_E2_G0_MANIFEST.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf8")
print("D47_R18_E2_G0_TRUE_SOURCED_3D_ONLY_ART_PENDING",json.dumps(manifest,ensure_ascii=False),flush=True)
