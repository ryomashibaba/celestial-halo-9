"""B2-G6: actual mesh architecture in a disposable background Blender process.
No external mesh assets; units metres; all measurements from evaluated meshes.
Macro candidates are built before any occupied districts. Detail requires selection.json.
"""
import bpy,bmesh,math,json,sys,hashlib,argparse,random
from pathlib import Path
from mathutils import Vector
P=argparse.ArgumentParser();P.add_argument('--candidate',choices=['A','B','C'],default='A');P.add_argument('--detail',action='store_true');P.add_argument('--views',default='02_OBLIQUE,01_FRONT');P.add_argument('--preview',action='store_true')
o=P.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
R=Path(__file__).resolve().parent; OUT=R/('selected' if o.detail else 'macro_'+o.candidate);OUT.mkdir(exist_ok=True,parents=True)
if o.detail:
    selection=json.loads((R/'selection.json').read_text(encoding='utf-8'))
    assert selection['selected_candidate']==o.candidate and selection['permission']=='G6_LOCAL_3D_STUDY_ONLY'
bpy.ops.wm.read_factory_settings(use_empty=True)
S=bpy.context.scene;S.unit_settings.system='METRIC';S.unit_settings.scale_length=1
def coll(n):
    c=bpy.data.collections.new(n);S.collection.children.link(c);return c
MASS=coll('01_ROOF_GROUND_ARCHITECTURE');CITY=coll('02_LIVING_DISTRICTS');PUBLIC=coll('03_PUBLIC_SPACE');ROUTE=coll('04_TRANSPORT');CTX=coll('90_CONCEPT_W0_UNREGISTERED');CAMS=coll('91_CAMERAS')
def mat(n,c,rough=.65,metal=0,em=0):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    if em:p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=em
    return m
stone=mat('Warm luminous ceramic ground',(.68,.73,.70));white=mat('Public limestone ceramic',(.85,.82,.69));dark=mat('Recessed inhabited structural core',(.075,.115,.135));glass=mat('Opaque blue glazing - not interior proof',(.075,.25,.28),.24,.3);gold=mat('Civic bronze',(.52,.34,.12),.3,.5);green=mat('Planted public courts',(.12,.25,.19));water=mat('Eastern concept inland sea',(.045,.18,.25),.2,.3);land=mat('Context slate',(.14,.20,.23));light=mat('Light inset',(.9,.7,.35),.3,0,2);peoplemat=mat('Human scale charcoal',(.055,.07,.075))
def mesh(n,v,f,m,c=MASS):
    me=bpy.data.meshes.new(n);me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(n,me);c.objects.link(ob);me.materials.append(m);return ob
def tr(x,y,z,cx=0,cy=0,z0=0,a=0):return(cx+x*math.cos(a)-y*math.sin(a),cy+x*math.sin(a)+y*math.cos(a),z+z0)
def box(n,x,y,z,w,d,h,m=stone,c=CITY,a=0):
    v=[tr(dx,dy,dz,x,y,z,a) for dz in [0,h] for dx,dy in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]]
    return mesh(n,v,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m,c)
def extrude(n,profile,depth,cx,cy,z,a,m=stone,c=MASS):
    N=len(profile);v=[tr(x,y,zz,cx,cy,z,a) for y in [-depth/2,depth/2] for x,zz in profile];f=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(i,(i+1)%N,(i+1)%N+N,i+N) for i in range(N)]
    return mesh(n,v,f,m,c)
def beam(n,p,q,w=5,d=5,m=gold,c=ROUTE):
    vec=Vector(q)-Vector(p);ob=box(n,0,0,0,w,d,vec.length,m,c);ob.location=p;ob.rotation_euler=vec.to_track_quat('Z','Y').to_euler();return ob

