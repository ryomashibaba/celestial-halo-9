#!/usr/bin/env python3
"""Offline decision gate. NO Minecraft integration and NO write path."""
def check(*, formal_world_registered=False, world_transform_approved=False,
          exact_protection_voxels_loaded=False, canonical_design_approved=False,
          written_construction_authorization=False, real_world_backup_verified=False):
    conditions = {
        "formal_world_registered": formal_world_registered,
        "world_transform_approved": world_transform_approved,
        "exact_protection_voxels_loaded": exact_protection_voxels_loaded,
        "canonical_design_approved": canonical_design_approved,
        "written_construction_authorization": written_construction_authorization,
        "real_world_backup_verified": real_world_backup_verified,
    }
    return {"state": "HOLD", "can_write": False, "missing": [k for k,v in conditions.items() if v is not True],
            "reason":"M149 does not implement world writes and cannot promote research to construction."}
if __name__ == "__main__":
    import json
    print(json.dumps(check(), indent=2))
