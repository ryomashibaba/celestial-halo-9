"""INT17 — architecture-first M247-C representative civic section.  RESEARCH / ART UNREVIEWED.

The INT11–INT16 egg-shell geometry has failed direct image critique. This work
uses a NEW protected INT15 study copy; in THIS COPY ONLY, removes rejected
INT* building and bridge meshes while preserving official W0 geometry and the
three original E11 camera matrices. An authored sequence of inhabited ridge
buildings, open NAVE hall, staggered H1 urban façades, diagonal civic corridor,
four public destinations and sea arrival is built as true native Blender meshes.

A concrete spatial experiment, NOT an officially adopted new direction;
forms are designed from individually specified profiles rather than huge
spheres, shells, repeated skyscraper instancing, or decorative Boolean holes.
The method is manual CODE/mesh geometry, NOT interactive GUI hand sculpture.
"""
import bpy, math, sys, json, hashlib
from mathutils import Vector
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[args.index('--output')+1]);out.mkdir(parents=True,exist_ok=True)
(out/'renders').mkdir(exist_ok=True)
src=Path(bpy.data.filepath)
PARENT='e996fab613904dc557638612d4380ba67ef5c6bbd4aa9fb219d9aeaa8f511fb9'
assert src.name=='INT17_SOURCE.blend' and hashlib.sha256(src.read_bytes()).hexdigest()==PARENT
sc=bpy.context.scene
assert sc['CONSTRUCTION']=='HOLD' and sc['COMPLETED_TARGETS']==sc['FORMAL_ART_ACCEPTED']==0
fixed=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
w0=('W0_NORTH_FRACTURED_RANGE','W0_WEST_BASALT_ESCARPMENT','W0_GROUND_BASIN','W0_EASTERN_ARTIFICIAL_SEA')
def digest(o):
    h=hashlib.sha256()
    for v in o.data.vertices:h.update((','.join(f'{float(c):.10g}' for c in v.co)+';').encode())
    return h.hexdigest()
orig_w0={n:digest(bpy.data.objects[n]) for n in w0}
orig_cams={n:bpy.data.objects[n].matrix_world.copy() for n in fixed}
# Physically clean ONLY the new experiment COPY.  No CUTAWAY render toggles.
rejected=[o for o in list(sc.objects) if o.type=='MESH' and
    o.name.startswith(('INT1_','INT2_','INT3_','INT4_','INT5_',
                       'INT6_','INT7_','INT8_','INT9_',
                       'INT10_','INT11_','INT12_','INT13_','INT14_','INT15_','INT16_'))]
assert len(rejected)>=40,('REJECTED_STUDY_SCENE_NOT_FOUND',len(rejected))
deleted=[o.name for o in rejected]
for o in rejected:bpy.data.objects.remove(o,do_unlink=True)
assert all(n in bpy.data.objects for n in w0+fixed)

coll=bpy.data.collections.new('INT17_ARCHITECTURE_FIRST_RESEARCH_COPY')
sc.collection.children.link(coll)
mats={}
def material(name,rgba,metal=.05,rough=.67):
    m=bpy.data.materials.new('INT17_'+name);m.diffuse_color=(*rgba,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgba,1);p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough
    mats[name]=m
material('west_foundation',(.30,.34,.38))
material('west_library',(.72,.69,.61))
material('east_city',(.74,.75,.71))
material('east_deep',(.22,.29,.34))
material('civic_stone',(.79,.77,.70))
material('bridge',(.50,.57,.59),.3)
material('school',(.80,.68,.53))
material('market',(.60,.49,.38))
material('green',(.20,.38,.34))
material('crown',(.82,.84,.81),.24)
material('roof',(.25,.34,.39))
material('plaza',(.57,.54,.49))

made=[]
def native(name,pts,faces,mat):
    mesh=bpy.data.meshes.new('INT17_'+name)
    mesh.from_pydata([tuple(p) for p in pts],[],faces)
    mesh.update()
    ob=bpy.data.objects.new(mesh.name,mesh);coll.objects.link(ob)
    ob.data.materials.append(mats[mat])
    for face in ob.data.polygons:face.use_smooth=False
    assert len(ob.data.polygons)>=5
    assert all(math.isfinite(float(v)) for vert in mesh.vertices for v in vert.co)
    made.append(ob.name)
    return ob

def building(name,footprint,roof,z0,z1,mat):
    """Each hand-authored lower/upper footprint is specific to this programme.
    Closed faceted inhabited MASS, not a thin plate or a generic loft copy."""
    assert len(footprint)==len(roof)>=5 and z1-z0>=35
    n=len(footprint);vs=[(x,y,z0) for x,y in footprint]+[(x,y,z1) for x,y in roof]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    for i in range(n):
        j=(i+1)%n
        faces.append((i,j,j+n,i+n))
    return native(name,vs,faces,mat)

