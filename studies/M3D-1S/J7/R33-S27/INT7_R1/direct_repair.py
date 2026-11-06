"""INT7-R1 image-led native mesh surgery, same rejected INT7 BLEND.
Keep E11 fixed 3 camera matrices. No fake camera moves; no main, original,
Freeze, World or formal-art changes. No new block/shelf generator.
Observed defects: NAVE public floor collides with human original view and
east fault invades H1 camera neighborhood. Reshape those REAL meshes.
"""
import bpy,sys,hashlib,json,math
from mathutils import Vector
from pathlib import Path

p=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(p[p.index('--output')+1]);out.mkdir(parents=True,exist_ok=True)
(out/'renders').mkdir(exist_ok=True)
src=Path(bpy.data.filepath)
SHA='26bdedb3681a83cb3db39145d1ee7e036c2ee8a557622c6d0aeb9344a90637f6'
assert src.name=='INT7_R1_SOURCE.blend' and hashlib.sha256(src.read_bytes()).hexdigest()==SHA
sc=bpy.context.scene
assert sc['CONSTRUCTION']=='HOLD' and sc['COMPLETED_TARGETS']==sc['FORMAL_ART_ACCEPTED']==0
protected=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
matrices={n:bpy.data.objects[n].matrix_world.copy() for n in protected}
def trace_cam(n):
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get()
    cam=bpy.data.objects[n];origin=cam.matrix_world.translation
    fwd=cam.matrix_world.to_quaternion()@Vector((0,0,-1))
    hit,point,normal,index,target,matrix=sc.ray_cast(dg,origin,fwd,distance=5000)
    return dict(hit=hit,object=target.name if hit else 'SKY',
                distance=round((point-origin).length,3) if hit else None)
before={n:trace_cam(n) for n in protected}
print('INT7_R1_ACTUAL_SOURCE_CAMERA_CENTER_RAYS',before,flush=True)
edits=[]

floor=bpy.data.objects['INT7_NAVE_GREAT_CIVIC_ASSEMBLY_FLOOR']
assert floor.type=='MESH' and len(floor.data.vertices)==16
top=max(v.co.z for v in floor.data.vertices)
assert abs(top-88)<.001,top
# Camera E11 NAVE stays at z73.7. Correct the civic floor instead of
# cheating by raising the protected camera. Floor top is now z71.5.
for v in floor.data.vertices:v.co.z-=16.5
floor.data.update()
edits.append(dict(object=floor.name,vertex_count=len(floor.data.vertices),
                  true_vertical_edit_m=-16.5,original_top_z=top,new_top_z=top-16.5))
# Connect the lower road approaches to the altered civic floor. A tapered
# curve is preferable to a disconnected raised false platform.
for name in ('NAVE_CONTINUOUS_PUBLIC_CENTRAL_BOULEVARD',
             'NAVE_WEST_READING_RAMP','NAVE_STATION_ACCESS'):
    ob=bpy.data.objects['INT7_'+name]
    assert ob.type=='MESH' and len(ob.data.vertices)>=8
    change=0
    for v in ob.data.vertices:
        taper=max(0,min(1,(185-v.co.y)/475))
        delta=16.5*taper
        if delta>.0001:
            v.co.z-=delta;change+=1
    ob.data.update()
    edits.append(dict(object=ob.name,vertices_moved=change,maximum_lowering_m=16.5))

# Move the *actual eastern inhabited cliff cross sections* east of H1,
# rather than deleting the entire shell or moving H1's camera.
# This is a staggered counter-fault offset with real rock and public interior
# on the same mesh; node order and topology remain untouched.
east=bpy.data.objects['INT7_M247_ALPHA_EAST_ASCENDING_CIVIC_SHEAR']
assert east.type=='MESH' and len(east.data.vertices)==7*9
offset={
 -379:0.,-129:110.,94:520.,326:550.,588:380.,855:135.,1176:0.
}
moved=0
for v in east.data.vertices:
    y=int(round(v.co.y))
    if y not in offset:raise AssertionError(('Unexpected east section',y))
    dx=offset[y]
    if dx:
        v.co.x+=dx;moved+=1
