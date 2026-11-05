# CELESTIAL HALO-9 R4-E7: CIVIC CANYON / INHABITED ARCS
# Fresh editable architectural 3D, no R0B or E6 meshes imported.
# NONBUILD, unverified research metres; ART UNREVIEWED until actual renders inspected.
import bpy, math, sys, json, hashlib
from pathlib import Path
from mathutils import Vector

argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(argv[argv.index('--output')+1] if '--output' in argv else '/tmp/halo9_e7_native')
out.mkdir(parents=True,exist_ok=True)
(out/'renders').mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for col in list(bpy.data.collections):
    if col.name!='Collection' and col.users==0:bpy.data.collections.remove(col)
scene=bpy.context.scene
scene['project']='CELESTIAL HALO-9 R4-E7'
scene['minecraft_write']='FORBIDDEN'
scene['official_coordinates_verified']=False
scene['formal_art_adoption']=False
scene['completed_targets']=0
scene['art_status']='UNREVIEWED_NATIVE_RESEARCH'
scene['research_units']='METRES_NOT_MINECRAFT_COORDINATES'
scene.render.engine='CYCLES'
scene.cycles.samples=12
scene.render.resolution_x=960
scene.render.resolution_y=640
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
try:scene.view_layers[0].cycles.use_denoising=False
except (AttributeError,TypeError):pass
scene.world.color=(0.48,0.58,0.68)
scene.view_settings.view_transform='Filmic'
scene.view_settings.look='Medium High Contrast'
scene.camera=None

def collection(n):
    c=bpy.data.collections.new(n);scene.collection.children.link(c);return c
cols={n:collection(n) for n in (
    'W0_MACRO_RESEARCH','M247_DUAL_INHABITED_ARCS','NAVE_OPEN_SKY_PUBLIC_ROOM',
    'H1_LIVING_CITY_FABRIC','THREE_DIMENSIONAL_TRANSIT','CAMERA_AND_LIGHT',
    '30_TARGETS_REGISTRY_ONLY')}
def material(name,color,metal=0,rough=.65,emission=0,alpha=1):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,alpha);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,alpha)
    bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
    bs.inputs['Emission'].default_value=(*color,1)
    bs.inputs['Emission Strength'].default_value=emission
    if alpha<1:m.blend_method='BLEND';bs.inputs['Alpha'].default_value=alpha
    return m
M={
'ivory':material('ivory ceramic civic architecture',(.77,.79,.74),.11,.45),
'stone':material('silver limestone civic plinth',(.43,.51,.52),.07,.72),
'graphite':material('graphite deep city structure',(.15,.23,.29),.44,.6),
'glass':material('smoked blue glass inhabited facades',(.12,.36,.48),.45,.32),
'brass':material('aged luminous bronze',(.63,.47,.21),.63,.34),
'copper':material('weathered green copper',(.27,.43,.40),.44,.45),
'park':material('high-altitude planted commons',(.24,.41,.26),.0,.9),
'walk':material('sunlit public sandstone',(.62,.60,.53),.04,.78),
'water':material('east artificial inland sea',(.07,.28,.39),.38,.23),
'terrain':material('mountain basin weathered limestone',(.40,.43,.37),.0,.91),
'light':material('soft linear city luminaire',(.65,.83,.78),.0,.35,1.8),
}
def object_mesh(n,vs,fs,mat,col):
    mesh=bpy.data.meshes.new(n);mesh.from_pydata(vs,[],fs);mesh.update()
    o=bpy.data.objects.new(n,mesh);cols[col].objects.link(o);o.data.materials.append(M[mat])
    return o
def poly_prism(n,poly,z0,z1,mat,col):
    N=len(poly)
    vs=[(x,y,z) for z in (z0,z1) for x,y in poly]
    fs=[tuple(reversed(range(N))),tuple(range(N,2*N))]
    for k in range(N):fs.append((k,(k+1)%N,(k+1)%N+N,k+N))
    return object_mesh(n,vs,fs,mat,col)
