"""HALO9 INT4 — spatially authored civic sculpture, actual Blender research.

Research-only: discard all rejected INT1 architecture in a verified duplicate;
retain only reference terrain, sky, lighting and *unchanged* E11 comparison
cameras. Not a revival of INT2/INT3 giant monolithic shells, false
GUI-sculpt claim, official coordinates, art adoption or Minecraft construction.

One authored, non-repeating 3D study: NAVE library/station/ceremony,
H1 interwoven school/market/inhabited quarters, asymmetric elevated twin
civic districts and a diagonal open rupture integrated into the W0 shore.
No hollow decorative giant cylinders, algorithmic windows, or Boolean punches.
"""
import bpy,math,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[args.index('--output')+1]);out.mkdir(parents=True,exist_ok=True)
rd=out/'renders';rd.mkdir(exist_ok=True)
parent=Path(bpy.data.filepath)
SOURCE='422a60469123500e7eb4f5be886ed390665c9daadad3ad8c5e8a3b9699443100'
assert parent.name=='INT4_SOURCE.blend' and hashlib.sha256(parent.read_bytes()).hexdigest()==SOURCE
sc=bpy.context.scene
assert sc['FORMAL_ART_ACCEPTED']==sc['COMPLETED_TARGETS']==0 and sc['CONSTRUCTION']=='HOLD'
cameras=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
poses={n:bpy.data.objects[n].matrix_world.copy() for n in cameras}
original_terrain={'W0_NORTH_FRACTURED_RANGE','W0_WEST_BASALT_ESCARPMENT',
                  'W0_GROUND_BASIN','W0_EASTERN_ARTIFICIAL_SEA'}
deleted=0
for ob in list(sc.objects):
    if ob.type in ('MESH','CURVE') and ob.name not in original_terrain:
        bpy.data.objects.remove(ob,do_unlink=True);deleted+=1
assert deleted==6439,deleted
col=bpy.data.collections.new('INT4_ART_DIRECTED_SPATIAL_OCCUPANCY')
sc.collection.children.link(col)
M={}
for key,rgb,metal,rough in (
 ('pearl',(.72,.74,.69),.20,.62),
 ('civic_gold',(.77,.64,.43),.30,.52),
 ('basalt',(.12,.22,.25),.28,.69),
 ('ivory',(.84,.82,.73),.08,.72),
 ('terracotta',(.55,.36,.27),.21,.62),
 ('cyan_glass',(.08,.39,.45),.32,.22),
 ('shade',(.10,.18,.23),.10,.83),
 ('garden',(.20,.36,.25),.0,.83),
 ('light',(.94,.79,.46),.06,.41)):
    mat=bpy.data.materials.new('INT4_'+key);mat.use_nodes=True
    mat.diffuse_color=(*rgb,1)
    bs=mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*rgb,1)
    bs.inputs['Metallic'].default_value=metal
    bs.inputs['Roughness'].default_value=rough
    if key=='light':
        bs.inputs['Emission Color'].default_value=(*rgb,1)
        bs.inputs['Emission Strength'].default_value=.5
    M[key]=mat
counters={}
def obj(name,vs,fs,material):
    mesh=bpy.data.meshes.new('INT4_'+name)
    mesh.from_pydata(vs,[],fs);mesh.update()
    o=bpy.data.objects.new('INT4_'+name,mesh)
    col.objects.link(o);o.data.materials.append(M[material])
    role=name.split('_')[0];counters[role]=counters.get(role,0)+1
    return o

def solid(name,poly,z0,z1,material):
    assert len(poly)>=3 and z1>z0
    n=len(poly)
    vs=[(x,y,z0) for x,y in poly]+[(x,y,z1) for x,y in poly]
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    fs.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    return obj(name,vs,fs,material)

def stratum(name,low,high,material):
    """Eight/six-sided manually placed perimeter profiles: a real sloped
    occupied tectonic mass, deliberately open to civic void between bodies."""
    assert len(low)==len(high) and len(low)>=5
    n=len(low);vs=low+high
    fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]
    fs.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    return obj(name,vs,fs,material)

