"""INT14 / H1: visually directed REPAIR of an observed fatal blocking wall.

Uses the existing, verified INT13 native BLEND as a research copy.
No new skyline/roof/facade, no boxes or shells. Reopens the physical H1
school/market/commons mass at the unchanged original eye position, cutting
a broad human-facing inhabited public hall that intersects the previously
carved market atrium, rather than simply hiding the mass for a screenshot.

The fixed-E11 original H1 camera is inside the rejected INT13 H1 solid.
Only that one rejected study mesh is modified. This is NOT a functional
or formal art approval; rendering both fixed and newly labeled inspection
views is compulsory.
"""
import bpy, math, json, hashlib, sys
from mathutils import Vector
from pathlib import Path

args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
ROOT=Path(args[args.index('--output')+1]); ROOT.mkdir(parents=True,exist_ok=True)
(ROOT/'renders').mkdir(exist_ok=True)
src=Path(bpy.data.filepath)
PARENT='da098354430d0aa62d0f4825c23127340aba8e8c353c6dc33f53c5b8b0fec3c3'
assert src.name=='INT14_SOURCE.blend'
assert hashlib.sha256(src.read_bytes()).hexdigest()==PARENT
scene=bpy.context.scene
assert scene['CONSTRUCTION']=='HOLD' and scene['FORMAL_ART_ACCEPTED']==scene['COMPLETED_TARGETS']==0
e11=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
poses={n:bpy.data.objects[n].matrix_world.copy() for n in e11}
w0=('W0_NORTH_FRACTURED_RANGE','W0_WEST_BASALT_ESCARPMENT',
    'W0_GROUND_BASIN','W0_EASTERN_ARTIFICIAL_SEA')
def datahash(ob):
    hash=hashlib.sha256()
    for v in ob.data.vertices:
        hash.update((','.join(f'{float(x):.10g}' for x in v.co)+';').encode())
    return hash.hexdigest()
w0_hash={n:datahash(bpy.data.objects[n]) for n in w0}
TARGET='INT13_H1_OCCUPIED_SCHOOL_MARKET_COMMONS_MASS'
target=bpy.data.objects[TARGET]
assert target.type=='MESH' and len(target.data.polygons)>=30
original_mesh_count=len(target.data.polygons)
cam=bpy.data.objects['E11_H1_HUMAN']
origin=cam.matrix_world.translation.copy()
def screen_ray(u,v):
    frame=cam.data.view_frame(scene=scene)
    xx=[p.x for p in frame];yy=[p.y for p in frame]
    local=Vector((min(xx)+u*(max(xx)-min(xx)),
                  min(yy)+v*(max(yy)-min(yy)),
                  sum(q.z for q in frame)/len(frame)))
    return (cam.matrix_world.to_3x3()@local).normalized()
def hit(u,v):
    bpy.context.view_layer.update()
    direction=screen_ray(u,v)
    yes,point,normal,index,ob,mat=scene.ray_cast(bpy.context.evaluated_depsgraph_get(),origin,direction,distance=4000)
    return {'name':ob.name if yes else 'SKY',
            'distance':round((point-origin).length,3) if yes else None,
            'u':u,'v':v}
points=[(u,v) for v in (.18,.34,.5,.66,.82) for u in (.18,.34,.5,.66,.82)]
before=[hit(u,v) for u,v in points]
count_before=sum(h['name']==TARGET for h in before)
center_before=hit(.5,.5)
print('INT14_PHYSICAL_H1_FIXED_EYE_BEFORE',center_before,
      'blocking_samples',count_before,flush=True)
assert count_before>=6 or center_before['name']==TARGET,(
  'H1_VIEW_BLOCKED_BY_DIFFERENT_OBJECT_ABORT_UNGROUNDED_EDIT',
  count_before,center_before)

