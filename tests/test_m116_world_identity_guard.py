import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from tools.m116_world_identity_guard import inspect,require_construction_permission
ROOT=Path(__file__).resolve().parents[1]

class IdentityGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.registry={"known_saves":[]}
    def save(self,name,body):
        p=self.root/"SKYTREE_3500"/"saves"/name
        p.mkdir(parents=True)
        (p/"level.dat").write_bytes(body)
        record={"id":name,"save_folder_tail":["SKYTREE_3500","saves",name],
                "role":"READ_ONLY_TEST","screenshot_match":"UNVERIFIED",
                "level_dat_sha256":hashlib.sha256(body).hexdigest()}
        self.registry["known_saves"].append(record)
        return p
    def test_same_world_display_name_distinct_save_folders(self):
        a=self.save("imagine",b"LevelName: imagine version A")
        b=self.save("CH9_D6D_REVIEW_COPY",b"LevelName: imagine version B")
        ar=inspect(a,self.registry);br=inspect(b,self.registry)
        self.assertEqual(ar["record_id"],"imagine")
        self.assertEqual(br["record_id"],"CH9_D6D_REVIEW_COPY")
        self.assertFalse(ar["identity_proven"])
        self.assertFalse(br["construction_permitted"])
    def test_changed_level_dat_never_silent_approval(self):
        a=self.save("CH9_D6D_REVIEW_COPY",b"original")
        (a/"level.dat").write_bytes(b"updated by game")
        result=inspect(a,self.registry)
        self.assertEqual(result["match"],"KNOWN_FOLDER_DIFFERENT_SNAPSHOT")
        self.assertFalse(result["construction_permitted"])
    def test_same_hash_in_different_folder_not_identity(self):
        p=self.save("CH9_D6D_REVIEW_COPY",b"clone")
        other=self.root/"SKYTREE_3500"/"saves"/"copy"
        other.mkdir();(other/"level.dat").write_bytes((p/"level.dat").read_bytes())
        result=inspect(other,self.registry)
        self.assertEqual(result["match"],"UNREGISTERED_FOLDER")
    def test_missing_or_broken_save_refused(self):
        p=self.root/"unknown"
        self.assertEqual(inspect(p,self.registry)["match"],"UNREADABLE_OR_INVALID")
    def test_live_construction_always_denied(self):
        self.assertFalse(require_construction_permission())
        self.assertFalse(require_construction_permission("review-copy-candidate",True))
        reg=json.loads((ROOT/"survey"/"identity"/"M116_world_candidates.json").read_text())
        self.assertIsNone(reg["official_construction_world_id"])
        self.assertFalse(reg["construction_authorized"])
        self.assertTrue(all(not x["may_use_for_world_writes"] for x in reg["known_saves"]))

if __name__=="__main__":
    unittest.main()
