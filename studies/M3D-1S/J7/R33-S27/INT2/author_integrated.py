"""HALO-9 INT2: inhabited tectonic fault, one isolated macro/civic research candidate.
Source is the rejected INT1 BLEND, but *all its architecture* is discarded.
The camera/light/known W0 context survive solely as comparison context.
Research units are unregistered metres. Nothing is adopted or built in Minecraft.
"""
import bpy, math, json, hashlib, sys
from pathlib import Path
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
out = Path(args[args.index('--output') + 1]); out.mkdir(parents=True, exist_ok=True)
renders = out / 'renders'; renders.mkdir(exist_ok=True)
source = Path(bpy.data.filepath)
EXPECTED = '422a60469123500e7eb4f5be886ed390665c9daadad3ad8c5e8a3b9699443100'
assert source.name == 'INT2_SOURCE.blend' and hashlib.sha256(source.read_bytes()).hexdigest() == EXPECTED
scene = bpy.context.scene
assert scene['CONSTRUCTION'] == 'HOLD' and scene['COMPLETED_TARGETS'] == 0 and scene['FORMAL_ART_ACCEPTED'] == 0
camera_names = ('E11_NAVE_HUMAN', 'E11_H1_HUMAN', 'E11_URBAN_AERIAL')
cameras = {n: bpy.data.objects[n].matrix_world.copy() for n in camera_names}
keep_terrain = {'W0_NORTH_FRACTURED_RANGE', 'W0_WEST_BASALT_ESCARPMENT',
                'W0_GROUND_BASIN', 'W0_EASTERN_ARTIFICIAL_SEA'}
removed = 0
for ob in list(scene.objects):
    if ob.type in {'MESH', 'CURVE'} and ob.name not in keep_terrain:
        bpy.data.objects.remove(ob, do_unlink=True); removed += 1
assert removed >= 6400, ('Not the expected INT1 architecture', removed)
coll = bpy.data.collections.new('INT2_INHABITED_TECTONIC_FAULT_RESEARCH')
scene.collection.children.link(coll)
palette = {}
for key, rgb, metal, rough in (
    ('shell_ochre', (.47,.45,.39),.22,.71),
    ('shell_pearl', (.68,.68,.61),.22,.53),
    ('cavity_stone', (.12,.21,.24),.11,.80),
    ('civic_ivory', (.79,.74,.62),.08,.74),
    ('oxide_copper', (.40,.29,.20),.66,.48),
    ('roof_azure', (.21,.41,.46),.46,.37),
    ('inhabited_glass', (.06,.25,.32),.32,.22),
    ('garden', (.17,.29,.23),.08,.81),
    ('sunlit_stone', (.71,.54,.32),.27,.58),
):
    m = bpy.data.materials.new('INT2_'+key); m.use_nodes = True
    m.diffuse_color = (*rgb,1)
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*rgb,1)
    bsdf.inputs['Metallic'].default_value = metal
    bsdf.inputs['Roughness'].default_value = rough
    palette[key] = m
counts = {}
def mesh(name, vertices, faces, material, smooth=False):
    assert vertices and faces
    md = bpy.data.meshes.new('INT2_'+name)
    md.from_pydata(vertices,[],faces); md.update()
    ob = bpy.data.objects.new('INT2_'+name,md)
    coll.objects.link(ob); md.materials.append(palette[material])
    if smooth:
        for p in md.polygons: p.use_smooth = True
    head = name.split('_')[0]; counts[head] = counts.get(head,0)+1
    return ob

def solid(name, polygon, z_bottom, z_top, material):
    assert len(polygon)>=3 and z_top>z_bottom
    n=len(polygon)
    vs=[(x,y,z_bottom) for x,y in polygon]+[(x,y,z_top) for x,y in polygon]
    faces=[tuple(reversed(range(n))),tuple(range(n,n*2))]
    faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    return mesh(name,vs,faces,material)

def walk(name, points, width, depth, material):
    vs=[]
    for i,p in enumerate(points):
        before=Vector(points[max(0,i-1)])
        after=Vector(points[min(len(points)-1,i+1)])
        delta=after-before; ln=math.hypot(delta.x,delta.y)
        nx,ny=((-delta.y/ln,delta.x/ln) if ln>1e-5 else (1,0))
        x,y,z=p
        vs.extend(((x+nx*width/2,y+ny*width/2,z-depth),
                   (x-nx*width/2,y-ny*width/2,z-depth),
                   (x+nx*width/2,y+ny*width/2,z),
                   (x-nx*width/2,y-ny*width/2,z)))
    fs=[(0,2,3,1),tuple(range(len(vs)-4,len(vs)))]
    for i in range(len(points)-1):
        a=i*4; b=a+4
        fs.extend(((a,a+1,b+1,b),(a+2,b+2,b+3,a+3),
                   (a,a+2,b+2,b),(a+1,b+1,b+3,a+3)))
    return mesh(name,vs,fs,material)

