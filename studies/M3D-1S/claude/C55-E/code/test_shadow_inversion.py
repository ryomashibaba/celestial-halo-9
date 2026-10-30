"""Regression test: one thick box on a plane. Run with PYTHONPATH pointing at the old (C55-D) or fixed (C55-E) core.py."""
import sys,json,numpy as np
from core import *
V,F=boxes(np.array([0.]),np.array([0.]),np.array([0.]),np.array([1000.]),np.array([1000.]),np.array([1000.]))
m=Mesh(); m.add(V,F,None,mat=0,flat=True); mesh=m.done()
Ls=unit((-0.70,0.35,0.62)); L=Light(mesh,Ls,(0,0,500),3000,res=1024,sky=(2,2,1),log=lambda *a:None)
def sv(P,n):
    P=np.array([P],float); n=np.array([n],float); ndl=max(float(n[0]@Ls),1e-3); return float(L.sun_vis(P+n*5.0,np.array([ndl]))[0])
sp=np.array([500.,0,0])+np.array([0.70,-0.35,0])/0.62*500+np.array([200,-100,0])
r={'top_of_box (expect 1)':sv((0,0,1000),(0,0,1)),'ground_sun_side (expect 1)':sv((-1500,525,0),(0,0,1)),'ground_in_box_shadow (expect 0)':sv(tuple(sp),(0,0,1)),
   'shadow_camera_position':[round(float(x)) for x in L.sun_map[0].pos]}
print(json.dumps(r))
