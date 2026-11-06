"""INT8-R2 — genuine Blender GUI-context Sculpt Mode brush-operator edit.
Not X11 mouse sculpt, not manual GUI hand-sculpt; do not conflate.
The registered timer runs only after the GUI Console has returned to 3D View.
UI and actual target ray are read from the existing INT8-R1 preparation.
"""
import bpy, math, json, hashlib, traceback
from pathlib import Path
from mathutils import Vector
from bpy_extras.view3d_utils import (location_3d_to_region_2d,
    region_2d_to_origin_3d,region_2d_to_vector_3d)

OUT=Path('/tmp/halo9-int8-r2-native')
READY=json.loads((OUT/'GUI_READY.json').read_text())
assert READY['pick']['ray_hit'] and not bpy.app.background
TARGET='INT6_TRUE_BRUSH_west'
assert READY['pick']['hit_target']==TARGET
dispatch={'tries':0}
def actual_visible_gui_brush():
    dispatch['tries']+=1
    try:
        win=bpy.context.window
        assert win and win.screen
        areas=[a for a in win.screen.areas if a.type=='VIEW_3D']
        if not areas:
            if dispatch['tries']<12: return .5
            raise RuntimeError('GUI_VIEW3D_NOT_RESTORED_FROM_CONSOLE')
        area=max(areas,key=lambda a:a.width*a.height)
        reg=next(r for r in area.regions if r.type=='WINDOW')
        r3d=area.spaces.active.region_3d
        obj=bpy.data.objects[TARGET]
        assert bpy.context.active_object==obj and bpy.context.mode=='SCULPT'
        before=json.loads((OUT/'BEFORE_VERTICES.json').read_text())
        assert len(before)==len(obj.data.vertices)==1680
        focus=Vector(READY['pick']['sculpt_surface_point_world'])
        p=location_3d_to_region_2d(reg,r3d,focus)
        assert p is not None
        o=region_2d_to_origin_3d(reg,r3d,p)
        d=region_2d_to_vector_3d(reg,r3d,p)
        inv=obj.matrix_world.inverted()
        ok, hit_point, norm, face_idx=obj.ray_cast(inv@o,(inv.to_3x3()@d).normalized(),distance=20000)
        assert ok, 'PICK_SURFACE_RAY_NO_LONGER_HITS'
        brush=bpy.context.tool_settings.sculpt.brush
        assert brush and 'Clay' in brush.name
        brush.size=164
        brush.strength=.96
        records=[]
        # Reuse INT6's genuinely successful native strokes, but anchor
        # them to a newly GUI-observed, ray-confirmed actual mesh surface.
        def line(ax,ay,bx,by,weight=1.,count=38):
            return [(ax+(bx-ax)*i/(count-1),ay+(by-ay)*i/(count-1),
                     weight*(.88+.12*math.sin(math.pi*i/(count-1))))
                    for i in range(count)]
        paths=[
            line(-.22,-.08,.23,.16,.95),
            line(-.20,.21,.20,-.17,1.0),
            line(-.22,-.21,.16,.15,.93),
            line(-.13,.27,.23,-.13,.83)
        ]
        with bpy.context.temp_override(window=win,area=area,region=reg):
            for j,path in enumerate(paths):
                stroke=[]
                for i,(dx,dy,pressure) in enumerate(path):
                    sx=float(p.x+dx*reg.width)
                    sy=float(p.y+dy*reg.height)
                    stroke.append({
                      'name':'stroke',
                      'mouse':(0.0,0.0),
                      'mouse_event':(sx,sy),
                      'location':tuple(focus),
                      'is_start':i==0,
                      'pressure':float(pressure),
                      'time':float(.018*i),
                      'size':1.0,
                      'x_tilt':0.0,'y_tilt':0.0
                    })
                result=bpy.ops.sculpt.brush_stroke(stroke=stroke,override_location=True)
                records.append({'stroke':j,'result':sorted(result)})
                assert 'FINISHED' in result
        with bpy.context.temp_override(window=win,area=area,region=reg):
            bpy.ops.object.mode_set(mode='OBJECT')
        deltas=[math.dist(tuple(v.co),old) for v,old in zip(obj.data.vertices,before)]
        changed=sum(q>.01 for q in deltas)
        maximum=max(deltas)
        print('INT8_R2_ACTUAL_GUI_BRUSH_VERTICES',changed,maximum,records,flush=True)
        report={
          'schema':'halo9-int8-r2-gui-viewport-projected-operator-brush-v1',
          'source_sha256':READY['source_sha256'],
          'gui_blender_version':bpy.app.version_string,
          'gui_display_present':not bpy.app.background,
          'method':'GUI_VIEWPORT_PROJECTED_SCULPT_OPERATOR__NOT_X11_MOUSE',
          'ray_hit':bool(ok),'hit_target':TARGET,
          'ray_hit_face_idx':int(face_idx),
          'projected_region_xy':[round(float(p.x),2),round(float(p.y),2)],
          'actual_brush_strokes':records,
          'changed_vertices':changed,
          'max_vertex_displacement_m':round(maximum,6),
          'original_target_vertices':len(before),
          'formal_art_accepted':0,'completed_targets':0,
          'minecraft':'HOLD','art':'UNREVIEWED_NOT_ADOPTED'
        }
        (OUT/'GUI_OPERATOR_RESULT.json').write_text(json.dumps(report,indent=2),encoding='utf8')
        if changed<20 or maximum<=.02:
            raise RuntimeError(('GUI_SCULPT_OPERATOR_HAS_NO_PHYSICAL_EFFECT',changed,maximum))
        camera_before=json.loads((OUT/'BEFORE_CAMERAS.json').read_text())
        for name,m in camera_before.items():
            now=bpy.data.objects[name].matrix_world
            assert max(abs(float(now[i][k])-m[i][k]) for i in range(4) for k in range(4))<1e-6
        previous=json.loads((OUT/'BEFORE_VISIBILITY.json').read_text())
        for name,value in previous.items():
            bpy.data.objects[name].hide_set(bool(value))
        assert all(bpy.data.objects[name].hide_get()==value for name,value in previous.items())
        scene=bpy.context.scene
        assert scene['CONSTRUCTION']=='HOLD'
        assert scene['FORMAL_ART_ACCEPTED']==scene['COMPLETED_TARGETS']==0
        scene['INT8_R2_GUI_BRUSH_METHOD']='VIEWPORT_RAY_PROJECTED_SCULPT_OPERATOR_NOT_X11_MOUSE'
        scene['INT8_R2_PARENT_SHA256']=READY['source_sha256']
        scene['INT8_R2_VERIFIED_CHANGED_VERTICES']=changed
        scene['INT8_R2_RESEARCH_NOT_ART']=True
        scene.camera=bpy.data.objects['E11_URBAN_AERIAL']
        blend=OUT/'HALO9_INT8_R2_VISIBLE_GUI_SCULPT_OPERATOR.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
        report['saved_blend_sha256']=hashlib.sha256(blend.read_bytes()).hexdigest()
        report['source_visibility_restored']=True
        report['native_blend_saved']=True
        (OUT/'GUI_OPERATOR_PASS.json').write_text(json.dumps(report,indent=2),encoding='utf8')
        print('INT8_R2_VISIBLE_GUI_NATIVE_EDIT_SUCCESS',report['saved_blend_sha256'],flush=True)
        # The source is already saved; restore working Sculpt UI to show
        # the actual altered surface in an after-operation screenshot.
        with bpy.context.temp_override(window=win,area=area,region=reg):
            bpy.ops.object.mode_set(mode='SCULPT')
        area.tag_redraw()
        return None
    except Exception as exc:
        failure={'error':repr(exc),'traceback':traceback.format_exc(),
                 'tries':dispatch['tries']}
        (OUT/'GUI_OPERATOR_FAILURE.json').write_text(json.dumps(failure,indent=2),encoding='utf8')
        print('INT8_R2_GUI_OPERATOR_FAILED',failure,flush=True)
        return None

bpy.app.timers.register(actual_visible_gui_brush,first_interval=2.5)
print('INT8_R2_ACTUAL_GUI_CONTEXT_OPERATOR_SCHEDULED',flush=True)