def road(name,points,width,depth,material):
    assert len(points)>=2
    verts=[]
    for i,(x,y,z) in enumerate(points):
        d=Vector(points[min(len(points)-1,i+1)])-Vector(points[max(i-1,0)])
        L=math.hypot(d.x,d.y)
        nx,ny=(-d.y/L,d.x/L) if L>1e-6 else (1,0)
        verts.extend(((x+nx*width/2,y+ny*width/2,z-depth),
                      (x-nx*width/2,y-ny*width/2,z-depth),
                      (x+nx*width/2,y+ny*width/2,z),
                      (x-nx*width/2,y-ny*width/2,z)))
    faces=[(0,2,3,1),tuple(range(len(verts)-4,len(verts)))]
    for i in range(len(points)-1):
        a=i*4;b=a+4
        faces.extend(((a,a+1,b+1,b),(a+2,b+2,b+3,a+3),
                      (a,a+2,b+2,b),(a+1,b+1,b+3,a+3)))
    return obj(name,verts,faces,material)

def framed_hall(name,poly,z,height,material,entrance_edge=0):
    """Genuine open-fronted six/irregular-sided civic room, not a painted box.
    One inward-facing wall intentionally absent; roof covers only two pockets
    so the interior and public corridor remain observable from outside.
    """
    assert len(poly)>=5
    solid(name+'_floor',poly,z-8,z,'ivory')
    for i,(a,b) in enumerate(zip(poly,poly[1:]+poly[:1])):
        if i==entrance_edge:continue
        va,vb=Vector(a),Vector(b);delta=vb-va
        normal=Vector((-delta.y,delta.x))
        normal.normalize()
        p=[tuple(va),tuple(vb),tuple(vb+normal*8),tuple(va+normal*8)]
        solid(name+'_wall_'+str(i),p,z,z+height,material)
    roof=[(x*.53+poly[0][0]*.47,y*.53+poly[0][1]*.47) for x,y in poly]
    solid(name+'_upper_skyshade_core',roof,z+height+5,z+height+12,'pearl')

def light(name,point,energy=950000):
    data=bpy.data.lights.new('INT4_'+name,'AREA');data.energy=energy;data.shape='DISK';data.size=70
    o=bpy.data.objects.new(data.name,data);col.objects.link(o);o.location=point
    # Face downward; large halls remain visible even if sky is partly enclosed.
    o.rotation_euler=(0,0,0)

# Spatial architecture begins at W0 and the inside of the NAVE, not from a
# fashionable external silhouette. No solid above human camera sightline.
solid('W0_EMBEDDED_CIVIC_DELTA',[
 (-576,-678),(-389,-809),(-153,-854),(138,-775),
 (395,-644),(526,-472),(385,-432),(71,-545),(-229,-518)],-44,36,'basalt')
solid('W0_TIDAL_READING_CONCOURSE',[
 (-385,-623),(-194,-696),(2,-707),(184,-638),
 (270,-557),(73,-501),(-165,-480)],42,62,'ivory')
solid('W0_FERRY_CIVIC_FORECOURT',[
 (253,-670),(431,-599),(513,-483),(446,-341),
 (342,-369),(261,-486)],53,74,'civic_gold')
framed_hall('W0_TIDAL_LIBRARY',[
 (-298,-574),(-193,-636),(-94,-609),(-49,-510),
 (-165,-473),(-265,-504)],66,84,'terracotta',2)
framed_hall('W0_FERRY_PUBLIC_HALL',[
 (307,-538),(419,-578),(500,-486),(483,-381),
 (391,-378),(294,-437)],79,102,'basalt',3)
road('W0_COASTAL_OPEN_STREET',[(-316,-692,65),(-118,-676,66),
 (83,-621,72),(292,-527,82),(427,-451,90)],37,15,'ivory')
road('W0_PORT_NAVE_WALK',[(165,-607,73),(125,-503,76),
 (41,-399,81),(0,-291,89)],30,9,'light')

