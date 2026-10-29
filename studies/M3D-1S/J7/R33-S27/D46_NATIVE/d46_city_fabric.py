"""D46 INHABITED FAULT / first art-first native scene, NOT formally adopted.
An independent urban FOLD composed of occupied civic city-fabric; no old geometry used.
Main design:
 * diagonal 500m public void with a distinct urban base/skyline
 * asymmetric populated vertical neighborhoods physically shaping the skyline
 * diagonal transport and identifiable public plazas, no dummy "walking" claims
 * study-scale W0/H1-H6/SB01-16 anchors. Coordinates NOT canonical.
USAGE: python d46_city_fabric.py <outdir>
"""
import bpy, math, sys, json, random
from pathlib import Path
from mathutils import Vector
from math import sin, cos, radians, pi
out=Path(sys.argv[-1]);out.mkdir(parents=True,exist_ok=True)
random.seed(46)
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name!="Collection":
        if not c.objects: bpy.data.collections.remove(c)

def collection(name):
    c=bpy.data.collections.get(name)
    if c is None: c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c
def link(obj,category):
    c=collection(category)
    for old in list(obj.users_collection):old.objects.unlink(obj)
    c.objects.link(obj)
def material(name,rgb):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1.);return m
pearl=material("ceramic nacre / city exterior",(.68,.82,.83))
ivory=material("warm alabaster / inhabited public",(.95,.84,.65))
bronze=material("anodized bronze / city fabric",(.42,.35,.27))
shadow=material("obsidian / infrastructural void",(.09,.15,.20))
teal=material("turquoise / aqueduct civic",(.14,.50,.51))
light=material("skyline silver",(.82,.88,.92))
ground=material("W0 warm terrain / provisional",(.20,.24,.30))
water=material("inner sea / provisional",(.07,.23,.38))
signal=material("temporary land-use anchors",(.50,.38,.41))

def cube(n,loc,size,mat,cat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=n;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat);link(o,cat);return o

def prism(n,plan,zlo,zhi,mat,cat):
    assert zhi>zlo and len(plan)>=3
    verts=[(x,y,z) for z in (zlo,zhi) for x,y in plan]
    npoints=len(plan)
    faces=[tuple(range(npoints-1,-1,-1)),tuple(range(npoints,npoints*2))]
    for i in range(npoints):
        j=(i+1)%npoints
        faces.append((i,j,j+npoints,i+npoints))
    mesh=bpy.data.meshes.new(n+" / mesh");mesh.from_pydata(verts,[],faces)
    mesh.update()
    o=bpy.data.objects.new(n,mesh);collection(cat).objects.link(o)
    o.data.materials.append(mat)
    return o

