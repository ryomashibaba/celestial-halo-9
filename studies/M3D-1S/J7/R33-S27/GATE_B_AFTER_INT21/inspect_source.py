import bpy, json, pathlib
from mathutils import Vector
root=pathlib.Path(__file__).parent
bpy.ops.wm.open_mainfile(filepath=str(root/'reference/HALO9_INT21_M247C_OPEN_CIVIC_CANYON_RESEARCH.blend'),load_ui=False,use_scripts=False)
items=[]
for o in bpy.context.scene.objects:
    bb=[o.matrix_world@Vector(v) for v in o.bound_box]
    items.append(dict(name=o.name,type=o.type,collections=[c.name for c in o.users_collection],bounds=[[min(v[i] for v in bb),max(v[i] for v in bb)] for i in range(3)]))
(root/'source_inventory.json').write_text(json.dumps(items,indent=2),encoding='utf8')
print('SOURCE_INSPECTED',len(items))
