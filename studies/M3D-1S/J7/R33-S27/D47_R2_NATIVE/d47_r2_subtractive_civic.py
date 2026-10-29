"""D47-R2 — TRUE CARVED CIVIC VOLUME, exploratory spatial production method.
Art NOT reviewed. M247-C direction protected. Not canonical W0; no Minecraft writes.
The main roof, inhabited thickness and interior voids are ONE REAL Boolean-cut volume,
rather than detached slab/roof/column stage scenery. Editable cutters remain in BLEND.
Real Blender 4.5.15: python d47_r2_subtractive_civic.py OUTPUT_DIRECTORY
"""
import bpy, sys, json, math, hashlib
from pathlib import Path
from mathutils import Vector
P=Path(sys.argv[-1]);P.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
def collection(name):
    c=bpy.data.collections.get(name)
    if c is None:
        c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c)
    return c
def move(o,name):
    for c in tuple(o.users_collection):c.objects.unlink(o)
    collection(name).objects.link(o)
    return o
def mat(name,rgb):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);return m
ivory=mat("01 mother civic volume ivory",(.77,.78,.72))
shade=mat("02 cut interior stone",(.22,.30,.37))
public=mat("03 pale pedestrian surface",(.74,.70,.59))
station=mat("04 ocean station blue",(.27,.46,.53))
archive=mat("05 inhabited archive copper",(.59,.40,.29))
plaza=mat("06 low-context urban ground",(.32,.36,.37))
sea=mat("07 study-only water",(.08,.25,.32))
def mesh(name,verts,faces,m,group,role):
    me=bpy.data.meshes.new(name+"_EDITABLE")
    me.from_pydata(verts,[],faces);me.update()
    o=bpy.data.objects.new(name,me)
    collection(group).objects.link(o);o.data.materials.append(m)
    o["architectural_role"]=role
    return o
def closed_section(name):
    # Author-designed, convex eight-point x/z profile; front and rear unequal.
    # A test carrier for real inhabited voids: not an approved sculpture.
    profile=[(-470,-30),(490,-30),(505,95),(430,292),
             (260,455),(-85,545),(-365,397),(-505,167)]
    stations=[
       (-665,-55,-25,.92,.93),
       (-135,-25,0,1.00,1.00),
       (220,35,-10,1.10,1.06),
       (675,105,-35,.84,.87)]
    verts=[]
    for y,offset,vertical,sx,sz in stations:
        for x,z in profile: verts.append((x*sx+offset,y,z*sz+vertical))
    n=len(profile);N=len(stations)
    faces=[tuple(range(n))]
    for k in range(N-1):
        for i in range(n):
            j=(i+1)%n
            faces.append((k*n+j,k*n+i,(k+1)*n+i,(k+1)*n+j))
    faces.append(tuple(range((N-1)*n,N*n))[::-1])
    return mesh(name,verts,faces,ivory,"01 REAL CONTINUOUS MOTHER VOLUME",
                "single thick civic architecture to carve actual connected rooms")
mass=closed_section("R2_SINGLE_INHABITED_MOTHER_CARVED_VOLUME")
cutters=[]
def sphere(name,center,scale):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=center)
    o=bpy.context.object;o.name="CUTTER_"+name
    o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    move(o,"02 EDITABLE BOOLEAN ROOM AND SKY CUTTERS");cutters.append(o)
    return o
def box(name,loc,scale,rotation=0):
    bpy.ops.mesh.primitive_cube_add(size=2,location=loc)
    o=bpy.context.object;o.name="CUTTER_"+name
    o.scale=scale;o.rotation_euler[1]=rotation
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    move(o,"02 EDITABLE BOOLEAN ROOM AND SKY CUTTERS");cutters.append(o)
    return o
