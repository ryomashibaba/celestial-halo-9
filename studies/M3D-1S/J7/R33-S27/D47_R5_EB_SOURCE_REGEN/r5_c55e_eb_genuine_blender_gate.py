"""D47-R5 G0 — independently rerender verified Claude C55-E E-B SOURCE in genuine Blender.

PROVENANCE: original completed EB GLB is NOT in GitHub archive.
This run REGENERATES an approximate candidate from unchanged archived source
with explicitly reduced ds,dw and no terrain, not a copy of original C55-E v3.
The archived source branch is checked out read-only to c55e_ref.
No art adoption; no edit of Claude original; no main/Minecraft changes.
This is an early visual ART G0 to DECIDE whether direct sculpt is warranted.
"""
import sys,hashlib,json,math,time,importlib.util
from pathlib import Path
import numpy as np
import bpy
from mathutils import Vector
ROOT=Path.cwd()
SRC=ROOT/"c55e_ref"/"studies"/"M3D-1S"/"claude"/"C55-E"/"code"
OUT=Path(sys.argv[-1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
assert SRC.is_dir(),SRC
sys.path.insert(0,str(SRC))
from eb_well import build
# Original authored by Claude study. We do NOT alter its geometry source or
# claim the regenerated geometry is identical to absent original GLB.
DS=34.0; DW=22.0
start=time.time()
candidate, info, frames, sampled_solids=build(ds=DS,dw=DW,seed=3,
    ground=False,log=lambda s:print("C55E_SOURCE_LOG",s))
V=candidate["V"];F=candidate["F"];M=candidate["M"]
assert V.ndim==2 and V.shape[1]==3 and len(F)>140000
assert np.isfinite(V).all() and F.min()>=0 and F.max()<len(V)
if len(V)>4000000:raise RuntimeError(f"cap: materialized vertices {len(V)}")
print("SOURCE_REGENERATION_VERTS_TRIS",len(V),len(F),info,"seconds",round(time.time()-start,1))
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
def group(name):
    c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c);return c
geom_col=group("01 SOURCE-DERIVED EB REAL GEOMETRY NOT ORIGINAL EB GLB")
camera_col=group("02 FIXED ART G0 CAMERAS")
mats=[]
for n,rgb in [("E_B_inner_habitation_grey",(.66,.67,.67)),
              ("E_B_outer_mass_grey",(.54,.55,.57)),
              ("E_B_ground_context_absent",(.29,.29,.29))]:
    m=bpy.data.materials.new(n);m.diffuse_color=(*rgb,1);mats.append(m)
# The original source maintains distinct per-triangle classes 0/1.
# Split by those classes into separable real Blender meshes for future edits.
objects=[]
for mi in sorted(set(int(v) for v in M)):
    mask=np.flatnonzero(M==mi)
    if not len(mask):continue
    ff=F[mask]
    # remap only indexed vertices to keep 3D editable at scale.
    used,inverse=np.unique(ff.reshape(-1),return_inverse=True)
    xyz=V[used].astype(np.float32,copy=False)
    nf=len(ff);nv=len(used)
    mesh=bpy.data.meshes.new(f"C55E_EB_SOURCE_CLASS_{mi}_EDITABLE")
    mesh.vertices.add(nv)
    mesh.vertices.foreach_set("co",xyz.reshape(-1))
    mesh.loops.add(nf*3)
    mesh.loops.foreach_set("vertex_index",inverse.astype(np.int32))
    mesh.polygons.add(nf)
    mesh.polygons.foreach_set("loop_start",np.arange(0,3*nf,3,dtype=np.int32))
    mesh.polygons.foreach_set("loop_total",np.full(nf,3,np.int32))
    mesh.update(calc_edges=True)
    obj=bpy.data.objects.new(f"EB_REGEN_CLASS_{mi}_READONLY_G0",mesh)
    geom_col.objects.link(obj);mesh.materials.append(mats[min(mi,2)])
    obj["SOURCE_BACKREF"]="archive/claude-c55e-source-and-evidence-20261029"
    obj["MATERIAL_CLASS"]=mi
    obj["SOURCE_GENERATION_DOWNSAMPLED"]=True
    objects.append(obj)
    print("MESH_CREATED",obj.name,nv,nf,flush=True)
del V,F,M,candidate
def camera(name,eye,target,ortho=None,lens=32):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d)
    camera_col.objects.link(o);o.location=eye
    o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
    d.clip_end=60000
    if ortho:d.type="ORTHO";d.ortho_scale=ortho
    else:d.lens=lens
    return o
