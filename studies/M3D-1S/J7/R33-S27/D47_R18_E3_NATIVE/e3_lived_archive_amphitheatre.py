"""D47-R18 E3 / Tidal Archive Forum / 潮文光庭.
Native 1:1 m architectural art G0, NOT an external mega-shell.
An ACTUAL inhabited civic interior: public scientific artifact / public reading
terraces / archive bays / urban-transit viewing rim, around one open forum.
Independent new 3D from human-room viewpoints, not E2 shape refinement.
No formal art approval, functional safety certification or Minecraft write.
"""
import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector

OUT=Path(sys.argv[-1]).resolve(); OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
palette={
"light_stone":(.79,.77,.71,1),"warm_wood":(.52,.33,.20,1),
"bronze":(.78,.54,.30,1),"deep_teal":(.14,.36,.43,1),
"sea_glass":(.25,.70,.72,1),"pale_glass":(.54,.83,.81,1),
"archive_ceramic":(.88,.83,.72,1),"floor":(.47,.51,.49,1),
"dark_floor":(.22,.29,.32,1),"plants":(.28,.48,.31,1),
"research_white":(.83,.89,.83,1),"screen_ink":(.12,.23,.29,1)}
for name,color in palette.items():
 m=bpy.data.materials.new("E3_"+name);m.diffuse_color=color
def group(n):
 c=bpy.data.collections.get(n)
 if c is None:
  c=bpy.data.collections.new(n);scene.collection.children.link(c)
 return c
def mesh(n,V,F,mat,gr,role):
 d=bpy.data.meshes.new(n+"_MESH");d.from_pydata(V,[],F);d.update()
 o=bpy.data.objects.new(n,d);group(gr).objects.link(o)
 d.materials.append(bpy.data.materials["E3_"+mat])
 o["E3_role"]=role;o["formal_art_adopted"]=False
 o.shape_key_add(name="Basis");o.shape_key_add(name="E3_ART_EDIT")
 return o
def slab(n,P,z0,z1,mat,gr,role):
 assert len(P)>=3 and z1>z0
 N=len(P);V=[(x,y,z0) for x,y in P]+[(x,y,z1) for x,y in P]
 F=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]
 F += [(i,(i+1)%N,N+(i+1)%N,N+i) for i in range(N)]
 return mesh(n,V,F,mat,gr,role)
def box(n,x0,x1,y0,y1,z0,z1,mat,gr,role):
 return slab(n,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1,mat,gr,role)
def archpt(r,t,z=0):
 return (r*math.sin(t),22+r*math.cos(t),z)
def terrace(n,inner,outer,amin,amax,z,mat,role,N=42,thick=1.3):
 # One connected curving inhabited floor with real thickness, never a row of steps.
 corners=[]
 for i in range(N+1):
  t=amin+(amax-amin)*i/N
  corners.append(archpt(outer,t))
 for i in range(N,-1,-1):
  t=amin+(amax-amin)*i/N
  corners.append(archpt(inner,t))
 return slab(n,[(x,y) for x,y,z0 in corners],z-thick,z,mat,
             "01 FUNCTIONAL_LIVING_PUBLIC_DESTINATIONS",role)
def beam(n,A,B,w,d,mat,gr,role):
 A=Vector(A);B=Vector(B);v=B-A;v.normalize()
 side=v.cross(Vector((0,0,1)))
 if side.length<1e-4:side=v.cross(Vector((1,0,0)))
 side.normalize();up=v.cross(side).normalized()
 V=[]
 for p in (A,B):
  for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1)):
   V.append(tuple(p+side*sx*w*.5+up*sy*d*.5))
 F=[(3,2,1,0),(4,5,6,7)]
 F +=[(i,(i+1)%4,4+(i+1)%4,4+i) for i in range(4)]
 return mesh(n,V,F,mat,gr,role)
