import bpy,json,sys,shutil,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
src=R.parent/'R21/models/C55A_IMPORTED.blend'
dst=R/'models/C55A_BASELINE.blend'
shutil.copyfile(src,dst)
bpy.ops.wm.open_mainfile(filepath=str(dst))
s=bpy.context.scene
def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]
inventory=[dict(name=o.name,bounds=bounds(o),group=o.get('collection','')) for o in s.objects if o.type=='MESH']
arch=[o for o in s.objects if o.type=='MESH' and o.get('collection','') not in ['TERRAIN_CONTEXT','LIGHT_DECALS'] and o.get('material','')!='beam']
vs=[];fs=[];owners=[]
for o in arch:
 off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles()
 for t in o.data.loop_triangles:fs.append(tuple(off+i for i in t.vertices));owners.append(o.name)
b=BVHTree.FromPolygons(vs,fs,all_triangles=True)
def hits(p,d,length):
 p=Vector(p);d=Vector(d);out=[]
 for _ in range(25):
  q,n,i,t=b.ray_cast(p,d,length)
  if i is None:break
  out.append(dict(point=list(q),normal=list(n),name=owners[i]));p=q+d*.02
 return out
data=dict(source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),copy_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),inventory=inventory,
 probes={f'x{x}_z{z}':hits((x,100,z),(0,1,0),2400) for x in [-800,-600,-450,-250] for z in [440,460,500,550,600]},
 floors={f'x{x}_y{y}':hits((x,y,750),(0,0,-1),1000) for x in [-600,-450] for y in [300,400,500,600,700,800,900,1000,1100,1200]})
(R/'qa/INSPECT.json').write_text(json.dumps(data,indent=2),encoding='utf8')
print('INSPECTION_DONE',flush=True)
