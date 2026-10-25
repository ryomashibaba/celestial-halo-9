"""J7-R23: isolated background Blender sculpture, metres. No upstream writes.
Usage blender -b -t 4 --python create.py -- initial|revision|develop|render STAGE
"""
import bpy, bmesh, math, sys, json
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
MODE=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'initial'
STAGE=sys.argv[sys.argv.index('--')+2] if '--' in sys.argv and len(sys.argv)>sys.argv.index('--')+2 else MODE
for f in ['initial','revision','final','qa','sections']: (R/f).mkdir(exist_ok=True)

def savejson(path,x): (R/path).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8')
def mesh(name,vs,fs,role='architecture'):
    m=bpy.data.meshes.new(name);m.from_pydata(vs,[],fs);m.update()
    o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);o['role']=role
    bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(m);bm.free()
    o.data.materials.append(bpy.data.materials['NEUTRAL']);return o
def active(o):
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
def bevel(o,width=30):
    active(o);m=o.modifiers.new('Sculpted edge transition','BEVEL');m.width=width;m.segments=3
    bpy.ops.object.modifier_apply(modifier=m.name)
    for p in o.data.polygons:p.use_smooth=False
def box(name,c,d,role='architecture'):
    bpy.ops.mesh.primitive_cube_add(size=1,location=c);o=bpy.context.object;o.name=name;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o['role']=role;o.data.materials.append(bpy.data.materials['NEUTRAL']);return o
def cut(o,cutter):
    print('CUT',o.name,cutter.name,'before',len(o.data.vertices),len(o.data.polygons),flush=True)
    active(o);m=o.modifiers.new('Real excavated public void','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter
    bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cutter,do_unlink=True)
    print('CUT_RESULT',o.name,len(o.data.vertices),len(o.data.polygons),flush=True)
def prism(name,poly,z0,z1,role='architecture'):
    n=len(poly);vs=[(x,y,z) for z in [z0,z1] for x,y in poly]
    return mesh(name,vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],role)
def yzcut(name,poly,x0=-6000,x1=6000):
    n=len(poly);vs=[(x,y,z) for x in [x0,x1] for y,z in poly]
    return mesh(name,vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])
def spline(points,steps=7):
    out=[];p=[points[0]]+points+[points[-1]]
    for i in range(1,len(p)-2):
        for j in range(steps):
            t=j/steps
            out.append([.5*((2*p[i][k])+(-p[i-1][k]+p[i+1][k])*t+(2*p[i-1][k]-5*p[i][k]+4*p[i+1][k]-p[i+2][k])*t*t+(-p[i-1][k]+3*p[i][k]-3*p[i+1][k]+p[i+2][k])*t*t*t) for k in range(len(p[i]))])
    return out+[list(points[-1])]
def land(name,controls,role='architecture',steps=7):
    # Artist-directed plan + section: x,y, top, bottom, full width.
    pts=spline(controls,steps);vs=[]
    for i,(x,y,t,b,w) in enumerate(pts):
        v=Vector((pts[min(i+1,len(pts)-1)][0]-pts[max(0,i-1)][0],pts[min(i+1,len(pts)-1)][1]-pts[max(0,i-1)][1]))
        v.normalize();n=Vector((-v.y,v.x));h=t-b
        ring=[(-.5,t-h*.1),(-.43,t),(.38,t),(.5,t-h*.12),(.43,b+h*.25),(.18,b),(-.28,b),(-.46,b+h*.3)]
        vs.extend([(x+n.x*a*w,y+n.y*a*w,z) for a,z in ring])
    fs=[];N=8
    for i in range(len(pts)-1):
        for j in range(N):fs.append((i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j))
    fs += [tuple(reversed(range(N))),tuple((len(pts)-1)*N+j for j in range(N))]
    o=mesh(name,vs,fs,role);return o
def camera(name,pos,target,lens=38):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o)
    d.type='PERSP';d.lens=lens;d.sensor_width=36;d.sensor_fit='HORIZONTAL';d.clip_start=.1;d.clip_end=100000
    o.location=pos;o.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler();return o
