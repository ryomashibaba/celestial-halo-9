"""D47-B1: inhabited rift hand-controlled architectural mesh study, NOT ART APPROVED.
All units meters. 3D is provisional; 10km context not official M204/W0 coordinates.
The sculpted masses are continuous mesh control cages, not repeated floor/box modules.
Run with Blender 4.5.15 bpy: python d47_rift_base.py OUTPUT_DIR
"""
import bpy, math, sys, json, hashlib
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi
P=Path(sys.argv[-1]);P.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name!='Collection' and not c.objects:bpy.data.collections.remove(c)
def group(name):
    c=bpy.data.collections.get(name)
    if c is None:
        c=bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c
def mat(name,rgb):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);return m
chalk=mat("01 sculpted inhabited ivory",(.72,.74,.72))
pearl=mat("02 light civic stone",(.91,.85,.70))
deep=mat("03 dark structural fault",(.12,.17,.24))
rift=mat("04 glazed turquoise sanctuary",(.27,.48,.53))
terra=mat("05 provisional mountainous terrain",(.20,.24,.27))
sea=mat("06 provisional inland sea",(.05,.25,.32))
copper=mat("07 bronze cultural edges",(.44,.34,.24))
def mesh_obj(name,vertices,faces,material,category):
    mesh=bpy.data.meshes.new(name+"_editable_mesh")
    mesh.from_pydata(vertices,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);group(category).objects.link(o)
    mesh.materials.append(material);return o
def face_panel(name,poly,material,category):
    return mesh_obj(name,poly,[tuple(range(len(poly)))],material,category)
# Each entry: z, world x/y center, two transverse extents, cliff curvature.
# Unequal masses, rotated front/back, sideways displaced crowns, cantilevered shoulders.
# These control cages are unique, authored, editable vertices rather than a city-module grammar.
WEST=[
 (0,-1640, -150,1750,1200,.15),
 (480,-1750,-190,1860,1290,.19),
 (1000,-1660,  80,1730,1350,.10),
 (1660,-1740,310,1870,1060,.16),
 (2250,-1540,520,1530,1360,.28),
 (2960,-1220,550,1700,1000,.13),
 (3600,-1100,700,1260,1180,.28),
 (4190, -850,930,1550,900,.21),
 (4790, -710,1010,1030,840,.08)]
EAST=[
 (0,1740,220,1230,1500,-.18),
 (520,1730,190,1350,1570,-.20),
 (1060,1800,-120,1490,1170,-.18),
 (1700,1890,-300,1430,1300,-.10),
 (2250,1600,-570,1130,1420,-.08),
 (2810,1900,-720,1610,1160,-.16),
 (3430,2040,-900,1270,1360,-.20),
 (4070,2230,-1200,1500,920,-.13),
 (4660,2570,-1200,850,900,-.11)]
N=24
def ring(cage,side):
    rings=[]
    for z,cx,cy,rx,ry,tw in cage:
        pts=[]
        for i in range(N):
            t=2*pi*i/N
            # 24 distinct perimeter vertices, with folded facade curvature.
            sx=cos(t);sy=sin(t)
            cren=(1+.075*cos(3*t+z*.00065)+.05*sin(5*t-z*.00043))
            x=cx+rx*sx*cren + tw*ry*sy*.30
            y=cy+ry*sy*(1+.09*sin(4*t+z*.00028))
            # compress upper, inward-facing boundary to make rift bigger instead of blocking it
            if side=='WEST' and sx>0:x-=110*(.4+.6*z/4800)
            if side=='EAST' and sx<0:x+=135*(.3+.7*z/4660)
            pts.append((x,y,z))
        rings.append(pts)
    return rings
def thick_body(label,cage,material):
    rr=ring(cage,label)
    verts=[v for r in rr for v in r]
    faces=[tuple(range(N-1,-1,-1))]
    for k in range(len(rr)-1):
        for i in range(N):
            j=(i+1)%N
            a=k*N+i;b=k*N+j;c=(k+1)*N+j;d=(k+1)*N+i
            faces.append((a,b,c,d))
    faces.append(tuple((len(rr)-1)*N+i for i in range(N)))
    obj=mesh_obj(label+"_MASS_EDITABLE_VERTEX_CAGE",verts,faces,material,"CENTRAL / SCULPTURAL INHABITED MASS")
    # retain named arrays for authoring the actual, not imaginary, mesh
    obj["concept"]="unequal thick lived-in faultland, not an outer sculpture"
    obj["cage_levels"]=len(rr);obj["radial_vertices"]=N
    return obj,rr
w,WR=thick_body("WEST",WEST,chalk)
e,ER=thick_body("EAST",EAST,pearl)
# Façade lines follow the actual irregular mass surfaces, not floating horizontal city shelves.
# Their own sparse broad balcony/civic ledges are visibly embedded into the cliffs.
def panel_at_level(name,rr,level,indices,offset,material):
    pts=rr[level]
    # a folded recessed strip following consecutive existing mesh perimeter vertices
    outline=[]
    for i in indices:
        x,y,z=pts[i%N];outline.append((x,y,z+offset))
    for i in reversed(indices):
        x,y,z=pts[i%N];outline.append((x*.998,y*.998,z+offset+38))
    return face_panel(name,outline,material,"CENTRAL / EMBEDDED CIVIC EDGES")
