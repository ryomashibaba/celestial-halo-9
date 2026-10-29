"""C55-C software rasterizer (visibility buffer). numpy only. Double-sided, near-plane clipped,
perspective-correct. Outputs per-pixel parent-triangle id + parent barycentrics + camera depth."""
import numpy as np

class Camera:
    def __init__(s, pos, target, fov=60.0, W=1280, H=720, up=(0,0,1)):
        s.pos=np.array(pos,float); t=np.array(target,float)
        f=t-s.pos; s.f=f/np.linalg.norm(f)
        r=np.cross(s.f,np.array(up,float)); s.r=r/np.linalg.norm(r)
        s.u=np.cross(s.r,s.f); s.W=W; s.H=H; s.fov=fov
        s.fpx=(H/2)/np.tan(np.radians(fov)/2)
    def to_cam(s,P):
        d=P-s.pos
        return np.stack([d@s.r,d@s.u,d@s.f],-1)

def clip_near(C,B,pid,near):
    z=C[:,:,2]; behind=z<near; nb=behind.sum(1)
    oC=[C[nb==0]]; oB=[B[nb==0]]; oI=[pid[nb==0]]
    m=nb==1
    if m.any():
        Cm=C[m];Bm=B[m];im=pid[m];k=np.argmax(behind[m],1)
        idx=(np.arange(3)[None,:]+k[:,None])%3; ar=np.arange(len(Cm))[:,None]
        Cm=Cm[ar,idx];Bm=Bm[ar,idx]
        def inter(b):
            t=(near-Cm[:,0,2])/(Cm[:,b,2]-Cm[:,0,2])
            return Cm[:,0]+(Cm[:,b]-Cm[:,0])*t[:,None], Bm[:,0]+(Bm[:,b]-Bm[:,0])*t[:,None]
        P1,Q1=inter(1);P2,Q2=inter(2)
        oC+= [np.stack([P1,Cm[:,1],Cm[:,2]],1),np.stack([P1,Cm[:,2],P2],1)]
        oB+= [np.stack([Q1,Bm[:,1],Bm[:,2]],1),np.stack([Q1,Bm[:,2],Q2],1)]
        oI+= [im,im]
    m=nb==2
    if m.any():
        Cm=C[m];Bm=B[m];im=pid[m];k=np.argmin(behind[m],1)
        idx=(np.arange(3)[None,:]+k[:,None])%3; ar=np.arange(len(Cm))[:,None]
        Cm=Cm[ar,idx];Bm=Bm[ar,idx]
        def inter(b):
            t=(near-Cm[:,0,2])/(Cm[:,b,2]-Cm[:,0,2])
            return Cm[:,0]+(Cm[:,b]-Cm[:,0])*t[:,None], Bm[:,0]+(Bm[:,b]-Bm[:,0])*t[:,None]
        P1,Q1=inter(1);P2,Q2=inter(2)
        oC.append(np.stack([Cm[:,0],P1,P2],1));oB.append(np.stack([Bm[:,0],Q1,Q2],1));oI.append(im)
    return np.concatenate(oC),np.concatenate(oB),np.concatenate(oI)