def core(name, levels, material, phase):
    """Volumetric, three-dimensional non-repeated local strata.
    Continuous closed geometry, not a set of thin display terraces.
    Each radius belongs to a real inhabited mass, not a painted facade.
    """
    radial=48; intervals=7; rings=[]
    for j in range(len(levels)-1):
        lo=levels[j];hi=levels[j+1]
        for k in range(intervals):
            t=k/intervals; u=t*t*(3-2*t)
            z,cx,cy,rx,ry=[a+(b-a)*u for a,b in zip(lo,hi)]
            vs=[]
            for a in range(radial):
                angle=math.tau*a/radial
                relief=1+.07*math.sin(3*angle+z/290+phase)+.035*math.sin(7*angle-z/260+phase)
                rx2=rx*relief*(1+.09*math.sin(angle*2+z/230))
                ry2=ry*relief
                vs.append((cx+rx2*math.cos(angle),cy+ry2*math.sin(angle),z))
            rings.append(vs)
    rings.append([(levels[-1][1]+levels[-1][3]*math.cos(math.tau*a/radial),
                   levels[-1][2]+levels[-1][4]*math.sin(math.tau*a/radial),
                   levels[-1][0]) for a in range(radial)])
    verts=[p for ring in rings for p in ring]
    faces=[tuple(reversed(range(radial))),tuple(range((len(rings)-1)*radial,len(rings)*radial))]
    for i in range(len(rings)-1):
        for j in range(radial):
            a=i*radial+j; b=i*radial+(j+1)%radial
            faces.append((a,b,b+radial,a+radial))
    return mesh(name,verts,faces,material,smooth=True)

def carve(target,name,position,scale):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=28,ring_count=16,location=position)
    cutter=bpy.context.object;cutter.name='INT2_TEMP_CUT_'+name;cutter.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.context.view_layer.objects.active=target
    bpy.ops.object.select_all(action='DESELECT');target.select_set(True)
    mod=target.modifiers.new(name,'BOOLEAN');mod.operation='DIFFERENCE'
    mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    assert len(target.data.polygons)>100, name
    return len(target.data.polygons)

def wall(name,a,b,z,height,thick,mat):
    a=Vector(a);b=Vector(b);d=(b-a).normalized()
    norm=Vector((-d.y,d.x,0))
    p=[(a.x,a.y),(b.x,b.y),(b.x+norm.x*thick,b.y+norm.y*thick),
       (a.x+norm.x*thick,a.y+norm.y*thick)]
    return solid(name,p,z,z+height,mat)

def room(name,xy,z,height,material,open_side=0):
    """Six-sided spatial program, open to the real civic route."""
    x,y=xy
    outline=[(x-57,y-29),(x-26,y-58),(x+38,y-43),
             (x+70,y+8),(x+24,y+48),(x-46,y+39)]
    solid(name+'_accessible_floor',outline,z-8,z,'civic_ivory')
    for i in range(6):
        if i==open_side: continue
        wall(name+'_inhabitable_enclosure_'+str(i),outline[i],
             outline[(i+1)%6],z,height,7,material)
    roof=[(x+(xx-x)*1.12,y+(yy-y)*1.12) for xx,yy in outline]
    solid(name+'_folded_roof',roof,z+height+2,z+height+11,'roof_azure')
    return outline

def mini_tree(name,x,y,z):
    walk(name+'_branch',[(x,y,z),(x+2,y,z+19),(x+9,y+1,z+29)],2,2,'oxide_copper')
    poly=[(x-13,y-5),(x-4,y-15),(x+10,y-13),(x+17,y),
          (x+6,y+14),(x-12,y+11)]
    solid(name+'_crown',poly,z+19,z+31,'garden')

