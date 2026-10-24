"""J7-R11: original, NONCANONICAL editable Blender architectural studies.

Run only from this research folder, never from an immutable evidence directory.
Blender --background --python-exit-code 23 --python build_r11.py -- A|B [preview|all]
Meters, Z up. No Minecraft files, network access or inherited model import.
"""
import bpy
import math
import json
import random
import sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
RNG = random.Random(71125)
MODEL = None
MATS = {}


def material(name, color, metallic=0.0, roughness=.45, emission=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    if emission:
        p.inputs['Emission Color'].default_value = (*color, 1)
        p.inputs['Emission Strength'].default_value = emission
    return m


def mesh(name, verts, faces, mat='ivory', collection=None, bevel=0):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    (collection or MODEL).objects.link(obj)
    obj.data.materials.append(MATS[mat])
    obj['role'] = 'RESEARCH_ARCHITECTURE'
    if bevel:
        mod = obj.modifiers.new('Architectural edge radius', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
    return obj


def box(name, center, size, mat='ivory', collection=None, bevel=0):
    x, y, z = center
    a, b, c = [s / 2 for s in size]
    return mesh(name, [(x+u*a, y+v*b, z+w*c) for u,v,w in
                      [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),
                       (-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],
                [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),
                 (2,3,7,6),(3,0,4,7)], mat, collection, bevel)


def beam(name, a, b, width, depth=None, mat='dark'):
    a, b = Vector(a), Vector(b)
    d = b - a
    obj = box(name, (0,0,0), (width, depth or width, d.length), mat)
    obj.location = (a+b)/2
    obj.rotation_euler = d.to_track_quat('Z','Y').to_euler()
    return obj


def tube(name, points, radius, mat='gold', collection=None):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.resolution_u = 2
    data.bevel_depth = radius
    data.bevel_resolution = 2
    spl = data.splines.new('POLY')
    spl.points.add(len(points)-1)
    for p,co in zip(spl.points,points):
        p.co=(*co,1)
    ob=bpy.data.objects.new(name,data)
    (collection or MODEL).objects.link(ob)
    data.materials.append(MATS[mat])
    return ob


def loft(name, sections, mat='ivory', bevel=0):
    # Each section has the same ordered cross-section topology.
    n=len(sections[0])
    vs=[p for row in sections for p in row]
    fs=[tuple(reversed(range(n))),tuple((len(sections)-1)*n+j for j in range(n))]
    for i in range(len(sections)-1):
        for j in range(n):
            k=(j+1)%n
            fs.append((i*n+j,i*n+k,(i+1)*n+k,(i+1)*n+j))
    return mesh(name,vs,fs,mat,bevel=bevel)


def slab_polygon(name, outline, z, thickness, mat='ivory'):
    n=len(outline)
    return mesh(name,[(x,y,z) for x,y in outline]+[(x,y,z+thickness) for x,y in outline],
                [tuple(reversed(range(n))),tuple(range(n,2*n))]+
                [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat,bevel=3)


def setup(label):
    global MODEL,MATS
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.name='R11_'+label+'_NONCANONICAL_METERS'
    scene.unit_settings.system='METRIC'
    scene.unit_settings.scale_length=1
    scene['canonical_coordinates']='UNVERIFIED; origin is isolated research only'
    scene['construction']='HOLD'
    scene['formal_art_accepted']=0
    scene['city_master_complete']=False
    MODEL=bpy.data.collections.new('01_EDITABLE_ARCHITECTURE')
    scene.collection.children.link(MODEL)
    MATS={
        'ivory':material('01 | ceramic limestone / pearl',(.69,.72,.70),.18,.35),
        'silver':material('02 | champagne titanium',(.40,.49,.50),.6,.3),
        'dark':material('03 | deep graphite structure',(.035,.067,.077),.45,.39),
        'gold':material('04 | warm anodized edges',(.51,.30,.10),.65,.33),
        'glass':material('05 | deep blue inhabited recess',(.035,.14,.18),.5,.28),
        'light':material('06 | restrained civic daylight',(.30,.77,.83),.25,.3,2),
        'warm':material('07 | inhabited warm light',(.95,.55,.20),.1,.4,1.6),
        'ground':material('08 | neutral study datum',(.11,.145,.17),.05,.7),
        'garden':material('09 | planted terraces',(.10,.21,.17),.05,.9),
    }
    scene.render.engine='CYCLES'
    scene.cycles.samples=28
    scene.cycles.use_denoising=True
    try:
        p=bpy.context.preferences.addons['cycles'].preferences
        p.compute_device_type='OPTIX'
        p.get_devices()
        for d in p.devices:
            d.use=d.type=='OPTIX'
        scene.cycles.device='GPU'
    except Exception as e:
        print('GPU fallback:',e)
    scene.render.resolution_x=1440
    scene.render.resolution_y=1100
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGB'
    scene.render.film_transparent=False
    scene.view_settings.view_transform='AgX'
    world=bpy.data.worlds.new('soft blue atmospheric light')
    world.use_nodes=True
    bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND')
    bg.inputs[0].default_value=(.37,.48,.62,1)
    bg.inputs[1].default_value=.42
    scene.world=world
    env=bpy.data.collections.new('90_PRESENTATION_NOT_OFFICIAL_W0')
    scene.collection.children.link(env)
    box('unregistered 10km square study datum',(0,0,-35),(10000,10000,60),'ground',env)
    # Scale strip: real 100m intervals; restrained graphic elements, not a city proxy.
    for i in range(11):
        box('100m ground scale marker %02d'%i,(-4500+i*100,-3400,-2),(3,55,4),
            'ivory',env)
    sun_data=bpy.data.lights.new('sun','SUN')
    sun=bpy.data.objects.new('sun',sun_data)
    env.objects.link(sun)
    sun.rotation_euler=(math.radians(28),math.radians(-24),math.radians(-32))
    sun_data.energy=3.0
    sun_data.angle=math.radians(7)
    camera_data=bpy.data.cameras.new('matched research camera')
    camera=bpy.data.objects.new('matched research camera',camera_data)
    env.objects.link(camera)
    camera_data.clip_start=.1
    camera_data.clip_end=100000
    scene.camera=camera
    return scene


# A: continuous reversing continental section, not the B shear assembly.
def a_field(t):
    return -3050+6100*t, 390+2270*t*t+160*math.sin(math.pi*t), 120*math.sin(1.6*math.pi*t)


def a_band(name,t0,t1,y0,y1,lower,upper,mat='ivory',detail=True):
    rows=[]
    for i in range(55):
        t=t0+(t1-t0)*i/54
        x,h,cy=a_field(t)
        f=.68+.32*math.sin(math.pi*t)**.6
        ya=cy+y0*f
        yb=cy+y1*f
        rows.append([(x,ya,h+lower),(x,yb,h+lower+60*math.sin(math.pi*t)),
                     (x,yb,h+upper+60*math.sin(math.pi*t)),(x,ya,h+upper)])
    ob=loft(name,rows,mat,8)
    ob['design_role']='inhabited continental section; editable longitudinal stations'
    return ob


def inhabited_strip(name,points,height=110,depth=55):
    # Detailed long city sections with real recessed floors, structural mullions and planted gaps.
    for level in range(5):
        z=level*height/5
        row=[(x,y,zz+z) for x,y,zz in points]
        tube(name+' / occupied floor %02d'%level,row,2.8,'silver')
    for i in range(0,len(points)-1,2):
        x,y,z=points[i]
        beam(name+' / shear rib %03d'%i,(x,y,z),(x+12,y+5,z+height),8,depth,'ivory')
        if i%6==0:
            box(name+' / recessed lit opening %03d'%i,(x+25,y+4,z+height*.55),(9,depth+2,19),'warm')


def build_a():
    a_band('A01 | lower inhabited tectonic keel',0,1,-1470,1390,-350,-135,'silver')
    a_band('A02 | front returned continent',0,1,-1620,-670,0,460)
    a_band('A03 | rear high continent',.025,.99,420,1540,280,910)
    # Open 1.1km longitudinal civic canyon between the two upper living worlds.
    # Distinct, nonperiodic transverse connections form a floor-and-vault system.
    for j,t in enumerate([.08,.29,.53,.76,.94]):
        x,h,cy=a_field(t)
        beam('A10 | oblique deep bulkhead %d'%j,(x-130,cy-1390,h-240),
             (x+230,cy+1350,h+610),105,180,'ivory')
        beam('A11 | lower return column %d'%j,(x-100,cy-1280,max(0,h-1100)),
             (x+20,cy-1130,h-220),130,190,'dark')
    # Broad, curving urban section depths rather than little houses on a deck.
    for side,y,start,end,base in [('front',-1650,.02,.98,22),('inside',-660,.05,.94,70),
                                ('rear',1560,.04,.98,360),('canyon',440,.06,.97,380)]:
        for k in range(4):
            pts=[]
            for i in range(81):
                t=start+(end-start)*i/80
                x,h,cy=a_field(t)
                f=.68+.32*math.sin(math.pi*t)**.6
                pts.append((x,cy+y*f,h+base+k*103))
            inhabited_strip('A20 | '+side+' urban district '+str(k),pts,86,28)
    # Urban grand promenades within the canyon, not just surface patterns.
    for j,(t0,t1,yy,zz) in enumerate([(.04,.97,-500,-90),(.14,.91,200,120),(.25,.87,920,1050)]):
        a_band('A30 | public inner promenade %d'%j,t0,t1,yy-125,yy+125,zz,zz+24,'dark')
        pts=[]
        for i in range(81):
            t=t0+(t1-t0)*i/80
            x,h,cy=a_field(t)
            f=.68+.32*math.sin(math.pi*t)**.6
            pts.append((x,cy+(yy-120)*f,h+zz+29))
        tube('A31 | continuous civic light %d'%j,pts,4,'light')
    # Primary circulation climbs continuously through the returned land.
    for yy in [-1170,1110]:
        pts=[]
        for i in range(101):
            t=i/100
            x,h,cy=a_field(t)
            pts.append((x,cy+yy*(.68+.32*math.sin(math.pi*t)**.6),h+480 if yy<0 else h+930))
        tube('A40 | inhabited ridgeline transit',pts,15,'dark')
        tube('A41 | transit guideway',[(x,y,z+18) for x,y,z in pts],3,'light')
    # Turned upper crest has substantial inhabited thickness.
    for k in range(7):
        t=.84+k*.021
        x,h,cy=a_field(t)
        beam('A50 | crest sectional pier %d'%k,(x,cy+520,h+210),(x+120,cy+1200,h+950),45,70,'gold')
    public_overlook('A',(-1340,-1150,925))


# B: segmented diagonal city fault; elevation of districts is horizontal while
# perimeter and civic fissure shear obliquely. Different topology from A.
FAULTS=[
    # z, footprint (six corners). These are authored contours, not random towers.
    (100,[(-2970,-1250),(-750,-1730),(1630,-1160),(2620,340),(80,1420),(-2630,750)]),
    (660,[(-2440,-1400),(-640,-1530),(2110,-650),(2840,510),(430,1370),(-2360,870)]),
    (1240,[(-1830,-1250),(-220,-1420),(2460,-420),(2830,700),(740,1310),(-1740,1010)]),
    (1830,[(-1020,-1110),(500,-1100),(2700,-120),(2900,800),(1110,1190),(-860,1050)]),
    (2400,[(-200,-780),(960,-840),(2870,160),(2840,880),(1480,1100),(-30,1010)]),
    (2920,[(670,-450),(1610,-380),(3030,490),(2680,950),(1900,1010),(790,840)]),
]


def lerp(a,b,t):
    return tuple(x+(y-x)*t for x,y in zip(a,b))


def build_b():
    # Each city stratum is split into two joined inhabited peninsulas;
    # there is a real widening diagonal civic void, no transparent fake hole.
    for j,(z,poly) in enumerate(FAULTS):
        a,b,c,d,e,f=poly
        # Front district and rear district: unequal plans, staggered ends.
        front=[a,b,c,lerp(c,d,.27),lerp(b,e,.35),lerp(a,f,.32)]
        back=[lerp(a,f,.69),lerp(b,e,.76),lerp(c,d,.78),d,e,f]
        for side,outline in [('sunward',front),('landward',back)]:
            slab_polygon('B01 | '+side+' tectonic plinth '+str(j),outline,z,90,'silver')
            slab_polygon('B02 | '+side+' inhabited canopy '+str(j),outline,z+340,90,'ivory')
            # Occupied 5-level section as actual floors with recesses open to the sky vein.
            for level in range(1,6):
                inset=[lerp(p,tuple(sum(v[k] for v in outline)/len(outline) for k in range(2)),.025)
                       for p in outline]
                slab_polygon('B03 | '+side+' occupied urban layer %d.%d'%(j,level),
                             inset,z+level*49,9,'dark' if level%2 else 'ivory')
            for edge,(p,q) in enumerate(zip(outline,outline[1:]+outline[:1])):
                length=Vector(q).xy.length if False else math.dist(p,q)
                count=max(2,int(length/95))
                for k in range(count+1):
                    x,y=lerp(p,q,k/count)
                    beam('B04 | '+side+' city rib %d.%d.%d'%(j,edge,k),
                         (x,y,z+80),(x+20,y+13,z+350),12,24,'ivory')
                    if k%3==1:
                        box('B05 | light court %d.%d.%d'%(j,edge,k),
                            (x,y,z+165),(8,10,85),'warm')
        # Nonperiodic diagonal public crossings, 70m wide, within the fissure.
        if j in [0,2,3,5]:
            p=lerp(b,e,.33)
            q=lerp(b,e,.78)
            beam('B10 | shared civic traverse '+str(j),(p[0],p[1],z+95),
                 (q[0],q[1],z+95),22,76,'gold')
    # Deep sheared buttresses bind several strata into an asymmetrical urban continent.
    for j,(p,q,w,d) in enumerate([
        ((-2670,530,0),(-320,990,2220),230,310),
        ((-2700,-1010,0),(1930,-340,3350),190,250),
        ((450,1150,0),(2680,880,3450),260,270),
        ((1590,-920,0),(2980,480,3340),180,250),
    ]):
        beam('B20 | continuous diagonal city backbone '+str(j),p,q,w,d,'ivory')
        tube('B21 | lift inside fault '+str(j),[p,q],16,'dark')
    # A distinct diagonal crown is a thick inhabitable end of the fault.
    loft('B30 | skewed inhabited crown',[
        [(2440,-60,3140),(2910,360,3140),(2860,860,3140),(2310,620,3140)],
        [(2800,300,3600),(3100,520,3550),(2870,840,3510),(2570,660,3570)]
    ],'ivory',6)
    # Ground civic approach actually runs into the lower void.
    slab_polygon('B40 | ground portal approach',
                 [(-900,-2900),(-260,-2900),(800,600),(200,600)],0,22,'dark')
    public_overlook('B',(-850,-1300,760))


def public_overlook(label,origin):
    x,y,z=origin
    box(label+'60 | human observation concourse',(x,y,z-8),(260,180,16),'ivory')
    # Human height rail, visible only at close scale.
    for off in [-85,85]:
        tube(label+'61 | 1.1m rail',[(x-125,y+off,z+1.1),(x+125,y+off,z+1.1)],.055,'gold')
        for i in range(26):
            beam(label+'62 | rail post', (x-125+i*10,y+off,z),(x-125+i*10,y+off,z+1.1),.065,mat='gold')
    # 1.75m articulated human datum, no 100m overscaled people.
    for dx,dy in [(10,0),(12,1.4),(26,8)]:
        beam(label+'63 | human torso',(x+dx,y+dy,z+.75),(x+dx,y+dy,z+1.45),.29,mat='dark')
        box(label+'64 | human head',(x+dx,y+dy,z+1.63),(.20,.20,.24),'dark')
        for dd in [-.12,.12]:
            beam(label+'65 | human leg',(x+dx+dd,y+dy,z),(x+dx+dd,y+dy,z+.8),.12,mat='dark')


VIEWS={
 '01_FRONT':((0,-13000,2800),(0,0,1650),'ORTHO',8700),
 '02_OBLIQUE':((-9500,-11500,7600),(0,0,1650),'ORTHO',8700),
 '03_SIDE':((13500,0,2800),(0,0,1650),'ORTHO',8700),
 '04_REAR':((0,13000,2800),(0,0,1650),'ORTHO',8700),
 '05_AERIAL':((-6200,-7200,13200),(0,0,1400),'ORTHO',8700),
 '06_GROUND_HUMAN':((0,-4700,1.7),(400,0,1550),'PERSP',24),
}


def point_camera(pos,target,kind='PERSP',size=28):
    cam=bpy.context.scene.camera
    cam.location=pos
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type=kind
    if kind=='ORTHO':cam.data.ortho_scale=size
    else:cam.data.lens=size


def render_views(folder,label,preview=False,camera_overrides=None):
    scene=bpy.context.scene
    views=dict(VIEWS)
    if label=='A':
        views.update({
          '07_PUBLIC_VOID':((-1800,-290,1020),(1700,170,2450),'PERSP',22),
          '08_INHABITED_SECTION':((-1820,-2380,1170),(-670,-900,1410),'PERSP',38),
          '09_HUMAN_CONCOURSE':((-1440,-1175,926.7),(-1120,-820,1270),'PERSP',20)})
    else:
        views.update({
          '07_PUBLIC_VOID':((-1800,-150,520),(2000,500,2100),'PERSP',22),
          '08_INHABITED_SECTION':((-2020,-2370,1020),(-850,-900,1100),'PERSP',40),
          '09_HUMAN_CONCOURSE':((-950,-1330,761.7),(-650,-780,1050),'PERSP',20)})
    for name,c in (camera_overrides or {}).items():
        views[name]=(c['position_m'],c['target_m'],c['type'],c.get('ortho_scale_m',c.get('focal_length_mm',24)))
    chosen=['01_FRONT','02_OBLIQUE','03_SIDE','04_REAR'] if preview else list(views)
    manifest={}
    for name in chosen:
        pos,target,kind,scale=views[name]
        point_camera(pos,target,kind,scale)
        scene.render.filepath=str(folder/(name+'.png'))
        bpy.ops.render.render(write_still=True)
        manifest[name]={'position_m':pos,'target_m':target,'type':kind,
                        'ortho_scale_m' if kind=='ORTHO' else 'focal_length_mm':scale,
                        'resolution':[scene.render.resolution_x,scene.render.resolution_y]}
        if camera_overrides and name in camera_overrides:
            manifest[name].update(camera_overrides[name])
        print('R11_RENDER_DONE',label,name,flush=True)
    (folder/('preview_cameras.json' if preview else 'cameras.json')).write_text(
        json.dumps(manifest,indent=2),encoding='utf8')


def evidence(folder,label):
    obs=[o for o in MODEL.objects if o.type in {'MESH','CURVE'}]
    low=[float('inf')]*3
    high=[-float('inf')]*3
    vertices=faces=triangles=0
    dg=bpy.context.evaluated_depsgraph_get()
    for o in obs:
        ev=o.evaluated_get(dg)
        m=ev.to_mesh()
        vertices+=len(m.vertices)
        faces+=len(m.polygons)
        m.calc_loop_triangles()
        triangles+=len(m.loop_triangles)
        for v in m.vertices:
            p=ev.matrix_world@v.co
            for k in range(3):
                low[k]=min(low[k],p[k]);high[k]=max(high[k],p[k])
        ev.to_mesh_clear()
    result={'schema':'halo9.r11.measured.v1','concept':label,'units':'METERS',
            'coordinates':'ISOLATED_RESEARCH_NOT_CANONICAL','architecture_objects':len(obs),
            'mesh_objects':sum(o.type=='MESH' for o in obs),
            'native_curve_objects':sum(o.type=='CURVE' for o in obs),
            'evaluated_vertices':vertices,'evaluated_faces':faces,'evaluated_triangles':triangles,
            'bounds_min_m':low,'bounds_max_m':high,'span_m':[high[i]-low[i] for i in range(3)],
            'renderer':bpy.context.scene.render.engine,'blender':bpy.app.version_string,
            'construction':'HOLD','formal_art_accepted':0,
            'walkability':'UNVERIFIED','full_10km_master':False}
    (folder/'measured.json').write_text(json.dumps(result,indent=2),encoding='utf8')
    return result


def save_exports(folder,label):
    scene=bpy.context.scene
    point_camera(*VIEWS['02_OBLIQUE'])
    # Save editable bevels, curves, real floorplates. Export only architecture.
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/('R11_'+label+'.blend')),compress=True)
    bpy.ops.object.select_all(action='DESELECT')
    for o in MODEL.objects:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(folder/('R11_'+label+'.glb')),
                              export_format='GLB',use_selection=True,
                              export_apply=True,export_yup=True)
    evidence(folder,label)


def main():
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['A','preview']
    label=args[0]
    mode=args[1] if len(args)>1 else 'all'
    folder=ROOT/('concept_'+label)
    folder.mkdir(exist_ok=True)
    scene=setup(label)
    (build_a if label=='A' else build_b)()
    if mode=='preview':
        scene.render.resolution_x=1100
        scene.render.resolution_y=840
        scene.cycles.samples=16
    save_exports(folder,label)
    render_views(folder,label,mode=='preview')


if __name__=='__main__':
    main()
