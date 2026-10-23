"""Improve inspection framing only, preserve blank-wall and dark-interior diagnostics.
No architecture edits after final internal art REJECT.
"""
import bpy,json,shutil
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent;O=R/'selected';D=R/'diagnostics';D.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(O/'study.blend'))
m=json.loads((O/'manifest.json').read_text(encoding='utf-8'));record={}
for n,target in [('07_HIGH_B',(220,-950,1810)),('08_HALL',(-860,-1100,930)),('10_ALLEY',(-489.2,-110,1710))]:
    shutil.copy2(O/(n+'.png'),D/(n+'_original.png'))
    ca=bpy.data.objects[n];record[n]={'position_m':list(ca.location),'previous_rotation_euler':list(ca.rotation_euler),'issue':'Previous view documented wall dominance or dark interior; preserved as diagnostic'}
    if n=='08_HALL':ca.location=(-860,-450,781.7);m['cameras'][n]['position_m']=list(ca.location)
    ca.rotation_euler=(Vector(target)-ca.location).to_track_quat('-Z','Y').to_euler()
    m['cameras'][n]['rotation_euler']=list(ca.rotation_euler)
    record[n]['new_target_m']=target
(D/'camera_review.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(O/'study.blend'),compress=True)
(O/'manifest.json').write_text(json.dumps(m,indent=2),encoding='utf-8')
exec(compile((R/'render_saved.py').read_text(encoding='utf-8'),str(R/'render_saved.py'),'exec'))
