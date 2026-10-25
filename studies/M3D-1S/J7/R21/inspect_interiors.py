"""Supplemental headlamp inspection, explicitly NOT common-sun art comparison."""
import bpy, sys, json
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
sys.argv=['inspect_interiors.py','--','inspection','C55A']
import compare as c
for model,tag in [('C55A','hall'),('R19','mid')]:
    c.MODEL=model;s,T,clay=c.setup()
    j=json.loads((R/'qa'/(model+'_floor_'+tag+'.json')).read_text(encoding='utf8'))
    eye=Vector(j['position_m']);target=Vector(j['target_m'])
    lamp=bpy.data.lights.new('R21_SUPPLEMENTAL_INSPECTION_LAMP','POINT');lamp.energy=1e7;lamp.shadow_soft_size=3
    obj=bpy.data.objects.new(lamp.name,lamp);s.collection.objects.link(obj);obj.location=eye+Vector((0,0,3))
    c.shoot(s,'inspection_interior',eye,target,True,False,dict(
       supplemental_inspection_only=True,common_sun_art_set=False,point_lamp_energy=1e7,
       point_lamp_radius_m=3,point_lamp_eye_offset_m=[0,0,3],eye_above_floor_m=j['eye_above_floor_m'],floor=j['floor'],
       note='Identical point lamp relative to each supported camera. Different interior spaces; diagnostic shape visibility only, not aesthetic success or global scale comparison.'))
