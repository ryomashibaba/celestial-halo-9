"""Read actual R28 BLEND and GLB before any architectural edits. R29 output only."""
import bpy, sys, json, hashlib
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode = True
R = Path(__file__).resolve().parent
S = R.parent / 'R28'
def bounds(o):
    v=[o.matrix_world @ Vector(p) for p in o.bound_box]
    return [[min(p[i] for p in v) for i in range(3)], [max(p[i] for p in v) for i in range(3)]]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(S/'model/R28_CELESTIAL_ESTUARY.blend'))
bpy.context.view_layer.update()
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
rows=[{'name':o.name,'group':o.get('study_group'), 'bbox_m':bounds(o),'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)} for o in sc.objects if o.type=='MESH']
samples=[]
for label,pt in [('forum',(550,-600,110)),('sea',(1000,-1100,110)),('reading',(1000,-960,124)),('upper',(860,230,655)),('B street',(2280,-769,810)),('east low',(850,0,450)),('east upper',(750,450,900))]:
    h,p,n,f,o,m=sc.ray_cast(dg,Vector(pt),Vector((0,0,-1)),distance=1000)
    samples.append({'label':label,'from':pt,'hit':o.name if h else None,'surface_m':list(p) if h else None})
probes=[]
for label,a,b in [('east cut',(300,0,300),(1200,0,300)),('upper sea view',(850,200,651.7),(2250,-650,850)),('forum east edge',(250,-600,106.7),(1050,-600,106.7)),('reading to forum',(650,-960,120.7),(500,-960,106.7))]:
    a,b=Vector(a),Vector(b);h,p,n,f,o,m=sc.ray_cast(dg,a,(b-a).normalized(),distance=(b-a).length)
    probes.append({'label':label,'start':list(a),'end':list(b),'first_hit':o.name if h else None,'hit_m':list(p) if h else None})
out={'source_blend_sha256':digest(S/'model/R28_CELESTIAL_ESTUARY.blend'),'source_glb_sha256':digest(S/'model/R28_CELESTIAL_ESTUARY.glb'),'blender':bpy.app.version_string,'objects':rows,'floor_samples':samples,'rays':probes}
print(json.dumps({'floors':samples,'rays':probes,'east':[r for r in rows if 'EAST' in r['name'] or 'B_HARBOR' in r['name'] or 'transit ' in r['name']]},indent=2),flush=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(S/'model/R28_CELESTIAL_ESTUARY.glb'))
out['source_glb_reload']={'meshes':sum(o.type=='MESH' for o in bpy.context.scene.objects),'triangles':sum(len(o.data.polygons) for o in bpy.context.scene.objects if o.type=='MESH')}
(R/'qa/SOURCE_GEOMETRY.json').write_text(json.dumps(out,indent=2),encoding='utf8')
