"""CELESTIAL HALO-9 / R16 E0 — artist-authored double inhabited-shell void.

NONCANONICAL G0 3D massing: shell surfaces are shaped by explicit asymmetric
hand-authored control sections, not by repeated boxes/towers/pavilions. Gallery
floors are *inside* the shell, and visible public openings are missing topology
(not textures). Only an early ART G0 probe. No 10km master / M247-C adoption.

World Z-up, meters; genuine editable Blender 4.5 BLEND + GLB + 8 PNG.
"""
import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector
OUT=Path(sys.argv[-1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
M={}
def material(n,col):
    ma=bpy.data.materials.new(n)
    ma.diffuse_color=(*col,1.0)
    M[n]=ma
    return ma
material("01 pearl-white outer urban shell",(.79,.79,.73))
material("02 graphite hollow inward city",(.23,.29,.32))
material("03 champagne gallery city floor",(.68,.59,.45))
material("04 deep city cut edges",(.26,.36,.38))
material("05 civic arrival stone",(.50,.53,.52))
def col(n):
    c=bpy.data.collections.get(n)
    if c is None:
        c=bpy.data.collections.new(n)
        scene.collection.children.link(c)
    return c
def mesh_obj(name,verts,faces,mat,collection,role,editable=True):
    me=bpy.data.meshes.new(name+"_real_3d")
    me.from_pydata(verts,[],faces)
    me.update()
    ob=bpy.data.objects.new(name,me)
    col(collection).objects.link(ob)
    me.materials.append(M[mat])
    ob["R16_program"]=role
    ob["R16_artist_authored_control_topology"]=True
    ob["R16_art_approved"]=False
    if editable:
        ob.shape_key_add(name="Basis")
        ob.shape_key_add(name="R16_GUI_SCULPT_COPY")
    return ob
def spline(ks,t):
    """Cubic Catmull Rom evaluation on intentionally designed section controls."""
    t=max(0,min(1,t))
    f=t*(len(ks)-1)
    i=min(len(ks)-2,int(f));u=f-i
    a=ks[max(0,i-1)];b=ks[i];c=ks[i+1];d=ks[min(len(ks)-1,i+2)]
    return tuple(.5*((2*B)+(-A+C)*u+
         (2*A-5*B+4*C-D)*u*u+(-A+3*B-3*C+D)*u*u*u)
         for A,B,C,D in zip(a,b,c,d))
# z, center_x, center_y, x_radius, y_radius, rotation_deg, arc_start_deg
# The 2 curvilinear bodies are intentionally NON-mirrors:
# left a looming leeward low city cave, right a higher displaced sky-city.
CONTROL={
"L": [
 (70,-470,-170,505,390,-10,55),
 (260,-550,-125,590,475,-19,53),
 (550,-635,-70,710,480,-34,54),
 (930,-510,-185,625,545,-39,66),
 (1310,-460,-340,510,485,-50,88),
 (1710,-515,-470,565,445,-65,93),
 (2060,-710,-590,385,355,-84,108),
 ],
"R": [
 (35,570,230,410,385,22,-125),
 (390,610,235,480,490,28,-119),
 (720,790,150,615,500,43,-117),
 (1210,690,90,530,425,51,-110),
 (1640,515,260,480,450,68,-108),
 (2150,580,520,620,370,88,-98),
 (2740,890,685,365,325,108,-85),
 ]
}
SAMPLES_Z=64
SAMPLES_A=66
# Explicit deliberate open air windows; skip actual shell quads not texturing.
# coordinates (height s, along arcuate extent a)
WINDOWS={
"L":[(.14,.29,.17,.32),(.37,.51,.42,.58),(.65,.77,.20,.36)],
"R":[(.10,.26,.66,.81),(.34,.49,.36,.52),(.62,.73,.62,.78)]
}
def is_window(tag,s,a,outer):
    if not outer:return any((z0<s<z1 and p0<a<p1)
                for z0,z1,p0,p1 in WINDOWS[tag][1:])
    return any(z0<s<z1 and p0<a<p1 for z0,z1,p0,p1 in WINDOWS[tag])
def coord(tag,s,a,outer):
    z,cx,cy,rx,ry,rot,start=spline(CONTROL[tag],s)
    ang=math.radians(start+257*a)
    rotation=math.radians(rot)
    rad=1 if outer else (.62 if tag=="L" else .58)
    x=rx*rad*math.cos(ang);y=ry*rad*math.sin(ang)
    return (
      cx+x*math.cos(rotation)-y*math.sin(rotation),
      cy+x*math.sin(rotation)+y*math.cos(rotation),
      z+(.018*rx*math.sin(math.pi*a*1.8) if outer else 0)
    )
def make_shell(tag):
    verts=[]
    for outside in (True,False):
      for i in range(SAMPLES_Z+1):
        s=i/SAMPLES_Z
        for j in range(SAMPLES_A+1):
            a=j/SAMPLES_A
            verts.append(coord(tag,s,a,outside))
    count=(SAMPLES_Z+1)*(SAMPLES_A+1)
    faces=[]
    # Inner/outer hollow shell with genuinely missing large openings.
    for outside in (True,False):
      base=0 if outside else count
      for i in range(SAMPLES_Z):
       for j in range(SAMPLES_A):
        s=(i+.5)/SAMPLES_Z;a=(j+.5)/SAMPLES_A
        if is_window(tag,s,a,outside):continue
        n=base+i*(SAMPLES_A+1)+j
        q=(n,n+1,n+SAMPLES_A+2,n+SAMPLES_A+1)
        faces.append(q if outside else tuple(reversed(q)))
    # Top, bottom and ends: geometric thickness, not a 1-plane painted shell.
    for j in range(SAMPLES_A):
        a=j
        faces.append((a,a+1,a+1+count,a+count))
        t=SAMPLES_Z*(SAMPLES_A+1)
        faces.append((t+a+count,t+a+1+count,t+a+1,t+a))
    for i in range(SAMPLES_Z):
      n=i*(SAMPLES_A+1)
      faces.append((n+count,n,n+SAMPLES_A+1,n+SAMPLES_A+1+count))
      m=n+SAMPLES_A
      faces.append((m,m+count,m+SAMPLES_A+1+count,m+SAMPLES_A+1))
    return mesh_obj(tag+"_SCULPTED_INHABITED_HOLLOW_CITY_BODY",
       verts,faces,"01 pearl-white outer urban shell",
       "01 ARTHOUSE DOUBLE SHELL","multi-storey occupied architectural hollow; interior layouts NOT completed")
def gallery(tag,s0,a0,a1,kind):
    # Truly internal deck INSIDE the two wall surfaces, not an external shelf.
    Ns=55;rows=[]
    for rad in (.62 if tag=="L" else .58,.97):
      pts=[]
      for i in range(Ns+1):
        a=a0+(a1-a0)*i/Ns
        z,cx,cy,rx,ry,rot,start=spline(CONTROL[tag],s0)
        ang=math.radians(start+257*a)
        rr=rad
        X=rx*rr*math.cos(ang);Y=ry*rr*math.sin(ang)
        rot=math.radians(rot)
        pts.append((cx+X*math.cos(rot)-Y*math.sin(rot),
                    cy+X*math.sin(rot)+Y*math.cos(rot),z+.8))
      rows.append(pts)
    v=rows[0]+rows[1];f=[]
    for i in range(Ns):
       f.append((i,i+1,Ns+2+i,Ns+1+i))
    return mesh_obj(tag+"_REAL_INTERNAL_CITY_GALLERY_"+kind,
         v,f,"03 champagne gallery city floor",
         "02 REAL INNER URBAN FLOORS",
         "single spatial public street inside source hollow, accessibility NOT certified")
for tag in ("L","R"):make_shell(tag)
GALLERY_CONTROLS={
"L":[(.205,.27,.72,"LOWER_CIVIC"),
     (.485,.07,.44,"LIBRARY_CULTURAL"),
     (.745,.44,.83,"HIGH_LIFE")],
"R":[(.18,.09,.54,"GROUND_TRANSIT"),
     (.45,.39,.88,"MARKET_CULTURE"),
     (.695,.05,.46,"HIGH_INHABITED")]
}
for tag,data in GALLERY_CONTROLS.items():
 for s0,a0,a1,name in data:gallery(tag,s0,a0,a1,name)
# Shared municipal entry: self-contained irregular civic floor INSIDE both
# shell bodies' near-ground ranges, NOT a large bridge.
pts=[(-650,-680),(80,-760),(540,-470),(680,-180),(280,100),
      (-80,285),(-600,185),(-790,-220)]
v=[(x,y,z) for z in (15,25) for x,y in pts]
f=[tuple(range(7,-1,-1)),tuple(range(8,16))]
f.extend((i,(i+1)%8,8+(i+1)%8,8+i) for i in range(8))
mesh_obj("SHARED_OPEN_PUBLIC_ARRIVAL_BASIN",v,f,"05 civic arrival stone",
    "03 GROUND PUBLIC CITY", "common occupied arrival surface, geometry only")
# Deliberately exclude boxes, neon strips, decorative ribs and arbitrary H1/H6 markers.
SCENE_CAMERA={
 "01_FRONTAL":((0,-5200,1480),(0,0,1280),3950),
 "02_OBLIQUE":((3700,-4400,3300),(0,0,1450),4500),
 "03_SIDE":((5500,0,1950),(0,0,1400),4100),
 "04_REAR":((0,5000,1760),(0,0,1400),3900),
 "05_AERIAL":((-3200,-3600,6400),(0,0,1250),4700),
 "06_GROUND_ARRIVAL":((0,-900,34),(100,280,620),None),
 "07_CIVIC_HOLLOW":((-300,-20,400),(450,100,1350),None),
 "08_HIGH_CITY_EYE":((300,300,1630),(-520,0,1710),None),
}
for name,(eye,target,scale) in SCENE_CAMERA.items():
 d=bpy.data.cameras.new(name)
 o=bpy.data.objects.new(name,d)
 col("04 EIGHT G0 ART CAMERAS").objects.link(o)
 o.location=eye
 o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
 d.clip_start=.2;d.clip_end=100000
 if scale:d.type="ORTHO";d.ortho_scale=scale
 else:d.type="PERSP";d.lens=24
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_cavity=True
scene.render.resolution_x=1060
scene.render.resolution_y=720
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.camera=bpy.data.objects["02_OBLIQUE"]
scene["R16_FORMAL_M247C_ADOPTED"]=False
scene["R16_10KM_MASTER_COMPLETED"]=False
scene["R16_MINECRAFT_WRITE"]=False
scene["R16_ART_STATUS"]="G0_UNREVIEWED"
scene["R16_SOURCE_CONCEPT"]="asymmetric inhabited double hollow city body"
scene["R16_UNCERTIFIED"]="architecture interior, circulation, structural safety"
native=OUT/"R16_E0_EDITABLE_DOUBLE_HOLLOW_CITY.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(native))
glb=OUT/"R16_E0_DOUBLE_HOLLOW_CITY.glb"
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
                         export_cameras=False,export_lights=False)
for name in SCENE_CAMERA:
 scene.camera=bpy.data.objects[name]
 scene.render.filepath=str(OUT/(name+".png"))
 bpy.ops.render.render(write_still=True)
m=[o for o in bpy.data.objects if o.type=="MESH"]
summary={
 "title":"R16 first AUTHORED sculptural architectural void (G0), real editable BLEND",
 "architectural_form":"two distinctly different large hollow continuous curved city bodies, with inner genuine public gallery floors",
 "hand_authored_section_controls":CONTROL,
 "large_urban_window_cutouts":WINDOWS,
 "mesh_count":len(m),
 "vertices":sum(len(o.data.vertices) for o in m),
 "triangles":sum(sum(max(1,len(p.vertices)-2) for p in o.data.polygons) for o in m),
 "saved_blend":native.name,
 "saved_glb":glb.name,
 "real_cam_pngs":[n+".png" for n in SCENE_CAMERA],
 "shape_keys":"Basis plus artist-editable R16_GUI_SCULPT_COPY per original mesh",
 "not_city_master":True,"public_access_verified":False,
 "art":"G0_UNREVIEWED","formal_M247C_adopted":False,"minecraft_written":False,
 "blender_version":bpy.app.version_string
}
(OUT/"R16_E0_TRUE_3D_MANIFEST.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf8")
print("R16_E0_NATIVE_SCULPTURAL_VOID_REAL_BLENDER_RENDERED",json.dumps({k:v for k,v in summary.items() if k not in ("hand_authored_section_controls","large_urban_window_cutouts")}))