def rect_angled(center,width,depth,angle):
    cx,cy=center; a=radians(angle);c=cos(a);s=sin(a)
    return [(cx+px*c-py*s,cy+px*s+py*c) for px,py in [
        (-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]]

def tri_plaza(n,center,width,depth,angle,z,mat,cat):
    cx,cy=center; a=radians(angle);c,s=cos(a),sin(a)
    shape=[(-.62,-.5),(.74,-.48),(1,-.17),(.77,.50),(-.85,.46),(-1,.13)]
    plan=[(cx+(x*c-y*s)*width,cy+(x*s+y*c)*depth) for x,y in shape]
    return prism(n,plan,z,z+28,mat,cat)

def beam(name,A,B,width,depth,mat,cat):
    a=Vector(A);b=Vector(B);d=b-a;mid=(a+b)*.5
    bpy.ops.mesh.primitive_cube_add(size=1,location=mid)
    o=bpy.context.object;o.name=name
    o.dimensions=(width,depth,d.length)
    o.rotation_euler=d.to_track_quat("Z","Y").to_euler()
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    o.data.materials.append(mat);link(o,cat)
    return o

# Preserve city-scale study scaffold distinct from actual approved city coordinates.
cube("W0_STUDY_EARTH_NOT_CANONICAL",(0,0,-130),(10600,10200,200),ground,"W0 PROVISIONAL")
cube("W0_PROVISIONAL_INNER_SEA",(3600,350,-32),(2850,4200,17),water,"W0 PROVISIONAL")
for i in range(8):
    h=220+90*sin(i*1.7)
    cube("W0_NORTH_ESCARPMENT_%02d"%i,(-4300+i*650,4480,130+h/2),(570,850,h),ground,"W0 PROVISIONAL")

# Art-directed, manually composed, NOT a repeated ring/shelf design.
# Occupied cliff walks diagonally migrate through 3.8km and form a faulted spatial delta.
# A/B are urban habitation densities, not an external loft or separate hollow shell.
# Each "zone" is a connected civic district with 500m-scale public court, city
# street, distinct residential enclosure, glazed lofts and a street-level threshold.
ZONES=[
 # name, xyz center, approximate building frontage, terraces, plan skew, mass type
 ("Hearth_Fault_Base",(-1150,-720,350),780,625,-17,"west"),
 ("West_Elevated_Court",(-1440,-410,1050),860,660,20,"west"),
 ("Hanging_Ambulatory",(-1730,100,1770),820,620,-26,"west"),
 ("Northern_Civic_Rift",(-990,530,2460),1060,640,33,"west"),
 ("Crown_Sky_Borough",(-350,810,3350),980,610,-16,"west"),
 ("West_Upper_Sanctum",(-760,1050,4140),600,440,17,"west"),
 ("East_Quay_City",(1480,580,430),650,720,24,"east"),
 ("East_Civic_Gallery",(1640,220,1180),720,580,-31,"east"),
 ("East_Sea_Terraces",(1130,-180,1910),810,640,12,"east"),
 ("Upper_Transit_Forum",(1320,-620,2680),860,570,-21,"east"),
 ("High_Estuary_Quarter",(760,-900,3450),620,560,35,"east"),
 # cross/cavity districts sitting on the rim, no ordinary duplicate "rings"
 ("Sunken_Atrium",(100,1240,950),760,690,7,"rear"),
 ("Fractured_Civic_Walk",(-250,1520,2150),850,620,-19,"rear"),
 ("Rift_Observatory",(420,1440,2950),690,470,21,"rear"),
]
# Each zone: occupied city ground has a jagged plan, vertical walls are populated,
# open courts are gaps in construction (not bolted-on roof windows).
for i,(name,(x,y,z),w,d,theta,groupname) in enumerate(ZONES):
    cat="CITY / "+groupname.upper()+" / OCCUPIED"
    tri_plaza(name+"_CITY_GROUND",(x,y),w,d,theta,z,ivory,cat)
    # Morphologically varying perimeter wards: no continuous donut or external shell.
    a=radians(theta)
    sides=[(-.67,-.41,.44,.23),(.40,-.38,.55,.30),(-.63,.33,.30,.24),(.38,.33,.46,.20)]
    for j,(fx,fy,wx,dy) in enumerate(sides):
        if (i*3+j)%7==0:continue # street entrance opens to sky void
        xx=x+fx*w*cos(a)-fy*d*sin(a)
        yy=y+fx*w*sin(a)+fy*d*cos(a)
        hh=170+65*((i+j)%3)
        form=rect_angled((xx,yy),w*wx,d*dy,theta+(12 if j%2 else -8))
        prism(name+f"_INHABITED_MASS_{j}",form,z+30,z+30+hh,pearl if j%2 else bronze,cat)
        # sculptural upper cloister setback: tower mass articulation (NOT a canopy)
        if (i+j)%2==0:
            p=rect_angled((xx+38,yy+20),w*wx*.72,d*dy*.76,theta)
            prism(name+f"_UPPER_HOUSE_{j}",p,z+hh+30,z+hh+130,light,cat)
    # Inner ground-level open public court (visible in top/down shot) and 2 portals.
    tri_plaza(name+"_INNER_CIVIC_SPACE",(x-25,y+10),w*.34,d*.4,theta,z+30,teal,cat)
    for j in range(4):
        t=(j-1.5)/2
        if (i+j)%4==0: continue
        xx=x+t*w*.50
        yy=y+(j%2-.5)*d*.18
        beam(name+f"_CIVIC_PIER_{j}",(xx,yy,z+20),(xx+80,yy+12,z+190),30,28,shadow,cat)

# Spatial continuity: physically modeled lift+sky rail cores.
# These links are research circulation, NOT verified human-walkable routing.
for tag,inds in [("WEST",[0,1,2,3,4,5]),("EAST",[6,7,8,9,10]),
                 ("REAR",[11,12,13])]:
    for ii in range(len(inds)-1):
        a,b=ZONES[inds[ii]],ZONES[inds[ii+1]]
        x,y,z=a[1];x2,y2,z2=b[1]
        # Vertical transport cores deliberately articulated, not diagonal "walkways".
        px=(x+x2)/2;py=(y+y2)/2
        beam(tag+f"_VERTICAL_LIFT_{ii}",(px,py,z+24),(px,py,z2+130),95,110,shadow,"SKY TRANSPORT / UNVERIFIED")
        # Actual platforms are horizontal, not 85° disguised "walkways".
        beam(tag+f"_LOWER_HORIZONTAL_ACCESS_{ii}",(x,y,z+35),(px,py,z+35),125,30,ivory,"SKY TRANSPORT / UNVERIFIED")
        beam(tag+f"_UPPER_HORIZONTAL_ACCESS_{ii}",(px,py,z2+42),(x2,y2,z2+42),125,30,ivory,"SKY TRANSPORT / UNVERIFIED")

# Three huge civic voids between populated escarpments:
# no shell is generated around them, volume is reserved from the start.
VOID_CONTRACT=[
 {"name":"THE_GREAT_DIAGONAL_AIR","center":(0,0,1530),"radii":(390,450,1280)},
 {"name":"SKY_COUNCIL_VOID","center":(240,0,2780),"radii":(360,410,490)},
 {"name":"NORTH_PUBLIC_GULF","center":(-150,740,990),"radii":(330,390,300)}
]
# Literal datum markers as Empties, never opaque geometry that might mask a void.
for v in VOID_CONTRACT:
    ob=bpy.data.objects.new("RESERVED_AIR::"+v["name"],None)
    ob.location=v["center"];ob.empty_display_type="SPHERE"
    ob.empty_display_size=20;collection("VOID CONTRACT - NOT RENDERED").objects.link(ob)

# Major public paths at elevations, located next to populated districts.
PUBLIC=[
("GRAND_FORUM",(-180,-270,660),900,540,-8),
("PUBLIC_SUSPENDED_GARDEN",(-210,520,1700),760,420,21),
("SKY_LANTERN_SQUARE",(240,60,2650),730,470,-26)
]
for name,(x,y,z),w,d,ang in PUBLIC:
    tri_plaza(name+"_ACTUAL_PUBLIC_FLOOR",(x,y),w,d,ang,z,teal,"PUBLIC CIVIC - ROUTE UNVERIFIED")
    for j in range(2):
        xx=x+(-1 if j==0 else 1)*w*.40
        beam(name+f"_SERVICE_PYLON_{j}",(xx,y,z+10),(xx+60,y+40,z+260),45,50,bronze,"PUBLIC CIVIC - ROUTE UNVERIFIED")

# Urban spine hierarchy - deliberately 1-3 large sky crossings, never repeated floors.
for n,(a,b,w) in enumerate([
    ((-750,480,1800),(680,460,1800),150),
    ((-620,250,2650),(830,240,2650),180),
    ((-280,-180,3530),(550,-200,3530),135)
]):
    beam(f"PUBLIC_CROSS_CITY_SQUARE_{n}",a,b,w,40,ivory,"PUBLIC TRANSFERS - UNVERIFIED")

# Sky districts are not yet designed. Give explicitly marked compact stand-ins.
for i in range(6):
    angle=i*2*pi/6+.20
    x,y=3400*cos(angle),3350*sin(angle);z=800+180*(i%3)
    cube(f"H{i+1}::STUDY_MARKER_NOT_CITY",(x,y,z),(490,380,75),teal,"H / PLACEHOLDERS")
for i in range(16):
    angle=i*2*pi/16+.27
    x,y=4500*cos(angle),4420*sin(angle)
    cube(f"SB{i+1:02d}::PROVISIONAL_MARKER",(x,y,120),(105,100,220),signal,"SB / PLACEHOLDERS")

def cam(name,loc,target,ortho):
    ca=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,ca)
    collection("CAMERAS::FIXED").objects.link(ob)
    ob.location=loc
    d=Vector(target)-ob.location
    ob.rotation_euler=d.to_track_quat("-Z","Y").to_euler()
    ca.type="ORTHO";ca.ortho_scale=ortho;ca.clip_end=40000
    return ob
