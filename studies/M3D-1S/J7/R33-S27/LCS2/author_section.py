"""HALO9 / one architecture-first spatial re-authoring from untouched LCS1-R1 research COPY.
The fixed research cameras/units and canonical constraints remain untouched.
No formal art adoption, no Minecraft writes, and no official coordinate reconciliation.
"""
import bpy, math, sys, hashlib, json
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[args.index('--output')+1]) if '--output' in args else Path('/tmp/halo9_section')
out.mkdir(parents=True,exist_ok=True);(out/'renders').mkdir(exist_ok=True)
source=Path(bpy.data.filepath)
assert source.name=='SECTION_R1_SOURCE.blend',source
assert hashlib.sha256(source.read_bytes()).hexdigest()=='25a31c532d4e70556400b51882b58af7d42f27056755d2b5b6075b394dbd39f0'
S=bpy.context.scene
assert S['CONSTRUCTION']=='HOLD' and S['FORMAL_ART_ACCEPTED']==0 and S['COMPLETED_TARGETS']==0
camera_names=['E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL']
fixed={k:bpy.data.objects[k].matrix_world.copy() for k in camera_names}
# Preserve original landform, sea, cameras and lights. Research-only, remove all
# rejected LCS1/R1 superstructure and old NAVE/H1 scaffolds from a COPY.
retain={'W0_NORTH_FRACTURED_RANGE','W0_WEST_BASALT_ESCARPMENT','W0_GROUND_BASIN','W0_EASTERN_ARTIFICIAL_SEA'}
removed=[]
for o in tuple(S.objects):
    if o.type in {'MESH','CURVE'} and o.name not in retain:
        removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
assert len(removed)>200,len(removed)
C=bpy.data.collections.new('LCS2_SECTION_WITH_OCCUPIED_MASS_UNAPPROVED');S.collection.children.link(C)

def material(key,rgb,metal=0,rough=.6,emit=0):
    m=bpy.data.materials.new('LCS2_'+key);m.diffuse_color=(*rgb,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*rgb,1);bs.inputs['Metallic'].default_value=metal
    bs.inputs['Roughness'].default_value=rough
    if emit:
        bs.inputs['Emission Color'].default_value=(*rgb,1)
        bs.inputs['Emission Strength'].default_value=emit
    return m
M={
 'ivory':material('porous_limestone',(.62,.70,.69),.14,.59),
 'pale':material('ceramic_public_rooms',(.82,.79,.65),.05,.67),
 'night':material('deep_rift_stone',(.075,.125,.16),.22,.54),
 'bronze':material('bronze_tracer',(.55,.32,.17),.48,.36),
 'glass':material('civic_glass',(.055,.28,.34),.37,.24),
 'moss':material('roof_gardens',(.18,.36,.24),0,.88),
 'walk':material('pedestrian_paving',(.40,.48,.46),.1,.7),
 'warm':material('inhabited_luminance',(.88,.53,.26),.05,.45,1.3),
 'way':material('public_wayfinding',(.34,.75,.79),.1,.28,1.6),
 'roof':material('matte_titanium',(.27,.36,.4),.4,.42),
}
def mesh(name,vs,fs,mat):
    m=bpy.data.meshes.new('LCS2_'+name);m.from_pydata(vs,[],fs);m.update()
    ob=bpy.data.objects.new('LCS2_'+name,m);C.objects.link(ob);m.materials.append(M[mat]);return ob

def slab(name,poly,z,d,mat):
    n=len(poly);assert n>=3 and d>0
    verts=[(x,y,z-d) for x,y in poly]+[(x,y,z) for x,y in poly]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,verts,faces,mat)

def block(name,center,dim,mat):
    x,y,z=center;dx,dy,dz=(v/2 for v in dim)
    v=[(x+a*dx,y+b*dy,z+c*dz) for c in (-1,1) for a,b in ((-1,-1),(1,-1),(1,1),(-1,1))]
    return mesh(name,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)

def strut(name,a,b,w,h,mat):
    a=Vector(a);b=Vector(b);delta=b-a
    assert delta.length>1
    q=delta.to_track_quat('Z','Y');verts=[]
    for t in (0,1):
        for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]:
            verts.append(tuple(a+q@Vector((x*w/2,y*h/2,t*delta.length))))
    return mesh(name,verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)

