# CELESTIAL HALO-9 R4-E8 — LIVED SPINE / PUBLIC CITY
# New native Blender master study, in independent research metres only.
# Artistic admission requires real 3-view visual review; TECH is not ART.
# Never opens E6, E7, R0B, original models, Freeze or Minecraft.
import bpy, math, sys, hashlib, json
from mathutils import Vector
from pathlib import Path
argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(argv[argv.index('--output')+1] if '--output' in argv else '/tmp/halo9_e8')
out.mkdir(parents=True,exist_ok=True);(out/'renders').mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene
for k,v in {'project':'HALO9 R4-E8 LIVED SPINE PUBLIC CITY','minecraft_write':'FORBIDDEN','official_coordinates_verified':False,'formal_art_adoption':False,'completed_targets':0,'source_e6_e7_meshes_imported':False,'art_review':'UNREVIEWED','coordinate_system':'RESEARCH METRES - NOT OFFICIAL'}.items():s[k]=v
s.render.engine='CYCLES';s.cycles.samples=12
s.render.resolution_x=960;s.render.resolution_y=640;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
try:s.view_layers[0].cycles.use_denoising=False
except:pass
try:s.view_settings.view_transform='Filmic';s.view_settings.look='Medium High Contrast'
except:pass
coll={}
for n in ('W0_WORLD_CONTEXT_INCOMPLETE','CENTRAL_SPLIT_LIVED_SPINE','NAVE_MULTILEVEL_PUBLIC_CITY',
          'H1_INHABITED_HIGH_CITY','CONTINUOUS_CITY_TRANSPORT','CINEMATIC_CAMERAS','REGISTRY_30_UNFINISHED'):
    c=bpy.data.collections.new(n);s.collection.children.link(c);coll[n]=c
def mat(n,col,metal=0,rough=.55,emit=0):
    m=bpy.data.materials.new(n);m.diffuse_color=(*col,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*col,1)
    bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
    a=bs.inputs.get('Emission Color') or bs.inputs.get('Emission')
    if a:a.default_value=(*col,1)
    a=bs.inputs.get('Emission Strength')
    if a:a.default_value=emit
    return m
MAT={
 'limestone':mat('warm ivory structural ceramic',(.70,.68,.59),.14,.62),
 'graphite':mat('smoked graphite deep foundations',(.15,.18,.22),.38,.54),
 'copper':mat('aged bronze civic frame',(.55,.40,.23),.64,.35),
 'glass':mat('blue green inhabited curtain glazing',(.20,.42,.48),.43,.25),
 'bright':mat('public terrazzo',(.73,.69,.59),.09,.82),
 'dark':mat('deep urban paving',(.31,.34,.33),.04,.87),
 'garden':mat('landscape vegetation',(.20,.36,.22),.01,.96),
 'water':mat('turbid east inland sea',(.09,.27,.34),.4,.24),
 'earth':mat('fossil limestone land',(.39,.38,.32),.01,.93),
 'lamp':mat('soft honey luminaires',(.97,.82,.51),0,.35,2.1),
 'coral':mat('terra cotta inhabited facades',(.50,.33,.27),.10,.72),
 }
def mesh(n,vs,fs,key,layer):
    me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.update()
    ob=bpy.data.objects.new(n,me);coll[layer].objects.link(ob);ob.data.materials.append(MAT[key]);return ob
def box(n,x,y,z,w,d,h,key,layer,ang=0):
    c=math.cos(ang);si=math.sin(ang)
    poly=[(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]
    verts=[]
    for zz in (z-h/2,z+h/2):
        verts.extend((x+a*c-b*si,y+a*si+b*c,zz) for a,b in poly)
    return mesh(n,verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],key,layer)
def slab(n,poly,z0,z1,key,layer):
    N=len(poly);vs=[(x,y,z) for z in (z0,z1) for x,y in poly]
    faces=[tuple(reversed(range(N))),tuple(range(N,N*2))]
    for i in range(N):faces.append((i,(i+1)%N,N+(i+1)%N,N+i))
    return mesh(n,vs,faces,key,layer)
