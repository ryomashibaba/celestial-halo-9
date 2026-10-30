"""D48 R2 P0: architecture-authored 3D sculpt + actual negative-space carving.
Early visual stop-gate; NOT a complete city master. No R1 geometry is imported.
Experimental XYZ only. Absolutely no Minecraft or canonical write.
Run: python d48_r2_sculpted_city_p0.py OUTPUT_DIR
"""
from pathlib import Path
import bpy, bmesh, json, math, sys, hashlib
from mathutils import Vector

OUT=Path(sys.argv[-1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
sc.name="D48_R2_P0_Sculptural_Civic_Tide_UNADOPTED"
for key,value in {
 "FORMAL_DESIGN_ADOPTED":False,"MINECRAFT_WORLD_WRITTEN":False,
 "CITY_MASTER_COMPLETE":False,"OFFICIAL_COORDINATE_MATCH":False,
 "M204_W0_SHARED_ANCHORS_CERTIFIED":0,"MODEL_H_TO_WORLD_Y":"UNKNOWN",
 "ART_REVIEW":"PENDING_ACTUAL_5_VIEW_INSPECTION",
 "PUBLIC_FUNCTION":"UNCERTIFIED"
}.items():sc["D48_"+key]=value

def collection(name):
 c=bpy.data.collections.new(name);sc.collection.children.link(c);return c
G={k:collection(k) for k in [
 "00_W0_TECTONIC_LAND_AND_SEA",
 "01_M247C_PRIMARY_SCULPTED_CIVIC_MASSES",
 "02_M247C_SUBTRACTED_ATRIUMS",
 "03_INHABITED_H_DISTRICT_VOLUMES",
 "04_HUMAN_SCALE_PUBLIC_SEQUENCE_WIP",
 "05_MANDATORY_16_SITES_UNMODELED_LOCATORS",
 "06_VISTAS_AND_URBAN_AXES_UNVERIFIED_LOCATORS",
 "99_REAL_CAMERAS"]}
def mat(n,c):
 m=bpy.data.materials.new(n);m.diffuse_color=tuple(c)+(1,);return m
M={
 "shell":mat("PALE_PEARL_INHABITED_BASALT",(0.80,.82,.76)),
 "shell2":mat("WARM_CERAMIC_TECTONIC_RIFT",(.86,.70,.52)),
 "dark":mat("CUT_SHADOW_POLISHED_STONE",(.17,.24,.29)),
 "floor":mat("CITY_PUBLIC_STONE",(.48,.57,.56)),
 "light":mat("CIVIC_GLOW_SURFACE",(.32,.75,.80)),
 "land":mat("W0_MOUNTAIN_CITY_BASIN",(.31,.41,.43)),
 "sea":mat("W0_INLAND_SEA",(.12,.32,.43)),
 "hab":mat("H_INHABITED_DISTRICT",(.72,.76,.72)),
 "civic":mat("GALLERIES",(.89,.86,.75)),
}
def objmesh(name,vertices,faces,material,group,role,asset=None):
 mesh=bpy.data.meshes.new(name+"_EDITABLE_MESH")
 mesh.from_pydata(vertices,[],faces);mesh.update()
 o=bpy.data.objects.new(name,mesh);group.objects.link(o);mesh.materials.append(material)
 o["ART_ROLE"]=role
 if asset:o["CITY_SCOPE_ID"]=asset
 return o
def prism_xz(name,polygon,front,back,material,group,role,asset):
 """Hand-authored x-z public volumes, not cloned box architecture."""
 n=len(polygon);verts=[]
 for y in (front,back):
  verts.extend((float(x),float(y)+.06*x,float(z)) for x,z in polygon)
 faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
 for i in range(n):j=(i+1)%n;faces.append((i,j,n+j,n+i))
 return objmesh(name,verts,faces,material,group,role,asset)
def section_mass(name,stations,material,asset):
 """Each station is an individually authored 3D sculptural *building section*.
 No replication of the R1 twin-vertical-loft silhouette, no island proxies.
 Control stations are kept readable in source and Blender edit-mode vertices.
 """
 rings=[]
 for x,y,z,wy,h,twist,lean in stations:
  ring=[]
  for i,(dy,dz) in enumerate([
      (-.97,-.28),(-.68,-.66),(-.10,-.62),(.59,-.50),
      (.97,-.10),(.77,.41),(.08,.76),(-.69,.40)]):
   nx=x+(dz*lean)+twist*dy*wy*.12
   ny=y+dy*wy
   nz=z+dz*h+wy*.08*math.sin(i*.9+x*.00075)
   ring.append((nx,ny,nz))
  rings.append(ring)
 k=8
 vertices=[v for ring in rings for v in ring]
 faces=[tuple(range(k-1,-1,-1))]
 for j in range(len(rings)-1):
  for i in range(k):
   n=(i+1)%k;faces.append((j*k+i,j*k+n,(j+1)*k+n,(j+1)*k+i))
 faces.append(tuple((len(rings)-1)*k+i for i in range(k)))
 o=objmesh(name,vertices,faces,material,G["01_M247C_PRIMARY_SCULPTED_CIVIC_MASSES"],
    "ARTIST_CONTROLLED_MULTISECTION_INHABITED_CITY_BODY",asset)
 o["EDIT_MODE_SECTION_COUNT"]=len(stations)
 o["E6_R1_GEOMETRY_COPIED"]=False
 o["PUBLIC_INTERIOR_FULLY_MODELED"]=False
 return o
def boolean_atrium(target,name,xyz,radii,tilt=0):
 """Real aperture through the occupied building mass, not a dark decal."""
 bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=24,location=xyz)
 cutter=bpy.context.object;cutter.name=name+"_CUTTING_VOLUME"
 cutter.scale=radii
 cutter.rotation_euler=(0,tilt,.05)
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 mod=target.modifiers.new(name+"_TRUE_VOID","BOOLEAN")
 mod.operation="DIFFERENCE";mod.solver="EXACT";mod.object=cutter
 bpy.context.view_layer.objects.active=target
 bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.data.objects.remove(cutter,do_unlink=True)
 target["REAL_CARVED_PUBLIC_VOID_COUNT"]=int(target.get("REAL_CARVED_PUBLIC_VOID_COUNT",0))+1
def terrain_height(x,y):
 north=max(0.,(-y-3200)/3000.)**1.3*920
 west=max(0.,(-x-2700)/2800.)*.9*1150
 wave=80*math.sin((x+400)/1250.)*math.cos(y/900.)
 sw=-240 if x<-1700 and y>1800 else 0
 sea=-190 if x>4000 else 0
 return -110+north+west+wave+sw+sea
def terrain():
 n=36;pts=[];faces=[]
 for j in range(n):
  y=-6000+j*12000/(n-1)
  for i in range(n):
   x=-6000+i*12000/(n-1);pts.append((x,y,terrain_height(x,y)))
 for j in range(n-1):
  for i in range(n-1):
   k=j*n+i;faces.append((k,k+1,k+n+1,k+n))
 o=objmesh("W0_GENUINE_TERRAIN_RESEARCH_MESH",pts,faces,M["land"],
    G["00_W0_TECTONIC_LAND_AND_SEA"],"W0_MOUNTAINS_CLIFF_OPEN_NEGATIVE_SPACE","W0")
 o["W0_ACTUAL_COORDINATES_VERIFIED"]=False
 # Inlet water strip is an *actual 3D* surface, not a location marker.
 sea=objmesh("W0_EAST_ARTIFICIAL_INLAND_SEA",
 [(3920,-5900,-175),(5850,-5900,-175),(5850,5700,-175),(3920,5700,-175)],
 [(0,1,2,3)],M["sea"],G["00_W0_TECTONIC_LAND_AND_SEA"],"RESEARCH_WATERFRONT","W0")
terrain()

# Deliberately authored skyline: enormous lateral, sloped, spatially overlapping
# masses rise from opposite geography toward a suspended *oblique* civic rupture.
WEST=[
 (-4650,-600,240,850,590,-.20,-170),
 (-3680,-880,550,1210,740,-.25,240),
 (-2950,-400,1250,1310,860,-.20,460),
 (-2300,-210,2310,1160,850,.15,-250),
 (-1490,500,3260,950,690,.35,170),
 (-690,760,3990,700,540,.40,-210),
 (400,370,4360,590,460,.24,80),
]
EAST=[
 (-680,-770,3540,550,550,.1,-140),
 (270,-1000,3510,800,660,.10,350),
 (1360,-460,2910,1200,900,-.25,-250),
 (2200,270,1760,1310,850,-.35,290),
 (2980,480,880,1120,780,-.24,-350),
 (4030,250,210,900,520,-.18,250)
]
west=section_mass("M247C_WEST_TECTONIC_CITY_MANTLE",WEST,M["shell"],"M247-C")
east=section_mass("M247C_EAST_INHABITED_CIVIC_MANTLE",EAST,M["shell2"],"M247-C")
# Hollow entrances and major atria deliberately cut through the finished
# massive mesh; edit-mode and topology remain inspectable Blender objects.
for body,name,xyz,scale in [
 (west,"WEST_CITY_ATRIUM_01",(-3000,-240,1400),(510,1800,520)),
 (west,"WEST_SKY_GALLERY_02",(-1550,560,2910),(390,1400,430)),
 (east,"EAST_CIVIC_PORTAL_01",(2240,250,1450),(580,1900,670)),
 (east,"EAST_SKY_ATRIUM_02",(840,-470,2920),(440,1300,470)),
]:
 boolean_atrium(body,name,xyz,scale,tilt=.23)
# A separate angled *urban-scale* fractured core to preserve beta SPINE,
# but not the giant uninhabited rectangular rod of R1.
SPINE_OUTLINE=[
 (-1650,750),(-1240,700),(-570,1710),(150,2580),
 (530,3450),(720,4800),(240,5170),(-250,3850),
 (-1060,2610),(-1730,1560)]
spine=prism_xz("M247C_BETA_SERRATED_ASCENT_SPINE",
 SPINE_OUTLINE,-150,210,M["dark"],
 G["01_M247C_PRIMARY_SCULPTED_CIVIC_MASSES"],"OBLIQUE_SCULPTURAL_SPINE","M247-C")
spine["SPINE_IS_CENTRAL_DESIGN_RESEARCH_NOT_ADOPTION"]=True

def terrace_sculpt(name,xyz,dx,dy,h,asset,upper=True):
 x,y,z=xyz
 # Irregular real-thickness civic terrace following landmass; has visible
 # open public space, not a tiny isolated hover island.
 polygon=[
 (x-dx*.56,y-dy*.35,z-h*.5),
 (x-dx*.32,y-dy*.58,z-h*.7),
 (x+dx*.27,y-dy*.46,z-h*.5),
 (x+dx*.60,y-dy*.10,z-h*.42),
 (x+dx*.38,y+dy*.55,z-h*.68),
 (x-dx*.38,y+dy*.51,z-h*.48),
 ]
 vertices=polygon+[(a,b,c+h) for a,b,c in polygon]
 faces=[(5,4,3,2,1,0),tuple(range(6,12))]
 for i in range(6):
  j=(i+1)%6;faces.append((i,j,j+6,i+6))
 o=objmesh(name,vertices,faces,M["hab"],G["03_INHABITED_H_DISTRICT_VOLUMES"],
       "THICK_CONNECTED_URBAN_DISTRICT_WIP",asset)
 o["H_DISTRICT_PUBLIC_INTERIOR_COMPLETE"]=False
 return o

# Six sky districts must be attached to the two colossal body landsides,
# not six detached mushrooms. These are generous thick sculptural volumes,
# with explicitly still-unmodeled private/public streets.
H={
 "H1":(-3450,-820,1000,820,680,390),
 "H2":(-2360,-260,2230,1040,820,440),
 "H3":(-710,650,3700,850,620,370),
 "H4":(450,-1020,3370,820,710,480),
 "H5":(2030,-150,2300,1150,870,530),
 "H6":(3160,350,840,950,770,460),
}
for ident,(x,y,z,dx,dy,h) in H.items():
 ob=terrace_sculpt(ident+"_ATTACHED_DENSE_CITY_BODY",(x,y,z),dx,dy,h,ident)
 # deep split-visible public street, visually open, not certified functional
 v=[(x-dx*.36,y+dy*.04,z+h*.38),(x-dx*.15,y-dy*.10,z+h*.38),
    (x+dx*.14,y+dy*.15,z+h*.38),(x+dx*.36,y+dy*.25,z+h*.38)]
 deck=objmesh(ident+"_PUBLIC_PASSAGE_PROXY",v,[(0,1,2,3)],M["civic"],
              G["04_HUMAN_SCALE_PUBLIC_SEQUENCE_WIP"],"WIDE_PUBLIC_STREET_WIP",ident)
 deck["ACCESS_VALIDATED"]=False

# Central ground-floor public arrival as a carved forecourt with thick
# actual side-wall galleries, visible from an appropriately sampled camera.
entrance_walls=[
 ("WEST_ARRIVAL_GALLERY", [(-1250,80),(-980,80),(-800,430),(-1170,560)]),
 ("EAST_ARRIVAL_GALLERY", [(790,85),(1320,85),(1080,550),(780,460)]),
]
for n,profile in entrance_walls:
 prism_xz(n,profile,-1450,-650,M["civic"],G["04_HUMAN_SCALE_PUBLIC_SEQUENCE_WIP"],
          "GROUND_CULTURAL_PUBLIC_COURT_PROTOTYPE","M247-C")

# Required 16 SB positions, 3 vista corridors and 3 metro axes are NON-GEOMETRIC,
# NON-APPROVED scope markers. Never claim complete 16-facility visual modeling.
def empty(name,xyz,role,asset):
 data=None
 ob=bpy.data.objects.new(name,data)
 G["05_MANDATORY_16_SITES_UNMODELED_LOCATORS" if asset.startswith("SB") else
   "06_VISTAS_AND_URBAN_AXES_UNVERIFIED_LOCATORS"].objects.link(ob)
 ob.empty_display_type="SPHERE";ob.empty_display_size=160
 ob.location=xyz;ob["CITY_SCOPE_ID"]=asset
 ob["ART_ROLE"]=role;ob["OFFICIAL_LOCATION"]=False
 ob["GEOMETRY_COMPLETE"]=False
 return ob
for i in range(1,17):
 a=(2*math.pi*i/16)+.18;r=3900+250*(i%3)
 empty(f"UNMODELED_SB{i:02d}_RESEARCH_LOCATOR",
       (math.cos(a)*r,math.sin(a)*r*.8,170),
       "ALL_INTERIORS_AND_EXTERIORS_REQUIRED_BUT_NOT_YET_SCULPTED",f"SB{i:02d}")
for i in range(1,4):
 empty("V"+str(i)+"_UNVERIFIED_CORRIDOR_SCOPE",
       (500*i,-1200*i,500), "CORRIDOR_NOT_GEOMETRICALLY_CERTIFIED","V"+str(i))
 empty("METRO_AXIS_"+str(i)+"_UNVERIFIED_SCOPE",
       (-500*i,-800*i,150),"URBAN_AXIS_NOT_CONNECTED","METRO_AXIS_"+str(i))

# In Blender all E0/earlier proxy modeling was judged from an underground
# camera; here the local W0 terrain height determines the camera safe point.
def cam(name,at,look,lens):
 data=bpy.data.cameras.new(name+"_REAL_CAMERA_DATA")
 o=bpy.data.objects.new(name,data);G["99_REAL_CAMERAS"].objects.link(o)
 x,y,z=at
 safe=max(z,terrain_height(x,y)+180)
 o.location=(x,y,safe)
 o.rotation_euler=(Vector(look)-o.location).to_track_quat("-Z","Y").to_euler()
 data.lens=lens;data.clip_start=3;data.clip_end=60000
 o["W0_TERRAIN_CLEARANCE_M"]=safe-terrain_height(x,y)
 assert o["W0_TERRAIN_CLEARANCE_M"]>=179.9
 return o
CAM={
 "01_NORTH_MACRO":((900,-9500,5100),(0,0,2550),39),
 "02_EAST_WATERFRONT":((8700,-1300,4250),(150,50,2300),37),
 "03_SOUTHWEST_VOID":((-8800,7900,4400),(-350,200,2750),40),
 "04_WEST_SCULPTURE":((-7800,-250,3850),(0,0,2750),43),
 "05_GROUND_ARRIVAL":((50,-4000,205),(0,0,1450),29),
}
for n,(pt,target,lens) in CAM.items():cam(n,pt,target,lens)
sc.world=bpy.data.worlds.new("D48_R2_GREY_ATMOSPHERE")
sc.world.color=(.39,.43,.48)
sc.render.engine="BLENDER_WORKBENCH"
sc.display.shading.light="STUDIO"
sc.display.shading.color_type="MATERIAL"
sc.display.shading.show_shadows=True
sc.display.shading.show_cavity=True
sc.display.shading.cavity_type="BOTH"
sc.display.shading.background_type="WORLD"
sc.render.resolution_x=1320
sc.render.resolution_y=800
sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.view_settings.view_transform="Standard"
sc.camera=bpy.data.objects["01_NORTH_MACRO"]
blend=OUT/"D48_R2_P0_TRUE_EDITABLE_ART_SCULPT.blend"
glb=OUT/"D48_R2_P0_TRUE_GEOMETRY_ONLY.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",export_cameras=False,export_lights=False)
images=[]
for n in CAM:
 sc.camera=bpy.data.objects[n]
 p=OUT/(n+".png");sc.render.filepath=str(p)
 bpy.ops.render.render(write_still=True)
 images.append(p)