# A continuous negative public space that STARTS BEHIND the original
# camera, shares its immediate floor, and joins the existing market
# courtyard/sky room. 5 individually authored section profiles, not a
# replacement sphere or generic repeated room.
direction=screen_ray(.5,.5)
right=direction.cross(Vector((0,0,1))).normalized()
up=right.cross(direction).normalized()
if up.z<0: up=-up
ringspec=[
 (-95,81,91,-8),
 (12,89,117,0),
 (145,118,150,31),
 (305,135,194,74),
 (515,157,215,104),
 (710,144,205,128)
]
N=15
verts=[]
for k,(d,width,height,rise) in enumerate(ringspec):
    middle=origin+direction*d+up*rise+right*15*math.sin(k*.8)
    for i in range(N):
        angle=2*math.pi*i/N
        irregular=1+.06*math.sin(3*angle+.3*k)+.04*math.cos(5*angle-.2*k)
        pos=middle+right*width*math.cos(angle)*irregular+up*height*math.sin(angle)*irregular
        verts.append(tuple(pos))
faces=[tuple(range(N)),
       tuple(reversed(range((len(ringspec)-1)*N,len(ringspec)*N)))]
for k in range(len(ringspec)-1):
    for i in range(N):
        a=k*N+i;b=k*N+(i+1)%N
        faces.append((a,a+N,b+N,b))
cutmesh=bpy.data.meshes.new('INT14_TEMP_H1_CONTINUOUS_PUBLIC_ENTRY_NEGATIVE_SPACE')
cutmesh.from_pydata(verts,[],faces);cutmesh.update()
cut=bpy.data.objects.new(cutmesh.name,cutmesh)
scene.collection.objects.link(cut)
bpy.ops.object.select_all(action='DESELECT')
target.select_set(True)
bpy.context.view_layer.objects.active=target
operation=target.modifiers.new('INT14_H1_VISIBLE_CIVIC_ENTRY_IN_EXISTING_MASS','BOOLEAN')
operation.operation='DIFFERENCE';operation.solver='EXACT';operation.object=cut
bpy.ops.object.modifier_apply(modifier=operation.name)
bpy.data.objects.remove(cut,do_unlink=True)
assert len(target.data.polygons)>original_mesh_count+10,(
    'ENTRY_HALL_REAL_BOOLEAN_NOT_CREATED',
    original_mesh_count,len(target.data.polygons))
assert all(math.isfinite(float(c)) for v in target.data.vertices for c in v.co)
after=[hit(u,v) for u,v in points]
count_after=sum(h['name']==TARGET for h in after)
center_after=hit(.5,.5)
print('INT14_PHYSICAL_H1_FIXED_EYE_AFTER',center_after,
      'blocking_samples',count_after,flush=True)
# The original human eye must no longer stare immediately into
# the same research building, or this would be another fake image fix.
assert count_after<=count_before-3 or (
 center_before['name']==TARGET and center_after['name']!=TARGET),(
  'FIXED_E11_PUBLIC_HALL_STILL_OBSCURED',
  count_before,count_after,center_before,center_after)

# Actual old nine-route gradients remain disclosed: the new entrance
# is not by itself proof of steep-path fix or walkability.
parent_spatial=[
 ('W0_ARRIVAL','NAVE_STATION',(-235,-870,48),(-110,-300,90)),
 ('NAVE_STATION','NAVE_FORUM',(-110,-300,90),(-68,-40,124)),
 ('NAVE_FORUM','NAVE_LIBRARY',(-68,-40,124),(-240,150,230)),
 ('NAVE_LIBRARY','NAVE_CEREMONY',(-240,150,230),(35,325,326)),
 ('NAVE_CEREMONY','NAVE_ASCENT',(35,325,326),(260,390,355)),
 ('NAVE_ASCENT','H1_MARKET',(260,390,355),(615,410,435)),
 ('H1_MARKET','H1_SCHOOL',(615,410,435),(840,520,530)),
 ('H1_SCHOOL','H1_COMMONS',(840,520,530),(1045,680,630)),
 ('H1_COMMONS','H1_RESIDENCES',(1045,680,630),(1200,900,810)),
]
gradients=[]
for a,b,p,q in parent_spatial:
    horizontal=math.dist(p[:2],q[:2])
    rise=q[2]-p[2]
    gradients.append({'from':a,'to':b,
        'rise_m':rise,'horizontal_m':round(horizontal,3),
        'grade_pct':round(100*rise/horizontal,3),
        'accessible_solution':'UNBUILT_UNVERIFIED'})
