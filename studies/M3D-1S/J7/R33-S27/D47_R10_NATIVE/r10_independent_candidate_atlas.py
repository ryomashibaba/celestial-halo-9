"""CELESTIAL HALO-9 D47 R10: art evidence board from EXISTING actual native 3D.

No new massing. No changes to existing art/a/b/c files; only reads checked-out
original 3D and their actual source-linked preview captures. All materials are
neutralized consistently, each model independently framed within its *own*
bounding box, and the exact dimensions remain in manifest. Important:
equalized image size is NOT the same real-world scale; never infer superiority
or M247-C art approval from these images.
"""
from pathlib import Path
import bpy, math, hashlib, json, sys
from mathutils import Vector
from PIL import Image, ImageDraw, ImageFont, ImageOps
P=Path(sys.argv[-1]).resolve()
P.mkdir(parents=True,exist_ok=True)
S=Path.cwd()
CANDIDATES=[
 {
  "id":"A_G7_HOLD",
  "ref":"art/a",
  "name":"A2 G7 I: Goryu Tenkutsu / held, no adoption",
  "model":"source_a/studies/A2-G7/selected.glb",
  "photo":"source_a/studies/A2-G7/preview.jpg",
  "decision":"source_a/studies/A2-G7/decision.md",
  "status":"ART HOLD / no new art approval",
  "risk":"front monumental arch; side wall; rear featureless monument"},
 {
  "id":"B_G6_REJECT",
  "ref":"art/b",
  "name":"B2 G6 C: Raised Street Fold City / rejected",
  "model":"source_b/studies/B2-G6/selected/study.glb",
  "photo":"source_b/studies/B2-G6/selected_views.jpg",
  "decision":"source_b/studies/B2-G6/REPORT_ja.md",
  "status":"ART REJECT / no details",
  "risk":"thick gate and nested public halls read as one huge slab"},
 {
  "id":"C_G6_HOLD_SUPERSEDED",
  "ref":"art/c",
  "name":"C2 G6 A: Kailiu Canopy / newer G7 rejected its mass",
  "model":"source_c/studies/C2-G6/A_CENTRAL.glb",
  "photo":"source_c/studies/C2-G6/SIX_VIEWS.png",
  "decision":"source_c/studies/C2-G7/decision.md",
  "status":"Historical HOLD; G7 self-review says ART BELOW BAR / STOP",
  "risk":"biological canopy shell dominates lived city"},
 {
  "id":"C_G7_N1_REJECT",
  "ref":"art/c",
  "name":"C2 G7 N1: Cross-Chamber Capitol / rejected",
  "model":"source_c/studies/C2-G7/N1_CENTRAL.glb",
  "photo":"source_c/studies/C2-G7/new_comparison.jpg",
  "decision":"source_c/studies/C2-G7/decision.md",
  "status":"ART REJECT / sculpted angular block",
  "risk":"big solid side wall and unoccupied high city"}
]
for c in CANDIDATES:
    for key in ("model","photo","decision"):
        assert (S/c[key]).exists(),(c["id"],key,c[key])

def cameras_for_bounds(cx,cy,cz,d):
    # Identical dimensionless viewing directions and identical screen padding.
    # Real measurements remain separate and originals are not rescaled.
    direction={
       "01_FRONT":Vector((.05,-1.0,.16)),
       "02_SIDE":Vector((1.0,.02,.19)),
       "03_OBLIQUE":Vector((1.0,-1.1,.68)),
       "04_REAR":Vector((.03,1.0,.2))}
    target=Vector((cx,cy,cz))
    scale=max(d)*1.55
    out={}
    for n,vec in direction.items():
        ob=bpy.data.objects.new(n,bpy.data.cameras.new(n))
        bpy.context.collection.objects.link(ob)
        ob.location=target+vec.normalized()*max(d)*2.6
        ob.rotation_euler=(target-ob.location).to_track_quat("-Z","Y").to_euler()
        ob.data.type="ORTHO";ob.data.ortho_scale=scale
        ob.data.clip_end=max(40000.0,max(d)*15)
        out[n]=ob
    return out

