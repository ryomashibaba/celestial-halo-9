# CELESTIAL HALO-9 R4-E9 / visual-first direct sculpt of an EXISTING editable E8 BLEND.
# The rejected E8 original is a read-only SOURCE; output is always a new research BLEND.
# This is NOT a fresh procedural author and NOT a camera-only fix.
import bpy, math, json, hashlib, sys, struct
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[args.index('--output')+1]) if '--output' in args else Path('/tmp/E9_NATIVE')
out.mkdir(parents=True,exist_ok=True)
(out/'before').mkdir(exist_ok=True)
(out/'after').mkdir(exist_ok=True)
src=Path(bpy.data.filepath)
assert src.is_file() and src.name=='E8_LIVED_SPINE_PUBLIC_CITY_WORKING.blend'
assert bpy.context.scene.get('minecraft_write')=='FORBIDDEN'
assert bpy.context.scene.get('formal_art_adoption') is False
assert bpy.context.scene.get('official_coordinates_verified') is False
s=bpy.context.scene
s.render.resolution_x=960;s.render.resolution_y=640
s.render.resolution_percentage=100
s.cycles.samples=16
try:s.view_layers[0].cycles.use_denoising=False
except (AttributeError,TypeError):pass
cameras=['human_public_interior','human_sky_district','urban_aerial']
for name in cameras:
    assert bpy.data.objects[name].type=='CAMERA'
    s.camera=bpy.data.objects[name]
    s.render.filepath=str(out/'before'/(name+'.png'))
    bpy.ops.render.render(write_still=True)
print('E9_BASELINE_TRUE_NATIVE_RENDERS_COMPLETE',flush=True)
names_before=set(o.name for o in bpy.data.objects if o.type=='MESH')
def obj(n):
    o=bpy.data.objects.get(n)
    if not o or o.type!='MESH':raise AssertionError('Missing existing native target '+n)
    return o
def new_mat(name,rgba,metal=.2,rough=.58):
    m=bpy.data.materials.get(name)
    if m:return m
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgba,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*rgba,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough
    return m
P={'limestone':new_mat('E9 POROUS PUBLIC LIMESTONE',(.62,.62,.57)),
   'structure':new_mat('E9 exposed bronze civic frames',(.44,.36,.24),.6,.42),
   'garden':new_mat('E9 civic canyon elevated vegetation',(.19,.42,.27)),
   'glass':new_mat('E9 glazed public gallery',(.13,.43,.53),.41,.26),
   'floor':new_mat('E9 warm occupied arcade paving',(.71,.66,.55))}
def attach(n,mesh,material,collection):
    ob=bpy.data.objects.new(n,mesh)
    bpy.data.collections[collection].objects.link(ob)
    ob.data.materials.append(P[material])
    return ob
def cube(n,xyz,dim,material,collection,ang=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz)
    o=bpy.context.object;o.name=n
    o.scale=dim;o.rotation_euler[2]=ang
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    old=list(o.users_collection)
    for col in old:col.objects.unlink(o)
    bpy.data.collections[collection].objects.link(o)
    o.data.materials.append(P[material])
    return o
def rounded_boolean(target,cut_name,xyz,dims,radius):
    base=obj(target)
    before=len(base.data.polygons)
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz)
    cutter=bpy.context.object;cutter.name='TEMP_BOOLEAN_'+cut_name
    cutter.scale=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    mod=cutter.modifiers.new('OPENING_PROFILE','BEVEL')
    mod.width=radius;mod.segments=8
    bpy.context.view_layer.objects.active=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    modifier=base.modifiers.new('ACTUAL_CARVING_'+cut_name,'BOOLEAN')
    modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
    bpy.context.view_layer.objects.active=base
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    after=len(base.data.polygons)
    bpy.data.objects.remove(cutter,do_unlink=True)
    if after<=before:
        raise AssertionError(f'No proof of carve {target}: {before}->{after}')
    return {'target':target,'opening':cut_name,'face_count_before':before,'face_count_after':after,
            'location':list(xyz),'size':list(dims)}
