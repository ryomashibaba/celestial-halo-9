"""R33 D43 / genuine bpy authoring baseline. Research only; NOT approved art.
Structural intent: a diagonally migrating civic canyon with intertwined inhabited
escapements. No old D40/41/42 shapes are imported.
Run: python d43_base.py /tmp/d43-base
"""
import bpy, math, random, json, sys
from pathlib import Path
from mathutils import Vector
from math import sin, cos, pi
rng=random.Random(43001)
out=Path(sys.argv[-1]); out.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

def mat(name, rgb):
    m=bpy.data.materials.new(name); m.diffuse_color=(*rgb, 1); return m
ceramic=mat("01 silver pearl / civil structures",(.67,.76,.80))
dark=mat("02 abyss structural interior",(.105,.155,.22))
warm=mat("03 luminous ivory / public access",(.91,.84,.60))
azure=mat("04 blue-green residential lattice",(.22,.50,.55))
stone=mat("05 metropolitan basin",(.21,.25,.34))
water=mat("06 inner sea",(.075,.22,.35))
accent=mat("07 elevated district identity",(.36,.62,.68))
mark=mat("08 provisional facility only",(.58,.28,.28))

def box(name, center, dims, material, col=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o=bpy.context.object; o.name=name
    o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material)
    if col: move(o,col)
    return o

collections={}
def group(name):
    if name not in collections:
        c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
        collections[name]=c
    return collections[name]
def move(o, name):
    col=group(name)
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o)

def loft(name, points, widths, depths, material, collection):
    """Editable tapered structural ribbon with in-plane articulated city-face."""
    rings=[]
    for i, p in enumerate(points):
        here=Vector(p)
        tangent=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])
        tangent.normalize()
        ref=Vector((0,1,0))
        n=tangent.cross(ref).normalized()
        if n.length < .01: n=Vector((1,0,0))
        b=tangent.cross(n).normalized()
        w,d=widths[i]/2,depths[i]/2
        # irregular octagonal profile: asymmetric, open-canyon-facing facets
        profile=[(-.78,-1),(.72,-1),(1,-.66),(1,.56),(.53,1),(-.64,1),(-1,.56),(-1,-.67)]
        rings.append([tuple(here+n*ax*w+b*ay*d) for ax,ay in profile])
    verts=[v for ring in rings for v in ring]; faces=[]
    faces.append(tuple(range(7,-1,-1)))
    for j in range(len(rings)-1):
        for k in range(8):
            t=(k+1)%8
            faces.append((j*8+k,j*8+t,(j+1)*8+t,(j+1)*8+k))
    faces.append(tuple((len(rings)-1)*8+k for k in range(8)))
    mesh=bpy.data.meshes.new(name+" mesh")
    mesh.from_pydata(verts,[],faces); mesh.update()
    ob=bpy.data.objects.new(name,mesh); group(collection).objects.link(ob)
    mesh.materials.append(material)
    return ob

# 10km urban study: NOT registered official coordinates.
box("W0 research ground - not canonical", (0,0,-120),(10600,10300,160),stone,"W0 STUDY ONLY")
box("W0 artificial inner sea - placeholder", (3550,600,-29),(2700,4500,18),water,"W0 STUDY ONLY")
for i in range(11):
    x=-4500+i*610
    h=155+115*abs(sin(.71*i))
    box(f"W0 north range {i:02}",(x,4550,h*.45),(470,680,h),stone,"W0 STUDY ONLY")

# Three asymmetric inhabited fault masses, deliberately separated by real air:
# Important: not inherited from any rejected R33 mesh.
left=[(-1820,-650,130),(-1420,-580,780),(-1320,-200,1490),
      (-1670,220,2300),(-1210,520,3170),(-540,760,4240)]
right=[(1510,570,110),(1190,550,980),(1260,100,1740),
       (890,-330,2620),(1220,-550,3390)]
back=[(-240,1550,230),(-620,1260,1090),(-160,1150,2100),
      (510,1280,2920)]
for name,pts,ww,dd,ma in [
    ("CITY_MASS A left ascending cliff",left,[900,1020,850,760,680,400],[650,820,820,760,620,430],ceramic),
    ("CITY_MASS B right dislocated escarpment",right,[730,860,800,710,520],[680,790,760,640,400],ceramic),
    ("CITY_MASS C inhabited back-fold",back,[480,700,650,400],[720,660,600,350],dark),
]: loft(name,pts,ww,dd,ma,"CENTRAL: SCULPTABLE FORM")

# Construct inhabitable civic city segments *within and between* flanks.
# Every bay is a real public floor and open colonnade, not a painted decal.
levels=[410,825,1270,1690,2180,2720,3320]
widths=[490,520,570,450,510,390,320]
for ix,z in enumerate(levels):
    y=(-120+ix*110)
    w=widths[ix]
    if ix<5:
        box(f"PUBLIC-CANYON route level {ix} - actual deck",(-120,y,z),(w,510,38),warm,"PUBLIC FLOOR / ROUTE UNVERIFIED")
        for side in [-1,1]:
            for j in range(4):
                x=side*(w/2-15)
                box(f"civic balcony pier {ix}-{side}-{j}",(x,y-180+j*120,z+54),(30,30,110),dark,"PUBLIC FLOOR / ROUTE UNVERIFIED")
    for side,xc in [(-1,-1040),(1,1050)]:
        # genuine public pockets and habitation court volumes on the city face
        if (side,ix) in [(1,5),(-1,6)]: continue
        bx=xc + 70*sin(ix*.9+side)
        w2=310+25*ix
        box(f"habited urban court {side} at z{z}",(bx,y,z),(w2,450,44),warm,"INHABITED CITY / OPEN FLOORS")
        for j in range(4):
            by=y-165+j*108
            for s in [-1,1]:
                box(f"urban bay arc {side}-{ix}-{j}-{s}",(bx+s*(w2/2-20),by,z+100),(26,34,200),azure,"INHABITED CITY / OPEN FLOORS")
        box(f"upper residence lintel {side}-{ix}",(bx,y,z+198),(w2,450,28),azure,"INHABITED CITY / OPEN FLOORS")
