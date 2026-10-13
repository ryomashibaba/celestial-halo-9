import unittest,math,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
from m119_city_model import produce,SITES,ATLAS
from m120_city_model import produce_m120
from m120_audit import analyze
class M120ArchitectureAndSafety(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=produce_m120();cls.audit=analyze(cls.m)
 def test_parent_and_new_differentiated_shapes(self):
  old=produce('B_FRACTURED_SKY_TERRACES');m=self.m
  self.assertEqual(m['original_M119_mesh_count'],603)
  self.assertEqual(len(m['meshes']),m['original_M119_mesh_count']+m['m120_added_meshes'])
  self.assertGreaterEqual(m['m120_added_meshes'],120)
  self.assertEqual(m['meshes'][:603],old['meshes'])
  self.assertTrue(all(x['approved_for_world_write']==False and x['collision_certified']==False for x in m['meshes']))
  self.assertEqual({x['site'] for x in m['meshes'][603:] if x['site'] in ('SB05','SB08','SB09','SB12')},{'SB05','SB08','SB09','SB12'})
  self.assertTrue(all(any(x['site']==s for x in m['meshes']) for s in SITES))
 def test_mesh_faces_finite(self):
  for obj in self.m['meshes']:
   self.assertGreaterEqual(len(obj['v']),4)
   self.assertTrue(all(len(f)>=3 and all(isinstance(i,int) and 0<=i<len(obj['v']) for i in f) for f in obj['f']))
   self.assertTrue(all(math.isfinite(k) for v in obj['v'] for k in v))
 def test_path_mathematical_continuity_but_not_accessible(self):
  route=self.m['public_route_concept'];nodes=route['stations'];edges=route['segments']
  self.assertEqual(len(nodes),10);self.assertEqual(len(edges),9)
  self.assertTrue(all(tuple(a['end'])==tuple(b['start']) for a,b in zip(edges,edges[1:])))
  self.assertTrue(all(tuple(x['start'])==tuple(nodes[i]['xyz']) and tuple(x['end'])==tuple(nodes[i+1]['xyz']) for i,x in enumerate(edges)))
  self.assertEqual(sum(s['type']=='VERTICAL_LIFT_UNBUILT' for s in edges),2)
  self.assertEqual(edges[0]['observed_material_tile_AABB_risks'],13)
  self.assertEqual(edges[1]['observed_material_tile_AABB_risks'],8)
  self.assertTrue(all(not s['collision_cleared'] and not s['stairs_or_elevator_operational'] for s in edges))
  self.assertFalse(route['publicly_traversable']);self.assertFalse(self.m['accessible_continuous_public_route'])
 def test_no_fake_height_or_protected_mapping(self):
  m=self.m;a=self.audit
  self.assertEqual(m['world_writes'],0)
  self.assertEqual(m['model_H_to_world_Y'],'UNVERIFIED')
  self.assertEqual(m['reference_review_copy'],'CH9_D6D_REVIEW_COPY')
  self.assertFalse(m['governance']['formal_protection_clearance'])
  self.assertFalse(a['SB13_actual_protected_entry_coordinates_verified'])
  self.assertFalse(a['full_frozen408_world_voxel_map_verified'])
  self.assertFalse(a['pedestrian_traversable'])
  self.assertFalse(a['official_live_world_registered'])
  self.assertEqual(a['world_writes'],0)
 def test_broadphase_is_explicitly_noncertified(self):
  a=self.audit
  self.assertEqual(a['site_material_8x8_tiles'],2096)
  self.assertEqual(a['new_proposal_meshes_with_observed_tile_AABB_risk'],38)
  self.assertEqual(a['new_proposal_meshes_without_observed_tile_AABB_risk'],92)
  self.assertGreater(a['distinct_old_tiles_potentially_overlapped'],0)
  self.assertGreater(a['new_geometry_versus_observed_8x8_tile_Y_AABB_potential_hits'],0)
  self.assertFalse(a['exact_old_voxel_collision_check'])
  self.assertFalse(a['protected_reserved_88_voids_checked'])
 def test_m119_parent_source_bundle_not_modified(self):
  mf=json.loads((ROOT/'M119_FILE_SHA256_MANIFEST.json').read_text())
  self.assertTrue(mf['source_immutable_user_atlas'])
  for name,sha in mf['files'].items():
   source=ROOT/name
   self.assertTrue(source.exists(),name)
   self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),sha,name)
if __name__=='__main__':unittest.main()
