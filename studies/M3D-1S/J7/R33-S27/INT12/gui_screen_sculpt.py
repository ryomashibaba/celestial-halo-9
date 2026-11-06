"""INT12: real visible Blender GUI, fixed-E11-screen-directed native 3D sculpt.
No new architecture primitives: rework existing rejected egg-like M247-C
volumes in-place. Remove repetitive rejected blue ribs, keep actual M247-C
diagonal seam. Recompose image-facing surfaces by measured 3D projection.

No X11 hand-sculpt claim; GUI visual feedback + native mesh vertex sculpt,
not formal art. Independent renderer must independently reopen the BLEND.
"""
import bpy,json,hashlib,math,traceback
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path('/tmp/halo9-int12');ROOT.mkdir(exist_ok=True)
SOURCE='2ec37b65868509060a499e9c648c3030aa3d008a7a9f603a2598dc4358b2140e'
p=Path(bpy.data.filepath)
assert p.name=='INT12_SOURCE.blend'
assert hashlib.sha256(p.read_bytes()).hexdigest()==SOURCE
assert not bpy.app.background,'INT12 must run in actual visible Blender GUI'
scene=bpy.context.scene
assert scene['CONSTRUCTION']=='HOLD' and scene['FORMAL_ART_ACCEPTED']==scene['COMPLETED_TARGETS']==0
cameras=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
camera_matrices={n:[[float(z) for z in row] for row in bpy.data.objects[n].matrix_world] for n in cameras}
w0names=('W0_NORTH_FRACTURED_RANGE','W0_WEST_BASALT_ESCARPMENT',
         'W0_GROUND_BASIN','W0_EASTERN_ARTIFICIAL_SEA')
def hash_geometry(ob):
    h=hashlib.sha256()
    for v in ob.data.vertices:
        h.update((','.join(format(float(x),'.10g') for x in v.co)+';').encode())
    return h.hexdigest()
W0={n:hash_geometry(bpy.data.objects[n]) for n in w0names}
M247WEST='INT11_M247C_ALPHA_WEST_ACCRETED_ARCHIVE'
M247EAST='INT11_M247C_ALPHA_EAST_CIVIC_HIGH_CITY'
M247FLOAT='INT11_M247C_ALPHA_FLOATING_SEVERED_NORTH'
assert all(n in bpy.data.objects for n in [M247WEST,M247EAST,M247FLOAT])
win=bpy.context.window
views=[a for a in win.screen.areas if a.type=='VIEW_3D']
assert win is not None and views,'actual on-screen VIEW_3D missing'
area=max(views,key=lambda a:a.width*a.height)
area.spaces.active.region_3d.view_perspective='CAMERA'
scene.camera=bpy.data.objects['E11_NAVE_HUMAN']
bpy.context.view_layer.update()
area.tag_redraw()
start={
 'schema':'halo9-int12-fixed-image-directed-sculpt',
 'source_sha256':SOURCE,'actual_gui':not bpy.app.background,
 'preserved_cameras':camera_matrices,
 'protected_W0_sha256':W0,
 'preserved_beta_slanted_seam':'INT11_M247C_BETA_SLANTED_CIVIC_SEAM',
 'formal_art':0,'completed_targets':0,'minecraft':'HOLD'
}
(ROOT/'GUI_READY.json').write_text(json.dumps(start,indent=2))
print('INT12_TRUE_GUI_FIXED_CAMERA_READY',flush=True)

def camera_hit(name,u,v):
    cam=bpy.data.objects[name]
    frame=cam.data.view_frame(scene=scene)
    xx=[r.x for r in frame];yy=[r.y for r in frame]
    point=Vector((min(xx)+u*(max(xx)-min(xx)),
                 min(yy)+v*(max(yy)-min(yy)),
                 sum(r.z for r in frame)/len(frame)))
    origin=cam.matrix_world.translation
    direction=(cam.matrix_world.to_3x3()@point).normalized()
    ok,location,normal,idx,obj,m=scene.ray_cast(
        bpy.context.evaluated_depsgraph_get(),origin,direction,distance=9000)
    return {'name':obj.name if ok else 'SKY',
            'distance':round(float((location-origin).length),3) if ok else None}
