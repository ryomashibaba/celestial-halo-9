"""Synchronize saved BLEND cameras with the final authoring camera table.
No geometry or GLB changes. Separate camera correction from architectural edits.
"""
import bpy,sys,importlib.util
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r28_author',R/'build_estuary.py')
author=importlib.util.module_from_spec(spec);spec.loader.exec_module(author)
bpy.ops.wm.open_mainfile(filepath=str(R/'model/R28_CELESTIAL_ESTUARY.blend'))
names={c[0] for c in author.CAMERAS}
for ob in list(bpy.context.scene.objects):
    if ob.type=='CAMERA' and ob.name not in names:bpy.data.objects.remove(ob,do_unlink=True)
for name,pos,target,lens,floor in author.CAMERAS:
    ob=bpy.data.objects.get(name)
    if not ob:
        ob=bpy.data.objects.new(name,bpy.data.cameras.new(name));bpy.context.scene.collection.objects.link(ob)
        ob.data.clip_start=.1;ob.data.clip_end=90000
    ob.location=pos;ob.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler()
    ob.data.lens=lens;ob['floor_expected']=floor or '';ob['target_m']=list(target)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'model/R28_CELESTIAL_ESTUARY.blend'),compress=True)
print('R28 camera corrections saved, unchanged geometry',flush=True)
