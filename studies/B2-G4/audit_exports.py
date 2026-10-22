"""Reload all three real GLBs in a disposable background Blender scene."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
result={}
for n in ['N1','N2','N3']:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.gltf(filepath=str(R/n/'study.glb'))
 objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
 bpy.context.view_layer.update()
 ps=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box]
 lo=[min(p[k] for p in ps) for k in range(3)];hi=[max(p[k] for p in ps) for k in range(3)]
 source=json.loads((R/n/'manifest.json').read_text(encoding='utf-8'))
 # Blender glTF importer restores Blender's Z-up coordinates. Curves become meshes,
 # so their bevels can add a few metres to bounds omitted by source mesh-only bbox.
 expected=source['bounds_m']
 delta=max(abs(lo[k]-expected['min'][k]) for k in range(3))
 delta=max(delta,max(abs(hi[k]-expected['max'][k]) for k in range(3)))
 assert delta<25,(n,delta,lo,hi,expected)
 assert len(objects)>0
 result[n]={'actual_glb_import':'PASS','mesh_objects':len(objects),'bounds_m':{'min':lo,'max':hi},'bounds_max_difference_m':delta,'note':'source bbox excludes curve bevels; world axes restored by glTF importer'}
(R/'glb_reload_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
