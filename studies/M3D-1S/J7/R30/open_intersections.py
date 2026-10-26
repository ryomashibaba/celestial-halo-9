"""Fourth pass: remove intersecting parent masses across actual public rooms.
The v3 human images revealed that an adjacent pendant still obstructed the aperture.
"""
import bpy,sys,math
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
g.materials()
v='B'
bpy.ops.wm.open_mainfile(filepath=str(g.R/'model/R30_B.blend'));g.materials()
g.GROUP='B_REV4_ACTUAL_SHARED_CAVITY'
targets=['B inhabited horizon','B west suspended city','B central suspended city','B eastern suspended city','B lower lee inhabited reach']
g.cut_portal('B continuous actual west urban cavern',[(-2280,996),(-600,996),(-520,1490),(-960,1930),(-1710,2050),(-2180,1670)],'Y',-1500,3600,targets)
g.cut_portal('B all-mass horizon civic room',[(-850,2189),(980,2189),(1370,2470),(1230,2740),(500,2910),(-80,2900),(-680,2570)],'Y',-1500,3600,targets)
# Clear intersecting old roof strays above the inner walking axis, keeping the deliberately
# designed diagonal canopy and unequal public banks.
for o in list(bpy.context.scene.objects):
    if o.type=='MESH' and o.get('study_group','').startswith('B') and o.name.startswith(('tree stems','canopy foliage')):
        g.remove(o)
# These are on explicit, named flat deck polygons. Retained context foliage is untouched.
for x,y,z in [(-2070,500,1000),(-1910,600,1000),(-1500,650,1000),(-600,1080,2190),(0,1100,2190),(700,1100,2190),(140,1490,3020),(-1100,-180,105),(350,-1510,105)]:g.tree(x,y,z,22)
g.flush();bpy.context.view_layer.update()
sc=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();checks=[]
for name in ['03_PUBLIC','04_HUMAN','07_SKY_STREET']:
    cam=bpy.data.objects[name];eye=cam.location.copy();direction=(Vector(cam['target_m'])-eye).normalized()
    hit,p,n,f,o,m=sc.ray_cast(dg,eye,direction,distance=10000)
    checks.append(dict(camera=name,first_sight_hit=o.name if hit else None,distance_m=(p-eye).length if hit else None))
g.CHANGES.append({'visual_reason':'v3 near/far views remained blocked by a different original parent mass; actual apertures are now cut through ALL five intersecting primary bodies. Floating authored trees removed, replacement restricted to explicit deck datums. This is a geometry correction, separate from camera changes.','first_sight_rays':checks})
g.save('B',4)