# The two major 250m public halls have real air between columns and structure;
# no retrospective exterior shell fills the reserved civic volumes.
for j,(y,z,span) in enumerate([(-260,830,940),(200,1685,1030)]):
    box(f"public forum void {j} - FLOOR",(-40,y,z),(span,400,35),warm,"HERO PUBLIC SPACE GATE")
    for s in [-1,1]:
        x=s*span*.47
        for iy in [-150,150]:
            box(f"forum {j} piers {s} {iy}",(x,y+iy,z+260),(50,45,500),dark,"HERO PUBLIC SPACE GATE")
    box(f"public forum {j} open crown",(-40,y,z+530),(span,420,28),ceramic,"HERO PUBLIC SPACE GATE")
# Cross-axis bridges at stepped levels.
for i,(y,z) in enumerate([(100,910),(480,1850),(720,2690)]):
    box(f"multi-level metropolitan crossing {i}",(0,y,z),(1350,110,32),warm,"TRANSPORT: PROVISIONAL")
    for edge in [-1,1]:
        box(f"cross-axis framed rail {i} {edge}",(0,y+edge*52,z+40),(1350,15,80),dark,"TRANSPORT: PROVISIONAL")
# Vertical mass transit corridor indication; connections still unverified.
for x,y in [(-860,-200),(800,150)]:
    box(f"multi-level lift core {x}",(x,y,1400),(125,120,2800),dark,"TRANSPORT: PROVISIONAL")

# The six districts and 16 exceptional buildings are only study anchors here.
for i in range(6):
    a=2*pi*i/6+.38
    x,y=3350*cos(a),2900*sin(a)
    z=1220+330*(i%3)
    box(f"H{i+1} UNBUILT DISTRICT STUDY ANCHOR",(x,y,z),(580,520,75),accent,"H1-H6 PROVISIONAL")
    for k in [-1,1]:
        box(f"H{i+1} port court {k}",(x+k*160,y,z+100),(175,320,32),warm,"H1-H6 PROVISIONAL")
for i in range(16):
    a=2*pi*i/16+.12
    x,y=4600*cos(a),4100*sin(a)
    box(f"SB{i+1:02} UNBUILT ANCHOR",(x,y,110),(130,130,250),mark,"SB01-SB16 PROVISIONAL")

# Fixed cameras, reusable for edits of this exact .blend file.
def camera(name, location, target, ortho):
    cam=bpy.data.cameras.new(name); obj=bpy.data.objects.new(name,cam)
    group("FIXED 8 CAMERAS").objects.link(obj)
    obj.location=location
    vec=Vector(target)-obj.location
    obj.rotation_euler=vec.to_track_quat('-Z','Y').to_euler()
    cam.type='ORTHO';cam.ortho_scale=ortho;cam.clip_end=50000
    return obj
cameras=[
("01_city_aerial",(11500,-14500,13800),(0,0,1100),15000),
("02_hero_front",(300,-10500,3700),(0,0,2150),6200),
("03_hero_oblique",(8200,-8300,5900),(0,0,2050),6500),
("04_hero_side",(9800,600,4800),(0,0,2050),6900),
("05_hero_back",(-220,11100,3800),(0,0,2050),6900),
("06_ground_approach",(250,-2300,450),(0,0,2500),6100),
("07_civic_void",(0,-900,1100),(0,0,1450),3100),
("08_sky_residential",(-1700,-1900,2900),(-900,100,2900),2500)]
for args in cameras:camera(*args)

scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.1
scene.display.shading.curvature_valley_factor=.85
scene.render.resolution_x=900;scene.render.resolution_y=540;scene.render.resolution_percentage=100
scene.camera=bpy.data.objects[cameras[0][0]]
scene.render.image_settings.file_format='PNG'
bpy.ops.wm.save_as_mainfile(filepath=str(out/"D43_BASE_EDITABLE.blend"))
bpy.ops.export_scene.gltf(filepath=str(out/"D43_BASE.glb"),export_format='GLB',export_cameras=False,export_lights=False)
for name,*_ in cameras:
    scene.camera=bpy.data.objects[name]
    scene.render.filepath=str(out/(name+".png"))
    bpy.ops.render.render(write_still=True)
data={"kind":"D43_BASE_REAL_BPY_NOT_ART_PASS","blender":bpy.app.version_string,
      "camera_specs":[{"name":n,"location":list(loc),"target":list(target),"orthoscale":scale} for n,loc,target,scale in cameras],
      "objects":len(bpy.data.objects),
      "geometry_objects":[o.name for o in bpy.data.objects if o.type=='MESH'],
      "status":"ART_UNREVIEWED","official_coords":False}
(out/"D43_BASE_MANIFEST.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
print("D43_BASE_NATIVE_COMPLETED",json.dumps({"blender":bpy.app.version_string,"objects":len(bpy.data.objects),"renders":8}))
