"""HALO-9 D47 R18 E5 / VISUAL-EDIT METHOD PROBE / stage A.
Produce a NEW small civic chamber from scratch only once. Then freeze as an
actual .blend file; stage B must open and directly edit this very same file.
This deliberate G0 art-study baseline includes a low, opaque central sail
hiding the cultural research room. The question is whether inspecting real
pictures and editing actual native vertices can rescue the sightline.
Uncertified research ONLY; not a viable or adopted building.
"""
import bpy,math,json,sys
from mathutils import Vector
from pathlib import Path

out=Path(sys.argv[-1]).resolve();out.mkdir(exist_ok=True,parents=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
palette={
 "stone":(.60,.64,.60,1),"ivory":(.86,.84,.74,1),
 "deep":(.15,.22,.26,1),"bronze":(.73,.50,.27,1),
 "books":(.52,.34,.20,1),"sea":(.24,.66,.70,1),
 "pale":(.61,.82,.80,1),"path":(.42,.47,.46,1),
 "green":(.31,.50,.37,1)}
for k,v in palette.items():
 m=bpy.data.materials.new("E5_"+k);m.diffuse_color=v
def collection(n):
 c=bpy.data.collections.get(n)
 if not c:
  c=bpy.data.collections.new(n);sc.collection.children.link(c)
 return c
def mesh(n,v,f,mat,group,role):
 me=bpy.data.meshes.new(n+"_native");me.from_pydata(v,[],f);me.update()
 o=bpy.data.objects.new(n,me);collection(group).objects.link(o)
 me.materials.append(bpy.data.materials["E5_"+mat])
 o["E5_role"]=role
 o["E5_formal_art_adopted"]=False
 o.shape_key_add(name="Basis");o.shape_key_add(name="ART_EDIT")
 return o
def prism(n,P,z0,z1,mat,g,role):
 N=len(P);v=[(x,y,z0) for x,y in P]+[(x,y,z1) for x,y in P]
 f=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]
 f +=[(i,(i+1)%N,N+(i+1)%N,N+i) for i in range(N)]
 return mesh(n,v,f,mat,g,role)
def box(n,x0,x1,y0,y1,z0,z1,mat,g,role):
 return prism(n,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1,mat,g,role)
