"""Write explicit research-only handoff and latest pointer from actual QA outputs."""
from pathlib import Path
import json,sys
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
qa=json.loads((R/'qa/BLEND_GLB_READBACK.json').read_text(encoding='utf8'))
space=json.loads((R/'qa/SPATIAL_SAMPLES.json').read_text(encoding='utf8'))
floors=json.loads((R/'qa/FLOOR_VERIFIED_CAMERAS.json').read_text(encoding='utf8'))
final=qa['models']['final/R19_LIVING_HORIZON']
handoff={
 'schema':'halo9.j7r19.living_horizon.research.v1','date_jst':'2026-10-25',
 'branch':'research/m3d1s-j7-r19-living-horizon-blender-20261025',
 'base_R18_head':'dcbe2b3bdb19b1b7c500aab6b3c1ceddd0fb8bca','base_R18_pr':50,
 'verified_main_head':'a2f88995eee8d10ee4830dbdf33ccb9c0790de8f',
 'research_only':True,'art_decision':'ART_REJECT','art_improvement_goal_reached':False,
 'formal_central_art_adoptions':0,'minecraft_construction':'HOLD','city_master_complete':False,
 'name_ja':'天環地脈','name_en':'LIVING HORIZON','name_formally_adopted':False,
 'production_completed':'Real editable initial model, two macro reconstruction attempts, before/after source models and actual images, floor-verified internal views, two physical mesh sections, GLB persistence and noncanonical 10km scale scene.',
 'art_goal_not_completed':'Still reads as repeated precinct stacks / horizontal bands; side disconnected, ground underside blank; does not achieve a grand civilization continuum.',
 'initial_blend':'initial/R19_INITIAL.blend','revision_1_blend':'revision_1/R19_REVISION_1.blend',
 'revision_2_before_collar_repair':'revision_2/R19_LIVING_HORIZON.blend',
 'latest_attempt_blend':'final/R19_LIVING_HORIZON.blend','latest_attempt_glb':'final/R19_LIVING_HORIZON.glb',
 'model_geometry':final['native'],'persistence_checks':final['checks'],
 'basic_saved_geometry_readback_pass':qa['basic_persistence_pass'],'model_pairs_checked':len(qa['models']),
 'sections':['sections/XZ_Y200/XZ_Y200.blend','sections/YZ_X0/YZ_X0.blend'],
 'actual_section_source_before_camera_only_edits_retained':'qa/INITIAL_FLOATING_CAMERAS/R19_BEFORE_FLOOR_VIEWS.blend',
 'floor_verified_internal_cameras':floors['views'],
 'interior_visibility_groups':{n:v['visible_actual_target_groups'] for n,v in space['cameras'].items()},
 'free_air_connectivity_samples':space['public_air_path'],
 'human_floor_ray':space['human_floor'],
 'connected_enclosed_cavity_volume_m3':None,'void_volume_status':'UNVERIFIED',
 'traffic':'Real mesh route placements exist; grade, every junction, lifts and operation UNVERIFIED.',
 'walkability':'UNVERIFIED','all_inter_solid_collisions':'UNVERIFIED','occupancy_and_structural_safety':'UNVERIFIED',
 'R15_R17_binary_or_dimensions_reused':False,
 'foreground_computer_use':False,'live_blender_modified':False,'actual_minecraft_saves_accessed':False,
 'protected_assets_changed':False,'production_method':'Independent background Blender 5.2.1 LTS bpy, actual Cycles CPU images, actual vertex/mesh replacements, no ImageGen enhancement.',
 'cpu':'24 logical CPU machine; 5 main render threads, 3 verification render threads, 1 spatial worker; still consumes CPU.',
 'mcp':'Connected, addon protocol 5 vs expected 15; live R13 inspected read-only at start and close.',
 'context':'context/R19_NONCANONICAL_10KM.blend','official_alignment':'UNVERIFIED','W0_H_SB_integrated':False,
 'protected_obligations_retained':['W0','HALO-9 / CELESTIAL SPINE','H1-H6','SB01-SB16','HERO4','three metropolitan axes','V1-V3','M247-C research direction','Freeze and original models'],
 'report':'R19_ART_REVIEW_JA.md','comparison':'qa/FORM_COMPARISON.jpg','all_directions':'qa/FINAL_SIX.jpg','interiors':'qa/INTERIOR_VIEWS.jpg',
 'source_pipeline':['atelier.py','revise_landform.py','compose_worlds.py','floor_views.py'],
 'qa':['qa/BLEND_GLB_READBACK.json','qa/SPATIAL_SAMPLES.json','qa/FLOOR_VERIFIED_CAMERAS.json','qa/ACTUAL_SECTIONS.json','qa/OFFLINE_PACKAGE_CHECK.json'],
 'source_iteration_limits':'The generator grammar is still two main families, path-bank and court-section. Vertex shearing and shared grounds did not resolve the visual repetition.',
 'next_priority':'Do not decorate/adopt this rejected arrangement. Replace the repeated section grammar, design genuinely different contiguous city terrains and independent public skies from real 3D sections, with side/underside equally primary in first art review.',
 'next_stage':'J7-R20; not started',
 'github_delivery':'PENDING_NEW_DRAFT_RESEARCH_PR', 'draft_pr_url':None,'artifact_commit':None,
}
(R/'R19_HANDOFF.json').write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
latest={'schema':'halo9.research.latest.v1','research_id':'M3D-1S/J7-R19','date_jst':'2026-10-25',
 'status':'REAL_BLENDER_CITY_LANDFORM_AND_TWO_MACRO_RECONSTRUCTIONS_SAVED__ART_REJECT',
 'research_branch':handoff['branch'],'approval':'RESEARCH_ONLY','canonical_adoption':'NONE','construction':'HOLD',
 'formal_central_art_adopted':0,'city_master_complete':False,'official_alignment':'UNVERIFIED',
 'art_decision':'ART_REJECT','art_goal_reached':False,'work_status':'LOCAL_BACKGROUND_BLENDER_EXECUTED_NO_FOREGROUND_COMPUTER_USE',
 'outputs':{'report':'studies/M3D-1S/J7/R19/R19_ART_REVIEW_JA.md','handoff':'studies/M3D-1S/J7/R19/R19_HANDOFF.json',
 'current_new_blend':'studies/M3D-1S/J7/R19/final/R19_LIVING_HORIZON.blend',
 'current_new_glb':'studies/M3D-1S/J7/R19/final/R19_LIVING_HORIZON.glb',
 'comparison':'studies/M3D-1S/J7/R19/qa/FORM_COMPARISON.jpg','all_directions':'studies/M3D-1S/J7/R19/qa/FINAL_SIX.jpg'},
 'previous_pointer':{'research_id':'M3D-1S/J7-R18','branch':'research/m3d1s-j7-r18-civilization-landscape-art-20261025','head':handoff['base_R18_head'],'pr':50,'new_3d':False},
 'R15_R17_still_rejected':True,'next_priority':handoff['next_priority'],'next_stage':'J7-R20_NOT_STARTED',
 'draft_pr_url':None,'artifact_commit':None,'github_readback_all_files_match':None}
(R.parents[1]/'latest.json').write_text(json.dumps(latest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Wrote research-only R19 handoff and latest pointer. Art goal remains unmet.')
