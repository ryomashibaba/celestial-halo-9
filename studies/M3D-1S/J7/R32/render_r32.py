"""Actual Cycles fixed comparisons. All output limited to R32; no image synthesis."""
import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
import bpy,meshkit as g
args=sys.argv[sys.argv.index('--')+1:]
stage=args[0];style=args[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'model/R32_A.blend'))
g.materials();g.setup_gpu_only()
sc=bpy.context.scene
sc.view_layers[0].material_override=bpy.data.materials['clay'] if style=='clay' else None
preview='preview' in args
sc.render.resolution_x=1600;sc.render.resolution_y=1000;sc.render.resolution_percentage=60 if preview else 100
sc.cycles.samples=16 if preview else 48
folder=R/('process/'+stage if preview else 'renders/'+stage);folder.mkdir(parents=True,exist_ok=True)
rows=[]
for name in [n for n in args[2:] if n[:2].isdigit()]:
    cam=bpy.data.objects[name];sc.camera=cam;sc.render.filepath=str(folder/(style+'_'+name+'.png'))
    print('RENDER_START',name,flush=True);bpy.ops.render.render(write_still=True)
    rows.append({'camera':name,'matrix':[list(r) for r in cam.matrix_world],'lens':cam.data.lens,'clip':[cam.data.clip_start,cam.data.clip_end],
                 'resolution':[sc.render.resolution_x*sc.render.resolution_percentage//100,sc.render.resolution_y*sc.render.resolution_percentage//100],
                 'samples':sc.cycles.samples,'style':style,'world':sc.world.name,'exposure':sc.view_settings.exposure,'source':'R32_A.blend'})
(folder/('conditions_'+style+'.json')).write_text(json.dumps(rows,indent=2),encoding='utf8')
print('RENDERS_COMPLETE',flush=True)
