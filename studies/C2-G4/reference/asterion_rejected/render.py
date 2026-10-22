"""Blender 5.2 background renderer/exporter. Never connects to a live Blender.
blender --background --factory-startup --disable-autoexec --threads 4 --python render.py -- --stage preview|final
"""
import bpy,json,os,sys,math,argparse
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent
REFERENCE=ROOT/'reference'
ap=argparse.ArgumentParser();ap.add_argument('--stage',default='preview');ap.add_argument('--only',default='')
ap.add_argument('--legacy',action='store_true')
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT=ROOT/('legacy_matched' if args.legacy else ('preview' if args.stage=='preview' else 'renders'));OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
geo=json.loads((ROOT/'geometry.json').read_text(encoding='utf-8'))

def mat(name,col):
    m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=.74
    return m
colors={'TENRYO':(.66,.70,.73),'CHOTEI':(.73,.68,.57),'SHATO':(.48,.59,.65),'JUNCTION':(.80,.75,.64),'TRANSIT':(.37,.43,.47),'PUBLIC_GROUND':(.80,.75,.64)}
mats={n:mat(n,c) for n,c in colors.items()}
for obj in ([] if args.legacy else geo['objects']):
    me=bpy.data.meshes.new(obj['name']);me.from_pydata(obj['vertices'],[],obj['faces']);me.update()
    ob=bpy.data.objects.new(obj['name'],me);bpy.context.scene.collection.objects.link(ob)
    ob.data.materials.append(mats[obj['body']]);ob['body']=obj['body'];ob['role']=obj['role'];ob['units']='metres'
    # Recalculate orientation once for two-sided shell faces, not a watertight repair.
    import bmesh
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()

def cube(name,loc,size,material):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material);o['role']='CONTEXT';return o

if args.legacy:
    bpy.ops.import_scene.gltf(filepath=str(REFERENCE/'legacy.glb'))
    for ob in bpy.context.scene.objects:
        if ob.type=='MESH':
            system=ob.get('system','TENRYO');body='JUNCTION' if system.startswith('JUNCTION') else system
            ob.data.materials.clear();ob.data.materials.append(mats.get(body,mats['TENRYO']))
    cube('CONTEXT_legacy_public_forum',(0,-30,-12),(1550,1400,24),mats['JUNCTION'])