def walk(name,pts,w,d,mat):
    assert len(pts)>=2
    vs=[]
    for i,(x,y,z) in enumerate(pts):
        delta=Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(0,i-1)])
        l=math.hypot(delta.x,delta.y);dx,dy=(-delta.y/l,delta.x/l) if l>1 else (1,0)
        vs.extend([(x+s*dx*w/2,y+s*dy*w/2,z-q) for q in (d,0) for s in (-1,1)])
    f=[]
    for i in range(len(pts)-1):
        a=i*4;b=(i+1)*4
        f.extend([(a,a+1,b+1,b),(a+2,b+2,b+3,a+3),(a,a+2,b+2,b),(a+1,b+1,b+3,a+3)])
    f.extend([(0,1,3,2),(len(vs)-4,len(vs)-2,len(vs)-1,len(vs)-3)])
    return mesh(name,vs,f,mat)

def loft(name,profiles,mat):
    n=len(profiles[0]);assert n>=3 and all(len(p)==n for p in profiles)
    v=[p for prof in profiles for p in prof]
    f=[tuple(reversed(range(n))),tuple(range((len(profiles)-1)*n,len(profiles)*n))]
    for j in range(len(profiles)-1):
        for i in range(n):
            a=j*n+i;b=j*n+(i+1)%n;f.append((a,b,b+n,a+n))
    return mesh(name,v,f,mat)

def stairline(name,start,end,count,width):
    a,b=Vector(start),Vector(end);d=b-a
    h=Vector((-d.y,d.x,0)).normalized()*width/2
    for k in range(count):
        f=(k+.5)/count;p=a+d*f
        slab(name+'_'+str(k),[(p.x-h.x-4,p.y-h.y-4),(p.x+h.x-4,p.y+h.y-4),
            (p.x+h.x+4,p.y+h.y+4),(p.x-h.x+4,p.y-h.y+4)],p.z+0.5,1.8,'pale')

def tree(n,x,y,z,h=22):
    strut('garden_tree_trunk_'+str(n),(x,y,z),(x+1,y+1,z+h*.7),1.2,1.2,'night')
    # Irregular tapered canopy; clearly local gardens, not another central mega-shell.
    p1=[(x-8,y-5,z+h*.58),(x+7,y-8,z+h*.58),(x+11,y+3,z+h*.58),(x,y+9,z+h*.58),(x-10,y+4,z+h*.58)]
    p2=[(x-4,y-3,z+h),(x+4,y-5,z+h),(x+6,y+3,z+h),(x,y+7,z+h),(x-7,y+2,z+h)]
    loft('garden_tree_canopy_'+str(n),[p1,p2],'moss')

# Architectural sequence 1: contiguous civic excavation at sea level. No giant exterior box.
# NAVE floor is visible from its preserved pedestrian camera (15,-360,73.7).
slab('NAVE_FORUM_EXCAVATED_PUBLIC_FLOOR',[(-230,-450),(-71,-495),(106,-455),(227,-330),
 (244,-98),(155,79),(45,209),(-102,201),(-242,44),(-286,-199)],70,22,'pale')
slab('NAVE_PUBLIC_CONCOURSE',[(-180,-371),(-60,-405),(91,-375),(180,-232),(127,-88),
 (-4,-23),(-137,-111)],98,8,'walk')
slab('NAVE_LIBRARY_AUDITORIUM_WEST', [(-361,-341),(-224,-324),(-207,-151),
 (-300,13),(-390,27),(-429,-175)],145,18,'pale')
slab('NAVE_LIBRARY_BALCONY_WEST',[(-383,-263),(-303,-258),(-266,-139),
 (-328,-80),(-400,-123)],208,8,'ivory')
# Rear wall becomes inhabited masonry, not false decorative signage.
for i, (x,y) in enumerate([(-368,-305),(-375,-120),(-252,-301),(-284,-61)]):
    strut('library_branched_support_'+str(i),(x,y,137),(x+22,y+18,313),9,13,'night')