east.data.update()
edits.append(dict(object=east.name,vertices_moved=moved,
                  east_section_displacements_m=offset,
                  intent='REOPEN_H1_LIVED_CIVIC_SPACE'))
# Verify that the candidate is still an actual non-empty, finite mesh.
assert len(east.data.polygons)>50
assert all(math.isfinite(component) for vert in east.data.vertices for component in vert.co)

# Better independent review views are allowed only as *additional*
# cameras. Never change a pre-existing E11 view for pretty screenshots.
def aim_camera(name,eye,at):
    obj=bpy.data.objects[name];assert obj.type=='CAMERA' and name not in protected
    obj.location=Vector(eye)
    obj.rotation_euler=(Vector(at)-Vector(eye)).to_track_quat('-Z','Y').to_euler()
    return trace_cam(name)
detail_hit=aim_camera('INT7_NAVE_CIVIC_INTERIOR_DETAIL',
                      (24,-96,150),(-310,80,324))
oblique_hit=aim_camera('INT7_M247_W0_SCULPTURE_OBLIQUE',
                       (1430,-1240,1220),(-330,70,540))
print('INT7_R1_ACTUAL_EXTRA_REVIEW_VIEW_RAYS',{
    'interior':detail_hit,'oblique':oblique_hit},flush=True)
after={n:trace_cam(n) for n in protected}
print('INT7_R1_REAL_CAMERA_AFTER_RAYS',after,flush=True)
for n,m in matrices.items():
    ob=bpy.data.objects[n].matrix_world
    assert max(abs(ob[i][j]-m[i][j]) for i in range(4) for j in range(4))<1e-6
assert max(v.co.z for v in floor.data.vertices)<bpy.data.objects['E11_NAVE_HUMAN'].location.z
sc['INT7_R1_SOURCE_SHA256']=SHA
sc['INT7_R1_METHOD']='REAL_SOURCE_FLOOR_ACCESS_RESCULPT_AND_ASYMMETRIC_H1_FAULT_SHIFT'
sc['CONSTRUCTION']='HOLD';sc['FORMAL_ART_ACCEPTED']=0;sc['COMPLETED_TARGETS']=0
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=18
sc.cycles.use_denoising=True
sc.render.threads_mode='FIXED';sc.render.threads=2
sc.render.resolution_x=1100;sc.render.resolution_y=825
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
views=list(protected)+['INT7_NAVE_CIVIC_INTERIOR_DETAIL',
                       'INT7_M247_W0_SCULPTURE_OBLIQUE']
dest=out/'HALO9_INT7_R1_CORRECTED_PUBLIC_CIVIC_RIFT.blend'
sc.camera=bpy.data.objects[protected[-1]]
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
images={}
for n in views:
    sc.camera=bpy.data.objects[n]
    dst=out/'renders'/(n+'.png')
    sc.render.filepath=str(dst)
    bpy.ops.render.render(write_still=True)
    assert dst.exists() and dst.stat().st_size>5000
    images[n]=hashlib.sha256(dst.read_bytes()).hexdigest()
    print('INT7_R1_TRUE_IMAGE',n,dst.stat().st_size,flush=True)
sc.camera=bpy.data.objects[protected[-1]]
bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
r={
 'schema':'halo9-int7-r1-image-led-actual-geometry-revision',
 'source_sha256':SHA,'blend_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
 'modified_geometry':edits,'camera_rays_before':before,
 'camera_rays_after':after,'additional_review_rays':{
    'interior':detail_hit,'oblique':oblique_hit},
 'original_three_camera_matrices_unchanged':True,
 'true_render_hashes':images,
 'technical_integrity':'NONZERO_MESH_PASS_FULL_BVH_FUNCTION_UNKNOWN',
 'functional_public_routes':'UNKNOWN_NO_INDEPENDENT_WALKABILITY_SWEEP',
 'art':'UNREVIEWED_NOT_ADOPTED',
 'formal_art_adopted':0,'completed_targets':0,'minecraft':'HOLD',
 'coordinates':'UNREGISTERED_RESEARCH_METRES'}
(out/'INT7_R1_NATIVE_EVIDENCE.json').write_text(json.dumps(r,indent=2),encoding='utf8')
print('INT7_R1_NATIVE_SAME_SCENE_COMPLETE',r['blend_sha256'],flush=True)