def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True);s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
    m=bpy.data.materials.new('NEUTRAL');m.diffuse_color=(.52,.52,.52,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.52,.52,.52,1);p.inputs['Roughness'].default_value=.72
    s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=24;s.cycles.use_denoising=True
    s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=1440;s.render.resolution_y=960;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG';s.world=bpy.data.worlds.new('Neutral studio sky');s.world.use_nodes=True
    bg=s.world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(.38,.42,.46,1);bg.inputs[1].default_value=.65
    d=bpy.data.lights.new('SUN','SUN');d.energy=2.8;d.angle=math.radians(8);o=bpy.data.objects.new('SUN',d);s.collection.objects.link(o)
    o.rotation_euler=Vector((.5,.45,-.9)).to_track_quat('-Z','Y').to_euler()
    s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.film_transparent=False
    return s

def initial():
    s=setup()
    land('01 UPLIFTED CONTINENT',[
        (-2200,-2300,650,-180,400),(-1850,-1450,2250,-150,1250),(-1450,-100,3850,-80,1650),
        (-900,1000,4750,100,1300),(-350,2050,4100,700,850),(100,2900,3350,2050,80)])
    # A single rising public fissure, physically subtracted through the mother mass.
    cut(bpy.data.objects['01 UPLIFTED CONTINENT'],yzcut('Excavation A',[
        (-1900,600),(-1350,1450),(-200,2150),(950,2800),(2050,3150),(1700,2350),(400,1650),(-900,850)]))
    land('02 CROSSING HIGH HORIZON',[
        (-3000,1500,2900,2450,80),(-2100,900,3100,2300,1200),(-850,350,2900,2150,1500),
        (550,-250,2700,2050,1450),(1800,-1050,2520,1900,1350),(3150,-1500,2180,1820,90)])
    land('03 EAST ASCENDING WORLD',[
        (2700,-3100,250,-150,100),(2450,-2300,650,0,1100),(1850,-1300,1350,850,1250),
        (1250,-100,1820,1280,1300),(1000,1300,2250,1600,1150),(1550,2650,2400,1980,100)])
    land('04 REAR SKY BASIN',[
        (-1450,1250,3740,3150,100),(-550,1700,3590,2900,1350),(600,2100,3450,2800,1700),
        (1900,2700,3250,2650,1250),(2600,3100,3110,2750,50)])
    prism('05 GROUND DELTA WEST',[(-3600,-2800),(-1700,-3550),(-550,-2700),(-650,-800),(-300,1500),(-1000,3100),(-2800,2700),(-3000,600),(-3800,-800)],-220,80,'terrain')
    prism('06 GROUND DELTA EAST',[(700,-3300),(3200,-2950),(3750,-1100),(2700,1000),(2900,2600),(1400,3250),(350,2600),(650,850),(420,-1000)],-220,80,'terrain')
    land('07 PROCESSIONAL COMMON',[(0,-3700,80,30,700),(0,-2300,80,20,850),(0,-600,80,0,1000),(0,1100,80,0,1150),(0,2950,80,0,900)],'public_floor')
    for n,c,d in [('GROUND FLOOR',(0,-2900,65),(180,220,30)),('MID FLOOR',(1450,-650,1610),(460,620,20)),('SKY FLOOR',(650,2100,3460),(650,600,30))]:
        box(n,c,d,'public_floor')
    # Actual 1.75 m figure in each floor scene; no enlarged proxy figures.
    for x,y,z in [(0,-2893,80),(1453,-640,1620),(650,2100,3475)]:
        box('Human 1.75m',(x,y,z+.875),(.46,.3,1.75),'scale_witness')
    addcameras()
    bpy.ops.wm.save_as_mainfile(filepath=str(R/'initial/R23_INITIAL.blend'),compress=True)
    savejson('qa/INITIAL_INTENT.json',dict(phase='macro only',formal_coordinates=False,source='new R23 geometry, no original imported',unit='m',priority='ART FIRST before technical QA',dimensions='measured later',cpu_threads=4,parallel_render_processes=1))

