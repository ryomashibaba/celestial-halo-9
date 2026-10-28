"""D10 approved isolated Blender trial. Authored boundary meshes, not canonical assets.
Creates a NEW factory scene in a dedicated background process. No existing file reads.
Main composition: oblique inhabited cliff / civic seam / lifted exchange district.
This is one incomplete local architectural fragment, never a central-city proposal.
"""
import bpy, bmesh, math, json, os, sys
from pathlib import Path
from mathutils import Vector

OUT=Path(sys.argv[sys.argv.index('--')+1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
assert not (OUT/'D10_BASE.blend').exists(), 'Use a fresh research output directory; do not overwrite baseline.'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
scene.unit_settings.scale_length=1
scene['study']='R33-S27-D10-BLENDER / independent local fragment / NOT canonical coordinates'
scene['art_status']='UNREVIEWED'
scene['minecraft']='HOLD'

def material(name,color,rough=.45,metal=.0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    n.inputs['Base Color'].default_value=(*color,1)
    n.inputs['Roughness'].default_value=rough
    n.inputs['Metallic'].default_value=metal
    m.diffuse_color=(*color,1)
    return m
stone=material('Warm mineral alloy',(.57,.60,.60),.54,.16)
edge=material('Pale structural ceramic',(.72,.74,.72),.46,.1)
dark=material('Occupied facade recess',(.075,.11,.14),.35,.18)
floor_mat=material('Civic stone',(.32,.36,.37),.65,.04)
glass=material('Opaque study glazing - no fake interior',(.13,.20,.23),.25,.4)
ground=material('Ground',(.19,.22,.23),.8,0)
accent=material('Navigation bronze',(.37,.27,.16),.45,.3)

def mesh(name,verts,faces,mat,bindings=()):
    me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob)
    ob.data.materials.append(mat)
    ob['role']=name;ob['research_only']=True
    if bindings:
        group=ob.vertex_groups.new(name='CIVIC_EAST_EDGE')
        group.add(list(bindings),1.0,'REPLACE')
    return ob

def slab(name,poly,z,t,mat=floor_mat,bind_indices=()):
    n=len(poly);v=[(x,y,z) for x,y in poly]+[(x,y,z-t) for x,y in poly]
    f=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
    f += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,v,f,mat,list(bind_indices)+[i+n for i in bind_indices])

def box(name,lo,hi,mat):
    x,y,z=lo;X,Y,Z=hi
    return mesh(name,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],
                [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)

# Three separately authored polyhedral bodies. Their different boundaries are explicit.
# They are general habitation exteriors: private interiors intentionally NOT represented.
west_v=[(-216,-94,0),(-139,-140,0),(-60,-113,0),(-40,36,0),(-109,128,0),(-226,78,0),
        (-241,-66,103),(-154,-106,124),(-75,-75,104),(-36,26,95),(-115,99,119),(-252,68,138),
        (-222,-35,267),(-147,-56,305),(-78,-27,260),(-67,36,239),(-128,80,276),(-236,56,288)]
west_f=[(5,4,3,2,1,0),(0,1,7,6),(1,2,8,7),(2,3,9,8),(3,4,10,9),(4,5,11,10),(5,0,6,11),
        (6,7,13,12),(7,8,14,13),(8,9,15,14),(9,10,16,15),(10,11,17,16),(11,6,12,17),(12,13,14,15,16,17)]
mesh('WEST_INHABITED_CLIFF',west_v,west_f,stone)

east_v=[(110,-86,36),(181,-100,36),(271,-31,36),(250,80,36),(173,119,36),(110,72,36),
        (110,-86,112),(185,-93,144),(292,-3,174),(274,80,188),(191,111,143),(110,72,112),
        (116,-65,164),(192,-51,203),(312,16,242),(277,69,257),(187,77,199),(116,51,172)]
east_f=[(5,4,3,2,1,0),(0,1,7,6),(1,2,8,7),(2,3,9,8),(3,4,10,9),(4,5,11,10),(5,0,6,11),
        (6,7,13,12),(7,8,14,13),(8,9,15,14),(9,10,16,15),(10,11,17,16),(11,6,12,17),(12,13,14,15,16,17)]
mesh('EAST_EXCHANGE_BODY',east_v,east_f,edge,[0,5,6,11,12,17])

# An oblique inhabited crown grows from the rear, NOT an arch across the whole gap.
crown_v=[(-172,63,148),(-92,12,144),(-21,52,132),(58,101,112),(36,168,127),(-104,185,153),(-197,141,174),
         (-170,76,222),(-90,42,224),(-8,76,198),(83,128,181),(35,178,203),(-99,198,251),(-202,149,270)]
crown_f=[(6,5,4,3,2,1,0),(7,8,9,10,11,12,13),
         (0,1,8,7),(1,2,9,8),(2,3,10,9),(3,4,11,10),(4,5,12,11),(5,6,13,12),(6,0,7,13)]
mesh('REAR_OBLIQUE_HABITAT',crown_v,crown_f,stone)

# Civic spaces determine the open seam between the inhabited bodies.
slab('FORUM_FLOOR',[(-73,-132),(42,-153),(110,-86),(110,72),(54,110),(-40,36)],36,7,bind_indices=[2,3])
slab('UPPER_PUBLIC_FLOOR',[(-77,-69),(18,-89),(110,-70),(110,51),(43,78),(-36,26)],112,6,bind_indices=[2,3])
slab('LOW_APPROACH',[(-106,-360),(-25,-360),(42,-153),(-73,-132)],0,5)
mesh('APPROACH_RAMP',[(-106,-360,0),(-25,-360,0),(42,-153,36),(-73,-132,36),
                      (-106,-360,-4),(-25,-360,-4),(42,-153,30),(-73,-132,30)],
     [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],floor_mat)
# One lateral public hall: floor, true side walls and overhead boundary, open entrances.
slab('HALL_FLOOR',[(-73,-132),(-150,-109),(-180,-27),(-75,-75)],36,5)
mesh('HALL_WEST_WALL',[(-150,-109,36),(-180,-27,36),(-180,-27,89),(-150,-109,81)],[(0,1,2,3)],dark)
mesh('HALL_CEILING',[(-73,-132,81),(-150,-109,81),(-180,-27,89),(-75,-75,96)],[(3,2,1,0)],edge)
mesh('HALL_NORTH_WALL',[(-180,-27,36),(-75,-75,36),(-75,-75,96),(-180,-27,89)],[(0,1,2,3)],stone)

# Excise the actual public hall from the general-habitation solid, rather than putting
# a nominal room inside an opaque mass. Original cutter dimensions remain in source.
cutter=slab('TEMP_HALL_VOID',[(-48,-151),(-167,-126),(-198,-11),(-58,-48)],106,72)
for ob in [bpy.data.objects['WEST_INHABITED_CLIFF'],cutter]:
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
host=bpy.data.objects['WEST_INHABITED_CLIFF']
mod=host.modifiers.new('Public hall is real empty volume','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter
bpy.context.view_layer.objects.active=host
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cutter,do_unlink=True)

# Public supports and circulation are explicit, but full-height accessibility remains unverified.
box('EAST_PUBLIC_CORE',(145,-55,0),(169,-18,145),dark)
box('WEST_PUBLIC_CORE',(-103,-45,0),(-83,-15,244),dark)
slab('UPPER_WEST_LANDING',[(-103,-49),(-55,-52),(-36,26),(-83,23)],112,6)
slab('EAST_GROUND_LANDING',[(110,-86),(169,-55),(169,-18),(110,-8)],36,7,bind_indices=[0,3])
slab('EAST_UPPER_LANDING',[(110,-70),(169,-55),(169,-18),(110,15)],112,6,bind_indices=[0,3])

# Broad, deliberately placed inset occupation registers, not a population of small boxes.
# These are flat opaque architectural studies, not proof of detailed dwelling interiors.
for name,verts in [
 ('WEST_CITY_FACE_LOW',[(-154,-106.8,49),(-76,-76,50),(-76,-76,88),(-154,-106.8,94)]),
 ('WEST_CITY_FACE_MID',[(-155,-88,145),(-76,-56,136),(-76,-56,171),(-155,-88,183)]),
 ('WEST_CITY_FACE_HIGH',[(-150,-64,223),(-78,-35,210),(-78,-35,243),(-150,-64,269)]),
 ('REAR_CITY_FACE',[(-90,11.5,159),(-20,51.5,149),(57,100.5,132),(57,100.5,162),(-20,51.5,180),(-90,11.5,205)]),
 ('EAST_CITY_FACE',[(181,-100.7,54),(268,-32,62),(280,-18,117),(184,-94,119)])]:
    mesh(name,verts,[tuple(range(len(verts)))],dark)

# Sparse vertical reveals express occupation scale; not used to score artistic success.
for i,(x,y,z,h) in enumerate([(-146,-106,53,37),(-117,-95,53,37),(-91,-85,53,37),
                             (-137,-82,148,30),(-109,-70,144,29),(-86,-59,141,27)]):
    box('FACADE_REVEAL_%02d'%i,(x-1,y-1,z),(x+1,y+1,z+h),edge)

# Plain research context: cropped terrain, not W0 or a finished city backdrop.
slab('CONTEXT_GROUND',[(-660,-600),(660,-600),(660,510),(-660,510)],-5,12,ground)
slab('CROPPED_WEST_EMBANKMENT',[(-470,-120),(-226,-110),(-226,200),(-420,230)],-1,15,stone)
box('SCALE_MARKER_1P8M',(7,-200,0),(7.5,-199.5,1.8),accent)

def camera(name,loc,target,lens=40,ortho=None):
    d=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,d);scene.collection.objects.link(o)
    o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    d.lens=lens;d.clip_start=.1;d.clip_end=10000
    if ortho is not None:d.type='ORTHO';d.ortho_scale=ortho
    return o