for k,(x,y) in enumerate([(-359,-245),(-320,-225),(-338,-166),(-291,-105),(-380,-94)]):
    block('library_actual_reading_stacks_'+str(k),(x,y,168),(8,34,43),'bronze')
# East station lower and upper concourses; shaded public waiting rather than blank roof.
slab('NAVE_EAST_STATION_PLATFORM',[(190,-377),(346,-365),(369,-225),(331,-68),
 (204,7),(149,-118)],135,12,'walk')
slab('NAVE_STATION_MEZZANINE',[(221,-339),(308,-314),(330,-210),(288,-95),(213,-108)],220,9,'pale')
for k,(x,y) in enumerate([(195,-367),(330,-326),(340,-176),(236,-55)]):
    strut('east_station_actual_arch_pier_'+str(k),(x,y,132),(x-16,y+39,343),10,13,'ivory')
for i in range(12):
    block('station_wayfinding_platform_'+str(i),(205+i*10,-353,138),(1,15,1),'way')
# NAVE north civic theater: amphitheatre destination facing the main public void.
slab('NAVE_NORTH_CEREMONY', [(-173,160),(-104,100),(75,107),(210,199),
 (166,302),(-19,325),(-151,263)],170,15,'pale')
for i in range(9):
    zz=174+i*3;yy=197+i*11
    slab('ceremonial_seats_'+str(i),[(-111+i*2,yy),(123-i*1.5,yy),
      (116-i*1.5,yy+7),(-104+i*2,yy+7)],zz,3,'ivory')
# Real pedestrian continuities from shore to forum to each destination.
walk('shore_into_forum',[(-157,-638,38),(-125,-540,57),(-100,-460,68),(-46,-383,72)],25,8,'pale')
walk('forum_to_library',[(-90,-255,77),(-180,-220,106),(-252,-177,145)],21,6,'ivory')
walk('forum_to_station',[(111,-277,80),(180,-283,112),(235,-271,135)],22,7,'walk')
walk('forum_to_ritual',[(-38,-85,86),(-23,43,129),(7,179,169)],24,7,'ivory')
# The monumental positive structure is built AROUND these destinations.
# Twin facing inhabited fault escarpments are composed of real interior porticoes,
# supports and accessible terraces, NOT a solid rectangular shell with pasted facades.
west_profiles=[
 [(-510,-354,70),(-295,-383,70),(-211,-167,70),(-263,64,70),(-526,124,70),(-626,-164,70)],
 [(-562,-340,346),(-316,-383,346),(-196,-144,346),(-261,101,346),(-565,171,346),(-672,-136,346)],
 [(-623,-283,665),(-298,-330,665),(-138,-87,665),(-234,190,665),(-601,247,665),(-749,-69,665)],
 [(-681,-240,906),(-296,-267,906),(-91,-20,906),(-212,253,906),(-640,321,906),(-849,10,906)] ]
# Instead of sealing huge volumes, these five separated cut-space ribs make
# the very large *missing space* legible while supporting civic and residential galleries.
for i in range(len(west_profiles)-1):
    a=west_profiles[i];b=west_profiles[i+1]
    for j in (0,2,4):
        strut('west_fault_deep_inhabited_support_%d_%d'%(i,j),a[j],b[j],29+i*3,35+i*4,'night' if j==0 else 'ivory')
    z0=a[0][2];z1=b[0][2]
    # Walkable volumes span across the supports on different heights and y offsets.
    poly=[(a[j][0]*.7+b[j][0]*.3,a[j][1]*.7+b[j][1]*.3) for j in range(6)]
    slab('west_fault_public_inhabited_level_'+str(i),poly,z0+(z1-z0)*.6,20,'pale' if i%2 else 'ivory')
    # A few distinct skylit hall volumes (not repetitive facade floor slats).
    slab('west_fault_recessed_library_gallery_'+str(i),poly[1:5],z0+(z1-z0)*.6+54,9,'roof')
