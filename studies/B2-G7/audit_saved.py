"""Reload saved comparison BLENDs without touching the originals."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
p=Path(__file__).resolve().parent;results=[]
for c in 'AB':
 folder=p/(c+'_massing');m=json.loads((folder/'manifest.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(folder/'study.blend'))
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name!='10km comparison frame' and not o.name.startswith('Context urban tile')]
 bad=0;finite=True;volumes=[]
 for o in obs:
  bm=bmesh.new();bm.from_mesh(o.data);bad+=sum(not e.is_manifold for e in bm.edges);volumes.append(bm.calc_volume(signed=True));bm.free()
  finite &= all(math.isfinite(v) for q in o.data.vertices for v in q.co)
 imgs=[folder/(v+'.png') for v in ['oblique','side','rear','context']]
 checks=dict(mesh_count_matches=len(obs)==m['mesh_objects'],all_coordinates_finite=finite,closed_individual_solids=bad==0,positive_signed_volume=all(v>0 for v in volumes),four_renders_exist=all(f.exists() and f.stat().st_size>1000 for f in imgs),four_saved_cameras=all(v in bpy.data.objects for v in ['oblique','side','rear','context']),same_geometry_for_all_views=all(v['geometry_sha256']==m['geometry_sha256'] for v in m['renders']))
 results.append(dict(concept=c,checks=checks,mesh_objects=len(obs),nonmanifold_edges=bad,bounds_m=m['bounds_m'],public_ground_count=len(m['grounds']),ground_area_sum_m2=sum(g['area_m2'] for g in m['grounds']),high_ground_area_sum_m2=sum(g['area_m2'] for g in m['grounds'] if g['center'][2]>=1000)))
out=dict(study_id='B2-G7',method='Reload each saved BLEND; inspect solid meshes and four actual render files',results=results,passed=all(all(r['checks'].values()) for r in results),limits=['Per-object closure is not an assembled-building or collision check.','High-ground area is gross schematic surface, not net usable area or capacity.','Same-geometry signatures were asserted during rendering; this audit checks recorded provenance, not pixel equivalence.','No structure, geotechnics, daylight, wind, life safety, access or W0 registration validation.'])
(p/'verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');assert out['passed'];print('RELOAD QA PASS')
