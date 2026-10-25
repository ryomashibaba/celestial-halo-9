"""Inspect the saved final mesh, sample free-air connectivity and cross-world sightlines.
All results are samples. No enclosed cavity volume or complete walkability certificate.
"""
import bpy,sys,json,math,heapq
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'final/R19_LIVING_HORIZON.blend'));S=bpy.context.scene
verts=[];triangles=[];owners=[];centroids=[]
for o in bpy.data.collections['R19_LIVING_HORIZON'].objects:
 if o.type!='MESH':continue
 me=o.data;me.calc_loop_triangles();offset=len(verts);verts.extend([o.matrix_world@v.co for v in me.vertices])
 for t in me.loop_triangles:
  ids=tuple(offset+i for i in t.vertices);triangles.append(ids);owners.append(o.name);centroids.append(sum((verts[i] for i in ids),Vector())/3)
bvh=BVHTree.FromPolygons(verts,triangles,all_triangles=True)
def ray(p,d,dist=15000):
 hit,n,idx,t=bvh.ray_cast(Vector(p),Vector(d).normalized(),dist)
 return None if hit is None else dict(object=owners[idx],point_m=list(hit),normal=list(n),distance_m=t)
def clear(p,q,radius=0):
 p=Vector(p);q=Vector(q);d=q-p;length=d.length
 if length<.001:return True
 u=d.cross(Vector((0,0,1))).normalized();v=d.normalized().cross(u)
 offsets=[Vector((0,0,0))] if not radius else [Vector((0,0,0)),radius*u,-radius*u,radius*v,-radius*v]
 return all(ray(p+off,d,length-.05) is None for off in offsets)
out={'scope':'Actual world-space BVH of saved final architecture; finite ray samples only. Sky path is free air, not pedestrian access or enclosed volume.','cameras':{},'public_air_path':{}}
for name in ['08_LOW','09_MID','10_HIGH','11_REVERSE_CITY','13_HUMAN']:
 cam=bpy.data.objects.get(name)
 if not cam:continue
 p=cam.matrix_world.translation
 axes={str(d):ray(p,d) for d in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]}
 samples=[];prefixes={}
 # Subsample actual triangle centroids, test image inclusion and first-hit identity.
 for idx in range(0,len(centroids),max(1,len(centroids)//18000)):
  target=centroids[idx];co=world_to_camera_view(S,cam,target)
  if co.z<=0 or not (.06<co.x<.94 and .06<co.y<.94):continue
  d=target-p
  if not 150<d.length<7000:continue
  hit=ray(p,d,d.length+1)
  if hit and hit['object']==owners[idx] and abs(hit['distance_m']-d.length)<2:
   pre=owners[idx].split('_')[0]
   prefixes[pre]=prefixes.get(pre,0)+1
   if len(samples)<30:samples.append(dict(target_object=owners[idx],target_m=list(target),distance_m=d.length,normalized_image_xy=[co.x,co.y]))
 out['cameras'][name]=dict(position_m=list(p),six_axis_hits=axes,visible_actual_target_groups=prefixes,first_hit_sightline_samples=samples)

# Candidate open-air graph stays inside the central city envelope. Broad views
# alone cannot certify a connected bounded cavity, so preserve explicit samples.
nodes=[]
for x in [-850,-450,-50,350,750]:
 for y in [-1000,-600,-200,200,600,1000,1400]:
  for z in [650,1000,1350,1700,2050,2400,2750,3100]:
   p=Vector((x,y,z));nearest=bvh.find_nearest(p)
   if nearest[0] is None or nearest[3]<55:continue
   # A candidate must have at least three enclosing surfaces within 3500m.
   axes=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
   results=[ray(p,d,3500) for d in axes]
   # Conservative inside-solid rejection from outward first-hit normals.
   if any(hit and Vector(hit['normal']).dot(Vector(d))>.01 for d,hit in zip(axes,results)):continue
   hits=sum(hit is not None for hit in results)
   if hits>=3:nodes.append(p)
adj=[[] for _ in nodes]
for i,p in enumerate(nodes):
 for j in range(i+1,len(nodes)):
  q=nodes[j];dist=(q-p).length
  if dist<=650 and clear(p,q,25):adj[i].append((j,dist));adj[j].append((i,dist))
low=[i for i,p in enumerate(nodes) if p.z<=1000 and p.y<=-200]
high=set(i for i,p in enumerate(nodes) if p.z>=2750 and p.y>=200)
pq=[];best={};previous={}
for i in low:best[i]=0;heapq.heappush(pq,(0,i))
goal=None
while pq:
 dist,i=heapq.heappop(pq)
 if dist!=best[i]:continue
 if i in high:goal=i;break
 for j,w in adj[i]:
  nd=dist+w
  if nd<best.get(j,math.inf):best[j]=nd;previous[j]=i;heapq.heappush(pq,(nd,j))
route=[]
if goal is not None:
 i=goal
 while True:
  route.append(i)
  if i not in previous:break
  i=previous[i]
 route.reverse()
out['public_air_path']=dict(candidate_count=len(nodes),graph_edge_count=sum(map(len,adj))//2,low_to_high_sample_path_found=bool(route),points_m=[list(nodes[i]) for i in route],sample_offset_m=25,tested_parallel_rays_per_edge=5,edge_segments=[dict(a=list(nodes[i]),b=list(nodes[j]),clear_5_rays=clear(nodes[i],nodes[j],25)) for i,j in zip(route,route[1:])],cavity_volume_m3=None,cavity_volume_status='UNVERIFIED',walkability='UNVERIFIED')
cam=bpy.data.objects.get('13_HUMAN')
if cam:
 floor=ray(cam.matrix_world.translation,(0,0,-1),5)
 out['human_floor']=dict(camera_xyz_m=list(cam.matrix_world.translation),down_ray=floor,pass_1_7m_2mm=bool(floor and abs(floor['distance_m']-1.7)<.002 and floor['normal'][2]>.95))
(R/'qa/SPATIAL_SAMPLES.json').write_text(json.dumps(out,indent=2),encoding='utf8')
print(json.dumps({'public_air_path':out['public_air_path'],'human_floor':out.get('human_floor'), 'camera_visible_groups':{k:v['visible_actual_target_groups'] for k,v in out['cameras'].items()}},indent=2),flush=True)
