"""HALO-9 J7-R5: Blender-native, inhabited civic-rift section (ART RESEARCH, not canonical).
Unlike R1 (tiny shelved parts), R2 (smooth closed monolith), R3 (folded sails),
this studies interlocked massive inhabited cliff architecture and an actual sheltered
public hall, its section/entrances/sky wells and local circulation in real Blender.
All dimensions are NONCANONICAL metres. Not a completed city or artistic adoption.
"""
import bpy, bmesh, math, json, sys, collections
from mathutils import Vector, Matrix
from pathlib import Path
from math import sin, cos, pi
def need(ok,msg):
    if not ok:raise RuntimeError(msg)
def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc=bpy.context.scene
    sc.unit_settings.system="METRIC"
    sc.unit_settings.scale_length=1.0
    return sc
OUT=Path(sys.argv[sys.argv.index("--")+1]).resolve() if "--" in sys.argv else Path("/tmp/j7r5")
need(not OUT.exists() or not list(OUT.iterdir()),"J7-R5 output must be empty: "+str(OUT))
OUT.mkdir(parents=True,exist_ok=True)
sc=clear()
MATS={}
def mat(name,col,metal=.0):
    x=bpy.data.materials.new(name); x.diffuse_color=(*col,1); x.use_nodes=True
    bs=x.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Base Color"].default_value=(*col,1)
        bs.inputs["Metallic"].default_value=metal
        bs.inputs["Roughness"].default_value=.48
    MATS[name]=x
for name,col,metal in [
 ("ivory_ceramic",(.78,.80,.74),.35),
 ("chiseled_white",(.91,.91,.83),.1),
 ("urban_nacre",(.53,.70,.73),.35),
 ("graphite_strata",(.10,.19,.23),.55),
 ("gold_inlay",(.84,.63,.37),.7),
 ("inner_civic",(.67,.73,.72),.1),
 ("garden_city",(.16,.43,.37),.05),
 ("transit_blue",(.13,.60,.72),.45),
 ("context_gray",(.15,.19,.22),.05),
 ("glass_blue",(.26,.59,.68),.2),
 ]:mat(name,col,metal)
PARTS=[]
def mesh(name,verts,faces,role,material):
    need(len(verts)>=3 and len(faces)>0,name+" is empty")
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
    o.data.materials.append(MATS[material]);o["halo_role"]=role;o["research_only"]=True
    PARTS.append({"name":name,"role":role,"mat":material,"vertices":len(verts),"faces":len(faces)})
    return o
def circle(cx,cy,rx,ry,N=12,phase=0,wobble=0):
    return [(cx+(1+wobble*sin(3*2*pi*i/N+.2))*rx*cos(2*pi*i/N+phase),
             cy+(1+wobble*sin(4*2*pi*i/N))*ry*sin(2*pi*i/N+phase)) for i in range(N)]
def poly_prism(name,outline,z0,z1,role,material,lean=(0,0),taper=1.0):
    n=len(outline);center=(sum(x for x,y in outline)/n,sum(y for x,y in outline)/n)
    a=[(x,y,z0) for x,y in outline]
    b=[(center[0]+(x-center[0])*taper+lean[0],center[1]+(y-center[1])*taper+lean[1],z1) for x,y in outline]
    faces=[tuple(reversed(tuple(range(n)))),tuple(range(n,2*n))]
    for i in range(n):j=(i+1)%n;faces.append((i,j,n+j,n+i))
    return mesh(name,a+b,faces,role,material)
def courtyard_ring(name,cx,cy,rx,ry,inner,z0,z1,role,material,N=14,phase=0):
    outer=circle(cx,cy,rx,ry,N,phase,wobble=.07)
    inside=circle(cx,cy,rx*inner,ry*inner,N,phase,wobble=.04)
    v=[]
    for z in [z0,z1]:
        v.extend([(x,y,z) for x,y in outer])
        v.extend([(x,y,z) for x,y in inside])
    f=[]
    for i in range(N):
        j=(i+1)%N
        f.extend([(i,j,2*N+j,2*N+i),                         # outer vertical
                  (N+i,3*N+i,3*N+j,N+j),                     # open inner wall
                  (2*N+i,2*N+j,3*N+j,3*N+i),                # top ring
                  (i,N+i,N+j,j)])                           # bottom ring
    return mesh(name,v,f,role,material)
