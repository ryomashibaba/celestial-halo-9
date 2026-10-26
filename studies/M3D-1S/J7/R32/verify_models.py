"""Limited geometry/export and camera QA; floor identity is mandatory.
Not a route, structure, full collision, art or Minecraft certification.
"""
import sys,math,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parent
def geom():
    arrays=[];central=[];count=tri=zero=0
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or o.name=='far ground':continue
        count+=1;me=o.data;me.calc_loop_triangles();tri+=len(me.loop_triangles)
        a=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',a);a=a.reshape(-1,3)
        mw=np.array(o.matrix_world);a=a@mw[:3,:3].T+mw[:3,3];arrays.append(a)
        if str(o.get('study_group','')).startswith('R32_'):central.append(a)
        zero+=sum(t.area<1e-8 for t in me.loop_triangles)
    pts=np.concatenate(arrays);q=np.unique(np.rint(pts*1000).astype(np.int64),axis=0)
    out={'meshes':count,'triangles':tri,'world_vertex_hash_1mm':hashlib.sha256(q.tobytes()).hexdigest(),'finite':bool(np.isfinite(pts).all()),'bounds_m':[pts.min(0).tolist(),pts.max(0).tolist()],'zero_area_triangles':int(zero)}
    if central:
        c=np.concatenate(central);out['R32_bounds_m']=[c.min(0).tolist(),c.max(0).tolist()];out['R32_size_m']=(c.max(0)-c.min(0)).tolist()
    return out
def cams():return {o.name:{'matrix':[list(r) for r in o.matrix_world],'lens':o.data.lens,'clip':[o.data.clip_start,o.data.clip_end]} for o in bpy.context.scene.objects if o.type=='CAMERA'}
def light():
    sc=bpy.context.scene
    return {'background':[list(n.inputs['Color'].default_value)+[n.inputs['Strength'].default_value] for n in sc.world.node_tree.nodes if n.type=='BACKGROUND'],
            'lights':[{'type':o.data.type,'energy':o.data.energy,'angle':o.data.angle,'matrix':[list(r) for r in o.matrix_world]} for o in sc.objects if o.type=='LIGHT'],
            'exposure':sc.view_settings.exposure,'transform':sc.view_settings.view_transform,'look':sc.view_settings.look,'unit':sc.unit_settings.scale_length}
def containing(eye,dg):
    hits=[]
    dirs=[Vector(d).normalized() for d in ((.71,.43,.19),(-.41,.23,.83),(.37,-.81,.47))]
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        inv=o.matrix_world.inverted();p=inv@eye;bb=[Vector(v) for v in o.bound_box]
        if any(p[k]<min(v[k] for v in bb)-.001 or p[k]>max(v[k] for v in bb)+.001 for k in range(3)):continue
        tree=BVHTree.FromObject(o,dg);votes=[]
        for direction in dirs:
            q=p.copy();n=0
            for _ in range(100):
                loc,norm,idx,dist=tree.ray_cast(q,direction)
                if loc is None:break
                n+=1;q=loc+direction*.001
            votes.append(n%2==1)
        if sum(votes)>=2:hits.append(o.name)
    return hits
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'R30/model/R30_B.blend'))
base_cams=cams();base_light=light()
bpy.ops.wm.open_mainfile(filepath=str(R/'model/R32_A.blend'));bpy.context.view_layer.update()
sc=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();before=geom()
matched={n:base_cams[n]==cams()[n] for n in base_cams};light_match=base_light==light()
human=[]
for name in ('03_PUBLIC','04_HUMAN','07_SKY_STREET','09_EXPLORATORY_FORUM'):
    cam=bpy.data.objects[name];eye=cam.location.copy();expected=cam['support_floor'];samples=[]
    for dx,dy in ((0,0),(.45,0),(-.45,0),(0,.45),(0,-.45)):
        ee=eye+Vector((dx,dy,0));h,p,n,f,o,m=sc.ray_cast(dg,ee,Vector((0,0,-1)),distance=3)
        samples.append({'actual_floor':o.name if h else None,'expected_floor':expected,'identity_match':bool(h and o.name==expected),'eye_height_m':ee.z-p.z if h else None})
    inside=containing(eye,dg)
    d=cam.matrix_world.to_quaternion()@Vector((0,0,-1));h,p,n,f,o,m=sc.ray_cast(dg,eye,d,distance=5000)
    human.append({'camera':name,'role':'exploratory, not fixed comparison' if name.startswith('09') else 'fixed inherited comparison; changed subject may be invalid',
                  'eye_m':list(eye),'expected_floor':expected,'floor_samples':samples,'inside_mesh_candidates_parity_3_rays':inside,
                  'first_sightline_hit':o.name if h else None,'first_hit_distance_m':(p-eye).length if h else None,
                  'limited_standing_pass':not inside and all(s['identity_match'] and abs(s['eye_height_m']-1.7)<.03 for s in samples)})
unpacked=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file]
bpy.ops.object.select_all(action='DESELECT')
for o in sc.objects:
    if o.type=='MESH' and o.name!='far ground':o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'model/R32_A.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(R/'model/R32_A.glb'));bpy.context.view_layer.update()
after=geom();checks={k:before[k]==after[k] for k in ('meshes','triangles','world_vertex_hash_1mm','bounds_m')}
out={'blender':bpy.app.version_string,'saved_blend':before,'independent_glb_reload':after,'glb_match':checks,'fixed_original_7_cameras':matched,'sun_sky_exposure_units_match_R30':light_match,
     'human_cameras':human,'external_unpacked_images':unpacked,'floor_policy':'Matching height alone never passes; exact expected floor identity and no camera containment required. Invalid old viewpoints are retained as failure evidence, not artistic success.',
     'scope':'Finite geometry, 1mm world vertex set, export roundtrip, fixed cameras/light/units, four camera support footprints and mesh containment only. No complete collision, route, stair/lift operability, structure, evacuation, topology, canonical coordinate or Minecraft certification.'}
(R/'qa/SAVED_MODELS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'geometry':before,'glb_match':checks,'cameras_match':matched,'light_match':light_match,'standing':[(h['camera'],h['limited_standing_pass'],h['inside_mesh_candidates_parity_3_rays']) for h in human]},ensure_ascii=False),flush=True)
assert before['finite'] and all(checks.values()) and all(matched.values()) and light_match and not unpacked
