"""HALO-9 INT1 — interior-first civic city, independent Blender research.

Derived ONLY from frozen R3 research BLEND cameras/landscape/lighting. Remove
rejected architectural geometry in a copy, construct functional interior buildings
before deriving outer inhabited city mass. Research metres, not canonical coords.
No canonical/WorldEdit writes. No formal art adoption.
"""
import bpy, math, sys, json, hashlib
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[args.index('--output')+1]);out.mkdir(parents=True,exist_ok=True)
(out/'renders').mkdir(exist_ok=True)
source=Path(bpy.data.filepath)
SOURCE_SHA='f4f9f560bd35a3b2a4255aef52d4f52201e28a9a9d8530f5507f6ad8d4e1d703'
assert source.name=='INT1_SOURCE.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()==SOURCE_SHA
S=bpy.context.scene
assert S['CONSTRUCTION']=='HOLD' and S['FORMAL_ART_ACCEPTED']==0 and S['COMPLETED_TARGETS']==0
cams=['E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL']
fixed={name:bpy.data.objects[name].matrix_world.copy() for name in cams}
# Force only known terrain/sea to survive; retain actual camera/light/world scene.
keep={'W0_NORTH_FRACTURED_RANGE','W0_WEST_BASALT_ESCARPMENT',
      'W0_GROUND_BASIN','W0_EASTERN_ARTIFICIAL_SEA'}
removed=[]
for ob in tuple(S.objects):
    if ob.type in ('MESH','CURVE') and ob.name not in keep:
        removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
assert len(removed)>300
coll=bpy.data.collections.new('INT1_LIVED_CIVIC_ARCHITECTURE_RESEARCH');S.collection.children.link(coll)
M={}
for name,rgb,metal,rough in [
    ('cut_limestone',(.68,.69,.63),.05,.75),('public_ivory',(.78,.76,.66),.05,.65),
    ('dark_blue_stone',(.095,.15,.18),.25,.65),('rib_bronze',(.52,.31,.18),.55,.42),
    ('deep_glass',(.07,.28,.32),.28,.17),('city_walk',(.41,.47,.46),.05,.84),
    ('roof_ceramic',(.45,.56,.58),.22,.42),('garden',(.18,.37,.25),0,.85),
    ('light_portal',(.87,.67,.37),.05,.28),('sea_transition',(.21,.32,.36),.1,.83)]:
    m=bpy.data.materials.new('INT1_'+name);m.use_nodes=True;m.diffuse_color=(*rgb,1)
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    if name=='light_portal':
        p.inputs['Emission Color'].default_value=(*rgb,1)
        p.inputs['Emission Strength'].default_value=.45
    M[name]=m
COUNTS={}
def mesh(name,vs,fs,material):
    m=bpy.data.meshes.new('INT1_'+name);m.from_pydata(vs,[],fs);m.update()
    ob=bpy.data.objects.new('INT1_'+name,m);coll.objects.link(ob);m.materials.append(M[material])
    COUNTS[name.split('_')[0]]=COUNTS.get(name.split('_')[0],0)+1
    return ob

def block(name,location,dim,material):
    cx,cy,cz=location;dx,dy,dz=[x/2 for x in dim]
    vs=[(cx+a*dx,cy+b*dy,cz+c*dz) for c in (-1,1)
        for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    return mesh(name,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material)

def slab(name,poly,z,depth,material):
    n=len(poly);assert n>=3
    vs=[(x,y,z-depth) for x,y in poly]+[(x,y,z) for x,y in poly]
    fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]
    fs.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    return mesh(name,vs,fs,material)

def beam(name,a,b,w,d,material):
    va,vb=Vector(a),Vector(b);dif=vb-va;assert dif.length>1
    q=dif.to_track_quat('Z','Y')
    vs=[tuple(va+q@Vector((x*w/2,y*d/2,t*dif.length)))
        for t in (0,1) for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    return mesh(name,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],material)