# NAVE: three *different*, visibly functional civic interiors across a single
# massive split public campus (library on west, station on east, ritual to north).
solid('NAVE_PLAZA_CIVIC_RIFT',[
 (-187,-454),(-37,-495),(174,-441),(238,-273),
 (172,-37),(27,148),(-131,78),(-207,-119)],59,70,'ivory')
framed_hall('NAVE_WEST_CIVIC_LIBRARY',[
 (-452,-336),(-341,-414),(-240,-358),(-207,-241),
 (-269,-144),(-401,-132)],86,118,'basalt',3)
solid('NAVE_LIBRARY_OPEN_READING_TERRACE',[
 (-414,-208),(-322,-248),(-232,-177),
 (-249,-18),(-368,35)],205,221,'civic_gold')
for i,(x,y) in enumerate([
 (-383,-298),(-353,-255),(-320,-323),(-295,-268),(-269,-222)]):
    solid('NAVE_ARCHIVE_ACTUAL_BOOKSHELF_'+str(i),[
      (x-6,y-17),(x+8,y-15),(x+9,y+17),(x-6,y+20)],96,140+(i%2)*8,'terracotta')
framed_hall('NAVE_EAST_STATION',[
 (251,-423),(372,-421),(459,-330),(468,-155),
 (354,-105),(242,-180)],91,112,'basalt',4)
road('NAVE_STATION_PUBLIC_PLATFORM',[
 (265,-423,79),(289,-291,88),(334,-163,101),
 (389,-55,119)],48,14,'civic_gold')
for i,x in enumerate((294,320)):
    road('NAVE_STATION_TRACK_'+str(i),[
 (x,-460,76),(x+7,-331,82),(x+16,-169,93)],4,2,'shade')
framed_hall('NAVE_NORTH_CEREMONY_AND_GATHERING',[
 (-133,125),(18,114),(164,193),(123,320),
 (-24,367),(-162,262)],149,136,'pearl',0)
for i in range(6):
    y=198+i*18
    solid('NAVE_CEREMONY_AUDIENCE_'+str(i),[
      (-101+i*5,y),(102-i*5,y-4),(106-i*5,y+9),(-107+i*5,y+11)
    ],158+i*4,165+i*4,'ivory')
road('NAVE_PUBLIC_CIVIC_CROSS',[
 (-11,-399,72),(8,-282,74),(32,-101,88),
 (36,60,119),(15,179,158)],35,11,'ivory')
road('NAVE_LIBRARY_PUBLIC_ACCESS',[
 (-11,-309,73),(-132,-292,85),(-247,-267,91),
 (-324,-244,96)],24,8,'light')
road('NAVE_STATION_PUBLIC_ACCESS',[
 (51,-320,73),(159,-285,83),(260,-251,93)],25,8,'ivory')

# M247-C's α "double suspended" is represented by *inhabited folded urban
# tectonic terraces*, never an uninhabited giant solid wedge or cylinder.
# Each settlement is uniquely proportioned and visibly shares the chasm.
def terrace_group(name,profiles,floors,materials):
    assert len(profiles)==len(floors)
    # each profile is a different 8-point researched sculptural outline.
    for i,(poly,z) in enumerate(zip(profiles,floors)):
        solid(name+'_urban_occupied_stratum_'+str(i),poly,z-40-i*4,z,materials[i%len(materials)])
        # Distinct actual external inhabited public rim follows the uneven
        # leading 3/4 vertices, without copying a whole fake building facade.
        pts=[(x,y,z+5) for x,y in poly[:4]]
        road(name+'_external_civic_street_'+str(i),pts,18+i*5,6,'civic_gold')
    return True

