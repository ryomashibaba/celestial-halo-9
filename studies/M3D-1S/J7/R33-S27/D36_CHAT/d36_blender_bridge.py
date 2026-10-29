#!/usr/bin/env python3
"""D36 Blender 5.2 background bridge (UNEXECUTED in Chat: bpy is unavailable).

blender --background --factory-startup --python-exit-code 12 \
    --python d36_blender_bridge.py -- D36_EDIT_PLAN.json D36_OUTPUT

Creates a NEW native .blend and edited GLB; never overwrites source GLB.
The .blend contains an editable sculpt shape key (Basis + D36_SCULPT_EDIT).
Only a named permitted mesh is deformable; nontarget meshes are protected.
This is a Blender-run recipe; its behavior must be checked on a Blender machine.
"""
import sys, os, json, math, hashlib
from pathlib import Path


def sha(data): return hashlib.sha256(data).hexdigest()


def vec3(values):
    if not isinstance(values, (list,tuple)) or len(values)!=3: raise ValueError('Expected vec3')
    a=tuple(float(v) for v in values)
    if not all(math.isfinite(v) for v in a): raise ValueError('Non-finite input')
    return a


def validate(plan, src, geom_names):
    if plan.get('schema')!='halo9.d36.sculpt.v1':raise ValueError('Wrong schema')
    if plan.get('art_status')!='TECHNICAL_FIXTURE_ONLY':raise ValueError('Not a technical fixture')
    if plan['source_sha256']!=sha(src.read_bytes()):raise ValueError('Source GLB SHA mismatch')
    if set(geom_names)!=(set(plan['protected_geometries'])|{plan['target_geometry']}):
        raise ValueError('Unexpected mesh or missing protected object')
    if plan['target_geometry'] in plan['protected_geometries']:raise ValueError('Target protected')
    if not plan.get('protect_original',False):raise ValueError('Source protection required')
    if not 1<=len(plan.get('strokes',[]))<=12:raise ValueError('Unsafe stroke count')
    for s in plan['strokes']:
        f=vec3(s['center_fraction']); d=vec3(s['delta_xyz_m']); r=float(s['radius_m'])
        if any(t<0 or t>1 for t in f) or s.get('falloff')!='smoothstep':raise ValueError('Bad sculpt center/falloff')
        if not (1<=r<=750) or sum(t*t for t in d)>300**2:raise ValueError('Unsafe sculpt radius/displacement')