# STAGE A: two physically thick and non-identical linked civic escarpments.
# The vertical scar changes gap, urban elevation and coastline in a single gesture.
west=core('M247_ALPHA_WEST_LIVED_FAULT_CORE',[
 (6,-535,-257,330,355),(170,-493,-235,350,399),
 (395,-495,-142,362,421),(610,-578,-43,354,404),
 (851,-684,115,322,360),(1074,-713,319,269,309),
 (1280,-642,450,148,183),(1355,-636,475,73,92)
],'shell_pearl',.12)
east=core('M247_ALPHA_EAST_DISPLACED_FAULT_CORE',[
 (3,589,-293,398,369),(180,527,-215,395,419),
 (421,648,-80,431,457),(646,747,106,380,432),
 (883,850,295,349,360),(1101,982,489,301,301),
 (1389,1094,694,218,245),(1500,1114,745,77,104)
],'shell_ochre',1.08)
# Each great volume is excavated into public programmes; the gap remains a
# long diagonal city-scale negative space, NOT a filled Boolean cavity.
cuts=[
 (west,'NAVE_LIBRARY',(-275,-200,205),(243,239,126)),
 (west,'NAVE_HIGH_READING_ROOM',(-232,7,398),(210,201,126)),
 (west,'WEST_ATRIUM_STACK',(-300,208,685),(249,247,155)),
 (west,'WEST_UPPER_CITY_VOID',(-476,390,965),(201,205,129)),
 (east,'NAVE_STATION',(298,-306,171),(228,225,119)),
 (east,'NAVE_CEREMONY',(316,-45,386),(228,204,157)),
 (east,'H1_MARKET_ATRIUM',(726,335,493),(249,246,131)),
 (east,'H1_SCHOOL_LIGHTWELL',(764,592,724),(224,218,128)),
 (east,'EAST_FLOATING_PUBLIC_ROOM',(1007,654,1123),(187,184,125))
]
boolean_counts={key:carve(ob,key,pos,scale) for ob,key,pos,scale in cuts}

# STAGE B: the actual interior is the geometric reason for the excavation.
# Three different destinations share a continuous open NAVE, not a roofless
# labeled platform or ordinary box row.
solid('NAVE_MAIN_FORUM',[
 (-228,-513),(29,-542),(221,-420),(257,-211),(194,31),(26,170),
 (-127,140),(-249,-91)],58,83,'civic_ivory')
solid('NAVE_LIBRARY_INTERIOR',[
 (-456,-311),(-290,-414),(-181,-328),(-185,-105),(-290,-20),
 (-451,-74)],113,123,'civic_ivory')
solid('NAVE_LIBRARY_READING_GALLERY',[
 (-454,-112),(-301,-170),(-170,-65),(-234,66),(-401,87)],245,254,'sunlit_stone')
# Shelves are functional-scale shapes clustered within carved room, not windows
# copied onto the outside of an uninhabited shell.
for i,(x,y) in enumerate(((-395,-240),(-373,-189),(-338,-278),
                          (-300,-220),(-273,-134),(-360,-113))):
    solid('NAVE_LIBRARY_RADIAL_ARCHIVE_'+str(i),[
        (x-7,y-21),(x+9,y-18),(x+13,y+18),(x-10,y+19)
    ],124,145+(i%3)*7,'oxide_copper')
walk('NAVE_LIBRARY_OPEN_ACCESS',[
 (-92,-293,86),(-175,-219,106),(-264,-181,122),
 (-336,-137,130)],22,7,'sunlit_stone')
walk('NAVE_LIBRARY_UPPER_PUBLIC_ACCESS',[
 (-300,-94,132),(-334,-54,180),(-353,-10,250)],19,7,'civic_ivory')
solid('NAVE_STATION_TRAIN_CONCOURSE',[
 (168,-423),(321,-447),(409,-372),(404,-108),(290,-83),
 (176,-154)],99,110,'civic_ivory')
for i,x in enumerate((246,305)):
    walk('NAVE_STATION_RAIL_'+str(i),[(x,-480,91),(x,-300,96),
         (x+22,-86,104)],4.5,3,'oxide_copper')
walk('NAVE_STATION_MAIN_PLATFORM',[(225,-418,115),
     (281,-255,118),(291,-102,122)],39,10,'sunlit_stone')
room('NAVE_STATION_TICKET_HALL',(332,-243),129,63,'cavity_stone',open_side=0)
walk('NAVE_STATION_FORUM_LINK',[(71,-372,86),(180,-292,101),
    (256,-230,110)],26,9,'civic_ivory')
