#!/usr/bin/env python3
"""M117 city atlas result validator, NO file write and NO construction approval.
This is NOT the scanner. Scanner source is in the user's portable M117 ZIP.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
def validate(d):
    assert d["project"]=="CELESTIAL HALO-9"
    assert d["phase"]=="M117"
    assert d["mode"]=="EXACT_SAVED_BLOCKS_READ_ONLY_REVIEW_COPY"
    assert d["world_save_folder"]=="CH9_D6D_REVIEW_COPY"
    assert d["world_role"]=="USER_VERIFIED_OLD_ARCHITECTURE_REVIEW_COPY_ONLY"
    assert d["world_writes"]==0
    assert not d["construction_approved"]
    assert not d["construction_target_registered"]
    assert d["model_H_to_world_Y"]=="UNKNOWN_NEEDS_INDEPENDENT_LANDMARK_MATCH"
    assert d["coordinates_are_real_saved_block_positions"]
    assert len(d["sites"])==16
    assert len(set(s["site"] for s in d["sites"]))==16
    assert {s["site"] for s in d["sites"]}=={f"SB{i:02d}" for i in range(1,17)}
    assert 0<=d["chunks_readable"]<=d["total_distinct_chunks_requested"]<=2500
    if d["survey_complete"]:
        assert d["chunks_readable"]==d["total_distinct_chunks_requested"]
        assert not d["errors"] and d["chunks_missing"]==0
    for s in d["sites"]:
        assert s["artificial_blocks_exact"]>=0
        assert sum(n for _,n in s["top_materials"])<=s["artificial_blocks_exact"]
        assert s["occupied_8x8_tiles"]==len(s["tiles"])
        if s["artificial_blocks_exact"]==0:
            assert s["real_world_min_artificial_y"] is None
            assert s["real_world_max_artificial_y"] is None
        else:
            assert s["real_world_min_artificial_y"]<=s["real_world_max_artificial_y"]
        assert sum(v["count"] for v in s["tiles"])==s["artificial_blocks_exact"]
        assert sum(v["count"] for v in s["y_band_counts"])==s["artificial_blocks_exact"]
    return {"status":"READ_ONLY_OUTPUT_VALIDATED",
            "full_survey":bool(d["survey_complete"]),
            "sites_with_detected_artificial_materials":sum(s["artificial_blocks_exact"]>0 for s in d["sites"]),
            "total_artificial_blocks":sum(s["artificial_blocks_exact"] for s in d["sites"]),
            "world_y_calibrated":False,"protected_geometry_certified":False,
            "construction_approved":False}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("report",type=Path);a=p.parse_args()
    print(json.dumps(validate(json.loads(a.report.read_text(encoding="utf-8"))),indent=2))