def main(plan_path, output_dir):
    import bpy
    from mathutils import Vector
    if bpy.app.version<(4,3,0):raise RuntimeError('Requires Blender version with supported glTF importer')
    plan_path=Path(plan_path).resolve(); base_dir=plan_path.parent
    plan=json.loads(plan_path.read_text(encoding='utf-8'))
    source=(base_dir / plan['source_filename']).resolve()
    if source.parent!=base_dir or source.suffix.lower()!='.glb':raise ValueError('Source must be local GLB fixture')
    output_dir=Path(output_dir).resolve()
    if output_dir==base_dir:raise ValueError('Output directory must be a separate directory')
    # Strictly avoid overwriting any old result. The launcher uses a new timestamp-free output directory.
    if output_dir.exists():raise ValueError('Output directory already exists. Use a new directory.')
    output_dir.mkdir(parents=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    objects={obj.name:obj for obj in bpy.context.scene.objects if obj.type=='MESH'}
    validate(plan,source,list(objects))
    for obj in objects.values():
        if obj.data.shape_keys is not None:raise ValueError('Pre-existing morph keys are unsupported')
    target=objects[plan['target_geometry']]
    # Verify and fingerprint nontarget vertex positions without changing them.
    protected={}
    for name in plan['protected_geometries']:
        obj=objects[name]
        protected[name]=sha(json.dumps([tuple(round(c,6) for c in v.co) for v in obj.data.vertices],separators=(',',':')).encode())
    from mathutils import Vector
    basis=target.shape_key_add(name='Basis',from_mix=False)
    edit=target.shape_key_add(name='D36_SCULPT_EDIT',from_mix=False)
    mx=target.matrix_world
    minmax=[(min((mx@v.co)[i] for v in target.data.vertices),max((mx@v.co)[i] for v in target.data.vertices)) for i in range(3)]
    strokes=[]
    for s in plan['strokes']:
        center=Vector([minmax[i][0]+float(s['center_fraction'][i])*(minmax[i][1]-minmax[i][0]) for i in range(3)])
        strokes.append((center,float(s['radius_m']),Vector(vec3(s['delta_xyz_m']))))
    inverse=mx.inverted_safe().to_3x3()
    moved=0; max_displacement=0.0
    for idx,v in enumerate(target.data.vertices):
        world=mx@v.co
        delta_world=Vector((0,0,0))
        for center,radius,shift in strokes:
            f=max(0.0,1.0-(world-center).length/radius)
            f=f*f*(3-2*f)
            delta_world+=f*shift
        if delta_world.length>1e-5:moved+=1
        max_displacement=max(max_displacement,delta_world.length)
        edit.data[idx].co=basis.data[idx].co+inverse@delta_world
    if moved<30:raise ValueError('Edit hit fewer than 30 vertices: check glTF axes and scale')
    edit.value=1.0
    target['D36_ART_STATUS']='TECHNICAL_FIXTURE_ONLY'
    target['D36_SOURCE_SHA256']=plan['source_sha256']
    bpy.context.view_layer.update()
    for name in plan['protected_geometries']:
        obj=objects[name]
        signature=sha(json.dumps([tuple(round(c,6) for c in v.co) for v in obj.data.vertices],separators=(',',':')).encode())
        if signature!=protected[name]:raise ValueError('Protected mesh modified: '+name)
    # Add authoring cameras. The native .blend is freely editable in Blender UI.
    allcoords=[obj.matrix_world@v.co for obj in objects.values() for v in obj.data.vertices]
    bounds=[(min(x[i] for x in allcoords),max(x[i] for x in allcoords)) for i in range(3)]
    center=Vector([(lo+hi)/2 for lo,hi in bounds]); extent=max(hi-lo for lo,hi in bounds)
    camera_vectors={
        'south':Vector((0,-2.3,0.32)), 'north':Vector((0,2.3,0.32)),
        'east':Vector((2.3,0,0.32)), 'west':Vector((-2.3,0,0.32)),
        'aerial':Vector((1.3,-1.2,1.9)), 'oblique':Vector((1.7,-1.7,0.8))}
    rig=bpy.data.collections.new('D36_REVIEW_CAMERAS');bpy.context.scene.collection.children.link(rig)
    cameras={}
    for name,dir in camera_vectors.items():
        data=bpy.data.cameras.new('D36_'+name+'_camera');cam=bpy.data.objects.new('D36_CAM_'+name,data)
        rig.objects.link(cam);cam.location=center+dir*extent
        direction=center-cam.location;cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
        cam.data.type='ORTHO';cam.data.ortho_scale=extent*2.6;cameras[name]=cam
    scene=bpy.context.scene
    scene.render.resolution_x=1000;scene.render.resolution_y=650;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.camera=cameras['oblique']
    try:scene.render.engine='BLENDER_WORKBENCH'
    except (TypeError,ValueError):pass
    # Save editable .blend first so changes can be manually continued.
    blend=output_dir/'D36_EDITABLE_SCULPT_STUDY.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend),check_existing=False)
    glb=output_dir/'D36_BLENDER_OUTPUT.glb'
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=False)
    renders={}
    for name,cam in cameras.items():
        scene.camera=cam;scene.render.filepath=str(output_dir/('D36_BLENDER_'+name+'.png'))
        try:
            bpy.ops.render.render(write_still=True)
            renders[name]=Path(scene.render.filepath).exists()
        except Exception as exc:
            renders[name]='RENDER_NOT_AVAILABLE: '+str(exc)[:150]
    audit={'blender_version':bpy.app.version_string,'source_sha256':plan['source_sha256'],
           'protected_local_mesh_digests':protected,
           'original_source_untouched':sha(source.read_bytes())==plan['source_sha256'],
           'protected_names':plan['protected_geometries'],'target_name':target.name,
           'moved_vertices':moved,'maximum_world_displacement_m':max_displacement,
           'shape_key':'D36_SCULPT_EDIT','native_blend_exists':blend.exists(),'export_glb_exists':glb.exists(),
           'blender_glb_sha256':sha(glb.read_bytes()) if glb.exists() else None,
           'render_results':renders,'art_adoption':False,'minecraft_construction':False}
    (output_dir/'D36_BLENDER_AUDIT.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if not audit['native_blend_exists'] or not audit['export_glb_exists']:
        raise RuntimeError('Blender failed to emit required files')
    print('D36 Blender bridge complete:',json.dumps(audit))


if __name__=='__main__':
    if '--' not in sys.argv: raise SystemExit('Usage: blender -b --python d36_blender_bridge.py -- plan.json OUTPUT_DIRECTORY')
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=2:raise SystemExit('Expected plan and new output directory')
    main(*args)
