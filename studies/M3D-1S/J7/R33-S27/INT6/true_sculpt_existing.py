"""HALO-9 INT6: Actual Blender Sculpt Mode/brush test on existing research 3D.

NOT a new procedural shell/block design. Edit three selected *existing*
floating inhabited sections from INT4-R1, using the official Blender sculpt
brush-stroke operator in a 3D viewport. Abort unless actual vertices MOVE.
Preserve full original camera matrices and whole public-space scene.
Noncanonical research only. Never change main, Freeze, source, Minecraft.
"""
import bpy,sys,hashlib,json,math
from mathutils import Vector
from pathlib import Path
from bpy_extras.view3d_utils import (location_3d_to_region_2d,region_2d_to_vector_3d,region_2d_to_origin_3d)

params=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
output=Path(params[params.index('--output')+1])
output.mkdir(parents=True,exist_ok=True);(output/'renders').mkdir(exist_ok=True)
SOURCE='7cf765923b91f06cce7951fc3558f042e488bf9f1157791b59b14d11954dc2bb'
source=Path(bpy.data.filepath)
assert source.name=='INT6_SOURCE.blend' and hashlib.sha256(source.read_bytes()).hexdigest()==SOURCE
S=bpy.context.scene
assert S['CONSTRUCTION']=='HOLD' and S['FORMAL_ART_ACCEPTED']==S['COMPLETED_TARGETS']==0
original_cameras=['E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL']
matrices={n:bpy.data.objects[n].matrix_world.copy() for n in original_cameras}
sculpt_collection=bpy.data.collections.new('INT6_TRUE_SCULPTED_EDITABLE_DISTRICTS')
S.collection.children.link(sculpt_collection)
targets=[
 ('M247_WEST_LOWER_INHABITED_LIMESTONE_urban_occupied_stratum_2',
  (-310,-610,270),'west',(-1.0,-1.6,.67)),
 ('M247_EAST_CHIRAL_INHABITED_QUARTERS_urban_occupied_stratum_2',
  (700,160,100),'east',(1.3,-1.5,.66)),
 ('M247_BETA_DISPLACED_SUSPENDED_CITY_urban_occupied_stratum_1',
  (740,1090,1150),'beta',(1.0,-1.3,.9)),
]
# A flat-patch artwork is not valid. Each selected existing urban district is
# thickened on its lower face before brushing to obtain actual occupied cliff.
# The public access streets and inner civic room geometry stay untouched.

def bbox(o):
    vv=[o.matrix_world @ v.co for v in o.data.vertices]
    return [(min(a[i] for a in vv),max(a[i] for a in vv)) for i in range(3)]

def viewport():
    win=bpy.context.window
    assert win is not None,'Blender SCULPT needs a UI window even in background context'
    for area in win.screen.areas:
        if area.type=='VIEW_3D':
            for region in area.regions:
                if region.type=='WINDOW':
                    return win,area,region,area.spaces.active.region_3d
    raise RuntimeError('NO_VIEW3D_REGION_FOR_REAL_BRUSH')

def stroke_samples(region,points,pixel_center,location3d):
    mid=pixel_center
    result=[]
    for j,(px,py,pressure) in enumerate(points):
        result.append({
            'name':'stroke',
            'mouse':(0.0,0.0),
            'mouse_event':(float(mid[0]+px*region.width),float(mid[1]+py*region.height)),
            'is_start':j==0,
            'location':tuple(location3d),
            'pressure':float(pressure),
            'time':.018*j,
            'size':1.,
            'x_tilt':0.,'y_tilt':0.
        })
    return result

def line(x0,y0,x1,y1,weight=1.,samples=38):
    return [(x0+(x1-x0)*i/(samples-1),y0+(y1-y0)*i/(samples-1),
             weight*(.88+.12*math.sin(math.pi*i/(samples-1))))
            for i in range(samples)]

