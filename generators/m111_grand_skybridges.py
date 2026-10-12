#!/usr/bin/env python3
"""M111 outer halo civic viaducts and skyline cradles — NON-CONSTRUCTION.
No world read/write APIs, no deployment endpoints, no absolute Minecraft Y.
Reference geometry is relative-H only. Exact frozen-mesh audit must be performed
separately using immutable M107 files not yet present in this GitHub repository.
"""
from __future__ import annotations
from pathlib import Path
import argparse, json, math
from generators.m110_halo_overlays import SOURCE, CENTER, runs, prism
ROOT=Path(__file__).resolve().parents[1]
KINDS={'SB05':'HERO','SB08':'HERO','SB09':'HERO','SB12':'HERO'}
VARIANTS=('MONUMENTAL_DARK_PORTALS','LUMINOUS_SKYFANS')
def prism_box(x,z,low,xx,zz,high,material,name):
    v=[[x,z,low],[xx,z,low],[xx,zz,low],[x,zz,low],
       [x,z,high],[xx,z,high],[xx,zz,high],[x,zz,high]]
    f=[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],
       [1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]
    return {'id':name,'material':material,'v':[[round(p,5) for p in v0] for v0 in v],
            'f':f,'construction_approved':False,'world_absolute_y_known':False,'load_path_certified':False}
def beam(a,b,width,below,above,material,name):
    p=prism(a,b,width,below,above,material,name)
    p.update(construction_approved=False,world_absolute_y_known=False,load_path_certified=False)
    return p
def interp(a,b,t):
    return tuple(a[i]*(1-t)+b[i]*t for i in range(3))
def option_b():
    data=json.loads(SOURCE.read_text(encoding='utf8'))
    return data,next(o for o in data['alternatives'] if o['id']=='B_ASCENDING_RIFT')
def endpoints(data,opt):
    out=[]
    nodes=[v for run in runs(opt,opt['rings'][0],n=150) for v in run]
    for fid in ('SB05','SB08','SB09','SB12'):
        s=next(x for x in data['sites'] if x['id']==fid)
        x0,z0,x1,z1=s['parcel']
        center=((x0+x1)/2,(z0+z1)/2)
        target=min(nodes,key=lambda p:(p[0]-center[0])**2+(p[1]-center[1])**2)
        tx,tz,h=target
        dz=tz-center[1]
        edge=z0 if dz<0 else z1
        t=min((abs(edge-center[1])+16.)/abs(dz),.85)
        a=(center[0]+(tx-center[0])*t,center[1]+dz*t,h)
        b=(tx,tz,h)
        span=math.hypot(tx-a[0],tz-a[1])
        out.append({'fid':fid,'a':a,'b':b,'bridge_length_m':round(span,2),
                    'ring_relative_H':round(h,2),'parcel_to_bridge_gap_m':16,
                    'existing_building_interface_built':False,'verified_minecraft_Y':False})
    return out
