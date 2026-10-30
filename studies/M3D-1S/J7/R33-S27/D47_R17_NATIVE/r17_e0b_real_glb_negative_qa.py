"""R17 E0B independent NEGATIVE topology/functional gate.

Audits the real archived GLB, not the generation script's favorable labels.
Its result is expected FAIL for certified circulation even though Blender
generation/source-shape readback is TECH PASS. The 168 disconnected stair
tread quad components must NEVER be called a structurally continuous stair.

This script does NOT edit source city geometry, main, or Minecraft.
"""
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import hashlib,json,sys
import trimesh
from shapely.geometry import MultiPoint
repo=Path(sys.argv[1]).resolve()
out=Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=True)
archive=repo/"studies/M3D-1S/J7/R33-S27/D47_R17_EVIDENCE/R17_E0_REAL_INHABITED_CITY_SECTION_10_VIEW_G0_ART_UNREVIEWED.zip"
hashfile=archive.parent/"R17_E0_EVIDENCE_SHA256.json"
h=json.loads(hashfile.read_text())
assert hashlib.sha256(archive.read_bytes()).hexdigest()==h["zip_sha256"]
with ZipFile(archive) as z:
    glb=z.read("R17_E0_PUBLIC_FORUM_CITY_SECTION.glb")
    manifest=json.loads(z.read("R17_E0_TRUE_3D_MANIFEST.json"))
assert manifest["real_stair_treads"]==168
scene=trimesh.load(BytesIO(glb),file_type="glb",force="scene")
names=list(scene.graph.nodes_geometry)
assert len(names)==manifest["real_mesh_count"]
def find(prefix):
    rows=[n for n in names if n.startswith(prefix)]
    assert len(rows)==1,(prefix,rows)
    transform,g=scene.graph[rows[0]]
    return rows[0],scene.geometry[g],transform
name,stair,T=find("168_ACTUAL_SINGLE_CONNECTED_STAIR_TREADS")
components=stair.split(only_watertight=False)
assert len(components)==168,(len(components),"Expected independent flat quads")
assert len(stair.faces)==336,(len(stair.faces),"168 source quads imported as 336 triangles")
assert not stair.is_watertight
real_decks=[n for n in names if "INHABITED_DECK" in n]
assert len(real_decks)==15
assert not any("STAIR_RISER" in n or "GUARDRAIL" in n or "ELEVATOR" in n for n in names)
_,court,courtTf=find("OPEN_TO_SKY_PUBLIC_COMMONS_WHOLE_FLOOR")
_,entry,entryTf=find("CITY_FRONT_ENTRY_STREET_TO_COURT")
# glTF is Y-up; XZ is the horizontal plane after GLB export.
def top_plan(mesh,transform):
    p=trimesh.transform_points(mesh.vertices,transform)
    h=max(p[:,1]);projected=[(q[0],q[2]) for q in p if h-q[1]<.015]
    assert len(projected)>=4,len(projected)
    poly=MultiPoint(projected).convex_hull
    assert poly.geom_type=="Polygon" and poly.area>5
    return poly
c=top_plan(court,courtTf);e=top_plan(entry,entryTf)
intersection=c.intersection(e)
assert intersection.area>1
report={
 "research_stage":"R17 E0B",
 "geometric_source_sha256":h["files_sha256"]["R17_E0_PUBLIC_FORUM_CITY_SECTION.glb"],
 "signed_source_archive_sha256":h["zip_sha256"],
 "independent_library":"trimesh + shapely, GLB scene geometry and transforms",
 "source_generation":{"status":"TECH_LIMITED_PASS",
     "editable_native_3D":True,
     "floor_decks_confirmed":len(real_decks),
     "ten_views_source_verified_in_previous_GitHub_CI":True},
 "architectural_functional_negative_gate":{
     "status":"FAIL",
     "stair_source_mesh_name":name,
     "claimed_tread_count":168,
     "actual_disconnected_stair_components":len(components),
     "triangles":len(stair.faces),
     "stair_mesh_watertight":False,
     "separate_riser_geometry_found":False,
     "guardrails_found":False,
     "lift_to_unserved_levels_found":False,
     "ground_entry_court_real_overlap_area_square_m":round(intersection.area,3),
     "entry_ground_overlap_exists":True,
     "room_to_room_public_access_certified":False,
     "stairs_continuous_loadbearing_structure_certified":False,
     "upper_levels_accessibility_certified":False,
     "corrective_note":"The named one-object stair is 168 disconnected tread quads. Do NOT call it structurally connected. At least all unserved upper tiers remain uncertified."
 },
 "visual_10_view_human_review":"ART REJECT: parking garage/arena-like repetitive gallery, generic massing, neither α/β nor high-city culture legible",
 "formal_city_master_approved":False,
 "minecraft_write":False
}
target=out/"R17_E0B_INDEPENDENT_FUNCTIONAL_NEGATIVE_AUDIT.json"
target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
print("R17_E0B_REPRODUCED_FUNCTIONAL_NEGATIVE_GATE",report["architectural_functional_negative_gate"])