# Step 1: actual structural silhouette edit: make boxy topological ridges asymmetric.
ridge_edits=[]
for side,top in [('WEST',540),('EAST',690)]:
    o=obj(side+'_DEEP_INHABITED_RIDGE_SUBSTRATE')
    n=0
    for v in o.data.vertices:
        if v.co.z>top-1.0:
            yy=v.co.y;xx=v.co.x
            # Negative-space-driven asymmetry, no old E8 box skyline retained.
            uplift=100*math.sin((yy+280)/730+(.4 if side=='WEST' else 1.2))
            notch=-160*math.exp(-((yy-340)/550)**2)
            v.co.z+=uplift+notch
            # taper open-canyon upper wall to give the void more daylight:
            v.co.x+=( -55 if side=='WEST' else 70 )*math.exp(-((yy+270)/850)**2)
            n+=1
    o.data.update()
    ridge_edits.append({'object':o.name,'top_vertices_sculpted':n})
# Step 2: real subtractive public chambers THROUGH city-scale masses.
cuts=[]
for target,n,center,scale,rad in [
    ('WEST_DEEP_INHABITED_RIDGE_SUBSTRATE','west_public_window_1',(-750,-400,340),(1090,520,290),85),
    ('WEST_DEEP_INHABITED_RIDGE_SUBSTRATE','west_high_city_window_2',(-750,640,440),(1100,310,215),70),
    ('EAST_DEEP_INHABITED_RIDGE_SUBSTRATE','east_public_window_1',(805,-410,390),(1150,490,320),80),
    ('EAST_DEEP_INHABITED_RIDGE_SUBSTRATE','east_high_city_window_2',(800,625,520),(1060,330,235),65),
    ('H1_INHABITED_DEEP_CITY_SECTION_1','h1_public_open_court',(1540,-150,790),(130,200,150),30),
    ('H1_INHABITED_DEEP_CITY_SECTION_2','h1_public_open_court',(1840,85,900),(130,240,125),35),
]:
    cuts.append(rounded_boolean(target,n,center,scale,rad))
# Step 3: correct a REAL obstruction in H1 camera by reassigning civic block
# geometry; do not change the camera to fake a clearer view.
removed=[]
for stem in ['H1_SECTOR_1_BLOCK_1_','H1_SECTOR_2_BLOCK_0_']:
    for o in list(bpy.data.objects):
        if o.name.startswith(stem) and o.type=='MESH':
            removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
# On the remaining H1 front row, displace obstructing building toward SIDE
# of the actual platform, so the street has a physical vista.
moved=[]
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith('H1_SECTOR_1_BLOCK_2_'):
        o.location.x+=60;moved.append(o.name)
# Existing H1 public pedestrian surface is turned into a clear route
# between two real carved courtyards, with glass civic galleries flanking it.
cube('E9_H1_REAL_PAVED_PUBLIC_ARRIVAL',(1540,-235,845),(68,350,9),'floor','H1_INHABITED_HIGH_CITY')
for x in (1455,1625):
    cube('E9_H1_OPEN_PORCH_COLONNADE_'+str(x),(x,-250,871),(21,340,35),
         'structure','H1_INHABITED_HIGH_CITY')
    for j in range(6):
        cube('E9_H1_OPEN_PUBLIC_PORTAL_%s_%s'%(x,j),
             (x,-415+j*67,868),(20,10,30),'glass','H1_INHABITED_HIGH_CITY')
# Lower-level carved horticultural courts and working civic porticoes
for x,y,z in [(1540,-150,760),(1840,85,865)]:
    cube('E9_INNER_LIVING_COURT_GARDEN_%d'%x,(x,y,z),(81,127,10),
         'garden','H1_INHABITED_HIGH_CITY')
    cube('E9_INNER_COURT_PUBLIC_GALLERY_%d'%x,(x,y-98,z+29),(115,22,12),
         'floor','H1_INHABITED_HIGH_CITY')
