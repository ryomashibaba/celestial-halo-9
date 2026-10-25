import bpy,json,hashlib,struct,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[1]
def signature(o):
 h=hashlib.sha256();h.update(bytes(str([list(v) for v in o.matrix_world]),'utf8'))
 for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
 for p in o.data.polygons:h.update(str(tuple(p.vertices)).encode())
 return h.hexdigest()
def load(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
 objects={o.name:signature(o) for o in s.objects if o.type=='MESH'}
 vs=[];fs=[];owners=[]
 for o in s.objects:
  if o.type!='MESH' or o.hide_render:continue
  off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);o.data.calc_loop_triangles()
  for t in o.data.loop_triangles:fs.append(tuple(off+i for i in t.vertices));owners.append(o.name)
 return BVHTree.FromPolygons(vs,fs,all_triangles=True),owners,objects
def ray(tree,owners,p,d,dist):
 q,n,i,t=tree.ray_cast(Vector(p),Vector(d).normalized(),dist)
 return None if i is None else dict(point=list(q),normal=list(n),distance=t,object=owners[i])
before,bnames,bs=load(R/'models/C55A_BEFORE.blend')
after,anames,asig=load(R/'models/C55A_R25_LOCAL_EDIT.blend')
sections=json.loads((R/'qa/EDIT_MANIFEST.json').read_text())['sections']
samples=[]
for a,b in zip(sections,sections[1:]):
 for j in range(max(1,math.ceil((b[0]-a[0])/2))):
  t=j/max(1,math.ceil((b[0]-a[0])/2));y=a[0]+t*(b[0]-a[0]);z=a[1]+t*(b[1]-a[1]);x=(a[2]+a[3]+t*((b[2]+b[3])-(a[2]+a[3])))/2
  for dx in [-1,0,1]:
   eye=(x+dx,y,z+1.7);floor=ray(after,anames,eye,(0,0,-1),2)
   clear=[ray(after,anames,eye,d,.5) for d in [(0,0,1),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]]
   samples.append(dict(eye=eye,floor=floor,supported=bool(floor and abs(floor['distance']-1.7)<.08),local_clear=not any(clear)))
aperture=[]
for x,z in [(-450,675),(-460,700),(-430,730)]:
 aperture.append(dict(start=[x,580,z],before=ray(before,bnames,(x,580,z),(0,1,0),100),after=ray(after,anames,(x,580,z),(0,1,0),100)))
ties=[]
for x,y in [(-450,585),(-410,980),(-410,986),(-385,986)]:
 ties.append(dict(x=x,y=y,before=ray(before,bnames,(x,y,671),(0,0,-1),150),after=ray(after,anames,(x,y,671),(0,0,-1),150)))
out=dict(source_sha256=hashlib.sha256((R.parent/'R21/models/C55A_IMPORTED.blend').read_bytes()).hexdigest(),
 source_unchanged=hashlib.sha256((R.parent/'R21/models/C55A_IMPORTED.blend').read_bytes()).digest()==hashlib.sha256((R/'models/C55A_BASELINE.blend').read_bytes()).digest(),
 changed_original_objects=[n for n in bs if bs[n]!=asig.get(n)],unchanged_original_count=sum(bs[n]==asig.get(n) for n in bs),
 aperture_samples=aperture,route_sample_count=len(samples),supported_count=sum(q['supported'] for q in samples),clear_count=sum(q['local_clear'] for q in samples),route_samples=samples,endpoint_samples=ties,
 limits='Finite center-lane floor/head/body samples only; no whole-space occupancy, mesh manifold, full accessible route, lower-city approach, egress, structural or safety certification.')
(R/'qa/LIMITED_GEOMETRY.json').write_text(json.dumps(out,indent=2),encoding='utf8')
# Deliver a faithful editable geometry export, including original materials; presentation-only lights/cameras excluded.
for o in bpy.context.scene.objects:o.select_set(o.type=='MESH' and not o.hide_render)
bpy.ops.export_scene.gltf(filepath=str(R/'models/C55A_R25_LOCAL_EDIT.glb'),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False)
print('LIMITED_QA',json.dumps({k:v for k,v in out.items() if k not in ['route_samples','endpoint_samples','aperture_samples']}),flush=True)