def beam(name,a,b,w,d,role,material):
    p=Vector(a);q=Vector(b);v=q-p
    horizontal=Vector((-v.y,v.x,0))
    if horizontal.length<.0001:horizontal=Vector((1,0,0))
    horizontal.normalize();u=horizontal*w*.5;t=Vector((0,0,d*.5))
    def facebase(point):
        return [tuple(point-u-t),tuple(point+u-t),tuple(point+u+t),tuple(point-u+t)]
    vs=facebase(p)+facebase(q)
    fs=[(3,2,1,0),(4,5,6,7)]
    for i in range(4):j=(i+1)%4;fs.append((i,j,j+4,i+4))
    return mesh(name,vs,fs,role,material)
def arc_ribbon(name,points,width,thick,role,material):
    vs=[]
    for x,y,z in points:
        vs += [(x-width*.5,y,z-thick*.5),(x+width*.5,y,z-thick*.5),
               (x+width*.5,y,z+thick*.5),(x-width*.5,y,z+thick*.5)]
    f=[(0,1,2,3),(len(vs)-4,len(vs)-3,len(vs)-2,len(vs)-1)]
    for seg in range(len(points)-1):
        for i in range(4):
            j=(i+1)%4; a=seg*4+i;b=seg*4+j;c=(seg+1)*4+j;d=(seg+1)*4+i
            f.append((a,b,c,d))
    return mesh(name,vs,f,role,material)
def notched_outline(cx,cy,rx,ry,phase=0):
    pts=circle(cx,cy,rx,ry,14,phase,wobble=.10)
    # Deliberate deep inward notches along the public-facing section
    pts[0]=(cx+rx*.68,cy+ry*.04)
    pts[1]=(cx+rx*.71,cy+ry*.25)
    pts[13]=(cx+rx*.78,cy-ry*.27)
    return pts
def building(name,x,y,z,w,h,depth,style):
    p=[(x-w*.55,y-depth*.42),(x+w*.43,y-depth*.52),(x+w*.52,y+depth*.43),(x-w*.46,y+depth*.53)]
    poly_prism(name+"_MASS",p,z,z+h, "city_building_exterior_draft","chiseled_white" if style%3==0 else "urban_nacre",lean=(h*.08 if style%2 else -h*.13,0),taper=.84)
    poly_prism(name+"_ROOF",p,z+h-9,z+h+12,"city_roof_detail","graphite_strata",taper=.70)
    # Vertical window band as actual geometry, not final facade.
    for k in range(2):
        yy=y+(k-.5)*depth*.22
        beam(name+"_FACADE_FIN_"+str(k),(x+w*.48,yy,z+h*.13),(x+w*.38,yy,z+h*.91),7,7,"facade_rhythm_preliminary","gold_inlay")
def stair_flights(base,z0,z1,dx,dy,steps,id):
    # Access concept only; no grade/walkability QA until later phase.
    for i in range(steps):
        t=i/steps
        x=base[0]+t*dx;y=base[1]+t*dy;z=z0+(z1-z0)*t
        p=[(x-45,y-30),(x+45,y-30),(x+45,y+30),(x-45,y+30)]
        poly_prism(id+"_"+str(i),p,z-15,z,"interlevel_civic_ramp_steps_not_access_certified","inner_civic")
