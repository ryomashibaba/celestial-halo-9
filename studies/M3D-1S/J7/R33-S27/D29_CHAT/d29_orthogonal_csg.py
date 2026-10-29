#!/usr/bin/env python3
"""D29 bounded *exact orthogonal* box subtraction from a saved GLB box mesh.

Not a general-purpose boolean, architecturally complete interior, or Minecraft importer.
Uses a globally partitioned 3D arrangement, emitting the actual boundary triangles of
remaining material, including the opening's inner surfaces. No untrusted mesh execution.
"""
import io, hashlib, json
from pathlib import Path
import numpy as np
import trimesh

TARGET='MASS_TEST'
PUBLIC='PUBLIC_APPROACH'
MAX_BOXES=3

def sha(data): return hashlib.sha256(data).hexdigest()

def box_mesh(bounds, color=(178,196,212,255)):
    bounds=np.asarray(bounds,dtype=float)
    m=trimesh.creation.box(extents=bounds[1]-bounds[0])
    m.apply_translation(bounds.mean(axis=0))
    m.visual.vertex_colors=np.tile(np.array(color,dtype=np.uint8),(len(m.vertices),1))
    return m

def fixture_glb():
    s=trimesh.Scene()
    mass=box_mesh([[-380,-240,0],[380,240,345]])
    approach=box_mesh([[-85,-335,37],[85,-238,40]],(115,201,197,255))
    s.add_geometry(mass,geom_name=TARGET,node_name=TARGET)
    s.add_geometry(approach,geom_name=PUBLIC,node_name=PUBLIC)
    return trimesh.exchange.gltf.export_glb(s)

def load_checked(raw):
    if len(raw)>16_000_000: raise ValueError('oversized source GLB')
    s=trimesh.load(io.BytesIO(raw),file_type='glb',force='scene',process=False)
    if set(s.geometry)!={TARGET,PUBLIC}:raise ValueError('unsupported source mesh set')
    if len(s.graph.nodes_geometry)!=2:raise ValueError('instancing unsupported')
    for node in s.graph.nodes_geometry:
        T,g=s.graph.get(node)
        if not np.allclose(T,np.eye(4)):raise ValueError('nonidentity transform')
    m=s.geometry[TARGET]
    if not m.is_watertight or not m.is_winding_consistent or m.volume<=0:
        raise ValueError('source mass not positive watertight solid')
    # exact orthogonal bounding box constraint: 8 unique corner positions, 12 faces.
    lo,hi=m.bounds
    if len(m.vertices)!=8 or len(m.faces)!=12:raise ValueError('target must be one rectangular solid')
    for vertex in m.vertices:
        if not np.all(np.isclose(vertex,lo,atol=1e-4)|np.isclose(vertex,hi,atol=1e-4)):
            raise ValueError('target is not an axis-aligned box')
    return s

def valid_voids(outer,boxes):
    if not isinstance(boxes,list) or not 1<=len(boxes)<=MAX_BOXES:raise ValueError('void count must be 1..3')
    lo,hi=np.asarray(outer,dtype=float)
    validated=[]
    for box in boxes:
        if not isinstance(box,dict) or set(box)!={'min','max'}:raise ValueError('bad void object')
        a,b=np.asarray(box['min'],dtype=float),np.asarray(box['max'],dtype=float)
        if a.shape!=(3,) or b.shape!=(3,) or not np.isfinite(a).all() or not np.isfinite(b).all():
            raise ValueError('invalid void coordinate')
        if np.any(b-a<5) or np.any(b-a>900):raise ValueError('void too thin or too large')
        if np.any(b<=lo) or np.any(a>=hi):raise ValueError('void misses mass')
        if np.any(a<-1500) or np.any(b>1500):raise ValueError('unsafe coordinate')
        validated.append((np.maximum(a,lo),np.minimum(b,hi)))
    # All void cells must be connected by positive-volume overlaps to an exterior
    # cut, not merely by a face, line or point that gives no practical passage.
    sources={i for i,(a,b) in enumerate(validated)
             if np.any(a<=lo+1e-6) or np.any(b>=hi-1e-6)}
    if not sources:raise ValueError('no exterior access to void')
    reached=set(sources)
    while True:
        expansion={i for i,(a,b) in enumerate(validated) if i not in reached and
           any(np.all(np.minimum(b,validated[j][1])-np.maximum(a,validated[j][0])>1e-5)
               for j in reached)}
        if not expansion:break
        reached.update(expansion)
    if len(reached)!=len(validated):raise ValueError('disconnected inner void')
    return validated