# The ceremonial room is part of the right hollow, and faces the inhabited fissure.
solid('NAVE_CEREMONY_HOLLOW',[
 (212,-57),(344,-89),(455,-19),(451,173),
 (295,207),(186,106)],275,288,'sunlit_stone')
for i in range(6):
    y=12+i*24
    solid('NAVE_CEREMONY_AUDITORIUM_STEP_'+str(i),[
      (240+i*5,y),(404-i*3,y-5),(412-i*4,y+13),(239+i*4,y+15)
    ],289+i*3.4,295+i*3.4,'civic_ivory')
walk('NAVE_CEREMONY_UPPER_RITUAL_APPROACH',[
 (35,-170,92),(130,-60,154),(206,19,238),
 (255,72,291)],22,8,'sunlit_stone')
walk('NAVE_PUBLIC_CONTINUOUS_SPINE',[
 (-56,-494,85),(5,-360,87),(38,-185,92),
 (47,5,131),(97,171,244),(202,285,330)],31,9,'civic_ivory')
# A singular inhabited cross-fault, thick enough for a civic atrium.
# Its rise follows the β scar instead of a repetitive array of arches.
walk('M247_BETA_INHABITED_TRANSFAULT',[
 (-490,289,685),(-306,284,722),(-101,314,762),
 (108,346,808),(352,416,863),(611,500,931)],74,41,'shell_pearl')
walk('M247_BETA_PUBLIC_INTERNAL_PASSAGE',[
 (-490,288,709),(-306,283,746),(-101,313,786),
 (108,345,832),(352,415,887),(611,499,955)],22,3,'sunlit_stone')
# A second asymmetric, narrower crossing is a lower inhabited gallery,
# sharing actual landings with the library and station cut rooms.
walk('M247_SECONDARY_PUBLIC_CROSSING',[
 (-246,23,387),(-89,44,411),(71,69,435),
 (219,104,446),(318,158,461)],29,12,'oxide_copper')

# STAGE C: H1 and the upper city actually live in the excavated scar.
# The camera's original street is preserved. Dwellings are not towers:
# use a few unlike enclosed pockets embedded into and offset from excavated rock.
walk('H1_PUBLIC_CIVIC_STREET',[
 (758,242,437),(767,371,446),(777,493,456),
 (784,616,471),(798,760,488)],37,12,'civic_ivory')
walk('H1_PUBLIC_CLIFF_PASSAGE_LOWER',[
 (693,140,278),(725,246,349),(758,310,437)],21,8,'sunlit_stone')
walk('H1_PUBLIC_SCHOOL_VERTICAL_ROUTE',[
 (790,593,470),(796,616,536),(797,640,620),
 (795,655,721)],20,10,'civic_ivory')
room('H1_MARKET_HALL',(604,424),454,92,'shell_ochre',open_side=2)
room('H1_PUBLIC_SCHOOL',(981,565),483,109,'cavity_stone',open_side=5)
room('H1_CIVIC_LIBRARY',(590,650),502,94,'shell_pearl',open_side=1)
room('H1_INHABITED_HOUSE_CLUSTER',(1000,756),547,91,'shell_ochre',open_side=4)
solid('H1_MARKET_GARDEN_COURTYARD',[
 (656,371),(711,344),(737,415),(699,483),(652,448)
],449,457,'garden')
solid('H1_SCHOOL_ROOF_GARDEN',[
 (892,569),(945,535),(1019,557),(1071,625),(962,674)
],596,609,'garden')
for i,(x,y,z) in enumerate(((681,434,459),(921,504,489),
 (706,611,478),(924,717,528))):
    mini_tree('H1_INHABITED_COURT_TREE_'+str(i),x,y,z)
# Upper living chambers cut directly into the civic body, not placed on
# shallow free-standing floating plates.
for i,(x,y,z) in enumerate((
    (-525,122,663),(-479,324,763),(-580,437,1010),
    (595,306,692),(845,453,948),(1056,693,1153)
)):
    room('M247_OCCUPIED_CLIFF_CHAMBER_'+str(i),(x,y),
        z,58+11*(i%3),'cavity_stone',open_side=i%6)
walk('M247_WEST_LIVED_CITY_ASCENT',[
 (-321,-46,416),(-407,91,513),(-493,201,680),
 (-483,327,792),(-567,425,1019)],28,12,'sunlit_stone')
walk('M247_EAST_LIVED_CITY_ASCENT',[
 (339,54,430),(533,242,590),(678,358,708),
 (847,484,964),(1038,676,1171)],30,11,'sunlit_stone')

