"""E11 authored control-mesh construction, run in the live Blender over MCP.
No canonical asset imports. Repeated detail is subordinate to authored city sections.
Research metres only; not Minecraft coordinates. No external assets or paid services.
"""
import bpy, math, pathlib, json
from mathutils import Vector
ROOT=pathlib.Path(__file__).parent
S=bpy.data.scenes.new('E11_INHABITED_SECTION_RESEARCH')
bpy.context.window.scene=S
C={}
for name in ['M247_C','NAVE','H1','W0','TRANSIT','DETAIL','LIGHTS','CAMERAS']:
    c=bpy.data.collections.new('E11_'+name); S.collection.children.link(c); C[name]=c
def mat(name,rgb,metal=0,rough=.5,emission=0):
    m=bpy.data.materials.new('E11_'+name); m.use_nodes=True
    n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    n.inputs['Base Color'].default_value=(*rgb,1); n.inputs['Roughness'].default_value=rough
    n.inputs['Metallic'].default_value=metal
    if emission: n.inputs['Emission Color'].default_value=(*rgb,1); n.inputs['Emission Strength'].default_value=emission
    m.diffuse_color=(*rgb,1); return m
stone=mat('pearl_ceramic',(.61,.68,.67),.22,.36)
lightstone=mat('warm_limestone',(.64,.58,.46),.1,.6)
dark=mat('deep_structure',(.035,.065,.08),.42,.4)
glass=mat('recessed_blue_glazing',(.055,.16,.19),.5,.23)
copper=mat('bronze_edges',(.37,.22,.10),.55,.38)
water=mat('estuary',(.035,.19,.22),.45,.22)
terrain=mat('basalt',(.16,.20,.21),.08,.87)
green=mat('garden',(.15,.24,.16),0,.85)
glow=mat('daylight_wayfinding',(.24,.65,.70),.25,.3,.65)
warm=mat('occupied_interiors',(.78,.43,.16),.1,.45,1.1)
def mesh(name,vs,fs,ma,group,bevel=0):
    m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.update()
    o=bpy.data.objects.new(name,m); C[group].objects.link(o);o.data.materials.append(ma)
    if bevel:
        mod=o.modifiers.new('Authored edge radius','BEVEL');mod.width=bevel;mod.segments=2
    return o
def slab(name,poly,z,thick,ma=stone,group='NAVE',bevel=1):
    n=len(poly);vs=[(x,y,z-thick) for x,y in poly]+[(x,y,z) for x,y in poly]
    fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,vs,fs,ma,group,bevel)
def volume(name,rings,ma=stone,group='M247_C',bevel=2):
    n=len(rings[0]);vs=[p for ring in rings for p in ring];fs=[tuple(range(n-1,-1,-1))]
    for j in range(len(rings)-1):
        for i in range(n): fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    fs.append(tuple(range((len(rings)-1)*n,len(rings)*n)))
    return mesh(name,vs,fs,ma,group,bevel)
def beam(name,a,b,width,depth=None,ma=stone,group='M247_C'):
    a,b=Vector(a),Vector(b);d=b-a
    q=d.to_track_quat('Z','Y');w=width/2;h=(depth or width)/2
    vs=[tuple(a+q@Vector((x*w,y*h,z*d.length))) for z in (0,1) for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    return mesh(name,vs,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],ma,group,min(width*.08,1.5))
def line(name,pts,r,ma=stone,group='DETAIL'):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2
    p=c.splines.new('POLY');p.points.add(len(pts)-1)
    for v,co in zip(p.points,pts):v.co=(*co,1)
    o=bpy.data.objects.new(name,c);C[group].objects.link(o);c.materials.append(ma);return o
def interpolate(profiles,z):
    for (za,pa),(zb,pb) in zip(profiles,profiles[1:]):
        if za<=z<=zb:
            t=(z-za)/(zb-za);return [(a[0]*(1-t)+b[0]*t,a[1]*(1-t)+b[1]*t) for a,b in zip(pa,pb)]
    return profiles[-1][1]