# Middle and high public rooms express the diagonal transfer fault by paired inhabited islands.
for i,(x,y,z,w,d) in enumerate([(-393,53,380,230,170),(-337,192,637,243,170),
                                 (-245,351,852,209,145),(-113,455,1058,205,124)]):
    pl=[(x-w*.6,y-d*.4),(x+w*.53,y-d*.6),(x+w*.72,y+d*.5),(x-w*.41,y+d*.62)]
    slab('diagonal_fault_civic_public_hall_floor_'+str(i),pl,z,15,'pale')
    roof=[(u+12*(i%2),v+11) for u,v in pl]
    slab('diagonal_fault_departed_civic_roof_'+str(i),roof,z+95+12*i,11,'roof')
    for j in (0,2):
        xx,yy=pl[j];strut('fault_civic_hall_fork_%d_%d'%(i,j), (xx,yy,z-4),
                         (xx+17,yy+23,z+95+12*i),10,17,'ivory')
# Spatially DIFFERENT elevated inhabited flank around the fault, not symmetric second skyscraper.
for i,(x,y,z,wi,di) in enumerate([(408,210,330,190,154),(480,322,535,201,184),
                                  (570,390,745,189,160),(672,500,911,170,139)]):
    poly=[(x-wi*.6,y-di*.2),(x+wi*.35,y-di*.6),(x+wi*.66,y+di*.43),
          (x-wi*.22,y+di*.71)]
    slab('east_displaced_occupied_city_floor_'+str(i),poly,z,24,'ivory')
    # Real public viewing rooms with substantial height and broken roof profiles.
    near=[(a+6,b+7) for a,b in poly]
    slab('east_displaced_civic_glazed_gallery_'+str(i),near[:3]+[near[-1]],z+52,7,'glass')
    for j in (0,2):
        xx,yy=poly[j];strut('east_sky_room_weightbearing_%d_%d'%(i,j),
                            (xx,yy,z-4),(xx+14,yy+16,z+81),7,12,'night')
    slab('east_displaced_occupied_roof_'+str(i),poly[:3]+[(x-14,y+di*.34)],z+86,10,'roof')
# Diagonal displaced central CIVIC BRIDGE: crossing made of a thick space with two
# branches around a 200m-open rift, rather than a continuous giant canopy.
walk('deep_fault_branch_west',[(-413,48,370),(-341,211,615),(-228,328,843),(-91,447,1055)],35,14,'ivory')
walk('deep_fault_branch_east',[(377,171,330),(468,302,532),(563,391,740),(671,512,910)],38,15,'night')
walk('central_upper_occupied_crossing',[(-293,310,829),(-116,378,864),
                                         (118,425,862),(360,450,815),(535,421,740)],38,13,'pale')
# NAVE overhead is an open public VAULT, genuine deep struts support occupancies;
# no wide horizontal opaque plate conceals the 400m tall interior.
for i,(y,z) in enumerate([(-345,309),(-78,356),(165,415),(345,483)]):
    strut('civic_open_vault_west_root_'+str(i),(-336,y,70+i*44),(-212,y+33,z),18,20,'ivory')
    strut('civic_open_vault_east_root_'+str(i),(335,y,130+i*46),(220,y+11,z+15),18,20,'ivory')
    strut('skylight_vault_fork_west_'+str(i),(-212,y+33,z),(-55,y+54,z+68),11,14,'roof')
    strut('skylight_vault_fork_east_'+str(i),(220,y+11,z+15),(42,y+54,z+77),12,13,'roof')
# The NAVE view cannot become boxed; large span between upper forks remains daylight open.

