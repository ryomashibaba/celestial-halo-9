import sys; sys.path.insert(0,'/home/claude/c55e/code')
from rig import *
which=sys.argv[1]
if which=='ea':
    from ea_cams import cams_ea
    run('/home/claude/c55e/model/_ea.npz','EA_v2','clay',cams_ea(),res=1536)
else:
    from eb_cams import cams_eb
    run('/home/claude/c55e/model/_eb.npz','EB_v3','clay',cams_eb(),res=1536)
