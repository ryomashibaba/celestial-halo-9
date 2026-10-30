"""HALO-9 D47 R18 E6 G0: inhabited oblique public fissure.
New noncanonical art study, not an E5 repair or E4 mesh import.
Specific goal: a unique architectural view from a human-scale library,
research exchange forum, and elevated civic transit.
An architecturally significant WEST_INHABITED_FOLD is intended for a
SUBSEQUENT local edit after inspecting ACTUAL four real Blender renderings.
Only Blender-native editable geometry; no Minecraft writes.
"""
from pathlib import Path
from mathutils import Vector
import math,json,sys,bpy
OUT=Path(sys.argv[-1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
PALETTE={
 "ivory":(.80,.80,.74,1),"pearl":(.92,.87,.76,1),
 "dark":(.14,.22,.27,1),"bronze":(.65,.44,.25,1),
 "research":(.25,.59,.61,1),"glass":(.52,.79,.78,1),
 "floor":(.45,.49,.46,1),"wood":(.50,.33,.23,1),
 "green":(.27,.49,.37,1),"warm":(.69,.66,.55,1)}
for k,c in PALETTE.items():
 m=bpy.data.materials.new("E6_"+k);m.diffuse_color=c

def coll(n):
 c=bpy.data.collections.get(n)
 if not c:c=bpy.data.collections.new(n);sc.collection.children.link(c)
 return c
def mk(n,V,F,material,collection,role):
 m=bpy.data.meshes.new(n+"_3D");m.from_pydata(V,[],F);m.update()
 o=bpy.data.objects.new(n,m);coll(collection).objects.link(o)
 m.materials.append(bpy.data.materials["E6_"+material])
 o["E6_public_role"]=role
 o["E6_formal_adoption"]=False
 o.shape_key_add(name="Basis")
 o.shape_key_add(name="ArtistEdit")
 return o
def slab(n,P,z0,z1,material,collection,role):
 assert len(P)>=3 and z1>z0
 N=len(P)
 V=[(x,y,z0) for x,y in P]+[(x,y,z1) for x,y in P]
 F=[tuple(range(N-1,-1,-1)),tuple(range(N,N*2))]
 F.extend((i,(i+1)%N,N+(i+1)%N,N+i) for i in range(N))
 return mk(n,V,F,material,collection,role)
def box(n,x0,x1,y0,y1,z0,z1,mat,collection,role):
 return slab(n,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1,mat,collection,role)
def loft(n,rings,material,group,role):
 assert len(rings)>=2 and all(len(x)==len(rings[0]) for x in rings)
 N=len(rings[0])
 V=[p for ring in rings for p in ring]
 F=[tuple(range(N-1,-1,-1))]
 for j in range(len(rings)-1):
  for i in range(N):
   a=j*N+i; b=j*N+(i+1)%N
   F.append((a,b,b+N,a+N))
 F.append(tuple(range((len(rings)-1)*N,len(rings)*N)))
 return mk(n,V,F,material,group,role)
def beam(n,A,B,w,d,mat,group,role):
 a=Vector(A);b=Vector(B);T=(b-a).normalized()
 U=T.cross(Vector((0,0,1)))
 if U.length<1e-6:U=T.cross(Vector((0,1,0)))
 U.normalize();V=T.cross(U).normalized()
 verts=[]
 for p in (a,b):
  for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]:
   verts.append(tuple(p+U*u*w/2+V*v*d/2))
 faces=[(3,2,1,0),(4,5,6,7)]
 faces += [(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
 return mk(n,verts,faces,mat,group,role)

# E6 architectural premise: diagonally shifted HUMAN-SCALE cultural rooms,
# cut across by a large inhabited civic fold, not a U-shaped arena.
slab("CITY_ARRIVAL_STREET",
 [(-34,-84),(30,-84),(31,-57),(23,-44),(-27,-45),(-39,-60)],
 -1.2,0,"floor","01 REAL PUBLIC ACTIVITY",
 "urban arrival threshold with full floor depth")
slab("CENTRAL_CIVIC_COMMONS",
 [(-28,-47),(26,-47),(38,-20),(28,28),(4,51),(-33,34),(-40,-5)],
 -.7,.15,"ivory","01 REAL PUBLIC ACTIVITY",
 "public research cultural forum with full walkable-area geometry")
slab("WEST_PUBLIC_ARCHIVE",
 [(-60,-44),(-29,-43),(-27,-15),(-32,15),(-56,23),(-73,3)],
 6.6,7.8,"wood","01 REAL PUBLIC ACTIVITY",
 "actual elevated archives and personal study zones")
slab("EAST_RESEARCH_OBSERVATORY",
 [(27,-27),(53,-31),(67,2),(57,34),(31,28),(23,4)],
 13.2,14.6,"pearl","01 REAL PUBLIC ACTIVITY",
 "offset public laboratory with varied real stations")
slab("NORTH_CIVIC_TRANSIT_BAY",
 [(-36,40),(7,44),(31,68),(24,92),(-29,89),(-44,69)],
 25.0,26.6,"warm","01 REAL PUBLIC ACTIVITY",
 "future city transit platform, station function NOT yet certified")
# Real public function: exhibition-atrium, readable research equipment, archive library.
slab("CENTRAL_EARTH_ATLAS_INTERACTIVE",
 [(-16,-3),(14,-5),(20,16),(3,26),(-19,17)],
 .15,1.25,"bronze","02 CIVIC PROGRAM",
 "large walk-around environmental atlas in a central public interior")
for i,(x,y,z) in enumerate([(-11,4,8),(-2,6,14),(10,5,11)]):
 box("PHYSICAL_ATLAS_DATA_COLUMN_"+str(i),x-1.8,x+1.8,y-1.4,y+1.4,
     1.25,z,"research","02 CIVIC PROGRAM","public legible vertical data display")
 for a in [3.1,5.7,8.0]:
  if a<z:
   box("PUBLIC_RESEARCH_GLOW_REFERENCE_"+str(i)+"_"+str(a),
       x-1.7,x+1.7,y-1.55,y-1.4,a,a+.35,"glass",
       "02 CIVIC PROGRAM","physical instrument readout, not a label")
for i,(x,y) in enumerate([(-56,-25),(-55,-12),(-54,1),(-48,12)]):
 box("ARCHIVE_PUBLIC_BAY_"+str(i),x-2.7,x+2.7,y-1.5,y+1.5,7.8,15.2,
     "dark","02 CIVIC PROGRAM","real publicly readable archive storage")
 for h in [9.2,11.6,13.7]:
  box("EXHIBIT_BOOK_ROW_"+str(i)+"_"+str(h),x-3,x+3,y-1.7,y+1.7,
      h,h+.3,"bronze","02 CIVIC PROGRAM","visible culture records and books")
for i,(x,y) in enumerate([(38,-18),(46,-1),(48,17)]):
 box("LAB_CONFERENCE_TABLE_"+str(i),x-4.3,x+4.3,y-2.1,y+2.1,
     15.35,15.9,"ivory","02 CIVIC PROGRAM","actual open-air research collaboration desk")
 for dx in [-3.2,3.2]:
  beam("REAL_LAB_SUPPORT_"+str(i)+"_"+str(dx),
       (x+dx,y,14.6),(x+dx,y,15.6),.44,.44,
       "dark","02 CIVIC PROGRAM","small but physical desk support")
# First monumental part: a continuous editable fold whose geometry is
# intentionally articulated across 7 independent y-sections and 6 profile
# points. E6 G1 must edit THIS SAME BLEND object, not regenerate its source.
WEST=[
 [(-81,-58,0),(-70,-58,1),(-62,-58,19),(-58,-58,31),(-74,-58,39),(-86,-58,26)],
 [(-80,-33,0),(-69,-33,2),(-58,-33,25),(-49,-33,42),(-70,-33,49),(-87,-33,31)],
 [(-77,-9,0),(-62,-9,2),(-48,-9,31),(-42,-9,49),(-65,-9,58),(-87,-9,38)],
 [(-74,17,0),(-59,17,3),(-38,17,35),(-35,17,59),(-64,17,66),(-89,17,40)],
 [(-77,39,0),(-56,39,3),(-36,39,38),(-34,39,64),(-64,39,70),(-91,39,47)],
 [(-70,59,0),(-48,59,2),(-33,59,35),(-36,59,59),(-70,59,66),(-87,59,45)],
 [(-58,84,0),(-42,84,2),(-32,84,29),(-38,84,50),(-72,84,55),(-79,84,39)]
]
fold=loft("WEST_INHABITED_FOLD_EDITABLE",WEST,"dark",
     "03 EDITABLE MONUMENTAL SPACE",
     "actual west occupied architectural fold; NEXT stage visual edit target")
fold["E6_ring_vertices"]=6
fold["E6_ring_count"]=7
# East changes direction and scale; not a mirrored duplicate.
EAST=[
 [(39,-66,16),(62,-66,14),(75,-66,25),(78,-66,38),(59,-66,43),(36,-66,31)],
 [(42,-32,16),(69,-32,15),(84,-32,37),(80,-32,56),(55,-32,62),(32,-32,39)],
 [(36,-4,16),(66,-4,17),(89,-4,43),(81,-4,66),(54,-4,73),(28,-4,43)],
 [(33,22,17),(63,22,18),(90,22,44),(84,22,72),(59,22,81),(35,22,45)],
 [(45,53,18),(72,53,19),(102,53,41),(95,53,66),(65,53,73),(44,53,41)],
 [(52,83,16),(78,83,20),(99,83,34),(90,83,51),(62,83,59),(48,83,30)]
]
loft("EAST_RESEARCH_HORIZON",EAST,"pearl","03 EDITABLE MONUMENTAL SPACE",
     "offset luminous housing for public planetary research")
# Suspended finite daylight blade crosses neither wall entirely.
loft("DAYLIGHT_SEAM_NOT_AN_ARCH",[
 [(-45,-48,50),(-38,-48,52),(-36,-48,55),(-48,-48,55)],
 [(-30,-16,61),(-21,-16,60),(-20,-16,64),(-31,-16,66)],
 [(-7,15,70),(2,15,66),(5,15,71),(-8,15,76)],
 [(18,43,72),(27,43,70),(31,43,76),(18,43,77)],
 [(35,66,56),(41,66,53),(46,66,58),(33,66,61)]],
 "bronze","03 EDITABLE MONUMENTAL SPACE",
 "visible off-axis light seam opens central civic forum to the city sky")
# Human-scale camera orientation MUST not be post-hoc changed to fake improvement.
specs={
 "01_HUMAN_ARRIVAL":((0,-72,1.7),(0,7,22),None),
 "02_HUMAN_CULTURAL_ATLAS":((11,-22,1.7),(0,12,24),None),
 "03_WEST_ARCHIVE_VIEW":((-49,-26,9.5),(13,10,23),None),
 "04_CITY_ANGLED":((180,-164,116),(0,10,34),230),
 "05_CITY_REAR":((33,178,104),(-5,11,34),230)}
for name,(eye,target,ortho) in specs.items():
 d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d)
 coll("04 FIXED CAMERAS").objects.link(o)
 o.location=eye;o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
 d.clip_start=.06;d.clip_end=4000
 if ortho:d.type="ORTHO";d.ortho_scale=ortho
 else:d.type="PERSP";d.lens=27
sc.world=bpy.data.worlds.new("E6_GREY_STUDIO_BACKGROUND")
sc.world.color=(.50,.54,.57)
sc.render.engine="BLENDER_WORKBENCH"
sc.display.shading.light="STUDIO"
sc.display.shading.color_type="MATERIAL"
sc.display.shading.show_cavity=True
sc.display.shading.cavity_type="BOTH"
sc.display.shading.background_type="WORLD"
sc.render.resolution_x=1160;sc.render.resolution_y=760
sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.camera=bpy.data.objects["01_HUMAN_ARRIVAL"]
sc["E6_ART_ADOPTED"]=False
sc["E6_FUNCTION_CERTIFIED"]=False
sc["E6_CITY_MASTER_COMPLETE"]=False
sc["E6_M247C_ADOPTED"]=False
sc["E6_MINECRAFT_WRITTEN"]=False
sc["E6_DESIGN_STATUS"]="G0_NATIVE_PREEDIT_ART_PENDING"
native=OUT/"E6_G0_REAL_INHABITED_FISSURE_BEFORE.blend"
glb=OUT/"E6_G0_REAL_INHABITED_FISSURE_BEFORE.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
                           export_cameras=False,export_lights=False)
for name in specs:
 sc.camera=bpy.data.objects[name]
 sc.render.filepath=str(OUT/("BEFORE_"+name+".png"))
 bpy.ops.render.render(write_still=True)
meshes=[o for o in bpy.data.objects if o.type=="MESH"]
manifest={
 "phase":"E6 G0 baseline NEW geometric architecture, not E5 art work",
 "source":"E6 independent new 3D; edit later must reopen native BLEND",
 "files":{"blend":native.name,"glb":glb.name,"images":["BEFORE_"+n+".png" for n in specs]},
 "edit_target":fold.name,
 "fold_verts":len(fold.data.vertices),
 "fold_faces":len(fold.data.polygons),
 "mesh_count":len(meshes),"verts":sum(len(o.data.vertices) for o in meshes),
 "triangles":sum(len(f.vertices)-2 for o in meshes for f in o.data.polygons),
 "ART":"PENDING_REAL_5_VIEW_VISUAL_INSPECTION",
 "FUNCTION":"UNCERTIFIED","CITY_MASTER_COMPLETE":False,
 "FORMAL_ADOPTION":False,"MINECRAFT_CONSTRUCTION":False}
(OUT/"E6_G0_REAL_NATIVE_MANIFEST.json").write_text(
 json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf8")
print("E6_G0_NATIVE_BLENDER_CREATED_ART_NOT_YET_JUDGED",json.dumps(manifest),flush=True)
