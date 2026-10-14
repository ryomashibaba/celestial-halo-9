import json,sys,unittest
from pathlib import Path
SRC=Path(__file__).resolve().parents[1]/'source'
sys.path.insert(0,str(SRC))
from m121_city_experience import build_experience
from m121_audit import audit_m121
class M121MonumentalPublicRealm(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=build_experience();cls.a=audit_m121(cls.m)
 def test_unchanged_existing_models_and_valid_3d_proposals(self):
  m=self.m;self.assertEqual(m['phase'],'M121')
  self.assertEqual(m['m121_meshes_start_index'],733)
  self.assertEqual(len(m['meshes']),1299)
  self.assertEqual(m['m121_new_mesh_count'],566)
  self.assertEqual(m['world_writes'],0)
  self.assertFalse(m['accessible_continuous_public_route'])
  for o in m['meshes'][733:]:
   self.assertFalse(o['approved_for_world_write'])
   self.assertFalse(o['collision_certified'])
   self.assertEqual(o['existing_frozen_voxel_clearance'],'UNKNOWN')
   self.assertGreaterEqual(len(o['v']),4)
 def test_open_mega_vault_not_flat_overlay(self):
  m=self.m
  ids=[x['id'] for x in m['meshes'][733:]]
  self.assertGreaterEqual(sum('PRIMARY_VAULT_RIB' in x for x in ids),120)
  self.assertGreaterEqual(sum('CIVIC_MAJOR_HEAVY_VAULT' in x for x in ids),70)
  self.assertTrue(any('SB08_NAVE_STONE_FLOOR' in x for x in ids))
  self.assertTrue(any('CIVIC_PUBLIC_STONE_COURT' in x for x in ids))
  self.assertEqual(sum('SCALE_PERSON' in x for x in ids),9)
  self.assertGreaterEqual(sum('GALLERY' in x for x in ids),15)
 def test_tile_broadphase_not_assumed_protected_clearance(self):
  r=self.a
  self.assertEqual(r['M120_inherited_overlap_triage']['potential_old_material_overlap_meshes'],38)
  self.assertEqual(r['M121_new_mesh_overlap_triage']['proposals_scanned'],566)
  self.assertEqual(r['M121_new_mesh_overlap_triage']['potential_old_material_overlap_meshes'],0)
  self.assertFalse(r['protected_source_masks_loaded'])
  self.assertFalse(r['historical_reserved_88_voids_screened'])
  self.assertFalse(r['public_walk_route_fully_traversable'])
  self.assertEqual(r['categorization']['DESIGNABLE_proven_count'],0)
  self.assertEqual(r['categorization']['LOCKED_proven_count'],0)
  self.assertEqual(r['categorization']['UNKNOWN_classification_count_M120'],130)
  self.assertEqual(r['categorization']['UNKNOWN_classification_count_M121'],566)
  self.assertEqual(r['world_writes'],0)
 def test_public_eye_view_does_not_claim_real_minecraft(self):
  exp=self.m['experience']
  self.assertEqual(exp['public_eye_level_cameras'],2)
  self.assertEqual(exp['1p8m_scale_figures'],9)
  self.assertFalse(exp['continuous_physical_route_pass'])
  self.assertFalse(exp['usable_real_elevator'])
  self.assertFalse(exp['safe_for_construction'])
  self.assertEqual(exp['next_work_mode'],'SETUP_LOCAL_WORK_PROJECT_AFTER_M121')
if __name__=='__main__':unittest.main()
