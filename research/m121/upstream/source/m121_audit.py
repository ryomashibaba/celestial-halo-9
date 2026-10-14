#!/usr/bin/env python3
"""M121 8x8-tile broadphase triage with deliberately UNKNOWN protection.
Data is a M117 user-provided exact-material aggregate, NOT exact protected voxel mesh.
"""
from __future__ import annotations
import sys,json
from collections import Counter,defaultdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from m121_city_experience import build_experience,ATLAS,ROOT
from m120_audit import analyze as m120_analyze


def risk_scan(objects):
    tiles=[(s['site'],t) for s in ATLAS['sites'] for t in s['tiles']]
    rows=[];by_site=Counter();risk_tiles=set();candidate_pairs=0
    for o in objects:
        verts=o['v'];minx=min(p[0] for p in verts);maxx=max(p[0] for p in verts)
        minz=min(p[1] for p in verts);maxz=max(p[1] for p in verts)
        miny=min(p[2] for p in verts);maxy=max(p[2] for p in verts)
        hits=[]
        for sid,t in tiles:
            if maxx<t['x'] or minx>t['x']+8 or maxz<t['z'] or minz>t['z']+8:continue
            if maxy<t['min_y'] or miny>t['max_y']:continue
            hits.append((sid,t['x'],t['z']))
        candidate_pairs+=len(hits);risk_tiles.update(hits)
        for sid,x,z in hits:by_site[sid]+=1
        rows.append({'mesh_id':o['id'],'site_label':o.get('site'),
          'm117_material_tile_potential_overlap':bool(hits),'overlap_pair_count':len(hits),
          'touched_sites':sorted(set(t[0] for t in hits)),
          'risk':'OBSERVED_OLD_MATERIAL_TILE_POTENTIAL_CONTACT' if hits else 'NO_HIT_IN_LIMITED_M117_SCREEN',
          'protected_Freeze408_or_S_B_reserved_voxel_classification':'UNKNOWN',
          'automatic_demolition_allowed':False,'automatic_construction_allowed':False})
    return {'proposals_scanned':len(objects),
       'potential_old_material_overlap_meshes':sum(r['m117_material_tile_potential_overlap'] for r in rows),
       'no_observed_tile_overlap_meshes':sum(not r['m117_material_tile_potential_overlap'] for r in rows),
       'potential_mesh_tile_overlap_pairs':candidate_pairs,
       'distinct_8x8_material_tiles_potentially_touched':len(risk_tiles),
       'potential_overlap_pairs_by_site':dict(sorted(by_site.items())),
       'rows':rows}


def audit_m121(model):
    m120_start=model['new_meshes_start_index']
    m121_start=model['m121_meshes_start_index']
    # Separate inherited 130 M120 meshes from this M121 patch.
    before=risk_scan(model['meshes'][m120_start:m121_start])
    current=risk_scan(model['meshes'][m121_start:])
    # An exact protected mask has NOT been imported. No 38 legacy overlaps can be
    # classified as ALTERABLE or LOCKED based on material tile alone.
    assert before['proposals_scanned']==130
    assert before['potential_old_material_overlap_meshes']==38
    assert before['distinct_8x8_material_tiles_potentially_touched']==600
    assert before['potential_mesh_tile_overlap_pairs']==1204
    return {'phase':'M121','status':'PROPOSAL_GEOMETRY_OVERLAP_TRIAGE_ONLY',
      'surveyed_world':'CH9_D6D_REVIEW_COPY_USER_CONFIRMED_READ_ONLY',
      'observed_actual_material_blocks':1095343,
      'observed_8x8_tile_count':2096,
      'M120_inherited_overlap_triage':before,
      'M121_new_mesh_overlap_triage':current,
      'categorization':{
        'LOCKED_proven_count':0,'DESIGNABLE_proven_count':0,
        'UNKNOWN_classification_count_M120':130,'UNKNOWN_classification_count_M121':current['proposals_scanned'],
        'important':'0 proven locked does NOT mean none locked; protected exact voxel masks unavailable'
      },
      'protected_source_masks_loaded':False,
      'historical_reserved_88_voids_screened':False,
      'approved_roads_and_parks_3D_screened':False,
      'actual_SB13_entrance_anchored':False,
      'model_relative_H_to_world_Y_matched':False,
      'public_walk_route_fully_traversable':False,
      'user_approved_construction_world':None,
      'M101_baseline_promoted':False,'construction_approved':False,'world_writes':0,
      'interpretation':'Every mesh is conceptual replacement-like research; no deletion, world writes or approval.'}

if __name__=='__main__':
    model=build_experience();summary=audit_m121(model)
    output=ROOT/'data/M121_TILE_RISK_TRIAGE.json'
    output.write_text(json.dumps(summary,indent=2),encoding='utf8')
    s=summary['M121_new_mesh_overlap_triage']
    print(json.dumps({k:s[k] for k in ('proposals_scanned','potential_old_material_overlap_meshes','no_observed_tile_overlap_meshes','potential_mesh_tile_overlap_pairs')},indent=2))
