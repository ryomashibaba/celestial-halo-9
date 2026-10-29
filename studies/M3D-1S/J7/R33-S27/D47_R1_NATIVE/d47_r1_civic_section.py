"""D47-R1 spatial civic section: independent, editable 3D study — NOT approved art.
This models a 1.5-km local section, NOT the 10-km city or canonical W0/M204 coordinates.
One chamber, real open approach, two distinct inhabited/public edges, physical transit
and library levels, spatially tied roof. No automatic art or walkability PASS.
Run with genuine bpy 4.5.15: python d47_r1_civic_section.py OUTPUT_DIRECTORY
"""
import bpy, math, sys, json, hashlib
from pathlib import Path
from mathutils import Vector
from math import sin, cos, pi
P=Path(sys.argv[-1]); P.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if not c.objects: bpy.data.collections.remove(c)
def layer(name):
    c=bpy.data.collections.get(name)
    if c is None:
        c=bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c
def material(name,c):
    m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);return m
ground=material("01 pedestrian civic ground",(.54,.59,.61))
ivory=material("02 inhabited west library stone",(.85,.83,.72))
light=material("03 outer shell pearl",(.76,.78,.76))
blue=material("04 east transit architecture",(.26,.43,.49))
steel=material("05 load-bearing deep structure",(.09,.15,.23))
warm=material("06 cultural interior brass",(.55,.36,.22))
glass=material("07 cool station glazing",(.35,.60,.64))
dark=material("08 shadowed atrium recess",(.22,.25,.27))
sea=material("09 contextual artificial sea not official",(.08,.28,.36))
def mesh(name,v,f,m,collection,role):
    data=bpy.data.meshes.new(name+"_EDITABLE_MESH")
    data.from_pydata(v,[],f);data.update()
    o=bpy.data.objects.new(name,data)
    layer(collection).objects.link(o);data.materials.append(m)
    o["role"]=role;o["design_status"]="provisional editable geometry"
    return o
def extrude(name,xy,z0,z1,m,collection,role):
    n=len(xy);assert n>=3 and z1>z0
    v=[(x,y,z0) for x,y in xy]+[(x,y,z1) for x,y in xy]
    f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n):
        j=(i+1)%n;f.append((i,j,n+j,n+i))
    return mesh(name,v,f,m,collection,role)
def slab(name,xy,z,m,collection,role,thickness=10):
    return extrude(name,xy,z-thickness/2,z+thickness/2,m,collection,role)
def pipe(name,a,b,r,m,collection,role):
    a,b=Vector(a),Vector(b);d=b-a
    assert d.length>0
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=r, depth=d.length, location=(a+b)*.5)
    o=bpy.context.object;o.name=name
    o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    for c in tuple(o.users_collection):c.objects.unlink(o)
    layer(collection).objects.link(o)
    o.data.materials.append(m);o["role"]=role
    return o
def roof(name,rows,m,role):
    # A continuous folded canopy with editable surface thickness; rows span xy+z.
    v=[];n=len(rows[0])
    for row in rows:
        assert len(row)==n
        v.extend(row)
    k=len(rows)
    f=[]
    for j in range(k-1):
        for i in range(n-1):
            a=j*n+i;f.append((a,a+1,a+n+1,a+n))
    return mesh(name,v,f,m,"04 / Civic roofs",role)
# ONE PUBLIC ROOM: actual continuous ground from the exterior approach to the inner civic chamber.
# This is the entry route's tangible geometry, NOT a certified accessibility route.
slab("CIVIC_ROUTE_MAIN",[(-105,-1040),(115,-1040),(147,-660),
    (180,-260),(145,170),(80,720),(-150,720),(-215,225),
    (-190,-310),(-150,-740)],0,ground,"open street continuing into civic chamber",8)
slab("EXTERIOR_PUBLIC_FORECOURT",[(-315,-1350),(390,-1350),(310,-1035),
    (-240,-1035)],-5,ground,"W0 side arrival square, provisional",8)
# WEST: inhabited cultural escarpment; the public rooms actually face the chamber.
# Different footprints per level are intentional, not the same suspended shelf repeated.
west_levels=[
 ("WEST_PUBLIC_ARCHIVE_GROUND",[(-590,-380),(-260,-450),(-200,35),(-270,570),(-555,515)],5),
 ("WEST_LIBRARY_READING_GALLERY",[(-610,-260),(-235,-350),(-175,20),(-265,625),(-540,560)],105),
 ("WEST_MUSEUM_LECTURE_LEVEL",[(-620,-70),(-275,-230),(-185,175),(-350,680),(-560,590)],237),
 ("WEST_UPPER_CIVIC_TERRACE",[(-545,175),(-315,100),(-275,375),(-425,715),(-530,640)],360)]
