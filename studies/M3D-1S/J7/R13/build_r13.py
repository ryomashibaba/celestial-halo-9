"""R13 independent metre-space study. No upstream assets/worlds are read.
Run in Blender. Initial explorations only; revisions are separate observed edits.
"""
import bpy, math, json, sys
sys.dont_write_bytecode=True
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
PROMPT='それでは既存ローカル環境を確認し、J7-R13のBlender制作を開始してください。'

def material(name,color,metal=.0,rough=.55,emission=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    if emission:
        p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
    return m

def mesh(name,verts,faces,mat,collection=None,bevel=0):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);(collection or ARCH).objects.link(ob)
    if mat:me.materials.append(mat)
    if bevel:
        mod=ob.modifiers.new('Soft edges of inhabited mass','BEVEL');mod.width=bevel;mod.segments=2
    return ob

def prism(name,poly,z0,z1,mat,bevel=0):
    n=len(poly);v=[(x,y,z) for z in (z0,z1) for x,y in poly]
    f=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    f += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,v,f,mat,bevel=bevel)

def box(name,loc,size,mat,bevel=0,collection=None):
    x,y,z=loc;a,b,c=[s/2 for s in size]
    v=[(x+u*a,y+v*b,z+w*c) for w in (-1,1) for v in (-1,1) for u in (-1,1)]
    return mesh(name,v,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],mat,collection,bevel)

def beam(name,a,b,width,depth,mat):
    a,b=Vector(a),Vector(b);d=b-a
    ob=box(name,(a+b)/2,(width,depth,d.length),mat,4)
    # box vertices were in world space: move them local before rotation
    center=(a+b)/2
    for v in ob.data.vertices:v.co-=center
    ob.location=center;ob.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    return ob

def ring(name,outer,inner,z0,z1,mat,skip=()):
    obs=[];n=len(outer)
    for i in range(n):
        if i in skip:continue
        j=(i+1)%n
        obs.append(prism(name+f'_{i:02}',[outer[i],outer[j],inner[j],inner[i]],z0,z1,mat,5))
    return obs

PLAN=[(-.74,-1),(.42,-1),(.93,-.53),(1,.29),(.48,.93),(-.37,1),(-1,.40),(-1,-.45)]
def district(label,center,rx,ry,h,rot=0,open_edges=(0,2),roof=True,kind='TIDAL'):
    """A district is a 3D public courtyard + 140-260m deep inhabitable rim.
    No solid fictitiously labelled habitable: all large galleries have real voids.
    """
    x,y,z=center;c,s=math.cos(rot),math.sin(rot)
    def pt(a,b):return (x+c*a-s*b,y+s*a+c*b)
    outer=[pt(a*rx,b*ry) for a,b in PLAN]
    inner=[pt(a*rx*.54,b*ry*.54) for a,b in PLAN]
    prefix=label+'__'
    ring(prefix+'thick_city_ground',outer,inner,z,z+115,STONE)
    ring(prefix+'upper_inhabited_ground',outer,inner,z+h-130,z+h,PEARL,skip=(3,) if not roof else ())
    # Segmented district-depth galleries, with large apertures, not window copies.
    for i in range(8):
        j=(i+1)%8
        p,q=Vector(outer[i]),Vector(outer[j]);u,v=Vector(inner[i]),Vector(inner[j])
        def patch(t0,t1,z0,z1,mat,name):
            prism(prefix+name+f'_{i}',[p.lerp(q,t0),p.lerp(q,t1),u.lerp(v,t1),u.lerp(v,t0)],z0,z1,mat,4)
        if i in open_edges:
            patch(0,.12,z+115,z+h-130,STONE,'opening_west_jamb')
            patch(.88,1,z+115,z+h-130,STONE,'opening_east_jamb')
        else:
            patch(0,.27,z+115,z+h-130,PEARL,'deep_living_buttress')
            patch(.66,1,z+115,z+h-130,PEARL,'deep_civic_buttress')
            patch(.27,.66,z+115,z+195,STONE,'gallery_lower_world')
            patch(.27,.66,z+h-220,z+h-130,STONE,'gallery_upper_world')
        # inset transport landing has open air above and below
        if i in (1,4,6):
            patch(.12,.8,z+240,z+267,BRONZE,'public_transfer_ground')
    # The courtyard itself contains different ground/biome fragments, not houses.
    if kind=='TIDAL':
        poly=[pt(a*rx*.47,b*ry*.47) for a,b in PLAN]
        prism(prefix+'inner_water_basin',poly,z+68,z+79,WATER)
    elif kind=='GROVE':
        for j,(a,b,w) in enumerate([(-.12,-.2,.27),(.18,.16,.22)]):
            poly=[pt((a+px*w)*rx,(b+py*w)*ry) for px,py in PLAN]
            prism(prefix+f'cultivation_topography_{j}',poly,z+80,z+135,GREEN,5)
    else:
        poly=[pt(a*rx*.4,b*ry*.4) for a,b in PLAN]
        prism(prefix+'assembly_basin',poly,z+72,z+90,STONE,3)
    obnames=[o.name for o in ARCH.objects if o.name.startswith(prefix)]
    for name in obnames:bpy.data.objects[name]['district']=label
    DISTRICTS.append(dict(label=label,center_m=list(center),radii_m=[rx,ry],height_m=h,
                          central_court_nominal_width_m=[rx*1.08,ry*1.08],role=kind,objects=obnames))