study=[]
renders=[]
for c in CANDIDATES:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    original=S/c["model"]
    orig_bytes=original.read_bytes()
    orig_hash=hashlib.sha256(orig_bytes).hexdigest()
    bpy.ops.import_scene.gltf(filepath=str(original.resolve()))
    objs=[o for o in bpy.data.objects if o.type=="MESH"]
    assert objs and len(objs)<100000
    minv=[float("inf")]*3; maxv=[float("-inf")]*3
    tri=0;verts=0; nonfinite=0
    for o in objs:
        tri+=sum(max(1,len(poly.vertices)-2) for poly in o.data.polygons)
        verts+=len(o.data.vertices)
        for corner in o.bound_box:
            xyz=o.matrix_world@Vector(corner)
            for i in range(3):
                p=xyz[i]
                if not math.isfinite(p):nonfinite+=1
                else:
                    minv[i]=min(minv[i],p)
                    maxv[i]=max(maxv[i],p)
    assert nonfinite==0 and tri>=20 and all(math.isfinite(x) for x in minv+maxv)
    d=[maxv[i]-minv[i] for i in range(3)]
    assert max(d)>50, (c["id"],d)
    center=[(minv[i]+maxv[i])/2 for i in range(3)]
    # Keep original native GLB vertices untouched (camera and neutral shading only).
    before_checks={o.name:hashlib.sha256("".join(
        "%0.5f,%0.5f,%0.5f;"%tuple(v.co) for v in o.data.vertices
       ).encode()).hexdigest() for o in objs}
    cam=cameras_for_bounds(*center,d)
    scene=bpy.context.scene
    scene.render.engine="BLENDER_WORKBENCH"
    scene.display.shading.light="STUDIO"
    scene.display.shading.color_type="SINGLE"
    scene.display.shading.single_color=(.71,.72,.72)
    scene.display.shading.show_cavity=True
    scene.display.shading.cavity_type="BOTH"
    scene.render.resolution_x=960
    scene.render.resolution_y=640
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG"
    scene["R10_source_model"]=c["model"]
    scene["R10_source_GLB_sha256"]=orig_hash
    scene["R10_canonical_art_adopted"]=False
    scene["R10_comparison_not_same_real_scale"]=True
    scene["R10_original_geometry_modified"]=False
    scene["R10_status"]=c["status"]
    rowfiles={}
    for n,o in cam.items():
        scene.camera=o
        path=P/(c["id"]+"_"+n+".png")
        scene.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)
        rowfiles[n]=path.name
        renders.append(path.name)
    assert before_checks=={o.name:hashlib.sha256("".join(
       "%0.5f,%0.5f,%0.5f;"%tuple(v.co) for v in o.data.vertices
       ).encode()).hexdigest() for o in objs}
    blend=P/(c["id"]+"_ORIGINAL_GLB_IMPORTED_CAMERAS.blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    rendered={
      "id":c["id"],"author_ref":c["ref"],"source_model_path":c["model"],
      "source_model_sha256":orig_hash,
      "original_preview_path":c["photo"],
      "original_preview_sha256":hashlib.sha256((S/c["photo"]).read_bytes()).hexdigest(),
      "review_source_path":c["decision"],
      "review_source_sha256":hashlib.sha256((S/c["decision"]).read_bytes()).hexdigest(),
      "original_art_state":c["status"],"source_review_risk":c["risk"],
      "mesh_objects":len(objs),"triangulated_faces":tri,"mesh_vertices":verts,
      "bound_min_m":minv,"bound_max_m":maxv,"bound_span_m":d,
      "orthographic_views_normalized_to_own_bound":rowfiles,
      "true_native_blend_from_original_glb_plus_camera":blend.name,
      "geometry_vertex_hashes_unchanged":True,
      "formal_city_master_complete":False,"art_adopted":False
    }
    study.append(rendered)
    print("R10_VERIFIED_GLTF_AND_NATIVE",rendered["id"],rendered["mesh_objects"],
          rendered["triangulated_faces"],rendered["bound_span_m"],flush=True)

# Contact sheet: four normalized directions plus SOURCE PREVIEW from
# the original authors. Explicit mismatch: preview may show other scenes.
WIDTH,HEIGHT=550,355
pad=14;head=58;rowh=HEIGHT+92
board=Image.new("RGB",(5*WIDTH,head+4*rowh+85),(240,243,245))
draw=ImageDraw.Draw(board)
try:
    font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",20)
    small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",16)
except OSError:
    font=ImageFont.load_default();small=font
draw.text((20,12),"HALO-9 R10 | Existing GLB evidence | neutral cameras | NOT 1:1 real scale",font=font,fill=(25,38,53))
columns=["FRONT", "SIDE","OBLIQUE","REAR","ORIGINAL SOURCE PREVIEW (different camera)"]
for j,name in enumerate(columns):
    draw.text((j*WIDTH+12,head-5),name,font=small,fill=(19,32,50))
for i,c in enumerate(study):
    y=head+26+i*rowh
    draw.rectangle((0,y-2,5*WIDTH,y+rowh-5),fill=(231,233,236) if i%2 else (247,247,246))
    for j,label in enumerate(("01_FRONT","02_SIDE","03_OBLIQUE","04_REAR")):
        im=Image.open(P/c["orthographic_views_normalized_to_own_bound"][label]).convert("RGB")
        im=ImageOps.contain(im,(WIDTH-18,HEIGHT-14))
        x=j*WIDTH+(WIDTH-im.width)//2
        board.paste(im,(x,y+8))
    preview_source=next(v for v in CANDIDATES if v["id"]==c["id"])["photo"]
    source_image=Image.open(S/preview_source).convert("RGB")
    source_image=ImageOps.contain(source_image,(WIDTH-18,HEIGHT-14))
    board.paste(source_image,(4*WIDTH+(WIDTH-source_image.width)//2,y+8))
    draw.text((12,y+HEIGHT+10),
       c["id"]+" | "+c["original_art_state"],font=small,fill=(20,30,43))
    label=("original source "+c["author_ref"]+" / "+str(c["mesh_objects"])+" native meshes")
    draw.text((12,y+HEIGHT+35),label,font=small,fill=(72,78,90))
board.save(P/"R10_REAL_4_CANDIDATES_UNBIASED_VIEW_ATLAS.jpg",quality=88)
manifest={
 "study":"R10 cross-lineage native evidence screen",
 "meaning":"All art statuses sourced from newer G6/G7 decisions; no candidate adopted",
 "comparison_camera_policy":"four 3D orthographic same relative directions; each source model FITS ITS OWN BOUND, absolute scale intentionally NOT comparable in pixels",
 "source_previews": "Last column uses original artistic images and original rendering conditions, not neutral cameras",
 "candidate_count":len(study),
 "candidate_states":{c["id"]:c["original_art_state"] for c in study},
 "all_canonical_original_source_glbs_untouched":True,
 "no_new_mass_generated":True,
 "10km_city_master_complete":False,
 "formal_M247C_adopted":False,"minecraft_construction":False,
 "models":study
}
(P/"R10_ORIGINAL_LINEAGE_INDEPENDENT_AUDIT.json").write_text(
    json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf8")
print("R10_FOUR_ORIGINAL_GLBS_NEUTRAL_REVIEW_COMPLETE_ART_UNAPPROVED",
      json.dumps({x["id"]:x["bound_span_m"] for x in study}))