terrace_group('M247_WEST_LOWER_INHABITED_LIMESTONE',[
 [(-545,-90),(-392,-111),(-267,-34),(-224,135),(-311,243),(-529,240),(-650,76)],
 [(-600,74),(-414,92),(-272,218),(-293,346),(-433,414),(-687,326),(-737,148)],
 [(-655,264),(-481,285),(-329,406),(-387,525),(-579,582),(-786,498),(-816,346)],
 [(-776,448),(-546,492),(-421,620),(-502,721),(-684,757),(-842,655),(-886,533)]
], [238,385,556,752],['basalt','pearl','terracotta'])
terrace_group('M247_EAST_CHIRAL_INHABITED_QUARTERS',[
 [(316,-37),(449,-85),(601,14),(715,167),(672,272),(461,234),(320,117)],
 [(342,119),(508,84),(716,186),(837,330),(731,419),(527,388),(372,281)],
 [(421,312),(566,285),(772,414),(928,561),(828,672),(625,618),(454,477)],
 [(497,544),(703,491),(866,601),(1043,766),(961,873),(759,798),(579,672)]
], [249,425,644,884],['pearl','basalt','civic_gold'])

# In each thick district, inner open-faced public rooms grow as *program*:
# the volumes are part of the structural strata rather than decorative boxes.
framed_hall('M247_WEST_SKY_LIBRARY',[
 (-587,290),(-494,243),(-367,290),(-342,381),
 (-491,447),(-596,397)],589,124,'basalt',2)
framed_hall('M247_EAST_TERRACE_SCHOOL',[
 (574,383),(682,341),(808,418),(817,521),
 (683,553),(562,467)],672,114,'terracotta',4)
road('M247_WEST_INTERTERRACE_PUBLIC_ASCENT',[
 (-381,-22,250),(-395,89,385),(-450,208,559),
 (-535,422,755)],27,13,'ivory')
road('M247_EAST_INTERTERRACE_PUBLIC_ASCENT',[
 (438,-45,252),(551,121,426),(659,318,648),
 (776,621,889)],28,15,'ivory')

# H1 living city: actual public programmes and multilevel inhabited streets
# centered beyond protected camera location (760,270,439), with a clear
# unobstructed northward corridor between different urban masses.
solid('H1_URBAN_MAIN_PEDESTRIAN_CROSSING',[
 (746,286),(799,277),(828,589),(805,777),
 (760,786),(728,543)],432,446,'ivory')
road('H1_PUBLIC_BOULEVARD',[
 (756,283,446),(760,383,453),(774,504,471),
 (793,640,507),(808,758,561)],36,10,'ivory')
framed_hall('H1_MARKET_CIVIC_COURT',[
 (487,355),(587,319),(709,379),(716,489),
 (584,544),(468,474)],455,106,'terracotta',2)
framed_hall('H1_SCHOOL_AND_ASSEMBLY',[
 (869,366),(1011,336),(1138,442),(1090,578),
 (944,596),(864,508)],480,139,'basalt',5)
framed_hall('H1_READERS_PUBLIC_LIBRARY',[
 (480,573),(597,546),(726,615),(689,741),
 (551,769),(465,698)],530,109,'pearl',2)
framed_hall('H1_OCCUPIED_HOUSING_COURT',[
 (883,628),(1024,621),(1139,712),(1071,817),
 (949,828),(856,746)],569,113,'basalt',4)
road('H1_MARKET_NAVE_CONNECTOR',[(745,390,456),
 (668,417,458),(570,450,463)],28,8,'civic_gold')
road('H1_SCHOOL_PEDESTRIAN_LINK',[(797,489,476),
 (907,487,485),(994,481,493)],29,8,'light')
road('H1_UPPER_INHABITED_CITY_ROUTE',[(788,638,508),
 (697,668,554),(592,702,631),(523,725,760)],27,12,'civic_gold')
solid('H1_OPEN_COURTYARD_GARDEN',[
 (699,538),(730,511),(751,562),(717,603),
 (685,583)],462,466,'garden')
solid('H1_HIGH_GARDEN',[
 (829,713),(886,687),(919,733),
 (882,783),(831,758)],583,589,'garden')

# β oblique city-scale *open fault* is built through the deliberate absence of
# mass, with a single lived-in transfer above and several accessible lower
# connections. The displaced high-altitude quarter is a thick real inhabited
# district, but not an opaque megablock.
terrace_group('M247_BETA_DISPLACED_SUSPENDED_CITY',[
 [(532,806),(706,774),(853,841),(928,991),
  (792,1065),(601,1017),(487,894)],
 [(492,963),(707,943),(910,1016),(1013,1133),
  (877,1218),(659,1165),(508,1081)],
 [(433,1137),(646,1127),(900,1229),(1056,1364),
  (896,1451),(643,1412),(447,1283)]
], [1058,1269,1483], ['basalt','pearl','terracotta'])
framed_hall('M247_HIGH_CIVIC_OBSERVATORY',[
 (595,1082),(703,1051),(865,1114),
 (888,1241),(736,1290),(614,1219)],1293,133,'basalt',1)
