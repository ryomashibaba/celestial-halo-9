#!/usr/bin/env python3
"""M118 data conservation test, no world access or writes."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def check():
 s=json.loads((ROOT/"survey/reports/M118_REAL_CITY_SUMMARY.json").read_text())
 p=json.loads((ROOT/"design/drafts/M118_WHOLE_CITY_REGENERATION_CHOICES.json").read_text())
 assert s["world_save_folder"]=="CH9_D6D_REVIEW_COPY"
 assert s["chunks_readable"]==s["chunks_requested"]==1456
 assert s["chunks_missing"]==s["report_errors"]==0
 assert s["sites_count"]==len(s["site_samples"])==16
 assert len({x["site"] for x in s["site_samples"]})==16
 assert sum(x["blocks"] for x in s["site_samples"])==s["total_heuristic_artificial_material_blocks"]==1095343
 assert sum(x["tiles"] for x in s["site_samples"])==s["occupied_8x8_tiles"]==2096
 assert sum(s["site_group_blocks"].values())==sum(s["material_counts"].values())==1095343
 assert s["min_saved_artificial_block_Y"]==min(x["min_saved_Y"] for x in s["site_samples"])==-1865
 assert s["max_saved_artificial_block_Y"]==max(x["max_saved_Y"] for x in s["site_samples"])==-1703
 assert set(p["protected_legacy_objects"])>=set(["Freeze408","SB13 minimum 3x4 entrance"])
 assert len(p["alternatives"])==2
 assert all(not s[k] for k in ("actual_frozen_protection_classified","masterplans_approved","verified_buildability","construction_target_approved","M101_formal_baseline_promotion"))
 assert not p["formal_design_choice_approved"]
 assert p["unresolved_protection_classification"]
 assert p["world_writes"]==s["world_writes"]==0
 assert s["model_H_to_world_Y"]=="UNVERIFIED"
 assert p["baseline_promotion"] is False
 return True
if __name__=="__main__":assert check();print("M118 RESEARCH CONSERVATION PASS; NO CONSTRUCTION")
