"""Space-first / thick-section-first authoring for Gate B research.

The hand-authored cross-sections begin with the NAVE public room and H1's
market/school/housing spaces. The surrounding alpha masses follow those room
sections; beta is a populated diagonal public route through them. This is a
single reviewed study, not a city generator.
"""
import bpy, bmesh, os, math, json
from mathutils import Vector

ROOT=r"C:\Users\ryoma\Projects\CELESTIAL_HALO9\repo_gateb_section_work\studies\M3D-1S\J7\R33-S28\GATE_B_SECTION_FIRST"
BASE=os.path.join(ROOT,"BASELINE_INT21.blend")
OUT=os.path.join(ROOT,"SPATIAL_A0.blend")
IMG=os.path.join(ROOT,"A0")
os.makedirs(IMG,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=BASE)
scene=bpy.context.scene

protected={"W0_NORTH_FRACTURED_RANGE","W0_WEST_BASALT_ESCARPMENT",
           "W0_GROUND_BASIN","W0_EASTERN_ARTIFICIAL_SEA"}
fixed_cameras={"E11_NAVE_HUMAN","E11_H1_HUMAN","E11_URBAN_AERIAL",
               "E11_WATER_APPROACH","E11_REVERSE"}
for obj in list(bpy.data.objects):
    if obj.name in protected or obj.name in fixed_cameras or obj.type=="LIGHT":
        continue
    bpy.data.objects.remove(obj,do_unlink=True)