def path_volume(n,P,ws,mat,gr,role):
 assert len(P)==len(ws)
 V=[]
 for i,(x,y,z) in enumerate(P):
  a=Vector(P[max(0,i-1)]);b=Vector(P[min(len(P)-1,i+1)])
  d=b-a;d.z=0;d.normalize()
  side=Vector((-d.y,d.x,0))
  for k,h in ((-1,0),(1,0),(-1,-.75),(1,-.75)):
   V.append(tuple(Vector((x,y,z))+side*k*ws[i]/2+Vector((0,0,h))))
 F=[(0,2,3,1)]
 for i in range(len(P)-1):
  a=4*i;b=a+4
  F +=[(a,a+1,b+1,b),(a,b,b+2,a+2),(a+1,a+3,b+3,b+1),(a+2,b+2,b+3,a+3)]
 a=4*(len(P)-1);F.append((a,a+1,a+3,a+2))
 o=mesh(n,V,F,mat,gr,role)
 o["E3_points"]=json.dumps(P)
 grades=[abs(b[2]-a[2])/math.hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(P,P[1:])]
 o["E3_segment_max_slope"]=max(grades)
 return o,max(grades)
def arch_wall_band(n,r,t0,t1,z0,z1,mat,role,N=20,thick=1.25):
 # Real curved solid wall band, not entire monolithic envelope.
 def strip(rr):
  return [archpt(rr,t0+(t1-t0)*k/N)[:2] for k in range(N+1)]
 P=strip(r+thick/2)+list(reversed(strip(r-thick/2)))
 return slab(n,P,z0,z1,mat,"02 CIVIC_ARCHIVE_FACADES",role)
def living_bookcase(n,r,t,z,h,side="center"):
 # Four shelves, real collection spines, end-screens and public undercanopy.
 x,y,_=archpt(r,t)
 width=6.7;depth=1.2
 box(n+"_BACK",x-width/2,x+width/2,y-depth/2,y+depth/2,z,z+h,
     "deep_teal","03 ARCHIVES_AND_LEARNING","vertical archive shelving in an inhabited room")
 for level in range(1,5):
  zz=z+level*h/5
  box(n+"_SHELF_"+str(level),x-width/2-.25,x+width/2+.25,
      y-depth/2-.28,y+depth/2+.28,zz,zz+.24,
      "bronze","03 ARCHIVES_AND_LEARNING","real horizontal storage and shelf floor")
 for j in range(8):
  # stored research volumes physically arranged in real shelving with distinct heights
  xx=x-width/2+.3+j*.75
  for i in (0,1,2):
   zz=z+.3+i*h/4
   box(n+"_BOOK_"+str(i)+"_"+str(j),xx,xx+.46,y-.75,y-.25,
       zz,zz+h/8+.12*(j%3),"archive_ceramic" if j%3 else "warm_wood",
       "03 ARCHIVES_AND_LEARNING","individual legible civic archive collection volume")
def table(n,x,y,z,w,depth,mat):
 box(n+"_SURFACE",x-w/2,x+w/2,y-depth/2,y+depth/2,z+.68,z+.9,mat,
     "04 INHABITED_CIVIC_STUDY_LIFE","actual collective working surface")
 for dx in (-w*.37,w*.37):
  for dy in (-depth*.32,depth*.32):
   box(n+"_SUPPORT_"+str(dx)+"_"+str(dy),x+dx-.16,x+dx+.16,
       y+dy-.16,y+dy+.16,z,z+.69,"deep_teal",
       "04 INHABITED_CIVIC_STUDY_LIFE","working table actual support")
def plant(n,x,y,z,r=1.7):
 # physically anchored living interior bed, not exterior landscaping pasted for effect
 box(n+"_BED",x-r,x+r,y-r,y+r,z,z+.55,"warm_wood",
     "04 INHABITED_CIVIC_STUDY_LIFE","sunlit planted civic indoor garden")
 for i in range(6):
  t=2*math.pi*i/6
  px=x+.67*r*math.cos(t);py=y+.67*r*math.sin(t)
  beam(n+"_STEM_"+str(i),(px,py,z+.55),(px+.3,py+.2,z+1.2+i*.18),
       .21,.21,"plants","04 INHABITED_CIVIC_STUDY_LIFE","actual planted interior leaves")
def human(n,x,y,z):
 box(n+"_BODY",x-.23,x+.23,y-.18,y+.18,z+.68,z+1.56,
     "research_white","05 HUMAN_VIEW_REFERENCES","scale-only proxy; NOT proof of population")
 box(n+"_HEAD",x-.18,x+.18,y-.18,y+.18,z+1.57,z+1.88,
     "warm_wood","05 HUMAN_VIEW_REFERENCES","scale-only standing person")