def walkway(n,path,width,depth,key,layer):
    vs=[]
    for i,p in enumerate(path):
        a=Vector(path[max(i-1,0)]);b=Vector(path[min(i+1,len(path)-1)])
        dx,dy=b.x-a.x,b.y-a.y
        L=max(1e-6,math.hypot(dx,dy))
        nx,ny=-dy/L,dx/L
        for q in (-1,1):
            vs.append((p[0]+q*nx*width/2,p[1]+q*ny*width/2,p[2]))
            vs.append((p[0]+q*nx*width/2,p[1]+q*ny*width/2,p[2]-depth))
    f=[]
    for i in range(len(path)-1):
        a=4*i;b=4*(i+1)
        f.extend([(a,b,b+2,a+2),(a+1,a+3,b+3,b+1),
                  (a,a+1,b+1,b),(a+2,b+2,b+3,a+3)])
    f.extend([(0,2,3,1),tuple(reversed(range(4*(len(path)-1),4*len(path))))])
    return mesh(n,vs,f,key,layer)
# Connected 10km W0 research geography; actual ground never certified as done.
N=57;v=[];f=[]
for j in range(N+1):
    y=-5000+10000*j/N
    for i in range(N+1):
        x=-5000+10000*i/N
        north=940*math.exp(-((y-3400)/1650)**2)*(0.75+.24*math.sin(x/670)**2)
        west=630/(1+math.exp(max(-40,min(40,(x+3200)/170))))
        sw=-360*math.exp(-((x+2400)/1450)**2-((y+2550)/1550)**2)
        east=-280*math.exp(-((x-3300)/1650)**2-((y+200)/2800)**2)
        v.append((x,y,110+north+west+sw+east+27*math.sin(x/460+y/370)))
for j in range(N):
    for i in range(N):
        a=j*(N+1)+i;f.append((a,a+1,a+N+2,a+N+1))
mesh('W0_NORTH_MOUNTAIN_WEST_ESCARPMENT_SOUTHWEST_VOID',v,f,'earth','W0_WORLD_CONTEXT_INCOMPLETE')
box('W0_EAST_INLAND_SEA_STUDY_ONLY',3350,400,-150,3300,6400,7,'water','W0_WORLD_CONTEXT_INCOMPLETE')
# Urban canyon geometries are distinct stepped CITY FACADES rather than blades
# or co-centric radial stages. Each side is a thick asymmetric inhabited ridge.
west=[(-1030,-1380),(-620,-1400),(-350,-1100),(-350,760),(-520,1220),(-960,1250),(-1230,620)]
east=[(390,-1320),(915,-1240),(1200,-720),(1190,320),(1030,1210),(480,1220),(420,640)]
for side,p,z in [('WEST',west,540),('EAST',east,690)]:
    slab(side+'_DEEP_INHABITED_RIDGE_SUBSTRATE',p,120,z,'graphite','CENTRAL_SPLIT_LIVED_SPINE')
    # diagonal setbacks create actual city decks, not suspended one-layer shelves
    X=-1 if side=='WEST' else 1
    for level,(step,raisez) in enumerate([(0,210),(115,330),(250,470)]):
        y0=-1090+level*120; y1=940-level*90
        x0=X*(410+step); x1=X*(850+step)
        left,right=sorted((x0,x1))
        box(side+'_INHABITED_TERRAIN_LEVEL_'+str(level),(left+right)/2,(y0+y1)/2,
            raisez-22,right-left,y1-y0,43,'limestone','CENTRAL_SPLIT_LIVED_SPINE')
        # A readable continuous public street on each tier
        box(side+'_CONTINUOUS_URBAN_STREET_'+str(level),
            X*(472+step),(y0+y1)/2,raisez+3,52,y1-y0,7,'bright','NAVE_MULTILEVEL_PUBLIC_CITY')
        for k in range(7):
            y=y0+135+k*(y1-y0-270)/6
            if k==3 and level!=1:continue
            x=X*(630+step+24*math.sin(k*1.1+level))
            # buildings with real external facades, entrances and windows
            w=85+11*(k%3);d=105+13*((k+level)%3)
            h=92+19*((k*3+level)%4)
            key=['limestone','coral','copper','limestone'][k%4]
            # site-specific shifted masses, not deformed opaque triangles
            box(side+'_LIVED_ZONE_%d_%d_BODY'%(level,k),x,y,raisez+8+h/2,w,d,h,key,'CENTRAL_SPLIT_LIVED_SPINE')
            box(side+'_LIVED_ZONE_%d_%d_GLAZED_PUBLIC_GROUND'%(level,k),
                x-X*w*.46,y,raisez+23,8,d*.58,36,'glass','CENTRAL_SPLIT_LIVED_SPINE')
            for floor in range(3):
                # long recessed horizontal bands create scale and occupancy
                box(side+'_LIVED_ZONE_%d_%d_FRONT_WINDOW_%d'%(level,k,floor),
                    x-X*(w/2+1),y,raisez+48+floor*24,3,d*.77,10,
                    'glass','CENTRAL_SPLIT_LIVED_SPINE')
            box(side+'_LIVED_ZONE_%d_%d_ROOF_WALK'%(level,k),
                x,y,raisez+8+h+3,w*.93,d*.93,6,'bright','CENTRAL_SPLIT_LIVED_SPINE')
            if k in (1,5):
                box(side+'_LIVED_ZONE_%d_%d_ROOF_GARDEN'%(level,k),
                    x,y,raisez+8+h+8,w*.60,d*.50,4,'garden','CENTRAL_SPLIT_LIVED_SPINE')
        # Open several long vertical public light shafts through city fabric
        for y in (-610,520):
            box(side+'_CIVIC_ATRIUM_GLAZED_SIDEWALL_%d_%d'%(level,y),
                X*(840+step),y,raisez+38,7,94,80,'glass','CENTRAL_SPLIT_LIVED_SPINE')
