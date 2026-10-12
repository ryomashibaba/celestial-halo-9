import unittest
from generators.m112_skyports import study,VARIANTS
class ReadOnlySkyports(unittest.TestCase):
 def test_four_approaches_without_construction(self):
  for name in VARIANTS:
   scene=study(name)
   self.assertEqual(scene["world_writes"],0)
   self.assertFalse(scene["construction_approved"])
   self.assertTrue(scene["model_H_not_actual_Y"])
   self.assertEqual(len(scene["interfaces"]),4)
   self.assertEqual(set(v["fid"] for v in scene["interfaces"]),{"SB05","SB08","SB09","SB12"})
   for v in scene["interfaces"]:
    self.assertEqual(v["gap_to_parcel_m"],2)
    self.assertAlmostEqual(v["low_approach_m"],14,places=5)
    self.assertFalse(v["existing_door_connected"])
    self.assertFalse(v["functional_lift"])
    self.assertFalse(v["absolute_y_verified"])
   self.assertTrue(all(not m["construction_approved"] and not m["load_path_certified"] for m in scene["meshes"]))
 def test_separate_skyport_designs(self):
  a=study(VARIANTS[0]);b=study(VARIANTS[1])
  self.assertNotEqual(set(x["id"] for x in a["meshes"]),set(x["id"] for x in b["meshes"]))
if __name__=="__main__":unittest.main()
