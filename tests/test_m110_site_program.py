import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'design/drafts/M110_SITE_AND_ROUTE_PROGRAM.json'
class UrbanProgramNonconstruction(unittest.TestCase):
    def test_sites_have_distinct_program_and_primary_interior(self):
        d=json.loads(P.read_text())
        sites=d['architecture']
        self.assertEqual(len(sites),16)
        self.assertEqual(len(set(x['id'] for x in sites)),16)
        self.assertEqual(len(set(x['name'] for x in sites)),16)
        self.assertTrue(all(x['principal_interior'] for x in sites))
        self.assertEqual([sum(x['kind']==k for x in sites) for k in ('HERO','CIVIC','FRAME')],[4,4,8])
    def test_routes_not_misrepresented_as_constructed(self):
        d=json.loads(P.read_text())
        self.assertEqual(len(d['proposed_routes']),13)
        self.assertTrue(all(not x['geometry_constructed'] and not x['continuous_public_access_certified'] for x in d['proposed_routes']))
        self.assertEqual(sum('ORBITAL_TRANSFER' in x['to'] for x in d['proposed_routes']),4)
    def test_approval_and_world_locks_held(self):
        d=json.loads(P.read_text())
        self.assertFalse(d['initial_pilot_study_only']['authorized_for_world_construction'])
        self.assertEqual(d['world_absolute_Y'],'UNKNOWN')
        self.assertFalse(d['safety']['formal_design_promotion_approved'])
        self.assertEqual(d['safety']['world_writes'],0)
if __name__=='__main__':unittest.main()