def setup():
    global ARCH,CONTEXT,PEARL,STONE,BRONZE,WATER,GREEN,LIGHT,DISTRICTS
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ARCH=bpy.data.collections.new('R13_EDITABLE_CITY');bpy.context.scene.collection.children.link(ARCH)
    CONTEXT=bpy.data.collections.new('PRESENTATION_ONLY');bpy.context.scene.collection.children.link(CONTEXT)
    PEARL=material('Mineral silver ceramic',(.64,.72,.72),.32,.48)
    STONE=material('Dark structural city strata',(.10,.17,.20),.25,.58)
    BRONZE=material('Warm alloy transfer grounds',(.40,.25,.13),.5,.45)
    WATER=material('Tidal civic reservoirs',(.035,.34,.39),.45,.26)
    GREEN=material('Cultivated world ground',(.16,.27,.19),.0,.88)
    LIGHT=material('Soft navigation light',(.38,.82,.88),.1,.4,2)
    DISTRICTS=[]
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=1200;sc.render.resolution_y=1000;sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
    sc.world=bpy.data.worlds.new('Cool neutral daylight');sc.world.use_nodes=True
    bg=next(n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.20,.29,.39,1);bg.inputs[1].default_value=.5
    sc.view_settings.view_transform='AgX'
    for name,loc,energy,color,angle in [('Sun',(0,0,8000),2.5,(1,.87,.72),(.5,-.4,-.65)),('Sky fill',(0,0,9000),1.4,(.60,.78,1),(.6,.4,2.3))]:
        ld=bpy.data.lights.new(name,'SUN');ld.energy=energy;ld.color=color;ld.angle=.15
        ob=bpy.data.objects.new(name,ld);CONTEXT.objects.link(ob);ob.rotation_euler=angle
    groundmat=material('Neutral test datum not W0',(.055,.085,.115),.1,.8)
    box('Neutral datum NOT W0',(0,0,-65),(14000,14000,100),groundmat,collection=CONTEXT)
    # 100m scale marks on the datum, restrained and physically present
    for j in range(-5,6):
        box('Datum 1km scale marker '+str(j),(j*1000,-3600,-10),(8,100,6),BRONZE,collection=CONTEXT)
    cd=bpy.data.cameras.new('R13 review camera');cam=bpy.data.objects.new('R13 review camera',cd);CONTEXT.objects.link(cam);sc.camera=cam
    cd.clip_start=.3;cd.clip_end=60000

