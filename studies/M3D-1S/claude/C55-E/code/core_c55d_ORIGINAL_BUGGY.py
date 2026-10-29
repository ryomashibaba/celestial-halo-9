"""C55-D core: mesh container, GLB I/O (numpy only), software renderer with multi-direction shadow maps.
Renderer = C55-D numpy rasterizer (visibility buffer; rasterize() reused from C55-C raster_c55c.py) + sun / sky-visibility shadow maps.
NOT Blender. NOT Cycles. Every report must say so."""
import numpy as np, json, struct, time, cv2
from raster_c55c import Camera, rasterize

class Mesh:
    """Accumulates (V,F,N) + per-triangle material id. Z-up, metres."""
    def __init__(s): s.V=[]; s.F=[]; s.N=[]; s.M=[]; s.n=0
    def add(s,V,F,N=None,mat=0,flat=False):
        V=np.asarray(V,np.float32); F=np.asarray(F,np.int64)
        if flat or N is None:
            A=V[F[:,0]];B=V[F[:,1]];C=V[F[:,2]]
            fn=np.cross(B-A,C-A); fn=fn/np.maximum(np.linalg.norm(fn,axis=1,keepdims=True),1e-12)
            k=len(F); V=np.concatenate([A,B,C]); N=np.concatenate([fn,fn,fn]); F=np.stack([np.arange(k),np.arange(k)+k,np.arange(k)+2*k],1)
        s.V.append(V); s.F.append(F+s.n); s.N.append(np.asarray(N,np.float32)); s.M.append(np.full(len(F),mat,np.int16)); s.n+=len(V)
    def done(s): return dict(V=np.concatenate(s.V),F=np.concatenate(s.F).astype(np.int32),N=np.concatenate(s.N),M=np.concatenate(s.M))

def grid_faces(nu,nv,wrap_u=False):
    i,j=np.meshgrid(np.arange(nu-(0 if wrap_u else 1)),np.arange(nv-1),indexing='ij'); i2=(i+1)%nu
    a=i*nv+j; b=i2*nv+j; c=i2*nv+j+1; d=i*nv+j+1
    return np.concatenate([np.stack([a,b,c],-1).reshape(-1,3),np.stack([a,c,d],-1).reshape(-1,3)])

def vertex_normals(V,F):
    V=V.astype(np.float64); A=V[F[:,0]];B=V[F[:,1]];C=V[F[:,2]]; fn=np.cross(B-A,C-A); N=np.zeros_like(V)
    for k in range(3): np.add.at(N,F[:,k],fn)
    return (N/np.maximum(np.linalg.norm(N,axis=1,keepdims=True),1e-12)).astype(np.float32)

