#!/usr/bin/env python3
"""Topology-only route graph derived from physical path segments.
This is NOT a certified accessible route or full continuous collision proof.
"""
from pathlib import Path
import math,json,collections,heapq
import numpy as np
from d34_civic_section import PATH,BRANCH
OUT=Path(__file__).parent
roads=PATH+BRANCH
# split main segments at three intermediate branch locations for graph attachment
splits={
 'GROUND_ENTRY':[(-260.,-90.,0.)],
 'TOP_PROMENADE':[(190.,90.,16.)]
}
adj=collections.defaultdict(list)
for name,a,b in roads:
 nodes=[tuple(a)]+[tuple(t) for t in splits.get(name,[])]+[tuple(b)]
 for u,v in zip(nodes,nodes[1:]):
  cost=math.dist(u,v);adj[u].append((v,cost,name));adj[v].append((u,cost,name))
origin=(-300.,-90.,0.)
dist={origin:0.0};seen=set();pq=[(0.0,origin)]
while pq:
 d,u=heapq.heappop(pq)
 if u in seen:continue
 seen.add(u)
 for v,cost,_ in adj[u]:
  if d+cost<dist.get(v,float('inf'))-1.e-8:
   dist[v]=d+cost;heapq.heappush(pq,(d+cost,v))
ends={'G0':(-260.,-147.,0.),'G1':(-80.,-147.,8.),'G2':(190.,147.,16.)}
assert all(k in dist for k in ends.values())
# physically supported sampled path is tested in D34_QA.json, not here
res={'network_component_node_count':len(seen),'named_route_meshes':len(roads),'reachable_gallery_centers':{k:{'reachable':True,'network_path_m':round(dist[v],3)} for k,v in ends.items()},'connection_test':'design-network graph only; verify D34_QA.json for real GLB sampled surface support','not_proven':['continuous swept body','unbroken structural joints','elevator function','egress/building regulation']}
(OUT/'D34_ROUTE_GRAPH.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
