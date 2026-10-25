"""R27B relative art study. Background Blender only. No source imports/world I/O.
blender -b -t 4 --python build_city.py -- build|render [camera names...]
All geometry is newly authored, metres, +X east +Y north +Z up.
"""
import bpy, bmesh, math, random, json, sys
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'model'
OUT.mkdir(exist_ok=True)
(ROOT / 'renders').mkdir(exist_ok=True)
(ROOT / 'qa').mkdir(exist_ok=True)
args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['build']
rng = random.Random(270025)
GROUP = 'TERRAIN_STUDY'

def write(name, value):
    (ROOT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf8')

def mat(name, color, metal=0, rough=.65):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    return m

def mesh(name, vs, fs, material):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    ob=bpy.data.objects.new(name,me)
    co=bpy.data.collections.get(GROUP)
    if not co: co=bpy.data.collections.new(GROUP);bpy.context.scene.collection.children.link(co)
    co.objects.link(ob);me.materials.append(material)
    ob['study_group']=GROUP;ob['placement']='PROVISIONAL_RELATIVE_ART_ONLY';return ob

def prism(name, poly, z0, z1, material):
    n=len(poly)
    return mesh(name,[(x,y,z) for z in [z0,z1] for x,y in poly],
        [tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],material)

def box(name, c, d, material, angle=0):
    x,y,z=c;w,l,h=d;co,si=math.cos(angle),math.sin(angle)
    poly=[(x+a*co-b*si,y+a*si+b*co) for a,b in [(-w/2,-l/2),(w/2,-l/2),(w/2,l/2),(-w/2,l/2)]]
    return prism(name,poly,z-h/2,z+h/2,material)

def beam(name,a,b,w,depth,material):
    a,b=Vector(a),Vector(b);v=b-a
    o=box(name,(0,0,0),(w,depth,v.length),material)
    q=v.to_track_quat('Z','Y');o.rotation_mode='QUATERNION';o.rotation_quaternion=q;o.location=(a+b)/2
    return o

def path(name, pts, w, thick, material):
    # Mitered ribbon, real thickness. Endpoints are research connections only.
    left=[];right=[]
    for i,p in enumerate(pts):
        v=Vector(pts[min(i+1,len(pts)-1)])-Vector(pts[max(i-1,0)])
        n=Vector((-v.y,v.x,0)).normalized()*w/2
        left.append(Vector(p)+n);right.append(Vector(p)-n)
    n=len(pts);top=left+right
    vs=[tuple(v-Vector((0,0,thick))) for v in top]+[tuple(v) for v in top]
    fs=[]
    for i in range(n-1):
        fs += [(2*n+i,2*n+i+1,3*n+i+1,3*n+i),(i,n+i,n+i+1,i+1),
               (i,i+1,2*n+i+1,2*n+i),(n+i,3*n+i,3*n+i+1,n+i+1)]
    fs += [(0,2*n,3*n,n),(n-1,2*n-1,4*n-1,3*n-1)]
    return mesh(name,vs,fs,material)

def tower(name, x,y,z,w,d,h,material,lean=(0,0)):
    # Five bespoke stations; chamfered profile, occupied mass rather than thin fin.
    outline=[(-.5,-.32),(-.30,-.5),(.32,-.5),(.5,-.23),(.5,.32),(.28,.5),(-.35,.5),(-.5,.22)]
    vs=[]
    for t,s in [(0,1),(.18,1.04),(.66,.83),(.88,.55),(1,.12)]:
        vs += [(x+a*w*s+lean[0]*t,y+b*d*s+lean[1]*t,z+h*t) for a,b in outline]
    fs=[tuple(reversed(range(8))),tuple(range(32,40))]
    fs += [(j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i) for j in range(4) for i in range(8)]
    return mesh(name,vs,fs,material)

def arch(name, cx,cy,z,span,rise,depth,thick,material,turn=0):
    pts=[]
    for i in range(25):
        t=math.pi*i/24;xx=span/2*math.cos(t)
        pts.append((cx+xx*math.cos(turn),cy+xx*math.sin(turn),z+rise*math.sin(t)))
    # Rectangular members individually remain editable.
    for i in range(24): beam(name+f'_{i:02}',pts[i],pts[i+1],thick,depth,material)

def courtyard(name,x,y,z,w,d,h,material,opening='south'):
    # Open courtyard with four inhabited wings, south gap is an actual gateway.
    wing=min(w,d)*.18
    box(name+'_west',(x-w/2+wing/2,y,z+h/2),(wing,d,h),material)
    box(name+'_east',(x+w/2-wing/2,y,z+h*.43),(wing,d,h*.86),material)
    box(name+'_north',(x,y+d/2-wing/2,z+h*.4),(w-wing*2,wing,h*.8),material)
    for s in [-1,1]: box(name+'_entry',(x+s*w*.31,y-d/2+wing/2,z+h*.3),(w*.2,wing,h*.6),material)
    box(name+'_court',(x,y,z+1),(w-wing*2,d-wing*2,2),PAVING)

def tree(x,y,z,size=12):
    beam('garden_trunk',(x,y,z),(x,y,z+size*.65),size*.12,size*.12,BRONZE)
    # eight-faced sculpted tree canopy, lightweight and exported with real geometry.
    vs=[(x+math.cos(i*math.pi/4)*size*.38,y+math.sin(i*math.pi/4)*size*.38,z+size*.6) for i in range(8)]
    vs += [(x,y,z+size*1.25),(x,y,z+size*.35)]
    mesh('garden_canopy',vs,[(i,(i+1)%8,8) for i in range(8)]+[(i,9,(i+1)%8) for i in range(8)],GREEN)

def apartments(name,x,y,z,w,d,h,material,angle=0):
    # Roof, facade relief and an actual sheltered ground arcade with a 5m clear height.
    box(name+'_upper',(x,y,z+6+h/2),(w,d,h),material,angle)
    box(name+'_roof',(x,y,z+6+h+1),(w+3,d+3,2),WHITE,angle)
    co,si=math.cos(angle),math.sin(angle)
    def pos(a,b,zz):return(x+a*co-b*si,y+a*si+b*co,zz)
    for side in [-1,1]:
        for a in [-w*.4,0,w*.4]: box(name+'_arcade_pier',pos(a,side*d*.38,z+3),(1.5,1.5,6),WHITE,angle)
        for zz in range(10,int(h)+4,12):
            box(name+'_inset_glazing',pos(0,side*(d/2+.1),z+zz),(w*.88,.35,3.4),GLASS,angle)

def terrain_z(x,y):
    # Authored landform hypothesis; never described as canonical W0.
    north=max(0,min(1,(y-1800)/3100))
    ridge=1150+550*math.sin(x/850)+380*math.cos(x/430+1.1)+220*math.sin(x/180)
    cliff=650/(1+math.exp((x+3420)/70))
    basin=45+45*math.sin(x/1000)*math.cos(y/1200)
    sea=-150/(1+math.exp(-(x-1950)/160))
    return basin+cliff+sea+north*north*ridge+38*math.sin(x/190+y/270)*north

def build():
    global GROUP, WHITE,DARK,BRONZE,GLASS,GREEN,PAVING,WATER,ROCK,SAND
    bpy.ops.wm.read_factory_settings(use_empty=True)
    WHITE=mat('Ivory ceramic / study',(.66,.70,.67),.28,.37)
    DARK=mat('Blue titanium',(.075,.13,.16),.65,.4)
    BRONZE=mat('Warm structural alloy',(.33,.22,.105),.65,.4)
    GLASS=mat('Deep teal glazing',(.065,.21,.23),.55,.28)
    GREEN=mat('Garden vegetation',(.11,.22,.13),0,.9)
    PAVING=mat('Pale civic stone',(.43,.45,.40),.08,.7)
    WATER=mat('Inland sea',(.065,.22,.25),.4,.24)
    ROCK=mat('Basalt mountain',(.20,.265,.27),0,.9)
    SAND=mat('Basin mineral ground',(.33,.34,.285),0,.95)
    GROUP='TERRAIN_STUDY'
    n=121;vs=[];fs=[]
    for j in range(n):
        for i in range(n):
            x=-5400+i*90;y=-5400+j*90;vs.append((x,y,terrain_z(x,y)))
    for j in range(n-1):
        for i in range(n-1):
            a=j*n+i;fs += [(a,a+1,a+n+1),(a,a+n+1,a+n)]
    ground=mesh('New hypothetical basin / NOT W0 source',vs,fs,SAND)
    ground.data.materials.append(ROCK);ground.data.materials.append(GREEN)
    for p in ground.data.polygons:
        c=p.center
        # polygon centers update after from_pydata
        heights=[ground.data.vertices[i].co.z for i in p.vertices]
        p.material_index=1 if max(heights)>450 else (2 if rng.random()<.12 and max(heights)>80 else 0)
    prism('Artificial inland sea study',[(1950,-5200),(5350,-5200),(5350,3900),(3600,3400),(2300,1800),(1850,-600)],-85,-78,WATER)
    # Long inhabited western escarpment terraces, not a blank cliff facade.
    GROUP='WEST_ESCARPMENT_PUBLIC_STUDY'
    for j,(y,l,z) in enumerate([(-850,1100,270),(450,1250,440),(1950,1000,610)]):
        box('Cliff concourse',(-3400,y,z-16),(240,l,32),PAVING)
        for i in range(5):
            apartments(f'cliff_{j}_{i}',-3530,y-l*.38+i*l*.18,z,100,115,60+30*(i%3),DARK)
        path('Escarpment rail',[(-3260,y-l/2,z+10),(-3260,y+l/2,z+10)],12,5,BRONZE)
    # Central civic arrival, long axis open to the south.
    GROUP='CENTRAL_CIVIC_GROUND'
    arrival=prism('ENTRY_PROMENADE_REAL_FLOOR',[(-180,-2220),(180,-2220),(300,-650),(-300,-650)],125,145,PAVING)
    box('NAVE_REAL_FLOOR',(0,200,146),(680,2050,22),PAVING)
    # Long reflecting channels leave a walkable center.
    for s in [-1,1]:box('Civic water channel',(s*210,-1400,147),(36,950,2),WATER)
    for s in [-1,1]:
        for y in [-2040,-1850,-1660,-1470,-1280,-1090]:
            tree(s*125,y,145,18)
            box('Stone bench',(s*105,y+18,145.5),(4,1.2,1),WHITE)
    # Central mass: two inhabited banks and a rising split spine.
    GROUP='CENTRAL_INHABITED_BANKS'
    central_specs=[(-860,-350,155,630,900,1040,(-220,120)),
                   (-980,620,150,750,950,1800,(-150,180)),
                   (-530,1300,145,620,700,2650,(190,110)),
                   (580,1100,145,710,870,2210,(260,-160)),
                   (900,160,155,680,1060,1380,(220,80)),
                   (810,-680,150,520,590,740,(70,-100))]
    for i,(x,y,z,w,d,h,lean) in enumerate(central_specs):
        tower(f'Central occupied bank {i+1}',x,y,z,w,d,h,WHITE if i%2==0 else DARK,lean)
        # Only a few deep vertical structural reveals: avoid R19 horizontal shelving.
        for k in [-.28,0,.28]:
            beam('Bank bronze reveal',(x+k*w,y-d*.49,z+80),(x+k*w+lean[0]*.7,y-d*.33+lean[1]*.7,z+h*.76),12,18,BRONZE)
    # Public nave comprises real structural arches, open walls and separate roof portions.
    GROUP='CENTRAL_PUBLIC_NAVE'
    for y,span,rise in [(-700,770,590),(-300,920,760),(150,1050,950),(660,980,1020)]:
        arch('Nave structural arch',0,y,157,span,rise,85,44,WHITE)
    path('Western nave canopy',[(-360,-730,610),(-430,-200,790),(-460,400,985),(-370,950,1120)],190,40,DARK)
    path('Eastern nave canopy',[(360,-730,610),(430,-200,790),(460,400,985),(370,950,1120)],175,38,WHITE)
    # Tapered displaced crown, two unequal inhabited masses rather than ring stacks.
    tower('Displaced high civic citadel',-110,1540,1840,520,620,1260,WHITE,(360,0))
    tower('Celestial spine',130,1710,1520,240,370,1820,DARK,(110,80))
    beam('Crown structural bridge',(-420,1300,2130),(520,1150,1990),110,180,BRONZE)
    box('High public hall floor',(-30,1250,2110),(750,340,34),PAVING)
    for x in [-350,330]:beam('High hall pier',(x,1250,2110),(x+75,1250,2370),30,30,WHITE)
    path('High hall roof',[(-340,1250,2370),(0,1250,2490),(410,1250,2370)],350,24,WHITE)
    # Central populated shoulders are spatially different courtyards, not full facade scatter.
    GROUP='CENTRAL_REPRESENTATIVE_QUARTERS'
    for i,(x,y,z,w,d,h) in enumerate([(-1120,-950,155,500,420,120),(-1400,150,155,420,640,180),(1220,-490,155,420,500,155),(1310,600,155,600,420,130)]):
        box('Quarter ground',(x,y,z-20),(w+60,d+60,40),DARK)
        courtyard('Central court '+str(i),x,y,z,w,d,h,WHITE)
    # Six individually composed sky-district prototypes. No official H-number mapping.
    # Different footprints, orientation, public section, base thickness, and street grain.
    districts=[
        ('A_RIDGE',(-2550,1550,1100),[(-850,-240),(-300,-460),(680,-170),(850,200),(170,350),(-700,290)],170),
        ('B_CASCADE',(-2150,-500,690),[(-700,-430),(300,-520),(680,-100),(470,490),(-460,300)],240),
        ('C_HARBOR',(2380,-1050,740),[(-650,-400),(800,-250),(940,130),(150,440),(-670,250)],200),
        ('D_CULTURE',(1850,1760,1270),[(-650,-490),(580,-550),(810,170),(260,570),(-650,410)],230),
        ('E_HIGH',(0,3220,1820),[(-850,-170),(-320,-480),(560,-300),(700,240),(-190,420),(-680,220)],280),
        ('F_REVERSE',(-1700,3100,1470),[(-570,-550),(430,-400),(690,140),(220,610),(-590,310)],220)]
    manifest=[]
    for idx,(name,(x,y,z),poly,thick) in enumerate(districts):
        GROUP='SKY_PROTOTYPE_'+name
        # Sloped undercroft: distinct bottom outline in real solid geometry.
        n=len(poly);vs=[(x+a*.6,y+b*.6,z-thick) for a,b in poly]+[(x+a,y+b,z) for a,b in poly]
        mesh(name+'_city_ground',vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],DARK)
        prism(name+'_public_surface',[(x+a,y+b) for a,b in poly],z,z+4,PAVING)
        # Broad real public street crosses district, calibrated for human-scale view C.
        path(name+'_main_street',[(x-500,y,z+5),(x,y,z+5),(x+540,y+80,z+5)],38,3,WHITE)
        if idx==0:
            for k in range(5):
                courtyard('Ridge residential court',x-520+k*230,y+60*(k%2),z+4,190,200,90+k*19,WHITE)
            tower('Ridge civic needle',x+610,y+120,z+4,140,180,420,WHITE,(80,0))
        elif idx==1:
            # Three offset inhabited stair districts, not circular disk copies.
            for k,(dx,dy,h) in enumerate([(-400,-220,75),(0,160,140),(330,-200,225)]):
                courtyard('Cascade court',x+dx,y+dy,z+4,270,220,h,WHITE)
                path('Cascade sloped street',[(x+dx-80,y+dy-130,z+4),(x+dx+80,y+dy+130,z+4)],22,4,BRONZE)
        elif idx==2:
            # Harbor linear street and two open public hangars; no ship icon.
            for k in range(6):
                apartments('Harbor residence',x-450+k*200,y+180,z+4,120,90,55+12*(k%3),WHITE)
                apartments('Harbor arcade',x-450+k*200,y-200,z+4,100,80,38+8*(k%2),DARK)
            for xx in [-270,280]:
                arch('Harbor canopy',x+xx,y+40,z+4,210,140,170,14,BRONZE)
        elif idx==3:
            for dx in [-380,380]:courtyard('Culture living court',x+dx,y,z+4,240,620,170,WHITE)
            arch('Culture opera vault',x,y+260,z+4,520,350,230,24,WHITE)
            box('Culture open civic room',(x,y+230,z+4),(470,260,8),PAVING)
        elif idx==4:
            courtyard('High garden inhabited court',x-240,y+40,z+4,620,520,210,WHITE)
            tower('High school citadel',x+390,y+110,z+4,220,230,360,BRONZE,(60,-50))
            path('High garden diagonal',[(x-550,y-180,z+5),(x+350,y-200,z+5),(x+510,y+180,z+5)],44,4,WHITE)
        else:
            for dx,dy,w,d,h in [(-320,-180,220,310,180),(110,230,470,240,110),(330,-180,190,270,260)]:
                courtyard('Reverse living courtyard',x+dx,y+dy,z+4,w,d,h,WHITE)
            box('Undercroft public station',(x,y-200,z-thick+35),(470,150,65),BRONZE)
            path('Undercroft arrival',[(x-480,y-420,z-thick+5),(x,y-420,z-thick+5)],55,12,WHITE)
        for k in range(10):
            xx=x-400+k*85;yy=y-100
            tree(xx,yy,z+4,16+idx)
        # Visible underside is subdivided structural/service space, still not completed internal city.
        for dx in [-300,150,400]:
            beam('Underside buttress',(x+dx,y-220,z-10),(x+dx*.6,y+180,z-thick+10),30,42,BRONZE)
        manifest.append({'prototype':name,'official_H_assignment':None,'origin_m':[x,y,z],'ground_thickness_m':thick,'status':'PARTIAL_RESEARCH_NOT_DISTRICT_COMPLETE'})
    write('qa/SKY_PROTOTYPES.json',manifest)
    # Four distinct secondary landmark investigations, deliberately not registered SB replacements.
    GROUP='FOUR_UNASSIGNED_SECONDARY_LANDMARKS'
    tower('Sail citadel analogue / unassigned',3400,650,80,470,670,930,WHITE,(-260,60))
    tower('Sail companion',3660,800,80,160,400,530,BRONZE,(-180,50))
    for x,z in [(1000,180), (1430,240)]:
        arch('Twin vault analogue / unassigned',x,-2700,z,570,420,270,35,WHITE,turn=.25)
        box('Twin vault public floor',(x,-2700,z-10),(520,280,20),PAVING,.25)
    # Gateway is an actual passage between solid inhabited pylons, clear at grade.
    for x in [-340,340]:tower('Gateway occupied pylon / unassigned',x,-3020,80,210,260,600,WHITE,(-x*.3,0))
    beam('Gateway lintel',(-270,-3020,570),(270,-3020,570),110,150,BRONZE)
    path('Gateway arrival floor',[(0,-3300,145),(0,-2200,145)],160,20,PAVING)
    for i in range(3):
        xx=2100+i*250;yy=3520-i*160;zz=terrain_z(xx,yy)+15
        tower('Mountain sanctuary analogue / unassigned',xx,yy,zz,190,270,490-i*90,WHITE,(0,-100))
    # Three research alignments and a branching transportation skeleton.
    GROUP='RESEARCH_TRANSIT_NOT_OFFICIAL_AXES'
    routes=[('West ascent',[(-3260,100,450),(-2500,-500,695),(-1300,-730,400),(-400,-730,157)]),
            ('East harbor',[ (400,-780,157),(1400,-1100,420),(2380,-1050,745),(3300,-900,600)]),
            ('North high',[(-120,1500,1850),(0,2400,1825),(0,3220,1825)]),
            ('Culture branch',[(400,800,900),(1400,1500,1275),(1850,1760,1275)]),
            ('Ridge approach',[(-1100,800,1105),(-2550,1550,1105)]),
            ('Reverse approach',[(-2550,1550,1105),(-2300,2400,1475),(-1700,3100,1475)])]
    for name,pts in routes:
        path(name+' transit viaduct',pts,38,20,DARK)
        path(name+' transit guideway',[(x,y,z+2) for x,y,z in pts],7,2,BRONZE)
        for x,y,z in pts[1:-1]:
            base=terrain_z(x,y)
            beam(name+' pier',(x,y,base),(x,y,z-20),35,45,WHITE)
    write('qa/TRANSIT_LIMITS.json',{'routes':[{'name':n,'polyline_m':p} for n,p in routes],
        'status':'GEOMETRIC_INTENT_ONLY_NOT_WALKABLE_OR_OPERATION_CERTIFIED','official_axes_or_V_assignment':None})
    # Representative street close to the entry: arcade, shops, people, benches.
    GROUP='HUMAN_SCALE_REPRESENTATIVE_STREET'
    box('PLAZA_REAL_FLOOR',(-480,-1830,144),(510,500,22),PAVING)
    for x,y,w,d,h in [(-695,-1980,90,110,46),(-695,-1800,90,130,64),(-685,-1600,110,110,85),(-350,-1610,90,120,50)]:
        apartments('Arrival mixed use',x,y,155,w,d,h,WHITE)
    for k in range(8):tree(-570,-2020+k*49,155,14)
    # Human figures are simple real silhouette meshes, not photoreal inhabitants.
    for x,y,z in [(-460,-1900,155),(-455,-1898,155),(-488,-1880,155),(-482,-1840,155),(45,-1960,145),(50,-1958,145),(1870,-1340,744),(1875,-1338,744)]:
        beam('Human 1.75m',(x,y,z),(x,y,z+1.38),.38,.25,DARK)
        box('Human head',(x,y,z+1.59),(.27,.25,.32),DARK)
    setup_scene()
    cameras()
    bpy.context.scene['disclaimer']='ALL PROVISIONAL RELATIVE ART STUDY. NOT W0/H/SB MASTER. NO MINECRAFT COORDINATES.'
    bpy.context.scene['source_geometry']='New R27B only. No old meshes imported or scaled.'
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'R27B_LIVING_HORIZONS.blend'),compress=True)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.context.scene.objects:
        if ob.type=='MESH':ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(OUT/'R27B_LIVING_HORIZONS.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
    write('qa/BUILD.json',{'blender':bpy.app.version_string,'mesh_count':sum(o.type=='MESH' for o in bpy.context.scene.objects),'seed':270025,
         'base_head':'61608a286922e296ffc129f844fe0e700dae0518','canonical_coordinate_transform':None,
         'facility_status':'4 unassigned analogues only; SB01-SB16 formal models and interiors NOT produced',
         'art_status':'PENDING_RENDER_REVIEW','scene_units':'metres +X east +Y north +Z up, study origin only'})
    print('R27B_BUILD_FINISHED',flush=True)

def setup_scene():
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=20;sc.cycles.use_denoising=True
    sc.render.threads_mode='FIXED';sc.render.threads=4
    sc.render.resolution_x=1440;sc.render.resolution_y=960;sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
    sc.world=bpy.data.worlds.new('Clear pale atmosphere');sc.world.use_nodes=True
    nodes=sc.world.node_tree.nodes;bg=nodes.get('Background');bg.inputs[0].default_value=(.50,.65,.75,1);bg.inputs[1].default_value=.65
    light=bpy.data.lights.new('Late morning sun','SUN');light.energy=2.5;light.angle=.16
    ob=bpy.data.objects.new('Late morning sun',light);sc.collection.objects.link(ob);ob.rotation_euler=(math.radians(28),math.radians(-22),math.radians(-28))
    sc.view_settings.view_transform='AgX';sc.view_settings.exposure=.1
    sc.render.image_settings.color_mode='RGB'

def cameras():
    specs=[
      ('01_SW_VOID',(-10500,-11500,5700),(0,500,900),39,None),
      ('02_EAST_SEA',(10900,-5000,3200),(0,600,1000),40,None),
      ('03_NORTH_HIGHLAND',(2500,9100,4300),(0,400,700),36,None),
      ('04_CENTRAL_OBLIQUE',(-5200,-7100,3650),(0,700,1250),38,None),
      ('05_ENTRY_HUMAN',(24,-2010,146.7),(0,600,700),24,'ENTRY_PROMENADE_REAL_FLOOR'),
      ('06_PUBLIC_PLAZA',(-470,-1940,156.7),(200,-100,520),26,'PLAZA_REAL_FLOOR'),
      ('07_SKY_HARBOR',(1870,-1350,745.7),(-200,700,1400),24,'C_HARBOR_public_surface'),
      ('08_REAR_UNDERSIDE',(-1450,3990,1130),(0,1000,1600),28,None),
      ('09_WHOLE_AERIAL',(9300,-11700,13500),(0,400,400),39,None)]
    audit=[];dg=bpy.context.evaluated_depsgraph_get()
    for name,pos,target,lens,floor in specs:
        data=bpy.data.cameras.new(name);ob=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(ob)
        ob.location=pos;ob.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler();data.lens=lens;data.clip_start=.1;data.clip_end=65000
        row={'name':name,'position_m':pos,'target_m':target,'lens_mm':lens,'floor_claim':None,'camera_kind':'AERIAL_OR_FLOATING_STUDY_VIEW'}
        if floor:
            hit,loc,normal,face,obhit,_=bpy.context.scene.ray_cast(dg,Vector(pos),Vector((0,0,-1)),distance=5)
            row.update({'down_ray_hit':bool(hit),'hit_object':obhit.name if hit else None,'hit_m':list(loc) if hit else None,'eye_above_floor_m':pos[2]-loc.z if hit else None})
            assert hit and obhit.name==floor and abs(pos[2]-loc.z-1.7)<.01,(name,row)
            row['floor_claim']='REAL_STUDY_FLOOR_1.7m_NOT_ROUTE_CERTIFICATION';row['camera_kind']='SUPPORTED_HUMAN_VIEW'
        audit.append(row)
    write('qa/CAMERAS.json',audit)

def render():
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'R27B_LIVING_HORIZONS.blend'))
    sc=bpy.context.scene
    names=args[1:] or ['01_SW_VOID','02_EAST_SEA','03_NORTH_HIGHLAND','04_CENTRAL_OBLIQUE','05_ENTRY_HUMAN','06_PUBLIC_PLAZA','07_SKY_HARBOR','08_REAR_UNDERSIDE','09_WHOLE_AERIAL']
    for name in names:
        sc.camera=bpy.data.objects[name];sc.render.filepath=str(ROOT/'renders'/f'{name}.png')
        print('RENDER_START',name,flush=True);bpy.ops.render.render(write_still=True);print('RENDER_DONE',name,flush=True)

if args[0]=='build':build()
elif args[0]=='render':render()
else:raise ValueError(args)
