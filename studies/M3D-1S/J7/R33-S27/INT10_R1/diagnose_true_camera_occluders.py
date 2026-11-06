"""Image-led actual-camera obstruction diagnosis in original INT10 BLEND.
Find concrete blocking meshes *before* touching more protected terrain.
This is an instrument in the real city model, not new visual QA evidence.
"""
import bpy,hashlib,json,sys,collections,math
from pathlib import Path
from mathutils import Vector
a=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(a[a.index('--output')+1]);out.mkdir(parents=True,exist_ok=True)
src=Path(bpy.data.filepath)
sha="b5a38f353c814acaade8848ca420c3a38cfa724e41a1aafeb07a071244c6c94e"
assert src.name=="INT10_R1_SOURCE.blend" and hashlib.sha256(src.read_bytes()).hexdigest()==sha
sc=bpy.context.scene
assert sc['CONSTRUCTION']=='HOLD' and sc['FORMAL_ART_ACCEPTED']==sc['COMPLETED_TARGETS']==0
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
def trace(c,u,v):
    frame=c.data.view_frame(scene=sc)
    x=[z.x for z in frame];y=[z.y for z in frame]
    loc=Vector((min(x)+u*(max(x)-min(x)),min(y)+v*(max(y)-min(y)),sum(z.z for z in frame)/len(frame)))
    origin=c.matrix_world.translation
    direction=(c.matrix_world.to_3x3()@loc).normalized()
    hit,p,n,idx,target,m=sc.ray_cast(dg,origin,direction,distance=6000)
    return {'u':u,'v':v,'name':target.name if hit else 'SKY',
        'distance':round((p-origin).length,2) if hit else None}
names=['E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL']
views={}
for n in names:
    cam=bpy.data.objects[n]
    grid=[trace(cam,u,v) for v in (.1,.3,.5,.7,.9) for u in (.1,.3,.5,.7,.9)]
    counts=collections.Counter(x['name'] for x in grid)
    distances={}
    for item in grid:
        if item['distance'] is not None:
            distances.setdefault(item['name'],[]).append(item['distance'])
    views[n]={
      'camera_xyz':list(cam.matrix_world.translation),
      'grid':grid,
      'counts':counts.most_common(12),
      'ranges':{name:[min(ds),max(ds)] for name,ds in distances.items()},
    }
    print('INT10_R1_REAL_CAMERA_HITS',n,views[n]['counts'],flush=True)
road={}
for n in ('INT10_W0_MARITIME_CIVIC_APPROACH','INT10_H1_HIGH_CITY_INHABITED_MARKET_STREET'):
    obj=bpy.data.objects[n]
    road[n]={
       'vertices':len(obj.data.vertices),
       'positions':[[round(float(v.co.x),2),round(float(v.co.y),2),round(float(v.co.z),2)] for v in obj.data.vertices[0:32]],
    }
old=[x.name for x in sc.objects if x.type=='MESH' and
     not x.name.startswith(('INT10_','INT7_'))]
r={'schema':'halo9-int10-r1-actual-image-occlusion-probe-v1',
   'source_sha256':sha,
   'camera_hits':views,
   'road_initial_vertices':road,
   'old_context_mesh_count':len(old),
   'old_context_names':old,
   'formal_art_accepted':0,'completed_targets':0,'minecraft':'HOLD',
   'art':'UNREVIEWED_NOT_ADOPTED'}
(out/'TRUE_IMAGE_OCCLUSION_DIAG.json').write_text(json.dumps(r,indent=2),encoding='utf8')
print('INT10_R1_ACTUAL_3D_OCCLUSION_PROBE_COMPLETE',flush=True)