def city_volume(name,profiles,group='M247_C',floor=12):
    # Contours are authored per major city mass. Detail loops create floor edges/glazing only.
    z0,z1=profiles[0][0],profiles[-1][0]
    skins=[];faces=[];ids=[];n=len(profiles[0][1])
    z=z0
    while z<z1:
        top=min(z+floor,z1);p=interpolate(profiles,z);pt=interpolate(profiles,top)
        cx=sum(x for x,y in p)/n;cy=sum(y for x,y in p)/n
        for i in range(n):
            j=(i+1)%n;k=len(skins)
            skins.extend([(cx+(p[i][0]-cx)*.975,cy+(p[i][1]-cy)*.975,z+2),
                          (cx+(p[j][0]-cx)*.975,cy+(p[j][1]-cy)*.975,z+2),
                          (pt[j][0],pt[j][1],top-1.5),(pt[i][0],pt[i][1],top-1.5)])
            faces.append((k,k+1,k+2,k+3));ids.append(1 if int(z/floor)%7 else 2)
        slab(name+'_floor_'+str(round(z)),p,z,2,stone,group,.25)
        z=top
    o=mesh(name+'_inhabited_facades',skins,faces,glass,group)
    o.data.materials.append(dark);o.data.materials.append(warm)
    for p,mi in zip(o.data.polygons,ids):p.material_index=mi
    for i in [0,2,4,6]:
        line(name+'_folded_spine_'+str(i),[(p[i][0],p[i][1],z) for z,p in profiles],3.5,stone,group)
    slab(name+'_roof_garden',profiles[-1][1],z1+.3,1.2,green,group,.5)
    return o

# Each eight-point contour is a deliberately different occupied, faceted section.
west=[(72,[(-490,-330),(-350,-380),(-210,-280),(-175,-80),(-210,210),(-350,340),(-510,260),(-555,-50)]),
      (310,[(-470,-300),(-350,-350),(-220,-250),(-165,-50),(-190,190),(-320,300),(-480,240),(-535,-20)]),
      (570,[(-430,-240),(-310,-285),(-160,-180),(-105,0),(-160,200),(-290,290),(-440,220),(-490,-10)]),
      (820,[(-365,-165),(-270,-210),(-135,-120),(-75,65),(-135,245),(-250,295),(-385,180),(-440,5)]),
      (1010,[(-300,-45),(-225,-90),(-125,-25),(-65,115),(-110,260),(-215,300),(-340,210),(-380,80)])]
city_volume('M247_WEST_ASCENDING_CITY',west)
east=[(72,[(170,-240),(270,-330),(430,-280),(515,-150),(520,170),(420,270),(250,210),(165,40)]),
      (285,[(180,-200),(290,-275),(430,-230),(510,-90),(505,170),(400,260),(260,205),(180,30)]),
      (480,[(235,-155),(330,-210),(465,-150),(545,0),(530,200),(420,290),(295,235),(230,70)]),
      (615,[(310,-50),(390,-100),(510,-55),(580,85),(560,260),(460,340),(350,275),(290,125)])]
city_volume('M247_EAST_TIDAL_BUTTRESS_CITY',east)
north=[(410,[(-90,235),(40,195),(200,240),(305,355),(290,505),(150,570),(-25,515),(-105,375)]),
       (650,[(-60,270),(80,225),(245,280),(335,395),(300,540),(155,590),(-10,530),(-80,400)]),
       (980,[(5,350),(110,300),(260,350),(330,450),(275,570),(165,610),(35,560),(-15,450)]),
       (1280,[(85,440),(150,400),(230,420),(280,490),(245,570),(180,605),(110,575),(65,515)])]
