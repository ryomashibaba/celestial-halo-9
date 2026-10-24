"""HALO-9 J7-R4: REAL Blender-native noncanonical mesh-edit smoke test.
Never edits protected originals; imports R3 GLB, renders before, deforms *existing* NAVE meshes
using bmesh, renders after, exports GLB and BLEND with auditable measurements.
This proves Blender execution & editable mesh operation only, NOT beautiful architecture.
"""
import bpy, bmesh, json, math, sys
from pathlib import Path
from mathutils import Vector, Matrix
def ensure(condition, msg):
    if not condition: raise RuntimeError(msg)
def mesh_objects():
    return [o for o in bpy.context.scene.objects if o.type == 'MESH']
def get_mesh(prefix):
    matches=[o for o in mesh_objects() if o.name.startswith(prefix)]
    ensure(len(matches)==1, 'Expected unique imported mesh '+prefix+' got '+str([m.name for m in matches]))
    return matches[0]
def bounds(o):
    pts=[o.matrix_world@v.co for v in o.data.vertices]
    return [[round(min(p[i] for p in pts),3) for i in range(3)],[round(max(p[i] for p in pts),3) for i in range(3)]]
def normalize_imported_glb_basis():
    # R3's Trimesh-exported GLB has Z-up numeric vertices embedded as glTF Y-up.
    # Blender sees (x, -z, y); rotate imported root transforms -90 degrees around X
    # to restore the numerical study coordinate (x, y, z). This is research-only.
    rot=Matrix.Rotation(-math.pi/2.0,4,'X')
    roots=[o for o in bpy.context.scene.objects if o.parent is None]
    ensure(bool(roots),'no glTF root objects to transform')
    for obj in roots: obj.matrix_world=rot@obj.matrix_world
    bpy.context.view_layer.update()
    return len(roots)
def setup_camera(name, loc, target, ortho):
    cd=bpy.data.cameras.new(name); cam=bpy.data.objects.new(name,cd)
    bpy.context.scene.collection.objects.link(cam)
    cam.location=tuple(loc);target=Vector(target)
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    cd.type='ORTHO';cd.ortho_scale=ortho;cd.clip_end=60000
    return cam
def scene_prep():
    scene=bpy.context.scene
    scene.render.engine='BLENDER_WORKBENCH'
    scene.render.resolution_x=960;scene.render.resolution_y=700
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.display.shading.light='STUDIO'
    scene.display.shading.color_type='MATERIAL'
    scene.display.shading.show_shadows=True
    scene.view_settings.view_transform='Standard'
    scene.render.film_transparent=False
    return scene
def render(scene, cam, name, out):
    scene.camera=cam
    scene.render.filepath=str(out/name)
    bpy.ops.render.render(write_still=True)
    p=out/name
    ensure(p.exists() and p.stat().st_size>3000,'render missing or too small '+name)
    return {'name':name,'bytes':p.stat().st_size}
def deform_in_blender(o, selection_axis='Y', multiplier=1.22, shift=30):
    # Use bmesh and GLOBAL axis geometry when working with imported GLB transforms.
    # Extend width by 22% around own centroid and shift upper vertices 30 m.
    ensure(o.type=='MESH','non-mesh selected')
    bb=bounds(o)
    axis=1 if selection_axis=='Y' else 0
    cen=(bb[0][axis]+bb[1][axis])*0.5
    zcen=(bb[0][2]+bb[1][2])*0.5
    inv=o.matrix_world.inverted()
    bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table()
    total=0; moved=0; max_delta=0
    for v in bm.verts:
        w=o.matrix_world@v.co
        old=w.copy()
        w[axis]=cen+(w[axis]-cen)*multiplier
        if w[2]>zcen:w[2]+=shift
        delta=(w-old).length
        if delta>0.0001:
            v.co=inv@w;moved+=1;max_delta=max(max_delta,delta)
        total+=1
    bm.to_mesh(o.data);bm.free();o.data.update()
    ensure(moved>=8,'too few edited vertices')
    return {'object':o.name,'vertices_total':total,'vertices_moved':moved,
            'max_displacement_m':round(max_delta,3),'bounds_before_m':bb,'bounds_after_m':bounds(o)}
