"""Visual correction: resolve coincident prototype grounds and floating authored trees.
This is not a certification of all joints or walkable routes.
"""
import bpy,sys
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
bpy.ops.wm.open_mainfile(filepath=str(g.R/'model/R30_B.blend'));g.materials()
shifts=[]
for o in bpy.context.scene.objects:
    dz=-.4 if o.name.startswith('B_HORIZON_2190_FLOOR') or o.name=='B_REAL_LOW_FLOOR' else -.03 if o.name=='B east tidal route' else -1.6 if o.name=='B tidal public water' else 0
    if dz:o.location.z+=dz;shifts.append(dict(object=o.name,z_shift_m=dz))
for o in list(bpy.context.scene.objects):
    if o.type=='MESH' and o.get('study_group','').startswith('B') and o.name.startswith(('tree stems','canopy foliage')):g.remove(o)
bpy.context.view_layer.update();sc=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();trees=[]
g.GROUP='B_VERIFIED_GARDEN_THRESHOLDS'
for x,y,z in [(-2070,500,1000),(-1910,600,1000),(-1500,650,1000),(-600,920,2190),(0,1000,2190),(700,1000,2190),(140,1490,3020),(-1100,-180,105),(350,-1510,105)]:
    hit,p,n,f,o,m=sc.ray_cast(dg,Vector((x,y,z+3)),Vector((0,0,-1)),distance=4)
    if hit and abs(p.z-z)<.5 and 'water' not in o.name.lower():
        g.tree(x,y,p.z,22);trees.append(dict(position=list(p),actual_support=o.name))
g.flush();g.CHANGES.append({'visual_floor_overlap_repair':shifts,'tree_support_samples':trees,'scope':'Only obvious coincident public grounds seen in images, not all mesh intersections.'});g.save('B',6)