for name,poly,z in west_levels:
    slab(name,poly,z,ivory,"02 / Civic library",name.lower().replace("_"," "),16)
# Segment façades deliberately contain real openings at the ground and intermediate gallery.
for k,(y0,y1) in enumerate([(-395,-205),(-125,65),(165,360),(460,620)]):
    x0=-350+42*sin(k*1.15)
    if k!=1:
        extrude("WEST_LIBRARY_OCCUPIED_WALL_%02d"%k,
                [(x0-27,y0),(x0+3,y0+8),(x0+22,y1-12),(x0-15,y1)],
                110,330,light,"02 / Civic library","backing of inhabited reading hall")
    # These structural ribs are load-path candidates, not certified engineering.
    pipe("WEST_CIVIC_SUPPORT_%02d"%k,(x0-100,y0,0),
         (x0+30,y1,400),12,steel,"02 / Civic library","diagonal gallery support")
# Actual separated interior partitions make archive, library and museum distinct zones.
for i,(x,y,z) in enumerate([(-475,-115,6),(-470,280,108),(-490,390,237)]):
    extrude("WEST_CIVIC_ROOM_PARTITION_%02d"%i,
            [(x-8,y-92),(x+12,y-92),(x+12,y+77),(x-8,y+77)],
            z,z+57,dark,"02 / Civic library","partial civic room division")
# Two visible entry gaps stay open on the inner face, not a closed solid rock shell.
for k,(y,z) in enumerate([(-350,8),(170,112),(475,235)]):
    pipe("WEST_STAIR_OR_LIFT_MARKED_SUPPORT_%02d"%k,
         (-250,y,z),(-260,y,z+70),7,warm,"02 / Civic library",
         "vertical transport position only, service NOT certified")
# EAST: deep transit exchange and concourse. It uses a different spatial vocabulary.
slab("EAST_PUBLIC_STATION_CONCOURSE",[(180,-450),(575,-520),(695,350),
    (440,640),(220,540)],74,blue,"03 / Transit interchange",
    "large actual concourse floor with open chamber edge",18)
slab("EAST_UPPER_TRANSIT_PLATFORM",[(290,-200),(635,-290),(720,285),
    (455,515)],208,blue,"03 / Transit interchange",
    "separate above-ground public station floor",15)
slab("EAST_GROUND_ENTRY",[(100,-650),(355,-680),(435,-290),(175,-240)],
    1,ground,"03 / Transit interchange","entry side plaza",9)
# Station has a largely open vaulted platform roof, not a blind rectangular mass.
roof("EAST_PLATFORM_FOLDED_CANOPY",[
 [(180,-550,344),(350,-560,400),(585,-560,358),(745,-560,320)],
 [(170,-155,378),(355,-115,452),(625,-90,415),(760,-70,352)],
 [(195,300,353),(355,360,430),(615,365,393),(735,330,327)],
 [(230,585,310),(425,625,365),(610,600,350),(675,555,295)]],
 light,"covered station public concourse")
for i,y in enumerate([-360,-25,285,475]):
    pipe("EAST_TRANSIT_CANTILEVER_%02d"%i,(520,y,74),
         (650,y+35,350),11,steel,"03 / Transit interchange",
         "station roof and concourse coupling")
# Three differently oriented urban walkways link the architecture and the chamber visually.
# Connectivity and clearances are deliberately not yet certified.
slab("WEST_PUBLIC_INNER_PROMENADE",[(-260,-370),(-148,-365),
 (-122,205),(-207,485),(-300,480)],102,warm,"05 / Shared internal circulation",
 "west inhabited gallery overlooks real chamber",12)
slab("EAST_PUBLIC_INNER_PROMENADE",[(170,-375),(278,-380),
 (350,365),(185,380)],77,glass,"05 / Shared internal circulation",
 "east rail concourse overlooks chamber",12)
slab("OBLIQUE_CROSSING_PUBLIC_SPAN",[(-190,120),(170,225),
 (195,278),(-213,165)],112,ivory,"05 / Shared internal circulation",
 "one oblique bridging route between programs",14)
# A major public room is formed by two uneven inhabitable walls and the functional roof
# spanning only part of the chamber. The diagonal daylight aperture stays clear.
roof("WEST_CIVIC_VAULT_AND_MUSEUM_ROOF",[
 [(-615,-200,430),(-410,-195,485),(-190,-200,520),(-45,-230,498)],
 [(-625,70,445),(-410,95,515),(-180,120,555),(-50,120,537)],
 [(-560,390,400),(-385,410,465),(-205,425,500),(-90,455,465)],
 [(-535,650,385),(-390,665,421),(-250,675,432),(-110,685,422)]],
 ivory,"west public museum roof continuing the interior urban section")