def linear_beam(n,A,B,w,h,mat,group,role):
 a=Vector(A);b=Vector(B);t=(b-a).normalized()
 u=t.cross(Vector((0,0,1)))
 if u.length<.01:u=t.cross(Vector((0,1,0)))
 u.normalize();q=t.cross(u).normalized()
 V=[]
 for center in (a,b):
  for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]:
   V.append(tuple(center+u*sx*w*.5+q*sy*h*.5))
 F=[(3,2,1,0),(4,5,6,7)]
 F +=[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
 return mesh(n,V,F,mat,group,role)
def suspended_veil():
 # A true finite facade surface with 9 x 7 native control points.
 # In iteration B only this EXISTING source object's actual vertices / faces
 # are edited in reopened BLEND, no source regeneration.
 nx=9;nz=7
 xvals=[-36,-27,-18,-9,0,9,18,27,36]
 zvals=[0,5,10,15,20,25,31]
 V=[];F=[]
 for j,z in enumerate(zvals):
  for i,x in enumerate(xvals):
   y=-6 + 3*math.sin(x/15+z/21) + .16*z
   zz=z+2.2*math.sin(x/13.5+z/14)
   V.append((x,y,zz))
 for j in range(nz-1):
  for i in range(nx-1):
   a=j*nx+i
   F.append((a,a+1,a+nx+1,a+nx))
 obj=mesh("E5_SOURCE_EDITABLE_MAIN_VEIL",V,F,"deep",
          "02 SINGLE_SOURCE_ARCHITECTURAL_MASS",
          "visually dominant opaque fold that blocks genuine cultural program")
 obj["E5_grid_nx"]=nx;obj["E5_grid_nz"]=nz
 return obj

prism("ENTRANCE_PUBLIC_STREET",
 [(-24,-68),(24,-68),(28,-50),(27,-24),(-28,-24),(-34,-45)],
 -1.2,0,"path","01 PUBLIC_FUNCTION_WITH_REAL_GEOMETRY",
 "original human-scale arrival threshold")
prism("ONE_LARGE_INHABITED_CIVIC_ROOM",
 [(-32,-25),(34,-25),(42,5),(32,43),(-28,43),(-43,11)],
 -.75,.1,"ivory","01 PUBLIC_FUNCTION_WITH_REAL_GEOMETRY",
 "single occupiable public room floor with actual scientific destinations")
prism("LEFT_CURATOR_READING_GALLERY",
 [(-47,-14),(-26,-15),(-25,26),(-46,30),(-56,4)],
 4.7,5.9,"books","01 PUBLIC_FUNCTION_WITH_REAL_GEOMETRY",
 "public archive room with true shelves, not a label")
prism("RIGHT_OPEN_RESEARCH_LAB",
 [(26,-10),(48,-13),(56,8),(39,33),(28,24)],
 6.7,7.8,"stone","01 PUBLIC_FUNCTION_WITH_REAL_GEOMETRY",
 "public working research room, open to civic atrium")
# Model a named cultural destination with real recognizable geometry.
prism("CENTRAL_PUBLIC_EXHIBIT_BASE",
 [(-12,14),(12,14),(16,30),(-17,30)],.1,1.25,
 "bronze","01 PUBLIC_FUNCTION_WITH_REAL_GEOMETRY",
 "orbital environmental archive interpretation island")
# One true 3D vertical exhibit, visually meaningful from approach.
for i,(x,y,top) in enumerate([(-9,20,10),(-1,23,15),(9,19,11)]):
 box("SCIENCE_PUBLIC_EXHIBIT_"+str(i),x-1.8,x+1.8,y-1.2,y+1.2,
     1.25,top,"sea","03 USABLE_ROOM_FUNCTION",
     "actual three-dimensional public science archive display")
 for hz in [2.7,5.2,7.7]:
  if hz<top:
   box("SCIENCE_DISPLAY_ACTIVE_PANEL_"+str(i)+"_"+str(hz),x-1.7,x+1.7,
       y-1.4,y-1.22,hz,hz+.45,"pale",
       "03 USABLE_ROOM_FUNCTION","physically visible display panel")
# Public archive: legible shelves, at an oblique site-specific orientation.
for j,(y,h) in enumerate([(-9,10.8),(0,11.6),(10,12.3),(20,12.0)]):
 box("READABLE_HISTORY_COLLECTION_"+str(j),-47,-41,y,y+4,
     5.9,h,"books","03 USABLE_ROOM_FUNCTION",
     "inhabited library with actual storage and usable archive racks")
 for zz in [7.2,9.4]:
  box("PHYSICAL_SHELVES_"+str(j)+"_"+str(zz),-48,-40,y,y+4,
      zz,zz+.25,"bronze","03 USABLE_ROOM_FUNCTION",
      "physical shelves and study collection")
# Scientific public lab: two real workbench surfaces and a public instrument.
for j,(x,y) in enumerate([(37,-4),(41,18)]):
 box("RESEARCH_REAL_DESK_"+str(j),x-4,x+4,y-1.8,y+1.8,
     8.5,8.9,"ivory","03 USABLE_ROOM_FUNCTION",
     "readable public working table")
 for dx in (-3.0,3.0):
  linear_beam("DESK_SUPPORT_%d_%s"%(j,str(dx)),
    (x+dx,y,7.8),(x+dx,y,8.6),.35,.35,
    "deep","03 USABLE_ROOM_FUNCTION","structurally visible research workdesk support")
box("RESEARCH_WINDOW_REAL_INSTRUMENT",39,44,6,12,7.8,14.4,
    "sea","03 USABLE_ROOM_FUNCTION","large experimental interactive civic exhibit")
# Distinct light-bearing structural shell is integrated with room edges.
for idx,(A,B,w,h) in enumerate([
 ((-35,-31,0),(-29,35,27),3.2,2.0),
 ((39,-25,0),(30,30,33),4.2,2.5),
 ((-25,41,0),(24,42,28),4.5,3.0)]):
 linear_beam("URBAN_DAYLIGHT_STRUCTURE_"+str(idx),A,B,w,h,
   "ivory" if idx==1 else "bronze","02 SINGLE_SOURCE_ARCHITECTURAL_MASS",
   "room edge structural feature, not a complete enclosed stadium")
suspended_veil()
# Camera visibility can be evaluated by pixels, but art judgment needs a real reviewer.
cam_specs={
 "01_HUMAN_ROOM_ARRIVAL":((0,-57,1.75),(0,20,11.5),None),
 "02_HUMAN_INTERIOR_SIDE":((-14,-24,2.3),(9,20,10),None),
 "03_FRONT_ARCHITECTURE":((93,-115,88),(0,0,21),135),
 "04_OTHER_SIDE":((-86,-80,62),(0,0,20),139)}
for n,(eye,target,ortho) in cam_specs.items():
 d=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,d)
 collection("04 FIXED_ART_CAMERAS").objects.link(o)
 o.location=eye
 o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
 d.clip_start=.05;d.clip_end=1000
 if ortho:d.type="ORTHO";d.ortho_scale=ortho
 else:d.type="PERSP";d.lens=27