HALLS=[];DISTRICTS=[];ROUTES=[]
def vault(n,x,y,z,span,depth,height,a=0,bays=3):
    """Closed arch sections with real sky slits; flat roof plateau is next district ground.
    Inner arch is not a hole texture. Outer roof flattens to an inhabited plateau.
    """
    half=span/2;outer=half+85;plateau=half*.68;spring=55;apex=height-100
    inner=[(-half+span*i/40,spring+(apex-spring)*math.sqrt(max(0,1-(-1+2*i/40)**2))) for i in range(41)]
    xs=[-outer+2*outer*i/48 for i in range(49)]
    upper=[(xx,height if abs(xx)<=plateau else height*math.sqrt(max(0,1-((abs(xx)-plateau)/(outer-plateau))**2))) for xx in xs]
    profile=inner+list(reversed(upper))
    gap=32;dd=(depth-(bays-1)*gap)/bays
    roof_objects=[]
    for k in range(bays):
        yy=-depth/2+dd/2+k*(dd+gap);p=tr(0,yy,0,x,y,z,a)
        roof_objects.append(extrude(n+f' roof/ground bay {k}',profile,dd,p[0],p[1],z,a))
        # civic floor is independent of the occupied arch body; openings remain physically open
        box(n+f' public floor {k}',p[0],p[1],z-14,span,dd,14,dark,PUBLIC,a)
        if o.detail:
            for edge in [-1,1]:
                # Two tiers of real public galleries within haunches, visibly open in the arch interior.
                for lev in [72,142]:
                    lx=edge*(half*.79); pp=tr(lx,yy,lev,x,y,z,a)
                    box(n+f' interior gallery {k} {edge} {lev}',pp[0],pp[1],pp[2],68,dd,8,stone,PUBLIC,a)
                    for side in [-1,1]:
                        p0=tr(lx+side*32,yy-dd/2,lev+10,x,y,z,a);p1=tr(lx+side*32,yy+dd/2,lev+10,x,y,z,a)
                        beam(n+' interior balustrade',p0,p1,1.2,2,gold,PUBLIC)
            for lx in [-span*.22,span*.22]:
                p0=tr(lx,yy-dd*.4,2,x,y,z,a);p1=tr(lx,yy+dd*.4,2,x,y,z,a)
                beam(n+' hall floor light',p0,p1,3,.3,light,PUBLIC)
    # Plateau seams are the actual surface of the roof, no detached urban platform.
    HALLS.append({'id':n,'centre_m':[x,y,z],'angle_rad':a,'span_m':span,'depth_m':depth,'floor_z_m':z,'roof_ground_z_m':z+height,'roof_plateau_width_m':plateau*2,'roof_bays':bays,'sky_slit_m':gap,'roof_object_names':[ob.name for ob in roof_objects]})
    return HALLS[-1]

if o.candidate=='A':
    # One civic succession with a branching lower arm, not three repeated parallel ridges.
    specs=[('A0 Arrival Forum',0,-1280,0,1700,1040,360,0),('A1 Library Market',-420,-600,360,1480,940,420,-.28),('A2 Thousandlight Court',170,80,780,1560,1020,440,.20),('A3 High Civic Commons',-250,770,1220,1400,940,480,-.25),('A4 School Culture Ground',100,1420,1700,1080,820,360,.12),('A_West Ground Archive',-1330,-380,0,920,1000,360,.40)]
    for sp in specs:vault(*sp,bays=3)
elif o.candidate=='B':
    # Closed-court urban sections rotate around an open central court.
    # Public roofs are U-shaped occupied rooms, leaving a multi-storey urban canyon.
    for k,(x,y,z,a) in enumerate([(-700,-850,0,0),(650,-150,450,math.pi/2),(-620,450,900,math.pi),(500,1100,1350,-math.pi/2)]):
        for j,(lx,ly,ang) in enumerate([(-520,0,math.pi/2),(520,0,math.pi/2),(0,520,0)]):
            pp=tr(lx,ly,0,x,y,z,a);vault(f'B{k} court wing {j}',pp[0],pp[1],z,650,1000,450,a+ang,bays=2)
        # Distinct outdoor court floor as the next civic arrival.
        box(f'B{k} open court',x,y,z-18,960,950,18,dark,PUBLIC,a)

