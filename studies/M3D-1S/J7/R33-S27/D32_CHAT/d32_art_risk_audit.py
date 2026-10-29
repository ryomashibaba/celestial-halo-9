#!/usr/bin/env python3
"""D32 fail-closed research gate. Quantitative risks, NOT algorithmic art rating.

Checks actual reloaded GLBs, their named geometry and a sample local ground route.
Do NOT infer whole-building occupancy or access from program strings in a JSON.
"""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parent


def audit(record):
    p=ROOT/record['file'];scene=trimesh.load(p,force='scene',process=False)
    geometries=scene.geometry
    tri=np.array([len(g.faces) for g in geometries.values()])
    route=geometries['rift_spine_public_floor']
    thresholds=[(k,g) for k,g in geometries.items() if k.startswith('transverse_civic_threshold_')]
    samples=[]
    # Ground corridor, sample 5 lateral tracks every 1m. This computes
    # highest public floor *box top* at each route point, not a legal clearance test.
    for y in np.arange(-639.5,709.5,1.0):
        for x in (-65,-32.5,0,32.5,65):
            # All threshold mesh outlines are rectilinear, exact AABBs at these points.
            tops=[]
            for g in [route]+[m for _,m in thresholds]:
                lo,hi=g.bounds
                if lo[0]-1e-6<=x<=hi[0]+1e-6 and lo[1]-1e-6<=y<=hi[1]+1e-6:
                    tops.append(float(hi[2]))
            samples.append((float(x),float(y),max(tops) if tops else None))
    supported=sum(z is not None for _,_,z in samples)
    by_x={float(x):[z for xx,_,z in samples if xx==x] for x in (-65,-32.5,0,32.5,65)}
    vertical_steps=[abs(b-a) for zs in by_x.values() for a,b in zip(zs,zs[1:]) if a is not None and b is not None]
    big_steps=sum(s>0.2 for s in vertical_steps)
    lines=[k for k in geometries if ('stair' in k.lower() or 'lift' in k.lower() or 'elevator' in k.lower())]
    # Mandatory art-human qualitative decision separate from structural signals.
    flags={
       'only_12_triangle_prism_components':bool(np.all(tri==12)),
       'has_no_vertical_connectors':len(lines)==0,
       'public_ground_route_has_3m_step_risk':max(vertical_steps)>2.5,
       'inhabited_room_geometry_verified':False,
       'M247C_central_art_verified':False,
       'H1_to_H6_and_SB01_to_SB16_verified':False,
    }
    return {
       'study':record['study'],'saved_glb':record['file'],'saved_glb_sha_match':record['sha256']==hashlib.sha256(p.read_bytes()).hexdigest(),
       'geometry_count':len(geometries),'triangle_count':int(sum(tri)),
       'watertight_meshes':sum(g.is_watertight for g in geometries.values()),
       'twelve_triangle_mesh_count':int(np.count_nonzero(tri==12)),
       'ground_route_samples_supported':supported,'ground_route_samples_total':len(samples),
       'max_neighboring_sample_floor_step_m':float(max(vertical_steps)),
       'number_of_floor_step_transitions_over_20cm':int(big_steps),
       'verified_vertical_connectors_count':len(lines),
       'program_labels_are_not_occupancy_evidence':True,
       'red_flag_results':flags,
       'technical_gate':'FAIL_CONTINUOUS_GROUND_WALKABILITY_NOT_CLAIMED',
       'art_gate':'REJECT_BY_8_CAMERA_VISUAL_REVIEW_NOT_BY_ALGORITHM',
       'formal_adoption':False,
       'lessons':[
         'A spatial-function name in JSON never establishes inhabitable rooms.',
         'Watertight prisms are not verified building interiors.',
         'A continuous ground slab exists, but four decorative threshold slabs create 3m steps.',
         'Upper terraces are not connected by stair/elevator in real geometry.',
         'The main silhouettes remain rectangular blocks/plates rather than a genuinely new megastructure.',
       ]
    }

if __name__=='__main__':
    records=json.loads((ROOT/'D32_GEOMETRY_EVIDENCE.json').read_text())
    results=[audit(record) for record in records]
    assert all(x['saved_glb_sha_match'] for x in results)
    assert all(x['ground_route_samples_supported']==x['ground_route_samples_total'] for x in results)
    assert all(x['max_neighboring_sample_floor_step_m']==3 for x in results)
    (ROOT/'D32_ART_RISK_AND_ROUTE_AUDIT.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps([{k:v for k,v in item.items() if k not in ('lessons','red_flag_results')} for item in results],ensure_ascii=False,indent=2))