# Architectural sequence 2: H1 is a VERTICAL REAL CITY, not one elevated island.
# Upper public datum at z~434, camera x760 y270 z438.7; keep its forward cone free.
# Deep three-level inhabited undercroft with opening to the eastern water.
for i,(z,poly) in enumerate([
 (116,[(416,42),(574,14),(741,89),(837,230),(756,334),(533,315),(430,217)]),
 (239,[(448,87),(632,78),(843,169),(926,316),(815,426),(561,382),(457,254)]),
 (352,[(494,129),(665,130),(907,239),(1022,383),(908,505),(608,458),(507,297)])]):
    slab('H1_OCCUPIED_UNDERCITY_CIVIC_LEVEL_'+str(i),poly,z,19,'walk' if i==0 else 'ivory')
    # Structural buttresses double as occupied arcades and harbor-facing vertical corridors.
    for k in (0,2,4,6):
        x,y=poly[k];top=(239,352,431)[i]
        strut('H1_UNDERCITY_CIVIC_PIER_%d_%d'%(i,k),(x,y,z-18),
              (x+4+(k%3)*11,y+7,top),12+(i%2)*2,19,'night' if k%4==0 else 'ivory')
    if i<2:
        hall=poly[1:5]
        slab('H1_CITY_LIBRARY_SUBCITY_PUBLIC_HALL_'+str(i),hall,z+52,6,'pale')
    walk('H1_UNDERCITY_WALK_TO_NEXT_'+str(i),[(587,122,z+2),
        (653,206,z+42),(706,305,(239,352,438)[i])],15,5,'pale')
# The surface city forms two INTERLOCKED inhabited cliff neighborhoods with an open main street.
left=[(540,310),(713,310),(721,788),(568,827),(520,663)]
right=[(833,317),(1060,295),(1113,404),(1100,787),(886,813),(841,692)]
slab('H1_INHABITED_LEFT_CLIFF_FOUNDATION',left,436,17,'ivory')
slab('H1_INHABITED_RIGHT_CLIFF_FOUNDATION',right,436,24,'pale')
slab('H1_LIVING_PEDESTRIAN_CANYON',[(736,330),(820,326),(837,809),(739,830)],435,9,'walk')
# Actual school/library/market with roof break and publicly entered atria.
slab('H1_LIVING_LIBRARY_ATRIUM_FLOOR',[(548,344),(703,336),(716,476),(607,494),(536,416)],442,8,'pale')
slab('H1_LIVING_LIBRARY_DOUBLE_HEIGHT_GALLERY',[(551,362),(631,347),(657,447),(576,457)],474,8,'ivory')
for j,(x,y) in enumerate([(559,353),(694,359),(682,480),(554,419)]):
    strut('H1_LIBRARY_PUBLIC_BRANCH_'+str(j),(x,y,437),(x+9,y+12,519),6,11,'roof')
slab('H1_LIBRARY_NORTH_LIGHTROOF',[(533,342),(612,325),(631,477),(547,460)],523,11,'roof')
slab('H1_LIBRARY_EAST_OPEN_ROOF',[(667,341),(721,346),(734,471),(673,488)],548,7,'ivory')
# Opposite library: school open courtyard, real galleried public learning wings.
slab('H1_LIVING_SCHOOL_COURTYARD',[(865,415),(1022,402),(1060,581),(878,605)],442,5,'moss')
for j,(poly,roofh) in enumerate([
 ([(851,327),(921,310),(947,408),(865,440)],501),
 ([(965,333),(1070,343),(1084,464),(1020,456)],544),
 ([(887,595),(1073,562),(1096,690),(932,725)],522)]):
    slab('H1_SCHOOL_CLASSROOM_FLOOR_'+str(j),poly,446,8,'pale')
    slab('H1_SCHOOL_OPEN_MEZZANINE_'+str(j),[(x+4,y+6) for x,y in poly],
         465+(roofh-490)*.4,7,'walk')
    slab('H1_SCHOOL_WING_MONO_ROOF_'+str(j),[(x+6,y+12) for x,y in poly],roofh,9,'roof')
    for k in (0,2):
        x,y=poly[k];strut('H1_SCHOOL_ACTUAL_PIER_%d_%d'%(j,k),
                         (x,y,435),(x+9,y+13,roofh),5,8,'ivory')
# Sky main street continues to elevated transit and cliff overlook; avoid dark roof overhead.
walk('H1_TRUE_PUBLIC_HIGH_STREET',[(776,350,436),(777,462,436),(783,605,439),(793,755,443)],29,8,'walk')
walk('H1_SCHOOL_LIBRARY_PEDESTRIAN_CROSSING',[(661,490,440),(728,508,438),
 (786,535,439),(848,530,441),(918,515,443)],17,6,'pale')
