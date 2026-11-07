"""One authored Gate B mass study on an isolated INT21 copy.

This is not an automatic city generator. The few explicit section stations and
the angular H1 plan are the authored macro forms; Blender is used for the
actual editable meshes and fixed-condition image review.
"""
import bpy, math, os, json
from mathutils import Vector

ROOT = r"C:\Users\ryoma\Projects\CELESTIAL_HALO9\repo\studies\M3D-1S\J7\R33-S28\GATE_B_INTEGRATED_CIVIC"
BASE = os.path.join(ROOT, "BASELINE_INT21.blend")
OUT = os.path.join(ROOT, "AUTHORING_A0.blend")
IMG = os.path.join(ROOT, "A0")
os.makedirs(IMG, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=BASE)
scene = bpy.context.scene
protected = {"W0_NORTH_FRACTURED_RANGE", "W0_WEST_BASALT_ESCARPMENT",
             "W0_GROUND_BASIN", "W0_EASTERN_ARTIFICIAL_SEA"}
for obj in list(bpy.data.objects):
    if obj.name in protected or obj.type == "LIGHT" or (obj.type == "CAMERA" and obj.name.startswith("E11_")):
        continue
    bpy.data.objects.remove(obj, do_unlink=True)

def material(name, color, metallic, roughness):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return m

mat_west = material("M247C | basalt ceramic", (0.095, 0.16, 0.19), 0.28, 0.31)
mat_east = material("M247C | pearl mineral", (0.63, 0.76, 0.78), 0.18, 0.34)
mat_spine = material("M247C | cut silver", (0.78, 0.85, 0.84), 0.42, 0.28)
mat_h1 = material("H1 | inhabited limestone", (0.43, 0.57, 0.56), 0.12, 0.4)

# A hand-authored, deliberately asymmetric swept section: heavy and inhabited,
# with a folded undercut instead of a thin plate or roof.
PROFILE = [(-0.78, -0.18), (-0.55, -0.67), (0.18, -0.79),
           (0.83, -0.32), (1.0, 0.08), (0.49, 0.31),
           (0.10, 0.88), (-0.64, 0.54)]

def sweep(name, stations, mat, phase=0.0):
    """Stations: x,y,z, half-width, half-height, section rotation."""
    verts, faces = [], []
    for i, (x, y, z, width, height, twist) in enumerate(stations):
        a = math.radians(twist + phase)
        ca, sa = math.cos(a), math.sin(a)
        if i == 0:
            dx, dy = stations[1][0]-x, stations[1][1]-y
        elif i == len(stations)-1:
            dx, dy = x-stations[i-1][0], y-stations[i-1][1]
        else:
            dx, dy = stations[i+1][0]-stations[i-1][0], stations[i+1][1]-stations[i-1][1]
        ln = max(1e-6, math.hypot(dx, dy))
        nx, ny = -dy/ln, dx/ln
        for u, v in PROFILE:
            # rotate the section in its own normal/vertical plane, varying the
            # torsion across each authored control station.
            ur, vr = u*ca-v*sa, u*sa+v*ca
            verts.append((x + nx*ur*width, y + ny*ur*width, z + vr*height))
    count = len(PROFILE)
    faces.append(tuple(reversed(range(count))))
    for j in range(len(stations)-1):
        for k in range(count):
            a = j*count+k
            b = j*count+(k+1)%count
            faces.append((a, b, b+count, a+count))
    faces.append(tuple((len(stations)-1)*count+k for k in range(count)))
    mesh = bpy.data.meshes.new(name+" | sculpted loft")
    mesh.from_pydata(verts, [], faces)
    mesh.materials.append(mat)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    for p in mesh.polygons:
        p.use_smooth = False
    return obj

# Alpha west: one mass rises directly out of the protected W0 western range,
# then folds inward over the civic cleft. Its lower terminus stays out of the
# NAVE camera's central sight line.
west = sweep("M247C_ALPHA_WEST_ANCHORED_MASS", [
    (-1510, 950, 245, 500, 270, -14),
    (-1260, 650, 390, 520, 330, 8),
    (-930, 365, 540, 470, 390, 22),
    (-650, 155, 485, 390, 365, -18),
    (-430, 80, 255, 285, 245, -34),
], mat_west)

# Alpha east: lifted, offset counterpart. The changing section shifts the
# inhabited underside away from a conventional overhead canopy.
east = sweep("M247C_ALPHA_EAST_SEVERED_MASS", [
    (1740, 960, 280, 520, 280, 22),
    (1490, 650, 445, 565, 360, -5),
    (1370, 365, 690, 500, 405, 18),
    (1510, 80, 785, 410, 345, 37),
    (1730, -120, 575, 300, 275, 54),
], mat_east, 4.0)

