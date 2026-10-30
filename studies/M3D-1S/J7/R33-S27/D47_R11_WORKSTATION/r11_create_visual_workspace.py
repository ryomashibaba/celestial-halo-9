"""R11: a real native Blender ART-DIRECTION workbench, not a city design.

Creates an editable high-resolution neutral mesh purely for UI/shape-key technique
tests; no new M247-C proposal or source-model edits. Packs the actual R10 source
comparison atlas to keep negative art precedents available in the .blend.
Controls exist as actual Blender cameras and named workspaces, not just exports.
"""
import bpy, math, sys, hashlib, json, zipfile
from pathlib import Path
from mathutils import Vector, Euler

args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
assert len(args)==2,"Usage blender -b --python script -- OUTPUT_DIRECTORY R10_ZIP_PATH"
dst=Path(args[0]).resolve(); dst.mkdir(parents=True,exist_ok=True)
original_archive=Path(args[1]).resolve()
assert original_archive.is_file()
with zipfile.ZipFile(original_archive) as z:
    atlas=z.read("R10_REAL_4_CANDIDATES_UNBIASED_VIEW_ATLAS.jpg")
atlas_sha=hashlib.sha256(atlas).hexdigest()
atlas_path=dst/"R11_R10_READONLY_ART_HISTORY.jpg";atlas_path.write_bytes(atlas)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
def coll(name):
    c=bpy.data.collections.get(name)
    if c is None:
        c=bpy.data.collections.new(name);scene.collection.children.link(c)
    return c
geom=coll("01 EDITABLE ONLY - NEUTRAL SCULPT TEST NOT ARCHITECTURE")
guide=coll("02 FIXED CAMERAS - REAL 3D COMPARISON")
guide.hide_select=True
note=coll("03 READ-ONLY HISTORICAL IMAGE (R10 rejects)")
note.hide_select=True
N,M=41,29
vertices=[]
for j in range(M):
    for i in range(N):
        x=-360+i*720/(N-1)
        z=45+j*580/(M-1)
        y=28*math.sin(x/160)*math.sin(z/160)-19*math.cos((x+z)/240)
        vertices.append((x,y,z))
faces=[]
for j in range(M-1):
    for i in range(N-1):
        a=j*N+i
        faces.append((a,a+1,a+N+1,a+N))
me=bpy.data.meshes.new("R11_NEUTRAL_EDITABLE_TESSELLATED_MESH")
me.from_pydata(vertices,[],faces);me.update()
o=bpy.data.objects.new("R11_EDIT_ONLY_UNAPPROVED_STUDY_SURFACE",me);geom.objects.link(o)
o["not_design_or_city"]="Only a neutral geometric editing fixture"
o["edit_allowed"]=True;o["art_approved"]=False
o.shape_key_add(name="Basis")
shape=o.shape_key_add(name="R11_ARTIST_REVERSIBLE_LAYER")
shape.value=1.0
o.active_shape_key_index=1
for v in shape.data: v.co.y+=0
ma=bpy.data.materials.new("Neutral graphite-grey : no art grading")
ma.diffuse_color=(.66,.69,.73,1)
me.materials.append(ma)
# Control fixture contains no imaginary buildings or lifestyle labels.
# First save an exact single-file baseline for comparing real GUI edits.
camera_def=[
 ("01_FRONTAL_EYE", (0,-950,250),(0,0,330),1000),
 ("02_SIDE_CROSS_SECTION",(1150,-90,350),(0,0,330),1100),
 ("03_OBLIQUE_MASS",(700,-1020,800),(0,0,335),1320),
 ("04_REAR_OTHER_SIDE",(50,1150,400),(0,0,330),1050),
 ("05_LOW_PUBLIC_VIEW",(0,-330,70),(0,0,450),700),
 ("06_ABOVE_OTHER_WORLD",(600,-500,1350),(0,0,360),1400),
]
for n,pos,target,scale in camera_def:
    d=bpy.data.cameras.new(n);ob=bpy.data.objects.new(n,d);guide.objects.link(ob)
    ob.location=pos
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat("-Z","Y").to_euler()
    d.type="ORTHO";d.ortho_scale=scale;d.clip_end=100000
    ob["fixed_review_camera"]=True
    ob.hide_select=True
