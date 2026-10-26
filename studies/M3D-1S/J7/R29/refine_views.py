"""Only final new-camera corrections. Geometry and GLB stay unchanged."""
import bpy,sys,importlib.util,json
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('r29',R/'build_commons.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
bpy.ops.wm.open_mainfile(filepath=str(R/'model/R29_TIDAL_COMMONS.blend'));bpy.context.preferences.filepaths.save_version=0
rows=[]
for name,pos,target,lens,floor in m.NEW_CAMERAS:
    ob=bpy.data.objects[name]
    if (ob.location-Vector(pos)).length>.01 or abs(ob.data.lens-lens)>.01:
        rows.append({'camera':name,'old_eye_m':list(ob.location),'new_eye_m':pos,'old_lens':ob.data.lens,'new_lens':lens,'reason':'Frame the open central aisle / arrival threshold rather than a low gallery underside. Camera correction only.'})
    ob.location=pos;ob.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler();ob.data.lens=lens;ob['floor_expected']=floor or '';ob['target_m']=list(target)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'model/R29_TIDAL_COMMONS.blend'),compress=True)
(R/'qa/NEW_CAMERA_CORRECTIONS.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
print('CAMERA_CORRECTION_ONLY',len(rows),flush=True)
