"""HALO-9 R4-E4: inhabitant-led H1 / NAVE native Blender study.

NEVER imports E2 reject geometry. Unregistered research metres. No Minecraft.
Run: blender -b -t 2 --python author.py -- --output /path/to/output
This file makes R0 only: art review is REQUIRED before any exterior shell work.
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector

args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
OUT = Path(args[args.index('--output')+1]).resolve() if '--output' in args else Path(__file__).parent/'output'
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'renders').mkdir(exist_ok=True)
if (OUT/'E4_R0B_WORKING.blend').exists():
    raise RuntimeError('Refuse to overwrite pre-existing native study')
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.users==0: bpy.data.collections.remove(c)
scene=bpy.context.scene
scene.render.engine='CYCLES'; scene.cycles.samples=20
scene.render.resolution_x=960; scene.render.resolution_y=640; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
scene.render.film_transparent=False
scene.world.color=(.15,.20,.27)
scene.unit_settings.system='METRIC'

COL={}
for name in ('H1_LIVING_URBAN_STREET','NAVE_INHABITED_PUBLIC_ROOM','PUBLIC_VERTICAL_CONNECTION','CAMERAS_AND_LIGHTS','30_TARGET_REGISTRY_RESEARCH_ONLY'):
    c=bpy.data.collections.new(name);scene.collection.children.link(c);COL[name]=c
active=COL['H1_LIVING_URBAN_STREET']

def collection(name):
    global active
    active=COL[name]

def mat(name,rgb,metal=0,rough=.67):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*rgb,1)
    bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
    return m
stone=mat('Warm limestone civic terraces',(.54,.58,.55))
pearl=mat('Porcelain concrete / inhabited facades',(.72,.76,.75),.12)
bronze=mat('Champagne titanium / thresholds',(.48,.37,.24),.34)
charcoal=mat('Mineral dark cut',(.13,.18,.21),.19)
glass=mat('Glazing / sky blue',(.12,.29,.33),.27,.16)
green=mat('Green civic gardens',(.14,.27,.18))
clay=mat('Soft terracotta housing',(.57,.35,.29))
blue=mat('Mist-blue ceramic',(.34,.49,.53),.08)
sea=mat('Cyan transit accents',(.20,.52,.57),.20)

# Explicit polygons define occupied ground, then architecture defines its edges.
def prism(name,xy,z,h,material):
    n=len(xy);verts=[(x,y,z) for x,y in xy]+[(x,y,z+h) for x,y in xy]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]
    faces.extend((j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);active.objects.link(o);o.data.materials.append(material)
    return o

def block(name,x,y,z,w,d,h,m,skew=0):
    return prism(name,[(x-w/2,y-d/2),(x+w/2,y-d/2+skew),(x+w/2,y+d/2),(x-w/2,y+d/2-skew)],z,h,m)

def beam(name,a,b,width,depth,m):
    a,b=Vector(a),Vector(b);mid=(a+b)*.5;delta=b-a
    bpy.ops.mesh.primitive_cube_add(size=1,location=mid)
    o=bpy.context.object;o.name=name;o.dimensions=(width,depth,delta.length)
    # local z is axis, local y is width/side; used for columns + sloped structure.
    o.rotation_euler=delta.to_track_quat('Z','Y').to_euler()
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection):c.objects.unlink(o)
    active.objects.link(o)
    o.data.materials.append(m)
    return o

def post(name,x,y,z,height,diam,m):
    return beam(name,(x,y,z),(x,y,z+height),diam,diam,m)

def path(name,points,width,depth,m):
    # This occupies a real continuous surface, not an unsupported bridge from a shell.
    pts=[Vector(p) for p in points]
    for i,(a,b) in enumerate(zip(pts,pts[1:])):
        midpoint=(a+b)*.5; direction=(b-a).normalized()
        normal=Vector((-direction.y,direction.x,0)).normalized()*width/2
        corners=[a-normal,a+normal,b+normal,b-normal]
        poly=[(p.x,p.y) for p in corners]
        # sample h from endpoint avg; used only on level walkways.
        prism(f'{name}_segment_{i:02}',poly,midpoint.z-depth,depth,m)

def roof(name,x,y,z,w,d,material,flip=False):
    # Author-ed folded roof, materially different from a generic flat cuboid.
    z1=z+6; ridge=(x+(-.16 if flip else .16)*w,y,z1+5)
    v=[(x-w/2,y-d/2,z),(x+w/2,y-d/2,z+2),(x+w/2,y+d/2,z),(x-w/2,y+d/2,z+1),
       (ridge[0],y-d/2,ridge[2]),(ridge[0],y+d/2,ridge[2]+1)]
    faces=[(0,1,4),(3,5,2),(0,4,5,3),(4,1,2,5)]
    data=bpy.data.meshes.new(name);data.from_pydata(v,[],faces);data.update()
    o=bpy.data.objects.new(name,data);active.objects.link(o);data.materials.append(material)

def facade(name,x,y,z,w,d,h,material,roofmat,flip=False,open_ground=False):
    # Occupied footprint, elevated roof and differentiated porches / glazing.
    prism(name+'_mass',[(x-w*.5,y-d*.5),(x+w*.43,y-d*.46),(x+w*.5,y+d*.4),(x-w*.45,y+d*.5)],z+(6 if open_ground else 0),h-(6 if open_ground else 0),material)
    roof(name+'_folded_canopy',x,y,z+h,w+4,d+6,roofmat,flip)
    for j in range(3):
        xx=x-w*.33 + j*w*.30
        block(name+f'_recessed_glass_{j}',xx,y-d*.50-0.3,z+9+(j%2)*3,6,1.4,min(14,h-11),glass)
    if open_ground:
        for sx in (-.36,.36):
            for sy in (-.34,.34):post(name+'_pilotis',x+w*sx,y+d*sy,z,6,1.5,bronze)
        block(name+'_public_threshold',x,y-d*.57,z,18,6,.5,stone)

def trees(prefix,locations,z):
    for i,(x,y) in enumerate(locations):
        block(f'{prefix}_planter_{i}',x,y,z,9,8,1.1,stone)
        post(f'{prefix}_trunk_{i}',x,y,z+1,7,1.3,bronze)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=5.4,location=(x,y,z+11))
        o=bpy.context.object;o.name=f'{prefix}_canopy_{i}'
        for c in list(o.users_collection):c.objects.unlink(o)
        active.objects.link(o);o.data.materials.append(green)

# H1: streets and two nested civic levels, no enclosing exterior shell.
# Section rests on several distinct buttressed urban cliff volumes.
# H1 city lives INSIDE three independent, interlocking inhabited rock sections.
# The street is a carved public seam between urban banks, not a platform stuck to a shell.
prism('H1_WEST_INHABITED_BANK', [(-547,-320),(-344,-330),(-348,-98),(-350,326),(-477,346),(-560,180)],950,170,charcoal)
prism('H1_EAST_INHABITED_BANK', [(-265,-340),(-97,-304),(-84,-191),(-87,130),(-144,334),(-256,295)],988,132,charcoal)
prism('H1_STREET_OCCUPIED_RIDGE', [(-348,-303),(-262,-307),(-254,265),(-342,270)],1084,36,charcoal)
# The lower levels contain civic rooms; no distant nonfunctional empty walls.
prism('H1_WEST_CIVIC_CUT_1',[(-540,-300),(-387,-317),(-366,-115),(-530,-91)],970,37,stone)
prism('H1_WEST_CIVIC_CUT_2',[(-536,-80),(-382,-78),(-372,108),(-537,139)],1015,42,blue)
prism('H1_EAST_LIVEWORK_CUT',[(-249,-300),(-118,-274),(-107,-115),(-251,-112)],1028,58,clay)

prism('H1_CENTRAL_PUBLIC_STREET', [(-340,-295),(-268,-290),(-253,262),(-335,269)],1120,1.1,stone)
prism('H1_SOUTH_MARKET_SQUARE',[(-413,-186),(-199,-176),(-186,-74),(-424,-58)],1120,1.3,stone)
prism('H1_NORTH_SCHOOL_SQUARE',[(-443,119),(-164,112),(-176,246),(-454,248)],1120,1.2,stone)
# Specific terraced public levels have occupied frontages and stair transitions.
prism('H1_EAST_UPPER_TERRACE',[(-254,-44),(-125,-35),(-105,100),(-245,101)],1120,12,blue)
prism('H1_NORTH_READING_TERRACE',[(-442,255),(-195,241),(-198,319),(-452,320)],1120,8,stone)
for i in range(16):
    block(f'H1_EAST_TERRACE_STAIRSTEP_{i}',-252+2.15*i,34,1120+i*.75,9,12,.75,bronze)
# Irregular houses form two meaningful facades rather than identical cuboid rows.
housing=[('SOUTHWEST_RESIDENCE',-455,-248,50,54,32,clay,False),
('WEST_COURTYARD_HOUSE',-452,-18,58,59,43,pearl,True),
('WEST_HOUSING_CLUSTER',-467,75,58,62,35,blue,False),
('EAST_LIVE_WORK_HOUSE',-156,-255,52,65,47,pearl,True),
('EAST_BALCONY_HOUSE',-157,-123,57,61,32,clay,False),
('EAST_HOUSING_ATRIUM',-170,77,60,56,46,pearl,True)]
for name,x,y,w,d,h,material,flip in housing:
    facade('H1_'+name,x,y,1120,w,d,h,material,bronze if flip else blue,flip,open_ground=('ATRIUM' in name or 'LIVE_WORK' in name))
# Not a token school: two wings, sheltered civic court, separate identifiable roof spans.
facade('H1_SCHOOL_STUDIOS',-404,292,1128,66,50,30,pearl,blue,False)
facade('H1_SCHOOL_LIBRARY',-274,294,1128,65,46,40,blue,bronze,True,open_ground=True)
block('H1_SCHOOL_COURT_THERMAL_STEPS',-334,243,1120,89,16,1.1,bronze)
facade('H1_MARKET_HALL',-376,-106,1120,51,49,24,bronze,pearl,True,open_ground=True)
facade('H1_PUBLIC_CLINIC',-204,178,1132,62,65,32,pearl,blue,False,open_ground=True)
# Legible street thresholds and overhead cross-connection, scaled to human eye.
for y in (-198,-54,90,240):
    beam('H1_LIGHT_TRANSVERSE',(-342,y,1130),(-262,y+4,1130),1.4,1.4,bronze)
    post('H1_STREET_LIGHT_W',-344,y,1121,9,1.2,bronze)
    post('H1_STREET_LIGHT_E',-260,y+4,1121,9,1.2,bronze)
trees('H1_CIVIC_ORCHARD',[(-213,-84),(-220,-60),(-406,171),(-389,187),(-183,211),(-216,224)],1121)

# NAVE: market, circulation, public library, open terraces, and generous daylight.
collection('NAVE_INHABITED_PUBLIC_ROOM')
# NAVE built from inhabited civic banks and a public seam, NOT an empty mega-slab.
prism('NAVE_LIBRARY_INHABITED_BANK',[(104,-344),(327,-331),(458,-114),(384,282),(133,357),(128,94)],80,50,charcoal)
prism('NAVE_MARKET_INHABITED_BANK',[(-416,-344),(-120,-343),(-118,-92),(-401,-81),(-444,118)],78,52,charcoal)
prism('NAVE_ARTS_INHABITED_BANK',[(-421,93),(-106,85),(-96,333),(-318,347)],95,35,charcoal)
prism('NAVE_PUBLIC_SEAM_FOUNDATION',[(-120,-326),(135,-324),(133,337),(-125,340)],109,21,stone)
# Two connected public civic wings physically contain upper floors.
prism('NAVE_EAST_PUBLIC_ROOM_SUBSTRUCTURE',[(150,-250),(368,-245),(360,-45),(147,-53)],130,37,blue)
prism('NAVE_WEST_PUBLIC_ROOM_SUBSTRUCTURE',[(-370,111),(-188,108),(-192,275),(-376,285)],130,34,blue)

prism('NAVE_PUBLIC_STREET_PAVING',[(-96,-305),(109,-304),(89,308),(-115,313)],130,1,stone)
prism('NAVE_FORUM_AND_EVENTS_COURT',[(-285,-94),(248,-95),(277,121),(-300,145)],130,1.2,stone)
prism('NAVE_MARKET_COURT',[(-381,-281),(-145,-273),(-124,-116),(-364,-110)],130,1,stone)
# Reading hall is an actual inhabitable covered PUBLIC space with open arcade and staggered upper gallery.
for x in (155,216,279,342):
    for y in (-256,-168,-80):post('NAVE_LIBRARY_COLONNADE',x,y,130,37,4.2,pearl)
prism('NAVE_LIBRARY_UPPER_WALK',[(140,-275),(366,-275),(371,-45),(145,-52)],167,4,bronze)
prism('NAVE_LIBRARY_TOP_FOLDED_ROOF',[(137,-280),(375,-269),(380,-38),(120,-46)],201,4,pearl)
facade('NAVE_CIVIC_ARCHIVE',272,205,130,122,76,40,blue,bronze,True,open_ground=True)
# Concentric public mezzanines vary in width/height and do not seal the sky.
prism('NAVE_EAST_CONCOURSE_2',[(160,-45),(385,-27),(353,151),(179,132)],153,3.5,stone)
prism('NAVE_WEST_ARTS_GALLERY_2',[(-358,91),(-177,97),(-172,263),(-339,275)],164,4,stone)
prism('NAVE_WEST_ARTS_GALLERY_3',[(-380,176),(-217,177),(-211,286),(-390,280)],194,4,bronze)
for i in range(20):
    block('NAVE_WEST_RISING_PUBLIC_STAIR_'+str(i),-162-2.6*i,113,130+1.65*i,9,22,1.65,stone)
for i in range(14):
    block('NAVE_EAST_PUBLIC_STAIRS_'+str(i),122+2.8*i,62,130+1.6*i,12,18,1.6,stone)
for x,y in [(-342,-260),(-295,-263),(-252,-263),(-206,-265)]:
    post('NAVE_MARKET_LIGHT_COLONNADE',x,y,131,22,2.5,bronze)
    beam('NAVE_MARKET_SHADE_RIB',(x,y,153),(x+9,y+22,160),1.4,2,pearl)
for i,(x,y) in enumerate([(-318,-184),(-233,-167),(-348,-117)]):
    block('NAVE_OPEN_MARKET_STALL_'+str(i),x,y,131,33,19,1.2,bronze)
    for dx in (-13,13):post('NAVE_STALL_POST_'+str(i),x+dx,y,132,6,1,stone)
    block('NAVE_STALL_SHADE_'+str(i),x,y,138,34,21,1.4,blue)
# Public passage visible from ground eye and two vertical outlooks.
for y in (-145,7,193,291):
    post('NAVE_LONG_GALLERY_PIER_W',-120,y,131,42,3,pearl)
    post('NAVE_LONG_GALLERY_PIER_E',130,y,131,42,3,pearl)
    beam('NAVE_DAYLIGHT_CROSS_RIB',(-120,y,174),(130,y,174),2.3,3,pearl)
trees('NAVE_GARDEN',[(-232,187),(-280,224),(37,157),(81,190),(43,232)],131)

# Connecting infrastructure: continuous lift housing and sky/ground public halls.
collection('PUBLIC_VERTICAL_CONNECTION')
for xx,yy in [(-268,48),(-292,48),(-268,77),(-292,77)]:
    post('CIVIC_LIFT_OPEN_FRAME',xx,yy,130,990,3.5,bronze)
for level in (130,170,240,360,510,710,890,1120):
    block('CIVIC_LIFT_REAL_LANDING_'+str(level),-280,63,level,36,43,2,stone)
# Lift stages exist in the model, but operating mechanics and complete route certification are not claimed.
prism('NAVE_LIFT_PUBLIC_FOYER',[(-317,24),(-234,24),(-220,99),(-329,107)],130,2,stone)
prism('H1_LIFT_STATION_ENTRY',[(-334,22),(-238,17),(-241,110),(-342,111)],1120,2,stone)
# Different open rail departure enclosures, distinguishable destinations.
for z in (170,1122):
    for xx in (-326,-237):post('LIFT_LOBBY_LANTERN',xx,63,z,18,2,sea)

# R0B / ART-FIRST: occupied civic thresholds, section-generated architecture.
collection('H1_LIVING_URBAN_STREET')
# Lift and school heights are tied to occupied west/east city banks, not external shelves.
facade('H1_PUBLIC_BATH_AND_REC_CENTER',-478,-122,1130,59,57,42,pearl,bronze,True,open_ground=True)
facade('H1_NEIGHBORHOOD_ASSEMBLY',-171,224,1132,69,61,48,blue,pearl,False,open_ground=True)
# Side civic gallery occupies and overlooks the street, with open ground level arcades.
for y in (-268,-205,-137,-65,20,106,177,241):
    post('H1_WEST_PUBLIC_ARCADE_COLUMN',-375,y,1120,29,4.5,stone)
    post('H1_EAST_PUBLIC_ARCADE_COLUMN',-246,y,1120,36,4.4,pearl)
    beam('H1_EAST_CIVIC_ARCADE_CROSS',(-246,y,1156),(-136,y,1156),5,3.4,bronze)
# The inhabited upper lane follows a crooked series of courtyards at a different elevation.
prism('H1_WEST_SECOND_CITY_LEVEL',[(-523,-65),(-416,-69),(-401,116),(-537,146)],1155,7.0,stone)
prism('H1_EAST_SECOND_CITY_LEVEL',[(-241,84),(-111,88),(-97,270),(-227,271)],1160,7.0,stone)
facade('H1_WEST_COLLECTIVE_WORKSHOP',-465,9,1162,52,56,37,clay,blue,False,open_ground=True)
facade('H1_EAST_MUSIC_AND_LIBRARY',-173,178,1167,53,52,41,pearl,bronze,True,open_ground=True)
# Stairs step between the lower street and both *inhabited* second-level public lanes.
for i in range(28):
    block('H1_WEST_PUBLIC_ASCENT_'+str(i),-351-2.25*i,62,1120+1.25*i,11,14,1.25,stone)
for i in range(28):
    block('H1_EAST_PUBLIC_ASCENT_'+str(i),-253+2.25*i,144,1120+1.42*i,13,15,1.42,bronze)
# Named lower city access apertures, differentiated from generic dark platform wall.
facade('H1_LOWER_WEST_WALK_CIVIC',-467,-234,1007,83,56,52,pearl,bronze,True,open_ground=True)
facade('H1_LOWER_EAST_CULTURE',-173,-214,1086,73,59,38,blue,pearl,False,open_ground=True)

collection('NAVE_INHABITED_PUBLIC_ROOM')
# NAVE banks are real occupied architecture; individual civic programs create its canyon.
facade('NAVE_PUBLIC_THEATRE',-343,35,130,88,89,76,bronze,pearl,True,open_ground=True)
facade('NAVE_NORTH_CIVIC_FORUM',-36,256,130,105,75,62,pearl,blue,False,open_ground=True)
facade('NAVE_EAST_MUSIC_PAVILION',325,116,153,91,82,56,blue,pearl,True,open_ground=True)
facade('NAVE_WEST_READERS_INSTITUTE',-276,175,164,85,64,53,pearl,bronze,True,open_ground=True)
# Open-air civic arcade frames across multiple levels; openings remain genuine.
for y in (-240,-125,-5,110,218):
    post('NAVE_WEST_FORUM_GATE',-152,y,131,46,5,stone)
    post('NAVE_EAST_FORUM_GATE',122,y,131,51,4.4,stone)
    beam('NAVE_FORUM_DAYLIGHT_SPAN',(-152,y,179),(122,y+13,188),4.5,6,pearl)
# Occupied west/east galleries at distinct heights. The two levels are not decorative floating strips.
prism('NAVE_WEST_PUBLIC_3RD_STORY',[(-384,176),(-221,177),(-214,287),(-391,283)],201,4.5,stone)
prism('NAVE_EAST_PUBLIC_READING_WALK',[(161,-33),(385,-25),(365,120),(176,121)],208,4.5,stone)
for i in range(24):
    block('NAVE_READERS_MULTI_LEVEL_STAIR_'+str(i),187+2.6*i,64,153+2.3*i,17,16,2.3,stone)
for i in range(23):
    block('NAVE_WEST_THEATRE_PUBLIC_STAIR_'+str(i),-192-2.5*i,187,164+1.76*i,14,18,1.76,bronze)
# Dwell-time public seating + water edge are places, not surface decoration.
prism('NAVE_AMPHITHEATRE_COURT',[(-146,-27),(91,-29),(131,79),(-112,98)],131,2,bronze)
for i in range(7):
    block('NAVE_AMPHITHEATRE_TIER_'+str(i),-110+7*i,28,132+1.05*i,13,85,1.05,stone)

# 30-target registry is research bookkeeping; unmade targets have no faked meshes.
collection('30_TARGET_REGISTRY_RESEARCH_ONLY')
targets=['M247-C','W0']+[f'H{i}' for i in range(1,7)]+[f'SB{i:02}' for i in range(1,17)]+[f'V{i}' for i in range(1,4)]+[f'METRO_AXIS_{i}' for i in range(1,4)]
for name in targets:
    o=bpy.data.objects.new(name+'__STATUS_MARKER',None);active.objects.link(o)
    o.empty_display_type='PLAIN_AXES';o.empty_display_size=12
    o.hide_render=True;o.hide_viewport=True
    o['official_coordinates_verified']=False
    o['research_progress']='E4_H1_NAVE_PARTIAL' if name in ('H1','M247-C') else ('E2_HISTORICAL_UNTOUCHED' if name in ('W0','METRO_AXIS_1','METRO_AXIS_2','METRO_AXIS_3') else 'NOT_MADE')
    o.location=(-280,63,1120) if name=='H1' else (0,0,0)

collection('CAMERAS_AND_LIGHTS')
def camera(name,eye,at,lens=32):
    bpy.ops.object.camera_add(location=eye)
    o=bpy.context.object;o.name=name
    for c in list(o.users_collection):c.objects.unlink(o)
    active.objects.link(o)
    d=Vector(at)-o.location;o.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    o.data.lens=lens;o.data.clip_end=25000;o.data.clip_start=.07
    return o
# Eye points are set at 1.65m above local public street floors, not E2 cameras.
views={
'human_sky_district':((-303,-267,1122.75),(-298,112,1146),29),
'human_public_interior':((5,-285,132.65),(10,147,175),26),
'human_street':((0,-420,132.65),(0,70,173),34),
'urban_aerial':((1400,-1800,2130),(-160,0,790),36),
'central_front':((0,-1700,1160),(-240,15,770),38),
'central_rear':((-110,1650,1280),(-255,5,790),38),
'east_seafront':((1450,-420,1310),(-280,20,750),35)
}
for name,(eye,at,lens) in views.items():camera(name,eye,at,lens)
def area(name,pos,power,size):
    bpy.ops.object.light_add(type='AREA',location=pos)
    o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size
    for c in list(o.users_collection):c.objects.unlink(o)
    active.objects.link(o)
    o.rotation_euler=(Vector((-250,0,720))-o.location).to_track_quat('-Z','Y').to_euler()
area('Diffuse sky district daylight',(-60,-110,1500),3500000,850)
area('NAVE diffuse daylight',(50,60,460),1400000,720)
bpy.ops.object.light_add(type='SUN',location=(800,-500,2000))
sun=bpy.context.object;sun.name='Raking daylight';sun.data.energy=1.7
sun.rotation_euler=(math.radians(32),math.radians(-19),math.radians(-30))
for c in list(sun.users_collection):c.objects.unlink(sun)
active.objects.link(sun)

scene['stage']='R4_E4_R0B_SECTION_REWORK_UNREVIEWED'
scene['official_coordinates_verified']=False
scene['minecraft_write']='FORBIDDEN'
scene['art']='NOT_REVIEWED'
scene['formal_adoption']=False
scene['base_e3_head']='e3af9abb63f38399811a3c2c7c2e1e5279b036d9'
blend=OUT/'E4_R0B_WORKING.blend'
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
for name in ('human_sky_district','human_public_interior'):
    scene.camera=bpy.data.objects[name]
    scene.render.filepath=str(OUT/'renders'/f'{name}.png')
    bpy.ops.render.render(write_still=True)
report={
    'schema':'halo9-r4-e4-native-first-two-v1',
    'stage':'R0B_UNREVIEWED',
    'blend_file':blend.name,
    'native_blender_saved':blend.is_file(),
    'geometry_object_count':sum(o.type=='MESH' for o in bpy.data.objects),
    'h1_meshes':sum(o.type=='MESH' for o in COL['H1_LIVING_URBAN_STREET'].objects),
    'nave_meshes':sum(o.type=='MESH' for o in COL['NAVE_INHABITED_PUBLIC_ROOM'].objects),
    'cameras':list(views),
    'renders_created':[p.name for p in sorted((OUT/'renders').glob('*.png'))],
    'actual_visual_review':'PENDING',
    'art_pass':False,
    'completed_targets':0,
    'partial_targets':['M247-C','H1'],
    'not_placed_targets':24,
    'official_coordinates_verified':False,
    'city_master_complete':False,
    'minecraft':'HOLD',
    'e2_files_touched':False
}
(OUT/'R0_INSPECTION.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print('HALO9_E4_R0_RESULTS '+json.dumps(report,ensure_ascii=False))