def sample(name):
    return {f'{u:.2f},{v:.2f}':camera_hit(name,u,v)
        for u in (.17,.33,.50,.67,.83)
        for v in (.18,.34,.50,.66,.82)}
def scene_counts(data):
    result={}
    for n,hits in data.items():
        names={}
        for val in hits.values():
            key=val['name'];names[key]=names.get(key,0)+1
        result[n]=sorted(names.items(),key=lambda x:-x[1])[:10]
    return result

def recompose_existing_surface(obj,cam_name,amount,seed):
    """Screen-space MASK sculpt: real vertices only, actual fixed camera.
    Non-GUI synthesis is explicitly distinct from Blender brush_stroke.
    Surface in lens is pushed *into* its native building mass to reveal its
    previously existing internal Boolean spaces; no replacement egg or loft.
    """
    cam=bpy.data.objects[cam_name]
    cam_pos=cam.matrix_world.translation.copy()
    mat=obj.matrix_world
    inv=mat.inverted()
    verts=obj.data.vertices
    data=[]
    for v in verts:
        world=mat@v.co
        projection=world_to_camera_view(scene,cam,world)
        d=(world-cam_pos).length
        if projection.z>0 and math.isfinite(d):
            data.append((v,world,float(projection.x),float(projection.y),d))
    if len(data)<300:raise RuntimeError(('NOT_ENOUGH_VISIBLE_PROJECTED_VERTICES',obj.name,len(data)))
    depths=sorted(z[4] for z in data)
    near=depths[int(.21*len(depths))]
    far=depths[int(.58*len(depths))]
    moved=0;maxdelta=0.;maxscreen=0.
    # One asymmetrical negative-space incision with deeply re-entrant
    # branches; avoid flat circular/spherical replacements and pure ellipses.
    for v,world,u,w,d in data:
        if not (-.10<u<1.1 and -.1<w<1.1):continue
        if d>far:continue
        # Central shared urban forum and two branching public side courts.
        centers=((.51,.47,.26,.32,1.0),(.30,.61,.17,.19,.55),
                 (.77,.35,.16,.24,.70))
        weight=0.
        for x,y,sx,sy,k in centers:
            form=((u-x)/sx)**4 + ((w-y)/sy)**4
            weight+=k*math.exp(-.55*form)
        weight=min(1.0,weight)
        if weight<.06:continue
        norm=math.sqrt((u-.51)**2+(w-.47)**2)
        jagged=.80+.13*math.sin(u*27.3+seed)+.09*math.cos(w*36.1-seed)
        taper=max(.12,min(1.,(far-d)/(far-near+1e-6)))
        dist=amount*weight*jagged*taper
        if dist<.5:continue
        # A tangible nonplanar recessed inhabited excavation, pushed
        # away from the original human eye; different direction at edges.
        direction=(world-cam_pos).normalized()
        lateral=Vector((-direction.y,direction.x,0))
        if lateral.length>.1:lateral.normalize()
        move=direction*dist + lateral*dist*.18*math.sin(w*9.1+seed)
        new=world+move
        v.co=inv@new
        moved+=1;maxdelta=max(maxdelta,move.length)
        maxscreen=max(maxscreen,weight)
    obj.data.update()
    print('INT12_FIXED_SCREEN_NATIVE_SCULPT',obj.name,cam_name,moved,round(maxdelta,3),flush=True)
    return {'target':obj.name,'fixed_camera':cam_name,'changed_vertices':moved,
            'max_world_displacement':round(maxdelta,5),
            'screen_mask_max':round(maxscreen,4),
            'depth_quantiles':[round(near,2),round(far,2)],
            'method':'REAL_VERTICES_MOVED_BY_E11_SCREEN_PROJECTION_NOT_GUI_MOUSE'}
