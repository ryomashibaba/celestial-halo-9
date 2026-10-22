"""Offline Blender only. Same mesh data -> GLB, BLEND and physically matched images.
blender --background --factory-startup --threads 4 --python render.py -- N1|N2|legacy [preview]
"""
import bpy,bmesh,json,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:];name=args[0];preview='preview' in args
OUT=ROOT/'renders'/name;OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene
def mat(n,c):
    m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.82
    return m
M={n:mat(n,c) for n,c in {'CITY_MASS':(.68,.72,.74),'PUBLIC_GROUND':(.72,.62,.44),'FACILITY':(.43,.57,.61),'DISTRICT':(.68,.65,.57),'TRANSIT_ENVELOPE':(.27,.37,.43)}.items()}
if name=='legacy':
    ref=ROOT/'reference/asterion_rejected/ASTERION_REINVENTION.glb'
    if not ref.exists():ref=ROOT.parent.parent/'research_asterion_massing_reinvention/ASTERION_REINVENTION.glb'
    bpy.ops.import_scene.gltf(filepath=str(ref))
    for ob in sc.objects:
        if ob.type=='MESH':ob.data.materials.clear();ob.data.materials.append(M['CITY_MASS']);ob['role']='CITY_MASS'
else:
    geo=json.loads((ROOT/(name+'.json')).read_text())
    for d in geo['objects']:
        me=bpy.data.meshes.new(d['name']);me.from_pydata(d['vertices'],[],d['faces']);me.update()
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        ob=bpy.data.objects.new(d['name'],me);sc.collection.objects.link(ob);ob['role']=d['role'];ob.data.materials.append(M[d['role']])
sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
sc.render.engine='CYCLES';sc.cycles.samples=12 if preview else 24;sc.cycles.use_denoising=True;sc.cycles.device='CPU'
sc.render.resolution_x=960 if preview else 1440;sc.render.resolution_y=int(sc.render.resolution_x*.75);sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='Standard'
sc.world.use_nodes=True;bg=next(n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.55,.63,.75,1);bg.inputs['Strength'].default_value=.55
ld=bpy.data.lights.new('NEUTRAL_SUN','SUN');ld.energy=2.3;ld.angle=.12
sun=bpy.data.objects.new('NEUTRAL_SUN',ld);sc.collection.objects.link(sun);sun.rotation_euler=(.5,-.6,-.5)
cd=bpy.data.cameras.new('Camera');cam=bpy.data.objects.new('Camera',cd);sc.collection.objects.link(cam);sc.camera=cam;cd.clip_start=.1;cd.clip_end=60000;cd.sensor_width=36
camera_ref=ROOT/'reference/asterion_rejected/model_metrics.json'
if not camera_ref.exists():camera_ref=ROOT.parent.parent/'research_asterion_massing_reinvention/model_metrics.json'
cameras=json.loads(camera_ref.read_text())['cameras']
cameras={k:v for k,v in cameras.items() if k in ['01_front','02_oblique','03_side','04_top','05_back']}
if name=='N2':cameras.update({'06_middle_pedestrian':dict(eye=(-1000,-210,1663.7),target=(200,700,1900),lens=24),'07_high_pedestrian':dict(eye=(-570,590,2873.7),target=(200,700,3060),lens=24),'08_ground_pedestrian':dict(eye=(0,-1800,1.7),target=(-100,300,1300),lens=24),'09_hall_pedestrian':dict(eye=(-100,150,1661.7),target=(-100,650,1770),lens=24)})
if name=='N1':cameras['06_interior']=dict(eye=(200,-300,651.7),target=(-100,1000,1900),lens=24)
if name=='N1R1':cameras.update({'06_middle_pedestrian':dict(eye=(1000,100,1459.7),target=(-900,300,1850),lens=24),'07_high_pedestrian':dict(eye=(1710,100,2709.7),target=(-1300,600,2920),lens=24),'08_ground_pedestrian':dict(eye=(150,-1800,1.7),target=(0,200,1500),lens=24),'09_hall_pedestrian':dict(eye=(-50,140,761.7),target=(-50,600,860),lens=24)})
def configure(spec):
    cam.location=spec['eye'];cam.rotation_euler=(Vector(spec['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO' if 'ortho' in spec else 'PERSP'
    if 'ortho' in spec:cd.ortho_scale=spec['ortho']
    else:cd.lens=spec['lens']
def render(n,spec):
    configure(spec);sc.render.filepath=str(OUT/(n+'.png'));bpy.ops.render.render(write_still=True);print('DONE',name,n,flush=True)
obs=[o for o in sc.objects if o.type=='MESH']
dg=bpy.context.evaluated_depsgraph_get();trees=[(o.name,BVHTree.FromObject(o,dg)) for o in obs]
pts=[o.matrix_world@Vector(p) for o in obs for p in o.bound_box]
mn=[min(p[i] for p in pts) for i in range(3)];mx=[max(p[i] for p in pts) for i in range(3)]
metrics=dict(units='metres',bbox_min_m=mn,bbox_max_m=mx,bbox_dimensions_m=[mx[i]-mn[i] for i in range(3)],cameras=cameras,mesh_count=len(obs),faces=sum(len(o.data.polygons) for o in obs),render_settings=dict(width=sc.render.resolution_x,height=sc.render.resolution_y,samples=sc.cycles.samples,engine='CYCLES',sun_energy=2.3,world_strength=.55),rays={})
for n,spec in cameras.items():
    if 'ortho' in spec:continue
    p=Vector(spec['eye']);hits=[];forward=[];d=(Vector(spec['target'])-p).normalized()
    for obj,t in trees:
        loc,_,_,dist=t.ray_cast(p,Vector((0,0,-1)),10000)
        if loc is not None:hits.append((dist,obj))
        loc,_,_,dist=t.ray_cast(p,d,10000)
        if loc is not None:forward.append((dist,obj))
    metrics['rays'][n]=dict(floor_below_eye=min(hits) if hits else None,first_forward_hit=min(forward) if forward else None)
(ROOT/(name+'_metrics.json')).write_text(json.dumps(metrics,indent=2),encoding='utf-8')
if name!='legacy':
    bpy.ops.object.select_all(action='DESELECT')
    for ob in obs:ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(ROOT/(name+'.glb')),export_format='GLB',use_selection=True,export_extras=True)
# Site deliberately excluded from models / physical dimensions.
bpy.ops.mesh.primitive_plane_add(size=10000,location=(0,0,-85));site=bpy.context.object;site.name='CONTEXT_10km';site.data.materials.append(mat('CONTEXT',(.19,.23,.27)))
if not preview and name!='legacy':
    configure(cameras['02_oblique']);bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/(name+'.blend')),compress=True)
for n in (['02_oblique','04_top'] if preview or 'compare' in args else list(cameras)):render(n,cameras[n])
if not preview and name in ['N2','N1R1']:
    sc.view_layers[0].material_override=M['CITY_MASS'];render('10_clay',cameras['02_oblique']);sc.view_layers[0].material_override=None
    # Exact model sectional display: hide forward urban bands only, explicitly a cutaway.
    for ob in obs:
        if name=='N2' and ob.name.startswith('N2_inhabited_stratum_') and int(ob.name.rsplit('_',1)[1])<4:ob.hide_render=True
        if name=='N1R1' and ob.name in ['N1R1_city_shell_3','N1R1_city_shell_4']:ob.hide_render=True
    render('11_cutaway',cameras['02_oblique'])
print('COMPLETE',name,flush=True)