def extruded_curve(n,pts,width,depth,mat,col):
    vs=[]
    for i,p in enumerate(pts):
        a=Vector(pts[max(0,i-1)]);b=Vector(pts[min(len(pts)-1,i+1)])
        dx,dy=b.x-a.x,b.y-a.y
        L=max(1e-6,math.hypot(dx,dy));nx,ny=-dy/L,dx/L
        for z in (p[2]-depth,p[2]):
            vs.extend([(p[0]-nx*width/2,p[1]-ny*width/2,z),
                       (p[0]+nx*width/2,p[1]+ny*width/2,z)])
    fs=[]
    for i in range(len(pts)-1):
        k=i*4;u=(i+1)*4
        fs.extend([(k,k+1,u+1,u),(k+2,u+2,u+3,k+3),
                   (k,u,u+2,k+2),(k+1,k+3,u+3,u+1)])
    fs.append((0,2,3,1));i=(len(pts)-1)*4
    fs.append((i,i+1,i+3,i+2))
    return object_mesh(n,vs,fs,mat,col)
def arc_prism(n,ri,ro,a0,a1,z0,z1,mat,col,steps=24,xc=0,yc=0):
    vs=[]
    for z in (z0,z1):
        for r in (ri,ro):
            for k in range(steps+1):
                a=math.radians(a0+(a1-a0)*k/steps)
                vs.append((xc+r*math.cos(a),yc+r*math.sin(a),z))
    L=steps+1
    fs=[]
    for k in range(steps):
        fs.extend([(k,k+1,L+k+1,L+k),
                   (2*L+k,3*L+k,3*L+k+1,2*L+k+1),
                   (k,2*L+k,2*L+k+1,k+1),
                   (L+k,L+k+1,3*L+k+1,3*L+k)])
    fs.extend([(0,L,3*L,2*L),(steps,2*L+steps,3*L+steps,L+steps)])
    return object_mesh(n,vs,fs,mat,col)
def loft(n,poly,levels,mat,col):
    N=len(poly);vs=[]
    for x,y,z,sx,sy,theta in levels:
        c,s=math.cos(theta),math.sin(theta)
        for a,b in poly:
            a*=sx;b*=sy
            vs.append((x+a*c-b*s,y+a*s+b*c,z))
    fs=[tuple(reversed(range(N))),tuple(range((len(levels)-1)*N,len(levels)*N))]
    for j in range(len(levels)-1):
        for k in range(N):
            a=j*N+k;b=j*N+(k+1)%N
            fs.append((a,b,b+N,a+N))
    return object_mesh(n,vs,fs,mat,col)
