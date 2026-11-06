import bpy,json,pathlib,hashlib,struct
ROOT=pathlib.Path(__file__).parent
def sig(o):
    r={'matrix':list(sum((list(row) for row in o.matrix_world),[]))}
    if o.type=='MESH':
        h=hashlib.sha256()
        for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
        for p in o.data.polygons:h.update(struct.pack('<%di'%len(p.vertices),*p.vertices))
        r['mesh']=h.hexdigest()
    if o.type=='CAMERA':r.update(lens=o.data.lens,sensor_width=o.data.sensor_width,clip_end=o.data.clip_end)
    return r
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'GATE_B_R1.blend'),load_ui=False,use_scripts=False)
expected=json.loads((ROOT/'protected_before.json').read_text())
checks={n:sig(bpy.data.objects[n])==s for n,s in expected.items()}
old=json.loads((ROOT/'R0_authoring_record.json').read_text())['excluded_source_objects']
retained=[n for n in old if n in bpy.context.scene.objects]
src=hashlib.sha256((ROOT/'reference/HALO9_INT21_M247C_OPEN_CIVIC_CANYON_RESEARCH.blend').read_bytes()).hexdigest()
r={'independent_reopen':'PASS','source_sha256':src,'source_unchanged':src=='9b950f0b9d5315605d5dc0bec252950e0c150739c94249a201667c9e2d675a27','W0_mesh_topology_and_matrix_E11_matrix_lens_sensor_clip':checks,'old_architecture_retained':retained,'blend_sha256':hashlib.sha256((ROOT/'GATE_B_R1.blend').read_bytes()).hexdigest(),'object_count':len(bpy.context.scene.objects),'art':'NOT_A_TECHNICAL_VERDICT','function':'UNVERIFIED','construction':'HOLD'}
assert all(checks.values()) and not retained and r['source_unchanged']
(ROOT/'INDEPENDENT_REOPEN.json').write_text(json.dumps(r,indent=2))
print('INDEPENDENT_SOURCE_W0_E11_PASS')
