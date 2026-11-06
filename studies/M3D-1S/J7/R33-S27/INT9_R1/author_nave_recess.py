"""INT9-R1: correct the dominant NAVE human-eye obstruction seen in INT9.
This surgical negative-space edit operates on EXISTING integrated native
geometry, not a fresh box/shell generator. It is background Blender editing,
NOT GUI hand-sculpt. Original E11 cameras are immutable. Research only.
"""
import bpy,math,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[args.index('--output')+1]);out.mkdir(parents=True,exist_ok=True)
(out/'renders').mkdir(exist_ok=True)
src=Path(bpy.data.filepath)
SOURCE='c407de616a0e2cf8807fb5ac79c102a052062725f6e89f75b978570a2b7693c7'
assert src.name=='INT9_R1_SOURCE.blend'
assert hashlib.sha256(src.read_bytes()).hexdigest()==SOURCE
scene=bpy.context.scene
assert scene['CONSTRUCTION']=='HOLD'
assert scene['COMPLETED_TARGETS']==scene['FORMAL_ART_ACCEPTED']==0
orig_cameras=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
poses={n:bpy.data.objects[n].matrix_world.copy() for n in orig_cameras}
cam=bpy.data.objects['E11_NAVE_HUMAN']

def screen_ray(u,v):
    frame=cam.data.view_frame(scene=scene)
    xx=[q.x for q in frame];yy=[q.y for q in frame]
    local=Vector((min(xx)+u*(max(xx)-min(xx)),
                  min(yy)+v*(max(yy)-min(yy)),
                  sum(q.z for q in frame)/len(frame)))
    return cam.matrix_world.translation,(cam.matrix_world.to_3x3()@local).normalized()

def trace(u,v):
    origin,ray=screen_ray(u,v)
    dg=bpy.context.evaluated_depsgraph_get()
    hit,location,normal,face,obj,matrix=scene.ray_cast(dg,origin,ray,distance=5000)
    return {'hit':bool(hit),
        'name':obj.name if hit else 'SKY',
        'distance':round(float((location-origin).length),4) if hit else None,
        'u':u,'v':v}

points=[(u,v) for u in (.64,.74,.84,.91) for v in (.32,.44,.56,.67)]
hits=[trace(u,v) for u,v in points]
exclusions=(
 'INT7_NAVE_CONTINUOUS_PUBLIC_CENTRAL_BOULEVARD',
 'INT7_NAVE_STATION_ACCESS',
 'INT7_NAVE_WEST_READING_RAMP',
 'INT7_M247_NAVE_WEST_CLIFF_LEARNING_ACCESS',
)
hits=[h for h in hits if h['hit'] and h['distance']<1500]
eligible=[h for h in hits if h['name'].startswith('INT7_')
          and h['name'] not in exclusions]
assert eligible,('NO_NAVE_FOREGROUND_VISIBLE_TARGET',hits)
freq={}
for h in eligible:
    n=h['name']
    freq.setdefault(n,[]).append(h)
# Most frequently blocking in the original fixed camera's right-hand view;
# tie broken toward nearer obstruction (not a distant civic destination).
winner=sorted(freq,key=lambda k:(-len(freq[k]),
                 min(h['distance'] for h in freq[k])))[0]
selected=min(freq[winner],key=lambda h:
    abs(h['u']-.77)+abs(h['v']-.50))
target=bpy.data.objects[winner]
assert target.type=='MESH' and len(target.data.polygons)>=6
assert target.name.startswith('INT7_')
assert not any(x in target.name for x in ('W0_','E11_'))
source_polys=len(target.data.polygons)
print('INT9_R1_REAL_NAVE_VISIBLE_OBSTRUCTION',{
 'winner':winner,'selected':selected,
 'freq':{k:len(a) for k,a in freq.items()}},flush=True)

origin,d=screen_ray(selected['u'],selected['v'])
right=d.cross(Vector((0,0,1))).normalized()
up=right.cross(d).normalized()
dist=selected['distance']
half_width=max(52,min(135,dist*.24))
half_height=max(75,min(155,dist*.31))
# Tapered, irregular and heavily oblique architectural daylight aperture
# not a standard circular porthole. Sign/normal orientation for Boolean
# was verified in INT9: first cap forward and far cap reverse.
rings=[]
for k,(t,wx,hy,shift) in enumerate([
   (dist-60,half_width*.88,half_height*.92,-.08),
   (dist+30,half_width,half_height,0.),
   (dist+260,half_width*1.24,half_height*1.25,.11),
   (dist+570,half_width*.96,half_height*.86,-.10)]):
    center=origin+d*t+right*(shift*half_width)
    ring=[]
    for i in range(15):
        angle=2*math.pi*i/15
        modifier=1+.11*math.sin(3*angle+.62*k)+.065*math.cos(5*angle)
        vertex=center+right*(wx*math.cos(angle)*modifier)+up*(hy*math.sin(angle)*modifier)
        ring.append(tuple(vertex))
    rings.append(ring)
