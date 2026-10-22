"""Offline-only fix for saved viewport camera and metadata; no geometry changes."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
for name in ['N1','N2','N1R1']:
    bpy.ops.wm.open_mainfile(filepath=str(R/(name+'.blend')))
    m=json.loads((R/(name+'_metrics.json')).read_text());s=m['cameras']['02_oblique'];sc=bpy.context.scene
    sc.camera.location=s['eye'];sc.camera.rotation_euler=(Vector(s['target'])-sc.camera.location).to_track_quat('-Z','Y').to_euler();sc.camera.data.type='ORTHO';sc.camera.data.ortho_scale=s['ortho']
    m['render_settings']=dict(width=sc.render.resolution_x,height=sc.render.resolution_y,samples=sc.cycles.samples,engine='CYCLES',sun_energy=2.3,world_strength=.55)
    (R/(name+'_metrics.json')).write_text(json.dumps(m,indent=2),encoding='utf-8')
    bpy.ops.wm.save_as_mainfile(filepath=str(R/(name+'.blend')),compress=True)
