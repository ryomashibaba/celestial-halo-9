"""INT8: prepare a REAL Blender window for a visible, mouse-driven sculpt.
No geometry creation or source file saving here. Research copy only.
"""
import bpy, json, hashlib, math, sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_origin_3d, region_2d_to_vector_3d

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
# Previous actual GUI screenshots showed foreground meshes covering
# the selected district; the mouse stroke hit an occluder instead of target.
# Isolate only the working viewport, with exact prior states serialized.
visibility={ob.name:bool(ob.hide_get()) for ob in scene.objects if ob.type=='MESH'}
(out/'BEFORE_VISIBILITY.json').write_text(json.dumps(visibility),encoding='utf8')
for other in scene.objects:
    if other.type=='MESH' and other != subject:
        other.hide_set(True)
subject.hide_set(False)
bpy.context.view_layer.update()
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
# INT18-R1: Original ray-hit pick was the CENTRE of an exceptionally
# large flat polygon. A 100px GUI brush can hit that polygon but have
# NO mesh vertices within its deformation footprint. Move the picked
# point INSIDE this existing face but close to an existing corner.
# This does not add any mesh geometry or simulate a brush operator.
face_center=subject.matrix_world@face.center
corner_index=int(face.vertices[0])
corner=subject.matrix_world@subject.data.vertices[corner_index].co
focus=face_center.lerp(corner,0.92)
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

# In the REAL desktop Blender's asset library may still be loading when
# the command-line --python script starts (the immediate asset operator
# reports unfinished). Resume in Blender's actual GUI event loop.
attempt={'number':0}
def finish_real_gui_setup():
    attempt['number']+=1
    try:
        brush=bpy.context.tool_settings.sculpt.brush
        if brush is None:
            with bpy.context.temp_override(window=win,area=area,region=reg):
                status=bpy.ops.brush.asset_activate(
                    asset_library_type='ESSENTIALS',
                    asset_library_identifier='',
                    relative_asset_identifier='brushes/essentials_brushes-mesh_sculpt.blend/Brush/Clay Strips')
                print('INT8_ACTIVATE_BRUSH_GUI',status,flush=True)
            brush=bpy.context.tool_settings.sculpt.brush
        if brush is None:
            if attempt['number']<25:
                return .5
            raise RuntimeError('SCULPT_ASSET_DID_NOT_LOAD_IN_GUI_EVENT_LOOP')
        brush.size=240
        brush.strength=.96
        # Blender 5.2 GUI previously displayed 100 px despite setting
        # the underlying brush.size to 164. Explicit unified-size
        # override also drives the actual onscreen brush cursor.
        unified=bpy.context.tool_settings.unified_paint_settings
        if hasattr(unified,'use_unified_size'):
            unified.use_unified_size=True
        unified.size=240
        bpy.context.view_layer.update()
        area.tag_redraw()
        projected=location_3d_to_region_2d(reg,r3d,focus)
        if projected is None:
            raise RuntimeError('REAL_GUI_SURFACE_CANNOT_PROJECT')
        ray_o=region_2d_to_origin_3d(reg,r3d,projected)
        ray_d=region_2d_to_vector_3d(reg,r3d,projected)
        invert=subject.matrix_world.inverted()
        ok, local_point, local_normal, index=subject.ray_cast(
            invert@ray_o,(invert.to_3x3()@ray_d).normalized(),distance=20000)
        if not ok:
            raise RuntimeError('REAL_GUI_VIEWPORT_RAY_MISSES_SELECTED_MESH')
        # Blender coordinates have a bottom-left origin; xdotool window
        # coordinates have a top-left origin. No hard-coded screen pixel!
        px=int(round(reg.x+projected.x))
        py=int(round(win.height-(reg.y+projected.y)))
        if not (90<px<win.width-120 and 90<py<win.height-110):
            raise RuntimeError(('REAL_GUI_PICK_OUTSIDE_VIEWPORT',px,py))
        pick={
          'window_client_xy_top_left':[px,py],
          'region_xy_bottom_left':[round(float(projected.x),2),round(float(projected.y),2)],
          'window_wh':[int(win.width),int(win.height)],
          'viewport_area_xywh':[area.x,area.y,area.width,area.height],
          'region_xywh':[reg.x,reg.y,reg.width,reg.height],
          'hit_target':subject.name,
          'hit_face_index':int(index),
          'hit_location_world':[round(float(x),3) for x in subject.matrix_world@local_point],
          'sculpt_surface_point_world':[round(float(x),3) for x in focus],
          'ray_hit':True
        }
        print('INT18_GUI_PICK_RAY_VERIFIED',json.dumps(pick),flush=True)
        ui={
          'schema':'halo9-int8-r1-precise-gui-ray-projected-sculpt-session',
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
          'near_corner_vertex_index':corner_index,
          'near_corner_world':[round(float(v),3) for v in corner],
          'near_corner_distance_m':round((corner-focus).length,3),
          'unified_brush_size':unified.size,
          'brush':brush.name,'brush_size':brush.size,'brush_strength':brush.strength,
          'initial_mode':bpy.context.mode,
          'gui_event_loop_attempts':attempt['number'],
          'original_camera_matrices_recorded':True,
          'target_isolated_in_working_viewport':True,
          'pick':pick,
          'temporarily_hidden_mesh_count':sum(1 for x in scene.objects if x.type=='MESH' and x!=subject),
          'formal_art_adopted':0,'completed_targets':0,'minecraft':'HOLD',
          'art':'NOT_REVIEWED'}
        (out/'GUI_READY.json').write_text(json.dumps(ui,indent=2),encoding='utf8')
        print('INT18_REAL_GUI_PICK_READY',json.dumps(ui),flush=True)
        return None
    except Exception as exc:
        if attempt['number']<25:
            print('INT8_GUI_NOT_READY_YET',attempt['number'],repr(exc),flush=True)
            return .5
        (out/'GUI_BOOT_FAILED.json').write_text(json.dumps({
            'error':repr(exc),'attempts':attempt['number']},indent=2))
        print('INT8_GUI_BOOT_FATAL',repr(exc),flush=True)
        return None

bpy.app.timers.register(finish_real_gui_setup,first_interval=1.2)