def main():
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    ensure(len(args)==2,'Expected -- path/to/R3.glb output_dir')
    source=Path(args[0]).resolve();out=Path(args[1]).resolve()
    ensure(source.is_file() and source.suffix.lower()=='.glb','original R3 GLB required')
    ensure(source.parent!=out,'output must be separate from input')
    ensure(not out.exists() or not list(out.iterdir()),'output directory must be new/empty')
    out.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    imported=mesh_objects()
    corrected_roots=normalize_imported_glb_basis()
    ensure(len(imported)>=150,'R3 expected at least 150 mesh objects')
    nave=get_mesh('NAVE_MAIN_PROCESSIONAL_FLOOR')
    roof=get_mesh('NAVE_VAULT_SUSPENDED_NORTH_FOLD')
    before_nave=bounds(nave);before_roof=bounds(roof)
    ensure(abs(before_nave[0][2]-1215.0)<2 and abs(before_roof[0][2]-1760.0)<2,
           'Imported coordinate basis not Z-up after correction: '+str(before_nave))

    scene=scene_prep()
    # Two fixed 10km views, and one local examination view shared by before/after.
    cams=[
      setup_camera('CITY_FRONT',(0,-10500,4450),(0,0,2050),10500),
      setup_camera('CITY_SIDE',(10500,0,4450),(0,0,2050),10500),
      setup_camera('NAVE_LOCAL',(2800,-3900,3000),(0,-750,1730),3800)]
    images=[]
    for cam in cams:images.append(render(scene,cam,'BEFORE_'+cam.name+'.png',out))
    measurements=[deform_in_blender(nave,multiplier=1.38,shift=42),
                  deform_in_blender(roof,multiplier=1.16,shift=86)]
    # Create a conventional editable BLEND where the native mesh changes are retained.
    blend=out/'J7R4_REAL_BLENDER_EDIT.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
    ensure(blend.exists() and blend.stat().st_size>10000,'BLEND save failed')
    for cam in cams:images.append(render(scene,cam,'AFTER_'+cam.name+'.png',out))
    glb=out/'J7R4_REAL_BLENDER_EDIT.glb'
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',export_apply=False)
    ensure(glb.exists() and glb.stat().st_size>10000,'edited GLB export failed')
    metadata={'schema':'halo9.j7r4.blender_execution_evidence.v1',
      'blender_version':bpy.app.version_string, 'engine':'BLENDER_WORKBENCH',
      'source_glb_repo':'studies/M3D-1S/J7/R3/J7R3_FRACTURED_INHABITED_CIVIC_SKY_NONCANONICAL.glb',
      'source_mesh_objects':len(imported),'normalized_root_objects':corrected_roots, 'coordinate_basis_normalization':'Trimesh R3 authored XYZ Z-up restored by imported-root -90deg X rotation', 'blender_mesh_edit_method':'bmesh direct change of existing imported vertex geometry',
      'before_nave_bounds_m':before_nave,'before_roof_bounds_m':before_roof,
      'edited_objects':measurements,'screenshots':images,
      'glb_bytes':glb.stat().st_size,'blend_bytes':blend.stat().st_size,
      'art_judgement':'NOT_ACCEPTED; experimental technical geometry edit only',
      'canonical_coordinates':'UNVERIFIED','city_master_complete':False,
      'human_walkability':'NOT_TESTED','blender_GUI_manual_session':'NOT_PERFORMED',
      'minecraft_construction':'HOLD','source_glb_modified':False}
    # Also test Blender re-import of its own exported edited GLB
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    metadata['edited_glb_reimport_mesh_count']=len(mesh_objects())
    ensure(metadata['edited_glb_reimport_mesh_count']>=len(imported),'reimport lost mesh objects')
    exported_nave=get_mesh('NAVE_MAIN_PROCESSIONAL_FLOOR')
    metadata['edited_glb_reimport_nave_bounds_m']=bounds(exported_nave)
    ensure(abs(metadata['edited_glb_reimport_nave_bounds_m'][0][2]-measurements[0]['bounds_after_m'][0][2])<3,
           'Reimport changed Z coordinate unexpectedly')
    ensure(any(abs(a-b)>3 for u,v in zip(measurements[0]['bounds_before_m'], measurements[0]['bounds_after_m']) for a,b in zip(u,v)),
           'Mesh bounds before and after indistinguishable')

    (out/'J7R4_BLENDER_ACTUAL_EXECUTION.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    print('J7R4_SUCCESS',json.dumps({'blender':bpy.app.version_string,
        'source_meshes':len(imported),'reimport':len(mesh_objects()),
        'edited_vertices':sum(x['vertices_moved'] for x in measurements),
        'renders':len(images),'glb_bytes':glb.stat().st_size,'blend_bytes':blend.stat().st_size}))
if __name__=='__main__':main()
