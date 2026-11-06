"""INT19 finalize: real X11 mouse sculpt of INT15 native NAVE shell.
No numerical vertex edits or synthetic sculpt operator fallback. W0 & cameras
must be unchanged; original full research scene must be restored before save.
"""
import bpy, json, hashlib, math
from pathlib import Path

out=Path('/tmp/halo9-int19-native')
assert out.is_dir()
ready=json.loads((out/'GUI_READY.json').read_text())
assert not bpy.app.background and ready['background'] is False
subject=bpy.data.objects['INT11_M247C_ALPHA_WEST_ACCRETED_ARCHIVE']
assert subject.type=='MESH'
if bpy.context.object and bpy.context.object.mode=='SCULPT':
    bpy.ops.object.mode_set(mode='OBJECT')
initial=json.loads((out/'BEFORE_VERTICES.json').read_text())
assert len(initial)==len(subject.data.vertices)
dist=[math.dist([float(c) for c in v.co],orig) for v,orig in zip(subject.data.vertices,initial)]
changed=sum(d>.01 for d in dist)
maximum=max(dist)
record={
  'schema':'halo9-int19-nave-real-gui-mouse-geometry-evidence',
  'source_sha256':ready['source_sha256'],
  'blender_version':bpy.app.version_string,
  'real_window':not bpy.app.background,
  'input_method':'Xvfb+xdotool ABSOLUTE_ROOT_COORDS pointer mouseDown/move/mouseUp and GUI Console',
  'physical_vertices_changed':changed,
  'max_vertex_displacement':round(maximum,6),
  'target_vertices':len(dist),
  'target':subject.name,
  'ray_verified_pick':ready['pick'],
  'old_geometry_sha256':hashlib.sha256((out/'BEFORE_VERTICES.json').read_bytes()).hexdigest(),
  'formal_art_adopted':0,'completed_targets':0,'minecraft':'HOLD',
  'art':'UNREVIEWED_NOT_ADOPTED',
  'fixed_e11_review':'PENDING_ACTUAL_RENDER',
  'gui_morph_scope':'ONE_ACTUAL_WEST_CIVIC_NAVE_MESH_ONLY'
}
(out/'MOUSE_EDIT_CHECK.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print('INT19_TRUE_GUI_MOUSE_RESULT',record,flush=True)
assert ready['pick']['ray_hit'] and changed>10 and maximum>.02,('GUI_POINTER_DID_NOT_MOVE_MESH',changed,maximum)
for name,original in json.loads((out/'BEFORE_CAMERAS.json').read_text()).items():
    actual=bpy.data.objects[name].matrix_world
    assert max(abs(float(actual[i][j])-original[i][j]) for i in range(4) for j in range(4))<1e-6
def geom_hash(obj):
    h=hashlib.sha256()
    for vv in obj.data.vertices:
        h.update((','.join(f'{float(c):.10g}' for c in vv.co)+';').encode())
    return h.hexdigest()
for key,original_sha in json.loads((out/'BEFORE_W0.json').read_text()).items():
    assert geom_hash(bpy.data.objects[key])==original_sha,('W0_PROTECTION_VIOLATION',key)
assert bpy.context.scene['CONSTRUCTION']=='HOLD'
assert bpy.context.scene['COMPLETED_TARGETS']==bpy.context.scene['FORMAL_ART_ACCEPTED']==0
assert all(math.isfinite(float(x)) for v in subject.data.vertices for x in v.co)
# Undo viewport-only isolation before saving the FULL research 3D city.
previous=json.loads((out/'BEFORE_VISIBILITY.json').read_text())
for name,flag in previous.items():
    ob=bpy.data.objects[name]
    assert ob.type=='MESH'
    ob.hide_set(bool(flag))
assert all(bpy.data.objects[n].hide_get()==flag for n,flag in previous.items())
record['original_viewport_visibility_restored']=True
scene=bpy.context.scene
scene['INT19_REAL_GUI_SCULPT_MODE']='YES__X11_MOUSE_EVENTS'
scene['INT19_SOURCE_SHA256']=ready['source_sha256']
scene['INT19_PHYSICAL_CHANGED_VERTICES']=changed
scene['INT19_MAX_PHYSICAL_VERTEX_DELTA']=maximum
scene['INT19_RESEARCH_ONLY_NOT_ART']=True
scene.camera=bpy.data.objects['E11_URBAN_AERIAL']
blend=out/'HALO9_INT19_NAVE_REAL_GUI_SCULPT_RESEARCH.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
record['saved_blend_sha256']=hashlib.sha256(blend.read_bytes()).hexdigest()
record['saved_blend']=str(blend)
record['native_edit_valid']=True
(out/'GUI_SAVE_PASS.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print('INT19_REAL_GUI_SAVE_PASS',record['saved_blend_sha256'],flush=True)
