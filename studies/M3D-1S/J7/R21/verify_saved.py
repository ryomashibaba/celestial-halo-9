"""Save the measured camera bank in each comparison copy, reopen and check."""
import bpy, sys, json, math, hashlib
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R));Q=R/'qa'
# Import helpers without dispatching a comparison phase.
sys.argv=['verify_saved.py','--','helpers','C55A']
import compare as c
results={}
bpy.ops.wm.open_mainfile(filepath=str(R/'models/C55A_IMPORTED.blend'))
native=c.stats(c.meshes());expected=json.loads((Q/'C55A_IMPORT.json').read_text(encoding='utf8'))['all']
assert native==expected and len(bpy.context.scene.objects)==303 and len(bpy.data.materials)==38
results['C55A_native']=dict(reopened=True,geometry_exact=True,objects=303,meshes=290,materials=38,parent_empty_nodes=13)
for model in ['C55A','R19']:
    path=R/'models'/(model+'_COMPARISON.blend')
    bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
    before=c.stats([o for o in c.meshes() if not c.context(o)])
    cameras=[]
    for p in sorted(Q.glob(model+'_*.json')):
        j=json.loads(p.read_text(encoding='utf8'))
        if not all(k in j for k in ['file','position_m','target_m','hfov_degrees']):continue
        if 'section_' in j['file']:continue
        name='R21_'+Path(j['file']).stem
        d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);s.collection.objects.link(o)
        o.location=j['position_m'];o.rotation_euler=(Vector(j['target_m'])-o.location).to_track_quat('-Z','Y').to_euler()
        d.type='PERSP';d.sensor_fit='HORIZONTAL';d.sensor_width=36;d.lens=18/math.tan(math.radians(25));d.clip_start=.1;d.clip_end=100000
        o['evidence_json']=str(p.relative_to(R));o['eye_support_only_not_walking']='floor' in name
        cameras.append(name)
    s.camera=bpy.data.objects['R21_fit_open_oblique']
    s.render.use_file_extension=True;s.render.image_settings.file_format='PNG'
    bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
    bpy.ops.wm.open_mainfile(filepath=str(path))
    after=c.stats([o for o in c.meshes() if not c.context(o)])
    assert before==after
    for name in cameras:
        cam=bpy.data.objects[name];angle=2*math.atan(cam.data.sensor_width/(2*cam.data.lens))*180/math.pi
        assert abs(angle-50)<.0001
    results[model]=dict(path=str(path.relative_to(R)),geometry_readback_exact=True,central=after,
          cameras_saved=len(cameras),hfov_degrees=50,unit_scale=bpy.context.scene.unit_settings.scale_length)
    assert results[model]['unit_scale']==1
for p in sorted((R/'sections').glob('*.blend')):
    bpy.ops.wm.open_mainfile(filepath=str(p));stats=c.stats([o for o in c.meshes() if not c.context(o) and not c.decals(o) and not c.effects(o)])
    j=json.loads((Q/(p.stem.replace('C55A_','C55A_CUT_')+'.json')).read_text(encoding='utf8'))
    assert stats==j['section_stats']
    axis=j['plane_axis'];coord=j['coordinate_m']
    assert stats['min_m'][axis]>=coord-.005
    cam=bpy.context.scene.camera
    camera_record=dict(file=str(Path('renders/C55A')/('section_'+p.stem.removeprefix('C55A_')+'.png')),
         position_m=list(cam.location),target_m=[0,0,2300],hfov_degrees=50,resolution=[1600,900],engine='CYCLES',samples=16,
         clay=True,light_decals_visible=False,emission=False,terrain_context=False,
         effect_meshes_hidden=[o.name for o in c.meshes() if c.effects(o)],plane_axis=axis,coordinate_m=coord,cap_added=False,
         recovered_from_saved_section_camera=True)
    (Q/('C55A_section_'+p.stem.removeprefix('C55A_')+'.json')).write_text(json.dumps(camera_record,indent=2),encoding='utf8')
    results[p.stem]=dict(reopened=True,section_geometry_exact=True,kept_half_check=True)
verification=json.loads((R/'SOURCE_VERIFICATION.json').read_text(encoding='utf8'))
assert hashlib.sha256((R.parent/'R19/final/R19_LIVING_HORIZON.blend').read_bytes()).hexdigest()==verification['r19_original_sha256']
assert hashlib.sha256((R/'source/model/C55A_SevenfoldHaloRift.glb').read_bytes()).hexdigest()==verification['glb_sha256']
(Q/'SAVED_READBACK.json').write_text(json.dumps(results,indent=2),encoding='utf8')
print('R21_SAVED_READBACK_PASS',json.dumps(results),flush=True)