# STAGE D: W0 coast is a buttressed route and a formed urban embankment,
# not a separate triangular terrain illustration. This remains a partial W0 study.
solid('W0_EMBEDDED_TIDAL_CIVIC_BUTTRESS',[
 (110,-620),(312,-681),(577,-550),(650,-365),
 (550,-252),(366,-373),(172,-481)],-24,52,'cavity_stone')
solid('W0_SHORE_PUBLIC_INTERIOR',[
 (230,-643),(371,-668),(513,-567),(527,-441),
 (405,-416),(280,-519)],54,67,'civic_ivory')
solid('W0_TIDAL_TRANSIT_COURT',[
 (380,-540),(533,-557),(629,-421),(542,-332),
 (423,-389)],83,95,'sunlit_stone')
walk('W0_INHABITED_QUAY_TO_NAVE',[
 (472,-535,68),(317,-547,70),(159,-508,83),
 (30,-465,86)],30,12,'civic_ivory')
walk('W0_LONG_ASCENT_TO_H1',[
 (562,-394,88),(630,-234,157),(679,-55,266),
 (728,155,385),(758,252,441)],28,13,'sunlit_stone')
room('W0_TIDAL_LIBRARY_PUBLIC_ROOM',(428,-477),97,76,'cavity_stone',open_side=1)
# One unusual, contiguous cliff face added at its actual shore interface.
solid('W0_CARVED_MARINE_FORESHORE',[
 (-381,-584),(-145,-719),(125,-788),(282,-744),
 (419,-668),(205,-612),(-42,-555)],-30,24,'shell_ochre')

# No camera redirection or relabeling of the protected comparison views.
bpy.context.view_layer.update()
for n,m in cameras.items():
    cur=bpy.data.objects[n].matrix_world
    assert max(abs(cur[i][j]-m[i][j]) for i in range(4) for j in range(4)) < 1e-6
scene['INT2_RESEARCH']='INHABITED_MACRO_TWO_FAULT_CORES_SINGLE_CIVIC_SECTION'
scene['INT2_SOURCE_SHA256']=EXPECTED
scene['INT2_REMOVED_REJECTED_INT1_MESHES']=removed
scene['INT2_NEW_RESEARCH_MESHES']=len(coll.objects)
scene['INT2_CARVED_CAVITIES']=len(cuts)
scene['INT2_COORDS']='UNREGISTERED_RESEARCH_METRES'
scene['CONSTRUCTION']='HOLD'
scene['FORMAL_ART_ACCEPTED']=0
scene['COMPLETED_TARGETS']=0
scene.render.engine='CYCLES'
scene.cycles.device='CPU';scene.cycles.samples=16
scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=1100;scene.render.resolution_y=825
scene.render.resolution_percentage=100
scene.render.film_transparent=False
scene.render.image_settings.file_format='PNG'
dest=out/'HALO9_INT2_INHABITED_FAULT_MACRO.blend'
scene.camera=bpy.data.objects[camera_names[-1]]
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
saved={}
for n in camera_names:
    scene.camera=bpy.data.objects[n]
    path=renders/(n+'.png')
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    assert path.exists() and path.stat().st_size>5000
    saved[n]=hashlib.sha256(path.read_bytes()).hexdigest()
    print('INT2_ACTUAL_CYCLES_RENDER',n,path.stat().st_size,flush=True)
scene.camera=bpy.data.objects[camera_names[-1]]
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
report={
    'status':'TECH_UNDER_TEST_NOT_ART_PASS','source_sha256':EXPECTED,
    'blend_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
    'removed_rejected_architecture':removed,'new_mesh_count':len(coll.objects),
    'section_counts':counts,'boolean_cut_polygons':boolean_counts,
    'render_hashes':saved,'same_three_cameras':True,
    'scene_coordinates':'UNREGISTERED_RESEARCH_METRES',
    'nave_programs':['station','library','ceremony'],
    'h1_programs':['market','school','library','housing'],
    'w0_programs':['public quay','tidal library'],
    'human_access':'FUNCTION_UNKNOWN_NO_CONTINUOUS_SWEEP_QA',
    'formal_art_adopted':0,'completed_targets':0,'minecraft':'HOLD',
    'art':'UNREVIEWED_AWAITING_DIRECT_IMAGES'}
(out/'INT2_NATIVE_REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('INT2_NATIVE_FINISHED',report['blend_sha256'],flush=True)
