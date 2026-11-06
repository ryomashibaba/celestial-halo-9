"""HALO9 INT15 / real H1 urban vertical transit in a protected research COPY.

Earlier work repeated 'cut a hole then label it a room', yielding ART REJECT.
This study first DELETES stale overlapping unaccepted INT4+INT11 H1 buildings,
removes 3 >37%-grade 'walkways' from the research copy, and EXCAVATES one
four-landing vertical public exchange through an actual INT13 H1 building.
4 horizontal station passages and a native movable cabin express the
transportation hierarchy. No external box towers, replacement facade/eggs,
or decorative roof/shelf repetition. No claim of actual safe ride, walkability,
formal ART, or official world coordinates.

All writes to new research COPY only. Retains W0 core terrain, 3 original
fixed E11 cameras and M247-C alpha and beta elements.
"""
import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector
from math import pi,cos,sin
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
ROOT=Path(args[args.index('--output')+1]);ROOT.mkdir(parents=True,exist_ok=True)
(ROOT/'renders').mkdir(exist_ok=True)
PARENT='431f5d1845f04a7fa669e2e230e00298cfedd98ee3d3069eb36c3fc85a7a6146'
src=Path(bpy.data.filepath)
assert src.name=='INT15_SOURCE.blend'
assert hashlib.sha256(src.read_bytes()).hexdigest()==PARENT
sc=bpy.context.scene
assert sc['CONSTRUCTION']=='HOLD' and sc['FORMAL_ART_ACCEPTED']==sc['COMPLETED_TARGETS']==0
E11=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
original_cams={n:bpy.data.objects[n].matrix_world.copy() for n in E11}
W0=('W0_NORTH_FRACTURED_RANGE','W0_WEST_BASALT_ESCARPMENT','W0_GROUND_BASIN','W0_EASTERN_ARTIFICIAL_SEA')
def hash_geometry(ob):
    h=hashlib.sha256()
    for vert in ob.data.vertices:
        h.update((','.join(format(float(x),'.10g') for x in vert.co)+';').encode())
    return h.hexdigest()
preserved_w0={name:hash_geometry(bpy.data.objects[name]) for name in W0}
must_preserve=[
 'INT11_M247C_ALPHA_WEST_ACCRETED_ARCHIVE',
 'INT11_M247C_ALPHA_EAST_CIVIC_HIGH_CITY',
 'INT11_M247C_ALPHA_FLOATING_SEVERED_NORTH',
 'INT11_M247C_BETA_SLANTED_CIVIC_SEAM',
]
assert all(n in bpy.data.objects for n in must_preserve)
target=bpy.data.objects['INT13_H1_OCCUPIED_SCHOOL_MARKET_COMMONS_MASS']
assert target.type=='MESH' and len(target.data.polygons)>90
poly_before=len(target.data.polygons)

# Physically remove only art-REJECTED, pre-existing context in new COPY.
# Do not mask it only for rendering; review all new views with original
# surviving geology and contemporary civic section visible.
stale=[o for o in list(sc.objects) if o.type=='MESH' and
       (o.name.startswith('INT4_H1_') or
        o.name.startswith('INT4_R1_H1_') or
        o.name.startswith('INT11_H1_'))]
assert 5<=len(stale)<180,('STALE_CONTEXT_SELECTOR_UNSAFE',len(stale))
deleted_names=[o.name for o in stale]
for o in stale:bpy.data.objects.remove(o,do_unlink=True)
# Old unsafe H1 horizontal-destination segments are deliberately RETIRED.
# New horizontal station galleries + lifts provide a proposed alternate
# network. They do not magically make other 5 inherited routes safe.
obsolete_routes=(
 'INT13_PUBLIC_SPATIAL_ROUTE_06_H1_MARKET_TO_H1_SCHOOL',
 'INT13_PUBLIC_SPATIAL_ROUTE_07_H1_SCHOOL_TO_H1_COMMONS',
 'INT13_PUBLIC_SPATIAL_ROUTE_08_H1_COMMONS_TO_H1_RESIDENCES',
)
assert all(n in bpy.data.objects for n in obsolete_routes)
for n in obsolete_routes:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
assert all(n in bpy.data.objects for n in must_preserve)