n=len(rings[0])
verts=[p for ring in rings for p in ring]
faces=[tuple(range(n)),tuple(reversed(range((len(rings)-1)*n,len(rings)*n)))]
for k in range(len(rings)-1):
    for i in range(n):
        a=k*n+i;b=k*n+(i+1)%n
        faces.append((a,a+n,b+n,b))
md=bpy.data.meshes.new('INT9_R1_TEMP_DAYLIT_NAVE_VOID')
md.from_pydata(verts,[],faces);md.update()
cutter=bpy.data.objects.new(md.name,md)
scene.collection.objects.link(cutter)
bpy.ops.object.select_all(action='DESELECT')
target.select_set(True);bpy.context.view_layer.objects.active=target
mod=target.modifiers.new('INT9_R1_NAVE_DAYLIT_CIVIC_ATRIUM','BOOLEAN')
mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cutter,do_unlink=True)
assert len(target.data.polygons)>source_polys+3,('CUT_NOT_SUBSTANTIAL',winner,source_polys,len(target.data.polygons))
assert all(math.isfinite(float(c)) for v in target.data.vertices for c in v.co)
bpy.context.view_layer.update()
after=trace(selected['u'],selected['v'])
assert after['name']!=winner or (after['distance'] is not None and after['distance']>dist+100),(
    'NAVE_SIGHTLINE_NOT_REALLY_OPENED',selected,after)
print('INT9_R1_REAL_NAVE_CUT_OPEN',source_polys,len(target.data.polygons),
      selected,after,flush=True)

for name,old in poses.items():
    now=bpy.data.objects[name].matrix_world
    assert max(abs(now[i][j]-old[i][j]) for i in range(4) for j in range(4))<1e-6
assert scene['CONSTRUCTION']=='HOLD' and scene['COMPLETED_TARGETS']==scene['FORMAL_ART_ACCEPTED']==0
scene['INT9_R1_PARENT_SHA256']=SOURCE
scene['INT9_R1_NAVE_CUT_TARGET']=winner
scene['INT9_R1_METHOD']='IMAGE_LED_NATIVE_CUT_NOT_GUI_HAND_SCULPT'
scene['INT9_R1_NO_OFFICIAL_WORLD_ANCHORS']=True
scene.camera=bpy.data.objects['E11_URBAN_AERIAL']
dst=out/'HALO9_INT9_R1_NAVE_DAYLIT_CIVIC_RECESS.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=True)
scene.render.engine='CYCLES';scene.cycles.device='CPU'
scene.cycles.samples=12;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=2
scene.render.resolution_x=1100;scene.render.resolution_y=825
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
sha={}
for name in orig_cameras:
    scene.camera=bpy.data.objects[name]
    path=out/'renders'/(name+'.png')
    scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    assert path.stat().st_size>5000
    sha[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    print('INT9_R1_TRUE_FIXED_E11_RENDER',name,path.stat().st_size,flush=True)
result={
 'schema':'halo9-int9-r1-obstruction-cut-v1',
 'source_sha256':SOURCE,
 'edited_blend_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),
 'original_cameras_unchanged':True,
 'nave_selected_obstruction':winner,
 'nave_cut_polygon_count_before':source_polys,
 'nave_cut_polygon_count_after':len(target.data.polygons),
 'fixed_nave_screen_ray_before':selected,
 'fixed_nave_screen_ray_after':after,
 'fixed_camera_render_sha256':sha,
 'minecraft':'HOLD','formal_art_accepted':0,'completed_targets':0,
 'art':'UNREVIEWED_NOT_ADOPTED','function':'UNKNOWN',
 'source_int9_h1_cavity_preserved':True}
(out/'INT9_R1_TECH_NOT_ART.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print('INT9_R1_TRUE_NATIVE_CIVIC_RECESS_COMPLETE',result['edited_blend_sha256'],flush=True)