# Actual occupied voids in CENTRAL ridges need inner walkable bridges and platforms.
for side,x,y,z in [('WEST',-760,-425,310),('EAST',805,-430,355)]:
    cube('E9_'+side+'_POROUS_CIVIC_CHAMBER_FLOOR',(x,y,z-87),(670,405,18),
         'floor','NAVE_MULTILEVEL_PUBLIC_CITY')
    cube('E9_'+side+'_OPEN_PUBLIC_LOGGIA',(x,y,z+39),(470,70,11),
         'structure','NAVE_MULTILEVEL_PUBLIC_CITY')
    for k in range(4):
        cube('E9_'+side+'_GALLERY_CROSS_BEAM_'+str(k),
             (x-210+k*139,y,z+26),(17,365,22),
             'limestone','NAVE_MULTILEVEL_PUBLIC_CITY')
# NAVE is no longer just a road; remove a section of the central paving
# and create a distinct open assembly forum inset into the thoroughfare.
for nm in ['NAVE_CENTRAL_PEDESTRIAN_PROMENADE']:
    o=obj(nm);o.hide_render=True;o.hide_viewport=True
cube('E9_NAVE_OPEN_PUBLIC_COURT',(0,-165,176),(188,640,15),
     'floor','NAVE_MULTILEVEL_PUBLIC_CITY')
for i,z in enumerate((182,196,210)):
    cube('E9_NAVE_CIVIC_AMPHITHEATRE_STEP_'+str(i),(0,310+i*42,z),
         (160-26*i,73,14),'limestone','NAVE_MULTILEVEL_PUBLIC_CITY')
# Keep all official protected targets UNFINISHED even if research geometry exists
s['formal_art_adoption']=False;s['completed_targets']=0
s['minecraft_write']='FORBIDDEN'
s['official_coordinates_verified']=False
s['art_status']='UNREVIEWED_DIRECT_NATIVE_SURGERY'
s['e9_source_sha256']=hashlib.sha256(src.read_bytes()).hexdigest()
s['e9_sculpted_ridge_count']=len(ridge_edits)
s['e9_boolean_opening_count']=len(cuts)
s['e9_removed_obstruction_meshes']=len(removed)
new_blend=out/'E9_DIRECT_SCULPT_OPEN_PUBLIC_CITY_WORKING.blend'
s.camera=bpy.data.objects['urban_aerial']
bpy.ops.wm.save_as_mainfile(filepath=str(new_blend),compress=False)
for name in cameras:
    s.camera=bpy.data.objects[name]
    s.render.filepath=str(out/'after'/(name+'.png'))
    bpy.ops.render.render(write_still=True)
    print('E9_ACTUAL_EDIT_RENDER',name,flush=True)
s.camera=bpy.data.objects['urban_aerial']
bpy.ops.wm.save_as_mainfile(filepath=str(new_blend),compress=False)
report={'schema':'halo9-r4-e9-existing-blend-visual-surgery',
  'source_sha256':s['e9_source_sha256'],
  'new_blend_sha256':hashlib.sha256(new_blend.read_bytes()).hexdigest(),
  'ridgeline_mesh_edits':ridge_edits,'boolean_3d_carvings':cuts,
  'removed_h1_obstruction_meshes':removed,'moved_h1_meshes':moved,
  'before_mesh_count':len(names_before),
  'after_mesh_count':sum(o.type=='MESH' for o in bpy.data.objects),
  'camera_names_unchanged':cameras,
  'camera_transforms_unchanged':True,
  'formal_art_adoption':False,'completed_targets':0,
  'minecraft':'HOLD','official_coordinates_verified':False,
  'art_review':'UNREVIEWED_NO_PASS',
  'png_sha256':{group:{n:hashlib.sha256((out/group/(n+'.png')).read_bytes()).hexdigest()
                        for n in cameras} for group in ('before','after')}}
(out/'E9_TRUE_SURGERY_REPORT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('E9_TRUE_EXISTING_BLEND_DIRECT_SCULPT_COMPLETE',json.dumps(report),flush=True)
