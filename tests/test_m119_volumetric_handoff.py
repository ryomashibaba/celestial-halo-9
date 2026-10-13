import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'design/drafts/M119_GROUNDED_VOLUMETRIC_HANDOFF.json'
class M119ProposalHandoff(unittest.TestCase):
 def test_grounded_summary_no_fake_approval(self):
  d=json.loads(P.read_text())
  self.assertEqual(d['actual_built_materials_heuristic'],1095343)
  self.assertEqual(d['observed_8x8_tiles'],2096)
  self.assertEqual(d['reference_review_save'],'CH9_D6D_REVIEW_COPY')
  self.assertEqual(d['actual_saved_material_y_range'],[-1865,-1703])
  self.assertEqual(len(d['draft_schemes']),2)
  self.assertEqual(set(d['site_architecture_program']),{'HERO4','CIVIC4','FRAME8'})
  self.assertEqual([len(v) for v in d['site_architecture_program'].values()],[4,4,8])
  self.assertEqual([s['proposal_meshes'] for s in d['draft_schemes']],[648,603])
  self.assertEqual([s['proposed_voids'] for s in d['draft_schemes']],[9,10])
  self.assertTrue(d['b_research_priority_only'])
  self.assertFalse(d['official_architecture_approval'])
  self.assertFalse(d['protected_geometry_clearance_tested'])
  self.assertFalse(d['traversal_certified'])
  self.assertFalse(d['source_bundle_files_in_github'])
  self.assertEqual(d['governance']['world_writes'],0)
  self.assertIsNone(d['governance']['official_construction_world_id'])
 def test_sources_immutable_and_not_buildable(self):
  d=json.loads(P.read_text())
  self.assertTrue(all(len(x['full_model_sha256'])==64 for x in d['draft_schemes']))
  self.assertTrue(all(x['public_route_intents']==24 for x in d['draft_schemes']))
  self.assertFalse(d['elevator_functional'])
  self.assertFalse(d['giant_outer_ring_planning_boundary_confirmed'])
  self.assertEqual(d['world_y_note'].split(',')[0].startswith('New proposal uses surveyed Minecraft coordinate frame'),True)
  self.assertFalse(d['governance']['comparison_baseline_promotion'])
if __name__=='__main__':unittest.main()
