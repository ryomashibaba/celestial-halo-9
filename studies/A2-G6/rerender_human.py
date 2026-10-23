"""Re-render three human views from the saved reimported GLB scene, at exposure -2.
No geometry changes. Optional finishing step; build.py already uses the same exposure.
"""
from pathlib import Path
import sys,json,bpy
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R))
from build import render_to
bpy.ops.wm.open_mainfile(filepath=str(R/'selected.blend'))
sc=bpy.context.scene
sc.render.resolution_x=1900;sc.render.resolution_y=1400
data=json.loads((R/'geometry-record.json').read_text(encoding='utf-8'))
for key in ['07_human','08_public_hall','11_living_street']:
    render_to(R/'renders'/(key+'.png'),*data['human_cameras'][key])
data['human_diagnostic_exposure']=-2
data['external_diagnostic_exposure']=0
data['human_comparison_lighting']='same camera; initial failed image and final diagnosis have different diagnostic light/exposure'
(R/'geometry-record.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sc.view_settings.exposure=0
sc.camera=bpy.data.objects.get('CAM_02_oblique')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'selected.blend'),compress=True)