# CENTRAL OPEN-TO-SKY public NAVE and inhabited canyon streets
box('NAVE_PUBLIC_SPINE_LANDSCAPED_BOULEVARD',0,-230,165,265,2190,14,'bright','NAVE_MULTILEVEL_PUBLIC_CITY')
box('NAVE_CENTRAL_PEDESTRIAN_PROMENADE',0,-240,176,46,1980,9,'dark','NAVE_MULTILEVEL_PUBLIC_CITY')
for k in range(12):
    y=-1070+k*168
    for X in (-1,1):
        box('NAVE_PUBLIC_TREE_COURT_%d_%d'%(k,X),X*95,y,180,53,65,7,'garden','NAVE_MULTILEVEL_PUBLIC_CITY')
for name,x,y,w,d in [('CENTRAL_COUNCIL',-280,35,120,230),
                    ('EAST_LIBRARY',280,330,120,240),
                    ('WEST_MARKET',-276,-470,120,190),
                    ('EAST_CIVIC_STATION',276,-570,120,220)]:
    # Tall multi-floor entrance halls, not empty exterior shells
    key='coral' if name=='WEST_MARKET' else 'limestone'
    box(name+'_SOLID_INHABITED_PUBLIC_HALL',x,y,261,w,d,158,key,'NAVE_MULTILEVEL_PUBLIC_CITY')
    box(name+'_FULL_STREET_ENTRANCE',x+(-49 if x>0 else 49),y,207,13,d*.62,65,'glass','NAVE_MULTILEVEL_PUBLIC_CITY')
    for floor in range(3):
        box(name+'_PUBLIC_GALLERY_LEVEL_'+str(floor),x,y,208+floor*45,w*.84,d*.82,6,'bright','NAVE_MULTILEVEL_PUBLIC_CITY')
        box(name+'_PUBLIC_FACADE_RIBBON_'+str(floor),
            x+(-61 if x>0 else 61),y,228+floor*43,4,d*.83,14,'glass','NAVE_MULTILEVEL_PUBLIC_CITY')
    box(name+'_ROOF_SCULPTED_COPPER',x,y,347,w*1.09,d*.96,15,'copper','NAVE_MULTILEVEL_PUBLIC_CITY')
# Visible canyon-access footbridges are deliberately AFTER courtyard, not above human head.
for j,(y,z) in enumerate([(270,420),(750,575)]):
    walkway('NAVE_HIGH_CROSS_CONNECTION_'+str(j),
            [(-820,y,280+j*140),(-500,y+35,z-35),(0,y+68,z),
             (530,y+30,z-26),(1050,y,z+65)],26,14,
             'copper','CONTINUOUS_CITY_TRANSPORT')
