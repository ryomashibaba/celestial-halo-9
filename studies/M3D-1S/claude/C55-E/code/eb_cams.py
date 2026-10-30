import numpy as np
from rig import *
def cams_eb():
    c=ext_cams((0,0,2200),tgt_side=(0,0,2200),tgt_aerial=(0,0,1800))
    fr=np.load('/home/claude/c55e/model/_eb_frames.npz')
    # 08: close view of the habitation face of ribbon A (about half way up), eye 150 m above the banked terraces, looking along the climb
    i=int(0.50*len(fr['A_C'])); j=i+45
    eyeA=fr['A_C'][i]+fr['A_n'][i]*(fr['A_T'][i]/2+330)-fr['A_w'][i]*30; tgA=fr['A_C'][j]+fr['A_n'][j]*(fr['A_T'][j]/2+60)-fr['A_w'][j]*120
    c['06_groundup']=((700,-500,15),(-200,300,3000),74,Z)
    c['07_void_interior']=((0,-700,2300),(2300,1300,2600),80,Z)
    c['08_habitat_close']=(tuple(eyeA),tuple(tgA),70,Z)
    return c
if __name__=="__main__":
    import sys
    npz=sys.argv[1]; prefix=sys.argv[2]; W=int(sys.argv[3]); ss=float(sys.argv[4]); sel=sys.argv[5:] or None
    run(npz,prefix,'clay',cams_eb(),sel=sel,W=W,H=W*9//16,ss=ss,res=1024)
