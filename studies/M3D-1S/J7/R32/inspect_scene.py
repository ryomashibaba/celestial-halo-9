import bpy,json,sys
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'model/R32_A.blend'))
bpy.context.view_layer.update();sc=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get()
for n in ('04_HUMAN','07_SKY_STREET'):
    o=bpy.data.objects[n];direction=o.matrix_world.to_quaternion()@Vector((0,0,-1))
    h,p,no,f,ob,m=sc.ray_cast(dg,o.location,direction,distance=5000)
    print(n,'eye',list(o.location),'first',ob.name if h else None,'distance',(p-o.location).length if h else None)
print('new mesh count',sum(o.type=='MESH' and str(o.get('study_group','')).startswith('R32_') for o in sc.objects))
for o in sc.objects:
    if o.type=='MESH' and not str(o.get('study_group','')).startswith('R32_') and 'R31' in o.name:print('LEFTOVER',o.name,o.get('study_group'))