# SECTION INTENT: two thick inhabited cliff banks, one tall, one wide; an internal
# open civic room and ground civic field actually accessible from open void frontage.
poly_prism("WEST_FOUNDATION_BUTTRESS",notched_outline(-1470,110,1030,1190),80,640,"inhabited_thick_city_foundation","graphite_strata",taper=.96)
poly_prism("WEST_HIGH_CITY_MASS",notched_outline(-1600,120,910,950,.13),630,1210,"inhabited_continuous_west_mass","ivory_ceramic",lean=(-130,80),taper=.89)
poly_prism("WEST_CROWN_CIVIC_RIDGE",circle(-1720,50,700,680,12,.15,.13),1200,1550,"thick_top_city_not_sail","urban_nacre",lean=(-210,40),taper=.80)
poly_prism("EAST_FOUNDATION_BUTTRESS",notched_outline(1500,270,1050,1050,.25),100,790,"inhabited_thick_east_foundation","graphite_strata",taper=.98)
poly_prism("EAST_MAIN_RESIDENTIAL_MASS",notched_outline(1530,330,950,940,.07),780,1600,"inhabited_continuous_east_mass","ivory_ceramic",lean=(170,120),taper=.85)
poly_prism("EAST_UPPER_CIVIC_CITY",circle(1660,380,840,720,14,.07,.11),1570,2060,"elevated_inhabited_city_mass","urban_nacre",lean=(180,190),taper=.79)
poly_prism("EAST_CROWN_INHABITED_PEAK",circle(1960,560,600,510,11,.10,.13),2030,2460,"highest_habitable_city_profile","chiseled_white",lean=(190,90),taper=.68)
# DEEP, TRUE COURTYARD CUTOUTS (topological ring holes, not painted surface)
courtyard_ring("WEST_CITY_SKYWELL",-1590,-120,590,450,.49,1210,1330,"open_courtyard_void_with_real_inner_wall","inner_civic")
courtyard_ring("EAST_CITY_SKYWELL",1570,260,550,460,.42,1600,1750,"open_courtyard_void_with_real_inner_wall","inner_civic")
# PUBLIC ASSEMBLY NAVE — floor, opposed side halls, two non-opaque roofing galleries,
# and South open ingress; central hall void approx 1100×760×>450m.
public_floor=[(-620,-760),(-490,-880),(500,-880),(690,-660),(610,420),(-540,490)]
poly_prism("NAVE_PUBLIC_ASSEMBLY_HALL_FLOOR",public_floor,480,548,"large_public_floor_shared_between_inhabited_cliffs","chiseled_white")
poly_prism("NAVE_EAST_CIVIC_GALLERY",[ (565,-550),(725,-480),(700,420),(565,420)],540,1040,"inhabited_civic_side_gallery","ivory_ceramic",lean=(45,-45))
poly_prism("NAVE_WEST_CIVIC_GALLERY",[(-755,-550),(-560,-550),(-565,450),(-720,440)],540,980,"inhabited_civic_side_gallery","ivory_ceramic",lean=(-60,60))
poly_prism("NAVE_PUBLIC_NORTH_READING_WALL",[(-565,410),(-565,515),(660,515),(600,415)],535,945,"closed_north_boundary_civic_nave","urban_nacre")
# North-side public entrance is an opening at south side: NO infill south wall.
courtyard_ring("NAVE_UPPER_OPEN_OCULUS",10,-30,710,650,.74,1080,1145,
              "major_skylight_aperture_and_public_roof_balcony","chiseled_white",N=16,phase=.1)
# Architectural vault: articulated ribs, increasing arches rather than continuous opaque shell.
for j,y in enumerate([-565,-260,40,345]):
    pts=[]
    for k in range(13):
        t=k/12; x=-690+1380*t
        z=1000+360*max(0,1-(2*t-1)**2)+32*cos(j*1.2)
        pts.append((x,y,z))
    arc_ribbon("NAVE_VAULT_OCCUPIABLE_RIB_"+str(j),pts,58,72,"civic_structural_vault_actual_mesh","ivory_ceramic")
    for side,x in [("W",-695),("E",695)]:
        beam("NAVE_VAULT_PIER_"+side+"_"+str(j),(x,y,540),(x,y,1000),65,100,"vault_support_not_load_certified","graphite_strata")
# The roof stays visibly open between ribs, and from south entry.
# Public gallery promenade and TWO stations; both connect to actually thick cliffs.
beam("WEST_GATEWAY_LANDSCAPED_APPROACH",(-1300,-1000,600),(-575,-660,600),220,54,"ground_to_nave_public_access_level_not_walk_certified","inner_civic")
beam("EAST_GATEWAY_APPROACH",(1390,-790,690),(575,-500,690),260,58,"east_transit_public_connection_not_walk_certified","inner_civic")
# inhabited upper communal levels
for side,centers,z0 in [
 ("W",[(-1650,-230),(-1600,320)],1255),
 ("E",[(1500,70),(1740,610)],1660)]:
    for q,(cx,cy) in enumerate(centers):
        rx,ry=(440,330) if side=="W" else (490,360)
        courtyard_ring(side+"_TERRACE_STREET_"+str(q),cx,cy,rx,ry,.24,z0,z0+44,
           "local_city_street_with_true_open_courtyard","inner_civic")
        for k in range(4):
            a=k*pi*.5+.2;xx=cx+rx*.72*cos(a);yy=cy+ry*.70*sin(a)
            building(side+"_STREET_"+str(q)+"_BUILDING_"+str(k),xx,yy,z0+44,
                     145+12*k,180+55*((k+q)%3),110+6*k, k+q*3)