# Sequence from W0 ground into same CITY NAVE without pretended route certification
walkway('W0_SOUTH_GROUND_ARRIVAL_TO_CITY',
        [(0,-2200,127),(0,-1750,146),(0,-1330,158),(0,-1110,178)],
        64,12,'bright','CONTINUOUS_CITY_TRANSPORT')
# Monumental M247-C research silhouette grows from occupied city,
# not abstract giant blades pasted above it. One legible 900m civic archive
# and asymmetric luminous upper terrace with transverse main public hall.
box('CENTRAL_ARCHIVE_SUPERSTRUCTURE_BASE',-825,650,780,310,430,620,'graphite',
    'CENTRAL_SPLIT_LIVED_SPINE',.16)
box('CENTRAL_ARCHIVE_SUPERSTRUCTURE_LUMINOUS_APERTURE',-665,620,705,20,225,315,'glass',
    'CENTRAL_SPLIT_LIVED_SPINE')
box('CENTRAL_ARCHIVE_UPPER_OCCUPIED_CROWN',-780,690,1120,460,380,114,'limestone',
    'CENTRAL_SPLIT_LIVED_SPINE',-.09)
box('CENTRAL_ARCHIVE_TOP_PUBLIC_GLASS_HALL',-772,676,1208,350,235,65,'glass',
    'CENTRAL_SPLIT_LIVED_SPINE')
box('EAST_LIVING_CREST_TERRACE',960,940,1078,570,250,148,'limestone',
    'CENTRAL_SPLIT_LIVED_SPINE',-.19)
# W0 and central lower city emerge into H1 as linked inhabited station ridges:
H1_sites=[(1180,-470,740,300,360), (1540,-220,825,330,430),
          (1840,70,930,320,490), (2220,240,1050,340,460),
          (2570,550,1160,360,390)]
for i,(x,y,z,w,d) in enumerate(H1_sites):
    # 140-220m thick differentiated inhabited ground, with real public space
    box('H1_INHABITED_DEEP_CITY_SECTION_'+str(i),x,y,z-86,w,d,174,'graphite',
        'H1_INHABITED_HIGH_CITY',(.09 if i%2 else -.10))
    box('H1_LIVING_MAIN_STREET_'+str(i),x,y,z+5,w*.85,57,12,'bright',
        'H1_INHABITED_HIGH_CITY',(.09 if i%2 else -.10))
    for j in range(6):
        xx=x+((j%3)-1)*w*.29
        yy=y+(-1 if j//3==0 else 1)*d*.26
        h=90+(i*17+j*19)%107
        key=['coral','limestone','copper','limestone'][((j+i)%4)]
        name='H1_SECTOR_%d_BLOCK_%d'%(i,j)
        box(name+'_BUILT_VOLUME',xx,yy,z+14+h/2,76,82,h,key,
            'H1_INHABITED_HIGH_CITY',.07*i)
        box(name+'_PUBLIC_GROUND_STOREFRONT',xx,yy-41,z+33,56,5,32,'glass',
            'H1_INHABITED_HIGH_CITY')
        for f in range(3):
            box(name+'_WINDOW_FLOOR_%d'%f,xx,yy-42,z+60+22*f,54,4,10,
                'glass','H1_INHABITED_HIGH_CITY')
        box(name+'_SOLAR_ROOFGARDEN',xx,yy,z+14+h+4,61,63,7,
            'garden' if (j+i)%3==1 else 'bright','H1_INHABITED_HIGH_CITY')
    box('H1_CITY_COMMUNITY_COMMONS_'+str(i),x,y+d*.1,z+16,w*.52,d*.28,8,
        'garden','H1_INHABITED_HIGH_CITY')
for i in range(len(H1_sites)-1):
    x,y,z,_,_=H1_sites[i];X,Y,Z,_,_=H1_sites[i+1]
    walkway('H1_CONTINUOUS_INHABITED_CITY_TRANSIT_'+str(i),
            [(x,y,z+12),((x+X)/2,(y+Y)/2,(z+Z)/2+18),(X,Y,Z+12)],
            46,16,'copper','CONTINUOUS_CITY_TRANSPORT')
# Continuity: central east upper city -> initial H1 civic district.
walkway('M247_PUBLIC_CONNECTION_TO_H1',
       [(880,540,552),(1040,180,660),(1180,-470,752)],43,19,
       'bright','CONTINUOUS_CITY_TRANSPORT')
# Singular elevated diagonal spine crossing canyon NORTH of open room.
walkway('CELESTIAL_NORTHERN_LIVED_SKY_SPINE',
        [(-920,960,865),(-600,1210,935),(-90,1245,1020),
         (480,1165,1080),(1150,930,1140),(1680,750,1210)],
        83,31,'graphite','CENTRAL_SPLIT_LIVED_SPINE')
for i,(x,y,z) in enumerate([(-540,1195,936),(200,1200,1071),(1050,945,1155)]):
    box('SPINE_REAL_PUBLIC_SKY_STATION_'+str(i),x,y,z+48,
        130,115,96,'limestone','CENTRAL_SPLIT_LIVED_SPINE')
    box('SPINE_PUBLIC_GLAZED_HALL_'+str(i),x,y-55,z+48,94,6,62,
        'glass','CENTRAL_SPLIT_LIVED_SPINE')
# Camera engineering: ground view has genuine pedestrian foreground;
# no roof hides center. H1 camera looks down a human street.
def cam(name,loc,target,lens=31,ortho=None):
    data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data)
    coll['CINEMATIC_CAMERAS'].objects.link(ob);ob.location=loc
    vec=Vector(target)-ob.location;ob.rotation_euler=vec.to_track_quat('-Z','Y').to_euler()
    data.lens=lens;data.clip_end=30000
    if ortho:data.type='ORTHO';data.ortho_scale=ortho
    return ob
