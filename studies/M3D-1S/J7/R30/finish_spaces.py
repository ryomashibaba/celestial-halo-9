"""Finish the demonstrable human thresholds, without claiming whole-city completion."""
import bpy,sys,math
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
V=sys.argv[sys.argv.index('--')+1]
bpy.ops.wm.open_mainfile(filepath=str(g.R/f'model/R30_{V}.blend'));g.materials()
g.GROUP=V+'_FINAL_PUBLIC_THRESHOLD'
if V=='A':
    # Original common human location straddled the canal. Give it a real bridge,
    # not a changed eye height or a camera hovering above water.
    bpy.data.objects['A canal inlet'].location.z-=.5
    g.deck('A_HUMAN_CANAL_BRIDGE_REAL_FLOOR',[(20,-1730),(205,-1730),(205,-1580),(20,-1580)],105,6,'porcelain')
    bpy.data.objects['04_HUMAN']['support_floor']='A_HUMAN_CANAL_BRIDGE_REAL_FLOOR'
    g.CHANGES.append({'geometry':'Actual bridge at unchanged common human eye; canal water lowered 0.5m to remove coplanar water/floor overlap.'})
    rev=4
else:
    # A distinct vertical public destination at the end of the formerly sky-only
    # horizon street. It inhabits the gap beside the eastern hanging city.
    for side in (-1,1):
        rows=[]
        for i in range(17):
            t=i/16;z=2190+440*t;xx=1540+side*(175-40*t)+70*t*t
            yy=1320+60*t;w=90-20*t;d=180-50*t
            rows.append([(xx-w/2,yy-d/2,z),(xx+w/2,yy-d/2,z),(xx+w/2,yy+d/2,z),(xx-w/2,yy+d/2,z)])
        g.solid('B eastern convergence inhabited pier '+str(side),rows,'recess')
        for k,z in enumerate((2190,2240,2320,2420,2540)):
            g.box('B eastern convergence public galleries',(1540+side*(172-k*7)+k*10,1320+k*9,z),(145-k*8,210-k*15,5),'ivory')
    g.deck('B_EAST_2190_DESTINATION_FLOOR',[(1270,1150),(1830,1150),(1850,1500),(1310,1550)],2190,18,'ground')
    g.surface('B eastern convergence tilted upper room',[[ (1330,1200,2580),(1550,1200,2710),(1810,1200,2630)],[(1400,1500,2630),(1630,1500,2700),(1840,1500,2560)]],15,'porcelain')
    g.ribbon('B horizon destination public bridge',g.catmull([(940,840,2190),(1150,1020,2190),(1450,1300,2190)],15),78,14,'ivory',True)
    g.people([(1420+i*14,1300,2190) for i in range(10)])
    cam=bpy.data.objects['07_SKY_STREET'];target=Vector((1550,1320,2410));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam['target_m']=list(target)
    g.CHANGES.append({'geometry':'New 440m-high public destination and 2190m bridge at end of actual horizon street. Camera07 aims into it; common views remain fixed. This new block is an explicitly unfinished public-room study, not a full district.'})
    rev=5
g.flush();g.save(V,rev)