else:
    # Redesign C: one inhabited stepped arch-landform. Large civic voids are cut
    # inside the main body. Every horizontal terrace is the roof of a public hall.
    outer=[(-1950,0),(-1740,360),(-1450,360),(-1430,780),(-1120,780),(-1100,1220),(-620,1220),(-600,1700),(-100,1700),(-80,2060),(520,2060),(610,1700),(1130,1700),(1210,1220),(1610,1220),(1680,780),(1910,780),(2100,0)]
    inner=[(-1030+2060*i/64,55+1015*math.sqrt(max(0,1-(-1+2*i/64)**2))) for i in range(65)]
    profile=outer+list(reversed(inner))
    terraces=[('C0 Arrival Library',-1595,0,360,280),('C1 Civic Forum',-1275,360,780,290),('C2 Thousandlight Market',-860,780,1220,460),('C3 High School Commons',-350,1220,1700,480),('C4 Culture Sky Ground',220,1700,2060,540),('C_East Civic Quarter',870,1220,1700,480),('C_East Clinic',1410,780,1220,340)]
    for k,yy in enumerate([-690,0,690]):
        body=extrude(f'C INHABITED LAND bay {k}',profile,630,0,yy,0,0)
        # Carve multiple actual civic rooms with arched soffits; render and export
        # the applied mesh rather than annotation-only openings.
        for ident,cx,fl,roof,w in terraces:
            voidw=w*.73;hh=roof-fl-105
            cutprof=[(-voidw/2,-4),(voidw/2,-4),(voidw/2,hh*.45)]
            cutprof += [(voidw/2*math.cos(t*math.pi/32),hh*.45+hh*.55*math.sin(t*math.pi/32)) for t in range(1,33)]
            cutter=extrude('temporary public hall void',cutprof,660,cx,yy,fl,0,dark)
            mod=body.modifiers.new('Real public hall aperture','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
            bpy.context.view_layer.objects.active=body;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
            box(ident+f' internal floor bay {k}',cx,yy,fl-10,voidw,630,10,dark,PUBLIC)
        box(f'C main interior public floor {k}',0,yy,-12,2060,630,12,dark,PUBLIC)
    for ident,cx,fl,roof,w in terraces:
        HALLS.append({'id':ident,'centre_m':[cx,0,fl],'angle_rad':0,'span_m':w*.73,'depth_m':2010,'floor_z_m':fl,'roof_ground_z_m':roof,'roof_plateau_width_m':w,'roof_bays':3,'sky_slit_m':60,'roof_object_names':[f'C INHABITED LAND bay {i}' for i in range(3)]})
    # The main central void is a through-city, not a forbidden inaccessible hole.
    box('C central ground civic promenade',0,0,.03,72,2010,.15,gold,ROUTE)

# Ground arrival: broad public concourse with a measurable eye-level floor.
box('GROUND ARRIVAL / 0m',0,-2020,-20,2100,720,20,stone,PUBLIC)
box('Arrival processional street',0,-2020,.02,90,720,.12,gold,PUBLIC)
if o.detail and o.candidate=='C':
    box('C Arrival continuity floor',0,-1700,-20,2060,1600,20,stone,PUBLIC)
    box('C Arrival continuity street',0,-1700,.02,72,1600,.12,gold,ROUTE)

def localbox(n,h,lx,ly,z,w,d,hh,m=stone,c=CITY):
    p=tr(lx,ly,z,h['centre_m'][0],h['centre_m'][1],h['roof_ground_z_m'],h['angle_rad'])
    return box(n,p[0],p[1],p[2],w,d,hh,m,c,h['angle_rad'])

def district(h,index):
    # Roof surface lies exactly at district ground. Real U-shaped buildings surround open courts.
    z=h['roof_ground_z_m'];span=h['roof_plateau_width_m'];depth=h['depth_m'];a=h['angle_rad']
    gap=h['sky_slit_m'];baydepth=(depth-2*gap)/3
    for row in range(3):
        ly=-depth/2+baydepth/2+row*(baydepth+gap)
        for col in [-1,1]:
            if (row==0 and col==-1) or (row==2 and col==1):continue
            lx=col*span*.29;ident=f'D{index}_{row}_{col}'
            # Each three-wing block has genuine open 48x44m court and 8m entry, 14m residential depth.
            for wing,(dx,dy,w,d) in enumerate([(-31,0,14,72),(31,0,14,72),(0,29,48,14),(-14,-29,20,14),(14,-29,20,14)]):
                localbox(ident+f' occupied wing {wing}',h,lx+dx,ly+dy,0,w,d,28+7*((row+index)%3),stone)
                for floor in range(3):
                    # Shallow blue facade panels annotate occupied frontage; interiors not modelled.
                    if wing<2:localbox(ident+f' glazing {wing} {floor}',h,lx+dx-col*.02,ly-36.05,7+floor*8,w*.8,.15,3.2,glass)
            localbox(ident+' open planted court',h,lx,ly,0,43,42,.25,green,PUBLIC)
            localbox(ident+' public access',h,lx,ly-45,0,16,22,.2,gold,PUBLIC)
            DISTRICTS.append({'id':ident,'parent_roof':h['id'],'base_z_m':z,'open_court_m':[48,44],'residential_wing_depth_m':14,'nominal_entrance_m':8,'interiors':'NOT_MODELLED'})
        # Roof street: two 24m longitudinal public ways flank a central planted seam.
        for side in [-1,1]:localbox(f'{h["id"]} roof street {row} {side}',h,side*80,ly,.05,24,baydepth,.18,gold,ROUTE)
    # Public institutional bodies form an inhabitable civic edge, never landmark temples on a plinth.
    for label,lx,ly,w,d,hh in [('School',-span*.27,-depth*.31,160,82,46),('Market',span*.27,depth*.29,170,76,38)]:
        # Avoid district rows: institutions go at outer edges, not on open street/courts.
        lx=(-1 if lx<0 else 1)*(span/2-w*.65/2-15)
        localbox(h['id']+' '+label,h,lx,ly,0,w*.65,d,hh,white)
        localbox(h['id']+' '+label+' entry canopy',h,lx,ly-d/2-8,8,w*.62,16,5,stone,PUBLIC)
    # Transverse walk is 24m wide, actually bridging 32m daylight slots.
    for yy in [-depth/2+baydepth+gap/2,-depth/2+2*baydepth+gap*1.5]:
        localbox(h['id']+' slot crossing',h,0,yy,-4,span*.75,gap+8,4,stone,ROUTE)
    # Parapets at exposed long edges, with space for retained street setbacks.
    for side in [-1,1]:
        for row in range(3):
            ly=-depth/2+baydepth/2+row*(baydepth+gap)
            localbox(h['id']+' roof edge guard',h,side*(span/2-5),ly,0,2,baydepth,1.4,gold,PUBLIC)

if o.detail:
    for idx,h in enumerate(HALLS):district(h,idx)
    # Daily urban rooms along the main roof / public building interfaces.
    for idx,h in enumerate(HALLS[:5]):
        # Enter through arch mouths; small market arcade at public floor on both sides.
        for side in [-1,1]:
            for j in range(7):
                p=tr(side*h['span_m']*.27,-h['depth_m']*.42+j*26,0,*h['centre_m'],h['angle_rad'])
                box(h['id']+f' ground market room {side} {j}',p[0],p[1],p[2],38,19,12,white,PUBLIC,h['angle_rad'])
    # Vertical transport is expressed as paired inhabited cores, not a 20% pedestrian ramp.
    for k,(a,b) in enumerate(zip(HALLS[:4],HALLS[1:5])):
        for side in [-1,1]:
            x=b['centre_m'][0]+side*410;y=(a['centre_m'][1]+b['centre_m'][1])/2;lo=a['floor_z_m'];hi=b['roof_ground_z_m']
            box(f'L{k} vertical public lift core {side}',x,y,lo,38,50,hi-lo,dark,ROUTE)
            box(f'L{k} transparent lift annotation {side}',x,y-25.2,lo+10,16,.3,hi-lo-20,glass,ROUTE)
            # Horizontal bridge at each adjacent roof height, actual continuous floor.
            for h in [a,b]:
                tx=h['centre_m'][0]+side*80;ty=h['centre_m'][1];zz=h['roof_ground_z_m']
                p=Vector((x,y,zz-7));q=Vector((tx,ty,zz-7));vec=q-p
                ob=box(f'L{k} roof connection {side} {zz}',(p.x+q.x)/2,(p.y+q.y)/2,zz-14,vec.length,22,14,stone,ROUTE,math.atan2(vec.y,vec.x))
            ROUTES.append({'id':f'L{k}_{side}','lower_floor_m':lo,'upper_roof_m':hi,'system':'conceptual lift core + horizontal bridges; no capacity or clash guarantee'})

    # Foreground human-scale cues are actual 1.75m meshes, not painted image overlays.
    random.seed(9)
    for group,(cx,cy,zz,count) in enumerate([(0,-2160,0,18),(-860,-750,780,12),(-430,-350,1700.23,18)]):
        for i in range(count):
            x=cx+random.uniform(-28,28);y=cy+random.uniform(-30,30)
            box(f'Human {group}/{i} body 1.75m',x,y,zz,.42,.30,1.45,peoplemat,PUBLIC)
            box(f'Human {group}/{i} head',x,y,zz+1.45,.25,.25,.3,peoplemat,PUBLIC)
    for x in [-32,32]:
        for y in [-2180,-2100,-2020]:
            box('Arrival bench',x,y,.1,3.0,.65,.5,white,PUBLIC)
            box('Arrival light column',x+3,y,0,.35,.35,5,light,PUBLIC)

# W0 conceptual background only. No copied M207 or M117 coordinates.
box('10km research datum',0,0,-120,10000,10000,100,land,CTX)
box('Eastern concept inland sea',3900,300,-18,2200,5200,5,water,CTX)
for k,(x,y,w,d,h) in enumerate([(-3200,4200,2100,1400,600),(-500,4500,2600,900,850),(2400,4300,2300,1400,550)]):
    # Low-poly natural ridges are contextual, excluded from architecture bounds.
    mesh(f'North context ridge {k}',[(x-w/2,y-d/2,-20),(x+w/2,y-d/2,-20),(x+w/2,y+d/2,-20),(x-w/2,y+d/2,-20),(x-w*.1,y,h)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)],land,CTX)
