import sys,unittest,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
from m119_city_model import ATLAS,SITES,produce,HERO,CIVIC
class M119ConceptSafety(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.A=produce('A_CROWNED_MERIDIAN');cls.B=produce('B_FRACTURED_SKY_TERRACES')
 def test_ground_truth(self):
  self.assertEqual(ATLAS['world_save_folder'],'CH9_D6D_REVIEW_COPY')
  self.assertTrue(ATLAS['survey_complete'])
  self.assertEqual(ATLAS['chunks_readable'],1456)
  self.assertFalse(ATLAS['errors'])
  self.assertEqual(len(SITES),16)
  self.assertEqual(sum(s['actual_building_like_blocks'] for s in SITES.values()),1095343)
  self.assertEqual(sum(s['tiles'] for s in SITES.values()),2096)
  self.assertEqual(max(s['observed_y_max'] for s in SITES.values()),-1703)
 def test_all_sites_and_primary_interiors(self):
  for model in [self.A,self.B]:
   p=model['facility_programs'];self.assertEqual(len(p),16)
   self.assertEqual({x['site'] for x in p},set(SITES))
   self.assertEqual(sum(x['kind']=='HERO' for x in p),4)
   self.assertEqual(sum(x['kind']=='CIVIC' for x in p),4)
   self.assertEqual(sum(x['kind']=='FRAME' for x in p),8)
   self.assertEqual(len(set(x['proposed_primary_interior'] for x in p)),16)
   self.assertTrue(all(x['new_geometry_clashes_with_existing_not_clearance_tested'] for x in p))
   self.assertTrue(all(not x['actual_indoor_walkable_route_certified'] and x['frozen_legacy_mask_unresolved'] for x in p))
 def test_creative_distinction_and_hero_form(self):
  a=set(x['id'] for x in self.A['meshes']);b=set(x['id'] for x in self.B['meshes'])
  self.assertNotEqual(a,b)
  for model in [self.A,self.B]:
   for s in HERO:
    self.assertGreaterEqual(len([x for x in model['meshes'] if x['site']==s]),5)
   self.assertGreaterEqual(len(model['proposed_courts_and_voids']),9)
   self.assertGreaterEqual(len(model['unverified_route_intents']),24)
   self.assertGreater(len(model['meshes']),450)
 def test_formal_safety_not_claimed(self):
  for m in [self.A,self.B]:
   self.assertEqual(m['world_writes'],0)
   self.assertIsNone(m['minecraft_save_to_modify'])
   self.assertFalse(m['protected_mesh_collision_certified'])
   self.assertFalse(m['all_facility_entrances_walkable'])
   self.assertTrue(m['protected_existing_geometry_intentionally_unmodified'])
   self.assertEqual(m['observed_legacy_blocks_deleted'],0)
   self.assertEqual(m['model_relative_H_mapping_still'],'UNKNOWN')
   self.assertTrue(all(not x['approved_for_world_write'] and not x['collision_certified'] for x in m['meshes']))
   self.assertTrue(all(x['real_saved_blocks_not_removed'] for x in m['proposed_courts_and_voids']))
 def test_coordinate_finiteness(self):
  for m in [self.A,self.B]:
   for g in m['meshes']:
    self.assertTrue(g['v'])
    self.assertTrue(g['f'])
    self.assertTrue(all(-2000 < p[2] < -1490 and 2900 < p[0] < 4500 and -2650 < p[1] < -1750 for p in g['v']))
    self.assertTrue(all(0<=idx<len(g['v']) for face in g['f'] for idx in face))
if __name__=='__main__':unittest.main()
