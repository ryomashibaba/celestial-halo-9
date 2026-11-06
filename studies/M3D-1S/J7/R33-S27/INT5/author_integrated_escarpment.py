"""CELESTIAL HALO-9 / INT5 — inhabited escarpment surgical study.

Edit the *existing real* INT4-R1 BLEND in isolation. INT4's rejected detached
thin residential strata are removed only from the study copy, then replaced
with two connected, spatially inhabited, independently sculpted city masses.
No rings of generic buildings, cylindrical shells, cosmetic openings or
uninhabited slab towers. Main CIVIC library/station/ceremony/H1/W0 source
remains editable and the 3 original camera matrices remain unchanged.

This is native Blender Python mesh sculpting, NOT verified GUI hand-sculpting.
Formal ART acceptance, completed target count and construction remain zero.
"""
import bpy, math, json, sys, hashlib
from mathutils import Vector
from pathlib import Path

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[args.index('--output')+1]);out.mkdir(parents=True,exist_ok=True)
(out/'renders').mkdir(exist_ok=True)
parent=Path(bpy.data.filepath)
PARENT_SHA='7cf765923b91f06cce7951fc3558f042e488bf9f1157791b59b14d11954dc2bb'
assert parent.name=='INT5_SOURCE.blend' and hashlib.sha256(parent.read_bytes()).hexdigest()==PARENT_SHA
sc=bpy.context.scene
assert sc['CONSTRUCTION']=='HOLD' and sc['COMPLETED_TARGETS']==0 and sc['FORMAL_ART_ACCEPTED']==0
CAMERAS=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
fixed={n:bpy.data.objects[n].matrix_world.copy() for n in CAMERAS}
removed=[]
for o in list(sc.objects):
    if o.name.startswith('INT4_M247_') and (
        '_urban_occupied_stratum_' in o.name or '_external_civic_street_' in o.name):
        removed.append(o.name)
        bpy.data.objects.remove(o,do_unlink=True)
assert len(removed)==22, ('unexpected stratum replacement scope',removed)

c=bpy.data.collections.new('INT5_DIRECT_INHABITED_ESCARPMENT_RESEARCH')
sc.collection.children.link(c)
mats={}
for name,color,metal,rough in (
    ('deep_stone',(.13,.21,.25),.18,.68),
    ('calcite',(.70,.68,.60),.22,.61),
    ('warm_sandstone',(.58,.47,.34),.20,.66),
    ('oxidized_bronze',(.43,.30,.22),.69,.38),
    ('ceramic_pearl',(.79,.78,.70),.16,.54),
    ('teal_glass',(.08,.29,.35),.35,.19),
    ('verdigris',(.25,.43,.37),.15,.66),
    ('civic_light',(.93,.76,.42),.08,.43)):
    m=bpy.data.materials.new('INT5_'+name);m.use_nodes=True;m.diffuse_color=(*color,1)
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metal
    bs.inputs['Roughness'].default_value=rough
    if name=='civic_light':
        bs.inputs['Emission Color'].default_value=(*color,1)
        bs.inputs['Emission Strength'].default_value=.8
    mats[name]=m
counts={}
def mesh(name,vs,fs,mat):
    md=bpy.data.meshes.new('INT5_'+name);md.from_pydata(vs,[],fs);md.update()
    ob=bpy.data.objects.new('INT5_'+name,md);c.objects.link(ob)
    ob.data.materials.append(mats[mat])
    k=name.split('_')[0];counts[k]=counts.get(k,0)+1
    return ob
def prism(name,poly,lo,hi,mat):
    assert hi>lo and len(poly)>=3
    n=len(poly)
    vs=[(x,y,lo) for x,y in poly]+[(x,y,hi) for x,y in poly]
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    fs.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    return mesh(name,vs,fs,mat)
def street(name,points,width,depth,mat):
    vs=[]
    for i,(x,y,z) in enumerate(points):
        diff=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)])
        L=math.hypot(diff.x,diff.y)
        nx,ny=(-diff.y/L,diff.x/L) if L>1e-5 else (1,0)
        vs.extend(((x+nx*width/2,y+ny*width/2,z-depth),
                   (x-nx*width/2,y-ny*width/2,z-depth),
                   (x+nx*width/2,y+ny*width/2,z),
                   (x-nx*width/2,y-ny*width/2,z)))
    fs=[(0,2,3,1),tuple(range(len(vs)-4,len(vs)))]
    for i in range(len(points)-1):
        a=i*4;b=a+4
        fs.extend(((a,a+1,b+1,b),(a+2,b+2,b+3,a+3),
                   (a,a+2,b+2,b),(a+1,b+1,b+3,a+3)))
    return mesh(name,vs,fs,mat)

