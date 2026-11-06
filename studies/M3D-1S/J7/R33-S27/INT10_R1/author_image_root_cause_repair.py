"""INT10-R1 true 3D camera-motivated root correction of INT10 research city.
Move only unaccepted civic access mesh in COPY; carve a large inhabited public
canyon along original H1 eyesight. NO camera changes, no main/W0 terrain writes.
This is background/native mesh surgery, not GUI hand-sculpt and not ART pass.
"""
import bpy,math,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
out=Path(args[args.index('--output')+1]);out.mkdir(parents=True,exist_ok=True)
(out/'renders').mkdir(exist_ok=True)
src=Path(bpy.data.filepath)
SOURCE='b5a38f353c814acaade8848ca420c3a38cfa724e41a1aafeb07a071244c6c94e'
assert src.name=='INT10_R1_SOURCE.blend' and hashlib.sha256(src.read_bytes()).hexdigest()==SOURCE
sc=bpy.context.scene
assert sc['CONSTRUCTION']=='HOLD' and sc['FORMAL_ART_ACCEPTED']==sc['COMPLETED_TARGETS']==0
names=('E11_NAVE_HUMAN','E11_H1_HUMAN','E11_URBAN_AERIAL')
cameras={n:bpy.data.objects[n].matrix_world.copy() for n in names}
# W0 actual terrain/sea remain BYTE-identical mesh vertex coordinate sets
preserve=('W0_NORTH_FRACTURED_RANGE','W0_WEST_BASALT_ESCARPMENT',
          'W0_GROUND_BASIN','W0_EASTERN_ARTIFICIAL_SEA')
def geomhash(ob):
    m=hashlib.sha256()
    for v in ob.data.vertices:
        m.update((','.join(format(float(x),'.10g') for x in v.co)+';').encode())
    return m.hexdigest()
terrain={n:geomhash(bpy.data.objects[n]) for n in preserve}

def ray(name,u=.5,v=.5):
    bpy.context.view_layer.update()
    frame=bpy.data.objects[name].data.view_frame(scene=sc)
    fx=[p.x for p in frame];fy=[p.y for p in frame]
    c=bpy.data.objects[name]
    point=Vector((min(fx)+u*(max(fx)-min(fx)),
                  min(fy)+v*(max(fy)-min(fy)),
                  sum(p.z for p in frame)/4))
    origin=c.matrix_world.translation
    direction=(c.matrix_world.to_3x3()@point).normalized()
    ok,loc,no,idx,obj,m=sc.ray_cast(bpy.context.evaluated_depsgraph_get(),origin,direction,distance=6000)
    return {'name':obj.name if ok else 'SKY','distance':round(float((loc-origin).length),3) if ok else None}
before={n:ray(n) for n in names}
assert before['E11_NAVE_HUMAN']['name']=='INT10_W0_MARITIME_CIVIC_APPROACH',before
assert before['E11_H1_HUMAN']['name']=='INT10_H1_HIGH_CITY_INHABITED_MARKET_STREET',before
edits=[]
def shift_ribbon(name,dxs):
    ob=bpy.data.objects[name]
    assert ob.type=='MESH' and len(ob.data.vertices)==4*len(dxs),name
    for i,d in enumerate(dxs):
        for j in range(4):
            ob.data.vertices[4*i+j].co.x+=d
    ob.data.update()
    edits.append({'name':name,'stations':len(dxs),'shifts_x_m':dxs})
# Relocate occupied marine approach away from camera without deleting
# route, leaving an unobstructed central great-civic vista.
shift_ribbon('INT10_W0_MARITIME_CIVIC_APPROACH',[0,72,148,205,180,135])
# The new H1 high-city route originally PUT ITS FLOOR at the E11 camera's
# eye z=438.7. Move route along east public-city rim (not hide it in render).
shift_ribbon('INT10_H1_HIGH_CITY_INHABITED_MARKET_STREET',
             [145,195,220,155,80,26,0])
# Earlier rejected research street similarly overlaps E11_H1 at 30m.
# Only research COPY is edited, never the old original.
older=bpy.data.objects['INT4_H1_PUBLIC_BOULEVARD']
assert older.type=='MESH' and len(older.data.vertices)>=8
moved_old=0
for v in older.data.vertices:
    if 90<=v.co.y<=730:
        taper=max(.25,1-abs(v.co.y-315)/680)
        v.co.x+=155*taper
        moved_old+=1
older.data.update()
edits.append({'name':older.name,'vertices_shifted':moved_old,'original_research_copy_only':True})
# Previous INT4 harbor gangway can also blind E11_NAVE at the left margin.
# Re-route this *research* connector, not protected shore terrain/sea.
oldport=bpy.data.objects['INT4_W0_PORT_NAVE_WALK']
assert oldport.type=='MESH' and len(oldport.data.vertices)>=8
moved_port=0
for v in oldport.data.vertices:
    if -850<=v.co.y<=170:
        taper=max(.2,1-abs(v.co.y+340)/890)
        v.co.x+=155*taper;moved_port+=1