def build(data,opt,variant):
    if variant not in VARIANTS:raise ValueError(variant)
    meshes=[]
    for bridge in endpoints(data,opt):
        fid=bridge['fid'];a=bridge['a'];b=bridge['b'];tag='M111_'+variant+'_'+fid
        for i in range(12):
            p0,p1=interp(a,b,i/12),interp(a,b,(i+1)/12)
            if variant=='MONUMENTAL_DARK_PORTALS':
                meshes.append(beam(p0,p1,40,9.5,1,'spine',tag+f'_CAUSEWAY_{i:02d}'))
                meshes.append(beam(p0,p1,30,0,4,'shell',tag+f'_BRIGHT_DECK_{i:02d}'))
                if i%3==0:meshes.append(beam(p0,p1,47,21,-8,'structure',tag+f'_DEEP_RIB_{i:02d}'))
            else:
                meshes.append(beam(p0,p1,34,7.5,1,'spine',tag+f'_DARK_RIBBON_{i:02d}'))
                meshes.append(beam(p0,p1,25,0,3.5,'shell',tag+f'_WHITE_DECK_{i:02d}'))
                if i%3==0:meshes.append(beam(p0,p1,47,19,-10,'structure',tag+f'_SPLAY_{i:02d}'))
        if variant=='MONUMENTAL_DARK_PORTALS':
            stations=[a,interp(a,b,.58)]
            for k,(x,z,h) in enumerate(stations):
                root=f'{tag}_PORTAL{k}'
                meshes.append(prism_box(x-12,z-12,max(5,h-87),x+12,z+12,h+39,'structure',root+'_DARK'))
                meshes.append(prism_box(x-17,z-7,h+24,x+17,z+7,h+42,'shell',root+'_CROWN'))
                meshes.append(prism_box(x-20,z-4,h+40,x+20,z+4,h+44,'gold',root+'_LIGHT'))
        else:
            stations=[interp(a,b,t) for t in (.15,.58)]
            for k,(x,z,h) in enumerate(stations):
                root=f'{tag}_SKYFAN{k}'
                meshes.append(prism_box(x-9,z-9,max(5,h-66),x+9,z+9,h+13,'structure',root+'_CORE'))
                meshes.append(prism_box(x-18,z-4,h+11,x+18,z+4,h+52,'shell',root+'_SAIL'))
                meshes.append(prism_box(x-19,z-2,h+51,x+19,z+2,h+56,'cyan',root+'_LIGHT'))
    # Full ring visual piers: NOT actual verified structural columns or ground anchors.
    for ri,ring in enumerate(opt['rings']):
        for index,arc in enumerate(runs(opt,ring,n=150)):
            for nth in range(1,5):
                x,z,h=arc[round(len(arc)*nth/5)]
                if h<30:continue
                tag=f'M111_{variant}_R{ri}_ARC{index}_OUTER{nth}'
                if variant=='MONUMENTAL_DARK_PORTALS':
                    meshes.append(prism_box(x-15,z-15,10,x+15,z+15,h+12,'structure',tag+'_DARK_PIER'))
                    meshes.append(prism_box(x-28,z-10,h-17,x+28,z+10,h+17,'spine',tag+'_YOKE'))
                    meshes.append(prism_box(x-32,z-6,h+8,x+32,z+6,h+21,'shell',tag+'_LIGHT_CROWN'))
                    meshes.append(prism_box(x-33,z-2,h+20,x+33,z+2,h+25,'gold',tag+'_BEACON'))
                else:
                    meshes.append(prism_box(x-12,z-12,10,x+12,z+12,h+7,'spine',tag+'_DARK_PIER'))
                    meshes.append(prism_box(x-9,z-25,h-21,x+9,z+25,h+28,'shell',tag+'_FIN'))
                    meshes.append(prism_box(x-5,z-30,h+23,x+5,z+30,h+31,'cyan',tag+'_FIN_LIGHT'))
                    meshes.append(prism_box(x-23,z-8,h-13,x+23,z+8,h-5,'structure',tag+'_SPREADER'))
    return {'phase':'M111','variant':variant,'status':'RESEARCH_ONLY','parent_option':'B_ASCENDING_RIFT',
            'comparison_baseline':'M101_UNMODIFIED','relative_H_not_actual_world_Y':True,
            'world_writes':0,'construction_approved':False,
            'four_bridges':endpoints(data,opt),'meshes':meshes,
            'remaining_critical_gaps':['16m+ protected building interface at each HERO site',
                                       'Unverified vertical circulation/elevators',
                                       'Real terrain and outer mast foundations',
                                       'Planning extent and actual Minecraft absolute Y',
                                       'Exact collisions with all 88 reserved void volumes']}
def main():
    p=argparse.ArgumentParser();p.add_argument('--output-dir',type=Path)
    args=p.parse_args()
    data,opt=option_b()
    summaries={}
    for variant in VARIANTS:
        model=build(data,opt,variant)
        summaries[variant]={'meshes':len(model['meshes']),
                            'outboard_bridges':len(model['four_bridges']),
                            'all_actual_building_interfaces_connected':False,
                            'construction_approved':False}
        if args.output_dir:
            folder=args.output_dir.resolve()
            if any(x in str(folder).lower() for x in ('minecraft','saves','schematic','world')):
                raise SystemExit('Output destination may not be a Minecraft/world path')
            folder.mkdir(parents=True,exist_ok=True)
            (folder/('M111_'+variant+'.json')).write_text(json.dumps(model,ensure_ascii=False))
    print(json.dumps({'status':'NON_CONSTRUCTION','proposals':summaries,'world_writes':0},indent=2))
if __name__=='__main__':main()
