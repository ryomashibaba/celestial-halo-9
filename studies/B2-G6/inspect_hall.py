"""One-time inspection camera correction, represented in frame_views.py for reproduction."""
import bpy,json,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;O=R/'selected'
bpy.ops.wm.open_mainfile(filepath=str(O/'study.blend'))
shutil.copy2(O/'08_HALL.png',R/'diagnostics/08_HALL_outside_framing.png')
m=json.loads((O/'manifest.json').read_text(encoding='utf-8'))
ca=bpy.data.objects['08_HALL'];ca.location=(-860,-450,781.7);ca.rotation_euler=(Vector((-860,-1100,930))-ca.location).to_track_quat('-Z','Y').to_euler()
m['cameras']['08_HALL']['position_m']=list(ca.location);m['cameras']['08_HALL']['rotation_euler']=list(ca.rotation_euler)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'study.blend'),compress=True)
(O/'manifest.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
exec(compile((R/'render_saved.py').read_text(encoding='utf-8'),str(R/'render_saved.py'),'exec'))