# A true thick, multiple-profile tectonic civic body with an asymmetric skyline.
# Each section records a different *inhabitable* cross-section (y, inner x,
# outer x, actual low level, inhabited terrace level, high crown elevation).
# Both masses are more than 300m wide and have deep urban caverns. They form
# one continuous diagonal negative space from NAVE to the H1/W0 landscape.
west=[
 (-510,-271,-748, 42,252,420),
 (-321,-306,-837, 76,308,570),
 (-100,-319,-908,108,388,710),
 (143,-355,-984,180,510,937),
 (392,-467,-1026,272,672,1135),
 (652,-518,-1145,427,832,1296),
 (917,-590,-1258,620,1068,1553),
 (1158,-663,-1223,789,1156,1671),
 (1398,-729,-1015,953,1265,1449)]
east=[
 (-510,282,805,43,266,451),
 (-319,328,917,80,318,587),
 (-83,382,1062,126,436,797),
 (180,458,1168,213,580,1039),
 (420,580,1306,292,727,1197),
 (664,719,1455,435,889,1398),
 (921,825,1549,625,1046,1548),
 (1171,964,1657,842,1260,1782),
 (1415,1032,1518,981,1368,1607)]
def sculpt_tectonic_mass(name,table,side,mat):
    # Not an extruded slab: every cross section has a seven-vertex angular,
    # strongly unequal profile representing inner public street, multi-story
    # inhabited body, broken roofline, distant outer support and deep mass.
    rings=[]
    for i,(y,inner,outer,zlow,terrace,crest) in enumerate(table):
        offset=side
        mid=inner+side*abs(outer-inner)*.42
        outer2=inner+side*abs(outer-inner)*.82
        vals=[
            (inner, y, zlow),
            (inner-side*31,y,terrace*.61+zlow*.39),
            (inner+side*12,y,terrace+36+19*math.sin(i)),
            (mid,y,crest-91-26*math.cos(i*.7)),
            (outer2,y,crest+33*math.sin(i*.91)),
            (outer,y,terrace*.83+zlow*.17),
            (outer-side*24,y,zlow-42)
        ]
        rings.append(vals)
    n=len(rings[0]);v=[xyz for ring in rings for xyz in ring]
    fs=[tuple(reversed(range(n))),
        tuple(range(n*(len(rings)-1),n*len(rings)))]
    for j in range(len(rings)-1):
        for k in range(n):
            a=j*n+k;b=j*n+(k+1)%n
            fs.append((a,b,b+n,a+n))
    return mesh(name,v,fs,mat)

W=sculpt_tectonic_mass('M247_WEST_CONNECTED_INHABITED_ESCARPMENT',west,-1,'calcite')
E=sculpt_tectonic_mass('M247_EAST_CONNECTED_INHABITED_ESCARPMENT',east,1,'warm_sandstone')
# City atrium apertures are deep, tapered, irregular seven-sided cut-out rooms,
# not replicated circular portholes or color changes to solid facade.
def cavity(name,body,side,y,z,front,depth,wy,hz):
    region=[(-1.04,-.62),(-.79,.31),(-.31,.87),(.32,1),
            (.94,.44),(1.03,-.46),(.19,-.97),(-.61,-.90)]
    yz=[(y+a*wy,z+b*hz) for a,b in region]
    xnear=front-side*103;xdeep=front+side*depth
    xlo,xhi=sorted((xnear,xdeep))
    n=len(yz)
    vs=[(xlo,yy,zz) for yy,zz in yz]+[(xhi,yy,zz) for yy,zz in yz]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    md=bpy.data.meshes.new('INT5_TEMP_CUT_'+name);md.from_pydata(vs,[],faces);md.update()
    cut=bpy.data.objects.new('INT5_TEMP_CUT_'+name,md);sc.collection.objects.link(cut)
    before=len(body.data.polygons)
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True);bpy.context.view_layer.objects.active=body
    mod=body.modifiers.new('INT5_CITY_ATRIUM_'+name,'BOOLEAN')
    mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cut,do_unlink=True)
    return (before,len(body.data.polygons))

