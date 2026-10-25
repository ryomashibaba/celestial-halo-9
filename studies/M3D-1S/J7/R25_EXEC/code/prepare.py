import bpy,math,json,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'models/C55A_BASELINE.blend'))
s=bpy.context.scene
for o in list(s.objects):
 if o.type in {'CAMERA','LIGHT'}:bpy.data.objects.remove(o,do_unlink=True)
for o in s.objects:
 if o.type=='MESH':o.hide_render=o.get('collection','') in {'TERRAIN_CONTEXT','LIGHT_DECALS'} or o.get('material','')=='beam' or o.name.startswith('sunshaft') or o.name=='sacred_light_cone'
s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
s.render.threads_mode='FIXED';s.render.threads=4
s.render.resolution_x=1100;s.render.resolution_y=750;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.film_transparent=False
s.world=bpy.data.worlds.new('R25_FIXED_WORLD');s.world.use_nodes=True
bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.32,.36,.42,1);bg.inputs[1].default_value=.65
d=bpy.data.lights.new('R25_FIXED_SUN','SUN');d.energy=3;d.angle=math.radians(12)
o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.rotation_euler=Vector((.3,.8,-.65)).to_track_quat('-Z','Y').to_euler()
m=bpy.data.materials.new('R25_NEUTRAL_CLAY');m.use_nodes=True
p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Base Color'].default_value=(.48,.48,.48,1);p.inputs['Roughness'].default_value=.8
s.view_layers[0].material_override=m
s.view_settings.view_transform='AgX';s.view_settings.exposure=0
cameras={
 '01_local':([-160,200,860],[-450,790,700],55),
 '02_entrance':([-450,582,649.48],[-450,950,690],65),
 '03_interior':([-450,800,659.5],[-450,1080,705],65),
 '04_destination':([-450,982,669.7],[-900,1200,700],65),
 '05_front_wide':([6500,-10000,6500],[-1000,300,2400],50),
 '06_rear_wide':([-6500,11000,6500],[-1000,300,2400],50)}
for name,(pos,target,fov) in cameras.items():
 d=bpy.data.cameras.new(name);d.sensor_fit='HORIZONTAL';d.sensor_width=36;d.lens=18/math.tan(math.radians(fov/2));d.clip_start=.1;d.clip_end=100000
 o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler()
(R/'qa/CAMERAS.json').write_text(json.dumps(cameras,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'models/C55A_BEFORE.blend'),compress=True)
for name in cameras:
 s.camera=bpy.data.objects[name];s.render.filepath=str(R/'renders'/('before_'+name+'.png'));bpy.ops.render.render(write_still=True);print('DONE',name,flush=True)