# First author the one ROOM: 90m deep open, inhabited public forum.
slab("ENTRY_ROOM_TRUE_FLOOR",
 [(-23,-87),(24,-87),(27,-54),(18,-42),(-18,-43),(-25,-59)],
 -.9,0,"floor","01 FUNCTIONAL_LIVING_PUBLIC_DESTINATIONS",
 "street-level accessible-looking approach, certification withheld")
slab("ARCHIVE_FORUM_CONTIGUOUS_FLOOR",
 [(-23,-44),(24,-45),(31,-6),(24,46),(-26,45),(-31,-4)],
 .9,2,"light_stone","01 FUNCTIONAL_LIVING_PUBLIC_DESTINATIONS",
 "public archive and planetary science teaching forum, actual occupiable floor")
P=[(0,-77,0),(0,-66,.5),(0,-55,1),(0,-43,1.55),(0,-31,2)]
route,grade=path_volume("REAL_PHYSICAL_ENTRY_TO_FORUM",
 P,[9,9,10,11,12],"floor","01 FUNCTIONAL_LIVING_PUBLIC_DESTINATIONS",
 "one true welded volume from public street to inner shared forum")
assert grade<1/12
# Distinct U-shaped inhabited terraces, in a real amphitheatre arrangement.
terraces=[
 ("CURATOR_PUBLIC_DISCUSSION",24,31,-2.02,2.02,5.0,"warm_wood"),
 ("READING_COLLECTION_BALCONY",33,41,-2.13,2.20,10.0,"archive_ceramic"),
 ("OPEN_RESEARCH_LABORATORY",43,52,-2.27,2.10,16.0,"floor"),
 ("HIGH_CITY_EDUCATION_TRANSIT",54,61,-2.18,2.24,22.0,"bronze")]
for name,inn,out,aa,bb,z,mat in terraces:
 terrace(name,inn,out,aa,bb,z,mat,"human-occupiable unique civic destination with distinct program")
# Terraces supported by physical piers at their own sector edges; high routes
# and guards are NOT certified. Main art G0 prioritises the genuine interior.
for ti,(name,inn,outer,a,b,z,mat) in enumerate(terraces):
 for j,t in enumerate((a+.12,(a+b)*.45,b-.12)):
  x,y,_=archpt(outer-1,t)
  beam(name+"_SUPPORT_"+str(j),(x,y,-2),(x,y,z-1.2),
       2.4,2.4,"deep_teal","02 CIVIC_ARCHIVE_FACADES",
       "visible civic gallery floor load-path expression; loads uncalculated")
 # short inner glass guards are actual physical meshes but not safety certified
 for j in range(15):
  t0=a+(b-a)*j/15
  t1=a+(b-a)*(j+1)/15
  if j in (1,7,13):continue  # intentionally legible access openings
  x0,y0,_=archpt(inn,t0);x1,y1,_=archpt(inn,t1)
  beam(name+"_TRANSLUCENT_PARAPET_"+str(j),
       (x0,y0,z+.68),(x1,y1,z+.68),
       .35,1.25,"sea_glass","02 CIVIC_ARCHIVE_FACADES",
       "human scale balcony parapet preview; access safety uncertified")
# Human-facing archive actually contains working rooms and reading.
for j,t in enumerate((-.92,-.64,-.36,.12,.42,.77,1.10)):
 living_bookcase("INHABITED_ARCHIVE_BAY_%02d"%j,38,t,10,6.1)
for j,t in enumerate((-.96,-.35,.45,1.04)):
 x,y,_=archpt(27,t)
 table("PUBLIC_READING_TABLE_"+str(j),x,y,5,4.5,2.6,"light_stone")
 human("READER_"+str(j),x+2.3,y-.9,5)
for j,t in enumerate((-.89,-.20,.55,.94)):
 x,y,_=archpt(47.5,t)
 table("PUBLIC_RESEARCH_TABLE_"+str(j),x,y,16,5.4,3.1,"research_white")
 human("RESEARCHER_"+str(j),x-1.9,y+1.8,16)
for j,t in enumerate((-.7,.23,.8)):
 x,y,_=archpt(57,t)
 plant("SUNLIGHT_LIBRARY_TREE_"+str(j),x,y,22,1.65)
for j,t in enumerate((-.72,0,.68)):
 x,y,_=archpt(56,t)
 human("HIGH_TRANSIT_PEDESTRIAN_"+str(j),x,y,22)