districts=[
 # side, unique purpose, y,z, front inner-side coordinate, depth, halfY, halfZ
 ('W','NAVE_PUBLIC_LIBRARY',-165,355,-325,342,126,120),
 ('E','NAVE_STATION_TRAIN_HALL',-157,356,391,366,130,116),
 ('W','ELEVATED_LIBRARY_MUSEUM',172,666,-374,345,140,136),
 ('E','NAVE_CEREMONY_PUBLIC_SQUARE',200,673,469,381,128,129),
 ('W','H1_CLIFF_MARKET',431,812,-485,350,140,135),
 ('E','H1_SCHOOL_CAMPUS',496,835,614,390,149,124),
 ('W','H1_PUBLIC_HOUSING_ATRIUM',743,1049,-545,370,136,143),
 ('E','H1_INHABITED_COMMUNITY',779,1155,763,389,142,137),
 ('W','HIGH_READING_GARDEN',1085,1274,-650,328,122,130),
 ('E','HIGH_SKY_RAIL_EXCHANGE',1136,1432,920,383,144,141)
]
cut_results={}
for side,label,y,z,front,depth,wy,hz in districts:
    body=W if side=='W' else E
    sign=-1 if side=='W' else 1
    cut_results[label]=cavity(label,body,sign,y,z,front,depth,wy,hz)
    # A physically occupied double-deck city is *inside* the carved chamber,
    # with exposed transparent galleries instead of a window decal.
    x=front+sign*(depth*.43)
    poly=[
      (x-61,y-wy*.68),(x+18,y-wy*.81),(x+112,y-wy*.39),
      (x+129,y+wy*.43),(x+13,y+wy*.82),(x-87,y+wy*.31)
    ]
    prism('CITY_'+label+'_PUBLIC_INTERIOR_LEVEL',poly,z-hz*.66-10,z-hz*.66,'ceramic_pearl')
    prism('CITY_'+label+'_MEZZANINE',[
       (px*.73+x*.27,py*.73+y*.27) for px,py in poly
    ],z+hz*.12-11,z+hz*.12,'oxidized_bronze')
    # Deep study room/school/market/water side enclosure within excavation.
    p=[(x-43,y-56),(x+53,y-48),(x+69,y+38),
       (x+22,y+59),(x-51,y+32)]
    prism('CITY_'+label+'_INNER_OCCUPIED_WING',p,z-hz*.54,z+hz*.05,'deep_stone')
    # Halls have a real daylight mouth and an elevated public approach,
    # rather than pretending the entire deep cavity is traversable.
    street('CITY_'+label+'_EXPOSED_LIVING_ROUTE',[
       (front-sign*58,y-wy*.49,z-hz*.62+4),
       (front+sign*32,y-wy*.14,z-hz*.49+6),
       (x,y+wy*.21,z-hz*.38+5)
    ],24,7,'civic_light')

# The β oblique crown is a displaced *inhabited* transit district with deep,
# non-symmetric single-volume roof, not a free-floating thin standard platform.
beta_sections=[
 [(-581,734,1014),(-482,696,1012),(-364,704,1057),
  (-321,759,1106),(-434,794,1100),(-553,785,1050)],
 [(-379,876,1140),(-239,841,1170),(-86,858,1234),
  (-91,958,1257),(-250,991,1196),(-389,968,1154)],
 [(-28,1022,1253),(138,982,1295),(283,1036,1353),
  (249,1149,1349),(86,1166,1284),(-46,1111,1261)],
 [(343,1155,1445),(502,1125,1488),(659,1157,1569),
  (642,1245,1538),(476,1306,1504),(331,1260,1459)]
]
def loft_civic_bridge(name,rings,mat):
    n=len(rings[0])
    vs=[v for a in rings for v in a]
    fs=[tuple(reversed(range(n))),tuple(range((len(rings)-1)*n,len(rings)*n))]
    for j in range(len(rings)-1):
        for k in range(n):
            a=j*n+k;b=j*n+(k+1)%n
            fs.append((a,b,b+n,a+n))
    return mesh(name,vs,fs,mat)
beta=loft_civic_bridge('M247_BETA_INHABITED_DISPLACED_SKY_CIVIC_CITY',
                       beta_sections,'deep_stone')
# Large diagonal arch gate, carved to open a real high-altitude room.
cut_results['BETA_HIGH_PUBLIC_VOID']=cavity(
    'BETA_HIGH_PUBLIC_VOID',beta,1,1001,1328,44,475,128,89)
street('M247_BETA_SUSPENDED_INHABITED_STREET',[
 (-430,748,1061),(-248,895,1188),
 (50,1037,1324),(351,1199,1513)],36,13,'ceramic_pearl')

# A visibly occupied continuous shift links shore and H1 to both great cores:
# distinguish travel, library, marketplace and public assembly in the art.
street('M247_W0_TO_WEST_CIVIC_ROOT',[
 (-280,-623,72),(-380,-431,135),(-430,-251,247),
 (-445,-151,322)],35,16,'oxidized_bronze')
