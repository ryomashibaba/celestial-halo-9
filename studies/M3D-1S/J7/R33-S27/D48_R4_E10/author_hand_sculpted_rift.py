# CELESTIAL HALO-9 R4-E10 — inhabited bifurcation / sculptural city section.
# ART-FIRST; research only. Hand-authored irregular 3D control cages for main form.
# Does NOT load E2-E9, R0B, Freeze, Minecraft, canonical originals.
# Macro / human NAVE / human H1 are authored together in a SINGLE Blender scene.
import bpy,math,sys,json,hashlib,struct
from mathutils import Vector
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[args.index('--output')+1] if '--output' in args else '/tmp/halo9_e10')
out.mkdir(parents=True,exist_ok=True);(out/'renders').mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene
for n,v in {
  'project':'HALO-9 R4-E10 hand-sculpted civic rift',
  'minecraft_write':'FORBIDDEN','official_coordinates_verified':False,
  'formal_art_adoption':False,'completed_targets':0,
  'old_rejected_models_imported':False,
  'art_status':'UNREVIEWED_NOT_ADOPTED',
  'units':'fictional research metres / NOT canonical Minecraft coordinates'
}.items():s[n]=v
s.render.engine='CYCLES'
s.cycles.samples=18
s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
try:s.view_layers[0].cycles.use_denoising=False
except (AttributeError,TypeError):pass
try:s.view_settings.view_transform='Filmic';s.view_settings.look='Medium High Contrast'
except:pass
groups={}
for n in ['W0_WORLD_CONTEXT_UNFINISHED','M247_C_INHABITED_RIFT_MASSES',
          'NAVE_PUBLIC_CIVIC_INTERIORS','H1_INHABITED_SKY_CITY',
          'PUBLIC_TRANSPORT_AND_BRIDGES','CAMERAS_LIGHTING',
          '30_TARGET_REGISTRY_NOT_COMPLETED']:
    c=bpy.data.collections.new(n);s.collection.children.link(c);groups[n]=c
def material(name,rgb,metal=0,rough=.54,emit=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    k=p.inputs.get('Emission Color') or p.inputs.get('Emission')
    if k:k.default_value=(*rgb,1)
    k=p.inputs.get('Emission Strength')
    if k:k.default_value=emit
    return m
P={
 'ivory':material('pearl limestone structure',(.75,.71,.62),.12,.48),
 'chalk':material('bone ceramic sunlit',(.84,.82,.75),.1,.52),
 'obsidian':material('glaucous architectural basalt',(.17,.22,.26),.45,.50),
 'copper':material('oxidized bronze structural inlay',(.49,.41,.28),.60,.42),
 'glazing':material('bluegreen public glass',(.16,.42,.49),.45,.28),
 'cyan':material('luminous cool public guidance',(.32,.72,.78),0,.45,.85),
 'stone':material('silver weathered civic paving',(.52,.55,.51),.07,.74),
 'rock':material('terraced limestone geology',(.35,.38,.34),0,.90),
 'grass':material('cliff gardens',(.19,.37,.26),0,.94),
 'water':material('inland basin sea',(.09,.28,.38),.35,.27),
 'warm':material('accessible timber-bronze promenade',(.57,.43,.29),.43,.59),
}
def addmesh(name,verts,faces,mat,collection):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);groups[collection].objects.link(ob)
    ob.data.materials.append(P[mat]);return ob
def prism(name,poly,z0,z1,mat,group):
    k=len(poly);pts=[(x,y,z) for z in (z0,z1) for x,y in poly]
    fs=[tuple(reversed(range(k))),tuple(range(k,2*k))]
    for j in range(k):fs.append((j,(j+1)%k,(j+1)%k+k,j+k))
    return addmesh(name,pts,fs,mat,group)
def loft(name,base,profiles,mat,group):
    n=len(base);vs=[]
    for z,xshift,yshift,sx,sy,rotation in profiles:
        c=math.cos(rotation);q=math.sin(rotation)
        for x,y in base:
            a=x*sx;b=y*sy
            vs.append((xshift+a*c-b*q,yshift+a*q+b*c,z))
    faces=[tuple(reversed(range(n))),tuple(range((len(profiles)-1)*n,len(profiles)*n))]
    for k in range(len(profiles)-1):
        for j in range(n):
            a=k*n+j;b=k*n+(j+1)%n
            faces.append((a,b,b+n,a+n))
    return addmesh(name,vs,faces,mat,group)
