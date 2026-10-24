"""Repair occluded human cameras: place observation floor at an exposed city edge.
No macro shape changes. Initial human-view frames were inside solid geometry;
they are rejected evidence and are replaced with actual 1.7m eye-level renders.
"""
import bpy,sys,json,importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r11',ROOT/'build_r11.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
folder,label=sys.argv[sys.argv.index('--')+1:][:2]
f=ROOT/folder
fn='R11_B_REFINED' if folder=='refined' else 'R11_'+label
bpy.ops.wm.open_mainfile(filepath=str(f/(fn+'.blend')))
r.MODEL=bpy.data.collections['01_EDITABLE_ARCHITECTURE']
for key,prefix in [('ivory','01 |'),('silver','02 |'),('dark','03 |'),('gold','04 |')]:
    r.MATS[key]=next(m for m in bpy.data.materials if m.name.startswith(prefix))
for o in list(r.MODEL.objects):
    if o.name.startswith(tuple(label+str(i) for i in range(60,66))):
        bpy.data.objects.remove(o,do_unlink=True)
if folder=='concept_A':
    center=(-1800,-1640,1065)
    pos=(-1895,-1880,1066.7);target=(1700,-900,2900)
elif folder=='concept_B':
    center=(-1800,-1650,190)
    pos=(-1895,-1890,191.7);target=(1700,-650,2500)
else:
    center=(-1380,-1850,820)
    pos=(-1475,-2090,821.7);target=(1700,-700,2900)
x,y,z=center
r.box('H01 | exterior public viewpoint connected into city edge',(x,y,z-9),(260,600,18),'ivory')
for off in [-290,290]:
    r.tube('H02 | 1.1m public guardrail',[(x-125,y+off,z+1.1),(x+125,y+off,z+1.1)],.055,'gold')
    for j in range(26):r.beam('H03 | guard post',(x-125+j*10,y+off,z),(x-125+j*10,y+off,z+1.1),.07,mat='gold')
for j in range(3):
    px,py=pos[0]+12+j*3,pos[1]+5+j*2
    r.beam('H04 | 1.75m human torso',(px,py,z+.75),(px,py,z+1.45),.28,mat='dark')
    r.box('H05 | human head',(px,py,z+1.63),(.20,.20,.24),'dark')
    for dd in [-.11,.11]:r.beam('H06 | human leg',(px+dd,py,z),(px+dd,py,z+.8),.12,mat='dark')
scene=bpy.context.scene
scene.render.resolution_x=1440;scene.render.resolution_y=1100;scene.cycles.samples=40
pref=bpy.context.preferences.addons['cycles'].preferences
pref.compute_device_type='OPTIX';pref.get_devices()
for d in pref.devices:d.use=d.type=='OPTIX'
scene.cycles.device='GPU'
r.point_camera(pos,target,'PERSP',24)
scene.render.filepath=str(f/'09_HUMAN_CONCOURSE.png')
bpy.ops.render.render(write_still=True)
c=json.loads((f/'cameras.json').read_text(encoding='utf8'))
c['09_HUMAN_CONCOURSE']={'position_m':pos,'target_m':target,'type':'PERSP','focal_length_mm':24,
                         'eye_above_public_floor_m':1.7,'public_floor_elevation_m':z,'resolution':[1440,1100]}
(f/'cameras.json').write_text(json.dumps(c,indent=2),encoding='utf8')
r.save_exports(f,'B_REFINED' if folder=='refined' else label)
print('R11 HUMAN VIEW REPAIRED',folder,flush=True)