# Building diversity: actual masonry enclosure from piers, nested occupied levels,
# inset glazing/awnings, nonparallel roofs. Modular bays NEVER become the main mass.
buildings=[
 ('southwest_market',554,522,56,70,58,4),('west_school_housing',641,530,64,59,77,3),
 ('middle_living_quarter',550,615,72,66,90,4),('cliff_steps_housing',640,643,59,88,63,5),
 ('northern_court',560,738,64,66,68,3),('north_floating_house',656,742,59,54,80,4),
 ('east_south_bazaar',856,702,81,55,67,3),('east_residential_bay',966,712,77,58,92,5)]
for i,(name,x,y,w,d,h,typ) in enumerate(buildings):
    z=444+(i%3)*4
    p=[(x,y),(x+w,y+5),(x+w-7,y+d),(x+7,y+d+7)]
    slab('H1_'+name+'_ground',p,z,6,'walk')
    slab('H1_'+name+'_inhabited_upper',[(a+5,b+9) for a,b in p],z+h*.54,6,'ivory')
    for k in (0,1,2,3):
        xx,yy=p[k];strut('H1_'+name+'_loadpier_'+str(k),
            (xx,yy,z-3),(xx+(k-1)*3,yy+7,z+h),4,9,'night' if typ>3 else 'ivory')
    # Substantial cantilevered independent roof pitch, with real sky court opening.
    roof=[(a+(k%2)*8-4,b+(k%3)*4-7) for k,(a,b) in enumerate(p)]
    slab('H1_'+name+'_distinct_roof',roof,z+h+(-6 if i%2 else 8),8,'roof')
    # Public shop/house porch at the high street, with physical glazed recess.
    block('H1_'+name+'_porch_entry',(x+w*.53,y+2,z+8),(w*.27,4,16),'glass')
    strut('H1_'+name+'_door_header',(x+w*.34,y-3,z+17),
           (x+w*.73,y+1,z+18),2,3,'bronze')
    for k in range(3 if typ>=4 else 2):
        block('H1_'+name+'_upper_inhabited_glazing_'+str(k),
              (x+15+k*17,y+d-2,z+28+k*2),(12,4,18),'glass')
    # Visibly accessible exterior balconies on the public street side.
    walk('H1_'+name+'_exterior_balcony',[(x+3,y+7,z+h*.6),
      (x+w*.45,y+2,z+h*.62),(x+w-6,y+9,z+h*.61)],6,3,'ivory')
# Roof court / waterfront overlooks and multiple traversable school connections.
slab('H1_NORTH_GARDEN_TERMINAL',[(722,782),(834,782),(863,853),(709,858)],446,10,'ivory')
slab('H1_OVERLOOK_TRANSIT_CANOPY',[(709,776),(828,780),(888,848),(725,863)],485,8,'roof')
walk('H1_HIGH_TERRACE_TO_NAVE',[(677,374,442),(615,312,437),
 (543,241,382),(462,185,303),(355,91,220),(251,26,161)],24,8,'ivory')
walk('H1_STAIRS_TO_EAST_HARBOR',[(884,356,442),(907,236,360),
 (859,101,240),(710,-58,121),(607,-207,61)],25,7,'walk')
for i,(x,y,z) in enumerate([(728,390,442),(824,465,442),(734,565,445),
                             (837,645,446),(729,767,448),(879,572,445)]):
    tree(i,x,y,z,23+i%3*4)
# W0 water and terrain aren't decorative wallpaper: new inhabited shore carved into slope.
for i,(z,p) in enumerate([
 (45,[(-474,-478),(-275,-551),(-108,-654),(151,-642),(314,-472),(482,-360),
       (612,-185),(550,80),(333,112),(88,-103),(-228,-195)]),
 (22,[(-303,-662),(-62,-744),(182,-696),(383,-528),(575,-394),(638,-275),
       (510,-221),(266,-432),(56,-585),(-221,-583)])]):
    slab('W0_TIDAL_QUAY_LIVING_TERRACE_'+str(i),p,z,13+i*7,'night' if i==0 else 'walk')
