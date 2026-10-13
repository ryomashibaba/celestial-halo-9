import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"design/drafts/M121_HUMAN_SCALE_ATRIUM_LEDGER.json"
class M121HonestProgress(unittest.TestCase):
 def test_model_progress_and_no_write(self):
  x=json.loads(P.read_text())
  self.assertEqual(x["inherited_meshes"],733)
  self.assertEqual(x["new_research_meshes"],566)
  self.assertEqual(x["total_research_meshes"],1299)
  self.assertEqual(len(x["render_figures"]),4)
  self.assertEqual(x["local_unittest_count"],15)
  self.assertEqual(x["world_writes"],0)
  self.assertFalse(x["official_construction_world_registered"])
  self.assertFalse(x["official_B_design_adopted"])
  self.assertFalse(x["M101_comparison_baseline_changed"])
 def test_overlap_cannot_be_called_clearance(self):
  x=json.loads(P.read_text())
  self.assertEqual(x["inherited_M120_old_material_tile_AABB_overlap_meshes"],38)
  self.assertEqual(x["new_M121_8x8_material_tile_AABB_overlap_meshes"],0)
  self.assertIn("UNVERIFIED",x["new_M121_voxel_protection_status"])
  self.assertFalse(x["exact_Freeze408_and_public959_3D_voxel_map_loaded"])
  self.assertFalse(x["all_88_reserved_voids_checked"])
  self.assertFalse(x["physical_pedestrian_walkability_verified"])
  self.assertFalse(x["full_source_uploaded_into_this_GitHub_pr"])
 def test_next_is_work_setup_not_construction(self):
  x=json.loads(P.read_text())
  self.assertEqual(x["followup"],"USER_WANTS_LOCAL_WORK_PROJECT_SETUP_AFTER_M121")
  self.assertEqual(x["reference_world"],"CH9_D6D_REVIEW_COPY_READ_ONLY_NOT_CONSTRUCTION_TARGET")
  self.assertTrue(all(len(s)==64 for s in x["repro_sha256"].values()))
if __name__=="__main__":unittest.main()