def beam(name,pts,width,depth,mat,group):
    if len(pts)<2:raise ValueError('beam length')
    verts=[]
    for i,p in enumerate(pts):
        a=Vector(pts[max(0,i-1)]);b=Vector(pts[min(i+1,len(pts)-1)])
        dx,dy=b.x-a.x,b.y-a.y
        L=max(1e-6,math.hypot(dx,dy));u=(-dy/L,dx/L)
        for z in (p[2],p[2]-depth):
            for side in (-1,1):
                verts.append((p[0]+side*u[0]*width/2,p[1]+side*u[1]*width/2,z))
    faces=[]
    for i in range(len(pts)-1):
        a=4*i;b=4*(i+1)
        faces.extend([(a,a+1,b+1,b),(a+2,b+2,b+3,a+3),
                      (a,b,b+2,a+2),(a+1,a+3,b+3,b+1)])
    faces.extend([(0,2,3,1),(len(verts)-4,len(verts)-3,len(verts)-1,len(verts)-2)])
    return addmesh(name,verts,faces,mat,group)
def cube(name,xyz,dim,mat,group,rot=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz)
    ob=bpy.context.object;ob.name=name;ob.scale=dim;ob.rotation_euler[2]=rot
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    for col in list(ob.users_collection):col.objects.unlink(ob)
    groups[group].objects.link(ob);ob.data.materials.append(P[mat]);return ob
def carve(target,name,loc,scale,bevel=0):
    old=len(target.data.polygons)
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    cut=bpy.context.object;cut.name='TEMP_BOOLEAN_'+name;cut.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        m=cut.modifiers.new('Sculpted corner radius','BEVEL');m.width=bevel;m.segments=5
        bpy.context.view_layer.objects.active=cut
        bpy.ops.object.modifier_apply(modifier=m.name)
    mod=target.modifiers.new('EXPLICIT_PUBLIC_VOID_'+name,'BOOLEAN')
    mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
    bpy.context.view_layer.objects.active=target
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cut,do_unlink=True)
    return {'name':name,'target':target.name,
            'faces_before':old,'faces_after':len(target.data.polygons)}
# W0 is an intentionally OPEN, uncompleted shared 10km research landscape.
n=65;vs=[];fs=[]
for iy in range(n+1):
    y=-5100+10200*iy/n
    for ix in range(n+1):
        x=-5100+10200*ix/n
        plateau=850*math.exp(-((y-3700)/1580)**2)*(0.72+0.28*math.cos(x/940)**2)
        western_cliff=660/(1+math.exp(max(-45,min(45,(x+3100)/100))))
        gulf=-450*math.exp(-((x+2600)/1450)**2-((y+2400)/1350)**2)
        sea=-370*math.exp(-((x-3500)/1650)**2-((y-220)/2400)**2)
        erosion=37*math.sin(x/310+y/740)+43*math.cos(x/690-y/270)
        vs.append((x,y,15+plateau+western_cliff+gulf+sea+erosion))
for j in range(n):
    for i in range(n):
        a=j*(n+1)+i;fs.append((a,a+1,a+n+2,a+n+1))
addmesh('W0_NORTH_HIGHLANDS_WEST_SCARP_SW_EMPTY_EAST_INLAND_SEA_UNFINISHED',
        vs,fs,'rock','W0_WORLD_CONTEXT_UNFINISHED')
prism('W0_EAST_INLAND_SEA_CONTEXT',[ (2680,-2800),(4800,-3300),(5100,2500),
      (3400,3200),(2920,1620)],-135,-121,'water','W0_WORLD_CONTEXT_UNFINISHED')

# TWO DISTINCT sculpted, occupied cliff-bodies.
# These explicit ring control points are not arrayed boxes and not reuse of E9.
west=[(-1750,-1170),(-990,-1290),(-500,-1000),(-535,-250),(-455,700),
      (-850,1280),(-1490,1130),(-1760,240),(-1950,-490)]
east=[(480,-1090),(1130,-1320),(1810,-920),(1980,-300),(1830,590),
      (1270,1340),(660,1180),(520,440)]
w=loft('M247_ALPHA_WEST_CITY_CARVED_CIVIC_CLIFF',west,
       [(70,0,0,1,1,0),(250,-20,0,.99,1,.035),
        (510,-160,30,.89,.95,.11),
        (820,-360,95,.76,.86,.17),
        (1080,-570,160,.60,.70,.22),
        (1310,-790,230,.36,.46,.28)],'ivory','M247_C_INHABITED_RIFT_MASSES')
e=loft('M247_BETA_EAST_FAULT_RIDGE_INHABITED',east,
       [(70,0,0,1,1,0),(320,30,0,1.02,.99,-.02),
        (620,160,50,.96,.92,-.09),
        (860,290,100,.86,.84,-.18),
        (1160,520,180,.67,.72,-.26)],'chalk','M247_C_INHABITED_RIFT_MASSES')
