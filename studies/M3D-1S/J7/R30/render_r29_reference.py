"""One actual R29 neutral reference under R30's exterior camera and lighting.
Never saves or edits the source BLEND on disk.
"""
import bpy,sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import geometry as g
bpy.ops.wm.open_mainfile(filepath=str(g.R.parent/'R29/model/R29_TIDAL_COMMONS.blend'))
for o in list(bpy.context.scene.objects):
    if o.type=='LIGHT':g.remove(o)
g.materials();g.setup_lighting()
g.camera('R30_MATCHED_REFERENCE',(5300,-7000,3500),(0,800,1800),38)
sc=bpy.context.scene;sc.camera=bpy.data.objects['R30_MATCHED_REFERENCE'];sc.view_layers[0].material_override=bpy.data.materials['clay']
sc.render.filepath=str(g.R/'comparison/R29_clay_02_CENTRAL.png')
bpy.ops.render.render(write_still=True)
g.record('qa/R29_MATCHED_REFERENCE.json',dict(source='R29/model/R29_TIDAL_COMMONS.blend',source_head='d9f30a36946138359667676a904eba1a9c34da72',camera='R30 02_CENTRAL',eye=[5300,-7000,3500],target=[0,800,1800],lens=38,lighting='R30 common sun/sky/exposure and clay override',resolution=[1600,1000],source_saved=False))
