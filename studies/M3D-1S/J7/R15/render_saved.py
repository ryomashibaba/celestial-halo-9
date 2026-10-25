"""Render cameras from a saved native file in an independent background process."""
import bpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
args=sys.argv[sys.argv.index('--')+1:]
folder=Path(args[0]).resolve();blend=next(folder.glob('*.blend'))
bpy.ops.wm.open_mainfile(filepath=str(blend))
s=bpy.context.scene
for name in args[1:]:
 s.camera=bpy.data.objects[name];s.render.filepath=str(folder/(name+'.png'))
 bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