city_volume('M247_DISPLACED_NORTH_CROWN',north)
# Giant diagonal transfer truss carries a real multi-storey civic city, leaving the rift open.
beam('RIFT_WEST_DIAGONAL',(-275,180,300),(-20,330,650),24,30)
beam('RIFT_EAST_DIAGONAL',(380,180,260),(235,360,665),28,32)
beam('RIFT_NORTH_CROSSING',(-250,300,602),(340,365,680),28,55)
beam('RIFT_SUSPENDED_GALLERY',(-225,195,525),(335,275,600),16,42,dark)
slab('SKY_PUBLIC_CONFLUENCE',[(-245,170),(-85,155),(185,220),(330,295),(300,375),(15,340),(-210,280)],603,20,stone,'M247_C')

# NAVE is a broad public bowl with occupied side rooms, not a longitudinal road.
forum=[(-165,-380),(-45,-435),(110,-390),(190,-250),(170,-75),(85,30),(-60,45),(-170,-90),(-210,-255)]
slab('NAVE_FORUM_GROUND',forum,72,15,lightstone)
# Authored concave terraces face across the forum; different destinations at three heights.
slab('NAVE_WEST_LIBRARY_LOGGIA',[(-350,-320),(-210,-300),(-180,-160),(-215,-20),(-180,130),(-300,170),(-385,45)],134,18)
slab('NAVE_EAST_CIVIC_BALCONY',[(170,-300),(320,-280),(360,-140),(310,35),(190,70),(145,-75),(190,-185)],181,22)
slab('NAVE_NORTH_AUDITORIUM',[(-190,65),(-90,20),(100,55),(205,145),(175,245),(-20,230),(-175,155)],104,22,lightstone)
slab('NAVE_SOUTH_WATER_THRESHOLD',[(-170,-560),(20,-595),(190,-520),(110,-390),(-45,-435),(-165,-380)],70,12)
for side,pts in [('W',[(-200,-270,76),(-225,-110,134),(-200,75,205),(-145,165,270)]),('E',[(165,-235,76),(205,-115,128),(200,40,181),(280,180,255)])]:
    for i,(a,b) in enumerate(zip(pts,pts[1:])):
        # Broad physical stairs + a continuous parallel sloping accessible route (research grade).
        n=28;dx=(b[0]-a[0])/n;dy=(b[1]-a[1])/n;dz=(b[2]-a[2])/n
        for j in range(n):
            x=a[0]+j*dx;y=a[1]+j*dy
            slab('NAVE_'+side+'_STAIR_'+str(i)+'_'+str(j),[(x-9,y-2),(x+9,y-2),(x+9,y+dy+3),(x-9,y+dy+3)],a[2]+(j+1)*dz,3,lightstone)
        beam('NAVE_'+side+'_SLOPED_ROUTE_'+str(i),(a[0]+20,a[1],a[2]-2),(b[0]+20,b[1],b[2]-2),12,4,stone,'TRANSIT')
# The auditorium seating is a semicircular room landscape, not another city road.
for j in range(13):
    r=70+j*3.5;poly=[]
    for a in range(0,181,6):poly.append((math.cos(math.radians(a))*r,110+math.sin(math.radians(a))*r*.65))
    for a in range(180,-1,-6):poly.append((math.cos(math.radians(a))*(r-3),110+math.sin(math.radians(a))*(r-3)*.65))
    slab('NAVE_AUDITORIUM_SEAT_'+str(j),poly,107+j*1.1,1.3,lightstone)
# Multiple substantial civic interiors, independently modelled in the rift faces.
for name,base,roof in [
('LIBRARY', [(-345,-230),(-225,-210),(-205,-110),(-280,-65),(-370,-130)],134),
('WATER_ARCHIVE',[(205,-235),(310,-205),(325,-105),(230,-80),(195,-150)],181),
('NORTH_FORUM',[(-120,120),(-10,75),(115,125),(120,200),(-75,210)],270)]:
    slab('NAVE_'+name+'_PUBLIC_ROOF',base,roof+43,7,stone)
    for i in [0,2,4]:
        p=base[i];beam('NAVE_'+name+'_TREE_COLUMN_'+str(i),(p[0],p[1],roof),(p[0]+9,p[1]+8,roof+43),5,6,stone,'NAVE')
    line('NAVE_'+name+'_LIT_EAVE',[(x,y,roof+39) for x,y in base+[base[0]]],.6,warm)

