#!/usr/bin/env python3
"""Offline fail-closed policy guard. No world-write capability."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def load(n):
    return json.loads((ROOT/'governance'/n).read_text(encoding='utf-8'))
def check():
    p=load('project_policy.json')
    g=load('release_gate.json')
    r=load('protected_registry.json')
    assert p['project']=='CELESTIAL HALO-9'
    assert p['project_guiding_priorities']==['NO_DIRECTION_DRIFT','MAXIMUM_EFFICIENT_PROGRESS']
    assert set(p['locked_design_principles'])==set(('urban_form','colors','density','redesign','interiors','construction','world','experience'))
    assert p['construction_status']=='HOLD'
    assert p['world_status']=='NOT_VERIFIED'
    assert p['design_comparison_baseline']=='M101_TERRACED_DISTRICT_RIM'
    assert p['authorization']['no_automatic_merge_of_baseline_prs'] is True
    assert {'formal_design_baseline_change','live_world_construction','freeze_change','repository_governance_change'} <= set(p['authorization']['requires_explicit_user_approval'])
    assert g['release_state']=='BLOCKED_UNTIL_SEPARATE_USER_APPROVAL'
    assert g['approved_pilot_region'] is None
    assert all(g[k] is False for k in ('world_write_enabled','construction_approved','freeze_write_enabled','canonical_write_enabled','staging_write_enabled','minecraft_absolute_y_verified','registered_live_world_snapshot','deployment_workflow_present'))
    assert r['construction_ready'] is False
    assert r['coordinate_system']['minecraft_absolute_y']=='UNKNOWN'
    assert r['protection_source_status']=='METADATA_ONLY_REQUIRES_EXACT_GEOMETRY_IMPORT'
    assert sum(map(len,r['sites'].values()))==16
    for k in ('Freeze408','public_existing_meshes_959','M81_H0_pier_proxies_91','SB09_UPPER_GATE_WALL','SB13_entry_width3_height4'):
        assert r['preserved_objects'][k]=='LOCKED'
    flows=list((ROOT/'.github/workflows').glob('*.yml'))+list((ROOT/'.github/workflows').glob('*.yaml'))
    assert len(flows)==1
    for f in flows:
        s=f.read_text().lower()
        assert all(t not in s for t in ('pull_request_target:', 'workflow_run:', 'worldedit paste', 'minecraft-deploy'))
    return True
if __name__=='__main__':
    assert check()
    print('HALO9 POLICY PASS — NO LIVE WORLD ACCESS, CONSTRUCTION HOLD')
