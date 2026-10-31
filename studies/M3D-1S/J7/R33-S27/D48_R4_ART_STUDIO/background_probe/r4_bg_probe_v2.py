"""R4-E1B: limited native Blender I/O verification. NOT artwork or aesthetic approval."""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

import bpy
from mathutils import Vector

TARGET = 'HALO9_ONLY_TEST_MESH_NOT_ART'
GROUND = 'HALO9_ONLY_TEST_GROUND'
CAMERA = 'HALO9_ONLY_TEST_CAMERA'


def digest_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mesh_digest(obj):
    assert obj is not None and obj.type == 'MESH'
    payload = b''.join(struct.pack('<fff', *tuple(v.co)) for v in obj.data.vertices)
    return hashlib.sha256(payload).hexdigest()


def matrix_digest(obj):
    return hashlib.sha256(b''.join(
        struct.pack('<f', float(value)) for row in obj.matrix_world for value in row
    )).hexdigest()


def create_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.context.preferences.filepaths.save_version = 0

    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1.2))
    target = bpy.context.object
    target.name = TARGET

    bpy.ops.mesh.primitive_plane_add(size=200)
    bpy.context.object.name = GROUND

    bpy.ops.object.camera_add(location=(7.5, -8.0, 6.0))
    cam = bpy.context.object
    cam.name = CAMERA
    cam.rotation_euler = (Vector((0, 0, 1.1)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 45
    bpy.context.scene.camera = cam

    bpy.ops.object.light_add(type='AREA', location=(0, -3, 8))
    light = bpy.context.object
    light.name = 'HALO9_ONLY_TEST_LIGHT'
    light.data.energy = 1200
    light.data.shape = 'DISK'
    light.data.size = 8

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
    bpy.context.view_layer.update()
    return target


def snapshot_scene(blend_path, png_path):
    scene = bpy.context.scene
    scene.render.filepath = str(png_path)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False)
    bpy.ops.render.render(write_still=True)


def reopen_and_measure(blend_path):
    bpy.ops.wm.open_mainfile(filepath=str(blend_path), load_ui=False)
    bpy.context.view_layer.update()
    return {
        'mesh': mesh_digest(bpy.data.objects.get(TARGET)),
        'ground': mesh_digest(bpy.data.objects.get(GROUND)),
        'camera': matrix_digest(bpy.data.objects.get(CAMERA)),
        'filepath': bpy.context.scene.render.filepath,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--outdir', type=Path, required=True)
    if '--' not in sys.argv:
        raise ValueError('Run Blender with: --python r4_bg_probe_v2.py -- --outdir NEW_DIRECTORY')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    assert bpy.app.background, 'Must run Blender --background; refuse UI mode'
    out = args.outdir.resolve()
    # Only new research path; never reuse existing folders.
    out.mkdir(parents=True, exist_ok=False)
    before_blend = out / 'before.blend'
    after_blend = out / 'after.blend'
    before_png = out / 'before.png'
    after_png = out / 'after.png'

    target = create_scene()
    snapshot_scene(before_blend, before_png)
    baseline = {
        'mesh': mesh_digest(target),
        'ground': mesh_digest(bpy.data.objects[GROUND]),
        'camera': matrix_digest(bpy.data.objects[CAMERA]),
    }

    # This is a tiny existing-mesh I/O probe, not an architectural candidate.
    for v in target.data.vertices:
        if v.co.z > 0.0:
            v.co.x += 0.7
            v.co.y += 0.25
            v.co.z += 0.15
    target.data.update()
    assert mesh_digest(target) != baseline['mesh'], 'No existing-mesh edit occurred'
    snapshot_scene(after_blend, after_png)
    after_read = reopen_and_measure(after_blend)
    before_read = reopen_and_measure(before_blend)

    assert before_read['mesh'] == baseline['mesh'], 'Original native mesh not preserved'
    assert after_read['mesh'] != before_read['mesh'], 'Native modified scene not preserved'
    assert before_read['ground'] == after_read['ground'] == baseline['ground'], 'Untargeted ground changed'
    assert before_read['camera'] == after_read['camera'] == baseline['camera'], 'Camera moved between scenes'
    assert Path(before_read['filepath']).resolve() == before_png, 'Before scene render path inconsistent'
    assert Path(after_read['filepath']).resolve() == after_png, 'After scene render path inconsistent'
    required = (before_blend, after_blend, before_png, after_png)
    assert all(p.is_file() and p.stat().st_size > 0 for p in required), 'Missing or empty source/render'
    assert digest_file(before_png) != digest_file(after_png), 'Before and after PNG bytes identical'
    report = {
        'status': 'E1B_NATIVE_IO_PROBE_PASS_NOT_ART',
        'headless': True,
        'blender_version': bpy.app.version_string,
        'scope': 'NEW_DISPOSABLE_SCENE_ONLY',
        'cpu_threads': 2,
        'render_engine': 'CYCLES_CPU',
        'render_size_px': [320, 180],
        'same_existing_mesh_modified': True,
        'native_before_and_after_reopened': True,
        'untargeted_mesh_unchanged': True,
        'same_camera_verified': True,
        'images_distinct_by_sha256': True,
        'original_mesh_sha256': before_read['mesh'],
        'modified_mesh_sha256': after_read['mesh'],
        'files': {p.name: {'bytes': p.stat().st_size, 'sha256': digest_file(p)} for p in required},
        'art_review_performed': False,
        'art_pass': False,
        'city_master_complete': False,
        'minecraft_write': False,
    }
    (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('E1B_NATIVE_IO_PROBE_PASS_NOT_ART')


if __name__ == '__main__':
    main()