# Sculpt genuine eroded public rooms in both ridges:
cuts=[]
for ob,nm,pos,dim,rad in [
    (w,'west_civic_hall_entry',(-810,-510,260),(990,590,285),110),
    (w,'west_upper_civic_gallery',(-1150,580,665),(900,360,225),73),
    (e,'east_station_entry',(1010,-540,285),(1130,540,320),112),
    (e,'east_high_civic_room',(1310,560,635),(1160,330,280),82)]:
    cuts.append(carve(ob,nm,pos,dim,rad))
# A sculpted transverse crown forms a populated CITY connection NORTH of
# the sky-lit void (avoids giant opaque canopy above the public camera).
crown=[(-920,740),(-660,490),(-150,560),(280,810),(880,820),
       (1140,1120),(660,1290),(-260,1330)]
upper=loft('M247_DIAGONAL_LIVED_UPPER_CITY_ASTRAL_CROWN',crown,
       [(990,0,0,1,1,-.04),(1090,90,45,.96,.92,.01),
        (1220,180,100,.83,.82,.06),
        (1350,260,170,.55,.57,.10)],'obsidian','M247_C_INHABITED_RIFT_MASSES')
cuts.append(carve(upper,'crown_public_light_well',(70,990,1140),(550,600,335),74))
# NAVE civic room itself: THIS open volume takes precedence over facade.
floor=[(-380,-1260),(360,-1240),(415,370),(330,920),
       (-335,970),(-450,350)]
prism('NAVE_PUBLIC_CIVIC_ROOM_800M_OPEN_TO_SKY',floor,70,87,'stone',
      'NAVE_PUBLIC_CIVIC_INTERIORS')
beam('NAVE_MAIN_WALKABLE_GROUND_SPINE',[(0,-1300,87),(0,-840,88),
     (12,-360,90),(0,170,93),(5,750,93)],50,8,'warm',
     'NAVE_PUBLIC_CIVIC_INTERIORS')
# Deep public amphitheatre and its shifting steps, a real place to meet.
for i in range(6):
    poly=[(-320+i*27,170+i*31),(305-i*22,160+i*33),
          (275-i*19,300+i*25),(-285+i*25,295+i*23)]
    prism('NAVE_OPEN_CIVIC_FORUM_STEP_'+str(i),poly,93+i*11,102+i*11,'ivory',
          'NAVE_PUBLIC_CIVIC_INTERIORS')
# Public institution ramps are architecturally part of carved walls.
for side,points in [
    ('WEST',[(-155,-650,95),(-410,-590,125),(-610,-510,175),
       (-770,-430,260),(-930,-250,340),(-1080,80,490),(-1140,460,645)]),
    ('EAST',[(155,-710,95),(420,-620,130),(680,-560,190),
       (880,-470,270),(1050,-260,390),(1130,180,540),
       (1240,530,675)])]:
    beam('NAVE_'+side+'_INHABITED_VERTICAL_PUBLIC_PROMENADE',points,24,9,
         'copper','PUBLIC_TRANSPORT_AND_BRIDGES')
# Exposed atriums, visible floor plates and truly occupied public arcades:
for side,cx,cy,z in [('WEST',-810,-525,235),('EAST',1005,-560,253)]:
    for k in range(3):
        prism('NAVE_'+side+'_OPEN_PLAZA_FLOOR_'+str(k),[
            (cx-220,cy-185),(cx+190,cy-166),(cx+220,cy+167),
            (cx-200,cy+180)],z+67*k,z+6+67*k,'warm',
            'NAVE_PUBLIC_CIVIC_INTERIORS')
    for k in range(6):
        x=cx-192+k*76
        beam('NAVE_'+side+'_HALL_LIGHT_COLONNADE_'+str(k),[
            (x,cy-170,z),(x,cy-170,z+215)],14,15,'copper',
            'NAVE_PUBLIC_CIVIC_INTERIORS')
    beam('NAVE_'+side+'_CIVIC_LIGHT_CANOPY',[
        (cx-240,cy-175,z+215),(cx-60,cy-180,z+260),
        (cx+140,cy-155,z+251),(cx+245,cy-100,z+225)],30,17,
         'chalk','NAVE_PUBLIC_CIVIC_INTERIORS')
# Ground city to NAVE, 1 continuous public street along the floor.
beam('W0_CANYON_TO_NAVE_PEDESTRIAN_ARRIVAL',[
    (0,-2250,55),(0,-1850,64),(0,-1410,82),(0,-1120,87)],
    80,11,'stone','PUBLIC_TRANSPORT_AND_BRIDGES')