# Beta: a steep, oblique inhabited ridge ties the two alpha masses at the back
# of the NAVE. Its high, rising route leaves the public chamber open to sky.
spine = sweep("M247C_BETA_OBLIQUE_INHABITED_RIDGE", [
    (-1320, 1090, 660, 285, 205, -18),
    (-900, 1130, 815, 330, 240, -7),
    (-390, 1080, 980, 355, 245, 12),
    (240, 950, 1135, 390, 245, 24),
    (880, 760, 1130, 365, 235, 37),
    (1390, 570, 915, 300, 205, 49),
], mat_spine, -8.0)

# H1 is a non-circular inhabited court, expressed as a thick three-tier public
# district. Each tier is angular and offset; the center remains a true civic
# void open to the fixed human camera and the NAVE approach.
center = Vector((825.0, 760.0))
outline = [(-365,-105),(-300,-310),(-110,-390),(190,-335),(390,-145),
           (350,135),(225,340),(-40,410),(-295,275),(-420,65)]
inner = [(-205,-48),(-165,-182),(-55,-230),(112,-202),(228,-86),
         (205,82),(126,197),(-22,238),(-171,160),(-244,36)]
levels = [
    (0, 1.00, 0.96, (0,0)),
    (96, 1.04, 0.99, (-18,4)),
    (218, 0.91, 0.86, (28,16)),
    (338, 0.76, 0.72, (60,48)),
]
N = len(outline)
verts, faces = [], []
for z, so, si, shift in levels:
    for loop, scale in ((outline, so), (inner, si)):
        for x,y in loop:
            verts.append((center.x+x*scale+shift[0], center.y+y*scale+shift[1], z))
def vid(level, loop, i): return level*(2*N)+loop*N+(i%N)
# Bottom and top bands plus faceted inner/outer walls.
for i in range(N):
    faces.append((vid(0,0,i),vid(0,0,i+1),vid(0,1,i+1),vid(0,1,i)))
    for l in range(len(levels)-1):
        faces.append((vid(l,0,i),vid(l,0,i+1),vid(l+1,0,i+1),vid(l+1,0,i)))
        faces.append((vid(l,1,i+1),vid(l,1,i),vid(l+1,1,i),vid(l+1,1,i+1)))
for i in range(N):
    faces.append((vid(len(levels)-1,0,i),vid(len(levels)-1,0,i+1),
                  vid(len(levels)-1,1,i+1),vid(len(levels)-1,1,i)))
hmesh = bpy.data.meshes.new("H1 | tiered civic court mesh")
hmesh.from_pydata(verts, [], faces)
hmesh.materials.append(mat_h1)
hmesh.update()
h1 = bpy.data.objects.new("H1_LIVING_CITY_CIVIC_COURT", hmesh)
scene.collection.objects.link(h1)

# Two generous walkable shoulders visibly stitch H1 into the east shell and
# carry the public approach toward the NAVE. These are part of the macro plan.
walk = sweep("H1_NAVE_PUBLIC_SHOULDER", [
    (600, 430, 82, 165, 52, -14),
    (400, 150, 74, 175, 50, -6),
    (120, -80, 42, 205, 44, 7),
    (-120, -190, 18, 230, 42, 21),
], mat_h1, -3.0)
walk2 = sweep("H1_UPPER_COURT_CONNECTION", [
    (485, 780, 250, 120, 54, 18),
    (540, 950, 295, 145, 62, 28),
    (685, 1100, 362, 165, 66, 36),
    (880, 1160, 428, 175, 72, 43),
    (1045, 1080, 446, 150, 64, 51),
], mat_h1, 8.0)

# Preserve the original fixed camera, lighting, render, exposure, W0 meshes and
# camera matrices. The baseline file remains untouched.
scene.camera = bpy.data.objects.get("E11_URBAN_AERIAL")
bpy.ops.wm.save_as_mainfile(filepath=OUT)
render = {"engine": scene.render.engine, "resolution": [scene.render.resolution_x, scene.render.resolution_y],
          "samples": scene.cycles.samples if scene.render.engine == "CYCLES" else None,
          "exposure": scene.view_settings.exposure, "camera_matrices_fixed": True,
          "lights_unchanged": True}
for name in ("E11_NAVE_HUMAN", "E11_H1_HUMAN", "E11_URBAN_AERIAL"):
    scene.camera = bpy.data.objects[name]
    scene.render.filepath = os.path.join(IMG, name + ".png")
    bpy.ops.render.render(write_still=True)
with open(os.path.join(IMG, "render.json"), "w", encoding="utf-8") as f:
    json.dump(render, f, ensure_ascii=False, indent=2)
print(json.dumps({"saved": OUT, "objects_added": [o.name for o in (west,east,spine,h1,walk,walk2)],
                  "render": render}, ensure_ascii=False))
