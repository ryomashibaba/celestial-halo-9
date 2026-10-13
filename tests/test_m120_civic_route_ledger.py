import json,math,unittest
from pathlib import Path
from generators.m120_civic_research_route import research_route
S=Path(__file__).resolve().parents[1]/"design/drafts/M120_ARCHITECTURAL_SPINE_FINDINGS.json"
class M120NonConstructionSummary(unittest.TestCase):
 def test_research_route_has_true_endpoint_continuity_but_no_access_claim(self):
  d=research_route()
  self.assertEqual(d["station_count"],10)
  self.assertEqual(d["segment_count"],9)
  self.assertEqual(sum(x["type"]=="UNBUILT_LIFT" for x in d["segments"]),2)
  self.assertTrue(all(a["end"]==b["start"] for a,b in zip(d["segments"],d["segments"][1:])))
  self.assertTrue(all(not x["collision_certified"] and not x["operational"] for x in d["segments"]))
  self.assertFalse(d["real_portal_xyz_registered"])
  self.assertFalse(d["pedestrian_traversable"])
  self.assertEqual(d["world_write_operations"],0)
 def test_audit_summary_is_conservative_and_grounded(self):
  d=json.loads(S.read_text())
  self.assertEqual(d["original_M119_B_proposal_meshes"],603)
  self.assertEqual(d["M120_added_meshes"],130)
  self.assertEqual(d["total_M120_research_meshes"],733)
  o=d["new_geometry_vs_saved_8x8_xy_y_AABB_broadphase"]
  self.assertEqual(o["new_meshes_with_potential_overlap"]+o["new_meshes_with_zero_detected_8x8_material_overlap"],130)
  self.assertEqual(o["new_meshes_with_potential_overlap"],38)
  self.assertGreater(o["mesh_tile_overlap_pairs"],o["distinct_8x8_old_material_tiles_with_potential_overlap"])
  self.assertFalse(d["path_plan"]["publicly_traversable"])
  self.assertEqual(d["governance"]["world_writes"],0)
  self.assertFalse(d["governance"]["live_minecraft_construction_authorized"])
  self.assertEqual(d["assumptions"]["M101_relative_H_to_real_Y"],"UNVERIFIED")
if __name__=="__main__":unittest.main()