road('M247_BETA_ACTUAL_PUBLIC_INHABITED_TRANSFER',[
 (-560,578,766),(-271,659,833),(65,746,916),
 (392,838,1030),(699,930,1155)],43,27,'civic_gold')
road('M247_HIGH_PUBLIC_INTRA_CITY',[
 (637,954,1118),(709,1028,1218),
 (782,1117,1328),(800,1201,1494)],29,10,'ivory')
# One oblique arching open-air transit bridge from NAVE to upper H1.
road('M247_NAVE_H1_GRADIENT_PUBLIC_SPINE',[
 (109,163,180),(253,285,290),(404,394,393),
 (591,518,476),(720,670,590)],34,18,'civic_gold')
road('W0_NAVE_H1_LIVING_TRANSIT',[
 (360,-485,91),(493,-292,182),(591,-105,287),
 (691,112,391),(758,279,445)],27,11,'ivory')

# Carefully staged interior lighting, not a substitute for architecture.
for i,point in enumerate([
 (-280,-218,175),(361,-189,177),(6,179,241),
 (556,426,534),(1003,483,581),(561,681,596),
 (1042,729,639),(721,1172,1380)]):
    light('ACTUAL_CIVIC_'+str(i),point,600000)
bpy.context.view_layer.update()
for name,m in poses.items():
    now=bpy.data.objects[name].matrix_world
    assert max(abs(now[i][j]-m[i][j]) for i in range(4) for j in range(4))<1e-6
sc['INT4_SOURCE_SHA256']=SOURCE
sc['INT4_METHOD']='EXPLICIT_EDITABLE_PROGRAM_COHERENT_SCULPTURAL_FACETS_NO_BOOLEAN'
sc['INT4_RESEARCH_UNITS']='UNREGISTERED_METRES'
sc['INT4_REMOVED_REJECTED_INT1']=deleted
sc['CONSTRUCTION']='HOLD';sc['FORMAL_ART_ACCEPTED']=0;sc['COMPLETED_TARGETS']=0
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=20
sc.cycles.use_denoising=True;sc.render.threads_mode='FIXED';sc.render.threads=2
sc.render.resolution_x=1100;sc.render.resolution_y=825
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
sc.camera=bpy.data.objects[cameras[-1]]
dst=out/'HALO9_INT4_CIVIC_SCULPTURE.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=True)
render_hashes={}
for n in cameras:
    sc.camera=bpy.data.objects[n]
    f=rd/(n+'.png')
    sc.render.filepath=str(f);bpy.ops.render.render(write_still=True)
    assert f.stat().st_size>5000
    render_hashes[n]=hashlib.sha256(f.read_bytes()).hexdigest()
    print('INT4_REAL_RENDER',n, f.stat().st_size, flush=True)
sc.camera=bpy.data.objects[cameras[-1]]
bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=True)
report={
 'schema':'halo9-int4-explicit-sculptural-civic-city-v1',
 'source_sha256':SOURCE,
 'blend_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),
 'removed_rejected_architecture':deleted,
 'new_geometry_by_role':counters,
 'source_blend_real':True,'unchanged_cameras':True,
 'render_sha256':render_hashes,
 'function':'UNKNOWN_NOT_INDEPENDENTLY_PROVEN',
 'coordinates':'UNREGISTERED_RESEARCH_METRES',
 'formal_art_adopted':0,'completed_targets':0,
 'minecraft_construction':'HOLD','art':'AWAITING_DIRECT_IMAGE_REVIEW'}
(out/'INT4_NATIVE_TECH.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('INT4_NATIVE_COMPLETE',report['blend_sha256'],flush=True)