def boxes(cx,cy,z0,w,d,h,rot=None):
    """boxes (top + 4 sides), unwelded by caller via Mesh.add(flat=True)."""
    n=len(cx); c=np.array([[-1,-1],[1,-1],[1,1],[-1,1]],np.float32)
    ox=c[None,:,0]*(w/2)[:,None]; oy=c[None,:,1]*(d/2)[:,None]
    if rot is not None:
        co=np.cos(rot)[:,None];si=np.sin(rot)[:,None]; ox,oy=ox*co-oy*si,ox*si+oy*co
    X=cx[:,None]+ox; Y=cy[:,None]+oy; zb=z0[:,None]*np.ones((1,4)); zt=(z0+h)[:,None]*np.ones((1,4))
    V=np.stack([np.concatenate([X,X],1),np.concatenate([Y,Y],1),np.concatenate([zb,zt],1)],-1).reshape(-1,3); base=(np.arange(n)*8)[:,None]; F=[]
    for q in [[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]:
        F+=[(base+np.array([[q[0],q[1],q[2]]])).reshape(-1,3),(base+np.array([[q[0],q[2],q[3]]])).reshape(-1,3)]
    return V.astype(np.float32),np.concatenate(F)

# ------------------------------------------------------------------ GLB
def read_glb(path,zup=True):
    d=open(path,'rb').read(); jl=struct.unpack('<I',d[12:16])[0]; g=json.loads(d[20:20+jl]); bo=20+jl; bl=struct.unpack('<I',d[bo:bo+4])[0]; b=d[bo+8:bo+8+bl]; out=[]
    def acc(i,dt,cnt):
        a=g['accessors'][i]; v=g['bufferViews'][a['bufferView']]; return np.frombuffer(b,dt,a['count']*cnt,v.get('byteOffset',0)+a.get('byteOffset',0))
    for me in g['meshes']:
        for p in me['primitives']:
            P=acc(p['attributes']['POSITION'],np.float32,3).reshape(-1,3).astype(np.float32); F=acc(p['indices'],np.uint32,1).reshape(-1,3).astype(np.int64)
            N=acc(p['attributes']['NORMAL'],np.float32,3).reshape(-1,3) if 'NORMAL' in p['attributes'] else None
            if zup:
                P=np.stack([P[:,0],-P[:,2],P[:,1]],1)
                if N is not None: N=np.stack([N[:,0],-N[:,2],N[:,1]],1)
            out.append((me['name'],P,F,N))
    return out

def write_glb(path,mesh,mat_defs,generator="C55-D numpy exporter (Claude Sonnet 5.5)"):
    V,F,N,M=mesh['V'],mesh['F'],mesh['N'],mesh['M']; chunks=[];views=[];acc=[];prims=[];mats=[]
    def add_buf(arr,target):
        bb=arr.tobytes(); off=sum(len(c) for c in chunks); chunks.append(bb+b'\0'*((-len(bb))%4)); views.append(dict(buffer=0,byteOffset=off,byteLength=len(bb),target=target)); return len(views)-1
    def add_acc(arr,ct,typ,target,mm=False):
        a=dict(bufferView=add_buf(arr,target),componentType=ct,count=len(arr),type=typ)
        if mm: a['min']=arr.min(0).tolist(); a['max']=arr.max(0).tolist()
        acc.append(a); return len(acc)-1
    yup=lambda A: np.stack([A[:,0],A[:,2],-A[:,1]],1).astype(np.float32)
    for mid,(name,base,met,rough,em) in mat_defs.items():
        sel=np.nonzero(M==mid)[0]
        if len(sel)==0: continue
        uniq,inv=np.unique(F[sel].ravel(),return_inverse=True)
        pa=add_acc(yup(V[uniq]),5126,"VEC3",34962,True); na=add_acc(yup(N[uniq]),5126,"VEC3",34962); ia=add_acc(inv.reshape(-1,3).astype(np.uint32).ravel(),5125,"SCALAR",34963)
        m=dict(name=name,pbrMetallicRoughness=dict(baseColorFactor=base,metallicFactor=met,roughnessFactor=rough),doubleSided=True)
        if max(em)>0: m['emissiveFactor']=em
        mats.append(m); prims.append(dict(name=name,primitives=[dict(attributes=dict(POSITION=pa,NORMAL=na),indices=ia,material=len(mats)-1)]))
    meshes=[dict(name=p['name'],primitives=p['primitives']) for p in prims]; nodes=[dict(name=p['name'],mesh=i) for i,p in enumerate(prims)]
    gl=dict(asset=dict(version="2.0",generator=generator),scene=0,scenes=[dict(nodes=list(range(len(nodes))))],nodes=nodes,meshes=meshes,materials=mats,accessors=acc,bufferViews=views,buffers=[dict(byteLength=sum(len(c) for c in chunks))])
    js=json.dumps(gl,separators=(',',':')).encode(); js+=b' '*((-len(js))%4); binb=b''.join(chunks)
    out=struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(binb))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(binb),0x004E4942)+binb
    open(path,'wb').write(out); return len(out)