records=[]
for k,(label,_,district,view_direction) in enumerate(targets):
    original=bpy.data.objects.get('INT4_'+label)
    assert original is not None and original.type=='MESH',(label,'ORIGINAL_NOT_FOUND')
    assert len(original.data.polygons)>=5
    # Editable duplicate physically replaces only its own rejected paper floor,
    # so the research source object remains present but hidden from final render.
    target=original.copy()
    target.data=original.data.copy()
    target.name='INT6_TRUE_BRUSH_'+district
    sculpt_collection.objects.link(target)
    target.hide_render=False
    original.hide_render=True
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True);bpy.context.view_layer.objects.active=target
    # A real 2-sided inhabited ledge requires substantial structural depth.
    before_bounds=bbox(target)
    zbase=min(v.co.z for v in target.data.vertices)
    for v in target.data.vertices:
        if abs(v.co.z-zbase)<.0001:
            v.co.z-=(80 if district=='beta' else 125)
    target.data.update()
    # Subdivision supplies enough vertices for sculpt; not a new box generator.
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.subdivide(number_cuts=14,smoothness=0)
    bpy.ops.object.mode_set(mode='OBJECT')
    assert len(target.data.vertices)>800
    native_before=[v.co.copy() for v in target.data.vertices]
    bounds=bbox(target)
    center=Vector(tuple((a+b)/2 for a,b in bounds))
    size=max(b-a for a,b in bounds)
    win,area,region,r3d=viewport()
    # Aim at the CENTER OF A REAL FRONT-FACING SURFACE, not a potentially
    # invisible bounding-box center inside the 3D building.
    approx=Vector(view_direction).normalized()
    def visual_area(poly):
        facing=max(.0,poly.normal.dot(approx))
        return poly.area*(facing**2)
    face=max(target.data.polygons,key=visual_area)
    surface=target.matrix_world @ face.center
    outward=(target.matrix_world.to_3x3() @ face.normal).normalized()
    viewer=surface+outward*(size*1.45)
    r3d.view_location=surface
    r3d.view_distance=size*.98
    r3d.view_perspective='PERSP'
    r3d.view_rotation=(surface-viewer).to_track_quat('-Z','Y')
    bpy.context.view_layer.update()
    area.tag_redraw()
    projected=location_3d_to_region_2d(region,r3d,surface)
    assert projected is not None,('SCULPT_SURFACE_NOT_PROJECTED',district)
    # Independent 3D view-ray tests; Sculpt operator FINISHED alone is fake evidence.
    origin=region_2d_to_origin_3d(region,r3d,projected)
    direction=region_2d_to_vector_3d(region,r3d,projected)
    matinv=target.matrix_world.inverted()
    hit,point,normal,face_idx=target.ray_cast(
        matinv@origin,(matinv.to_3x3()@direction).normalized(),distance=20000)
    print('INT6_VIEWPORT_SURFACE_RAY',district,
        {'region':[region.width,region.height],'area':[area.width,area.height],
         'surface':tuple(round(v,2) for v in surface),
         'pixel':tuple(round(v,2) for v in projected),
         'ray_hit':hit,'face':face_idx,
         'mode':bpy.context.mode},flush=True)
    if not hit:
        raise RuntimeError(('VIEWPORT_RAY_DID_NOT_HIT_TARGET',district))
    try:
        bpy.ops.ed.undo_push()
    except Exception as exc:
        print('INT6_UNDO_STACK_INIT_NONFATAL',str(exc),flush=True)
    bpy.ops.object.mode_set(mode='SCULPT')
    with bpy.context.temp_override(window=win,area=area,region=region):
        act=bpy.ops.brush.asset_activate(
            asset_library_type='ESSENTIALS',
            asset_library_identifier='',
            relative_asset_identifier='brushes/essentials_brushes-mesh_sculpt.blend/Brush/Clay Strips')
        assert 'FINISHED' in act,('SCULPT_BRUSH_ASSET_NOT_LOADED',act)
        brush=bpy.context.tool_settings.sculpt.brush
        assert brush is not None
        brush.size=max(100,int(min(region.width,region.height)*.24))
        brush.strength=.69
        print('INT6_SCULPT_RUNTIME',district,
            {'mode':bpy.context.mode,'active_object':bpy.context.active_object.name,
             'brush':brush.name,'brush_size':brush.size,
             'strength':brush.strength},flush=True)
        paths=[
          line(-.34,-.09,.31,.18,.97),
          line(-.24,.26,.23,-.16,1.),
          line(-.30,-.23,.23,.11,.92),
          line(-.13,.34,.35,-.13,.78)
        ]
        for idx,points in enumerate(paths):
            retval=bpy.ops.sculpt.brush_stroke(
                stroke=stroke_samples(region,points,projected,surface),override_location=True)
            assert 'FINISHED' in retval,('BRUSH_OPERATOR_FAILED',district,idx,retval)
            print('INT6_REAL_SCULPT_STROKE',district,idx,retval,flush=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    # Quantify real Blender sculpt effect, not only thickening/subdivision.
    native_after=[v.co.copy() for v in target.data.vertices]
    assert len(native_after)==len(native_before)
    displacements=[(a-b).length for a,b in zip(native_after,native_before)]
    changed=sum(d>.02 for d in displacements)
    maxshift=max(displacements)
    print('INT6_TRUE_BRUSH_CHANGED_VERTICES',district,changed,'of',
          len(displacements),'max_m',round(maxshift,4),flush=True)
    assert changed>30 and maxshift>.12,('BRUSH_DID_NOT_CHANGE_MESH',district,changed,maxshift)
    assert all(math.isfinite(c) for v in target.data.vertices for c in v.co[:])
    assert len(target.data.polygons)>1200
    bbox_after=bbox(target)
    records.append({
        'district':district,'replaced_research_object':original.name,
        'sculpt_object':target.name,
        'geometry_before':before_bounds,'geometry_after':bbox_after,
        'sculpt_brush_asset':'ESSENTIALS/Clay Strips',
        'subdivided_vertex_count':len(native_after),
        'brush_strokes':4,'true_vertices_changed':changed,
        'max_brush_displacement_m':round(maxshift,5)
    })
    original.hide_render=True

# Main viewpoints are immutable. Optional close-ups evidence actual surface
# instead of making the original fixed human/aerial screenshots look better
# by swapping their camera location. They are labeled as NEW views.
for name,m in matrices.items():
    now=bpy.data.objects[name].matrix_world
    assert max(abs(now[i][j]-m[i][j]) for i in range(4) for j in range(4))<1e-6
for n,ob in (
 ('INT6_WEST_SCULPT_DETAIL',bpy.data.objects['INT6_TRUE_BRUSH_west']),
 ('INT6_EAST_SCULPT_DETAIL',bpy.data.objects['INT6_TRUE_BRUSH_east'])
):
    bounds=bbox(ob)
    center=Vector(tuple((a+b)/2 for a,b in bounds))
    dist=max(b-a for a,b in bounds)*1.12
    eye=center+Vector((1,-1,.50)).normalized()*dist
    data=bpy.data.cameras.new(n);cam=bpy.data.objects.new(n,data)
    sculpt_collection.objects.link(cam)
    cam.location=eye
    cam.rotation_euler=(center-eye).to_track_quat('-Z','Y').to_euler()
    data.type='PERSP';data.lens=31
S['INT6_PARENT_SHA256']=SOURCE
S['INT6_TRUE_BRUSH_STROKES']=sum(r['brush_strokes'] for r in records)
S['INT6_SCULPT_METHOD']='BLENDER_SCULPT_MODE_BRUSH_STROKE_NOT_CODED_VERTICES_ONLY'
S['INT6_RESEARCH_COORDS']='UNREGISTERED_METRES'
S['CONSTRUCTION']='HOLD';S['FORMAL_ART_ACCEPTED']=0;S['COMPLETED_TARGETS']=0
S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=14
S.cycles.use_denoising=True;S.render.threads_mode='FIXED';S.render.threads=2
S.render.resolution_x=1100;S.render.resolution_y=825
S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG'
views=original_cameras+['INT6_WEST_SCULPT_DETAIL','INT6_EAST_SCULPT_DETAIL']
S.camera=bpy.data.objects[original_cameras[-1]]
dst=output/'HALO9_INT6_TRUE_BRUSH_SCULPT_DISTRICTS.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=True)
render_hashes={}
for v in views:
    S.camera=bpy.data.objects[v]
    path=output/'renders'/(v+'.png')
    S.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    assert path.exists() and path.stat().st_size>5000
    render_hashes[v]=hashlib.sha256(path.read_bytes()).hexdigest()
    print('INT6_TRUE_BLENDER_VIEW',v,path.stat().st_size,flush=True)
S.camera=bpy.data.objects[original_cameras[-1]]
bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=True)
report={
    'schema':'halo9-int6-true-native-sculpt-brush-study-v1',
    'source_sha256':SOURCE,
    'blend_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),
    'authoring_method':'ACTUAL_SCULPT_BRUSH_OPERATOR_NOT_GUI_HAND_CONTROL',
    'original_three_camera_matrices_unchanged':True,
    'brush_sculpt_records':records,
    'render_sha256':render_hashes,
    'extra_closeups_are_new_cameras':True,
    'function':'UNKNOWN_NO_PEDESTRIAN_QA',
    'formal_art_adopted':0,'completed_targets':0,
    'minecraft_construction':'HOLD',
    'art':'UNREVIEWED_NOT_ADOPTED'
}
(output/'INT6_NATIVE_EVIDENCE.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('INT6_ACTUAL_SCULPT_COMPLETE',report['blend_sha256'],flush=True)
