#!/usr/bin/env python3
"""M109 early-stage macro centerline screening and SVG rendering. NON-CONSTRUCTION.
This does not load Minecraft worlds, validate real coordinates, or authorize any write.
"""
import json, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'design/drafts/M109_macro_alternatives.json'
def gap(theta, gaps):
    t=theta%(2*math.pi)
    return any((a<=t<=b) if a>=0 else (t>=2*math.pi+a or t<=b) for a,b in gaps)
def points(c,ring,steps=1440):
    rx,rz=c['ring_axes_m']; group=[]
    for i in range(steps+1):
        t=i*2*math.pi/steps
        if gap(t,ring['gap_rad']):
            if len(group)>=2:yield group
            group=[];continue
        x=rx*ring['scale']*math.cos(t);z=rz*ring['scale']*math.sin(t)
        h=ring['height_H']+ring['height_variation_H']*math.sin(t+ring['phase_rad'])
        group.append((x,z,h))
    if len(group)>=2:yield group
def segment_hits_rect(a,b,rect):
    # Liang-Barsky: exact crossing of the sampled segment against a site rectangle.
    x0,z0,x1,z1=rect;dx=b[0]-a[0];dz=b[1]-a[1];lo=0.;hi=1.
    for p,q in ((-dx,a[0]-x0),(dx,x1-a[0]),(-dz,a[1]-z0),(dz,z1-a[1])):
        if abs(p)<1e-12:
            if q<0:return False
            continue
        t=q/p
        if p<0:lo=max(lo,t)
        else:hi=min(hi,t)
        if lo>hi:return False
    return True
def screen(data):
    out={}
    for c in data['alternatives']:
        hits=set()
        for ring in c['rings']:
            for line in points(c,ring):
                for a,b in zip(line,line[1:]):
                    for site in data['sites']:
                        x0,z0,x1,z1=site['parcel']
                        if segment_hits_rect(a,b,(x0-3703.5,z0+2184.5,x1-3703.5,z1+2184.5)):
                            hits.add(site['id'])
        out[c['id']]=sorted(hits)
    return out
def plan_svg(data,c):
    # SVG is a comparative schematic. 16 parcel outlines are NOT accurate 3D meshes.
    W,H=1200,790
    conv=lambda x,z:(round(W/2+x*.78,2),round(H/2-(z*.78),2))
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">','<rect width="100%" height="100%" fill="#07141d"/>',
       f'<text x="55" y="63" fill="{c["color"]}" font-size="40" font-family="sans-serif" font-weight="bold">{c["title"]}</text>',
       '<text x="55" y="94" fill="#e6effa" font-size="17" font-family="sans-serif">M109 CONCEPT ONLY — MODEL H NOT MINECRAFT Y — NO CONSTRUCTION</text>']
    for site in data['sites']:
        x0,z0,x1,z1=site['parcel']
        a,b=conv(x0-3703.5,z0+2184.5);p,q=conv(x1-3703.5,z1+2184.5)
        color={'HERO':'#f4d892','CIVIC':'#79cce7','FRAME':'#7e9baa'}[site['kind']]
        s.append(f'<rect x="{a}" y="{q}" width="{p-a}" height="{b-q}" fill="{color}" fill-opacity=".19" stroke="{color}" stroke-opacity=".65" stroke-width="1"/>')
        mx,my=conv((x0+x1)/2-3703.5,(z0+z1)/2+2184.5)
        s.append(f'<text x="{mx}" y="{my}" fill="{color}" text-anchor="middle" font-size="15" font-family="sans-serif">{site["id"]}</text>')
    for i,ring in enumerate(c['rings']):
        for group in points(c,ring,720):
            pts=' '.join(f'{conv(x,z)[0]},{conv(x,z)[1]}' for x,z,h in group)
            s.append(f'<polyline points="{pts}" fill="none" stroke="{c["color"] if i==0 else "#e8f7ff"}" stroke-width="{8 if i==0 else 4}" stroke-opacity=".9" stroke-linecap="round"/>')
    s.append('<text x="55" y="753" fill="#a9bdc8" font-size="16" font-family="sans-serif">HERO4 golden / CIVIC4 cyan / FRAME8 grey blue — +X EAST right; +Z SOUTH down</text>')
    s.append('</svg>');return '\n'.join(s)+'\n'
if __name__=='__main__':
    data=json.loads(SOURCE.read_text(encoding='utf-8'))
    print(json.dumps(screen(data),ensure_ascii=False,indent=2))
    if '--render' in sys.argv:
        dst=ROOT/'visualization/m109'
        dst.mkdir(parents=True,exist_ok=True)
        for c in data['alternatives']:
            (dst/(c['id']+'.svg')).write_text(plan_svg(data,c),encoding='utf-8')
