"""CELESTIAL HALO-9 INT3 — one occupied diagonal fault city.
New sculptural strategy, not INT2/R3 shape continuation.
One continuous asymmetrical civic seam connects NAVE, H1, the split sky district
and W0 coastline; two thick urban escarpments are *inhabited*, not empty towers.
All positions are non-registered study metres. No Minecraft writing/adoption.
Native Blender background geometry authoring (NOT mouse/GUI hand-sculpting).
"""
import bpy, math, sys, json, hashlib
from pathlib import Path
from mathutils import Vector

argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(argv[argv.index('--output')+1])
out.mkdir(parents=True,exist_ok=True)
renderdir=out/'renders';renderdir.mkdir(exist_ok=True)
source=Path(bpy.data.filepath)
SOURCE_SHA='422a60469123500e7eb4f5be886ed390665c9daadad3ad8c5e8a3b9699443100'
assert source.name=='INT3_SOURCE.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()==SOURCE_SHA
scene=bpy.context.scene
assert scene['CONSTRUCTION']=='HOLD'
assert scene['COMPLETED_TARGETS']==0 and scene['FORMAL_ART_ACCEPTED']==0
cameras=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
fixed={n:bpy.data.objects[n].matrix_world.copy() for n in cameras}
existing_landscape={'W0_NORTH_FRACTURED_RANGE','W0_WEST_BASALT_ESCARPMENT',
                    'W0_GROUND_BASIN','W0_EASTERN_ARTIFICIAL_SEA'}
deleted=0
for ob in list(scene.objects):
    if ob.type in {'MESH','CURVE'} and ob.name not in existing_landscape:
        bpy.data.objects.remove(ob,do_unlink=True);deleted+=1
assert deleted==6439,('unexpected INT1 research parent',deleted)
collection=bpy.data.collections.new('INT3_ONE_OCCUPIED_FAULT_CITY_RESEARCH')
scene.collection.children.link(collection)
materials={}
for name,rgb,metal,rough in [
 ('pearl_rock',(.72,.69,.61),.19,.68),
 ('ocher_rock',(.49,.45,.41),.28,.68),
 ('canyon_recess',(.12,.18,.21),.25,.81),
 ('civic_cream',(.83,.76,.63),.06,.70),
 ('copper',(.44,.31,.20),.65,.48),
 ('ceramic',(.22,.43,.47),.39,.40),
 ('translucent',(.10,.30,.37),.32,.19),
 ('green',(.21,.34,.25),.0,.81),
 ('white_light',(.96,.75,.40),.09,.31)]:
    m=bpy.data.materials.new('INT3_'+name)
    m.use_nodes=True
    m.diffuse_color=(*rgb,1)
    bsdf=m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(*rgb,1)
    bsdf.inputs['Metallic'].default_value=metal
    bsdf.inputs['Roughness'].default_value=rough
    if name=='white_light':
        bsdf.inputs['Emission Color'].default_value=(*rgb,1)
        bsdf.inputs['Emission Strength'].default_value=0.6
    materials[name]=m

count={}
def mesh(name,vs,faces,mat,second=None):
    md=bpy.data.meshes.new('INT3_'+name)
    md.from_pydata(vs,[],faces);md.update()
    obj=bpy.data.objects.new('INT3_'+name,md)
    collection.objects.link(obj)
    md.materials.append(materials[mat])
    if second:md.materials.append(materials[second])
    count[name.split('_')[0]]=count.get(name.split('_')[0],0)+1
    return obj

def prism(name,outline,bottom,top,material):
    assert top>bottom and len(outline)>=3
    n=len(outline)
    vs=[(x,y,bottom) for x,y in outline]+[(x,y,top) for x,y in outline]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    return mesh(name,vs,faces,material)