# Inner-facing banks: west front at i=0; east inner at i=12
for zindex,idx,rr,m in [(2,list(range(21,27)),WR,copper),
                         (5,list(range(21,27)),WR,rift),
                         (3,list(range(9,16)),ER,deep),
                         (6,list(range(9,16)),ER,rift)]:
    panel_at_level("INTEGRATED_PUBLIC_FRONT_%02d"%zindex,rr,zindex,idx,0,m)
# One giant open public interior/urban gorge is the real empty gap between the two continuous meshes.
# Reserve non-rendered inspection points along the gorge: not sufficient to prove clearance.
for i,(x,y,z) in enumerate([(-90,-50,350),(0,-110,1300),(160,-80,2250),(290,-230,3120),(530,-240,3900)]):
    ob=bpy.data.objects.new("RIFT_AIR_INSPECTION_ONLY_%02d"%i,None)
    ob.empty_display_type="SPHERE";ob.empty_display_size=50;ob.location=(x,y,z)
    group("UNVERIFIED AIR INSPECTION MARKERS").objects.link(ob)
# Human-scale floors are deliberately not bulk-generated at G0: quality gate is on the masses.
# Provisional W0 terrain is an honest location scaffold with mountains, escarpment, coastal basin.
def terrain(nx=40,ny=40):
    verts=[]
    for j in range(ny+1):
        y=-5200+10400*j/ny
        for i in range(nx+1):
            x=-5400+10800*i/nx
            north=max(0,(y-1850)/3300)
            west=max(0,(-x-2600)/2700)
            cliff=720*west**1.9+1550*north**2
            waves=65*sin(.001*x)*cos(.0013*y)
            z=-125+cliff+waves
            verts.append((x,y,z))
    faces=[]
    for j in range(ny):
        for i in range(nx):
            a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
    return mesh_obj("W0_STUDY_TERRAIN_NOT_CANONICAL",verts,faces,terra,"W0 / PROVISIONAL")
terrain()
face_panel("W0_PROVISIONAL_INLAND_SEA",[(3300,-2400,-120),(5400,-2400,-120),
 (5400,2250,-120),(3300,2250,-120)],sea,"W0 / PROVISIONAL")
# No deceptive rendered H/SB blocks. Study-only positions are scene metadata, not finished city assets.
scene=bpy.context.scene
scene["H1_to_H6"]="required 6 COMPLETE floating cities, NOT BUILT in D47"
scene["SB01_to_SB16"]="required 16 COMPLETE facilities, NOT BUILT in D47"
scene["official_coordinates"]=False
scene["art_approved"]=False
scene["public_routes_verified"]=False
scene["provisional_world_size_m"]=10800
def camera(name,at,target,scale):
    ca=bpy.data.cameras.new(name);obj=bpy.data.objects.new(name,ca)
    group("FIXED REVIEW CAMERAS").objects.link(obj)
    obj.location=at;d=Vector(target)-obj.location
    obj.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    ca.type='ORTHO';ca.ortho_scale=scale;ca.clip_end=40000
    return obj
CAMS=[
("01_city",(10000,-12400,10800),(0,0,1900),14400),
("02_front",(0,-9700,3500),(0,0,2400),6700),
("03_oblique",(7400,-7700,6900),(0,0,2150),7500),
("04_side",(10000,600,3900),(0,0,2200),7100),
("05_ground",(-1700,-3800,470),(0,0,1750),6400),
("06_rift",(150,-1800,2300),(100,200,2000),3400)]
for row in CAMS:camera(*row)
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_cavity=True
scene.render.resolution_x=1100;scene.render.resolution_y=700
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
bpy.ops.wm.save_as_mainfile(filepath=str(P/'D47_B1_BASE_EDITABLE.blend'))
bpy.ops.export_scene.gltf(filepath=str(P/'D47_B1_BASE.glb'),export_format='GLB',export_cameras=False,export_lights=False)
for name,*_ in CAMS:
    scene.camera=bpy.data.objects[name]
    scene.render.filepath=str(P/(name+'.png'))
    bpy.ops.render.render(write_still=True)
manifest={
 "status":"D47_B1_BASE_REAL_BPY_CREATED_NOT_ART_REVIEWED",
 "process":"hand-authored 24-point per-level continuous editable mass cages, no replicated residential boxes",
 "public_gap":"physical gap between two meshes; entrance and walkability UNVERIFIED",
 "central_mesh_count":2,"western_cage_levels":len(WEST),"eastern_cage_levels":len(EAST),
 "center_city_scale_m":~0 if False else 4800,
 "named_cameras":[row[0] for row in CAMS],
 "blender_version":bpy.app.version_string,
 "provisional_coordinates":True,"official_master":False,
 "work_gui_control_proven":False,"functional_routes_proven":False,
 "art_approved":False,"accepted_for_construction":False,
 "w0_full_design_complete":False,"h1_h6_complete":False,"sb01_sb16_complete":False}
(P/'D47_B1_MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf-8')
print('D47_B1_REAL_NATIVE_DONE',json.dumps(manifest,ensure_ascii=False))