def box(n,x,y,z,w,d,h,mat,col,angle=0):
    p=[(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]
    return loft(n,p,[(x,y,z-h/2,1,1,angle),(x,y,z+h/2,1,1,angle)],mat,col)
def urban_hall(n,x,y,z,w,d,h,rot,col,primary):
    # faceted accessible multi-level volume, glazed public entrance and terrace:
    p=[(-.50,-.33),(-.21,-.52),(.30,-.48),(.53,-.15),(.43,.42),
       (.12,.53),(-.38,.40),(-.55,.06)]
    p=[(a*w,b*d) for a,b in p]
    loft(n+'_OCCUPIED_CIVIC_ENVELOPE',p,[
        (x,y,z,1,1,rot),(x+9,y+3,z+h*.37,1.01,.94,rot+.07),
        (x-5,y+11,z+h*.70,.87,.90,rot-.10),
        (x+15,y+6,z+h,.69,.73,rot+.04)],primary,col)
    # Public facade, never a bare icon on the floor
    box(n+'_ENTRY_GLAZING',x+14,y-d*.33,z+27,w*.32,5,50,'glass',col,rot)
    box(n+'_OPEN_PUBLIC_FLOOR',x,y,z+h*.40,w*.78,d*.71,6,'walk',col,rot)
    box(n+'_UPPER_GALLERY',x+5,y,z+h*.76,w*.63,d*.60,5,'copper',col,rot)
    box(n+'_VERTICAL_LIFTHALL',x-w*.28,y+d*.16,z+h*.52,12,15,h*.82,'glass',col,rot)

# 10km-wide W0 urban topography, retained only as unapproved research context.
N=56;vs=[];faces=[]
for j in range(N+1):
    y=-5000+10000*j/N
    for i in range(N+1):
        x=-5000+10000*i/N
        hill=1120*math.exp(-((y-3500)/1420)**2)*(0.6+0.4*math.cos(x/1100)**2)
        cliff=670/(1+math.exp(max(-100,min(100,(x+3250)/115))))
        negative=-490*math.exp(-((x+2700)/1170)**2-((y+2500)/1290)**2)
        sea=-270*math.exp(-((x-3000)/1720)**2-((y+200)/3100)**2)
        wave=38*math.cos(x/550+y/450)+29*math.sin(x/260-y/420)
        vs.append((x,y,40+hill+cliff+negative+sea+wave))
for j in range(N):
    for i in range(N):
        a=j*(N+1)+i;faces.append((a,a+1,a+N+2,a+N+1))
object_mesh('W0_WIDE_BASIN_RESEARCH_PLACEHOLDER_NOT_COMPLETE',vs,faces,'terrain','W0_MACRO_RESEARCH')
box('EAST_INLAND_SEA_TO_BE_SCULPTED',3170,200,-130,3200,6600,6,'water','W0_MACRO_RESEARCH')

# The urban architecture is the negative volume: a half-kilometre, open-sky
# civic canyon continuously occupied on its two outward-flaring city walls.
# No imported blade forms, no high opaque roof over the human camera.
for side,a0,a1 in [('WEST',112,248),('EAST',-68,68)]:
    for tier in range(7):
        # central void remains at least 680m wide even at lowest terraces
        ri=355+tier*111
        ro=ri+255-10*(tier%2)
        z=152+tier*116
        # Different urban cuts, not two identical ringed walls
        cuts=([(a0,a0+56),(a0+70,a1)] if side=='WEST' else
              [(a0,a0+61),(a0+72,a1)])
        for part,(p0,p1) in enumerate(cuts):
            arc_prism(side+'_OCCUPIED_CANYON_BENCH_%02d_%d'%(tier,part),
                      ri,ro,p0,p1,z-60,z+2,
                      'ivory' if tier%3!=1 else 'stone','M247_DUAL_INHABITED_ARCS',
                      steps=16)
            arc_prism(side+'_PUBLIC_CANYON_PROMENADE_%02d_%d'%(tier,part),
                      ri,ri+41,p0,p1,z+2,z+7,'walk','NAVE_OPEN_SKY_PUBLIC_ROOM',steps=16)
        # Airy distinct building courts integrated through several heights,
        # interrupted for vertical walking gorges. Avoid roof afterthoughts.
        for k in range(7):
            a=math.radians(a0+13+(a1-a0-26)*(k+.38*(tier%2))/6.6)
            r=ri+128+20*math.sin(k+0.7*tier)
            x=r*math.cos(a);y=r*math.sin(a)
            if k==3:continue
            h=76+((k*23+tier*19)%91)
            w=90+((k*17+tier*23)%42)
            d=78+((k*13+tier*7)%33)
            urban_hall('%s_TIER%d_WARD%d'%(side,tier,k),
                       x,y,z+6,w,d,h,a+math.pi/2,
                       'M247_DUAL_INHABITED_ARCS',
                       'ivory' if (k+tier)%4<3 else 'copper')
    # accessible radial stair spines to successive occupied terraces.
    for a in ([144,224] if side=='WEST' else [-35,42]):
        pts=[]
        for tier in range(7):
            r=382+tier*111
            ang=math.radians(a+2*math.sin(tier*.7))
            pts.append((r*math.cos(ang),r*math.sin(ang),154+tier*116))
        extruded_curve(side+'_VISIBLE_SLOPED_PEDESTRIAN_GORGE_'+str(a),
                      pts,25,9,'brass','THREE_DIMENSIONAL_TRANSIT')

# NAVE: a sequence of public rooms/terraces within unobstructed open sky.
# A genuine destination at ground level, with occupied institutions on
# concave city edges and readable transport to upper terraces.
poly_prism('NAVE_OPEN_CIVIC_BASIN',
          [(-295,-280),(-135,-430),(143,-408),(320,-180),(245,205),
           (90,355),(-212,255),(-345,50)],141,158,'walk','NAVE_OPEN_SKY_PUBLIC_ROOM')
for k,(x,y,z,w,d,h,rot) in enumerate([
  (-278,-128,160,136,118,126,.22),
  (262,20,160,145,124,180,-.22),
  (-162,340,172,190,118,134,.18),
  (98,-315,170,150,102,124,-.28)]):
    urban_hall(['NAVE_PUBLIC_LIBRARY','NAVE_CITY_COUNCIL',
                'NAVE_STATION_HALL','NAVE_MARKET_ATRIUM'][k],
               x,y,z,w,d,h,rot,'NAVE_OPEN_SKY_PUBLIC_ROOM',
               'copper' if k==1 else 'ivory')
# Large active courtyard island and urban water line, not anonymous flat floor.
arc_prism('NAVE_PUBLIC_ASSEMBLY_STEP_LOWER',90,190,195,341,158,170,'stone',
          'NAVE_OPEN_SKY_PUBLIC_ROOM',steps=25)
arc_prism('NAVE_PUBLIC_ASSEMBLY_STEP_MIDDLE',200,270,186,327,160,183,'ivory',
          'NAVE_OPEN_SKY_PUBLIC_ROOM',steps=25)
arc_prism('NAVE_CIVIC_POOL_STONE_EDGE',45,100,20,330,160,166,'brass',
          'NAVE_OPEN_SKY_PUBLIC_ROOM',steps=44)
arc_prism('NAVE_INNER_WATER',0,44,0,360,161,165,'water',
          'NAVE_OPEN_SKY_PUBLIC_ROOM',steps=48)
# Three real multi-level public arrivals, exposed in the canyon and seen from the floor
for name,pts in [
 ('WEST_CIVIC_PROMENADE',[(-200,-300,163),(-335,-295,224),(-415,-260,270),(-492,-250,382)]),
 ('EAST_CIVIC_PROMENADE',[(230,-245,165),(356,-250,230),(445,-190,283),(520,-112,385)]),
 ('NAVE_LIBRARY_TO_SKY',[(30,335,175),(220,490,285),(440,635,405),
                         (660,705,550),(850,630,680)])]:
    extruded_curve(name,pts,31,8,'brass','THREE_DIMENSIONAL_TRANSIT')

# H1 climbs from the eastern occupied canyon rim into a continuous elevated
# city district. Built on deep stepped urban substrata, not a single floating shelf.
for i,(ri,ro,a0,a1,z) in enumerate([
 (1110,1430,-40,31,775),
 (1360,1710,-38,34,854),
 (1610,1990,-32,40,934),
 (1920,2300,-27,47,1018)]):
    for j,(b0,b1) in enumerate([(a0,0),(7,a1)]):
        arc_prism('H1_DEEP_OCCUPIED_CITY_STRATUM_%d_%d'%(i,j),
                  ri,ro,b0,b1,z-125,z+5,'stone' if i%2==0 else 'ivory',
                  'H1_LIVING_CITY_FABRIC',steps=20)
        arc_prism('H1_PUBLIC_STREET_TERRACE_%d_%d'%(i,j),
                  ri+65,ri+116,b0,b1,z+4,z+10,'walk',
                  'H1_LIVING_CITY_FABRIC',steps=20)
    for k in range(9):
        if k==4:continue
        a=math.radians(a0+8+(a1-a0-16)*(k+.5*(i%2))/8.0)
        r=ri+193+35*math.sin(k*1.2+i)
        x=r*math.cos(a);y=r*math.sin(a)
        name=['RESIDENCES','SCHOOL','BAZAAR','COMMUNITY_LABS','CLINIC',
              'URBAN_GARDENS','TRANSIT_HALL','LIBRARY','CIVIC_HOUSING'][k]
        urban_hall('H1_LAYER%d_%s'%(i,name),x,y,z+10,
                   82+((k*19)%46),76+((i*17+k*7)%40),95+(k*17+i*23)%135,
                   a+math.pi/2,'H1_LIVING_CITY_FABRIC',
                   'ivory' if k%3 else 'copper')
    # prominent green urban commons integrated into every 3D level
    a=math.radians(16+i*3);r=(ri+ro)*.5
    x=r*math.cos(a);y=r*math.sin(a)
    arc_prism('H1_GREEN_PUBLIC_COMMONS_%d'%i,r-38,r+54,
              math.degrees(a)-5,math.degrees(a)+12,z+6,z+15,'park',
              'H1_LIVING_CITY_FABRIC',steps=12)
# Ascending main public cross-section, with multiple continuity options.
for k,theta in enumerate([-23,21]):
    pts=[]
    for i,(r,z) in enumerate([(1050,753),(1260,795),(1500,868),
                              (1780,948),(2070,1034),(2370,1135)]):
        a=math.radians(theta+i*1.1)
        pts.append((r*math.cos(a),r*math.sin(a),z))
    extruded_curve('H1_CITY_TRANSIT_INCLINED_AXIS_'+str(k),pts,
                   39,16,'brass','THREE_DIMENSIONAL_TRANSIT')

# Beta is a late-rising, inhabited civic traverse across the NORTHERN BACK of
# the canyon, leaving the central open-sky chamber unroofed and truly visible.
beta=[(-1240,580,830),(-900,800,895),(-500,940,974),
      (80,1030,1075),(540,910,1170),(1120,660,1265)]
extruded_curve('BETA_LIVED_DIAGONAL_SKY_SPINE_NORTHERN_TRAVERSE',
               beta,91,24,'graphite','M247_DUAL_INHABITED_ARCS')
for k,(x,y,z) in enumerate(beta[1:-1]):
    urban_hall('BETA_LIVED_PUBLIC_STATION_%d'%k,x,y,z+9,
               112,90,86+k*13,.10*k,'M247_DUAL_INHABITED_ARCS','ivory')
# A street-scale entry sequence physically links W0 basin to NAVE.
extruded_curve('W0_GROUND_ARRIVAL_CIVIC_BOULEVARD',
               [(0,-1250,145),(0,-1000,147),(0,-760,151),
                (0,-530,158),(0,-420,161)],49,9,'walk',
               'THREE_DIMENSIONAL_TRANSIT')

def camera(n,p,target,lens=29,ortho=None):
    cam=bpy.data.cameras.new(n);o=bpy.data.objects.new(n,cam)
    cols['CAMERA_AND_LIGHT'].objects.link(o);o.location=p
    direction=Vector(target)-o.location
    o.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    cam.lens=lens;cam.clip_end=30000
    if ortho:cam.type='ORTHO';cam.ortho_scale=ortho
    return o
# Named camera rig: 3 early verdict cameras, 4 reserved for 7-view jury.
camera('human_public_interior',(0,-815,160.65),(0,100,415),lens=27)
camera('human_sky_district',(1290,-530,861.65),(1770,-30,1035),lens=27)
camera('urban_aerial',(3150,-3700,2560),(120,60,780),ortho=5650)
camera('ground_arrival',(0,-1235,146.65),(0,0,600),lens=26)
camera('central_front',(0,-2800,1000),(0,0,730),ortho=3400)
camera('central_rear',(0,2550,1500),(0,0,800),ortho=3750)
camera('east_seafront',(3450,-420,1230),(0,0,800),ortho=4850)
sun=bpy.data.lights.new('Warm daylight','SUN')
s=bpy.data.objects.new('Warm daylight',sun)
cols['CAMERA_AND_LIGHT'].objects.link(s);s.rotation_euler=(.60,-.34,-.65)
sun.energy=3.1;sun.angle=.19
# Ambient brightens occupied interiors; avoid shadows swallowing streets
world=bpy.data.worlds.new('Blue atmospheric ambient') if not bpy.data.worlds else bpy.data.worlds[0]
scene.world=world;world.use_nodes=True
bg=world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(.55,.67,.76,1)
bg.inputs['Strength'].default_value=.72

names=['M247-C','W0']+[f'H{i}' for i in range(1,7)]+[
    f'SB{i:02d}' for i in range(1,17)]+[f'V{i}' for i in range(1,4)]+[
    f'METRO_AXIS_{i}' for i in range(1,4)]
assert len(names)==30
for name in names:
    o=bpy.data.objects.new('REGISTRY_ONLY_'+name,None)
    cols['30_TARGETS_REGISTRY_ONLY'].objects.link(o)
    o['status']='UNFINISHED_RESEARCH_NOT_COMPLETE'
    o['official_art_adoption']=False
# Save first then render same scene; no existing files or original meshes touched.
blend=out/'E7_CIVIC_CANYON_INHABITED_ARCS_WORKING.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=False)
for name in ('human_public_interior','human_sky_district','urban_aerial'):
    scene.camera=bpy.data.objects[name]
    scene.render.filepath=str(out/'renders'/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('HALO9_E7_REAL_RENDER',name,flush=True)
scene.camera=bpy.data.objects['urban_aerial']
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=False)
report={
 'schema':'halo9-r4-e7-arts-first-author-v1',
 'status':'NATIVE_FILES_SAVED_ART_UNREVIEWED',
 'blender_version':bpy.app.version_string,
 'blend_sha256':hashlib.sha256(blend.read_bytes()).hexdigest(),
 'mesh_count':sum(o.type=='MESH' for o in bpy.data.objects),
 'three_real_cameras':['human_public_interior','human_sky_district','urban_aerial'],
 'formal_adoption':False,'completed_targets':0,'minecraft':'HOLD',
 'official_coordinates_verified':False,'e6_mesh_reused':False,
 'image_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted((out/'renders').glob('*.png'))}}
(out/'AUTHOR_REPORT.json').write_text(json.dumps(report,indent=2))
print('HALO9_E7_NATIVE_AUTHOR_FINISHED',json.dumps(report),flush=True)
