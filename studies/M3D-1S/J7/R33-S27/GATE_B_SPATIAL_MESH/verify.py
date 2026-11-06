"""One independent Blender reopen at close-out; deliberately not an ART test."""
import bpy,json,pathlib,hashlib,struct,sys
R=pathlib.Path(__file__).parent;P=R.parent/'GATE_B_AFTER_INT21'
def sig(o):
    r={'matrix':list(sum((list(row) for row in o.matrix_world),[]))}
    if o.type=='MESH':
        h=hashlib.sha256()
        for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
        for p in o.data.polygons:h.update(struct.pack('<%di'%len(p.vertices),*p.vertices))
        r['mesh']=h.hexdigest()
    if o.type=='CAMERA':r.update(lens=o.data.lens,sensor_width=o.data.sensor_width,clip_end=o.data.clip_end)
    return r
rev=sys.argv[sys.argv.index('--')+1]
f=R/('SPATIAL_'+rev+'.blend');bpy.ops.wm.open_mainfile(filepath=str(f),load_ui=False,use_scripts=False)
base=json.loads((P/'protected_before.json').read_text());checks={n:sig(bpy.data.objects[n])==s for n,s in base.items()}
names=[o.name for o in bpy.context.scene.objects];old=[n for n in names if n not in base and not n.startswith('SC_')]
source=P/'reference/HALO9_INT21_M247C_OPEN_CIVIC_CANYON_RESEARCH.blend'
src=hashlib.sha256(source.read_bytes()).hexdigest()
r={'source_sha256':src,'source_unchanged':src=='9b950f0b9d5315605d5dc0bec252950e0c150739c94249a201667c9e2d675a27','W0_and_E11':checks,'old_architecture_in_scene':old,'independent_reopen':True,'blend_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'object_names':names,'function':'UNVERIFIED','art':'NOT_TESTED_BY_TECHNICAL_VERIFICATION'}
assert r['source_unchanged'] and all(checks.values()) and not old
(R/'INDEPENDENT_REOPEN.json').write_text(json.dumps(r,indent=2),encoding='utf8',newline='\n')
print('INDEPENDENT_SOURCE_W0_FIXED_E11_PASS',flush=True)
