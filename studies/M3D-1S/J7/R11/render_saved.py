"""Render existing saved models without rebuilding or modifying their architecture."""
import bpy
import sys
import json
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r11',ROOT/'build_r11.py')
r=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
args=sys.argv[sys.argv.index('--')+1:]
folder,label=args[:2]
f=ROOT/folder
filename='R11_B_REFINED.blend' if folder=='refined' else 'R11_'+label+'.blend'
bpy.ops.wm.open_mainfile(filepath=str(f/filename))
scene=bpy.context.scene
r.MODEL=bpy.data.collections['01_EDITABLE_ARCHITECTURE']
scene.render.resolution_x=1440
scene.render.resolution_y=1100
scene.cycles.samples=40
scene.cycles.use_denoising=True
try:
    pref=bpy.context.preferences.addons['cycles'].preferences
    pref.compute_device_type='OPTIX'
    pref.get_devices()
    for d in pref.devices:d.use=d.type=='OPTIX'
    scene.cycles.device='GPU'
except Exception:pass
saved_cameras=json.loads((f/'cameras.json').read_text(encoding='utf8')) if (f/'cameras.json').exists() else {}
overrides={k:v for k,v in saved_cameras.items() if k=='09_HUMAN_CONCOURSE'}
r.render_views(f,label,preview=False,camera_overrides=overrides)
r.point_camera(*r.VIEWS['02_OBLIQUE'])
bpy.ops.wm.save_as_mainfile(filepath=str(f/filename),compress=True)
r.evidence(f,'B_REFINED' if folder=='refined' else label)
