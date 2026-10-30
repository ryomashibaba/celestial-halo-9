"""R14 E1 independent check of REAL native GUI partial edit and matched six Blender views.
No art score automatically; do not confuse a shape edit with a city proposal.
"""
import bpy,hashlib,json,sys,math
from pathlib import Path
from statistics import median
from mathutils import Vector
p=Path(sys.argv[-1]).resolve()
x=json.loads((p/"R14_E0_PROVENANCE.json").read_text())
objname="R11_EDIT_ONLY_UNAPPROVED_STUDY_SURFACE"
cams=[
"01_FRONTAL_EYE","02_SIDE_CROSS_SECTION","03_OBLIQUE_MASS",
"04_REAR_OTHER_SIDE","05_LOW_PUBLIC_VIEW","06_ABOVE_OTHER_WORLD"]
assert x["selected_vertex_count"]>=100
def setup(fn):
    bpy.ops.wm.open_mainfile(filepath=str(p/fn))
    obj=bpy.data.objects[objname]
    if obj.mode=='EDIT':obj.update_from_editmode()
    keys=obj.data.shape_keys.key_blocks
    basic=[tuple(k.co) for k in keys["Basis"].data]
    shaped=[tuple(k.co) for k in keys["R11_ARTIST_REVERSIBLE_LAYER"].data]
    cameras={n:(tuple(bpy.data.objects[n].location),
       tuple(bpy.data.objects[n].rotation_euler)) for n in cams}
    assert len(basic)==x["total_vertices"]==len(shaped)
    assert bpy.context.scene.get("R14_ART_ADOPTED") is False
    if obj.mode=='EDIT':bpy.ops.object.mode_set(mode='OBJECT')
    return basic,shaped,cameras
basis0,shape0,cam0=setup("R14_E0_NATIVE_PRESELECTED.blend")
basis1,shape1,cam1=setup("R14_E1_ACTUAL_LOCAL_SCULPT.blend")
assert basis0==basis1,"Basis was changed, only shape key was intended"
assert cam0==cam1
selected=set(x["selected_indices"])
moved=[];unchanged=[]
for i,(a,b) in enumerate(zip(shape0,shape1)):
    d=[b[k]-a[k] for k in range(3)]
    if i in selected:
        assert abs(d[0])<.0001 and abs(d[2])<.0001
        assert abs(d[1]-120)<.025,(i,d)
        moved.append(d[1])
    else:
        assert all(abs(v)<.0001 for v in d),(i,d)
        unchanged.append(i)
assert len(moved)==len(selected) and len(unchanged)>200
assert abs(median(moved)-120)<.01
# Genuine source native model is byte-identical across audit.
assert hashlib.sha256((p/"R11_ORIGINAL_READONLY.blend").read_bytes()).hexdigest()==x["source_R11_blend_SHA256"]
assert hashlib.sha256((p/"R14_E0_NATIVE_PRESELECTED.blend").read_bytes()).hexdigest()==x["prepared_blend_sha256"]

# Capture genuine 6-view images, same camera and materials from each BLEND,
# not AI images; same WB settings and 960x650 each.
def render(fn,tag):
    bpy.ops.wm.open_mainfile(filepath=str(p/fn))
    scene=bpy.context.scene
    obj=bpy.data.objects[objname]
    if obj.mode=='EDIT':
        bpy.ops.object.mode_set(mode='OBJECT')
    scene.render.engine="BLENDER_WORKBENCH"
    scene.display.shading.color_type="MATERIAL"
    scene.display.shading.light="STUDIO"
    scene.display.shading.show_cavity=True
    scene.render.resolution_x=960;scene.render.resolution_y=650
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    for name in cams:
        scene.camera=bpy.data.objects[name]
        path=p/(tag+"_"+name+".png")
        scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
        assert path.stat().st_size>3000
render("R14_E0_NATIVE_PRESELECTED.blend","E0")
render("R14_E1_ACTUAL_LOCAL_SCULPT.blend","E1")
import struct
for f in [p/"R14_E0_REAL_GUI_BEFORE.png",p/"R14_E1_REAL_GUI_LOCAL_AFTER.png"]:
    raw=f.read_bytes()
    assert raw[:4]==bytes([137,80,78,71]) and len(raw)>9000
    w,h=struct.unpack(">II",raw[16:24])
    assert w>=1250 and h>=700
images=[]
for name in cams:
    before=(p/("E0_"+name+".png")).read_bytes()
    after=(p/("E1_"+name+".png")).read_bytes()
    images.append({"camera":name,"bytes_differ":hashlib.sha256(before).digest()!=hashlib.sha256(after).digest()})
assert sum(v["bytes_differ"] for v in images)>=4,images
report={
 "result":"REAL_GUI_PARTIAL_SHAPE_KEY_TECH_PASS_ONLY",
 "original_R11_file_hash_verified":True,
 "original_R11_file_not_modified":True,
 "basis_mesh_exactly_unchanged":True,
 "selected_local_vertices_moved":len(moved),
 "unselected_vertices_exactly_unchanged":len(unchanged),
 "actual_local_Y_displacement_m":round(median(moved),4),
 "all_6_camera_objects_unchanged":True,
 "matched_6_view_real_Blender_before_and_after":images,
 "true_GUI_desktop_screenshots":2,
 "art_quality":"NOT_EVALUATED",
 "not_urban_design":True,
 "formal_M247C_adopted":False,
 "minecraft_write":False}
(p/"R14_E1_INDEPENDENT_GUI_AND_12_RENDER_AUDIT.json").write_text(
    json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
print("R14_REAL_GUI_LOCAL_EDIT_COMPARISON_COMPLETE",json.dumps(report))
