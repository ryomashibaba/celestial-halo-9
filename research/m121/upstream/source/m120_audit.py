#!/usr/bin/env python3
"""Conservative research-only clearance flags, never exact voxel collision certification."""
import json,math,hashlib,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m120_city_model import produce_m120,ATLAS,ROOT

def analyze(m):
    assert m['phase']=='M120' and m['world_writes']==0
    new=m['meshes'][m['new_meshes_start_index']:]
    old=[(s['site'],t) for s in ATLAS['sites'] for t in s['tiles']]
    at_risk=set(); hits=0; with_tile_overlap=[]; without_tile_overlap=[]
    for block in new:
        mesh_hits=0
        vv=block['v'];xmin=min(x[0] for x in vv);xmax=max(x[0] for x in vv)
        zmin=min(x[1] for x in vv);zmax=max(x[1] for x in vv)
        ymin=min(x[2] for x in vv);ymax=max(x[2] for x in vv)
        for id,t in old:
            if xmax<t['x'] or xmin>t['x']+8 or zmax<t['z'] or zmin>t['z']+8:continue
            if ymax<t['min_y'] or ymin>t['max_y']:continue
            hits+=1;mesh_hits+=1;at_risk.add((id,t['x'],t['z']))
        (with_tile_overlap if mesh_hits else without_tile_overlap).append(block['id'])
    route=m['public_route_concept']
    return {
      'phase':'M120','status':'OFFLINE_BROADPHASE_ONLY_NO_CONSTRUCTION',
      'source_review_copy':'CH9_D6D_REVIEW_COPY','site_material_8x8_tiles':sum(len(s['tiles']) for s in ATLAS['sites']),
      'inherited_m119_B_meshes':m['original_M119_mesh_count'],
      'm120_new_meshes':m['m120_added_meshes'],'total_proxy_meshes':len(m['meshes']),
      'new_geometry_versus_observed_8x8_tile_Y_AABB_potential_hits':hits,
      'distinct_old_tiles_potentially_overlapped':len(at_risk),
      'new_proposal_meshes_with_observed_tile_AABB_risk':len(with_tile_overlap),
      'new_proposal_meshes_without_observed_tile_AABB_risk':len(without_tile_overlap),
      'risky_mesh_id_sample':with_tile_overlap[:16],
      'potentially_overlapped_site_ids':sorted({sid for sid,x,z in at_risk}),
      'route_segment_count':len(route['segments']),
      'route_station_count':len(route['stations']),
      'route_math_centerline_continuous':True,
      'route_old_material_tile_broadphase_risks':[{'id':r['id'],'risk_tiles':r['observed_material_tile_AABB_risks']} for r in route['segments']],
      'exact_old_voxel_collision_check':False,'protected_reserved_88_voids_checked':False,
      'SB13_actual_protected_entry_coordinates_verified':False,
      'full_frozen408_world_voxel_map_verified':False,
      'existing_approved_roads_and_parks_checked':False,
      'outer_ring_planning_extent_approved':False,
      'elevator_and_lift_operational':False,
      'pedestrian_traversable':False,
      'model_relative_H_to_world_Y_verified':False,
      'comparison_baseline_promoted':False,
      'official_live_world_registered':False,
      'world_writes':0,
      'interpretation':'New proposal intersects old observed region in conservative tiles, NOT permissions to erase or modify frozen buildings; 0 hit does not mean full clearance.'
    }

if __name__=='__main__':
    m=produce_m120();o=analyze(m)
    dest=ROOT/'data/M120_NONCONSTRUCTION_AUDIT.json'
    dest.write_text(json.dumps(o,indent=2),encoding='utf8')
    print(json.dumps({k:o[k] for k in ('m120_new_meshes','route_segment_count','new_geometry_versus_observed_8x8_tile_Y_AABB_potential_hits','distinct_old_tiles_potentially_overlapped')},indent=2))
