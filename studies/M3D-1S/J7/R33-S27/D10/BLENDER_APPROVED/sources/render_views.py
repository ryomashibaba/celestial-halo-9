"""Render saved scene; camera transforms are embedded in BLEND, shared between variants."""
import bpy,sys,json
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:]
out=Path(args[0]);stage=args[1];names=args[2:] or ['OBLIQUE','REAR','FRONT','TOP','CIVIC','HALL']
scene=bpy.context.scene
for name in names:
    scene.camera=bpy.data.objects['CAM_'+name]
    scene.render.filepath=str(out/(stage+'_'+name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('D10_VIEW',name,flush=True)