def terrace(name,path,width,depth,mat):
    """One named, usable thick civic floor corridor; not replicated ornamental shelves."""
    assert len(path)>=2 and depth>=12
    vertices=[]
    for i,p in enumerate(path):
        prior=Vector(path[max(0,i-1)])
        future=Vector(path[min(len(path)-1,i+1)])
        delta=future-prior
        norm=Vector((-delta.y,delta.x,0)).normalized()
        center=Vector(p)
        for z in (0,-depth):
            for side in (-1,1):
                vertices.append(tuple(center+side*width[i]/2*norm+Vector((0,0,z))))
    faces=[]
    # 4 verts per station: top -/+ then lower -/+.
    for i in range(len(path)-1):
        a=i*4;b=(i+1)*4
        faces.extend([(a,a+1,b+1,b),(a+2,b+2,b+3,a+3),
                      (a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
    faces.extend([(0,1,3,2),(4*(len(path)-1),4*(len(path)-1)+2,4*(len(path)-1)+3,4*(len(path)-1)+1)])
    return native(name,vertices,faces,mat)

def massive_beam(name,a,b,width,depth,mat):
    """Structural section support; axis-aligned cross-section is in true 3D."""
    A=Vector(a);B=Vector(b);v=(B-A).normalized();axis=Vector((0,0,1))
    side=v.cross(axis)
    if side.length<.01:side=Vector((1,0,0))
    side.normalize();up=side.cross(v).normalized()
    base=[]
    for p in (A,B):
        for s,t in [(-1,-1),(1,-1),(1,1),(-1,1)]:
            base.append(tuple(p+side*s*width/2+up*t*depth/2))
    fs=[(0,3,2,1),(4,5,6,7)]
    for i in range(4):j=(i+1)%4;fs.append((i,j,j+4,i+4))
    return native(name,base,fs,mat)

# 1. W0-rooted asymmetric LIVED civic foundation: western zone of the diagonal
# negative space. Hand-designed silhouettes contain actual thick cubic-km volumes.
building('WEST_FRACTURED_ARCHIVE_CIVIC_ROOT',
 [(-1800,-640),(-1040,-810),(-520,-540),(-480,190),
  (-730,750),(-1480,1070),(-1940,430)],
 [(-1690,-410),(-1120,-660),(-610,-420),(-580,250),
  (-830,670),(-1520,900),(-1910,310)],
 70,620,'west_foundation')
building('WEST_NAVE_PUBLIC_LIBRARY_MEGAHALL_BODY',
 [(-1160,-190),(-560,-270),(-280,90),(-355,750),
  (-780,1280),(-1460,1200),(-1690,500)],
 [(-1270,-90),(-620,-160),(-330,220),(-570,880),
  (-960,1190),(-1530,1070),(-1640,520)],
 530,1420,'west_library')
building('WEST_UPPER_INHABITED_CITADEL',
 [(-1470,650),(-920,620),(-470,1040),(-670,1650),
  (-1320,1850),(-1690,1290)],
 [(-1510,810),(-1000,740),(-520,1160),(-850,1650),
  (-1290,1720),(-1550,1400)],
 1370,1870,'west_foundation')

# 2. Eastern core is offset and higher: the middle plaza stays OPEN for H1.
# Thin connection planks are avoided; each occupancy zone has 100m+ thick mass.
building('EAST_H1_LOWER_CIVIC_ESCARPMENT',
 [(1290,-450),(1820,-510),(2200,-90),(2420,660),
  (2180,1410),(1700,1650),(1350,1060)],
 [(1250,-250),(1880,-390),(2220,70),(2230,850),
  (1980,1430),(1640,1480),(1380,950)],
 170,820,'east_deep')
building('EAST_H1_THICK_RESIDENTIAL_MEGABLOCK',
 [(1390,360),(1810,150),(2410,490),(2470,1350),
  (2010,2050),(1510,1860),(1240,1150)],
 [(1330,420),(1900,260),(2300,720),(2370,1570),
  (2040,2150),(1520,1740),(1360,1200)],
 790,1590,'east_city')
building('EAST_ASCENDING_PUBLIC_SKY_CITY',
 [(1620,900),(2160,650),(2590,1150),(2500,1970),
  (2050,2450),(1610,2040)],
 [(1710,1150),(2320,840),(2640,1350),(2480,2160),
  (2050,2310),(1710,2010)],
 1510,2210,'crown')
building('HIGH_SEVERED_NORTH_METROPOLITAN_BODY',
 [(980,1790),(1340,1660),(1830,1810),(2010,2370),
  (1600,2800),(1070,2590)],
 [(910,1830),(1310,1650),(1830,1790),(1930,2350),
  (1510,2750),(1060,2530)],
 1900,2660,'west_library')

# 3. Distinct NAVE public interior, aligned with ORIGINAL E11 human eye
# (x=15,y=-360,z=74 looking north). Keep deep visual axis at x=-150..+800.
terrace('NAVE_MAIN_CIVIC_FLOOR',
 [(70,-300,66),(115,10,82),(180,360,110),(200,700,138),(315,1080,184)],
 [320,350,360,325,300],28,'plaza')
# Multi-level open-front architectural roof frames (not a giant flat ceiling)
massive_beam('NAVE_PUBLIC_SOUTH_PYLON_W',(-380,160,60),(-310,220,450),112,100,'west_library')
massive_beam('NAVE_PUBLIC_SOUTH_PYLON_E',(860,190,80),(930,250,480),140,135,'east_city')
massive_beam('NAVE_NORTH_OCCUPIED_CROSS_VAULT',(-335,710,540),(880,860,710),95,115,'civic_stone')
massive_beam('NAVE_DIAGONAL_PUBLIC_NORTH_ROOF',(-320,430,450),(870,960,770),130,100,'roof')
building('NAVE_STATION_PUBLIC_GATE_BODY',
 [(-340,910),(220,880),(570,1050),(600,1460),(80,1630),(-440,1310)],
 [(-350,940),(230,910),(570,1100),(520,1430),(50,1580),(-420,1270)],
 110,390,'civic_stone')
# The central void's dramatic diagonal line is OPEN air, not a decorative pipe.
massive_beam('BETA_SLANTED_PUBLIC_TRANSPORT_SPINE',
 (-240,920,330),(1140,1850,2110),115,130,'roof')
massive_beam('BETA_UPPER_FRACTURE_NORTH',
 (1100,1820,2080),(1750,2480,2500),95,105,'west_foundation')

# 4. H1 actual occupied street aligned with ORIGINAL eye (760,270,439).
# No new solid occupies this eye. Layered school, market and habitat appear
# AHEAD of the viewer with air between sides; not surface labels on a blob.
terrace('H1_MARKET_TO_SCHOOL_BOULEVARD',
 [(760,300,432),(815,520,445),(875,730,485),(995,1010,535)],
 [155,180,160,135],22,'plaza')
building('H1_MARKET_CIVIC_TRADING_HALL',
 [(430,470),(620,410),(700,620),(690,970),(480,1110),(340,830)],
 [(430,510),(630,465),(720,630),(650,935),(470,1040),(360,820)],
 380,700,'market')
building('H1_SCHOOL_PUBLIC_ATRIUM',
 [(1070,490),(1290,420),(1350,710),(1240,990),(1100,1110),(990,825)],
 [(1060,540),(1260,470),(1390,720),(1270,950),(1100,1050),(1010,840)],
 520,860,'school')
building('H1_COMMONS_ROOF_GARDEN_BLOCK',
 [(520,1240),(850,1130),(1120,1250),(1080,1660),(700,1850),(430,1520)],
 [(490,1250),(840,1110),(1130,1310),(1020,1610),(710,1770),(450,1500)],
 790,1150,'green')
building('H1_RESIDENTIAL_CRAG_SOUTH',
 [(1220,1120),(1410,1160),(1470,1510),(1390,1810),(1180,1750),(1100,1370)],
 [(1200,1170),(1420,1150),(1490,1500),(1400,1770),(1180,1680),(1140,1410)],
 830,1310,'east_city')
terrace('H1_SCHOOL_TO_COMMONS_PUBLIC_BRIDGE',
 [(1005,970,555),(930,1130,640),(890,1330,795)],
 [118,120,140],45,'bridge')
# 5. Native transport shaft has actual walls + four named station approaches;
# this is not certified lift function, and is not a 60% walkable ramp.
massive_beam('H1_VERTICAL_TRANSIT_NEAR_SIDE',
 (1115,635,370),(1115,635,905),48,75,'east_deep')
massive_beam('H1_VERTICAL_TRANSIT_FAR_SIDE',
 (1175,660,370),(1175,660,905),52,75,'east_deep')
terrace('H1_SCHOOL_LANDING',( (970,900,530),(1130,680,530) ),(86,92),20,'school')
terrace('H1_MARKET_LANDING',( (680,680,435),(1120,650,435) ),(105,98),24,'market')
terrace('H1_COMMONS_LANDING',( (1025,1170,630),(1135,665,630) ),(108,112),24,'civic_stone')
terrace('H1_RESIDENCE_LANDING',( (1170,1400,810),(1145,650,810) ),(110,98),24,'east_city')
# human-experience detail in foreground; low-cost only, not many instanced towers
massive_beam('H1_CIVIC_STREET_GATE_W',(580,530,425),(540,530,760),42,68,'market')
massive_beam('H1_CIVIC_STREET_GATE_E',(1170,515,440),(1170,535,880),65,78,'civic_stone')
massive_beam('H1_CIVIC_STREET_LINTEL',(535,530,770),(1170,530,870),55,65,'roof')

# Ensure W0 and original cameras are exactly preserved; research flags never rise.
assert all(digest(bpy.data.objects[k])==v for k,v in orig_w0.items()),'W0_CORE_MUTATED'
for k,q in orig_cams.items():
    m=bpy.data.objects[k].matrix_world
    assert max(abs(m[i][j]-q[i][j]) for i in range(4) for j in range(4))<1e-6, 'E11_CAMERA_CHANGED'
assert sc['CONSTRUCTION']=='HOLD' and sc['FORMAL_ART_ACCEPTED']==sc['COMPLETED_TARGETS']==0
sc['INT17_RESEARCH_METHOD']='CLEANED_REJECTED_STUDY_COPY_DIRECT_AUTHORED_ARCHITECTURAL_MESH'
sc['INT17_STATUS']='UNREVIEWED_NOT_ADOPTED'
sc['INT17_FUNCTION']='UNVERIFIED'
sc['INT17_MINECRAFT']='HOLD'
sc['INT17_WORLD_COORDINATES']='RESEARCH_NOT_OFFICIAL'
sc.camera=bpy.data.objects['E11_URBAN_AERIAL']

def camera_obj(name,eye,at,lens):
    dat=bpy.data.cameras.new('INT17_'+name);dat.lens=lens;dat.clip_end=14000
    ob=bpy.data.objects.new(dat.name,dat);coll.objects.link(ob);ob.location=eye
    ob.rotation_euler=(Vector(at)-Vector(eye)).to_track_quat('-Z','Y').to_euler()
    return ob
camera_obj('NEW_ARCHITECTURAL_W0_CITY_AERIAL',(2450,-3400,2000),(260,850,1200),34)
camera_obj('NEW_H1_LIVED_STREET',(820,350,465),(900,940,590),26)

blend=out/'HALO9_INT17_ARCHITECTURE_FIRST_RESEARCH.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=12
sc.cycles.use_denoising=True;sc.render.threads_mode='FIXED';sc.render.threads=2
sc.render.resolution_x=960;sc.render.resolution_y=720
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
views=fixed+('INT17_NEW_ARCHITECTURAL_W0_CITY_AERIAL','INT17_NEW_H1_LIVED_STREET')
image_sha={}
for name in views:
    sc.camera=bpy.data.objects[name]
    path=out/'renders'/(name+'.png');sc.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    assert path.stat().st_size>5500
    image_sha[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    print('INT17_REAL_ARCHITECTURAL_SCENE_RENDER',name,path.stat().st_size,flush=True)
sc.camera=bpy.data.objects['E11_URBAN_AERIAL']
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
report={'source_sha256':PARENT,'real_blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),
 'method':'DIRECT_AUTHOR_CODE_NAMED_ARCHITECTURAL_MESH_NOT_GUI_SCULPT',
 'study_rejected_meshes_removed_in_COPY':len(deleted),
 'study_rejected_meshes_names':deleted,
 'new_native_3d_components':made,'original_E11_poses':{k:[[float(v) for v in row] for row in q] for k,q in orig_cams.items()},
 'W0_protected_core_vertex_sha256':orig_w0,'render_sha256':image_sha,
 'image_classification':'ACTUAL_FULL_RESEARCH_COPY_NO_RENDER_TIME_CUTAWAY',
 'formal_adoption':0,'completed_city_master_targets':0,'minecraft':'HOLD',
 'walkability':'UNVERIFIED','art':'UNREVIEWED_NOT_ADOPTED',
 'world_coordinate_registration':'UNVERIFIED'}
(out/'INT17_NATIVE_EVIDENCE_NOT_ART.json').write_text(json.dumps(report,indent=2))
print('INT17_TRUE_EDITABLE_ARCHITECTURAL_SCENE_COMPLETE_PENDING_ART',report['real_blend_sha256'],flush=True)
