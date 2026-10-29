"""E-A section: the ground is bent by CLOTHOID (railway easement) transitions, not a log-spiral.
Reason (design logic): the ground is a transit surface; curvature changes linearly with arclength so that riders/vehicles feel a smooth rate of turn.
u = front direction (barrel opens toward +u), z up. Path starts on the BACK ground heading +u (forward)."""
import numpy as np
SEGS = [  # (length m, k_start, k_end)  curvature k = 1/R  (+ = concave-up ramp, - = clockwise curl over the crest)
    (1800, 0.0, 1/3600), (3000, 1/3600, 1/3600), (1500, 1/3600, 0.0),
    (1400, 0.0, -1/1750), (4300, -1/1750, -1/1750), (1000, -1/1750, 0.0),
]
def profile(ds=5.0, segs=SEGS):
    u=[0.0]; z=[0.0]; ph=[0.0]; s=[0.0]; th=0.0
    for L,k0,k1 in segs:
        n=int(L/ds)
        for i in range(n):
            k=k0+(k1-k0)*(i+0.5)/n
            th+=k*ds; u.append(u[-1]+np.cos(th)*ds); z.append(z[-1]+np.sin(th)*ds); ph.append(th); s.append(s[-1]+ds)
    return np.array(s),np.array(u),np.array(z),np.array(ph)
if __name__=="__main__":
    s,u,z,ph=profile()
    print('length',s[-1],'crest z',z.max(),'at u',u[z.argmax()],'end u,z',u[-1],z[-1],'end heading deg',np.degrees(ph[-1]),'u range',u.min(),u.max())
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(9,5)); ax.plot(u,z,lw=3); ax.set_aspect('equal'); ax.axhline(0,color='k'); ax.grid(alpha=.3); ax.set_title('E-A clothoid section (m)'); fig.savefig('../notes/ea_profile.png',dpi=80)