CAMS=[
("01_city", (10700,-13000,11500),(0,0,1350),14200),
("02_front", (180,-9600,3550),(0,0,2180),6300),
("03_oblique",(7500,-7700,5700),(0,0,2070),6800),
("04_side",(9300,600,3800),(0,0,2150),6800),
("05_back",(-120,9600,3900),(0,0,2130),6700),
("06_ground",(180,-2400,350),(0,0,2300),5900),
("07_public",(-270,-1400,1260),(-50,120,1680),3300),
("08_sky_residential",(-1700,-1600,2950),(-780,50,3030),2700),
]
for row in CAMS:cam(*row)
scene=bpy.context.scene;scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO";scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_cavity=True
scene.render.resolution_x=1024;scene.render.resolution_y=640
scene.render.resolution_percentage=100;scene.render.image_settings.file_format="PNG"
bpy.ops.wm.save_as_mainfile(filepath=str(out/"D46_BASE.blend"))
bpy.ops.export_scene.gltf(filepath=str(out/"D46_BASE.glb"),export_format="GLB",export_cameras=False,export_lights=False)
for n,*_ in CAMS[:4]:
    scene.camera=bpy.data.objects[n]
    scene.render.filepath=str(out/(n+".png"))
    bpy.ops.render.render(write_still=True)
manifest={"status":"D46_NATIVE_BASE_RENDERED_NOT_ART_ACCEPTED","blender":bpy.app.version_string,
          "mesh_count":len([o for o in bpy.data.objects if o.type=="MESH"]),
          "studied_neighborhoods":len(ZONES),"civic_public_square_count":len(PUBLIC),
          "cameras":[{"name":n,"loc":list(loc),"target":list(target),"scale":ortho} for n,loc,target,ortho in CAMS],
          "void_contract":VOID_CONTRACT,"art":"NOT_REVIEWED",
          "route":"NOT_VERIFIED", "official_coordinates":False}
(out/"D46_BASE_MANIFEST.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
print("D46_NATIVE_BASE_COMPLETED",json.dumps({k:v for k,v in manifest.items() if k not in ("cameras","void_contract")}))