sphere("01_CHAMBER_ACTUAL_VAULT",(0,-5,245),(305,420,195))
box("02_PUBLIC_ENTRY_THROUGH_FACADE",(0,-447,126),(128,305,113))
sphere("03_WEST_CULTURAL_INTERIOR",(-310,110,180),(180,262,130))
sphere("04_EAST_RAIL_INTERCHANGE",(328,75,180),(186,275,137))
box("05_NORTH_TRUE_PUBLIC_EXIT",(0,487,128),(120,245,93))
sphere("06_WEST_UPPER_ARCHIVE",(-305,163,322),(125,185,81))
# Actual vertical shaft connects occupied east/west levels but lift service remains unverified.
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=39,depth=305,
    location=(-315,145,200))
shaft=bpy.context.object;shaft.name="CUTTER_07_WEST_SHARED_VERTICAL_SHAFT"
move(shaft,"02 EDITABLE BOOLEAN ROOM AND SKY CUTTERS");cutters.append(shaft)
# Daylight slot is cut into the same physical roof volume, rather than placing
# a nonstructural decorative roof object above an empty space.
box("08_ASYMMETRIC_DAYLIGHT_RIFT",(40,145,498),(84,205,166),.14)
# Entry and two adjacent chambers are connected by overlap of actual subtracted solids.
for cutter in cutters:
    bpy.ops.object.select_all(action="DESELECT")
    mass.select_set(True);bpy.context.view_layer.objects.active=mass
    modifier=mass.modifiers.new("REAL_SPACE_CUT_"+cutter.name,"BOOLEAN")
    modifier.operation="DIFFERENCE";modifier.solver="EXACT";modifier.object=cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    cutter.hide_render=True;cutter.hide_set(True)
mass["authored_subtractions"]=[c.name for c in cutters]
mass["not_art_adopted"]=True
def prism(name,poly,zlo,zhi,m,group,role):
    n=len(poly);v=[(x,y,zlo) for x,y in poly]+[(x,y,zhi) for x,y in poly]
    f=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n):
        j=(i+1)%n;f.append((i,j,n+j,n+i))
    return mesh(name,v,f,m,group,role)
def slab(name,poly,z,th,m,role):
    return prism(name,poly,z-th/2,z+th/2,m,
       "03 INHABITABLE FLOOR AND CONNECTION GEOMETRY",role)
# Here the floors belong to carved occupied rooms rather than roof shelves.
slab("PUBLIC_ENTRY_REAL_FLOOR",[(-98,-690),(100,-690),
    (103,-210),(-102,-210)],85,13,public,
    "physically inside subtracted entrance tunnel")
slab("CHAMBER_MAIN_PUBLIC_FLOOR",[(-108,-170),(103,-170),
    (118,156),(-105,151)],94,12,public,
    "in real roofed central vault; not a mere gap between sculptures")
slab("WEST_ARCHIVE_GROUND_FLOOR",[(-390,-85),(-226,-75),
    (-215,233),(-379,240)],104,12,archive,
    "in real carved cultural room")
slab("EAST_RAIL_PUBLIC_CONCOURSE",[(260,-124),(398,-105),
    (423,223),(272,235)],102,12,station,
    "in real carved rail concourse, station function not certified")
slab("WEST_INTERNAL_GALLERY_CONNECTOR",[(-243,7),(-84,22),
    (-91,144),(-245,133)],104,10,public,
    "physical west-side chamber route")
slab("EAST_INTERNAL_GALLERY_CONNECTOR",[(79,-36),(276,-28),
    (280,110),(81,101)],103,10,public,
    "physical east-side chamber route")
slab("NORTHERN_PUBLIC_EXIT_FLOOR",[(-91,135),(93,135),
    (99,670),(-85,670)],102,10,public,
    "through real north exit portal")
slab("WEST_UPPER_ARCHIVE_PUBLIC_FLOOR",[(-371,70),(-240,79),
    (-245,229),(-367,224)],289,10,archive,
    "distinct cultural room connected by reserved vertical void; transport not certified")
# Provisional ground/sea; small context explicitly cannot count as W0 completed.
slab("W0_PROVISIONAL_APPROACH_GROUND",[(-970,-1050),(900,-1050),
    (900,-710),(-970,-710)],-37,15,plaza,
    "context ONLY: not official W0 terrain")
slab("W0_PROVISIONAL_EAST_WATER",[(710,-1100),(1150,-1100),
    (1150,800),(710,800)],-38,8,sea,
    "context ONLY: not a finished inland sea")
