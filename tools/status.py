#!/usr/bin/env python3
"""Transparent offline project status, not a progress counter."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=json.loads((ROOT/'governance/project_policy.json').read_text(encoding='utf-8'))
    g=json.loads((ROOT/'governance/release_gate.json').read_text(encoding='utf-8'))
    print(json.dumps({
        'project':p['project'],
        'comparison_baseline':p['design_comparison_baseline'],
        'candidate_status':p['candidate_status'],
        'construction_status':p['construction_status'],
        'live_world_write':g['world_write_enabled'],
        'world_absolute_y_verified':g['minecraft_absolute_y_verified'],
        'current_repo_status':'Initial M108 remote CI and governance bootstrap; full M107 per-file manifest migration pending',
        'new_city_completion_claim':'NONE'
    },indent=2,ensure_ascii=False))
if __name__=='__main__':main()
