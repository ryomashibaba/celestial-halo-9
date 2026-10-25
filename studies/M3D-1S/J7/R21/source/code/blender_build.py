"""C55-A  《七環天裂都》 SEVENFOLD HALO RIFT  --  Blender build script.

!!! STATUS: UNVERIFIED. This script was authored in a sandbox that has NO Blender / bpy, so it has never been executed.
!!! The BLEND file therefore does NOT exist yet. Running this script is the one step the author could not perform.

Usage (one command):
    blender -b -P blender_build.py -- --out ./blender_out                # build .blend + export .glb + render 11 views (Cycles)
    blender -b -P blender_build.py -- --out ./blender_out --no-render    # build .blend + .glb only
    blender -b -P blender_build.py -- --out ./blender_out --engine EEVEE --samples 32 --res 1280 720

The mesh data comes from c55a_city.py (pure numpy, identical to the data used for the GLB and the software-rasteriser previews).
Every procedural part becomes one editable mesh object, grouped in Blender collections named like the GLB scene nodes.
"""
import bpy, sys, os, math, argparse
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument('--out', default='./blender_out')
ap.add_argument('--no-render', action='store_true')
ap.add_argument('--engine', default='CYCLES')
ap.add_argument('--samples', type=int, default=64)
ap.add_argument('--res', type=int, nargs=2, default=[1920, 1080])
args = ap.parse_args(argv)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import c55a_city as C
import camera_specs

os.makedirs(args.out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
S = C.build_scene()


def setin(bsdf, names, value):
    for n in names:
        if n in bsdf.inputs:
            bsdf.inputs[n].default_value = value
            return True
    return False


def make_material(name, m):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    base = m.get('base', (0, 0, 0))
    setin(bsdf, ['Base Color'], (base[0], base[1], base[2], 1.0))
    emit = m.get('emit', (0, 0, 0))
    mx = max(emit)
    if mx > 0:
        setin(bsdf, ['Emission Color', 'Emission'], (emit[0] / mx, emit[1] / mx, emit[2] / mx, 1.0))
        setin(bsdf, ['Emission Strength'], float(mx))
    spec = m.get('spec', 0.0)
    setin(bsdf, ['Metallic'], 0.85 if spec >= 0.5 else 0.0)
    setin(bsdf, ['Roughness'], 0.28 if spec >= 0.5 else (0.55 if spec > 0 else 0.85))
    if m.get('alpha', 1.0) < 1.0:
        setin(bsdf, ['Alpha'], float(m['alpha']))
        try:
            mat.blend_method = 'BLEND'
        except Exception:
            pass
    return mat


mats = {k: make_material(k, v) for k, v in C.MATERIALS.items()}
cols = {}
for p in S.parts:
    if p['coll'] not in cols:
        c = bpy.data.collections.new(p['coll'])
        scene.collection.children.link(c)
        cols[p['coll']] = c
    V = np.ascontiguousarray(p['V'], dtype=np.float32)
    F = np.ascontiguousarray(p['F'], dtype=np.int32)
    me = bpy.data.meshes.new(p['name'])
    me.vertices.add(len(V))
    me.vertices.foreach_set('co', V.ravel())
    me.loops.add(F.size)
    me.loops.foreach_set('vertex_index', F.ravel())
    me.polygons.add(len(F))
    me.polygons.foreach_set('loop_start', np.arange(0, F.size, 3, dtype=np.int32))
    me.polygons.foreach_set('loop_total', np.full(len(F), 3, dtype=np.int32))
    me.update()
    me.validate()
    me.materials.append(mats[p['mat']])
    ob = bpy.data.objects.new(p['name'], me)
    ob['c55a_collection'] = p['coll']
    ob['c55a_interior'] = bool(p['interior'])
    ob['c55a_context_placeholder'] = bool(p['context'])
    cols[p['coll']].objects.link(ob)

# --- world + sun (matches the software preview: low warm sun from WSW)
SUN = Vector((-0.80, -0.34, 0.40)).normalized()
sun = bpy.data.objects.new('SUN', bpy.data.lights.new('SUN', 'SUN'))
sun.data.energy = 4.0
sun.data.color = (1.0, 0.80, 0.58)
sun.rotation_euler = (-SUN).to_track_quat('-Z', 'Y').to_euler()
scene.collection.objects.link(sun)
world = bpy.data.worlds.new('C55A_dusk')
world.use_nodes = True
nt = world.node_tree
bg = nt.nodes.get('Background')
try:
    sky = nt.nodes.new('ShaderNodeTexSky')
    sky.sky_type = 'NISHITA'
    sky.sun_elevation = math.radians(23.0)
    sky.sun_disc = False
    nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
except Exception:
    bg.inputs['Color'].default_value = (0.35, 0.22, 0.30, 1.0)
bg.inputs['Strength'].default_value = 1.0
scene.world = world

# --- cameras
cams = {}
for spec in camera_specs.get_specs(S):
    cd = bpy.data.cameras.new(spec['name'])
    cd.sensor_fit = 'HORIZONTAL'
    cd.sensor_width = 36.0
    cd.lens = 18.0 / math.tan(math.radians(spec['hfov']) / 2)
    cd.clip_start, cd.clip_end = 0.3, 60000.0
    co = bpy.data.objects.new('CAM_' + spec['name'], cd)
    co.location = spec['pos']
    co.rotation_euler = (Vector(spec['target']) - Vector(spec['pos'])).to_track_quat('-Z', 'Y').to_euler()
    scene.collection.objects.link(co)
    cams[spec['name']] = (co, spec)

# --- render settings
scene.render.resolution_x, scene.render.resolution_y = args.res
scene.render.image_settings.file_format = 'PNG'
try:
    scene.view_settings.view_transform = 'AgX'
except Exception:
    try:
        scene.view_settings.view_transform = 'Filmic'
    except Exception:
        pass
if args.engine.upper() == 'CYCLES':
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True
else:
    for eng in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        try:
            scene.render.engine = eng
            break
        except TypeError:
            continue

blend_path = os.path.join(args.out, 'C55A_SevenfoldHaloRift.blend')
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
try:
    bpy.ops.export_scene.gltf(filepath=os.path.join(args.out, 'C55A_SevenfoldHaloRift_blender_export.glb'), export_format='GLB')
except Exception as e:
    print('GLB export from Blender failed:', e)

if not args.no_render:
    for name, (co, spec) in cams.items():
        scene.camera = co
        for cname, c in cols.items():
            if cname == 'GREAT_HALL_INTERIOR':
                c.hide_render = not spec['interior']   # hall only visible to the interior camera
            else:
                c.hide_render = bool(spec['interior'])  # exterior hidden for the interior camera
        scene.render.filepath = os.path.join(args.out, 'blender_render_' + name + '.png')
        bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print('C55A build finished ->', blend_path)
