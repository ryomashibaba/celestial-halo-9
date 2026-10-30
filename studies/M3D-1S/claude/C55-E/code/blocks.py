"""Sheared slab blocks (not cuboids): base rectangle in the skin tangent plane, leans downstream with the flow, sloped roof, optional tiers."""
import numpy as np
def block_mesh(P,n,f,Lf,Wb,H,lean,rs):
    """P,n,f (M,3); Lf,Wb,H,lean,rs (M,). returns V (M*8,3), F (M*10,3). roof drops by rs*H at the downstream end."""
    M=len(P); b=np.cross(n,f); b/=np.maximum(np.linalg.norm(b,axis=1,keepdims=True),1e-9); f=np.cross(b,n); f/=np.maximum(np.linalg.norm(f,axis=1,keepdims=True),1e-9)
    sx=np.array([-1,1,1,-1.]); sy=np.array([-1,-1,1,1.])
    Bc=P[:,None,:]+f[:,None,:]*(sx[None,:,None]*Lf[:,None,None]/2)+b[:,None,:]*(sy[None,:,None]*Wb[:,None,None]/2)
    Hc=H[:,None]*(1-rs[:,None]*(sx[None,:]+1)/2)
    Tc=Bc+n[:,None,:]*Hc[...,None]+f[:,None,:]*(lean[:,None]*Hc/np.maximum(H[:,None],1e-6))[...,None]
    V=np.concatenate([Bc,Tc],1).reshape(-1,3); o=(np.arange(M)*8)[:,None]
    F=[o+np.array([[4,5,6]]),o+np.array([[4,6,7]])]
    for i in range(4):
        j=(i+1)%4; F+=[o+np.array([[i,j,4+j]]),o+np.array([[i,4+j,4+i]])]
    return V.astype(np.float32),np.concatenate([x.reshape(-1,3) for x in F])
def tier_tower(P,n,f,Lf,Wb,H,lean,tiers=((0.52,1.0),(0.30,0.68),(0.18,0.42))):
    """stack of 3 sheared tiers, each narrower and leaning more; returns list of (V,F)"""
    out=[];base=P.copy();acc=np.zeros(len(P))
    for fr,sc in tiers:
        h=H*fr; Pt=base.copy(); V,F=block_mesh(Pt,n,f,Lf*sc,Wb*sc,h,lean*fr*1.2,np.full(len(P),0.12)); out.append((V,F))
        base=base+n*h[:,None]+f*(lean*fr*1.2)[:,None]
    return out