# Deep public canyon shelves along city walls, cut open between levels.
for side,xsign in [('WEST',-1),('EAST',1)]:
    for k,(z,width,y0,y1) in enumerate([
        (185,126,-820,-40),(350,156,-200,620),(560,136,-760,180),
        (750,145,70,820)]):
        x=xsign*(500+138*k)
        beam(side+'_RIFT_OCCUPIED_PUBLIC_GALLERY_'+str(k),[
            (x,y0,z),(x+20*xsign,(y0+y1)*.45,z+25),
            (x+60*xsign,y1,z+53)],width,15,
            'warm' if k%2==0 else 'stone',
            'NAVE_PUBLIC_CIVIC_INTERIORS')
# H1: hand-built terraced 3D city carved FROM east body, not floating small island.
# A recognisable set of differentiated large civic courtyards with urban street.
h1base=[(790,20),(1560,-370),(2220,-150),(2850,580),(2590,1270),
        (1770,1560),(1050,1210)]
h1=loft('H1_DEEP_LIVED_CITY_SUBSTRATE',h1base,
    [(430,0,0,.89,.92,0),(560,90,20,.98,.99,.025),
     (690,180,30,1.01,1.0,.046),
     (775,250,50,.92,.89,.07)],'obsidian','H1_INHABITED_SKY_CITY')
cuts.append(carve(h1,'H1_urban_civic_light_court',(1730,500,618),
                  (690,470,360),80))
# True open inhabited terraces at multiple heights; distinctive public streets
# run along the courtyard's OUTER rim, not underneath either pedestrian camera.
for idx,name,poly,z in [
 (0,'ARRIVAL_PUBLIC_PLATE',[(1100,-250),(1520,-320),(1710,-90),(1600,230),
      (1240,320),(1090,110)],785),
 (1,'RESIDENTIAL_GARDENS',[(1680,770),(2170,675),(2430,980),
      (2150,1330),(1770,1240)],811),
 (2,'SKY_CIVIC_STATION',[(2250,100),(2640,270),(2860,710),
      (2400,900),(2190,550)],842)]:
    prism('H1_'+name,poly,z,z+16,'stone' if idx!=1 else 'grass',
          'H1_INHABITED_SKY_CITY')
# Four distinct PUBLIC architectural pieces, not hundreds of cloned icons.
# Their semi-open galleries and facade architecture are spatially readable.
public_places=[
 ('H1_LIBRARY_OF_TIDAL_MEMORY',(1300,205,856),[(-135,-125),(145,-95),
   (185,65),(85,195),(-155,150)],'chalk'),
 ('H1_CIVIC_OBSERVATORY',(2450,490,912),[(-155,-115),(140,-160),
   (220,65),(65,160),(-185,115)],'ivory'),
 ('H1_MARKET_AND_SCHOOLS',(1980,1080,869),[(-205,-115),(170,-115),
   (205,125),(-135,190)],'ivory'),
 ('H1_PUBLIC_BATHS_AND_GARDENS',(1650,-40,830),[(-110,-130),(155,-110),
   (140,95),(-75,130)],'copper')]
for name,(cx,cy,z),poly,key in public_places:
    poly=[(cx+x,cy+y) for x,y in poly]
    # Sculpt the occupied superstructure from control rings, no rectangular box.
    pts=[(x-cx,y-cy) for x,y in poly]
    outer=loft(name+'_SCULPTED_OCCUPIED_FORM',pts,
        [(z,cx,cy,1,1,0),(z+95,cx+14,cy-12,.99,.94,.04),
        (z+230,cx-12,cy+20,.79,.77,-.06),
        (z+320,cx+8,cy+26,.56,.61,.02)],key,'H1_INHABITED_SKY_CITY')
    cuts.append(carve(outer,name+'_ACTUAL_PUBLIC_ATRIUM',(cx,cy,z+82),
         (180,150,150),14))
    for k in range(3):
        prism(name+'_OCCUPIED_PUBLIC_FLOOR_'+str(k),
              [(cx-92,cy-68),(cx+93,cy-68),(cx+95,cy+67),(cx-98,cy+66)],
              z+27+k*56,z+34+k*56,'warm','H1_INHABITED_SKY_CITY')
    beam(name+'_GLAZED_PUBLIC_ENTRY',[ (cx,cy-175,z+22),
      (cx,cy-83,z+30),(cx,cy-10,z+39)],26,5,'glazing',
         'H1_INHABITED_SKY_CITY')