def track(name,path,w,depth,material):
    vs=[]
    for i,(x,y,z) in enumerate(path):
        a=Vector(path[max(i-1,0)]);b=Vector(path[min(i+1,len(path)-1)])
        d=b-a;length=math.hypot(d.x,d.y)
        nx,ny=((-d.y/length,d.x/length) if length>1e-5 else (1.,0.))
        vs.extend(((x+nx*w/2,y+ny*w/2,z-depth),
                   (x-nx*w/2,y-ny*w/2,z-depth),
                   (x+nx*w/2,y+ny*w/2,z),
                   (x-nx*w/2,y-ny*w/2,z)))
    fs=[(0,2,3,1),tuple(range(len(vs)-4,len(vs)))]
    for i in range(len(path)-1):
        a=4*i;b=a+4
        fs.extend(((a,a+1,b+1,b),(a+2,b+2,b+3,a+3),
                   (a,a+2,b+2,b),(a+1,b+1,b+3,a+3)))
    return mesh(name,vs,fs,material)

# Real spatial path from the NAVE fixed camera through H1; interpolated in
# *study* coordinate space, not assumed official terrain anchoring.
stations=[
 (-870,-195,185,515,420,520),
 (-720,-135,195,690,480,780),
 (-540,-25,185,880,530,960),
 (-360,15,178,1010,520,1060),
 (-130,120,178,1110,580,1160),
 (100,595,173,1280,600,1280),
 (270,760,162,1350,555,1420),
 (510,792,169,1230,610,1530),
 (750,834,195,1320,575,1660),
 (970,932,214,1510,590,1690),
 (1190,1060,220,1350,535,1540),
 (1430,1120,225,920,475,1070)]
def station(y):
    for i in range(len(stations)-1):
        a,b=stations[i:i+2]
        if a[0]<=y<=b[0]:
            t=(y-a[0])/(b[0]-a[0])
            return tuple(a[j]+(b[j]-a[j])*t for j in range(1,6))
    a=stations[0] if y<stations[0][0] else stations[-1]
    return a[1:]

# One seamless shell on each side. Profiles are architectural cross sections
# composed of ground, NAVE cliff, upper inhabited section and displaced roof.
# This is an oriented, eroded occupied fault, not two cylindrical rock lobes.
bank_objects={}
for side,bank,material in [(-1,'WEST','pearl_rock'),(1,'EAST','ocher_rock')]:
    verts=[]
    segments=10
    for k,(y,cx,gap,roof,width,_) in enumerate(stations):
        roof=roof*(.94 if bank=='WEST' else 1.06)
        for j in range(segments):
            # Actual inner civic wall near the open public axis, with thick
            # 3D city hinterland and a jagged displaced high-level crest.
            d=(gap+[
                8,20,34,56,101,172,335,width-50,width+18,width-5][j])
            frac=[.01,.12,.28,.46,.64,.83,1.0,.96,.42,-.025][j]
            z=40+(roof-40)*frac
            if j in (5,6,7):
                z+=37*math.sin(.9*k+side*1.4+j)+17*math.sin(2.3*k-j)
            else:
                z+=10*math.sin(1.4*k+j)
            # Different y-facing cliff alignments keep the double mass
            # chiral without displacing the fixed camera corridor.
            x=cx+side*d+side*22*math.sin(k*.7+j*.91)
            verts.append((x,y,z))
    faces=[tuple(reversed(range(segments))),
           tuple(range((len(stations)-1)*segments,len(stations)*segments))]
    for k in range(len(stations)-1):
        for j in range(segments):
            a=k*segments+j;b=k*segments+(j+1)%segments
            faces.append((a,b,b+segments,a+segments))
    body=mesh('M247_'+bank+'_OCCUPIED_ESCARPMENT',verts,faces,material,'canyon_recess')
    bank_objects[bank]=body