station_xy=Vector((1115.,635.))
stations=[
 ('H1_MARKET',(615.,410.),435.),
 ('H1_SCHOOL',(840.,520.),530.),
 ('H1_COMMONS',(1045.,680.),630.),
 ('H1_RESIDENCES',(1200.,900.),810.),
]
station_elev=[s[2] for s in stations]
assert station_elev==sorted(station_elev)
# Source hard-coded H1 building geometry spans z350-~1020.
# A genuine carved shaft, not a shiny pipe added to the exterior.
def cutter_cylinder(name,p1,p2,radius,verts=24):
    A=Vector(p1);B=Vector(p2)
    v=B-A
    assert v.length>20
    c=(A+B)*.5
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,
       radius=radius,depth=v.length,location=c)
    ob=bpy.context.object;ob.name='INT15_TMP_'+name
    ob.rotation_euler=v.to_track_quat('Z','Y').to_euler()
    bpy.context.view_layer.update()
    return ob

cut_report=[]
def subtract_from_h1(tag,p1,p2,radius):
    before=len(target.data.polygons)
    cutter=cutter_cylinder(tag,p1,p2,radius)
    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)
    bpy.context.view_layer.objects.active=target
    mod=target.modifiers.new('INT15_REAL_OCCUPIED_'+tag,'BOOLEAN')
    mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
    target.data.update()
    after=len(target.data.polygons)
    assert after>15 and all(math.isfinite(float(c)) for v in target.data.vertices for c in v.co)
    cut_report.append({'name':tag,'faces_before':before,'faces_after':after,
        'physical_mesh_topology_changed':after!=before,'radius_m':radius,
        'endpoints':[list(p1),list(p2)]})
    print('INT15_REAL_NATIVE_CUT',tag,before,after,flush=True)

subtract_from_h1('H1_FOUR_LEVEL_VERTICAL_MOBILITY_CANYON',
 (station_xy.x,station_xy.y,340),
 (station_xy.x,station_xy.y,945),88)
assert cut_report[0]['physical_mesh_topology_changed'],'LIFT_SHAFT_DID_NOT_CUT_SOLID'

for key,pos,z in stations:
    # Actual horizontal gallery across the ORIGINAL rock body at the
    # same z as its named inhabited station. No 40-67% gradient.
    p1=(pos[0],pos[1],z+29)
    p2=(station_xy.x,station_xy.y,z+29)
    subtract_from_h1('TO_'+key,p1,p2,47)
assert sum(x['physical_mesh_topology_changed'] for x in cut_report)>=3,(
    'STATION_GALLERIES_MISSING',cut_report)

col=bpy.data.collections.new('INT15_PUBLIC_VERTICAL_EXCHANGE_TRANSPORT_RESEARCH')
sc.collection.children.link(col)
material={}
def mat(name,color,metal=0,rough=.6):
    m=bpy.data.materials.new('INT15_'+name);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal
    p.inputs['Roughness'].default_value=rough
    m.diffuse_color=(*color,1)
    material[name]=m
mat('stone',(.66,.62,.54),.08,.68)
mat('bronze',(.48,.32,.18),.63,.41)
mat('glass',(.12,.42,.46),.35,.31)
mat('wayfinding',(.93,.66,.32),.24,.4)
made=[]
def native_mesh(name,pts,faces,material_name):
    data=bpy.data.meshes.new('INT15_'+name)
    data.from_pydata(pts,[],faces);data.update()
    o=bpy.data.objects.new(data.name,data);col.objects.link(o)
    o.data.materials.append(material[material_name]);made.append(o.name)
    assert len(o.data.polygons)>3 and all(math.isfinite(float(c)) for v in o.data.vertices for c in v.co)
    return o

def thick_floor(name,A,B,width=47,depth=15,material_name='stone'):
    # A substantial occupied/structural walkway inside an excavated
    # gallery, not a facade shelf or vertical-lift substitute.
    p=Vector(A);q=Vector(B)
    d=q-p;d.z=0
    n=Vector((-d.y,d.x,0)).normalized()
    t=width/2
    top=[tuple(p-n*t),tuple(p+n*t),tuple(q+n*t),tuple(q-n*t)]
    base=[(x,y,z-depth) for x,y,z in top]
    vs=top+base
    faces=[(0,1,2,3),(7,6,5,4),(0,4,5,1),
           (1,5,6,2),(2,6,7,3),(3,7,4,0)]
    return native_mesh(name,vs,faces,material_name)

