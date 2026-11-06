"""INT15 independent-process evidence gate. TECH != ART != FUNCTION."""
import bpy,math,hashlib,struct,json
from pathlib import Path
ROOT=Path('/tmp/halo9-int15')
file=Path(bpy.data.filepath)
d=json.loads((ROOT/'INT15_TRUE_NATIVE_TECH_NOT_ART.json').read_text())
assert file.name=='HALO9_INT15_H1_OCCUPIED_LIFT_PUBLIC_CORE.blend'
assert hashlib.sha256(file.read_bytes()).hexdigest()==d['native_blend_sha256']
assert d['input_sha256']=='431f5d1845f04a7fa669e2e230e00298cfedd98ee3d3069eb36c3fc85a7a6146'
sc=bpy.context.scene
assert sc['CONSTRUCTION']=='HOLD'
assert sc['FORMAL_ART_ACCEPTED']==sc['COMPLETED_TARGETS']==0
assert sc['INT15_NO_FORMAL_ART_ACCEPTANCE']
assert d['formal_art_accepted']==d['completed_targets']==0 and d['minecraft']=='HOLD'
assert len(d['old_rejected_research_objects_physically_removed_in_copy'])>=5
for n in d['old_rejected_research_objects_physically_removed_in_copy']:
    assert n not in bpy.data.objects,n
assert len(d['unsafe_H1_walkway_3_removed_in_copy'])==3
for n in d['unsafe_H1_walkway_3_removed_in_copy']:
    assert n not in bpy.data.objects,n
assert len(d['actual_boolean_subtractions'])==5
assert sum(c['physical_mesh_topology_changed'] for c in d['actual_boolean_subtractions'])>=3
assert d['actual_boolean_subtractions'][0]['physical_mesh_topology_changed']
t=bpy.data.objects[d['target_h1_mass']]
assert len(t.data.polygons)==d['final_polygons']
assert t.type=='MESH'
assert all(math.isfinite(float(c)) for v in t.data.vertices for c in v.co)
assert len(d['four_stations'])==4
assert len(d['flat_gallery_segments'])==4
for entry in d['flat_gallery_segments']:
    assert entry['rise_m']==0.0
    ob=bpy.data.objects[entry['gallery']]
    assert ob.type=='MESH' and len(ob.data.vertices)>=8
    assert all(math.isfinite(float(c)) for v in ob.data.vertices for c in v.co)
assert d['physical_walkability']=='NOT_CERTIFIED'
assert d['elevator_mechanism'].startswith('KEYFRAMED_PLATFORM_ONLY')
cab=bpy.data.objects['INT15_MOVABLE_CIVIC_PUBLIC_LIFT_PLATFORM']
assert cab.animation_data is not None and cab.animation_data.action is not None
assert d['cabin_keyframes']==[1,64,128,192]
for n,mat in d['fixed_E11_matrices'].items():
    actual=bpy.data.objects[n].matrix_world
    assert max(abs(actual[i][j]-mat[i][j]) for i in range(4) for j in range(4))<1e-6,n
for n,sha in d['W0_original_sha'].items():
    h=hashlib.sha256()
    for v in bpy.data.objects[n].data.vertices:
        h.update((','.join(format(float(c),'.10g') for c in v.co)+';').encode())
    assert h.hexdigest()==sha,n
for name in ('INT11_M247C_ALPHA_WEST_ACCRETED_ARCHIVE','INT11_M247C_ALPHA_EAST_CIVIC_HIGH_CITY','INT11_M247C_ALPHA_FLOATING_SEVERED_NORTH','INT11_M247C_BETA_SLANTED_CIVIC_SEAM'):
    assert name in bpy.data.objects,name
assert d['no_cutaway_masking']
assert len(d['native_5_png_sha256'])==5
for name,sha in d['native_5_png_sha256'].items():
    img=ROOT/'renders'/(name+'.png')
    with img.open('rb') as f:head=f.read(24)
    assert head[:8]==bytes.fromhex('89504e470d0a1a0a')
    assert struct.unpack('>II',head[16:24])==(960,720)
    assert hashlib.sha256(img.read_bytes()).hexdigest()==sha
print('INT15_INDEPENDENT_TRUE_MESH_CARVED_LIFT_AND_5_RENDER_TECH_PASS_NOT_ART_OR_WALKABILITY',flush=True)
