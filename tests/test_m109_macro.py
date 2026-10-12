import json,unittest
from pathlib import Path
from generators.m109_macro_schematic import screen
ROOT=Path(__file__).resolve().parents[1]
class M109MacroNoConstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obj=json.loads((ROOT/'design/drafts/M109_macro_alternatives.json').read_text(encoding='utf8'))
    def test_three_genuinely_different_macro_structures(self):
        obj=self.obj;self.assertEqual(len(obj['alternatives']),3)
        self.assertEqual(len(set(c['id'] for c in obj['alternatives'])),3)
        self.assertEqual(len({str(c['rings']) for c in obj['alternatives']}),3)
    def test_all_six_centerlines_clear_existing_site_parcels(self):
        self.assertEqual(screen(self.obj),{c['id']:[] for c in self.obj['alternatives']})
    def test_no_world_writes_or_baseline_promotion(self):
        a=self.obj['authorization']
        self.assertFalse(a['new_formal_baseline_approved'])
        for k in ('live_world_writes','freeze_writes','canonical_writes','staging_writes'):
            self.assertEqual(a[k],0)
    def test_16_sites_and_unknown_actual_world_y(self):
        self.assertEqual(len(self.obj['sites']),16)
        self.assertEqual(self.obj['coordinates']['minecraft_world_absolute_Y'],'UNKNOWN')
        self.assertTrue(self.obj['coordinates']['model_relative_height_not_world_y'])
if __name__=='__main__':unittest.main()
