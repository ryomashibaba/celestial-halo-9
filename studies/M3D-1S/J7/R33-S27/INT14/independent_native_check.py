"""INT14 separate-process H1 real corridor/geometry and four image checks.
This validates physical differences but NEVER assigns formal ART / FUNCTION.
"""
import bpy,json,hashlib,math,struct
from pathlib import Path
root=Path('/tmp/halo9-int14')
file=Path(bpy.data.filepath)
r=json.loads((root/'INT14_NATIVE_EVIDENCE_NOT_ART.json').read_text())
assert file.name=='HALO9_INT14_H1_PUBLIC_ENTRY_HUMAN_SIGHTLINE.blend'
assert hashlib.sha256(file.read_bytes()).hexdigest()==r['saved_blend_sha256']
assert r['input_sha256']=='da098354430d0aa62d0f4825c23127340aba8e8c353c6dc33f53c5b8b0fec3c3'
scene=bpy.context.scene
assert scene['CONSTRUCTION']=='HOLD'
assert scene['FORMAL_ART_ACCEPTED']==scene['COMPLETED_TARGETS']==0
assert scene['INT14_FORMAL_ART_ADOPTED']==0
assert r['formal_art_accepted']==r['completed_targets']==0 and r['minecraft']=='HOLD'
assert r['source_masses_unhidden_no_cutaway_substitution']
ob=bpy.data.objects[r['real_mesh_modified']]
assert ob.type=='MESH'
assert len(ob.data.polygons)==r['polygons_after']>r['polygons_before']+10
assert all(math.isfinite(float(c)) for v in ob.data.vertices for c in v.co)
assert r['fixed_h1_research_wall_hits_after']<=r['fixed_h1_research_wall_hits_before']-3 or (
 r['fixed_h1_camera_center_before']['name']==ob.name and
 r['fixed_h1_camera_center_after']['name']!=ob.name)
assert len(r['old_route_grade_audit'])==9
assert sum(x['grade_pct']>12 for x in r['old_route_grade_audit'])==8
for name,mat in r['original_three_E11_camera_matrices'].items():
    cur=bpy.data.objects[name].matrix_world
    assert max(abs(cur[i][j]-mat[i][j]) for i in range(4) for j in range(4))<1e-6
for name,sha in r['protected_W0_vertex_sha256'].items():
    h=hashlib.sha256()
    for v in bpy.data.objects[name].data.vertices:
        h.update((','.join(f'{float(c):.10g}' for c in v.co)+';').encode())
    assert h.hexdigest()==sha,name
assert len(r['real_native_render_sha256'])==4
for name,sha in r['real_native_render_sha256'].items():
    p=root/'renders'/(name+'.png')
    with p.open('rb') as f:head=f.read(24)
    assert head[:8]==bytes.fromhex('89504e470d0a1a0a')
    assert struct.unpack('>II',head[16:24])==(1024,768)
    assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
print('INT14_INDEPENDENT_NATIVE_E11_H1_ENTRY_AND_FOUR_IMAGES_VERIFIED_NOT_ART')