# Cut city-scale *angular* public rooms from the inner face: not circular
# portholes or cosmetic windows on an uninhabited pillar.
def angular_cutter(label,xnear,xfar,y,z,r_y,r_z):
    # Offset and intentionally non-symmetric Y/Z profile.
    section=[
        (y-r_y,z-r_z*.68),(y-r_y*.89,z+r_z*.26),
        (y-r_y*.44,z+r_z*.96),(y+r_y*.20,z+r_z),
        (y+r_y*.81,z+r_z*.54),(y+r_y,z-r_z*.40),
        (y+r_y*.28,z-r_z),(y-r_y*.51,z-r_z*.87)]
    n=len(section)
    vs=[(xnear,yy,zz) for yy,zz in section]+[(xfar,yy,zz) for yy,zz in section]
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    fs.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    md=bpy.data.meshes.new('CUT_'+label);md.from_pydata(vs,[],fs);md.update()
    cutter=bpy.data.objects.new('TEMP_CUT_'+label,md)
    scene.collection.objects.link(cutter)
    return cutter

carves=[]
openings=[
 ('WEST','NAVE_LIBRARY',-165,145,135,93,205),
 ('EAST','NAVE_STATION',-165,154,137,103,225),
 ('WEST','NAVE_HIGH_ARCHIVE',60,424,146,107,201),
 ('EAST','NAVE_CEREMONY',75,354,132,111,227),
 ('WEST','H1_MARKET',408,478,138,103,201),
 ('EAST','H1_PUBLIC_SCHOOL',542,534,154,115,235),
 ('WEST','H1_ELEVATED_READING',728,766,147,119,212),
 ('EAST','H1_HOUSE_ATRIUM',739,882,142,110,214),
 ('WEST','UPPER_CIVIC_GARDEN',1072,1170,149,131,232),
 ('EAST','SKY_MARKET',1050,1245,136,124,224)
]
for bank,label,y,z,half_y,half_z,inset in openings:
    cx,gap,roof,width,_=station(y)
    side=-1 if bank=='WEST' else 1
    inner=cx+side*(gap+42)
    # Cutter physically crosses the canyon-side vertical facade and reaches
    # hundreds of metres into the inhabited rock (capped at current width).
    near=inner-side*105
    far=inner+side*inset
    cutter=angular_cutter(label,near,far,y,z,half_y,half_z)
    obj=bank_objects[bank]
    mod=obj.modifiers.new('INT3_REAL_CUT_'+label,'BOOLEAN')
    mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    carves.append(label)

# A gigantic diagonal β sky rupture, not a freestanding bar. A displaced
# occupied neighbourhood is a *different* asymmetric high-altitude body
# that emerges from upper east cliff and crosses the fault far behind H1.
upper_levels=[
 (790,1015,675,260,135),
 (890,1047,825,312,157),
 (1110,1148,1030,348,194),
 (1260,1140,1264,294,165)]
def prism_loft(name,sections,material):
    # Each is a six-sided lived-in terrace, NOT a roof panel.
    rings=[]
    for y,x,z,rx,ry in sections:
        rings.append([(x-rx*.92,y-ry*.59,z-30),
          (x-rx*.25,y-ry*.94,z+29),
          (x+rx*.55,y-ry*.75,z+66),
          (x+rx,y+ry*.20,z+17),
          (x+rx*.49,y+ry*.87,z-18),
          (x-rx*.81,y+ry*.54,z+22)])
    n=6;vs=[v for ring in rings for v in ring]
    fs=[tuple(reversed(range(n))),tuple(range((len(rings)-1)*n,len(rings)*n))]
    for k in range(len(rings)-1):
        for j in range(n):
            a=k*n+j;b=k*n+(j+1)%n
            fs.append((a,b,b+n,a+n))
    return mesh(name,vs,fs,material)
upper=prism_loft('M247_BETA_DISPLACED_INHABITED_SKY_CITY',upper_levels,'pearl_rock')
# carve real public sky atrium; not a painted opening
c=angular_cutter('SKY_DISPLACED_ATRIUM',785,1210,1062,1038,130,92)
m=upper.modifiers.new('INT3_DISPLACED_ATRIUM','BOOLEAN')
m.operation='DIFFERENCE';m.solver='EXACT';m.object=c
bpy.context.view_layer.objects.active=upper
bpy.ops.object.select_all(action='DESELECT');upper.select_set(True)
bpy.ops.object.modifier_apply(modifier=m.name)
bpy.data.objects.remove(c,do_unlink=True);carves.append('SKY_DISPLACED_ATRIUM')