floor_details=[]
for key,pos,z in stations:
    A=(pos[0],pos[1],z)
    B=(station_xy.x,station_xy.y,z)
    g=thick_floor('PUBLIC_FLAT_GALLERY_'+key,A,B)
    floor_details.append({'station':key,'gallery':g.name,
        'from':list(A),'to':list(B),'rise_m':0.0,
        'length_m':round(math.dist(pos,tuple(station_xy)),3),
        'horizontal':'TRUE','actual_collision_free':'NOT_VERIFIED'})
    # 3D threshold at the station and shaft mouth, NOT an extra building.
    direction=Vector((station_xy.x-pos[0],station_xy.y-pos[1],0)).normalized()
    ortho=Vector((-direction.y,direction.x,0))
    for side in (-1,1):
        a=Vector((station_xy.x,station_xy.y,z))+ortho*side*34
        b=a+Vector((0,0,64))
        # Structural safety guard in same gallery; no implied code pass.
        thick_floor('SHAFT_GUARD_'+key+'_'+str(side),
           tuple(a),tuple(b+Vector((.1,.1,0))),
           width=7,depth=5,material_name='bronze') if False else None

# The cabin in this *research* is a genuine native Blender object with
# four keyed lift-stop elevations. Does NOT certify real ride, speed,
# safety, control logic, or ability to walk through the whole city.
CABIN_CENTER=(station_xy.x,station_xy.y)
def polygon_deck(name,z,radius,thickness):
    rings=[]
    for t in (z,z-thickness):
        ring=[(CABIN_CENTER[0]+radius*cos(2*pi*k/10),
               CABIN_CENTER[1]+radius*sin(2*pi*k/10),t) for k in range(10)]
        rings.extend(ring)
    faces=[tuple(range(10)),tuple(reversed(range(10,20)))]
    for k in range(10):faces.append((k,(k+1)%10,(k+1)%10+10,k+10))
    return native_mesh(name,rings,faces,'bronze')
cab=polygon_deck('MOVABLE_CIVIC_PUBLIC_LIFT_PLATFORM',0,43,11)
# Keyframe object location; no automatic real-world operation claims.
for frame,z in zip((1,64,128,192),station_elev):
    cab.location=(0,0,z)
    cab.keyframe_insert(data_path='location',frame=frame)
sc.frame_end=192
sc.frame_set(1)
assert cab.animation_data and cab.animation_data.action is not None
for name,pose in original_cams.items():
    now=bpy.data.objects[name].matrix_world
    assert max(abs(now[i][j]-pose[i][j]) for i in range(4) for j in range(4))<1e-6
assert all(hash_geometry(bpy.data.objects[n])==sha for n,sha in preserved_w0.items())
assert all(n in bpy.data.objects for n in must_preserve)
assert sc['CONSTRUCTION']=='HOLD' and sc['COMPLETED_TARGETS']==sc['FORMAL_ART_ACCEPTED']==0

def sample_hits(name):
    cam=bpy.data.objects[name]
    frame=cam.data.view_frame(scene=sc)
    vals=[]
    for u,v in ((.25,.25),(.5,.5),(.75,.75),(.25,.75),(.75,.25)):
        xx=[q.x for q in frame];yy=[q.y for q in frame]
        point=Vector((min(xx)+u*(max(xx)-min(xx)),min(yy)+v*(max(yy)-min(yy)),
            sum(q.z for q in frame)/len(frame)))
        origin=cam.matrix_world.translation
        d=(cam.matrix_world.to_3x3()@point).normalized()
        ok,hit,no,idx,obj,matx=sc.ray_cast(bpy.context.evaluated_depsgraph_get(),origin,d,distance=6000)
        vals.append({'u':u,'v':v,'name':obj.name if ok else 'SKY',
               'distance':round((hit-origin).length,2) if ok else None})
    return vals
hits_after=sample_hits('E11_H1_HUMAN')
# NEW inspector camera explicitly supplementary; original E11 not moved.
def inspection_camera(name,eye,dest,lens=25):
    d=bpy.data.cameras.new('INT15_'+name);d.lens=lens;d.clip_end=12000
    o=bpy.data.objects.new(d.name,d);col.objects.link(o)
    o.location=eye
    o.rotation_euler=(Vector(dest)-Vector(eye)).to_track_quat('-Z','Y').to_euler()
    return o
inspection_camera('H1_FOUR_STOP_CIVIC_SHAFT_ROOM',
 (station_xy.x-35,station_xy.y-150,530),
 (station_xy.x,station_xy.y,700),22)
