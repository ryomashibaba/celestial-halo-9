# HALO9 E9-R1: DIRECT IN-PLACE SCULPT on an isolated copy of real E9 native BLEND.
# E9 primary reject remains immutable; this fixes art-invalid H1 camera geometry,
# NOT a camera-only hack and NOT an artistic acceptance.
import bpy, sys, hashlib, json, struct
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[args.index('--output')+1] if '--output' in args else '/tmp/halo9_e9r1')
out.mkdir(parents=True,exist_ok=True)
(out/'before').mkdir(exist_ok=True)
(out/'after').mkdir(exist_ok=True)
sc=bpy.context.scene
source=Path(bpy.data.filepath)
assert source.is_file() and source.name=='E9_DIRECT_SCULPT_OPEN_PUBLIC_CITY_WORKING.blend'
assert sc.get('minecraft_write')=='FORBIDDEN'
assert sc.get('official_coordinates_verified') is False
assert sc.get('formal_art_adoption') is False
assert sc.get('completed_targets')==0
floor=bpy.data.objects.get('E9_H1_REAL_PAVED_PUBLIC_ARRIVAL')
cam=bpy.data.objects.get('human_sky_district')
assert floor is not None and floor.type=='MESH'
assert cam is not None and cam.type=='CAMERA'
def inside_bbox(ob,point):
    inv=ob.matrix_world.inverted() @ point
    xs=[v[0] for v in ob.bound_box];ys=[v[1] for v in ob.bound_box];zs=[v[2] for v in ob.bound_box]
    return min(xs)<=inv.x<=max(xs) and min(ys)<=inv.y<=max(ys) and min(zs)<=inv.z<=max(zs)
assert inside_bbox(floor,cam.matrix_world.translation),'First image problem no longer reproducible'
cam_matrix=[list(row) for row in cam.matrix_world]
floor_z_before=floor.location.z
sc.render.resolution_x=960;sc.render.resolution_y=640
sc.render.resolution_percentage=100;sc.cycles.samples=20
try:sc.view_layers[0].cycles.use_denoising=False
except (AttributeError,TypeError):pass
sc.camera=cam
sc.render.filepath=str(out/'before'/'human_sky_district.png')
bpy.ops.render.render(write_still=True)
# Physical architecture correction: lower public gallery deck to
# camera's eye height, leaving 1.7 m eye clearance above the SAME deck.
floor.location.z=cam.matrix_world.translation.z - 1.7 - floor.dimensions.z/2
assert abs(floor.location.z-839.4)<0.1
assert not inside_bbox(floor,cam.matrix_world.translation)
# A deck needs physical piers; avoid a floating walkway.
piers=[]
for x in (1522,1558):
    for y in (-365,-180):
        bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,832))
        ob=bpy.context.object
        ob.name=f'E9R1_H1_PUBLIC_DECK_SUPPORT_{x}_{y}'
        ob.scale=(9,12,16)
        bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
        for collection in list(ob.users_collection):collection.objects.unlink(ob)
        bpy.data.collections['H1_INHABITED_HIGH_CITY'].objects.link(ob)
        source_material=floor.data.materials[0] if len(floor.data.materials) else None
        if source_material:ob.data.materials.append(source_material)
        piers.append(ob.name)
# Non-invasive camera proof: exact world matrix remains unchanged.
assert cam_matrix==[list(row) for row in cam.matrix_world]
assert sc.get('e9_boolean_opening_count')>=6
sc['e9r1_h1_before_camera_inside_floor']=True
sc['e9r1_h1_after_camera_inside_floor']=False
sc['e9r1_h1_human_eye_clearance_m']=1.7
sc['e9r1_fixed_camera_no_movement']=True
sc['e9r1_original_scene_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
sc['art_status']='NOT_YET_ART_APPROVED'
dest=out/'E9R1_TRUE_SAME_BLENDER_CORRECTED_CITY.blend'
sc.camera=bpy.data.objects['urban_aerial']
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=False)
views=['human_sky_district','human_public_interior','urban_aerial']
for name in views:
    sc.camera=bpy.data.objects[name]
    sc.render.filepath=str(out/'after'/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('E9R1_ACTUAL_NATIVE_RENDER',name,flush=True)
sc.camera=bpy.data.objects['urban_aerial']
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=False)
result={
 'schema':'halo9-e9r1-correct-human-occlusion-actual-existing-blend',
 'source_sha256':sc['e9r1_original_scene_sha256'],
 'new_blend_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
 'h1_camera_world_position':list(cam.matrix_world.translation),
 'h1_camera_world_transform_unchanged':True,
 'h1_floor_old_z':floor_z_before,'h1_floor_new_z':floor.location.z,
 'camera_inside_floor_before':True,'camera_inside_floor_after':False,
 'human_camera_eye_clearance_m':1.7,'pier_names':piers,
 'formal_art_adoption':False,'completed_targets':0,'minecraft':'HOLD',
 'art_review':'PENDING_DIRECT_IMAGE_REVIEW',
 'renders_sha256':{
    phase:{n:hashlib.sha256((out/phase/(n+'.png')).read_bytes()).hexdigest()
           for n in (['human_sky_district'] if phase=='before' else views)}
    for phase in ('before','after')}
 }
(out/'E9R1_DIRECT_EDIT_REPORT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print('E9R1_SAVED_NATIVE_SAME_BLEND_DIRECT_EDIT_PASS',json.dumps(result),flush=True)
