"""Read-only R29 source inspection. Run using background Blender."""
import bpy, json, sys
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
(R/'qa').mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R.parent/'R29/model/R29_TIDAL_COMMONS.blend'))
bpy.context.view_layer.update()
rows=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH': continue
    pts=[o.matrix_world@Vector(p) for p in o.bound_box]
    rows.append(dict(name=o.name,group=o.get('study_group',''),bounds=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],vertices=len(o.data.vertices)))
(R/'qa/R29_INSPECTION.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
print('GROUPS',sorted(set(r['group'] for r in rows)),flush=True)
print('CAMERAS',[(o.name,list(o.location),o.data.lens) for o in bpy.context.scene.objects if o.type=='CAMERA'],flush=True)
print('LIGHTS',[(o.name,o.type) for o in bpy.context.scene.objects if o.type=='LIGHT'],flush=True)
print('RENDER',bpy.context.scene.render.engine, bpy.context.scene.cycles.device,flush=True)
try:
    cp=bpy.context.preferences.addons['cycles'].preferences
    cp.get_devices()
    print('DEVICES',[(d.name,d.type) for d in cp.devices],flush=True)
except Exception as e: print(type(e).__name__,str(e))
