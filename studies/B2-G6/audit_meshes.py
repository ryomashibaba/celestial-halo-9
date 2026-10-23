"""Read saved BLENDs, compare macro C primary mass, import actual GLBs afresh."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
def key(obs):
    h=hashlib.sha256()
    for o in sorted(obs,key=lambda q:q.name):
        h.update(o.name.encode());h.update(str([tuple(v.co) for v in o.data.vertices]).encode());h.update(str([tuple(p.vertices) for p in o.data.polygons]).encode());h.update(str([list(row) for row in o.matrix_world]).encode())
    return h.hexdigest()
primary={};audit={}
for v in ['macro_A','macro_B','macro_C','selected']:
    O=R/v;m=json.loads((O/'manifest.json').read_text(encoding='utf-8'))
    bpy.ops.wm.open_mainfile(filepath=str(O/'study.blend'));bpy.context.view_layer.update()
    if v in ['macro_C','selected']:primary[v]=key(bpy.data.collections['01_ROOF_GROUND_ARCHITECTURE'].objects)
    if v=='selected':
        floors={}
        for n in ['06_GROUND_A','07_HIGH_B','08_HALL','10_ALLEY']:
            cam=bpy.data.objects[n];hit,p,no,idx,ob,ma=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),cam.location,Vector((0,0,-1)),distance=4)
            floors[n]={'hit':hit,'floor':ob.name if hit else None,'floor_z_m':p.z if hit else None,'eye_height_m':cam.location.z-p.z if hit else None}
        # Sample actual roof slabs next to each civic interior; these are local
        # evidence points, not a complete whole-city navigation certificate.
        roofchecks=[]
        for h in m['halls']:
            x=h['centre_m'][0];z=h['roof_ground_z_m'];y=-850
            hit,p,no,idx,ob,ma=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector((x,y,z+2)),Vector((0,0,-1)),distance=5)
            roofchecks.append({'id':h['id'],'hit':hit,'hit_object':ob.name if hit else None,'expected_roof_z_m':z,'actual_surface_z_m':p.z if hit else None,'note':'street overlay can be 0.23m above roof'})
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(O/'study.glb'));bpy.context.view_layer.update()
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];pts=[o.matrix_world@Vector(p) for o in objects for p in o.bound_box]
    lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)]
    delta=max(abs(q[k]-m['bounds_m'][n][k]) for q,n in [(lo,'min'),(hi,'max')] for k in range(3))
    assert objects and delta<.05,(v,delta)
    nonfinite=sum(not all(math.isfinite(c) for c in ve.co) for ob in objects for ve in ob.data.vertices)
    assert nonfinite==0
    audit[v]={'actual_glb_reload':'PASS','mesh_objects':len(objects),'bounds_m':{'min':lo,'max':hi,'size':[hi[k]-lo[k] for k in range(3)]},'bounds_max_delta_m':delta,'nonfinite_vertices':nonfinite}
assert primary['macro_C']==primary['selected'],'Selected main mass changed after basic form selection'
audit['primary_mass_unchanged_from_macro_C']={'result':'PASS','sha256':primary['selected']}
audit['selected_eye_floor_checks']=floors;audit['selected_roof_surface_samples']=roofchecks
audit['scope']='Finite geometry, actual GLB reload, bounds and specific eye/roof samples only. No structural, collision-free navigation, egress or environmental guarantee.'
(R/'glb_reload_audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps(audit))
