"""INT12 independent process renders same fixed E11 camera directions and three
INT11 supplementary views, then verifies saved changes against GUI records.
This is tech/visual evidence, never formal art certification.
"""
import bpy,json,math,hashlib
from pathlib import Path
OUT=Path('/tmp/halo9-int12')
p=Path(bpy.data.filepath)
d=json.loads((OUT/'GUI_AUTHOR_SUCCESS.json').read_text())
assert p.name=='HALO9_INT12_E11_SCREEN_DIRECT_NATIVE_RESCULPT.blend'
assert hashlib.sha256(p.read_bytes()).hexdigest()==d['saved_blend_sha256']
assert d['real_gui'] and d['method_not_x11_hand_brush']
sc=bpy.context.scene
assert sc['CONSTRUCTION']=='HOLD'
assert sc['FORMAL_ART_ACCEPTED']==sc['COMPLETED_TARGETS']==0
assert sc['INT12_PARENT_SHA256']==d['parent_sha256']
assert sc['INT12_ART_ACCEPTED']==sc['INT12_COMPLETED_TARGETS']==0
assert len(d['deleted_rejected_ribs'])>=7
for name in d['deleted_rejected_ribs']:
    assert name not in bpy.data.objects,name
assert 'INT11_M247C_BETA_SLANTED_CIVIC_SEAM' in bpy.data.objects
assert d['new_external_city_objects_created']==0
for a in d['sculpted_original_meshes']:
    ob=bpy.data.objects[a['target']]
    assert len(ob.data.vertices)>300 and len(ob.data.polygons)>500
    assert a['changed_vertices']>=20 and a['max_world_displacement']>=25
    assert all(math.isfinite(float(x)) for v in ob.data.vertices for x in v.co)
for name,old in d['fixed_camera_matrices'].items():
    current=bpy.data.objects[name].matrix_world
    assert max(abs(current[i][j]-old[i][j]) for i in range(4) for j in range(4))<1e-6
for name,sha in d['protected_W0_sha256'].items():
    ob=bpy.data.objects[name]
    h=hashlib.sha256()
    for v in ob.data.vertices:
        h.update((','.join(format(float(x),'.10g') for x in v.co)+';').encode())
    assert h.hexdigest()==sha,name

sc.render.engine='CYCLES'
sc.cycles.device='CPU'
sc.cycles.samples=10
sc.cycles.use_denoising=True
sc.render.threads_mode='FIXED'
sc.render.threads=2
sc.render.resolution_x=1024
sc.render.resolution_y=768
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
names=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL',
       'INT11_NAVE_HOLLOW_PUBLIC_INTERIOR',
       'INT11_H1_CIVIC_MARKET_INTERIOR',
       'INT11_M247C_W0_THREE_DIMENSIONAL_AERIAL')
rdir=OUT/'renders';rdir.mkdir(exist_ok=True)
imgs={}
for n in names:
    ob=bpy.data.objects[n]
    assert ob.type=='CAMERA'
    sc.camera=ob
    f=rdir/(n+'.png')
    sc.render.filepath=str(f)
    bpy.ops.render.render(write_still=True)
    assert f.stat().st_size>10000,(n,f.stat().st_size)
    imgs[n]=hashlib.sha256(f.read_bytes()).hexdigest()
    print('INT12_REAL_E11_IMAGE_RENDER',n,f.stat().st_size,flush=True)
out={
    'schema':'halo9-int12-independent-render-inspection-v1',
    'native_blend_sha256':d['saved_blend_sha256'],
    'source_sha256':d['parent_sha256'],
    'original_3_E11_cameras_unchanged':True,
    'original_4_W0_geometry_unchanged':True,
    'two_native_screen_sculpt_ops':d['sculpted_original_meshes'],
    'deleted_repeated_rejected_ribs':d['deleted_rejected_ribs'],
    'preserved_beta_seam':True,
    'native_6_render_sha256':imgs,
    'visible_gui_author':True,
    'independent_reopen':'PASS',
    'function':'UNKNOWN','art':'UNREVIEWED_NOT_ADOPTED',
    'formal_art_accepted':0,'completed_targets':0,'minecraft':'HOLD'
}
(OUT/'INDEPENDENT_TECH_NOT_ART.json').write_text(json.dumps(out,indent=2))
print('INT12_INDEPENDENT_E11_3D_AND_SIX_RENDERS_VERIFIED_NOT_ART',flush=True)