def mat(name,color,metal=0.12,rough=0.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Metallic"].default_value=metal
    p.inputs["Roughness"].default_value=rough
    return m

NAVE=mat("NAVE | pale civic stone",(0.64,0.72,0.72),0.16,0.36)
NAVE_INNER=mat("NAVE | warm occupied strata",(0.40,0.51,0.51),0.08,0.42)
H1_MARKET=mat("H1 | market mineral",(0.60,0.47,0.31),0.12,0.4)
H1_SCHOOL=mat("H1 | school porcelain",(0.76,0.78,0.68),0.12,0.38)
H1_HOMES=mat("H1 | inhabited umber",(0.34,0.48,0.43),0.10,0.44)
BETA=mat("BETA | diagonal public artery",(0.73,0.82,0.82),0.22,0.32)
ALPHA_W=mat("ALPHA west | cliff-grafted basalt",(0.105,0.18,0.20),0.24,0.38)
ALPHA_E=mat("ALPHA east | lifted pearl mass",(0.53,0.67,0.67),0.18,0.34)

def mesh_object(name,verts,faces,material):
    me=bpy.data.meshes.new(name+" | authored mesh")
    me.from_pydata(verts,[],faces); me.materials.append(material); me.update()
    bm=bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(me); bm.free(); me.update()
    ob=bpy.data.objects.new(name,me); scene.collection.objects.link(ob)
    return ob

def tunnel_shell(name,xcenter,stations,outer,inner,material):
    """A real hollow public room; each station is y, scale, xshift, zshift."""
    n=len(outer); assert n==len(inner)
    verts=[]; faces=[]
    for y,scale,dx,dz in stations:
        for loop in (outer,inner):
            verts.extend((xcenter+dx+x*scale,y,z*scale+dz) for x,z in loop)
    ring=2*n
    for s in range(len(stations)-1):
        for i in range(n):
            faces.append((s*ring+i,s*ring+(i+1)%n,(s+1)*ring+(i+1)%n,(s+1)*ring+i))
            faces.append((s*ring+n+(i+1)%n,s*ring+n+i,(s+1)*ring+n+i,(s+1)*ring+n+(i+1)%n))
    # Thick annular portals at both ends. The center remains an actual open room.
    for end in (0,len(stations)-1):
        off=end*ring
        for i in range(n): faces.append((off+i,off+n+i,off+n+(i+1)%n,off+(i+1)%n))
    return mesh_object(name,verts,faces,material)

def prism(name,outline,y0,y1,z0,z1,material):
    """Irregular, explicit plan profile with a substantial vertical section."""
    pts=[(x,z) for x,z in outline]
    n=len(pts); verts=[]
    verts += [(x,y0+z,z0) for x,z in pts]
    verts += [(x,y1+z,z0) for x,z in pts]
    verts += [(x,y0+z,z1) for x,z in pts]
    verts += [(x,y1+z,z1) for x,z in pts]
    faces=[tuple(reversed(range(n))),tuple(3*n+i for i in range(n))]
    for i in range(n):
        j=(i+1)%n
        faces += [(i,j,n+j,n+i),(2*n+i,2*n+j,3*n+j,3*n+i),
                  (i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)]
    return mesh_object(name,verts,faces,material)

def tiered_court(name,cx,cy,outer,inner,levels,material,open_south=True):
    """Thick inhabited tiers around a true court and through public gateways."""
    n=len(outer); assert len(inner)==n
    verts=[]; faces=[]
    for z,oscale,iscale,dx,dy in levels:
        for loop,scale in ((outer,oscale),(inner,iscale)):
            for x,y in loop: verts.append((cx+dx+x*scale,cy+dy+y*scale,z))
    def v(level,loop,i): return level*(2*n)+loop*n+(i%n)
    for i in range(n): faces.append((v(0,0,i),v(0,0,i+1),v(0,1,i+1),v(0,1,i)))
    for lev in range(len(levels)-1):
        for i in range(n):
            if not(open_south and i in (0,1)): # a broad inhabited street opens to the approach
                faces.append((v(lev,0,i),v(lev,0,i+1),v(lev+1,0,i+1),v(lev+1,0,i)))
            faces.append((v(lev,1,i+1),v(lev,1,i),v(lev+1,1,i),v(lev+1,1,i+1)))
            faces.append((v(lev+1,0,i),v(lev+1,0,i+1),v(lev+1,1,i+1),v(lev+1,1,i)))
    return mesh_object(name,verts,faces,material)

def ramp(name,stations,width,thickness,material):
    """A genuinely walkable, sloping route with finite thick section."""
    verts=[]; faces=[]
    for i,(x,y,z) in enumerate(stations):
        if i==0: dx,dy=stations[1][0]-x,stations[1][1]-y
        elif i==len(stations)-1: dx,dy=x-stations[i-1][0],y-stations[i-1][1]
        else: dx,dy=stations[i+1][0]-stations[i-1][0],stations[i+1][1]-stations[i-1][1]
        ln=max(1e-6,math.hypot(dx,dy)); nx,ny=-dy/ln,dx/ln
        verts.extend([(x+nx*width/2,y+ny*width/2,z),(x-nx*width/2,y-ny*width/2,z),
                      (x+nx*width/2,y+ny*width/2,z-thickness),(x-nx*width/2,y-ny*width/2,z-thickness)])
    for i in range(len(stations)-1):
        a=4*i;b=4*(i+1)
        faces.extend([(a,a+1,b+1,b),(a+2,b+2,b+3,a+3),(a,a+2,b+2,b),
                      (a+1,b+1,b+3,a+3)])
    return mesh_object(name,verts,faces,material)

def gallery_bridge(name,x0,x1,y,z,width,height,material):
    # a deep civic crossing, expressed as a faceted spatial bay, not a thin plank
    outline=[(x0,y-width/2,z),(x1,y-width/2,z),(x1+35,y,z+height),
             (x1,y+width/2,z),(x0,y+width/2,z),(x0-35,y,z+height)]
    # This broad section is a public room/connection; floors and underside are real mass.
    verts=[]
    for dz in (0,-36): verts.extend((x,yy,zz+dz) for x,yy,zz in outline)
    n=len(outline);faces=[tuple(range(n)),tuple(n+i for i in reversed(range(n)))]
    for i in range(n): faces.append((i,(i+1)%n,n+(i+1)%n,n+i))
    return mesh_object(name,verts,faces,material)

# 1) NAVE: begin with the inner public room and its substantial built thickness.
# The room is an 800 m clear hall with a 120–170 m structural/occupied section.
nave_outer=[(-525,0),(-525,145),(-480,315),(-360,455),(-180,555),(80,545),
            (300,470),(455,340),(525,145),(515,0)]
nave_inner=[(-395,0),(-395,135),(-355,260),(-255,365),(-120,430),(70,425),
            (220,365),(325,260),(395,130),(385,0)]
nave=tunnel_shell("NAVE_ALPHA_WEST_OCCUPIED_VAULT",-120,
    [(-310,0.88,0,0),(-175,1.0,0,0),(110,1.0,0,0),(390,0.94,45,18)],
    nave_outer,nave_inner,NAVE)

# Internal public section: two occupied galleries, stair/ramp ascents and bridges.
for side,sign in (("west",-1),("east",1)):
    prism("NAVE_"+side.upper()+"_LOWER_READING_GALLERY",
          [(sign*210,0),(sign*395,0),(sign*375,40),(sign*210,40)],-110,340,115,150,NAVE_INNER)
    prism("NAVE_"+side.upper()+"_UPPER_PUBLIC_GALLERY",
          [(sign*205,0),(sign*365,0),(sign*345,42),(sign*205,42)],40,380,225,265,NAVE)
    ramp("NAVE_"+side.upper()+"_PROMENADE_RISE",
         [(sign*355,-190,5),(sign*345,-60,35),(sign*295,95,115),(sign*250,230,225)],
         92,32,NAVE_INNER)
gallery_bridge("NAVE_LEVEL_1_CROSSING",-300,300,-25,150,70,34,NAVE)
gallery_bridge("NAVE_LEVEL_2_CROSSING",-250,330,250,260,90,42,NAVE_INNER)

# The entrance concourse has an ordered procession and broad civic stair section;
# the protected W0 basin remains the ground, with no added generic floor sheet.
ramp("NAVE_W0_PROCESSIONAL_ASCENT",
     [(-40,-305,0),(-35,-225,12),(15,-150,28),(75,-75,48),(105,5,66)],
     155,22,NAVE)

# 2) H1: connected program spaces in section. Each is a real hollow volume.
market_outer=[(-205,0),(-205,95),(-160,185),(-55,235),(95,215),(185,130),(205,0),(-10,-12)]
market_inner=[(-145,0),(-145,78),(-108,135),(-40,170),(72,157),(130,95),(145,0),(-8,-5)]
tunnel_shell("H1_MARKET_HALL_AND_COVERED_STREET",495,
    [(185,0.90,0,0),(305,1.0,0,0),(560,0.98,25,0)],market_outer,market_inner,H1_MARKET)

school_outer=[(-215,0),(-215,110),(-170,235),(-70,325),(90,315),(190,205),(225,80),(220,0)]
school_inner=[(-150,0),(-150,92),(-115,184),(-48,244),(62,239),(130,170),(160,70),(155,0)]
tunnel_shell("H1_SCHOOL_ATRIUM_AND_PUBLIC_LIBRARY",1020,
    [(490,0.84,0,55),(650,1.0,0,0),(930,0.92,-35,30)],school_outer,school_inner,H1_SCHOOL)

outer=[(-310,-115),(-260,-300),(-40,-375),(230,-310),(390,-95),(335,160),
       (145,320),(-135,300),(-340,125)]
inner=[(-165,-55),(-138,-155),(-22,-198),(118,-161),(210,-45),(176,95),
       (78,168),(-72,153),(-184,68)]
h1west=tiered_court("H1_WEST_INHABITED_COURT_HOUSING",430,775,outer,inner,
    [(18,1.0,1.0,0,0),(108,1.02,1.02,-12,0),(218,.93,.90,18,12),
     (330,.82,.79,45,35),(405,.72,.66,66,58)],H1_HOMES)
outer_e=[(-335,-105),(-295,-315),(-70,-420),(235,-330),(415,-100),(350,190),
         (140,350),(-155,320),(-360,125)]
inner_e=[(-170,-48),(-150,-181),(-35,-240),(126,-190),(232,-42),(194,110),
         (76,210),(-82,189),(-198,70)]
h1east=tiered_court("H1_EAST_LIFTED_RESIDENTIAL_ARCADE",1335,860,outer_e,inner_e,
    [(160,1.0,1.0,0,0),(260,1.03,1.0,-18,12),(390,.93,.88,-35,36),
     (525,.80,.76,-56,65),(610,.70,.63,-76,90)],H1_HOMES)

# An H1 public street stitches market, school, homes and NAVE. It rises through
# three broad inhabited landings rather than ending at isolated display blocks.
ramp("H1_MULTILEVEL_PUBLIC_STREET",
     [(255,60,8),(340,245,28),(480,430,70),(615,590,118),(765,715,185),
      (930,820,255),(1100,910,345)],
     112,34,H1_SCHOOL)
gallery_bridge("H1_MARKET_TO_SCHOOL_GALLERY",610,875,560,120,88,38,H1_MARKET)
gallery_bridge("H1_HOMES_SHARED_CIVIC_LEVEL",690,1190,830,260,115,45,H1_HOMES)

# 3) Beta is a diagonal public rift occupied by ramps, landings and lift halls.
# Its rising route cuts across the NAVE/H1 section instead of forming a roof.
ramp("BETA_DIAGONAL_RIFT_PUBLIC_RAMP",
     [(-265,140,88),(-130,275,136),(50,420,224),(235,555,340),
      (430,690,485),(630,820,640),(800,925,770)],
     82,38,BETA)
gallery_bridge("BETA_RIFT_NAVE_LANDING",-210,235,300,176,130,50,BETA)
gallery_bridge("BETA_RIFT_H1_LANDING",445,865,710,208,165,60,BETA)

# 4) The two alpha masses follow these occupied rooms. The west one physically
# grafts into the protected basalt escarpment; the lifted east one is the upper
# H1 residential district, with its actual courts and public routes inside.
west_outline=[(-1050,-330),(-840,-520),(-620,-430),(-555,-200),(-650,35),
              (-790,245),(-1025,370),(-1250,250),(-1320,-5),(-1190,-250)]
prism("ALPHA_WEST_W0_GRAFTED_LIVING_MASS",west_outline,-135,245,15,390,ALPHA_W)

# An inhabited, angular three-level east shell around the raised H1 court group.
east_outline=[(410,-80),(575,-230),(830,-210),(1040,-55),(1080,185),(930,350),
              (690,365),(500,240),(390,80)]
prism("ALPHA_EAST_LIFTED_H1_LIVING_MASS",east_outline,640,1070,260,745,ALPHA_E)

# Preserve source camera transforms, lights, W0, world and render settings.
scene.camera=bpy.data.objects["E11_URBAN_AERIAL"]
bpy.ops.wm.save_as_mainfile(filepath=OUT)
render={"engine":scene.render.engine,"resolution":[scene.render.resolution_x,scene.render.resolution_y],
        "samples":scene.cycles.samples if scene.render.engine=="CYCLES" else None,
        "exposure":scene.view_settings.exposure,"view_transform":scene.view_settings.view_transform,
        "look":scene.view_settings.look,"fixed_E11":True,"protected_W0":True,"lights_unchanged":True,
        "cutaway":False,"camera_matrices_changed":False}
for name in ("E11_NAVE_HUMAN","E11_H1_HUMAN","E11_URBAN_AERIAL"):
    scene.camera=bpy.data.objects[name]
    scene.render.filepath=os.path.join(IMG,name+".png")
    bpy.ops.render.render(write_still=True)
with open(os.path.join(IMG,"render.json"),"w",encoding="utf-8") as f:
    json.dump(render,f,ensure_ascii=False,indent=2)
print(json.dumps({"saved":OUT,"new_objects":[o.name for o in scene.objects if o.name not in protected|fixed_cameras],
                  "render":render},ensure_ascii=False))
