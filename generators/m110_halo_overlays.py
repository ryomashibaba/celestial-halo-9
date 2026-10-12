#!/usr/bin/env python3
"""M110 pure-stdlib, NO-WORLD-WRITE procedural macro halo prototypes.
M101/frozen geometry and absolute Minecraft Y are NOT bundled in GitHub yet.
This CLI generates ONLY unapproved relative-H overlay JSON; no construction.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'design/drafts/M109_macro_alternatives.json'
CENTER=(3703.5,-2184.5)
WIDTH=30.0
CONSERVATIVE_BUFFER=18.5

def blocked(t,gaps):
    t=t%(2*math.pi)
    return any((t>=2*math.pi+a or t<=b) if a<0 else a<=t<=b for a,b in gaps)

def runs(option,ring,n=180):
    rx,rz=option['ring_axes_m']
    line=[]
    for i in range(n+1):
        t=i*2*math.pi/n
        if blocked(t,ring['gap_rad']):
            if len(line)>1:yield line
            line=[]
            continue
        x=CENTER[0]+rx*ring['scale']*math.cos(t)
        z=CENTER[1]+rz*ring['scale']*math.sin(t)
        h=ring['height_H']+ring['height_variation_H']*math.sin(t+ring['phase_rad'])
        line.append((x,z,h))
    if len(line)>1:yield line

def hit_rect(a,b,rect):
    """Line vs expanded parcel AABB; expansion is conservative for width."""
    x0,z0,x1,z1=rect
    dx=b[0]-a[0];dz=b[1]-a[1];lo=0.;hi=1.
    for p,q in ((-dx,a[0]-x0),(dx,x1-a[0]),(-dz,a[1]-z0),(dz,z1-a[1])):
        if abs(p)<1e-12:
            if q<0:return False
            continue
        t=q/p
        if p<0:lo=max(lo,t)
        else:hi=min(hi,t)
        if lo>hi:return False
    return True

def site_hits(options,sites,margin=CONSERVATIVE_BUFFER):
    results={}
    for o in options:
        hits=set()
        for ring in o['rings']:
            for line in runs(o,ring):
                for a,b in zip(line,line[1:]):
                    for s in sites:
                        x0,z0,x1,z1=s['parcel']
                        if hit_rect(a,b,(x0-margin,z0-margin,x1+margin,z1+margin)):
                            hits.add(s['id'])
        results[o['id']]=sorted(hits)
    return results

def prism(a,b,width,below,above,material,name):
    x,z,h=a;xx,zz,hh=b
    dx=xx-x;dz=zz-z;n=math.hypot(dx,dz)
    px=-dz/n*width/2;pz=dx/n*width/2
    v=[[x+px,z+pz,h-below],[x-px,z-pz,h-below],[xx-px,zz-pz,hh-below],[xx+px,zz+pz,hh-below],
       [x+px,z+pz,h+above],[x-px,z-pz,h+above],[xx-px,zz-pz,hh+above],[xx+px,zz+pz,hh+above]]
    f=[[0,1,2],[0,2,3],[4,6,5],[4,7,6],[0,4,5],[0,5,1],[1,5,6],[1,6,2],
       [2,6,7],[2,7,3],[3,7,4],[3,4,0]]
    return {'id':name,'material':material,'v':[[round(t,5) for t in q] for q in v],'f':f,
            'construction_approved':False,'structural_support_certified':False,'source':'M109'}

def overlay(option):
    result=[]
    for ring_num,ring in enumerate(option['rings']):
        for run_id,arc in enumerate(runs(option,ring)):
            for i,(a,b) in enumerate(zip(arc,arc[1:])):
                prefix='M110_'+option['id']+'_R'+str(ring_num)+'_A'+str(run_id)+'_S'+str(i)
                result.append(prism(a,b,WIDTH,11,0.7,'spine',prefix+'_DARK_DECK'))
                result.append(prism(a,b,20,0,3.1,'shell',prefix+'_LIGHT_SKIN'))
                result.append(prism(a,b,2.4,0,4,'cyan' if ring_num==0 else 'gold',prefix+'_LIGHT_TRACE'))
                if i%9==0:result.append(prism(a,b,36,16,-8.2,'structure',prefix+'_RIB'))
    return {'phase':'M110','candidate':option['id'],'status':'DRAFT_NONCONSTRUCTION_ONLY',
            'model_relative_H_not_actual_minecraft_Y':True,
            'construction_approved':False,'world_writes':0,'meshes':result}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output-dir',type=Path,help='Optional local export; never a world path')
    args=p.parse_args()
    data=json.loads(SOURCE.read_text())
    assert site_hits(data['alternatives'],data['sites'])=={o['id']:[] for o in data['alternatives']}
    summary={}
    for o in data['alternatives']:
        model=overlay(o)
        summary[o['id']]=len(model['meshes'])
        if args.output_dir:
            dest=args.output_dir.resolve()
            # This script is not a Minecraft construction API.
            if any(x.lower() in str(dest).lower() for x in ('minecraft','world','saves','schematics')):
                raise SystemExit('Refuse output under Minecraft-like paths')
            dest.mkdir(parents=True,exist_ok=True)
            (dest/(o['id']+'.json')).write_text(json.dumps(model,separators=(',',':')))
    print(json.dumps({'status':'NON_CONSTRUCTION','world_writes':0,
                      'relative_H_not_world_Y':True,'site_hits':site_hits(data['alternatives'],data['sites']),
                      'overlay_meshes':summary},indent=2))
if __name__=='__main__':main()