# Different real civic destinations, not the same window-covered box repeated.
def civic_room(label,x,y,z,w,d,h,opening_side,material):
    # Six-sided civic volume with physically open public entrance.
    shape=[(x-w*.53,y-d*.32),(x-w*.18,y-d*.56),
           (x+w*.48,y-d*.43),(x+w*.60,y+d*.26),
           (x+w*.04,y+d*.57),(x-w*.53,y+d*.31)]
    prism(label+'_FLOOR',shape,z-9,z,'civic_cream')
    for i in range(6):
        if i==opening_side:continue
        a=Vector(shape[i]);b=Vector(shape[(i+1)%6])
        v=(b-a);ln=v.length
        n=Vector((-v.y/ln,v.x/ln))
        wall=[tuple(a),tuple(b),tuple(b+n*7),tuple(a+n*7)]
        prism(label+'_INHABITABLE_WALL_'+str(i),wall,z,z+h,material)
    # Independent non-flat roof with central skylight and separated folds
    # (not one gigantic opaque plate)
    roof1=[(x-w*.47,y-d*.43),(x+w*.03,y-d*.48),
           (x+w*.16,y+d*.10),(x-w*.28,y+d*.32)]
    prism(label+'_PARTIAL_CLERESTORY',roof1,z+h+9,z+h+18,'ceramic')
    prism(label+'_REAR_SOLID_READING_ROOF',[
        (x-w*.16,y+d*.03),(x+w*.49,y-d*.25),
        (x+w*.53,y+d*.32),(x-w*.06,y+d*.49)],z+h+5,z+h+14,'pearl_rock')
    return shape

# Accessible central NAVE forum and three distinct destinations.
prism('NAVE_CIVIC_FORUM',[
 (-182,-498),(30,-529),(183,-451),(245,-236),
 (181,-17),(36,85),(-181,1),(-228,-190)],67,84,'civic_cream')
civic_room('NAVE_LIBRARY_CARVED_READING_ROOM',-265,-171,138,
           162,141,93,3,'canyon_recess')
civic_room('NAVE_STATION_MAIN_CONCOURSE',327,-172,144,
           178,166,88,5,'ocher_rock')
civic_room('NAVE_CEREMONY_LIGHT_AUDITORIUM',389,58,354,
           182,172,115,5,'pearl_rock')
# Real tracks and platforms within the same carved railway opening.
track('NAVE_STATION_PUBLIC_PLATFORM',[(258,-422,102),
      (289,-274,111),(317,-117,123),(354,39,151)],35,12,'civic_cream')
for k,x in enumerate((262,294,327)):
    track('NAVE_STATION_ACTUAL_TRACK_'+str(k),[
      (x,-459,91),(x+13,-228,101),(x+31,-74,107)],3,2,'copper')
prism('NAVE_LIBRARY_STUDY_MEZZANINE',[
 (-376,-223),(-285,-267),(-207,-165),
 (-217,-26),(-339,-8),(-390,-116)],232,244,'civic_cream')
for i,(x,y) in enumerate([(-320,-181),(-306,-130),(-273,-157),(-249,-111)]):
    prism('NAVE_ARCHIVE_PHYSICAL_SHELF_'+str(i),[
       (x-7,y-14),(x+6,y-15),(x+8,y+14),(x-7,y+12)],
        143,166+(i%2)*6,'copper')
track('NAVE_TO_LIBRARY_ENTRY',[(14,-366,89),(-64,-271,105),
      (-162,-204,132),(-231,-166,140)],21,8,'white_light')
track('NAVE_PUBLIC_TO_STATION',[(57,-372,84),(152,-323,102),
      (254,-240,137),(328,-183,146)],23,9,'civic_cream')
track('NAVE_TO_CEREMONY',[(35,-225,91),(115,-80,171),
      (199,8,261),(304,67,354)],23,9,'civic_cream')

