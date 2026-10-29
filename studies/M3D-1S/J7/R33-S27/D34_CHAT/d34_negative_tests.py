#!/usr/bin/env python3
"""Physically mutate isolated test GLBs and verify that readback QA catches the defect."""
from pathlib import Path
import json,hashlib
import trimesh
from d34_independent_qa import verify
OUT=Path(__file__).parent
source=OUT/'D34_CIVIC_THREE_LEVEL_REAL.glb'
orig=trimesh.load(source,force='scene',process=False)
# The obstruction extends from Z=4.6 to Z=9; RAMP_WEST center Z=4, head is 5.7.
obstruct=trimesh.creation.box(extents=(10,10,4.4));obstruct.apply_translation((-160,-90,6.8))
obscene=orig.copy();obscene.add_geometry(obstruct,geom_name='OBSTACLE_INJECTED',node_name='OBSTACLE_INJECTED')
po=OUT/'D34_NEGATIVE_OBSTACLE.glb';po.write_bytes(trimesh.exchange.gltf.export_glb(obscene))
# Real obstruction filling the central G1 front doorway, detected by doorway test.
seal=trimesh.creation.box(extents=(20,2.0,8.0));seal.apply_translation((-80,-113.7,12))
sealed=orig.copy();sealed.add_geometry(seal,geom_name='G1_sealed_portal',node_name='G1_sealed_portal')
ps=OUT/'D34_NEGATIVE_SEALED_PORTAL.glb';ps.write_bytes(trimesh.exchange.gltf.export_glb(sealed))
# Separate no-ramp actual GLB (not merely simulated exclusion)
no=trimesh.Scene()
for name,m in orig.geometry.items():
 if name!='RAMP_WEST':no.add_geometry(m.copy(),geom_name=name,node_name=name)
pn=OUT/'D34_NEGATIVE_MISSING_RAMP.glb';pn.write_bytes(trimesh.exchange.gltf.export_glb(no))
positive=verify(source); obstacle=verify(po); missing=verify(pn); sealed_result=verify(ps)
assert positive['tech_pass_limited']
assert obstacle['head_collisions']>0 and not obstacle['tech_pass_limited']
assert missing['missing_support']>=505 and not missing['tech_pass_limited']
assert sealed_result['door_probes']['G1']['blocked']>0 and not sealed_result['tech_pass_limited']
results={'original_glb_sha256':positive['sha256'],
'obstruction_glb_sha256':obstacle['sha256'],'obstruction_head_collision_detections':obstacle['head_collisions'],
'missing_ramp_glb_sha256':missing['sha256'],'removed_ramp_support_failures':missing['missing_support'],
'sealed_portal_glb_sha256':sealed_result['sha256'],'sealed_G1_doorway_failures':sealed_result['door_probes']['G1']['blocked'],
'positive_pass':positive['tech_pass_limited'],'negative_obstruction_detected':not obstacle['tech_pass_limited'],
'negative_missing_ramp_detected':not missing['tech_pass_limited'],
'negative_sealed_portal_detected':not sealed_result['tech_pass_limited']}
(OUT/'D34_NEGATIVE_QA.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
