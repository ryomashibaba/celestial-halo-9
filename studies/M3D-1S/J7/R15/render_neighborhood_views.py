"""Additional midrange views of lower urban streets from unchanged saved geometry.
Camera poses recorded separately; does not overwrite the model or existing views.
"""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;F=R/'revision_2'
bpy.ops.wm.open_mainfile(filepath=str(F/'R15_FINAL.blend'));s=bpy.context.scene
views={
 '11_WEST_STREET_WORLD':((-700,-900,385),(-650,-390,270),27),
 '12_EAST_CANAL_WORLD':((700,-900,430),(795,-250,370),27)}
for name,(location,target,lens) in views.items():
 c=bpy.data.objects['07_WEST_DISTRICT'];c.location=location;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.lens=lens;s.camera=c
 s.render.filepath=str(F/(name+'.png'));bpy.ops.render.render(write_still=True)
(R/'qa/ADDITIONAL_CAMERA_POSES.json').write_text(json.dumps(views,indent=2),encoding='utf8')