cams=[
 ("01_FRONT",(0,-10900,2900),(0,0,2300),11600,35),
 ("02_OBLIQUE",(8800,-8900,6200),(0,0,2100),13200,35),
 ("03_SIDE",(10700,0,2900),(0,0,2300),11800,35),
 ("04_REAR",(0,10900,3000),(0,0,2300),11600,35),
 ("05_AERIAL",(4800,-5200,12200),(0,0,2100),14600,35),
 ("06_GROUND_UP",(720,-1400,70),(0,200,2800),None,23),
 ("07_VOID_INSIDE",(0,-500,2100),(2300,1700,2650),None,26)]
for name,eye,target,ortho,lens in cams:camera(name,eye,target,ortho,lens)
scene=bpy.context.scene
scene.render.engine="BLENDER_WORKBENCH"
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_cavity=True
scene.render.resolution_x=900;scene.render.resolution_y=590
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene["research_phase"]="D47-R5 C55E EB genuine Blender independent SOURCE regeneration G0"
scene["art_adopted"]=False
scene["original_C55E_GLb_imported"]=False
scene["resampled_source_parameters"]={"ds_m":DS,"dw_m":DW}
scene["official_city_master"]=False
scene["minecraft_write"]=False
scene["Work_used"]=False
scene["c55e_art_state"]="HOLD / this regenerated geometry UNREVIEWED"
scene["formal_coordinates_verified"]=False
blend=OUT/"R5_EB_SOURCE_DERIVED_G0_EDITABLE.blend"
glb=OUT/"R5_EB_SOURCE_DERIVED_G0.glb"
bpy.ops.wm.save_as_mainfile(filepath=str(blend))
# GLB export may be slower but is required to prove a shared, editable 3D output.
bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",
                export_cameras=False,export_lights=False,export_yup=True)
for name,*_ in cams:
    scene.camera=bpy.data.objects[name]
    scene.render.filepath=str(OUT/(name+".png"))
    bpy.ops.render.render(write_still=True)
source_files=("eb_well.py","lib_e.py","core.py","blocks.py","raster_c55c.py","rig.py")
sha={n:hashlib.sha256((SRC/n).read_bytes()).hexdigest() for n in source_files}
bounds=np.array([tuple(obj.matrix_world@Vector(x) for x in obj.bound_box)
                 for obj in objects],dtype=object) if False else None
manifest={
 "state":"TRUE_BLENDER_REGENERATED_FROM_ARCHIVED_SOURCE_ART_UNREVIEWED",
 "never_original_C55E_GLb":True,
 "source_branch":"archive/claude-c55e-source-and-evidence-20261029",
 "source_code_sha256":sha,
 "sampling_differs_from_C55E_original":{"ds_m":DS,"dw_m":DW,"ground":False},
 "source_info":info,
 "numpy_source_regeneration_time_s":round(time.time()-start,1),
 "blender_version":bpy.app.version_string,
 "mesh_classes":[{"name":o.name,"vertices":len(o.data.vertices),"triangles":len(o.data.polygons)} for o in objects],
 "cameras":[n for n,*_ in cams],
 "art":"NOT REVIEWED", "strongest_void_principle":"unverified with independent Blender",
 "complete_10km_master":False,"formal_m247_c_art_adopted":False,
 "same_coords_M204_W0_M207":False,"minecraft_construction":False
}
(OUT/"R5_EB_G0_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2,default=str),encoding="utf8")
print("R5_REAL_BLENDER_SOURCE_DERIVED_EB_DONE",json.dumps(manifest,ensure_ascii=False,default=str)[:3500])
