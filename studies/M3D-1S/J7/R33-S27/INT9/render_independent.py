"""INT9 independent Blender re-open: 3 ORIGINAL E11 cameras only.
Renders do not certify ART or public-route functionality.
"""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
ROOT=Path('/tmp/halo9-int9')
p=Path(bpy.data.filepath)
assert p.name=='HALO9_INT9_CIVIC_ATRIUM_AND_SCULPTED_FAULT.blend',p
r=json.loads((ROOT/'AUTHOR_SUCCESS.json').read_text())
ready=json.loads((ROOT/'AUTHOR_READY.json').read_text())
assert hashlib.sha256(p.read_bytes()).hexdigest()==r['blend_sha256']
sc=bpy.context.scene
assert sc['CONSTRUCTION']=='HOLD'
assert sc['COMPLETED_TARGETS']==sc['FORMAL_ART_ACCEPTED']==0
assert sc['INT9_GUI_SOURCE_SHA256']==r['source_sha256']
assert sc['INT9_ART_ADOPTION']==0
assert r['western_real_vertices_changed']>=20
assert r['western_real_max_displacement_m']>.5
names=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
for n in names:
    old=ready['cameras'][n]
    new=bpy.data.objects[n].matrix_world
    assert max(abs(new[i][j]-old[i][j]) for i in range(4) for j in range(4))<1e-6
school=bpy.data.objects[ready['school_name']]
west=bpy.data.objects[ready['west_name']]
assert len(school.data.polygons)==r['h1_school_atrium_after_poly']>10
assert len(west.data.vertices)==r['western_sculpt_vertices']
assert len(west.data.polygons)>500
for ob in [school,west]:
    assert all(math.isfinite(v) for vert in ob.data.vertices for v in vert.co)
assert r['previous_visibility_restored']
out=ROOT/'renders';out.mkdir(exist_ok=True)
sc.render.engine='CYCLES';sc.cycles.device='CPU'
sc.cycles.samples=12
sc.cycles.use_denoising=True
sc.render.threads_mode='FIXED'
sc.render.threads=2
sc.render.resolution_x=1100;sc.render.resolution_y=825
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
hashes={}
for name in names:
    sc.camera=bpy.data.objects[name]
    file=out/(name+'.png');sc.render.filepath=str(file)
    bpy.ops.render.render(write_still=True)
    assert file.stat().st_size>5000
    hashes[name]=hashlib.sha256(file.read_bytes()).hexdigest()
    print('INT9_FIXED_ORIGINAL_E11_TRUE_RENDER',name,file.stat().st_size,flush=True)
result={
  'schema':'halo9-int9-independent-e11-validation',
  'original_gui_authored_blend_sha256':r['blend_sha256'],
  'original_source_sha256':r['source_sha256'],
  'actual_h1_school_cavity_polygons':len(school.data.polygons),
  'actual_h1_original_ray_before':r['h1_cam_center_before'],
  'actual_h1_original_ray_after':r['h1_cam_center_after'],
  'actual_west_sculpt_changed_vertices':r['western_real_vertices_changed'],
  'actual_west_sculpt_max_displacement':r['western_real_max_displacement_m'],
  'fixed_original_camera_matrices_unchanged':True,
  'true_png_sha256':hashes,
  'independent_blend_reopen':'PASS',
  'art':'NOT_REVIEWED_NOT_ADOPTED',
  'function':'UNKNOWN',
  'formal_art_adopted':0,'completed_targets':0,'minecraft':'HOLD'
}
(ROOT/'INDEPENDENT_RENDER_RESULT.json').write_text(json.dumps(result,indent=2))
print('INT9_INDEPENDENT_REAL_BLENDER_RENDER_PASS_NOT_ART',flush=True)