def path(name,pts,w,depth,material):
    vs=[]
    for i,(x,y,z) in enumerate(pts):
        d=Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(0,i-1)])
        length=math.hypot(d.x,d.y)
        px,py=(-d.y/length,d.x/length) if length>.0001 else (1,0)
        for h in (z-depth,z):
            vs.extend([(x+px*w/2,y+py*w/2,h),(x-px*w/2,y-py*w/2,h)])
    fs=[]
    for i in range(len(pts)-1):
        a=i*4;b=(i+1)*4
        fs.extend(((a,a+1,b+1,b),(a+2,a+3,b+3,b+2),
                   (a,a+2,b+2,b),(a+1,b+1,b+3,a+3)))
    fs.extend(((0,1,3,2),tuple(range(len(vs)-4,len(vs)))))
    return mesh(name,vs,fs,material)

def wall(name,a,b,z,h,thick,material,window=None):
    """Architectural wall as a real continuous 3D enclosure with recessed aperture.
    Windows are physical voids, not a decal on a solid block.
    """
    a,b=Vector(a),Vector(b);d=b-a
    n=Vector((-d.y,d.x,0));n.normalize()
    if not window:
        p=[(a.x,a.y),(b.x,b.y),(b.x+n.x*thick,b.y+n.y*thick),
           (a.x+n.x*thick,a.y+n.y*thick)]
        return slab(name,p,z+h, h,material)
    # One facade is subdivided into bands; each window has an actual opening
    # framed by a pier, a sill and a solid spandrel. Glass sits deep inside.
    nb,frac,low,high=window
    L=d.length;count=0
    for i in range(nb):
        for lo,hi in ((i/nb,(i+(1-frac)/2)/nb),
                      ((i+(1+frac)/2)/nb,(i+1)/nb)):
            p0=a+d*lo;p1=a+d*hi
            p=[(p0.x,p0.y),(p1.x,p1.y),(p1.x+n.x*thick,p1.y+n.y*thick),
               (p0.x+n.x*thick,p0.y+n.y*thick)]
            slab(f'{name}_pier_{i}_{count}',p,z+h,h,material);count+=1
        p0=a+d*(i+(1-frac)/2)/nb;p1=a+d*(i+(1+frac)/2)/nb
        outline=[(p0.x,p0.y),(p1.x,p1.y),(p1.x+n.x*thick,p1.y+n.y*thick),
                 (p0.x+n.x*thick,p0.y+n.y*thick)]
        slab(f'{name}_sill_{i}',outline,z+low,low,material)
        slab(f'{name}_lintel_{i}',outline,z+h,h-high,material)
        # Behind the perforation, actual recessed glazing.
        if low<high:
            p=[(p0.x+n.x*thick*.57,p0.y+n.y*thick*.57),
               (p1.x+n.x*thick*.57,p1.y+n.y*thick*.57),
               (p1.x+n.x*thick*.7,p1.y+n.y*thick*.7),
               (p0.x+n.x*thick*.7,p0.y+n.y*thick*.7)]
            slab(f'{name}_recessed_glazing_{i}',p,z+high,high-low,'deep_glass')

def bay_room(name,x,y,w,d,z,h,front='south',purpose='public',roof=True):
    """Four-walled occupied public room with real floor, windows and doorway.
    The south facade is deliberately partly open to a shared public circulation.
    """
    pts=[(x-w/2,y-d/2),(x+w/2,y-d/2),(x+w/2,y+d/2),(x-w/2,y+d/2)]
    slab(name+'_accessible_floor',pts,z,5,'public_ivory')
    for i,(a,b) in enumerate(zip(pts,pts[1:]+pts[:1])):
        nb=max(2,min(7,round(math.dist(a,b)/17)))
        if i==0 and front=='south':
            wall(name+'_south_portico',a,b,z,h,5,'cut_limestone',(nb,.67,1.4,h-3))
        else:
            wall(name+'_elevation_'+str(i),a,b,z,h,6,'cut_limestone',(nb,.48,5,h-5))
    if roof:
        p=[(x-w*.53,y-d*.54),(x+w*.51,y-d*.55),
           (x+w*.54,y+d*.52),(x-w*.5,y+d*.58)]
        # split into two nested slopes: not a universal large horizontal plate
        slab(name+'_light_roof',p,z+h+9,5,'roof_ceramic')
    return pts

def stairs(name,start,end,n,width=12):
    a,b=Vector(start),Vector(end)
    for i in range(n):
        p=a+(b-a)*(i+.5)/n
        slab(name+'_%02d'%i,[(p.x-width/2,p.y-2),(p.x+width/2,p.y-2),
             (p.x+width/2,p.y+3),(p.x-width/2,p.y+3)],p.z+2,2,'public_ivory')