box('West conceptual escarpment',-4400,1000,-30,1100,4800,240,dark,CTX)
# Southwest intentionally remains empty; no local proxy for H/SB/HERO4 positions.

def camera(n,pos,target,ortho=None,lens=30):
    ca=bpy.data.cameras.new(n);ob=bpy.data.objects.new(n,ca);CAMS.objects.link(ob);ob.location=pos;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();ca.lens=lens;ca.clip_start=.08;ca.clip_end=60000
    if ortho:ca.type='ORTHO';ca.ortho_scale=ortho
    return ob
camera('00_CITY',(9000,-11500,9500),(0,300,450),14500)
camera('01_FRONT',(0,-10500,2300),(0,0,950),6200)
camera('02_OBLIQUE',(6200,-8500,5600),(-250,100,900),6600)
camera('03_SIDE',(10000,0,2300),(0,100,1000),6200)
camera('04_REAR',(-5000,9000,4300),(-200,200,950),6200)
camera('05_TOP',(0,100,14000),(0,100,0),6500)
camera('06_GROUND_A',(0,-2150,1.7),(-100,-100,690),lens=23)
camera('07_HIGH_B',(-170,680,1701.7),(100,1470,1880),lens=25)
camera('08_HALL',(170,-320,781.7),(250,470,970),lens=24)
camera('09_SECTION',(10000,-250,2300),(0,100,1000),6200)
camera('10_ALLEY',(-420-330,-600-190,781.7),(-420-330,-600+50,800),lens=28)
if o.candidate=='C':
    for n,pos,target in [('07_HIGH_B',(-430,-390,1701.93),(-80,500,1820)),('08_HALL',(-860,-800,781.7),(-860,650,900)),('10_ALLEY',(-489.2,-14,1701.95),(-489.2,23,1706))]:
        ca=bpy.data.objects[n];ca.location=pos;ca.rotation_euler=(Vector(target)-ca.location).to_track_quat('-Z','Y').to_euler()