camera('CAM_OBLIQUE',(700,-980,610),(5,10,125),48)
camera('CAM_REAR',(-560,820,425),(0,20,140),48)
camera('CAM_FRONT',(25,-1150,260),(0,0,125),48)
camera('CAM_TOP',(0,0,1500),(0,0,0),48,950)
camera('CAM_CIVIC',(16,-118,37.7),(25,30,102),22)
camera('CAM_HALL',(-95,-114,37.7),(-139,-67,64),21)
world=bpy.data.worlds.new('D10 sky');world.use_nodes=True
world.node_tree.nodes.get('Background').inputs[0].default_value=(.49,.56,.65,1)
world.node_tree.nodes.get('Background').inputs[1].default_value=.6
scene.world=world
sun_d=bpy.data.lights.new('Study sun','SUN');sun_d.energy=2.3;sun_d.angle=.18
sun=bpy.data.objects.new('Study sun',sun_d);scene.collection.objects.link(sun)
sun.rotation_euler=(math.radians(24),math.radians(-28),math.radians(-29))
area_d=bpy.data.lights.new('Sky fill','AREA');area_d.energy=2000000;area_d.shape='DISK';area_d.size=500
area=bpy.data.objects.new('Sky fill',area_d);scene.collection.objects.link(area);area.location=(0,-300,600)
area.rotation_euler=(Vector((0,0,100))-area.location).to_track_quat('-Z','Y').to_euler()
try:scene.render.engine='CYCLES'
except TypeError:pass
if scene.render.engine=='CYCLES':scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1100;scene.render.resolution_y=825;scene.render.resolution_percentage=100
scene.render.image_settings.file_format=next(i.identifier for i in scene.render.image_settings.bl_rna.properties['file_format'].enum_items if i.identifier=='PNG')
scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
scene.camera=bpy.data.objects['CAM_OBLIQUE']
for ob in scene.objects:
    if ob.type=='MESH' and ob.name not in ['HALL_WEST_WALL','HALL_CEILING','HALL_NORTH_WALL']:
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'D10_BASE.blend'),compress=True)
print('D10_BASE_SAVED',scene.render.engine,len([o for o in scene.objects if o.type=='MESH']))
