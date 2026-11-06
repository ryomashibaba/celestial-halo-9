"""Executed ONLY through a real open Blender GUI Python Console, after
X11 pointer press/drag/release events. No fake brush-operator fallback.
If real saved vertices did not move: hard FAIL, preserve debug screenshots.
"""
import bpy, json, hashlib, math
from pathlib import Path

out=Path('/tmp/halo9-int8-native')
assert out.is_dir()
ready=json.loads((out/'GUI_READY.json').read_text())
assert not bpy.app.background and ready['background'] is False
subject=bpy.data.objects['INT6_TRUE_BRUSH_west']
assert subject.type=='MESH'
if bpy.context.object and bpy.context.object.mode=='SCULPT':
    bpy.ops.object.mode_set(mode='OBJECT')
initial=json.loads((out/'BEFORE_VERTICES.json').read_text())
assert len(initial)==len(subject.data.vertices)
dist=[math.dist([float(c) for c in v.co],orig) for v,orig in zip(subject.data.vertices,initial)]
changed=sum(d>.01 for d in dist)
maximum=max(dist)
record={
  'schema':'halo9-int8-x11-real-gui-mouse-geometry-evidence',
  'source_sha256':ready['source_sha256'],
  'blender_version':bpy.app.version_string,
  'real_window':not bpy.app.background,
  'input_method':'Xvfb+xdotool pointer mouseDown/move/mouseUp and GUI Console',
  'physical_vertices_changed':changed,
  'max_vertex_displacement':round(maximum,6),
  'target_vertices':len(dist),
  'target':subject.name,
  'old_geometry_sha256':hashlib.sha256((out/'BEFORE_VERTICES.json').read_bytes()).hexdigest(),
  'formal_art_adopted':0,'completed_targets':0,'minecraft':'HOLD',
  'art':'UNREVIEWED_NOT_ADOPTED'
}
(out/'MOUSE_EDIT_CHECK.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print('INT8_TRUE_GUI_MOUSE_RESULT',record,flush=True)
assert changed>10 and maximum>.02,('GUI_POINTER_DID_NOT_MOVE_MESH',changed,maximum)
for name,original in json.loads((out/'BEFORE_CAMERAS.json').read_text()).items():
    actual=bpy.data.objects[name].matrix_world
    assert max(abs(float(actual[i][j])-original[i][j]) for i in range(4) for j in range(4))<1e-6
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
scene['INT8_REAL_GUI_SCULPT_MODE']='YES__X11_MOUSE_EVENTS'
scene['INT8_SOURCE_SHA256']=ready['source_sha256']
scene['INT8_PHYSICAL_CHANGED_VERTICES']=changed
scene['INT8_MAX_PHYSICAL_VERTEX_DELTA']=maximum
scene['INT8_RESEARCH_ONLY_NOT_ART']=True
scene.camera=bpy.data.objects['E11_URBAN_AERIAL']
blend=out/'HALO9_INT8_GUI_MOUSE_EDITED_RESEARCH.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
record['saved_blend_sha256']=hashlib.sha256(blend.read_bytes()).hexdigest()
record['saved_blend']=str(blend)
record['native_edit_valid']=True
(out/'GUI_SAVE_PASS.json').write_text(json.dumps(record,indent=2),encoding='utf8')
print('INT8_REAL_GUI_SAVE_PASS',record['saved_blend_sha256'],flush=True)
