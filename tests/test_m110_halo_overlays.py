import json,unittest
from pathlib import Path
from generators.m110_halo_overlays import (SOURCE,WIDTH,CONSERVATIVE_BUFFER,site_hits,overlay)
class M110NonConstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.obj=json.loads(SOURCE.read_text())
    def test_site_buffer_clearance(self):
        self.assertEqual((WIDTH,CONSERVATIVE_BUFFER),(30.0,18.5))
        self.assertEqual(site_hits(self.obj['alternatives'],self.obj['sites']),
                         {o['id']:[] for o in self.obj['alternatives']})
    def test_macro_designs_distinct_and_proposals_only(self):
        self.assertEqual(len(self.obj['alternatives']),3)
        counts=set()
        for o in self.obj['alternatives']:
            m=overlay(o)
            counts.add(len(m['meshes']))
            self.assertGreater(len(m['meshes']),500)
            self.assertEqual(m['world_writes'],0)
            self.assertFalse(m['construction_approved'])
            self.assertTrue(m['model_relative_H_not_actual_minecraft_Y'])
            self.assertTrue(all(not q['structural_support_certified'] and
                                not q['construction_approved'] for q in m['meshes']))
        self.assertEqual(len(counts),3)
    def test_all_sixteen_facilities_still_present(self):
        self.assertEqual(len(self.obj['sites']),16)
        self.assertEqual(len({s['id'] for s in self.obj['sites']}),16)
if __name__=='__main__':unittest.main()
