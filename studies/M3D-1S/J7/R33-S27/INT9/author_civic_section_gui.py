"""INT9: NAVE/H1 inhabited-section repair in the real Blender GUI.

Edit an isolated copy of the previous INT7-R1 study, never its original.
Specific edits: carve a traversable high atrium through the school that
obstructs the ORIGINAL H1 camera; subdivide and true-brush-sculpt the EXISTING
M247 west inhabited fault surface. Do not generate a new shell or a box city.
Xvfb renders are not proof of aesthetic acceptance. Formal ART=0, city=0/30.
"""
import bpy, json, math, hashlib, traceback
from pathlib import Path
from mathutils import Vector
from bpy_extras.view3d_utils import (location_3d_to_region_2d,
    region_2d_to_vector_3d,region_2d_to_origin_3d)

ROOT=Path('/tmp/halo9-int9')
ROOT.mkdir(exist_ok=True)
PARENT_SHA='8d1b5a8a3c9cd1889e34684a071883f67a1252227f5aff5b2736d613e3e8b4a2'
source=Path(bpy.data.filepath)
assert source.name=='INT9_SOURCE.blend'
assert hashlib.sha256(source.read_bytes()).hexdigest()==PARENT_SHA
assert not bpy.app.background,'This is a real GUI author, NOT a background author'
s=bpy.context.scene
assert s['CONSTRUCTION']=='HOLD' and s['COMPLETED_TARGETS']==0
assert s['FORMAL_ART_ACCEPTED']==0
originals=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
cameras={n:[[float(c) for c in row] for row in bpy.data.objects[n].matrix_world]
         for n in originals}
school=bpy.data.objects['INT7_CITY_EAST_INHABITED_SCHOOL_PHYSICAL_PUBLIC_BODY']
west=bpy.data.objects['INT7_M247_ALPHA_WEST_LIVED_FAULT_SHEAR']
assert school.type==west.type=='MESH'
assert len(school.data.polygons)>5 and len(west.data.polygons)>50
win=bpy.context.window
assert win is not None
views=[a for a in win.screen.areas if a.type=='VIEW_3D']
assert views,'No Blender real GUI viewport'
area=max(views,key=lambda a:a.width*a.height)
region=next(r for r in area.regions if r.type=='WINDOW')
r3d=area.spaces.active.region_3d

def origin_ray(name):
    b=bpy.data.objects[name]
    return b.matrix_world.translation,b.matrix_world.to_quaternion() @ Vector((0,0,-1))

def hit_camera(name):
    bpy.context.view_layer.update()
    dep=bpy.context.evaluated_depsgraph_get()
    origin,direction=origin_ray(name)
    ok,p,n,idx,target,matrix=s.ray_cast(dep,origin,direction,distance=5000)
    return {'object':target.name if ok else 'SKY',
            'distance':round((p-origin).length,4) if ok else None}

before={n:hit_camera(n) for n in originals}
assert before['E11_H1_HUMAN']['object']==school.name, before
initial={'schema':'halo9-int9-visible-gui-civic-section-v1',
         'input_sha256':PARENT_SHA,'gui_mode':not bpy.app.background,
         'cameras':cameras,'camera_center_hits_before':before,
         'school_name':school.name,'west_name':west.name,
         'formal_art':0,'completed':0,'minecraft':'HOLD'}
(ROOT/'AUTHOR_READY.json').write_text(json.dumps(initial,indent=2))
print('INT9_GUI_READY_FOR_VISUAL_CAPTURE',before,flush=True)

