#!/usr/bin/env python3
"""Execute a native Blender (bpy) pipeline. Must run in genuine bpy environment.

Save editable shape-key .blend, and an independently baked, plain GLB for QA.
Not a formal building or a general-purpose sculpt system. Does not render art.
"""
import sys,json,hashlib
from pathlib import Path
import numpy as np
from d37_kernel import validate,apply,sha

def main(planpath,outdir):
    try:import bpy
    except ImportError as e:raise RuntimeError('BLENDER_NOT_AVAILABLE: this step MUST run with genuine bpy') from e
    planpath=Path(planpath).resolve();outdir=Path(outdir).resolve()
    if outdir.exists():raise ValueError('Refuse to modify existing output directory')
    if outdir==planpath.parent:raise ValueError('Separate output directory required')
    p=json.loads(planpath.read_text(encoding='utf-8'));src=(planpath.parent/p['source_filename']).resolve()
    if src.parent!=planpath.parent or src.suffix.lower()!='.glb':raise ValueError('Source fixture must be local glb')
    if bpy.app.version<(4,3,0):raise RuntimeError('Blender version too old')
    # Fail closed BEFORE creating output directory.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(src))
    objects={ob.name:ob for ob in bpy.data.objects if ob.type=='MESH'}
    if len(objects)!=3:raise ValueError('Expected exactly three imported mesh objects')
    validate(p,src,objects.keys())
    if any(ob.data.shape_keys for ob in objects.values()):raise ValueError('Unexpected input shape keys')
    obj=objects[p['target_geometry']];obj_world=obj.matrix_world.copy()
    orig=np.array([tuple(obj_world @ v.co) for v in obj.data.vertices],dtype=np.float64)
    expected=apply(orig,p['strokes'])
    mx_inv=obj_world.inverted_safe()
    basis=obj.shape_key_add(name='Basis',from_mix=False)
    sculpt=obj.shape_key_add(name='D37_SCULPT_EDIT',from_mix=False)
    for i,co in enumerate(expected):sculpt.data[i].co=mx_inv@__import__('mathutils').Vector(co)
    sculpt.value=1
    # Keep all original protected mesh coordinates unchanged.
    protected={name:np.array([tuple(ob.matrix_world@v.co) for v in ob.data.vertices])
               for name,ob in objects.items() if name in p['protected_geometries']}
    outdir.mkdir(parents=True)
    project=outdir/'D37_NATIVE_EDITABLE.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(project),check_existing=False)
    if not project.is_file() or project.stat().st_size<1000:raise ValueError('Blender native file not saved')
    # Export only fresh BAKED geometries; do not rely on morph weight import support of third-party GLB viewers.
    export_collection=bpy.data.collections.new('D37_TEMP_EXPORT_ONLY')
    bpy.context.scene.collection.children.link(export_collection)
    export_objects=[]
    # Preserve exact names in GLB. The authoring .blend was already saved above;
    # rename only the transient in-memory originals to free their object names.
    for name,ob in objects.items():
        ob.name='D37_AUTHORING_'+name
    for name,ob in objects.items():
        mesh=ob.data.copy()
        # the duplicate may inherit morph keys; strip them before writing explicit vertex positions.
        if mesh.shape_keys:
            # write through freshly created mesh to guarantee no inherited morph data in baked result
            newmesh=bpy.data.meshes.new(name+'_BAKED_DATA')
            newmesh.from_pydata([tuple(v.co) for v in ob.data.vertices],[],[tuple(p.vertices) for p in ob.data.polygons])
            newmesh.update();mesh=newmesh
        du=bpy.data.objects.new(name,mesh);export_collection.objects.link(du)
        du.matrix_world=ob.matrix_world.copy()
        if name==p['target_geometry']:
            for i,world in enumerate(expected):du.data.vertices[i].co=mx_inv@__import__('mathutils').Vector(world)
        else:
            before=protected[name];after=np.array([tuple(du.matrix_world@v.co) for v in du.data.vertices])
            if not np.allclose(before,after,rtol=0,atol=1e-5):raise ValueError('Protected mesh altered in export: '+name)
        export_objects.append(du)
    bpy.ops.object.select_all(action='DESELECT')
    for o in export_objects:o.select_set(True)
    bpy.context.view_layer.objects.active=export_objects[0]
    glb=outdir/'D37_BLENDER_BAKED.glb'
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_morph=False)
    if not glb.exists():raise ValueError('Baked export missing')
    moved=np.linalg.norm(expected-orig,axis=1)
    report={'blender_version':bpy.app.version_string,'bpy_module':True,'source_sha256':sha(src.read_bytes()),
       'native_blend_filename':project.name,'native_blend_sha256':sha(project.read_bytes()),
       'baked_glb_filename':glb.name,'baked_glb_sha256':sha(glb.read_bytes()),
       'sculpt_shape_key':'D37_SCULPT_EDIT','moved_vertices':int((moved>1e-4).sum()),
       'max_world_displacement_m':float(moved.max()),'protected_names':p['protected_geometries'],
       'art':'NOT_SUBMITTED','formal_adoptions':0,'minecraft':'HOLD'}
    (outdir/'D37_BLENDER_RUN.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('usage: python d37_blender_execute.py PLAN.json FRESH_OUTPUT_DIR')
    main(*sys.argv[1:])