# transit/urban infrastructure outwards from the body, not floating toy decks
for side,x,base,top in [("W",-1040,500,1310),("E",980,520,1700)]:
    for d in [-120,120]:
        beam(side+"_ASCENT_GUIDE_"+str(d),(x+d,250,base),(x+d,250,top),31,43,"vertical_transit_unverified","transit_blue")
    for k,z in enumerate([base,(base+top)*.5,top]):
        poly_prism(side+"_TRANSIT_STATION_"+str(k),
             [(x-200,150),(x+200,150),(x+190,415),(x-185,430)],z-25,z+22,
             "multi_level_public_station_not_certified","chiseled_white")
beam("CITY_SKYBRIDGE_FORUM_A",(-1020,200,1120),(980,290,1140),115,46,"upper_east_west_public_crossing","urban_nacre")
beam("CITY_SKYBRIDGE_FORUM_B",(-1100,650,1430),(980,720,1550),95,46,"upper_neighborhood_exchange_prototype","urban_nacre")
# banks' civic cliff face: niches and window strata provide legible inhabited depth
for side,xsign,yylist,ztop in [("W",-1,[-640,-310,40,360],1300),("E",1,[-600,-220,170,550],1790)]:
    for k,y in enumerate(yylist):
        x=xsign*(760+25*k)
        z=650+(k%2)*330 if side=="W" else 900+(k%2)*350
        poly_prism(side+"_CLIFF_PUBLIC_HANGING_GARDEN_"+str(k),
          [(x-145,y-100),(x+145,y-100),(x+155,y+120),(x-160,y+120)],
          z,z+52,"exposed_civic_terrace_cutaway_not_traversal_pass","garden_city")
        for b in range(3):
            beam(side+"_ARCH_FACADE_PIER_"+str(k)+"_"+str(b),
                 (x-100+100*b,y+80,z+48),(x-90+100*b,y+75,min(ztop,z+330)),
                 16,28,"civic_facade_structure","gold_inlay")
# minimal noncanonical W0 reference - no official placement or fabricated H/SB locations
poly_prism("NONCANONICAL_10KM_BASIS",
   [(-5000,-5000),(5000,-5000),(5000,5000),(-5000,5000)],
   -180,-168,"ground_reference_not_official_w0","context_gray")
# Real blender bmesh direct edit of structural vault: intentionally engineered to make
# the central nave skylight asymmetric while keeping roof/opening spatially linked.
rib=next(o for o in sc.objects if o.name=="NAVE_VAULT_OCCUPIABLE_RIB_1")
bm=bmesh.new();bm.from_mesh(rib.data);moved=0
for v in bm.verts:
    if abs(v.co.x)<300 and v.co.z>1100:
        v.co.z+=120*(1-abs(v.co.x)/300)
        moved+=1
bm.to_mesh(rib.data);bm.free();rib.data.update()
need(moved>0,"Blender bmesh direct vault edit did not move vertices")
# Save selected camera outputs from exactly this Blender scene. Separate FIXED and LOCAL.
sc.render.engine="BLENDER_WORKBENCH"
sc.render.resolution_x=1200;sc.render.resolution_y=840;sc.render.resolution_percentage=100
sc.render.image_settings.file_format="PNG"
sc.display.shading.light="STUDIO"
sc.display.shading.color_type="MATERIAL"
sc.display.shading.show_shadows=True
sc.display.shading.show_cavity=True
sc.display.shading.cavity_type="BOTH"
sc.view_settings.view_transform="Standard"
sc.render.film_transparent=False
def render(name,loc,target,ortho,kind):
    camd=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,camd)
    bpy.context.collection.objects.link(cam)
    cam.location=Vector(loc);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    camd.type="ORTHO";camd.ortho_scale=ortho;camd.clip_end=80000
    sc.camera=cam
    path=OUT/(name+".png");sc.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    need(path.exists() and path.stat().st_size>9000,"render failed "+name)
    return {"name":name,"kind":kind,"ortho_m":ortho,"bytes":path.stat().st_size}
