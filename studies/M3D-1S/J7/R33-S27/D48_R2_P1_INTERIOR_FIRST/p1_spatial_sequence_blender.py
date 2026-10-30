"""D48 R2 P1: public spaces first, shell LAST. Independent editable Blender scene.
Pure research ART-FIRST / no Minecraft. World coordinates not verified.
The central model is a spatial METHOD proof, never the full 10km City Master.
"""
import bpy
from mathutils import Vector
from pathlib import Path
import math,json,hashlib,sys

OUT=Path(sys.argv[-1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene
S.name="D48_P1_INHABITED_CIVIC_SPATIAL_PROOF_NOT_ADOPTED"
for k,v in {
 "CITY_MASTER_COMPLETE":False,"FORMAL_ADOPTED":False,
 "MINECRAFT_WRITTEN":False,"OFFICIAL_COORDINATES":False,
 "MODEL_H_TO_MINECRAFT_Y":"UNKNOWN","ART":"UNREVIEWED",
 "FUNCTION":"UNVERIFIED_PORTAL_GEOMETRY_ONLY"
}.items():S["D48_"+k]=v
def group(s):
 c=bpy.data.collections.new(s);S.collection.children.link(c);return c
GR={n:group(n) for n in [
 "01_PUBLIC_ROOM_AND_FLOORS_FIRST",
 "02_STATIONS_AND_ELEVATOR_SPACE",
 "03_INHABITED_H1_H2_LINKED_DESTINATIONS",
 "04_ARCHITECTURAL_ENVELOPE_ONLY_AFTER_INTERIORS",
 "05_W0_LANDSCAPE_RESEARCH",
 "06_RESEARCH_SCOPE_LOCATORS",
 "07_REAL_EYE_CAMERAS"]}
def material(n,rgb):
 m=bpy.data.materials.new(n);m.diffuse_color=(*rgb,1);return m
M={
 "travertine":material("IVORY_CIVIC_STONE",(.89,.85,.76)),
 "pearl":material("PEARL_SHELL",(.73,.81,.82)),
 "blue":material("TEAL_PUBLIC_CIRCULATION",(.28,.71,.76)),
 "dark":material("VOID_SIDE_STRUCTURE",(.14,.23,.29)),
 "brass":material("SACRED_BRONZE",(.65,.48,.30)),
 "earth":material("W0_CITY_BASIN_STONE",(.38,.49,.47)),
 "sea":material("EAST_INLAND_SEA",(.20,.41,.51)),
 "garden":material("SKY_GARDEN",(.26,.46,.37)),
 "public":material("CULTURAL_ATLAS",(.69,.68,.59)),
}
def mesh(name,pts,faces,mat,coll,role,asset=None):
 me=bpy.data.meshes.new(name+"_EDITABLE")
 me.from_pydata(pts,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);coll.objects.link(ob)
 me.materials.append(mat);ob["D48_ROLE"]=role
 if asset:ob["D48_ASSET"]=asset
 ob["ACTUAL_CITY_MASTER_FINISHED"]=False
 return ob
def box(name,center,dimensions,mat,coll,role,asset=None,heading=0):
 cx,cy,cz=center;wx,wy,wz=dimensions
 # Real editable mesh, no hidden procedural proxy or instance.
 px=[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
     (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]
 pts=[]
 for x,y,z in px:
  xx=x*wx*.5;yy=y*wy*.5
  pts.append((cx+xx*math.cos(heading)-yy*math.sin(heading),
              cy+xx*math.sin(heading)+yy*math.cos(heading),cz+z*wz*.5))
 faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 return mesh(name,pts,faces,mat,coll,role,asset)
def extrude_xz(name,outline,y0,y1,mat,coll,role,asset=None):
 n=len(outline)
 pts=[(x,y0,z) for x,z in outline]+[(x,y1,z) for x,z in outline]
 fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]
 for i in range(n):
  j=(i+1)%n;fs.append((i,j,j+n,i+n))
 return mesh(name,pts,fs,mat,coll,role,asset)
def walkway(name,a,b,width,thick,mat,coll,asset,role="VISIBLE_CIVIC_WALKWAY"):
 # Genuine connected walkable planar deck (height validated independently),
 # measured by public path stations rather than a thin curve tube.
 ax,ay,az=a;bx,by,bz=b
 d=Vector((bx-ax,by-ay,0));assert d.length>1e-3
 n=Vector((-d.y,d.x,0)).normalized()*width/2
 top=[(ax+n.x,ay+n.y,az),(ax-n.x,ay-n.y,az),
      (bx-n.x,by-n.y,bz),(bx+n.x,by+n.y,bz)]
 bottom=[(x,y,z-thick) for x,y,z in top]
 ob=mesh(name,top+bottom,[(0,1,2,3),(7,6,5,4),(0,4,5,1),
         (1,5,6,2),(2,6,7,3),(3,7,4,0)],mat,coll,role,asset)
 ob["FLOOR_TOP_CENTER_START"]=str(a);ob["FLOOR_TOP_CENTER_END"]=str(b)
 return ob
def landscape(x,y):
 # Exactly flat at ground approach route; mountain/sea geography only beyond.
 north=max(0.,(y-2800)/2700.)**1.4*920
 west=max(0.,(-x-3000)/2600.)*800
 sw=-280 if x< -2000 and y<-1850 else 0.
 east=-200 if x>4500 else 0.
 return north+west+sw+east
def ground():
 size=34;v=[];f=[]
 for j in range(size):
  y=-5800+11600*j/(size-1)
  for i in range(size):
   x=-5800+11600*i/(size-1)
   v.append((x,y,landscape(x,y)))
 for j in range(size-1):
  for i in range(size-1):
   k=j*size+i;f.append((k,k+1,k+size+1,k+size))
 mesh("W0_FRACTURED_BASIN_EDITABLE",v,f,M["earth"],GR["05_W0_LANDSCAPE_RESEARCH"],
      "W0_TERRAIN_RESEARCH_NOT_FORMAL", "W0")
 mesh("W0_EAST_SEA_RESEARCH",
      [(4800,-5700,-155),(5800,-5700,-155),(5800,5500,-155),(4800,5500,-155)],
      [(0,1,2,3)],M["sea"],GR["05_W0_LANDSCAPE_RESEARCH"],"W0_ARTIFICIAL_SEA","W0")
ground()
# 1. Real public activity and floor volumes are designed FIRST.
GROUND_STATIONS=[
 ("W0_PUBLIC_ARRIVAL",(0,-1600,0)),
 ("WELCOME_COURT",(0,-1240,0)),
 ("OPEN_CULTURAL_THRESHOLD",(0,-850,0)),
 ("CENTRAL_ATLAS_FORUM",(0,-440,0)),
 ("PUBLIC_CIVIC_VOID",(0,0,0)),
 ("RESEARCH_EXCHANGE",(0,380,0)),
 ("VERTICAL_STATION_GROUND",(0,780,0)),
]
path_segments=[]
for i in range(len(GROUND_STATIONS)-1):
 name=f"LOWER_PUBLIC_FLOOR_{i:02d}"
 a,b=GROUND_STATIONS[i][1],GROUND_STATIONS[i+1][1]
 walkway(name,a,b,240 if i<2 else 340,15,M["travertine"],
         GR["01_PUBLIC_ROOM_AND_FLOORS_FIRST"],"M247-C")
 path_segments.append({"name":name,"start":a,"end":b,"mode":"WALK","floor_width_m":240 if i<2 else 340})
# Interlocked cultural program: genuine publicly accessible room floors and
# asymmetrical open galleries, not building-identity labels or facade windows.
ROOMS=[
 ("RESEARCH_ARCHIVE_WEST",(-560,-350,55),(700,470,110),M["public"]),
 ("CULTURAL_ATLAS_EAST",(560,-80,75),(640,650,150),M["travertine"]),
 ("EXCHANGE_FORUM_WEST",(-650,430,140),(520,580,280),M["brass"]),
 ("OPEN_SCIENCE_WALL_EAST",(600,500,135),(480,450,270),M["public"]),
]
def inhabited_public_room(name,center,dim,mat):
 # Open, hollow, *actually enterable* room shell: floor/roof and six walls
 # with a 240m opening toward the civic street. Never use a sealed cube.
 x,y,z=center;dx,dy,dz=dim
 wall=18
 floor_z=z-dz/2
 coll=GR["01_PUBLIC_ROOM_AND_FLOORS_FIRST"]
 for n,ctr,dimensions in [
  ("FLOOR",(x,y,floor_z-6),(dx,dy,12)),
  ("ROOF",(x,y,z+dz/2+8),(dx,dy,16)),
  ("NORTH_WALL",(x,y+dy/2-wall/2,z),(dx,wall,dz)),
  ("SOUTH_WALL",(x,y-dy/2+wall/2,z),(dx,wall,dz)),
  ("OUTER_WALL",(x+(dx/2-wall/2 if x>0 else -dx/2+wall/2),y,z),
   (wall,dy,dz))
 ]:
  box(name+"_"+n,ctr,dimensions,mat,coll,"HOLLOW_PUBLIC_ROOM_SHELL_WIP","M247-C")
 inner_x=x+(-dx/2+wall/2 if x>0 else dx/2-wall/2)
 aperture=240
 remainder=(dy-aperture)/2
 for sign in [-1,1]:
  section_center_y=y+sign*(aperture/2+remainder/2)
  box(name+"_PUBLIC_DOOR_WALL_"+str(sign),(inner_x,section_center_y,z),
      (wall,remainder,dz),mat,coll,"OPEN_PORTAL_ROOM_WALL_WIP","M247-C")
 # A real branch deck from central public path into the aperture.
 port_x=inner_x+(-25 if x>0 else 25)
 walkway(name+"_ENTRY_FLOOR",(0,y,0),(port_x,y,0),110,12,
     M["travertine"],coll,"M247-C","ROOM_ENTRY_CONNECTED_FLOOR_WIP")
for n,xyz,dim,m in ROOMS:
 inhabited_public_room(n,xyz,dim,m)
for i,(x,y,z) in enumerate([
 (-310,-350,0),(-280,180,0),(300,120,0),(260,540,0)]):
 box("INTERIOR_FORUM_EXHIBIT_"+str(i),(x,y,z+45),(90,115,90),
     M["blue"] if i%2 else M["brass"],
     GR["01_PUBLIC_ROOM_AND_FLOORS_FIRST"],"CIVIC_EXHIBITION_PROXY_NOT_DETAILED",
     "M247-C")
# Public gathering terraces and inner city floors positioned *before shell*.
for z,cx,cy,dx,dy in [(150,-560,-160,620,690),(325,600,80,570,720),
                      (540,-700,470,670,610),(760,550,530,520,620)]:
 box(f"CIVIC_BALCONY_Z{z}",(cx,cy,z),(dx,dy,34),M["travertine"],
   GR["01_PUBLIC_ROOM_AND_FLOORS_FIRST"],"INHABITED_MASS_PUBLIC_BALCONY_WIP","M247-C")
# Concrete three-dimensional station: lower and upper floors, column volumes,
# and a 3D open elevator shaft; lift operation NOT certified.
box("CENTRAL_STATION_GROUND",(0,780,-6),(520,480,12),M["brass"],
    GR["02_STATIONS_AND_ELEVATOR_SPACE"],"PUBLIC_METRO_CONCOURSE_FLOOR","M247-C")
box("CENTRAL_STATION_UPPER",(0,780,772),(520,480,24),M["travertine"],
    GR["02_STATIONS_AND_ELEVATOR_SPACE"],"UPPER_STATION_LANDING","M247-C")
for x in (-200,200):
 for y in (570,990):
  box(f"ASCENT_SHAFT_SUPPORT_{x}_{y}",(x,y,390),(28,28,780),M["dark"],
       GR["02_STATIONS_AND_ELEVATOR_SPACE"],"VERTICAL_STATION_STRUCTURE","M247-C")
box("PUBLIC_LIFT_CAR_VOLUME",(0,780,36),(115,120,70),M["blue"],
    GR["02_STATIONS_AND_ELEVATOR_SPACE"],
    "ELEVATOR_PHYSICAL_CAR_UNOPERATED","M247-C")
# 2. Topological vertical transfer: mode ELEVATOR, not fake walkable ramp.
route=[*path_segments,{
 "name":"PUBLIC_ELEVATOR_ROUTE","start":(0,780,0),"end":(0,780,784),
 "mode":"LIFT","floor_width_m":None,"physical_shaft":True,
 "operational_mechanism":"NOT_IMPLEMENTED"}]
# 3. Attached THICK inhabited H1 and H2 districts, with internal public
# floors and real bridging deck, not detached thin hover islands.
h_specs=[
 ("H1",(-260,1540,780),(1150,950,440),M["pearl"]),
 ("H2",(1470,1890,1060),(1280,1140,560),M["public"]),
]
def inhabitable_h_shell(asset,c,dim,color):
 # No solid occupied block: roof/foundation/perimeter wall with an
 # actual open bridge entry and multiple real floors.
 x,y,z=c;dx,dy,dz=dim;wall=30
 coll=GR["03_INHABITED_H1_H2_LINKED_DESTINATIONS"]
 for n,ct,dims in [
  ("FOUNDATION",(x,y,z-dz/2-15),(dx,dy,30)),
  ("ROOF",(x,y,z+dz/2+17),(dx,dy,34)),
  ("NORTH_EDGE",(x,y+dy/2-wall/2,z),(dx,wall,dz)),
  ("EAST_EDGE",(x+dx/2-wall/2,y,z),(wall,dy,dz))]:
  box(asset+"_"+n,ct,dims,color,coll,"HOLLOW_INHABITED_SKY_CITY_WIP",asset)
 if asset=="H1":
  a=x-dx/2;b=x+dx/2;cut=-70;gap=150
  for suffix,lo,hi in [("WEST",a,cut-gap),("EAST",cut+gap,b)]:
   box(asset+"_SOUTH_PORTAL_WALL_"+suffix,
       ((lo+hi)/2,y-dy/2+wall/2,z),(hi-lo,wall,dz),
       color,coll,"OPEN_H1_PUBLIC_ENTRY",asset)
  box(asset+"_WEST_EDGE",(x-dx/2+wall/2,y,z),(wall,dy,dz),
      color,coll,"H1_CIVIC_SIDE_WALL",asset)
 else:
  a=y-dy/2;b=y+dy/2;cut=1755;gap=175
  for suffix,lo,hi in [("SOUTH",a,cut-gap),("NORTH",cut+gap,b)]:
   box(asset+"_WEST_PORTAL_WALL_"+suffix,
       (x-dx/2+wall/2,(lo+hi)/2,z),(wall,hi-lo,dz),
       color,coll,"OPEN_H2_PUBLIC_ENTRY",asset)
  box(asset+"_SOUTH_EDGE",(x,y-dy/2+wall/2,z),(dx,wall,dz),
      color,coll,"H2_CIVIC_SIDE_WALL",asset)
for asset,c,dim,color in h_specs:
 inhabitable_h_shell(asset,c,dim,color)
 for j in range(3):
  # First/second research floors cross the actual attached route at z=784.
  # Separate public floors are not a fully authored private city interior.
  top_levels=([640,784,925] if asset=="H1" else [784,1060,1230])
  lvl=top_levels[j]-9.5
  box(f"{asset}_PUBLIC_LEVEL_{j}",(c[0],c[1],lvl),
     (dim[0]*.82,dim[1]*.82,19),M["travertine"],
     GR["03_INHABITED_H1_H2_LINKED_DESTINATIONS"],
     "CITY_PUBLIC_LEVEL_REAL_FLOOR_ONLY_WIP",asset)
 for j in range(8):
  x=c[0]-dim[0]*.35+dim[0]*.1*j
  box(f"{asset}_CIVIC_STREET_BAY_{j}",(x,c[1]+130,c[2]+dim[2]*.36),
     (65,85,145),M["blue"] if j%2 else M["brass"],
     GR["03_INHABITED_H1_H2_LINKED_DESTINATIONS"],
     "PUBLIC_BLOCK_FACADE_WIP",asset)
# top of H1 is not necessarily walkable at z=780: real landing is open cavity
# matching the lower inhabited public floor surface.
walkway("UPPER_FROM_STATION_TO_H1",(0,780,784),(-180,1540,784),
       125,23,M["brass"],GR["03_INHABITED_H1_H2_LINKED_DESTINATIONS"],
       "H1","HIGH_CIVIC_TRANSFER_DECK")
route.append({"name":"UPPER_FROM_STATION_TO_H1",
              "start":(0,780,784),"end":(-180,1540,784),
              "mode":"WALK","floor_width_m":125})
walkway("H1_TO_H2_PUBLIC_TECTONIC_CORRIDOR",
        (-180,1540,784),(1470,1890,784),160,45,M["blue"],
        GR["03_INHABITED_H1_H2_LINKED_DESTINATIONS"],"H2",
        "INHABITED_ELEVATED_PUBLIC_TRANSFER_DECK")
route.append({"name":"H1_TO_H2_PUBLIC_TECTONIC_CORRIDOR",
              "start":(-180,1540,784),"end":(1470,1890,784),
              "mode":"WALK","floor_width_m":160})
# 4. Only now: main building architectural boundary. Sculptural folded,
# nonmirrored and inhabited shell, with continuous daylight aperture above
# the large public hall. No copied P0 arches.
WEST_FOLD=[
 (-1160,-1450,0),(-1000,-1550,530),(-740,-1510,1180),
 (-590,-1140,1700),(-680,-420,1930),(-900,200,1650),
 (-1120,880,950),(-1260,1450,170),(-940,1520,0)]
EAST_FOLD=[
 (1250,-1360,0),(1060,-1390,540),(910,-970,970),
 (1090,-440,1550),(1370,0,1790),(1640,850,1240),
 (1850,1760,690),(1500,2250,0),(1150,2300,0)]
# Folded curved buttresses are assembled from manually authored city section
# stations, not identical rings or columns. Space remains open to daylight.
def bent_wall(name,controls,mat,asset):
 # Build contiguous (but not simply vertical) thick mesh cells connecting
 # consecutive control points with graduated width/depth.
 for i in range(len(controls)-1):
  x0,y0,z0=controls[i];x1,y1,z1=controls[i+1]
  d=Vector((x1-x0,y1-y0,z1-z0))
  center=(Vector(controls[i])+Vector(controls[i+1]))*.5
  half_width=270+95*math.sin(i*1.33+(.7 if name=="WEST" else 2))
  # Placed within the layout as individually editable architectural solids.
  # A single big cube-massing iteration would fail; these control sections
  # have explicit access balconies/life volumes connected on lower levels.
  ob=box(f"{name}_FOLDED_INHABITED_BUTTRESS_{i}",center,
         (2*half_width,430,d.length+120),mat,
         GR["04_ARCHITECTURAL_ENVELOPE_ONLY_AFTER_INTERIORS"],
         "FOLDED_OCCUPIED_CITY_ENVELOPE_WIP",asset)
  ob.rotation_mode="QUATERNION"
  ob.rotation_quaternion=Vector((0,0,1)).rotation_difference(d)
  ob["SHAPE_CONTROL_POINTS"]=f"{controls[i]} -> {controls[i+1]}"
bent_wall("WEST",WEST_FOLD,M["pearl"],"M247-C")
bent_wall("EAST",EAST_FOLD,M["dark"],"M247-C")
# A genuine asymmetrical sky city canopy partially spans the central public
# canyon; importantly not a full thin lid closing the courtyard.
for i,(x,y,z,sx,sy) in enumerate([
 (-700,300,1810,670,440),
 (-330,640,2000,560,590),
 (490,1120,1730,800,550),
 (1040,1470,1550,930,500)]):
 box("PARTIAL_HIGH_CITY_CANOPY_"+str(i),(x,y,z),
     (sx,sy,110),M["travertine"],
     GR["04_ARCHITECTURAL_ENVELOPE_ONLY_AFTER_INTERIORS"],
     "PUBLIC_CANOPY_WITH_THICK_LOWER_STREET_WIP","M247-C")
# Non-geometric scope marker for unbuilt urban entities. Explicitly forbid
# treating these as built, or as official registered coordinates.
def locator(asset,pos,role):
 ob=bpy.data.objects.new("UNBUILT_"+asset,bpy.data.objects.new if False else None)
 GR["06_RESEARCH_SCOPE_LOCATORS"].objects.link(ob)
 ob.location=pos
 ob.empty_display_type="ARROWS";ob.empty_display_size=200
 ob["D48_ASSET"]=asset;ob["D48_ROLE"]=role
 ob["REAL_GEOMETRY_COMPLETE"]=False;ob["OFFICIAL_POSITION"]=False
 return ob
for i in range(3,7):
 locator("H"+str(i),(-3800+i*1050,3900+500*(i%2),1850+250*i),
         "SKY_CITY_NOT_BUILT_P1")
for i in range(1,17):
 a=i*2*math.pi/16
 locator(f"SB{i:02d}",(4400*math.cos(a),3900*math.sin(a),320),
         "SPECIAL_CITY_FACILITY_UNBUILT_P1")
for i in range(1,4):
 locator("V"+str(i),(i*850,-3200,300),"VISTA_NOT_VALIDATED")
 locator("METRO_AXIS_"+str(i),(-i*900,-2300,250),
         "AXIS_NOT_PHYSICALLY_CONNECTED")
# Route data is stored inside BLEND as provenance, not as proof of walkability.
S["D48_ROUTE_STATION_COUNT"]=len(GROUND_STATIONS)
S["D48_ROUTE_LIFT_ENGINE_IMPLEMENTED"]=False
S["D48_ROUTE_PHYSICAL_FLOOR_SEGMENTS"]=len(route)-1
# All human cameras are verified exactly 1.65m above their authored floor.
CAMS={
 "01_REAL_EYE_ARRIVAL":((0,-1490,1.65),(0,-510,110),24,"W0_GROUND"),
 "02_REAL_EYE_FORUM":((0,-430,1.65),(0,450,135),26,"W0_GROUND"),
 "03_REAL_EYE_RESEARCH":((0,250,1.65),(0,850,260),24,"W0_GROUND"),
 "04_REAL_EYE_H1_PUBLIC":((-180,1530,785.65),(600,1810,900),27,"H1_DECK"),
 "05_NORTH_MACRO":((2400,7400,4200),(0,500,1150),38,"MACRO"),
 "06_EAST_SEA":((7250,500,3000),(0,350,1300),38,"MACRO"),
 "07_SOUTHWEST_NEGATIVE":((-7700,-6100,4300),(0,400,1450),40,"MACRO"),
}
for name,(origin,target,lens,groundref) in CAMS.items():
 data=bpy.data.cameras.new(name+"_REAL_LENS")
 ob=bpy.data.objects.new(name,data);GR["07_REAL_EYE_CAMERAS"].objects.link(ob)
 ob.location=origin
 ob.rotation_euler=(Vector(target)-ob.location).to_track_quat("-Z","Y").to_euler()
 data.lens=lens;data.clip_start=.05;data.clip_end=60000.
 ob["VIEW_TYPE"]=groundref
 ob["ACTUAL_EYE_OFFSET_M"]=(1.65 if groundref!="MACRO" else -1)
 if groundref=="W0_GROUND":
  assert abs(ob.location.z-(landscape(origin[0],origin[1])+1.65))<.001
 if groundref=="H1_DECK":assert abs(ob.location.z-784-1.65)<.001
S.world=bpy.data.worlds.new("CITY_WARM_STUDIO_SKY")
S.world.color=(.42,.47,.53)
S.render.engine="BLENDER_WORKBENCH"
S.display.shading.light="STUDIO"
S.display.shading.color_type="MATERIAL"
S.display.shading.show_shadows=True
S.display.shading.show_cavity=True
S.display.shading.cavity_type="BOTH"
S.display.shading.background_type="WORLD"
S.view_settings.view_transform="Standard"
S.render.resolution_x=1360
S.render.resolution_y=800
S.render.resolution_percentage=100
S.render.image_settings.file_format="PNG"
S.camera=bpy.data.objects["01_REAL_EYE_ARRIVAL"]
save=OUT/"D48_R2_P1_PUBLIC_SPACE_FIRST_EDITABLE.blend"
glb=OUT/"D48_R2_P1_PUBLIC_SPACE_FIRST_GEOMETRY.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(save))
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
                           export_cameras=False,export_lights=False)
images=[]
for name in CAMS:
 S.camera=bpy.data.objects[name]
 out=OUT/(name+".png");S.render.filepath=str(out)
 bpy.ops.render.render(write_still=True)
 images.append(out)
all_objects=[o for o in bpy.data.objects if o.type=="MESH"]
id_real=sorted({o.get("D48_ASSET") for o in all_objects if o.get("D48_ASSET")})
expected_real={"M247-C","W0","H1","H2"}
assert expected_real.issubset(id_real)
assert len(CAMS)==7 and len(route)>=8
assert all(s["mode"] in ("WALK","LIFT") for s in route)
assert sum(x["mode"]=="LIFT" for x in route)==1
data={
 "stage":"D48_R2_P1_INTERIOR_FIRST_REAL_3D",
 "formal_adoption":False,"minecraft_construction":False,
 "world_coords":"RESEARCH_LOCAL_XYZ_NOT_OFFICIAL",
 "city_master_complete":False,
 "source_tech":"AWAIT_INDEPENDENT_RELOAD",
 "art":"AWAIT_ACTUAL_7_VIEW_REVIEW",
 "function":"UNVERIFIED_ELEVATOR_AND_PUBLIC_ACCESSES",
 "real_public_floor_segments":len(route)-1,
 "route_sequence":[{"name":x["name"],"mode":x["mode"],"start":x["start"],"end":x["end"]} for x in route],
 "physical_real_3d_assets":id_real,
 "unmodeled_required_assets":["H3","H4","H5","H6"]+[f"SB{i:02d}" for i in range(1,17)],
 "camera_names":list(CAMS),
 "eye_heights_m":{"01_REAL_EYE_ARRIVAL":1.65,"02_REAL_EYE_FORUM":1.65,
                  "03_REAL_EYE_RESEARCH":1.65,"04_REAL_EYE_H1_PUBLIC":1.65},
 "files":{"blend":save.name,"glb":glb.name,"pngs":[p.name for p in images]},
 "sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [save,glb]+images},
 "mesh_count":len(all_objects)}
(OUT/"D48_R2_P1_MANIFEST.json").write_text(json.dumps(data,indent=2,ensure_ascii=False))
print("D48_R2_P1_SPATIAL_SEQUENCE_GENERATED",len(all_objects),"meshes",len(images),"genuine cameras")
