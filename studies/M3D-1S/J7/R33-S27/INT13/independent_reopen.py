"""Independent INT13 Blender process — native source and image validation.
Physical adjacency in the authored floor graph != certified traversal.
Explicit cutaway renders are not evidence of integrated-master ART success.
"""
import bpy,math,json,hashlib,struct
from pathlib import Path
ROOT=Path('/tmp/halo9-int13')
p=Path(bpy.data.filepath)
r=json.loads((ROOT/'INT13_NATIVE_RESEARCH_NOT_ART.json').read_text())
assert p.name=='HALO9_INT13_PURPOSE_FIRST_INHABITED_SECTION.blend'
assert hashlib.sha256(p.read_bytes()).hexdigest()==r['saved_native_blend_sha256']
assert r['parent_sha256']=='563773c54328f249978c0ed6d989edfc437d467a9d543a0b21511f99d6a508a1'
sc=bpy.context.scene
assert sc['CONSTRUCTION']=='HOLD'
assert sc['FORMAL_ART_ACCEPTED']==sc['COMPLETED_TARGETS']==0
assert sc['INT13_NOT_A_FORMAL_ART_ADOPTION']
assert r['formal_art_accepted']==r['completed_targets']==0 and r['minecraft']=='HOLD'
assert r['rejected_shell_visibility_restored_for_native_blend']
for n in r['rejected_shells_masked_in_section_only']:
    assert n in bpy.data.objects
    assert bpy.data.objects[n].hide_render==False,('unexpected persistent hidden shell',n)
assert len(r['physical_route_edges'])==9
assert len(r['physical_voids'])==6
assert len(r['public_program_nodes'])==10
assert len(r['new_native_meshes'])>=17
# Physical end-points: every designed link meets exactly at the same
# research world point, but no collision/ray/walkability proof is asserted.
for edge in r['physical_route_edges']:
    aa=r['public_program_nodes'][edge['from']]
    bb=r['public_program_nodes'][edge['to']]
    assert math.dist(aa,edge['start_xyz'])<1e-6
    assert math.dist(bb,edge['end_xyz'])<1e-6
    assert edge['rise_m']>0
    assert edge['length_m']>edge['rise_m']
    ob=bpy.data.objects[edge['object']]
    assert len(ob.data.vertices)>=40 and len(ob.data.polygons)>25
for n in r['new_native_meshes']:
    obj=bpy.data.objects[n]
    assert obj.type=='MESH' and len(obj.data.vertices)>=4 and len(obj.data.polygons)>=4
    assert all(math.isfinite(float(v)) for vert in obj.data.vertices for v in vert.co)
for n,old in r['fixed_original_E11_camera_matrices'].items():
    m=bpy.data.objects[n].matrix_world
    assert max(abs(m[i][j]-old[i][j]) for i in range(4) for j in range(4))<1e-6
for n,old in r['protected_W0_geometry_hash'].items():
    h=hashlib.sha256()
    for v in bpy.data.objects[n].data.vertices:
        h.update((','.join(f'{float(x):.10g}' for x in v.co)+';').encode())
    assert h.hexdigest()==old
assert len(r['source_view_full_original_E11'])==3
assert len(r['source_view_cutaway_art_rejected_shells_hidden'])==4
for n,sha in r['all_native_render_png_sha256'].items():
    f=ROOT/'renders'/(n+'.png')
    with f.open('rb') as fd:header=fd.read(24)
    assert header[:8]==bytes.fromhex('89504e470d0a1a0a')
    assert struct.unpack('>II',header[16:24])==(960,720)
    assert hashlib.sha256(f.read_bytes()).hexdigest()==sha
print('INT13_INDEPENDENT_REOPEN_PURPOSE_FIRST_3D_AND_7_PIXELS_PASS_NOT_ART',flush=True)