street('M247_W0_TO_EAST_TRANSPORT_ROOT',[
 (350,-567,91),(473,-408,161),(497,-225,285),
 (523,-141,338)],40,18,'oxidized_bronze')
street('M247_NAVE_TO_H1_MULTILEVEL_SPINE',[
 (179,150,199),(305,280,298),(465,373,423),
 (592,523,533),(777,706,619)],35,14,'ceramic_pearl')
street('M247_WEST_CIVIC_SKY_ACCESS',[
 (-375,151,655),(-451,427,802),(-560,741,1052),
 (-651,1083,1279)],27,10,'ceramic_pearl')
street('M247_EAST_CIVIC_SKY_ACCESS',[
 (447,176,663),(609,484,818),(783,774,1149),
 (925,1121,1425)],29,12,'ceramic_pearl')

# A second interleaved hierarchy of functional carved wings prevents an
# enormous blank wall from standing alone, but remains nonrepeating and
# connected to the irregular shared escarpment.
for i,(x,y,z,rx,ry) in enumerate([
 (-804,310,566,165,134),(-927,622,869,171,149),
 (-1118,903,1170,199,148),(885,377,690,176,152),
 (1091,660,990,173,162),(1300,1024,1342,188,171)
]):
    footprint=[
      (x-rx*.83,y-ry*.58),(x-rx*.49,y-ry*.96),
      (x+rx*.29,y-ry*.78),(x+rx*.9,y-ry*.13),
      (x+rx*.68,y+ry*.69),(x-rx*.24,y+ry*.92),
      (x-rx*.89,y+ry*.33)]
    prism('CITY_DIVERGENT_LIVED_COURT_'+str(i),
           footprint,z-72,z+19,'warm_sandstone' if i%2 else 'calcite')
    garden=[(x-35,y-41),(x+43,y-31),(x+49,y+27),(x-32,y+49)]
    prism('CITY_DIVERGENT_PUBLIC_GARDEN_'+str(i),garden,z+19,z+24,'verdigris')

# Neither fake white-out nor moved cameras are allowed. Show the actual three.
bpy.context.view_layer.update()
for name,m in fixed.items():
    now=bpy.data.objects[name].matrix_world
    assert max(abs(now[i][j]-m[i][j]) for i in range(4) for j in range(4))<1e-6
sc['INT5_PARENT_SHA256']=PARENT_SHA
sc['INT5_REPLACED_INT4_THIN_STRATA']=len(removed)
sc['INT5_METHOD']='SAME_NATIVE_EDITED_CITY_TWO_INHABITED_ROCKS_OPEN_FAULT'
sc['INT5_COORDS']='RESEARCH_METRES_UNREGISTERED'
sc['FORMAL_ART_ACCEPTED']=0;sc['COMPLETED_TARGETS']=0;sc['CONSTRUCTION']='HOLD'
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=16
sc.cycles.use_denoising=True;sc.render.threads_mode='FIXED';sc.render.threads=2
sc.render.resolution_x=1100;sc.render.resolution_y=825
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
sc.camera=bpy.data.objects[CAMERAS[-1]]
blend=out/'HALO9_INT5_INHABITED_RUPTURE_SCULPT.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
hashes={}
for n in CAMERAS:
    sc.camera=bpy.data.objects[n];p=out/'renders'/(n+'.png')
    sc.render.filepath=str(p);bpy.ops.render.render(write_still=True)
    assert p.exists() and p.stat().st_size>5000
    hashes[n]=hashlib.sha256(p.read_bytes()).hexdigest()
    print('INT5_TRUE_FIXED_CAM_RENDER',n,p.stat().st_size,flush=True)
sc.camera=bpy.data.objects[CAMERAS[-1]]
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
report={'schema':'halo9-int5-actual-escarpment-sculpt-v1',
 'source_sha256':PARENT_SHA,
 'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),
 'replaced_thin_architecture':len(removed),
 'created_meshes_by_role':counts,
 'real_boolean_cavities':cut_results,
 'render_sha256':hashes,
 'unchanged_original_cameras':True,
 'coordinates':'UNREGISTERED_RESEARCH_METRES',
 'function':'UNKNOWN_NO_COMPLETE_PEDESTRIAN_QA',
 'formal_art_adopted':0,'completed_targets':0,
 'minecraft':'HOLD','art':'UNREVIEWED_NO_ART_ADOPTION'}
(out/'INT5_NATIVE_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('INT5_TRUE_NATIVE_COMPLETE',report['blend_sha256'],flush=True)
