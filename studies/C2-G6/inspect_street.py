"""Quick diagnostic from the saved final scene. Output is local-only, not a final render."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'A.blend'))
s=json.loads((R/'A_metrics.json').read_text())['cameras']['13_elevated_living_street']
sc=bpy.context.scene;cam=sc.camera;cam.location=s['eye'];cam.rotation_euler=(Vector(s['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=s['lens']
sc.cycles.samples=3;sc.render.resolution_x=800;sc.render.resolution_y=600;sc.render.filepath=str(R/'street_check.local.png');bpy.ops.render.render(write_still=True)