# The fault's *inhabited* cross section is revealed in external civic routes
# and cantilevered reading rooms rather than residential box repetition.
for label,x,y,z,w,d,h,opens,mat in [
 ('H1_MARKET',534,410,475,176,128,97,2,'ocher_rock'),
 ('H1_PUBLIC_SCHOOL',1090,531,523,195,147,117,5,'canyon_recess'),
 ('H1_NORTH_PUBLIC_LIBRARY',559,724,755,167,139,100,2,'pearl_rock'),
 ('H1_CROSSRIFT_RESIDENTIAL_COMMUNITY',1185,737,874,171,131,91,4,'canyon_recess'),
 ('M247_WEST_SKY_LIBRARY',602,1050,1160,173,145,93,2,'ocher_rock'),
 ('M247_EAST_SKY_MARKET',1417,1025,1253,150,144,115,4,'pearl_rock'),
 ]:
    civic_room(label,x,y,z,w,d,h,opens,mat)

# The protected H1 human camera at (760,270,439) looks north into actual
# open public life. No foreground mass is allowed in its sight corridor.
track('H1_OPEN_PUBLIC_BOULEVARD',[(757,262,445),(760,372,465),
 (781,511,509),(810,667,602),(839,812,723)],42,14,'civic_cream')
track('H1_MARKET_PUBLIC_BRANCH',[(765,394,467),(691,398,472),
  (600,407,479)],22,9,'white_light')
track('H1_SCHOOL_PUBLIC_BRANCH',[(788,501,510),(879,526,517),
 (1027,537,529)],23,10,'civic_cream')
track('H1_PUBLIC_VERTICAL_CITY_ASCENT',[(811,615,549),
 (791,674,642),(700,714,725),(607,737,766)],27,12,'copper')
track('H1_HIGH_RESIDENTIAL_CROSSING',[(691,737,772),
 (848,751,808),(996,751,853),(1120,757,877)],32,15,'pearl_rock')
track('M247_DISPLACED_CIVIC_SPINE',[(820,774,839),
 (872,861,938),(977,990,1098),(1107,1114,1269)],34,19,'civic_cream')

# Medium-scale inhabited facets cut into the cliff sides, not free-standing
# thin aerial shelves. Each destination has a physical wall/floor ratio.
for i,(x,y,z) in enumerate([
   (-315,-35,332),(386,-11,318),(245,290,558),
   (471,389,624),(1101,688,705),(679,904,1004),
   (1227,938,1150)]):
    footprint=[(x-70,y-39),(x-26,y-75),(x+49,y-68),
        (x+82,y+17),(x+19,y+74),(x-57,y+46)]
    prism('M247_HABITABLE_FACET_'+str(i),footprint,z-20,z,'pearl_rock' if i%2 else 'ocher_rock')
    # Elevated garden inhabitation is distinct at every point
    q=[(x-26,y-25),(x+25,y-29),(x+33,y+23),(x-21,y+31)]
    prism('M247_LOCAL_INHABITED_GARDEN_'+str(i),q,z,z+6,'green')

# W0 is a formed buttress and sea-access city, not a distant triangle.
prism('W0_INTEGRATED_MARINE_BUTTRESS',[
 (-443,-628),(-198,-741),(62,-822),(281,-768),
 (491,-627),(555,-470),(309,-495),(52,-545)],-24,55,'ocher_rock')
prism('W0_SUNKEN_COASTAL_CONCOURSE',[
 (-273,-627),(-22,-698),(247,-679),
 (403,-590),(311,-463),(91,-514)],55,76,'civic_cream')
civic_room('W0_TIDAL_LIBRARY',-83,-589,83,172,114,83,1,'canyon_recess')
civic_room('W0_FERRY_PUBLIC_HALL',352,-536,91,165,142,84,4,'pearl_rock')
track('W0_TIDAL_CIVIC_FRONTAGE',[
 (-229,-679,61),(-72,-682,62),(118,-665,69),
 (303,-603,79),(457,-501,88)],36,13,'white_light')
track('W0_TERRAIN_TO_NAVE',[
 (187,-624,75),(143,-552,84),(68,-473,85),
 (4,-373,87)],25,9,'civic_cream')