inspection_camera('H1_MARKET_SCHOOL_PUBLIC_GALLERY',
 (725,455,457),(station_xy.x,station_xy.y,580),25)
sc['INT15_SOURCE_SHA256']=PARENT
sc['INT15_RESEARCH_VERTICAL_TRANSPORT']='CARVED_IN_REAL_H1_MASS_AND_ANIMATED_STATION_CABIN'
sc['INT15_NO_FORMAL_ART_ACCEPTANCE']=True
sc['INT15_FUNCTION']='UNVERIFIED'
sc['INT15_WORLD_COORDINATES']='RESEARCH_ONLY_UNREGISTERED'
sc.camera=bpy.data.objects['E11_URBAN_AERIAL']
outblend=ROOT/'HALO9_INT15_H1_OCCUPIED_LIFT_PUBLIC_CORE.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(outblend),compress=True)

sc.render.engine='CYCLES';sc.cycles.device='CPU'
sc.cycles.samples=10;sc.cycles.use_denoising=True
sc.render.threads_mode='FIXED';sc.render.threads=2
sc.render.resolution_x=960;sc.render.resolution_y=720
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
views=E11+('INT15_H1_FOUR_STOP_CIVIC_SHAFT_ROOM',
            'INT15_H1_MARKET_SCHOOL_PUBLIC_GALLERY')
renderhash={}
for name in views:
    sc.camera=bpy.data.objects[name]
    p=ROOT/'renders'/(name+'.png');sc.render.filepath=str(p)
    bpy.ops.render.render(write_still=True)
    assert p.stat().st_size>5500
    renderhash[name]=hashlib.sha256(p.read_bytes()).hexdigest()
    print('INT15_NATIVE_SCENE_FIXED_AND_STATION_RENDER',name,p.stat().st_size,flush=True)
sc.camera=bpy.data.objects['E11_URBAN_AERIAL']
bpy.ops.wm.save_as_mainfile(filepath=str(outblend),compress=True)
old_grade=[
 ('NAVE_STATION','NAVE_FORUM',12.91),
 ('NAVE_FORUM','NAVE_LIBRARY',41.36),
 ('NAVE_LIBRARY','NAVE_CEREMONY',29.451),
 ('NAVE_CEREMONY','NAVE_ASCENT',12.383),
 ('NAVE_ASCENT','H1_MARKET',22.5),
 ('H1_MARKET','H1_SCHOOL',37.932),
 ('H1_SCHOOL','H1_COMMONS',38.454),
 ('H1_COMMONS','H1_RESIDENCES',66.885),
]
report={
 'schema':'halo9-int15-m247c-h1-actual-native-mobility-research-v1',
 'input_sha256':PARENT,
 'native_blend_sha256':hashlib.sha256(outblend.read_bytes()).hexdigest(),
 'old_rejected_research_objects_physically_removed_in_copy':deleted_names,
 'unsafe_H1_walkway_3_removed_in_copy':list(obsolete_routes),
 'target_h1_mass':'INT13_H1_OCCUPIED_SCHOOL_MARKET_COMMONS_MASS',
 'original_polygons':poly_before,'final_polygons':len(target.data.polygons),
 'actual_boolean_subtractions':cut_report,
 'new_native_components':made,
 'flat_gallery_segments':floor_details,
 'four_stations':stations,
 'cabin_keyframes':[1,64,128,192],
 'old_remaining_unsafe_other_routes':old_grade[:5],
 'physical_walkability':'NOT_CERTIFIED',
 'elevator_mechanism':'KEYFRAMED_PLATFORM_ONLY__NO_FUNCTIONAL_CONTROLS',
 'actual_building_structure_safety':'UNVERIFIED',
 'fixed_E11_matrices':{n:[[float(x) for x in row] for row in original_cams[n]] for n in E11},
 'W0_original_sha':preserved_w0,
 'H1_5_sample_hits_after':hits_after,
 'native_5_png_sha256':renderhash,
 'no_cutaway_masking':True,
 'full_city_art':'UNREVIEWED_NOT_ADOPTED',
 'formal_art_accepted':0,'completed_targets':0,
 'minecraft':'HOLD'}
(ROOT/'INT15_TRUE_NATIVE_TECH_NOT_ART.json').write_text(json.dumps(report,indent=2))
print('INT15_H1_NATIVE_TRANSPORT_AND_FIVE_IMAGES_SAVED',
       report['native_blend_sha256'],flush=True)