world=bpy.data.worlds.new('Pale blue daylight');S.world=world;world.use_nodes=True;bg=world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.44,.59,.7,1);bg.inputs['Strength'].default_value=.45
ld=bpy.data.lights.new('Sun','SUN');sun=bpy.data.objects.new('Sun',ld);S.collection.objects.link(sun);sun.rotation_euler=(.45,-.5,-.45);ld.energy=3.0;ld.angle=.09
S.render.engine='CYCLES';S.cycles.samples=24 if o.detail else 12;S.cycles.use_denoising=True;S.render.threads_mode='FIXED';S.render.threads=10
S.render.resolution_x=1440 if o.detail else 1120;S.render.resolution_y=1080 if o.detail else 900;S.render.resolution_percentage=60 if o.preview else 100;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGB';S.view_settings.view_transform='AgX'
S.world.color=(.4,.5,.6);S.render.film_transparent=False
bpy.context.view_layer.update()
arch=[ob for c in [MASS,CITY,PUBLIC,ROUTE] for ob in c.objects]
def signature(obs):
    h=hashlib.sha256()
    for ob in sorted(obs,key=lambda q:q.name):
        h.update(ob.name.encode());h.update(str([list(r) for r in ob.matrix_world]).encode());h.update(str([tuple(v.co) for v in ob.data.vertices]).encode());h.update(str([tuple(p.vertices) for p in ob.data.polygons]).encode())
    return h.hexdigest()
