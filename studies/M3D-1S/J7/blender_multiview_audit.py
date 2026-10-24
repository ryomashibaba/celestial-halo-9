# J7 review-only runner. Blender 5.x, bpy included. NEVER edits source GLB.
# Run: blender --background --factory-startup --python blender_multiview_audit.py -- input.glb output_dir
import bpy, json, math, sys, os
from mathutils import Vector
from pathlib import Path

def main():
    if "--" not in sys.argv:
        raise ValueError("Expected -- input.glb output_directory")
    args = sys.argv[sys.argv.index("--") + 1:]
    if len(args) != 2:
        raise ValueError("Provide exactly input.glb and output_directory")
    source = Path(args[0]).resolve()
    output = Path(args[1]).resolve()
    if not source.is_file() or source.suffix.lower() != ".glb":
        raise ValueError("Missing real GLB input: " + str(source))
    if output == source.parent:
        raise ValueError("Do not write renders into the source model folder")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("Refuses to overwrite a non-empty output directory")
    output.mkdir(parents=True, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    objects = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not objects:
        raise ValueError("GLB imported without mesh objects")
    samples = [o.matrix_world @ Vector(v) for o in objects for v in o.bound_box]
    bounds_min = [float(min(p[k] for p in samples)) for k in range(3)]
    bounds_max = [float(max(p[k] for p in samples)) for k in range(3)]
    bounds_span = [b-a for a,b in zip(bounds_min, bounds_max)]

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    world = bpy.data.worlds.new("J7_Noncanonical_Audit_World")
    world.use_nodes = True
    world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.055, 0.073, 0.095, 1.0)
    world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.75
    scene.world = world
    scene.render.use_stamp = True
    scene.render.use_stamp_note = True
    scene.render.use_stamp_filename = False
    scene.render.use_stamp_scene = False
    scene.render.use_stamp_camera = False

    light_data = bpy.data.lights.new("J7_Audit_Sun", type="SUN")
    light = bpy.data.objects.new("J7_Audit_Sun", light_data)
    scene.collection.objects.link(light)
    light.rotation_euler = (0.55, -0.45, -0.50)
    light_data.energy = 2.1

    cam_data = bpy.data.cameras.new("J7_Fixed_Orthographic_Camera")
    camera = bpy.data.objects.new("J7_Fixed_Orthographic_Camera", cam_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    cam_data.type = "ORTHO"
    cam_data.clip_end = 80000

    fixed_target = Vector((0, 0, 1700))
    local_target = Vector([(a+b)/2 for a,b in zip(bounds_min,bounds_max)])
    views = [
        ("01_FRONT", (0,-9800,4100), fixed_target, 10500, "FIXED_10KM"),
        ("02_OBLIQUE", (6900,-7600,5500), fixed_target, 10500, "FIXED_10KM"),
        ("03_SIDE", (10500,0,4700), fixed_target, 10500, "FIXED_10KM"),
        ("04_REAR", (0,9800,4200), fixed_target, 10500, "FIXED_10KM"),
        ("05_AERIAL", (5500,-6000,13500), fixed_target, 10500, "FIXED_10KM"),
        ("06_GROUND", (0,-10500,350), Vector((0,0,1900)), 10500, "FIXED_10KM"),
        ("07_REVERSE_DIAGONAL", (-6200,7800,5500), fixed_target, 10500, "FIXED_10KM"),
        ("08_LOCAL_DETAIL", (3400,-4100,2800), local_target, max(bounds_span)*1.5, "LOCAL_NON_COMPARABLE")
    ]
    info = {"schema":"halo9.j7.real_blender_render_readback.v1",
            "source_glb":str(source), "render_output":str(output),
            "mesh_objects":len(objects), "bounds_min_m":bounds_min,
            "bounds_max_m":bounds_max, "bounds_span_m":bounds_span,
            "status":"BLENDER_IMPORT_AND_RENDER_TECHNICAL_ONLY_ART_NOT_JUDGED",
            "views":[]}
    for name, delta, target, ortho, classification in views:
        camera.location = target + Vector(delta)
        camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
        cam_data.ortho_scale = ortho
        scene.render.stamp_note_text = name + " | " + classification + " | NONCANONICAL | ART UNASSESSED"
        scene.render.filepath = str(output / (name + ".png"))
        bpy.ops.render.render(write_still=True)
        info["views"].append({"name":name, "classification":classification,
                               "orthographic_scale_m":ortho, "path":scene.render.filepath})
    (output / "J7_BLENDER_RENDER_READBACK.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
if __name__ == "__main__":
    main()