state={'attempt':0}
def edit_civic_section():
    state['attempt']+=1
    if not (ROOT/'BEGIN_EDIT').exists():
        return .35
    try:
        assert bpy.context.window==win
        # First bring the already existing school building to the forefront,
        # find the exact blocking point, and sculpt out one LARGE occupied
        # public atrium along its sightline. A tapered irregular cutter is
        # a negative space with physical walls, not an exterior facade icon.
        dg=bpy.context.evaluated_depsgraph_get()
        origin,direction=origin_ray('E11_H1_HUMAN')
        hit,p,n,idx,obj,_=s.ray_cast(dg,origin,direction,distance=1000)
        assert hit and obj.name==school.name,(hit,obj.name if hit else 'SKY')
        center_distance=(p-origin).length
        assert 15<center_distance<180
        right=direction.cross(Vector((0,0,1))).normalized()
        up=right.cross(direction).normalized()
        if up.z<0:
            up=-up
        # Far-side rooms remain physically embedded in the old school.
        # The opening is wide enough for a city-scale hall and spans
        # the school thickness rather than a decorative round window.
        rings=[]
        for step,(distance,rw,rh,skew) in enumerate([
            (center_distance-120,48,83,-.12),
            (center_distance-12,53,91,.15),
            (center_distance+165,71,117,-.10),
            (center_distance+420,86,130,.13)]):
            base=origin+direction*distance+right*skew*40
            ring=[]
            for j in range(13):
                a=2*math.pi*j/13
                radial=(1+.12*math.sin(3*a+.8*step)+.08*math.cos(5*a))
                pos=base+right*(rw*math.cos(a)*radial)+up*(rh*math.sin(a)*radial)
                ring.append(tuple(pos))
            rings.append(ring)
        verts=[v for ring in rings for v in ring]
        size=len(rings[0])
        faces=[tuple(reversed(range(size))),
               tuple(range((len(rings)-1)*size,len(rings)*size))]
        for k in range(len(rings)-1):
            for j in range(size):
                a=k*size+j;b=k*size+(j+1)%size
                faces.append((a,b,b+size,a+size))
        md=bpy.data.meshes.new('INT9_TEMP_PUBLIC_ATRIUM_BOOLEAN_CUTTER')
        md.from_pydata(verts,[],faces);md.update()
        cutter=bpy.data.objects.new(md.name,md)
        s.collection.objects.link(cutter)
        assert len(school.data.polygons)>=9
        school_poly_before=len(school.data.polygons)
        bpy.ops.object.select_all(action='DESELECT')
        school.select_set(True)
        bpy.context.view_layer.objects.active=school
        boolmod=school.modifiers.new('INT9_REAL_H1_CIVIC_ATRIUM_VACANCY','BOOLEAN')
        boolmod.operation='DIFFERENCE'
        boolmod.solver='EXACT'
        boolmod.object=cutter
        bpy.ops.object.modifier_apply(modifier=boolmod.name)
        bpy.data.objects.remove(cutter,do_unlink=True)
        assert len(school.data.polygons)>10,'School vanished / invalid cavity'
        assert all(math.isfinite(z) for v in school.data.vertices for z in v.co)
        after_h1=hit_camera('E11_H1_HUMAN')
        print('INT9_H1_REAL_PUBLIC_ATRIUM_CUT',school_poly_before,
              len(school.data.polygons),before['E11_H1_HUMAN'],after_h1,flush=True)
        # No mere ray-center preflight can claim ART or full walkability.
        # If the camera now sees the same school boundary, retain evidence
        # but do not make any image-pass claim.

        # Next the shared M247-C western fault, keeping the original solid,
        # is subdivided in-place to enable a genuine large sculpt deformation.
        bpy.ops.object.select_all(action='DESELECT')
        west.select_set(True)
        bpy.context.view_layer.objects.active=west
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.subdivide(number_cuts=7,smoothness=0)
        bpy.ops.object.mode_set(mode='OBJECT')
        assert len(west.data.vertices)>1900
        base_positions=[v.co.copy() for v in west.data.vertices]
        recorded_visibility={o.name:bool(o.hide_get()) for o in s.objects
                             if o.type=='MESH'}
        # Isolate visible mesh only in the viewport for actual source sculpt.
        for ob in s.objects:
            if ob.type=='MESH' and ob!=west:ob.hide_set(True)
        west.hide_set(False)
        # Aim real 3D viewport at a large face toward the central NAVE.
        desired=Vector((1.,-.3,.14)).normalized()
        viable=[poly for poly in west.data.polygons
                if poly.area>1e-5 and poly.normal.dot(desired)>.1]
        assert viable,'Existing western cliff is not facing NAVE'
        face=max(viable,key=lambda p:p.area*max(0.,p.normal.dot(desired))**2)
        focus=west.matrix_world@face.center
        normal=(west.matrix_world.to_3x3()@face.normal).normalized()
        points=[west.matrix_world@v.co for v in west.data.vertices]
        scale=max(max(v[k] for v in points)-min(v[k] for v in points) for k in range(3))
        eye=focus+normal*scale*1.45
        r3d.view_location=focus
        r3d.view_distance=scale*.97
        r3d.view_perspective='PERSP'
        r3d.view_rotation=(focus-eye).to_track_quat('-Z','Y')
        bpy.context.view_layer.update()
        area.tag_redraw()
        bpy.ops.object.mode_set(mode='SCULPT')
        with bpy.context.temp_override(window=win,area=area,region=region):
            if bpy.context.tool_settings.sculpt.brush is None:
                bpy.ops.brush.asset_activate(
                  asset_library_type='ESSENTIALS',asset_library_identifier='',
                  relative_asset_identifier='brushes/essentials_brushes-mesh_sculpt.blend/Brush/Clay Strips')
            brush=bpy.context.tool_settings.sculpt.brush
            assert brush is not None
            brush.size=330
            brush.strength=.97
            p=location_3d_to_region_2d(region,r3d,focus)
            assert p is not None
            inv=west.matrix_world.inverted()
            o=region_2d_to_origin_3d(region,r3d,p)
            d=region_2d_to_vector_3d(region,r3d,p)
            ok,h,n,faceidx=west.ray_cast(inv@o,(inv.to_3x3()@d).normalized(),distance=20000)
            assert ok, 'GUI projected ray must hit existing western architecture'
            strokes=[]
            for j,(ax,ay,bx,by) in enumerate([
               (-.33,-.17,.31,.23),(-.31,.20,.19,-.25),
               (-.15,.34,.29,-.17),(0.,-.31,.39,.12),
               (-.25,-.28,.25,.26)]):
                line=[]
                for k in range(43):
                    frac=k/42
                    x=p.x+(ax+(bx-ax)*frac)*region.width
                    y=p.y+(ay+(by-ay)*frac)*region.height
                    line.append({'name':'stroke','mouse':(0.,0.),
                         'mouse_event':(float(x),float(y)),
                         'location':tuple(focus),
                         'is_start':k==0,
                         'pressure':.95,
                         'size':1.,
                         'time':k*.018,'x_tilt':0.,'y_tilt':0.})
                result=bpy.ops.sculpt.brush_stroke(
                    stroke=line,override_location=True)
                strokes.append({'index':j,'return':sorted(result)})
                assert 'FINISHED' in result
        bpy.ops.object.mode_set(mode='OBJECT')
        diff=[(v.co-old).length for v,old in zip(west.data.vertices,base_positions)]
        changed=sum(q>.02 for q in diff)
        maximum=max(diff)
        print('INT9_REAL_GUI_CLIFF_SCULPT',changed,round(maximum,4),flush=True)
        assert changed>=20 and maximum>.5,('NO_MEANINGFUL_ACTUAL_GUI_SCULPT',changed,maximum)
        for name,flag in recorded_visibility.items():
            bpy.data.objects[name].hide_set(flag)
        assert all(bpy.data.objects[name].hide_get()==flag
                   for name,flag in recorded_visibility.items())
        for name,old in cameras.items():
            now=bpy.data.objects[name].matrix_world
            assert max(abs(now[i][k]-old[i][k]) for i in range(4) for k in range(4))<1e-6
        assert s['CONSTRUCTION']=='HOLD'
        assert s['FORMAL_ART_ACCEPTED']==s['COMPLETED_TARGETS']==0
        s['INT9_GUI_SOURCE_SHA256']=PARENT_SHA
        s['INT9_SCHOOL_CIVIC_ATRIUM_REWORK']='DIRECT_CUT_IN_EXISTING_BUILDING'
        s['INT9_WEST_FAULT_SCULPT']='VISIBLE_GUI_BRUSH_OPERATOR_NOT_X11_MOUSE'
        s['INT9_ART_ADOPTION']=0
        s['INT9_RESEARCH_METRES_NOT_REGISTERED_WORLD_COORDINATES']=True
        s.camera=bpy.data.objects['E11_URBAN_AERIAL']
        dst=ROOT/'HALO9_INT9_CIVIC_ATRIUM_AND_SCULPTED_FAULT.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=True)
        result={'schema':'halo9-int9-native-civic-fault-v1',
          'source_sha256':PARENT_SHA,
          'blend_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),
          'h1_school_atrium_before_poly':school_poly_before,
          'h1_school_atrium_after_poly':len(school.data.polygons),
          'h1_cam_center_before':before['E11_H1_HUMAN'],
          'h1_cam_center_after':after_h1,
          'western_sculpt_vertices':len(base_positions),
          'actual_brush_operator_strokes':strokes,
          'western_real_vertices_changed':changed,
          'western_real_max_displacement_m':round(maximum,6),
          'original_camera_matrices_unchanged':True,
          'previous_visibility_restored':True,
          'functional_access':'UNKNOWN_NO_COMPLETE_3D_ROUTE_PROOF',
          'formal_art_adopted':0,'completed_targets':0,
          'minecraft':'HOLD','art':'UNREVIEWED'}
        (ROOT/'AUTHOR_SUCCESS.json').write_text(json.dumps(result,indent=2))
        print('INT9_GUI_REAL_SCULPT_AND_CIVIC_REWORK_SAVED',
              result['blend_sha256'],flush=True)
        return None
    except Exception as exc:
        (ROOT/'AUTHOR_FAILURE.json').write_text(json.dumps(
          {'error':repr(exc),'traceback':traceback.format_exc()},indent=2))
        print('INT9_AUTHOR_FAILED',repr(exc),flush=True)
        return None

bpy.app.timers.register(edit_civic_section,first_interval=1.7)
