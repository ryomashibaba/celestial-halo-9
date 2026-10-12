import unittest
from generators.m111_grand_skybridges import option_b,endpoints,build,VARIANTS
class M111SkybridgesNonConstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data,cls.o=option_b()
    def test_all_four_bridges_and_explicit_remaining_gaps(self):
        es=endpoints(self.data,self.o)
        self.assertEqual({x['fid'] for x in es},{'SB05','SB08','SB09','SB12'})
        for e in es:
            self.assertEqual(e['parcel_to_bridge_gap_m'],16)
            self.assertGreater(e['bridge_length_m'],130)
            self.assertLess(e['bridge_length_m'],165)
            self.assertFalse(e['existing_building_interface_built'])
    def test_unapproved_model_masses_and_unsafe_gaps_remain(self):
        for v in VARIANTS:
            m=build(self.data,self.o,v)
            self.assertEqual(m['world_writes'],0)
            self.assertFalse(m['construction_approved'])
            self.assertTrue(m['relative_H_not_actual_world_Y'])
            self.assertGreater(len(m['meshes']),190)
            self.assertEqual(len(m['four_bridges']),4)
            self.assertTrue(all(not x['construction_approved'] and
                                not x['load_path_certified'] for x in m['meshes']))
            self.assertGreaterEqual(len(m['remaining_critical_gaps']),5)
    def test_preserve_parent_scope_and_distinct_visual_languages(self):
        a=build(self.data,self.o,VARIANTS[0]);b=build(self.data,self.o,VARIANTS[1])
        self.assertEqual(a['parent_option'],b['parent_option'])
        self.assertEqual(a['comparison_baseline'],'M101_UNMODIFIED')
        self.assertNotEqual(set(x['id'] for x in a['meshes']),set(x['id'] for x in b['meshes']))
if __name__=='__main__':unittest.main()