for k in range(13):
    y=-620-k*7
    slab('W0_TIDAL_PUBLIC_SLOPING_STAIR_'+str(k),
      [(-145-k*4,y),(88+k*4,y-8),(155+k*4,y+16),(-115-k*4,y+19)],
      43-k*1.85,3,'pale')
slab('W0_EAST_FERRY_PUBLIC_FLOOR',[(393,-392),(551,-388),(654,-279),
 (661,-165),(576,-127),(453,-207)],44,11,'pale')
slab('W0_EAST_FERRY_PUBLIC_MEZZANINE',[(434,-344),(562,-325),(613,-246),
 (570,-175),(491,-223)],82,9,'ivory')
for k,(x,y) in enumerate([(423,-378),(538,-365),(645,-240)]):
    strut('W0_TERMINAL_FOLDED_HALL_PIER_'+str(k),(x,y,35),(x+13,y+11,148),8,12,'ivory')
slab('W0_FERRY_SPLIT_ROOF_NORTH',[(395,-400),(509,-393),(555,-294),(461,-251)],147,11,'roof')
slab('W0_FERRY_SPLIT_ROOF_SOUTH',[(554,-310),(659,-275),(667,-159),(585,-150)],165,11,'ivory')
walk('W0_FERRY_TO_NAVE',[(480,-368,51),(377,-449,50),(202,-553,54),(20,-602,59),
                          (-117,-639,42)],25,6,'pale')
walk('W0_FERRY_TO_H1',[(598,-180,55),(666,-65,98),(713,70,211),
                          (764,211,353),(785,335,437)],24,9,'walk')
# Preserve requirements; no fancy material/mesh counts can declare art accepted.
S['LCS2_STATUS']='REAL_SPATIAL_REBUILD_AWAITING_DIRECT_ART_REVIEW'
S['LCS2_SOURCE_LCS1_R1_SHA256']='25a31c532d4e70556400b51882b58af7d42f27056755d2b5b6075b394dbd39f0'
S['LCS2_REJECTED_RESEARCH_MESHES_REMOVED']=len(removed)
S['LCS2_PROGRAM']='NAVE_LIBRARY_STATION_CEREMONY_H1_SCHOOL_RESIDENTS_W0_PORT'
S['LCS2_COORDINATES']='ISOLATED_RESEARCH_METRES_NOT_WORLD_REGISTERED'
S['CONSTRUCTION']='HOLD';S['FORMAL_ART_ACCEPTED']=0;S['COMPLETED_TARGETS']=0
for name, matrix in fixed.items():
    bpy.context.view_layer.update()
    actual=bpy.data.objects[name].matrix_world
    assert max(abs(actual[i][j]-matrix[i][j]) for i in range(4) for j in range(4))<1e-6
S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=12;S.cycles.use_denoising=True
S.render.threads_mode='FIXED';S.render.threads=2
S.render.resolution_x=1100;S.render.resolution_y=825;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.film_transparent=False
S.camera=bpy.data.objects['E11_URBAN_AERIAL']
p=out/'LCS2_TRUE_ARCHITECTURAL_SECTION.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True)
shots={}
for name in camera_names:
    S.camera=bpy.data.objects[name];f=out/'renders'/(name+'.png');S.render.filepath=str(f)
    bpy.ops.render.render(write_still=True)
    assert f.exists() and f.stat().st_size>4000, name
    shots[name]=hashlib.sha256(f.read_bytes()).hexdigest()
    print('LCS2_REAL_RENDER',name, f.stat().st_size,flush=True)
S.camera=bpy.data.objects['E11_URBAN_AERIAL']
bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True)
report={'schema':'halo9-lcs2-real-section-rebuild-v1','engine':bpy.app.version_string,
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'output_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
        'removed_rejected_meshes':len(removed),'authored_new_meshes':len(C.objects),
        'render_png_sha256':shots,'cameras_unmodified':True,
        'art':'AWAITING_REAL_IMAGE_REVIEW_NOT_ACCEPTED','completed_targets':0,
        'formal_art_acceptances':0,'minecraft':'HOLD'}
(out/'LCS2_AUTHOR_REPORT.json').write_text(json.dumps(report,indent=2))
print('LCS2_NATIVE_REAL_COMPLETE',json.dumps(report),flush=True)