cam('human_public_interior',(0,-1050,186.7),(0,210,370),lens=28)
cam('human_sky_district',(1540,-390,845.6),(2100,130,1010),lens=28)
cam('urban_aerial',(3450,-3150,2490),(280,20,650),ortho=5200)
cam('ground_arrival',(0,-2080,140),(0,-200,500),lens=29)
cam('central_front',(0,-2200,860),(0,0,760),ortho=3900)
cam('central_rear',(0,2500,1020),(0,0,710),ortho=4200)
cam('east_seafront',(3180,-600,1290),(0,0,670),ortho=5100)
light=bpy.data.lights.new('Golden high-angle sunlight','SUN')
o=bpy.data.objects.new('Golden high-angle sunlight',light)
coll['CINEMATIC_CAMERAS'].objects.link(o)
o.rotation_euler=(.58,-.30,-.52);light.energy=3.2;light.angle=.18
world=bpy.data.worlds.new('bright atmospheric hemisphere')
s.world=world;world.use_nodes=True
bg=world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.62,.73,.79,1);bg.inputs['Strength'].default_value=.73
targetnames=['M247-C','W0']+[f'H{i}' for i in range(1,7)]+[f'SB{i:02d}' for i in range(1,17)]+[f'V{i}' for i in range(1,4)]+[f'METRO_AXIS_{i}' for i in range(1,4)]
assert len(targetnames)==30
for n in targetnames:
    o=bpy.data.objects.new('UNFINISHED_REGISTRY_ONLY_'+n,None)
    coll['REGISTRY_30_UNFINISHED'].objects.link(o)
    o['completed']=False;o['formal_art_adoption']=False
blend=out/'E8_LIVED_SPINE_PUBLIC_CITY_WORKING.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=False)
for n in ('human_public_interior','human_sky_district','urban_aerial'):
    s.camera=bpy.data.objects[n];s.render.filepath=str(out/'renders'/(n+'.png'))
    bpy.ops.render.render(write_still=True);print('E8_REAL_RENDER',n,flush=True)
s.camera=bpy.data.objects['urban_aerial']
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=False)
report={'schema':'halo9-r4-e8-real-blender-v1',
 'technical':'NATIVE_FILES_CREATED_REOPEN_PENDING',
 'art':'UNREVIEWED','formal_adoptions':0,'completed_targets':0,
 'minecraft':'HOLD','official_coordinates_verified':False,'e7_mesh_reused':False,
 'blender':bpy.app.version_string,
 'sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),
 'meshes':sum(o.type=='MESH' for o in bpy.data.objects),
 'renders':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (out/'renders').glob('*.png')}}
(out/'E8_AUTHOR_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('E8_NATIVE_AUTHOR_COMPLETE',json.dumps(report),flush=True)