assert len(gradients)==9
for n,m in poses.items():
    now=bpy.data.objects[n].matrix_world
    assert max(abs(now[i][j]-m[i][j]) for i in range(4) for j in range(4))<1e-6
assert all(datahash(bpy.data.objects[n])==sha for n,sha in w0_hash.items())
assert scene['CONSTRUCTION']=='HOLD' and scene['FORMAL_ART_ACCEPTED']==scene['COMPLETED_TARGETS']==0
scene['INT14_RESEARCH_H1_ENTRY_CUT']='ACTUAL_BOOLEAN_IN_EXISTING_PUBLIC_MASS'
scene['INT14_PARENT_SHA256']=PARENT
scene['INT14_FORMAL_ART_ADOPTED']=0
scene['INT14_PUBLIC_WALKABLE']='NOT_VERIFIED'
scene.camera=bpy.data.objects['E11_URBAN_AERIAL']
file=ROOT/'HALO9_INT14_H1_PUBLIC_ENTRY_HUMAN_SIGHTLINE.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(file),compress=True)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=13
scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=1024;scene.render.resolution_y=768
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
names=e11+('INT13_H1_MARKET_SCHOOL_INTERIOR',)
images={}
for name in names:
    scene.camera=bpy.data.objects[name]
    output=ROOT/'renders'/(name+'.png')
    scene.render.filepath=str(output)
    bpy.ops.render.render(write_still=True)
    assert output.stat().st_size>7000
    images[name]=hashlib.sha256(output.read_bytes()).hexdigest()
    print('INT14_TRUE_CYCLES_FIXED_E11_RENDER',name,output.stat().st_size,flush=True)
scene.camera=bpy.data.objects['E11_URBAN_AERIAL']
bpy.ops.wm.save_as_mainfile(filepath=str(file),compress=True)
result={
 'schema':'halo9-int14-h1-public-entrance-native-repair-v1',
 'input_sha256':PARENT,
 'saved_blend_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),
 'real_mesh_modified':TARGET,
 'polygons_before':original_mesh_count,
 'polygons_after':len(target.data.polygons),
 'fixed_h1_camera_center_before':center_before,
 'fixed_h1_camera_center_after':center_after,
 'fixed_h1_25sample_hit_before':before,
 'fixed_h1_25sample_hit_after':after,
 'fixed_h1_research_wall_hits_before':count_before,
 'fixed_h1_research_wall_hits_after':count_after,
 'old_route_grade_audit':gradients,
 'original_three_E11_camera_matrices':{n:[[float(x) for x in row] for row in poses[n]] for n in e11},
 'protected_W0_vertex_sha256':w0_hash,
 'real_native_render_sha256':images,
 'source_masses_unhidden_no_cutaway_substitution':True,
 'method':'REAL_NEGATIVE_PUBLIC_ENTRY_IN_EXISTING_H1_MASS_NOT_REPLACEMENT_BOX',
 'walkability':'UNVERIFIED',
 'formal_art_accepted':0,'completed_targets':0,'minecraft':'HOLD',
 'art':'UNREVIEWED_NOT_ADOPTED'}
(ROOT/'INT14_NATIVE_EVIDENCE_NOT_ART.json').write_text(json.dumps(result,indent=2))
print('INT14_REAL_H1_ENTRY_CARVED_AND_FIXED_VIEWS_SAVED',
      result['saved_blend_sha256'],flush=True)
