"""INT8: prepare a REAL Blender window for a visible, mouse-driven sculpt.
No geometry creation or source file saving here. Research copy only.
"""
import bpy, json, hashlib, math, sys
from pathlib import Path
from mathutils import Vector

argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(argv[argv.index('--output')+1]);out.mkdir(parents=True,exist_ok=True)
file=Path(bpy.data.filepath)
EXPECTED='51ec4f2c58c74fe03dd44dc7ababcdec315dd77b556d27cfb9541b65d56b28fe'
assert file.name=='INT8_SOURCE.blend',file
assert hashlib.sha256(file.read_bytes()).hexdigest()==EXPECTED
assert not bpy.app.background,'UI mode required: no background simulation'
scene=bpy.context.scene
assert scene['CONSTRUCTION']=='HOLD' and scene['FORMAL_ART_ACCEPTED']==0 and scene['COMPLETED_TARGETS']==0
subject=bpy.data.objects['INT6_TRUE_BRUSH_west']
assert subject.type=='MESH' and len(subject.data.vertices)==1680
assert len(subject.data.polygons)>1200
before=[list(v.co) for v in subject.data.vertices]
cameras=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
camera_poses={n:[list(row) for row in bpy.data.objects[n].matrix_world] for n in cameras}
(out/'BEFORE_VERTICES.json').write_text(json.dumps(before),encoding='utf8')
(out/'BEFORE_CAMERAS.json').write_text(json.dumps(camera_poses),encoding='utf8')

if bpy.context.object and bpy.context.object.mode!='OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.select_all(action='DESELECT')
subject.select_set(True);bpy.context.view_layer.objects.active=subject
win=bpy.context.window
assert win is not None and win.screen is not None
areas=[a for a in win.screen.areas if a.type=='VIEW_3D']
assert areas,'Blender has no interactive VIEW_3D area'
area=max(areas,key=lambda a:a.width*a.height)
reg=next(r for r in area.regions if r.type=='WINDOW')
r3d=area.spaces.active.region_3d
world=[subject.matrix_world@v.co for v in subject.data.vertices]
ranges=[(min(v[j] for v in world),max(v[j] for v in world)) for j in range(3)]
size=max(b-a for a,b in ranges)
look=Vector((-1,-1.6,.67)).normalized()
face=max(subject.data.polygons,key=lambda p:p.area*max(0.,p.normal.dot(look))**2)
focus=subject.matrix_world@face.center
normal=(subject.matrix_world.to_3x3()@face.normal).normalized()
eye=focus+normal*size*1.45
r3d.view_location=focus
r3d.view_distance=size*.97
r3d.view_perspective='PERSP'
r3d.view_rotation=(focus-eye).to_track_quat('-Z','Y')
sp=area.spaces.active
sp.shading.type='SOLID'
sp.shading.color_type='MATERIAL'
sp.overlay.show_overlays=False
bpy.context.view_layer.update()
area.tag_redraw()

bpy.ops.object.mode_set(mode='SCULPT')
with bpy.context.temp_override(window=win,area=area,region=reg):
    outcome=bpy.ops.brush.asset_activate(
        asset_library_type='ESSENTIALS',
        asset_library_identifier='',
        relative_asset_identifier='brushes/essentials_brushes-mesh_sculpt.blend/Brush/Clay Strips')
    assert 'FINISHED' in outcome
    brush=bpy.context.tool_settings.sculpt.brush
    assert brush is not None
    brush.size=164
    brush.strength=.96

ui={
 'schema':'halo9-int8-real-blender-desktop-session',
 'source_sha256':EXPECTED,
 'blender_version':bpy.app.version_string,
 'background':bpy.app.background,
 'source_blend':file.name,
 'target':subject.name,
 'target_vertices':len(before),
 'visible_view3d_area':[area.x,area.y,area.width,area.height],
 'region':[reg.x,reg.y,reg.width,reg.height],
 'screen_width':win.width,'screen_height':win.height,
 'surface_point':[round(float(v),3) for v in focus],
 'brush':brush.name,'brush_size':brush.size,'brush_strength':brush.strength,
 'initial_mode':bpy.context.mode,
 'original_camera_matrices_recorded':True,
 'formal_art_adopted':0,'completed_targets':0,'minecraft':'HOLD',
 'art':'NOT_REVIEWED'}
(out/'GUI_READY.json').write_text(json.dumps(ui,indent=2),encoding='utf8')
print('INT8_REAL_GUI_READY',json.dumps(ui),flush=True)
