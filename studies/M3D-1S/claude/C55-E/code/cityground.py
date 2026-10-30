import numpy as np
from core import boxes
def ground_city(allow,seed=7,R=11000.,pitch=360.,hscale=1.0):
    """generic low-rise ground field (scale reference only). allow(x,y)->(keep_mask,hmul)"""
    rng=np.random.default_rng(seed); g=np.arange(-R,R+1,pitch); X,Y=np.meshgrid(g,g); X=X.ravel();Y=Y.ravel()
    X=X+rng.uniform(-0.12,0.12,len(X))*pitch; Y=Y+rng.uniform(-0.12,0.12,len(Y))*pitch
    r=np.hypot(X,Y); k=(r<R)&(rng.random(len(X))>0.07); X,Y,r=X[k],Y[k],r[k]
    keep,hm=allow(X,Y); X,Y,r,hm=X[keep],Y[keep],r[keep],hm[keep]
    h=26*np.exp(rng.normal(0,0.65,len(X)))*(1+2.2*np.exp(-r/3800.))*hm*hscale
    w=pitch*rng.uniform(0.50,0.80,len(X)); d=pitch*rng.uniform(0.50,0.80,len(X))
    V,F=boxes(X,Y,np.zeros(len(X)),w,d,np.maximum(h,6.0),rng.uniform(-0.05,0.05,len(X)))
    return V,F