# H1 is a thick inhabited cliff with two open city canyons, not an attached thin island.
h1lower=[(390,135),(590,60),(865,100),(1050,230),(1090,430),(930,580),(660,550),(440,380)]
h1upper=[(435,145),(620,80),(875,125),(1050,250),(1060,420),(905,540),(670,510),(480,350)]
city_volume('H1_SOUTH_HABITABLE_CLIFF',[(305,h1lower),(435,h1upper)],'H1',10)
slab('H1_PUBLIC_GROUND',h1upper,437,8,lightstone,'H1')
city_volume('H1_WEST_LIBRARY_WING',[(437,[(480,210),(570,155),(670,170),(720,250),(675,325),(590,340),(505,300),(470,255)]),
 (535,[(500,220),(575,180),(650,195),(685,255),(655,310),(585,325),(520,290),(490,250)]),
 (590,[(540,245),(590,215),(650,235),(665,280),(630,325),(580,320),(535,290),(525,260)])],'H1',8)
city_volume('H1_EAST_RESIDENTIAL_RISE',[(437,[(855,210),(925,200),(1000,255),(1030,345),(990,420),(915,435),(850,380),(825,280)]),
 (565,[(860,230),(925,225),(990,265),(1010,345),(975,405),(915,420),(860,370),(840,290)]),
 (660,[(895,265),(945,255),(995,300),(1010,365),(970,415),(925,425),(880,375),(865,310)])],'H1',8)
city_volume('H1_NORTH_SCHOOL_CRESCENT',[(437,[(655,415),(750,365),(865,395),(940,475),(910,530),(800,555),(685,520),(630,470)]),
 (505,[(675,425),(755,390),(855,420),(905,480),(885,520),(800,535),(700,510),(655,470)])],'H1',8)
slab('H1_CLINIC_CANOPY',[(720,145),(795,130),(855,170),(845,230),(755,250),(700,215)],478,9,stone,'H1')
for a,b in [((720,160,437),(735,165,478)),((825,175,437),(820,180,478)),((760,225,437),(775,220,478))]:beam('H1_CLINIC_BRANCH',a,b,5,7,stone,'H1')
beam('H1_HIGH_CROSS_STREET',(650,300,510),(900,350,535),13,5,stone,'TRANSIT')
beam('H1_NAVE_PUBLIC_LIFT',(350,140,180),(520,195,437),15,18,dark,'TRANSIT')
beam('H1_WATERFRONT_INCLINE',(600,-100,52),(785,125,437),16,12,dark,'TRANSIT')

# W0: authored northern terrain ridgeline and west urban cliff; eastern sea meets civic steps.
def landstrip(name,rows):
    n=len(rows[0]);vs=[p for row in rows for p in row];fs=[]
    for j in range(len(rows)-1):
        for i in range(n-1):fs.append((j*n+i,j*n+i+1,(j+1)*n+i+1,(j+1)*n+i))
    return mesh(name,vs,fs,terrain,'W0')
landstrip('W0_NORTH_FRACTURED_RANGE',[
 [(-2200,1800,180),(-1500,1750,570),(-900,1850,850),(-200,1900,1100),(500,1800,760),(1250,1900,580),(2000,2000,210)],
 [(-2100,1250,80),(-1500,1100,390),(-850,1200,480),(-100,1150,670),(600,1250,420),(1300,1350,275),(2100,1400,20)],
 [(-2200,650,-15),(-1450,700,145),(-800,650,180),(-150,650,150),(600,700,90),(1300,800,28),(2200,850,-15)]])
landstrip('W0_WEST_BASALT_ESCARPMENT',[
 [(-1800,-1400,190),(-1550,-650,230),(-1500,0,310),(-1400,650,450),(-1250,1200,560)],
 [(-1200,-1400,140),(-1050,-650,170),(-1000,0,210),(-1050,650,320),(-1000,1200,430)],
 [(-1030,-1400,-20),(-900,-650,-12),(-800,0,12),(-850,650,30),(-800,1200,85)]])