def addcameras():
    target=Vector((0,0,2200))
    poses={'front':(0,-16500,3800),'oblique':(12500,-15000,10500),'side':(17000,0,4500),'rear':(0,17000,4500),'aerial':(7500,-8500,20000),'underside':(10000,-12000,-8500)}
    for n,p in poses.items():camera(n,p,target)
    camera('ground_1p7',(0,-2900,81.7),(-100,1800,1400),30)
    camera('mid_1p7',(1450,-650,1621.7),(-700,1700,2700),30)
    camera('high_1p7',(650,2100,3476.7),(-1200,200,3850),30)
    camera('rear_city',(2500,5400,2400),(0,1300,2600),32)

def render(stage):
    path={'initial':'initial/R23_INITIAL.blend','revision':'revision/R23_REVISED.blend','final':'final/R23_CROSSING_HORIZONS.blend'}[stage]
    bpy.ops.wm.open_mainfile(filepath=str(R/path));s=bpy.context.scene
    out=R/stage/'renders';out.mkdir(exist_ok=True)
    args=sys.argv[sys.argv.index('--')+3:];names=args or ['front','oblique','side','rear','aerial','underside','ground_1p7','mid_1p7']
    settings=[]
    for n in names:
        s.camera=bpy.data.objects[n];s.render.filepath=str(out/(n+'.png'))
        settings.append(dict(view=n,position_m=list(s.camera.location),lens_mm=s.camera.data.lens,hfov=math.degrees(2*math.atan(18/s.camera.data.lens)),neutral_material=True,emission=False,fog=False))
        print('R23_RENDER',stage,n,flush=True);bpy.ops.render.render(write_still=True)
    savejson('qa/'+stage+'_CAMERAS_'+('_'.join(names))+'.json',settings)

def revision():
    bpy.ops.wm.open_mainfile(filepath=str(R/'initial/R23_INITIAL.blend'))
    # Macro re-sculpt, not added windows: remove the three projecting fingers.
    for n in ['02 CROSSING HIGH HORIZON','03 EAST ASCENDING WORLD','04 REAR SKY BASIN']:
        bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
    core=bpy.data.objects['01 UPLIFTED CONTINENT']
    # Break the uninhabited blade into a dominant crown and interlocking concavities.
    cut(core,box('Upper canyon excavation',(-1350,200,3600),(1800,1050,450)))
    land('02 TRANSVERSE CONTINENT',[
        (-3000,1000,2600,1950,90),(-2050,650,3300,1800,1700),(-700,100,3180,1720,2200),
        (700,-650,2850,1500,2250),(2000,-1350,2360,1100,1600),(3100,-2100,1350,700,100)])
    # Two enormous courts, offset and of unlike proportion. The urban land is thick.
    trans=bpy.data.objects['02 TRANSVERSE CONTINENT']
    c=prism('Sky court mouth',[(-1100,-300),(-550,-720),(50,-850),(300,-570),(50,-170),(-600,100)],2200,4000)
    cut(trans,c)
    c=yzcut('Public crossing vault',[(-1400,1720),(-1050,2230),(-600,2430),(-100,2260),(150,2020),(-100,1720)],-400,3300)
    cut(trans,c)
    land('03 EASTERN UPLAND',[
        (2800,-3050,380,-160,100),(2550,-2200,920,0,1600),(2050,-1150,1620,300,1750),
        (1650,200,2230,1000,1800),(1700,1500,2600,1400,1450),(2300,2900,2380,1850,100)])
    east=bpy.data.objects['03 EASTERN UPLAND']
    cut(east,yzcut('East public hall',[(-1900,400),(-1450,850),(-600,1310),(150,1710),(750,1750),(900,1410),(50,1150),(-800,600)],500,3900))
    land('04 REAR SKY CONTINENT',[
        (-1650,900,3980,2950,90),(-900,1500,4150,2900,1700),(200,2100,3960,2600,2200),
        (1350,2650,3550,2400,1950),(2450,3100,2940,2300,90)])
    rear=bpy.data.objects['04 REAR SKY CONTINENT']
    cut(rear,prism('Rear open basin',[(-600,1800),(50,1550),(1050,2130),(1300,2580),(700,2800),(-350,2250)],3260,5000))
    cut(rear,yzcut('Undercontinent arcade',[(1000,2750),(1500,3200),(2000,3290),(2550,2940),(2800,2620),(2100,2640),(1400,2500)],-3000,3000))
    # Former mid sample pad is relocated to an actual open receiving forecourt.
    o=bpy.data.objects['MID FLOOR'];o.location=(1450,-650,1610)
    # Crown facets are carved into the dominant mass rather than pasted decoration.
    cut(core,prism('Crown sky incision',[(-1600,750),(-1000,1250),(-500,2050),(-350,1750),(-650,900),(-1200,400)],4060,5500))
    # Clear the real sample forecourt before judging the view; a named pad alone
    # does not make a camera in a filled terrain body an interior viewpoint.
    for obj in [east,trans]:cut(obj,box('Mid arrival court excavation',(1450,-650,2500),(700,850,1760)))
    # Remove coplanar ground pad that caused black overlap artifacts in initial.
    bpy.data.objects.remove(bpy.data.objects['GROUND FLOOR'],do_unlink=True)
    bpy.data.objects.remove(bpy.data.objects['SKY FLOOR'],do_unlink=True)
    bpy.data.objects['high_1p7'].location.z=3261.7
    for o in list(bpy.context.scene.objects):
        if o.get('role')=='scale_witness':bpy.data.objects.remove(o,do_unlink=True)
    for x,y,z in [(4,-2884,80),(1456,-634,1620),(660,2112,3260)]:box('Human 1.75m',(x,y,z+.875),(.46,.3,1.75),'scale_witness')
    camera('upper_underside',(7500,-10500,350),(0,500,2900),38)
    bpy.ops.wm.save_as_mainfile(filepath=str(R/'revision/R23_REVISED.blend'),compress=True)
    savejson('qa/MACRO_CHANGE.json',dict(trigger='Initial front: blade plus shelves, not a central civilization. Initial gate failed.',changes=['Three projecting fingers removed and rebuilt as 1.0-1.5km thick urban continents','Open high court and rear basin physically excavated','Different public voids cut through transverse and east bodies','Main blade carved at upper canyon and crown'],initial_preserved=True,detail_added=False))

