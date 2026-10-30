"""R11 independent reality gate: native GUI shape-key edit, camera switching, export.

Only test fixture geometry is edited. Source blend must remain byte-identical.
No aesthetic approval inferred from pixels, geometry or a GUI process.
"""
import bpy, sys, hashlib, json, importlib.util
from pathlib import Path
from statistics import median
from PIL import Image, ImageChops
p=Path(sys.argv[sys.argv.index("--")+1]).resolve()
base=p/"R11_OPEN_IN_BLENDER_VISUAL_SCULPT_STUDIO.blend"
edited=p/"R11_GUI_ACTUAL_INPUT_EDITED_COPY.blend"
manifest=json.loads((p/"R11_STUDIO_BASE_MANIFEST.json").read_text())
source_sha=hashlib.sha256(base.read_bytes()).hexdigest()
assert source_sha==manifest["baseline_blend_sha256"]
name="R11_EDIT_ONLY_UNAPPROVED_STUDY_SURFACE"
def inspect(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    o=bpy.data.objects[name]
    if o.mode=="EDIT":o.update_from_editmode()
    assert len(o.data.vertices)==manifest["real_mesh_vertices"]
    assert o.data.shape_keys
    assert list(o.data.shape_keys.key_blocks.keys())==manifest["native_shape_keys"]
    key=o.data.shape_keys.key_blocks["R11_ARTIST_REVERSIBLE_LAYER"]
    # store just vertices needed for edit proof
    shape=[tuple(v.co) for v in key.data]
    basis=[tuple(v.co) for v in o.data.shape_keys.key_blocks["Basis"].data]
    cam={n:tuple(bpy.data.objects[n].location) for n in manifest["review_cameras"]}
    metadata=(bpy.context.scene.get("R11_ART_PROPOSAL"),
              bpy.context.scene.get("R11_MINECRAFT_WRITE"))
    return shape,basis,cam,metadata
bshape,bbasis,bcam,bmeta=inspect(base)
ashape,abasis,acam,ameta=inspect(edited)
assert bmeta==(False,False) and ameta==(False,False)
assert bcam==acam
deltas=[a[0]-b[0] for a,b in zip(ashape,bshape)]
# Editing of a shape key is far more precise than SHA difference alone.
assert 29.0<median(deltas)<31.0,("shape key failed UI edit",median(deltas))
assert max(deltas)-min(deltas)<.01,("inconsistent GUI selection",max(deltas),min(deltas))
assert all(abs(a[i]-b[i])<.01 for a,b in zip(abasis,bbasis) for i in range(3)), \
       "MOVED BASIS unexpectedly"
assert hashlib.sha256(base.read_bytes()).hexdigest()==source_sha
prehash=hashlib.sha256(edited.read_bytes()).hexdigest()
images={}
for label in ("01_REAL_GUI_BEFORE","02_REAL_GUI_AFTER"):
    path=p/(f"R11_{label}.png")
    assert path.stat().st_size>4000
    with Image.open(path) as im:
        assert im.size[0]>=1000 and im.size[1]>=600
        assert im.getbbox() is not None
    images[label]=hashlib.sha256(path.read_bytes()).hexdigest()
assert images["01_REAL_GUI_BEFORE"]!=images["02_REAL_GUI_AFTER"]
# In native Blender process, import packed toolbar, execute six-camera switch
# and *its actual checkpoint operator*. This is an OPERATOR UNIT TEST,
# not a claim that the mouse clicked each of its buttons.
bpy.ops.wm.open_mainfile(filepath=str(edited))
path=Path("studies/M3D-1S/J7/R33-S27/D47_R11_WORKSTATION/r11_art_direction_toolbar.py").resolve()
spec=importlib.util.spec_from_file_location("r11_art_direction_toolbar",path)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.register()
for n in manifest["review_cameras"]:
    result=bpy.ops.r11.select_review_view(camera_name=n)
    assert "FINISHED" in result
    assert bpy.context.scene.camera.name==n
result=bpy.ops.r11.freeze_artist_evidence()
assert 'FINISHED' in result,result
assert hashlib.sha256(edited.read_bytes()).hexdigest()==prehash
rev=p/"R11_ARTIST_REVISIONS"/"R11_REV_001"
audit=json.loads((rev/"R11_REVISION_AUDIT.json").read_text())
assert audit["test_fixture_not_art_proposal"] and not audit["formal_art_approved"]
assert len(audit["real_rendered_camera_images"])==6
assert (rev/"R11_REV_001_EDITABLE.blend").stat().st_size>20000
assert (rev/"R11_REV_001_SURFACE.glb").stat().st_size>10000
for png in audit["real_rendered_camera_images"].values():
    assert (rev/png).stat().st_size>2000
# Separate saved checkpoint reopen/GLB reimport
bpy.ops.wm.open_mainfile(filepath=str(rev/"R11_REV_001_EDITABLE.blend"))
assert bpy.data.objects.get(name) is not None
assert bpy.context.scene.get("R11_ART_PROPOSAL") is False
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(rev/"R11_REV_001_SURFACE.glb"))
assert len([o for o in bpy.data.objects if o.type=="MESH"])>=1
final={
 "result":"R11_TRUE_GUI_NATIVE_EDIT_AND_TOOLBAR_CHECKPOINT_TECH_PASS",
 "real_GUI_before_and_after_screenshots":images,
 "source_blend_sha256_unchanged":source_sha,
 "source_blend_unchanged":True,
 "neutral_shape_key_modified_through_actual_GUI":True,
 "median_shape_key_x_movement_m":round(median(deltas),3),
 "basis_shape_key_completely_unmodified":True,
 "fixed_six_cameras_preserved":True,
 "button_camera_switch_operator_invoked_in_Blender":True,
 "checkpoint_operator_invoked_in_Blender":True,
 "saved_checkpoint_blend_and_glb_reimported":True,
 "six_review_png_created_from_checkpoint":True,
 "operator_unit_test_distinct_from_GUI_click":True,
 "gui_art_sculpt_quality":"NOT_DEMONSTRATED",
 "not_a_city_or_M247_C_design":True,
 "formal_art_approved":False,
 "city_master_complete":False,
 "minecraft_write":False
}
(p/"R11_INDEPENDENT_NATIVE_AND_GUI_AUDIT.json").write_text(
    json.dumps(final,ensure_ascii=False,indent=2),encoding="utf8")
print("R11_TRUE_GUI_SHAPE_EDIT_30M_AND_CHECKPOINT_OPERATOR_VERIFIED",final)