def attach_existing():
    global ARCH,CONTEXT,PEARL,STONE,BRONZE,WATER,GREEN,LIGHT,DISTRICTS
    ARCH=bpy.data.collections['R13_EDITABLE_CITY'];CONTEXT=bpy.data.collections['PRESENTATION_ONLY']
    PEARL=bpy.data.materials['Mineral silver ceramic'];STONE=bpy.data.materials['Dark structural city strata']
    BRONZE=bpy.data.materials.get('Warm alloy transfer grounds') or material('Warm alloy transfer grounds',(.40,.25,.13),.5,.45)
    WATER=bpy.data.materials.get('Tidal civic reservoirs') or material('Tidal civic reservoirs',(.035,.34,.39),.45,.26)
    GREEN=bpy.data.materials.get('Cultivated world ground') or material('Cultivated world ground',(.16,.27,.19),0,.88)
    LIGHT=bpy.data.materials.get('Soft navigation light') or material('Soft navigation light',(.38,.82,.88),.1,.4,2)
    DISTRICTS=json.loads(bpy.context.scene.get('district_specifications','[]'))

VIEWS={
 '01_FRONT':((0,-13000,2350),(0,0,2300),'ORTHO',8100),
 '02_OBLIQUE':((9800,-13000,8200),(0,0,2200),'ORTHO',8100),
 '03_SIDE':((14000,0,2300),(0,0,2300),'ORTHO',8100),
 '04_REAR':((0,14000,2400),(0,0,2300),'ORTHO',8100),
 '05_AERIAL':((5000,-6200,15000),(0,0,2200),'ORTHO',8100),
 '06_GROUND':((350,-6400,1.7),(0,0,2000),'PERSP',20),
}
def camera(view):
    loc,target,typ,value=view;cam=bpy.context.scene.camera;cam.location=loc
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type=typ
    if typ=='ORTHO':cam.data.ortho_scale=value
    else:cam.data.lens=value
    return dict(location_m=list(loc),target_m=list(target),projection=typ,value=value)

def render(folder,views=None):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    records=json.loads((folder/'cameras.json').read_text(encoding='utf8')) if (folder/'cameras.json').exists() else {}
    for name,v in (views or VIEWS).items():
        records[name]=camera(v);bpy.context.scene.render.filepath=str(folder/(name+'.png'))
        bpy.ops.render.render(write_still=True);print('RENDER_DONE',name,flush=True)
    (folder/'cameras.json').write_text(json.dumps(records,indent=2),encoding='utf8')

def save(folder,stem):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    camera(VIEWS['02_OBLIQUE'])
    for ar in bpy.context.screen.areas if bpy.context.screen else []:
        if ar.type=='VIEW_3D':
            ar.spaces.active.clip_end=60000;ar.spaces.active.region_3d.view_perspective='CAMERA'
            ar.spaces.active.overlay.show_overlays=False
    bpy.context.scene['R13_RESEARCH_ONLY']=True
    bpy.context.scene['canonical_adoption']='NONE';bpy.context.scene['construction']='HOLD'
    bpy.context.scene['district_specifications']=json.dumps(DISTRICTS)
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/(stem+'.blend')),compress=True)
    bpy.ops.object.select_all(action='DESELECT')
    for o in ARCH.objects:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(folder/(stem+'.glb')),use_selection=True,export_format='GLB',export_cameras=False,export_lights=False,export_apply=True)
    (folder/'districts.json').write_text(json.dumps(DISTRICTS,indent=2),encoding='utf8')