def carve_axis_box(outer, boxes):
    """Exact arrangement subtraction. Each exposed boundary is meshed at shared partition vertices."""
    lo,hi=np.asarray(outer,dtype=float)
    valid=valid_voids((lo,hi),boxes)
    axes=[]
    for j in range(3):
        coords=[float(lo[j]),float(hi[j])]
        for a,b in valid:coords.extend((float(a[j]),float(b[j])))
        axes.append(np.array(sorted(set(coords)),dtype=float))
    nx,ny,nz=(len(a)-1 for a in axes)
    if nx*ny*nz>512:raise ValueError('arrangement exceeds safe cell cap')
    occupied=np.ones((nx,ny,nz),dtype=bool)
    for i in range(nx):
      for j in range(ny):
       for k in range(nz):
        c=np.array([(axes[0][i]+axes[0][i+1])/2,(axes[1][j]+axes[1][j+1])/2,(axes[2][k]+axes[2][k+1])/2])
        if any(np.all(c>=a) and np.all(c<=b) for a,b in valid): occupied[i,j,k]=False
    if not occupied.any():raise ValueError('void consumed entire structural solid')
    names={};verts=[];faces=[]
    def vertex(p):
        key=tuple(float(v) for v in p)
        if key not in names:names[key]=len(verts);verts.append(key)
        return names[key]
    basis={
      (0,1):(1,2),(0,-1):(2,1),
      (1,1):(2,0),(1,-1):(0,2),
      (2,1):(0,1),(2,-1):(1,0)}
    shape=occupied.shape
    for i,j,k in np.argwhere(occupied):
        idx=np.array([i,j,k],dtype=int)
        lows=np.array([axes[0][i],axes[1][j],axes[2][k]])
        highs=np.array([axes[0][i+1],axes[1][j+1],axes[2][k+1]])
        for axis in range(3):
          for sign in (-1,1):
            neigh=idx.copy();neigh[axis]+=sign
            if np.all(neigh>=0) and np.all(neigh<shape) and occupied[tuple(neigh)]: continue
            u,v=basis[(axis,sign)]
            center=(lows+highs)/2
            center[axis]=highs[axis] if sign>0 else lows[axis]
            uvec=np.zeros(3);vvec=np.zeros(3)
            uvec[u]=(highs[u]-lows[u])/2;vvec[v]=(highs[v]-lows[v])/2
            quad=[vertex(center-uvec-vvec),vertex(center+uvec-vvec),vertex(center+uvec+vvec),vertex(center-uvec+vvec)]
            faces.append([quad[0],quad[1],quad[2]]); faces.append([quad[0],quad[2],quad[3]])
    m=trimesh.Trimesh(vertices=np.array(verts),faces=np.array(faces,dtype=int),process=False)
    # Export true triangle boundary, never overlay invisible / color-only holes.
    if not m.is_watertight or not m.is_winding_consistent or m.volume<=0:raise ValueError('carve produced invalid solid')
    m.visual.vertex_colors=np.tile(np.array([182,196,220,255],dtype=np.uint8),(len(m.vertices),1))
    return m

def carve_glb(raw,plan):
    if set(plan)!={'baseline_sha256','target_geometry','voids'}:raise ValueError('unknown or missing plan fields')
    if plan['baseline_sha256']!=sha(raw):raise ValueError('baseline SHA mismatch')
    if plan['target_geometry']!=TARGET:raise ValueError('unknown/protected target')
    sc=load_checked(raw)
    original_route=sc.geometry[PUBLIC].copy()
    sc.geometry[TARGET]=carve_axis_box(sc.geometry[TARGET].bounds,plan['voids'])
    if not np.array_equal(sc.geometry[PUBLIC].vertices,original_route.vertices):raise ValueError('public route moved')
    if not np.array_equal(sc.geometry[PUBLIC].faces,original_route.faces):raise ValueError('public route faces changed')
    out=trimesh.exchange.gltf.export_glb(sc)
    verify=trimesh.load(io.BytesIO(out),file_type='glb',force='scene',process=False)
    if set(verify.geometry)!={TARGET,PUBLIC} or not verify.geometry[TARGET].is_watertight:
        raise ValueError('GLB export invalid')
    return out

def run_cli():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('plan');ap.add_argument('output')
    a=ap.parse_args(); src=Path(a.source);dst=Path(a.output)
    if src.resolve()==dst.resolve() or dst.exists():raise ValueError('refuse source/output overwrite')
    b=src.read_bytes();p=json.loads(Path(a.plan).read_text('utf-8'));out=carve_glb(b,p)
    dst.write_bytes(out)
    print(json.dumps({'sha256':sha(out),'output':str(dst),'geometry_count':2},indent=2))
if __name__=='__main__':run_cli()