completed={'started':False}
def perform_once():
    if not (ROOT/'BEGIN_EDIT').exists():return .35
    if completed['started']:return None
    completed['started']=True
    try:
        # Remove the four repeated oversized blue structural ribs and five
        # floating-rock supports from this rejected isolated copy. They
        # are not the fixed beta slanted seam.
        strips=[
            o for o in list(scene.objects) if o.type=='MESH' and
            (o.name.startswith('INT11_NAVE_OCCUPIED_CROSS_VAULT_') or
             o.name.startswith('INT11_H1_INHABITED_ROCK_SUPPORT_'))
        ]
        assert len(strips)>=7,('REJECTED_REPEATED_PIPES_NOT_FOUND',len(strips))
        for ob in strips:bpy.data.objects.remove(ob,do_unlink=True)
        assert 'INT11_M247C_BETA_SLANTED_CIVIC_SEAM' in bpy.data.objects
        bpy.context.view_layer.update()
        before={n:sample(n) for n in cameras[:2]}
        print('INT12_FIXED_CAMERA_HITS_BEFORE_SCULPT',scene_counts(before),flush=True)
        # Move ONLY existing rejected shell vertices, never make another
        # slab, outer shell, roof, massive eggs, or sets of boxes.
        edits=[
            recompose_existing_surface(bpy.data.objects[M247WEST],
                                       'E11_NAVE_HUMAN',430.,2.5),
            recompose_existing_surface(bpy.data.objects[M247EAST],
                                       'E11_H1_HUMAN',530.,4.1)
        ]
        assert sum(x['changed_vertices'] for x in edits)>100
        assert min(x['max_world_displacement'] for x in edits)>25
        bpy.context.view_layer.update()
        after={n:sample(n) for n in cameras[:2]}
        print('INT12_FIXED_CAMERA_HITS_AFTER_SCULPT',scene_counts(after),flush=True)
        # The actual geometry and camera transforms, not brightness, are
        # the TECH gate. ART remains independently assessed from images.
        for name,mat in camera_matrices.items():
            current=bpy.data.objects[name].matrix_world
            assert max(abs(current[i][j]-mat[i][j])
                       for i in range(4) for j in range(4))<1e-6
        assert all(hash_geometry(bpy.data.objects[n])==sha for n,sha in W0.items())
        assert scene['CONSTRUCTION']=='HOLD' and scene['FORMAL_ART_ACCEPTED']==scene['COMPLETED_TARGETS']==0
        scene['INT12_PARENT_SHA256']=SOURCE
        scene['INT12_METHOD']='SCREEN_SPACE_DIRECT_MESH_SCULPT_IN_VISIBLE_BLENDER_GUI_NOT_MOUSE_BRUSH'
        scene['INT12_COMPLETED_TARGETS']=0
        scene['INT12_ART_ACCEPTED']=0
        scene['INT12_FUNCTION']='NOT_VALIDATED'
        scene.camera=bpy.data.objects['E11_NAVE_HUMAN']
        p=ROOT/'HALO9_INT12_E11_SCREEN_DIRECT_NATIVE_RESCULPT.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(p),compress=True)
        report={
          'schema':'halo9-int12-real-gui-fixed-screen-direct-sculpt-v1',
          'parent_sha256':SOURCE,
          'saved_blend_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
          'real_gui':True,
          'deleted_rejected_ribs':[o.name for o in strips],
          'preserved_beta_slanted_seam':True,
          'sculpted_original_meshes':edits,
          'camera_hit_map_before':before,'camera_hit_map_after':after,
          'fixed_camera_matrices':camera_matrices,
          'protected_W0_sha256':W0,
          'new_external_city_objects_created':0,
          'method_not_x11_hand_brush':True,
          'function':'UNKNOWN',
          'formal_art_accepted':0,'completed_targets':0,
          'minecraft':'HOLD','art':'UNREVIEWED_NOT_ADOPTED'
        }
        (ROOT/'GUI_AUTHOR_SUCCESS.json').write_text(json.dumps(report,indent=2))
        print('INT12_REAL_VISIBLE_GUI_DIRECT_SCULPT_SAVED',report['saved_blend_sha256'],flush=True)
        area.tag_redraw()
        return None
    except Exception as e:
        failure={'error':repr(e),'traceback':traceback.format_exc()}
        (ROOT/'GUI_AUTHOR_FAILURE.json').write_text(json.dumps(failure,indent=2))
        print('INT12_REAL_GUI_NATIVE_SCULPT_FAILED',repr(e),flush=True)
        return None
bpy.app.timers.register(perform_once,first_interval=1.5)