def build_A():
    setup()
    # Open contiguous atmospheric canyon. No macro skin exists outside districts.
    specs=[
     ('A01_TIDE_ROOT',(-1550,-200,0),1000,1100,850,-.18,(0,2),'TIDAL'),
     ('A02_SEED_ROOT',(1180,380,0),950,1100,1050,.22,(0,6),'GROVE'),
     ('A03_MEMORY_DEPTH',(-270,1050,580),1080,850,940,-.08,(0,7),'COMMON'),
     ('A04_WEST_SKY',(-1790,80,740),850,900,1000,.1,(0,2),'GROVE'),
     ('A05_EAST_TIDE',(1550,480,920),1050,930,900,-.26,(0,6),'TIDAL'),
     ('A06_INNER_CONFLUENCE',(-650,1250,1490),1050,900,970,.12,(0,1),'COMMON'),
     ('A07_OUTER_WEST',(-1750,220,1670),810,1000,950,-.2,(0,2),'COMMON'),
     ('A08_HIGH_GARDEN',(1200,800,1780),990,1000,1070,.32,(0,6),'GROVE'),
     ('A09_SKY_TIDE',(-1050,650,2520),1050,950,950,-.15,(0,2),'TIDAL'),
     ('A10_EAST_CROWN',(1000,830,2750),850,850,970,.18,(0,6),'COMMON'),
     ('A11_ZENITH',(-530,950,3400),1050,800,1080,-.1,(0,2),'GROVE'),
    ]
    for name,c,rx,ry,h,r,op,k in specs:district(name,c,rx,ry,h,r,op,True,k)

def vaulted_world(label,c,rx,depth,rz,tilt=0):
    # Closed meridional sky, unlike A's stacked open courtyards.
    x,y,z=c;n=16;ct,st=math.cos(tilt),math.sin(tilt)
    def p(t,d,fac=1):
        a=rx*math.cos(t)*fac;b=rz*math.sin(t)*fac
        return (x+ct*a+st*b,y+d,z-st*a+ct*b)
    for i in range(n):
        a=2*math.pi*i/n;b=2*math.pi*(i+1)/n
        # shell is an inhabited district-depth chamber between two radial layers
        v=[p(t,d,f) for d in (-depth/2,depth/2) for f in (1,.68) for t in (a,b)]
        o=mesh(label+f'__inhabited_sector_{i:02}',v,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],PEARL,bevel=9)
        o['district']=label
        # Large internal 100m gallery is cut from shell, not added outside it.
        cutter=box('temporary_void',Vector(p((a+b)/2,0,.83)),(140,depth+50,150),None)
        cutter.rotation_euler[1]=-(a+b)/2-tilt
        mod=o.modifiers.new('Actual inhabited sector gallery','BOOLEAN');mod.object=cutter;mod.operation='DIFFERENCE'
        bpy.context.view_layer.objects.active=o
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter,do_unlink=True)
    # civic ground enters the sky void at its lower third
    prism(label+'__inner_landscape',[(x-rx*.6,y-depth*.45),(x+rx*.6,y-depth*.45),(x+rx*.55,y+depth*.43),(x-rx*.5,y+depth*.43)],z-rz*.49,z-rz*.49+85,STONE,5)
    DISTRICTS.append(dict(label=label,center_m=list(c),radii_m=[rx,depth/2,rz],role='ENCLOSED_MERIDIONAL_SKY'))

def build_B():
    setup()
    for label,c,rx,d,rz,t in [
     ('B01_LOWER_SEA',(-1250,0,1300),1700,1100,1300,-.18),
     ('B02_EAST_INNER',(1340,580,1900),1300,1450,1750,.28),
     ('B03_HIGH_SEED',(-430,900,3430),1410,1000,1210,-.35),
     ('B04_REVERSE_WORLD',(-1100,1560,2190),1280,1200,1250,.55)]:
        vaulted_world(label,c,rx,d,rz,t)

if __name__=='__main__':
    case=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'A'
    (build_A if case=='A' else build_B)()
    folder=ROOT/('exploration_'+case);save(folder,'R13_'+case);render(folder)
