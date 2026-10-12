import json,unittest
from pathlib import Path
from tools.m113_verify_reality_survey import check_grounded,check_new_probe
ROOT=Path(__file__).resolve().parents[1]
class M113EvidenceTests(unittest.TestCase):
 def test_reality_grounded_and_held(self):
  d=json.loads((ROOT/'survey/reports/M113_ACTUAL_WORLD_EVIDENCE.json').read_text())
  self.assertTrue(check_grounded(d))
 def test_report_does_not_authorize_construction(self):
  d=json.loads((ROOT/'survey/reports/M113_ACTUAL_WORLD_EVIDENCE.json').read_text())
  self.assertEqual(d['world_writes'],0)
  self.assertFalse(d['world_identity_proven_unique'])
  self.assertEqual(d['model_relative_h_to_world_absolute_y'],'UNKNOWN')
 def test_new_probe_validator_never_marks_mapping_verified(self):
  d={'project':'CELESTIAL HALO-9','mode':'READ_ONLY_PROBED_BLOCK_COLUMNS',
   'world_write_operations':0,'construction_approved':False,'probes_requested':49,
   'model_relative_H_to_actual_world_Y':'UNVERIFIED',
   'full_protected_volume_and_building_geometry_verified':False,
   'no_player_data_collected':True,'raw_world_path_not_exported':True,
   'probes_reported':1,
   'probes':[{'site':'OFFSITE','label':'M113_SCREENSHOT_POINT','min_solid_y':-1710,'max_solid_y':-1598}]}
  self.assertEqual(check_new_probe(d)['model_to_world_height_registration'],'UNVERIFIED')
if __name__=='__main__':unittest.main()
