import unittest
from tools.m117_validate_atlas import validate
def fixture():
 s=[]
 for i in range(1,17):
  s.append({"site":f"SB{i:02d}","artificial_blocks_exact":0,
    "top_materials":[],"occupied_8x8_tiles":0,"tiles":[],"y_band_counts":[],
    "real_world_min_artificial_y":None,"real_world_max_artificial_y":None})
 return {"project":"CELESTIAL HALO-9","phase":"M117",
 "mode":"EXACT_SAVED_BLOCKS_READ_ONLY_REVIEW_COPY",
 "world_save_folder":"CH9_D6D_REVIEW_COPY",
 "world_role":"USER_VERIFIED_OLD_ARCHITECTURE_REVIEW_COPY_ONLY",
 "world_writes":0,"construction_approved":False,"construction_target_registered":False,
 "model_H_to_world_Y":"UNKNOWN_NEEDS_INDEPENDENT_LANDMARK_MATCH",
 "coordinates_are_real_saved_block_positions":True,"sites":s,
 "chunks_readable":0,"total_distinct_chunks_requested":1456,
 "survey_complete":False,"chunks_missing":1456,
 "errors":["synthetic fixture intentionally has no region data"]}
class M117ReadOnlySchema(unittest.TestCase):
 def test_accept_partial_zero_building_not_false_pass(self):
  r=validate(fixture());self.assertFalse(r["full_survey"])
  self.assertFalse(r["world_y_calibrated"])
  self.assertFalse(r["protected_geometry_certified"])
  self.assertFalse(r["construction_approved"])
 def test_reject_wrong_world_even_if_same_levelname(self):
  d=fixture();d["world_save_folder"]="imagine"
  with self.assertRaises(AssertionError):validate(d)
 def test_reject_world_write_or_premature_y_claim(self):
  d=fixture();d["world_writes"]=1
  with self.assertRaises(AssertionError):validate(d)
  d=fixture();d["model_H_to_world_Y"]="-1800"
  with self.assertRaises(AssertionError):validate(d)
 def test_validate_exact_material_tile_band_accounting(self):
  d=fixture();site=d["sites"][8]
  site.update({"artificial_blocks_exact":2,
    "top_materials":[["minecraft:smooth_quartz",2]],"occupied_8x8_tiles":1,
    "real_world_min_artificial_y":-1701,"real_world_max_artificial_y":-1700,
    "tiles":[{"x":3824,"z":-2344,"count":2,"min_y":-1701,"max_y":-1700,
    "materials":[["minecraft:smooth_quartz",2]]}],
    "y_band_counts":[{"y0":-1712,"count":2}]})
  self.assertEqual(validate(d)["total_artificial_blocks"],2)
  site["artificial_blocks_exact"]=3
  with self.assertRaises(AssertionError):validate(d)
if __name__=="__main__":unittest.main()
