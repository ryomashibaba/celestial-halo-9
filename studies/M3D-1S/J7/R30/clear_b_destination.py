"""Final visual finding: the high destination still sits behind a parent-mass lip.
Open the actual shared route volume; move only the fifth north room to the back bank.
"""
import bpy,sys
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
bpy.ops.wm.open_mainfile(filepath=str(g.R/'model/R30_B.blend'));g.materials()
targets=['B inhabited horizon','B west suspended city','B central suspended city','B eastern suspended city','B lower lee inhabited reach']
revision=int(bpy.context.scene['revision'])
if revision<7:g.cut_portal('B real horizon-to-destination shared opening',[(-850,2189),(1880,2189),(2000,2530),(1780,2830),(1160,2930),(500,2910),(-80,2900),(-680,2570)],'Y',-1500,3600,targets)
moved=[]
for o in bpy.context.scene.objects:
    if revision<7 and o.type=='MESH' and o.name.startswith(('B northern city-room','B unequal north civic roofs','B civic front porch supports','B north public chamber real floors')):
        count=0
        for v in o.data.vertices:
            if v.co.x>750 and v.co.y>1100:v.co.y+=300;count+=1
        if count:o.data.update();moved.append(dict(object=o.name,vertices_moved=count,delta_y_m=300))
# The old ascending route crossed the new flat destination bridge at head height.
# Move its start to the south bank; its later crossing is now far above the flat route.
for o in list(bpy.context.scene.objects):
    if o.type=='MESH' and o.name.startswith('B horizon-to-highland public transit'):g.remove(o)
g.GROUP='B_FINAL_SEPARATED_HIGH_ROUTES'
g.ribbon('B horizon-to-highland public transit',g.catmull([(800,640,2190),(1080,660,2270),(1300,1020,2700),(1480,1560,3020)],14),70,14,'ivory',True)
g.flush()
bpy.context.view_layer.update();sc=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();rays=[]
for label,a,b in [('high street to bridge mouth',(-650,840,2191.7),(940,840,2191.7)),('bridge to destination',(940,840,2191.7),(1450,1300,2191.7))]:
    a,b=Vector(a),Vector(b);hit,p,n,f,o,m=sc.ray_cast(dg,a,(b-a).normalized(),distance=(b-a).length)
    rays.append(dict(label=label,start=list(a),end=list(b),first_hit=o.name if hit else None,hit_distance_m=(p-a).length if hit else None))
g.CHANGES.append({'visual_reason':'Final image still showed a blank inclined lip hiding the distant public room. Open five actual parent masses along high-street/destination volume, move fifth north room 300m to back bank. Common exterior and low cameras unchanged.','north_room_move':moved,'two_centerline_rays_only':rays})
g.save('B',8)