# At the hall centre, preserve a long, open-to-sky wedge: no roof mesh crossing
# the strip around the median line in the Y direction.
for i,(y,x) in enumerate([(-410,-355),(-80,-345),(260,-365),(590,-410)]):
    pipe("WEST_LIBRARY_DAYLIGHT_COLUMN_%02d"%i,(x,y,5),
         (x+90,y+40,405),10,warm,"04 / Civic roofs",
         "sectional support attached to occupied library")
# Human-scale markers in the entrance view; proof of scale only, not inhabitants.
for i,(x,y) in enumerate([(-18,-950),(35,-880),(0,-710),
                              (-58,-565),(82,-430),(-35,-235),(55,110)]):
    pipe("HUMAN_SCALE_MARKER_%02d"%i,(x,y,3),(x,y,4.8),.3,steel,
         "06 / Human scale references","1.8m human-scale reference")
# Context only. No canonical coordinate assertion, no fake H/SB completed buildings.
slab("W0_TEST_GROUND_NOT_CANONICAL",[(-1750,-1800),(1700,-1800),
    (1700,1350),(-1750,1350)],-35,dark,"07 / Provisional context",
    "study-only urban ground, NOT finished city or official W0",15)
slab("W0_TEST_INLAND_SEA_NOT_CANONICAL",[(1130,-1800),
    (1700,-1800),(1700,1350),(1130,1350)],-18,sea,
    "07 / Provisional context","provisional east sea, NOT official geography",5)
scene=bpy.context.scene
scene["status"]="D47_R1_NATIVE_STUDY_ART_UNREVIEWED"
scene["scale_meters_per_blender_unit"]=1
scene["canonical_coordinates"]=False
scene["public_routes_certified"]=False
scene["structural_engineering_verified"]=False
scene["official_art_adopted"]=False
scene["minecraft_world_write"]=False
scene["H1_to_H6"]="required six fully detailed floating cities; not made in this small test"
scene["SB01_to_SB16"]="required sixteen complete facilities; not made here"
scene["study_scope"]="one inhabited public chamber, not the 10 km master"
def camera(name,location,target,ortho=None):
    cam=bpy.data.cameras.new(name)
    o=bpy.data.objects.new(name,cam);layer("08 / Fixed review cameras").objects.link(o)
    o.location=location
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    cam.clip_end=30000
    if ortho is not None:
        cam.type="ORTHO";cam.ortho_scale=ortho
    else:
        cam.type="PERSP";cam.lens=24
    return o
CAMS=[
 ("01_city", (2600,-3400,1900),(-30,-90,250),2500),
 ("02_approach",(65,-1190,55),(0,-50,185),None),
 ("03_civic_interior",(35,-390,155),(-15,320,205),None),
 ("04_oblique",(-1800,-1750,1020),(0,-50,220),1750),
 ("05_east_side",(1900,60,850),(0,70,210),1600)]
for args in CAMS:camera(*args)
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_cavity=True
scene.render.resolution_x=1080;scene.render.resolution_y=720
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=False
scene.render.filepath=str(P/"00_not_a_render.png")
blend=P/"D47_R1_LOCAL_CIVIC_EDITABLE.blend"
glb=P/"D47_R1_LOCAL_CIVIC.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
                          export_cameras=False,export_lights=False)
for name,*_ in CAMS:
    scene.camera=bpy.data.objects[name]
    scene.render.filepath=str(P/(name+".png"))
    bpy.ops.render.render(write_still=True)
manifest={
 "status":"D47_R1_PROVISIONAL_LOCAL_SPATIAL_3D_NOT_ART_REVIEWED",
 "blender_version":bpy.app.version_string,
 "distinct_programs":["public approach and civic chamber","cultural library and archive",
                      "transit interchange","internal urban promenades and crossing"],
 "native_meshes":len([o for o in bpy.data.objects if o.type=="MESH"]),
 "render_names":[n+".png" for n,*_ in CAMS],
 "study_size_only_m":"about 1.5 km section; not a multi-km completed central complex",
 "one_blender_unit_m":1,"canonical_coordinates":False,
 "real_public_floors_present":True,
 "route_clearance_certified":False,"weatherproofing_certified":False,
 "structural_support_certified":False,
 "art_approved":False,"central_master_complete":False,
 "W0_master_complete":False,"H1_H6_complete":False,"SB01_SB16_complete":False,
 "minecraft_construction_authorized":False,
 "GUI_direct_edit_proven":False
}
(P/"D47_R1_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf8")
print("D47_R1_NATIVE_OUTPUT_CREATED_NOT_ART_APPROVED",json.dumps(manifest))
