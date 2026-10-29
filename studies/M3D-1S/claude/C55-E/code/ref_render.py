"""Re-render the C55-C and C55-D (D1e) references with the FIXED shadow renderer, same cameras/sun/material as the original C55-D sheets."""
import sys,time,numpy as np
sys.path.insert(0,'/home/claude/c55e/code')
from rig import *
which=sys.argv[1]
if which=='d1e':
    CAMS={'01_far':((-10200,-7600,420),(0,900,2000),40,Z),'02_front':((0,-9800,1300),(0,900,2000),46,Z),'04_back':((300,9800,1100),(0,900,2000),46,Z),
          '05_aerial':((0,-2600,8800),(0,300,1800),52,Z),'06_groundup':((1500,-1000,12),(-2300,300,1700),74,Z),'03_side':((-12500,900,1100),(0,1900,1900),40,Z),
          '07_barrel_axis':((900,100,230),(-2600,250,1250),80,Z)}
    run('/home/claude/c55e/model/_d1e_from_glb.npz','D1e','clay',CAMS,res=1536)
else:
    z=np.load('/home/claude/c55e/model/_c55c_mesh.npz') if False else None
    import os
    if not os.path.exists('/home/claude/c55e/model/_c55c_mesh.npz'):
        parts=read_glb('/home/claude/work/c55c_orig/research/claude_c55c/model/C55C_endless_gorge_knot.glb')
        m=Mesh()
        for i,(name,P,F,N) in enumerate(parts): m.add(P,F,N,mat=i,flat=N is None)
        mesh=m.done(); np.savez('/home/claude/c55e/model/_c55c_mesh.npz',**mesh); print('c55c tris',len(mesh['F']),[p[0] for p in parts])
    T=(0,0,2400)
    CAMS={'01_far':((-10200,-7600,420),T,40,Z),'02_front':((0,-9800,1300),T,46,Z),'04_back':((300,9800,1100),T,46,Z),'05_aerial':((0,-2600,8800),(0,0,2000),52,Z),'06_groundup':((800,-600,6),(0,0,2500),64,Z)}
    run('/home/claude/c55e/model/_c55c_mesh.npz','C55C','clay',CAMS,res=1536)