# H1 street: follows the district geometry and has civic destinations
beam('H1_MAIN_INHABITED_BOULEVARD',[(1200,-340,799),(1510,-210,799),
    (1730,105,815),(1990,420,815),(2190,680,828),(2370,885,843)],
    57,12,'warm','PUBLIC_TRANSPORT_AND_BRIDGES')
beam('H1_MULTI_ALTITUDE_PUBLIC_CONNECTION_FROM_NAVE',[
    (950,-100,580),(1120,-30,650),(1200,-340,799)],
    37,15,'copper','PUBLIC_TRANSPORT_AND_BRIDGES')
# Plants and terraces integrated at destinations, not scattered tree icons.
for i,(x,y,z,wid,deep) in enumerate([
    (1460,90,809,250,55),(1890,1025,831,350,105),
    (2480,525,870,270,75)]):
    cube('H1_ACTUAL_PUBLIC_PLANTED_COURT_'+str(i),
         (x,y,z),(wid,deep,13),'grass','H1_INHABITED_SKY_CITY',
         rot=[.20,-.10,.38][i])
# no user input needed; research 30 target completion remains zero
ids=['M247-C','W0']+[f'H{i}' for i in range(1,7)]+[
    f'SB{i:02d}' for i in range(1,17)]+[f'V{i}' for i in range(1,4)]+[
    f'METRO_AXIS_{i}' for i in range(1,4)]
assert len(ids)==30
for name in ids:
    ob=bpy.data.objects.new('UNFINISHED_RESEARCH_ONLY_'+name,None)
    groups['30_TARGET_REGISTRY_NOT_COMPLETED'].objects.link(ob)
    ob['completion_certified']=False
    ob['formal_art_adoption']=False
# Camera rules: independently measured eye locations; no giant overhead cover.
def cam(name,location,target,lens=31,ortho=None):
    d=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,d)
    groups['CAMERAS_LIGHTING'].objects.link(ob);ob.location=location
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    d.clip_end=30000;d.lens=lens
    if ortho:d.type='ORTHO';d.ortho_scale=ortho
    return ob
cam('human_nave_civic_room',(0,-950,92.6),(0,320,450),lens=28)
cam('human_h1_inhabited_city',(1320,-230,803.7),(1980,455,970),lens=30)
cam('urban_oblique_entire_core',(3400,-3100,2450),(370,220,740),ortho=5600)
cam('public_inner_civic_gallery',(-800,-560,310),(-160,55,325),lens=28)
cam('canyon_southern_arrival',(0,-2030,61.7),(0,170,800),lens=32)
cam('central_rear',(0,2600,1450),(0,400,860),ortho=4200)
cam('h1_from_east',(3380,-200,1370),(1500,300,810),ortho=3850)
sun=bpy.data.lights.new('stratified atmospheric daylight','SUN')
ob=bpy.data.objects.new('stratified atmospheric daylight',sun)
groups['CAMERAS_LIGHTING'].objects.link(ob)
ob.rotation_euler=(.58,-.34,-.56);sun.energy=3.4;sun.angle=.21
world=bpy.data.worlds.new('sky and shadow balance')
world.use_nodes=True;s.world=world
bg=world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(.57,.67,.72,1)
bg.inputs['Strength'].default_value=.75
# Produce real editable BLEND, THREE actual native renders; never formally adopt.
blend=out/'E10_HAND_SCULPTED_LIVED_RIFT_WORKING.blend'
s.camera=bpy.data.objects['urban_oblique_entire_core']
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=False)
views=['human_nave_civic_room','human_h1_inhabited_city','urban_oblique_entire_core']
for name in views:
    s.camera=bpy.data.objects[name]
    s.render.filepath=str(out/'renders'/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('E10_REAL_NATIVE_RENDER',name,flush=True)
s.camera=bpy.data.objects['urban_oblique_entire_core']
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=False)
report={'schema':'halo9-r4-e10-native-geometry-art-unreviewed',
  'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),
  'visible_meshes':sum(o.type=='MESH' for o in bpy.data.objects),
  'main_form_from_independent_sculpt_cages':True,
  'openings_carved':cuts,'city_master_completed':False,
  'completed_targets':0,'formal_art_adoption':False,
  'minecraft':'HOLD','official_coordinates_verified':False,
  'art_jury':'PENDING_DIRECT_VISUAL_REVIEW',
  'true_png_sha256':{x:hashlib.sha256((out/'renders'/(x+'.png')).read_bytes()).hexdigest() for x in views}}
(out/'AUTHOR_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('E10_TRUE_NATIVE_AUTHOR_PASS',json.dumps(report,flush=True),flush=True)