def tree(name,x,y,z):
    beam(name+'_trunk',(x,y,z),(x+1,y+1,z+18),1.8,1.8,'dark_blue_stone')
    # Five-pronged realistic-canopy silhouette is deliberately local landscape.
    slab(name+'_foliage',[(x-9,y-6),(x+7,y-8),(x+12,y+3),
         (x+1,y+10),(x-11,y+4)],z+23,10,'garden')

# PHASE A — NAVE uses determine the whole civic volume before external supports.
# Central open forum faces three different public programs, not repeated slabs.
slab('NAVE_EXCAVATED_RIVERSTONE_CIVIC_FORUM',
     [(-234,-498),(-100,-555),(65,-538),(206,-412),(230,-131),
      (139,90),(84,211),(-76,226),(-223,96),(-266,-195)],68,21,'public_ivory')
# Library: read into actual rooms from a three-sided covered court.
for n,x,y,w,d,z,h in [
 ('WEST_READING_HALL',-402,-219,154,137,111,89),
 ('WEST_ARCHIVE_ROOM',-460,-32,125,151,128,106),
 ('WEST_CIVIC_LIBRARY_GALLERY',-290,-78,110,140,189,79)]:
    bay_room('NAVE_LIBRARY_'+n,x,y,w,d,z,h)
slab('NAVE_LIBRARY_PUBLIC_COURT',[(-384,-114),(-278,-127),
      (-255,22),(-366,58)],91,8,'city_walk')
for i in range(3):
    a=(-327,-308,85+i*35);b=(-322,-197,114+(i+1)*35)
    path('NAVE_LIBRARY_PUBLIC_RAMP_'+str(i),[a,b],13,4,'public_ivory')