sig=signature(arch)
pts=[ob.matrix_world@Vector(v) for ob in arch for v in ob.bound_box];lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)]
stats={'mesh_objects':len(arch),'vertices':sum(len(ob.data.vertices) for ob in arch),'polygons':sum(len(ob.data.polygons) for ob in arch),'primary_non_manifold_edges':0}
for ob in MASS.objects:
    bm=bmesh.new();bm.from_mesh(ob.data);stats['primary_non_manifold_edges']+=sum(not e.is_manifold for e in bm.edges);bm.free()
manifest={'study_id':'B2-G6','candidate':o.candidate,'stage':'OCCUPIED_3D_STUDY' if o.detail else 'MACRO_MASSING','units':'metres','geometry_sha256':sig,'bounds_m':{'min':lo,'max':hi,'size':[hi[k]-lo[k] for k in range(3)]},'geometry':stats,'halls':HALLS,'districts':DISTRICTS,'routes':ROUTES,'cameras':{ca.name:{'position_m':list(ca.location),'rotation_euler':list(ca.rotation_euler),'type':ca.data.type,'ortho_scale_m':ca.data.ortho_scale,'lens_mm':ca.data.lens} for ca in CAMS.objects},'render':{'engine':'CYCLES','samples':S.cycles.samples,'resolution':[int(S.render.resolution_x*S.render.resolution_percentage/100),int(S.render.resolution_y*S.render.resolution_percentage/100)]},'W0':'CONCEPT_BACKGROUND_UNREGISTERED_NO_COORDINATE_TRANSFORM','art_status':'CENTRAL_REVIEW_PENDING','construction':'HOLD','renders':[]}
if o.detail:
    manifest['eye_floor_checks']={}
    for n in ['06_GROUND_A','07_HIGH_B','08_HALL','10_ALLEY']:
        cam=bpy.data.objects[n];hit,p,no,idx,ob,ma=S.ray_cast(bpy.context.evaluated_depsgraph_get(),cam.location,Vector((0,0,-1)),distance=4)
        manifest['eye_floor_checks'][n]={'hit':hit,'floor':ob.name if hit else None,'floor_z_m':p.z if hit else None,'eye_height_m':cam.location.z-p.z if hit else None}
S.camera=bpy.data.objects['02_OBLIQUE'];S['research_only']='B2-G6 / art/b / no construction or formal adoption'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'study.blend'),compress=True)
# Mesh-only architectural export. Context and cameras remain in BLEND.
bpy.ops.object.select_all(action='DESELECT')
for ob in arch:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'study.glb'),use_selection=True,export_format='GLB',export_cameras=False,export_lights=False)
for n in o.views.split(','):
    if not n:continue
    # Section is derived from the same mesh via temporary object-space bisection.
    # Save original meshes and restore before any next render. Architectural BLEND/GLB are uncut.
    backup={}
    if n=='09_SECTION':
        for ob in arch:
            backup[ob]=ob.data;me=ob.data.copy();ob.data=me;bm=bmesh.new();bm.from_mesh(me)
            inv=ob.matrix_world.inverted();pp=inv@Vector((0,0,0));normal=ob.matrix_world.to_3x3().transposed()@Vector((1,0,0))
            bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.001,plane_co=pp,plane_no=normal,clear_outer=True,clear_inner=False)
            bm.to_mesh(me);bm.free()
    S.camera=bpy.data.objects[n];S.render.filepath=str(OUT/(n+'.png'));bpy.ops.render.render(write_still=True)
    for ob,me in backup.items():tmp=ob.data;ob.data=me;bpy.data.meshes.remove(tmp)
    bpy.context.view_layer.update();assert signature(arch)==sig
    manifest['renders'].append({'camera':n,'path':n+'.png','source_geometry_sha256':sig,'section_derived':n=='09_SECTION'})
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('B2-G6 COMPLETE',o.candidate,o.detail,stats,manifest['bounds_m'])