c=(0,0,1150)
views=[
 ("01_CITY_FRONT",(0,-11000,4300),c,10500,"FIXED_10KM"),
 ("02_CITY_OBLIQUE",(7600,-8500,6200),c,10500,"FIXED_10KM"),
 ("03_CITY_SIDE",(11000,0,5100),c,10500,"FIXED_10KM"),
 ("04_CITY_REAR",(0,11000,4900),c,10500,"FIXED_10KM"),
 ("05_CITY_AERIAL",(6000,-6600,13500),c,10500,"FIXED_10KM"),
 ("06_CITY_GROUND",(0,-10000,180),(0,0,1000),10500,"FIXED_10KM"),
 ("07_CITY_REVERSE",(-7600,7600,6900),c,10500,"FIXED_10KM"),
 ("08_NAVE_INTERIOR",(160,-1650,1200),(0,-130,980),2700,"LOCAL_NOT_SCALE_COMPARABLE"),
 ("09_DISTRICT_SECTION",(3450,-3800,2850),(0,100,1050),5700,"LOCAL_NOT_SCALE_COMPARABLE")]
images=[render(*args) for args in views]
# Remove cameras before export so Blender glTF scene contains mesh nodes only.
bpy.ops.object.select_all(action="DESELECT")
for obj in list(bpy.data.objects):
    if obj.type=="CAMERA":bpy.data.objects.remove(obj,do_unlink=True)
# Native .blend is the primary editable original; glTF is a transport derivative.
blend=OUT/"J7R5_INHABITED_CIVIC_SECTION_NONCANONICAL.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
glb=OUT/"J7R5_INHABITED_CIVIC_SECTION_NONCANONICAL.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB")
need(blend.stat().st_size>15000 and glb.stat().st_size>15000,"real model exports failed")
num=len([o for o in bpy.data.objects if o.type=="MESH"])
counts=collections.Counter(x["role"] for x in PARTS)
evidence={"schema":"halo9.m3d1s.j7r5.actual_blender_model.v1",
 "blender":bpy.app.version_string,"research_only":True,
 "coordinate":"NONCANONICAL_Z_UP_METERS",
 "meters_gross_section_dimensions":"LOCAL SECTION, NOT WHOLE 10KM CITY",
 "mesh_object_count":num,"vertex_count":sum(len(o.data.vertices) for o in bpy.data.objects if o.type=="MESH"),
 "triangles_count":sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in bpy.data.objects if o.type=="MESH"),
 "bmesh_direct_edit_vertices":moved,"role_count":dict(counts),
 "real_public_hall_floor":True,"roof_open_between_ribs":True,
 "two_open_courtyards":True,"public_access_measured":False,
 "all_public_rooms_detailed":False,
 "inhabited_civic_section_quality":"EXPERIMENTAL_REVIEW_REQUIRED",
 "formal_art_accepted":False,"construction":"HOLD","formal_world_coordinates":False,
 "derived_model_GLB":glb.name,"native_editable_BLENDER":blend.name,
 "glb_bytes":glb.stat().st_size,"blend_bytes":blend.stat().st_size,
 "render_views":images}
(OUT/"J7R5_BLENDER_MODEL_EVIDENCE.json").write_text(json.dumps(evidence,indent=2),encoding="utf8")
# Import the actual exported file into an empty scene and check object count
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(glb))
newcount=len([o for o in bpy.data.objects if o.type=="MESH"])
evidence["glb_reimport_mesh_count"]=newcount
need(newcount>=num,"GLB reimport dropped mesh objects")
(OUT/"J7R5_BLENDER_MODEL_EVIDENCE.json").write_text(json.dumps(evidence,indent=2),encoding="utf8")
print("J7R5_REAL_BLENDER_SUCCESS",json.dumps({"mesh_objects":num,"reimport":newcount,"views":len(images),"bmesh_edits":moved,"glb_bytes":glb.stat().st_size}))