# ------------------------------------------------------------------ lighting
def unit(v): v=np.asarray(v,float); return v/np.linalg.norm(v)

def shadow_map(V,F,L,center,radius,res):
    dist=80000.0; pos=center-unit(L)*dist; fov=np.degrees(2*np.arctan(radius/dist))
    cam=Camera(pos,center,fov,res,res,up=(0,0,1) if abs(L[2])<0.97 else (0,1,0))
    z,_,_=rasterize(cam,V,F,near=dist-radius*1.6,budget=2_000_000); return cam,z

def lookup_shadow(cam,zb,P,bias):
    bias=np.asarray(bias,np.float64)
    C=cam.to_cam(P.astype(np.float64)); z=C[:,2]; x=cam.W/2+cam.fpx*C[:,0]/z; y=cam.H/2-cam.fpx*C[:,1]/z
    xi=np.floor(x-0.5).astype(int); yi=np.floor(y-0.5).astype(int); inb=(x>=0)&(x<cam.W)&(y>=0)&(y<cam.H); vis=np.zeros(len(P),np.float32)
    for dx,dy in((0,0),(1,0),(0,1),(1,1)):
        vis+=(z-bias<=zb[np.clip(yi+dy,0,cam.H-1),np.clip(xi+dx,0,cam.W-1)]).astype(np.float32)
    vis/=4; vis[~inb]=1.0; return vis

def sky_dirs(n_ring=(6,6,3),elev=(18,45,75)):
    ds=[];w=[]
    for k,(nr,el) in enumerate(zip(n_ring,elev)):
        for i in range(nr):
            a=2*np.pi*(i+0.5*(k%2))/nr; e=np.radians(el); ds.append((np.cos(e)*np.cos(a),np.cos(e)*np.sin(a),np.sin(e))); w.append(np.sin(e)*np.cos(e)*(2*np.pi/nr)*(np.radians(30) if k<2 else np.radians(30)))
    d=np.array(ds); w=np.array(w); return d,w/w.sum()

