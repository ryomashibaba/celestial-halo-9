"""Evidence-only D48 citywide scope checks. Never asserts artwork quality.
No Blender/MC dependency; no world write. Intended for the research branch.
"""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
manifest = json.loads((HERE / "D48_R0_CITY_SCOPE_PROVENANCE.json").read_text(encoding="utf-8"))
art = (HERE / "D48_R0_ART_DIRECTION_JA.md").read_text(encoding="utf-8")
ids = [a["id"] for a in manifest["assets"]]

expected = (
    {"M247-C", "W0"}
    | {f"H{i}" for i in range(1, 7)}
    | {f"SB{i:02d}" for i in range(1, 17)}
    | {f"V{i}" for i in range(1, 4)}
    | {f"METRO_AXIS_{i}" for i in range(1, 4)}
)
assert len(ids) == 30 and len(set(ids)) == 30 and set(ids) == expected
assert {a["id"] for a in manifest["assets"] if a.get("hero4") is True} == {
    "SB05", "SB08", "SB09", "SB12"
}
assert manifest["source_main_head"] == "a2f88995eee8d10ee4830dbdf33ccb9c0790de8f"
assert manifest["source_e6_head"] == "8802d31996b8f90907287b52da1ba11300a682bc"
assert manifest["coordinate_policy"]["M204_to_W0_M207_common_anchor_count_certified"] == 0
assert manifest["coordinate_policy"]["model_relative_H_to_minecraft_Y"] == "UNKNOWN"
assert manifest["coordinate_policy"]["official_origin_xyz_m"] is None
assert manifest["city_master_3d_complete"] is False
assert manifest["minecraft_construction"] == "HOLD"
assert manifest["formal_design_choice_approved"] is False
assert manifest["allowed_final_simplification"] == [
    "PRIVATE_INTERIORS_OF_ORDINARY_BUILDINGS_ONLY"
]
for a in manifest["assets"]:
    assert a["formal_position_xyz_m"] is None, a["id"]
    assert a["formal_dimensions_xyz_m"] is None, a["id"]
    assert a["model_relative_to_world_transform"] is None, a["id"]
    assert a["geometry_file"] is None, a["id"]
    assert a["linked_3d_asset"] is None, a["id"]
    assert a["formal_adoption"] is False and a["minecraft_write"] is False, a["id"]
    assert a["art"] == "UNREVIEWED", a["id"]
for item in ("A《地層を貫く光都》", "B《双殻を縫う都市潮流》",
             "C《静謐な浮断群島都市》", "V01", "V09",
             "R0は文章による設計研究", "E6"):
    assert item in art, item
assert len(manifest["mandatory_gates"]) >= 9
assert len(manifest["unmodeled_completion_duties"]) >= 7
print(json.dumps({
    "result": "SCOPE_AND_PROVENANCE_CHECKS_PASS_ONLY",
    "registered_entities": len(ids),
    "art_quality": "NOT_TESTED",
    "genuine_3d": "NOT_CREATED_IN_R0",
    "formal_adoption": False,
    "minecraft_write": False,
}, ensure_ascii=False, indent=2))
