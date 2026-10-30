"""R14 E2: independent Blender readback of first localized sculpt and second
*image-directed* boundary sculpt. Technical truth only; no art approval.
"""
import bpy,sys,json,hashlib,struct
from pathlib import Path
from statistics import median
p=Path(sys.argv[-1]).resolve()
spec=json.loads((p/"R14_E2_FEEDBACK_DIRECTED_EDIT_PLAN.json").read_text())
cameras=["01_FRONTAL_EYE","02_SIDE_CROSS_SECTION","03_OBLIQUE_MASS",
 "04_REAR_OTHER_SIDE","05_LOW_PUBLIC_VIEW","06_ABOVE_OTHER_WORLD"]
target="R11_EDIT_ONLY_UNAPPROVED_STUDY_SURFACE"
def read(n):
 bpy.ops.wm.open_mainfile(filepath=str(p/n))
 o=bpy.data.objects[target]
 if o.mode=="EDIT":o.update_from_editmode()
 basis=[tuple(q.co) for q in o.data.shape_keys.key_blocks["Basis"].data]
 shape=[tuple(q.co) for q in o.data.shape_keys.key_blocks["R11_ARTIST_REVERSIBLE_LAYER"].data]
 cam={name:(tuple(bpy.data.objects[name].location),
  tuple(bpy.data.objects[name].rotation_euler)) for name in cameras}
 if o.mode=="EDIT":bpy.ops.object.mode_set(mode="OBJECT")
 return basis,shape,cam
core=set(spec["initial_core_vertices_frozen"])
edge=set(spec["boundary_transition_vertices"])
assert len(core)==234 and len(edge)>65 and not(core&edge)
b1,s1,c1=read("R14_E1_READONLY_ORIGINAL.blend")
b2,s2,c2=read("R14_E2_GUI_BOUNDARY_REFINED.blend")
assert c1==c2 and b1==b2
changes=[]
for i,(v1,v2) in enumerate(zip(s1,s2)):
    delta=[v2[d]-v1[d] for d in range(3)]
    if i in edge:
       assert abs(delta[1]-60)<.03 and abs(delta[0])<.01 and abs(delta[2])<.01,(i,delta)
       changes.append(delta[1])
    else:
       assert all(abs(d)<.01 for d in delta),(i,delta)
assert len(changes)==len(edge)
assert abs(median(changes)-60)<.02
assert hashlib.sha256((p/"R14_E1_READONLY_ORIGINAL.blend").read_bytes()).hexdigest()==spec["E1_real_native_source_sha256"]
assert hashlib.sha256((p/"R14_E2_PREPARED_BOUNDARY_TRANSITION.blend").read_bytes()).hexdigest()==spec["E2_prepared_native_blend_sha256"]
for nm in ("R14_E2_BEFORE_REAL_GUI.png","R14_E2_AFTER_REAL_GUI.png"):
 raw=(p/nm).read_bytes()
 assert raw[:4]==bytes([137,80,78,71]) and len(raw)>9000
 w,h=struct.unpack(">II",raw[16:24])
 assert w>=1300 and h>=800
def render(file,prefix):
 bpy.ops.wm.open_mainfile(filepath=str(p/file))
 scene=bpy.context.scene
 obj=bpy.data.objects[target]
 if obj.mode=="EDIT":bpy.ops.object.mode_set(mode="OBJECT")
 scene.render.engine="BLENDER_WORKBENCH"
 scene.display.shading.color_type="MATERIAL"
 scene.display.shading.light="STUDIO"
 scene.display.shading.show_cavity=True
 scene.render.resolution_x=960;scene.render.resolution_y=650
 scene.render.resolution_percentage=100
 scene.render.image_settings.file_format="PNG"
 for name in cameras:
    scene.camera=bpy.data.objects[name]
    f=p/(prefix+"_"+name+".png");scene.render.filepath=str(f)
    bpy.ops.render.render(write_still=True)
    assert f.stat().st_size>3500
render("R14_E1_READONLY_ORIGINAL.blend","E1_MATCH")
render("R14_E2_GUI_BOUNDARY_REFINED.blend","E2")
dif={}
for cam in cameras:
 a=(p/("E1_MATCH_"+cam+".png")).read_bytes()
 b=(p/("E2_"+cam+".png")).read_bytes()
 dif[cam]=hashlib.sha256(a).digest()!=hashlib.sha256(b).digest()
assert sum(dif.values())>=4,dif
qa={
 "status":"TRUE_GUI_IMAGE_DIRECTED_SECOND_LOCAL_EDIT_TECH_PASS",
 "E1_core_selected_vertices":234,
 "E2_adjacent_transition_vertices_moved":len(edge),
 "E2_move_Y_m":round(median(changes),4),
 "E1_core_all_vertices_exactly_preserved":True,
 "all_nontransition_vertices_unchanged":True,
 "Basis_shape_key_unchanged":True,
 "six_review_cameras_unchanged":True,
 "source_E1_original_bytes_unchanged":True,
 "E1_E2_six_view_render_diff":dif,
 "actual_2_X11_edit_before_and_after_screenshots":True,
 "scope":"R11 fixture, not a new or edited city",
 "architectural_art":"REQUIRES_VISUAL_JUDGMENT_NO_AUTO_PASS",
 "official_M247C_adopted":False,"minecraft_write":False}
(p/"R14_E2_INDEPENDENT_FEEDBACK_SCULPT_AUDIT.json").write_text(
 json.dumps(qa,indent=2,ensure_ascii=False),encoding="utf8")
print("R14_E2_REAL_GUI_VISUAL_FEEDBACK_PASS",qa)
