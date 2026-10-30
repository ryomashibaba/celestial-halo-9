"""D48 R3 G2 | MAJOR FORM RESET: a populated open civic rift, not a tower/island/box generator.
True Blender editable art study. The previous R3-G1 rejected mesh is NOT used.
No city-master claim: 10km integrated context is research local coords; only W0,
M247-C and H1-H6 are partially modeled; SB01-16 are ONLY unmodeled locators.
Author specified irregular inner/outer terrain-city section contours. Assess by
actual 7 camera visual inspection before any further detailing or adoption.
python g2_authored_tectonic_civic_city.py OUTPUT_DIR
"""
import bpy, math, json, hashlib, sys
from pathlib import Path
from mathutils import Vector

OUT=Path(sys.argv[-1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
SC=bpy.context.scene
SC.name="D48_R3_G2_DEEP_CIVIC_RIFT_URBAN_SECTION_RESEARCH_NOT_ADOPTED"
for k,v in {"ART":"AWAIT_TRUE_7_CAMERA_INSPECTION","SOURCE_STATUS":"EDITABLE_RESEARCH",
 "OFFICIAL_COORDINATES":False,"CITY_MASTER_COMPLETE":False,
 "FORMAL_ADOPTED":False,"MINECRAFT_WRITTEN":False,"FULL_H_AND_SB_DETAILS":False}.items():
 SC["D48_"+k]=v

def group(name):
 c=bpy.data.collections.new(name);SC.collection.children.link(c);return c
C={s:group(s) for s in ["00_W0_GEOLOGY","01_M247C_WEST_INHABITED_CLIFF",
 "02_M247C_EAST_INHABITED_CLIFF","03_PUBLIC_STREETS_AND_CANYON",
 "04_H1_H6_INHABITED_SKY_SECTIONS_WIP",
 "05_CULTURAL_PROGRAM_INTERIORS_WIP",
 "06_SCOPE_ONLY_UNBUILT_MARKERS",
 "07_TRUE_CAMERA_RIG"]}
def mat(name,color):
 m=bpy.data.materials.new(name);m.diffuse_color=tuple(color)+(1,);return m
M={
 "chalk":mat("IVORY_TECTONIC_ARCHITECTURAL_CLIFF",(.79,.80,.73)),
 "bronze":mat("SUNLIT_CERAMIC_SANDSTONE",(.78,.63,.48)),
 "shadow":mat("DEEP_CIVIC_VOIDS_GRAPHITE",(.16,.22,.25)),
 "civic":mat("PUBLIC_STREETS_PALE_STONE",(.75,.69,.58)),
 "garden":mat("SKY_GARDEN_EMBEDDED",(.26,.44,.35)),
 "city":mat("INHABITED_SHELL_CITY_TAN",(.59,.68,.64)),
 "light":mat("RESEARCH_CIVIC_DAYLIGHT_BLUE",(.23,.67,.71)),
 "land":mat("W0_REAL_EDITABLE_TERRAIN",(.34,.40,.38)),
 "water":mat("W0_EAST_INLAND_SEA",(.17,.36,.42)),
}
def mesh(name,verts,faces,material,coll,role,asset):
 m=bpy.data.meshes.new(name+"_EDITABLE_GEOMETRY")
 m.from_pydata(verts,[],faces);m.update()
 ob=bpy.data.objects.new(name,m);coll.objects.link(ob)
 m.materials.append(material);ob["CITY_ASSET_ID"]=asset
 ob["ART_ROLE"]=role;ob["ART_ADOPTED"]=False
 return ob
def profile_solid(name,poly,y0,y1,ma,co,role,asset):
 n=len(poly)
 v=[(x,y0,z) for x,z in poly]+[(x,y1,z) for x,z in poly]
 f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
 f.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
 return mesh(name,v,f,ma,co,role,asset)
def city_terrain(x,y):
 # x east, y north — all in a temporary artist scene, NOT official.
 north=920*max(0,(y-2400)/3000)**1.33
 west=980*max(0,(-x-2900)/2850)**1.13
 sw=-260 if x<-2200 and y<-1600 else 0
 se=-200 if x>4400 else 0
 return north+west+75*math.sin(x/1800+.7)*math.cos(y/1350-.3)+sw+se
def terrain():
 n=48;v=[];f=[]
 for j in range(n):
  y=-6200+j*12400/(n-1)
  for i in range(n):
   x=-6200+i*12400/(n-1);v.append((x,y,city_terrain(x,y)))
 for j in range(n-1):
  for i in range(n-1):
   k=j*n+i;f.append((k,k+1,k+n+1,k+n))
 mesh("W0_URBAN_GEOLOGICAL_BASIN",v,f,M["land"],C["00_W0_GEOLOGY"],
     "NORTH_PLATEAU_WEST_CLIFF_SOUTHWEST_NEGATIVE_SPACE_WIP","W0")
 mesh("W0_EAST_INLAND_SEA_SURFACE",
      [(4500,-6200,-165),(6200,-6200,-165),(6200,6200,-165),(4500,6200,-165)],
      [(0,1,2,3)],M["water"],C["00_W0_GEOLOGY"],"ARTIFICIAL_INLAND_SEA_WIP","W0")
terrain()

# PRIMARY AUTHOR-DRAWN URBAN SECTION (central "rift" open to sky). Each
# station is [north_y, ground_inner_x, inner_upper_offset,
# outer_lower_offset, upper_height, axial_shear]. East and west profiles are
# intentionally profoundly unequal: one deep carved continent, one coastal
# tilted mantle. NOT two lofted vertical towers.
WEST_SECTIONS=[
 (-3050,760,-420,950,900,-290),
 (-2470,800,-140,920,1450,-320),
 (-1750,700,-550,1170,2550,-220),
 (-900,650,-910,1540,3230,-90),
 (200,630,-1160,1680,4000,140),
 (1100,880,-780,1430,3760,310),
 (1850,890,-430,1020,2400,260),
 (2650,760,60,730,1330,160),
 (3200,900,140,660,850,70)
]
EAST_SECTIONS=[
 (-3140,750,80,670,710,220),
 (-2580,830,270,840,1200,350),
 (-1830,850,180,1120,1550,180),
 (-1120,760,330,1310,2200,-20),
 (-100,720,760,1280,2870,-260),
 (900,690,490,1220,3310,-320),
 (1700,740,620,1100,2740,-170),
 (2640,950,250,890,1850,110),
 (3260,1020,-90,630,980,210)
]
def sculpted_mantle(name,sections,side,material,co):
 """Hand-directed watertight solid between two independent canyon/outer faces.
 Each y station has a nonlinear 3D vertical sectional stroke from original
 artist values; width and slope built per station, not a repeated box array.
 Surfaces are kept genuinely mesh-editable in Blender."""
 n=len(sections);k=19;V=[]
 def p(section,t,outer):
  y,inner,top_shift,thickness,high,shear=section
  # top crest belongs to the inhabited surface rather than a linear "tower".
  # Oriented offset includes a diagonal interrupted cut-like shear.
  yy=y+shear*(t**1.55)+65*math.sin(t*math.pi*2+y*.0002)
  d=inner+top_shift*(t**1.2)+65*math.sin(t*math.pi*1.7+y*.0006)
  if outer:d+=thickness*(.72+.28*t)+55*math.sin(t*math.pi*1.2)
  z=70+high*t+40*math.sin(t*math.pi+y*.0005)
  return (side*d,yy,z)
 # order: inner surface, outer surface
 for outer in (False,True):
  for sec in sections:
   for j in range(k):
    V.append(p(sec,j/(k-1),outer))
 def at(outer,i,j):return (n*k if outer else 0)+i*k+j
 F=[]
 for outer in (False,True):
  for i in range(n-1):
   for j in range(k-1):
    q=[at(outer,i,j),at(outer,i+1,j),at(outer,i+1,j+1),at(outer,i,j+1)]
    F.append(tuple(reversed(q)) if outer else tuple(q))
 for i in range(n-1):
  F.append((at(False,i,0),at(True,i,0),at(True,i+1,0),at(False,i+1,0)))
  F.append((at(False,i,k-1),at(False,i+1,k-1),at(True,i+1,k-1),at(True,i,k-1)))
 for j in range(k-1):
  F.append((at(False,0,j),at(False,0,j+1),at(True,0,j+1),at(True,0,j)))
  F.append((at(False,n-1,j),at(True,n-1,j),at(True,n-1,j+1),at(False,n-1,j+1)))
 ob=mesh(name,V,F,material,co,"TRUE_SOLID_SHELTERING_INHABITED_RIFT_CLIFF", "M247-C")
 ob["SECTION_CONTROLS"]=json.dumps(sections)
 ob["NO_IMPORT_FROM_REJECTED_R3_G1"]=True
 ob["REAL_MESH_EDITABLE"]=True
 # Smooth over authored y station transitions only enough to eliminate block
 # corners. Keep original editable mesh non-destructive.
 mod=ob.modifiers.new("D48_G2_SUBDIVIDED_HAND_SCULPT","SUBSURF")
 mod.subdivision_type="CATMULL_CLARK";mod.levels=2;mod.render_levels=2
 return ob
west=sculpted_mantle("M247C_WEST_DEEP_INHABITED_CLIFF",WEST_SECTIONS,-1,M["chalk"],C["01_M247C_WEST_INHABITED_CLIFF"])
east=sculpted_mantle("M247C_EAST_ASCENDING_COASTAL_MANTLE",EAST_SECTIONS,1,M["bronze"],C["02_M247C_EAST_INHABITED_CLIFF"])

# Down-center public void is intentionally kept BIG/OPEN.
# Real city ground is continuous with approach; no giant panel suspended over it.
def plaza(name,poly,height,mat,role):
 # 24 m thick polygonal occupation, urban street-level stone not proxy tube.
 top=[(x,y,height) for x,y in poly];bottom=[(x,y,height-24) for x,y in poly]
 n=len(poly);fs=[tuple(range(n)),tuple(reversed(range(n,2*n)))]
 fs.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
 return mesh(name,top+bottom,fs,mat,C["03_PUBLIC_STREETS_AND_CANYON"],role,"M247-C")
plaza("CANYON_CITY_PUBLIC_ARRIVAL",
 [(-520,-3100),(430,-3150),(580,-1500),(-540,-1430)],74,M["civic"],"OPEN_CIVIC_STREET_WIP")
plaza("CANYON_MAIN_NAVE",
 [(-580,-1470),(590,-1490),(570,480),(-570,560)],77,M["civic"],"CULTURAL_PUBLIC_NAVE_WIP")
plaza("CANYON_UPPER_ARCHIVE_FORUM",
 [(-560,540),(510,530),(490,1950),(-610,1960)],83,M["civic"],"DEEP_PUBLIC_ARCHIVE_WIP")
plaza("CANYON_NORTH_PUBLIC_TERRACE",
 [(-570,1920),(470,1930),(500,3120),(-510,3130)],88,M["civic"],"DEEP_PUBLIC_CITY_EXTENSION_WIP")
# Direct multi-level route uses intentionally huge thick streets and mass.
# Two volumes connect asymmetric cliffs and public void, but these are not
# thin spans or 'white line' city transportation.
def artist_terrace(name,poly,z,depth,material,coll,asset,role):
 n=len(poly);top=[(x,y,z) for x,y in poly];low=[(x,y,z-depth) for x,y in poly]
 faces=[tuple(range(n)),tuple(reversed(range(n,2*n)))]
 faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
 ob=mesh(name,top+low,faces,material,coll,role,asset)
 ob["PUBLIC_FUNCTION_VALIDATED"]=False
 return ob

# Six sky cities must be visibly anchored to their separate canyon sides.
# Each city is a distinct authored 2D public urban shape, terraced in 3D.
# An individual section has inhabited thickness; still requires full details.
H=[
 ("H1",-1,(-1360,-2150,790),[(-1890,-2720),(-850,-2550),(-680,-1600),(-1780,-1420)],390),
 ("H2",-1,(-1530,-800,1710),[(-2100,-1310),(-950,-1220),(-770,-250),(-2030,-160)],470),
 ("H3",-1,(-1850,500,2900),[(-2250,-120),(-960,-20),(-720,940),(-2300,1150)],520),
 ("H4",1,(1560,-1660,960),[(790,-2240),(2200,-2370),(2430,-1300),(890,-1250)],430),
 ("H5",1,(1720,-180,1860),[(920,-720),(2300,-990),(2520,190),(830,340)],560),
 ("H6",1,(1630,1270,2450),[(800,720),(2260,600),(2550,1940),(950,2050)],510),
]
for asset,side,center,outline,thick in H:
 x,y,z=center
 terrace=artist_terrace(asset+"_THICK_CITY_INHABITED_STRATUM",
                        outline,z,thick,M["city"],C["04_H1_H6_INHABITED_SKY_SECTIONS_WIP"],
                        asset,"THICK_INHABITED_CITY_BODY_NOT_OMNISCIENT")
 # Multiple intersecting actual civic terraces form a section, not floating
 # islands and not 6 equal little platforms with a few cubic towers.
 side_extension=[(xx+(120 if side==1 else -120),yy+40) for xx,yy in outline]
 artist_terrace(asset+"_PUBLIC_GALLERY_01",side_extension,z-160,22,
                M["civic"],C["04_H1_H6_INHABITED_SKY_SECTIONS_WIP"],asset,
                "PUBLIC_GALLERY_UNVERIFIED_WALKABILITY")
 # Author-specific irregular spatial promenade cuts; real volumes at multiple
 # altitudes, do not claim connection validated.
 for level in (1,2):
  shift=level*85
  in_poly=[(xx-(side*shift)*.75,yy+level*65) for xx,yy in outline]
  artist_terrace(asset+f"_CIVIC_GALLERY_{level+1:02d}",in_poly,z+level*115,18,
                 M["civic"],C["04_H1_H6_INHABITED_SKY_SECTIONS_WIP"],asset,
                 "CULTURAL_STREET_VOLUME_RESEARCH_ONLY")
 # Large openings for public gathering between edges; no repetition of boxhouses
 # while macro remains unacceptable.
 terrace["FULL_INTERIOR_DESIGNED"]=False
 terrace["ACTUAL_OFFICIAL_SITE_COORDINATE"]=False

# Embedded cultural masses are genuinely open courts in the civic canyon.
# The public hall floors touch the city floor and are not floating cube cubbies.
for i,(asset,outline,z) in enumerate([
 ("M247-C",[(-610,-980),(-350,-1290),(-160,-880),(-230,-410),(-560,-280)],90),
 ("M247-C",[(310,100),(530,-80),(630,450),(180,700),(160,330)],105),
 ("M247-C",[(-620,1090),(-300,900),(-170,1540),(-530,1780)],125)]):
 artist_terrace(f"CIVIC_ARCHIVE_LIBRARY_COURT_{i}",outline,z,65,M["bronze"],
                C["05_CULTURAL_PROGRAM_INTERIORS_WIP"],asset,
                "CITY_CULTURAL_HALL_TRUE_FLOOR_NOT_FULL_INTERIOR")
# Sculpted beta characteristic = slanted *negative* public sky rift, not a rod.
# An open slanted cut in a real high-level suspended civic terrace, with
# two dislocated massive halves at different z. Both are real urban floors.
artist_terrace("BETA_SKY_FRACTURE_WEST_CITY",
 [(-2150,-155),(-280,40),(-450,520),(-2310,340)],2870,290,
 M["chalk"],C["03_PUBLIC_STREETS_AND_CANYON"],"M247-C",
 "MASSIVE_DISLOCATED_INHABITED_SKY_CITY_SHEAR")
artist_terrace("BETA_SKY_FRACTURE_EAST_CITY",
 [(350,190),(2090,-250),(2180,550),(510,900)],3160,365,
 M["bronze"],C["03_PUBLIC_STREETS_AND_CANYON"],"M247-C",
 "MASSIVE_DISLOCATED_INHABITED_SKY_CITY_SHEAR")
# The genuinely open gap between the two slabs is the spatial beta spine.
# Do not insert a black stick / beam there; it's architectural NEGATIVE SPACE.

# Required scope, always honest. Not modeled structures.
def marker(asset,xyz):
 ob=bpy.data.objects.new("UNBUILT_"+asset,None);C["06_SCOPE_ONLY_UNBUILT_MARKERS"].objects.link(ob)
 ob.location=xyz;ob.empty_display_type="SPHERE";ob.empty_display_size=85
 ob["CITY_ASSET_ID"]=asset;ob["FULL_REAL_GEOMETRY"]=False
 ob["CANONICAL_COORDINATES_CONFIRMED"]=False
for i in range(1,17):
 angle=2*math.pi*i/16
 marker(f"SB{i:02d}",(4000*math.cos(angle),4000*math.sin(angle),120))
for i in range(1,4):
 marker("V"+str(i),(-3900+i*1200,-3400,250))
 marker("METRO_AXIS_"+str(i),(2200-i*700,-3500,250))

def camera(name,xyz,target,lens):
 data=bpy.data.cameras.new(name+"_LENS");ob=bpy.data.objects.new(name,data)
 C["07_TRUE_CAMERA_RIG"].objects.link(ob)
 ob.location=xyz;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat("-Z","Y").to_euler()
 data.clip_start=.4;data.clip_end=60000;data.lens=lens
 return ob
cams=[
 ("01_WEST_NORTH_MACRO",(-7900,7200,3900),(0,-100,2100),39),
 ("02_EAST_SEA_MACRO",(9000,700,3900),(0,-250,1900),38),
 ("03_SOUTHWEST_VOID",(-8600,-7900,4800),(0,-250,2000),38),
 ("04_CITY_REAR_NORTH",(1200,8800,4400),(0,-200,2100),39),
 ("05_OPEN_CIVIC_CANYON_EYE",(0,-2900,82),(0,-200,650),22),
 ("06_CANYON_PUBLIC_SECTION",(-250,-600,84),(250,1400,850),24),
 ("07_H3_SKY_CITY_EYE",(-1610,460,2901.7),(250,1100,3050),26)]
for n,xyz,t,l in cams:camera(n,xyz,t,l)
SC.world=bpy.data.worlds.new("G2_CINEMATIC_NEUTRAL_DAYLIGHT")
SC.world.color=(.45,.53,.60)
SC.render.engine="BLENDER_WORKBENCH"
SC.display.shading.light="STUDIO"
SC.display.shading.color_type="MATERIAL"
SC.display.shading.show_shadows=True
SC.display.shading.show_cavity=True
SC.display.shading.cavity_type="BOTH"
SC.display.shading.background_type="WORLD"
SC.view_settings.view_transform="Standard"
SC.render.resolution_x=1360;SC.render.resolution_y=820
SC.render.resolution_percentage=100;SC.render.image_settings.file_format="PNG"
SC.camera=bpy.data.objects[cams[0][0]]
blend=OUT/"D48_R3_G2_AUTHORED_CIVIC_RIFT_REAL_NATIVE.blend"
glb=OUT/"D48_R3_G2_AUTHORED_CIVIC_RIFT_REAL_GEOMETRY.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",export_cameras=False,export_lights=False)
imgs=[]
for n,_,_,_ in cams:
 SC.camera=bpy.data.objects[n];p=OUT/(n+".png");SC.render.filepath=str(p)
 bpy.ops.render.render(write_still=True);imgs.append(p)
real=[ob for ob in bpy.data.objects if ob.type=="MESH"]
ids={ob.get("CITY_ASSET_ID") for ob in real if ob.get("CITY_ASSET_ID")}
assert all(f"H{i}" in ids for i in range(1,7))
assert ids.issuperset({"W0","M247-C"})
assert len([ob for ob in bpy.data.objects if ob.type=="CAMERA"])==7
report={
 "design":"D48_R3_G2_MANUALLY_AUTHORED_TECTONIC_CIVIC_RIFT",
 "method":"AS_YMMETRICAL_HAND_AUTHORED_SECTIONS_PLUS_PUBLIC_STREET_FLOORS",
 "source_origin":"NO_GEOMETRY_IMPORTED_FROM_P1_P2_R3_G1_ART_REJECT",
 "official_coordinates":"UNVERIFIED_LOCAL_ART_STUDY",
 "formal_adoption":False,"minecraft_write":False,"city_master_complete":False,
 "art":"UNREVIEWED","real_mesh_count":len(real),
 "present_mandatory_real_partial_entities":sorted(ids),
 "unmodeled_SB01_SB16_LOCATORS":True,
 "H1_H6_ENTIRE_DETAIL":"NOT_COMPLETE",
 "public_circulation":"NOT_FUNCTION_VALIDATED",
 "camera_count":len(cams),"camera_names":[x[0] for x in cams],
 "files":{"blend":blend.name,"glb":glb.name,"images":[p.name for p in imgs]},
 "sha256":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [blend,glb,*imgs]}}
(OUT/"D48_R3_G2_NATIVE_MANIFEST.json").write_text(json.dumps(report,indent=2,ensure_ascii=False))
print("D48_G2_TRUE_3D_ART_STUDY_GENERATED",report["real_mesh_count"],flush=True)
