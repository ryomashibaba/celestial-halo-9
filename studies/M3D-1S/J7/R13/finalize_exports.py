"""Export the evaluated geometry seen in the renders, including edge modifiers."""
import bpy,sys
from pathlib import Path
ROOT=Path(__file__).parent;sys.path.insert(0,str(ROOT))
import build_r13 as H
for folder,stem in [('exploration_A','R13_A'),('exploration_B','R13_B'),
                    ('exploration_C','R13_C'),('selected','R13_C_SELECTED'),
                    ('revision_1','R13_C_R1'),('revision_2','R13_C_R2')]:
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/folder/(stem+'.blend')))
    H.attach_existing();bpy.ops.object.select_all(action='DESELECT')
    for o in H.ARCH.objects:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(ROOT/folder/(stem+'.glb')),use_selection=True,export_format='GLB',export_apply=True,export_cameras=False,export_lights=False)
    print('EVALUATED_EXPORT',folder,flush=True)
# Restore wide-camera manifest overwritten by the first internal render call.
H.render(ROOT/'revision_2')
# Reimport final GLB into the same presentation rig; render the imported geometry.
for o in list(H.ARCH.objects):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'revision_2/R13_C_R2.glb'))
H.render(ROOT/'qa',{'ACTUAL_GLB_REIMPORT_OBLIQUE':H.VIEWS['02_OBLIQUE']})