oldport.data.update()
edits.append({'name':oldport.name,'vertices_shifted':moved_port,'original_research_copy_only':True})
# H1 would still lie in rock — this next edit is a 900 m long occupied
# civic valley, not a decorative hole. Its stations follow H1 public-city
# line and retain real rock walls for school, market, gardens, residences.
target=bpy.data.objects['INT10_M247_C_EAST_INHABITED_STRATA']
assert target.type=='MESH' and len(target.data.polygons)>300
source_faces=len(target.data.polygons)
cross=[
 (105,735,459,150,142),
 (240,758,451,175,176),
 (385,765,439,200,202),
 (600,782,479,239,231),
 (865,826,572,250,252),
 (1080,884,737,208,211)
]
n=17
vertices=[]
for k,(y,x,z,rx,rz) in enumerate(cross):
    for j in range(n):
        a=2*math.pi*j/n
        radial=1+.11*math.sin(3*a+.43*k)+.06*math.cos(5*a-.14*k)
        vertices.append((x+rx*math.cos(a)*radial,
                         y+12*math.sin(2*a+k*.3),
                         z+rz*math.sin(a)*radial))
faces=[tuple(range(n)),tuple(reversed(range((len(cross)-1)*n,len(cross)*n)))]
for k in range(len(cross)-1):
    for j in range(n):
        a=k*n+j;b=k*n+(j+1)%n
        faces.append((a,a+n,b+n,b))
md=bpy.data.meshes.new('INT10_R1_TEMP_INHABITED_CANYON_CUTTER')
md.from_pydata(vertices,[],faces);md.update()
cutter=bpy.data.objects.new(md.name,md);sc.collection.objects.link(cutter)
bpy.ops.object.select_all(action='DESELECT')
target.select_set(True);bpy.context.view_layer.objects.active=target
mod=target.modifiers.new('INT10_R1_LIVED_H1_PUBLIC_CANYON','BOOLEAN')
mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cutter,do_unlink=True)
assert len(target.data.vertices)>180 and len(target.data.polygons)>source_faces
assert all(math.isfinite(float(x)) for v in target.data.vertices for x in v.co)
edits.append({'name':target.name,'canyon_length_m':975,
              'volumetric_cavity':True,'faces_before':source_faces,
              'faces_after':len(target.data.polygons)})
bpy.context.view_layer.update()
after={n:ray(n) for n in names}
print('INT10_R1_FIXED_CAM_CENTER_BEFORE_AFTER',before,after,flush=True)
assert after['E11_NAVE_HUMAN']['name']!='INT10_W0_MARITIME_CIVIC_APPROACH'
assert after['E11_H1_HUMAN']['name']!='INT10_H1_HIGH_CITY_INHABITED_MARKET_STREET'
for name,old in cameras.items():
    now=bpy.data.objects[name].matrix_world
    assert max(abs(now[i][j]-old[i][j]) for i in range(4) for j in range(4))<1e-6
assert all(geomhash(bpy.data.objects[n])==h for n,h in terrain.items()),'protected real W0 terrain modified'
assert sc['CONSTRUCTION']=='HOLD' and sc['FORMAL_ART_ACCEPTED']==sc['COMPLETED_TARGETS']==0
sc['INT10_R1_SOURCE_SHA256']=SOURCE
sc['INT10_R1_GENUINE_METHOD']='FIX_E11_EYE_COLLISION_AND_CARVE_H1_OCCUPIED_CANYON'
sc['INT10_R1_WORLD_COORDINATES']='RESEARCH_UNREGISTERED'
sc['INT10_R1_ART_ADOPTION']=0
sc.camera=bpy.data.objects['E11_URBAN_AERIAL']
dst=out/'HALO9_INT10_R1_REBUILT_HUMAN_CIVIC_VIEWS.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=True)
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=13
sc.cycles.use_denoising=True;sc.render.threads_mode='FIXED';sc.render.threads=2
sc.render.resolution_x=980;sc.render.resolution_y=735;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
views=names+('INT10_NAVE_CIVIC_PUBLIC_ROOM','INT10_H1_MARKET_HUMAN_DEPTH',
             'INT10_W0_TIDAL_AND_TWIN_FAULT')
imgs={}
for n in views:
    sc.camera=bpy.data.objects[n]
    p=out/'renders'/(n+'.png');sc.render.filepath=str(p)
    bpy.ops.render.render(write_still=True)
    assert p.stat().st_size>10000,n
    imgs[n]=hashlib.sha256(p.read_bytes()).hexdigest()
    print('INT10_R1_REAL_RENDER_IMAGE',n,p.stat().st_size,flush=True)
sc.camera=bpy.data.objects['E11_URBAN_AERIAL']
bpy.ops.wm.save_as_mainfile(filepath=str(dst),compress=True)
result={
 'schema':'halo9-int10-r1-macro-vision-access-repair-v1',
 'source_sha256':SOURCE,
 'blend_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),
 'native_mesh_reconstruction':edits,
 'camera_hits_before':before,'camera_hits_after':after,
 'e11_original_matrices':{n:[[float(x) for x in row] for row in cameras[n]] for n in names},
 'protected_W0_native_terrain_geometry_sha256':terrain,
 'W0_native_terrain_unchanged':True,
 'fixed_E11_cameras_unchanged':True,
 'true_render_sha256':imgs,
 'function':'UNKNOWN',
 'art':'UNREVIEWED_NOT_ADOPTED',
 'formal_art_accepted':0,'completed_targets':0,'minecraft':'HOLD'
}
(out/'INT10_R1_TRUE_EDIT_NOT_ART.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print('INT10_R1_HUMAN_SIGHTLINES_ACTUALLY_CORRECTED',result['blend_sha256'],flush=True)
