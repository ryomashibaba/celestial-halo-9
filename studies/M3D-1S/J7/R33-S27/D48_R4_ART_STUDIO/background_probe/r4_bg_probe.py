"""R4 background Blender I/O probe, NOT artwork. Creates only new lab files."""
import bpy
import hashlib
import json
import struct
import sys
from pathlib import Path
from mathutils import Vector

def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def mesh_digest(obj):
    return hashlib.sha256(b''.join(
        struct.pack('<ddd', *map(float, v.co)) for v in obj.data.vertices
    )).hexdigest()

def main():
    if '--' not in sys.argv:
        raise ValueError('Use -- --outdir <new-directory>')
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--outdir', required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    out = Path(args.outdir).resolve()
    out.mkdir(parents=True, exist_ok=False)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.context.preferences.filepaths.save_version = 0

    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1.2))
    subject = bpy.context.object
    subject.name = 'R4_E0_ONLY_TEST_MESH_NOT_ART'
    original_geometry = mesh_digest(subject)
    bpy.ops.mesh.primitive_plane_add(size=200)
    bpy.context.object.name = 'R4_E0_ONLY_TEST_GROUND'
    bpy.ops.object.camera_add(location=(7.5, -8, 6))
    camera = bpy.context.object
    camera.rotation_euler = (Vector((0, 0, 1.1)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = camera
    bpy.ops.object.light_add(type='AREA', location=(0, -3, 8))
    bpy.context.object.data.energy = 1200
    bpy.context.object.data.shape = 'DISK'
    bpy.context.object.data.size = 8

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 4
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 2
    scene.render.resolution_x = 320
    scene.render.resolution_y = 180
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    before, after = out / 'before.blend', out / 'after.blend'
    before_png, after_png = out / 'before.png', out / 'after.png'

    bpy.ops.wm.save_as_mainfile(filepath=str(before), check_existing=False)
    scene.render.filepath = str(before_png)
    bpy.ops.render.render(write_still=True)
    for vertex in subject.data.vertices:
        if vertex.co.z > 0:
            vertex.co.x += 0.7
            vertex.co.y += 0.25
            vertex.co.z += 0.15
    subject.data.update()
    changed_geometry = mesh_digest(subject)
    assert original_geometry != changed_geometry, 'No native geometry change'
    bpy.ops.wm.save_as_mainfile(filepath=str(after), check_existing=False)
    scene.render.filepath = str(after_png)
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.open_mainfile(filepath=str(after), load_ui=False)
    obj = bpy.data.objects.get('R4_E0_ONLY_TEST_MESH_NOT_ART')
    assert obj is not None and mesh_digest(obj) == changed_geometry, 'Reopened geometry mismatch'
    files = (before, after, before_png, after_png)
    assert all(p.exists() and p.stat().st_size > 0 for p in files), 'Missing assets'
    data = dict(
        status='LOCAL_BACKGROUND_TEST_PASS_NOT_ART_PASS',
        headless=bool(bpy.app.background),
        blender_version=bpy.app.version_string,
        cpu_threads=2,
        same_existing_mesh_changed=True,
        reopened_native_blend_verified=True,
        before_mesh_sha256=original_geometry,
        after_mesh_sha256=changed_geometry,
        files={p.name: dict(sha256=digest(p), bytes=p.stat().st_size) for p in files},
        formal_art_accepted=False, city_master_complete=False, minecraft_write=False,
    )
    assert data['headless'], 'Blender is not running in background'
    (out / 'report.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    print('R4_BACKGROUND_PROBE_PASS_NOT_ART')

if __name__ == '__main__':
    main()