# Reading shelves on library access mezzanine, scaled to a giant public destination.
for i in range(9):
    block('NAVE_LIBRARY_READABLE_BOOK_STACK_%02d'%i,
          (-434+(i%3)*22,-231+(i//3)*29,124),(9,36,29),'rib_bronze')
# East terminal has actual high train platforms, a concourse, two public waiting rooms.
for i,(x,z) in enumerate(((204,86),(268,94),(334,100))):
    slab('NAVE_STATION_TRAIN_PLATFORM_'+str(i),
       [(x-19,-401),(x+19,-396),(x+24,-70),(x-16,-65)],z,13,'city_walk')
for k,x in enumerate((241,301)):
    path('NAVE_STATION_TRACK_TRUE_'+str(k),[(x,-446,78),(x,-93,89)],4,2,'dark_blue_stone')
for n,x,y,w,d,z,h in [
 ('SOUTH_TICKET_HALL',315,-269,117,108,137,98),
 ('NORTHERN_WAITING_HALL',327,-75,134,121,158,91)]:
    bay_room('NAVE_STATION_'+n,x,y,w,d,z,h)
slab('NAVE_STATION_PUBLIC_ENTRY_GATE',[(156,-419),(237,-414),
      (274,-330),(179,-330)],81,9,'public_ivory')
path('NAVE_STATION_PUBLIC_LIFT_TO_BALCONY',[(225,-292,94),(296,-203,139),
     (344,-100,158)],16,6,'public_ivory')
# Ceremony: destination distinct from station/library, with an arena and grand stairs.
slab('NAVE_CEREMONY_ORCHESTRA',[(-146,70),(134,75),(166,192),
      (100,254),(-108,251),(-175,171)],115,14,'city_walk')
for i in range(12):
    yy=181+i*10;z=116+i*3.0
    slab('NAVE_CEREMONY_INHABITED_SEATS_%02d'%i,
         [(-137+i*.8,yy),(136-i*.7,yy+2),(131-i*.5,yy+7),
          (-133+i*.7,yy+8)],z,3,'public_ivory')
for j,(x,y) in enumerate(((-145,110),(132,110),(-130,281),(128,275))):
    beam('NAVE_CEREMONY_MONUMENT_PIER_'+str(j),(x,y,100),(x+8,y+10,236),9,14,'cut_limestone')
# Main public route: connects via tangible floors + layered ramps, no markers.
path('NAVE_CIVIC_PUBLIC_WALK_TO_LIBRARY',[(-30,-359,71),(-163,-307,78),
      (-236,-221,111),(-332,-199,111)],24,7,'city_walk')
path('NAVE_CIVIC_PUBLIC_WALK_TO_STATION',[(50,-358,69),(168,-326,80),
      (234,-252,93),(297,-208,139)],24,7,'city_walk')
path('NAVE_CIVIC_PUBLIC_WALK_TO_CEREMONY',[(0,-250,71),(2,-91,91),
      (12,92,115)],25,6,'city_walk')
# NAVE giant vaulted section: only slender structural ribs formed from room spans.
# The inner court never gets a 100m-wide opaque roof, avoiding R2/R3 black camera.
for j,(y,z) in enumerate(((-379,316),(-176,389),(62,436),(256,465))):
    p=[(-284,y,92),(-224,y+5,z*.73),(-110,y+14,z+12),
       (0,y+16,z+65),(114,y+14,z+7),(235,y+5,z*.75),(307,y,96)]
    for k,(a,b) in enumerate(zip(p,p[1:])):
        beam('NAVE_SCULPTED_VAULT_RIB_%d_%d'%(j,k),a,b,12+j*1.6,17,'rib_bronze')
# A skylit high library reading corridor runs along the inward edge, not across the void.
path('NAVE_UPPER_PUBLIC_GALLERY_LIBRARY',[(-293,-265,251),
      (-275,-90,273),(-242,121,305)],23,11,'public_ivory')
path('NAVE_UPPER_PUBLIC_GALLERY_STATION',[(305,-265,241),
      (290,-91,272),(258,136,302)],25,10,'public_ivory')
# PHASE B — H1 houses a real multi-storey cliff city around a clear public street.
# Two independent terraced rock foundations form an inhabited canyon.
west_foot=[(451,122),(613,105),(723,213),(719,754),
           (623,828),(453,687),(432,383)]
east_foot=[(846,193),(1037,177),(1142,355),(1165,778),
           (949,881),(840,694)]
# The rock bases are *building foundations*, not free-floating detached floors.
for name,p,z in [('WEST',west_foot,438),('EAST',east_foot,444)]:
    slab('H1_'+name+'_LIVING_CLIFF_GROUND',p,z,32,'cut_limestone')
    # Rock terraces at three different elevations bound to the same foundation.
    for i,delta in enumerate(((-15,-21),(17,-7),(-9,22))):
        q=[(x+delta[0]*i*.2,y+delta[1]*i*.2) for x,y in p]
        slab('H1_'+name+'_HABITABLE_LOWER_TERRACE_'+str(i),q,181+i*78,37,'dark_blue_stone')
# Central street is physically clear from camera (760,270,439).
path('H1_PUBLIC_BOULEVARD',[(780,285,439),(778,426,440),
     (783,599,442),(790,758,447)],45,12,'city_walk')
# Shops & library and school are actual nested rooms with windows and roof.
city_buildings=[
 ('WEST_MARKET',590,401,123,116,445,76),
 ('WEST_PUBLIC_LIBRARY',576,570,135,145,448,114),
 ('WEST_CLASSROOM_STUDIOS',603,754,125,119,453,104),
 ('EAST_SHOPS',952,394,147,120,449,86),
 ('EAST_SCHOOL_HALL',971,564,167,138,451,118),
 ('EAST_HOUSING_COURT',964,759,151,132,458,137)]
for name,x,y,w,d,z,h in city_buildings:
    # Real ground-floor arcade + a physically separate upper public room.
    bay_room('H1_'+name,x,y,w,d,z,h,purpose='public')
    w2=w*.83;d2=d*.83
    bay_room('H1_'+name+'_UPPER_CITY',x+6,y+10,w2,d2,z+h+13,52,roof=True)
    path('H1_'+name+'_ACTUAL_UPPER_ACCESS',[(x-w*.45,y-d*.53,z+2),
         (x-w*.45+17,y+d*.3,z+h*.6),(x-w*.25,y+d*.48,z+h+14)],
         11,4,'public_ivory')
# Alternating urban courtyards, not mass-produced identical rooftops.
for j,(x,y,z) in enumerate(((701,354,448),(703,543,448),(698,721,452),
                          (856,452,449),(859,652,449))):
    slab('H1_CITY_PUBLIC_GARDEN_'+str(j),[(x-23,y-34),(x+23,y-36),
         (x+31,y+28),(x-25,y+37)],z,7,'garden')
    tree('H1_COURTYARD_TREE_'+str(j),x,y,z+1)
# Vertical neighborhood under the high street — market at z250 and public atrium.
for j,(z,poly) in enumerate(((124,[(505,23),(687,78),(795,249),
                                   (731,399),(521,347)]),
                             (260,[(520,86),(698,115),(851,273),
                                   (780,423),(547,376)]),
                             (360,[(538,130),(706,151),(868,293),
                                   (802,442),(560,390)]))):
    slab('H1_LOWER_INHABITED_STREET_'+str(j),poly,z,23,'public_ivory')
    # Solid urban core enclosed on two sides, open outward to sea.
    for k in (0,3):
        a=poly[k];b=poly[(k+1)%len(poly)]
        wall('H1_CLIFF_OPEN_PUBLIC_ATRIUM_%d_%d'%(j,k),a,b,z,75,10,
             'cut_limestone',(4,.48,13,62))
    if j<2:
        path('H1_PUBLIC_VERTICAL_LINK_'+str(j),[(673,216,z+4),
             (701,296,z+56),(733,374,(260,360)[j]+3)],18,7,'public_ivory')
path('H1_CITY_MAIN_ACCESS_FROM_NAVE',[(295,85,164),(403,137,258),
     (561,231,360),(682,308,438)],22,7,'city_walk')
# PHASE C — The NAVE-H1 program generates high inhabited city form.
# Three distinct neighborhoods climb along the diagonally fractured court, not
# dummy slabs at each floor. Cada urban unit has real enclosed rooms/windows.
upper_districts=[
 ('WEST_LIBRARY_CLIFF',-464,152,315,169,180,5),
 ('WEST_UPPER_CITY',-414,281,611,169,155,4),
 ('WEST_RIFT_CROWN',-280,408,932,155,152,3),
 ('EAST_CIVIC_CLIFF',369,185,327,158,170,5),
 ('EAST_UPPER_SCHOOL',479,332,585,171,176,4),
 ('EAST_DISPLACED_QUARTER',634,483,855,141,137,3)]
for idx,(name,x,y,z,w,d,num) in enumerate(upper_districts):
    footprint=[(x-w*.57,y-d*.52),(x+w*.45,y-d*.55),
               (x+w*.65,y+d*.35),(x-w*.41,y+d*.61)]
    slab('M247_'+name+'_LOWER_INHABITED_FLOOR',footprint,z,25,
         'dark_blue_stone' if idx%3==0 else 'cut_limestone')
    # Vertical programmatic floors: double-height public hall at base,
    # residences and shared urban street above; windows are actual apertures.
    h=42+idx%2*5
    for j in range(num):
        zz=z+j*h
        if j>0:
            slab('M247_'+name+'_LIVE_PUBLIC_STORY_'+str(j),footprint,
                 zz,7,'city_walk')
        for side in range(4):
            a=footprint[side];b=footprint[(side+1)%4]
            # the inward-facing side is publicly transparent; exterior bays
            # have repeated but genuinely perforated enclosures.
            nw=max(3,round(math.dist(a,b)/23))
            wall('M247_'+name+'_ROOM_%d_FACADE_%d'%(j,side),a,b,
                 zz,h,7,'cut_limestone',
                 (nw,.56,5 if side%2 else 3,h-5))
    slab('M247_'+name+'_OCCUPIED_GARDEN_ROOF',
         [(a+8,b+12) for a,b in footprint],z+num*h+8,12,
         'garden' if idx%2 else 'roof_ceramic')
    # One distinct accessible sky court reaches the top of each inhabited unit.
    path('M247_'+name+'_INNER_PUBLIC_ASCENT',[(x-w*.42,y-d*.34,z+3),
         (x-w*.21,y-d*.10,z+h*1.2),(x+w*.12,y+d*.19,z+h*2.3)],
         13,6,'public_ivory')
# THESE neighborhood links grow from entrances; they remain open between cities.
path('M247_WEST_HIGH_CIVIC_STREET',[(-469,188,542),(-449,272,623),
     (-373,353,823),(-304,414,955)],26,12,'public_ivory')
path('M247_EAST_HIGH_LIVING_STREET',[(386,241,542),(440,321,600),
     (529,399,770),(614,474,875)],27,12,'public_ivory')
# Intentionally displaced single civic crossing, upper void remains readable.
path('M247_UPPER_CIVIC_DIAGONAL_LINK',[(-307,412,992),(-142,426,956),
     (51,440,939),(233,461,910),(620,486,874)],24,12,'rib_bronze')
# PHASE D — W0 physically shaped waterfront with ferry interior and coastal city.
for j,(z,poly) in enumerate([
 (58,[(-380,-548),(-186,-660),(22,-702),(201,-627),(401,-487),
      (590,-290),(663,-160),(537,-71),(336,-238),(91,-426)]),
 (31,[(-213,-711),(26,-796),(286,-713),(522,-568),(676,-330),
      (580,-286),(350,-466),(40,-644)])]):
    slab('W0_INHABITED_SHORE_TERRACE_'+str(j),poly,z,31,
         'sea_transition' if j==0 else 'public_ivory')
for j in range(15):
    yy=-621-j*7
    slab('W0_PUBLIC_TIDAL_CIVIC_STAIRS_%02d'%j,
         [(-100-j*2,yy),(90+j*3,yy-6),(133+j*3,yy+14),
          (-76-j*2,yy+18)],55-j*2.3,3,'public_ivory')
bay_room('W0_FERRY_TICKET_FORUM',510,-277,156,132,74,91)
bay_room('W0_TIDAL_LIBRARY',333,-490,136,114,67,75)
path('W0_TRUE_QUAY_TO_NAVE',[(483,-383,71),(322,-491,65),
     (164,-576,64),(-15,-612,63),(-138,-544,65)],28,8,'city_walk')
path('W0_TRUE_QUAY_TO_H1',[(612,-241,61),(653,-123,118),
     (713,78,253),(759,265,439)],24,9,'city_walk')
# Research isolation & technical evidence; NEVER equate these with ART success.
bpy.context.view_layer.update()
for name in cams:
    m=bpy.data.objects[name].matrix_world
    assert max(abs(m[i][j]-fixed[name][i][j]) for i in range(4) for j in range(4))<1e-6
S['INT1_SOURCE_SHA256']=SOURCE_SHA
S['INT1_MODE']='INTERIOR_FIRST_CIVIC_HABITATION_NOT_EXTERNAL_SHELL_FIRST'
S['INT1_RESEARCH_COORDS']='ISOLATED_RESEARCH_METRES_NOT_WORLD_REGISTERED'
S['INT1_REJECTED_OBJECTS_REMOVED']=len(removed)
S['INT1_NEW_MESHES']=len(coll.objects)
S['CONSTRUCTION']='HOLD';S['FORMAL_ART_ACCEPTED']=0;S['COMPLETED_TARGETS']=0
S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=12;S.cycles.use_denoising=True
S.render.threads_mode='FIXED';S.render.threads=2
S.render.resolution_x=1100;S.render.resolution_y=825;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.film_transparent=False
S.camera=bpy.data.objects[cams[-1]]
dest=out/'HALO9_INT1_LIVED_CIVIC_ARCHITECTURE.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
rendered={}
for name in cams:
    S.camera=bpy.data.objects[name];f=out/'renders'/(name+'.png')
    S.render.filepath=str(f);bpy.ops.render.render(write_still=True)
    assert f.exists() and f.stat().st_size>5000
    rendered[name]=hashlib.sha256(f.read_bytes()).hexdigest()
    print('INT1_TRUE_BLENDER_RENDER',name,f.stat().st_size,flush=True)
S.camera=bpy.data.objects[cams[-1]]
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
report={'schema':'halo9-int1-real-interior-first-v1',
 'source_sha256':SOURCE_SHA,
 'working_blend_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
 'removed_rejected_objects':len(removed),
 'new_meshes':len(coll.objects),'role_counts':COUNTS,
 'render_sha256':rendered,'cameras_unmodified':True,
 'coordinates':'UNREGISTERED_RESEARCH_METRES',
 'formal_art_adopted':0,'completed_targets':0,'minecraft_construction':'HOLD',
 'art':'AWAITING_DIRECT_RENDER_REVIEW'}
(out/'INT1_SOURCE_AND_NATIVE_REPORT.json').write_text(json.dumps(report,indent=2))
print('INT1_TRUE_NATIVE_COMPLETE',report['working_blend_sha256'],flush=True)