# Woven cultural living walls and daylight aperture. Walls have DIFFERENT
# bays and openings, not a huge faceless stone mass.
for j in range(20):
 a=-2.24+j*4.48/20
 b=-2.24+(j+1)*4.48/20
 if j in (0,1,18,19):continue
 r=65.5 if j%2 else 64
 # The independent vertical frame is thin enough that visitors can see through.
 for z0,z1 in ((0,8),(9,20),(21,36)):
  if (j+z0)%7==0:continue
  # each bay owns real depth and differentiated aperture, part of one arena
  arch_wall_band("CIVIC_PERFORATED_ARCHIVE_BAY_%02d_Z%02d"%(j,z0),
      r,a+.026,b-.026,z0,z1,
      "archive_ceramic" if z0==9 else "deep_teal",
      "habitable porous vertical archive bay with visibly open central aperture",8)
 for h in (8.5,20.5,36.5):
  x0,y0,_=archpt(r,a);x1,y1,_=archpt(r,b)
  beam("HORIZON_DAYLIGHT_FRAME_%02d_Z%02d"%(j,int(h)),
       (x0,y0,h),(x1,y1,h),.50,.55,
       "bronze","02 CIVIC_ARCHIVE_FACADES",
       "continuous window-frame modules permit light into public theatre")
# Overhead: three off-axis daylight petals intentionally NOT a continuous arch.
for j,(a,b,high,twist) in enumerate([
 (-2.14,-.93,52,-4),(-.67,.12,60,7),(.48,2.20,49,-6)]):
 grid=[]
 for s in range(5):
  t0=a+(b-a)*s/4
  row=[]
  for k in range(17):
   u=k/16
   r=49+20*u
   x,y,_=archpt(r,t0)
   z=high+9*math.sin(math.pi*u)+twist*math.sin(t0*1.6)
   row.append((x,y,z))
  grid.append(row)
 v=[p for row in grid for p in row]
 f=[(i*17+k,i*17+k+1,(i+1)*17+k+1,(i+1)*17+k)
    for i in range(4) for k in range(16)]
 mesh("OPEN_SKYLIGHT_CREST_"+str(j),v,f,
       "archive_ceramic" if j!=1 else "sea_glass",
       "06 ARCHITECTURE_OF_DAYLIGHT",
       "three irregular overhead sculptural daylight wings leaving the center open")
# Central actual purpose: a planted luminous archive well with a readable
# multi-sided public archive + scientific orbital sculpture, not thin random poles.
slab("PUBLIC_ORBITAL_ARCHIVE_ISLAND",
 [(-12,9),(14,7),(19,21),(11,37),(-15,34),(-18,19)],
 2,2.7,"warm_wood","03 ARCHIVES_AND_LEARNING",
 "genuine shared central education destination connected to public forum")
for j,(x,y) in enumerate(((-10,14),(14,12),(-12,29),(12,30))):
 box("PLANETARY_ARCHIVE_WORK_PILLAR_"+str(j),x-1.4,x+1.4,y-1.4,y+1.4,
     2.7,7.2,"deep_teal","03 ARCHIVES_AND_LEARNING",
     "real multi-view science archive exhibit with reachable working positions")
 for h in (3.5,4.7,6.1):
  box("SCIENCE_DISPLAY_SURFACE_%d_%d"%(j,int(h*10)),
      x-1.3,x+1.3,y-1.51,y-1.36,h,h+.42,
      "sea_glass","03 ARCHIVES_AND_LEARNING",
      "three dimensional civic research readout integrated into pillar")
# One central planetary system ring for public education.
def torus(n,c,rr,tube,mat,role,segments=64):
 cx,cy,cz=c;V=[];F=[]
 for i in range(segments):
  t=math.tau*i/segments
  for j in range(8):
   s=math.tau*j/8
   r=rr+tube*math.cos(s)
   V.append((cx+r*math.cos(t),cy+r*math.sin(t),
             cz+tube*math.sin(s)+.18*rr*math.sin(t)))
 for i in range(segments):
  for j in range(8):
   a=i*8+j;b=i*8+(j+1)%8;c=((i+1)%segments)*8+(j+1)%8;d=((i+1)%segments)*8+j
   F.append((a,b,c,d))
 return mesh(n,V,F,mat,"03 ARCHIVES_AND_LEARNING",role)