class Light:
    """1 sun + K sky-direction shadow maps, computed once per scene."""
    def __init__(s,mesh,sun_dir,center,radius,res=1536,sky=(6,6,3),log=print):
        s.sun=unit(sun_dir); s.center=np.array(center,float); s.radius=radius; V,F=mesh['V'],mesh['F']
        t=time.time(); s.sun_map=shadow_map(V,F,s.sun,s.center,radius,res); log(f"  sun map {time.time()-t:.1f}s")
        s.dirs,s.w=sky_dirs(sky); s.sky_maps=[shadow_map(V,F,d,s.center,radius,res//2) for d in s.dirs]; log(f"  {len(s.dirs)} sky maps {time.time()-t:.1f}s total")
        s.ref=float((s.w*np.clip(s.dirs[:,2],0,1)).sum())
    def _bias(s,cam,c):
        tex=2*s.radius/cam.W; th=np.sqrt(np.clip(1-c*c,0,1))/np.maximum(c,0.12)
        return tex*(1.5+1.6*np.minimum(th,5.0))
    def sun_vis(s,P,ndl): return lookup_shadow(*s.sun_map,P,s._bias(s.sun_map[0],ndl))
    def sky_irr(s,P,N):
        acc=np.zeros(len(P),np.float32)
        for (cam,zb),d,w in zip(s.sky_maps,s.dirs,s.w):
            c=np.clip(N@d,0,1); m=c>1e-3
            if m.any(): acc[m]+=w*c[m]*lookup_shadow(cam,zb,P[m]+N[m]*10.0,s._bias(cam,c[m]))
        return acc/s.ref

# ------------------------------------------------------------------ render
MODES={
 'clay':dict(alb={'default':0.60,'ground':0.30},sun=(1.0,0.97,0.92),sunI=3.2,sky=(0.55,0.62,0.74),skyI=1.0,haze=(0.70,0.75,0.82),zen=(0.38,0.50,0.70),hor=(0.78,0.82,0.88),fog=1/22000.,fogH=1500.,expo=0.95,emis=False),
 'dusk':dict(alb={'default':0.30,'ground':0.14},sun=(1.0,0.60,0.34),sunI=3.2,sky=(0.16,0.24,0.46),skyI=0.8,haze=(0.40,0.30,0.38),zen=(0.015,0.035,0.12),hor=(0.78,0.42,0.30),fog=1/34000.,fogH=1200.,expo=1.0,emis=True,bloom=0.55),
}
def render(cam,mesh,light,mode='clay',ss=1,mat_info=None,near=2.0,log=print,ground=True,sun_disc=True):
    cfg=MODES[mode]; W,H=cam.W,cam.H; V,F,N,M=mesh['V'],mesh['F'],mesh['N'],mesh['M']
    t0=time.time(); zb,idb,bb=rasterize(cam,V,F,near=near,budget=2_500_000); log(f"   raster {time.time()-t0:.1f}s")
    hit=idb>=0; img=np.zeros((H,W,3),np.float32)
    # ray directions
    xs=(np.arange(W)+0.5-W/2)/cam.fpx; ys=-(np.arange(H)+0.5-H/2)/cam.fpx
    D=cam.f[None,None,:]+xs[None,:,None]*cam.r[None,None,:]+ys[:,None,None]*cam.u[None,None,:]; D/=np.linalg.norm(D,axis=2,keepdims=True)
    P=np.zeros((H,W,3),np.float64); Nn=np.zeros((H,W,3),np.float32); alb=np.full((H,W,3),cfg['alb']['default'],np.float32); em=np.zeros((H,W,3),np.float32); isg=np.zeros((H,W),bool)
    if hit.any():
        t=idb[hit]; b0=bb[...,0][hit]; b1=bb[...,1][hit]; b2=1-b0-b1; Fi=F[t]
        P[hit]=b0[:,None]*V[Fi[:,0]]+b1[:,None]*V[Fi[:,1]]+b2[:,None]*V[Fi[:,2]]
        n=b0[:,None]*N[Fi[:,0]]+b1[:,None]*N[Fi[:,1]]+b2[:,None]*N[Fi[:,2]]; n/=np.maximum(np.linalg.norm(n,axis=1,keepdims=True),1e-9)
        d=D[hit]; flip=(n*d).sum(1)>0; n[flip]*=-1; Nn[hit]=n
        mt=M[t]
        if mat_info is not None:
            for mid,inf in mat_info.items():
                s_=mt==mid
                if s_.any():
                    a=alb[hit]; a[s_]=inf.get(mode+'_alb',inf.get('alb',cfg['alb']['default'])); alb[hit]=a
                    if cfg['emis'] and 'emis' in inf:
                        e=em[hit]; e[s_]=np.array(inf['emis'],np.float32); em[hit]=e
    if ground:
        down=(~hit)&(D[...,2]<-1e-4)&(cam.pos[2]>0)
        tg=np.where(down,-cam.pos[2]/np.where(D[...,2]<-1e-4,D[...,2],-1),0); far=down&(tg<150000)
        P[far]=cam.pos[None,:]+D[far]*tg[far][:,None]; Nn[far]=(0,0,1); alb[far]=cfg['alb']['ground']; isg=far
    if isg.any():
        pg=P[isg]; dd=np.linalg.norm(pg-cam.pos,axis=1); fp=dd/cam.fpx
        mk=np.zeros(len(pg),np.float32)
        for ax in (0,1):
            f=np.abs(((pg[:,ax]/1000.0)%1.0)-0.5)*1000.0; f=500.0-f          # metres to nearest line
            w=np.maximum(5.0,fp*1.3); mk=np.maximum(mk,np.clip(1-f/w,0,1))
        fade=np.clip(1-(fp-60)/160,0,1); a=alb[isg]; a=a*(1-0.35*(mk*fade)[:,None]); alb[isg]=a
    surf=hit|isg
    ps=P[surf]; ns=Nn[surf]; a_=alb[surf]
    L=light.sun; ndl=np.clip(ns@L,0,1); sv=np.ones(len(ps),np.float32)
    m=ndl>0
    if m.any(): sv[m]=light.sun_vis(ps[m]+ns[m]*5.0,ndl[m])
    sirr=light.sky_irr(ps,ns)
    # screen-space AO (fine scale)
    z=np.where(hit,zb,1e9).astype(np.float32); zc=np.minimum(z,cam.fpx*50.0)
    ao=np.zeros((H,W),np.float32)
    for r in (3,9,24):
        bl=cv2.blur(zc,(2*r+1,2*r+1)); wr=r*zc/cam.fpx
        o=np.clip((zc-bl)/np.maximum(wr*1.2,1e-3),0,1)*((zc-bl)<wr*4); ao+=o/3
    aos=1-0.55*ao[surf]
    # bounce from ground onto downward faces
    bnc=np.clip(-ns[:,2],0,1)*0.55*(cfg['alb']['ground']+0.1)
    sun=np.array(cfg['sun'],np.float32); sky=np.array(cfg['sky'],np.float32)
    E=sun[None,:]*(cfg['sunI']*ndl*sv)[:,None]+sky[None,:]*(cfg['skyI']*sirr*aos)[:,None]+(sun*cfg['sunI']*0.15+sky*0.4)[None,:]*(bnc*aos)[:,None]+0.015
    col=a_*E
    if cfg['emis']: col=col+em[surf]*(0.55+0.45*aos[:,None])
    img[surf]=col
    # sky
    sk=~surf; dz=np.clip(D[...,2],-1,1)
    tt=np.clip(dz,0,1)**0.45; zen=np.array(cfg['zen'],np.float32); hor=np.array(cfg['hor'],np.float32)
    sky_img=hor[None,None,:]*(1-tt[...,None])+zen[None,None,:]*tt[...,None]
    if mode=='dusk' or sun_disc:
        cs=np.clip((D@light.sun),0,1); sky_img=sky_img+np.array(cfg['sun'],np.float32)[None,None,:]*((cs**64)*0.5+(cs**2000)*6.0)[...,None]
    img[sk]=sky_img[sk]
    # height fog (analytic integral)
    dist=np.where(hit,np.linalg.norm(P-cam.pos,axis=2),np.where(isg,np.linalg.norm(P-cam.pos,axis=2),150000.))
    z0=cam.pos[2]; z1=np.where(surf,P[...,2],z0+D[...,2]*150000.); Hh=cfg['fogH']
    dzz=(z1-z0); k=np.where(np.abs(dzz)>1e-3,(np.exp(-z0/Hh)-np.exp(-z1/Hh))/np.where(np.abs(dzz)>1e-3,dzz/Hh,1),np.exp(-z0/Hh))
    tau=cfg['fog']*dist*np.clip(k,0,1.5); T=np.exp(-tau)[...,None]
    haze=np.array(cfg['haze'],np.float32); img=img*T+haze[None,None,:]*(1-T)
    if cfg.get('bloom'):
        br=np.clip(img-0.9,0,None)
        bl=cv2.GaussianBlur(br,(0,0),sigmaX=max(3,W/220))*0.7+cv2.GaussianBlur(br,(0,0),sigmaX=max(8,W/70))*0.9
        img=img+bl*cfg['bloom']
    # tonemap
    x=img*cfg['expo']; x=x*(1+x/6.0)/(1+x); x=np.clip(x,0,None)**(1/2.2)
    out=(np.clip(x,0,1)*255).astype(np.uint8)[...,::-1]; log(f"   total {time.time()-t0:.1f}s")
    return out