slab('W0_GROUND_BASIN',[(-2500,-2200),(2400,-2200),(2600,2000),(-2500,2100)],-15,50,terrain,'W0',0)
slab('W0_EASTERN_ARTIFICIAL_SEA',[(-650,-1800),(2200,-1800),(2500,1000),(1100,1000),(750,600),(1050,150),(700,-300),(180,-700),(-430,-850)],-2,3,water,'W0',0)
slab('W0_CIVIC_QUAY',[(-545,-520),(-200,-650),(10,-600),(200,-520),(360,-400),(610,-260),(700,-100),(550,75),(220,-90),(-170,-80),(-500,-210)],42,35,terrain,'W0')
for j in range(16):
    z=42-j*2.6
    slab('W0_NAVE_TIDAL_PUBLIC_STAIR_'+str(j),[(-180-j*2,-630-j*5),(40+j*2,-670-j*5),(130+j*2,-610-j*5),(-150-j*2,-565-j*5)],z,3,lightstone,'W0',.3)
line('W0_WATERFRONT_SEAM',[(-540,-520,44),(-200,-650,44),(10,-600,44),(200,-520,44),(360,-400,44),(610,-260,44),(700,-100,44)],1.2,copper,'W0')

# Lighting and fixed research viewpoints.
world=bpy.data.worlds.new('E11_DAYLIGHT');S.world=world;world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.35,.46,.53,1);bg.inputs[1].default_value=.6
def light(name,kind,pos,energy,color,size=100):
    d=bpy.data.lights.new(name,kind);d.energy=energy;d.color=color
    if kind=='AREA':d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);C['LIGHTS'].objects.link(o);o.location=pos;return o
sun=light('E11_LATE_SUN','SUN',(0,0,1500),2.3,(1,.83,.65));sun.rotation_euler=(.43,-.53,-.55);sun.data.angle=.15
for name,pos,target,en,size in [('NAVE_SKYLIGHT',(0,-50,430),(0,-50,70),22000000,300),('H1_SKY',(760,200,750),(780,260,435),12000000,250)]:
    o=light(name,'AREA',pos,en,(.68,.82,1),size);o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def camera(name,loc,target,lens):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);C['CAMERAS'].objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();d.lens=lens;d.clip_start=.15;d.clip_end=20000;return o
camera('E11_NAVE_HUMAN',(15,-360,73.7),(0,110,255),23)
camera('E11_H1_HUMAN',(760,270,438.7),(770,480,505),24)
camera('E11_URBAN_AERIAL',(2150,-2700,1850),(100,120,450),43)
camera('E11_WATER_APPROACH',(1150,-1650,125),(30,100,480),32)
camera('E11_REVERSE',(-1700,1800,1150),(100,150,500),38)
S.camera=bpy.data.objects['E11_URBAN_AERIAL'];S.render.engine='CYCLES';S.cycles.samples=24;S.cycles.use_denoising=True
S.render.threads_mode='FIXED';S.render.threads=2
S.render.resolution_x=1200;S.render.resolution_y=900;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.film_transparent=False
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast'
S['ART_STATUS']='UNREVIEWED';S['FORMAL_ART_ACCEPTED']=0;S['COMPLETED_TARGETS']=0;S['CONSTRUCTION']='HOLD'
S['COORDINATES']='ISOLATED_RESEARCH_METRES_NOT_WORLD_REGISTERED'
S['AUTHOR_METHOD']='MCP explicit control-mesh editing; no GUI hand sculpt claim; repeated floor/facade details scripted'
S['E10_HEAD']='94073f97cd65e346e5a3a9846f8dd48a73c6e8e4'
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'E11_INHABITED_SECTION_WORKING.blend'))
bpy.app.driver_namespace['E11']=globals()
print('E11_STAGE01_SAVED',len(S.objects),len(bpy.data.meshes))
