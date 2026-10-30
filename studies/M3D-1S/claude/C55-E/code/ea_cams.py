import numpy as np
from rig import *
def cams_ea():
    c=ext_cams((0,300,1700),tgt_side=(0,300,1700),tgt_aerial=(0,300,1500))
    sf=np.load('/home/claude/c55e/model/_ea_surf.npz')
    S=sf['A_S']; NL=sf['A_NL']; tk=sf['A_tk']
    ip=S.shape[0]//2; isx=int(0.80*S.shape[1])
    eye=S[ip,isx]-NL[ip,isx]*(tk[ip,isx]/2+230)
    tg=S[ip+40,isx-30]-NL[ip+40,isx-30]*(tk[ip+40,isx-30]/2+30)
    c['06_groundup']=((-2300,-450,12),(-3200,-350,1900),74,Z)
    c['07_barrel_interior']=((-300,-700,230),(-3400,-600,1250),80,Z)
    c['08_habitat_close']=(tuple(eye),tuple(tg),70,Z)
    return c
if __name__=="__main__":
    import sys
    npz=sys.argv[1]; prefix=sys.argv[2]; W=int(sys.argv[3]); ss=float(sys.argv[4]); sel=sys.argv[5:] or None
    run(npz,prefix,'clay',cams_ea(),sel=sel,W=W,H=W*9//16,ss=ss,res=1024)