scene=bpy.context.scene
scene["study_id"]="D47_R2_SUBTRACTIVE_CIVIC_SPACE"
scene["units"]="meters"
scene["formal_coordinates"]=False
scene["art_approved"]=False
scene["formal_m247_c_mesh_adopted"]=False
scene["minecraft_construction_authorized"]=False
scene["routes_occupancy_audit"]="PENDING_INDEPENDENT_TEST"
scene["vertical_transport_complete"]=False
scene["W0_H_SB_10KM_MASTER_COMPLETE"]=False
scene["blender_GUI_visual_edit_proven"]=False
def camera(name,loc,target,ortho=None):
    ca=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,ca)
    collection("04 SAME-SCENE FIXED REVIEW CAMERAS").objects.link(o)
    o.location=loc
    o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
    ca.clip_end=25000
    if ortho:
        ca.type="ORTHO";ca.ortho_scale=ortho
    else:
        ca.type="PERSP";ca.lens=22
    return o
cams=[
 ("01_approach",(-30,-1200,140),(0,-20,230),None),
 ("02_room_interior",(0,-255,180),(10,230,260),None),
 ("03_west_cultural",(-95,80,175),(-290,85,180),None),
 ("04_east_station",(135,50,180),(320,120,200),None),
 ("05_distant_oblique",(1600,-1550,1150),(10,0,260),1550),
 ("06_high_threequarter",(-1250,1100,1330),(0,0,270),1600),
]
for x in cams:camera(*x)
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_cavity=True
scene.render.resolution_x=1100;scene.render.resolution_y=730
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=False
# Keep nonrendering cutter collections in original as source of intended cavities.
# Export only actual architecture; inspection cutters never become fake geometry.
native=P/"D47_R2_TRUE_SPATIAL_SUBTRACTION_EDITABLE.blend"
gltf=P/"D47_R2_TRUE_SPATIAL_SUBTRACTION.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.object.select_all(action="DESELECT")
for o in bpy.data.objects:
    if o.type=="MESH" and not o.name.startswith("CUTTER_"):o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=mass
bpy.ops.export_scene.gltf(filepath=str(gltf),export_format="GLB",
                          use_selection=True,export_cameras=False,export_lights=False)
bpy.ops.object.select_all(action="DESELECT")
for name,*_ in cams:
    scene.camera=bpy.data.objects[name]
    scene.render.filepath=str(P/(name+".png"))
    bpy.ops.render.render(write_still=True)
manifest={
 "scope":"one true carved spatial section / technical method test",
 "state":"TECH_UNREVIEWED_ART_UNREVIEWED",
 "blender_version":bpy.app.version_string,
 "real_mother_volume":mass.name,
 "editable_cutters":len(cutters),
 "real_floor_count":len([o for o in bpy.data.objects if o.name in [
 "PUBLIC_ENTRY_REAL_FLOOR","CHAMBER_MAIN_PUBLIC_FLOOR",
 "WEST_ARCHIVE_GROUND_FLOOR","EAST_RAIL_PUBLIC_CONCOURSE",
 "WEST_INTERNAL_GALLERY_CONNECTOR","EAST_INTERNAL_GALLERY_CONNECTOR",
 "NORTHERN_PUBLIC_EXIT_FLOOR","WEST_UPPER_ARCHIVE_PUBLIC_FLOOR"]]),
 "named_cameras":[n for n,*_ in cams],
 "render_names":[n+".png" for n,*_ in cams],
 "clearance_and_accessibility_verified":False,
 "physical_void_verification":"PENDING_INDEPENDENT_READ",
 "artist_G0":"NOT_REVIEWED",
 "vertical_transport_verified":False,
 "formal_coordinates":False,"formally_adopted":False,
 "full_10km_city_master":False,"construction_authorized":False,
 "work_or_GUI_direct_edit_used":False,
}
(P/"D47_R2_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf8")
print("D47_R2_NATIVE_OUTPUT_CREATED_UNREVIEWED",json.dumps(manifest))
