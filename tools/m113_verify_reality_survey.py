#!/usr/bin/env python3
"""M113: validate offline observation reports, no Minecraft access or writes."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def check_grounded(d):
    assert d['project']=='CELESTIAL HALO-9'
    assert d['world_candidate']=='imagine'
    assert d['screenshot']['x']==3885.4 and d['screenshot']['z']==-2405.0
    assert d['screenshot']['camera_y']==-1587.1
    assert d['screenshot']['camera_y_is_not_building_ground_or_roof_height']
    assert d['screenshot_chunk']['cx']==242 and d['screenshot_chunk']['cz']==-151
    assert d['screenshot_chunk']['status']=='minecraft:full'
    s=d['m112_readonly_survey']
    assert s['chunk_records']==3434 and s['errors']==0
    assert s['full']+s['structure_starts']+s['structure_references']==s['chunk_records']
    assert d['model_parcels']['facility_count']==16
    assert d['model_parcels']['full_chunk_coverage_facilities']==16
    assert not d['world_identity_proven_unique']
    assert not d['actual_minecraft_y_ground_verified']
    assert d['model_relative_h_to_world_absolute_y']=='UNKNOWN'
    assert d['world_writes']==0 and d['no_authorized_world_construction']
    return True
def check_new_probe(d):
    assert d['project']=='CELESTIAL HALO-9'
    assert d['mode']=='READ_ONLY_PROBED_BLOCK_COLUMNS'
    assert d['world_write_operations']==0 and not d['construction_approved']
    assert d['probes_requested']==49
    assert d['model_relative_H_to_actual_world_Y']=='UNVERIFIED'
    assert not d['full_protected_volume_and_building_geometry_verified']
    assert not d['no_player_data_collected'] is False
    assert d['raw_world_path_not_exported']
    p=d['probes']
    assert d['probes_reported']==len(p)
    assert len(p)<=49
    assert all('min_solid_y' in x and 'max_solid_y' in x for x in p)
    # A sampled column cannot guarantee a full building exists.
    return {'probes_reported':len(p),'site_labels_observed':sorted({x['site'] for x in p if x['site'].startswith('SB')}),
            'has_screenshot_sample':any(x['label']=='M113_SCREENSHOT_POINT' for x in p),
            'model_to_world_height_registration':'UNVERIFIED'}
if __name__=='__main__':
    evidence=json.loads((ROOT/'survey/reports/M113_ACTUAL_WORLD_EVIDENCE.json').read_text(encoding='utf8'))
    assert check_grounded(evidence)
    if len(sys.argv)>1:
        report=json.loads(Path(sys.argv[1]).read_text(encoding='utf8'))
        print(json.dumps(check_new_probe(report),indent=2))
    else:
        print('M113 GROUNDING PASS, NO WORLD WRITES, HEIGHT OFFSET UNKNOWN')