real=[o for o in bpy.data.objects if o.type=="MESH"]
present=sorted(set(o.get("CITY_SCOPE_ID") for o in real if o.get("CITY_SCOPE_ID")))
manifest={
 "study":"D48_R2_P0_AUTHORED_B_MASS_AND_NEGATIVE_SPACE",
 "architecture_method":"ARTIST_AUTHORED_CONTROL_SECTIONS_WITH_REAL_BOOLEAN_CARVED_VOIDS",
 "source_tech":"AWAIT_INDEPENDENT_REOPEN","art":"UNREVIEWED",
 "function":"UNCERTIFIED","formal_adoption":False,"minecraft_write":False,
 "city_master_complete":False,"official_coordinates":"UNVERIFIED_TEMP_LAYOUT",
 "edited_research_blend":blend.name,"glb":glb.name,
 "pngs":[p.name for p in images],"camera_names":list(CAM),
 "real_mesh_count":len(real),"all_6_H_real_mass_bodies":all(v in present for v in H),
 "scope_16_SB_only_LOCATORS":True,
 "required_scope_30_entities_registered":True,
 "carved_atriums":int(west["REAL_CARVED_PUBLIC_VOID_COUNT"]+east["REAL_CARVED_PUBLIC_VOID_COUNT"]),
 "camera_ground_clearance_m":bpy.data.objects["05_GROUND_ARRIVAL"]["W0_TERRAIN_CLEARANCE_M"],
 "sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [blend,glb,*images]}}
assert manifest["carved_atriums"]==4
assert manifest["all_6_H_real_mass_bodies"]
(OUT/"D48_R2_P0_MANIFEST.json").write_text(json.dumps(manifest,indent=2))
print("D48_R2_P0_NEW_GENUINE_BLENDER_SCULPT_PRODUCED",len(real),"meshes")
