"""Fixed R30-B camera/light/scale; actual Cycles renders, no image synthesis."""
import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
import meshkit as g
R=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
stage=args[0] if args else 'initial'
style='art' if 'art' in args else 'clay'
source=R.parent/'R30/model/R30_B.blend' if stage=='baseline' else R/'model/R31_A.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));g.materials();g.setup_gpu_only()
if stage=='baseline' and not bpy.data.objects.get('08_FRONT'):
    g.camera('08_FRONT',(200,-9500,2700),(0,1100,2100),37)
sc=bpy.context.scene
sc.view_layers[0].material_override=bpy.data.materials['clay'] if style=='clay' else None
preview=stage=='initial' or 'preview' in args
sc.render.resolution_x=1600;sc.render.resolution_y=1000
sc.render.resolution_percentage=60 if preview else 100
sc.cycles.samples=16 if preview else 48
folder=R/('process/initial' if stage=='initial' else 'renders/'+stage)
folder.mkdir(parents=True,exist_ok=True)
names=[n for n in args if n[:2].isdigit()] or ['01_CITY','02_CENTRAL','04_HUMAN','07_SKY_STREET','05_REAR','06_UNDERSIDE']
records=[]
for name in names:
    cam=bpy.data.objects[name];sc.camera=cam
    sc.render.filepath=str(folder/(style+'_'+name+'.png'))
    print('START',stage,style,name,flush=True)
    bpy.ops.render.render(write_still=True)
    records.append({'camera':name,'matrix':[list(r) for r in cam.matrix_world],'lens':cam.data.lens,'clip':[cam.data.clip_start,cam.data.clip_end],'resolution':[sc.render.resolution_x*sc.render.resolution_percentage//100,sc.render.resolution_y*sc.render.resolution_percentage//100],'samples':sc.cycles.samples,'world':sc.world.name,'exposure':sc.view_settings.exposure,'style':style,'source':source.name})
    print('DONE',name,flush=True)
(folder/('conditions_'+style+'.json')).write_text(json.dumps(records,indent=2),encoding='utf8')