torus("CENTRAL_PLANETARY_ARCHIVE_LUMINOUS_RING",
      (0,23,20),10,.95,"sea_glass",
      "large educational planetarium exhibit within actual occupied public room")
for j,(x,y,z) in enumerate(((-13,17,2),(20,14,2),(-18,30,2),(20,35,2))):
 human("PUBLIC_FORUM_SCIENCE_VISITOR_"+str(j),x,y,z)
for j,(x,y) in enumerate(((-20,-20),(21,-17),(-22,41))):
 plant("INDOOR_GARDEN_"+str(j),x,y,2)
# Independent edit-ready first G0 image inspection
CAMERAS={
 "01_HUMAN_ENTRY_TO_ARCHIVE":((0,-78,1.65),(0,22,20),None),
 "02_HUMAN_INSIDE_SCIENCE_FORUM":((3,-17,3.65),(0,35,24),None),
 "03_READER_HIGH_BALCONY":((0,56,12.45),(0,10,8),None),
 "04_ROOM_ARCHITECTURE_3D":((151,-137,120),(0,22,24),245)
}
for n,(eye,target,ortho) in CAMERAS.items():
 data=bpy.data.cameras.new(n)
 o=bpy.data.objects.new(n,data);group("07 TRUE_ART_REVIEW_CAMERAS").objects.link(o)
 o.location=eye;o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
 data.clip_start=.06;data.clip_end=2200
 if ortho: data.type="ORTHO";data.ortho_scale=ortho
 else:data.type="PERSP";data.lens=29
scene.camera=bpy.data.objects["01_HUMAN_ENTRY_TO_ARCHIVE"]
scene.world=bpy.data.worlds.new("E3_FOG_GREY_BACKGROUND")
scene.world.color=(.40,.46,.49)
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type="BOTH"
scene.display.shading.background_type="WORLD"
scene.render.resolution_x=1260;scene.render.resolution_y=840
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
for prop,value in {
 "R18_E3_APPROVED_ART":False,
 "R18_E3_FUNCTIONAL_ACCESS_CERTIFIED":False,
 "R18_E3_CITY_MASTER_COMPLETE":False,
 "R18_E3_PROTECTED_M247C_ADOPTED":False,
 "R18_E3_MINECRAFT_WRITTEN":False,
 "R18_E3_PUBLIC_ROOM_STATUS":"UNREVIEWED_GENUINE_G0",
 "R18_E3_METHOD":"inhabited public interior before exterior city mass"}.items():
 scene[prop]=value
native=OUT/"R18_E3_REAL_EDITABLE_PUBLIC_ARCHIVE_ROOM.blend"
glb=OUT/"R18_E3_REAL_PUBLIC_ARCHIVE_ROOM.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
                          export_cameras=False,export_lights=False)
for n in CAMERAS:
 scene.camera=bpy.data.objects[n]
 scene.render.filepath=str(OUT/(n+".png"))
 bpy.ops.render.render(write_still=True)
O=[o for o in bpy.data.objects if o.type=="MESH"]
manifest={
 "project":"CELESTIAL HALO-9 D47-R18-E3 G0 independent art study",
 "scene":"inhabited public archive amphitheatre, actual human-scale interiors",
 "method":"true user-facing cultural / reading / research destinations before heroic skin",
 "source_reuse":"E3 new geometry; previous rejected E0/E1/E2 source not imported",
 "blender_version":bpy.app.version_string,
 "files":{"blend":native.name,"glb":glb.name,"cameras":[n+".png" for n in CAMERAS]},
 "meshes":len(O),"vertices":sum(len(o.data.vertices) for o in O),
 "triangles":sum(len(f.vertices)-2 for o in O for f in o.data.polygons),
 "real_entry_route_segment_gradient_max":grade,
 "unverified_higher_level_access":True,
 "egress_accessibility_structure_uncertified":True,
 "formal_ART":"PENDING_TRUE_4_VIEW_REVIEW",
 "formal_adoption":False,"whole_city_master_complete":False,
 "minecraft_write":False}
(OUT/"R18_E3_G0_MANIFEST.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")
print("D47_R18_E3_NEW_NATIVE_PUBLIC_INTERIOR_ART_UNREVIEWED",json.dumps(manifest,ensure_ascii=False),flush=True)
