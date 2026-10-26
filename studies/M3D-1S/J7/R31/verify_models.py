"""Limited metre-scale geometry QA, saved BLEND and independent empty-scene GLB reload.
Does not certify whole-city routes, topology, structures, ART, or Minecraft suitability.
"""
import sys,math,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Vector
R=Path(__file__).resolve().parent

def geom():
    arrays=[];central=[];count=0;tri=0;zero=0
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or o.name=='far ground':continue
        count+=1;me=o.data;me.calc_loop_triangles();tri+=len(me.loop_triangles)
        a=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',a);a=a.reshape(-1,3)
        mw=np.array(o.matrix_world);a=a@mw[:3,:3].T+mw[:3,3];arrays.append(a)
        if str(o.get('study_group','')).startswith('R31_'):central.append(a)
        zero+=sum(t.area<1e-8 for t in me.loop_triangles)
    pts=np.concatenate(arrays);q=np.unique(np.rint(pts*1000).astype(np.int64),axis=0)
    out={'meshes':count,'triangles':tri,'raw_vertices':len(pts),'unique_vertices_1mm':len(q),'world_vertex_hash_1mm':hashlib.sha256(q.tobytes()).hexdigest(),'finite':bool(np.isfinite(pts).all()),'bounds_m':[pts.min(0).tolist(),pts.max(0).tolist()],'triangles_area_below_1e8':int(zero)}
    if central:
        c=np.concatenate(central);out['new_R31_architecture_bounds_m']=[c.min(0).tolist(),c.max(0).tolist()];out['new_R31_architecture_size_m']=(c.max(0)-c.min(0)).tolist()
    return out

def camset():
    return {o.name:{'matrix':[list(row) for row in o.matrix_world],'lens':o.data.lens,'clip':[o.data.clip_start,o.data.clip_end]} for o in bpy.context.scene.objects if o.type=='CAMERA'}

def lights():
    sc=bpy.context.scene
    return {'world_background':[list(n.inputs['Color'].default_value)+[n.inputs['Strength'].default_value] for n in sc.world.node_tree.nodes if n.type=='BACKGROUND'],
            'sun':[{'type':o.data.type,'energy':o.data.energy,'angle':o.data.angle,'matrix':[list(r) for r in o.matrix_world]} for o in sc.objects if o.type=='LIGHT'],
            'exposure':sc.view_settings.exposure,'transform':sc.view_settings.view_transform,'look':sc.view_settings.look,'unit':sc.unit_settings.scale_length}

bpy.ops.wm.open_mainfile(filepath=str(R.parent/'R30/model/R30_B.blend'))
baseline_cam=camset();baseline_light=lights()
bpy.ops.wm.open_mainfile(filepath=str(R/'model/R31_A.blend'));bpy.context.view_layer.update()
sc=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();before=geom();current_cam=camset()
matched={n:baseline_cam[n]==current_cam[n] for n in baseline_cam}
human=[]
for o in sc.objects:
    if o.type!='CAMERA' or not o.get('support_floor'):continue
    eye=o.location.copy();samples=[]
    for dx,dy in [(0,0),(.45,0),(-.45,0),(0,.45),(0,-.45)]:
        e=eye+Vector((dx,dy,0));hh,p,n,f,ob,m=sc.ray_cast(dg,e,Vector((0,0,-1)),distance=3)
        samples.append({'floor':ob.name if hh else None,'eye_height_m':e.z-p.z if hh else None})
    near=[]
    for j in range(16):
        d=Vector((math.cos(j*math.tau/16),math.sin(j*math.tau/16),0))
        h,p,n,f,ob,m=sc.ray_cast(dg,eye,d,distance=.23)
        if h:near.append(ob.name)
    target=Vector(o['target_m']);h,p,n,f,ob,m=sc.ray_cast(dg,eye,(target-eye).normalized(),distance=(target-eye).length)
    human.append({'camera':o.name,'eye_m':list(eye),'expected_floor':o['support_floor'],'footprint_5':samples,'head_23cm':near,'sightline_first_hit':ob.name if h else None,'sightline_hit_distance_m':(p-eye).length if h else None,'limited_floor_pass':all(s['eye_height_m'] is not None and abs(s['eye_height_m']-1.7)<.03 for s in samples) and not near})
# A deliberately limited high-street centreline sample, not full-body clearance.
sys.path.insert(0,str(R));import meshkit as g
route=g.catmull([(-650,840,2190),(-100,840,2190),(650,980,2190),(1170,1230,2190),(1430,1560,2190)],12)
route_samples=[]
for p in route:
    e=Vector(p)+Vector((0,0,1.7));h,pp,n,f,ob,m=sc.ray_cast(dg,e,Vector((0,0,-1)),distance=3)
    route_samples.append({'point_m':list(p),'floor':ob.name if h else None,'height_m':e.z-pp.z if h else None})
unpacked=[{'name':i.name,'path':i.filepath} for i in bpy.data.images if i.source=='FILE' and not i.packed_file]
light_match=baseline_light==lights()
# All architectural and context meshes exported; 300km background plane omitted.
bpy.ops.object.select_all(action='DESELECT')
for o in sc.objects:
    if o.type=='MESH' and o.name!='far ground':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'model/R31_A.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(R/'model/R31_A.glb'));bpy.context.view_layer.update()
after=geom()
checks={k:before[k]==after[k] for k in ['meshes','triangles','world_vertex_hash_1mm','bounds_m']}
out={'blender':bpy.app.version_string,'saved_blend':before,'independent_glb_reload':after,'glb_match':checks,'original_7_cameras_unchanged':matched,'sun_sky_exposure_scale_match_R30':light_match,'human_cameras':human,'high_street_centreline_samples_only':route_samples,'external_unpacked_images':unpacked,'scope':'Geometry finite, meshes, triangles, world-space vertex set at 1mm; fixed cameras/sun/sky/scale; four standing-camera footprint/head samples; high-street centreline floor only. No full-body sweep, route network, all collisions, topology/manifold, all rooms, structures, evacuation, rail operation, canonical coordinate or Minecraft certification.'}
(R/'qa/SAVED_MODELS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'geometry':before,'glb_match':checks,'camera_match':matched,'light_match':light_match,'human_floor':[(r['camera'],r['limited_floor_pass']) for r in human],'route_floor_samples':sum(s['height_m'] is not None and abs(s['height_m']-1.7)<.03 for s in route_samples),'route_total':len(route_samples)},ensure_ascii=False),flush=True)
assert before['finite'] and all(checks.values()) and all(matched.values()) and light_match
assert not unpacked
assert all(x['limited_floor_pass'] for x in human)
