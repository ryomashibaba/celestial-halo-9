"""R15 evidence-first art review of D2-G7 ORIGINAL seasonal living-city GLBs.

The archived art/d originals are imported without touching any vertex. Reframe
crown-only (hide 10km schematic background), then frame with background once.
All camera locations are fixed, and all photos are real Blender renders.
This is NOT an art pass and NOT a central-city design or source-model edit.
"""
import bpy, sys, json, hashlib, math
from pathlib import Path
from mathutils import Vector,Matrix
from PIL import Image,ImageOps,ImageDraw,ImageFont
ROOT=Path.cwd()
OUT=Path(sys.argv[-1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
SRC=ROOT/"source_d"/"studies"/"D2-G7"
CANDIDATES=[("WET",SRC/"Habitat-Crown-wet.glb"),("DRY",SRC/"Habitat-Crown-dry.glb")]
# Original trimesh source is Z-up. glTF Blender import in this source's
# recorded assets produces (x,-z,y) i.e. R_x(+90 degrees). Source GLBs
# must NOT be modified. Only normalize the imported viewing scene's ROOT
# transform by inverse Rx(-90), leaving all actual mesh vertices unchanged.
def source_corrected_import(filepath):
    bpy.ops.import_scene.gltf(filepath=str(filepath))
    roots=[o for o in bpy.data.objects if o.parent is None]
    assert roots,("No source scene roots",filepath)
    inverse=Matrix.Rotation(-math.pi/2,4,'X')
    for obj in roots:
        obj.matrix_world=inverse @ obj.matrix_world
    return [o for o in bpy.data.objects if o.type=="MESH"]

# The old hard-coded km camera target is NOT a trustworthy framing coordinate
# after Blender GLB importer applies source node transforms. Independently
# inspect native object world-space bounds in BOTH seasons first.
BG_PREFIXES=("10km_study_terrain","north_mountain_peak_",
    "west_cliff_face","east_artificial_inland_sea","southwest_great_void",
    "urban_context_")
season_bbox={}
for lab,glb in CANDIDATES:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    imported=source_corrected_import(glb)
    central=[o for o in imported
             if not o.name.startswith(BG_PREFIXES)]
    assert len(central)>=25,(lab,len(central))
    corners=[o.matrix_world@Vector(p) for o in central for p in o.bound_box]
    lo=Vector(tuple(min(v[k] for v in corners) for k in range(3)))
    hi=Vector(tuple(max(v[k] for v in corners) for k in range(3)))
    # Critical sanity check against D2-G7 author's recorded CENTRAL Z span.
    expected_height=3.8267 if lab=="WET" else 3.0903
    assert abs((hi-lo).z-expected_height)<.015,(lab,"Y/Z axis still wrong",list(lo),list(hi))
    season_bbox[lab]={"min":list(lo),"max":list(hi),
                       "span":list(hi-lo),"objects":len(central)}
    print("R15_REAL_NATIVE_WORLD_BOUNDS",lab,season_bbox[lab],flush=True)
full_lo=Vector(tuple(min(season_bbox[n]["min"][k] for n in ("WET","DRY"))
                     for k in range(3)))
full_hi=Vector(tuple(max(season_bbox[n]["max"][k] for n in ("WET","DRY"))
                     for k in range(3)))
C=(full_lo+full_hi)*.5
L=max(full_hi-full_lo)
assert 3<L<10,(L,full_lo[:],full_hi[:])
vnames=[
  "01_EAST_SEA_APPROACH",
  "02_FRONT",
  "03_SIDE",
  "04_REAR",
  "05_OBLIQUE",
  "06_AERIAL",
  "07_ROOT_CIVIC_EYE",
  "08_HIGH_INHABITED_EYE",
  "09_WIDE_CONTEXT"]
def cam_pose(offset,look=(0,0,0),ortho=1.3):
    # The same WORLD positions are reused verbatim for wet & dry.
    eye=tuple(C+Vector(offset)*L)
    target=tuple(C+Vector(look)*L)
    return (eye,target,None if ortho is None else L*ortho)
cams={
  "01_EAST_SEA_APPROACH":cam_pose((1.7,-1.9,.75),ortho=1.45),
  "02_FRONT":cam_pose((0,-2.3,.38),ortho=1.34),
  "03_SIDE":cam_pose((2.2,0,.38),ortho=1.34),
  "04_REAR":cam_pose((0,2.3,.38),ortho=1.34),
  "05_OBLIQUE":cam_pose((-2.0,-1.9,.90),ortho=1.48),
  "06_AERIAL":cam_pose((1.7,-1.7,2.3),ortho=1.50),
  "07_ROOT_CIVIC_EYE":cam_pose((0,-.28,-.40),look=(0,.15,.02),ortho=None),
  "08_HIGH_INHABITED_EYE":cam_pose((.20,-.22,.20),look=(-.15,.09,.05),ortho=None),
  "09_WIDE_CONTEXT":cam_pose((1.9,-2.15,1.6),ortho=2.65),
}
record={}
for label,source in CANDIDATES:
    assert source.is_file(),source
    bpy.ops.wm.read_factory_settings(use_empty=True)
    original=source_corrected_import(source)
    scene=bpy.context.scene
    assert len(original)>150,(label,len(original))
    vertex_count=sum(len(o.data.vertices) for o in original)
    tri_count=sum(sum(max(1,len(p.vertices)-2) for p in o.data.polygons) for o in original)
    orig_vertex_sha={}
    for o in original:
        h=hashlib.sha256()
        for v in o.data.vertices:h.update(("%0.7f,%0.7f,%0.7f;"%tuple(v.co)).encode())
        orig_vertex_sha[o.name]=h.hexdigest()
    # Authoritative background naming contract is D2-G7 build_study.py
    # validate(): terrain, mountain, west cliff, east inland sea, southwest
    # void, urban context markers. Size-only filtering wrongly retained all
    # non-terrain background and ruined eight candidate photographs.
    context_prefixes=BG_PREFIXES
    context=[o.name for o in original if o.name.startswith(context_prefixes)]
    assert len(context)>=15,(label,"background objects not isolated",len(context))
    assert len(original)-len(context)>=25,(label,"too few candidate meshes")
    assert not any(o.name in context for o in original
        if o.name.startswith(("crown_core_","root_city_","H1_","H2_","H3_","H4_","H5_","H6_"))),(label,"central mass incorrectly hidden")
    context_set=set(context)
    scene.render.engine="BLENDER_WORKBENCH"
    scene.display.shading.light="STUDIO"
    scene.display.shading.color_type="MATERIAL"
    scene.display.shading.show_cavity=True
    scene.display.shading.cavity_type="BOTH"
    scene.display.shading.background_type="VIEWPORT"
    scene.display.shading.background_color=(.085,.11,.13)
    scene.render.resolution_x=1100;scene.render.resolution_y=720
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    for name,(eye,target,ortho) in cams.items():
        d=bpy.data.cameras.new(name)
        o=bpy.data.objects.new(name,d)
        scene.collection.objects.link(o)
        o.location=eye
        o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
        d.clip_end=1000;d.clip_start=.002
        if ortho:
            d.type="ORTHO";d.ortho_scale=ortho
        else:
            d.type="PERSP";d.lens=20
    frames=[]
    for name in vnames:
        # Render central architectural candidate without large schematic context;
        # last frame deliberately restores ALL original source meshes.
        wide=name=="09_WIDE_CONTEXT"
        for o in original:o.hide_render=(o.name in context_set) and not wide
        scene.camera=bpy.data.objects[name]
        fp=OUT/f"{label}_{name}.png"
        scene.render.filepath=str(fp)
        bpy.ops.render.render(write_still=True)
        assert fp.stat().st_size>2000,fp
        frames.append(fp.name)
    for o in original:o.hide_render=False
    assert all(orig_vertex_sha[o.name]==hashlib.sha256("".join(
      "%0.7f,%0.7f,%0.7f;"%tuple(v.co) for v in o.data.vertices).encode()
    ).hexdigest() for o in original)
    scene["R15_canonical_M247_C_adopted"]=False
    scene["R15_central_city_10km_completed"]=False
    scene["R15_original_D_source_unchanged"]=True
    scene["R15_display_axis_normalization"]="source trimesh Z-up restored from imported glTF (x,-z,y) via root Rx(-90), original GLB bytes and vertices unchanged"
    scene["R15_visual_art_state"]="UNREVIEWED_G0"
    scene["R15_source_glb_sha256"]=hashlib.sha256(source.read_bytes()).hexdigest()
    dest=OUT/(label+"_D2G7_ORIGINAL_IMPORTED_NATIVE.blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(dest))
    record[label]={
        "original_branch":"art/d",
        "source_file":str(source.relative_to(ROOT)),
        "source_file_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "native_reopened_blend":dest.name,
        "source_mesh_objects":len(original),
        "source_mesh_vertices":vertex_count,
        "source_triangles":tri_count,
        "central_only_background_hidden_objects":context,
        "background_filter_method":"original D2-G7 build_study.py validate() context_prefixes",
        "camera_renders":frames,
        "original_vertices_unchanged":True,
        "formal_art_adopted":False,
        "real_inhabited_rooms_certified":False
    }
    print("R15_ORIGINAL_ART_D_SEASON_RELOADED",label,len(original),vertex_count,tri_count,"background",len(context),flush=True)

# The contact sheet is an INDEX of REAL PNGs, NOT a generated fake city.
pad=10;tilew=390;tileh=267;top=63;left=125
atlas=Image.new("RGB",(left+9*tilew,top+2*(tileh+50)+30),(238,239,240))
draw=ImageDraw.Draw(atlas)
try:
 font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",15)
 big=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",19)
except OSError:
 font=ImageFont.load_default();big=font
draw.text((12,10),"R15 | D2-G7 ORIGINAL WET/DRY | real Blender | background isolated for 01-08",font=big,fill=(30,40,49))
for col,n in enumerate(vnames):
 draw.text((left+col*tilew+6,35),n[3:].replace("_"," "),font=font,fill=(18,32,42))
for ri,lab in enumerate(("WET","DRY")):
 y=top+ri*(tileh+50)
 draw.text((12,y+100),lab+" source",font=big,fill=(18,33,50))
 for ci,n in enumerate(vnames):
    im=Image.open(OUT/f"{lab}_{n}.png").convert("RGB")
    im=ImageOps.contain(im,(tilew-8,tileh-8))
    atlas.paste(im,(left+ci*tilew+(tilew-im.width)//2,y+4))
atlas.save(OUT/"R15_D2G7_ORIGINAL_18_TRUE_VIEWS_ATLAS.jpg",quality=88)
f=SRC/"decision.md"
assert f.is_file()
data={
 "scope":"art/d D2-G7 independent source provenance and all eight source-faithful architecture views plus one wide background, both seasons",
 "history":"D branch's latest art status is HOLD awaiting central judgment; no approval",
 "original_D_decision_sha256":hashlib.sha256(f.read_bytes()).hexdigest(),
 "original_D_preview_sha256":hashlib.sha256((SRC/"preview.jpg").read_bytes()).hexdigest(),
 "all_original_GLBS_unchanged":True,
 "view_only_axis_orientation_correction":"Inverse Rx(-90deg) applied to imported scene roots, NOT to source geometry",
 "author_original_Z_height_span_crosschecked":True,
 "camera_conditions":"same for WET and DRY, Blender Workbench, 1100x720; center-only hides giant schematic background except 09",
 "comparison_not_10km_master":True,
 "minecraft_construction":False,
 "art_adopted":False,
 "real_source_world_bounds":season_bbox,
 "fixed_common_scene_center":list(C),
 "fixed_reference_scale":float(L),
 "models":record
}
(OUT/"R15_D_ORIGINALS_PROVENANCE_AND_VIEW_MANIFEST.json").write_text(
 json.dumps(data,ensure_ascii=False,indent=2),encoding="utf8")
print("R15_18_NATIVE_BLENDER_IMAGERY_READY_FOR_ART_REVIEW")