sc.world=bpy.data.worlds.new("E5_NEUTRAL_STUDIO_LIGHT")
sc.world.color=(.52,.57,.60)
sc.render.engine="BLENDER_WORKBENCH"
sc.display.shading.light="STUDIO"
sc.display.shading.color_type="MATERIAL"
sc.display.shading.show_cavity=True
sc.display.shading.cavity_type="BOTH"
sc.display.shading.background_type="WORLD"
sc.render.resolution_x=1160;sc.render.resolution_y=760
sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc["E5_FROM_NEW_SOURCE"]=True
sc["E5_RESEARCH_ART_ADOPTED"]=False
sc["E5_M247C_ADOPTED"]=False
sc["E5_BUILDING_FUNCTION_CERTIFIED"]=False
sc["E5_CITY_MASTER_COMPLETE"]=False
sc["E5_MINECRAFT_WRITTEN"]=False
sc.camera=bpy.data.objects["01_HUMAN_ROOM_ARRIVAL"]
native=out/"E5_G0_NEW_PUBLIC_ROOM_BEFORE_EDIT.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(native))
# Preview baseline, cameras unchanged for all later versions.
for n in cam_specs:
 sc.camera=bpy.data.objects[n]
 sc.render.filepath=str(out/("BEFORE_"+n+".png"))
 bpy.ops.render.render(write_still=True)
objects=[o for o in bpy.data.objects if o.type=="MESH"]
manifest={
 "type":"E5 METHOD TEST - new public room before editing any vertices",
 "source":"noncanonical new study and not E4 detailed artwork",
 "native_blend":native.name,"editable_target":"E5_SOURCE_EDITABLE_MAIN_VEIL",
 "cameras":list(cam_specs),
 "mesh_count":len(objects),"native_vertices":sum(len(o.data.vertices) for o in objects),
 "native_triangles":sum(len(f.vertices)-2 for o in objects for f in o.data.polygons),
 "ART":"INTENTIONALLY_UNREVIEWED","FUNCTION":"NOT_CERTIFIED",
 "canonical_assets_edited":False,"minecraft_write":False}
(out/"E5_G0_BASELINE_MANIFEST.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
print("E5_G0_NEW_NATIVE_BASELINE",json.dumps(manifest),flush=True)