def rasterize(cam,V,F,near=3.0,budget=2_500_000,log=None):
    W,H=cam.W,cam.H
    Cv=cam.to_cam(V.astype(np.float64))
    Zf=Cv[F][:,:,2]
    # coarse reject: all behind near
    keep=(Zf>near).any(1)
    # coarse frustum reject using projected bbox for fully-in-front tris
    fid=np.nonzero(keep)[0]
    C=Cv[F[fid]]; pid=fid.astype(np.int32)
    B=np.broadcast_to(np.eye(3)[None],(len(fid),3,3)).copy()
    C,B,pid=clip_near(C,B,pid,near)
    X=W/2+cam.fpx*C[:,:,0]/C[:,:,2]; Y=H/2-cam.fpx*C[:,:,1]/C[:,:,2]; Z=C[:,:,2]
    ok=~((X.max(1)<0)|(X.min(1)>=W)|(Y.max(1)<0)|(Y.min(1)>=H))
    X,Y,Z,B,pid=X[ok],Y[ok],Z[ok],B[ok],pid[ok]
    den=(X[:,1]-X[:,0])*(Y[:,2]-Y[:,0])-(X[:,2]-X[:,0])*(Y[:,1]-Y[:,0])
    ok=np.abs(den)>1e-9
    X,Y,Z,B,pid,den=X[ok],Y[ok],Z[ok],B[ok],pid[ok],den[ok]
    x0=np.clip(np.floor(X.min(1)-0.5),0,W-1).astype(np.int32); x1=np.clip(np.ceil(X.max(1)-0.5),0,W-1).astype(np.int32)
    y0=np.clip(np.floor(Y.min(1)-0.5),0,H-1).astype(np.int32); y1=np.clip(np.ceil(Y.max(1)-0.5),0,H-1).astype(np.int32)
    s=np.maximum(x1-x0,y1-y0)+1
    zbuf=np.full(H*W,np.inf,np.float32); idb=np.full(H*W,-1,np.int32); bb=np.zeros((H*W,2),np.float32)
    if log: log(f"  raster: {len(pid)} screen tris")
    edges=[1,2,3,4,6,8,12,16,24,32,48,64]; prev=0
    def proc(sel,d):
        T=len(sel)
        for a in range(0,T,max(1,budget//(d*d))):
            t=sel[a:a+max(1,budget//(d*d))]
            ar=np.arange(d)
            px=(x0[t][:,None,None]+ar[None,None,:]+0.5)*np.ones((1,d,1)); py=(y0[t][:,None,None]+ar[None,:,None]+0.5)*np.ones((1,1,d))
            ax,ay=X[t,0][:,None,None],Y[t,0][:,None,None]
            e1x,e1y=(X[t,1]-X[t,0])[:,None,None],(Y[t,1]-Y[t,0])[:,None,None]
            e2x,e2y=(X[t,2]-X[t,0])[:,None,None],(Y[t,2]-Y[t,0])[:,None,None]
            dn=den[t][:,None,None]
            l1=((px-ax)*e2y-e2x*(py-ay))/dn; l2=(e1x*(py-ay)-(px-ax)*e1y)/dn; l0=1-l1-l2
            e=-1e-7
            m=(l0>=e)&(l1>=e)&(l2>=e)&(px<=x1[t][:,None,None]+1)&(py<=y1[t][:,None,None]+1)&(px<W)&(py<H)
            ti,jy,ix=np.nonzero(m)
            if len(ti)==0: continue
            L0,L1,L2=l0[ti,jy,ix],l1[ti,jy,ix],l2[ti,jy,ix]; tt=t[ti]
            iz=L0/Z[tt,0]+L1/Z[tt,1]+L2/Z[tt,2]; z=1/iz
            pb=np.stack([L0*z/Z[tt,0],L1*z/Z[tt,1],L2*z/Z[tt,2]],1)
            par=(pb[:,:,None]*B[tt]).sum(1)
            pix=(y0[tt]+jy).astype(np.int64)*W+(x0[tt]+ix)
            vis=z<zbuf[pix]
            if not vis.any(): continue
            pix,z,par,tt=pix[vis],z[vis],par[vis],tt[vis]
            o=np.argsort(-z,kind='stable'); pix,z,par,tt=pix[o],z[o],par[o],tt[o]
            zbuf[pix]=z; idb[pix]=pid[tt]; bb[pix]=par[:,:2]
    for d in edges:
        sel=np.nonzero((s>prev)&(s<=d))[0]; prev=d
        if len(sel): proc(sel,d)
    big=np.nonzero(s>64)[0]
    if log and len(big): log(f"  raster: {len(big)} large tris")
    for t in big:
        d=int(s[t]); proc(np.array([t]),d) if d<=1500 else None
    return zbuf.reshape(H,W),idb.reshape(H,W),bb.reshape(H,W,2)