site=cube('CONTEXT_10km_reference',(0,0,-110),(10000,10000,100),mat('CONTEXT',(.16,.19,.22)))
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=12;sc.cycles.use_denoising=True
sc.world.use_nodes=True;bg=next(n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND')
bg.inputs['Color'].default_value=(.55,.63,.75,1);bg.inputs['Strength'].default_value=.45
sun=bpy.data.lights.new('COMPARISON_SUN','SUN');sun.energy=2.5;sun.angle=.15
so=bpy.data.objects.new(sun.name,sun);sc.collection.objects.link(so);so.rotation_euler=(.5,-.6,-.5)
for name,loc,size,power in [('crown',(-350,650,3570),500,8000000),('forum',(-700,-520,1920),250,3000000),('basin',(300,-300,2050),600,5000000)]:
    light=bpy.data.lights.new('NEUTRAL_ANALYTICAL_FILL_'+name,'AREA');light.energy=power;light.shape='DISK';light.size=size
    ob=bpy.data.objects.new(light.name,light);sc.collection.objects.link(ob);ob.location=loc
sc.render.resolution_x=1000 if args.stage=='preview' else 1600;sc.render.resolution_y=int(sc.render.resolution_x*.75)
sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='Standard'
sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
camdata=bpy.data.cameras.new('CAMERA');cam=bpy.data.objects.new('CAMERA',camdata);sc.collection.objects.link(cam);sc.camera=cam
camdata.clip_start=.25;camdata.clip_end=60000;camdata.sensor_width=36
CAMERAS=json.loads((REFERENCE/'legacy_model_metrics.json').read_text(encoding='utf-8'))['cameras']
# Exterior camera values are deliberately identical to the protected legacy study.
CAMERAS['06_interior']={'eye':(450,-300,1501.7),'target':(-500,500,1750),'lens':24}
CAMERAS['10_ground_pedestrian']={'eye':(-350,-1500,1.7),'target':(-50,650,1050),'lens':28}
CAMERAS['11_crown_pedestrian']={'eye':(-992.8,769.7,3001.7),'target':(100,600,3200),'lens':24}
CAMERAS['12_cavern_pedestrian']={'eye':(-510,-520,1551.7),'target':(300,-100,1750),'lens':28}

def camera(spec):
    cam.location=spec['eye'];cam.rotation_euler=(Vector(spec['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
    camdata.type='ORTHO' if 'ortho' in spec else 'PERSP'
    if 'ortho' in spec:camdata.ortho_scale=spec['ortho']
    else:camdata.lens=spec['lens']

def render(name,spec):
    for ob in sc.objects:
        if ob.type=='LIGHT' and ob.data.type=='AREA':ob.hide_render='ortho' in spec
    camera(spec);sc.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);print('DONE',name,flush=True)

def measurements():
    obs=[o for o in sc.objects if o.type=='MESH' and o.get('role')!='CONTEXT']
    pts=[o.matrix_world@Vector(p) for o in obs for p in o.bound_box]
    mn=[min(p[i] for p in pts) for i in range(3)];mx=[max(p[i] for p in pts) for i in range(3)]
    dg=bpy.context.evaluated_depsgraph_get();trees=[(o.name,BVHTree.FromObject(o,dg)) for o in obs]
    # Six measured rays from public-space reference points, not nominal envelope dimensions.
    spaces={}
    for label,pt in {'basin':(450,-300,1620),'crown':(-298,686,3200),'ground_portal':(-300,600,700),'diagonal_exchange':(80,650,2490)}.items():
        hits={}
        for k,d in [('west',(-1,0,0)),('east',(1,0,0)),('south',(0,-1,0)),('north',(0,1,0)),('down',(0,0,-1)),('up',(0,0,1))]:
            candidates=[]
            for n,t in trees:
                loc,normal,idx,dist=t.ray_cast(Vector(pt),Vector(d),10000)
                if loc is not None:candidates.append((dist,n))
            hits[k]={'distance_m':min(candidates)[0],'mesh':min(candidates)[1]} if candidates else {'distance_m':None,'open_to_context':True}
        spaces[label]={'reference_point_m':pt,'axis_rays':hits}
    camera_rays={}
    for name,spec in CAMERAS.items():
        if 'lens' not in spec:continue
        pt=Vector(spec['eye']);direction=(Vector(spec['target'])-pt).normalized();hits=[];downs=[]
        for n,t in trees:
            loc,_,_,dist=t.ray_cast(pt,direction,10000)
            if loc is not None:hits.append((dist,n))
            loc,_,_,dist=t.ray_cast(pt,Vector((0,0,-1)),5000)
            if loc is not None:downs.append((dist,n))
        camera_rays[name]={'first_forward_hit':min(hits) if hits else None,'floor_below_eye':min(downs) if downs else None}
    return {'bbox_min_m':mn,'bbox_max_m':mx,'bbox_dimensions_m':[mx[i]-mn[i] for i in range(3)],'meshes':len(obs),'polygons':sum(len(o.data.polygons) for o in obs),'space_axis_measurements':spaces,'camera_reference_rays':camera_rays,'aperture_geometry':geo['aperture_geometry'],'cameras':CAMERAS,
      'method':'Building meshes only; metres/Z up. Axis rays report first visible boundary, not maximum void volume or guaranteed clear cuboid. Exterior cameras match legacy exactly.'}

if args.legacy:
    for n in ['01_front','02_oblique','03_side','04_top','05_back']:render(n,CAMERAS[n])
elif args.stage=='preview':
    for n in (args.only.split(',') if args.only else ['01_front','02_oblique','04_top','06_interior']):render(n,CAMERAS[n])
else:
    data=measurements();(ROOT/'model_metrics.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    bpy.ops.object.select_all(action='DESELECT')
    for o in sc.objects:
        if o.type=='MESH' and o.get('role')!='CONTEXT':o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'ASTERION_REINVENTION.glb'),export_format='GLB',use_selection=True,export_extras=True)
    if args.stage=='analyze':print(json.dumps(data['camera_reference_rays'],indent=2),flush=True);sys.exit(0)
    names=args.only.split(',') if args.only else list(CAMERAS)
    for n in names:render(n,CAMERAS[n])
    if not args.only:
        # Same massing, neutral clay and analytical color layers; no small decoration exists.
        clay=mat('NEUTRAL_CLAY',(.60,.62,.64));sc.view_layers[0].material_override=clay
        site.hide_render=True
        render('07_basic_mass',CAMERAS['02_oblique']);render('07b_basic_back',CAMERAS['05_back'])
        sc.view_layers[0].material_override=None
        diagramcols={'TENRYO':(.22,.55,.85),'CHOTEI':(.86,.60,.23),'SHATO':(.30,.70,.56),'JUNCTION':(.9,.26,.22),'TRANSIT':(.9,.35,.7),'PUBLIC_GROUND':(.65,.65,.65)}
        for n,c in diagramcols.items():
            m=mats[n];m.diffuse_color=(*c,1);next(v for v in m.node_tree.nodes if v.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(*c,1)
        render('08_structure',CAMERAS['02_oblique']);render('09_structure_top',CAMERAS['04_top'])
        for ob in sc.objects:
            if ob.type!='MESH' or ob.get('role')=='CONTEXT':continue
            if ob.name in ['TENRYO_south_city_wall','SHATO_west_canyon_wall','CHOTEI_sky_landform'] or ob.name.endswith('_roof'):
                ob.hide_render=True
            role=ob.get('role');col=(.28,.75,.65) if role=='CITY_GROUND' else ((.95,.35,.7) if role=='TRANSIT' else None)
            if col:
                material=mat('DIAGRAM_'+ob.name,col);ob.data.materials.clear();ob.data.materials.append(material)
        render('13_cutaway_city_grounds',CAMERAS['02_oblique'])
        render('14_cutaway_top',CAMERAS['04_top'])
    print('FINAL_COMPLETE',flush=True)
