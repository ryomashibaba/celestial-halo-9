"""Inspect actual protected human-eye ray occlusion inside an existing INT4 BLEND.
Read-only native Blender scene diagnostic, no materials, geometry, cameras,
source file, or world are changed. Record actual hit objects for art surgery.
"""
import bpy,json,math,sys
from mathutils import Vector
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
output=Path(args[args.index('--output')+1])
output.parent.mkdir(parents=True,exist_ok=True)
sc=bpy.context.scene
view=bpy.context.evaluated_depsgraph_get()
results={}
for name in ('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL'):
    cam=bpy.data.objects[name]
    origin=cam.matrix_world.translation
    q=cam.matrix_world.to_quaternion()
    frame=cam.data.view_frame(scene=sc)
    h=max(abs(p.x/p.z) for p in frame)
    v=max(abs(p.y/p.z) for p in frame)
    record=[]
    for y in (-.75,-.35,0.,.35,.75):
        for x in (-.75,-.35,0.,.35,.75):
            local=Vector((x*h,y*v,-1.)).normalized()
            direction=q@local
            hit,pt,n,idx,obj,mat=sc.ray_cast(view,origin,direction,distance=5000)
            record.append(dict(x=x,y=y,object=obj.name if hit else 'SKY',
                distance=round((pt-origin).length,2) if hit else None,
                hit_xyz=[round(p,2) for p in pt] if hit else None))
    results[name]={
        'origin':[round(u,2) for u in origin],
        'center_hit':next(r for r in record if r['x']==0 and r['y']==0),
        'all_hits':record}
payload={'method':'ACTUAL_BLENDER_5_2_1_WORLD_RAYCAST_NOT_A_PICTURE_GUESS',
         'source_blend':Path(bpy.data.filepath).name,
         'results':results}
output.write_text(json.dumps(payload,indent=2),encoding='utf8')
for name,r in results.items():
    print('R1_REAL_CAMERA_RAYCAST',name,'CENTER',r['center_hit'],flush=True)
    summary={}
    for h in r['all_hits']:
        summary[h['object']]=summary.get(h['object'],0)+1
    print('R1_VIEW_HIT_OCCLUDERS',name,summary,flush=True)
print('R1_REAL_VIEW_DIAG_FINISHED',output,flush=True)
