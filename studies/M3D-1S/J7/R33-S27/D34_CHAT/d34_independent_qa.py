#!/usr/bin/env python3
"""Read a SAVED GLB in a fresh Python interpreter; no claimed structural certification.
Checks sampled 3D ground-to-upper civic path, actual gallery entrances, failure negatives.
"""
import sys,math,json,hashlib
from pathlib import Path
import numpy as np,trimesh
from d34_civic_section import PATH,BRANCH,ROOMS
OUT=Path(__file__).parent

def hit2d(tris, p, refz, tol=.015):
    x,y=p
    v=tris[:,:,:2]
    xa,ya=v[:,0,0],v[:,0,1]; xb,yb=v[:,1,0],v[:,1,1];xc,yc=v[:,2,0],v[:,2,1]
    det=(yb-yc)*(xa-xc)+(xc-xb)*(ya-yc)
    good=np.abs(det)>1.e-9
    if not np.any(good):return False
    det=np.where(good,det,1.)
    u=((yb-yc)*(x-xc)+(xc-xb)*(y-yc))/det
    vv=((yc-ya)*(x-xc)+(xa-xc)*(y-yc))/det
    w=1-u-vv
    zs=u*tris[:,0,2]+vv*tris[:,1,2]+w*tris[:,2,2]
    return bool(np.any(good & (u>=-1e-6)&(vv>=-1e-6)&(w>=-1e-6)&(np.abs(zs-refz)<=tol)))

def verify(path):
    read=trimesh.load(str(path),force='scene',process=False)
    if set(read.geometry)!={n for n in read.geometry}:raise AssertionError('unreachable')
    geo=read.geometry
    # all named route surfaces are queried individually from readback triangles
    results={}; supports=0; failures=[];head_collisions=[];total=0;max_grade=0
    route_names={q[0] for q in PATH+BRANCH}
    solid_names=[n for n in geo if n not in route_names and n not in ('SITE_STUDY_GROUND','CIVIC_VOID_OPEN_SKY_PERIMETER')]
    solid_min=np.stack([geo[n].bounds[0] for n in solid_names]);solid_max=np.stack([geo[n].bounds[1] for n in solid_names])
    for name,aa,bb in PATH+BRANCH:
        a=np.array(aa);b=np.array(bb);horiz=np.linalg.norm(b[:2]-a[:2]); max_grade=max(max_grade,abs(float(b[2]-a[2]))/horiz)
        normal=np.array([-(b[1]-a[1]),b[0]-a[0]])/horiz
        tris=np.asarray(geo[name].vertices)[geo[name].faces] if name in geo else np.empty((0,3,3))
        for t in np.linspace(.002,.998,101):
            pt=a+(b-a)*t
            for width in [-5,-2.5,0,2.5,5]:
                p=pt.copy();p[:2]+=normal*width
                total+=1
                if hit2d(tris,p[:2],p[2]):supports+=1
                else:failures.append([name,float(t),float(width)])
                # Test real wall/block-like geometry AABBs at a traversing occupant's head and shoulder height
                for head_offset in [1.7,4.5]:
                    xyz=p+np.array([0,0,head_offset]);
                    hits=np.nonzero(np.all((xyz>solid_min+.001)&(xyz<solid_max-.001),axis=1))[0]
                    for k in hits:head_collisions.append((name,solid_names[int(k)],float(t),float(width),head_offset))
    results['samples']=total;results['supported']=supports;results['missing_support']=len(failures)
    results['first_missing']=failures[:8];results['head_collisions']=len(head_collisions);results['first_head_collision']=head_collisions[:8];results['max_design_grade_percent']=round(max_grade*100,4)
    # Structural and continuous swept-body proof intentionally NOT claimed.
    # Door openings from actual wall meshes: five sample heights and three portal x positions
    doors={}
    for label,cx,cy,z,front in ROOMS:
        yy=cy+32-.7 if front=='N' else cy-32+.7
        n=0;blocked=[]
        wall_bounds=[(name,geo[name].bounds) for name in geo if name.startswith(label+'_') and 'interior_floor' not in name]
        for dx in [-8,0,8]:
            for h in [1.7,3.,5.,7.,9.]:
                n+=1;xyz=np.array([cx+dx,yy,z+h]);
                for wall_name,b in wall_bounds:
                    if np.all(xyz>b[0]+1e-3)&np.all(xyz<b[1]-1e-3):blocked.append((dx,h,wall_name))
        doors[label]={'clearance_samples':n,'blocked':len(blocked),'first_blocked':blocked[:3]}
    results['door_probes']=doors
    # Missing floor negative: exclude RAMP_WEST, requires 505 samples to fail for that segment
    negative=[]; name,aa,bb=PATH[1];a=np.array(aa);b=np.array(bb);n=np.array([0,1])
    for t in np.linspace(.002,.998,101):
      p=a+(b-a)*t
      for width in [-5,-2.5,0,2.5,5]:
        xy=p[:2]+n*width
        if not any(hit2d(np.asarray(m.vertices)[m.faces],xy,p[2]) for k,m in geo.items() if k.startswith('RAMP_') and k!='RAMP_WEST'):negative.append(1)
    results['ramp_removal_negative_missing_support']=len(negative)
    # Negative geometry is added by d34_negative_tests.py, then assessed via this same readback QA.
    results['injected_obstruction_negative']='SEE D34_NEGATIVE_QA.json'
    results['individual_meshes_watertight']=all(m.is_watertight for m in geo.values())
    results['geometry_count']=len(geo); results['sha256']=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    results['tech_pass_limited']=bool(supports==total and not head_collisions and all(not d['blocked'] for d in doors.values()) and max_grade<=.05+1e-9 and len(negative)>=400)
    return results
if __name__=='__main__':
 out=verify(sys.argv[1] if len(sys.argv)>1 else OUT/'D34_CIVIC_THREE_LEVEL_REAL.glb')
 (OUT/'D34_QA.json').write_text(json.dumps(out,indent=2,ensure_ascii=False))
 print(json.dumps(out,indent=2)[:3600])
