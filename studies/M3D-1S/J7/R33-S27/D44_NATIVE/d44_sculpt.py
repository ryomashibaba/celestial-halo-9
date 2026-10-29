"""D44 ACTUAL edit of saved D43 BLEND (not regenerated) – ART TEST ONLY.
Recompose rejected megamasses by severe spatial shear and excavated civic sky voids.
The intent is to test if direct geometry edits improve silhouette, not claim acceptance.
Usage: python d44_sculpt.py /tmp/d43_artifact /tmp/d44_output
"""
import bpy, json, sys, hashlib, math, struct
from pathlib import Path
from mathutils import Vector, Matrix
src,out=map(Path,sys.argv[-2:])
out.mkdir(parents=True,exist_ok=True)
base=src/"D43_BASE_EDITABLE.blend"
assert base.exists(),"Missing genuine D43 native source BLEND"
expected="429222e8d613dd72c00815b8f78f0f19f5b29603b8020f03203b9e98d3c65f96"
digest=hashlib.sha256(base.read_bytes()).hexdigest()
assert digest==expected,(digest,expected)
bpy.ops.wm.open_mainfile(filepath=str(base))
assert bpy.app.version_string.startswith("4.5.15")
def object_digest(o):
    h=hashlib.sha256()
    h.update(o.name.encode())
    for row in o.matrix_world:
        h.update(struct.pack("<4d",*row))
    for v in o.data.vertices:h.update(struct.pack("<3d",*v.co))
    for p in o.data.polygons:
        h.update(struct.pack("<I",len(p.vertices)))
        for i in p.vertices:h.update(struct.pack("<I",i))
    return h.hexdigest()
protected={o.name:object_digest(o) for o in bpy.data.objects
           if o.type=="MESH" and ("W0 STUDY ONLY" in [c.name for c in o.users_collection]
                            or "H1-H6 PROVISIONAL" in [c.name for c in o.users_collection]
                            or "SB01-SB16 PROVISIONAL" in [c.name for c in o.users_collection])}
assert len(protected)>20,len(protected)
names=[
"CITY_MASS A left ascending cliff",
"CITY_MASS B right dislocated escarpment",
"CITY_MASS C inhabited back-fold"]
shapes=[bpy.data.objects[n] for n in names]
before={o.name:{"vertices":len(o.data.vertices),"faces":len(o.data.polygons)} for o in shapes}
# Sculpt the existing mesh. The sparse profile receives deep non-rigid shears;
# this is an object DATA edit, not a visual overlay.
for idx,o in enumerate(shapes):
    for v in o.data.vertices:
        z=float(v.co.z); t=max(0.,min(1.,z/4200.))
        x=float(v.co.x);y=float(v.co.y)
        if idx==0:
            v.co.x=x-115*math.sin(t*6.8)-460*t*t
            v.co.y=y+280*math.sin(t*math.pi*1.35)+190*t
        elif idx==1:
            v.co.x=x+330*t+230*math.sin(2.5*math.pi*t)
            v.co.y=y-380*t*t+130*math.sin(4*t)
        else:
            v.co.x=x-510*t+220*math.sin(5*t)
            v.co.y=y+400*t+160*math.sin(6*t)
        # Remove thick monolith scale especially in the upper city:
        # city-volume is supposed to be porous, not a solid primitive.
        v.co.x*=1+0.025*math.sin(t*11+idx)
    o.data.update()
# Actual macro voids cut THROUGH existing monolithic masses.
# Cuts are 350-520m high and 650-1040m wide: not windows/decorations.
cut_params={
0:[(-1520,-450,1000,980,1700,420,0.12),
   (-1330,  80,2060,1000,1300,470,-0.14),
   (-1170, 590,3030,1040,1450,420,0.20)],
1:[(1290,440,1110,880,1650,390,-0.14),
   (1180,  0,2180,850,1550,480, 0.16),
   (1350,-440,3100,790,1450,440,-0.12)],
2:[(-360,1300,970,740,1550,380,0.08),
   (100,1330,1850,710,1400,470,-0.21)]
}
cut_stats={}
for idx,o in enumerate(shapes):
    cuts=[]
    for j,(x,y,z,sx,sy,sz,theta) in enumerate(cut_params[idx]):
        bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,z))
        cutter=bpy.context.object;cutter.name=f"D44_TEMP_VOID_{idx}_{j}"
        cutter.dimensions=(sx,sy,sz)
        cutter.rotation_euler[1]=theta
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        mod=o.modifiers.new(name=f"EXCAVATE_CIVIC_SKY_VOID_{j}",type="BOOLEAN")
        mod.operation="DIFFERENCE";mod.solver="EXACT";mod.object=cutter
        try:
            bpy.context.view_layer.objects.active=o
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception as e:
            raise AssertionError(f"Blender boolean failed {o.name}, cutter {j}: {e}")
        bpy.data.objects.remove(cutter,do_unlink=True)
        cuts.append((j,x,y,z,sx,sy,sz))
    o.data.update();cut_stats[o.name]={"cutters":cuts,"new_vertices":len(o.data.vertices),
        "new_polygons":len(o.data.polygons)}
# Explicitly verify protected original city coordinates and all its placeholder anchors.
for name,h in protected.items():
    assert name in bpy.data.objects
    assert object_digest(bpy.data.objects[name])==h,("PROTECTED_CHANGED",name)
assert len([o for o in bpy.data.objects if o.type=="CAMERA"])==8
assert all(bpy.data.objects[n].data.vertices for n in names)
assert all(not o.name.startswith("D44_TEMP_VOID") for o in bpy.data.objects)
scene=bpy.context.scene
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_cavity=True
scene.render.resolution_x=900;scene.render.resolution_y=540
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.camera=bpy.data.objects["01_city_aerial"]
bpy.ops.wm.save_as_mainfile(filepath=str(out/"D44_EDIT1_EDITABLE.blend"))
bpy.ops.export_scene.gltf(filepath=str(out/"D44_EDIT1.glb"),export_format="GLB",
                           export_cameras=False,export_lights=False)
cameras=[
"01_city_aerial","02_hero_front","03_hero_oblique",
"04_hero_side","05_hero_back","06_ground_approach",
"07_civic_void","08_sky_residential"]
for c in cameras:
    scene.camera=bpy.data.objects[c]
    scene.render.filepath=str(out/(c+".png"))
    bpy.ops.render.render(write_still=True)
report={"status":"SCULPTED_NATIVE_EDIT1_NO_ART_PASS",
        "d43_parent_blend_sha256":digest,
        "protected_total":len(protected),"protected_unchanged":True,
        "editable_masses":names,"before":before,"after":cut_stats,
        "genuine_native_blender":bpy.app.version_string,
        "real_rendered_views":len(cameras),
        "art":"NOT_REVIEWED",
        "route":"NOT_VERIFIED",
        "edit":"actual existing saved BLEND mesh vertex deformation + large BOOLEAN geometry removal"}
(out/"D44_SCULPT_AUDIT.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print("D44_ACTUAL_BLENDER_MESH_EDIT_COMPLETED",json.dumps({
    k:v for k,v in report.items() if k not in ("before","after")}))