scene.camera=bpy.data.objects["03_OBLIQUE_MASS"]

# Make a recoverable viewport edit environment in actual saved native file.
bpy.context.view_layer.objects.active=o
o.select_set(True)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=="VIEW_3D":
            sp=area.spaces.active
            sp.region_3d.view_location=Vector((0,0,335))
            sp.region_3d.view_distance=1200
            sp.region_3d.view_rotation=Euler(
              (math.radians(62),0,math.radians(22)),"XYZ").to_quaternion()
            sp.clip_end=20000
            sp.shading.type="SOLID"
            sp.shading.light="STUDIO"
            sp.shading.color_type="MATERIAL"
            sp.shading.show_cavity=True

scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_cavity=True
scene.render.resolution_x=960;scene.render.resolution_y=650
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
image=bpy.data.images.load(str(atlas_path),check_existing=False)
image.pack()
# Embedded toolbar can be run on Windows Blender 5.x via Text Editor / Run Script.
addon=Path(__file__).resolve().parent/"r11_art_direction_toolbar.py"
assert addon.is_file()
script_text=bpy.data.texts.load(str(addon))
script_text.name="R11_RUN_THIS_FOR_NATIVE_ART_TOOLBAR.py"
image["source"]="R10 archived actual four-GLB rendering, historical rejected/held references"
image["sha256"]=atlas_sha
scene["R11_PRODUCTION_WORKSPACE"]="Real Blender native visual editing experiment"
scene["R11_ART_PROPOSAL"]=False
scene["R11_EDITABLE_OBJECT"]=o.name
scene["R11_ORIGINAL_REFERENCE_IMAGE_SHA256"]=atlas_sha
scene["R11_R10_ORIGINALS_NOT_CHANGED"]=True
scene["R11_MAIN_CHANGED"]=False
scene["R11_MINECRAFT_WRITE"]=False
scene["R11_10KM_MASTER_COMPLETE"]=False
scene["R11_M247C_CENTRAL_ART_ADOPTED"]=False
scene["R11_CAMERA_LOCKED"]=True
scene["R11_GUI_ARTIST_REVISION"]=0
scene["R11_MODEL_READY_FOR_HUMAN_VISUAL_EDIT"]=True
bpy.ops.wm.save_as_mainfile(filepath=str(dst/"R11_OPEN_IN_BLENDER_VISUAL_SCULPT_STUDIO.blend"))
for name,*_ in camera_def:
    scene.camera=bpy.data.objects[name]
    scene.render.filepath=str(dst/(name+".png"))
    bpy.ops.render.render(write_still=True)
# Save original carefully; never overwrite canonical with last camera change.
baseline=hashlib.sha256((dst/"R11_OPEN_IN_BLENDER_VISUAL_SCULPT_STUDIO.blend").read_bytes()).hexdigest()
manifest={
 "workflow":"R11 native Blender art-directed visual workstation, neutral geometry fixture only",
 "not_a_new_city_massing":True,"not_art_adopted":True,
 "R10_original_source_art_status":"G7 A hold but stopped, G6 B rejected, G6 C later stopped, G7 C N1 rejected",
 "reference_art_image_source_sha256":atlas_sha,
 "baseline_blend_sha256":baseline,
 "real_mesh_vertices":len(o.data.vertices),
 "real_mesh_quads":len(o.data.polygons),
 "native_shape_keys":[x.name for x in o.data.shape_keys.key_blocks],
 "review_cameras":[a[0] for a in camera_def],
 "actual_blender_version":bpy.app.version_string,
 "main_changed":False,"m247_c_adopted":False,"minecraft_write":False,
 "human_sculpt_art_success":False
}
(dst/"R11_STUDIO_BASE_MANIFEST.json").write_text(
  json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf8")
print("R11_REAL_NATIVE_STUDIO_CREATED",json.dumps(manifest))
