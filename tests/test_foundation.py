import json,unittest
from pathlib import Path
from ci.check_policy import check
from ci.guard_changes import check_paths
ROOT=Path(__file__).resolve().parents[1]
class ProjectPolicyTests(unittest.TestCase):
    def test_policy_and_nonconstruction(self):self.assertTrue(check())
    def test_all_16_sites_registered(self):
        d=json.loads((ROOT/'governance/protected_registry.json').read_text())
        self.assertEqual(sum(map(len,d['sites'].values())),16)
    def test_locked_paths_rejected(self):
        self.assertEqual(check_paths(['design/drafts/a.json','generators/x.py']),[])
        self.assertEqual(set(check_paths(['governance/project_policy.json','.github/workflows/ci.yml'])),{'governance/project_policy.json','.github/workflows/ci.yml'})
    def test_no_execution_approval(self):
        d=json.loads((ROOT/'governance/release_gate.json').read_text())
        self.assertFalse(d['construction_approved'])
        self.assertFalse(d['world_write_enabled'])
if __name__=='__main__':unittest.main()