track('W0_MARINE_TO_H1_HIGH_TRANSIT',[
 (436,-535,91),(488,-333,152),(579,-151,251),
 (674,95,346),(753,270,446)],28,12,'pearl_rock')

# The large empty fault should be recognizable from aerial, but its crossings
# are both usable public destinations in the connected elevated structure.
track('M247_BETA_PUBLIC_SKY_CROSSING',[
 (534,898,1118),(721,959,1190),(960,1041,1261),
 (1166,1084,1276)],43,27,'copper')
track('M247_CIVIC_FISSURE_PEDESTRIAN_ATRIUM',[
 (463,578,768),(648,716,858),(806,867,1009),
 (1021,1026,1163)],22,9,'civic_cream')

# Small warm lights in actual carved interiors; not a disguise for silhouette.
for j,(x,y,z) in enumerate([
  (-263,-145,185),(317,-177,196),(385,50,411),
  (538,410,547),(1104,540,601),(561,731,833),
  (1174,739,966),(630,1053,1250),(1420,1026,1360)]):
    light=bpy.data.lights.new('INT3_PUBLIC_OCCUPIED_LIGHT_'+str(j),'POINT')
    light.energy=225000;light.shadow_soft_size=62
    ob=bpy.data.objects.new('INT3_PUBLIC_OCCUPIED_LIGHT_'+str(j),light)
    collection.objects.link(ob);ob.location=(x,y,z)

# Mandatory evidence boundaries.
bpy.context.view_layer.update()
for n,m in fixed.items():
    c=bpy.data.objects[n].matrix_world
    assert max(abs(c[i][j]-m[i][j]) for i in range(4) for j in range(4))<1e-6
scene['INT3_PARENT_SHA256']=SOURCE_SHA
scene['INT3_INHABITED_FAULT']='ONE_CHIRAL_SCULPTED_OCCUPIED_CIVIC_FISSURE'
scene['INT3_REJECTED_INT1_REMOVED']=deleted
scene['INT3_RESEARCH_COORDS']='UNREGISTERED_METRES'
scene['CONSTRUCTION']='HOLD'
scene['COMPLETED_TARGETS']=0;scene['FORMAL_ART_ACCEPTED']=0
scene.render.engine='CYCLES';scene.cycles.device='CPU'
scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=1100;scene.render.resolution_y=825
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.camera=bpy.data.objects[cameras[-1]]
saved=out/'HALO9_INT3_OCCUPIED_TECTONIC_CIVIC_SEAM.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(saved),compress=True)
hashes={}
for n in cameras:
    scene.camera=bpy.data.objects[n]
    png=renderdir/(n+'.png');scene.render.filepath=str(png)
    bpy.ops.render.render(write_still=True)
    assert png.stat().st_size>5000
    hashes[n]=hashlib.sha256(png.read_bytes()).hexdigest()
    print('INT3_ACTUAL_NATIVE_RENDER',n,png.stat().st_size,flush=True)
scene.camera=bpy.data.objects[cameras[-1]]
bpy.ops.wm.save_as_mainfile(filepath=str(saved),compress=True)
result={
 'schema':'HALO9_INT3_ONE_FAULT_CIVIC_SECTION_NATIVE',
 'source_sha256':SOURCE_SHA,
 'native_blend_sha256':hashlib.sha256(saved.read_bytes()).hexdigest(),
 'removed_int1_architecture':deleted,
 'new_mesh_roles':count,
 'native_angular_public_cutouts':carves,
 'render_hashes':hashes,
 'fixed_camera_poses':True,
 'coordinates':'NONCANONICAL_RESEARCH_METRES',
 'art':'AWAIT_DIRECT_SAME_SCENE_IMAGE_REVIEW',
 'function':'NOT_INDEPENDENTLY_VERIFIED',
 'formal_art_accepted':0,
 'completed_targets':0,
 'minecraft_construction':'HOLD',
}
(out/'INT3_NATIVE_REPORT.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print('INT3_REAL_NATIVE_COMPLETE',result['native_blend_sha256'],flush=True)