def finalmacro():
    bpy.ops.wm.open_mainfile(filepath=str(R/'revision/R23_REVISED.blend'))
    bpy.data.objects.remove(bpy.data.objects['01 UPLIFTED CONTINENT'],do_unlink=True)
    # Seven separately art-directed cross sections. The central mother mass is
    # rebuilt, abandoning the initial curved blade. No facade modules are added.
    rings=[
      (0,[(-3100,-1700),(-1750,-2200),(-650,-1600),(-350,-250),(-250,1200),(-1100,2400),(-2400,2100),(-3000,500)]),
      (800,[(-2850,-1500),(-1550,-2000),(-700,-1350),(-150,-150),(0,1300),(-850,2350),(-2350,1800),(-2750,300)]),
      (1700,[(-2400,-950),(-1300,-1200),(-500,-650),(350,100),(450,1450),(-450,2400),(-1750,2000),(-2250,600)]),
      (2750,[(-2300,-100),(-1250,-550),(-100,-250),(750,650),(850,2000),(-100,2850),(-1850,2450),(-2300,1200)]),
      (3650,[(-2000,450),(-1200,100),(-200,450),(550,1400),(400,2400),(-600,2800),(-1650,2300),(-2050,1400)]),
      (4350,[(-1500,1250),(-950,650),(-200,850),(150,1600),(-200,2300),(-850,2500),(-1450,2150),(-1700,1650)]),
      (4930,[(-650,1750),(-450,1550),(-200,1700),(-70,1920),(-180,2070),(-480,2200),(-690,2110),(-780,1950)])]
    vs=[(x,y,z) for z,ring in rings for x,y in ring];fs=[]
    for i in range(len(rings)-1):
      for j in range(8):fs.append((i*8+j,i*8+(j+1)%8,(i+1)*8+(j+1)%8,(i+1)*8+j))
    fs.extend([tuple(reversed(range(8))),tuple(48+j for j in range(8))])
    core=mesh('01 FRACTURED CIVIC MASSIF',vs,fs)
    # These broad hand-shaped cross sections have non-planar side quads.
    # Resolve their intended diagonal before exact boolean evaluation.
    bm=bmesh.new();bm.from_mesh(core.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(core.data);bm.free()
    cut(core,yzcut('Great oblique public canyon',[(-2200,220),(-1700,1100),(-700,1680),(500,2320),(1850,2800),(2350,2680),(1750,2030),(400,1480),(-900,680)],-2400,1800))
    cut(core,box('Open west high court',(-1670,1550,3950),(1000,1300,1420)))
    cut(core,yzcut('Crown horizon room',[(700,3360),(1200,3700),(2000,3900),(2350,3620),(2050,3330),(1250,3160)],-2700,1000))
    cut(core,prism('Ground inhabited gorge',[(-2500,-1800),(-1600,-1400),(-1000,-500),(-1300,500),(-1900,850),(-2500,300)],80,720))
    # Remove a large part of the front of the crossing terrain. Its court
    # becomes a genuine open inlet instead of a little hole on a shelf.
    trans=bpy.data.objects['02 TRANSVERSE CONTINENT']
    cut(trans,prism('Open transverse public inlet',[(-950,-2000),(250,-2000),(300,-570),(50,-170),(-600,100),(-1100,-300)],2200,4400))
    # Front of the east mass is opened to a differently oriented public inlet.
    east=bpy.data.objects['03 EASTERN UPLAND']
    cut(east,prism('Eastern gorge',[(800,-1850),(1500,-1800),(2150,-1350),(2400,-750),(2050,-200),(1500,-350),(1150,-1000)],1040,3500))
    # The ground body is carved too; no subdivision into repeated buildings.
    gw=bpy.data.objects['05 GROUND DELTA WEST']
    cut(gw,prism('Ground delta real water cut',[(-3500,-2200),(-1800,-1800),(-1350,-650),(-1750,400),(-2250,500),(-2050,-500),(-2300,-1200),(-3650,-1600)],-500,200))
    # Correct the middle witness to the actual floor of the open transverse inlet.
    bpy.data.objects.remove(bpy.data.objects['MID FLOOR'],do_unlink=True)
    # The crossing body itself is the actual court floor at 2200m. Clear the
    # overlapping massif 10m lower so the camera cannot be buried in that body.
    cut(core,prism('Massif continuation of public inlet',[(-950,-2000),(250,-2000),(300,-570),(50,-170),(-600,100),(-1100,-300)],2190,5500))
    cam=bpy.data.objects['mid_1p7'];cam.location=(-600,-400,2201.7)
    cam.rotation_euler=(Vector((1600,1800,2520))-cam.location).to_track_quat('-Z','Y').to_euler()
    g=bpy.data.objects['ground_1p7'];g.rotation_euler=(Vector((-100,1800,800))-g.location).to_track_quat('-Z','Y').to_euler()
    for o in list(bpy.context.scene.objects):
        if o.get('role')=='scale_witness':bpy.data.objects.remove(o,do_unlink=True)
    for x,y,z in [(4,-2884,80),(-594,-388,2200),(660,2112,3260)]:box('Human 1.75m',(x,y,z+.875),(.46,.3,1.75),'scale_witness')
    # Selective close foreground scale witnesses; no windows, houses or ribs.
    for x,y,z in [(0,-2900,80),(-600,-400,2200)]:
        box('Human scale curb',(x-9,y+30,z+.3),(1,60,.6),'scale_witness')
        box('Human scale seating',(x+5,y+12,z+.23),(3,.6,.46),'scale_witness')
    bpy.ops.wm.save_as_mainfile(filepath=str(R/'final/R23_CROSSING_HORIZONS.blend'),compress=True)
    savejson('qa/SECOND_MACRO_CHANGE.json',dict(trigger='Revision still reads as a composition of smooth giant parts; second macro re-sculpt before detail.',changes=['Initial blade completely removed, new seven-section asymmetric massif built','Diagonal city-scale canyon, ground gorge, west high court and crown room cut','Transverse court opened through the front edge','East public inlet and ground water cut physically excavated'],second_stage_urban_detail_started=False,formal_adoption=False))

if MODE=='initial':initial()
elif MODE=='render':render(STAGE)
elif MODE=='revision':revision()
elif MODE=='finalmacro':finalmacro()
